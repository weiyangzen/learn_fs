# sources/distributed-fs/ceph-client/fs/smb/server/server.c

## Purpose
Implements the ksmbd kernel module's server lifecycle, global configuration storage, work dispatch loop, sysfs control surface, transport callbacks, and module init/exit ordering. It is the central coordinator between network transport, protocol operations, session/tree validation, signing/encryption, request counters, and subsystem startup/shutdown.

## Important APIs, Types, and Functions
- Globals `int ksmbd_debug_types` and `struct ksmbd_server_config server_conf` hold debug flags and mutable server configuration.
- Config setters/getters `ksmbd_set_netbios_name()`, `ksmbd_set_server_string()`, `ksmbd_set_work_group()`, `ksmbd_netbios_name()`, `ksmbd_server_string()`, and `ksmbd_work_group()` manipulate string slots via `___server_conf_set()`.
- Request path functions: `check_conn_state()`, `__process_request()`, `__handle_ksmbd_work()`, `handle_ksmbd_work()`, `queue_ksmbd_work()`, and `ksmbd_server_process_request()`.
- Transport callbacks are registered by `ksmbd_server_tcp_callbacks_init()`, with termination handled by `ksmbd_server_terminate_conn()` calling session deregistration and lease table cleanup.
- Config lifecycle: `server_conf_init()` sets default state, protocols, auth mechanisms, and credit limit; `server_conf_free()` frees strings.
- Control work: `server_ctrl_struct`, `server_ctrl_handle_init()`, `server_ctrl_handle_reset()`, `server_ctrl_handle_work()`, `__queue_ctrl_work()`, `server_queue_ctrl_init_work()`, and `server_queue_ctrl_reset_work()` perform async start/reset under `ctrl_lock`.
- Sysfs class attributes expose `stats`, `kill_server`, and `debug` through `ksmbd-control`.
- Lifecycle functions `ksmbd_server_shutdown()`, `ksmbd_server_init()`, and `ksmbd_server_exit()` initialize and tear down procfs, work pools, IPC, global file table, inode hash, crypto, workqueues, transport, leases, and caches.

## Control Flow
Transport code receives an SMB request into `conn->request_buf` and calls the registered process callback. `queue_ksmbd_work()` initializes SMB dialect state, allocates `ksmbd_work`, moves the request buffer into it, enqueues it on the connection, increments connection request count, and schedules `handle_ksmbd_work()`. The worker optionally decrypts a transform request, allocates/initializes a response, checks session and tree connection, verifies and dispatches the command through `conn->cmds[command].proc`, handles compounded SMB2 messages, grants credits, signs responses when required, updates preauth hash, optionally encrypts the response, releases tree/session references, writes the response, dequeues and frees work.

Server init registers the sysfs class, procfs, session proc support, transport callbacks, then initializes config, work pool, file cache, IPC, global file table, inode hash, crypto, workqueue, and connection workqueue in dependency order. Shutdown reverses most resources, destroys lease tables, and uses `rcu_barrier()` before destroying the connection workqueue so deferred connection releases have drained.

## State and Persistence
`server_conf` stores runtime configuration and server state. Config strings are heap allocated and freed/reset on server reset or shutdown. Work items and request buffers are transient. Sysfs/procfs entries and counters are runtime-only. No persistent on-disk server state is created here; durable handle and share/user configuration state lives in other subsystems.

## Dependencies and Integration Points
This file depends on connection and transport callbacks, SMB dialect ops, authentication, crypto contexts, IPC, stats/procfs, oplock lease cleanup, session management, tree connect references, global file table/inode cache, and Linux module/workqueue/sysfs infrastructure. It calls protocol-specific operations supplied by `smb2ops.c` and validators from SMB common code.

## Risks and Edge Cases
- `__process_request()` aborts on signature failure or missing command handlers; command tables must be complete for negotiated dialects.
- Compound request handling shares response/session/tree state across loop iterations; reference and response-buffer handling must match dialect ops.
- On decrypt failure, `__handle_ksmbd_work()` returns before response allocation and relies on outer cleanup to free work and decrement connection request count.
- `stats_show()` indexes a fixed state string array by `server_conf.state`; invalid state values could read out of bounds.
- `kill_server_store()` performs synchronous reset under `ctrl_lock` and module reference manipulation; reset paths must not sleep in invalid contexts or race async control work.
- Init failure unwinding must mirror successful initialization exactly; missing cleanup can leave proc/sysfs/workqueue state behind.

## Test Signals
Exercise module load/unload, init failure injection at each subsystem step, server start/reset/kill sysfs paths, debug flag toggles, stats output, SMB2 request dispatch including unsupported commands and compounds, signing failure, encrypted request/response paths, disconnect while work is queued, session/tree invalidation, and RCU/KASAN validation during shutdown after active connections.
