# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.c

## Purpose

`chtls_cm.c` implements Chelsio TLS TOE connection management. It owns passive-open listener setup, child socket creation, accept queue movement, CPL dispatch for connection/data/close/abort messages, receive queue demultiplexing, close/disconnect/shutdown/destroy protocol operations, and WR acknowledgement handling.

## Important APIs, Types, and Functions

- Socket allocation/lifetime: `chtls_sock_create()`, `chtls_sock_release()`, `chtls_release_resources()`, and `chtls_destroy_sock()`.
- Listener management: `chtls_listen_start()`, `chtls_listen_stop()`, listen hash helpers, `chtls_reset_synq()`, and PASS_OPEN/CLOSE_LISTSRV reply handlers.
- Passive accept: `chtls_pass_accept_req()`, `chtls_pass_accept_request()`, `chtls_recv_sock()`, `chtls_pass_accept_rpl()`, `chtls_pass_establish()`, and accept queue helpers.
- Close/abort: `chtls_close()`, `chtls_disconnect()`, `chtls_shutdown()`, `chtls_close_conn()`, `chtls_send_reset()`, `chtls_send_abort()`, `chtls_peer_close()`, `chtls_close_con_rpl()`, `chtls_abort_req_rss()`, and `chtls_abort_rpl_rss()`.
- RX data/TLS: `chtls_rx_data()`, `chtls_recv_data()`, `chtls_rx_pdu()`, `chtls_recv_pdu()`, `chtls_rx_cmp()`, and `chtls_rx_hdr()`.
- ACK/TCB replies: `chtls_wr_ack()`/`chtls_rx_ack()` and `chtls_set_tcb_rpl()`.
- Exported dispatch table: `chtls_handlers[NUM_CPL_CMDS]`.

## Control Flow

Listener start resolves a Chelsio-owned netdev for the listening address, checks adapter initialization, allocates a `listen_ctx`, allocates an STID, records it in the listen hash, optionally installs an IPv6 CLIP entry, and calls `cxgb4_create_server()` or `cxgb4_create_server6()`. Listener stop removes the hash entry, resets SYN-received children, requests server removal, releases CLIP entries, and disconnects offloaded accept-queue children.

On `CPL_PASS_ACCEPT_REQ`, the handler validates the STID/TID, then processes the request under the listener lock or backlog. It allocates a Linux request socket, parses Ethernet/IP/TCP headers, records peer/local tuple and TCP options, creates a child socket with `tcp_create_openreq_child()`, resolves route/neighbour/L2T, fills `chtls_sock` fields, installs `chtls_backlog_rcv`, chooses RSS/TX queues, inserts the TID, and sends a PASS_ACCEPT_RPL through L2T. When `CPL_PASS_ESTABLISH` arrives, the child moves to `TCP_ESTABLISHED`, receives WR credits, and is either added to the parent accept queue or scheduled for reaping if the queue is full.

RX data CPLs are demultiplexed by TID. Plain `CPL_RX_DATA` strips CPL/RSS headers, updates TCP receive state, handles urgent pointers, queues the SKB on `sk_receive_queue`, and wakes readers. TLS payload CPLs are queued on `tlshws.sk_recv_queue`; TLS completion/header CPLs synthesize a TLS header SKB, mark errors as `CONTENT_TYPE_ERROR`, pair the header with queued payload, advance `rcv_nxt`, and wake readers.

Close and abort handling mirrors TCP state transitions with Chelsio CPLs. Local close may send `CPL_CLOSE_CON_REQ` or abort depending on data loss, SYN state, and linger. Peer close and close replies move sockets through CLOSE_WAIT, CLOSING, FIN_WAIT2, LAST_ACK, TIME_WAIT, or TCP_CLOSE and release hardware resources. Abort requests send abort replies, tear down TIDs/L2T/queues, and complete sockets; SYN_RECV aborts are coordinated through the listener backlog.

WR acknowledgements return credits, retire WR SKBs from the outstanding list by credit count stored in `skb->csum`, update `snd_una`, clear wait/failover flags, and push more queued frames if possible.

## State and Persistence Behavior

State is volatile and divided among listener hash entries, `listen_ctx` SYN queues, `request_sock` objects, child sockets, and `chtls_sock`. Hardware identity is tracked by STID/TID tables in `cdev->tids`. WR credits are maintained in `csk->wr_credits`, `wr_unacked`, `wr_max_credits`, `wr_nondata`, and the WR list. Passive children use `csk->passive_reap_next` both for request-socket linkage and reap-list linkage depending on state.

Synchronization uses socket locks, BH disabling, listener/device spinlocks, a global reap-list spinlock, and backlog callbacks when sockets are owned by user context.

## Dependencies and Integration Points

The file integrates with Linux TCP internals (`tcp_create_openreq_child`, request queues, timewait, port inheritance), TLS context destructors, IPv4/IPv6 routing and neighbour APIs, VLAN real devices, Chelsio L2T/TID/STID APIs, Chelsio CPL/FW formats, and `chtls_io.c`/`chtls_hw.c` for TX flow-control, push, key freeing, and TCB quiesce.

## Risks and Edge Cases

- Passive-open handling has many lifetime edges: request socket, child socket, listener, STID/TID, L2T, module ref, and accept queue state must unwind in the right order.
- `passive_reap_next` is reused for multiple logical links, increasing the risk of stale linkage if a path skips cleanup.
- RX TLS header/payload pairing assumes completion and payload queues remain ordered; missing payloads queue the header alone.
- `alloc_ctrl_skb()` can reuse cached SKBs by incrementing refcount; misuse could corrupt abort messages.
- Some allocations use `__GFP_NOFAIL`, which avoids failed control sends but can block under memory pressure.

## Test Signals

Exercise listen start/stop for IPv4/IPv6, duplicate listen attempts, CLIP failure, accept queue full, SYN queue reset, passive-open ARP failure, child establishment, TLS RX header/payload/error records, local close with data pending, peer close across FIN states, abort request/reply races, WR credit retirement, and detach while listeners/children exist.
