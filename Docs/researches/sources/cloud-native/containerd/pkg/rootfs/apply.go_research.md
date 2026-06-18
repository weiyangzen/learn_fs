<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/apply.go -->
# sources/cloud-native/containerd/pkg/rootfs/apply.go

## Purpose
Applies OCI image layers into a snapshotter and returns the resulting chain ID digest.

## Important APIs, Types, And Functions
Layer carries Diff and Blob descriptors. ApplyLayers, ApplyLayersWithOpts, ApplyLayer, ApplyLayerWithOpts, applyLayers, and uniquePart implement multi-layer and single-layer unpack.

## Control Flow
Top-level calls compute chain IDs, stat existing snapshots, recursively prepare parents as needed, create a unique unpack key, call diff.Applier.Apply, verify computed diff digest, and commit the snapshot under the chain ID.

## State And Persistence
Persistent state is snapshotter metadata and filesystem content created by Prepare/Commit. Temporary active snapshots are removed on error. uniquePart adds time plus random bytes to reduce key collisions.

## Dependencies And Integration Points
Integrates core/diff Applier, snapshots.Snapshotter, mount.Mounts, errdefs, image-spec identity. Used by image unpack/rootfs setup flows.

## Risks And Edge Cases
Concurrent unpack relies on AlreadyExists handling and unique keys. Cleanup is best-effort. Diff digest mismatch aborts after extraction. rand.Read errors are ignored, reducing but not eliminating uniqueness.

## Test Signals
No direct tests here; exercised by unpack and content integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/apply.go -->
