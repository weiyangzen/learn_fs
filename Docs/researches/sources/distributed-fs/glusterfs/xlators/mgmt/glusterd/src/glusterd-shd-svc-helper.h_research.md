# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.h

## Purpose
Declares helper APIs used by SHD service management for path building, mux cleanup, attach-failure recovery, volfile generation, and pidfile export.

## Important APIs, types, and functions
Declared functions are `glusterd_svc_build_shd_socket_filepath()`, `glusterd_svc_build_shd_pidfile()`, `glusterd_svc_build_shd_volfile_path()`, `glusterd_shd_svcproc_cleanup()`, `glusterd_recover_shd_attach_failure()`, `glusterd_shdsvc_create_volfile()`, and `glusterd_svc_set_shd_pidfile()`.

## Control flow
The implementation file provides the path builders, cleanup, and pidfile export; `glusterd-shd-svc.c` provides attach-failure recovery and volfile generation. Callers use these helpers around SHD mux initialization, start, stop, and status payload construction.

## State and persistence behavior
The header itself holds no state. Its functions operate on `glusterd_volinfo_t`, `glusterd_shdsvc_t`, `glusterd_svc_t`, mux process state, generated volfiles, pidfiles, and dictionaries.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`, which supplies service, volume, and dictionary-related types. It is the shared contract between SHD service implementation and generic GlusterD service helpers.

## Risks and test signals
Because some declarations are implemented outside the helper C file, signature drift can silently break service orchestration at compile time. Tests should include build coverage and start/stop/status paths that touch every declared function.
