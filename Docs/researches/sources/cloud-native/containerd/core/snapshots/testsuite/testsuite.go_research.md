# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite.go

## Purpose
This file defines a reusable conformance suite for implementations of `snapshots.Snapshotter`. `SnapshotterSuite` takes a snapshotter factory and runs a broad set of behavioral tests covering active, committed, and view snapshots; filesystem layering semantics; metadata updates; filtering; removal; readonly views; close idempotency; root permissions; rename behavior; and deep layer stacks.

## Important APIs, Types, and Functions
`SnapshotterFunc` is the factory contract. `SnapshotterSuite` wires named subtests through `makeTest`, which creates a temporary root/work directory, installs a namespace and mount manager, initializes the snapshotter, and dumps the temp tree on failure. Helpers include `snapshotterPrepareMount`, `baseTestSnapshots`, `assertLabels`, and the package-level `opt` label set with `containerd.io/gc.root`.

## Control Flow
Each test prepares snapshots, mounts returned mounts into the work tree, mutates files with `fstest` appliers or `os.WriteFile`, unmounts, commits, stats, walks, views, and removes snapshots. The suite validates both data-plane file visibility and metadata-plane fields such as kind, parent, timestamps, labels, and filter results.

## State and Persistence
State is persisted through the snapshotter under a per-test root. The tests assert key lifecycle transitions: `Prepare` creates active snapshots, `Commit` removes the active key and creates a committed key, `View` creates readonly views, and `Remove` must reject committed parents while children exist. Labels are updated and filtered, with GC-root labels intentionally kept.

## Dependencies and Integration Points
The suite depends on `github.com/containerd/containerd/v2/core/snapshots`, mount manager helpers, `continuity/fs/fstest`, namespace context, and test utilities. Platform-specific helpers in `testsuite_unix.go` and `testsuite_windows.go` supply umask handling.

## Risks
Tests use real mounts, filesystem permissions, and platform behavior, so failures may reflect host capabilities as much as snapshotter bugs. Several cases require careful cleanup after mount failures. The 128-layer test stresses mount option limits and may expose snapshotter-specific constraints.

## Test Signals
This is itself a test suite. Strong signals include transitive parent checks, immutable field rejection, label field-path updates, view readonly enforcement through an actual write attempt, whiteout/delete semantics, file move behavior, walk filters, root permissions, close twice, and deep layering consistency.
