# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.c

Purpose: manages RPC client connections from glusterd to managed service daemons, including initialization, start/disable, socket path generation, and notification dispatch under appropriate locks.

Important APIs/types/functions: `glusterd_conn_init()` builds Unix transport options, creates `rpc_clnt`, registers `glusterd_conn_common_notify()`, stores socket path, and records the service-specific notify callback. `glusterd_conn_term()`, `glusterd_conn_connect()`, and `glusterd_conn_disconnect()` wrap RPC lifecycle. `glusterd_conn_build_socket_filepath()` maps rundir and UUID to a socket path. Notification functions include `__glusterd_conn_common_notify()`, `glusterd_conn_common_notify()`, `__glusterd_muxsvc_conn_common_notify()`, and `glusterd_muxsvc_conn_common_notify()`.

Control flow: service initialization calls `glusterd_conn_init()`, which derives the owning service object, creates an RPC client named after the service, and registers a notify trampoline. Regular notifications are routed through `glusterd_big_locked_notify()` then to `conn->notify`. Multiplexed service notifications free `glusterd_svc_proc_t` and unref volume data on `RPC_CLNT_DESTROY`; other events run under `conf->attach_lock`.

State and persistence behavior: `glusterd_conn_t` stores the `rpc_clnt *`, service notify callback, and socket path. This is volatile runtime state. No persistent files are written, though socket paths point to runtime sockets.

Dependencies and integration points: depends on RPC client APIs, transport option builders, dict APIs, glusterd global locking, service helper, attach-lock state, and socket path utilities. Used by service managers such as BitD.

Risks and edge cases: `options` ownership is transferred to rpc transport but also unrefed locally; correctness depends on RPC API ref semantics. `glusterd_conn_term()` assumes `conn->rpc` is non-null. Notification callbacks silently ignore null connection/proc data. Multiplex destroy deliberately avoids locks to prevent deadlock, so lifetime ordering is critical.

Test signals: connection init failure injection at dict/transport/rpc/register stages, connect/disconnect, notify delivery under big lock, mux destroy freeing volume refs, socket filepath length handling, and repeated term/init cycles.
