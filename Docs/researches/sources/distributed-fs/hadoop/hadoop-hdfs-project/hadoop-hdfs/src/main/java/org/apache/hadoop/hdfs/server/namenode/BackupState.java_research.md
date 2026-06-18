# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupState.java

Purpose: HA state implementation used by BackupNode while presenting itself as a standby-like NameNode role with custom operation checks and service lifecycle.

Important APIs/types/functions: constructor sets HA service state to `STANDBY`. `checkOperation()` delegates to the BackupNode HA context. `shouldPopulateReplQueues()` returns false. `enterState()` starts active services through context; `exitState()` stops them; `prepareToExitState()` delegates standby-service preparation.

Control flow: `BackupNode.createHAState()` returns this state. Its lifecycle callbacks call the backup-specific `BNHAContext`, which gates allowed operations and starts/stops selected NameNode services.

State and persistence behavior: no persistent state; in-memory HA state controls service behavior and operation authorization.

Dependencies and integration points: extends `HAState`, uses `HAContext`, `OperationCategory`, and `ServiceFailedException`. Tightly coupled to `BackupNode.BNHAContext` behavior.

Risks: despite using `HAServiceState.STANDBY`, `enterState()` starts active services; correctness depends on BackupNode context muting unsafe services and safe mode. Replication queues are intentionally not populated.

Test signals: BackupNode operation restriction tests exercise state behavior through reads/writes/checkpoints.
