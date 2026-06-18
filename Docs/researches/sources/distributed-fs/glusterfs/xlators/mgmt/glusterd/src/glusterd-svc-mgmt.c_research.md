# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.c

## Purpose
`glusterd-svc-mgmt.c` implements the reusable low-level process and RPC management layer for auxiliary glusterd services. Service-specific modules use it to initialize paths, start and stop `glusterfs` service processes, build service volfile/log/pid paths, and track RPC connectivity.

## Important APIs, Types, and Functions
Public APIs include `glusterd_svc_create_rundir()`, `glusterd_svc_init()`, `glusterd_svc_start()`, `glusterd_svc_stop()`, path builders for pidfiles, volfiles, logfiles, service dirs and rundirs, `glusterd_svc_reconfigure()`, `glusterd_svc_common_rpc_notify()`, `glusterd_muxsvc_common_rpc_notify()`, `glusterd_muxsvc_conn_init()`, and `glusterd_genericsvc_start()`. File-local helpers include `glusterd_svc_init_common()`, `glusterd_svc_build_volfileid_path()`, and `svc_add_args()`.

## Control Flow
Initialization builds a service name, creates its run directory, creates a Unix-socket path, initializes `glusterd_conn_t`, builds pidfile/volfile/logfile/volfile-id values, resolves the volfile server from `transport.socket.bind-address` or `localhost`, and initializes `glusterd_proc_t`.

`glusterd_svc_start()` locks `priv->attach_lock`, avoids duplicate starts if the process is already running, verifies the volfile exists, builds a `runner_t` command for `SBIN_DIR/glusterfs` with volfile-id, pidfile, logfile, and socket path, adds optional valgrind, localtime logging, daemon log level, global threading, IO engine, and caller-supplied command-line args, then runs synchronously or asynchronously. Synchronous run temporarily releases `big_lock`.

`glusterd_svc_stop()` stops the process, disconnects RPC, clears `online`, unlinks the service socket, and logs success. RPC notify callbacks set `online` on connect and clear it on disconnect. Multiplexed notify walks every attached service in a mux process and updates shared status.

`glusterd_muxsvc_conn_init()` builds a Unix transport RPC client for a mux process and registers `glusterd_muxsvc_conn_common_notify`. `glusterd_genericsvc_start()` builds common command arguments for bitd/scrub-like daemons and delegates to `glusterd_svc_start()`.

## State and Persistence Behavior
The file does not write glusterd metadata. It creates runtime directories and pid/socket/log paths and launches processes using generated volfiles from the workdir. Runtime state includes `svc->name`, `svc->conn`, `svc->proc`, `svc->online`, mux-process `status`, and RPC client references.

## Dependencies and Integration Points
It depends on glusterd process management, connection management, RPC transport, runner utilities, global command arguments, and SHD-specific path building for volume-level service volfiles. Service-specific modules such as NFS, quotad, bitd, scrub, SHD, snapd, and gfproxyd layer their own policy on top of these primitives.

## Risks and Edge Cases
The start path depends on the generated volfile being present and stable. It uses `attach_lock` around process launch and service attach activity, so changes can affect deadlock behavior. Some path builder functions assert `len == PATH_MAX`, which restricts safe reuse with smaller buffers. The mux notifier is explicitly glustershd-oriented, so adding other multiplexed services requires revisiting event names and service-name assumptions. `glusterd_svc_init_common()` only checks negative `snprintf()` returns for `svc->name`, not truncation.

## Test Signals
Tests should validate command construction under valgrind, localtime logging, daemon log-level, global threading, IO engine, and extra cmdline dictionaries. Process lifecycle tests should assert idempotent start, missing volfile failure, synchronous and no-wait start paths, stop cleanup of sockets and `online`, and RPC connect/disconnect event state transitions. Mux tests should validate all attached services update on shared connect/disconnect.
