
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.c

## Purpose
`hinic3_tx.c` implements hinic3 transmit queue allocation, SKB DMA mapping into SQ descriptors, checksum/TSO/UFO/VLAN offload programming, doorbell submission, completion polling, and TX queue flushing.

## Important APIs, Types, And Functions
- `hinic3_alloc_txqs()`/`hinic3_free_txqs()` allocate static TXQ objects for all possible queues and initialize stats.
- `hinic3_alloc_txqs_res()`/`hinic3_free_txqs_res()` allocate/free dynamic TX descriptors, SKB tracking, and DMA-info arrays.
- `hinic3_configure_txqs()` binds dynamic resources and SQs to active TX queues and computes stop/start thresholds.
- `hinic3_xmit_frame()` is the netdev transmit entry point.
- `hinic3_send_one_skb()` validates carrier/queue space, prepares offload/task data, allocates WQEBBs, maps SKB fragments, writes descriptor control, and rings the SQ doorbell.
- `hinic3_tx_poll()` reclaims completed TX WQEs based on hardware CI.
- `hinic3_flush_txqs()` forces hardware TX drop/stop and resets subqueues during teardown.

## Control Flow
Transmit starts in `hinic3_xmit_frame()`, which drops if carrier is down or queue mapping is invalid. `hinic3_send_one_skb()` pads short frames, computes SGE/WQEBB needs, stops the subqueue if free WQEBBs are below threshold, prepares offload metadata, reserves queue elements, maps the linear SKB and frags for DMA, updates BDs/task WQE if needed, records the SKB in `tx_info[pi]`, updates BQL/netdev queue state, writes SQ control fields, and rings the SQ doorbell with local PI.

Completion polling reads hardware CI from the coherent CI table, walks `tx_info` entries from local CI while complete WQEBB spans are available, unmaps DMA, consumes SKBs through NAPI, advances local WQ CI by total WQEBBs, and wakes the subqueue based on free WQEBBs.

## State And Persistence Behavior
TXQ state includes `tx_info` per WQ index, per-SKB `dma_info` arrays, SQ pointer, queue thresholds, and stats. Hardware-visible state includes WQ descriptors, owner bits, producer index via doorbell, and CI updates through coherent memory. All state is runtime-only and released when queues are destroyed.

## Dependencies And Integration Points
The file depends on Linux VLAN, IP/IPv6, checksum, I/O polling, BQL netdev queue helpers, `hinic3_nic_io`, `hinic3_nic_cfg`, and `hinic3_wq`. It integrates with firmware/device control through `hinic3_force_drop_tx_pkt()` and with netdev through `ndo_start_xmit` and NAPI completion.

## Risks And Edge Cases
- DMA rollback is handled if mapping fails after WQ reservation; this relies on restoring both `prod_idx` and owner bit.
- `hinic3_tx_csum()` only offloads VXLAN UDP tunnels on the standard port; other encapsulations fall back to `skb_checksum_help()`.
- Compact WQE mode is only used for no-offload, single-SGE packets under `HINIC3_COMPACT_WQEE_SKB_MAX_LEN`; oversized compact candidates are dropped.
- `PLDOFF` above `SQ_CTRL_MAX_PLDOFF` invalidates offload and drops the packet.
- `hinic3_tx_poll()` assumes `tx_info->skb` is valid for any completed span; corrupted completion accounting can dereference null/stale SKBs.
- Stats structures are initialized but this file does not visibly update most counters, so observability may be incomplete.

## Test Signals
Validate line-rate TX, fragmented SKBs up to `HINIC3_MAX_SQ_SGE`, short frame padding, queue stop/wake behavior, TSO for IPv4/IPv6, VXLAN tunnel checksum/TSO, VLAN insertion, DMA mapping failure injection, TX completion wraparound, and `hinic3_flush_txqs()` during interface stop.
