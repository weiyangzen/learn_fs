# Research: subset-b-000485

Grouped research for Alluxio master journal, meta, configuration-check, and metastore tests. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemMetricsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemMetricsTest.java

Purpose: validates metric registration and metric values for the embedded Raft journal system and its state machine.

Important APIs/types/functions: uses `RaftJournalSystem`, `JournalStateMachine`, `SnapshotDirStateMachineStorage`, `MetricsSystem.METRIC_REGISTRY`, `MetricKey`, Ratis `RoleInfoProto`, and Mockito spies. Helper accessors read the cluster leader index/id, local master role id, and dynamically generated per-master journal sequence-number gauges.

Control flow: `journalStateMachineMetrics` resets selected metrics, builds a Raft journal system, constructs and closes state machines twice, and verifies state-machine gauges are registered on construction and removed on close. `metrics` stubs sequence-number maps and Ratis role info across waiting-for-election, leader, follower, and leader-again states, while calling `startInternal`, `gainPrimacy`, and `losePrimacy`.

State and persistence behavior: no durable journal entries are asserted here; the observable state is global metric registry contents plus the Raft journal system's local role/primacy transitions. Temporary folders isolate embedded journal storage.

Dependencies and integration points: depends on test port allocation through `JournalTestUtils.createEmbeddedJournalTestPorts`, Alluxio configuration reload, Ratis role protobufs, and Alluxio metric key naming conventions.

Risks: global metric registry cleanup is manual and can leak between tests if metric names change. The follower leader-id parsing assumes peer IDs are encoded as `localhost_port`. Metrics are validated through direct gauge lookup, so missing gauge lifecycle changes are caught but gauge type changes may fail with casts.

Test signals: good regression coverage for metric lifecycle and role/leader gauge semantics; does not exercise a full multi-node Ratis cluster or real journal sequence-number progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemMetricsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalTest.java

Purpose: integration-style tests for embedded Raft journal replication, joining nodes, suspended standby catch-up, primacy changes, corrupted entries, and Ratis configuration merging.

Important APIs/types/functions: uses `RaftJournalSystem`, `JournalContext`, `CatchupFuture`, `CountingNoopFileSystemMaster`, `NoopMaster`, `StateLockManager`, `QuorumServerInfo`, `RaftProperties`, and Ratis internals reached through reflection. Helpers create clustered journal systems with local free ports, start them asynchronously, add a joining peer, and force leadership changes with `changeToFollower`/`changeToCandidate`.

Control flow: setup starts a two-node Raft cluster, waits for leader election, assigns leader/follower references, and calls `gainPrimacy` on the leader. Tests append journal entries through leader contexts and wait for follower apply counts. Suspension tests call `suspend`, `catchup`, `resume`, and verify partial target sequences, repeated catchups, catch-up in chunks, and no application while suspended. Primacy tests promote the follower before, after, or during catch-up. Snapshot restart checks checkpoint behavior while suspended. `catchupCorruptedEntry` injects an unsupported delete entry and expects the catch-up future to surface the master's apply error. `testMergeAlluxioConfig` verifies Alluxio `MASTER_EMBEDDED_JOURNAL_RATIS_CONFIG.*` properties flow into Ratis config.

State and persistence behavior: journal entries are replicated through Ratis, applied to counting masters, checkpointed, and replayed across follower restart. Sequence targets are per-master maps keyed by `FileSystemMaster`. Cluster membership is inferred from quorum server info.

Dependencies and integration points: depends on Apache Ratis server internals, Alluxio journal abstractions, configurable election timeouts, checkpoint period, and network port availability.

Risks: reflection against Ratis implementation methods is brittle. Election sleeps and asynchronous writes make tests timing-sensitive. The free-port pattern can race with other processes. Corruption coverage uses one failure type only.

Test signals: strong end-to-end signal for Raft journal standby backup/catch-up semantics and promotion behavior, including error propagation from asynchronous catch-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalWriterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalWriterTest.java

Purpose: focused unit tests for `RaftJournalWriter` batching and flush behavior over a mocked `RaftJournalAppender`.

Important APIs/types/functions: uses `RaftJournalWriter`, `RaftJournalAppender.sendAsync`, Ratis `RaftClientReply`, `ClientId`, `RaftGroupMemberId`, `RaftGroupId`, and Alluxio journal protobuf entries. The setup returns a custom `CompletableFuture` whose `get` methods immediately return a successful Ratis reply.

Control flow: `writeAndFlush` writes ten mount entries and verifies no async send before explicit `flush`, one send after the first flush, no duplicate send on an empty second flush, then a second send after writing another entry. `writeTriggerFlush` reflectively lowers static `FLUSH_BATCH_SIZE` to 128 bytes, writes mount entries, and verifies automatic sends occur at least proportional to serialized path byte volume.

State and persistence behavior: state is in-memory writer buffer contents and appender invocation count. No real Raft log or durable journal is created.

Dependencies and integration points: integrates with Ratis reply construction enough for `RaftJournalWriter.flush` to see a successful append. Uses reflection to mutate a static final field and Mockito verification for batching behavior.

Risks: reflective mutation of `FLUSH_BATCH_SIZE` is JVM/version-sensitive. The byte estimate does not include full protobuf overhead, so the assertion is deliberately lower-bound. The mocked future reports `isDone=false` despite returning from `get`, which is acceptable for this writer path but not a complete async model.

Test signals: good signal for explicit flush idempotence and automatic batch-size flushing; does not cover append failures, close behavior, or sequence numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalWriterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/sink/JournalSinkTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/sink/JournalSinkTest.java

Purpose: integration tests for `JournalSink` delivery from the file-system master during live journal writes, replay, restart, and standby tailing.

Important APIs/types/functions: uses `JournalSystem`, `JournalSink`, `MasterRegistry`, `CoreMasterContext`, `MetricsMasterFactory`, `BlockMasterFactory`, `FileSystemMasterFactory`, `FileSystemMaster`, and file operation contexts for create, complete, rename, and delete. `TestJournalSink` appends entries to both a queue used by find helpers and an all-entry list used for replay comparison.

Control flow: setup configures UFS journaling, short tailer sleep, NOSASL auth, test work/root UFS directories, creates a journal system, registers a sink for the file-system master, starts masters as leader, and obtains `FileSystemMaster`. `writeEvents` performs file/dir create, nested create, rename, file delete, and recursive directory delete, then polls sink entries for expected inode, rename, and delete records. `writeInodePaths` repeats the mutation set while asserting path fields on inode, update, rename, and delete journal entries. `replayEvents` starts a standby with its own sink, generates 5000 random create/rename/delete operations, restarts the leader with a new sink, waits for leader-replay and standby counts to match the original sink, strips sequence numbers, and compares journal content.

State and persistence behavior: exercises UFS-backed journal files through master restart and standby replay. The sink itself is in-memory, but observations come from real journal emission and tailing.

Dependencies and integration points: depends on Alluxio master registry startup order, file-system master journaling, journal sink registration/removal, test UFS directories, and randomized operation generation.

Risks: queue polling consumes entries and makes helper order important. Random replay workload can make failures harder to reproduce. The standby registry created in `replayEvents` is not held for explicit stop in the test body, relying on process/test cleanup.

Test signals: strong integration signal that sink callbacks see semantically rich file-system journal entries during writes and replay, including path propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/sink/JournalSinkTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/tool/JournalToolTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/tool/JournalToolTest.java

Purpose: verifies `JournalTool.main` input directory resolution without executing the expensive journal dump.

Important APIs/types/functions: uses PowerMock to spy `JournalTool`, suppress private static `dumpJournal`, and `Whitebox.getInternalState` to read `sInputDir`. Tests manipulate `Configuration` keys `MASTER_JOURNAL_TYPE` and `MASTER_JOURNAL_FOLDER`.

Control flow: setup reloads configuration and stubs `dumpJournal`. `defaultJournalDir` calls main with no args and expects the configured default master journal folder. `hdfsJournalDir` sets UFS journal type and an HDFS URI and expects it unchanged. `absoluteLocalJournalInput` passes `-inputDir` with an absolute path while configured journal type is embedded and expects the provided path. `relativeLocalJournalInput` passes a relative path and expects it resolved against `user.dir`.

State and persistence behavior: no journal files are read. State is static `JournalTool.sInputDir` plus global configuration.

Dependencies and integration points: tests CLI argument parsing, configuration fallback, URI/path normalization, and PowerMock instrumentation of static methods.

Risks: relies on private static field names and private method signatures. It does not cover actual dump output, invalid arguments, or embedded journal directory discovery beyond the input path assignment.

Test signals: useful signal for CLI path resolution and safe regression guard around relative local path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/tool/JournalToolTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointThreadTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointThreadTest.java

Purpose: tests standby/checkpoint thread catch-up state, shutdown behavior, and checkpoint creation for UFS journals.

Important APIs/types/functions: uses `UfsJournal`, `UfsJournalCheckpointThread`, `UfsJournalSnapshot`, `UfsJournalLogWriter`, `MockMaster`, `NoopMaster`, `UnderFileSystem`, and `CloseableIterator`. Helpers build completed logs and then rename them to incomplete logs by using `UfsJournalFile.encodeLogFileLocation`.

Control flow: setup creates a spied UFS-backed journal for `FileSystemMaster`, starts it, and gains primacy. `catchupState` sets checkpoint period and tailer sleep, creates completed and incomplete logs, starts a checkpoint thread, waits until catch-up state is `DONE`, terminates it, and expects next sequence number 10. `catchStateShutdown` starts the thread then immediately awaits termination and expects `DONE`. `checkpointBeforeShutdown` sets a low checkpoint period and waits for a checkpoint ending at sequence 10 before shutdown. `checkpointAfterShutdown` shuts down after replay and verifies the mock master processed all ten completed log entries even if checkpointing was not required.

State and persistence behavior: UFS log/checkpoint files are the durable state. Incomplete current logs are present but standby checkpointing focuses on completed entries.

Dependencies and integration points: depends on UFS flush support mocking, journal snapshot discovery, configuration-driven checkpoint period, and mock master journal application.

Risks: timing waits can be sensitive to scheduler delays. The tests use empty lost-file sets and simple sequence-only entries, so richer master replay behavior is outside scope.

Test signals: good coverage that checkpoint threads converge to `DONE`, replay completed logs, and checkpoint before or during shutdown as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointThreadTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriterTest.java

Purpose: validates UFS checkpoint writer file creation, cancellation, and conflict handling with existing checkpoints.

Important APIs/types/functions: uses `UfsJournal`, `UfsJournalCheckpointWriter`, `UfsJournalSnapshot`, `UfsJournalFile`, `UnderFileSystem`, and delimited journal protobuf writes.

Control flow: setup creates a UFS journal with a spied local under filesystem. `writeJournalEntry` writes entries to a checkpoint ending at `0x20`, closes the writer, and expects one checkpoint file under the checkpoint directory with no temporary checkpoint remaining. `writeJournalEntryMoreThanJournalLogSequenceNumber` writes more entries than the checkpoint end sequence to confirm the file-name end sequence, not embedded entry sequence count, defines checkpoint identity. `cancel` writes entries then cancels and expects no checkpoint or temporary file. `checkpointExists` pre-creates the target checkpoint and verifies close leaves a single final checkpoint. `olderCheckpointExists` preserves both older and new checkpoints in order. `newerCheckpointExists` verifies a newer checkpoint wins and the attempted older result is not added.

State and persistence behavior: the writer creates temporary checkpoint state and atomically promotes/removes it on close or cancel. Snapshots read actual UFS files.

Dependencies and integration points: exercises checkpoint directory naming, UFS create/rename/delete behavior, and snapshot sorting.

Risks: tests use local UFS semantics and may not expose object-store rename/listing edge cases. Entry payload is sequence-only, so checkpoint content validation is limited.

Test signals: strong signal for checkpoint writer cleanup and idempotent handling of existing older/newer checkpoint files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalConfTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalConfTest.java

Purpose: verifies conversion from Alluxio journal-specific UFS option properties into `UnderFileSystemConfiguration`.

Important APIs/types/functions: uses `UfsJournal.getJournalUfsConf`, `UnderFileSystemConfiguration`, `PropertyKey.Template.MASTER_JOURNAL_UFS_OPTION_PROPERTY`, and `PropertyKey.UNDERFS_LISTING_LENGTH`.

Control flow: `emptyConfiguration` calls `getJournalUfsConf` with no journal UFS overrides and expects empty mount-specific configuration. `nonEmptyConfiguration` formats a journal UFS option key for `underfs.listing.length`, sets it to `10000`, then expects the resulting UFS configuration to return that value and contain exactly one mount-specific entry.

State and persistence behavior: no journal state is created. The only mutable state is global configuration, reset after each test.

Dependencies and integration points: covers the bridge from master journal configuration namespace to UFS mount-specific options.

Risks: tests a single property and type. It does not cover invalid property names, multiple overrides, string-valued options, or precedence against global UFS configuration.

Test signals: concise regression signal that journal UFS option templating is honored and does not create phantom mount-specific config when unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalConfTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalFileTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalFileTest.java

Purpose: tests `UfsJournalFile` classification, ordering, and filename encoding/decoding for UFS journal artifacts.

Important APIs/types/functions: uses `UfsJournalFile.createCheckpointFile`, `createLogFile`, `createTmpCheckpointFile`, `encodeLogFileLocation`, `decodeLogFile`, `encodeCheckpointFileLocation`, `decodeCheckpointFile`, `encodeTemporaryCheckpointFileLocation`, and `decodeTemporaryCheckpointFile`.

Control flow: factory tests assert start/end/location fields and boolean classifiers for checkpoint, completed log, incomplete log, and temporary checkpoint files. `sort` creates 100 log files with random starts but monotonically increasing ends, shuffles them, sorts them, and verifies order by end sequence. Filename tests check hexadecimal `0xstart-0xend` naming for completed logs, incomplete logs using `UNKNOWN_SEQUENCE_NUMBER`, checkpoints as `0x0-0xend`, and temporary checkpoints under the journal temp directory.

State and persistence behavior: no real files are written except temporary folder paths used to construct journal URIs. Behavior is pure metadata encoding/decoding.

Dependencies and integration points: filename conventions are consumed by `UfsJournalSnapshot`, reader, writer, checkpoint thread, and format logic.

Risks: malformed filename handling is not tested here. Sort ordering is validated only by end sequence, matching current expectations but not necessarily all tie-breakers.

Test signals: strong low-level signal that UFS journal artifact names and type predicates remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalFileTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalLogWriterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalLogWriterTest.java

Purpose: extensive tests for UFS journal log writer rotation, flush semantics, recovery after UFS failures, and detection of missing entries.

Important APIs/types/functions: uses `UfsJournalLogWriter`, `UfsJournalReader`, `UfsJournalSnapshot`, `UfsJournalFile`, `UnderFileSystem.supportsFlush`, `ExceptionMessage.JOURNAL_ENTRY_MISSING`, and PowerMock `Whitebox` to replace the writer's internal `DataOutputStream`.

Control flow: setup starts a primary UFS journal. Completion tests convert current incomplete logs into completed logs and deduplicate already completed logs. Write tests compare flush-supported UFS, which keeps one log until close, against non-flush UFS, which rotates on flush. Rotation test sets max log size to one byte and expects every entry to become its own log. Recovery tests inject write or flush failures, verify the writer resets its stream, retries writes/flushes, completes files after failed flush, and can recover after deleting an incomplete file. Missing-entry tests truncate or delete files after acknowledged flushes and expect runtime errors containing precise missing sequence ranges.

State and persistence behavior: exercises real local journal files, completed/incomplete log naming, and reader verification of sequence intervals. Failure injection mutates the active stream while files are partially written.

Dependencies and integration points: integrates with UFS flush capability, journal reader recovery scanning, log rotation configuration, runtime debug URL error messages, and snapshot current-log discovery.

Risks: relies on reflection into private writer internals. Local filesystem behavior may not represent all UFS backends. Sequence-only entries do not cover payload decode failures.

Test signals: very strong regression coverage for the most failure-prone UFS log writer paths, especially preserving or detecting flushed journal entries across I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalLogWriterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalReaderTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalReaderTest.java

Purpose: tests `UfsJournalReader` state transitions and sequence tracking across checkpoints, completed logs, incomplete logs, and newly created logs.

Important APIs/types/functions: uses `JournalReader.State` (`CHECKPOINT`, `LOG`, `DONE`), `UfsJournal.getReader`, direct `UfsJournalReader` construction with a starting sequence number, `UfsJournalCheckpointWriter`, `CheckpointOutputStream`, `CheckpointType.JOURNAL_ENTRY`, and `UfsJournalLogWriter`.

Control flow: `readCheckpoint` writes a checkpoint payload, reads until `DONE`, and verifies the checkpoint stream bytes and next sequence number. `readCompletedLog` creates contiguous completed logs and verifies all entries in order and repeated `DONE`. `readIncompleteLogPrimary` confirms a primary reader consumes the current incomplete log, while `readIncompleteLogSecondary` confirms a secondary reader stops before it. `readNewLogs` reaches `DONE`, then creates new completed and incomplete logs and verifies the same reader can continue. Checkpoint-plus-log tests cover checkpoint end sequences that do or do not exactly match log boundaries. Resume tests start reading from within or after a checkpoint and still reach the final log end.

State and persistence behavior: durable state is checkpoint files and completed/current log files under the test UFS journal. Reader state tracks next sequence number and current state.

Dependencies and integration points: depends on file naming/snapshot discovery, checkpoint stream format, UFS flush support, and primary-vs-secondary semantics for incomplete logs.

Risks: malformed or corrupted entries are not covered here. Timing/tailing behavior is simplified by building logs synchronously.

Test signals: strong signal for reader ordering, checkpoint skipping/resume logic, and primary-only visibility of incomplete logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalReaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalSnapshotTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalSnapshotTest.java

Purpose: verifies snapshot discovery and ordering for UFS journal checkpoints, temporary checkpoints, completed logs, current log, and malformed files.

Important APIs/types/functions: uses `UfsJournalSnapshot.getSnapshot`, `getCurrentLog`, `getNextLogSequenceNumberToCheckpoint`, and `UfsJournalFile` encoding helpers.

Control flow: the test creates two checkpoint files, one temporary checkpoint, ten completed log files with increasing sequence ranges, one incomplete current log, and one malformed `.tmp` log-like file. It then reads a snapshot and asserts checkpoint order, temporary checkpoint discovery, log list order matching creation/sequence order, current-log detection, and next log sequence number to checkpoint equal to the latest checkpoint end.

State and persistence behavior: all observations are derived from actual files in checkpoint, log, and temp directories. Malformed files are expected to be ignored.

Dependencies and integration points: snapshot discovery feeds UFS journal reader, writer recovery, checkpoint thread, and format behavior.

Risks: only one malformed suffix pattern is covered. It does not test holes, overlapping ranges, duplicate files, or UFS listing errors.

Test signals: solid low-level signal that snapshot parsing returns the correct artifact categories and current checkpoint cursor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalSnapshotTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalTest.java

Purpose: integration tests for the UFS journal lifecycle: formatting, availability, suspend/catch-up/resume, replay, standby catch-up, primacy transitions, and corrupted entry propagation.

Important APIs/types/functions: uses `UfsJournal`, `CountingNoopFileSystemMaster`, `CatchupFuture`, `UfsJournalLogWriter`, `UfsJournalCheckpointThread.CatchupState`, `UfsJournalSnapshot`, and journal protobuf entries.

Control flow: `format` creates checkpoint, temp checkpoint, completed logs, current log, and malformed files, then formats and expects all recognized journal artifacts gone. `unavailableAfterClose` verifies `createJournalContext` fails after close. `suspendNotAllowedOnPrimary` prevents suspending a primary. `suspendCatchupResume` uses a primary and standby sharing the same journal base, writes entries, suspends standby, catches up only to sequence 1, closes primary to complete the current log, then resumes standby to apply all entries. Replay tests verify initial startup catch-up and standby catch-up after losing primacy. Primacy tests cover gaining primary after suspend, after partial catch-up, and during in-progress catch-up. `subsequentCatchups` validates multiple target advances. `catchupCorruptedEntry` writes a bad delete entry and verifies `waitTermination` surfaces the apply error.

State and persistence behavior: durable UFS files are shared between primary and standby journals. Catch-up state transitions to `DONE`, sequence application counts model master state, and current logs are completed on primary close.

Dependencies and integration points: exercises UFS journal, checkpoint thread, file naming, standby reader, master apply errors, and primary lifecycle.

Risks: single-process primary/standby sharing a local path is simpler than distributed UFS deployment. Waits depend on background catch-up timing.

Test signals: strong behavioral coverage for UFS journal failover and backup-mode semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/AlluxioMasterRestServiceHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/AlluxioMasterRestServiceHandlerTest.java

Purpose: tests selected REST handler behavior for master info assembly, mount URI matching, and web UI log listing.

Important APIs/types/functions: uses `AlluxioMasterRestServiceHandler`, `AlluxioMasterProcess`, `MasterRegistry`, `MetricsMaster`, `BlockMaster`, `FileSystemMaster`, `NoopJournalSystem`, `UnderFileSystemFactoryRegistry`, `AlluxioMasterInfo`, `Capacity`, `WorkerInfo`, `MasterWebUILogs`, and `UIFileInfo`.

Control flow: setup creates a mocked master process and servlet context, starts a real registry with metrics, block, and file-system masters, registers a mock UFS factory for `test://test/`, registers two workers with tiered total/used bytes, and clears a pinned-files metric. `getMasterInfo` stubs RPC address, start/uptime, and a metric gauge, calls `getInfo(false)`, and validates configuration, metrics, version, capacity, UFS capacity, and worker IDs. `isMounted` stubs a mount table with an S3 URI and verifies only metric-escaped normalized variants match. `testGetWebUILogsByRegex` creates wanted and unwanted log file names, sets `LOGS_DIR`, and verifies web UI logs include only matching master log/out/txt/gc/exit-metrics files.

State and persistence behavior: uses in-memory masters with no-op journal plus real temporary log files. Metrics are global registry state.

Dependencies and integration points: integrates REST handler with servlet context lookup, master process facade, block worker registration, UFS capacity reporting, metric escaping, and UI log filtering.

Risks: PowerMock and global UFS factory/metric registry state can leak if cleanup changes. Only success responses are covered.

Test signals: useful integration signal for REST data aggregation and web log filename filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/AlluxioMasterRestServiceHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/DailyMetadataBackupTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/DailyMetadataBackupTest.java

Purpose: verifies daily metadata backup scheduling and backup-file retention deletion.

Important APIs/types/functions: uses `DailyMetadataBackup`, `MetaMaster.backup`, `BackupStatus`, `BackupPStatus`, `BackupState.Completed`, `UfsManager`, `UfsClient`, `UnderFileSystem`, `ControllableScheduler`, and backup filename format from `BackupManager`.

Control flow: setup mocks `MetaMaster.backup` to return a completed backup under `/tmp/test/alluxio_backups`, mocks a local UFS and root UFS client, and creates a controllable scheduler. The test enables daily backup, sets backup directory and retained-file count to one, starts `DailyMetadataBackup`, then for three simulated days updates `listStatus` to return one, two, and three generated backup files. After each `jumpAndExecute(1, DAYS)`, it verifies backup invocation count and cumulative delete calls based on `total - retain`.

State and persistence behavior: no real backups are written. Existing backup state is mocked as `UfsFileStatus` arrays; deletion is observed through mocked UFS calls.

Dependencies and integration points: covers scheduler interaction, meta master backup command, UFS root acquisition, backup naming, and retention policy.

Risks: generated backup timestamps are random and based on current time, but ordering behavior is not deeply asserted. Test verifies call counts, not exact deleted paths. It mixes `deleteFile` and `deleteExistingFile` expectations, reflecting implementation transition details.

Test signals: good signal that daily scheduled execution runs backups and enforces file-retention counts over repeated runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/DailyMetadataBackupTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/JournalSpaceMonitorTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/JournalSpaceMonitorTest.java

Purpose: tests Linux journal disk-space monitoring, disk-info parsing, and warning logging.

Important APIs/types/functions: uses `JournalSpaceMonitor`, `JournalDiskInfo`, `CommandReturn`, `TestLoggerRule`, `OSUtils.isLinux`, and Mockito spies over `getRawDiskInfo`.

Control flow: class-level assumption skips non-Linux platforms. `testNonExistentJournalPath` expects an invalid path to fail construction. `testSuccessfulInfo` stubs a `df`-style output and verifies disk path, total/used/available byte conversions from 1024-blocks, and percent available. `testFailedInfo` stubs `getRawDiskInfo` to throw and expects propagation. Logging tests create monitors with thresholds above or below the parsed free percentage, call `heartbeat`, and assert whether the warning regex was logged.

State and persistence behavior: no persistent state beyond the monitored path; command output is mocked.

Dependencies and integration points: integrates heartbeat executor contract, shell command parsing, Alluxio wire disk info, and log4j warning capture.

Risks: parser coverage uses one exact `df` output shape. Linux-only assumption avoids portability but leaves non-Linux behavior untested.

Test signals: good focused signal for threshold calculation and warning behavior on the supported Linux path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/JournalSpaceMonitorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/PathPropertiesTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/PathPropertiesTest.java

Purpose: validates journaled path-level property add/remove behavior and deterministic hashing.

Important APIs/types/functions: uses `PathProperties`, `NoopJournalContext`, `PropertyKey`, `ReadType`, and `WriteType`. Static maps model read/write property sets for root and nested paths.

Control flow: `empty` expects a fresh store to have no properties. `add` adds root and `/dir1` properties, overwrites existing path properties, then adds/merges additional root, nested, and sibling path entries and verifies string-keyed maps. `remove` exercises removal from empty state, removal of nonexistent paths/keys, targeted key removal leaving partial property maps, and full path removal. `hashEmpty` checks a stable non-null hash for empty state. `hash` verifies hash changes as properties are added or partially removed, returns to a previous hash when state returns to the same map, and returns to the empty hash after all removals.

State and persistence behavior: `PathProperties` is in-memory here, but operations accept a journal context, so these calls represent the journaled mutation API used by the meta master.

Dependencies and integration points: path properties feed per-path configuration in the master and must hash consistently for configuration/reporting comparisons.

Risks: `NoopJournalContext` means actual journal entry emission is not validated. Tests do not cover invalid property names, concurrent access, or path normalization.

Test signals: strong signal for core map mutation semantics and hash determinism.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/PathPropertiesTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationCheckerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationCheckerTest.java

Purpose: tests consistency-check report generation across registered master/worker/server configuration records.

Important APIs/types/functions: uses `ConfigurationChecker`, `ConfigurationStore`, dynamic `PropertyKey` builders with `ConsistencyCheckLevel.ENFORCE` or `WARN`, gRPC `ConfigProperty`, `Scope`, `ConfigStatus`, `Address`, and wire `ConfigCheckReport`.

Control flow: setup creates two independent stores and a checker. `checkConf` defines master-enforce, worker-warn, and server-enforce keys, builds matching properties, and registers two node addresses. It first verifies identical records pass. Then it changes the WARN-scoped worker property on one record and expects one warning with status `WARN`. Then it changes the ENFORCE-scoped master property and expects one error plus one warning with status `FAILED`. Finally it introduces a mismatched server-enforce property and expects failure with one error and no warnings.

State and persistence behavior: all state is in-memory `ConfigurationStore` records keyed by node address. Reports are regenerated explicitly before inspection.

Dependencies and integration points: validates the master-side configuration consistency check that classifies mismatches by property consistency level and scope.

Risks: uses dynamically built test keys, so it avoids some real property metadata interactions. It checks counts/status but not exact report contents or grouping.

Test signals: clear regression signal for PASS/WARN/FAILED status transitions and warn-vs-error classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationCheckerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationStoreTest.java

Purpose: tests registration and node-loss bookkeeping for configuration records.

Important APIs/types/functions: uses `ConfigurationStore`, `ConfigRecord`, gRPC `ConfigProperty`, `PropertyKey`, and wire `Address`.

Control flow: setup creates two property lists using real known keys (`ZOOKEEPER_ELECTION_PATH`, `WORKER_FREE_SPACE_TIMEOUT`) with different values and two random addresses. `registerNewConf` registers both nodes and verifies both appear in the config map. `registerNewConfUnknownProperty` registers `unknown.property` and verifies the store preserves an unknown key name rather than dropping the record. `detectNodeLost` removes one address and verifies the other remains. `lostNodeFound` removes both, then marks one found and verifies only that node returns to the config map.

State and persistence behavior: state is an in-memory mapping from addresses to lists of config records plus lost-node tracking used to restore records when a node is found again.

Dependencies and integration points: supports configuration checker inputs and master node lifecycle notifications.

Risks: tests map membership but not record value/source equality for known properties. Random ports/hosts are fine because equality is object-value based.

Test signals: useful signal that configuration reports survive unknown keys and correctly react to node loss/recovery events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/BlockMetaStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/BlockMetaStoreTest.java

Purpose: parameterized behavioral tests for block metadata stores backed by RocksDB and heap memory.

Important APIs/types/functions: uses `BlockMetaStore`, `RocksBlockMetaStore`, `HeapBlockMetaStore`, protobuf `BlockMeta` and `BlockLocation`, `CloseableIterator`, and configuration key `ROCKS_BLOCK_CONF_FILE`.

Control flow: parameter setup creates a temporary Rocks options file and supplies both Rocks and heap store factories. Each test creates a fresh store and closes it after. Rocks-specific tests reopen with a valid config file and run `testPutGet`, or reopen with invalid config text and expect a `RuntimeException` caused by `RocksDBException`. `testPutGet` writes three blocks and verifies lengths. `testIterator` verifies iterator order and content for three blocks. `blockLocations` writes five blocks and one location each, then reads locations back. `blockSize` verifies `size` increments with writes and returns to zero after removals.

State and persistence behavior: heap store is transient; Rocks store persists under the temporary directory during each store instance. Tests explicitly clear after some operations.

Dependencies and integration points: verifies common `BlockMetaStore` contract used by block master metadata, plus RocksDB option-file loading.

Risks: iterator ordering is assumed to match insertion/id order. It does not test multiple locations per block, duplicate locations, remove-location behavior, or checkpoint/restore.

Test signals: good cross-implementation contract signal for basic block metadata CRUD and Rocks config handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/BlockMetaStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreBench.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreBench.java

Purpose: standalone microbenchmark for inode store write throughput and checkpoint/restore performance.

Important APIs/types/functions: uses `InodeStore`, `RocksInodeStore`, `HeapInodeStore`, `MutableInodeDirectory`, `CreateDirectoryContext`, `CheckpointInputStream`, and `PropertyKey.MASTER_METASTORE_DIR`. Helpers `runBenchmarks`, `writeBenchmark`, `checkpointBenchmark`, `doForMs`, and `writeInode` drive the workload.

Control flow: `main` enables console logging, benchmarks a Rocks inode store from the configured metastore directory, then benchmarks a heap inode store. Write benchmark warms up for two seconds, then runs five three-second rounds with four threads sharing a `CyclicBarrier`, counting directory inode writes. Checkpoint benchmark clears the store, writes one million inodes, writes a checkpoint to a temp file, restores it, and prints elapsed milliseconds.

State and persistence behavior: Rocks state is under the configured metastore directory; heap state is in-memory. Checkpoint state is written to a temp file and restored into the same static store.

Dependencies and integration points: not a JUnit test; intended for manual performance checks of metastore implementations and checkpoint serialization paths.

Risks: static `NEXT_INODE_ID` is not reset between benchmark phases, so IDs monotonically grow across stores. Restore into the same store after checkpoint write may not model a cold empty restore. No assertions or automated pass/fail thresholds exist.

Test signals: provides manual throughput/checkpoint timing signal only; not suitable as deterministic correctness coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreBench.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreCheckpointTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreCheckpointTest.java

Purpose: parameterized checkpoint/restore tests for inode stores across heap, Rocks with default cache, and Rocks with disabled cache.

Important APIs/types/functions: uses `MasterUtils.getInodeStoreFactory`, `MetastoreType`, `InodeStore.writeToCheckpoint`, `restoreFromCheckpoint`, directory checkpoint APIs with an `ExecutorService`, `CheckpointInputStream`, and `InodeLockManager`.

Control flow: parameters cover heap and Rocks variants. Setup configures metastore type/cache size, creates a base store, writes root plus three child directories, and removes inode 2. `testOutputStream` writes a checkpoint to a file output stream, creates a new store, and restores from a checkpoint input stream. `testDirectory` writes and restores a directory-format checkpoint using a two-thread executor. The `@After` method acts as the shared assertion block, verifying restored root, inode 1, missing inode 2, and inode 3, then closing both stores.

State and persistence behavior: checkpoint output is either a single file or a directory. New store state must exactly reflect persisted inode entries and removals.

Dependencies and integration points: covers checkpoint compatibility for metastore factory output and both stream and directory checkpoint protocols.

Risks: assertions run in `@After`, which can obscure failures if setup fails before `mNewInodeStore` is initialized. Edges/children are not explicitly checked, only inode records.

Test signals: solid signal for basic inode checkpoint round-trip across configured metastore implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreCheckpointTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTest.java

Purpose: common inode store contract tests for heap, Rocks, and caching Rocks implementations.

Important APIs/types/functions: extends `InodeStoreTestBase`, using `InodeStore`, `MutableInodeDirectory`, `MutableInodeFile`, `Inode`, `WriteBatch`, `CloseableIterator`, `RocksInodeStore`, `CachingInodeStore`, and Rocks config key `ROCKS_INODE_CONF_FILE`.

Control flow: Rocks-specific tests reopen stores with valid or invalid Rocks options files, expecting successful read/write or a `RocksDBException` cause. CRUD tests cover `get`, `getMutable`, `getChild`, inode removal, child edge removal, and updating inode modification time. `batchWrite` verifies atomic write/remove of inode and edge for stores that support batches. Listing tests add/remove/re-add children, repeatedly remove and add the same edge, force cache churn with extra directories, and check child listing size. `manyOperations` builds a 100-directory deep tree with files, verifies presence, deletes all files and parent edges, then renames a middle directory to root and verifies descendant linkage and old parent emptiness.

State and persistence behavior: heap state is in-memory; Rocks/caching state persists in temporary directories. Inode and edge state are tested together through parent-child lookups and listings.

Dependencies and integration points: captures the core contract consumed by `InodeTree` and file-system master metadata operations.

Risks: locking correctness is delegated to base helper locks but concurrent mutation is not tested here. Batch rollback/failure behavior is not covered.

Test signals: strong cross-implementation signal for inode/edge CRUD, listing consistency, batch writes, and Rocks config handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTestBase.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTestBase.java

Purpose: shared parameterization and helper layer for inode store tests.

Important APIs/types/functions: provides parameter suppliers for `HeapInodeStore`, `RocksInodeStore`, and `CachingInodeStore`; configures cache size, eviction batch size, and Netty leak detector settings; owns `InodeLockManager`, root inode, and helper methods `writeInode`, `writeEdge`, `removeInode`, `removeParentEdge`, `inodeDir`, and `inodeFile`.

Control flow: static `parameters` creates a temporary directory and writes a Rocks options file used by child tests. `before` creates a new lock manager and store for each parameter. `after` closes the store. Helper methods acquire write locks for inode or edge operations before delegating to the store.

State and persistence behavior: test stores are fresh per test method but may share a static base directory. Lock acquisition models production expectations around inode/edge mutation.

Dependencies and integration points: all derived inode store tests rely on this to run identical scenarios against heap, Rocks, and caching implementations. The Rocks config string defines default, inodes, and edges column-family options.

Risks: static directory reuse means Rocks-backed tests must close/clear correctly to avoid cross-test contamination. Helpers hide lock boilerplate, so tests may not catch callers that omit locks unless the implementation enforces them.

Test signals: foundational infrastructure, not standalone coverage; it ensures derived tests exercise the same contract across implementations under leak-detection settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/RecursiveInodeIteratorTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/RecursiveInodeIteratorTest.java

Purpose: verifies recursive inode traversal order, locked path consistency, child skipping, and read-from resume behavior across inode store implementations.

Important APIs/types/functions: extends `InodeStoreTestBase`; uses `RecursiveInodeIterator`, `ReadOption`, `DescendantType.ALL`, `InodeTree`, `LockedInodePath`, `LockingScheme`, `InodeIterationResult`, `MountTable`, and mocked container/directory-id/UFS dependencies.

Control flow: `createInodeTree` builds a fixed tree under `/` with nested directories and files. `recursiveListing` locks root, obtains a skippable children iterator, and verifies each returned path and inode id in expected depth-first order, including `LockedInodePath.traverse`. `recursiveListingSkipChildren` calls `skipChildrenOfTheCurrent` for selected directories and verifies their descendants are omitted. `recursiveListingStartFrom1` uses `readFrom("a/b/c/f11")` to skip `/a/b/c/f1` but include later siblings. `recursiveListingStartFrom2` starts from `a/c/f3`, skipping earlier branches and children before that key. `recursiveListingStartFromSkipAll` starts from `z` and expects only root.

State and persistence behavior: inode/edge state is written to the parameterized store. Iteration state includes cursor position, locked path, and optional subtree skip flags.

Dependencies and integration points: tests the iterator used by recursive listing operations in the file-system master with lock-aware path traversal.

Risks: expected orders are hard-coded to current lexical/depth-first semantics. Mount behavior is mocked, so mount boundary traversal is not covered.

Test signals: strong signal for recursive listing correctness, resume cursors, and skip behavior across heap/Rocks/caching stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/RecursiveInodeIteratorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/caching/CachingInodeStoreMockedBackingStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/caching/CachingInodeStoreMockedBackingStoreTest.java

Purpose: tests `CachingInodeStore` cache hit behavior, eviction, listing cache accounting, backing-store flush, checkpoint restore, and skip-cache reads using a spied heap backing store.

Important APIs/types/functions: uses `CachingInodeStore`, `HeapInodeStore`, `InodeStore`, `ReadOption`, `CheckpointInputStream`, cache internals `mInodeCache`, `mEdgeCache`, and `mListingCache`, plus Mockito read/write verification.

Control flow: setup creates a spied heap backing store, wraps it in `CachingInodeStore`, and writes one test directory. Basic cache tests repeatedly call `getMutable`, `get`, `getChild`, and `getChildren` and verify no backing reads. Many-read tests create more inodes/edges than cache size and assert backing writes do not exceed expected once-per-object levels. Removal/write tests ensure cached values reflect deletes and updates. Eviction tests force inode/edge evictions and verify backing reads occur when needed. `edgeIndexTest` runs concurrent add/remove operations, waits for eviction sleep, and verifies edge cache indices. Listing cache tests cover many directories, one large directory, and add/remove edge churn without incorrect weight growth. `flushToBackingStore` verifies cache flush pushes inodes/edges to backing. `backupRestore` checkpoint round-trips cached state. `skipCache` reads from backing without populating the inode cache.

State and persistence behavior: state is split between caches and heap backing store; explicit flush synchronizes. Checkpoint state is serialized to an in-memory byte array.

Dependencies and integration points: targets production cache behavior used by Rocks-backed inode stores and recursive/listing paths.

Risks: accesses package-private cache internals, making tests sensitive to implementation refactors. Concurrency test is time/operation-count based.

Test signals: strong targeted signal for cache correctness, eviction invariants, backing-store isolation, and checkpoint compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/caching/CachingInodeStoreMockedBackingStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksBlockMetaStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksBlockMetaStoreTest.java

Purpose: tests Rocks-backed block metastore iterator lock cleanup and behavior during checkpoint/restore while long-running readers exist.

Important APIs/types/functions: uses `RocksBlockMetaStore`, `RocksStoreTestUtils.waitForReaders`, `BlockMetaStore.Block`, `CloseableIterator`, `CheckpointInputStream`, `Block.BlockMeta`, executor services, latches, queues, and `PropertyKey.MASTER_METASTORE_ROCKS_EXCLUSIVE_LOCK_TIMEOUT`.

Control flow: setup configures short Rocks exclusive-lock timeouts and test mode, creates a store and executor. `escapingIteratorExceptionInNext` and `escapingIteratorExceptionInHasNext` wrap the store iterator in `FlakyRocksBlockStore`, throw after five iterations from `next` or `hasNext`, and assert shared lock count returns to zero after the exception and close. `longRunningIterAndCheckpoint` disables test mode, prepares 400 blocks, starts 20 iterators that pause after ten entries, writes a checkpoint while readers are paused, releases them, and expects every reader to complete all 400 entries without errors. `longRunningIterAndRestore` writes a checkpoint, pauses 20 readers, restores from the checkpoint while readers are active, releases them, and expects all readers to abort at ten entries with errors because Rocks contents changed.

State and persistence behavior: RocksDB column-family state stores block metadata. Checkpoint writes a non-empty file; restore replaces store contents and invalidates active readers.

Dependencies and integration points: covers Rocks shared/exclusive lock coordination, iterator resource management, block checkpoint/restore, and reader behavior under concurrent maintenance operations.

Risks: timing depends on latches but still uses concurrent threads. The flaky wrapper extends `RocksInodeStore` only to host the wrapper class, so it is test scaffolding rather than a real delegate type.

Test signals: strong signal for avoiding Rocks shared-lock leaks and preserving/aborting long-running iterators appropriately around checkpoint and restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksBlockMetaStoreTest.java -->
