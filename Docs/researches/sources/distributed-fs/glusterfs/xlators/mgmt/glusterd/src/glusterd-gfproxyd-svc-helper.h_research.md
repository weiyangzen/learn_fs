# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.h

## Purpose

`glusterd-gfproxyd-svc-helper.h` declares the helper surface for the GlusterD gfproxyd service implementation. It exposes path builders, volfile comparison helpers, the gfproxy enabled check, and the generic-service-to-volume conversion used by the service manager. The file was reviewed as a complete 51-line header.

## Important APIs, Types, and Functions

The declarations are `glusterd_svc_build_gfproxyd_rundir`, `glusterd_svc_build_gfproxyd_socket_filepath`, `glusterd_svc_build_gfproxyd_pidfile`, `glusterd_svc_build_gfproxyd_volfile_path`, `glusterd_svc_build_gfproxyd_logdir`, `glusterd_svc_build_gfproxyd_logfile`, `glusterd_svc_check_gfproxyd_volfile_identical`, `glusterd_svc_check_gfproxyd_topology_identical`, `glusterd_is_gfproxyd_enabled`, and `glusterd_gfproxyd_volinfo_from_svc`.

## Control Flow

The header has no executable flow. Its callers use the path builders during service initialization, the comparison helpers during reconfiguration, and `glusterd_is_gfproxyd_enabled()` in manager decisions.

## State and Persistence Behavior

No state is owned here. The declared functions operate on caller-provided buffers, `glusterd_volinfo_t`, and `glusterd_svc_t`. The implementation derives file paths for pid, socket, volfile, and log artifacts but persistence belongs to the service and volfile layers.

## Dependencies and Integration Points

The header includes `glusterd.h` for service and volume types. It is included by both the gfproxyd service implementation and any other GlusterD code that needs to compare gfproxyd volfiles or derive gfproxyd runtime paths.

## Risks and Edge Cases

All path-builder APIs take raw character buffers and lengths; callers must pass buffers large enough for GlusterD path conventions. The header does not annotate ownership for comparison helper outputs because allocation is implementation-local, so misuse is mostly prevented by the narrow function signatures.

## Test Signals

Compile tests should catch declaration drift between the helper header and implementation. Runtime coverage should come through gfproxyd init, start, reconfigure, and restart tests that exercise every declared helper.
