<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/snapshot_test.go -->
# sources/cloud-native/containerd/integration/client/snapshot_test.go

## Purpose
Runs the shared snapshotter test suite against the daemon's default remote snapshotter client.

## APIs, Types, And Functions
`newSnapshotter` returns a `snapshots.Snapshotter`, cleanup function, and error for the testsuite. `TestSnapshotterClient` invokes `testsuite.SnapshotterSuite` with `defaults.DefaultSnapshotter`.

## Control Flow And State
The helper opens a containerd client, obtains `client.SnapshotService(defaults.DefaultSnapshotter)`, and returns a cleanup function that closes the client. The testsuite performs the actual snapshot operations.

## Persistence And Integration Points
The suite mutates snapshotter metadata and mounts through the running daemon. It integrates the remote snapshot service with the common snapshotter testsuite.

## Risks And Test Signals
Failures indicate the default snapshotter's remote client does not satisfy the standard snapshotter contract for prepare/view/commit/remove/walk/stat behavior. The test is skipped in short mode because it drives a full integration suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/snapshot_test.go -->
