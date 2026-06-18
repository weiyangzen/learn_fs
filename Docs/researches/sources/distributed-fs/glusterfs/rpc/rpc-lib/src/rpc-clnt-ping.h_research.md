## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-clnt-ping.h

Purpose: declares the client ping API used by `rpc-clnt.c` and other RPC client code.

Important APIs: defines `RPC_DEFAULT_PING_TIMEOUT 30`, forward-declares `struct rpc_clnt`, and declares `rpc_clnt_check_and_start_ping` plus `rpc_clnt_remove_ping_timer_locked`.

Control flow: no implementation. The function names document locking expectations: removal is for callers already holding the connection lock, while check/start is an external helper.

State and persistence: no state. The declared functions manipulate `rpc_clnt_connection_t` ping timer state in the implementation file.

Dependencies and integration: included by `rpc-clnt.c` and `rpc-clnt-ping.c`. It keeps ping internals mostly separate while exposing the cleanup hook needed when disabling or cleaning up connections.

Risks: callers must respect the lock contract for `rpc_clnt_remove_ping_timer_locked`; using it without `conn->lock` can race timers and cleanup.

Test signals: compile-time inclusion and runtime ping behavior tests from `rpc-clnt-ping.c`.
