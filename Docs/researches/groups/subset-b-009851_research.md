# Research: subset-b-009851

Grouped research for Samba source3 RPC host, worker, socket, named-pipe, daemon wrapper, and SAMR password-change code. Each section is source-tree aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_host.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_host.c

## Purpose
`rpc_host.c` implements the `samba-dcerpcd` supervisor. It discovers `rpcd_*` helper binaries, asks each helper which DCE/RPC interfaces and endpoint bindings it serves, creates listening sockets for those endpoints, accepts the first client bind PDU, then passes the socket and serialized client metadata to an appropriate helper worker process. It supports normal standalone mode, `--libexec-rpcds` discovery mode, and `--np-helper` mode for on-demand named-pipe service from smbd or winbind.

## Important APIs, Types, And Functions
The central state types are `struct rpc_host`, `struct rpc_server`, `struct rpc_host_endpoint`, `struct rpc_work_process`, and `struct rpc_host_pending_client`. Endpoint discovery is handled by `rpc_server_get_endpoints_send`, `rpc_server_get_endpoints_done`, `rpc_exe_parse_iface_line`, `rpc_host_endpoint_find`, and `rpc_server_setup_send`. Client intake is handled by `rpc_host_endpoint_accept_send`, `rpc_host_endpoint_accept_accepted`, `rpc_host_bind_read_send`, `rpc_host_bind_read_got_npa`, `rpc_host_bind_read_got_bind`, and `rpc_host_endpoint_accept_got_bind`. Worker lifecycle and load balancing are handled by `rpc_host_exec_worker`, `rpc_host_find_worker`, `rpc_host_find_idle_worker`, `rpc_host_distribute_clients`, `rpc_host_child_status_recv`, `rpc_host_exit_worker`, and `rpc_worker_exited`. `main` owns command-line parsing, daemonization, messaging setup, pidfile creation, and the top-level `rpc_host_send` event loop.

## Control Flow
Startup builds a list of server executables from explicit arguments or `dyn_SAMBA_LIBEXECDIR`, opens `epmdb.tdb`, registers messaging handlers, and launches asynchronous setup for every helper. Each setup runs the helper with `--list-interfaces`, parses the first two lines as `num_workers` and `idle_seconds`, parses interface lines plus indented binding lines, creates sockets through `dcesrv_create_binding_sockets`, calls `listen`, and fills the endpoint mapper TDB. Once all helpers are prepared, accept loops are installed for every endpoint. For each accepted socket, the host duplicates the fd to read the initial bind packet without consuming ownership of the fd to be sent to the worker. Named-pipe transports first unwrap named-pipe auth with `tstream_npa_accept_existing_send`; TCP and local RPC synthesize anonymous `named_pipe_auth_req_info8` from peer/local socket addresses. The pending client is queued and distributed to an existing, new, or exclusive idle worker depending on association group id and NPA flags.

## State And Persistence
Persistent on-disk state is the pidfile and `epmdb.tdb` under the Samba lock path; `epmdb.tdb` is opened with `TDB_CLEAR_IF_FIRST`, so it is a runtime registration cache rather than durable configuration. Runtime state tracks endpoints, worker pids, availability, association counts, connection counts, idle timers, pending client sockets, and ready-signal file descriptors through talloc ownership. The host also uses Samba messaging to exchange status, shutdown, ready, and dump-status events with workers and other daemons.

## Dependencies And Integration Points
This file integrates Samba command-line, loadparm, messaging, tevent, talloc, TDB, pidfile, endpoint mapper, generated `ndr_rpc_host`, `named_pipe_auth`, socket helpers, `rpc_worker.c`, and smbd/winbind on-demand named-pipe startup. It depends on helper binaries conforming to `rpc_worker_main` list-output format and on `dcesrv_create_binding_sockets` mutating endpoint bindings when dynamic ports or default local sockets are chosen.

## Risks And Test Signals
High-risk areas are process supervision, fd ownership, association group routing, endpoint parser tolerance, dynamic port allocation, and idle-worker shutdown. Specific risks include treating endpoint-list parse failures as OOM in some paths, relying on helper stdout format, race windows where a worker dies before SIGCHLD while the host is sending a fd, and `np_helper` self-exit behavior depending on accurate worker status. Test signals include `samba-dcerpcd --libexec-rpcds --list` style startup, helper `--list-interfaces` parsing, NCACN_NP/TCP/NCALRPC connection handoff, invalid bind packets, associated binds after worker death, dump-status messaging, ready-signal fd delivery, pidfile contention, and idle worker shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.c

## Purpose
This file provides local named-pipe style RPC client helpers for source3 RPC servers. It creates queue state for named-pipe authentication streams and opens local RPC client connections that dispatch directly to Samba's local named-pipe implementation instead of connecting over a remote network transport.

## Important APIs, Types, And Functions
`struct np_proxy_state` is a private proxy-shape state for pipe metadata and tevent queues. The public `npa_state_init` allocates `struct npa_state` and initializes separate read and write queues. `rpcint_binding_handle` opens a local named-pipe RPC client for a specific NDR interface table and returns its `dcerpc_binding_handle`. `rpc_pipe_open_interface` opens or reuses a `struct rpc_pipe_client` for a given interface table, session info, and remote/local address pair.

## Control Flow
`npa_state_init` is a simple allocation path with cleanup on queue allocation failure. `rpcint_binding_handle` calls `rpc_pipe_open_local_np`, using the provided session and address context, and moves the resulting binding handle out of the `rpc_pipe_client`. `rpc_pipe_open_interface` first checks whether an existing caller-supplied pipe is still connected. If not, it frees it, opens a new local named-pipe client with `rpc_pipe_open_local_np`, stores it back through `cli_pipe`, and reports errors with the interface table name.

## State And Persistence
There is no durable persistence. State is talloc-owned queue and pipe-client state. `rpc_pipe_open_interface` may preserve a live caller-owned `rpc_pipe_client` across calls, so the caller controls connection caching and lifetime.

## Dependencies And Integration Points
The code depends on `rpc_client/cli_pipe.h`, `rpc_dce.h`, `named_pipe_auth`, `auth_session_info`, `tsocket_address`, `rpc_pipes.h`, and `rpc_server.h`. It is the internal bridge used by RPC services that need to call another local RPC interface such as winreg, samr, or netlogon without routing through an external network client.

## Risks And Test Signals
Risks include stale cached clients, address/session mismatches when services reuse `cli_pipe`, and returning `rpccli->binding_handle` while freeing the containing client only on failure. Test signals are local interface open/reopen behavior, disconnected cached pipe replacement, session propagation, and service-to-service RPC calls made from inside worker processes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.h

## Purpose
This header exposes the local named-pipe RPC helper surface used by source3 RPC server code. It declares named-pipe auth stream state and functions for creating local RPC binding handles or pipe clients.

## Important APIs, Types, And Functions
`struct npa_state` stores the backing `tstream_context`, read/write `tevent_queue`s, pipe allocation size, device state, file type, and caller-private data. `npa_state_init` allocates that state. `rpcint_binding_handle` returns a `dcerpc_binding_handle` for an NDR interface. `rpc_pipe_open_interface` returns or refreshes a `struct rpc_pipe_client`.

## Control Flow
The header itself has no runtime flow, but its contracts imply talloc ownership: callers pass a memory context and receive objects owned under that context or the returned pipe client.

## State And Persistence
No persistent state is declared. Runtime state is per-pipe and is intended to be owned by the caller's talloc tree.

## Dependencies And Integration Points
It forward-declares DCE/RPC, NDR, tsocket, and endpoint structures so service code can include it without pulling in full implementation headers. It is paired with `rpc_ncacn_np.c` and integrates with local `rpc_pipe_open_local_np` dispatch.

## Risks And Test Signals
Risk is mostly ownership and incomplete-type coupling. Test signals are compile coverage for callers using only forward declarations, local pipe creation, and teardown of read/write queues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_pipes.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_pipes.h

## Purpose
`rpc_pipes.h` defines source3 compatibility state for DCE/RPC named-pipe handlers and declares policy-handle helpers used by generated RPC server stubs. It is the bridge between older source3 pipe-server code and the common `dcesrv` call model.

## Important APIs, Types, And Functions
`struct pipes_struct` carries the transport, messaging context, current fault code, per-PDU memory context, and `dcesrv_call_state`. Declared helpers include `check_open_pipes`, `num_pipe_handles`, `create_policy_hnd`, `_find_policy_by_hnd`, `find_policy_by_hnd`, `close_policy_hnd`, and `pipe_access_check`. The `DCESRV_COMPAT_NOT_USED_ON_WIRE` macro generates an operation stub that faults with `DCERPC_FAULT_OP_RNG_ERROR`.

## Control Flow
The header has no implementation flow, but generated or hand-written RPC operations receive a `pipes_struct`, use it to access current call state and policy handles, and can set `fault_state` for protocol-level failures.

## State And Persistence
Policy handles and per-call memory are runtime state only. The `mem_ctx` field is explicitly per-PDU and must not be used for long-lived pipe state.

## Dependencies And Integration Points
The header depends on source3 DCE/RPC declarations and is included by `rpc_server.h`, service implementations, and compatibility wrappers. It connects generated server stubs to Samba messaging and dcesrv call state.

## Risks And Test Signals
Risks include using per-PDU memory for persistent state, mismatched policy-handle types, and accidentally exposing compatibility stubs on the wire. Test signals are policy handle create/find/close tests, access-check behavior, and RPC operation fault mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_pipes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_server.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_server.c

## Purpose
This file implements generic source3 DCE/RPC server support shared by embedded and worker-based transports. It prepares GENSEC authentication, logs successful authorization, manages association groups, resolves named-pipe endpoints, and terminates ncacn transport connections.

## Important APIs, Types, And Functions
`dcesrv_auth_gensec_prepare` builds a `gensec_security` context for a call. `dcesrv_log_successful_authz` emits audit events after authorization. `dcesrv_assoc_group_new`, `dcesrv_assoc_group_reference`, and `dcesrv_assoc_group_find` manage association group IDs in `dce_ctx->assoc_groups_idr`. `dcesrv_transport_terminate_connection` and `ncacn_terminate_connection` free the ncacn connection object. `dcesrv_endpoint_by_ncacn_np_name` finds a named-pipe endpoint by pipe name. `dcesrv_get_pipes_struct` extracts the source3 `pipes_struct` from a `dcesrv_connection`.

## Control Flow
During bind handling, dcesrv calls the configured auth callback to prepare GENSEC, then association-group callback to either reference a requested group or allocate a new random ID. On successful authorization, audit logging constructs an auth4 context under root and records remote/local addresses, service, auth type, transport protection, and session info. Named-pipe endpoint lookup iterates the endpoint list, filters to `NCACN_NP`, strips a leading `\pipe\`, and compares names.

## State And Persistence
Association groups are runtime talloc objects registered in an IDR and removed by `dcesrv_assoc_group_destructor`. Audit logging persists through Samba's configured authz log path. No configuration is mutated.

## Dependencies And Integration Points
Dependencies include `dcesrv_core`, `rpc_pipes.h`, `rpc_config.h`, `rpc_dce.h`, generated auth/netlogon NDR headers, tsocket, named-pipe auth, source3 auth, and random ID allocation. Worker mode overrides association-group handling in `rpc_worker.c`, but still reuses auth preparation, authz logging, endpoint lookup, and transport termination.

## Risks And Test Signals
Risks include association group ID exhaustion, transport mismatch on reused groups, audit logging failures under memory pressure, and ambiguous named-pipe names if endpoint strings vary in slash or case normalization. Test signals are bind with new and existing association groups, cross-transport group reuse rejection, successful-authz audit records, named-pipe endpoint lookup with and without `\pipe\`, and connection termination callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_server.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_server.h

## Purpose
`rpc_server.h` declares the common ncacn connection wrapper and shared source3 DCE/RPC server hooks. It is included by worker, socket, named-pipe, and service code that needs transport-private state or common callbacks.

## Important APIs, Types, And Functions
`dcerpc_ncacn_termination_fn` defines termination callbacks. `struct dcerpc_ncacn_conn` links active connections, stores the socket, embedded `pipes_struct`, endpoint, termination callback, client/server names and addresses, and connection timestamp. The header declares fault/PDU helpers, auth callbacks, association group lookup, endpoint lookup, pipe-struct extraction, and transport termination.

## Control Flow
The declarations support bind and packet flow in dcesrv: a transport creates `dcerpc_ncacn_conn`, embeds it as `dcesrv_connection->transport.private_data`, uses callbacks for auth and association groups, and calls termination when the dcesrv connection is freed.

## State And Persistence
All declared state is in-memory connection or association state. No persistent data is owned by this header.

## Dependencies And Integration Points
It depends on common RPC definitions, `dcesrv_core`, `rpc_pipes.h`, and basic time types. It is used by `rpc_worker.c`, `rpc_server.c`, `rpc_sock_helper.c`, and internal service implementations.

## Risks And Test Signals
Risks are ABI and ownership coupling: every transport-private pointer must really be a `dcerpc_ncacn_conn`, and the embedded `pipes_struct` must match expectations of source3 RPC stubs. Test signals are compile coverage, connection create/free cycles, and callback invocation during forced disconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.c

## Purpose
This file creates listening sockets for DCE/RPC endpoint bindings. It supports named-pipe Unix sockets (`NCACN_NP`), local RPC Unix sockets (`NCALRPC`), and TCP sockets (`NCACN_IP_TCP`) for `samba-dcerpcd` endpoint setup.

## Important APIs, Types, And Functions
`dcesrv_create_ncacn_np_socket` normalizes `\pipe\` endpoints, creates the ncalrpc and `np` directories with appropriate modes, and creates the pipe socket. `dcesrv_create_ncacn_ip_tcp_socket` opens and configures a single TCP socket. `dcesrv_create_ncacn_ip_tcp_sockets` chooses explicit or dynamic ports and binds either configured interfaces or wildcard IPv4/IPv6 addresses. `dcesrv_create_ncalrpc_socket` creates local RPC sockets with role-specific defaults. Public `dcesrv_create_binding_sockets` dispatches by transport and marks returned fds close-on-exec.

## Control Flow
For named pipes and local RPC, endpoint strings are required or defaulted, directories are created, and a single Unix socket fd is returned. For TCP, the helper decides how many addresses to bind, chooses an explicit endpoint port when configured or scans `rpc low port` through `rpc high port`, attempts to bind the same port on every address, closes partial successes on conflict, and writes the selected port back into the binding endpoint string. The top-level dispatcher closes all fds and frees state on any close-on-exec failure.

## State And Persistence
Runtime fds are returned to the caller. Filesystem state includes created socket directories and socket path entries under `lp_ncalrpc_dir()`. Static `next_low_port` and `conf_high_port` persist within the process to spread dynamic TCP port choices.

## Dependencies And Integration Points
It depends on Samba socket helpers, interface enumeration, loadparm network settings, endpoint bindings, `create_pipe_sock`, and `dcesrv_core`. `rpc_host.c` calls this during endpoint setup before calling `listen`.

## Risks And Test Signals
Risks include permissions on `lp_ncalrpc_dir()/np`, stale Unix socket paths, dynamic port exhaustion, IPv4/IPv6 partial bind cleanup, and endpoint mutation being visible to endpoint mapper registration. Test signals are named-pipe socket creation with mixed-case and `\pipe\` prefixes, NCALRPC default endpoint on AD DC vs non-DC roles, TCP explicit and dynamic port binding, bind-interfaces-only behavior, and close-on-exec failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.h

## Purpose
This header exposes the socket creation helper used by the RPC host to turn a DCE/RPC binding into one or more listening file descriptors.

## Important APIs, Types, And Functions
It includes `rpc_server.h` and declares `dcesrv_create_binding_sockets(struct dcerpc_binding *b, TALLOC_CTX *mem_ctx, size_t *pnum_fds, int **fds)`.

## Control Flow
The header has no runtime flow. Its function contract returns a talloc-owned fd array and count, with the binding potentially updated by the implementation for dynamic endpoint selection.

## State And Persistence
No state is declared. Callers own returned fds and must close them when endpoint state is destroyed.

## Dependencies And Integration Points
The declaration is consumed by `rpc_host.c` during server setup and implemented by `rpc_sock_helper.c`.

## Risks And Test Signals
Risks are caller assumptions about single-fd endpoints and missing awareness that TCP can return multiple fds. Test signals are compile coverage and endpoint setup tests for all supported transports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_worker.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_worker.c

## Purpose
`rpc_worker.c` is the generic runtime used by every `rpcd_*` helper. It implements two modes: `--list-interfaces`, which prints worker limits and served endpoint bindings for `samba-dcerpcd`, and worker mode, which registers endpoint servers, receives client sockets from the host, and runs DCE/RPC packet processing.

## Important APIs, Types, And Functions
`struct rpc_worker` stores active ncacn connections, host pid, messaging context, dcesrv context, callbacks, status counters, completion state, and connection timestamps. Public `rpc_worker_main` is the entry point used by concrete daemons. Interface listing uses `rpc_worker_print_interface`. Host status is sent through `rpc_worker_report_status`. Client handoff is processed by `rpc_worker_new_client_filter` and `rpc_worker_new_client`. Connection teardown uses `rpc_worker_connection_terminated` and `dcesrv_connection_destructor`. Worker-local association group IDs are managed by `rpc_worker_assoc_group_new`, `rpc_worker_assoc_group_reference`, and `rpc_worker_assoc_group_find`. The async shell is `rpc_worker_send`, `rpc_worker_done`, `rpc_worker_shutdown`, and `rpc_worker_recv`.

## Control Flow
`rpc_worker_main` parses common options. In list mode it reads optional loadparm overrides for `num_workers` and `idle_seconds`, prints them, then prints each NDR interface syntax and endpoint list. In worker mode it initializes logging, smbd shim callbacks, signals, guest/system sessions, messaging, dcesrv context callbacks, and endpoint server implementations returned by the concrete daemon. It then registers each endpoint server and enters a tevent loop. New-client messages carry one fd plus an NDR-encoded `rpc_host_client`. The worker parses the binding, resolves the endpoint, rebuilds remote and local tsocket addresses from named-pipe auth data, wraps the socket in an NPA or BSD tstream, enforces that system tokens are only accepted over NCALRPC, connects to the endpoint, parses the already-read bind packet, adds the connection to the active list, updates counters, and calls `dcesrv_loop_next_packet`.

## State And Persistence
State is per-process and in-memory: active connection list, association group IDR through the global dcesrv context, connection counters, status messages, and timestamps. No durable files are written by this generic layer except logs and core/debug outputs configured by Samba. Association group IDs encode worker index in the high 16 bits and a worker-local random ID in the low 16 bits, matching host routing logic.

## Dependencies And Integration Points
It depends on command-line helpers, Samba messaging, tevent, talloc, dcesrv core, generated `ndr_rpc_host`, named-pipe auth, smbd shims, winbind toggling, source3 auth, security tokens, endpoint server registration, and concrete daemon callbacks for interfaces and endpoint servers. It is tightly coupled to `rpc_host.c` message types `MSG_RPC_HOST_NEW_CLIENT`, `MSG_RPC_WORKER_STATUS`, `MSG_RPC_WORKER_INFO`, `MSG_RPC_DUMP_STATUS`, and `MSG_SHUTDOWN`.

## Risks And Test Signals
Risks include fd/message ownership, accepting malformed serialized clients, mismatched endpoint strings after dynamic port assignment, transport/auth mismatches, system-token restrictions, association group leaks or counter drift, and duplicate assignment to `state->new_client_req` for different filtered reads. Test signals are helper `--list-interfaces` output, host-to-worker socket fd transfer, TCP and named-pipe binds, associated binds routed to the correct worker index, invalid worker indexes, `MSG_RPC_WORKER_INFO` and dump-status output, SIGHUP config reload, shutdown behavior, and counter updates after connection termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_worker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_worker.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_worker.h

## Purpose
This header declares the generic `rpc_worker_main` entry point used by all source3 `rpcd_*` daemon wrappers.

## Important APIs, Types, And Functions
`rpc_worker_main` accepts argv, a daemon config name, default worker count and idle timeout, a `get_interfaces` callback returning NDR interface tables, a `get_servers` callback returning endpoint server implementations, and caller-private data.

## Control Flow
Concrete daemons implement two callbacks and return `rpc_worker_main(...)` from `main`. The generic worker owns option parsing, list mode, service initialization, messaging, endpoint registration, and event loop execution.

## State And Persistence
No state is declared by the header. Runtime state is allocated inside `rpc_worker.c` based on the provided callbacks.

## Dependencies And Integration Points
It includes `replace.h` and `dcesrv_core` so callers can name NDR interface and endpoint server types. It is included by every `rpcd_*.c` wrapper in this group.

## Risks And Test Signals
Risks are callback contract drift and mismatched daemon config names. Test signals are compile coverage for each daemon wrapper and `--list-interfaces` output matching `samba-dcerpcd` parser expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_classic.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_classic.c

## Purpose
`rpcd_classic.c` defines a worker daemon for traditional source3 administrative RPC interfaces: SRVSVC, DFS, INITSHUTDOWN, SVCCTL, NTSVCS, EVENTLOG, and WKSSVC.

## Important APIs, Types, And Functions
`classic_interfaces` returns the NDR tables. `classic_servers` builds the matching endpoint server array with `*_get_ep_server` calls, initializes secrets, locking, share info, share-loaded configuration, mangle cache, and default machine-principal auth types. `main` runs `rpc_worker_main` with daemon config name `rpcd_classic`, five default workers, and 60 second idle timeout.

## Control Flow
List mode only reports the static interface list through `classic_interfaces`. Service mode performs required source3 state initialization before returning endpoint servers for registration by `rpc_worker.c`.

## State And Persistence
State initialized here includes secrets database access, locking database state, share info database state, loaded shares, and mangle cache. Persistent updates are delegated to those subsystems, not directly written here.

## Dependencies And Integration Points
It depends on generated NDR server compatibility headers, source3 secrets, share-mode locking, and smbd share/mangle helpers. It integrates with the generic worker and source3 administrative endpoint implementations.

## Risks And Test Signals
Risks include initialization order, failure paths that call `exit(1)` inside the callback, and stale share configuration without reload. Test signals are `rpcd_classic --list-interfaces`, startup with secrets/locking/share db available, and RPC smoke tests for srvsvc, dfs, svcctl, eventlog, and wkssvc.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_classic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_epmapper.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_epmapper.c

## Purpose
This daemon wrapper exposes the endpoint mapper service outside AD DC mode. It lets `samba-dcerpcd` provide epmapper as a small single-worker service.

## Important APIs, Types, And Functions
`epmapper_interfaces` returns `ndr_table_epmapper` except on AD DC, where source4 `samba` provides it. `epmapper_servers` registers supported default auth types with an empty principal, supplies `epmapper_get_ep_server`, and similarly disables the server list on AD DC. `main` runs one worker with a 10 second idle timeout.

## Control Flow
Both list and service callbacks branch on `lp_server_role`. Non-AD DC roles advertise and register epmapper; AD DC advertises zero interfaces and zero endpoint servers.

## State And Persistence
No direct persistent state is owned here. Auth type registrations modify the runtime dcesrv context.

## Dependencies And Integration Points
Dependencies include generated epmapper NDR, loadparm, role constants, and `rpc_worker_main`. The host uses its advertised bindings to populate `epmdb.tdb`.

## Risks And Test Signals
Risks include role mismatch between list and service mode, and auth type registration that diverges from what clients expect. Test signals are role-specific `--list-interfaces`, endpoint lookup through epmapper on fileserver/member roles, and absence of this service on AD DC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_epmapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_fsrvp.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_fsrvp.c

## Purpose
`rpcd_fsrvp.c` wraps the File Server VSS Agent RPC service. It advertises and registers FSRVP only when Samba is not running as an Active Directory DC.

## Important APIs, Types, And Functions
`fsrvp_interfaces` returns `ndr_table_FileServerVssAgent` or zero interfaces on AD DC. `fsrvp_servers` loads shares, returns `FileServerVssAgent_get_ep_server`, or returns an empty server list on AD DC. `main` uses `rpc_worker_main` with five workers and a 60 second idle timeout.

## Control Flow
The callbacks mirror each other: AD DC role short-circuits to no interfaces/servers; other roles load share configuration and register the FSRVP endpoint.

## State And Persistence
The file directly loads share configuration. Any snapshot or VSS state is handled by the endpoint server implementation, not this wrapper.

## Dependencies And Integration Points
It depends on generated FSRVP NDR compatibility and loadparm role/share APIs. It integrates with `rpc_worker.c` and the FSRVP endpoint implementation.

## Risks And Test Signals
Risks include role-gating divergence and share configuration assumptions for snapshot paths. Test signals are `--list-interfaces` in AD DC and file-server roles, startup after share reload, and FSRVP RPC calls against a configured file server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_fsrvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_lsad.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_lsad.c

## Purpose
This daemon wrapper provides LSA, SAMR, DSSETUP, and conditionally NETLOGON through source3. It adapts the advertised interfaces and endpoint servers to Samba server role.

## Important APIs, Types, And Functions
`lsad_interfaces` returns LSARPC, SAMR, DSSETUP, and maybe NETLOGON. Standalone and member roles drop NETLOGON, while AD DC returns no interfaces because source4 provides these services. `lsad_servers` builds matching endpoint servers, initializes secrets, registers default machine-principal auth types, and for classic DC roles registers schannel with an empty principal. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List and service callbacks apply the same role logic. Service initialization occurs before role-specific server count adjustment so secrets and auth registration are available for source3 roles.

## State And Persistence
The wrapper initializes secrets access and runtime auth registrations. Persistent account, SAM, LSA, and netlogon state is owned by endpoint implementations and passdb/secrets.

## Dependencies And Integration Points
It depends on generated NDR compatibility for LSA, SAMR, NETLOGON, DSSETUP, source3 auth, and secrets. It is a major provider for authentication and account-management RPC in non-AD-DC source3 deployments.

## Risks And Test Signals
Risks include incorrect role gating, schannel principal registration, and source4/source3 service overlap on AD DC. Test signals are role-specific interface listing, SAMR password operations, LSA policy calls, netlogon availability only for classic DC roles, and auth type negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_lsad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_mdssvc.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_mdssvc.c

## Purpose
`rpcd_mdssvc.c` wraps the Spotlight metadata service RPC endpoint for source3.

## Important APIs, Types, And Functions
`mdssvc_interfaces` returns `ndr_table_mdssvc`. `mdssvc_servers` loads shares, initializes POSIX locking with `posix_locking_init(false)`, resets the mangle cache, and returns `mdssvc_get_ep_server`. `main` runs through `rpc_worker_main` with five workers and 60 second idle timeout.

## Control Flow
List mode reports the metadata interface. Worker mode initializes filesystem/share support before endpoint server registration.

## State And Persistence
The wrapper initializes share configuration, POSIX locking runtime state, and mangle cache. Metadata indexes or search state are not managed here.

## Dependencies And Integration Points
It depends on source3 locking and smbd helper prototypes plus generated MDSSVC NDR compatibility. It integrates with the metadata endpoint implementation and Samba share configuration.

## Risks And Test Signals
Risks include startup failure if POSIX locking cannot initialize and stale share state. Test signals are interface listing, startup with shares loaded, and Spotlight/MDSSVC RPC calls against shares.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_mdssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_rpcecho.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_rpcecho.c

## Purpose
This daemon wrapper exposes the test/diagnostic RPCECHO interface outside AD DC mode.

## Important APIs, Types, And Functions
`rpcecho_interfaces` returns `ndr_table_rpcecho` unless the role is AD DC. `rpcecho_servers` returns `rpcecho_get_ep_server` unless AD DC. `main` uses one worker and a one second idle timeout through `rpc_worker_main`.

## Control Flow
The wrapper mirrors source4 ownership rules for AD DC. In non-AD DC roles it advertises and registers the echo endpoint; on AD DC it reports no interfaces or servers.

## State And Persistence
No persistent state is owned. The service is mainly diagnostic and keeps only worker runtime state.

## Dependencies And Integration Points
It depends on generated echo NDR compatibility, loadparm role detection, and `rpc_worker_main`.

## Risks And Test Signals
Risks are low but include accidental exposure in AD DC mode and idle timeout churn during tests. Test signals are role-specific `--list-interfaces`, basic echo RPC calls, and worker idle shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_rpcecho.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_spoolss.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_spoolss.c

## Purpose
`rpcd_spoolss.c` wraps the print spooler RPC service. It conditionally advertises SPOOLSS based on `disable spoolss` and initializes printing subsystems before registering the endpoint server.

## Important APIs, Types, And Functions
`spoolss_interfaces` returns `ndr_table_spoolss` unless `lp_disable_spoolss()` is true. `spoolss_servers` initializes secrets, locking, share configuration, printing subsystem state with the global messaging and tevent contexts, resets the mangle cache, and returns `spoolss_get_ep_server`. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List mode hides the interface when spoolss is disabled. Service mode initializes secrets/locking/shares/printing and returns a single endpoint server.

## State And Persistence
This wrapper initializes secrets access, locking state, print queue processing, share configuration, and mangle cache. Print queue persistence is handled by the printing subsystem.

## Dependencies And Integration Points
It depends on generated SPOOLSS NDR, global contexts, share-mode locking, printing queue processing, Samba messaging, secrets, and smbd helpers.

## Risks And Test Signals
Risks include advertising inconsistency when spoolss is disabled after host discovery, printing subsystem initialization failures, and locking dependencies. Test signals are `disable spoolss` interface listing, printer enumeration/open calls, print queue event handling, and startup failure behavior when secrets or locking are unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_winreg.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_winreg.c

## Purpose
This daemon wrapper exposes the Windows registry RPC service for source3.

## Important APIs, Types, And Functions
`winreg_interfaces` returns `ndr_table_winreg`. `winreg_servers` returns `winreg_get_ep_server`, initializes the full registry stack with `registry_init_full`, loads share configuration, and returns one endpoint server. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List mode always advertises winreg. Worker mode initializes registry state before endpoint registration and translates registry initialization errors from `WERROR` to `NTSTATUS`.

## State And Persistence
Registry initialization may open or prepare persistent registry databases. The wrapper itself only triggers initialization and share-load side effects.

## Dependencies And Integration Points
It depends on generated winreg NDR compatibility, the source3 registry initialization layer, loadparm shares, and `rpc_worker_main`. Many other RPC services may make local winreg calls, so availability affects broader RPC behavior.

## Risks And Test Signals
Risks include registry database initialization failure and service-to-service dependency failures when winreg is not available. Test signals are `--list-interfaces`, registry open/query/set RPCs, startup with corrupt/missing registry backend, and local winreg calls from other workers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_winreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_witness.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpcd_witness.c

## Purpose
`rpcd_witness.c` wraps the SMB witness RPC service used for clustered deployments. It only advertises and registers the witness endpoint when clustering is enabled.

## Important APIs, Types, And Functions
`witness_interfaces` returns `ndr_table_witness` when `lp_clustering()` is true. `witness_servers` registers NTLMSSP and SPNEGO principals of the form `cifs/<netbios name>`, optionally registers KRB5 in ADS security mode, sets the dcesrv preferred transfer syntax to NDR64, and returns `witness_get_ep_server`. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List and service callbacks short-circuit to empty results when clustering is disabled. With clustering enabled, service setup performs auth-principal registration, chooses NDR64 preference, and returns one endpoint server.

## State And Persistence
The wrapper mutates runtime dcesrv auth registrations and preferred transfer syntax. Cluster state and witness registrations are handled by the endpoint implementation.

## Dependencies And Integration Points
It depends on generated witness NDR compatibility, clustering and security loadparm settings, NetBIOS name, and dcesrv auth registration. It integrates with SMB clustered failover client notification flows.

## Risks And Test Signals
Risks include principal construction mismatch, missing KRB5 registration in ADS deployments, and NDR64 negotiation assumptions. Test signals are clustering on/off interface listing, auth negotiation for NTLMSSP/SPNEGO/KRB5, NDR64 bind preference, and witness subscription calls in clustered test environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpcd_witness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_chgpasswd.c -->
# sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_chgpasswd.c

## Purpose
This file implements SAMR password-change support for source3. It covers Unix password synchronization through a configurable password program and chat script, validation of legacy OEM/NTLM encrypted password-change buffers, password policy checks, password history checks, lockout and bad-password accounting, passdb updates, and AES encrypted password decoding for newer SAMR password-set flows.

## Important APIs, Types, And Functions
When `ALLOW_CHANGE_PASSWORD` is enabled, `findpty`, `dochild`, `expect`, `pwd_sub`, `talktochild`, and `chat_with_program` implement the pseudo-terminal conversation with the configured password program. Public `chgpasswd` drives PAM or non-PAM Unix password sync. `check_oem_password` decrypts the 516 byte legacy password buffers with RC4 using old NT or LM hashes, decodes the new password, and verifies old-password encrypted verifiers. `password_in_history` and `check_passwd_history` enforce password reuse restrictions. `check_password_complexity_internal` safely expands `%u` for `check password script`, including CVE-2026-4408 hardening warnings, while `check_password_complexity` sets environment variables and calls `smbrunsecret`. `change_oem_password` applies policy checks and writes the new passdb password. `pass_oem_change` coordinates account lookup, lockout checks, mutex-protected reload, login-attempt accounting, and password update. `samr_set_password_aes` decrypts AES-256-CBC-HMAC-SHA512 encrypted SAMR password buffers and returns a secret talloc string.

## Control Flow
Legacy password change starts in `pass_oem_change`: load the `samu` record as root, reject missing or locked accounts, verify the encrypted old/new password material with `check_oem_password`, then reload the account under a named mutex to avoid racing lockout changes. The backend is notified of login success or failure, bad-password counters are updated as needed, and only after successful verification does `change_oem_password` run under root. `change_oem_password` checks account permission, machine-password policy, minimum change time, minimum length, history, local Unix account presence, optional external complexity script, optional Unix password sync, then calls `pdb_set_plaintext_passwd` and `pdb_update_sam_account`. AES password-set flow is narrower: decrypt authenticated ciphertext with the current derived key, decode the UTF-16 password buffer, and return the plaintext as talloc secret memory.

## State And Persistence
Persistent state changes include Unix password database changes when `unix password sync` and PAM or `passwd program` are enabled, passdb password hash updates, bad password counters, bad password timestamps, login-attempt backend state, and account policy effects. Runtime sensitive state includes plaintext old/new passwords, encrypted buffers, hashes, pty fds, child process status, named mutexes, and environment variables for the password complexity script. The code uses `BURN_STR` for the legacy new password after use and `talloc_keep_secret` for AES-decoded passwords.

## Dependencies And Integration Points
Dependencies include passdb, source3 auth, account policies, PAM password change when compiled, configurable `passwd program`, `passwd chat`, `check password script`, GnuTLS RC4/MD5/AES helpers, SAMR protocol NDR helpers, pty/terminal APIs, named mutexes, and Samba privilege transitions. It is used by SAMR endpoint operations in the LSA/SAMR daemon path.

## Risks And Test Signals
This is security-sensitive code. Risks include shell interaction with password scripts, pty timeout behavior, locale and PAM side effects, RC4/LM legacy compatibility, FIPS mode transitions around RC4, username substitution safety for external complexity scripts, race conditions around account lockout, plaintext password lifetime, and incomplete cleanup if child password-program interaction fails. Test signals include NTLM disabled rejection, LM disabled behavior, null-password accounts, wrong old password and lockout counter updates, locked account rejection before and after mutex reload, password-too-short and history rejection reasons, `check password script` with unsafe usernames and environment variables, Unix password sync success/failure, AES decrypt failure, AES UTF-16 decode failure, and successful passdb update with bad-password count reset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_chgpasswd.c -->
