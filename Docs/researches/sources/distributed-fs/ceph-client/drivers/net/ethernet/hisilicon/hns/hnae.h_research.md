# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.h

## Purpose
`hnae.h` defines the shared HNAE contract: descriptor layout, ring and queue state, handle state, AE device registration structures, callback tables, ring helpers, buffer operations, descriptor bit fields, coalescing constants, media/port/loopback enums, and exported framework prototypes.

## Important APIs and Types
`struct hnae_desc` is the packed hardware descriptor union for TX and RX. `struct hnae_desc_cb` is the software companion carrying DMA address, CPU buffer, private skb/page pointer, length, page offset, reuse flag, and descriptor type. `struct hnae_ring`, `struct hnae_queue`, and `struct hnae_handle` model the runtime datapath. `struct hnae_ae_ops` is the provider contract for queue setup, start/stop/reset, IRQ control, link adjustment, MAC address, multicast/unicast TCAM operations, MTU, stats, LEDs, register dumps, coalescing, pause, loopback, and RSS.

## Control Flow
The header supplies inline helpers used by the framework and netdev paths. `ring_space`, `ring_dist`, and `is_ring_empty` define ring index semantics with one unused descriptor slot. `hnae_reserve_buffer_map`, `hnae_alloc_buffer_attach`, `hnae_free_buffer_detach`, `hnae_replace_buffer`, and `hnae_reuse_buffer` provide the common RX buffer lifecycle. `hnae_reinit_all_ring_desc` and `hnae_reinit_all_ring_page_off` rewrite RX descriptor addresses after buffer-size changes.

## State and Persistence
All state is volatile kernel state. Rings persist descriptor memory, software descriptor control blocks, interrupt numbers, coalescing counters, statistics, and producer/consumer indexes for the life of a handle. Handles persist ownership, PHY/media metadata, queue array, coalescing configuration, VF and port identifiers, and buffer operation hooks.

## Dependencies and Integration Points
The header depends on Linux netdevice, PHY, ACPI, notifier, module, and device APIs. It is included by the HNAE core, the DSAF platform driver, MAC code, RCB/PPE code, and upper Ethernet driver code. Register field helper macros (`hnae_set_field`, `hnae_get_field`, etc.) mirror DSAF register helpers and are used for descriptor bit manipulation.

## Risks
The header has a duplicated `get_regs` function pointer declaration in `struct hnae_ae_ops`, which is harmless only if the compiler accepts the duplicate member in this source snapshot; in normal C this would be a build issue, so this tree likely reflects an older or transformed source state that deserves compile validation. Descriptor bit masks include a suspicious `HNS_RXD_IPOFFSET_M` definition based on `HNS_TXD_IPOFFSET_S`, so any users should be checked for intended shift values. Inline buffer replacement assumes the reserved control block is fully mapped and initialized.

## Test Signals
Compile-time coverage is important for structure layout and callback-table compatibility. Runtime signals include RX descriptor address programming after MTU changes, correct ring-space accounting under wraparound, page reuse paths, and ethtool operation availability through the AE ops table.
