<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c

## Purpose
`recvmsg.c` implements AF_RXRPC userspace and kernel receive APIs. It notifies sockets about ready calls, prioritizes out-of-band security messages, copies verified DATA payloads to callers, advances receive windows, reports terminal call status, and exposes `rxrpc_kernel_recv_data()`.

## Important APIs, Types, And Functions
Important functions include `rxrpc_notify_socket()`, `rxrpc_recvmsg()`, and `rxrpc_kernel_recv_data()`. Internal helpers include `rxrpc_recvmsg_term()`, `rxrpc_rotate_rx_window()`, `rxrpc_verify_data()`, `rxrpc_recvmsg_user_id()`, `rxrpc_recvmsg_challenge()`, `rxrpc_recvmsg_oob()`, and `rxrpc_recvmsg_data()`.

## Control Flow
Call notification queues a referenced call on `rx->recvmsg_q` or invokes kernel callbacks. `rxrpc_recvmsg()` blocks or returns immediately according to socket timeout, handles OOB messages first, dequeues or peeks a call, serializes user access with `call->user_mutex`, emits user-call-ID and peer address control data, copies DATA through `rxrpc_recvmsg_data()`, and finally emits terminal ACK/ABORT/ERROR control messages when the call completes. Data receive verifies each SKB through the connection security module once, copies partial packet data, rotates fully consumed packets out of the receive window, sets idle ACK triggers, and stops on OOB priority or buffer fullness. Kernel receive follows the same data path but enforces expected length and want-more semantics.

## State And Persistence
State lives in socket `recvmsg_q`, `recvmsg_oobq`, locks, call `recvmsg_queue`, `rx_pkt_offset`, `rx_pkt_len`, `rx_consumed`, `ackr_nr_consumed`, `ackr_window`, flags such as `RECVMSG_READ_ALL`, and completion/error fields. Consuming SKBs updates ACK state and may poke the call for IDLE ACK generation.

## Dependencies And Integration Points
The file integrates with security `verify_packet()`, OOB challenge handling, socket callbacks/wait queues, call release/completion, SKB timestamp/control-message APIs, kernel service APIs, and ACK scheduling.

## Risks And Edge Cases
Concurrent recvmsg callers are serialized by call mutex but socket queues still need careful requeue logic. `MSG_PEEK` must not advance offsets or consume SKBs. OOB messages interrupt normal data delivery. Short/excess kernel-service reads abort at higher layers through returned errors. The function assumes `call->socket` exists when notifying; released calls are skipped.

## Test Signals
Test blocking/nonblocking receive, `MSG_PEEK`, partial reads across packet boundaries, terminal control messages, OOB challenge priority, concurrent recvmsg requeue behavior, security verification failures, kernel receive short/excess data, idle ACK triggering, and call release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c -->
