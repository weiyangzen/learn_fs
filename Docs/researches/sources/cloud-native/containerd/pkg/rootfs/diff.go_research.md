<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/diff.go -->
# sources/cloud-native/containerd/pkg/rootfs/diff.go

## Purpose
Creates an OCI layer diff descriptor by comparing a snapshot with its parent.

## Important APIs, Types, And Functions
CreateDiff stats a snapshot, creates a parent view, chooses active mounts or an upper view, and calls diff.Comparer.Compare.

## Control Flow
The function always prepares a temporary lower parent view, then either mounts an active upper snapshot or creates a temporary readonly view for committed snapshots before comparing.

## State And Persistence
Temporary snapshot views are removed via internal cleanup. The returned descriptor is persisted by whatever content writer the comparer uses.

## Dependencies And Integration Points
Depends on snapshots.Snapshotter, diff.Comparer, mount.Mount, and cleanup helpers. Used by image export/commit workflows.

## Risks And Edge Cases
Assumes the snapshot has a valid Parent; root snapshots need snapshotter behavior that tolerates empty parent. Cleanup ignores remove errors through cleanup.Do.

## Test Signals
Covered indirectly by diff/export integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/diff.go -->
