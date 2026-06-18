# sources/distributed-fs/ceph-client/net/tipc/topsrv.h

## Purpose
Declares the topology server interface used by subscriptions, kernel topology clients, and TIPC namespace lifecycle code.

## Important APIs, Types, And Constants
The header defines `TIPC_SERVER_NAME_LEN` and topology subscription filter bits for cluster scope, node scope, and no-status behavior. It exposes `tipc_topsrv_queue_evt` for subscription event delivery, `tipc_topsrv_kern_subscr` for creating an in-kernel subscription bound to a local port id, and `tipc_topsrv_kern_unsubscr` for dropping that kernel subscription.

## Control Flow And State
The header does not define state, but the API implies event queueing by connection id and asynchronous delivery by the topology server. Kernel subscribers receive an allocated `conid` that must be passed back to unsubscribe; userspace subscribers are handled through sockets in `topsrv.c`.

## Dependencies And Integration Points
Includes `core.h` for TIPC core and network namespace types. `subscr.h` includes this header to route events, while code outside the topology server can use kernel subscription helpers without seeing `struct tipc_conn`.

## Risks And Test Signals
The major risk is semantic drift in filter bits or event delivery contracts between name table, subscription, and topology server code. Build tests should cover `CONFIG_TIPC` with topology service enabled. Runtime tests should create kernel subscriptions, emit publication events, and verify unsubscribe removes all per-connection subscription state.
