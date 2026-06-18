# Research: subset-b-000471

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSystem.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSystem.java

## Purpose
`UfsJournalSystem` is the current UFS-backed implementation of `AbstractJournalSystem`. It creates one `UfsJournal` per master under a shared base URI and coordinates lifecycle, primacy transitions, catchup, formatting, checkpointing, and sequence-number reporting across those journals.

## Important APIs, Types, and Functions
The important entry points are the constructor, `createJournal(Master)`, `gainPrimacy()`, `losePrimacy()`, `suspend()`, `resume()`, `catchup()`, `waitForCatchup()`, `getCurrentSequenceNumbers()`, `startInternal()`, `stopInternal()`, `isFormatted()`, `isEmpty()`, `format()`, and `checkpoint(StateLockManager)`. It uses `UfsJournal`, `UfsJournalCheckpointThread.CatchupState`, `CatchupFuture`, `JournalSink`, `StateLockManager`, `StateLockOptions`, `MetricsSystem`, `Timer`, `CommonUtils.invokeAll`, `CommonUtils.waitFor`, `Closer`, and `ExponentialTimeBoundedRetry`.

## Control Flow, State, and Persistence
The system stores `mBase`, a quiet-time gate for standby-to-primary promotion, a concurrent map from master name to journal, and `mInitialCatchupTimeMs` for one-time catchup metrics. `createJournal()` appends the master name to the base URI, builds a sink supplier, records the journal, and returns it to the caller. Primacy gain is parallelized with `CommonUtils.invokeAll()` and propagates failures as runtime exceptions so a standby master crashes instead of serving with partially promoted journals. Primacy loss first signals every journal, then waits for each one to finish demotion.

Catchup receives a map of master names to target sequence numbers, delegates to each journal, and returns a combined future. `waitForCatchup()` polls every journal until all checkpoint threads report `DONE` or the configured maximum catchup time expires, recording the initial catchup duration either way. Checkpointing takes the master state lock exclusively before invoking each journal checkpoint, so snapshot persistence is coordinated with state mutation.

## Dependencies and Integration Points
This class is integrated into master startup and leader election through `AbstractJournalSystem`. It depends on Alluxio configuration keys for UFS catchup timeout, metric keys for UFS journal catchup/initial replay, master journal sink registration, URI path helpers, retry helpers, and the per-master `UfsJournal` implementation. Persistent effects are all delegated to the per-master UFS journals.

## Risks and Test Signals
Risks include partial journal promotion if a journal blocks inside `gainPrimacy()`, timeout-only handling in `waitForCatchup()` where startup continues after logging, and `catchup()` assuming every journal name exists in the supplied sequence map. Useful signals are multi-master promotion/demotion tests, catchup timeout metrics, checkpoint tests verifying state-lock exclusion, retry-on-close behavior, and sequence-number consistency across all registered journals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/AsyncJournalWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/AsyncJournalWriter.java

## Purpose
This legacy `journalv0` `AsyncJournalWriter` provides asynchronous append accounting and batched flushing on top of a synchronous `JournalWriter`. It lets callers append entries, receive a monotonically increasing counter, and later wait until that counter has been flushed.

## Important APIs, Types, and Functions
The class exposes `appendEntry(JournalEntry)` and `flush(long)`. It stores a `JournalWriter`, a `ConcurrentLinkedQueue<JournalEntry>`, atomic counters for appended, written, and flushed entries, a flush batch duration derived from `MASTER_JOURNAL_FLUSH_BATCH_TIME_MS`, and a fair `ReentrantLock` protecting actual writes and flushes.

## Control Flow, State, and Persistence
`appendEntry()` increments `mCounter` before enqueueing, then returns the current counter after enqueueing. This preserves the invariant that the returned counter is at least the entry's position even without an append lock. `flush(targetCounter)` returns immediately if the target is already flushed, otherwise it takes `mFlushLock`, drains queued entries through `mJournalWriter.write()`, updates `mWriteCounter`, optionally continues past the target within the configured batch window, then calls `mJournalWriter.flush()` and advances `mFlushCounter`.

Persistence is delegated to the underlying writer; this class only orders and batches writes. If a write throws, the queue head is left in place because it is polled only after a successful write. If flush throws, `mFlushCounter` is not advanced, so later flush calls retry.

## Dependencies and Integration Points
It depends on the legacy protobuf `JournalEntry`, `JournalWriter`, Alluxio configuration, Guava `Preconditions`, atomics, concurrent queues, and locks. It is the asynchronous facade used by legacy journal writers to amortize flush overhead while preserving caller-visible durability counters.

## Risks and Test Signals
Risks include an unbounded queue, contention around the fair flush lock, repeated retries of a permanently failing head entry, and reliance on caller discipline to flush returned counters. Signals are append counter monotonicity, no lost entries after write failure, no flush-counter advancement after flush failure, batch-window throughput, and concurrent append/flush ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/AsyncJournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/Journal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/Journal.java

## Purpose
`Journal` is the legacy read-only journal abstraction. It gives callers a location, reader, and formatted-state check while intentionally not exposing a writer.

## Important APIs, Types, and Functions
The interface defines `getLocation()`, `getReader()`, and `isFormatted()`. The nested `Journal.Factory` implements `JournalFactory`, appends names to a base URI, and creates `UfsJournal` instances. `Factory.create(URI)` builds a read-only UFS journal for a concrete location.

## Control Flow, State, and Persistence
The interface has no state. The nested factory stores only `mBase`; each `create(String)` appends the requested name and converts URI syntax failures to runtime exceptions. All persistence and replay behavior is supplied by the `UfsJournal` implementation returned by the factory.

## Dependencies and Integration Points
It depends on `alluxio.master.journalv0.ufs.UfsJournal`, `JournalReader`, `JournalFactory`, and `URIUtils`. It is the read side of the legacy journal stack and is extended by `MutableJournal` for read-write use.

## Risks and Test Signals
Risks are mostly URI handling and accidental use where a mutable journal is required. Test signals include factory path construction, `isFormatted()` delegation, and reader behavior against formatted and unformatted UFS journal directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/Journal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalCheckpointStreamable.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalCheckpointStreamable.java

## Purpose
`JournalCheckpointStreamable` is a small legacy contract for components that can stream their checkpoint representation directly as journal entries.

## Important APIs, Types, and Functions
It defines `streamToJournalCheckpoint(JournalOutputStream)` and allows `IOException` propagation.

## Control Flow, State, and Persistence
Implementations are expected to write one or more entries to the supplied `JournalOutputStream`. The interface itself stores no state; sequence numbering, flushing, and physical persistence are handled by the stream implementation.

## Dependencies and Integration Points
It depends only on `JournalOutputStream` and `IOException`. It integrates with legacy checkpoint creation when stateful components want to avoid materializing all checkpoint entries at once.

## Risks and Test Signals
Risks include partial checkpoint writes if implementations do not propagate failures correctly, and duplicate/missing entries if stream order is not deterministic. Useful signals are checkpoint round-trip tests and stream-close/flush behavior under implementation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalCheckpointStreamable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalEntryRepresentable.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalEntryRepresentable.java

## Purpose
`JournalEntryRepresentable` marks an object that can produce its protobuf `JournalEntry` representation for legacy journaling.

## Important APIs, Types, and Functions
It defines `toJournalEntry()`, returning `alluxio.proto.journal.Journal.JournalEntry`.

## Control Flow, State, and Persistence
The interface has no internal state. Implementations are responsible for translating their current object state into a journal entry; sequence numbers are normally added later by the journal output stream.

## Dependencies and Integration Points
It depends only on the generated journal protobuf. It integrates with checkpoint and log writers that accept `JournalEntry` objects.

## Risks and Test Signals
Risks include incomplete or stale object-to-entry conversion and incorrectly pre-setting sequence numbers. Signals are journal replay tests for each implementing type and coverage checks that every persisted domain object has a valid entry representation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalEntryRepresentable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFactory.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFactory.java

## Purpose
`JournalFactory` is the legacy factory abstraction for creating named journals under an implementation-defined backing store.

## Important APIs, Types, and Functions
It defines one method, `Journal create(String name)`.

## Control Flow, State, and Persistence
The interface carries no state and imposes no persistence behavior. Implementations decide how names map to physical journal locations, such as appending names to a base URI for UFS-backed journals.

## Dependencies and Integration Points
It depends on `Journal` and is implemented by nested factories in `Journal` and `MutableJournal`.

## Risks and Test Signals
Risks are name-to-path collisions, inconsistent read-only versus read-write factory behavior, and unchecked URI failures. Test signals are factory construction for multiple names and correct concrete journal type selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFormatter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFormatter.java

## Purpose
`JournalFormatter` abstracts serialization and deserialization of legacy journal entries. It lets storage implementations treat journal streams uniformly while the formatter owns entry framing.

## Important APIs, Types, and Functions
The interface defines `serialize(JournalEntry, OutputStream)` and `deserialize(InputStream)`. Its nested `Factory.create()` currently returns `ProtoBufJournalFormatter`.

## Control Flow, State, and Persistence
The formatter contract is stateless. Serialization writes one entry to an output stream; deserialization wraps an input stream in a `JournalInputStream` that yields entries until end of stream or truncation. Actual persistence is performed by the caller's streams.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry`, Java I/O streams, `JournalInputStream`, and `ProtoBufJournalFormatter`. It is used by `UfsJournalReader`, `UfsJournalWriter`, and `JournalTool`.

## Risks and Test Signals
Risks include format changes that break replay compatibility and deserializers that treat corrupted tail bytes incorrectly. Signals are protobuf round trips, truncated-entry handling, sequence-number tracking, and ability of `JournalTool` to read production log files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFormatter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalInputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalInputStream.java

## Purpose
`JournalInputStream` is the legacy entry-level read abstraction for checkpoint and log streams.

## Important APIs, Types, and Functions
It extends `AutoCloseable` and defines `read()`, `close()`, and `getLatestSequenceNumber()`.

## Control Flow, State, and Persistence
Implementations read the next `JournalEntry`, return `null` at end of stream, and track the latest sequence number seen. The interface does not prescribe buffering or corruption handling.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry` and `IOException`. It is returned by `JournalFormatter.deserialize()`, `JournalReader.getCheckpointInputStream()`, and `JournalReader.getNextInputStream()`.

## Risks and Test Signals
Risks include callers forgetting to read the checkpoint before logs, missing close semantics, and replay code misinterpreting `null` caused by a truncated entry. Signals include checkpoint replay order, latest-sequence correctness, and stream closure over UFS input streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalOutputStream.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalOutputStream.java

## Purpose
`JournalOutputStream` is the legacy entry-level write abstraction for checkpoint and log output.

## Important APIs, Types, and Functions
It extends `AutoCloseable` and defines `write(JournalEntry)`, `close()`, and `flush()`.

## Control Flow, State, and Persistence
Implementations write entries, may assign sequence numbers, flush buffered bytes, and close physical resources. Checkpoint and log implementations can enforce different ordering rules behind the same interface.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry` and `IOException`. It is returned by `JournalWriter.getCheckpointOutputStream()` and implemented by UFS checkpoint/log streams.

## Risks and Test Signals
Risks include writing after close, forgetting to flush log entries, and differing durability semantics on UFS backends that do not support flush. Signals are write-after-close failures, forced log rotation on no-flush stores, and checkpoint close updating the active checkpoint atomically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalReader.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalReader.java

## Purpose
`JournalReader` defines the legacy journal replay protocol: read a checkpoint first, then read completed logs in creation order while rejecting readers whose checkpoint changes during replay.

## Important APIs, Types, and Functions
It defines `isValid()`, `getCheckpointInputStream()`, `getNextInputStream()`, and `getCheckpointLastModifiedTimeMs()`.

## Control Flow, State, and Persistence
The contract requires callers to consume the checkpoint before requesting logs. `getNextInputStream()` returns only completed logs and returns `null` when the next completed log is not available. Validity is based on checkpoint last-modified time captured when the checkpoint stream was opened.

## Dependencies and Integration Points
It depends on `JournalInputStream` and `IOException`; `UfsJournalReader` provides the UFS implementation. Replay engines use it to reconstruct master state from persistent checkpoint and completed log files.

## Risks and Test Signals
Risks include timestamp granularity problems on some filesystems, replay races with checkpoint updates, and missed current-log entries because only completed logs are exposed. Signals include checkpoint-first enforcement, invalidation after checkpoint update, and sequential completed-log replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalTool.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalTool.java

## Purpose
`JournalTool` is a CLI utility for reading binary legacy journal entries from stdin and printing human-readable protobuf text separated by divider lines.

## Important APIs, Types, and Functions
Key functions are `main(String[])`, `parseInputArgs(String[])`, `stdinHasData()`, and `usage()`. It uses Apache Commons CLI options `-help` and `-noTimeout`, `ProtoBufJournalFormatter`, `JournalInputStream`, `JournalEntry`, `CommonUtils.sleepMs`, and `RuntimeConstants.VERSION`.

## Control Flow, State, and Persistence
`main()` parses options, prints usage on invalid input or help, optionally waits up to two seconds for stdin data, then deserializes stdin as protobuf-delimited journal entries. Each entry is printed to stdout followed by an 80-character separator. It does not write files or mutate journal state.

## Dependencies and Integration Points
The tool depends on the legacy journal formatter and standard input redirection. It is intended for operational debugging of files such as `journal/FileSystemMaster/log.out` from an Alluxio server assembly.

## Risks and Test Signals
Risks include reliance on `System.in.available()` for timeout behavior, process exits that complicate unit tests, and inability to recover from malformed/truncated streams beyond formatter behavior. Signals are successful decoding of known log files, `-help` output, `-noTimeout` behavior for pipes, and readable separators between printed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalWriter.java

## Purpose
`JournalWriter` defines the legacy read-write journal persistence protocol. It separates checkpoint creation from incremental log writes and provides recovery and log-compaction operations.

## Important APIs, Types, and Functions
The interface defines `completeLogs()`, `getCheckpointOutputStream(long)`, `write(JournalEntry)`, `flush()`, `getNextSequenceNumber()`, `close()`, `recover()`, `deleteCompletedLogs()`, and `completeCurrentLog()`.

## Control Flow, State, and Persistence
The contract requires checkpoint output to be obtained and closed before normal log writes begin. Checkpoints should represent master state with completed logs applied; subsequent current logs contain later entries. Completing logs moves current log data into the completed-log sequence, and deleting completed logs is safe after a checkpoint reflects their state.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry`, `JournalOutputStream`, and `IOException`. `UfsJournalWriter` is the concrete implementation in this subset, and `AsyncJournalWriter` can wrap it for batched flushing.

## Risks and Test Signals
Risks include caller misuse of checkpoint-before-log ordering, sequence-number gaps, deleting logs before a durable checkpoint update, and close/recover idempotency. Signals are checkpoint/log replay round trips, crash-recovery simulations, log rotation tests, and sequence-number monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/MutableJournal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/MutableJournal.java

## Purpose
`MutableJournal` extends the legacy read-only `Journal` with formatting and writer access, making it the read-write journal abstraction.

## Important APIs, Types, and Functions
It adds `format()` and `getWriter()`. The nested `MutableJournal.Factory` implements `JournalFactory`, appends names to a base URI, and returns `UfsMutableJournal` instances. `Factory.create(URI)` creates a mutable journal at a concrete location.

## Control Flow, State, and Persistence
The interface itself has no state. The factory stores `mBase` and delegates all persistence to UFS mutable journals. Formatting is expected to clear and initialize the underlying journal directory before writers are used.

## Dependencies and Integration Points
It depends on `Journal`, `JournalWriter`, `UfsMutableJournal`, and `URIUtils`. It is used by components that need to initialize or mutate legacy journal state.

## Risks and Test Signals
Risks include formatting the wrong URI, mixing mutable and read-only factory use, and URI syntax failures converted to runtime exceptions. Signals are format breadcrumb creation, writer creation, and factory path correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/MutableJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ProtoBufJournalFormatter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ProtoBufJournalFormatter.java

## Purpose
`ProtoBufJournalFormatter` is the legacy formatter implementation for protobuf-delimited journal entries. It writes length-delimited `JournalEntry` records and reads them back while tracking the latest sequence number.

## Important APIs, Types, and Functions
It implements `serialize(JournalEntry, OutputStream)` with `writeDelimitedTo()` and `deserialize(InputStream)` by returning an anonymous `JournalInputStream`. The reader uses `ProtoUtils.readRawVarint32()`, a reusable 1 KiB buffer for small entries, `JournalEntry.parseFrom()`, and `getLatestSequenceNumber()`.

## Control Flow, State, and Persistence
On read, the stream consumes the first byte, returns `null` for EOF, decodes the varint size, reads exactly that many bytes, logs and returns `null` for truncated entries, parses the entry, and records its sequence number. It does not close or advance any outer journal state except through the wrapped input stream.

## Dependencies and Integration Points
It depends on generated journal protobufs, `ProtoUtils`, Java I/O, and SLF4J. It is used by UFS readers/writers and `JournalTool`.

## Risks and Test Signals
Risks include memory allocation for very large entry sizes, accepting truncated tail entries as end of stream, and compatibility with protobuf delimiter semantics. Signals are exact round trips, latest-sequence updates, corrupted-tail behavior during log replay, and compatibility with older generated `JournalEntry` schemas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ProtoBufJournalFormatter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsCheckpointManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsCheckpointManager.java

## Purpose
`UfsCheckpointManager` manages crash-safe updates to a legacy UFS journal checkpoint. It coordinates temporary checkpoint, backup checkpoint, completed-log cleanup, and recovery from interrupted rename sequences.

## Important APIs, Types, and Functions
The main methods are `recover()` and `update(URI)`. State includes `mUfs`, `mCheckpoint`, `mBackupCheckpoint`, `mTempBackupCheckpoint`, and a `UfsJournalWriter` used to delete completed logs. It uses `UnderFileSystemUtils.deleteFileIfExists()` and UFS `renameFile()`.

## Control Flow, State, and Persistence
`update()` deletes stale backup files, renames the existing checkpoint to a temporary backup and then to a stable backup, renames the new temporary checkpoint into `checkpoint.data`, deletes completed logs because the new checkpoint includes them, and removes the backup. `recover()` inspects the presence of checkpoint, backup, and temp backup files, restores `checkpoint.data` from the temp backup if needed, either rolls back from backup or finalizes cleanup after a completed rename, and asserts that all three files never coexist.

## Dependencies and Integration Points
It depends on `UnderFileSystem`, `UfsJournalWriter`, Guava `Preconditions`, URI construction, and UFS file operations. It is invoked by `UfsJournalWriter` before creating a checkpoint stream and when closing a completed checkpoint.

## Risks and Test Signals
Risks include UFS rename implementations that behave as copy-plus-delete, path handling via `location.getPath()` for new checkpoints, runtime exception wrapping of I/O failures, and log deletion before backup cleanup. Signals are crash-recovery matrix tests for every rename step, object-store rename behavior, completed-log deletion after checkpoint success, and idempotent recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsCheckpointManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournal.java

## Purpose
`UfsJournal` is the legacy read-only UFS journal implementation. It defines the directory layout and exposes reader creation and formatted-state detection.

## Important APIs, Types, and Functions
Important methods are `getCompletedLocation()`, `getCheckpoint()`, `getCurrentLog()`, `getCompletedLog(long)`, `getJournalFormatter()`, `getLocation()`, `getReader()`, and `isFormatted()`. Constants define `completed/`, `log.out`, `checkpoint.data`, and zero-padded completed log filenames.

## Control Flow, State, and Persistence
The class stores a journal URI and a formatter. It maps checkpoint and log concepts to deterministic UFS paths: the current log lives in the base directory, completed logs live in `completed/log.%020d`, and the checkpoint is `checkpoint.data`. `isFormatted()` opens the UFS, lists the base path, and searches for a configured format-file prefix.

## Dependencies and Integration Points
It depends on Alluxio configuration, `UnderFileSystem`, `UnderFileSystemConfiguration`, `UfsStatus`, `URIUtils`, and `JournalFormatter`. It is used by both read-only `Journal.Factory` and mutable subclasses.

## Risks and Test Signals
Risks include unformatted directories returning `null` from `listStatus()`, path construction failures, format-prefix false positives, and timestamp/path behavior across UFS implementations. Signals include formatted and unformatted detection, reader creation, completed-log path ordering, and compatibility with `UfsJournalWriter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalReader.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalReader.java

## Purpose
`UfsJournalReader` implements checkpoint-first, completed-log replay for legacy UFS journals.

## Important APIs, Types, and Functions
It implements `isValid()`, `getCheckpointInputStream()`, `getNextInputStream()`, and `getCheckpointLastModifiedTimeMs()`. State includes the journal, UFS handle, checkpoint URI, `mCheckpointRead`, checkpoint opened/last-modified times, and current completed-log number.

## Control Flow, State, and Persistence
`getCheckpointInputStream()` can be called only once, captures the checkpoint's last modified time, opens the checkpoint through UFS, wraps it with the journal formatter, and marks the checkpoint as read. `getNextInputStream()` requires the checkpoint to have been read and rejects use if the checkpoint timestamp has changed. It opens the next numbered completed log if present, increments the log number, and returns `null` when the expected log is absent.

## Dependencies and Integration Points
It depends on `UfsJournal`, `UnderFileSystem`, configuration defaults, `JournalFormatter`, and `JournalInputStream`. Replay code uses it to reconstruct state from `checkpoint.data` plus numbered completed logs.

## Risks and Test Signals
Risks include no explicit close for the reader-owned UFS handle, timestamp granularity invalidation gaps, and inability to read current `log.out` until it is completed. Signals include checkpoint-once enforcement, log numbering order, missing-checkpoint failures, checkpoint-update invalidation, and deserializer behavior on truncated logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalWriter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalWriter.java

## Purpose
`UfsJournalWriter` is the legacy UFS-backed journal writer. It owns checkpoint creation, sequence-number assignment, current-log writing, completed-log rotation, completed-log deletion, and UFS resource closure.

## Important APIs, Types, and Functions
The public methods are `completeLogs()`, `getCheckpointOutputStream(long)`, `write(JournalEntry)`, `flush()`, `getNextSequenceNumber()`, `close()`, `recover()`, `deleteCompletedLogs()`, and `completeCurrentLog()`. It contains `CheckpointOutputStream` for temporary checkpoint writes and `EntryOutputStream` for current-log writes/rotation. It uses `UfsCheckpointManager`, `JournalFormatter`, `UnderFileSystem`, `CreateOptions`, `ExceptionMessage`, and configuration key `MASTER_JOURNAL_LOG_SIZE_BYTES_MAX`.

## Control Flow, State, and Persistence
The writer creates a UFS handle, computes `completed/` and `checkpoint.data.tmp` paths, and starts sequence numbers at one. `getCheckpointOutputStream()` recovers any interrupted checkpoint update, creates the journal directory if needed, sets the next sequence number from the supplied latest sequence, deletes stale temp checkpoint files, and returns a singleton checkpoint stream. Normal `write()` and `flush()` reject calls until the checkpoint stream has been closed.

`CheckpointOutputStream.write()` assigns a sequence number and serializes entries to the temporary checkpoint. Closing the checkpoint flushes and closes the temp file, atomically updates `checkpoint.data` through `UfsCheckpointManager`, completes any current log, and marks the stream closed. `EntryOutputStream` writes current log entries with assigned sequence numbers, flushes them, and marks the log for rotation when it exceeds max size, when UFS does not support flush, or after write/flush failures. Rotation closes `log.out`, renames it to the next completed log, and opens a fresh current log.

## Dependencies and Integration Points
It integrates with `UfsMutableJournal`, `AsyncJournalWriter`, `UfsCheckpointManager`, and legacy replay through `UfsJournalReader`. Persistent artifacts are `checkpoint.data.tmp`, `checkpoint.data`, `checkpoint.data.backup`, `log.out`, and `completed/log.%020d`.

## Risks and Test Signals
Risks include sequence-number gaps if serialization fails after incrementing, `deleteCompletedLogs()` iterating down to log zero, UFS rename semantics, no-flush object-store durability, singleton stream lifecycle misuse, and runtime exceptions during checkpoint update recovery. Signals are checkpoint-before-log enforcement, write-after-close errors, crash recovery for checkpoint files, log rotation on size/no-flush/error, replay from checkpoint plus completed logs, and UFS handle closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsMutableJournal.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsMutableJournal.java

## Purpose
`UfsMutableJournal` adds formatting and writer creation to `UfsJournal`, making a legacy UFS journal writable.

## Important APIs, Types, and Functions
It implements `format()` and `getWriter()`. Formatting uses `UnderFileSystem`, `UfsStatus`, recursive `DeleteOptions`, `URIUtils`, and `UnderFileSystemUtils.touch()`.

## Control Flow, State, and Persistence
`format()` opens the UFS, deletes every child of the journal directory if it exists, creates the directory if it does not, and writes a format breadcrumb whose name starts with the configured master format-file prefix and ends with the current timestamp. `getWriter()` returns a new `UfsJournalWriter` for this journal.

## Dependencies and Integration Points
It depends on `UfsJournal`, `MutableJournal`, Alluxio configuration, UFS APIs, and path utilities. It is used by `MutableJournal.Factory` to initialize writable legacy journals.

## Risks and Test Signals
Risks include destructive deletion of the journal directory contents, failure to delete nested directories or files, format breadcrumb prefix collisions, and repeated writer creation without external coordination. Signals are format clearing files/directories, directory creation, breadcrumb detection by `isFormatted()`, and writer persistence round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsMutableJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClient.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClient.java

## Purpose
`GrpcMessagingClient` creates outbound bidirectional messaging connections to remote embedded-journal transport servers.

## Important APIs, Types, and Functions
The main methods are the constructor, `connect(InetSocketAddress)`, and `close()`. It uses `GrpcChannelBuilder`, `GrpcServerAddress`, `MessagingServiceGrpc.MessagingServiceStub`, `GrpcMessagingClientConnection`, `GrpcMessagingContext.currentContextOrThrow()`, `UserState`, and request timeout configuration.

## Control Flow, State, and Persistence
`connect()` must be called from a `GrpcMessagingContext` thread. It builds the gRPC channel asynchronously on the transport executor, creates a stub, constructs a client connection, binds the connection as the response observer for `stub.connect()`, then completes the returned future back on the originating context. `close()` has no owned connection list and returns an already-completed future.

## Dependencies and Integration Points
It is created by `GrpcMessagingTransport.client()`, shares the transport executor, and authenticates channels with the configured user subject. It integrates with `GrpcMessagingConnection` for message serialization and lifecycle.

## Risks and Test Signals
Risks include calling from outside a messaging context, leaking channels if callers do not close returned connections, and `RuntimeException` wrapping of build errors. Signals are successful connection futures on the context thread, subject propagation, failure completion for channel build errors, and channel shutdown through `GrpcMessagingClientConnection.close()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClientConnection.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClientConnection.java

## Purpose
`GrpcMessagingClientConnection` specializes `GrpcMessagingConnection` for client-owned streams and closes the underlying gRPC channel when the logical connection closes.

## Important APIs, Types, and Functions
It defines a constructor and overrides `close()`. It stores a `GrpcChannel` and passes owner `CLIENT`, the channel key string, context, executor, and request timeout to the base class.

## Control Flow, State, and Persistence
The connection itself has no persistence. `close()` chains from `super.close()`, then attempts `mChannel.shutdown()` in a `finally` path and completes its result future with `null` even if shutdown logs a warning.

## Dependencies and Integration Points
It depends on the base connection state machine and Alluxio gRPC channel abstraction. It is created by `GrpcMessagingClient.connect()`.

## Risks and Test Signals
Risks include swallowing channel shutdown failures, completing close successfully even after base close errors, and requiring `setTargetObserver()` before use. Signals are pending request failure on close, stream completion, and channel shutdown invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClientConnection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingConnection.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingConnection.java

## Purpose
`GrpcMessagingConnection` is the core bidirectional messaging abstraction over a gRPC `StreamObserver<TransportMessage>`. It supports fire-and-forget sends, request/response futures, typed handlers, listener callbacks, close/error propagation, and request timeouts.

## Important APIs, Types, and Functions
Important methods include `setTargetObserver()`, `send()`, `sendAndReceive()`, `handler()`, `onException()`, `onClose()`, `close()`, `onNext()`, `onError()`, `onCompleted()`, `timeoutPendingRequests()`, and `failPendingRequests()`. Internal types include `ConnectionOwner`, `HandlerHolder`, and `ContextualFuture`. State includes listener collections, closed/stream flags, last failure, request counter, handler map, pending response map, owner, connection id, target observer, timeout scheduler, state read-write lock, and executor.

## Control Flow, State, and Persistence
Outbound sends take a read lock, create a context-bound future, reject closed connections, allocate a request id, store the future, serialize the request with the current context serializer, and call `mTargetObserver.onNext()`. Fire-and-forget sends complete immediately but still register a future. Inbound requests are deserialized on the connection context, dispatched to a handler context, and optionally responded to when the handler future completes. Inbound responses remove the pending future and complete it on the originating context, propagating serialized throwables as exceptions.

The timeout scheduler runs periodically from the context and fails old pending requests with `TimeoutException`. `close()` takes the write lock, marks closed, cancels the timeout scheduler, completes the gRPC stream if needed, fails pending requests with `ConnectException`, and invokes close listeners. `onError()` marks closed, records the failure for future listeners, fails pending requests, and invokes exception and close listeners. `onCompleted()` mirrors server/client stream completion and then closes.

## Dependencies and Integration Points
It depends on Alluxio gRPC message headers, protobuf `TransportMessage`, Atomix Catalyst serializer, `GrpcMessagingContext`, `Listeners`, `LockResource`, gRPC `StreamObserver`, Apache `Cancellable`, and Java concurrency primitives. It is subclassed by client and server connections and used by embedded journal transport.

## Risks and Test Signals
Risks include target observer not being set before send, fire-and-forget futures remaining in `mResponseFutures` until timeout, no removal of pending futures after send serialization failure, concurrent close/send races, serializer incompatibility, and response sends from outside the correct context. Signals are request/response round trips, unknown message type errors, timeout completion on originating contexts, listener close/unregister behavior, stream completion semantics for server-owned streams, and leak checks for pending futures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingConnection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingContext.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingContext.java

## Purpose
`GrpcMessagingContext` provides a single-threaded execution and scheduling context for gRPC messaging work, plus access to the serializer associated with that thread.

## Important APIs, Types, and Functions
Constructors accept a name format, a `GrpcMessagingThreadFactory`, or a `ScheduledExecutorService`. Important methods are `getThread(ExecutorService)`, `serializer()`, `executor()`, `schedule(Duration, Runnable)`, `schedule(Duration, Duration, Runnable)`, `close()`, `execute(Runnable)`, `execute(Supplier<T>)`, `currentContext()`, `currentContextOrThrow()`, and `logFailure(Runnable)`.

## Control Flow, State, and Persistence
The context installs itself into a `GrpcMessagingThread`. `executor()` returns a wrapper that logs failures and ignores rejected execution after shutdown. `schedule()` methods return cancellables wrapping scheduled futures. `execute()` submits work to the wrapped executor and completes a `CompletableFuture` with either result or exception. Current context lookup inspects the current thread and returns its weakly referenced context.

## Dependencies and Integration Points
It depends on `GrpcMessagingThread`, `GrpcMessagingThreadFactory`, Atomix Catalyst `Serializer`, Java scheduled executors, and Apache `Cancellable`. All client/server connection setup and handler completion paths require this context.

## Risks and Test Signals
Risks include executor initialization deadlock if the supplied executor is not usable, weak-reference context loss if no strong context reference remains, swallowed rejected executions, and unchecked assumptions that API calls happen on messaging threads. Signals are `currentContextOrThrow()` failures off-context, scheduled timeout execution, exception logging, close shutdown behavior, and handler/future callbacks running on the intended single thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingProxy.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingProxy.java

## Purpose
`GrpcMessagingProxy` stores optional address remapping for messaging servers, allowing a logical server address to bind through a different proxy address.

## Important APIs, Types, and Functions
It exposes `addProxy(InetSocketAddress, InetSocketAddress)`, `hasProxyFor(InetSocketAddress)`, and `getProxyFor(InetSocketAddress)`.

## Control Flow, State, and Persistence
The class stores a mutable `HashMap` from source address to proxy address. `addProxy()` mutates the map and returns `this` for chaining. There is no persistence or synchronization.

## Dependencies and Integration Points
It depends only on `InetSocketAddress` and collection classes. `GrpcMessagingServer.listen()` consults it before choosing the bind address.

## Risks and Test Signals
Risks include lack of thread safety, exact `InetSocketAddress` equality requirements, and stale proxy mappings. Signals are server binding to proxy addresses and non-proxied addresses binding directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServer.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServer.java

## Purpose
`GrpcMessagingServer` opens a gRPC server endpoint for embedded-journal messaging connections.

## Important APIs, Types, and Functions
Key methods are the constructor, `listen(InetSocketAddress, Consumer<GrpcMessagingConnection>)`, and `close()`. It uses `GrpcServerBuilder`, `GrpcService`, `GrpcMessagingServiceClientHandler`, `ClientContextServerInjector`, `GrpcMessagingProxy`, and max inbound message size/request timeout configuration.

## Control Flow, State, and Persistence
`listen()` is synchronized and reuses an existing non-exceptional listen future. It captures the current messaging context, resolves proxy bind address if configured, builds a gRPC server with the messaging service and client-context interceptor, starts it asynchronously on the transport executor, and stores the server reference. `close()` asynchronously shuts down the gRPC server and clears the reference.

## Dependencies and Integration Points
It is created by `GrpcMessagingTransport.server()` and provides the server side consumed by `GrpcMessagingClient.connect()`. It integrates with security context injection, Alluxio gRPC server configuration, and the caller's connection listener.

## Risks and Test Signals
Risks include listen calls outside a messaging context, reuse of a failed listen future semantics, asynchronous close using the common pool instead of the transport executor, and proxy misconfiguration. Signals are successful bind/start, max message size enforcement, listener invocation for new streams, proxy binding, and server shutdown releasing the port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServerConnection.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServerConnection.java

## Purpose
`GrpcMessagingServerConnection` specializes `GrpcMessagingConnection` for server-owned streams.

## Important APIs, Types, and Functions
It defines a constructor that passes owner `SERVER`, the transport id, context, executor, and request timeout to the base class.

## Control Flow, State, and Persistence
The class adds no additional state or persistence behavior. Server-specific completion behavior is handled by the base class through the `ConnectionOwner.SERVER` value.

## Dependencies and Integration Points
It depends on `GrpcMessagingConnection` and is instantiated by `GrpcMessagingServiceClientHandler.connect()`.

## Risks and Test Signals
Risks include relying entirely on base-class behavior and needing `setTargetObserver()` before use. Signals are server stream completion propagating to the client observer and server-side request/response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServerConnection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServiceClientHandler.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServiceClientHandler.java

## Purpose
`GrpcMessagingServiceClientHandler` is the gRPC service implementation that accepts client bidirectional streams and converts each stream into a server-side `GrpcMessagingConnection`.

## Important APIs, Types, and Functions
The key method is `connect(StreamObserver<TransportMessage>)`. State includes the server connection listener, server messaging context, request timeout, executor, and server address. It uses `ClientContextServerInjector.getIpAddress()` to include client address information in the transport id.

## Control Flow, State, and Persistence
When a client opens `connect`, the handler builds a transport id, creates a `GrpcMessagingServerConnection`, sets the client's response observer as its target observer, and synchronously registers the connection by executing the listener on the server messaging context. Interrupted registration restores the interrupt flag and throws; listener failures are wrapped in runtime exceptions.

## Dependencies and Integration Points
It extends `MessagingServiceGrpc.MessagingServiceImplBase` and is installed by `GrpcMessagingServer`. It bridges gRPC stream setup to the higher-level connection listener used by the embedded journal transport.

## Risks and Test Signals
Risks include blocking the gRPC service call while waiting for context registration, listener exceptions rejecting connection setup, and reliance on injected client IP for diagnostics only. Signals are listener invocation on the context thread, returned observer being the created server connection, and correct failure propagation on interrupted or failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServiceClientHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThread.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThread.java

## Purpose
`GrpcMessagingThread` is a `Thread` subclass that can hold the `GrpcMessagingContext` associated with the current messaging execution thread.

## Important APIs, Types, and Functions
It defines a constructor, `setContext(GrpcMessagingContext)`, and `getContext()`. The context is stored as a `WeakReference`.

## Control Flow, State, and Persistence
The thread starts with no context. `GrpcMessagingContext` sets itself after the thread is obtained from the executor. `getContext()` returns `null` if the weak reference has not been set or has been cleared. There is no persistence.

## Dependencies and Integration Points
It is created by `GrpcMessagingThreadFactory` and inspected by `GrpcMessagingContext.currentContext()`.

## Risks and Test Signals
Risks include weak-reference clearing, accidental use of non-messaging threads, and a typo in documentation not affecting behavior. Signals are context lookup from within the executor thread and `currentContextOrThrow()` rejection on ordinary threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThreadFactory.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThreadFactory.java

## Purpose
`GrpcMessagingThreadFactory` creates named `GrpcMessagingThread` instances for messaging contexts.

## Important APIs, Types, and Functions
It defines a constructor accepting a name format and `newThread(Runnable)`. It uses an `AtomicInteger` counter starting at one.

## Control Flow, State, and Persistence
Each `newThread()` call formats the thread name with the next counter value and returns a `GrpcMessagingThread`. There is no persistence.

## Dependencies and Integration Points
It implements `ThreadFactory` and is used by `GrpcMessagingContext` constructors.

## Risks and Test Signals
Risks include invalid name format strings and non-daemon thread behavior inherited from `Thread`. Signals are deterministic thread names and correct thread type for context installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThreadFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingTransport.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingTransport.java

## Purpose
`GrpcMessagingTransport` is the top-level factory and lifecycle owner for gRPC messaging clients and servers used by embedded journal transport.

## Important APIs, Types, and Functions
It exposes constructors, `withServerProxy(GrpcMessagingProxy)`, `client()`, `server()`, and `close()`. State includes client/server configurations and users, client type, lists of created clients and servers, server proxy config, a cached-thread-pool executor, and a closed flag.

## Control Flow, State, and Persistence
`client()` and `server()` are synchronized, reject calls after close, construct new objects sharing the transport executor, and track them for later shutdown. `withServerProxy()` replaces proxy configuration. `close()` marks the transport closed, closes all tracked clients and servers with `CompletableFuture.allOf().get()`, clears the lists, logs failures, and shuts down the executor.

## Dependencies and Integration Points
It depends on Alluxio configuration/user state, `GrpcMessagingClient`, `GrpcMessagingServer`, `GrpcMessagingProxy`, and `ThreadFactoryUtils`. It is the lifecycle boundary for transport resources but does not own per-connection objects returned by clients.

## Risks and Test Signals
Risks include clients not tracking their returned connections, close blocking on asynchronous futures, raw generic array creation, and no use of `mClientType` in this file. Signals are no client/server creation after close, all tracked servers shutting down, executor shutdown, and proxy propagation to new servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listener.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listener.java

## Purpose
`Listener` represents a registered event consumer that can unregister itself through `close()`.

## Important APIs, Types, and Functions
It extends `Consumer<T>` and `AutoCloseable`, defining `close()` with no checked exception.

## Control Flow, State, and Persistence
The interface has no state. Implementations consume events and remove themselves from their owner when closed.

## Dependencies and Integration Points
It depends on `Consumer` and is implemented by `Listeners.ListenerHolder`. `GrpcMessagingConnection` returns listener handles for exception and close events.

## Risks and Test Signals
Risks include forgetting to close listener handles and listener callbacks throwing. Signals are unregister behavior and no further events after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listeners.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listeners.java

## Purpose
`Listeners` is a small thread-safe listener registry that preserves the messaging context active at listener registration and replays events on that context when possible.

## Important APIs, Types, and Functions
It exposes `size()`, `add(Consumer<T>)`, `accept(T)`, and `iterator()`. Inner `ListenerHolder` implements `Listener<T>` with `accept(T)`, `close()`, `getContext()`, and `getListener()`. Storage is a `CopyOnWriteArrayList`.

## Control Flow, State, and Persistence
`add()` captures `GrpcMessagingContext.currentContext()` and returns a holder. `accept(T)` iterates listeners, executing callbacks on their captured context when present or inline otherwise, and returns a future aggregating context-executed callbacks. `ListenerHolder.accept()` similarly schedules or runs the callback and ignores rejected execution. `close()` removes the holder from the list.

## Dependencies and Integration Points
It depends on `GrpcMessagingContext`, `Listener`, Java futures, and Guava `Preconditions`. It is used for `GrpcMessagingConnection` close and exception listeners.

## Risks and Test Signals
Risks include inline listener exceptions interrupting dispatch, ignored rejected executions, raw generic use, and the aggregate future not representing inline callback failures. Signals are context capture, close removal, size changes, and callback execution order under concurrent modification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listeners.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/MetricsServlet.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/MetricsServlet.java

## Purpose
`MetricsServlet` is a metrics sink that exposes a Dropwizard `MetricRegistry` as pretty-printed JSON over HTTP.

## Important APIs, Types, and Functions
It defines `SERVLET_PATH` as `/metrics/json`, a shared Jackson `OBJECT_MAPPER` with Dropwizard `MetricsModule`, a constructor taking `MetricRegistry`, `createServlet()`, `getHandler()`, and no-op `start()`, `stop()`, and `report()`.

## Control Flow, State, and Persistence
`getHandler()` creates a Jetty `ServletContextHandler` at `/metrics/json` and mounts an anonymous servlet at `/`. The servlet handles GET by setting JSON content type, status OK, no-cache headers, serializing the registry, and writing the result. It stores no persistent state.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Jackson, Jetty servlet handlers, and the Alluxio `Sink` interface. `WebServer` installs its handler alongside Prometheus and application servlet handlers.

## Risks and Test Signals
Risks include expensive registry serialization, no access control in this class, and pretty-printed output size. Signals are HTTP 200 JSON responses, no-cache headers, and serialization of gauges, counters, timers, and histograms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/MetricsServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/PrometheusMetricsServlet.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/PrometheusMetricsServlet.java

## Purpose
`PrometheusMetricsServlet` exposes Dropwizard metrics in Prometheus format through the default Prometheus collector registry.

## Important APIs, Types, and Functions
It defines path `/metrics/prometheus`, constructors taking `MetricRegistry` or `Properties` plus registry, `getHandler()`, and no-op `start()`, `stop()`, and `report()`. It registers `DropwizardExports` in `CollectorRegistry.defaultRegistry`.

## Control Flow, State, and Persistence
Construction stores the default registry and registers a new Dropwizard exporter for the supplied registry. `getHandler()` creates a Jetty context and mounts Prometheus' `MetricsServlet` at `/`. There is no file persistence.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Prometheus Java client, Jetty, and `Sink`. `WebServer` installs it next to the JSON metrics endpoint.

## Risks and Test Signals
Risks include duplicate exporter registration in the global default registry if multiple servlet instances are created, no unregister on stop, and path-level exposure of all registered metrics. Signals are scrapeable Prometheus text output and absence of duplicate collector exceptions during repeated web-server construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/PrometheusMetricsServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisDropwizardExports.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisDropwizardExports.java

## Purpose
`RatisDropwizardExports` adapts Dropwizard metrics for Prometheus while applying Ratis-specific name rewriting.

## Important APIs, Types, and Functions
It extends `DropwizardExports`, constructs with `RatisNameRewriteSampleBuilder`, and exposes `registerRatisMetricReporters(Map<String, RatisDropwizardExports>)`. Private helpers `registerDropwizard()` and `deregisterDropwizard()` register/unregister collectors as Ratis metric registries appear or disappear.

## Control Flow, State, and Persistence
`registerRatisMetricReporters()` installs callbacks into `MetricRegistries.global()`. On registration, it wraps a Ratis Dropwizard registry, registers the collector in Prometheus' default registry, and records it by registry name. On deregistration, it removes the collector from the map and unregisters it if present.

## Dependencies and Integration Points
It depends on Apache Ratis metric registries, Prometheus collector registry, Dropwizard exports, and `RatisNameRewriteSampleBuilder`. It bridges Ratis embedded journal metrics into Alluxio's Prometheus endpoint.

## Risks and Test Signals
Risks include duplicate collector registration, deregistration races, and map thread-safety depending on caller-provided map. Signals are Ratis metrics appearing with rewritten labels, successful unregister on registry removal, and no default-registry collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisDropwizardExports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisNameRewriteSampleBuilder.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisNameRewriteSampleBuilder.java

## Purpose
`RatisNameRewriteSampleBuilder` rewrites Ratis Dropwizard metric names into Prometheus samples with explicit `instance`, `group`, and `follower` labels.

## Important APIs, Types, and Functions
It extends `DefaultSampleBuilder`, overrides `createSample()`, and defines `normalizeRatisMetric(String, List<String>, List<String>)`. It keeps regex patterns for follower-related metric names.

## Control Flow, State, and Persistence
For metric names starting with Ratis' application metrics prefix, `createSample()` copies the existing label lists, normalizes the name, appends labels, optionally logs trace output, and delegates to the parent. Non-Ratis names are passed through. Normalization splits names by `.`, extracts the third segment as `instance` and optional `group` separated by `@`, removes that segment, then matches follower-id patterns in the new third segment and converts follower ids into labels.

## Dependencies and Integration Points
It depends on Ratis metric naming constants, Prometheus Dropwizard sample builder APIs, regexes, and Log4j `Strings.join`. It is used by `RatisDropwizardExports`.

## Risks and Test Signals
Risks include regex overmatching, label cardinality from follower ids, unexpected metric name shapes, and mutation assumptions around label lists. Signals are representative Ratis metric names yielding stable sample names and labels, pass-through for non-Ratis metrics, and trace logs for rewritten metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisNameRewriteSampleBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/security/user/ServerUserState.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/security/user/ServerUserState.java

## Purpose
`ServerUserState` provides a process-global server `UserState` built from global Alluxio configuration.

## Important APIs, Types, and Functions
It contains a static `INSTANCE` initialized by `UserState.Factory.create(Configuration.global())`, a private constructor, and `global()`.

## Control Flow, State, and Persistence
The singleton is initialized at class load time and returned by `global()`. It has no persistence, reload, or synchronization logic beyond class initialization.

## Dependencies and Integration Points
It depends on `Configuration.global()` and `UserState`. Server components use it when they need a shared authentication user state.

## Risks and Test Signals
Risks include stale configuration if global auth settings change after class load, hidden initialization failures, and shared mutable state inside `UserState`. Signals are correct subject creation under server auth configurations and stable reuse across callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/security/user/ServerUserState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/underfs/AbstractUfsManager.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/underfs/AbstractUfsManager.java

## Purpose
`AbstractUfsManager` is a shared base implementation of `UfsManager`. It caches `UnderFileSystem` instances by scheme, authority, and mount-specific properties, tracks mount-id to client mappings, and lazily initializes root and journal UFS clients.

## Important APIs, Types, and Functions
Important pieces include nested `Key`, `getOrAddWithRecorder()`, abstract `connectUfs(UnderFileSystem)`, `addMount()`, `addMountWithRecorder()`, `removeMount()`, `get(long)`, `getRoot()`, `getJournal(URI)`, `close()`, and `hasMount(long)`. It uses `UfsClient`, `UnderFileSystemConfiguration`, `ManagedBlockingUfsForwarder`, `Recorder`, `IdUtils`, `Closer`, and Alluxio configuration keys for root and UFS managed-blocking behavior.

## Control Flow, State, and Persistence
Mount registration stores a lazy `UfsClient` supplier that calls `getOrAddWithRecorder()`. On cache miss, UFS creation is synchronized, creates an `UnderFileSystem`, optionally wraps object stores or configured UFSes with `ManagedBlockingUfsForwarder`, registers the UFS with `Closer`, calls subclass-specific `connectUfs()`, probes availability with `exists(path)`, and stores the instance in the cache. `getRoot()` lazily creates the root mount from global configuration; `getJournal()` lazily creates the journal mount using `UfsJournal.getJournalUfsConf()`.

## Dependencies and Integration Points
It depends on Alluxio URI/configuration, UFS factories, mount ids, recorder diagnostics, and subclasses that decide master versus worker connection calls. It is used by master and worker components needing mount-backed UFS access.

## Risks and Test Signals
Risks include no reference counting for cached UFS instances, cache keys ignoring path and depending on property-map equality, runtime wrapping of initial connection failures, object-store managed-blocking behavior, and lazy singleton root/journal clients not updating after config changes. Signals are cache reuse by scheme/authority/properties, mount-not-found errors, root/journal lazy initialization, close closing all registered UFSes, and recorder output for cache hits/misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/underfs/AbstractUfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/CORSFilter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/CORSFilter.java

## Purpose
`CORSFilter` adds configured CORS response headers to Alluxio web responses when CORS is enabled.

## Important APIs, Types, and Functions
It extends `HttpFilter` and overrides `doFilter(HttpServletRequest, HttpServletResponse, FilterChain)`. It reads `WEB_CORS_*` configuration keys and uses `StringUtils.equals()` to decide whether to add `Vary: Origin`.

## Control Flow, State, and Persistence
For each request, if `WEB_CORS_ENABLED` is true, it reads allowed origins, methods, headers, exposed headers, credential flag, and max age from global configuration, sets corresponding `Access-Control-*` headers, conditionally sets `Vary`, then always continues the filter chain. It stores no state.

## Dependencies and Integration Points
It depends on Alluxio configuration, `HttpFilter`, and servlet filters. `WebServer` installs it for all dispatcher types on `/*`.

## Risks and Test Signals
Risks include permissive wildcard origins, credentials with wildcard origin if configured, repeated `Vary` headers, and runtime global config reads per request. Signals are headers present only when enabled, `Vary` when origins are not `*`, and filter-chain continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/CORSFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/HttpFilter.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/HttpFilter.java

## Purpose
`HttpFilter` is a servlet filter base class that converts generic servlet requests/responses into HTTP-specific types for subclasses.

## Important APIs, Types, and Functions
It implements `Filter`, provides no-op `init()` and `destroy()`, final generic `doFilter(ServletRequest, ServletResponse, FilterChain)`, and abstract HTTP `doFilter(HttpServletRequest, HttpServletResponse, FilterChain)`.

## Control Flow, State, and Persistence
The final `doFilter()` validates that both request and response are HTTP types, throws `ServletException` otherwise, casts them, and delegates to the subclass. It has no state.

## Dependencies and Integration Points
It depends on the servlet API and is extended by `CORSFilter`.

## Risks and Test Signals
Risks include rejecting non-HTTP dispatches and subclasses being unable to override generic filter behavior. Signals are type validation failures for non-HTTP inputs and successful delegation for HTTP inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/HttpFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JacksonProtobufObjectMapperProvider.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JacksonProtobufObjectMapperProvider.java

## Purpose
`JacksonProtobufObjectMapperProvider` supplies Jersey with a Jackson `ObjectMapper` configured for protobuf JSON conversion.

## Important APIs, Types, and Functions
It implements `ContextResolver<ObjectMapper>`, constructs `mDefaultObjectMapper`, defines `createDefaultMapper()`, and returns the mapper from `getContext(Class<?>)`. The mapper uses lower-camel-case property naming and registers HubSpot's `ProtobufModule`.

## Control Flow, State, and Persistence
Construction creates one mapper instance. Every context lookup returns the same mapper independent of type. There is no persistence.

## Dependencies and Integration Points
It depends on Jackson, Jersey `@Provider`, and `ProtobufModule`. REST endpoints use it when converting protobuf-backed request/response types.

## Risks and Test Signals
Risks include global mapper mutation by consumers, protobuf module compatibility, and lower-camel-case assumptions. Signals are REST JSON/protobuf serialization and deserialization tests for representative proto messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JacksonProtobufObjectMapperProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JmxServlet.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JmxServlet.java

## Purpose
`JmxServlet` exposes read-only JMX data as JSON over HTTP, with optional query parameters for whole-bean or single-attribute lookup.

## Important APIs, Types, and Functions
Important methods are `init()`, `doTrace()`, `doGet()`, `listBeans()`, `writeAttribute(ObjectName, MBeanAttributeInfo)`, `writeAttribute(String, Object)`, and `writeObject()`. It uses platform `MBeanServer`, Jackson `JsonFactory`/`JsonGenerator`, JMX metadata and open-mbean types, and servlet response status codes.

## Control Flow, State, and Persistence
`init()` stores the platform MBean server and JSON factory. `doTrace()` returns method-not-allowed. `doGet()` sets JSON content type and permissive access-control headers, then handles `get=objectName:::attribute` for one attribute or `qry=pattern` for a bean query, defaulting to `*:*`. `listBeans()` queries names, gets bean info, handles modelerType specially, optionally fetches a single attribute, or iterates readable attributes while filtering invalid field names. `writeObject()` recursively emits arrays, numbers, booleans, composite data, tabular data, strings, and nulls.

## Dependencies and Integration Points
It is mounted by `WebServer` at `/metrics/jmx`. It integrates with JVM/platform MBeans and any Alluxio metrics exposed through JMX.

## Risks and Test Signals
Risks include broad unauthenticated JMX exposure at this layer, wildcard queries that can be expensive, recursive data serialization complexity, partial output when a single attribute is missing, and many caught reflection/runtime errors being logged and skipped. Signals are `/metrics/jmx?qry=...` JSON output, `/metrics/jmx?get=...` success and 404 behavior, TRACE rejection, malformed object name returning 400, and serialization of composite/tabular data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JmxServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/StacksServlet.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/StacksServlet.java

## Purpose
`StacksServlet` returns a plain-text thread dump for the current Alluxio process and optionally logs it.

## Important APIs, Types, and Functions
It overrides `doGet(HttpServletRequest, HttpServletResponse)`, uses `ThreadUtils.printThreadInfo()`, `ThreadUtils.logThreadInfo()`, and configuration key `WEB_THREAD_DUMP_TO_LOG`.

## Control Flow, State, and Persistence
For GET requests, it sets `text/plain; charset=UTF-8`, writes thread info to the response output stream with UTF-8 encoding, and logs thread info if configured. It has no persistent state.

## Dependencies and Integration Points
It depends on servlet APIs, Alluxio configuration, and thread utilities. `WebServer` mounts it at the REST common thread-dump path.

## Risks and Test Signals
Risks include exposing stack traces, response cost under high thread counts, and optional log volume. Signals are UTF-8 plain-text output and conditional log emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/StacksServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebInterfaceAbstractMetricsServlet.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebInterfaceAbstractMetricsServlet.java

## Purpose
`WebInterfaceAbstractMetricsServlet` is a base servlet for UI pages that need to expose metric values as request attributes.

## Important APIs, Types, and Functions
It constructs an `ObjectMapper` with Dropwizard `MetricsModule` and provides `populateCounterValues(Map<String, Metric>, Map<String, Counter>, HttpServletRequest)`.

## Control Flow, State, and Persistence
`populateCounterValues()` iterates operation metrics, setting request attributes for gauges and counters, then sets request attributes for RPC invocation counters. It stores no persistent state beyond its mapper.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Jackson, and servlet requests. Concrete web UI servlets use it to prepare metrics for JSP or template rendering.

## Risks and Test Signals
Risks include gauge value computation during request handling, ignoring non-gauge/non-counter metrics, and attribute name collisions. Signals are request attributes populated with current gauge values and counter counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebInterfaceAbstractMetricsServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebServer.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebServer.java

## Purpose
`WebServer` bootstraps a Jetty web server for Alluxio services, including REST/webapp handlers, thread dump, JMX, CORS, JSON metrics, and Prometheus metrics.

## Important APIs, Types, and Functions
Important methods are the constructor, `getServerConnector()`, `addHandler()`, `setHandler()`, `disableMethod()`, `getServer()`, `getBindHost()`, `getLocalPort()`, `stop()`, and `start()`. It uses Jetty `Server`, `ServerConnector`, `QueuedThreadPool`, `ServletContextHandler`, `ConstraintSecurityHandler`, `HandlerList`, `MetricsServlet`, `PrometheusMetricsServlet`, `StacksServlet`, `JmxServlet`, and `CORSFilter`.

## Control Flow, State, and Persistence
The constructor validates service name/address, sizes a Jetty thread pool from `WEB_THREADS`, creates and opens a server connector early so ephemeral ports are resolved, configures a security servlet context with no sessions, disables TRACE and OPTIONS through constraint mappings, mounts thread dump and JMX servlets, installs CORS for all dispatcher types, and sets a handler list containing JSON metrics, Prometheus metrics, the service servlet context, and a default handler. `start()` starts Jetty and wraps failures; `stop()` stops connectors then the server.

## Dependencies and Integration Points
It depends on Alluxio configuration, metrics registry, REST prefix constants, Jetty, and service subclasses that add concrete handlers/servlets. It is a base class for master and worker web servers.

## Risks and Test Signals
Risks include opening the connector in the constructor, constraint mapping path scope, duplicate Prometheus collector registration through member initialization, CORS exposure, and incomplete shutdown if connector stop fails. Signals are bind host/port resolution, disabled TRACE/OPTIONS behavior, servlet availability at metrics/JMX/thread-dump paths, handler ordering when `addHandler()` is used, and stop releasing the port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/AbstractWorker.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/AbstractWorker.java

## Purpose
`AbstractWorker` is the base class for Alluxio workers, centralizing executor-service lifecycle management.

## Important APIs, Types, and Functions
It stores an `ExecutorServiceFactory` and an `ExecutorService`, exposes protected `getExecutorService()`, and implements `start(WorkerNetAddress)`, `stop()`, and `close()`.

## Control Flow, State, and Persistence
`start()` asserts the executor has not already been created and obtains one from the factory. `stop()` calls `shutdownNow()`, waits up to ten seconds, logs timeout or interruption, restores interrupt status, and clears the executor in a `finally` block. `close()` delegates to `stop()`. It has no persistence.

## Dependencies and Integration Points
It depends on the `Worker` interface, `ExecutorServiceFactory`, `WorkerNetAddress`, Guava `Preconditions`, and Java executor APIs. Concrete workers subclass it and use the executor for internal tasks.

## Risks and Test Signals
Risks include not being thread-safe, abrupt `shutdownNow()` interrupting tasks, and `getExecutorService()` returning null before start or after stop. Signals are start/stop idempotency expectations, executor factory invocation, timeout logging, and close delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/AbstractWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/BlockUtils.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/BlockUtils.java

## Purpose
`BlockUtils` contains worker-side block helper methods. In this file it computes the UFS fallback path for a block.

## Important APIs, Types, and Functions
It defines `getUfsBlockPath(UfsManager.UfsClient, long)` and a private magic number `0x1D91AC0E01AB0165L`.

## Control Flow, State, and Persistence
The method concatenates the UFS mount point URI, a deterministic temporary directory name generated from the magic number and suffix `.alluxio_ufs_blocks`, and the block id. It does not touch storage directly.

## Dependencies and Integration Points
It depends on `UfsManager.UfsClient` and `PathUtils`. Worker block storage fallback code uses this path convention when writing blocks to UFS.

## Risks and Test Signals
Risks include path convention compatibility, mount URI formatting, and collisions if the magic/suffix changes. Signals are deterministic paths for known mount/block ids and compatibility with UFS cleanup/listing code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/BlockUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerFactory.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerFactory.java

## Purpose
`WorkerFactory` is the extension point for conditionally creating worker components.

## Important APIs, Types, and Functions
It defines `isEnabled()` and `create(WorkerRegistry, UfsManager)`.

## Control Flow, State, and Persistence
Implementations decide whether a worker should be created and build it using the shared registry and UFS manager. The interface itself has no state.

## Dependencies and Integration Points
It depends on `Worker`, `WorkerRegistry`, and `UfsManager`. Worker process bootstrapping uses factories to assemble enabled worker services.

## Risks and Test Signals
Risks include factories reporting enabled but failing during creation, registry dependency assumptions, and UFS manager sharing. Signals are enabled/disabled factory selection and created worker registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerRegistry.java -->
# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerRegistry.java

## Purpose
`WorkerRegistry` is the worker-specific typed registry for `Worker` instances started with a `WorkerNetAddress`.

## Important APIs, Types, and Functions
It extends `Registry<Worker, WorkerNetAddress>` and defines only a public constructor.

## Control Flow, State, and Persistence
All ordering, dependency, start, stop, and lookup behavior comes from the generic `Registry` base class. This subclass contributes type binding only.

## Dependencies and Integration Points
It depends on `Registry`, `Worker`, and `WorkerNetAddress`. Worker factories and worker process bootstrap code use it to manage worker services.

## Risks and Test Signals
Risks mirror the base registry: dependency cycles, missing services, and startup/shutdown order. Signals can follow `RegistryTest` patterns with worker types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/DefaultStorageTierAssocTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/DefaultStorageTierAssocTest.java

## Purpose
`DefaultStorageTierAssocTest` verifies storage-tier alias ordering, ordinal lookup, intersection-list construction, and ordinal interpretation for special and out-of-range tier indexes.

## Important APIs, Types, and Functions
The tests are `storageAliasListConstructor()` and `interpretTier()`. They exercise `DefaultStorageTierAssoc`, `StorageTierAssoc`, `Constants.MEDIUM_*`, `Constants.FIRST_TIER`, `Constants.SECOND_TIER`, `Constants.LAST_TIER`, `BlockStoreLocation.anyDirInTier()`, and `DefaultStorageTierAssoc.interpretOrdinal()`.

## Control Flow, State, and Persistence
The constructor test builds ordered aliases including a custom alias, checks size, alias-to-ordinal and ordinal-to-alias mappings, ordered alias list preservation, and adjacent tier intersections. The ordinal test covers single-tier and ten-tier cases, positive overflow, negative indexes, and named constants. There is no persistence.

## Dependencies and Integration Points
It depends on JUnit, Alluxio storage tier classes, and worker block-store locations. It protects tier ordering used by master and worker storage placement logic.

## Risks and Test Signals
Risks covered are off-by-one tier interpretation, custom alias handling, and incorrect adjacent-tier intersection generation. Passing tests signal stable tier semantics for configured storage levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/DefaultStorageTierAssocTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RestUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RestUtilsTest.java

## Purpose
`RestUtilsTest` verifies the common REST wrapper's success and error response behavior.

## Important APIs, Types, and Functions
The tests are `voidOkResponse()`, `stringOkResponse()`, `objectOkResponse()`, and `errorResponse()`. They exercise `RestUtils.call()`, `RestUtils.RestCallable`, `RestUtils.ErrorResponse`, global configuration, Jackson string serialization, `AlluxioStatusException`, and gRPC `Status`.

## Control Flow, State, and Persistence
Each test invokes `RestUtils.call()` with a callable. Null results should produce HTTP 200 with null entity, strings should be JSON-encoded strings, objects should be passed through as entities, and `AlluxioStatusException` should produce HTTP 500 with a status code and message in `ErrorResponse`. There is no persistence.

## Dependencies and Integration Points
It depends on JUnit, Jersey `Response`, Jackson, and Alluxio exception/configuration utilities. It protects REST endpoint wrappers used by web services.

## Risks and Test Signals
Risks covered include incorrect JSON handling for strings, object wrapping regressions, and loss of status/message data on exceptions. Passing tests signal stable REST response contracts for simple success and Alluxio-status failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RestUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RpcSensitiveConfigMaskTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RpcSensitiveConfigMaskTest.java

## Purpose
`RpcSensitiveConfigMaskTest` verifies that RPC debug/log masking hides sensitive UFS configuration values inside several protobuf request/response shapes.

## Important APIs, Types, and Functions
The test `maskObjectsAll()` exercises `RpcSensitiveConfigMask.CREDENTIAL_FIELD_MASKER.maskObjects()`, `MountPOptions`, `MountPRequest`, `UfsInfo`, `GetUfsInfoPResponse`, `UpdateMountPRequest`, and sensitive key `PropertyKey.Name.S3A_ACCESS_KEY`.

## Control Flow, State, and Persistence
The test constructs different protobuf objects containing a normal key/value and an S3 access key with value `mycredential`, stringifies the masked output, and asserts that normal data and key names remain visible while the credential value is absent and `Masked` appears. It also verifies a plain string is left unmasked. There is no persistence.

## Dependencies and Integration Points
It depends on generated gRPC/protobuf classes and the sensitive-config masker used for RPC logging or diagnostics.

## Risks and Test Signals
Risks covered include credential leakage from nested properties builders and accidental masking of non-protobuf objects. Passing tests signal coverage for common mount and UFS info RPC types, though new protobuf shapes need explicit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RpcSensitiveConfigMaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/cli/FormatTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/cli/FormatTest.java

## Purpose
`FormatTest` verifies worker-format behavior for tiered storage directories, including directory cleanup, permissions, and replacement of files that conflict with worker data directory names.

## Important APIs, Types, and Functions
The tests are `formatWorker()` and `formatWorkerDeleteFileSameName()`. They exercise `Format.format(Format.Mode.WORKER, Configuration.global())`, `ConfigurationRule`, worker tier directory keys, `WORKER_DATA_FOLDER_PERMISSIONS`, `CommonUtils.getWorkerDataDirectory()`, `FileUtils`, `PathUtils`, and POSIX permissions APIs.

## Control Flow, State, and Persistence
Each test creates temporary tier directories and configures three storage levels. `formatWorker()` pre-creates subdirectories/files under worker data folders, runs format, and asserts the parent tiers and worker data folders exist, permissions match, and data folders are empty. `formatWorkerDeleteFileSameName()` pre-creates files where worker data directories should be, runs format, and verifies they become empty directories with configured permissions.

## Dependencies and Integration Points
It depends on JUnit `TemporaryFolder`, Alluxio configuration test utilities, local filesystem permissions, and worker formatting code.

## Risks and Test Signals
Risks covered include stale worker data surviving format, wrong permissions, and file-vs-directory conflicts. Signals are local filesystem cleanup correctness; portability depends on POSIX permission support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/cli/FormatTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/AbstractPrimarySelectorTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/AbstractPrimarySelectorTest.java

## Purpose
`AbstractPrimarySelectorTest` verifies primary-selector state reads, blocking waits for state transitions, and listener registration/unregistration.

## Important APIs, Types, and Functions
Tests are `getState()`, `waitFor()`, and `onStateChange()`. The nested `TestSelector` extends `AbstractPrimarySelector` with no-op `start()` and `stop()`. It uses `NodeState`, `Scoped`, scheduled executors, and atomic counters.

## Control Flow, State, and Persistence
`getState()` directly toggles state and verifies safe and unsafe reads. `waitFor()` schedules delayed transitions to primary and standby and blocks until each state is observed. `onStateChange()` registers a listener, performs ten primary/standby cycles, verifies counters, closes the listener, and verifies no further increments. There is no persistence.

## Dependencies and Integration Points
It depends on the abstract master primary selector and JUnit. The behavior is important for master leader-election consumers waiting for primary or standby state.

## Risks and Test Signals
Risks covered include missed notifications, unsafe/safe state mismatch, and listener leaks after close. Passing tests signal basic state coordination but do not exercise concrete selector backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/AbstractPrimarySelectorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/ExecutorServiceBuilderTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/ExecutorServiceBuilderTest.java

## Purpose
`ExecutorServiceBuilderTest` verifies master RPC executor configuration validation and construction for supported executor variants.

## Important APIs, Types, and Functions
Tests cover zero/negative FJP parallelism, zero/negative keepalive, TPE creation, TPE core thread timeout, and every `ThreadPoolExecutorQueueType`. They exercise `ExecutorServiceBuilder.buildExecutorService()`, `RpcExecutorType`, `ThreadPoolExecutorQueueType`, and master RPC executor property keys.

## Control Flow, State, and Persistence
Each test reloads configuration first. Invalid tests set bad values and expect `IllegalArgumentException` with specific messages. Valid tests set executor type/options and call the builder. The tests do not persist data; they mutate global configuration during the test.

## Dependencies and Integration Points
It depends on Alluxio configuration and executor builder code used by master gRPC services.

## Risks and Test Signals
Risks covered include accepting unusable thread-pool parameters and queue type regressions. Signals are exact error messages and successful executor construction for valid TPE configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/ExecutorServiceBuilderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/RegistryTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/RegistryTest.java

## Purpose
`RegistryTest` verifies generic server registry dependency ordering, cycle detection, and timeout behavior when a requested server is unavailable.

## Important APIs, Types, and Functions
It defines `TestServer`, `ServerA`, `ServerB`, `ServerC`, and `ServerD`, and tests `registry()`, `cycle()`, and `unavailable()`. It exercises `Registry.add()`, `Registry.getServers()`, and `Registry.get(Class, timeout)`.

## Control Flow, State, and Persistence
`registry()` builds every permutation of A/B/C registration order and asserts the dependency-sorted order is C, B, A. `cycle()` registers servers with a dependency cycle and expects runtime failure. `unavailable()` waits briefly for a missing server and checks the timeout message includes the server class. There is no persistence.

## Dependencies and Integration Points
It depends on the common `Registry`, `Server`, gRPC service types, and JUnit. The same registry pattern underlies master and worker service startup.

## Risks and Test Signals
Risks covered include startup order depending on registration order, undetected dependency cycles, and poor diagnostics for missing services. Passing tests signal deterministic dependency resolution and timeout reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/RegistryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/StateLockManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/StateLockManagerTest.java

## Purpose
`StateLockManagerTest` verifies master state-lock behavior for timeout grace mode, forced interruption grace mode, exclusive-only startup phase, and reporting of shared waiters/holders.

## Important APIs, Types, and Functions
Tests are `testGraceMode_Timeout()`, `testGraceMode_Forced()`, `testExclusiveOnlyMode()`, and `testGetStateLockSharedWaitersAndHolders()`. The nested `StateLockingThread` acquires shared or exclusive locks and exposes acquisition/interruption state. The tests use `StateLockManager`, `StateLockOptions`, `GraceMode`, `LockResource`, and backup state-lock configuration keys.

## Control Flow, State, and Persistence
Timeout mode starts shared/exclusive holders and expects exclusive acquisition with a short grace period to time out, then verifies success when no holder remains. Forced mode enables interrupt cycles, starts a shared holder, takes the lock exclusively with forced grace, and expects holders/waiters to be interrupted. Exclusive-only mode simulates masters-started callback, verifies shared locks fail during the exclusive-only duration, and exclusive locks still succeed. Waiter/holder reporting starts multiple shared holders and asserts their thread names appear.

## Dependencies and Integration Points
It depends on master state locking used for backups/checkpointing and global configuration. The tests exercise concurrency behavior with real threads.

## Risks and Test Signals
Risks covered include backup exclusive lock starvation, failure to interrupt shared lockers, accidental shared access during exclusive-only startup, and inaccurate lock diagnostics. Signals are deterministic timeouts, interruption flags, and reported shared holder names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/StateLockManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/AsyncJournalWriterTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/AsyncJournalWriterTest.java

## Purpose
`AsyncJournalWriterTest` verifies the newer `alluxio.master.journal.AsyncJournalWriter` write/flush behavior with and without batching, including recovery from write and flush failures.

## Important APIs, Types, and Functions
It uses `setupAsyncJournalWriter(boolean)`, `writesAndFlushesInternal()`, `failedWriteInternal()`, and `failedFlushInternal()`, with public tests for batching enabled and disabled. It mocks `JournalWriter`, configures `MASTER_JOURNAL_FLUSH_BATCH_TIME_MS`, and uses default protobuf `JournalEntry`.

## Control Flow, State, and Persistence
The setup configures batching, mocks successful write/flush behavior, and creates an async writer with empty sink set. Normal tests append five entries, assert returned counters start at one, flush each counter, and verify the underlying writer flushed. Failure tests stop the async writer before changing Mockito behavior, make writes or flushes throw, start the writer, assert flush attempts fail, then stop, restore success behavior, restart, and verify later flushes succeed.

## Dependencies and Integration Points
It depends on Mockito, JUnit, Alluxio configuration, the current journal async writer, and the journal writer abstraction. It is a direct test signal for production async journal durability behavior.

## Risks and Test Signals
Risks covered include failure poisoning, batching regressions, and concurrent internal writer thread interactions while mocking. Passing tests signal retryability after transient write/flush failures and preservation of append counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/AsyncJournalWriterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalEntryAssociationTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalEntryAssociationTest.java

## Purpose
`JournalEntryAssociationTest` verifies that every supported journal entry type maps to a master and that the test's entry list stays in sync with the protobuf schema.

## Important APIs, Types, and Functions
It defines a static `ENTRIES` list containing one `JournalEntry` for each supported field, and tests `testUnknown()`, `testEntries()`, and `testFullCoverage()`. It exercises `JournalEntryAssociation.getMasterForEntry()` and many generated journal entry protobuf types across file, block, meta, table, and job domains.

## Control Flow, State, and Persistence
`testUnknown()` expects an empty default entry to throw `IllegalStateException`. `testEntries()` asserts every listed entry maps to a non-null master. `testFullCoverage()` compares the number of entries to the journal protobuf field count after subtracting non-operation fields (`sequence_number`, `operationId`, and `journal_entries`). There is no persistence.

## Dependencies and Integration Points
It depends on generated journal protobuf descriptors and the association table used by journal routing/replay.

## Risks and Test Signals
Risks covered include adding a new journal entry type without routing it to a master, default/unknown entries being accepted, and schema drift. Passing tests signal full operation-field coverage for the current journal proto.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalEntryAssociationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalUtilsTest.java

## Purpose
`JournalUtilsTest` verifies checkpoint writing and restoration for journal-entry checkpoints, compound checkpoints, mixed `Journaled`/`Checkpointed` components, and invalid checkpoint type handling.

## Important APIs, Types, and Functions
Tests include `checkpointAndRestore()`, `restoreInvalidJournalEntryCheckpoint()`, `checkpointAndRestoreComponents()`, entry-count variants, and compound-count variants. Helper types `TestJournaled`, `TestMultiEntryJournaled`, and `TestCheckpointed` implement `Journaled` and `Checkpointed`. The test exercises `JournalUtils.writeJournalEntryCheckpoint()`, `restoreJournalEntryCheckpoint()`, `writeToCheckpoint()`, `restoreFromCheckpoint()`, `CheckpointInputStream`, `CheckpointOutputStream`, `CheckpointType`, `CheckpointName`, and `CloseableIterator`.

## Control Flow, State, and Persistence
Simple checkpoint tests write to memory or temporary files, reset component state, and restore from checkpoint streams. Invalid tests create a checkpoint with an unexpected type and expect an `IllegalStateException`. Compound tests build alternating journaled and checkpointed components, write them to a compound checkpoint, clear state, restore, and compare to the original. Temporary files are used as test persistence.

## Dependencies and Integration Points
It depends on Alluxio journal checkpoint utilities, protobuf journal entries, JUnit temporary folders, and checkpoint stream classes. It is a strong test signal for master checkpoint compatibility.

## Risks and Test Signals
Risks covered include checkpoint type mismatch, ordering of compound components, journal-entry iterator replay, and mixed checkpoint implementations. Passing tests signal byte-level checkpoint round trips for empty, single-entry, and multi-entry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/JournalUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/checkpoint/CheckpointStreamTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/checkpoint/CheckpointStreamTest.java

## Purpose
`CheckpointStreamTest` verifies regular and optimized checkpoint stream round trips for every `CheckpointType`.

## Important APIs, Types, and Functions
It is parameterized over `CheckpointType.values()` and tests `regularStreamTest()` and `optimizedStreamTest()`. It uses `CheckpointOutputStream`, `CheckpointInputStream`, `OptimizedCheckpointOutputStream`, `OptimizedCheckpointInputStream`, Ratis `MD5Hash`, `MD5FileUtil`, `RandomString`, and temporary files.

## Control Flow, State, and Persistence
For each checkpoint type, the regular test writes random bytes through a checkpoint output stream, reads the type and bytes through a checkpoint input stream, and asserts equality. The optimized test writes through an MD5-calculating optimized output stream, saves the MD5 file, reads through an optimized input stream with a second digest, verifies the saved MD5, and asserts byte equality.

## Dependencies and Integration Points
It depends on checkpoint stream implementations and Ratis MD5 utilities. It protects checkpoint file format headers and optimized stream integrity checks used by journal checkpoint persistence.

## Risks and Test Signals
Risks covered include checkpoint type header corruption, optimized stream digest mismatch, and read/write byte loss across checkpoint types. Passing tests signal stream compatibility and MD5 verification for optimized checkpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/checkpoint/CheckpointStreamTest.java -->
