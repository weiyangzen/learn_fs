<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rxrpc.c -->
# sources/distributed-fs/ceph-client/fs/afs/rxrpc.c

## Purpose
Owns the RxRPC socket used by kAFS, client call lifecycle, asynchronous receive processing, incoming cache-manager callback dispatch, reply sending, and receive extraction.

## Important APIs, Types, And Functions
Exports `afs_async_calls`, `afs_open_socket()`, `afs_close_socket()`, `afs_charge_preallocation()`, `afs_put_call()`, `afs_deferred_put_call()`, `afs_make_call()`, `afs_deliver_to_call()`, `afs_wait_for_call_to_complete()`, `afs_alloc_flat_call()`, `afs_flat_call_destructor()`, `afs_send_empty_reply()`, `afs_send_simple_reply()`, `afs_extract_data()`, and `afs_protocol_error()`. It defines RxRPC kernel callbacks and the initial incoming `CB.xxxx` call type.

## Control Flow
`afs_open_socket()` creates an AF_RXRPC socket, binds AFS and YFS callback services, sets security/response behavior, installs callbacks, listens, and precharges incoming calls. Outgoing calls are allocated, optionally given flat buffers, started with `rxrpc_kernel_begin_call()`, transmit fixed and optional write data, then complete via synchronous waits or async work. Incoming calls use preallocated `afs_call` objects, read the operation ID, route through cache-manager dispatch, and send replies.

## State And Persistence
Tracks `afs_call` refcounts, RxRPC call handles, peer refs, call state transitions, outstanding call counts, spare incoming calls, and workqueue references. No disk persistence; network protocol state lives in RxRPC and remote peers.

## Dependencies And Integration Points
Integrates Linux AF_RXRPC, keyrings/security, callback service (`cmservice.c`), RxGK token setup, tracepoints, workqueues, server lookup by peer, and all RPC client files through `afs_call_type`.

## Risks And Edge Cases
Refcounting is delicate for async calls and notifications under spinlock. Send failures, immediate cancellation, remote abort parsing, unmarshalling errors, incoming preallocation exhaustion, and socket shutdown must not leak calls or leave waiters asleep.

## Test Signals
Mount/fetch/store workloads, callback storms, async fetch cancellation, module/netns teardown with outstanding calls, forced remote aborts, malformed replies, RxRPC security upgrade behavior, and leak/lockdep testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rxrpc.c -->
