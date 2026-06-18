# sources/cloud-native/composefs-rs/crates/composefs/src/mountcompat.rs

## Purpose
This module isolates Linux kernel compatibility differences for composefs mounting. It provides alternate implementations for overlayfs fd options, detached mount preparation, and EROFS image mountability based on Cargo features for pre-6.15 and RHEL9-like kernels.

## Important APIs, Types, and Functions
Public helpers are `overlayfs_set_fd()`, `overlayfs_set_lower_and_data_fds()`, `make_erofs_mountable()`, and `prepare_mount()`. Default builds pass fds directly via `fsconfig_set_fd()`, pass EROFS image fds through unchanged, and leave detached mounts as-is. With `pre-6.15`, overlay layer options use string `/proc/self/fd` paths and `prepare_mount()` returns a temporary mounted directory fd through `tmpmount::TmpMount`. With `rhel9`, `make_erofs_mountable()` calls `loopify()`.

## Control Flow
Feature flags select entire implementations at compile time. The pre-6.15 lower/data path constructs either `/proc/self/fd/lower` or `/proc/self/fd/lower::/proc/self/fd/data` and sets `lowerdir`. `TmpMount::mount()` creates a temporary directory, moves the detached mount there, opens it with `O_PATH|O_DIRECTORY|O_CLOEXEC`, and returns a guard object. Dropping the guard detaches the mount. RHEL9 loop support delegates to `composefs_ioctls::loop_device::loopify()`.

## State and Persistence Behavior
Default helpers create no extra persistent state. The pre-6.15 temp mount path temporarily mutates the mount namespace and creates a temporary directory that is cleaned on drop. The RHEL9 path creates loop device state managed by the lower helper. String-based `/proc/self/fd` options rely on the referenced fds staying open through fsconfig.

## Dependencies and Integration Points
`mount.rs` calls these helpers rather than branching on kernel features itself. The module depends on `rustix` mount/fs APIs, `tempfile` for temp mountpoints under `pre-6.15`, and `composefs-ioctls` loop helpers under `rhel9`. It also uses `crate::util::proc_self_fd()` for fd path conversion.

## Risks and Edge Cases
Feature selection must match target kernel behavior. The comments note overlayfs `fsconfig_set_fd()` support differences around Linux 6.13 and detached mount limitations before 6.15. Temp mounts depend on `Drop` for cleanup; leaked guards can leave mounts until process exit or manual cleanup. `/proc/self/fd` string options are sensitive to fd lifetime and namespace behavior.

## Test Signals
There are no direct unit tests. Practical validation requires feature-matrix integration tests on representative kernels: modern, pre-6.15, and RHEL9. Tests should verify temp mount cleanup and loop-device release.
