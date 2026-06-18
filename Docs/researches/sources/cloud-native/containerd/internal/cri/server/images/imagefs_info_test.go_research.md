
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go

## Purpose

This test file validates image filesystem usage aggregation from cached snapshot usage entries.

## Important APIs, Types, and Functions

It defines `TestImageFsInfo`, using `newTestCRIService`, `snapshotstore.Snapshot`, `(*GRPCCRIImageService).ImageFsInfo`, and CRI `FilesystemUsage`.

## Control Flow

The test adds three overlayfs snapshots with active, committed, and view kinds, different sizes, inode counts, and timestamps. It calls `ImageFsInfo`, expects two entries because the service also emits the default snapshotter entry first, and asserts that the overlayfs entry sums size and inodes and uses the oldest timestamp.

## State and Persistence Behavior

The test uses only the in-memory snapshot store. No live snapshotter usage calls or filesystem stat calls occur.

## Dependencies and Integration Points

Dependencies include containerd snapshot kind constants, CRI snapshot store, CRI runtime API, and assertion libraries. The test protects kubelet-facing imagefs stats behavior.

## Risks and Edge Cases

The test does not validate zero default snapshotter details, multiple non-default snapshotter ordering, missing mountpoint mapping, or content-store usage omission.

## Test Signals

Passing tests confirm per-snapshotter aggregation and timestamp selection in image filesystem stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go -->
