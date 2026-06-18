<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/alert.c -->
# sources/distributed-fs/ceph-client/net/handshake/alert.c

## Purpose
Implements TLS alert send/receive helpers used around kTLS-backed kernel handshake sessions.

## APIs, Types, and Functions
Exports `tls_alert_send()`, `tls_get_record_type()`, and `tls_alert_recv()`. `tls_alert_send()` constructs a two-byte TLS alert record and a `SOL_TLS/TLS_SET_RECORD_TYPE` control message. `tls_get_record_type()` parses `SOL_TLS/TLS_GET_RECORD_TYPE` control messages. `tls_alert_recv()` extracts alert level and description from an incoming kvec-backed message.

## Control Flow, State, and Persistence
Sending traces the alert, fills a two-byte alert payload, builds a `msghdr` with a TLS record-type control message, sets `MSG_DONTWAIT`, initializes a kvec iterator, and calls `sock_sendmsg()`, mapping positive byte counts to zero. Receiving does not own socket state; it assumes the message iterator has alert bytes in `msg_iter.kvec`, copies the first two bytes to outputs, and traces. The file persists no state.

## Dependencies and Integration
Depends on kTLS UAPI/control messages, socket sendmsg infrastructure, kvec iterators, and handshake tracepoints. The helpers are exported for TLS consumers and the handshake TLS adapter.

## Risks and Test Signals
Risks include assuming kvec-backed receive iterators, short alert payloads, nonblocking send failures, and control-message layout errors. Test signals include sending close_notify alerts on a kTLS socket, parsing correct and irrelevant cmsgs, tracepoint observation, and handling `sock_sendmsg()` error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/alert.c -->
