# Research: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot.go

This file implements a small in-memory snapshot usage cache. `Key` identifies a snapshot by logical key and snapshotter name, preventing collisions between snapshotters. `Snapshot` records the key, snapshot kind, size in bytes, inode count, and latest update timestamp in nanoseconds.

`Store` wraps a map from `Key` to `Snapshot` with an RW mutex. `NewStore` initializes the map. `Add` upserts a snapshot. `Get` returns a snapshot or `errdefs.ErrNotFound`. `List` returns a snapshot slice of current values. `Delete` removes a key without error.

There is no disk persistence in this package; it caches information gathered elsewhere, and consumers such as Windows pod stats use it to fill writable-layer usage. Dependencies are containerd snapshot kinds and errdefs. Risks include stale size/inode data if callers do not refresh it, map iteration order in `List`, no truncated lookup, and silent delete of missing keys. Tests cover add/get/list/delete and key separation by snapshotter.
