# Research: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot_test.go

This test file validates the snapshot store's keying and basic operations. `TestSnapshotStore` creates three snapshots: two keys in one snapshotter and one same logical key in a different snapshotter. It adds them, retrieves each by full `Key`, lists all snapshots, attempts to delete an invalid key, deletes one valid key, and verifies the deleted key returns an empty snapshot plus `errdefs.ErrNotFound`.

The test confirms that `Key{Key, Snapshotter}` is the identity, not just the snapshot key string, and that delete is a no-op for missing keys. It also covers different snapshot kinds and metadata fields in stored values.

The test signal is intentionally narrow. It does not exercise concurrent access, stale update replacement semantics beyond initial add, ordering of `List`, or integration with image filesystem stats. It guards the in-memory cache behavior used by CRI stats paths, especially writable-layer lookup by container ID plus runtime snapshotter.
