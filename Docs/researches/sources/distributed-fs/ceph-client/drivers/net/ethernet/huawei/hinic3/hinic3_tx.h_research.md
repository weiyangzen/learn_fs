
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.h

## Purpose
`hinic3_tx.h` defines hinic3 SQ descriptor/task formats, TX offload bitfields, TX queue state, dynamic TX resources, and public TX lifecycle/submit/poll functions.

## Important APIs, Types, And Functions
- `VXLAN_OFFLOAD_PORT_LE`, `TCP_HDR_DATA_OFF_UNIT_SHIFT`, `TRANSPORT_OFFSET`, `HINIC3_COMPACT_WQEE_SKB_MAX_LEN`, `HINIC3_TX_POLL_WEIGHT`, and default thresholds parameterize TX behavior.
- `enum sq_wqe_data_format`, `enum sq_wqe_ec_type`, `enum sq_wqe_tasksect_len_type`, and `enum hinic3_tx_offload_type` describe descriptor mode and offload flags.
- `SQ_CTRL_*`, `SQ_CTRL_QUEUE_INFO_*`, and `SQ_TASK_INFO*` macros encode hardware WQE control/task fields.
- `struct hinic3_sq_wqe_desc`, `struct hinic3_sq_task`, and `struct hinic3_sq_wqe_combo` describe the descriptor pieces assembled by `hinic3_tx.c`.
- `struct hinic3_txq_stats`, `struct hinic3_dma_info`, `struct hinic3_tx_info`, `struct hinic3_txq`, and `struct hinic3_dyna_txq_res` define software TX state.

## Control Flow
The implementation fills a `hinic3_sq_wqe_combo` from WQ elements, maps an SKB into `hinic3_dma_info`, encodes offload choices in `hinic3_sq_task` and descriptor control words, and stores the SKB/WQEBB count in `hinic3_tx_info` for later completion reclamation.

## State And Persistence Behavior
The header describes per-queue and per-packet runtime state only. No state persists beyond queue lifetime.

## Dependencies And Integration Points
It includes Linux bitops, IP/IPv6, netdevice, and checksum headers and relies on `struct hinic3_io_queue`/`struct hinic3_sq_bufdesc` from NIC I/O/WQ headers. Public functions are used by the hinic3 netdev open/close/NAPI paths.

## Risks And Edge Cases
- Hardware field masks are protocol-critical; changing bit positions breaks descriptor interpretation.
- `SQ_CTRL_QUEUE_INFO_GET()` expects a little-endian descriptor value and converts internally.
- `HINIC3_MAX_SQ_SGE` must remain aligned with dynamic DMA-info allocation and hardware maximum.
- `HINIC3_DEFAULT_STOP_THRS`/`START_THRS` are clamped by queue depth in implementation.

## Test Signals
Build and runtime TX offload tests, descriptor decode review against hardware spec, and queue threshold behavior under backpressure are the strongest signals.
