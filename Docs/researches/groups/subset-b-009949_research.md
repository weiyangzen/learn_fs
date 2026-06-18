# Research: subset-b-009949

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c -->
# sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c

## Purpose

`rpc_winreg.c` implements the Samba AD DC `winreg` DCE/RPC endpoint. It maps generated `winreg` RPC operations onto Samba's registry library, exposing predefined hives, key/value enumeration, basic key/value mutation, and a version query over the `dcerpc_server` handle model.

## Important APIs, Types, and Functions

The file uses `enum handle_types` to distinguish registry key handles from unused value handles. `dcesrv_winreg_openhive()` opens the Samba registry with the caller's `auth_session_info` and returns a `dcesrv_handle` wrapping a predefined key. The `func_winreg_OpenHive()` macro creates handlers for HKCR, HKCU, HKLM, HKPD, HKU, HKCC, HKDD, HKPT, and HKPN. Core handlers include `dcesrv_winreg_CreateKey()`, `DeleteKey()`, `DeleteValue()`, `EnumKey()`, `EnumValue()`, `OpenKey()`, `QueryInfoKey()`, `QueryValue()`, `SetValue()`, and `GetVersion()`.

## Control Flow

Generated NDR server glue included from `ndr_winreg_s.c` dispatches each RPC to the matching static handler. Open-hive and open-key paths create or reference `dcesrv_handle` objects; later calls recover them with `DCESRV_PULL_HANDLE_FAULT`. Read paths query registry backends and populate RPC output buffers with UTF-16 byte counts. Write paths first check `security_session_user_level()` and only allow `SECURITY_SYSTEM` or `SECURITY_ADMINISTRATOR` for create, delete, flush, and set operations. Many advanced operations return `WERR_NOT_SUPPORTED`.

## State and Persistence Behavior

Per-client registry handles live under the DCE/RPC call or connection talloc context until closed or unlinked. Persistent mutations are delegated to registry functions such as `reg_key_add_name()`, `reg_key_del()`, `reg_del_value()`, `reg_val_set()`, and `reg_key_flush()`. The endpoint itself stores no global registry state.

## Dependencies and Integration Points

It depends on `rpc_server/dcerpc_server.h`, `lib/registry/registry.h`, generated `ndr_winreg` and security descriptor parsers, and session-security helpers. Build integration is through the `dcerpc_winreg` module in `source4/rpc_server/wscript_build`.

## Risks and Edge Cases

The implementation is intentionally incomplete: security descriptor get/set, load/save/restore, notifications, shutdown, multiple-value queries, and extended delete are unsupported. Buffer-size checks are hand-coded around UTF-16 length units, so off-by-one behavior is important for Windows compatibility. `DeleteKey()` unlinks the input handle after deletion, which can surprise callers expecting parent-handle survival. Access checks are broad user-level checks rather than per-key ACL enforcement in this layer.

## Test Signals

Useful tests include RPC open-hive/open-key/read-only calls as normal users, create/set/delete as administrators, enumeration with undersized buffers expecting `WERR_MORE_DATA`, default-value queries, unsupported-operation status checks, and registry persistence checks through a second client connection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/wscript_build -->
# sources/user-network-fs/samba/source4/rpc_server/wscript_build

## Purpose

This waf build fragment declares Samba source4 DCE/RPC server libraries, subsystems, endpoint modules, service integration, and a DNS utility selftest binary.

## Important APIs, Types, and Functions

The script uses waf helper declarations such as `bld.SAMBA_SUBSYSTEM`, `bld.SAMBA_LIBRARY`, `bld.SAMBA_MODULE`, and `bld.SAMBA_BINARY`. It defines `DCERPC_SHARE`, `DCERPC_COMMON`, the public `dcerpc_server` library, endpoint modules including `dcerpc_epmapper`, `dcerpc_remote`, `dcerpc_srvsvc`, `dcesrv_samr`, `dcerpc_winreg`, `dcerpc_netlogon`, `dcerpc_lsarpc`, `dcerpc_backupkey`, `dcerpc_drsuapi`, `dcerpc_browser`, `dcerpc_eventlog`, `dcerpc_dnsserver`, and the `service_dcerpc` service module.

## Control Flow

At configure/build time, waf evaluates the declarations and emits targets subject to feature gates such as `AD_DC_BUILD_IS_ENABLED()`, `WITH_NTVFS_FILESERVER`, and `ENABLE_SELFTEST`. Module entries bind C sources to subsystem names and init functions so Samba module loading can register endpoint servers.

## State and Persistence Behavior

No runtime state is stored here. The persistent outputs are build artifacts, generated prototype headers such as `dcerpc_server_proto.h` and `samr/proto.h`, pkg-config metadata, installed binaries/libraries, and module objects.

## Dependencies and Integration Points

The file is a central integration point between endpoint C implementations, generated NDR libraries, Samba authentication/security/DSDB libraries, and the source4 service framework. `dcerpc_winreg` specifically links `winreg/rpc_winreg.c` with `registry` and `ndr-standard`.

## Risks and Edge Cases

Incorrect `enabled` gates can silently remove endpoints from an AD DC build. Dependency omissions tend to surface late as link errors or module-load failures. Internal versus external module choices affect static module registration and runtime module availability.

## Test Signals

Build tests should validate AD DC and non-AD configurations, `WITH_NTVFS_FILESERVER` toggles, selftest-enabled `dcerpc_rpcecho`, and endpoint startup through the `service_dcerpc` module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.c -->
# sources/user-network-fs/samba/source4/samba/process_model.c

## Purpose

`process_model.c` manages registration and lookup of Samba source4 process models. Process models decide how server services create tasks, accept stream connections, terminate work, and set process titles.

## Important APIs, Types, and Functions

The private `struct process_model` stores a `const struct model_ops *` plus an `initialised` flag. `register_process_model()` appends a model after duplicate-name checks. `process_model_startup()` locates a model by name, runs its `model_init()` once, and returns its ops. `process_model_init()` loads static and shared modules in the `process_model` class. `process_model_version()` returns `PROCESS_MODEL_VERSION` and `sizeof(struct model_ops)` for module ABI checks.

## Control Flow

`server.c` calls `process_model_init()` during daemon startup, which runs static and shared process-model init functions. Later, `server_service_startup()` calls `process_model_startup(model)`. The selected model's ops are passed into task and stream service startup.

## State and Persistence Behavior

The registered model table is process-global talloc memory. Each model is initialized at most once per process. No persistent disk state is written.

## Dependencies and Integration Points

It depends on `samba/process_model.h`, loadparm context, and Samba module-loading helpers. Static modules come from build-generated `STATIC_process_model_MODULES`.

## Risks and Edge Cases

Unknown model names call `exit(-1)`, so configuration mistakes abort startup. The registry is global and not synchronized; initialization is expected during single-threaded startup. Duplicate registration returns `NT_STATUS_OBJECT_NAME_COLLISION`.

## Test Signals

Tests should verify all built-in models register, duplicate registration fails, shared modules load, unknown model startup exits or is caught by integration tests, and selected `model_init()` is called only once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.h -->
# sources/user-network-fs/samba/source4/samba/process_model.h

## Purpose

This header defines the process-model ABI used by Samba source4 services and loadable process-model modules.

## Important APIs, Types, and Functions

`struct model_ops` contains the model name plus callbacks for `model_init`, `accept_connection`, `new_task`, `terminate_task`, `terminate_connection`, and `set_title`. `struct process_model_critical_sizes` exposes ABI version and structure size. Public declarations include `process_model_startup()`, `register_process_model()`, `process_model_init()`, and `extern const struct model_ops single_ops`.

## Control Flow

There is no runtime flow in the header. It defines the callback contract used by `service.c`, `service_task.c`, `service_stream.c`, and the `single`, `standard`, and `prefork` implementations.

## State and Persistence Behavior

The header itself stores no state. Implementations receive opaque `process_context` values to preserve model-specific state across task, connection, and termination callbacks.

## Dependencies and Integration Points

It includes socket, service, and generated process-model prototype headers. The ABI version is used by module compatibility checks and should be bumped when callback signatures or critical semantics change.

## Risks and Edge Cases

Every model must obey ownership and event-loop expectations implied by the callback signatures. A mismatch in `process_context` type or callback lifetime can crash service code. ABI changes without `PROCESS_MODEL_VERSION` changes can break external modules.

## Test Signals

Compile coverage across all process models is the primary signal. Runtime smoke tests should start services under `single`, `standard`, and `prefork` models and exercise stream accept and task shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_prefork.c -->
# sources/user-network-fs/samba/source4/samba/process_prefork.c

## Purpose

`process_prefork.c` implements the default source4 prefork process model: a top-level service master forks per-service prefork masters, which fork and supervise reusable worker processes.

## Important APIs, Types, and Functions

`prefork_ops` implements `model_ops`. Restart state is captured by `struct restart_context`, `master_restart_context`, and `worker_restart_context`. Key functions are `prefork_fork_master()`, `prefork_fork_worker()`, `prefork_child_pipe_handler()`, `prefork_restart()`, `prefork_restart_fn()`, `prefork_accept_connection()`, `prefork_new_task()`, `prefork_pipe_handler()`, `setup_handlers()`, and `prefork_reload_after_fork()`.

## Control Flow

`prefork_new_task()` forks a service master with `tfork`. The parent installs a child-pipe handler so unexpected master exit can be detected and restarted with backoff. The prefork master reinitializes tevent, LDB, and messaging after fork, creates the service task, registers an IRPC name, determines the configured child count, and forks workers. Workers listen on inherited sockets, run `post_fork()` and `before_loop()`, then process events. Worker exits are detected by `tfork_event_fd()` and restarted for fatal signals or nonzero status.

## State and Persistence Behavior

Runtime state lives in tevent contexts, control pipes, task servers, process titles, and imessaging registrations such as `prefork-master-*` and `prefork-worker-*`. No durable application data is written directly, but worker services may mutate Samba databases. Restart delay state is carried in memory and bounded by loadparm settings.

## Dependencies and Integration Points

The model integrates with `tfork`, tevent, messaging/IRPC cleanup, LDB fork hooks, cluster server IDs, loadparm parameters `prefork children`, `prefork backoff increment`, and `prefork maximum backoff`, plus `server_util` log-size tracing.

## Risks and Edge Cases

Fork/event-context separation is subtle: the master uses one event context for supervision and another to create worker-ready service state. Incorrect hook ordering can leave workers with stale messaging or DB handles. A child count of zero starts no workers. Fast-crashing workers can restart repeatedly until backoff limits. Control-pipe EOF is the shutdown signal.

## Test Signals

Tests should cover normal prefork startup, per-service child-count overrides, worker crash restart/backoff, master crash restart, parent-pipe shutdown, `inhibit_pre_fork`, SIGHUP log reopen, SIGTERM process-group cleanup, and IRPC process cleanup after worker death.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_prefork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_single.c -->
# sources/user-network-fs/samba/source4/samba/process_single.c

## Purpose

`process_single.c` implements the simplest process model, where one process handles all tasks and accepted connections without forking.

## Important APIs, Types, and Functions

`single_ops` supplies `model_init`, `accept_connection`, `new_task`, `terminate_task`, `terminate_connection`, and `set_title`. `single_accept_connection()` accepts a socket and invokes the service callback in the current process. `single_new_task()` creates a task with a monotonically increasing task id. `process_model_single_init()` registers the model.

## Control Flow

When a listener is readable, the model accepts the socket, steals it under service-private memory, and calls the supplied `new_conn()` callback with a server ID derived from the current PID and socket fd. Task startup calls the service's `new_task()` callback, then optional `post_fork()` and `before_loop()` hooks even though no fork occurred.

## State and Persistence Behavior

The only model-local persistent state is the static task id counter starting at `INT32_MAX`, avoiding collisions with fd-based IDs. All service and connection state remains inside the one event loop.

## Dependencies and Integration Points

It depends on socket helpers, cluster IDs, and `service_details` hooks. It is registered as the internal `process_model_single` module in `source4/samba/wscript_build`.

## Risks and Edge Cases

One busy or stuck connection can affect all services because there is no process isolation. `single_terminate_task()` logs but does not shut down the process. Accept failures sleep for one second to avoid spinning under resource pressure.

## Test Signals

Useful signals are startup under `--model=single`, multiple simultaneous connections sharing one PID, task id uniqueness, hook ordering, and temporary accept failure behavior without log flooding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_standard.c -->
# sources/user-network-fs/samba/source4/samba/process_standard.c

## Purpose

`process_standard.c` implements a process model where each task runs in its own process and, unless inhibited, each accepted connection is handled by a forked worker process.

## Important APIs, Types, and Functions

`standard_ops` implements `model_ops`. `struct standard_child_state` tracks child PID and pipe fds for cleanup. `struct process_context` carries service name, parent-control fd, and fork-on-accept flags. Key functions are `setup_standard_child_pipe()`, `standard_child_pipe_handler()`, `standard_accept_connection()`, `standard_new_task()`, `standard_pipe_handler()`, `standard_terminate_connection()`, and signal handlers.

## Control Flow

Task startup forks a child, reinitializes tevent, LDB, and messaging, registers parent-pipe and signal handlers, then runs the task callback and hooks. Connection accept first accepts the socket; if `inhibit_fork_on_accept` is set, the task process handles it directly. Otherwise, the parent creates a child tracking pipe and forks. The connection child frees listener state, reinitializes process-local subsystems, sets a connection title, invokes `new_conn()`, and runs its event loop until termination.

## State and Persistence Behavior

Parent process state tracks live children through pipes, avoiding zombies via `waitpid()`. `connections_active` and `smbd_max_processes` enforce max process limits. Per-child state is reset after fork; service databases are not persisted by this layer.

## Dependencies and Integration Points

The model integrates with tevent, messaging datagram cleanup, LDB fork hooks, socket addresses, cluster IDs, process titles, and loadparm `max smbd processes`.

## Risks and Edge Cases

Fork-after-accept has complex ownership: listener state must be released in children, and messaging/LDB must be reinitialized. If `SIGCHLD` is set to `SIG_IGN`, status collection can fail. `post_fork()` is not called per accepted connection, only after task init. Max-process counters rely on child-pipe cleanup.

## Test Signals

Tests should cover service task forking, per-connection forking, `inhibit_fork_on_accept`, max-process request dropping, child exit status logging, parent-pipe EOF shutdown, SIGTERM group termination, and cleanup without zombies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_standard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server.c -->
# sources/user-network-fs/samba/source4/samba/server.c

## Purpose

`server.c` is the main `samba` AD DC server binary. It parses daemon options, prepares runtime directories and databases, initializes process models and services, starts configured services, and runs the top-level event loop.

## Important APIs, Types, and Functions

`struct server_state` holds the top-level event context and binary name. Major helpers include `cleanup_tmp_files()`, `setup_signals()`, `server_stdin_handler()`, `max_runtime_handler()`, `handle_inplace_db_upgrade_check_and_update_fl()`, `prime_ldb_databases()`, `setup_parent_messaging()`, `samba_parent_shutdown()`, `samba_terminate()`, `show_build()`, `binary_smbd_main()`, and `main()`.

## Control Flow

`main()` initializes talloc and calls `binary_smbd_main()`. Startup initializes command-line parsing, handles daemon/interactive modes, sets signal masks, logs version info, daemonizes if requested, cleans tmp files, creates lock/pid directories, opens the pidfile, disables recursive winbind calls, initializes GENSEC, process models, services, tevent, log tracing, stdin EOF handling, max-runtime timer, signal handlers, and role validation. It primes SAM/privilege databases, refuses backup databases, registers parent messaging, creates a process-control pipe, and starts services through `server_service_startup()`. Then it signals daemon readiness and waits in `tevent_loop_wait()`.

## State and Persistence Behavior

Startup deletes Samba tmp files, creates pid/lock directories, writes a pidfile, may trigger DSDB reindexing and functional-level updates inside a transaction, opens persistent database contexts for reuse, and registers imessaging names. Runtime state hangs from `server_state`.

## Dependencies and Integration Points

The file integrates command-line/loadparm, daemon helpers, DSDB/SAMDB, secrets/schannel, winbind recursion guard, GENSEC, process-model and service registries, cluster server IDs, IRPC, tevent tracing, and `tfork` or pthread atfork handling.

## Risks and Edge Cases

Startup has many fatal exits; configuration mistakes around server role, missing smb.conf, backup databases, pid directories, schannel store, or process model names abort the daemon. `recursive_delete()` panics on unlink failure. Fork/atfork control-pipe handling differs by pthread support. In-place DB updates happen early and must remain transaction-safe.

## Test Signals

Integration tests should cover daemon, foreground, and interactive modes; role-check failure paths; backup database refusal; database reindex/functional-level path; service startup under different models; stdin EOF termination; `smbcontrol samba shutdown`; `SAMBA_TERMINATE`; max-runtime exit; and `--show-build`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.c -->
# sources/user-network-fs/samba/source4/samba/server_util.c

## Purpose

`server_util.c` provides shared server utility code for tevent tracing and periodic log-size enforcement.

## Important APIs, Types, and Functions

`struct samba_tevent_trace_state` records event count and last log-size check time. `create_samba_tevent_trace_state()` allocates zeroed state. `samba_tevent_trace_callback()` watches `TEVENT_TRACE_BEFORE_WAIT` points and periodically calls log-size checks under root privileges.

## Control Flow

The main server and prefork masters create trace state and register the callback with `tevent_set_trace_callback()`. On each before-wait trace point, the callback increments an event counter and triggers a check every 200 events or after roughly 29 seconds. It forces the log-size check path, verifies whether a check is needed, temporarily raises privileges, and calls `check_log_size()`.

## State and Persistence Behavior

Only in-memory counters are stored. The side effect is external log-file rotation or truncation through Samba logging backends.

## Dependencies and Integration Points

It depends on tevent trace points, Samba debug/log-size helpers, and `root_privileges()`. `server.c` and `process_prefork.c` use it.

## Risks and Edge Cases

The check frequency is heuristic. If trace callbacks stop firing, log-size checks are delayed. Privilege elevation must be correctly scoped around `check_log_size()`.

## Test Signals

Tests can simulate tevent activity and verify `check_log_size()` is invoked after event-count or time thresholds, and that no action is taken for trace points other than `TEVENT_TRACE_BEFORE_WAIT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.h -->
# sources/user-network-fs/samba/source4/samba/server_util.h

## Purpose

This header exposes the server utility API for tevent trace state and callbacks.

## Important APIs, Types, and Functions

It forward-declares `struct samba_tevent_trace_state` and declares `create_samba_tevent_trace_state()` plus `samba_tevent_trace_callback()`.

## Control Flow

There is no runtime flow in the header. Consumers allocate state and pass the callback to tevent.

## State and Persistence Behavior

The header hides the internal state layout, preserving ABI flexibility for users that only hold an opaque pointer.

## Dependencies and Integration Points

It requires `TALLOC_CTX` and `enum tevent_trace_point` to be visible in including translation units. It is included by `server.c` and `process_prefork.c`.

## Risks and Edge Cases

The callback must receive state created by `create_samba_tevent_trace_state()`; passing another pointer will fail the `talloc_get_type_abort()` in the implementation.

## Test Signals

Compile tests should ensure both server and prefork code include the header cleanly. Runtime tests should confirm callback registration with tevent does not require knowledge of the state internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.c -->
# sources/user-network-fs/samba/source4/samba/service.c

## Purpose

`service.c` manages registration and startup of named Samba source4 server services.

## Important APIs, Types, and Functions

The private linked list `registered_servers` stores service names and copied `service_details`. `register_server_service()` adds entries. `server_service_startup()` selects a process model and starts all configured service names. `server_service_init()` maps a configured name to the registered service and invokes `task_server_startup()`. `samba_service_init()` loads static and shared service modules.

## Control Flow

`server.c` calls `samba_service_init()` during startup. Later it calls `server_service_startup()` with `server services` from loadparm and a parent-control fd. Each configured service name is looked up case-insensitively, and task startup is delegated to the selected process model.

## State and Persistence Behavior

Service registration is process-global memory. `service_details` is copied during registration, so callers do not need to preserve the original structure. No disk state is written.

## Dependencies and Integration Points

The file integrates Samba module loading, process models, and task service startup. Static modules come from `STATIC_service_MODULES`.

## Risks and Edge Cases

An unknown service name returns `NT_STATUS_INVALID_SYSTEM_SERVICE` and aborts service startup. Registration does not reject duplicate service names, so the first matching entry wins. The copied `service_details` may contain function pointers that must remain valid for the process lifetime.

## Test Signals

Tests should register fake services, verify configured startup order, unknown-service failure, static/shared service module loading, and process-model startup failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.h -->
# sources/user-network-fs/samba/source4/samba/service.h

## Purpose

`service.h` defines the service callback contract used by source4 task services and process models.

## Important APIs, Types, and Functions

`struct process_details` currently carries a worker `instances` counter, with `initial_process_details` initialized to zero. `struct service_details` exposes `inhibit_fork_on_accept`, `inhibit_pre_fork`, `task_init`, `post_fork`, and `before_loop`. It declares `samba_service_init()` and includes generated `service_proto.h`.

## Control Flow

The header describes hook ordering across `standard`, `single`, and `prefork` models. `task_init()` creates service state, `post_fork()` handles per-process worker initialization where applicable, and `before_loop()` registers final event or messaging handlers before the event loop.

## State and Persistence Behavior

The structure carries behavior and lifecycle policy rather than state. `process_details.instances` lets prefork workers know their instance number.

## Dependencies and Integration Points

It includes stream and task service headers and is consumed by service modules, process models, and task startup helpers.

## Risks and Edge Cases

Hook order differs by model, especially prefork master versus worker behavior. Services must not assume that the `task_server` pointer or event/messaging contexts are unchanged between hooks.

## Test Signals

Model-specific service tests should assert hook order, `instances` values, and behavior when `inhibit_fork_on_accept` or `inhibit_pre_fork` is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_named_pipe.c -->
# sources/user-network-fs/samba/source4/samba/service_named_pipe.c

## Purpose

`service_named_pipe.c` adapts the generic stream service layer to Samba named-pipe transports over Unix-domain sockets and named-pipe authentication.

## Important APIs, Types, and Functions

`struct named_pipe_socket` stores pipe name/path, downstream stream ops, and private data. `tstream_setup_named_pipe()` creates the pipe directory and socket listener. `named_pipe_accept()` converts an accepted socket fd into a BSD tstream and starts `tstream_npa_accept_existing_send()`. `named_pipe_accept_done()` completes authentication/session setup and hands the connection to the real pipe server ops.

## Control Flow

The listener is created under `ncalrpc_dir/np`. New stream connections first use `named_pipe_stream_ops`. Accept disables normal fd handling, wraps the socket in tstream, and starts named-pipe-auth negotiation. Completion receives transport type, client/server addresses, names, and `auth_session_info_transport`, builds `conn->session_info`, enforces transport-specific constraints, then swaps `conn->ops` and `private_data` to the downstream server and calls its `accept_connection()`.

## State and Persistence Behavior

The file creates persistent socket path directories and a Unix-domain socket. Per-connection session information is stored in `stream_connection`. No registry or account state is changed.

## Dependencies and Integration Points

It depends on service stream APIs, loadparm `ncalrpc_dir`, auth session conversion, named-pipe-auth tstream helpers, NDR named-pipe auth definitions, and filesystem directory helpers.

## Risks and Edge Cases

It rejects system tokens on `NCACN_NP`, only allows `NCACN_NP` or `NCALRPC`, and terminates connections on any authentication or memory error. Directory permissions are strict for the `np` subdirectory. The temporary named-pipe ops intentionally terminate if raw recv/send handlers are called.

## Test Signals

Tests should cover pipe path normalization with and without `\\pipe\\`, directory creation/permissions, successful NCALRPC and NCACN_NP auth, system-token rejection on remote named pipes, invalid transport rejection, and downstream ops handoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_named_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.c -->
# sources/user-network-fs/samba/source4/samba/service_stream.c

## Purpose

`service_stream.c` provides reusable helpers for stream-oriented Samba services: listener setup, accept dispatch through process models, connection object creation, IO dispatch, and connection termination.

## Important APIs, Types, and Functions

`struct stream_socket` stores listener state. Public functions include `stream_setup_socket()`, `stream_new_connection_merge()`, `stream_terminate_connection()`, `stream_io_handler_fde()`, `stream_io_handler_callback()`, and `stream_connection_set_title()`. Static helpers include `stream_accept_handler()`, `stream_new_connection()`, and `stream_io_handler()`.

## Control Flow

`stream_setup_socket()` creates a socket, resolves/binds/listens on IP or non-IP addresses, registers a tevent fd, and stores model/service ops. When readable, `stream_accept_handler()` asks the selected process model to accept and possibly fork. `stream_new_connection()` builds `stream_connection`, checks host access, registers fd and messaging contexts, records addresses, sets a title, enables reads, and calls the service's accept hook. IO events call send or receive handlers. Termination defers if inside an IO callback, otherwise frees fd, messaging, connection, and calls the model's `terminate_connection()`.

## State and Persistence Behavior

Listener and connection state is talloc-owned. Connections have per-server IDs, local/remote addresses, optional tstream/session info, and process-context pointers. No durable state is written except effects of downstream services.

## Dependencies and Integration Points

It integrates socket backends, tevent fd events, process models, imessaging, loadparm host allow/deny, cluster IDs, tsocket formatting, and stream server ops.

## Risks and Edge Cases

Termination during a callback is intentionally deferred to avoid use-after-free. Dynamic RPC port allocation iterates the configured low/high range. Socket ownership is split between tevent and socket flags, so close semantics are delicate. Access checks use the default service's host allow/deny lists.

## Test Signals

Tests should cover IP and Unix listener setup, dynamic port assignment, socket option failures, host access denial, accept under each process model, deferred termination from recv/send handlers, merged connections, and process-title updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.h -->
# sources/user-network-fs/samba/source4/samba/service_stream.h

## Purpose

This header defines the public stream-service structures and callback contract for source4 stream servers.

## Important APIs, Types, and Functions

`struct stream_connection` contains stream ops, process model ops, server ID, private data, tevent fd/context, socket or tstream, imessaging context, loadparm context, local/remote addresses, optional session info, processing/termination flags, and model process context. `struct stream_server_ops` provides `name`, `accept_connection`, `recv_handler`, and `send_handler`. It declares `stream_terminate_connection()`.

## Control Flow

The header has no executable flow, but its fields are filled by `service_stream.c` and consumed by protocol-specific stream services and named-pipe adapters.

## State and Persistence Behavior

`stream_connection` is the in-memory per-connection state container. The `processing` and `terminate` fields coordinate deferred shutdown during callbacks.

## Dependencies and Integration Points

It depends on generated `server_id` definitions and forward-visible Samba types such as model ops, sockets, tstream, tsocket addresses, imessaging, loadparm, and auth session info.

## Risks and Edge Cases

Consumers must treat ownership as talloc-managed and avoid freeing embedded resources out from under `stream_terminate_connection()`. Callbacks must be prepared for `socket` to be `NULL` on merged or tstream-taken connections.

## Test Signals

Compile coverage for stream services validates structure visibility. Runtime tests should exercise recv/send callbacks, deferred termination, and named-pipe handoff that changes `ops` and `private_data`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.c -->
# sources/user-network-fs/samba/source4/samba/service_task.c

## Purpose

`service_task.c` provides the task-service wrapper that creates `task_server` objects, initializes imessaging, calls service-specific task initialization, and delegates lifecycle operations to process models.

## Important APIs, Types, and Functions

`task_server_startup()` is the public startup entry. `task_server_callback()` is passed into process models and creates `struct task_server`. `task_server_terminate()` logs, optionally notifies the parent `samba` process via IRPC `SAMBA_TERMINATE`, cleans messaging, and calls `model_ops->terminate_task()`. `task_server_set_title()` delegates title changes to the process model.

## Control Flow

Service startup allocates `task_state` with `service_details` and `model_ops`, then calls `model_ops->new_task()`. The selected model invokes `task_server_callback()` in the appropriate process. The callback fills event/loadparm/server-id/model/process-context fields, initializes imessaging, and calls `task_init()`. Termination may synchronously send a fatal termination request to the parent and then lets the model exit or continue as appropriate.

## State and Persistence Behavior

Task state is in-memory and talloc-owned from the event context. Messaging endpoints are registered per task and cleaned up during termination. Fatal termination can cause parent process exit through `samba_terminate()`.

## Dependencies and Integration Points

It depends on process models, imessaging/IRPC, generated `ndr_irpc_c`, loadparm, and `service_details` callbacks.

## Risks and Edge Cases

If `imessaging_init()` fails, `task_server_terminate()` is called on a partially initialized task. If `task_init()` fails, the task is returned as `NULL` without explicit cleanup in this function. Fatal termination uses a nested event loop through synchronous IRPC.

## Test Signals

Tests should cover successful task initialization, imessaging failure, `task_init()` failure cleanup, fatal parent notification, nonfatal model termination, and title delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.h -->
# sources/user-network-fs/samba/source4/samba/service_task.h

## Purpose

This header defines `struct task_server`, the shared state object for source4 task-based services.

## Important APIs, Types, and Functions

`struct task_server` holds the tevent context, selected model ops, imessaging context, loadparm context, cluster/server ID, service private data, and process-model context.

## Control Flow

There is no runtime flow in the header. `service_task.c` initializes the structure and service modules consume it in `task_init`, `post_fork`, and `before_loop`.

## State and Persistence Behavior

The structure is in-memory per task process or task instance. `private_data` belongs to service implementations; `process_context` belongs to the selected process model.

## Dependencies and Integration Points

It includes generated `server_id` definitions and relies on forward declarations from including units for tevent, imessaging, loadparm, and model ops.

## Risks and Edge Cases

Ownership is implicit through talloc parentage. Services must not assume `msg_ctx` or `event_ctx` remain unchanged across hook phases, as documented in `service.h`.

## Test Signals

Compile and runtime service startup tests validate the structure contract. Hook-order tests should confirm fields are valid at `task_init`, `post_fork`, and `before_loop`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/wscript_build -->
# sources/user-network-fs/samba/source4/samba/wscript_build

## Purpose

This waf build fragment defines the source4 service framework, process-model framework, server utility subsystem, `samba` binary, and built-in process model modules.

## Important APIs, Types, and Functions

Targets include `service`, `process_model`, `samba_server_util`, the `samba` binary, `process_model_single`, `process_model_standard`, and `process_model_prefork`. It also configures autoproto headers `service_proto.h` and `process_model_proto.h`.

## Control Flow

During build, waf resolves these target declarations, links dependencies, and controls AD DC-only enablement with `AD_DC_BUILD_IS_ENABLED()`. Runtime module registration is affected by `init_function` and `internal_module` settings.

## State and Persistence Behavior

The file writes no runtime state. Persistent build products include libraries, modules, generated prototypes, and the installed `samba` binary under `${SBINDIR}`.

## Dependencies and Integration Points

The service library links tevent, messaging, socket, named-pipe auth, tsocket, credentials, and process model. The `samba` binary links command-line, GENSEC, registry, cluster, schannel, secrets, and server-util components. Process model modules link their model-specific dependencies.

## Risks and Edge Cases

Incorrect `internal_module` or dependency declarations change which process models are available at runtime. Missing `samba_server_util` in prefork or server deps would break log-tracing integration. AD DC gates must match code assumptions.

## Test Signals

Build tests should verify AD DC-enabled builds produce all three process model modules and the `samba` binary. Runtime smoke tests should start `samba --model=single`, `standard`, and `prefork`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/buildtree.pl -->
# sources/user-network-fs/samba/source4/script/buildtree.pl

## Purpose

`buildtree.pl` mirrors the source directory tree into the build directory by creating corresponding directories while excluding paths under the build directory itself.

## Important APIs, Types, and Functions

It uses Perl `File::Find`, `File::Path::mkpath`, and `Cwd::abs_path`. Environment variables `builddir` and `srcdir` supply roots. The `wanted()` callback handles each filesystem entry.

## Control Flow

The script resolves absolute source/build roots, walks `$srcdir`, and for every directory not inside `$builddir`, substitutes the source prefix with the build prefix, creates the destination directory, and prints the created path.

## State and Persistence Behavior

It persists directory creation in the build tree. It does not copy file contents or remove old directories.

## Dependencies and Integration Points

It is a build helper used by source4 build processes that require a build tree shaped like the source tree.

## Risks and Edge Cases

Regex substitution on paths can behave oddly if source/build paths contain regex metacharacters. Missing `builddir` or `srcdir` environment variables cause `abs_path()` problems. Symlink and permission behavior follows `File::Find` and `mkpath`.

## Test Signals

Tests should run it with temporary source/build trees, nested directories, a build directory inside the source, and missing environment variables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/buildtree.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/depfilter.py -->
# sources/user-network-fs/samba/source4/script/depfilter.py

## Purpose

`depfilter.py` filters a Graphviz dot dependency graph to only the arcs reachable from a selected top node.

## Important APIs, Types, and Functions

The script parses one command-line argument, reads dot input from stdin, builds a `graph` mapping with a regex for `"node" -> "dep"` arcs, recursively fills `subgraph` with `add_deps(node)`, and prints a reduced dot graph.

## Control Flow

It validates argument count, stores all stdin lines, parses arcs from all lines except the first and last, recursively walks dependencies from the requested node, then emits the original graph header/footer with only reachable arcs.

## State and Persistence Behavior

All graph state is in memory. No files are written.

## Dependencies and Integration Points

It depends only on Python `sys` and `re`. It is useful with waf or build dependency graph output piped through stdin.

## Risks and Edge Cases

The regex assumes every interior line is a valid quoted arc; malformed dot input can raise `AttributeError`. Recursive traversal can hit recursion limits on very deep graphs. It does not preserve non-arc attributes.

## Test Signals

Tests should include simple chains, branching graphs, cycles, missing top node, malformed lines, and graph attributes that should be dropped or handled explicitly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/depfilter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/extract_allparms.sh -->
# sources/user-network-fs/samba/source4/script/extract_allparms.sh

## Purpose

This shell helper extracts Samba loadparm option names and whether they are local or global from `param/loadparm.c`.

## Important APIs, Types, and Functions

It uses a single `grep` pipeline with `sed` transformations and `sort -f`. It searches for table entries matching `{"...P_[GL]`.

## Control Flow

The script reads `param/loadparm.c`, strips trailing initializer content, maps `P_LOCAL` entries to `S`, maps `P_GLOBAL` entries to `G`, removes leading syntax, and sorts case-insensitively.

## State and Persistence Behavior

It writes only to stdout and has no persistent state.

## Dependencies and Integration Points

It depends on POSIX shell, `grep`, `sed`, and `sort`, and assumes it is run from a source tree where `param/loadparm.c` is present.

## Risks and Edge Cases

The parsing is brittle and tied to the C initializer formatting in `loadparm.c`. It does not handle unusual whitespace or multiline entries outside the expected pattern.

## Test Signals

Tests should compare output against representative `loadparm.c` snippets containing local, global, mixed-case, and unusual spacing entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/extract_allparms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/find_unused_options.sh -->
# sources/user-network-fs/samba/source4/script/find_unused_options.sh

## Purpose

`find_unused_options.sh` is a maintenance helper that identifies generated `lp_*()` loadparm accessor functions that appear unused in C files.

## Important APIs, Types, and Functions

It builds `LIST_GLOBAL` from `FN_GLOBAL` macros and `LIST_LOCAL` from `FN_LOCAL` macros in `param/loadparm.c`, scans all `*.c` files from the current directory, and reports accessors with no grep hits.

## Control Flow

For each global accessor, it searches for `key()` calls. For each local accessor, it searches for `key(` calls. Missing hits produce `Not Used Global` or `Not Used LOCAL` messages. A final reminder tells maintainers to clean and rebuild before removal.

## State and Persistence Behavior

The script reads source files and writes findings to stdout. It does not modify files.

## Dependencies and Integration Points

It depends on shell, `grep`, `sed`, `cut`, and `find`, and on `param/loadparm.c` macro formatting.

## Risks and Edge Cases

Plain grep can miss macro-indirect or generated uses and can produce false positives from comments or strings. Local and global search regexes differ, which may change sensitivity. It scans from the current directory and can include generated or irrelevant C files.

## Test Signals

Tests should use fixture `loadparm.c` and C files with direct calls, comment-only mentions, macro uses, and unused functions to characterize false positives/negatives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/find_unused_options.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/minimal_includes.pl -->
# sources/user-network-fs/samba/source4/script/minimal_includes.pl

## Purpose

`minimal_includes.pl` searches C files for top-level `#include` lines that can be removed without changing compiler output, optionally removing them.

## Important APIs, Types, and Functions

Options include `--remove`, `--skip-system`, `--waf`, and `--help`. Important functions are `load_lines()`, `save_lines()`, `test_compile()`, `test_include()`, `process_file()`, and `ShowHelp()`.

## Control Flow

For each input file, the script captures original compile output. It scans top-level include lines outside preprocessor conditionals and not marked `needed`. For each include, it temporarily renames the source to `.misaved`, writes a version without that include, recompiles via `make` or waf, compares output with the original, and either reports or removes the include. Otherwise it restores the original file.

## State and Persistence Behavior

In report mode it should restore files after each test. In `--remove` mode it can persist include removals by deleting the saved original. It creates temporary `.misaved` files during processing and object files during compilation.

## Dependencies and Integration Points

It depends on Perl, local build tooling, `make` or waf, and source files that map predictably to object targets.

## Risks and Edge Cases

The script deliberately edits files during tests, so interruption can leave `.misaved` files or modified sources. Comparing compiler output may miss semantic changes that still compile. Conditional includes are skipped only via simple nesting tracking.

## Test Signals

Tests should run on disposable files with removable and required includes, nested preprocessor blocks, `system/` includes under `--skip-system`, waf mode, and interruption recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/minimal_includes.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/mkproto.pl -->
# sources/user-network-fs/samba/source4/script/mkproto.pl

## Purpose

`mkproto.pl` generates C prototype headers from source files, splitting public `_PUBLIC_` functions from private prototypes when requested.

## Important APIs, Types, and Functions

Options include `--public`, `--private`, `--all`, `--define`, `--public-define`, `--private-define`, `--srcdir`, and `--builddir`. Key functions are `normalize_define()`, `file_load()`, `print_header()`, `print_footer()`, and `process_file()`. Output buffers are appended through `public()` and `private()`.

## Control Flow

The script parses options, derives include guard names, chooses whether public/private output share the same buffer, writes header prelude macros, processes each input C file, and emits detected function signatures. `process_file()` prefers builddir files, falls back to srcdir, captures Doxygen comments, skips indented lines, declarations, macros, and `main`, and reads multiline prototypes until a closing parenthesis.

## State and Persistence Behavior

It writes generated header files, creating parent directories with `mkpath`. If no output file is provided for one class, that class may be printed to stdout.

## Dependencies and Integration Points

It is used by Samba's build autoproto mechanism and depends on Perl `Getopt::Long`, `File::Basename`, and `File::Path`.

## Risks and Edge Cases

The parser is regex-based and can miss complex return types, function-pointer returns, macro-generated definitions, or unusual formatting. It writes generated files directly and can overwrite existing headers.

## Test Signals

Tests should cover public/private split, shared `--all` output, multiline prototypes, Doxygen comments, generated include guards, builddir fallback, and intentionally unsupported complex declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/mkproto.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/update-proto.pl -->
# sources/user-network-fs/samba/source4/script/update-proto.pl

## Purpose

`update-proto.pl` updates an existing C prototype header while trying to preserve surrounding formatting and comments.

## Important APIs, Types, and Functions

Options are `--help` and `--verbose`. `%new_protos` stores prototypes parsed from source files. Important functions are `count()`, `process_file()`, and `insert_new_protos()`.

## Control Flow

The script reads the target header and optional C files. It parses non-static function definitions into `%new_protos`. While streaming the header, it recognizes `/* The following definitions come from FILE */` markers to refresh source-derived prototypes, inserts new prototypes above the configured marker, updates changed prototypes, removes deleted prototypes, and reports counts on stderr.

## State and Persistence Behavior

It writes the updated header to stdout rather than modifying the file directly. New prototype state is in memory.

## Dependencies and Integration Points

It depends on Perl and is part of older Samba prototype maintenance workflows, complementary to generated autoproto headers.

## Risks and Edge Cases

Regex parsing cannot handle all C syntax, especially macros and function-pointer returns. The header must use expected comments for best results. Callers must redirect stdout safely to avoid losing headers on failure.

## Test Signals

Tests should cover added, modified, deleted, and kept prototypes; marker-driven source parsing; duplicate prototypes; verbose output; and malformed source/header input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/update-proto.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin -->
# sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin

## Purpose

`enablerecyclebin` enables the Active Directory Recycle Bin optional feature on a target Samba LDB URL.

## Important APIs, Types, and Functions

It uses `optparse`, Samba option/credential helpers, `samba.Ldb`, `system_session()`, rootDSE search, and an `ldb.Message` modification of `enableOptionalFeature`.

## Control Flow

The script requires one URL argument, loads smb.conf and credentials, opens the LDB with system session, searches rootDSE for `configurationNamingContext`, constructs a modify message on the root DN, and adds the Recycle Bin feature identifier under `CN=Partitions`.

## State and Persistence Behavior

It persists an AD configuration change by modifying `enableOptionalFeature`. The change is domain/forest significant and not local script state.

## Dependencies and Integration Points

It integrates Samba Python bindings, LDB, credentials, and AD optional-feature semantics.

## Risks and Edge Cases

It does not prompt for confirmation or check whether the feature is already enabled. Failures are mostly raw exceptions. Correct privileges are required, and enabling Recycle Bin is not a trivial reversible operation.

## Test Signals

Tests should use a disposable provision, verify rootDSE discovery, insufficient-privilege failure, idempotent/already-enabled behavior, and post-change feature visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges -->
# sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges

## Purpose

`findprovisionusnranges` identifies update sequence number ranges likely created by provision or upgradeprovision activity.

## Important APIs, Types, and Functions

It uses Samba option parsing, credentials with Kerberos disabled, `get_paths()`, `findprovisionrange()`, `print_provision_ranges()`, LDB rootDSE searches, `ndr_unpack()`, and `misc.GUID` for invocation ID decoding.

## Control Flow

The script loads configuration and credentials, opens `sam.ldb`, derives the base DN from the realm, reads `dsServiceName`, follows it to the NTDS settings object, extracts `invocationId`, computes provision-range buckets, and prints ranges affecting more than a fixed minimum object count.

## State and Persistence Behavior

It reads databases and optionally writes result files through `print_provision_ranges()` when `--storedir` is provided. It does not modify AD data.

## Dependencies and Integration Points

It depends on Samba upgrade helper APIs, local provision paths, LDB controls, and DSDB metadata.

## Risks and Edge Cases

It assumes local database layout and realm-derived base DN. Missing `dsServiceName` or invocation ID exits. The minimum threshold is hard-coded to five objects.

## Test Signals

Tests should run against known provisioned databases, databases without invocation ID, `--storedir` output, and upgraded databases with recognizable high-volume USN ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py

## Purpose

`gen_error_common.py` provides shared parsing helpers for generators that transform copied MS-ERREF error tables into Samba C, Python, or Rust definitions.

## Important APIs, Types, and Functions

`ErrorDef` stores `err_code`, `err_define`, `err_string`, `isWinError`, and source `linenum`. `escapeString()` prepares text for generated C strings. `parseErrorDescriptions()` parses table-like text into `ErrorDef` objects using a caller-provided transform function.

## Control Flow

The parser skips blank lines, starts a new error when a line begins with `0x`, treats the next non-code token as the symbolic name, appends later text as description, escapes strings, counts parsed lines, prints a summary, and returns the list.

## State and Persistence Behavior

All state is in-memory. No files are written by this helper.

## Dependencies and Integration Points

It is imported by `gen_hresult.py`, `gen_ntstatus.py`, and `gen_werror.py`.

## Risks and Edge Cases

Input parsing assumes a simple copied-table format. Lines before the first hex code are ignored. Description joining can blur table columns. It prints to stdout, which can be noisy in build logs.

## Test Signals

Unit tests should cover blank lines, missing descriptions, multiline descriptions, escaping quotes/tabs/backslash-angle text, and transform functions for HRESULT, NTSTATUS, and WERROR names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py

## Purpose

`gen_hresult.py` generates HRESULT headers, C lookup code, and Python bindings from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `write_license()`, `generateHeaderFile()`, `generateSourceFile()`, `generatePythonFile()`, `transformErrorName()`, and `main()`. Generated APIs include `HRESULT`, `HRES_ERROR`, `HRES_ERROR_V`, `hresult_errstr_const()`, `hresult_errstr()`, and conversion helpers for Win32-backed HRESULTs.

## Control Flow

`main()` requires four arguments after the script name: input table, header output, C source output, and Python source output. It parses errors with `parseErrorDescriptions()`, writes the header with macros and constants, writes C switch-based name/description lookup, and writes a Python module initializer exporting constants.

## State and Persistence Behavior

It writes three generated files. Generated source contains static lookup data and a static fallback message buffer.

## Dependencies and Integration Points

It imports `gen_error_common`, uses Samba WERROR helpers in generated C, and generates Python C-extension code.

## Risks and Edge Cases

Generation assumes trusted input; strings are escaped only by the common helper. The source lookup has unreachable `break` after `return` in one path but harmless. Missing or malformed arguments exit after usage output.

## Test Signals

Tests should generate from a small fixture, compile generated C, import generated Python module, verify Win32 HRESULT conversion fallback, and check names/descriptions with escaped input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py

## Purpose

`gen_ntstatus.py` generates NTSTATUS constants, C name/description tables, Python bindings, and Rust constants from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `generateHeaderFile()`, `generateSourceFile()`, `generatePythonFile()`, `generateRustFile()`, `transformErrorName()`, and `main()`. It also constructs a synthetic `NT_STATUS_OK` entry.

## Control Flow

`main()` expects input, header, source, Python, and Rust output paths. It parses UTF-8 input through `parseErrorDescriptions()`, inserts `NT_STATUS_OK` at the front, and writes all outputs. Name transformation normalizes `STATUS_`, `RPC_NT_`, and `EPT_NT_` prefixes.

## State and Persistence Behavior

It writes four generated files. Generated C defines static error-name and description arrays; generated Rust defines a tuple struct, constants, descriptions, and formatting traits.

## Dependencies and Integration Points

It imports `ErrorDef` and parser helpers from `gen_error_common`, generates code consumed by Samba's NTSTATUS utilities and Python modules, and participates in Rust bindings.

## Risks and Edge Cases

The Rust generator skips descriptions for a few duplicated/special constants to avoid pattern conflicts. Parser assumptions mirror the common helper. Generated arrays rely on downstream sentinel handling.

## Test Signals

Tests should compile generated C and Rust from fixtures, import Python constants, verify prefix normalization, ensure `NT_STATUS_OK` ordering, and validate description omission behavior for special constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_output.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_output.py

## Purpose

`gen_output.py` is a small test utility that emits repeated data to stdout and exits with a caller-selected status code.

## Important APIs, Types, and Functions

It uses `argparse` options `--data`, `--repeat`, and `--retcode`, then writes `args.data * args.repeat` to stdout.

## Control Flow

The script parses arguments, writes the repeated data string, and exits with the requested return code.

## State and Persistence Behavior

No state is persisted. Output volume is controlled entirely by arguments.

## Dependencies and Integration Points

It depends only on Python standard library modules and is designed for tests that need large stdout/stderr-like data or nonzero command exits.

## Risks and Edge Cases

Very large repeat values allocate and write a large Python string, which can consume memory. Negative repeat values produce an empty string under Python string multiplication. Non-integer values are rejected by argparse.

## Test Signals

Tests should check default 1 MiB output, custom data, zero and negative repeat behavior, and nonzero exit code propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py

## Purpose

`gen_werror.py` generates WERROR constants, DOS error name switch cases, friendly message switch cases, and Python bindings from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `generateHeaderFile()`, `generateSourceFile()`, `generateFriendlySourceFile()`, `generatePythonFile()`, `transformErrorName()`, and `main()`.

## Control Flow

`main()` requires input plus four output paths. It parses UTF-8 error data with Windows-error mode enabled, writes `WERR_*` macro definitions, writes C switch cases for symbolic and friendly strings, and writes a Python module initializer exporting numeric WERROR values.

## State and Persistence Behavior

It writes four generated files and stores no runtime state. Generated switch fragments are intended to be included in larger C functions.

## Dependencies and Integration Points

It imports `gen_error_common`, generates code for Samba WERROR handling, and uses Python C API helpers in generated module code.

## Risks and Edge Cases

`WERR_NERR_SUCCESS` is skipped in source switch generation. The usage string mentions fewer outputs than the code requires. Input parsing is format-sensitive.

## Test Signals

Tests should generate from fixture errors, compile generated fragments in their include context, import Python constants, validate `ERROR_` and `WERR_` name normalization, and check friendly messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py

## Purpose

`gen_wsp_props.py` generates C source tables describing Windows Search Protocol property sets from CSV input.

## Important APIs, Types, and Functions

`PropInfo` stores property metadata. Global maps `GuidToPropMap` and `GuidToPropMapLocation` group properties by GUID. Functions include `parseCSV()`, `parseGuid()`, `getBoolString()`, `getVtype()`, `generateSourceCode()`, and `main()`.

## Control Flow

The script expects a property CSV, output source path, and optional limited-info properties file. `parseCSV()` reads each non-comment line, splits up to ten columns, fills defaults, and appends properties by GUID. `generateSourceCode()` emits includes, per-GUID `full_propset_info` arrays, and a `full_propertyset` array mapping parsed GUID structs to property arrays.

## State and Persistence Behavior

Global maps accumulate parsed properties during one run. The output C file is persisted.

## Dependencies and Integration Points

Generated code includes Samba WSP NDR and utility headers. The script depends on Python `io` and expects CSV fields matching the documented property schema.

## Risks and Edge Cases

`parseCSV()` indexes `toParse[0]` without guarding empty lines. It uses simple comma splitting, so quoted commas are not supported. `parseGuid()` assumes brace-wrapped GUIDs. Dictionary iteration order controls output order on modern Python but was historically variable.

## Test Signals

Tests should cover full and limited-info CSV rows, blank/comment lines, every supported datatype mapping, vector properties, malformed GUIDs, and generated C compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/get-descriptors -->
# sources/user-network-fs/samba/source4/scripting/bin/get-descriptors

## Purpose

`get-descriptors` compares security descriptors between a local Samba AD database and a remote LDAP server, optionally producing LDIF modifications to align local descriptors with remote ones.

## Important APIs, Types, and Functions

`DescrGetter` owns local/remote LDB connections, domain DNs/SIDs, and descriptor maps. Methods include `get_domain_local_sid()`, `get_domain_remote_sid()`, `read_descr_by_base()`, `read_desc()`, `write_desc_to_ldif()`, `add_to_ldif()`, and `write_as_sddl()`.

## Control Flow

The script requires local domain, remote domain, and remote host. It opens local `SamDB` and remote LDAP, reads local and remote domain SIDs, searches schema/configuration/domain subtrees for `nTSecurityDescriptor`, maps descriptors by relative DN, compares SDDL after translating remote descriptors to the local SID, and prints either SDDL or LDIF replacement entries.

## State and Persistence Behavior

It is read-only against both directories and writes comparison output to stdout. The generated LDIF, if applied separately, would mutate local descriptors.

## Dependencies and Integration Points

It depends on Samba Python bindings, LDB paged search modules, NDR packing/unpacking, security descriptor/SID conversion, and credentials.

## Risks and Edge Cases

There is a typo in the description comment, and `add_to_ldif()` uses Python division in a range expression that may be invalid under Python 3 if long lines occur. `write_desc_to_ldif()` can reference `descr` before assignment if SDDL strings match but `opts.as_ldif` handling still reaches output. It requires high remote privileges.

## Test Signals

Tests should compare known local/remote fixture descriptors, exercise `--as-ldif` line folding, no-difference entries, SID translation, missing descriptor attributes, and remote bind failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/get-descriptors -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh -->
# sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh

## Purpose

`ktpass.sh` creates a keytab entry for a Samba principal using `ldbsearch` to discover the principal's key version number and `ktutil` to write the keytab.

## Important APIs, Types, and Functions

Options include `--out`, `--princ`, `--pass`, `--host`, `--ptype`, `--enc`, and `--path-to-ldbsearch`. The `usage()` function prints help. The script queries `msds-keyversionnumber` and drives `ktutil` via a here-document.

## Control Flow

It parses long options with `getopt`, defaults encryption to `rc4-hmac`, resolves an `ldbsearch` path, validates required options, defaults host to `hostname`, searches LDAP using Kerberos, prompts for password if `--pass '*'`, then invokes `ktutil add_entry -password` followed by `wkt`.

## State and Persistence Behavior

It writes the requested keytab file. Password material is held in shell variables and sent to `ktutil` stdin.

## Dependencies and Integration Points

It depends on shell, GNU-style `getopt`, `ldbsearch`, Kerberos authentication, and `ktutil`.

## Risks and Edge Cases

Password on the command line can leak through process listings; prompting disables echo but does not robustly restore terminal settings on interruption. The LDAP filter interpolates the principal directly. `--ptype` is accepted but ignored.

## Test Signals

Tests should cover kvno lookup success/failure, prompted password mode, each encryption value, alternate `ldbsearch` path, missing mandatory options, and keytab validation with `klist -k`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountccache -->
# sources/user-network-fs/samba/source4/scripting/bin/machineaccountccache

## Purpose

`machineaccountccache` initializes or retrieves a named Kerberos credential cache using the local machine account credentials.

## Important APIs, Types, and Functions

It uses Samba option parsing, `Credentials()`, `creds.guess()`, `creds.set_machine_account()`, and `creds.get_named_ccache()`.

## Control Flow

The script requires one ccache name argument, loads loadparm, creates credentials, guesses defaults, switches to the machine account, and asks Samba credentials code for the named ccache.

## State and Persistence Behavior

It can create or update the named credential cache through Samba/Kerberos credential handling. It does not print the credentials.

## Dependencies and Integration Points

It depends on Samba Python credentials bindings, local smb.conf, and stored machine account secrets.

## Risks and Edge Cases

Errors are not caught, so missing machine credentials or Kerberos failures produce tracebacks. The effect of `get_named_ccache()` depends on Kerberos environment and Samba credential backend behavior.

## Test Signals

Tests should cover missing argument, valid machine account ccache creation, missing secrets failure, and resulting ccache usability with Kerberos tools.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountccache -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw -->
# sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw

## Purpose

`machineaccountpw` prints the local machine account password from Samba stored credentials.

## Important APIs, Types, and Functions

It uses Samba options, `Credentials()`, `creds.guess()`, `creds.set_machine_account()`, `creds.get_password()`, and catches `RuntimeError` and `NTSTATUSError` for friendlier failures.

## Control Flow

The script accepts no positional arguments. It loads smb.conf, initializes credentials, selects the machine account, and prints the password. Missing configuration or stored credentials exits with diagnostic output.

## State and Persistence Behavior

It reads stored machine account secrets and writes the plaintext password to stdout. It does not modify credentials.

## Dependencies and Integration Points

It depends on Samba Python credentials and local Samba private secrets.

## Risks and Edge Cases

The primary risk is plaintext secret disclosure to stdout, shell history capture, or logs. The script intentionally exposes sensitive material for automation.

## Test Signals

Tests should cover no-argument validation, missing smb.conf, missing machine account, successful password output, and ensuring errors go to stderr with nonzero exits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss -->
# sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss

## Purpose

`nsupdate-gss` performs GSS-TSIG authenticated dynamic DNS updates against a Windows-compatible DNS server.

## Important APIs, Types, and Functions

Options include `--wipe`, `--add`, `--realm`, `--nameserver`, `--ntype`, `--noverify`, and `--verbose`. Key functions are `gss_sign()`, `sig_verify()`, `find_nameserver()`, `find_server_name()`, and `negotiate_tkey()`.

## Control Flow

The script accepts `HOST DOMAIN TARGET TTL`. It finds or uses a nameserver, creates a DNS resolver, generates a random TKEY name, acquires initiating GSS credentials for `dns/server@REALM`, performs a two-step TKEY negotiation, optionally verifies the MIC on the reply, builds a dynamic update that deletes old records unless `--add`, adds a new record unless `--wipe`, signs with TSIG using the GSS context, sends the update, and exits nonzero on failed rcode.

## State and Persistence Behavior

It mutates DNS records on the target server. It stores no local persistent state.

## Dependencies and Integration Points

It depends on Perl `Net::DNS`, `GSSAPI`, Kerberos credentials, DNS TKEY/TSIG support, and AD DNS naming conventions.

## Risks and Edge Cases

The script assumes one GSS continuation step is enough. It uses a random numeric key name without collision checking. `--noverify` weakens reply integrity checks. DNS update semantics differ for `--wipe`, `--add`, record type, and TTL.

## Test Signals

Tests should cover TKEY negotiation, MIC verification failure, add versus replace versus wipe, explicit nameserver, non-A record types, missing Kerberos creds, NXDOMAIN/YXDOMAIN behavior, and DNS rcode handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn -->
# sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn

## Purpose

`rebuildextendeddn` rewrites DN-valued and linked attributes in a Samba AD database to rebuild extended DN metadata.

## Important APIs, Types, and Functions

Functions include `message()`, `get_paths()`, and `rebuild_en_dn()`. It uses `ProvisionNames`, `provision_paths_from_lp()`, `get_linked_attributes()`, `get_dnsyntax_attributes()`, LDB transactions, and `search_options:1:2`.

## Control Flow

The script loads smb.conf and credentials with Kerberos disabled, resolves provision paths, opens `sam.ldb`, reads schema naming context, builds a list of linked and DN-syntax attributes, starts a transaction, searches all `cn=*` objects, replaces each relevant attribute with its current string values to force recalculation, verifies the attribute remains present with expected count, and commits.

## State and Persistence Behavior

It mutates `sam.ldb` inside one transaction by replacing attributes with equivalent values. It cancels the transaction on detected verification failure but may continue after printing errors in some branches.

## Dependencies and Integration Points

It depends on Samba provision/schema helpers, local LDB database paths, system session, and schema controls.

## Risks and Edge Cases

This is a broad database rewrite tool. It assumes `opts.quiet` exists even though no quiet option is added in this file, though `message()` is unused. Search filter `cn=*` may miss objects without CN. Failure handling prints diagnostics and cancels but does not immediately exit in the shown loop.

## Test Signals

Tests should run on disposable databases with known DN/link attributes, verify transaction rollback on mismatch, confirm extended DN metadata changes as expected, and check behavior with missing smb.conf or schema attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/renamedc -->
# sources/user-network-fs/samba/source4/scripting/bin/renamedc

## Purpose

`renamedc` renames a Samba domain controller account and related local secrets/configuration records.

## Important APIs, Types, and Functions

It uses Samba option parsing, `get_paths()`, `get_ldbs()`, `find_provision_key_parameters()`, `secretsdb_self_join()`, `generate_random_machine_password()`, and LDB transaction APIs.

## Control Flow

The script requires `--oldname` and `--newname`, opens SAM and secrets databases, starts transactions, finds the old DC computer object by `serverReferenceBL`, ensures the new computer name is unused, gathers provision parameters, renames the computer DN, replaces password, `sAMAccountName`, and `dNSHostName`, performs a secrets self-join with the new machine password and current KVNO, updates RID set reference, renames the server object in Sites configuration, prepares and commits both transactions, then rewrites `netbios name` in smb.conf.

## State and Persistence Behavior

It mutates `sam.ldb`, `secrets.ldb`, and smb.conf. Database changes are transactional across separate LDBs using prepare/commit, but smb.conf rewrite happens after database commits.

## Dependencies and Integration Points

It depends on Samba provision/upgrade helpers, local DB paths, secrets database semantics, RID set references, and site configuration objects.

## Risks and Edge Cases

Renaming a DC is high risk. smb.conf update is not transactional with database commits. Search filters interpolate names directly. The script assumes exactly one old DC result and one RID set. It leaves broader DNS/SPN/replication side effects to other tooling or later checks.

## Test Signals

Tests should use disposable DC databases, validate missing/duplicate names, transaction rollback on injected failure, secrets update, RID set and server object rename, smb.conf rewrite, and post-rename `dbcheck`/replication behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/renamedc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate

## Purpose

`samba-gpupdate` applies, unapplies, or reports resultant Group Policy settings for Samba clients.

## Important APIs, Types, and Functions

It imports `apply_gp()`, `unapply_gp()`, `GPOStorage`, `rsop()`, many machine and user client-side extension classes, `get_gp_client_side_extensions()`, `Credentials`, and `logger_init()`. Options include `--unapply`, `--target`, `--force`, and `--rsop`.

## Control Flow

The script parses Samba3 options and credentials, determines the target username for Computer or User policy, switches to machine credentials for fetching GPO lists, initializes logging, opens a TDB-backed GPO cache in the cache directory, builds the extension list for the selected target, loads configured extension plugins, then calls `rsop`, `apply_gp`, or `unapply_gp`.

## State and Persistence Behavior

It reads and writes the `gpo.tdb` cache and can mutate local system state through policy extensions: access rules, Kerberos settings, scripts, sudoers, smb.conf, messages, symlinks, files, OpenSSH, MOTD/issue, GNOME, certificates, browsers, firewalld, cron, and drive maps.

## Dependencies and Integration Points

It depends heavily on Samba GP Python modules, local smb.conf, machine credentials, SYSVOL/GPO access, and extension plugin loading.

## Risks and Edge Cases

Policy extensions can alter security-sensitive local configuration. User-target identity uses initial credentials, while GPO retrieval uses machine credentials. Extension ordering matters. Failed partial application depends on extension rollback semantics.

## Test Signals

Tests should cover Computer/User targets, force reapply, unapply, RSOP-only mode, extension discovery, missing machine credentials, cache persistence, and representative extension side effects in a sandbox.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-tool -->
# sources/user-network-fs/samba/source4/scripting/bin/samba-tool

## Purpose

`samba-tool` is the command-line entry point for Samba's Python netcmd command suite.

## Important APIs, Types, and Functions

It imports `samba.netcmd.main.samba_tool`, installs a default SIGINT handler, and calls `samba_tool(*sys.argv[1:])`.

## Control Flow

The script prepends `bin/python` for source-tree execution, resets SIGINT to default so Ctrl-C terminates immediately, invokes the command dispatcher with all user arguments, and exits with the returned status.

## State and Persistence Behavior

The wrapper itself stores no state. Invoked subcommands may perform extensive AD, filesystem, DNS, or configuration mutations.

## Dependencies and Integration Points

It depends on Samba Python modules and the `netcmd` dispatcher. It is the stable CLI front door for many administrative commands.

## Risks and Edge Cases

Because it delegates all behavior, wrapper risk is mostly environment/path and signal handling. The source-tree `bin/python` insertion can affect module resolution.

## Test Signals

Tests should cover help output, Ctrl-C behavior, return-code propagation, source-tree module resolution, and representative subcommand dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-tool -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba3dump -->
# sources/user-network-fs/samba/source4/scripting/bin/samba3dump

## Purpose

`samba3dump` inspects and prints data from a Samba3-style lib/private directory, either as a summary or detailed dump.

## Important APIs, Types, and Functions

Printing helpers include `print_header()`, `print_samba3_policy()`, `print_samba3_sam()`, `print_samba3_shares()`, `print_samba3_secrets()`, `print_samba3_regdb()`, `print_samba3_winsdb()`, `print_samba3_groupmappings()`, `print_samba3_aliases()`, `print_samba3_idmapdb()`, `print_samba3()`, and `print_samba3_summary()`.

## Control Flow

The script parses `--format` as `summary` or `full`, expects a libdir and optional smb.conf, creates a Samba3 parameter context with private/state/lock directories set to libdir, loads smb.conf, opens `samba.samba3.Samba3`, and prints either counts or full policy/WINS/registry/secrets/idmap/SAM/group/share data.

## State and Persistence Behavior

It is read-only but can print sensitive secrets, including stored plaintext machine passwords and LDAP bind passwords.

## Dependencies and Integration Points

It depends on Samba3 Python bindings, Samba3 passdb/registry/WINS/idmap readers, and LSA SID name constants.

## Risks and Edge Cases

There appears to be an argument bug: the optional smb.conf branch checks `len(args) < 1` after already requiring at least one argument, so a second argument may be ignored and `libdir/smb.conf` used. Full output leaks secrets to stdout.

## Test Signals

Tests should cover summary and full output against fixture Samba3 directories, optional smb.conf behavior, empty databases, secret redaction expectations if added, and invalid format/argument handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba3dump -->
