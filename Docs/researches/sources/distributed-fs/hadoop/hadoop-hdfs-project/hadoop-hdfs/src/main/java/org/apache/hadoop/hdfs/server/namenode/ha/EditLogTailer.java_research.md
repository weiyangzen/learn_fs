# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/EditLogTailer.java

## Purpose

`EditLogTailer.java` runs on standby/observer NameNodes to continuously read shared edit logs and apply transactions to the local `FSNamesystem`. The source was read as a complete 681-line file.

## Important APIs, Types, and Functions

The main class owns an `EditLogTailerThread`, `FSNamesystem`, `FSEditLog`, remote NameNode iterator, active proxy cache, timing fields, retry settings, and lock batching configuration. Important APIs are constructor, `start`, `stop`, `catchupDuringFailover`, `doTailEdits`, `triggerActiveLogRoll`, test timer hooks, and metrics getters. The nested `MultipleNameNodeProxy` lazily finds a remote active NameNode for `rollEditLog`.

## Control Flow

Construction reads tailing, log-roll, backoff, timeout, retry, in-progress, and max-transactions-per-lock settings; discovers remote NameNodes for log rolling; validates IPC addresses; and initializes metrics timing. The tailer thread runs as the login subject. Each loop optionally triggers active log rolling when too long has elapsed since successful loading and new transactions have been loaded since the last trigger, then takes the checkpoint lock, calls `doTailEdits`, records metrics, updates name-dir size after triggered rolls, and sleeps with exponential backoff when no edits are available.

`doTailEdits` selects input streams after the last applied txid, records fetch time, takes the global namesystem write lock interruptibly, verifies the image txid did not change before loading, applies edits through `FSImage.loadEdits` with `maxTxnsPerLock`, records loaded count, updates `lastLoadTimeMs` and `lastLoadedTxnId`, and releases the lock. `catchupDuringFailover` repeatedly tails without in-progress streaming until no more edits load, intended to run after the background thread has stopped.

## State and Persistence Behavior

The tailer mutates the standby namespace in memory by replaying persisted edit logs from shared storage or journal managers. It does not write namespace edits itself, but loaded txids and metrics reflect durable journal progress. It may ask the active to roll logs so finalized segments become available.

## Dependencies and Integration Points

It integrates with `FSEditLog`, `FSImage`, `FSNamesystem`, `EditLogInputStream`, `EditLogInputException`, `NameNodeMetrics`, `RemoteNameNodeInfo`, `NamenodeProtocolPB`, `RPC.waitForProxy`, `NamenodeProtocolTranslatorPB`, `SecurityUtil`, `SubjectInheritingThread`, and `RwLockMode.GLOBAL`.

## Risks and Edge Cases

Deadlock avoidance depends on interruptible namesystem locking during failover. Empty stream selection during an active log roll is treated as transient, while read errors after streams are selected are significant. In-progress tailing changes latency and journal-manager behavior. Remote active discovery is intentionally slow and retry-based. `nnCount` must be nonzero when log rolling is enabled, or retry arithmetic would be unsafe. Exponential backoff must reset after successful loads.

## Test Signals

Tests should cover tailing finalized and in-progress logs, empty stream transient failures, edit load exceptions with partial counts, failover catchup, stopping while blocked on locks or RPC, active log rolling timeout and retry across remotes, backoff timing, max transactions per lock, metrics increments, name-dir size update after roll, and secure subject execution.
