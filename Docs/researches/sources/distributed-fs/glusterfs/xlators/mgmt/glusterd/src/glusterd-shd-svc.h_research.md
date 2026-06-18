# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.h

## Purpose
Declares the self-heal daemon service wrapper and lifecycle API for per-volume `glustershd` management.

## Important APIs, types, and functions
`glusterd_shdsvc_t` contains a `glusterd_svc_t svc` and `gf_boolean_t attached` indicating mux/process attachment. Declared functions are `glusterd_shdsvc_build()`, `glusterd_shdsvc_init()`, `glusterd_shdsvc_manager()`, `glusterd_shdsvc_start()`, `glusterd_shdsvc_reconfigure()`, `glusterd_shdsvc_restart()`, and `glusterd_shdsvc_stop()`.

## Control flow
Volume initialization builds the service hooks; lifecycle callers then use manager/start/stop/reconfigure to converge the per-volume SHD service with volume status and compatibility.

## State and persistence behavior
The header exposes the service container and `attached` state but performs no persistence. The implementation persists volfiles, pidfiles, node-state store data, and process logs.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h` and forward-declares `glusterd_volinfo_t`. Used by volume metadata structures, SHD helper functions, and GlusterD service orchestration.

## Risks and test signals
Tests should verify lifecycle hook installation, attached-state transitions through start/stop, and compile-time agreement between this header and `glusterd-shd-svc.c`.
