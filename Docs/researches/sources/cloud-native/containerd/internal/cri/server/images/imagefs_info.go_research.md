
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go -->
# sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go

## Purpose

This file implements CRI `ImageFsInfo`, aggregating cached snapshot usage into filesystem usage entries grouped by snapshotter.

## Important APIs, Types, and Functions

The primary function is `(*CRIImageService).ImageFsInfo`. It reads `c.snapshotStore.List`, groups by `snapshotter`, and emits `runtime.FilesystemUsage` entries with mountpoints from `c.imageFSPaths`.

## Control Flow

The function walks cached snapshots and aggregates size and inode counts per snapshotter while preserving the oldest timestamp in each group. It emits the default snapshotter first for kubelet compatibility. If the default snapshotter has no cached usage, it emits a zero-usage entry with the current timestamp. It then appends entries for remaining snapshotters.

## State and Persistence Behavior

The function is read-only over cached snapshot usage. The cache is maintained asynchronously by `snapshotsSyncer`. It does not query the content store or live snapshotters directly and does not persist state.

## Dependencies and Integration Points

Dependencies include CRI snapshot store and CRI runtime API. It integrates with kubelet image filesystem stats and with the snapshot syncer started by `NewService`.

## Risks and Edge Cases

Content store disk usage is explicitly not counted. Windows usage is noted as unsupported. Snapshotter map iteration order for non-default snapshotters is not deterministic. Missing `imageFSPaths` entries can yield empty mountpoints.

## Test Signals

The adjacent test verifies aggregation, oldest timestamp selection, default snapshotter first-entry behavior, and mountpoint mapping for a non-default snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go -->
