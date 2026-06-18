# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_types.h

## Purpose
Defines `struct xe_gsc`, the per-GT GSC uC state object embedded in `struct xe_uc`.

## Important Types and Fields
- `fw`: generic Xe uC firmware object for discovery, status, version, and blob BO.
- `security_version`: SVN from the fetched firmware blob.
- `private`: private BO assigned to GSC firmware after load.
- `q`: default GSCCS exec queue used for firmware load and packet submission.
- `wq`, `work`, `lock`, `work_actions`: ordered async execution state for firmware load, proxy handling, and reset-complete actions.
- `proxy`: MEI component pointer, mutex, state flags, GSC BO/map halves, and CSME CPU buffers.

## State and Persistence
This state persists across the GT lifetime and is partially preserved across GT reset because firmware can remain loaded. `work_actions` is a bitmask updated under a spinlock; proxy component usage is serialized by a mutex.

## Dependencies and Integration
Includes uC firmware types, device types, iosys maps, workqueue, spinlock, and mutex primitives. The structure is consumed by GSC firmware load, proxy, submit, debugfs, and uC container code.

## Risks and Test Signals
- Workqueue and queue pointers are optional until post-hwconfig init; callers must check firmware loadability and queue presence.
- Proxy buffers split a single BO and a single CPU allocation into two directional halves; any size changes must preserve this invariant.
