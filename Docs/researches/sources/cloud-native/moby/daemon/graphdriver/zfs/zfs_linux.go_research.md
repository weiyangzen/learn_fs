# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_linux.go

Purpose: Linux-specific ZFS graphdriver helpers.

Important APIs and control flow: `checkRootdirFs` reads filesystem magic for the root directory, maps it to a human-readable backing filesystem name, and returns `ErrPrerequisites` with an error log if it is not ZFS. `getMountpoint` returns the full layer ID unchanged.

State, dependencies, and risks: no persistent state. Dependencies include daemon fstype detection and graphdriver errors. The helper is used when `zfs.fsname` is not explicitly configured, so incorrect rootdir filesystem detection prevents ZFS auto-discovery. Tests for ZFS initialization and graphtest behavior indirectly exercise this on suitable hosts.
