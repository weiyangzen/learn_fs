# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.c

## Purpose
Manages the per-volume snapshot daemon service `snapd`: service hook setup, connection/process initialization, start/stop decisions based on USS/snapd enablement and volume status, process launch, restart across volumes, and RPC connection notifications.

## Important APIs, types, and functions
`glusterd_snapdsvc_build()` installs manager/start/stop hooks. `glusterd_snapdsvc_init()` creates rundir, socket connection, pidfile, volfile, per-volume snapd log directory, logfile, volfile id, and process metadata. `glusterd_snapdsvc_manager()` starts or stops the daemon based on `glusterd_is_snapd_enabled()` and volume status. `glusterd_snapdsvc_start()` builds and runs the `glusterfsd` command line, assigns a brick port through `pmap_assign_port()`, and passes listen-port xlator options. `glusterd_snapdsvc_restart()` iterates started volumes. `glusterd_snapdsvc_rpc_notify()` updates online state and volume refs on RPC events.

## Control flow
Manager initializes once, checks snapd enablement, stops snapd if enabled but the volume is stopped, otherwise creates a snapd volfile, starts the process, refs the volume, and connects RPC. If snapd is disabled and the process is running, it stops and clears `volinfo->snapd.port`. Start is idempotent when the process is already running. If the volfile is missing, start regenerates it for nodes that were down when USS was enabled. It optionally prefixes Valgrind args, adds localtime logging when configured, assigns a port, appends brick-port/listen-port/no-mem-accounting options, and runs synchronously or asynchronously depending on flags.

## State and persistence behavior
Runtime state includes `svc->inited`, `svc->online`, connection socket path, process metadata, `volinfo->snapd.port`, and a volume ref held while RPC is connected. Persistent artifacts are snapd volfiles, pidfiles, log directories/logfiles, and pmap port assignment. `RPC_CLNT_DESTROY` releases the volume ref acquired before connecting.

## Dependencies and integration points
Depends on generic service, connection, and process management; snapd path helpers; snapshot utility enablement and volfile generation; pmap port allocation; runner command execution; GlusterD options for bind address and localtime logging; and event notifications for service connect/disconnect/failure.

## Risks and test signals
Risks include leaked volume refs if connect fails after partial startup, stale `snapd.port` after abnormal process death, race between `glusterd_proc_is_running()` and runner launch, missing volfile recovery failure, and incorrect command-line ordering for `glusterfsd`. Tests should cover enabled/disabled transitions, stopped-volume stop branch, missing-volfile regeneration, port exhaustion, localtime and Valgrind args, async versus sync launch, restart iteration, RPC connect/disconnect/destroy notifications, and port clearing on stop.
