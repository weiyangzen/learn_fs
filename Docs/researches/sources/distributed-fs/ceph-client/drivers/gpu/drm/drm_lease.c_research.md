# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_lease.c

## Purpose

`drm_lease.c` implements DRM KMS leasing. Leasing lets a DRM master create another master that controls a subset of mode-setting objects, used by workflows such as VR compositors that need direct ownership of specific connectors/CRTCs/planes while the main compositor owns the rest. The code tracks lessor/lessee relationships, validates lease object sets, filters object visibility, creates lease file descriptors, lists/get/revokes leases, and destroys lease state.

## Important APIs, Types, And Functions

The key type is `struct drm_master`, specifically its `lessor`, `lessees`, `lessee_list`, `lessee_id`, `lessee_idr`, and `leases` fields. Important functions include `drm_lease_owner()`, `_drm_lease_held()`, `drm_lease_held()`, `drm_lease_filter_crtcs()`, `drm_lease_destroy()`, `drm_lease_revoke()`, `drm_mode_create_lease_ioctl()`, `drm_mode_list_lessees_ioctl()`, `drm_mode_get_lease_ioctl()`, and `drm_mode_revoke_lease_ioctl()`. Internal helpers include `_drm_find_lessee()`, `_drm_lease_held_master()`, `_drm_has_leased()`, `drm_lease_create()`, `_drm_lease_revoke()`, `validate_lease()`, and `fill_object_idr()`.

`drm_lease_idr_object` is a dummy non-NULL IDR payload used to represent membership in a lease set; actual mode objects are resolved through `dev->mode_config.object_idr`.

## Control Flow

Lease creation begins in `drm_mode_create_lease_ioctl()`. It requires `DRIVER_MODESET`, validates flags against `O_CLOEXEC | O_NONBLOCK`, obtains the current master, rejects sub-leasing, copies object IDs from userspace, and builds an IDR with `fill_object_idr()`. That helper resolves each object through `drm_mode_object_find()`, rejects non-leaseable object types, requires at least a CRTC and connector plus a plane when universal planes are enabled, adds IDs to the lease IDR, and auto-adds primary/cursor planes for leased CRTCs when universal planes are not enabled. The ioctl then allocates a file descriptor, creates the lessee master with `drm_lease_create()`, clones the lessor file, swaps the cloned file's master to the lessee, marks it master/authenticated, returns fd and lessee ID, and installs the fd.

`drm_lease_create()` validates under `mode_config.idr_mutex` that every requested object exists and has not already been leased by another lessee, assigns a lessee ID in the owner `lessee_idr`, links the lessee into the lessor list, and transfers ownership of the lease IDR. Lease queries and filtering also lock `idr_mutex`: `drm_lease_held()` checks membership for lessees and returns true for owners; `drm_lease_filter_crtcs()` remaps CRTC bitmasks to only visible CRTCs. Revocation empties lease IDRs for a lessee tree without destroying the master object, preserving references. Destruction removes a master from the owner IDR and lessor list and emits a sysfs lease event.

## State And Persistence

Leasing state persists in DRM master objects for as long as the relevant file descriptors/masters exist. Owners have `lessor == NULL` and an IDR of lessees. Lessees store leased object IDs in `leases` and reference their lessor. Revocation empties `leases`, while close/destruction removes the lessee from IDRs/lists and drops lessor references. Lease visibility affects subsequent KMS ioctl behavior elsewhere by making non-leased objects appear unavailable.

## Dependencies And Integration Points

The file depends on Linux file descriptor helpers, usercopy, IDR/list locking, DRM auth/master/file infrastructure, CRTC/mode object helpers, sysfs lease events, and core ioctl dispatch through declarations in `drm_crtc_internal.h` and `drm_internal.h`. KMS object lookup and object-type leaseability are provided by the mode configuration layer. The core ioctl table in `drm_ioctl.c` exposes the create/list/get/revoke lease ioctls with `DRM_MASTER` permissions.

## Risks And Edge Cases

Sub-leases are explicitly rejected, so the conceptual tree is limited even though revocation walks generically. Lease validation requires a connector and CRTC, and conditionally a plane; unusual users requesting non-display objects or incomplete sets receive `-EINVAL`. Duplicate IDs in the lease request fail through `idr_alloc()` with `-EEXIST`. `drm_mode_create_lease_ioctl()` assumes `drm_file_get_master()` returns a valid master and must unwind fd, IDR, lessee, and cloned file references exactly. Empty leases are allowed when `object_count == 0`, producing a lessee with no controllable objects. Listing lessees omits revoked leases by checking for non-empty lease IDRs.

## Test Signals

Test create/list/get/revoke using valid connector/CRTC/plane sets, duplicate IDs, invalid object IDs, non-leaseable object types, missing connector/CRTC/plane combinations, universal-plane on/off behavior, attempted sub-leases, object already leased to another lessee, empty leases, close-time destruction, sysfs lease uevents, CRTC mask filtering for lessees, and KMS ioctls against leased versus non-leased objects.
