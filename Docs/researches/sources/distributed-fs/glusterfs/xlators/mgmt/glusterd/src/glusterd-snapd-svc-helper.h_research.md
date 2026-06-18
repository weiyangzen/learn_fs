# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.h

## Purpose
Declares snapd path-builder helpers shared by snapshot daemon service initialization and process startup.

## Important APIs, types, and functions
Declares `glusterd_svc_build_snapd_rundir()`, `glusterd_svc_build_snapd_socket_filepath()`, `glusterd_svc_build_snapd_pidfile()`, and `glusterd_svc_build_snapd_volfile()`.

## Control flow
The snapd service implementation calls these helpers during init to populate connection socket path, process pidfile, and volfile path before launching `glusterfsd`.

## State and persistence behavior
No state is stored in the header. The declared helpers determine the filesystem paths for runtime and persistent snapd artifacts.

## Dependencies and integration points
Relies on `glusterd_volinfo_t` being visible to includers. Used by `glusterd-snapd-svc.c` and any future status or cleanup code needing snapd paths.

## Risks and test signals
Header/implementation signature drift would break snapd service compilation. Tests should verify every declared path helper is used consistently by init/start and handles maximum path lengths.
