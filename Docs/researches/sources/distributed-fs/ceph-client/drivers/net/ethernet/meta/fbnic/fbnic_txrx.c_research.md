# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.c

## Purpose
`fbnic_txrx.c` implements the FBNIC packet data path and ring lifecycle: TX mapping/offloads/completion, RX buffer provisioning/completion, XDP pass/drop/TX, NAPI polling, MSI-X cleanup, ring resource allocation, hardware queue enable/disable/flush/fill, stats aggregation, idle waits, interrupt coalescing, drop-mode control, and dynamic queue memory operations.

## Important APIs, Types, And Functions
Public entry points include `fbnic_xmit_frame()`, `fbnic_features_check()`, counter aggregation helpers, NAPI/resource allocation/free, queue binding/reset, `fbnic_msix_clean_rings()`, NAPI enable/disable, `fbnic_enable()`, `fbnic_disable()`, `fbnic_flush()`, `fbnic_fill()`, `fbnic_config_drop_mode()`, `fbnic_napi_depletion_check()`, `fbnic_wait_all_queues_idle()`, `fbnic_ring_csr_base()`, and `fbnic_queue_mgmt_ops`. Major internal flows are TX offload metadata (`fbnic_tx_offloads()`/`fbnic_tx_lso()`), DMA mapping (`fbnic_tx_map()`), completion cleaning (`fbnic_clean_tcq()`/`fbnic_clean_twq*()`), RX packet assembly (`fbnic_pkt_prepare()`, `fbnic_add_rx_frag()`, `fbnic_clean_rcq()`), and XDP transmit (`fbnic_pkt_tx()`).

## Control Flow
Transmit pads short frames, checks descriptor availability, builds a metadata descriptor, requests TX timestamp/CSO/LSO as needed, DMA maps skb head/frags, marks the last descriptor, updates BQL, and rings the tail doorbell when needed. Completion polling reads TCQ descriptors, handles normal head updates and timestamp completions, unmaps descriptors, completes SKBs, updates stats, wakes stopped queues, and accounts lost timestamps during discard flush.

RX allocation creates page pools, descriptor rings, per-ring buffers, and XDP RXQ info. Fill paths allocate netmem pages, split them into BD fragments, and ring BDQ tails. RCQ polling reads header/data/optional metadata/final metadata descriptors, builds an XDP buffer from header and payload pages, converts optional timestamps, runs XDP, builds SKBs for pass, commits XDP_TX tails, returns pages on consume/drop, refills BDQs, writes RCQ heads, and updates stats.

Enable paths program descriptor DMA bases, sizes, queue controls, completion interrupt mapping, RDE layout/HDS/drop mode, page-pool direct recycling, and interrupt rearm values. Disable paths mask NAPI interrupts and clear queue enables. Flush drops outstanding TX/RX work and resets completions/BQL. Dynamic queue ops allocate replacement RX triads, stop a queue by disabling its NAPI vector and waiting idle, copy out old resources, and restart the vector with the replacement.

## State And Persistence
Rings track descriptor memory, DMA address, head/tail, doorbells, flags, queue indexes, buffers, page pools, deferred heads, and stats. NAPI vectors own flexible arrays of queue triads. Netdev-level stats aggregate destroyed ring counters. Hardware state persists in per-queue CSR registers for TWQ/TCQ/BDQ/RCQ, interrupt masks/rearms, idle status, and drop controls.

## Dependencies And Integration Points
This file depends on Linux netdev queues, BQL, DMA mapping, page_pool/netmem, XDP, NAPI, TCP/GSO helpers, PTP timestamp conversion state from `fbnic_time.c`, ring constants from `fbnic_txrx.h`, and CSR definitions. Netdev open/stop and PCI up/down call its lifecycle APIs; netdev TX and feature-check ops call its transmit paths; service work calls depletion checks.

## Risks
Descriptor accounting and wrap handling are correctness-critical. TX timestamp SKBs can block cleaning until timestamp completion unless flush discard handles them. XDP with fragments depends on HDS threshold and program capabilities enforced elsewhere. Page-pool bias/refcount handling must match BDQ cleanup or pages leak/recycle unsafely. Dynamic queue stop must wait for idle and synchronize IRQs before copying resources. Idle wait treats all-ones register values as idle masks and can trigger Tx flush, so MMIO failure semantics interact with shutdown.

## Test Signals
Exercise TX small-frame padding, CSO/LSO/GSO feature fallback, DMA map failure unwind, TX timestamp completion/loss, BQL stop/wake, RX single and fragmented packets, checksum/hash/timestamp population, XDP PASS/DROP/ABORTED/TX and invalid action paths, BDQ allocation failure, NAPI budget behavior, open/stop flush leak checks, interrupt coalescing settings, queue idle timeouts, and dynamic RX queue replacement.
