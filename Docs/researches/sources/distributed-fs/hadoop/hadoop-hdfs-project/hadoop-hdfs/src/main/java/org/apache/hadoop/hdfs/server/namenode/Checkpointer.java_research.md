# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Checkpointer.java

## Purpose
`Checkpointer` is the `Daemon` used by a BackupNode to periodically create HDFS namespace checkpoints from the active NameNode. It decides when to checkpoint, downloads missing images/edits when needed, applies edit logs, saves a fresh fsimage, uploads it if requested, and finalizes the checkpoint with the active NameNode.

## Important APIs and Types
Important methods are the constructor, `initialize`, `shutdown`, `work`, `countUncheckpointedTxns`, `doCheckpoint`, `getImageListenAddress`, and static `rollForwardByApplyingLogs`. It uses `BackupNode`, `BackupImage`, `CheckpointConf`, `NamenodeProtocol`, `CheckpointCommand`, `RemoteEditLogManifest`, `TransferFsImage`, `EditLogFileInputStream`, and `FSNamesystem` locks.

## Control Flow
The daemon loop wakes at the GCD of time and transaction polling periods. It checkpoints when the time period expires or uncheckpointed transactions exceed the configured threshold. `doCheckpoint` freezes the backup namespace at the next roll, starts a remote checkpoint, validates the signature, fetches missing image/edit logs if log-only roll-forward is impossible, optionally reloads the image under the global write lock, applies edits, saves fsimage in all dirs, uploads the image if requested, calls `endCheckpoint`, converges backup journals, and refreshes registration.

## State and Persistence
Checkpoint output is persisted through `BackupImage` and `NNStorage`. Downloaded edit logs are read from finalized files, then the new fsimage is saved with the resulting txid. Runtime state includes `shouldRun`, checkpoint config, and HTTP bind address.

## Dependencies and Integration
Integrates with active NameNode RPC and HTTP image transfer, backup node storage, global namespace locks, and edit-log loading. It also handles rolling-upgrade storage version behavior.

## Risks and Test Signals
Failure windows include missing edit-log ranges, signature mismatch, partial image download, image reload under lock, upload failure, and active NN shutdown command. `lastCheckpointTime` is updated to the pre-checkpoint `now`, so long checkpoints influence next scheduling. Tests should simulate log gaps, download/reload fallback, upload-needed and no-upload commands, rolling upgrade, startup checkpoint suppression, and `ACT_SHUTDOWN`.
