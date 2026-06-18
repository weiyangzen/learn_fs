<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c

## Purpose
`11n_rxreorder.c` implements mwifiex RX BlockAck reorder handling. It creates and deletes per-peer/TID reorder windows, buffers out-of-order packets, dispatches contiguous packets, flushes holes by timer, handles ADDBA/DELBA firmware commands and responses, adjusts RX AMPDU windows for coexistence, and processes RXBA sync events.

## Important APIs, Types, And Functions
Core reorder dispatch helpers are `mwifiex_11n_dispatch_amsdu_pkt()`, `mwifiex_11n_dispatch_pkt()`, `mwifiex_11n_dispatch_pkt_until_start_win()`, and `mwifiex_11n_scan_and_dispatch()`. Table lifecycle is handled by `mwifiex_11n_create_rx_reorder_tbl()`, `mwifiex_del_rx_reorder_entry()`, `mwifiex_11n_get_rx_reorder_tbl()`, `mwifiex_11n_del_rx_reorder_tbl_by_ta()`, and `mwifiex_11n_cleanup_reorder_tbl()`.

Command/event APIs include `mwifiex_cmd_11n_addba_req()`, `mwifiex_cmd_11n_addba_rsp_gen()`, `mwifiex_cmd_11n_delba()`, `mwifiex_11n_rx_reorder_pkt()`, `mwifiex_del_ba_tbl()`, `mwifiex_ret_11n_addba_resp()`, `mwifiex_11n_ba_stream_timeout()`, `mwifiex_update_rxreor_flags()`, `mwifiex_coex_ampdu_rxwinsize()`, and `mwifiex_11n_rxba_sync_event()`.

## Control Flow
When an ADDBA request is accepted, the response generator computes negotiated window size and A-MSDU permission, returns an ADDBA response command, and creates a reorder table at the requested starting sequence number. Incoming packets call `mwifiex_11n_rx_reorder_pkt()`: without a matching table they are dispatched immediately; with a table, old/duplicate packets are dropped, BAR frames advance the window, out-of-window packets shift and flush the window, and normal packets are stored at a computed index before contiguous packets are dispatched.

The reorder buffer is linear; helpers rotate pointer arrays to simulate a circular window. A timer flushes through the last occupied slot when holes persist. Deleting a BA table drains pending packets, synchronizes against RX processing, deletes the timer, removes the list node, and frees storage. RXBA sync TLVs instruct the driver to drop indicated packets by feeding NULL payloads through the reorder path.

## State And Persistence
State lives in `priv->rx_reorder_tbl_ptr`, per-table `start_win`, `init_win`, `win_size`, `amsdu`, flags, `rx_reorder_ptr[]`, and timer context. It also reads per-station/per-interface last RX sequence arrays and mutates `priv->add_ba_param.rx_win_size` for coexistence. All state is volatile.

## Dependencies And Integration Points
This file integrates with firmware ADDBA/DELBA/BATIMEOUT/RXBA events, WMM TID handling, station tables, cfg80211 interface type for A-MSDU conversion, uAP and STA RX delivery paths, TDLS action handling, adapter RX workqueue locking, and the Tx BA table deletion functions in `11n.c`.

## Risks
RX reorder logic is sequence-number and wraparound sensitive; mistakes can drop valid packets or release stale duplicates. `mwifiex_11n_rxba_sync_event()` returns if any referenced reorder table is missing, which can skip later TLVs in the same event. Timer callbacks hold table pointers, so deletion must keep `timer_delete_sync()` ordering intact. A-MSDU dispatch passes `skb->len` rather than `rx_skb->len` into TDLS action processing, which may be semantically surprising.

## Test Signals
Tests should cover in-order packets, gaps plus timer flush, duplicates, old sequence drops, sequence wraparound, BAR handling, ADDBA accept/reject, DELBA initiated by peer/local, A-MSDU allowed/disallowed in AMPDU, RXBA sync bitmap drops, coexistence-driven RX window changes, and teardown under active RX work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c -->
