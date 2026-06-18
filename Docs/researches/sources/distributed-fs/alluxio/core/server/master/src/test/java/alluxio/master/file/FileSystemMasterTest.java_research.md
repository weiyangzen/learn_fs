# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTest.java

## Purpose
This large parameterized unit test covers broad `FileSystemMaster` behavior: path creation, recursive delete against persisted UFS trees, ID/path lookup, block info, ACL/default ACL rules, TTL delete/free, attribute mutation, free semantics, mount/unmount validation, worker heartbeat integration, lost-file detection, UFS info lookup, fingerprint persistence, invalid UFS file filtering, persistence propagation, xAttr update/propagation, read-only write denial, recursive journal flushing, and `exists` with sync/no-sync contexts.

## Important APIs, Types, and Functions
- Parameterization runs the suite with `MASTER_FILE_SYSTEM_MERGE_INODE_JOURNALS` disabled and enabled, with forced flush max entries set to zero in the merged-journal case.
- Persistent delete helpers exercise `delete` with `DeletePOptions.recursive`, `alluxioOnly`, and `unchecked`.
- TTL tests use `HeartbeatScheduler.execute(HeartbeatContext.MASTER_TTL_CHECK)` and `TtlAction.FREE`.
- Free tests call `mFileSystemMaster.free` and verify block removal through `BlockMaster.workerHeartbeat`.
- Mount tests cover read-only mounts, shadow mounts, prefix/suffix UFS mount rejection, unmount behavior, and root/non-mount errors.
- `RecursiveDeleteForceFlushJournals()` spies `createJournalContext(true)` to count flushes and closes.
- xAttr tests cover `TRUNCATE`, `UNION_REPLACE`, `UNION_PRESERVE`, `DELETE_KEYS`, and creation-time propagation via `XAttrPropagationStrategy.NEW_PATHS` or `LEAF_NODE`.

## Control Flow
The test suite builds on `FileSystemMasterTestBase`. Most tests create an Alluxio tree, optionally mirror or mutate UFS state, call a master API, and then inspect `FileInfo`, inode IDs, UFS filesystem paths, block locations, journal replay after `stopServices`/`startServices`, or thrown exceptions. The mounted persisted directory tests construct a deterministic UFS tree, load it into Alluxio, introduce synced or unsynced entries, and assert what remains after delete.

## State and Persistence Behavior
Persistent state coverage is substantial. Restart/replay is tested for TTL delete/free, UFS fingerprint updates, and persistence propagation. Recursive delete tests verify UFS files/directories and Alluxio inode IDs are removed consistently. TTL free keeps metadata but removes block locations. Lost-file detection changes persistence state from `NOT_PERSISTED` to `LOST`. Journal flush behavior is checked under merged inode journals.

## Dependencies and Integration Points
The class integrates `DefaultFileSystemMaster` with block master state, worker heartbeats, journal contexts, UFS mounts, local filesystem temp paths, ACL authorization, TTL heartbeat scheduling, metrics/test registry setup, `FileSystemOptionsUtils`, protobuf options, and wire types such as `FileInfo`, `FileBlockInfo`, `FileSystemCommand`, and `UfsInfo`.

## Risks
- Because the class is broad, failures can arise from shared fixture assumptions rather than the API under direct test.
- Parameterized journal behavior means tests must be valid in both merged and unmerged journal modes.
- TTL and worker heartbeat tests depend on manual heartbeat execution and block-master state synchronization.
- Recursive delete tests mix Alluxio metadata deletion with real local filesystem deletion and can be sensitive to UFS sync-check semantics.
- Some tests use deprecated `ExpectedException` style and may stop at first expected failure, leaving later assertions unreachable by design.

## Test Signals
Signals include exact inode existence/invalid ID checks, `FileInfo` field values, thrown `AccessControlException`, `InvalidPathException`, `UnexpectedAlluxioException`, `FileDoesNotExistException`, block location counts, worker heartbeat command types, UFS path existence, replayed metadata after restart, xAttr map contents, ACL entries, and flush/close counts in recursive journal deletion.
