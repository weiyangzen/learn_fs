<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux_test.go -->
# sources/cloud-native/containerd/core/mount/mount_linux_test.go

Purpose: Linux tests for mount option helpers, real mount behavior, recursive cleanup, FUSE helper integration, and idmapped overlay lowerdir preparation.

Important APIs/types/functions: `TestLongestCommonPrefix`, `TestCompactLowerdirOption`, `TestFUSEHelper`, `TestMountAt`, `TestUnmountMounts`, `TestUnmountRecursive`, `TestDoPrepareIDMappedOverlayCleanups`, `TestDoPrepareIDMappedOverlay`, `TestGetUnprivilegedMountFlags`, `setupMounts`, `supportsIDMap`, `TestBuildIDMappedPaths`, `TestGetCommonDirectory`, and `TestXContainerdOptionsFiltered`.

Control flow: non-root-safe helpers test string/path logic directly; root tests mount bind/tmpfs/FUSE/idmapped trees, read files through mount points, and verify cleanup. IDMapped overlay tests create lowerdirs, remap a common parent, assert content appears through rewritten paths, and simulate busy cleanup failures.

State and persistence: creates temporary directories and real kernel mounts; tests clean up with `Unmount`, `UnmountAll`, or cleanup callbacks.

Dependencies and integration points: requires root for most mount syscalls, optional `fuse-overlayfs`, and idmap-capable kernel/filesystem for idmapped tests. Exercises functions used by `mount_linux.go` during normal `Mount.Mount`.

Risks covered: page-size compaction path correctness, working-directory isolation in `mountAt`, preservation of original lowerdirs during idmapped overlay cleanup, and rejection of unconsumed `X-containerd.*` options.

Test signals: high coverage but many environment skips/requirements. It complements pure parser checks with actual kernel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux_test.go -->
