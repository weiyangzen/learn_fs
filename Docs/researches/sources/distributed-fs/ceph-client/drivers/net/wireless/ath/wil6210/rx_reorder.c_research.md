# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/rx_reorder.c

## Purpose
`rx_reorder.c` implements software RX Block Ack reordering and ADDBA handling for wil6210, plus TX-side ADDBA initiation. It keeps 802.11 sequence-number windows ordered before passing frames to the network stack when hardware reordering is not used.

## Important APIs, Types, And Functions
Sequence helpers `seq_less()`, `seq_inc()`, `seq_sub()`, and `reorder_index()` implement 12-bit sequence arithmetic. `wil_rx_reorder()` is called from NAPI for received data. `wil_rx_bar()` processes BAR frames. `wil_tid_ampdu_rx_alloc()` and `wil_tid_ampdu_rx_free()` own reorder buffers. `wil_addba_rx_request()` responds to peer ADDBA requests and optionally allocates software reorder state. `wil_addba_tx_request()` sends originator-side ADDBA.

## Control Flow
RX reorder extracts TID/CID/MID/sequence/mcast/retry via `txrx_ops.get_reorder_params()`, finds the VIF/netdev, and locks the station TID state. Frames without reorder context are delivered immediately. Multicast duplicates are dropped by retry/last-sequence checks. Unicast frames older than the head are dropped; frames beyond the window advance the head and release stored frames; duplicate slots are dropped; in-order frames are delivered directly; out-of-order frames are buffered and contiguous frames are released.

## State And Persistence
Per-station/per-TID state lives in `wil_sta_info.tid_rx[]` as `wil_tid_ampdu_rx`: reorder buffer, starting sequence, head sequence, buffer size, stored count, first-frame adjustment flag, multicast last sequence, and drop counters. Crypto replay state is separate but displayed with this state in debugfs. ADDBA TX state is in `ring_tx_data`.

## Dependencies And Integration Points
It depends on TX/RX descriptor decoding ops, `wil_netif_rx_any()`, WMI ADDBA/DELBA response commands, station state from `main.c`, and firmware capability bits for A-MSDU/hardware reordering. Disconnect cleanup in `main.c` frees reorder contexts.

## Risks
Sequence arithmetic and window advancement are correctness-critical. Race handling around BACK establishment intentionally adjusts the first received sequence, but wrong assumptions can reorder/drop valid traffic. `wil_rx_reorder()` indexes `wil->sta[cid]` before explicit CID validation, relying on TX/RX ops to produce valid CIDs. Software buffers intentionally drop remaining frames on free to avoid delivering after socket teardown.

## Test Signals
Test in-order, out-of-order, duplicate, old, window-jump, multicast retry, first-frame mismatch, BAR release, ADDBA zero/nonzero window sizes, hardware-reordering enabled/disabled, A-MSDU capability combinations, and disconnect while reorder buffers hold frames.
