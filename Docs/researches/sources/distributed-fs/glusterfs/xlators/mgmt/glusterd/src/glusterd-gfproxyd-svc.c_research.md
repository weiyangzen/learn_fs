# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.c

## Purpose

`glusterd-gfproxyd-svc.c` implements the GlusterD service lifecycle for the per-volume `gfproxyd` process. It wires the service vtable, initializes connection/process metadata, creates gfproxyd volfiles, starts and stops `glusterfsd` as gfproxyd, restarts gfproxyd for all started volumes, and decides whether reconfiguration can be handled in place or requires a manager restart. The file was reviewed as a complete 450-line source.

## Important APIs, Types, and Functions

Public functions are `glusterd_gfproxydsvc_build`, `glusterd_gfproxydsvc_stop`, `glusterd_gfproxydsvc_init`, `glusterd_gfproxydsvc_manager`, `glusterd_gfproxydsvc_start`, `glusterd_gfproxydsvc_restart`, and `glusterd_gfproxydsvc_reconfigure`. The file-local `glusterd_gfproxydsvc_create_volfile` wraps `glusterd_generate_gfproxyd_volfile()` with logging.

`glusterd_gfproxydsvc_build()` assigns the service's manager/start/stop/reconfigure callbacks. `glusterd_gfproxydsvc_init()` populates `svc->name`, creates the rundir and logdir, initializes RPC connection state on the gfproxyd Unix socket, and initializes process metadata with pidfile, logfile, volfile, volfile ID, and volfile server. `glusterd_gfproxydsvc_start()` assembles the `glusterfsd` command line.

## Control Flow

Manager flow first initializes the service if needed. It reads `VKEY_CONFIG_GFPROXY` through `glusterd_is_gfproxyd_enabled()`. If gfproxy is enabled but the volume is not started, it stops any running gfproxyd. If gfproxy is enabled and the volume is started, it regenerates the volfile, stops any current gfproxyd, starts a new process, references the volume, and connects the service RPC connection. If gfproxy is disabled while the process is running, it stops the service.

Start flow ensures the volfile exists, optionally wraps the command in Valgrind according to daemon command-line settings, builds a gfproxyd brick id, runs `SBIN_DIR/glusterfsd` with `-s <volfileserver>`, `--volfile-id gfproxyd/<volname>`, pid/log paths, `--brick-name`, `-S <socket>`, optional memory accounting and localtime logging, and assigned brick-port/listen-port xlator options. It uses `pmap_assign_port()` to allocate or reuse `volinfo->gfproxyd.port` and supports both no-wait and synchronous execution, releasing `priv->big_lock` around synchronous process execution.

Reconfigure flow checks whether the service is initialized, enabled, and running. It compares current and generated volfiles byte-for-byte; if identical, nothing happens. If only options changed and topology is identical, it regenerates the volfile and calls `glusterd_fetchspec_notify(THIS)` so the running process fetches updated specs. If topology changed or prerequisites are not met, it delegates to the manager for a stop/start path. Restart flow iterates all started volumes in `conf->volumes` and calls each gfproxyd manager with `PROC_START_NO_WAIT`.

## State and Persistence Behavior

The service state is embedded in `volinfo->gfproxyd.svc`; the port is stored in `volinfo->gfproxyd.port` and reset to zero on stop. Runtime artifacts are pid files, sockets, volfiles, and logs derived by the helper file. The generated volfile is persisted under the volume directory as `<volname>.gfproxyd.vol`. The code does not write volume metadata directly, but it relies on volinfo status/options and updates in-memory process/connection state.

## Dependencies and Integration Points

The implementation depends on generic GlusterD service helpers (`glusterd_svc_stop`, `glusterd_svc_create_rundir`, `glusterd_conn_init`, `glusterd_conn_connect`, `glusterd_proc_init`, `glusterd_proc_is_running`), volfile generation (`glusterd_generate_gfproxyd_volfile`), volfile comparison helpers from `glusterd-gfproxyd-svc-helper.c`, port-map assignment, event reporting through `gf_event(EVENT_SVC_MANAGER_FAILED, ...)`, and `glusterfsd` process startup. It integrates with volume lifecycle by inspecting `glusterd_is_volume_started(volinfo)` and with daemon options such as bind address, Valgrind tool, memory accounting, and localtime logging.

## Risks and Edge Cases

The manager intentionally stops before every enabled-volume start, so startup failures can leave gfproxyd down after a previously running instance was stopped. A failed `glusterd_conn_connect()` unreferences the volume and reports service-manager failure, but the process may already have been started. Port assignment must remain consistent with the generated volfile and `--xlator-option <volname>-server.listen-port`. Long names can stress volfile IDs, brick names, log paths, and socket paths. Reconfigure correctness depends on topology comparison accurately distinguishing restart-required graph changes from live-updateable option changes.

## Test Signals

Useful tests include manager behavior for enabled/disabled gfproxy across started/stopped volumes, missing-volfile creation on start, no-wait versus synchronous start paths, port reuse/reset on restart/stop, localtime and memory-accounting argument inclusion, Valgrind argument construction, byte-identical and topology-identical reconfigure paths, fetchspec notification for option-only changes, and failure cases for logdir creation, process init, process start, and connection failure.
