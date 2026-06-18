# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogLoader.java

## Purpose

`FSEditLogLoader.java` replays edit-log transactions into the NameNode's in-memory state. It reads `FSEditLogOp` records from an `EditLogInputStream`, validates transaction ID ordering, applies each operation to `FSDirectory`, `BlockManager`, leases, snapshot/cache/token/erasure-coding managers, updates retry-cache entries, tracks startup progress, and provides edit-log scan/validation helpers.

The source was read as a complete 1446-line file for this report.

## Important APIs, Types, and Functions

Core state: `fsNamesys`, `blockManager`, injected `Timer`, `lastAppliedTxId`, `totalEdits`, replay log throttling constants, and `LOAD_EDITS_LOG_HELPER`.

Replay APIs: `loadFSEdits` overloads acquire the global write lock, record startup progress, call `loadEditRecords`, close streams, and log throttled load summaries. `loadEditRecords` performs the main read/validate/apply loop with optional `maxTxnsToRead`, `StartupOption`, and `MetaRecoveryContext`.

Apply helpers: `getAndUpdateLastInodeId`, `applyEditLogOp`, `addNewBlock`, `updateBlocks`, `formatEditLogReplayError`, `dumpOpCounts`, `incrOpCount`, and `check203UpgradeFailure`.

Validation utilities: static `scanEditLog`, nested `EditLogValidation`, nested `PositionTrackingInputStream implements StreamLimiter`, `getLastAppliedTxId`, and `createStartupProgressStep`.

Opcode coverage in `applyEditLogOp` includes file create/open/close/append/update/add-block, replication, concat, rename, delete, mkdir, generation stamps, block IDs, permissions/owner/quota/times/symlink, delegation tokens, leases, log segment markers, snapshots, rolling upgrades, cache directives/pools, ACLs, xattrs, truncate, storage policy, and erasure-coding policy add/enable/disable/remove.

## Control Flow

`loadFSEdits` begins a startup-progress step, acquires the global `FSNamesystem` write lock, logs a throttled start message, invokes `loadEditRecords`, logs a throttled completion summary, closes the stream, releases the lock, and ends the progress step.

`loadEditRecords` also acquires global and directory write locks, initializes expected txid and inode-id state, then loops reading `FSEditLogOp` records. Read failures produce a replay error with recent opcode offsets. Without recovery context, the loader throws `EditLogInputException`; with recovery, it prompts and resyncs. Transaction gaps and out-of-order txids are handled through `MetaRecoveryContext` prompts; out-of-order edits are skipped.

For each decoded op, `applyEditLogOp` mutates in-memory state. After successful apply, op counts and startup counters are incremented, `lastAppliedTxId` and `expectedTxId` advance, periodic replay progress is logged, and max transaction limits are honored. In `finally`, the directory inode ID counter is reset to the highest seen value, optional stream closure happens, locks are released, and debug op counts can be dumped.

`applyEditLogOp` is a large opcode switch. File operations resolve upgrade-renamed reserved paths, update or create `INodeFile` instances, adjust leases, update blocks, complete blocks, and reconstruct retry-cache payloads. Namespace operations delegate to unprotected or edit-log-specific methods in `FSDir*Op` helpers. Manager operations call into delegation-token secret manager, snapshot manager, cache manager, rolling-upgrade hooks, and erasure-coding policy manager.

Block replay is split between `addNewBlock` and `updateBlocks`. These verify block ID/generation-stamp continuity, complete prior blocks as needed, update generation stamps, remove abandoned blocks, add contiguous or striped `BlockInfo` instances, attach them to the file and `BlockManager`, and process queued DataNode messages.

## State and Persistence Behavior

The loader consumes persisted edit-log records and reconstructs volatile NameNode state. It updates `lastAppliedTxId` as replay progresses and restores `FSDirectory`'s last inode ID so subsequent allocations do not collide with persisted inode IDs. Old logs without inode IDs allocate new IDs unless the layout version claims inode-ID support, in which case a grandfather ID is an error.

Retry-cache state is reconstructed when the NameNode has retry cache enabled and an op contains RPC IDs. Some operations store only completion, while create/append/snapshot/cache-policy operations may store payloads such as `HdfsFileStatus`, `LastBlockWithStatus`, snapshot path, directive ID, or EC policy.

Rolling-upgrade records can stop replay for rollback, start rolling-upgrade state, trigger rollback checkpoints, finalize upgrade state, update storage version, and rename rollback images.

`scanEditLog` is non-mutating validation: it scans operations up to a requested txid, resyncs after corrupt sections, and returns valid length and end txid. `PositionTrackingInputStream` supports bounded reads for edit-log parsing by tracking current position and enforcing a temporary byte limit.

## Dependencies and Integration Points

The loader is the main consumer of `FSEditLogOp` records produced by `FSEditLog`. It integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `BlockIdManager`, `LeaseManager`, `SnapshotManager`, `CacheManager`, delegation token secret manager, erasure-coding policy manager, `FSImage`, startup progress, `MetaRecoveryContext`, layout-version compatibility, and rolling-upgrade startup options.

Namespace mutations are delegated to operation helpers including `FSDirWriteFileOp`, `FSDirAppendOp`, `FSDirDeleteOp`, `FSDirMkdirOp`, `FSDirRenameOp`, `FSDirConcatOp`, `FSDirAttrOp`, `FSDirSymlinkOp`, `FSDirAclOp`, `FSDirXAttrOp`, `FSDirTruncateOp`, and `FSDirErasureCodingOp`.

Block dependencies include `Block`, `BlockInfoContiguous`, `BlockInfoStriped`, `BlockUCState`, `BlocksMapUpdateInfo`, queued block message processing, replication adjustment, and erasure-coding policy lookup.

## Risks and Edge Cases

Replay must be deterministic and compatible across layout versions. Reserved path renaming, old append behavior, duplicate old `OP_CLOSE` handling, missing inode IDs, and 0.20.203 opcode conflicts are explicit compatibility paths.

Transaction ID gaps and corruption are fatal outside recovery mode. In recovery mode, skipping bad sections can produce a namespace that loads but may be missing operations, so prompts and logs are critical evidence.

Block list replay is high risk. Mismatched block IDs or generation stamps throw; removing more than one block is rejected; adding striped versus contiguous blocks depends on EC policy lookup; and generation-stamp updates also update the standby's global block ID manager.

The loader holds global and directory write locks while applying edits. Long replay time can block other NameNode activity during startup or catch-up, so progress logging and `maxTxnsToRead` are important operational controls.

Retry-cache reconstruction depends on ops carrying RPC IDs and on payload reconstruction matching original RPC results. Missing payloads can affect client idempotency after failover/restart.

## Test Signals

Useful coverage includes replay round trips for every opcode emitted by `FSEditLog`; txid gap, out-of-order, corrupt read, and recovery-mode resync tests; layout-version compatibility tests for inode IDs, reserved path upgrades, legacy append/close, and 0.20.203 failures; block replay tests for add, update, abandon, complete, striped EC files, and generation-stamp updates; retry-cache payload reconstruction tests; snapshot delete cleanup tests for block removal and inode-map removal; rolling-upgrade rollback/finalize tests; cache directive/pool and EC policy manager replay tests; startup progress/op count assertions; `scanEditLog` corruption handling; and `PositionTrackingInputStream` limit/mark/reset/skip behavior.
