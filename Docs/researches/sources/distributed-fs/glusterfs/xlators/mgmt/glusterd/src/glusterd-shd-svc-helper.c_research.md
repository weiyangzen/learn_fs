# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.c

## Purpose
Provides helper routines for per-volume self-heal daemon service paths, multiplexed service cleanup, and pidfile dictionary export.

## Important APIs, types, and functions
`glusterd_svc_build_shd_socket_filepath()` builds the SHD Unix socket path from the volume SHD rundir and local UUID, then shortens/normalizes it with `glusterd_set_socket_filepath()`. `glusterd_svc_build_shd_pidfile()` and `glusterd_svc_build_shd_volfile_path()` build per-volume pidfile and volfile paths. `glusterd_shd_svcproc_cleanup()` detaches a volume SHD service from its mux process, unrefs RPC clients, removes pidfiles, and marks service state uninitialized. `glusterd_svc_set_shd_pidfile()` adds the pidfile to a dict.

## Control flow
Path builders are leaf functions that return early if `THIS->private` is unavailable. Cleanup first drops the service's direct RPC ref, then under `conf->attach_lock` detaches list nodes, clears `svc_proc`, resets `inited`, unlinks the pidfile, and if the mux process has no services removes it from `conf->shd_procs`. The mux RPC unref is intentionally performed after releasing the attach lock.

## State and persistence behavior
Persistent filesystem effects are pidfile removal and use of generated workdir/rundir paths. Runtime state includes `shd->attached`, `svc->conn.rpc`, `svc->svc_proc`, `svc->inited`, `svc->mux_svc`, and mux-process lists. `glusterd_svc_set_shd_pidfile()` exports state to a dictionary for status or node operations.

## Dependencies and integration points
Depends on SHD path macros, generic service helper path shortening, RPC refcounting, GlusterD attach-lock discipline, and `glusterd-shd-svc.h` service structures. Used by SHD init/start/stop and management status paths.

## Risks and test signals
Risks include list corruption during detach, unrefing mux RPC while pending events still reference `svc_proc`, missing cleanup when `THIS->private` is null, and pidfile path truncation. Tests should cover cleanup of last and non-last service in a mux process, RPC ref release outside the lock, pidfile dict export, and socket/pid/volfile path construction for long volume names.
