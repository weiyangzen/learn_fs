# sources/cloud-native/moby/daemon/containerd/image_commit.go

## Purpose
Creates a new image from a container's current filesystem and commit configuration using containerd diff, content, snapshots, and OCI image config generation.

## Important APIs, Types, And Functions
- `CommitImage` is the main commit API.
- `generateCommitImageConfig` builds the new Docker OCI image config and history entry.
- `createDiff` exports a diff layer and handles idmapped rootfs unremapping.
- `applyDiffLayer` applies the produced diff to a snapshot chain for the new image.
- `uniquePart`, `cleanup`, and `CommitBuildStep` support temporary keys and builder shim behavior.

## Control Flow
Commit loads the container and parent manifest/config if present, creates a lease, exports a diff between container snapshot and parent, generates updated rootfs/history/config, applies non-empty diffs into a new chain snapshot, appends the layer descriptor, and delegates image/content creation to `createImageOCI`. Empty diffs create a history entry marked `EmptyLayer` without adding a layer.

## State And Persistence
Reads container state from the container store, creates temporary view/prepare snapshots, writes diff content, commits new snapshots, writes image manifests/configs through `createImageOCI`, and persists parent labels/content labels. Cleanup defers remove temporary snapshots with timeout contexts where possible.

## Dependencies And Integration Points
Depends on containerd differ/applier/snapshotter/content, OCI identity chain IDs, archive empty-diff detection, daemon idmapping copy/unremap helpers, backend commit configs, and classic builder shim APIs.

## Risks And Edge Cases
Idmapped rootfs handling creates whole-snapshot copies in some cases and can be expensive. Empty diffs must still update history correctly. Cleanup is best effort, relying on leases and GC if snapshot removal fails. Missing parent manifests are valid for `FROM scratch`, so callers must tolerate nil parent state.

## Test Signals
No direct tests in this subset. Integration tests should cover commits from scratch and parent images, empty/non-empty diffs, idmapped containers, history generation, and builder `CommitBuildStep`.
