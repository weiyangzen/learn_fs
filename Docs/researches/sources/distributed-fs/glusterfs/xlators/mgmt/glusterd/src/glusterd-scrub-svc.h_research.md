# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.h

## Purpose
Declares the GlusterD scrub service wrapper and lifecycle API used to manage the bitrot scrub daemon.

## Important APIs, types, and functions
`glusterd_scrubsvc_t` wraps `glusterd_svc_t svc` plus a `gf_store_handle_t *handle`. Declared functions are `glusterd_scrubsvc_build()`, `glusterd_scrubsvc_init()`, `glusterd_scrubsvc_manager()`, `glusterd_scrubsvc_stop()`, and `glusterd_scrubsvc_reconfigure()`.

## Control flow
Callers build the service hook table, initialize it through the manager or explicit init, then use the manager/reconfigure entry points to converge process state with current bitrot and topology options.

## State and persistence behavior
The header exposes the scrub service state container but does not itself persist data. The handle field suggests compatibility with GlusterD store-backed service metadata, while the implementation mainly uses shared service process/connection state and generated volfiles.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`; used by GlusterD service orchestration and the scrub service implementation. It sits alongside bitd/scrub volfile generation and service restart plumbing.

## Risks and test signals
Header drift between declarations and implementation would break daemon orchestration. Tests should compile lifecycle users and verify build/init/manager/reconfigure hooks are installed on the expected `glusterd_svc_t`.
