# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.c

## Purpose
`fallback.c` implements the legacy sysfs firmware fallback path used when direct filesystem/platform lookup fails or when fallback is forced.

## Important APIs, Types, And Functions
Key APIs are `firmware_fallback_sysfs()`, `kill_pending_fw_fallback_reqs()`, `fw_fallback_set_cache_timeout()`, and `fw_fallback_set_default_timeout()`. Internals include `pending_fw_head`, `fw_load_sysfs_fallback()`, `fw_load_from_user_helper()`, `fw_force_sysfs_fallback()`, and `fw_run_sysfs_fallback()`.

## Control Flow, State, And Persistence
Fallback creates a `fw_sysfs` device, enables paged-buffer loading when no destination buffer exists, adds the firmware request to the pending list under `fw_lock`, optionally sends a uevent with firmware name/timeout/async state, then waits for userspace to complete or abort via sysfs `loading`. Non-uevent/custom fallback waits indefinitely. On timeout or signal, the path aborts the request and deletes the sysfs device. Cache mode temporarily shortens the timeout.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysfs loader devices, usermodehelper read locks, LSM `security_kernel_load_data()`, firmware fallback sysctl state, and `fw_priv` completion. Risks include indefinite lingering for custom fallback, interaction with `ignore_sysfs_fallback` and forced fallback, abort races, module shutdown deadlocks, and security policy denial. Test signals include forced fallback, ignored fallback, no-fallback request flags, uevent contents, timeout, custom no-uevent path, suspend/shutdown abort, and userspace writes completing paged-buffer loads.
