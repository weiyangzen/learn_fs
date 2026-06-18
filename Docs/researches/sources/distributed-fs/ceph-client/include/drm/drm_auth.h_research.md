# sources/distributed-fs/ceph-client/include/drm/drm_auth.h

## Purpose
This internal DRM header defines master ownership, authentication token storage, and leasing metadata for legacy/primary DRM nodes. It captures who is current master, which files can access privileged operations, and how display-resource leases relate lessors and lessees.

## Important APIs, types, and functions
`struct drm_master` contains a kref, parent device, bus-unique string, magic-token IDR, driver-private data, lessor pointer, lessee id, lessee lists, leased-object IDR, and owner lessee IDR. Public functions are `drm_master_get`, `drm_file_get_master`, `drm_master_put`, `drm_is_current_master`, and `drm_master_create`.

## Control Flow
DRM file open/master transitions create or reference master objects. Authentication tokens are tracked in `magic_map`. Lease creation links a lessee master to a lessor and populates lease IDRs. Current-master checks gate privileged IOCTL behavior.

## State and Persistence
Master state is in-memory and scoped to a DRM device, open files, and lease lifetime. It persists across individual IOCTL calls until master drop, device close, lease revocation, or device teardown. Locking is split between `master_mutex` for unique/auth data and `mode_config.idr_mutex` for lease IDRs/lists.

## Dependencies and Integration Points
It depends on `idr`, `kref`, DRM file objects, device master locking, and mode-config object ID management. It integrates with DRM authentication, primary node semantics, and display-resource leasing.

## Risks and Test Signals
Risks include refcount leaks, use-after-free across file close, lock-order mistakes between master and mode-config mutexes, stale magic tokens, and lease revocation leaving object IDs accessible. Tests should cover master create/drop, file master reference acquisition, current-master changes, nested lessee teardown, lessor lifetime while lessees exist, and authenticated versus unauthenticated IOCTL access.
