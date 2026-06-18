# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLog.java

## Purpose

`FSEditLog.java` is the NameNode edit-log writer and reader selector. It maintains the transaction ID stream for namespace mutations, writes `FSEditLogOp` records to a `JournalSet`, syncs edits durably, manages edit-log segment lifecycle, exposes manifests and input streams for recovery/standby/checkpoint readers, and supports local, shared, backup, and plugin journal managers.

The source was read as a complete 1929-line file for this report.

## Important APIs, Types, and Functions

Core state: private `State` enum (`UNINITIALIZED`, `BETWEEN_LOG_SEGMENTS`, `IN_SEGMENT`, `OPEN_FOR_READING`, `CLOSED`), `journalSet`, `editLogStream`, monotonically increasing `txid`, last synced `synctxid`, current segment start `curSegmentTxId`, `isSyncRunning`, `isAutoSyncScheduled`, metrics counters, `NNStorage`, `Configuration`, edit directories, shared edit directories, operation cache, proxy users, and `journalSetLock`.

Construction/initialization: `newInstance` chooses `FSEditLogAsync` when `dfs.namenode.edits.async.logging` is enabled. `initJournalsForWrite`, `initSharedJournalsForRead`, and `initJournals` build a `JournalSet` with file journals or plugin journals and required/shared flags.

Write/sync core: `openForWrite`, `logEdit(FSEditLogOp)`, `doEditTransaction`, `beginTransaction`, `endTransaction`, `logSync`, `logSync(long)`, `logSyncAll`, `waitIfAutoSyncScheduled`, `doneWithAutoSyncScheduling`, `waitForSyncToFinish`, `getLastWrittenTxId`, `setNextTxId`, `getSyncTxId`, and metrics helpers.

Operation logging APIs: `logOpenFile`, `logCloseFile`, `logAppendFile`, `logAddBlock`, `logUpdateBlocks`, `logMkDir`, rename overloads, `logSetReplication`, `logSetStoragePolicy`, `logSetQuota`, `logSetQuotaByStorageType`, `logSetPermissions`, `logSetOwner`, `logConcat`, `logDelete`, `logTruncate`, generation stamp/block ID logging, `logTimes`, `logSymlink`, delegation token/master key logging, `logReassignLease`, snapshot logging, cache directive/pool logging, rolling upgrade logging, ACL/xattr logging, and erasure-coding policy logging.

Segment/journal lifecycle: `rollEditLog`, `startLogSegment`, `startLogSegmentAndWriteHeaderTxn`, `endCurrentLogSegment`, `abortCurrentLogSegment`, `purgeLogsOlderThan`, `recoverUnclosedStreams`, shared-log upgrade/finalize/rollback methods, `discardSegments`, backup node registration and release, `journal` for raw backup-node batches, and `logEdit(int, byte[])`.

Read selection/plugin APIs: `selectInputStreams` overloads, `checkForGaps`, `closeAllStreams`, `getEditLogManifest`, `getJournalClass`, `createJournal`, `getJournals`, `getJournalSet`, and test hooks.

## Control Flow

The write lifecycle begins in `UNINITIALIZED`, calls `initJournalsForWrite`, enters `BETWEEN_LOG_SEGMENTS`, then `openForWrite` verifies there is no readable stream at the next transaction ID before starting a segment and writing an `OP_START_LOG_SEGMENT` header transaction. While `IN_SEGMENT`, each operation-specific `log*` method populates an `FSEditLogOp`, optionally records RPC IDs for retry-cache reconstruction, and delegates to `logEdit`.

Synchronous `logEdit` is synchronized while assigning the next transaction ID and writing to the in-memory edit-log stream. If the stream's policy requests a forced sync, the caller marks `isAutoSyncScheduled`, exits the synchronized block, and calls `logSync`. Other writers wait while an auto sync is scheduled to preserve ordering around forced flushes.

`logSync(long)` implements the double-buffered sync protocol. Under the monitor, it waits for any active sync that already covers the caller's txid, sets `isSyncRunning`, captures `editLogStream`, checks journal availability, and calls `setReadyToFlush`. Outside the monitor it flushes to the journals. In `finally`, it updates `synctxid`, updates file-journal readable txid, clears `isSyncRunning`, and notifies waiters. Fatal inability to sync enough journals terminates the NameNode.

Rolling a log ends the current segment by optionally logging `OP_END_LOG_SEGMENT`, calling `logSyncAll`, asserting last-written equals last-synced, finalizing the segment in `JournalSet`, and returning to `BETWEEN_LOG_SEGMENTS`; then it starts the next segment and writes a header transaction.

Standby/checkpoint/recovery readers call `selectInputStreams`, which asks `JournalSet` for streams under `journalSetLock`, then checks that selected ranges cover the requested interval unless recovery mode allows gaps.

## State and Persistence Behavior

The durable state is a sequence of edit-log transactions spread across configured journals. `txid` advances before each write, `synctxid` advances only after successful flush, and `curSegmentTxId` names the in-progress segment. The thread-local `myTransactionId` lets each caller sync only through the edits it produced, while sync batching may flush additional transactions.

`JournalSet` abstracts multiple journal destinations and enforces the minimum redundant journals policy. Local `FileJournalManager` instances are tied to `NNStorage` directories; non-file journal managers are plugin-created from configuration; backup journals stream edits to backup NameNodes. Shared journals support HA standby reading and upgrade/rollback methods.

RPC IDs are persisted into selected operations when requested so edit-log replay can rebuild retry-cache entries and preserve idempotent client semantics after failover or restart.

Segment records (`OP_START_LOG_SEGMENT`, `OP_END_LOG_SEGMENT`) make log boundaries explicit. Purging is allowed only while open for write to avoid standby NameNodes deleting shared edits.

## Dependencies and Integration Points

`FSEditLog` depends on `FSEditLogOp` and its many concrete op types for serialization payloads. It integrates with `JournalSet`, `JournalManager`, `FileJournalManager`, `BackupJournalManager`, `EditLogOutputStream`, `EditLogInputStream`, `RemoteEditLogManifest`, and `LogsPurgeable`.

NameNode integration includes `NNStorage`, `FSNamesystem` edit/shared directory configuration, `NamespaceInfo`, `NamenodeRegistration`, `NameNodeMetrics`, `NameNode.getClientIdAndCallId`, `ExitUtil.terminate`, and storage upgrade/finalize/rollback hooks.

Namespace integration comes from the operation log methods accepting `INodeFile`, `INode`, blocks, ACLs, xattrs, snapshots, cache directives/pools, delegation tokens, storage policies, and erasure-coding policies. The paired `FSEditLogLoader` replays these op types into `FSDirectory`, `BlockManager`, and other managers.

## Risks and Edge Cases

The state machine is strict. Starting a segment at the wrong txid, opening for write when newer readable streams exist, or reducing txid via `setNextTxId` is guarded because any violation risks edit-log fork or data loss.

Sync failure is intentionally fatal when not enough journals can flush. Tests that mock journals need to account for `ExitUtil.terminate` behavior. The unsynchronized flush window is safe only because callers needing isolation call `waitForSyncToFinish`.

`isAutoSyncScheduled` prevents writes from racing ahead of a forced sync, but bugs around `doneWithAutoSyncScheduling` can block writers. The code uses `finally` to avoid runtime exceptions leaving the flag set.

Read stream selection assumes sorted, non-overlapping ranges from `JournalSet`; `checkForGaps` is deliberately simple and will reject missing txids unless recovery mode is active. In-progress streams have unknown end txid and are accepted only when allowed.

Plugin journal construction is reflection-based and supports two constructor signatures. Misconfiguration fails at runtime with `IllegalArgumentException`.

## Test Signals

Useful coverage includes state-machine tests for initialization, open, close, roll, abort, and recovery; transaction ID monotonicity and `setNextTxId` validation; multi-threaded log/sync batching tests; forced-sync scheduling tests; journal quorum failure tests that assert termination or exception behavior; segment finalization and purge tests; HA shared-edits input stream selection and gap detection; backup-node raw journal batch tests; plugin journal constructor tests; retry-cache RPC ID logging checks; and operation serialization/replay round trips with `FSEditLogLoader`.
