# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNode.java

## Purpose

`SecondaryNameNode.java` implements the non-HA Secondary NameNode daemon and startup utility commands. It periodically checkpoints a primary NameNode by rolling the primary edit log, downloading the latest fsimage and finalized edits, replaying the edits into a local `FSNamesystem`, saving a new fsimage in checkpoint storage, and uploading that image back to the primary over the image transfer servlet. The source was read as a complete 1,116-line file for this report.

## Important APIs, Types, and Functions

The main type is `SecondaryNameNode`, which implements `Runnable` and `SecondaryNameNodeInfoMXBean`. Important methods are constructors, `initialize`, `startInfoServer`, `startCheckpointThread`, `doWork`, `doCheckpoint`, `downloadCheckpointFiles`, `doMerge`, `shutdown`, `main`, `processStartupCommand`, and JMX getters such as `getLastCheckpointTime` and `getCheckpointDirectories`. The nested `CommandLineOpts` parses `-checkpoint`, `-checkpoint force`, `-geteditsize`, `-format`, and help. The nested `CheckpointStorage` extends `FSImage` for checkpoint-local image/edit storage and owns `recoverCreate`, `deleteTempEdits`, merge-error accounting, and a `CheckpointLogPurger`.

## Control Flow

Construction rejects HA nameservices, initializes generic NameNode keys, logs in with the secondary keytab when security is enabled, creates JVM metrics, opens a `NamenodeProtocol` RPC proxy to the primary, initializes checkpoint image and edits directories, recovers or creates local storage, creates a checkpoint-only `FSNamesystem`, disables quota checks, and registers the JMX bean. In daemon mode `main` starts the HTTP server, starts a daemon thread, and joins the web server. The thread sleeps for the configured check period, refreshes Kerberos credentials, then checkpoints when either transaction count or elapsed time crosses `CheckpointConf` thresholds.

`doCheckpoint` is the critical path. It ensures `current/` directories exist, calls `namenode.rollEditLog`, uses the returned `CheckpointSignature` to align local storage identity and validate namespace compatibility, fetches the manifest from the primary, downloads changed fsimage and required edits, reloads the image if needed or after a previous merge error, applies edit logs with `Checkpointer.rollForwardByApplyingLogs`, saves the resulting image in all local directories, updates storage version outside rolling upgrade, uploads the new image through `TransferFsImage.uploadImageFromStorage`, and optionally writes a legacy OIV image. Startup command mode runs a single checkpoint or edit-size query and exits.

## State and Persistence Behavior

Persistent state is the checkpoint storage tree: VERSION files, fsimage files, finalized edits, temporary edits, md5 digests, and any legacy OIV output. `CheckpointStorage.recoverCreate` analyzes and recovers storage directories, optionally formats them, reads existing VERSION files, unlocks/restores removed storage, and deletes temporary edits. The local `FSNamesystem` holds the replayed namespace image in memory between checkpoint cycles, but a merge failure marks `mergeErrorCount` so the next checkpoint reloads from downloaded image and edits instead of trusting possibly inconsistent memory. `lastCheckpointTime` uses monotonic time for scheduling, while `lastCheckpointWallclockTime` is exposed to JMX.

## Dependencies and Integration Points

The class integrates with `NameNodeProxies`, `NamenodeProtocol`, `CheckpointSignature`, `RemoteEditLogManifest`, `FSImage`, `FSNamesystem`, `NNStorage`, `FileJournalManager`, `TransferFsImage`, `ImageServlet`, `HttpServer2`, `MBeans`, `CheckpointFaultInjector`, Hadoop security, and `CheckpointConf`. It is intentionally disabled in HA deployments because `StandbyCheckpointer` handles checkpointing there. The HTTP server exposes `ImageServlet` so the primary can pull the newly generated image.

## Risks and Edge Cases

The code is sensitive to namespace identity and layout-version mismatches; accepting the wrong signature would corrupt checkpoint storage. Partial downloads and rename failures can leave temp edits, which are cleaned on startup but still affect recovery. Merge errors can leave in-memory namespace state inconsistent, so the merge-error counter and reload behavior are important. The daemon terminates after too many merge failures to avoid unbounded edit growth. Security setups rely on correct keytab, SPNEGO, and relogin behavior. `downloadCheckpointFiles` requires a continuous manifest starting at `mostRecentCheckpointTxId + 1`.

## Test Signals

Useful tests cover daemon scheduling by transaction count and period, CLI parsing and single-shot checkpoint behavior, HA rejection, fresh and existing checkpoint storage recovery, temp edit cleanup, manifest gap detection, namespace signature mismatch, fsimage reload after merge failure, upload failure handling, rolling-upgrade storage-version behavior, legacy OIV failures that should not abort checkpointing, JMX fields, secure keytab/relogin paths, and injected failures through `CheckpointFaultInjector`.
