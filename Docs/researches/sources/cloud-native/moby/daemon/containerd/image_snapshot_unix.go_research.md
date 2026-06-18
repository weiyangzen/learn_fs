<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go

Purpose: implements Unix user-namespace ownership remapping for containerd snapshots and root filesystems.

Important APIs and flow: `remapSnapshot` prepares a snapshot then mounts it and calls `remapRootFS`. `remapRootFS` walks the mounted root and maps container IDs to host IDs. `copyAndUnremapRootFS` copies a mounted source to destination, then walks destination and maps host IDs back to container IDs while deduplicating hard-linked inodes. `unremapRootFS` maps an existing rootfs back to container IDs. `chownWithCaps` preserves xattrs across `Lchown`, downgrading version-3 file capabilities to version 2 and trimming to the expected length.

State and persistence: mutates snapshot filesystem ownership and extended attributes in mounted snapshot directories. It does not directly edit containerd metadata beyond the snapshot prepared in the caller.

Dependencies and integration: used by `createLayer` and migration/export-like code paths that need userns remap. Depends on containerd mounts, continuity file copy/xattr helpers, syscall stat data, and Moby `idMapping`.

Risks: full filesystem walks can be expensive. Any xattr read/set failure aborts the remap. Capability byte indexing assumes expected xattr layout and length. `remapSnapshot` does not clean up the prepared snapshot if remapping fails. Hard-link dedup is only in copy/unremap, not plain remap.

Test signals: no direct tests here; userns remap behavior needs integration coverage with real snapshotters and file capabilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go -->
