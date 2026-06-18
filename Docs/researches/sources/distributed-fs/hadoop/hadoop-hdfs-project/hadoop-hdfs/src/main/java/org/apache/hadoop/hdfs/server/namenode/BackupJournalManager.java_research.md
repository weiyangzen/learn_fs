# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupJournalManager.java

Purpose: `JournalManager` implementation on the active NameNode side that writes edit log transactions to a registered BackupNode through RPC.

Important APIs/types/functions: constructor stores BackupNode registration and creates `JournalInfo` from the active NameNode registration. `startLogSegment()` creates an `EditLogBackupOutputStream`, starts a segment at the given txid, and returns it. `matchesRegistration()` compares BackupNode addresses. Most local-storage lifecycle methods (`format`, upgrade, rollback, input stream selection, purge) are unsupported, no-op, or intentionally empty because this manager is output-only.

Control flow: when the active NameNode rolls or writes edits, its edit log infrastructure can use this manager to create output streams targeting a BackupNode. It never provides input streams for recovery/replay.

State and persistence behavior: holds remote registration and journal identity. Persistence happens remotely through BackupNode RPC and local BackupNode edit logs, not in this manager.

Dependencies and integration points: uses `NamenodeRegistration`, `JournalInfo`, `EditLogBackupOutputStream`, and NameNode `JournalManager` plumbing.

Risks: unsupported methods must not be called in normal paths; accidental use for input/recovery would fail. `finalizeLogSegment()` is empty because BackupNode stream behavior differs from local journals, so callers must tolerate that.

Test signals: BackupNode integration tests exercise remote journaling and registration, indirectly covering this manager.
