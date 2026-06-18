<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/oob.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/oob.c

## Purpose
`oob.c` implements out-of-band message delivery and response handling, primarily for security challenge/response flows that must be surfaced to userspace or kernel services outside normal call data.

## Important APIs, Types, And Functions
Important APIs include `rxrpc_notify_socket_oob()`, `rxrpc_add_pending_oob()`, `rxrpc_sendmsg_oob()`, `rxrpc_kernel_query_oob()`, `rxrpc_kernel_dequeue_oob()`, `rxrpc_kernel_free_oob()`, `rxrpc_kernel_query_challenge()`, and `rxrpc_kernel_reject_challenge()`. Internal helpers parse `SOL_RXRPC` control messages and locate pending OOB SKBs by `RXRPC_OOB_ID`.

## Control Flow
Security code posts an OOB SKB with `rxrpc_notify_socket_oob()`. The function assigns a monotonically increasing OOB ID, queues the SKB on `recvmsg_oobq`, invokes app callbacks when present, or wakes userspace readers. `recvmsg()` exposes the message and moves response-required SKBs into a red-black pending tree. `sendmsg()` with OOB control messages parses `RXRPC_OOB_ID`, `RXRPC_RESPOND`, optional `RXRPC_ABORT`, and RxGK appdata, removes the matching pending SKB, then either aborts the connection or dispatches to the security module's `sendmsg_respond_to_challenge()`.

## State And Persistence
OOB state lives on `struct rxrpc_sock`: `recvmsg_oobq`, `pending_oobq`, `oob_id_counter`, `recvmsg_lock`, and optional app ops. SKBs carry the OOB type in `skb->mark`, the OOB ID in `skb_mstamp_ns`, and challenge connection references in `rxrpc_skb_priv`.

## Dependencies And Integration Points
This file integrates with `recvmsg.c`, `sendmsg` control-message parsing, security challenge handlers in RxGK/RxKAD, socket callbacks, SKB ref tracking, and kernel-service exported APIs.

## Risks And Edge Cases
The pending tree assumes the 64-bit OOB ID counter will not wrap. A response without a valid ID returns `-EBADSLT`; wrong OOB type returns protocol errors. Connection references must be released exactly once when an OOB SKB is freed. Socket-close state suppresses new OOB notifications.

## Test Signals
Cover userspace challenge receive/respond, invalid/missing duplicate control messages, challenge rejection, kernel dequeue/free/query paths, pending OOB lookup/removal, app callback versus `sk_data_ready`, and socket close while OOB messages are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/oob.c -->
