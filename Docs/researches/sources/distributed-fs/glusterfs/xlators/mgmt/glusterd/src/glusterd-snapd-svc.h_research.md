# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.h

## Purpose
Declares the per-volume snapshot daemon service wrapper and lifecycle API for `snapd`.

## Important APIs, types, and functions
`glusterd_snapdsvc_t` wraps `glusterd_svc_t svc`, a `gf_store_handle_t *handle`, and the assigned daemon `port`. Declared functions are `glusterd_snapdsvc_build()`, `glusterd_snapdsvc_init()`, `glusterd_snapdsvc_manager()`, `glusterd_snapdsvc_start()`, `glusterd_snapdsvc_restart()`, and `glusterd_snapdsvc_rpc_notify()`.

## Control flow
Volume setup builds hooks, manager initializes and starts/stops based on snapd enablement and volume status, start launches `glusterfsd`, restart applies the manager to all started volumes, and RPC notify maintains online/ref state.

## State and persistence behavior
The header exposes the service and port fields. Implementation persists volfiles, pidfiles, logs, and port assignment indirectly through process management and volume metadata.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`, which provides service and connection types. Used by volume metadata, snapd service implementation, and any service orchestration code that restarts or observes snapd.

## Risks and test signals
Tests should compile all lifecycle users and verify the `port` field is updated and cleared by start/stop paths while RPC notify releases the correct volume reference.
