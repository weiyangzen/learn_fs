## sources/cloud-native/buildkit/snapshot/merge.go

Purpose: wraps a snapshotter with a `Merge` operation that materializes a committed snapshot from a list of diffs, using Linux diff application and storing corrected usage for hardlink-based merges.

Important APIs/types/functions: `Diff` names lower and upper snapshot keys. `MergeSnapshotter` extends `Snapshotter` with `Merge`. `NewMergeSnapshotter` configures hardlink merge, overlay base skipping, and rootless userxattr behavior. `Merge` chooses a base key, creates a temporary lease, prepares a destination snapshot, applies diffs, and commits with usage labels. `Usage` returns stored merge usage when labels exist. `withMergeUsage` and `mergeUsageOf` encode/decode size and inode labels.

Control flow: overlay-based snapshotters can skip an initial chain of diffs that already matches parent relationships and use the last upper as the merge parent. A temporary lease protects views and prepared snapshots during merge. `diffApply` returns usage, then `Commit` persists it as labels.

State and persistence: persistent state is the committed snapshot plus labels `buildkit.mergeUsageSize` and `buildkit.mergeUsageInodes`. Runtime flags choose hardlink and xattr behavior.

Dependencies and integration points: depends on leases, user namespace detection, `needsUserXAttr`, and the underlying snapshotter. Tests exercise native/overlay behavior.

Risks and test signals: userxattr detection failures disable optimizations. Commit failure after prepare may leave cleanup to snapshotter/lease GC. Usage label parse errors make `Usage` fail. `snapshotter_test.go` covers merge content, hardlinks, file capabilities, and usage.
