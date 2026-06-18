# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.h

## Purpose

`glusterd-nfs-svc.h` exposes the legacy Gluster NFS service integration points. Its declarations are guarded by `BUILD_GNFS`, matching the conditional implementation in `glusterd-nfs-svc.c`.

## Important APIs

When `BUILD_GNFS` is enabled, the header declares `glusterd_nfssvc_build(glusterd_svc_t *svc)` to install NFS service callbacks and `glusterd_nfssvc_reconfigure(void)` to compare/regenerate/reconfigure or restart the running service. It includes `glusterd-svc-mgmt.h` for `glusterd_svc_t`.

## Control flow and state contract

Consumers call `glusterd_nfssvc_build()` during service setup, then invoke `glusterd_nfssvc_reconfigure()` after volume option or topology changes that may affect the NFS graph. The header makes NFS support a compile-time feature: callers must either be inside `#ifdef BUILD_GNFS` or tolerate the declarations being absent.

## Dependencies and integration points

The header depends on the generic GlusterD service-management type definitions. Its implementation integrates with volfile generation, service process lifecycle, pmap deregistration, and `nfs/server.so` availability.

## Risks and test signals

The main risk is build-configuration drift: code that calls these functions without the same `BUILD_GNFS` guard will fail in GNFS-disabled builds. Build matrix coverage should compile both GNFS-enabled and disabled configurations. Functional tests should verify that service callback wiring and reconfiguration behavior are reachable only in enabled builds.
