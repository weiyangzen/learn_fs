# subset-b-000470 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java

### Purpose
`BufferedJournalApplier` serializes application of Raft journal entries into Alluxio master state machines while supporting nonblocking suspension for backup or state-inspection workflows. During suspension, committed entries are held in an in-memory FIFO queue and later applied during resume or bounded catch-up.

### Important APIs, Types, And Functions
The public surface is `processJournalEntry()`, `suspend()`, `resume()`, `catchup(long)`, `isSuspended()`, and `close()`. `applyToMaster()` maps a `JournalEntry` to a master via `JournalEntryAssociation`, calls the target `Journaled.processJournalEntry()`, then appends to configured `JournalSink`s. The inner `RaftJournalCatchupThread` extends `AbstractCatchupThread` and drains the suspend buffer until a target sequence is reached.

### Control Flow
Normal `processJournalEntry()` holds `mStateLock` and either applies immediately or enqueues and notifies waiters. `suspend()` flips `mSuspended`; `resume()` cancels any catch-up thread, drains buffered entries, and eventually takes the state lock once the backlog is small or resume has run too long. `catchup()` requires suspension, starts one background thread, and leaves the applier suspended after reaching the requested sequence.

### State, Persistence, And Dependencies
State is in-memory only: `mLastAppliedSequence`, `mSuspended`, `mResumeInProgress`, `mSuspendBuffer`, and the optional catch-up thread. There is no on-disk spill despite a TODO. Dependencies include `RaftJournal`, `Journaled`, `JournalEntryAssociation`, `JournalUtils`, `JournalSink`, `LockResource`, and `AbstractCatchupThread`.

### Integration Points
`JournalStateMachine` owns this class to decouple Ratis commit application from Alluxio master state access. It is used by Raft suspend/resume/catchup operations and by snapshot pause logic, which resumes the applier before reloading state.

### Risks
The suspend buffer can grow without bound during long suspensions. `resume()` unconditionally unlocks `mStateLock` in `finally`, so its correctness relies on always having acquired the lock by construction before the block exits. Catch-up drains under `mSuspendBuffer` synchronization while `processJournalEntry()` enqueues under both locks, making lock-order changes risky. Replay failures are fatal or delegated to `JournalUtils`.

### Test Signals
Cover immediate apply, suspend-buffer ordering, resume with small and large backlogs, catch-up to an exact sequence, cancellation by resume, duplicate resume/catchup preconditions, sink append side effects, unknown journal entry routing, and stress cases where entries arrive while resume is draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java

### Purpose
`JournalStateMachine` is the Ratis state machine for the embedded journal. It applies replicated `JournalEntry` commands to the proper Alluxio master, manages sequence-number de-duplication, snapshots and restores master state, and coordinates primary-mode pre-apply behavior.

### Important APIs, Types, And Functions
It extends `BaseStateMachine`. Key methods are `initialize()`, `reinitialize()`, `applyTransaction()`, `applyJournalEntryCommand()`, `takeSnapshot()`, `takeLocalSnapshot()`, `install()`, `pause()`, `unpause()`, `suspend()`, `resume()`, `catchup()`, `upgrade()`, and leader/snapshot notifications. It owns `BufferedJournalApplier`, `RaftSnapshotManager`, and `SnapshotDirStateMachineStorage`.

### Control Flow
Initialization loads the latest snapshot. Each Ratis transaction parses log data into a `JournalEntry`, recursively expands batch entries, records negative sequence numbers as primary-start markers, ignores empty snapshot entries, skips duplicate sequence numbers, and fatals on gaps. Before primacy, entries are applied to masters; after `upgrade()`, `mIgnoreApplys` suppresses primary double-application because requests already modified state before journaling.

### State, Persistence, And Dependencies
Persistent state is held in Ratis logs and snapshot directories named by `SimpleStateMachineStorage`. Snapshots include a `SnapshotIdJournaled` entry plus all master `Journaled` checkpoints, and restore updates `mNextSequenceNumberToRead`. Volatile state tracks commit index, snapshot index/time/durations, primary-start sequence, leader status, suspension callbacks, and closed/snapshotting flags. Dependencies include Apache Ratis, Alluxio `Journaled`, `StateLockManager`, checkpoint streams, metrics, and `RaftSnapshotManager`.

### Integration Points
`RaftJournalSystem` constructs this state machine and calls it for catch-up, checkpoint, suspend/resume, leadership state changes, and dynamic quorum additions through read-only queries. Ratis calls snapshot and install hooks; followers may download snapshots from peers rather than using Ratis snapshot installation.

### Risks
Sequence-number gaps call fatal error, so writer and replay ordering are critical. Primary snapshots require a state lock unless a follower or explicitly allowed leader checkpoint. Snapshot restore can interrupt external suspended work via callback. `mIgnoreApplys` is central to pre-apply correctness and must only be set after catch-up and quiet-period validation. Metrics read some fields outside synchronization.

### Test Signals
Exercise batched entries, duplicates, gaps, negative primary-start markers, empty entries, upgrade no-op apply, snapshot creation/restoration in directory and old single-file formats, pause/unpause interrupt behavior, follower snapshot download hooks, manual leader checkpoint locking, and corruption-tolerant restore paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java

### Purpose
`RaftJournal` is the per-master `Journal` facade for embedded journals. It binds one `Journaled` state machine to the shared Raft-backed writer managed by `RaftJournalSystem`.

### Important APIs, Types, And Functions
The constructor stores the `Journaled`, journal URI, and `AtomicReference<AsyncJournalWriter>`. `getStateMachine()` exposes the master state machine for replay and snapshotting. `createJournalContext()` returns `MasterJournalContext` wrapping the current async writer or throws `UnavailableException` when the server is not primary or the writer is closed.

### Control Flow
Creation is passive. Write requests ask for a journal context, dereference the shared writer, and fail fast if it is absent. `close()` is intentionally empty because ownership of the shared writer and Ratis resources lives in `RaftJournalSystem`.

### State, Persistence, And Dependencies
The object keeps only pointers. Persistence is delegated to `AsyncJournalWriter`, `RaftJournalWriter`, and Ratis. It depends on Alluxio `Journal`, `Journaled`, `MasterJournalContext`, and `UnavailableException`.

### Integration Points
`RaftJournalSystem.createJournal()` creates one instance per `Master` and stores it by master name. `JournalStateMachine` later iterates these journals to replay entries and write or restore snapshots.

### Risks
The class is `@NotThreadSafe`, but the writer reference is atomic because writer availability changes during primacy transitions. Callers must treat `UnavailableException` as retryable failover. A stale context may continue to use an async writer until higher-level close/flush behavior stops it.

### Test Signals
Verify context creation with present and absent writer references, location propagation, state-machine exposure, close no-op behavior, and failover windows where the writer reference flips to null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java

### Purpose
`RaftJournalAppender` submits serialized journal messages to the embedded Ratis log, either directly through the local `RaftServer` or through a remote `RaftClient` depending on configuration.

### Important APIs, Types, And Functions
`sendAsync(Message)` chooses local or remote submission. `sendLocalRequest()` builds a write `RaftClientRequest` with the Alluxio Raft group and `RaftJournalSystem.nextCallId()`. `sendRemoteRequest()`, `ensureClient()`, and `handleRemoteException()` manage a lazily created remote client and recycle it after `AlreadyClosedException`. `close()` closes the remote client.

### Control Flow
Local submission bypasses a Ratis client and calls `mServer.submitClientRequestAsync()`. Remote submission calls `mClient.async().send()` and converts connection-closed failures into client reset before rethrowing through `CompletionException`.

### State, Persistence, And Dependencies
The appender owns the optional remote `RaftClient`; persistent storage is Ratis' log. Dependencies include `RaftServer`, `RaftClient`, Ratis protocol IDs, Alluxio configuration `MASTER_EMBEDDED_JOURNAL_WRITE_REMOTE_ENABLED`, and logging helpers.

### Integration Points
`RaftJournalWriter` uses this for normal journal flushes, and `RaftJournalSystem` uses it for catch-up primary-start marker writes and manual checkpoint catch-up.

### Risks
Remote client creation is lazy but not synchronized beyond volatile assignment, so concurrent use could create extra clients if external callers are added. Local request fields must stay aligned with the fixed `RAFT_GROUP_ID`. Remote exception handling assumes `AlreadyClosedException` is the recoverable client-staleness signal.

### Test Signals
Cover local request construction, remote send success, remote `AlreadyClosedException` client reset, close idempotence with and without remote client, and propagation of async failures to `RaftJournalWriter.flush()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java

### Purpose
`RaftJournalProgressLogger` adapts the generic `AbstractJournalProgressLogger` to embedded-journal replay progress.

### Important APIs, Types, And Functions
The constructor accepts a `JournalStateMachine` and optional final commit index. `getLastAppliedIndex()` returns `JournalStateMachine.getLastAppliedCommitIndex()`. `getJournalName()` returns a constant `"RAFT"`.

### Control Flow
There is no complex flow; callers periodically invoke inherited logging, which asks this class for the current applied index and label.

### State, Persistence, And Dependencies
It stores only a state-machine reference. It has no persistence. It depends on `AbstractJournalProgressLogger`, `OptionalLong`, and `JournalStateMachine`.

### Integration Points
`RaftJournalSystem.catchUp()` uses it when a `LeaderNotReadyException` suggests Ratis is still replaying, giving progress estimates while gaining primacy.

### Risks
The optional end index may be absent if Ratis group info could not be read, reducing progress logs to current index only. Accuracy depends on `mLastAppliedCommitIndex` being updated after every transaction.

### Test Signals
Validate last-applied forwarding, journal name, behavior with present and absent end commit indexes, and integration with catch-up retry logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java

### Purpose
`RaftJournalServiceClient` is a master client for the auxiliary Raft journal gRPC service used to discover and download snapshots from peer masters.

### Important APIs, Types, And Functions
It extends `AbstractMasterClient`, identifies `RAFT_JOURNAL_SERVICE`, and builds a blocking `RaftJournalServiceGrpc` stub after connection. `requestLatestSnapshotInfo()` sends `LatestSnapshotInfoPRequest` with a configured deadline. `requestLatestSnapshotData(SnapshotMetadata)` returns a streaming iterator of `SnapshotData`.

### Control Flow
The client is constructed with an explicit `MasterSelectionPolicy`, so `beforeConnect()` intentionally avoids primary discovery. Calls require `connect()` to have populated `mBlockingClient`.

### State, Persistence, And Dependencies
State is the gRPC channel/stub inherited from `AbstractMasterClient`. No data is persisted locally. Dependencies include Alluxio client context, retry policy suppliers, generated gRPC service types, and `MASTER_JOURNAL_REQUEST_INFO_TIMEOUT`.

### Integration Points
`RaftSnapshotManager` creates one client per other master RPC address, requests metadata in parallel, then streams the best snapshot candidate into a local temporary directory.

### Risks
Snapshot data streaming has no explicit deadline in this wrapper, so long-running transfers rely on gRPC/channel behavior and caller handling. `requestLatestSnapshotInfo()` only works after successful connection, and failed metadata calls force the manager to disconnect.

### Test Signals
Test service type/name/version, no-primary-selection behavior, deadline application on info requests, data iterator forwarding, reconnect after failed metadata requests, and use with specified-master selection policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java

### Purpose
`RaftJournalServiceHandler` serves latest snapshot metadata and snapshot directory bytes over gRPC so lagging embedded-journal followers can bootstrap from other masters.

### Important APIs, Types, And Functions
It implements `requestLatestSnapshotInfo()` and `requestLatestSnapshotData()`. `SnapshotGrpcOutputStream` chunks marshalled directory bytes into `SnapshotData` messages using `MASTER_EMBEDDED_JOURNAL_SNAPSHOT_REPLICATION_CHUNK_SIZE` and `UnsafeByteOperations` to avoid copies.

### Control Flow
Metadata requests return `exists=false` when storage has no snapshot, otherwise term/index. Data requests convert term/index to the Ratis snapshot directory name, marshal that directory into the gRPC stream, complete the observer, and update upload metrics. Cancellation is checked before doing work; exceptions are returned as internal gRPC errors.

### State, Persistence, And Dependencies
The handler is read-only over `StateMachineStorage` snapshot directories. It tracks last upload duration, compressed stream size, and disk size metrics. Dependencies include generated gRPC classes, Ratis `SnapshotInfo`, `SimpleStateMachineStorage`, `DirectoryMarshaller`, metrics, and protobuf `ByteString`.

### Integration Points
Registered by `RaftJournalSystem.getJournalServices()` as `RAFT_JOURNAL_SERVICE`. `RaftSnapshotManager` is the client-side consumer.

### Risks
The data path trusts requested term/index and reads the corresponding directory; missing or changing directories surface as upload failures. Chunk buffering allocates a new byte array per flush. Cancellation is only checked at request start, not during long marshalling.

### Test Signals
Cover no-snapshot metadata, valid metadata, cancelled requests, successful directory stream round trip, chunk boundary sizes, observer errors on marshalling failure, and metric updates for duration and byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java

### Purpose
`RaftJournalSystem` multiplexes Alluxio master journals into one embedded Apache Ratis group. It owns server startup, primacy transitions, catch-up, snapshots, dynamic quorum operations, leadership transfer, formatting, and journal services.

### Important APIs, Types, And Functions
It extends `AbstractJournalSystem`. Key methods include `initServer()`, `startInternal()`, `stopInternal()`, `createJournal()`, `gainPrimacy()`, `losePrimacy()`, `catchUp()`, `checkpoint()`, `sendMessageAsync()`, `getQuorumServerInfoList()`, `addQuorumServer()`, `removeQuorumServer()`, `transferLeadership()`, `format()`, and metric helpers. It owns `RaftServer`, `JournalStateMachine`, `SnapshotDirStateMachineStorage`, `RaftPrimarySelector`, and shared writer references.

### Control Flow
Startup builds peer IDs from configured embedded-journal addresses, creates a fixed Raft group, configures Ratis storage/log/snapshot/timeouts/transport limits, starts the server, and asynchronously joins the quorum. Gaining primacy writes a random negative sequence marker, waits for it to apply and for an election quiet period, upgrades the state machine to ignore primary replays, then publishes an `AsyncJournalWriter`. Losing primacy closes writers, closes and recreates the Ratis server, and returns to standby replay.

### State, Persistence, And Dependencies
Persistent data lives under the journal path's `raft` directory, migrated from an older group-root layout if present. State includes the Raft group, peer ID, transfer gate, journals map, shared writer references, quorum transfer messages, and metrics. Dependencies are Apache Ratis, Alluxio configuration, metrics, networking utilities, gRPC service registration, and filesystem utilities.

### Integration Points
Masters call `createJournal()` for per-master journals and use the returned `PrimarySelector`. Admin paths call quorum info, add/remove server, transfer leadership, and checkpoint. `JournalStateMachine` calls back on leadership and configuration changes.

### Risks
Pre-apply correctness depends on catch-up marker ordering and the quiet-period heuristic. Ratis configuration values must align with journal entry and flush batch sizes. Leadership transfer is asynchronous and temporarily disables repeated transfer attempts. Formatting deletes the journal path. Dynamic quorum changes assume the current server/group view is fresh.

### Test Signals
Exercise single-node timeout override, old journal migration, start/stop, primacy gain/loss, catch-up retry on `LeaderNotReadyException`, writer publication/removal, manual checkpoint, dynamic quorum add/remove, transfer success/failure messages, formatting access checks, metrics registration, and group update after configuration change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java

### Purpose
`RaftJournalUtils` centralizes small helper operations for embedded-journal peer IDs, storage paths, temporary snapshot files, and exceptional futures.

### Important APIs, Types, And Functions
`RAFT_DIR` is the storage subdirectory. `getPeerId(InetSocketAddress)` and `getPeerId(String,int)` encode peers as `host_port`. `getRaftJournalDir(File)` returns `<base>/raft`. `createTempSnapshotFile(SimpleStateMachineStorage)` creates a timestamped temp `.dat` file under a sibling `tmp` directory. `completeExceptionally(Exception)` creates a failed `CompletableFuture`.

### Control Flow
Methods are direct helpers. Temporary snapshot creation ensures the temp directory exists before calling `File.createTempFile()`.

### State, Persistence, And Dependencies
No mutable state is stored. The path helpers define persistent directory conventions consumed by `RaftJournalSystem` and Ratis. Dependencies include Ratis `RaftPeerId`, `SimpleStateMachineStorage`, Java `File`, and futures.

### Integration Points
`RaftJournalSystem` uses peer ID and raft directory helpers for group/server setup and quorum operations. `JournalStateMachine.applyTransaction()` uses `completeExceptionally()` through failed apply futures.

### Risks
Peer IDs replace host/port separator with `_`, so reverse parsing elsewhere assumes that convention. `createTempSnapshotFile()` is tied to the old single-file snapshot utility path and must not conflict with directory-snapshot tmp handling.

### Test Signals
Check peer ID formatting for hostnames/IPs, raft directory construction, temp directory creation failure, unique temp file creation, and failed future propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java

### Purpose
`RaftJournalWriter` assigns global sequence numbers to primary-side journal entries, batches them into an aggregate `JournalEntry`, and flushes the batch to Ratis.

### Important APIs, Types, And Functions
It implements `JournalWriter` with `write()`, `flush()`, `close()`, and `getNextSequenceNumberToWrite()`. It tracks `mNextSequenceNumberToWrite`, last submitted/committed sequence numbers, an aggregate `JournalEntry.Builder`, current serialized size, and the owned `RaftJournalAppender`.

### Control Flow
`write()` rejects closed writers and multi-field entries, flushes if the current batch exceeds one third of the Ratis max entry size, sets the next sequence number on the entry, and appends it to the batch. `flush()` sends the whole batch as one Ratis `Message`, waits for the configured timeout, checks the Ratis reply exception, records committed sequence, and clears the batch.

### State, Persistence, And Dependencies
Sequence assignment is in-memory; persistence is Ratis log replication via `RaftJournalAppender`. Dependencies include Alluxio `JournalWriter`, protobuf `JournalEntry`, Ratis `Message`/reply, configuration limits, and `UnsafeByteOperations`.

### Integration Points
`RaftJournalSystem.gainPrimacy()` creates this writer after catch-up and wraps it with `AsyncJournalWriter` for all `RaftJournal` contexts. `JournalStateMachine` de-duplicates retried flushes by sequence number.

### Risks
Flush retry can submit duplicate batches, requiring replay de-duplication to stay correct. A single oversized entry is only logged as an error before still entering the batch. Timeout and Ratis exceptions are surfaced as `IOException`, potentially leaving the same batch for retry. The class is not thread-safe and relies on async-writer serialization.

### Test Signals
Test sequence assignment, batch aggregation, automatic flush threshold, empty flush, timeout/exception propagation, duplicate flush retry behavior, close idempotence, writer start sequence after primacy, and oversized-entry logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java

### Purpose
`RaftPrimarySelector` adapts embedded-journal leadership notifications into Alluxio's primary selector abstraction.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector`. `start(InetSocketAddress)` initializes state to `STANDBY`, and `stop()` transitions to `STOPPED`.

### Control Flow
Actual primary/standby transitions are driven externally by `RaftJournalSystem.notifyLeadershipStateChanged()`, which calls inherited state-change methods. This class only initializes and stops the selector.

### State, Persistence, And Dependencies
Selector state is inherited and in-memory only. Dependencies are `NodeState`, `AbstractPrimarySelector`, and the local address passed on start.

### Integration Points
`RaftJournalSystem` exposes this selector to the master process and updates it from `JournalStateMachine` Ratis leader callbacks. `gainPrimacy()` checks it during catch-up.

### Risks
If Ratis leader notifications are delayed or missed, this selector reports stale primary state. `start()` always begins as standby even in a single-node cluster until Ratis elects the server.

### Test Signals
Verify start-to-standby, stop-to-stopped, external primary/standby notifications through the journal system, and waiters on `AbstractPrimarySelector` seeing transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java

### Purpose
`RaftSnapshotManager` downloads the newest available embedded-journal snapshot from peer masters when local Ratis logs are insufficient or leader snapshotting is disallowed.

### Important APIs, Types, And Functions
`downloadSnapshotFromOtherMasters()` starts or polls one async download. `waitForAttemptToComplete()` blocks for an in-flight attempt. `core()` selects candidate snapshots, `retrieveFollowerInfos()` requests peer metadata in parallel, and `downloadSnapshotFromAddress()` streams and installs one snapshot. `SnapshotGrpcInputStream` adapts streamed `SnapshotData` chunks to an `InputStream`.

### Control Flow
The manager compares local snapshot term/index to peer metadata, prioritizes newer peer snapshots by `TermIndex`, downloads into the Ratis tmp dir with `DirectoryMarshaller`, moves the tmp dir to the final snapshot directory name, reloads storage metadata, signals a new snapshot, and updates metrics. Failed peers are tried in descending freshness order.

### State, Persistence, And Dependencies
Persistent output is a directory snapshot under `SnapshotDirStateMachineStorage.getSnapshotDir()`. Volatile state includes one `CompletableFuture` and last download duration/size metrics. Dependencies include `RaftJournalServiceClient`, master address configuration, retry policies, `DirectoryMarshaller`, Apache Commons `FileUtils`, Ratis snapshot naming, and metrics.

### Integration Points
`JournalStateMachine.takeSnapshot()` uses this on leaders when local leader snapshots are not allowed, and `notifyInstallSnapshotFromLeader()` uses it when a follower needs a missing snapshot.

### Risks
Only one download future is tracked; callers must poll or wait to observe completion. Moving tmp directories assumes local filesystem semantics. A failed download deletes tmp data in `finally`. Metadata freshness compares only term/index, so peers with equal snapshots are ignored. Data streaming reads byte-by-byte through the marshaller.

### Test Signals
Cover no peers, no local snapshot, metadata sorting, ignoring stale peer snapshots, successful download/install, tmp cleanup on failure, metrics updates, repeated poll behavior, wait-for-attempt behavior, and chunked stream byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java

### Purpose
`SnapshotDirStateMachineStorage` implements Ratis `StateMachineStorage` for Alluxio snapshots that may be directories instead of single files, while preserving compatibility with older single-file snapshots.

### Important APIs, Types, And Functions
`init()` stores `RaftStorage` and loads the latest snapshot. `findLatestSnapshot()` scans snapshot names matching Ratis' snapshot regex and returns `SingleFileSnapshotInfo` or `FileListSnapshotInfo`. `loadLatestSnapshot()`, `signalNewSnapshot()`, `cleanupOldSnapshots()`, `getSnapshotDir()`, and `getTmpDir()` complete the storage contract. `matchSnapshotPath()` exposes regex matching.

### Control Flow
The latest snapshot is the matching path with the greatest term/index. Directory snapshots are represented by all non-MD5 files with relative paths and optional stored MD5 hashes. Cleanup only runs after `signalNewSnapshot()` and deletes older matching snapshot paths beyond the retention count.

### State, Persistence, And Dependencies
State is the `RaftStorage`, cached latest `SnapshotInfo`, and a boolean indicating a newly taken snapshot. Persistent data is in the Ratis state-machine dir and tmp dir. Dependencies include Ratis snapshot info types, `SimpleStateMachineStorage`, MD5 utilities, Apache Commons file filters, and Java NIO file listing.

### Integration Points
`JournalStateMachine`, `RaftSnapshotManager`, and `RaftJournalServiceHandler` share this storage for local snapshot creation, peer snapshot install, latest metadata, and cleanup after Ratis snapshot retention decisions.

### Risks
`Files.list()` failures return null latest snapshots and only log a warning. Directory snapshots without MD5 sidecars are allowed, so integrity coverage may vary by writer. Cleanup depends on `signalNewSnapshot()` and will not remove old snapshots if that call is missed.

### Test Signals
Test empty dirs, latest selection across term/index, old single-file compatibility, directory file-list metadata with relative paths, missing MD5 files, retention cleanup, tmp/snapshot directory paths, and malformed snapshot names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java

### Purpose
`SnapshotIdJournaled` is a small `SingleEntryJournaled` implementation used to store the last journal sequence number included in an embedded-journal snapshot.

### Important APIs, Types, And Functions
It overrides `getCheckpointName()` to return `CheckpointName.SNAPSHOT_ID`. It inherits single-entry checkpoint read/write behavior from `SingleEntryJournaled`.

### Control Flow
During snapshot creation, `JournalStateMachine` processes a synthetic `JournalEntry` whose sequence number is the snapshot ID, then writes this as a checkpoint entry. During restore, another instance restores that checkpoint and exposes the stored entry for sequence-number recovery.

### State, Persistence, And Dependencies
The persisted state is one `JournalEntry` under the `SNAPSHOT_ID` checkpoint name in the snapshot directory. Dependencies include `SingleEntryJournaled`, `CheckpointName`, and journal protobufs.

### Integration Points
`JournalStateMachine.takeLocalSnapshot()` and `install()` use this class before all master checkpoints to align snapshot term/index with Alluxio global sequence numbers.

### Risks
If the snapshot ID is missing or corrupt, restore cannot correctly set `mNextSequenceNumberToRead`, which can cause duplicate or skipped replay. It only stores sequence number, not per-master sequence state.

### Test Signals
Validate checkpoint name, write/restore of a sequence-number entry, missing entry handling through inherited behavior, and integration in snapshot restore updating next sequence number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java

### Purpose
`JournalSink` is the extension point for consumers that observe journal entries as they are replayed or applied.

### Important APIs, Types, And Functions
It defines one method, `append(JournalEntry entry) throws IOException`, for writing or forwarding a single journal entry.

### Control Flow
There is no implementation flow in the interface. Callers invoke sinks after successful state-machine processing through `JournalUtils.sinkAppend()`.

### State, Persistence, And Dependencies
The interface has no state. Implementations may persist or export entries externally. It depends only on the journal protobuf `JournalEntry` and `IOException`.

### Integration Points
Both `BufferedJournalApplier` and UFS replay paths append entries to configured sinks. `AsyncJournalWriter` also receives sink suppliers in the journal systems, so sink behavior can observe primary writes and standby replay depending on configuration.

### Risks
Sink implementations run in journal application paths, so slow or failing sinks can affect replay/write latency depending on `JournalUtils` handling. Implementations must tolerate duplicate or retried journal entries where upper layers permit them.

### Test Signals
Verify sink append on Raft and UFS replay, behavior when a sink throws `IOException`, ordering across entries, duplicate entry behavior, and configuration with empty sink sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java

### Purpose
`UfsJournal` is the legacy under-file-system journal implementation for a single master component. It manages versioned log/checkpoint directories, standby tailing, primary writing, suspend/catch-up, formatting, and checkpoints.

### Important APIs, Types, And Functions
It implements `Journal` with `createJournalContext()`, `getLocation()`, and `close()`. Lifecycle methods include `start()`, `gainPrimacy()`, `signalLosePrimacy()`, `awaitLosePrimacy()`, `suspend()`, `catchup()`, `resume()`, `checkpoint()`, `format()`, and reader/writer factory methods. The inner `UfsJournalCatchupThread` replays a bounded sequence range while suspended.

### Control Flow
Standby start resets master state and starts `UfsJournalCheckpointThread`. Gaining primacy waits for tailer shutdown and quiet period, catches up remaining entries, creates `UfsJournalLogWriter`, wraps it in `AsyncJournalWriter`, and switches to primary. Losing primacy first blocks new writes, then closes writers, resets state, and restarts tailing. Replay reads checkpoints and logs, applies entries, appends sinks, retries I/O for up to a year, and fatal-handles corruption.

### State, Persistence, And Dependencies
Persistent layout is `<base>/v1/logs`, `<base>/v1/checkpoints`, and `<base>/v1/.tmp`, with a format breadcrumb. State includes master, UFS handle, primary/standby/closed state, writer/tailer references, suspension sequence, catch-up flags, checkpoint metrics, and sink supplier. Dependencies include `UnderFileSystem`, `Master`, `UfsJournalReader`, `UfsJournalLogWriter`, checkpoint writer/snapshot helpers, retry policies, and metrics.

### Integration Points
`UfsJournalSystem` creates and coordinates one `UfsJournal` per master. Masters write through `MasterJournalContext`; standbys replay through the checkpoint thread. Backup and journal-system catch-up use suspend/catchup/resume.

### Risks
Primary failover relies on UFS file visibility and quiet-period heuristics. Replay retries I/O nearly indefinitely but crashes on logical gaps or corruption. Suspension stops the tailer and can accumulate unapplied entries until resume. Formatting recursively deletes versioned journal contents. State transitions are synchronized but involve background threads with failure propagation.

### Test Signals
Cover startup replay, primary gain/loss, context unavailability in standby, suspend/catchup/resume ranges, checkpoint no-op and write paths, format breadcrumb, replay retry on I/O, sink append, corrupted entry fatal path, and close during each lifecycle state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java

### Purpose
`UfsJournalCheckpointThread` is the standby tailer for UFS journals. It continuously replays checkpoint/log files into a master, reports catch-up progress, and periodically writes compacted checkpoints.

### Important APIs, Types, And Functions
It extends `AutopsyThread`. Public methods are `awaitTermination(boolean)`, `getNextSequenceNumber()`, `getCatchupState()`, and `onError()`. Core private methods are `runInternal()`, `maybeCheckpoint()`, and `writeCheckpoint(long)`. `CatchupState` reports `NOT_STARTED`, `IN_PROGRESS`, and `DONE`.

### Control Flow
`run()` starts a progress logger thread, then `runInternal()` loops over `JournalReader.advance()`. Checkpoints restore master state; log entries apply to the master and sinks. When no entry is found, the thread maybe checkpoints and sleeps. Shutdown optionally waits a quiet period; active checkpoint writes are interrupted and cancelled.

### State, Persistence, And Dependencies
It owns a `UfsJournalReader`, next sequence-to-checkpoint, shutdown flags, checkpointing flag, catch-up state, and last applied sequence. Persistent writes occur through `UfsJournalCheckpointWriter`. Dependencies include `Master`, `UfsJournal`, `JournalUtils`, `UfsJournalProgressLogger`, configuration sleep/checkpoint thresholds, and `AutopsyThread`.

### Integration Points
`UfsJournal.start()`, `awaitLosePrimacy()`, and `resume()` create this thread. `gainPrimacy()` and `suspend()` stop it and use `getNextSequenceNumber()` to continue replay or record suspend position.

### Risks
A crashed thread propagates during `awaitTermination()` and can kill standby promotion. Interrupted checkpoints are cancelled, but shutdown handling must distinguish intentional interruption. I/O errors reopen the reader and continue, while corruption can crash the master. Quiet-period shutdown is essential to avoiding missed final entries.

### Test Signals
Test checkpoint restore and log apply, catch-up state transitions, checkpoint threshold behavior, cancellation of in-progress checkpoints, quiet-period shutdown, I/O reader reopen, autopsy error propagation, progress logger shutdown, and sequence returned after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java

### Purpose
`UfsJournalCheckpointWriter` writes a checkpoint to a temporary UFS file and commits it atomically enough by renaming to the final checkpoint filename.

### Important APIs, Types, And Functions
`create(UfsJournal,long)` builds the tmp path, final `UfsJournalFile`, and output stream. `write(byte[],int,int)` delegates to the underlying stream. `close()` commits or discards the checkpoint. `cancel()` closes and deletes the temporary file.

### Control Flow
Checkpoint bytes are written under `.tmp/<uuid>`. On close, the writer checks whether an equal or newer checkpoint already exists; if so it deletes the tmp file. Otherwise it ensures the checkpoint directory exists and renames tmp to `checkpoints/0x0-0x<end>`. Rename failures are cleaned up and rethrown unless another writer already produced the destination.

### State, Persistence, And Dependencies
State includes the journal, UFS, final checkpoint file, tmp URI, and closed flag. Persistence is the committed checkpoint file named by exclusive end sequence. Dependencies include `UnderFileSystem`, `UfsJournalFile`, `UfsJournalSnapshot`, and Java `FilterOutputStream`.

### Integration Points
`UfsJournal.checkpoint()` and `UfsJournalCheckpointThread.writeCheckpoint()` use it when compacting master state.

### Risks
Rename semantics vary by UFS and may not be atomic. Concurrent standby checkpoint writers are handled by destination existence checks, but transient failures can still leave tmp files for GC. Closing twice is a no-op; cancellation after close will not delete a committed file.

### Test Signals
Cover successful commit, newer checkpoint preexistence, mkdir failure, rename failure with and without destination, cancel cleanup, double close/cancel, and checkpoint filename encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java

### Purpose
`UfsJournalFile` models UFS journal files and encodes/decodes the naming convention for checkpoints, completed logs, incomplete logs, and temporary checkpoints.

### Important APIs, Types, And Functions
Factory methods create checkpoint, log, and tmp checkpoint instances. Encoding methods build URIs such as `0x0-0x<end>` for checkpoints and `0x<start>-0x<end>` for logs. Decoders parse log/checkpoint filenames and skip temporary rename artifacts. Accessors expose location, start, end, and type predicates. `compareTo()` sorts by end sequence.

### Control Flow
Decoding splits names on `-`, parses hex/decimal-compatible `Long.decode()` values, validates checkpoint start is zero, and returns null for non-range names. Incomplete logs are represented by end `UfsJournal.UNKNOWN_SEQUENCE_NUMBER` (`Long.MAX_VALUE`).

### State, Persistence, And Dependencies
Instances are immutable and represent persistent UFS paths. Dependencies include `URIUtils`, Guava `Preconditions`/`MoreObjects`, and the `UfsJournal` directory helpers.

### Integration Points
All UFS journal readers, writers, snapshots, checkpoint writers, and garbage collection use this class to reason about file ranges and whether data has been superseded.

### Risks
Natural ordering by end sequence does not imply object equality; callers must not use compare result as identity. Range naming is the source of replay ordering, so bad filenames can cause gaps, duplicate scanning, or illegal-state exceptions. `UNKNOWN_SEQUENCE_NUMBER` sorts incomplete logs after completed logs.

### Test Signals
Test encoding/decoding for checkpoints, completed logs, incomplete logs, tmp files, invalid names, checkpoint start validation, type predicates, compare ordering, equality/hashCode, and URI directory placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java

### Purpose
`UfsJournalFileParser` is a low-level parser for reading delimited journal protobuf entries from one UFS file.

### Important APIs, Types, And Functions
It implements `JournalFileParser` with `next()` and `close()`. It owns an `UnderFileSystem`, input stream, current location, and a reusable byte buffer used by `ProtoUtils.readRawVarint32()`.

### Control Flow
On construction it opens the UFS file. `next()` reads a protobuf-delimited length prefix; `-1` means EOF and returns null. It grows the buffer if needed, reads exactly the encoded entry body, and parses a `JournalEntry`. `close()` closes the input stream.

### State, Persistence, And Dependencies
State is the open input stream and reusable buffer. It does not mutate persistent data. Dependencies include `UnderFileSystem`, `UnderFileSystemConfiguration`, `JournalFileParser`, protobuf utilities, and Alluxio configuration.

### Integration Points
This parser supports tools or utilities that parse an individual UFS journal file outside the higher-level `UfsJournalReader` sequencing logic.

### Risks
Malformed length prefixes, truncated bodies, or huge entry lengths can raise I/O/protobuf errors or force buffer resizing. It does not understand checkpoints or sequence ordering; callers must provide the correct file and interpret entries.

### Test Signals
Cover empty files, multiple delimited entries, buffer growth beyond 1024 bytes, truncated varints/bodies, invalid protobuf bytes, close idempotence expectations, and UFS open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java

### Purpose
`UfsJournalGarbageCollector` periodically removes UFS journal files that are no longer needed to recover full master state.

### Important APIs, Types, And Functions
The constructor schedules `gc()` at `MASTER_JOURNAL_GC_PERIOD_MS`. `close()` cancels scheduling and shuts down the executor. `gc()` snapshots journal files and delegates deletion decisions to `gcFileIfStale()`. `deleteNoException()` logs and swallows deletion failures.

### Control Flow
GC keeps the latest checkpoint, sets its end sequence as the checkpoint boundary, and considers older checkpoints, logs at or below that boundary, and temporary checkpoints. Files are only deleted if their last-modified time exceeds the normal or temporary-file threshold.

### State, Persistence, And Dependencies
State is the scheduled executor/future, journal, and UFS handle. Persistent effects are UFS file deletions. Dependencies include `UfsJournalSnapshot`, `UfsJournalFile`, Alluxio configuration thresholds, and `ThreadFactoryUtils`.

### Integration Points
`UfsJournalLogWriter` creates this collector while the journal is primary and closes it with the writer.

### Risks
Incorrect checkpoint boundary calculation can delete logs still needed for recovery. UFS last-modified metadata may be missing or stale, preventing cleanup. Delete failures are non-fatal and can leave buildup. Scheduling starts shortly after writer creation.

### Test Signals
Test latest checkpoint retention, stale old checkpoint/log deletion, fresh file retention, tmp checkpoint threshold, missing last-modified behavior, snapshot listing failure, delete failure logging, and close cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java

### Purpose
`UfsJournalLogWriter` writes primary-master journal entries to UFS log files, rotates completed logs, flushes durable data, and recovers from UFS write/flush failures.

### Important APIs, Types, And Functions
It implements `JournalWriter` with `write()`, `flush()`, `close()`, and `getNextSequenceNumber()`. Important helpers are `maybeRecoverFromUfsFailures()`, `recoverLastPersistedJournalEntry()`, `maybeRotateLog()`, `createNewLogFile()`, `completeLog()`, and inner `JournalOutputStream`.

### Control Flow
Writes ensure primary writability, recover if a prior I/O failure occurred, rotate if needed, assign the next sequence, write a delimited entry, enqueue it for retry, and advance the sequence. Flush syncs the output stream and clears retry entries; oversize logs or UFSs without true flush rotate on the next write. Recovery scans the incomplete log, completes it at the last persisted sequence, creates a new log, and rewrites unflushed entries from the retry queue.

### State, Persistence, And Dependencies
Persistent files are `logs/0x<start>-0x7fffffffffffffff` while open and `logs/0x<start>-0x<next>` when completed. State includes next sequence, rotate flag, current output stream, retry queue, recovery flag, max log size, closed flag, and garbage collector. Dependencies include `UnderFileSystem`, `UfsJournalSnapshot`, `JournalEntryStreamReader`, metrics, `CreateOptions`, and `OpenOptions`.

### Integration Points
`UfsJournal.gainPrimacy()` creates this writer and wraps it in `AsyncJournalWriter`. The writer's GC removes superseded files, and `UfsJournalReader` consumes completed logs.

### Risks
UFS rename and flush semantics differ, especially for object stores; the code rotates on non-flush-capable UFSs to force close/commit. Recovery cannot fill gaps before the oldest retry entry. Closing completes the current log and can race with leadership loss, so `completeLog()` rechecks writability and tolerates concurrent completion.

### Test Signals
Cover sequence assignment, log creation and completion, flush clearing retry queue, size-based rotation, non-flush UFS rotation, write/flush failure recovery, missing-entry recovery fatal path, concurrent complete handling, empty log deletion, close behavior, and GC lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java

### Purpose
`UfsJournalMultiMasterPrimarySelector` uses ZooKeeper/Curator leader election to choose the primary master for UFS journal deployments.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector` and implements `LeaderSelectorListener`. Public methods are `start()`, `stop()`, `getName()`, `stateChanged()`, and `takeLeadership()`. Helpers handle standard versus session-based connection error policy and build Curator clients.

### Control Flow
Construction creates a `LeaderSelector` with auto-requeue. `start()` sets this participant's `host:port` ID and starts selection. `takeLeadership()` sets `PRIMARY`, writes an ephemeral leader path, records the ZooKeeper session, waits until state becomes standby, then deletes the leader path and clears session ID. Connection state changes can demote to standby or preserve primary if session identity survived reconnection under session policy.

### State, Persistence, And Dependencies
State includes election/leader paths, Curator leader selector, participant name, ZooKeeper address, leader session ID, connection policy, and lifecycle state. Persistent/external state is ZooKeeper ephemeral znodes. Dependencies include Curator, ZooKeeper, Alluxio configuration, and `ZookeeperConnectionErrorPolicy`.

### Integration Points
`UfsJournalSystem` uses this selector in multi-master UFS mode to drive gain/loss of primacy across all UFS journals.

### Risks
Incorrect handling of suspended/lost ZooKeeper sessions can produce stale primary state; the session policy mitigates this by comparing session IDs. Leader path cleanup can fail if the session changes. The constructor intentionally creates and closes a client once to avoid stale server session behavior after fast restart.

### Test Signals
Test lifecycle transitions, participant ID, standard-policy demotion, session-policy reconnection with same/different session IDs, ephemeral leader path creation/deletion, auto-requeue behavior, stop before/after start, and Curator client configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java

### Purpose
`UfsJournalProgressLogger` adapts generic journal replay progress logging to UFS journal sequence numbers.

### Important APIs, Types, And Functions
The constructor takes the `UfsJournal`, optional final sequence number, and a supplier for the last applied sequence. `getLastAppliedIndex()` delegates to the supplier. `getJournalName()` returns `UfsJournal.toString()`.

### Control Flow
The checkpoint thread's side progress thread periodically invokes inherited logging; this adapter supplies current progress and journal name.

### State, Persistence, And Dependencies
It stores references only and has no persistent effects. Dependencies include `AbstractJournalProgressLogger`, `OptionalLong`, `Supplier<Long>`, and `UfsJournal`.

### Integration Points
`UfsJournalCheckpointThread.run()` creates this logger using `UfsJournalReader.getLastSN()` as the optional end sequence and `mLastAppliedSN` as current progress.

### Risks
If `getLastSN()` fails, progress estimates lack an end target. The last applied supplier starts at its default until the first log entry is processed, so early logs may show sparse progress.

### Test Signals
Verify supplier forwarding, journal name, optional end sequence behavior, and progress logging during checkpoint-thread replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java

### Purpose
`UfsJournalReader` reads UFS journal checkpoints and logs in sequence order, optionally including the current incomplete log for primary catch-up.

### Important APIs, Types, And Functions
It implements `JournalReader` with `advance()`, `getCheckpoint()`, `getEntry()`, `getNextSequenceNumber()`, and `close()`. `updateInputStream()` snapshots available files and opens the next one. `advanceEntry()` enforces sequence continuity. Static `getLastSN()` estimates the final sequence number without parsing entries.

### Control Flow
On advance, the reader may expose the latest checkpoint if it is newer than the current sequence, then queues logs whose end is beyond the checkpoint and current sequence. It skips incomplete logs unless configured. Entry reads accept exact next sequence, skip duplicates below next sequence, and throw on gaps. Truncated completed logs are fatal; incomplete logs may simply end.

### State, Persistence, And Dependencies
State includes next sequence, current `JournalInputStream`, queued `UfsJournalFile`s, checkpoint stream, next entry, read-incomplete flag, and closed flag. It reads but does not modify UFS files. Dependencies include `UfsJournalSnapshot`, `JournalEntryStreamReader`, `CheckpointInputStream`, UFS open options, and `ProcessUtils`.

### Integration Points
Used by standby checkpoint threads, UFS journal catch-up, primary promotion catch-up, and progress estimation.

### Risks
File snapshots are refreshed only when the processing queue is empty, so visibility timing matters. Gaps throw `IllegalStateException`, and truncated completed logs trigger fatal error. Duplicate entries are tolerated to handle rename races and checkpoint overlap. The checkpoint stream is caller-owned after `advance()` returns `CHECKPOINT`.

### Test Signals
Cover no files, latest checkpoint selection, log queue after checkpoint, incomplete-log include/exclude, duplicate skip, gap detection, truncated complete log fatal path, start sequence offsets, close behavior, and `getLastSN()` with listing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java

### Purpose
`UfsJournalSingleMasterPrimarySelector` is the primary selector for single-master UFS journal deployments.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector`. `start(InetSocketAddress)` immediately sets state to `PRIMARY`. `stop()` is a no-op.

### Control Flow
There is no election or external coordination; starting the selector makes the only master primary.

### State, Persistence, And Dependencies
Selector state is inherited and in-memory. It has no persistent state and depends only on `NodeState`, `AbstractPrimarySelector`, and the local address parameter.

### Integration Points
`UfsJournalSystem` can use this selector when ZooKeeper/multi-master election is not configured, allowing UFS journals to gain primacy immediately.

### Risks
Using this selector in a multi-master deployment would allow unsafe split-brain writes. Stop does not demote state, so lifecycle owners must not reuse it in contexts that expect a stopped state transition.

### Test Signals
Verify immediate primary on start, no exception on stop, and integration that single-master UFS journal systems gain primacy without ZooKeeper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java

### Purpose
`UfsJournalSnapshot` captures a point-in-time listing of UFS journal checkpoints, logs, and temporary checkpoints, and provides helper queries over that listing.

### Important APIs, Types, And Functions
`getSnapshot(UfsJournal)` lists and decodes checkpoint, log, and tmp directories. `getCheckpoints()`, `getLatestCheckpoint()`, `getLogs()`, and `getTemporaryCheckpoints()` expose sorted immutable-by-convention lists. `getCurrentLog()` finds the max log and returns it if incomplete. `getNextLogSequenceNumberToCheckpoint()` returns the latest checkpoint's end or zero.

### Control Flow
Listing methods tolerate absent directories via null status arrays. Checkpoints and logs are decoded through `UfsJournalFile` and sorted by end sequence; temp checkpoint files are decoded as UUID-like tmp entries without sorting requirements.

### State, Persistence, And Dependencies
The object stores lists from one UFS listing pass and does not mutate persistence. Dependencies include `UfsStatus`, `UfsJournalFile`, and Java collection sorting.

### Integration Points
Readers use it to plan replay, writers use it to find incomplete logs and recover failures, checkpoint writers use it to detect newer checkpoints, and GC uses it to delete stale files.

### Risks
It is only a snapshot; concurrent UFS writes/renames can make it stale immediately. Sorting by end sequence places incomplete logs last due to `Long.MAX_VALUE`. Invalid range filenames can throw from decoders.

### Test Signals
Cover empty/missing directories, multiple checkpoints/logs sorted by end, current incomplete log detection, no current log when max is completed, tmp checkpoint listing, latest checkpoint boundary, and invalid filename propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java -->
