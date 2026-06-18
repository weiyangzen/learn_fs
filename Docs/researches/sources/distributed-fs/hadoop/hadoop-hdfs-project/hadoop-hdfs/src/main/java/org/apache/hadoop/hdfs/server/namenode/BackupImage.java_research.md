# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupImage.java

Purpose: `FSImage` specialization for BackupNode, managing local backup storage and the state machine for receiving, spooling, and applying NameNode edit log batches.

Important APIs/types/functions: enum `BNState` has `DROP_UNTIL_NEXT_ROLL`, `JOURNAL_ONLY`, and `IN_SYNC`. Constructor disables pre-upgradable layout checks and starts in drop-until-roll. `recoverCreateRead()` analyzes/formats/recovers backup storage directories without loading image/edits. `journal()` handles remote edit batches: drop before first roll, apply and journal when in sync, or only journal when catching up. `applyEdits()` validates contiguous txid batches, feeds bytes through `EditLogBackupInputStream`, uses `FSEditLogLoader`, advances `lastAppliedTxId`, and updates quota counts under FS write lock. `convergeJournalSpool()` and `tryConvergeJournalSpool()` replay finalized and in-progress local logs until current, then transition to `IN_SYNC`. `namenodeStartedLogSegment()` starts local segments, transitions from drop to journal-only, and optionally freezes namespace. `freezeNamespaceAtNextRoll()` and `waitUntilNamespaceFrozen()` coordinate checkpoints. `close()` aborts current edit log segment instead of finalizing.

Control flow: BackupNode initially drops edits until the active NameNode rolls. It then journals incoming edits locally without applying them, catches up from local spool, loads the in-progress stream, transitions to in-sync, and thereafter applies incoming edit batches to its namespace while journaling them. For checkpoints, it requests freeze on the next roll, transitions back to journal-only, and waits until namespace application stops.

State and persistence behavior: persists local edit logs and storage directories; in-memory namespace is advanced through edit replay. `bnState`, `stopApplyingEditsOnNextRoll`, `lastAppliedTxId`, and current edit log segment ID govern consistency. It intentionally aborts current segments on close because BackupNode is not the authoritative finalizer.

Dependencies and integration points: used by `BackupNode`, `BackupNodeRpcServer`, `Checkpointer`, `FSNamesystem`, `FSEditLog`, `FSEditLogLoader`, storage inspectors, and quota code. It receives journal data through `JournalProtocol` implemented by BackupNode RPC server.

Risks: state transitions are synchronization-sensitive. `applyEdits()` enforces contiguous txids; gaps abort with IO errors. Catch-up loops may repeat if logs roll concurrently. Quota recount after every batch can be costly but preserves namespace accounting. Incorrect close/finalization behavior could corrupt backup edit logs.

Test signals: `TestBackupNode` covers tailing edits, synchronization, checkpoints, storage dir matching, startup behavior, and BackupNode/CheckpointNode read/write restrictions.
