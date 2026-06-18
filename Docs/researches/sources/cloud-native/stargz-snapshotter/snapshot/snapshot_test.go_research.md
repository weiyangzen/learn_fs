<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go -->
# sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go

## Purpose
Tests remote snapshot behavior and overlayfs compatibility for the custom snapshotter.

## Important APIs, Types, And Functions
- `prepareWithTarget` asserts remote prepare returns `ErrAlreadyExists` and returns the committed target name.
- `TestRemotePrepare`, `TestRemoteOverlay`, `TestRemoteCommit`, and `TestFailureDetection` cover remote-specific flows.
- `bindFs` simulates a remote filesystem using bind mounts and configurable check failures.
- `dummyFs` supports overlay compatibility tests without remote mounting.
- Overlay tests cover containerd `SnapshotterSuite`, mounts, commits, reads, and views.

## Control Flow
Remote tests create temp roots, instantiate snapshotters, prepare remote layers with labels, optionally build overlay children, mount/read/write data, and remove snapshots. Failure detection builds stacks of remote and overlay layers, toggles `bindFs.checkFailure`, and expects unavailable errors. Overlay tests exercise normal snapshot lifecycle.

## State And Persistence
Tests create temp directories, bind mounts, snapshot metadata, and overlay dirs, then remove/unmount via defers. Some tests require root privileges.

## Dependencies And Integration Points
Depends on containerd snapshot testsuite, mount helpers, storage metadata access, `errdefs`, and root-capable Linux mount behavior.

## Risks And Edge Cases
Root and kernel overlay support are required for several tests. Bind mount cleanup relies on defers and snapshot removal. Failure cases depend on labels marking broken mountpoints.

## Test Signals
Strong signals include committed remote snapshots with target labels, expected bind/overlay mount options, persisted file contents through commit/readback, `ErrUnavailable` for broken remote parents, and containerd snapshotter suite compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go -->
