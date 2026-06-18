<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go

Purpose: unit-tests native bind/overlay mount option construction.

Important tests: `TestMountNative` table-drives active/view/committed snapshots with zero, one, and multiple parents, asserting bind mounts or overlay mounts with expected `workdir`, `upperdir`, `lowerdir`, and `volatile` options. `TestMountNativeConfigVolatile` verifies config-level volatile is applied only to active snapshots.

Control flow and state: tests construct a minimal `snapshotter{root: ...}` without filesystem or metadata store and call `mountNative` directly.

Dependencies/integration: uses containerd mount/snapshot/storage types and testify require/assert.

Risks and test signals: good coverage for native mount formatting, but it does not exercise remote nydus mounts, tarfs/Kata volume options, snapshot metadata transactions, cleanup, or Prepare/View control flow.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go -->
