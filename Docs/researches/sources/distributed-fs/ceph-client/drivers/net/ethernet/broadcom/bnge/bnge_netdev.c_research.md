# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.c

## Purpose
This is the main Linux net_device integration file for `bnge`. It allocates and registers the netdev, owns open/close lifecycle, allocates software and DMA ring memory, programs firmware rings/VNICs/filters/stat contexts, handles NAPI/IRQ setup, manages RX buffer posting, accumulates stats, drives periodic service work, and exposes netdev operations.

## Important APIs, Types, And Functions
Public APIs are `bnge_netdev_alloc`, `bnge_netdev_free`, `bnge_set_ring_params`, `bnge_cp_ring_for_rx`, `bnge_cp_ring_for_tx`, `bnge_fill_hw_rss_tbl`, `bnge_alloc_rx_data`, `bnge_alloc_rx_netmem`, `bnge_find_next_agg_idx`, `__bnge_alloc_rx_frag`, `__bnge_queue_sp_work`, and `bnge_copy_hw_masks`. Important internal clusters cover stats allocation/accumulation, NQ/CP tree allocation, RX/TX ring memory, VNIC attributes, HWRM ring allocation/free, L2 filters, interrupts, NAPI, chip init, open/close, and netdev stat ops.

## Control Flow
`bnge_netdev_alloc` creates the netdev, sets feature flags, initializes workqueue/timer/ring sizing/filter hash/MAC/PHY/stats, and registers it. `ndo_open` calls `bnge_open_core`, which reserves rings, allocates core memory, adds NAPI, requests IRQs, initializes NIC firmware objects, enables NAPI/interrupts/TX, starts the timer, and polls module/link status. `ndo_stop` disables TX, clears open state, deletes the timer, frees firmware resources, disables NAPI, saves stats, frees buffers/IRQs/NAPI/core memory, and shuts down link.

## State And Persistence
The file owns most `struct bnge_net` runtime state: ring sizes/masks, NAPI array, RX/TX rings, NQ/CP tree, group firmware IDs, VNICs, filters, RSS key/table, stats memory, timer/workqueue events, pause/link request cache, and previous stats. Firmware-visible IDs are stored in ring/VNIC/filter/stat fields and reset to invalid on free.

## Dependencies And Integration Points
It depends on `bnge_hwrm_lib.c` for all firmware object operations, `bnge_rmem.c` for ring memory allocation, `bnge_resc.c` for reservation, `bnge_link.c` for PHY updates, `bnge_txrx.c` for poll/xmit, ethtool setup, page_pool, PCI MSI-X, and Linux netdev queue APIs.

## Risks
The open/close error paths are complex and must unwind in exact reverse order. RX page-pool handling differs for unreadable netmem and smaller hardware RX pages. Firmware IDs, doorbells, IRQ vectors, NAPI indices, and queue counts must stay aligned after resource reductions. Stats are accumulated across wrap masks and saved across close, so ordering around `BNGE_STATE_STATS_ENABLE` matters.

## Test Signals
Test probe/register/unregister, repeated open/close, traffic across all queues, jumbo and GRO/LRO/TPA, RSS distribution, multicast/unicast/promisc transitions, MSI-X affinity, IRQ/NAPI teardown races, link retry, stats before and after close, and error injection in ring/VNIC/stat allocation.
