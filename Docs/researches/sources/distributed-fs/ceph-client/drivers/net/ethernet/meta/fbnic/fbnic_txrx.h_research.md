# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.h

## Purpose
`fbnic_txrx.h` defines queue/ring constants, descriptor capacity limits, RX buffer geometry, ring/stat structures, NAPI vector layout, and public TX/RX lifecycle APIs for the FBNIC data path.

## Important APIs, Types, And Functions
Key constants set maximum descriptors per SKB, TX/RX minimum ring sizes, maximum TX/RX/XDP queues, queue size bounds/defaults, coalescing defaults, RX headroom/tailroom/padding, ring flags, HDS threshold bounds, and page-count bias. Key structs are `fbnic_pkt_buff`, `fbnic_queue_stats`, `fbnic_rx_buf`, `fbnic_ring`, `fbnic_q_triad`, and `fbnic_napi_vector`. Prototypes expose transmit, feature checks, stat aggregation, resource/NAPI/queue lifecycle, interrupt handling, enable/disable/fill/flush, drop-mode and depletion checks, idle wait, ring CSR base, debug hooks, and queue management ops.

## Control Flow
The header models each queue triad as two sub-rings plus one completion ring. TX triads use TWQ0/TWQ1 and TCQ; RX triads use HPQ/PPQ and RCQ. NAPI vectors hold flexible arrays of these triads, allowing mixed TX/RX assignment.

## State And Persistence
Ring structs hold both fast-path state (`head`, `tail`, descriptors, buffers, doorbells, stats) and slow-path DMA allocation metadata. Queue stats use `u64_stats_sync` for concurrent readers. Accumulated stats are moved to `fbnic_net` before ring destruction.

## Dependencies And Integration Points
The header includes netdevice, skbuff, u64 stats, and XDP APIs. It is included by netdev, PCI lifecycle, and TX/RX implementation modules. `fbnic_queue_mgmt_ops` integrates with netdev queue memory management.

## Risks
Constants must remain consistent with hardware descriptor formats and netdev/XDP constraints. Increasing stats fields requires updating aggregation `BUILD_BUG_ON()` checks in implementation. Ring flag semantics determine whether a ring has context, stats, or is disabled; misuse can leak counters or allocate the wrong buffers.

## Test Signals
Compile-time signals include descriptor-limit and stats-size checks. Runtime signals include correct ring allocation for configured queue sizes, XDP fragment compatibility, queue stats consistency, and no descriptor starvation under worst-case SKB fragment counts.
