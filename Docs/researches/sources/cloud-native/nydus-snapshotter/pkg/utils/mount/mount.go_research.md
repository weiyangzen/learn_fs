<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go

Purpose: provides common mountpoint detection, unmount, and wait-for-unmount helpers.

Important APIs/types: `Interface`, `Mounter`, `Mounter.Umount`, `NormalizePath`, `IsMountpoint`, and `WaitUntilUnmounted`. `Umount` first verifies the target is a mountpoint, then calls `syscall.Unmount(target, 0)`.

Control flow and state: `NormalizePath` resolves to an absolute symlink-evaluated path and stats it. `IsMountpoint` treats `/` as mounted and otherwise compares the device number of the path against its parent. `WaitUntilUnmounted` retries `IsMountpoint` up to 20 times with 50 ms delay and returns only the last error.

Dependencies/integration: uses `retry.Do` and project `errdefs.ErrDeviceBusy` to model still-mounted state. Mount detection follows traditional Unix device-boundary semantics.

Risks and test signals: bind mounts on the same device may not be detected by device comparison alone. `Umount` returns `"not mounted"` for non-mountpoints, which callers may need to treat as benign. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go -->
