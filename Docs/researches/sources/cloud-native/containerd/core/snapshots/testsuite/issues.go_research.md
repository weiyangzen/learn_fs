# sources/cloud-native/containerd/core/snapshots/testsuite/issues.go

## Purpose
Captures regression tests for historical filesystem layering bugs in snapshotter implementations.

## APIs, Flow, State, Dependencies, Risks, And Tests
`checkLayerFileUpdate` repeatedly verifies overwriting files and modes across layers, sleeping to cross timestamp boundaries. `checkRemoveDirectoryInLowerLayer` verifies removal/recreation of lower-layer directories. `checkChown` validates ownership changes except on Windows. `checkRename` returns a test function that accounts for overlay-style directory rename limitations while still testing file rename/overwrite cases. `checkDirectoryPermissionOnCommit` validates directory ownership/mode preservation across remove/recreate and commit. `checkStatInWalk` creates named snapshots and calls `Stat` from inside `Walk`. `createNamedSnapshots` builds a small committed/active/view graph.

State is all in the supplied snapshotter and temp work dirs through helper functions. Dependencies include fstest, runtime GOOS, strings, testing, time, and snapshots.

Integration is the snapshotter conformance suite. Risks covered include copy-up bugs, whiteout/remove behavior, chown/permission preservation, rename semantics, timestamp-sensitive failures, and deadlocks when statting during walk. Some listed TODO issue checks remain comments, not implemented tests.
