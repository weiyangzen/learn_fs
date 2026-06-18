<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java

## Purpose
Exercises `RaftSnapshotManager` snapshot download behavior across a small in-process cluster made from lightweight `SnapshotDirStateMachineStorage` instances and gRPC `RaftJournalServiceHandler` servers. It verifies that a master with no local snapshot can discover and copy the highest reachable snapshot from peer masters.

## Important APIs, Types, And Functions
- `before()` builds three Ratis state-machine storages, exposes them through Alluxio gRPC servers, configures `MASTER_RPC_ADDRESSES`, then creates one `RaftSnapshotManager` per server.
- `downloadSnapshotFromOtherMasters()` and `waitForAttemptToComplete()` are the tested manager APIs.
- `createStateMachineStorage`, `createGrpcServer`, `createSampleSnapshot`, and `directoriesEqual` are reusable test helpers for other Raft snapshot tests.

## Control Flow
Each test arranges peer snapshot directories and server availability, asks manager 0 to download, waits for the asynchronous attempt, and compares returned log index plus directory contents. The manager is expected to skip unavailable peers, prefer higher term/index snapshots, and tolerate repeated attempts after prior success or failure.

## State And Persistence Behavior
State lives in temporary Ratis storage directories and snapshot subdirectories named with Ratis `SimpleStateMachineStorage` term/index naming. Sample snapshots contain files plus saved MD5 sidecars. No persistent repository data is touched.

## Dependencies And Integration Points
Depends on Alluxio configuration, gRPC server builders, `RaftJournalServiceHandler`, Apache Ratis storage and MD5 utilities, commons-io directory traversal, and JUnit temporary folders. It covers the network-facing snapshot exchange path rather than only local storage APIs.

## Risks And Edge Cases
Tests use random available ports and local host addressing, so host resolution and port reuse can make failures environment-sensitive. `successThenFailureThenSuccess` recreates a gRPC server on the same port and is a useful regression guard for cached snapshot clients.

## Test Signals
Passing tests signal correct no-snapshot handling, successful peer copy, resilience to one unavailable peer, highest-snapshot selection, fallback when the highest peer is down, and recovery after a failed cached-client attempt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java -->
