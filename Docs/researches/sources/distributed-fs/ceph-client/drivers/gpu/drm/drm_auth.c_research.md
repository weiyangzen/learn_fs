# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_auth.c

## Purpose
`drm_auth.c` implements DRM primary-node master ownership and legacy authentication. It tracks `struct drm_master` groups, enforces which file is the current device master, supports GETMAGIC/AUTHMAGIC, handles SET_MASTER/DROP_MASTER, assigns implicit master on open, releases master state on close, integrates with leases, and lets internal DRM clients reserve the master mutex when no userspace master exists.

## Important APIs, Types, and Functions
`drm_is_current_master()` checks whether a file is the current master through its lease owner. `drm_getmagic()` and `drm_authmagic()` implement legacy magic authentication using the master's `magic_map`. `drm_master_create()`, `drm_master_get()`, `drm_file_get_master()`, `drm_master_put()`, and `drm_master_destroy()` manage master lifetime. `drm_setmaster_ioctl()` and `drm_dropmaster_ioctl()` implement public master ioctls with permission and lessee checks. `drm_master_open()` and `drm_master_release()` handle open/close behavior. `drm_master_internal_acquire()` and `drm_master_internal_release()` support kernel DRM clients such as fb helpers.

## Control Flow
On open, the first primary-node file becomes master if `dev->master` is NULL; later files take a reference to the current master. GETMAGIC allocates a per-file IDR magic under `dev->master_mutex`; AUTHMAGIC looks it up, authenticates the target file, and clears the IDR entry to prevent reuse. SET_MASTER checks rootless/CAP_SYS_ADMIN permission, rejects busy devices and lessees, creates a new master if needed, or installs the file's existing master. DROP_MASTER checks permission/current status and clears `dev->master` through the driver `master_drop` hook. Release removes magic IDs, drops current master when appropriate, revokes leases for real modeset masters, and drops references.

## State and Persistence Behavior
Persistent state includes `dev->master`, `drm_file.master`, `is_master`, `was_master`, `authenticated`, `magic`, the per-file `master_lookup_lock`, and each `drm_master`'s kref, `magic_map`, lease lists, and lease IDRs. `dev->master_mutex` serializes global master transitions and magic operations. `was_master` persists after a file once held master and is part of rootless SET/DROP permission logic.

## Dependencies and Integration Points
The file integrates with DRM file open/release paths, ioctl permission checks, driver `master_set`/`master_drop` callbacks, Linux capabilities, PID/TGID tracking, IDR, kref, and DRM leasing (`drm_lease_owner()`, `drm_lease_revoke()`, `drm_lease_destroy()`). Modesetting drivers rely on it to serialize display ownership among compositors, display managers, logind-style brokers, fbdev helpers, and legacy clients.

## Risks
Locking and reference mistakes can race master changes or free a master still referenced by files. Permission policy is compatibility-sensitive: requiring `CAP_SYS_ADMIN` too broadly breaks rootless compositors, but allowing SET/DROP too broadly lets clients disrupt the display server. Magic authentication must authenticate against the correct master and prevent reuse. Lease checks must keep lessees from becoming full device masters and revoke leases when a real master closes.

## Test Signals
Useful tests include first-open master assignment, multiple opens, SET_MASTER/DROP_MASTER with and without `CAP_SYS_ADMIN`, rootless compositor flows, logind FD passing, GETMAGIC/AUTHMAGIC success and bad-magic failure, lease revoke on master close, concurrent open/close/ioctl stress, driver callback ordering, and lockdep/KCSAN coverage around `master_mutex`, `master_lookup_lock`, and krefs.
