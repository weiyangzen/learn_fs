# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.c

## Purpose

`otx2_common.c` is the central shared implementation for OcteonTX2/RVU NIC PF/VF resource setup, queue configuration, stats, RSS, MAC/MTU/pause programming, TX scheduler configuration, NPA/NIX attach/detach, buffer/aura/pool management, interrupt affinity, feature gating, mailbox response handlers, and DMA mapping helpers used by the transmit path.

## Important APIs, Types, And Functions

- Stats APIs update RQ/SQ op stats, LMAC/FEC stats, device stats, and `ndo_get_stats64`.
- Netdev programming APIs set/get MAC address, MTU, pause frames, RSS key/table/flowkey, UDP GSO LSO formats, IRQ coalescing, and max MTU.
- Buffer helpers allocate RX buffers from AF_XDP, page_pool, or napi fragments and refill pools.
- Scheduler helpers allocate/configure/free/flush NIX TX scheduler queues and SQBs.
- Queue setup functions initialize RQ, SQ, CQ, NIX LF, NPA LF, SQ/RQ aura pools, refill work, and CQ interrupt affinity.
- Resource APIs attach/detach NPA/NIX LFs, disable NPA/NIX contexts, and configure backpressure.
- Mailbox handlers cache AF responses for CGX stats, FEC stats, NPA/NIX LF allocation, MSIX offsets, and backpressure ids.
- Feature helpers validate NTUPLE/TC feature interactions and query MACsec capability.
- Weak `otx2_mbox_up_handler_*` stubs provide default no-op handling for CGX/MCS up messages.
- DMA helpers map/unmap skb fragments, switching to bidirectional DMA for XFRM offload.

## Control Flow

Probe/open setup attaches NPA/NIX resources, reads MSIX offsets, configures NPA LF, allocates aura/pool software state, initializes RQ and SQ aura/pool contexts, allocates buffer pointers and frees them to hardware auras, configures NIX LF with queue counts and RSS settings, initializes RQ/SQ/CQ contexts, sets up scheduler hierarchy, RSS, LSO, IRQ coalescing, and refill work. Much of this code batches AQ mailbox messages and flushes when the shared mailbox buffer is full.

Queue initialization is layered. `otx2_rq_init()` programs RQ drop/pass thresholds and large-packet aura. `otx2_sq_init()` allocates SQE, doubled SQE/CPT-SG ring, CPT response memory, TSO headers, SG tracking, optional timestamp memory, SQB metadata, and then calls the silicon-selected `sq_aq_init`. `otx2_cq_init()` selects RX/TX/XDP/QoS type, allocates CQE memory, configures XDP memory model when needed, links the receive buffer pool, and programs CQ context.

Cleanup frees SQBs back to pools, drains/free buffer pointers, destroys page_pools and AF_XDP state, frees scheduler queues, disables contexts, and detaches resources through mailbox. Feature toggles ensure TC and ntuple rules do not conflict. Stats paths read hardware atomic op registers or send mailbox requests to refresh CGX counters.

## State And Persistence

The file manages most of `struct otx2_nic` runtime state: `hw` queue counts, channel bases, scheduler lists, RSS config, stats, bpid values, capability flags, `qset` queues/pools/CQs, refill work, flow config, AF_XDP bitmaps, and mailbox-derived resource metadata. Hardware state persists in NPA LF/aura/pool contexts, NIX LF/RQ/SQ/CQ/RSS/LSO contexts, scheduler hierarchy, backpressure, MAC/MTU/pause settings, interrupt coalescing registers, and flow/capability state until reset or detach.

## Dependencies And Integration Points

It depends on Linux PCI/interrupt/page_pool/XDP/DCB/XFRM APIs, OTX2 register and context headers, `cn10k.h` silicon ops, AF mailbox ABI, QoS/TC/flow helpers, devlink/ethtool call sites, and transmit/receive datapaths. Many functions are exported for PF, VF, representor, ethtool, TC, and XDP modules.

## Risks

- Error unwinding is complex; many setup functions allocate multiple qmem/page_pool/software structures before returning, so partial failures can leak or leave mailbox messages queued.
- `otx2_sq_init()` has repeated comment text and several allocations where later failures do not free earlier qmem allocations locally.
- `otx2_dma_map_skb_frag()` calls `skb_unshare()` for XFRM offload but assigns only to a local variable, which needs careful validation against caller expectations.
- Feature interaction rules for NTUPLE and TC are strict; stale flow counts can block feature changes.
- Shared mailbox batching requires callers to reset or flush correctly on allocation failures.
- Scheduler and backpressure configuration has many silicon/SDP/DCB branches; wrong channel/link type can break traffic shaping or pause behavior.

## Test Signals

Probe/open/close/reset cycles, RX/TX traffic, RSS indirection/hash tests, UDP GSO offload, XDP and AF_XDP zero-copy, page_pool and napi-frag paths, PTP timestamp SQ allocation, MAC/MTU/pause changes, DCB/PFC backpressure, TC/ntuple feature toggles, NPA/NIX attach/detach failure injection, IRQ affinity/coalescing, stats correctness, and IPsec DMA mapping/unmapping tests provide broad coverage.
