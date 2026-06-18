# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.c

## Purpose
`igc_xdp.c` handles XDP program attachment and AF_XDP zero-copy pool setup for IGC queues. It coordinates ring/NAPI quiescing when XDP state changes, updates netdev XDP redirect features, validates AF_XDP frame sizing, maps/unmaps UMEM DMA, and marks RX/TX rings for zero-copy operation.

## Important APIs, Types, and Functions
The public functions are `igc_xdp_set_prog()` and `igc_xdp_setup_pool()`. Internal helpers are `igc_xdp_enable_pool()` and `igc_xdp_disable_pool()`. The code uses `adapter->xdp_prog`, per-ring `IGC_RING_FLAG_AF_XDP_ZC`, `xsk_pool_dma_map()`, `xsk_pool_dma_unmap()`, `xsk_get_pool_from_qid()`, `igc_disable_rx_ring()`, `igc_disable_tx_ring()`, `igc_enable_rx_ring()`, `igc_enable_tx_ring()`, `napi_disable()`, `napi_enable()`, and `igc_xsk_wakeup()`.

## Control Flow
XDP program changes reject jumbo MTUs, compute whether queue restart is needed based on old and new XDP enabled state, disable each RX/TX ring and NAPI if running, atomically swap the BPF program, drop the old reference, update redirect target features, then re-enable NAPI and rings. AF_XDP pool enable validates queue IDs and frame size, maps the pool for DMA, optionally quiesces the queue pair if the interface is running with XDP enabled, sets zero-copy flags on both rings, restarts the queue pair, and wakes RX. Disable does the reverse: look up the pool, optionally quiesce, unmap DMA, clear flags, and restart.

## State and Persistence Behavior
The file updates runtime-only state: `adapter->xdp_prog`, netdev XDP feature flags, ring zero-copy flags, and DMA mapping state owned by the XSK pool. No persistent state exists. Running rings are temporarily stopped and restarted to make state transitions coherent.

## Dependencies and Integration Points
It integrates with Linux BPF/XDP, AF_XDP socket pools, VLAN sizing assumptions, netdev feature advertising, IGC ring enable/disable helpers, NAPI lifecycle, PCI device DMA attributes, and the IGC XSK wakeup path.

## Risks and Edge Cases
Jumbo frames are unsupported. AF_XDP frame size must hold a full Ethernet frame plus double VLAN tags because the driver does not support multi-buffer XDP. Queue ID validation must cover both RX and TX queue counts. If `igc_xsk_wakeup()` fails after re-enabling a pool, the code unmaps DMA and returns an error, so flag cleanup and ring state should be scrutinized. Program swaps rely on `xchg()` and correct BPF reference ownership.

## Test Signals
Test XDP attach/detach while down and running, jumbo MTU rejection, redirect feature toggling, AF_XDP pool enable/disable with invalid queues and small frames, DMA map failure, wakeup failure, and repeated pool transitions while packets are flowing.
