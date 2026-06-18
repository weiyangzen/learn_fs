## sources/cloud-native/buildkit/snapshot/diffapply_linux.go

Purpose: Linux implementation of merge snapshot diff application. It computes filesystem changes between lower/upper snapshots and applies them into a destination snapshot with metadata preservation, overlay whiteout handling, hardlink optimization, and corrected usage accounting.

Important APIs/types/functions: `mergeSnapshotter.diffApply` drives the process. `applierFor` resolves the destination root from bind/overlay/local mounts. `applier.Apply` sequences delete, hardlink, and copy paths. `applyCopy` preserves type, ownership, mode, xattrs, opaque dirs, and timestamps. `Usage` walks the apply root and avoids double-counting hardlinks, including cross-snapshot hardlinks. `differFor` mounts lower/upper views and selects overlay optimized changes or `fs.Changes`. `safeJoin` prevents unsafe path traversal. `needsUserXAttr` detects rootless overlay xattr mode via a temporary snapshot.

Control flow: for each `Diff`, committed snapshots are mounted as views and active snapshots via `Mounts`. A `differ` emits parent modifications and changes; the `applier` deletes/whiteouts old paths, links where possible, copies otherwise, defers directory mtimes, flushes mtimes after all changes, then reports usage.

State and persistence: writes directly into the destination snapshot upperdir/root. It records in-memory visited parents, inode maps, deferred mtimes, and cross-snapshot linked inodes. Persistent effects are filesystem contents and merge usage labels applied by `merge.go`.

Dependencies and integration points: tightly coupled to `mergeSnapshotter.Merge`, containerd continuity fs diffing, BuildKit overlay utilities, rootless mount options, leases, and Linux xattrs.

Risks and test signals: path safety, whiteout conversion, xattr failures, rootless overlay behavior, hardlink EXDEV/EMLINK fallback, and release ordering are critical. `snapshotter_test.go` covers merge ordering, metadata/mtime, hardlinks, capabilities, and usage across overlayfs/native variants.
