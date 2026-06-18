## sources/cloud-native/buildkit/snapshot/snapshotter_test.go

Purpose: Linux integration tests for merge snapshot behavior across overlayfs, native, and native without cross-snapshot hardlinks.

Important APIs/types/functions: `newSnapshotter` builds a containerd metadata DB, content store, lease manager, and merge snapshotter in a test namespace. Helpers `activeKey`, `committedKey`, `mergeKey`, `withMount`, `requireContents`, `statPath`, and capability helpers create and inspect snapshots. `TestMerge`, `TestHardlinks`, `TestMergeFileCapabilities`, and `TestUsage` cover the main behavior.

Control flow: tests create multiple committed snapshots with additions, removals, hardlinks, symlinks, renames, metadata changes, and file capabilities; merge different diff sequences; mount results; and compare full directory contents plus mtimes, link counts, capabilities, ownership, and usage.

State and persistence: all state is under `t.TempDir`, bbolt metadata DB, containerd snapshotter directories, and temporary leases. Cleanup closes DB/snapshotters.

Dependencies and integration points: exercises `merge.go`, `diffapply_linux.go`, local mounters, containerd metadata, native/overlay snapshotters, continuity fstest, and libcap.

Risks and test signals: root is required for overlayfs and capability tests. These tests are strong regression signals for merge correctness, but platform-gated to Linux and may skip parts in unprivileged environments.
