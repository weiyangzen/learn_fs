# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.c

## Purpose
Manages per-volume `glustershd` self-heal daemon services, including mux-process initialization, volfile generation, process start/attach/detach, reconfiguration, restart across all volumes, and stop/cleanup behavior.

## Important APIs, types, and functions
`glusterd_shdsvc_build()` initializes service hooks. `glusterd_shdsvc_init()` prepares connection and process metadata for either an existing mux connection or a new mux process. `glusterd_shdsvc_create_volfile()` generates a self-heal volfile with forced heal options for compatible volumes or removes stale volfiles for incompatible volumes. `glusterd_svcs_shd_compatible_volumes_stopped()` inspects mux members. `glusterd_shdsvc_manager()` serializes SHD restarts with `conf->restart_shd`. `glusterd_new_shd_svc_start()`, `glusterd_recover_shd_attach_failure()`, `glusterd_shdsvc_start()`, `glusterd_shdsvc_reconfigure()`, `glusterd_shdsvc_restart()`, and `glusterd_shdsvc_stop()` implement lifecycle operations.

## Control flow
The manager skips snapshot volumes, waits for any existing SHD restart, refs the volume, stops incompatible initialized services, creates a volfile, initializes mux state, then stops when all compatible mux members are stopped or starts only when the volume is started. Start initializes mux state if needed, attaches to an existing running process when `shd->attached` is true, or launches a new `glusterfsd` process with self-heald client pid and local node UUID xlator option. Reconfigure compares generated volfile and topology with a graph-check dictionary, uses fetchspec notification for option-only changes, and delegates to the manager for topology changes. Stop removes the service from the mux list, stops the whole process if it was the last service, otherwise detaches only this volume, marks offline, unlinks the pidfile, and calls shared cleanup.

## State and persistence behavior
Runtime state spans `volinfo->shd`, `glusterd_svc_t`, mux process lists, RPC refs, `svc->online`, `svc->inited`, `shd->attached`, and the restart condition variable. Persistent state includes per-volume SHD volfiles, pidfiles, node-state store updates, and potentially process logs. Generated volfiles force background self-heal count to zero and data/metadata/entry self-heal on.

## Dependencies and integration points
Depends on generic svc/proc/conn management, mux service attach/detach APIs, volfile generation (`glusterd_shdsvc_generate_volfile`), volume compatibility checks, store APIs, fetchspec notification, and process command-line construction. It integrates with volume start/stop/reconfigure, peer detach cleanup, daemon restart on GlusterD restart, and status/node operations through SHD helper functions.

## Risks and test signals
Risks include a likely iterator bug in `glusterd_svcs_shd_compatible_volumes_stopped()` where `cds_list_entry(svc, ...)` uses the original service instead of `temp_svc`, races around mux attach/detach cleanup, leaked volume refs on attach failures, serialized restart condition not being broadcast, and stale pidfiles/volfiles for incompatible volumes. Tests should cover compatible and incompatible volume transitions, all-volumes-stopped behavior, attach failure recovery, detach from shared mux process, last-service stop, reconfigure identical/topology-identical/topology-changed cases, snapshot-volume skip, and restart across started volumes.
