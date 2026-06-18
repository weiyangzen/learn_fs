# File Research: sources/block-storage/mdadm/tests/func.sh

## Purpose
Shared bash helper library for mdadm shell tests.

## Main Responsibilities
- Defines expected sizes for metadata formats and test devices.
- Provides colored output helpers and log preservation.
- Implements cleanup for loop, LVM, and disk backends.
- Verifies root, required commands, mdadm availability, absence of existing RAID arrays, and kernel support for multipath/linear.
- Sets up loop/LVM/ram/disk test devices and systemd environment variables for IMSM tests.
- Records/restores SELinux and RAID speed-limit settings.
- Provides test assertions through `check()`, covering RAID level, state, bitmap, readonly, inactive, chunk size, resync/recovery/reshape presence, and absence of sync.
- Provides filesystem/device validation helpers such as `testdev()` and `rotest()`.

## Integration
Sourced by `test`; individual tests rely on its globals (`dev0`, `md0`, sizes, flags) and assertions.

## Risks and Edge Cases
- Test setup is destructive to selected devices and requires a clean host md environment.
- `restore_system_speed_limit()` appears to write both saved min and max values to `speed_limit_max`, leaving `speed_limit_min` unrestored; this may be intentional typo-compatible behavior, but it looks like a bug.
- SELinux helpers assume `getenforce`/`setenforce` are available.
