# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_io.c

## Purpose

`chtls_io.c` implements the socket send and receive paths for Chelsio inline TLS TOE sockets. It builds flow-control, plain offload TX, and TLS TX work requests; manages SKB TX queues and WR credits; copies user data into SKBs/pages; handles TLS record-type control messages; returns RX credits; and implements TLS/plain receive behavior.

## Important APIs, Types, and Functions

- TX setup: `send_tx_flowc_wr()`, `flowc_wr_credits()`, `send_flowc_wr()`, and `tcp_state_to_flowc_state()`.
- TLS TX WR helpers: `tls_copy_ivs()`, `tls_copy_tx_key()`, `tls_tx_data_wr()`, `chtls_expansion_size()`, `make_tlstx_data_wr()`, and `chtls_wr_size()`.
- Plain TX WR helpers: `make_tx_data_wr()`, `is_ofld_imm()`, `calc_tx_flits()`, and `chtls_push_frames()`.
- Queue/application send: `chtls_sendmsg()`, `chtls_tcp_push()`, `skb_entail()`, `get_tx_skb()`, `get_record_skb()`, `tx_skb_finalize()`, and `chtls_splice_eof()`.
- Memory waits: `csk_mem_free()` and `csk_wait_memory()`.
- RX credit/read: `chtls_cleanup_rbuf()`, `send_rx_credits()`, `chtls_recvmsg()`, `chtls_pt_recvmsg()`, and `peekmsg()`.
- TLS control message parsing: `chtls_proccess_cmsg()` handles `TLS_SET_RECORD_TYPE`.

## Control Flow

`chtls_sendmsg()` locks the socket, waits for connection establishment if needed, checks errors/shutdown, then loops over the user iterator. When TLS TX is enabled and no record is active, it parses optional TLS control messages, sets record type, and starts a record with `tlshws.txleft`. It appends data to an existing tail SKB when possible or allocates a plain/TLS SKB with enough reserved headroom for WR headers, key memory reference, and IVs. Data is copied into linear tailroom, page fragments, or spliced from pages. Full/MSS-limited SKBs are finalized, `write_seq` advances, TLS `txleft` decreases, and push decisions honor corking, `MSG_MORE`, Nagle, and send buffer pressure.

`chtls_push_frames()` is the central TX drain. It ensures a FLOWC WR is sent before first data, computes immediate vs scatter-gather format, accounts WR credits, enqueues SKBs on the outstanding WR list, builds TLS or plain TX WR headers when needed, advances `snd_nxt`, sets completion requests, and sends through L2T. It stops when credits are insufficient or the head SKB is held.

For receives, `chtls_recvmsg()` delegates OOB to TCP, PEEK to `peekmsg()`, busy-polls when possible, and selects `chtls_pt_recvmsg()` when RX TLS offload is active. Plain receive copies queued SKB payloads from `sk_receive_queue`, handles urgent data, frees consumed SKBs, and returns RX credits. TLS receive treats TLS header SKBs specially: it emits `TLS_GET_RECORD_TYPE` cmsgs, suppresses copying the synthetic TLS header to user data, tracks payload length through `hws->rcvpld`, and increments TLS RX stats for payload consumption.

## State and Persistence Behavior

TX state is in `csk->txq`, WR list pointers, `wr_credits`, `wr_unacked`, `wr_nondata`, `CSK_TX_*` flags, `tp->write_seq`, `tp->snd_nxt`, and `tlshws.txleft/type/tx_seq_no`. RX state is in `tp->copied_seq`, `tp->rcv_wup`, `tp->rcv_wnd`, `hws->copied_seq`, `hws->rcvpld`, and receive queues. There is no persistent storage.

## Dependencies and Integration Points

This file depends on Linux socket send/receive APIs, iterator copying/splicing, TCP cork/Nagle/urgent handling, busy-poll support, Chelsio WR/CPL definitions, L2T send, and key state populated by `chtls_hw.c`. It is installed as socket operations by `chtls_main.c`.

## Risks and Edge Cases

- `chtls_push_frames()` temporarily increments `nr_frags` for IV DSGL accounting and must undo it when credits are insufficient.
- TLS IV allocation can fail after SKB state has been prepared; callers largely rely on later behavior rather than explicit propagation from `make_tlstx_data_wr()`.
- Send memory accounting spans `sk_wmem_queued`, `skb->truesize`, page caching in `TCP_PAGE`, and Chelsio WR credits.
- `chtls_pt_recvmsg()` peeks at the next SKB after freeing one and checks its flags; empty queue handling around `next_skb` is a sensitive edge.
- `chtls_proccess_cmsg` spelling is nonstandard but local; behavior rejects `MSG_MORE` with record-type cmsg.

## Test Signals

Exercise plain and TLS send with immediate and SG WRs, large records split by MFS, `MSG_MORE`, cork, OOB, splice pages, page-frag coalescing, no WR credits, send buffer exhaustion, TLS record type cmsgs, RX TLS header/payload pairing, `MSG_PEEK`, busy-poll receive, urgent data, RX credit thresholds, and socket error/shutdown handling.
