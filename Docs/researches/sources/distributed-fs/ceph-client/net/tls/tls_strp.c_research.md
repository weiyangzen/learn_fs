<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_strp.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_strp.c

## Purpose
`tls_strp.c` implements the kTLS receive stream parser used by software RX and device RX fallback. It assembles exactly one TLS record from the TCP receive queue into an anchor skb, supports zero-copy references to queued TCP skbs when safe, falls back to copy mode under short queues or mixed decrypted/encrypted data, and schedules process-context work when parsing cannot be completed in the data-ready path.

## Important APIs, Types, and Functions
- `tls_strp_abort_strp()` stops parsing and reports socket errors.
- `tls_strp_msg_load()`, `tls_strp_msg_done()`, `tls_strp_msg_detach()`, `tls_strp_msg_cow()`, and `tls_strp_msg_hold()` manage the current parsed TLS record.
- `tls_strp_copyin_frag()` and `tls_strp_copyin_skb()` copy incoming TCP data into either page frags or a frag_list-backed skb.
- `tls_strp_read_sock()`, `tls_strp_check_rcv()`, `tls_strp_data_ready()`, and `tls_strp_work()` drive parser progress from TCP readiness and workqueue contexts.
- `tls_strp_init()`, `tls_strp_stop()`, `tls_strp_done()`, `__tls_strp_done()`, `tls_strp_dev_init()`, and `tls_strp_dev_exit()` manage parser and global workqueue lifetime.

## Control Flow
RX setup initializes an empty anchor skb and arms `sk_data_ready` to call `tls_data_ready()` in `tls_sw.c`, which delegates to `tls_strp_data_ready()`. If the socket is user-owned, work is queued to avoid lock conflicts; otherwise the parser reads immediately. `tls_strp_read_sock()` checks `tcp_inq()`, maps the TCP queue directly into the anchor if a full contiguous record is available, asks `tls_rx_msg_size()` for the record length, and validates queue sequence/decryption consistency. If data is short, mixed, or memory pressure requires it, copy mode allocates page frags and pulls bytes with `tcp_read_sock()`. Once a full record is ready, `msg_ready` is set and upper TLS RX is notified. After decryption and consumption, `tls_strp_msg_done()` advances TCP copied sequence or flushes copied frags and immediately attempts to parse the next record.

## State and Persistence
Each `tls_strparser` stores the lower socket, anchor skb, current stream message offsets/length, `mark` content type, copy-mode and mixed-decryption flags, stop flag, message-ready flag, and a work item. Global state is only the `tls-strp` workqueue. The parser keeps skb/page references while a record is active and releases them when the record is consumed or the parser is torn down.

## Dependencies and Integration Points
The parser depends on TCP receive queue helpers, skb frag/frag_list mechanics, kTLS record-size validation in `tls_rx_msg_size()` from `tls_sw.c`, and the RX ready callback `tls_rx_msg_ready()`. Device TLS uses `skb->decrypted` state and `tls_strp_msg_detach()` to turn device-decrypted input into a delivered output skb.

## Risks and Edge Cases
Risk concentrates around skb ownership. Direct queue anchoring must not outlive TCP queue data; copy mode must correctly unref page frags and frag lists. Mixed decrypted status forces copy mode because device-offload records cannot be represented as a single consistent direct queue. `force_refresh` in `tls_strp_msg_load()` handles receive queue changes after the socket lock was released. Parser abort must set a positive `sk_err` and wake pollers.

## Test Signals
Receive tests should cover short headers, fragmented TLS records, coalesced records, low-memory fallback to workqueue, mixed device/software decrypted data, async decrypt holding records, parser abort on bad TLS length/version, and close/stop races. Instrumenting `tcp_read_done()` progress and skb refcounts is useful for leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_strp.c -->
