# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotListing.java

## Purpose
`TestSnapshotListing` verifies `.snapshot` directory listing semantics for a snapshottable directory. It ensures root snapshot listing behaves specially, non-snapshottable directories reject `.snapshot` listing, empty snapshottable directories list no snapshots, and snapshot create/delete operations are reflected in sorted listing results.

## Important APIs, Types, and Functions
The suite uses `MiniDFSCluster`, `DistributedFileSystem`, `FileStatus`, `Path`, `FSNamesystem`, and `GenericTestUtils.assertExceptionContains`. The sole test method is `testListSnapshots`.

## Control Flow
The setup creates `/test.snapshot/dir`. The test first lists `/.snapshot` and expects an empty result because root has zero snapshot quota by default. It then attempts to list `<dir>/.snapshot` before `allowSnapshot` and expects a `SnapshotException` surfaced as `IOException`. After enabling snapshots, it checks the empty listing, creates five snapshots `s_0` through `s_4`, verifying the listing length and names after each creation, then deletes snapshots in reverse order and verifies the listing shrinks while retaining the remaining names. Finally it deletes the last snapshot and expects an empty listing.

## State and Persistence Behavior
This file does not restart the NameNode. State is the in-memory and namespace-backed snapshot list of a single snapshottable directory. The expected order is stable by snapshot name/creation sequence used by the directory listing API.

## Dependencies and Integration Points
It integrates filesystem path resolution of the reserved `.snapshot` component with snapshot manager state and `FileSystem#listStatus` behavior.

## Risks and Edge Cases
Risks covered include exposing `.snapshot` on non-snapshottable directories, incorrectly reporting root snapshots, stale list entries after deletion, and unstable ordering while snapshots are added and removed.

## Test Signals
The test gives direct signals through list length checks, entry-name assertions after each mutation, and the exact non-snapshottable error substring.
