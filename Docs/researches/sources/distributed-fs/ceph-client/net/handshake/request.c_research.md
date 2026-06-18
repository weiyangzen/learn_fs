<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/request.c -->
# sources/distributed-fs/ceph-client/net/handshake/request.c

## Purpose
Owns handshake request allocation, socket association, pending-list management, hash lookup, completion, cancellation, and destruction.

## APIs, Types, and Functions
Defines the global rhashtable `handshake_rhashtbl` and exports or exposes for KUnit `handshake_req_hash_init()`, `handshake_req_hash_destroy()`, `handshake_req_hash_lookup()`, `handshake_req_alloc()`, `handshake_req_private()`, `handshake_req_next()`, `handshake_req_submit()`, `handshake_complete()`, and `handshake_req_cancel()`. Internal helpers include `handshake_req_hash_add()`, `handshake_req_destroy()`, `handshake_sk_destruct()`, `remove_pending()`, and pending-list add/remove helpers.

## Control Flow, State, and Persistence
Allocation validates protocol class and callbacks, then allocates a flex-array request. Submit validates socket and file, binds the request to `sock->sk`, replaces `sk_destruct` with `handshake_sk_destruct`, checks per-net availability and pending cap, atomically inserts into the socket-keyed rhashtable and pending list, notifies userspace, and holds the socket until completion/cancel. If notification fails after removal from pending, the request is destroyed and destructor restored. ACCEPT removes requests from pending via `handshake_req_next()`. Completion uses `test_and_set_bit(HANDSHAKE_F_REQ_COMPLETED)` to guarantee one `hp_done()` callback and one `sock_put()`. Cancellation races with completion, removes unaccepted requests when possible, marks completion, and releases the socket. Actual memory is freed from socket destruction through the installed destructor, which removes the request from the rhashtable, calls optional protocol destroy, then chains the original destructor.

## Dependencies and Integration
Depends on rhashtable, per-net handshake state, socket lifetime rules, spinlocks, RCU/list usage, protocol callbacks, and generic-netlink notification from `netlink.c`.

## Risks and Test Signals
Risks include replacing `sk_destruct` before all failure paths are known, hash/list consistency under races, callback double-invocation, pending counter imbalance, and request memory surviving until socket close even after completion. Test signals include invalid submit inputs, duplicate submit `-EBUSY`, pending cap `-EAGAIN`, lookup by socket, accept ordering by class, cancellation before and after accept, completion/cancel race behavior, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/request.c -->
