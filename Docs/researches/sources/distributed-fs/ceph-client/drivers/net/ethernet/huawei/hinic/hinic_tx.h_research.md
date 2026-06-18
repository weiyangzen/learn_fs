# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.h

## Purpose
Declares the original HiNIC logical Tx queue structure, Tx statistics, and public Tx datapath/lifecycle APIs used by the netdevice layer.

## Important APIs And Types
`struct hinic_txq_stats` tracks packets, bytes, busy events, wake events, dropped packets, oversized-fragment packet count, and a `u64_stats_sync` guard. `struct hinic_txq` binds a netdevice to a hardware `hinic_sq`, owns stats, maximum SGE count, scratch SGE arrays for mapping and freeing, IRQ name, and NAPI instance. Public functions are `hinic_txq_get_stats()`, `hinic_lb_xmit_frame()`, `hinic_xmit_frame()`, `hinic_init_txq()`, and `hinic_clean_txq()`.

## Control Flow And State
The header exposes state that `hinic_tx.c` manages. Runtime Tx submission uses `sges` as scratch descriptors before writing an SQ WQE, while completion cleanup uses `free_sges` to reconstruct and unmap DMA mappings from completed WQEs. The NAPI instance is used for Tx completion polling rather than Rx packet delivery.

## Dependencies And Integration Points
It includes Linux netdevice, SKB, stats sync, `hinic_common.h`, and `hinic_hw_qp.h`. `hinic_main.c` allocates and initializes one `hinic_txq` per hardware SQ, aggregates stats, and wires `hinic_xmit_frame()` into netdev ops.

## Risks And Test Signals
Risks include mismatched `max_sges` relative to hardware `HINIC_MAX_SQ_BUFDESCS`, stats changes not mirrored in aggregation, and misuse of scratch SGE arrays across concurrent queue contexts. Signals include multi-queue Tx traffic, high-fragment SKBs, stats validation, Tx NAPI enable/disable ordering, and loopback transmit tests.
