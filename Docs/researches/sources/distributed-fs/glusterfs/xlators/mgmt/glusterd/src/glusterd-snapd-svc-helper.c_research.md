# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.c

## Purpose
Builds per-volume snapshot daemon directory, socket, pidfile, and volfile paths used by `snapd` service management.

## Important APIs, types, and functions
`glusterd_svc_build_snapd_rundir()` returns the volume pid directory. `glusterd_svc_build_snapd_socket_filepath()` appends `run-<MY_UUID>` inside that rundir and passes it to `glusterd_set_socket_filepath()`. `glusterd_svc_build_snapd_pidfile()` builds `<rundir>/<volname>-snapd.pid`. `glusterd_svc_build_snapd_volfile()` builds `<volume-dir>/<volname>-snapd.vol`.

## Control flow
Each helper derives paths from `THIS->private` and volume macros. Socket construction protects against `snprintf()` overflow by clearing the intermediate path before shortening/normalizing it.

## State and persistence behavior
The functions do not mutate service state directly; they define the persistent filesystem locations for snapd sockets, pidfiles, and volfiles. Their outputs are later stored in `glusterd_svc_t` process and connection fields.

## Dependencies and integration points
Depends on `glusterd.h`, `glusterd-utils.h`, volume directory macros, local UUID formatting, and generic socket-path shortening. Used by `glusterd-snapd-svc.c` during init and start.

## Risks and test signals
Risks include path truncation, null `THIS->private` assumptions, and inconsistent path generation across init/start/status. Tests should cover long volume names, long workdirs, socket path shortening, and path agreement with snapd process metadata.
