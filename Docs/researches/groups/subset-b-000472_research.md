<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java

## Purpose
Exercises `RaftSnapshotManager` snapshot download behavior across a small in-process cluster made from lightweight `SnapshotDirStateMachineStorage` instances and gRPC `RaftJournalServiceHandler` servers. It verifies that a master with no local snapshot can discover and copy the highest reachable snapshot from peer masters.

## Important APIs, Types, And Functions
- `before()` builds three Ratis state-machine storages, exposes them through Alluxio gRPC servers, configures `MASTER_RPC_ADDRESSES`, then creates one `RaftSnapshotManager` per server.
- `downloadSnapshotFromOtherMasters()` and `waitForAttemptToComplete()` are the tested manager APIs.
- `createStateMachineStorage`, `createGrpcServer`, `createSampleSnapshot`, and `directoriesEqual` are reusable test helpers for other Raft snapshot tests.

## Control Flow
Each test arranges peer snapshot directories and server availability, asks manager 0 to download, waits for the asynchronous attempt, and compares returned log index plus directory contents. The manager is expected to skip unavailable peers, prefer higher term/index snapshots, and tolerate repeated attempts after prior success or failure.

## State And Persistence Behavior
State lives in temporary Ratis storage directories and snapshot subdirectories named with Ratis `SimpleStateMachineStorage` term/index naming. Sample snapshots contain files plus saved MD5 sidecars. No persistent repository data is touched.

## Dependencies And Integration Points
Depends on Alluxio configuration, gRPC server builders, `RaftJournalServiceHandler`, Apache Ratis storage and MD5 utilities, commons-io directory traversal, and JUnit temporary folders. It covers the network-facing snapshot exchange path rather than only local storage APIs.

## Risks And Edge Cases
Tests use random available ports and local host addressing, so host resolution and port reuse can make failures environment-sensitive. `successThenFailureThenSuccess` recreates a gRPC server on the same port and is a useful regression guard for cached snapshot clients.

## Test Signals
Passing tests signal correct no-snapshot handling, successful peer copy, resilience to one unavailable peer, highest-snapshot selection, fallback when the highest peer is down, and recovery after a failed cached-client attempt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/RaftSnapshotManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java

## Purpose
Validates `SnapshotDirStateMachineStorage`, Alluxio's directory-based Ratis state-machine snapshot storage, including snapshot discovery, latest snapshot selection, cleanup retention, and backward compatibility with older single-file snapshots.

## Important APIs, Types, And Functions
- `loadLatestSnapshot()` refreshes the storage's cached latest `SnapshotInfo`.
- `getLatestSnapshot()` returns either `FileListSnapshotInfo`, `SingleFileSnapshotInfo`, or null.
- `signalNewSnapshot()` enables deletion by `cleanupOldSnapshots`.
- The test reuses `RaftSnapshotManagerTest.createSampleSnapshot` and `createStateMachineStorage`.

## Control Flow
Tests first establish that newly created storage reports no snapshot and does not update its latest pointer until `loadLatestSnapshot()` is invoked. They then create multiple snapshot names to verify term/index ordering, exercise cleanup with a retention policy of one snapshot, and finally create a legacy single-file snapshot to ensure it still wins over an older directory snapshot.

## State And Persistence Behavior
The state is entirely filesystem-backed under the Ratis snapshot directory. Cleanup is intentionally gated by `signalNewSnapshot`, avoiding deletion merely because `loadLatestSnapshot()` observed old directories. This guards snapshot retention from accidental eager cleanup.

## Dependencies And Integration Points
Uses Apache Ratis `TermIndex`, `SnapshotRetentionPolicy`, `FileListSnapshotInfo`, `SingleFileSnapshotInfo`, and JUnit temporary storage. It integrates with the helper snapshot format used by the Raft snapshot manager tests.

## Risks And Edge Cases
The cleanup path must handle empty directories, exactly one snapshot, multiple snapshots, and mixed file/directory snapshot formats. Compatibility with `SimpleStateMachineStorage.getSnapshotFileName` is critical because Ratis naming drives both discovery and ordering.

## Test Signals
Passing tests signal lazy snapshot refresh, correct newest-term/newest-index selection, deletion only after explicit signaling, retention of a single newest snapshot, and legacy single-file snapshot support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/transport/GrpcMessagingTransportTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/transport/GrpcMessagingTransportTest.java

## Purpose
Tests the gRPC-backed Atomix Catalyst messaging transport used by master coordination features such as backup leader/worker messaging. It focuses on connection establishment, independent connections, closed-client behavior, and closed-server behavior.

## Important APIs, Types, And Functions
- `GrpcMessagingTransport`, `GrpcMessagingClient`, `GrpcMessagingServer`, `GrpcMessagingConnection`, and `GrpcMessagingContext` form the tested transport stack.
- `bindServer` listens on an ephemeral local port and installs a connection listener.
- `connectClient` opens a client connection and sends a dummy request to force the lazy gRPC stream to establish.
- `DummyRequest` implements `CatalystSerializable` and is registered in a local `Serializer`.

## Control Flow
Tests create a single-thread messaging context, bind a server, connect one or more clients, and issue `sendAndReceive` requests. Server-side `MessagingTransportTestListener` installs a handler returning a completed null response. Failure cases close either the connection or server before sending and assert the future completes with `IllegalStateException` or gRPC status failure.

## State And Persistence Behavior
State is transient: connection objects, serializer registrations, request futures, and listener flags. No on-disk state is used. Transport cleanup occurs in `after()` by closing the shared transport.

## Dependencies And Integration Points
Depends on Alluxio configuration and server user state, Atomix Catalyst serialization, Java futures, gRPC exceptions, and JUnit. It is an integration test for the generic messaging substrate consumed by backup roles and other master control paths.

## Risks And Edge Cases
The test captures gRPC's lazy stream behavior by explicitly sending a command before asserting establishment. It also ensures closing one connection does not poison another connection sharing the same client/server transport.

## Test Signals
Passing tests signal connection listeners fire, request handlers work, connections are isolated, closed connections reject sends, and server shutdown propagates to existing clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/transport/GrpcMessagingTransportTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java

## Purpose
Parameterized round-trip tests for `DirectoryMarshaller` implementations. It verifies that no-compression, gzip, and tar-gzip directory marshallers can serialize and reconstruct representative directory trees.

## Important APIs, Types, And Functions
- `DirectoryMarshaller.write(Path, OutputStream)` and `read(Path, InputStream)` are the tested contract.
- Parameter set includes `NoCompressionMarshaller`, `GzipMarshaller`, and `TarGzMarshaller`.
- `tarUntarTest` writes to a byte array, deletes the precreated destination directory, reads into that path, and compares trees with `FileUtil.assertDirectoriesEqual`.

## Control Flow
Each test creates a temporary source tree: empty directory, one-file directory, ten-file directory, empty subdirectory, or ten-level nested path with a file at the leaf. The same round-trip helper runs against all configured marshaller implementations.

## State And Persistence Behavior
State is temporary filesystem content plus an in-memory serialized byte array. The reconstructed path is intentionally removed before read to verify marshallers create their destination structure.

## Dependencies And Integration Points
Uses JUnit parameterized execution, temporary folders, Java NIO files, and the shared compression test `FileUtil`. It tests common `DirectoryMarshaller` behavior independent of the underlying archive format.

## Risks And Edge Cases
Important edge cases are empty directories and empty nested directories, because archive implementations can accidentally drop directory entries when no regular files exist. Deep nesting checks relative path handling.

## Test Signals
Passing tests signal each marshaller preserves directory existence, file content, file counts, and nested relative paths across write/read cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java

## Purpose
Provides a small assertion helper shared by compression tests to compare an original filesystem tree with a reconstructed tree after archive extraction.

## Important APIs, Types, And Functions
- `assertDirectoriesEqual(Path path, Path reconstructed)` walks the original tree, checks each corresponding reconstructed path exists, verifies file-vs-directory type, compares bytes for file inputs, and finally checks total entry counts match.

## Control Flow
The helper traverses `path` with `Files.walk`, relativizes each source entry, resolves it under `reconstructed`, and performs JUnit assertions. It increments an `AtomicLong` for original entry count, then separately walks the reconstructed tree to ensure no extra entries were produced.

## State And Persistence Behavior
No persistent state is kept. It reads bytes from test-created files and relies on temporary directories owned by the caller.

## Dependencies And Integration Points
Uses JUnit assertions, Java NIO walking and byte reads, and `AtomicLong` to mutate a count from inside a lambda. It is consumed by `TarUtilsTest`, `ParallelZipUtilsTest`, and `DirectoryMarshallerTest`.

## Risks And Edge Cases
The file-content branch checks `path.toFile().isFile()` rather than `subPath.toFile().isFile()`, so when the root is a directory it primarily verifies existence/type/count rather than content for every nested file. That makes the helper weaker for directory round trips than intended.

## Test Signals
The helper's passing assertions signal structural equality and, for root-file inputs, byte equality. Compression tests should be interpreted with the noted nested-file content limitation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java

## Purpose
Tests `ParallelZipUtils` directory compression/decompression behavior and verifies that nonzero compression levels reduce archive size for compressible input.

## Important APIs, Types, And Functions
- `ParallelZipUtils.compress(Path, OutputStream, int, int)` writes an archive using a thread count and compression level.
- `ParallelZipUtils.decompress(Path, String, int)` reconstructs a destination path from a zip file.
- `zipUnzipTest` creates a temporary zip file, deletes the precreated extraction directory, decompresses, and compares with `FileUtil.assertDirectoriesEqual`.

## Control Flow
Round-trip tests cover empty, one-file, ten-file, empty-subdirectory, and deeply nested trees. `compressionTest` loops compression levels 0 through 9, records the size at level 0 and later levels, verifies each archive can decompress, cleans each extracted tree and zip, then asserts compressed output is smaller than uncompressed output.

## State And Persistence Behavior
State is temporary directories and temporary zip files under JUnit's `TemporaryFolder`. Cleanup uses Alluxio `FileUtils.deletePathRecursively` and `FileUtils.delete` in the compression-level loop.

## Dependencies And Integration Points
Uses Java NIO, file output streams, JUnit, Alluxio file utilities, and the shared compression `FileUtil`. It validates the parallel zip utility that may be used by snapshot or backup packaging paths.

## Risks And Edge Cases
The test exercises directory entries and deep nesting, but inherits the helper's limited nested-file content check. Compression-size assertions can be sensitive to archive metadata overhead for very small inputs, though the repeated string is chosen to be compressible.

## Test Signals
Passing tests signal zip round-trip structure preservation across representative trees and functional compression-level handling where compressed levels produce smaller files than level 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java

## Purpose
Validates `TarUtils` tar-gzip write/read behavior for common directory shapes, compression levels, and large POSIX uid/gid metadata handling.

## Important APIs, Types, And Functions
- `TarUtils.writeTarGz(Path, OutputStream, int)` and `TarUtils.readTarGz(Path, InputStream)` are the tested APIs.
- `tarUntarTest` serializes to memory, deletes the destination directory, extracts, and compares with `FileUtil.assertDirectoriesEqual`.
- `testLargePosixUserAndGroupIds` uses PowerMock to intercept `TarArchiveEntry(File, String)` construction and force large user/group IDs.

## Control Flow
Basic tests create empty, single-file, multi-file, empty-subdirectory, and deeply nested trees. The large-id test verifies tar creation survives metadata values beyond `TarArchiveEntry.MAXID`. `compressionTest` runs levels 0 through 9 and checks that compressed output is smaller than uncompressed output while each archive remains readable.

## State And Persistence Behavior
Uses JUnit temporary directories and in-memory byte arrays. Extracted directories are deleted between compression-level iterations using Alluxio file utilities.

## Dependencies And Integration Points
Depends on Apache Commons Compress tar classes, PowerMock/JUnit runner integration, Java NIO, and the shared compression assertion helper. It covers the tar-gzip backend used by `TarGzMarshaller`.

## Risks And Edge Cases
Tar metadata can fail for large uid/gid values without long-file or big-number handling, so the PowerMock test is a targeted regression signal. The round-trip equality helper has limited nested-file byte checking, so archive content corruption in nested files may need additional direct assertions.

## Test Signals
Passing tests signal tar-gzip can preserve common directory layouts, tolerate large POSIX ids, and honor compression levels enough to shrink compressible input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/pom.xml -->
# sources/distributed-fs/alluxio/core/server/master/pom.xml

## Purpose
Defines the Maven module for `alluxio-core-server-master`, the jar containing Alluxio master services, REST documentation generation, and exported test classes.

## Important APIs, Types, And Functions
- Parent artifact is `alluxio-core-server`; artifact id is `alluxio-core-server-master`.
- Internal dependencies include common, transport, client-fs, server-common, job-client, and stress-shell modules.
- External dependencies cover AWS S3 SDK, Guava, Dropwizard metrics, Swagger/Jersey/Jetty REST support, RocksDB JNI, fastutil, and servlet APIs.
- Build plugins create a test jar and generate Swagger REST documentation for `AlluxioMasterRestServiceHandler`.

## Control Flow
Maven inherits common configuration from the parent, resolves module dependencies, packages master classes as a jar, optionally exports test classes, and can generate REST API documentation into `generated/master`.

## State And Persistence Behavior
Build output is Maven target data and generated Swagger/static documentation. The POM itself does not encode runtime state, but dependency choices enable runtime persistence implementations such as RocksDB-backed metastores.

## Dependencies And Integration Points
Integrates the master module with Alluxio's multi-module build, underfs implementations for tests, S3 proxy tests, HTTP client, Jersey REST stack, metrics, and RocksDB. The module is central to runtime and test classpath composition.

## Risks And Edge Cases
Dependency scope matters: Jersey JSON is provided, while underfs S3A is test-scoped. Incorrect scopes could bloat runtime artifacts or break tests. The module also repeats `build.path` so running Maven from subproject directories works.

## Test Signals
The test-jar plugin indicates downstream modules rely on master test utilities. Successful Maven test/package runs validate dependency compatibility and REST doc generation configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java

## Purpose
Main entry point for the core Alluxio master process. It validates command-line usage, sets process type, constructs the configured master process, registers shutdown handling, and runs it.

## Important APIs, Types, And Functions
- `main(String[] args)` is the only operational API.
- `CommonUtils.PROCESS_TYPE` is set to `MASTER`.
- `AlluxioMasterProcess.Factory.create()` creates the concrete `MasterProcess`.
- `ProcessUtils.stopProcessOnShutdown` and `ProcessUtils.run` manage lifecycle and error handling.

## Control Flow
If arguments are present, the program logs the expected invocation and exits with `-1`. Otherwise it creates an `AlluxioMasterProcess`; construction failures are routed through `ProcessUtils.fatalError`. A shutdown hook is registered so journal resources close on termination, and `ProcessUtils.run` starts the process.

## State And Persistence Behavior
This class does not own persistent state. Its main state effect is setting global process type, which influences configuration/logging/metrics behavior, and ensuring shutdown closes journal-backed master state through the process lifecycle.

## Dependencies And Integration Points
Depends on Alluxio runtime constants, process utilities, common process-type state, SLF4J logging, and the master process factory. It is invoked by scripts or service managers launching the master JVM.

## Risks And Edge Cases
Any throwable during process creation is fatal because a partially initialized master cannot safely continue. Argument handling is intentionally strict.

## Test Signals
Coverage is typically indirect through process/factory integration tests and launch scripts. The critical signal is that a no-argument launch creates and runs a fully configured master process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java

## Purpose
Implements the core Alluxio master runtime: journal lifecycle, leader election, master registry startup, safe mode, gRPC/web/metrics/JVM services, primary promotion/demotion, backup restore, and emergency backup handling.

## Important APIs, Types, And Functions
- Constructor validates formatted journals, builds `CoreMasterContext`, creates registered masters through `MasterUtils`, and registers primacy timestamp gauges.
- `createBaseRpcServer`, `createRpcExecutorService`, `createWebServer`, `getSafeModeManager`, and `isInSafeMode` customize `MasterProcess`.
- `start()` drives the standby/primary loop.
- `promote()` gains journal primacy and starts masters as leader; `demote()` loses primacy and restarts standby components.
- `startMasterComponents`, `stopMasterComponents`, `initFromBackup`, `takeEmergencyBackup`, and `stop()` manage operational state.
- `Factory.create()` chooses a primary selector based on ZooKeeper, embedded Raft, or UFS journal mode and registers simple services.

## Control Flow
Startup starts the journal, launches standby master components, starts services, optionally waits for journal catchup, then starts leader selection. The loop waits for `PRIMARY`, records gain time, promotes through `mJournalSystem.gainPrimacy`, promotes services, waits for `STANDBY`, records lose time, demotes services and journal, and restarts standby unless configured to exit on demotion.

## State And Persistence Behavior
Persistent state is journal-managed metadata and optional backup restore data. Safe mode is reset when primary starts and later cleared by RPC server/worker wait timing. Backup initialization reads from local or root UFS and can mark root as needing sync. Metrics gauges expose start time, RPC queue/thread state, and primacy timestamps.

## Dependencies And Integration Points
Integrates `JournalSystem`, `PrimarySelector`, `MasterRegistry`, `BackupManager`, `MasterUfsManager`, metastore factories, `RpcServerService`, `WebServerService`, `MetricsService`, `JvmMonitorService`, Ratis/UFS journal selectors, and network address utilities.

## Risks And Edge Cases
Promotion handles unstable leadership during slow journal primacy gain by demoting or exiting. Corruption can trigger emergency backup. Restore-from-backup only runs on an empty journal. Stop is synchronized around `mIsStopped`, but comments acknowledge a failed first stop may require retry.

## Test Signals
Signals include HA failover tests, journal catchup tests, backup restore tests, safe mode behavior, metrics registration, and service readiness checks inherited from `MasterProcess`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java

## Purpose
Runs the secondary master process that replays master journal logs and writes checkpoints without becoming primary.

## Important APIs, Types, And Functions
- Constructor builds a `JournalSystem`, `MasterRegistry`, and `CoreMasterContext` with `AlwaysStandbyPrimarySelector`.
- `start()` starts the journal, marks running, blocks on a latch, then stops journal and closes registry.
- `stop()` releases the latch.
- `waitForReady(int)` waits until `mRunning` becomes true.
- `main(String[] args)` validates no arguments and runs the process.

## Control Flow
Construction creates masters using secondary metastore directory configuration and validates journal formatting. Runtime is simple: start the journal, wait until stop is requested, then cleanly close resources.

## State And Persistence Behavior
The secondary uses journal replay/checkpoint state and metastore factories rooted at `SECONDARY_MASTER_METASTORE_DIR`. It does not own primary state transitions, because the primary selector is always standby.

## Dependencies And Integration Points
Depends on `JournalUtils`, `JournalSystem`, `MasterUtils`, `CoreMasterContext`, `BackupManager`, `MasterUfsManager`, `DefaultSafeModeManager`, and process utilities. It integrates with the same master factories as the primary process but in standby-only mode.

## Risks And Edge Cases
An unformatted journal is fatal at construction. Because startup blocks on a latch, failure to call `stop()` leaves the process waiting. The TODO notes process structure differs from newer master-process classes.

## Test Signals
Readiness is observable through `waitForReady`. Integration signals are successful journal start/replay and clean shutdown with registry close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java

## Purpose
Abstract base for simpler master processes that run a single master domain, such as job master style processes, while sharing journal, service, and primary/standby lifecycle behavior.

## Important APIs, Types, And Functions
- Constructor stores `mMasterName` and `mJournalDomain`, sets a hostname property if missing, and formats an unformatted journal.
- `start()` runs the standby/primary loop.
- `stop()` stops services, journal, components, and leader selector.
- `startMasterComponents` and `stopMasterComponents` wrap registry start/stop with master-specific error messages.

## Control Flow
Startup starts simple services and journal, then starts leader selection. Each loop starts registry components as standby, waits for primary, gains journal primacy, restarts components as leader, promotes services, waits for standby, demotes services, stops components, and loses journal primacy.

## State And Persistence Behavior
Persistent state is journal-backed and can be formatted during construction when absent. Runtime state includes registered simple services, registry components, and leader selector state.

## Dependencies And Integration Points
Extends `MasterProcess`, uses `JournalSystem`, `PrimarySelector`, `SimpleService`, `NodeState`, and network address utilities. It is a reusable lifecycle scaffold for non-core master domains.

## Risks And Edge Cases
Unlike `AlluxioMasterProcess`, this simpler loop does not include catchup protection, emergency backup, unstable-primacy callbacks, or explicit stop flags. Failures in registry start/stop become runtime exceptions.

## Test Signals
Relevant signals are promotion/demotion lifecycle tests for subclasses, journal formatting behavior, service promote/demote ordering, and readiness through inherited `MasterProcess` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java

## Purpose
Abstract base for masters running inside the core master process. It captures core-specific shared dependencies from `CoreMasterContext` and exposes them to subclasses.

## Important APIs, Types, And Functions
- Constructor accepts `CoreMasterContext`, `Clock`, and `ExecutorServiceFactory`, delegates to `AbstractMaster`, then stores safe mode manager, backup manager, journal system, primary selector, start time, and RPC port.

## Control Flow
There is no active control flow beyond construction. Subclasses use the protected fields during their own lifecycle, RPC handling, journaling, and service logic.

## State And Persistence Behavior
The class stores references rather than owning state transitions. Persistence flows through `mJournalSystem` and backup operations through `mBackupManager`.

## Dependencies And Integration Points
Depends on `AbstractMaster`, `CoreMasterContext`, `JournalSystem`, `SafeModeManager`, `BackupManager`, `PrimarySelector`, `Clock`, and executor-service factories. It is the shared superclass for core masters such as block, file system, meta, and metrics masters.

## Risks And Edge Cases
Because fields are protected, subclass behavior depends on `CoreMasterContext` being fully populated. Misconfigured context can cascade into many core master implementations.

## Test Signals
Signals are indirect through concrete core master tests. Construction tests should ensure context values propagate correctly to subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java

## Purpose
Carries shared dependencies and configuration needed by core master implementations, including journal access, safe mode, backup, metastore factories, UFS manager, primary selector, start time, and port.

## Important APIs, Types, And Functions
- `CoreMasterContext` extends `MasterContext<MasterUfsManager>`.
- Getters expose `SafeModeManager`, `BackupManager`, `BlockMetaStore.Factory`, `InodeStore.Factory`, `JournalSystem`, start time, port, and nullable `PrimarySelector`.
- `Builder` provides setters for all fields and `build()`.

## Control Flow
The builder collects dependencies, then the private constructor validates required fields with Guava `Preconditions.checkNotNull` and passes journal, selector, user state, and UFS manager to the superclass.

## State And Persistence Behavior
This is immutable context after construction. Persistence-related behavior is represented by the journal system and metastore factory choices rather than direct I/O.

## Dependencies And Integration Points
Integrates `JournalSystem`, `PrimarySelector`, `UserState`, `BackupManager`, `BlockMetaStore`, `InodeStore`, and `MasterUfsManager`. It is built by `AlluxioMasterProcess` and `AlluxioSecondaryMaster` before `MasterUtils.createMasters` instantiates services.

## Risks And Edge Cases
`PrimarySelector` is nullable by API but many consumers may assume it is available. Builder defaults for start time and port are primitive zero values if omitted, so callers must set them intentionally.

## Test Signals
Signals include construction failure for missing required dependencies and correct propagation into core master subclasses and backup roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java

## Purpose
Implements master safe mode timing. It keeps the primary master in safe mode until the RPC server has started and a configured worker-connect wait interval has elapsed.

## Important APIs, Types, And Functions
- `notifyPrimaryMasterStarted()` resets the state to safe mode with no worker-wait start time.
- `notifyRpcServerStarted()` records the current clock time and keeps safe mode marked true.
- `isInSafeMode()` lazily checks elapsed time and flips the mark to false after `MASTER_WORKER_CONNECT_WAIT_TIME`.
- `AtomicMarkableReference<Long>` stores both wait-start timestamp and safe-mode boolean.

## Control Flow
On primary start, the master is in safe mode. On RPC server start, the wait timer begins. Each `isInSafeMode` call first checks the mark, then either remains in safe mode if no start time exists or the wait interval has not elapsed, or uses compare-and-set to exit safe mode.

## State And Persistence Behavior
State is in-memory and clock-based only. It is reset on primary startup and does not persist across process restarts.

## Dependencies And Integration Points
Uses `ElapsedTimeClock`, Alluxio configuration, and SLF4J. It integrates with `AlluxioMasterProcess.startMasterComponents` and RPC server startup notifications through the `SafeModeManager` interface.

## Risks And Edge Cases
Safe mode exit is lazy and depends on callers querying `isInSafeMode`. Clock injection supports deterministic tests; production uses elapsed time to reduce wall-clock drift risks.

## Test Signals
Tests should cover initial true state, reset on primary start, timer start on RPC server start, true before wait time, false after wait time, and idempotent false after exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java

## Purpose
Common base for Alluxio master processes that own a journal system, primary selector, master registry, RPC/web bind/connect addresses, simple services, and readiness checks.

## Important APIs, Types, And Functions
- Constructor configures bind/connect addresses and registers the master start time metric.
- `configureAddress` assigns a random port only in HA mode when configured port is zero.
- Abstract `createBaseRpcServer` and `createWebServer` are implemented by concrete processes.
- `createRpcExecutorService`, `getSafeModeManager`, `registerService`, `getMaster`, `getRegistry`, and address getters expose shared behavior.
- Readiness APIs poll RPC leader serving, web serving, and metrics serving.

## Control Flow
Construction resolves all service addresses before runtime starts. Services are registered by factories after process construction. Readiness methods use `CommonUtils.waitFor` with configured timeout and convert interruption/timeout to boolean results.

## State And Persistence Behavior
The class itself has no persistent storage. It holds the journal system reference that concrete subclasses start, stop, promote, and demote. Runtime state is service list, registry, addresses, and start timestamp metric.

## Dependencies And Integration Points
Integrates Alluxio process interface, journal system, primary selector, registry, simple services, RPC/web service implementations, metrics system, and network configuration utilities.

## Risks And Edge Cases
Single-master mode rejects port zero to avoid an undiscoverable master. In HA mode, random port assignment mutates global configuration. Readiness depends on service implementation type checks, so custom services must fit expected `RpcServerService`/`WebServerService` contracts.

## Test Signals
Useful signals are port validation, HA random port assignment, service readiness polling, metric registration, and registry/master lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java

## Purpose
Utility class for creating configured master services and selecting metastore implementations for block and inode metadata.

## Important APIs, Types, And Functions
- `createMasters(MasterRegistry, MasterContext)` loads `MasterFactory` implementations from `ServiceUtils`, invokes enabled factories concurrently, and registers created masters.
- `getBlockStoreFactory(String)` returns heap or RocksDB block metastore factories based on `MASTER_BLOCK_METASTORE` or `MASTER_METASTORE`.
- `getInodeStoreFactory(String)` returns heap, RocksDB, or caching RocksDB inode store factories based on inode/metastore configuration and cache size.

## Control Flow
Master creation builds callables for all loaded factories and executes them via `CommonUtils.invokeAll` with a ten-minute timeout. Metastore factory selection checks more-specific config keys first, then falls back to global master metastore type.

## State And Persistence Behavior
Heap metastores are in-memory. RocksDB factories persist metadata under the supplied base directory. Caching inode store wraps RocksDB when the configured inode cache size is nonzero.

## Dependencies And Integration Points
Depends on Alluxio configuration, service loader utilities, metastore types, heap/Rocks/caching metastore classes, and `MasterRegistry`. Used by primary and secondary master process construction.

## Risks And Edge Cases
Factory invocation is parallel, so master factories must tolerate dependency lookup ordering or explicitly fetch already-created required masters. Unknown metastore types throw `IllegalStateException`.

## Test Signals
Signals include correct factory enablement/registration, timeout/error wrapping from `createMasters`, and metastore factory selection for heap, RocksDB, and RocksDB-with-cache configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java

## Purpose
Converts TTL action values between Alluxio gRPC wire enum `TtlAction` and journal protobuf enum `PTtlAction`.

## Important APIs, Types, And Functions
- `fromProtobuf(PTtlAction)` maps journal values to wire values.
- `toProtobuf(TtlAction)` maps wire values to journal values.
- Null inputs default to `DELETE_ALLUXIO` in both directions.

## Control Flow
Each method switches on the enum and returns the corresponding value for `DELETE_ALLUXIO`, `DELETE`, or `FREE`. Unknown enum values throw `IllegalStateException`.

## State And Persistence Behavior
The class is stateless. It influences persistence compatibility because TTL actions stored in journal protobufs must round-trip to the public wire model correctly.

## Dependencies And Integration Points
Depends on `alluxio.grpc.TtlAction` and `alluxio.proto.journal.File.PTtlAction`. It is a low-level bridge used by master metadata journaling and RPC conversion code.

## Risks And Edge Cases
New enum values require updating both switch statements. The null default preserves compatibility but can hide missing values by treating them as `DELETE_ALLUXIO`.

## Test Signals
Tests should verify each enum round-trips, null defaults are intentional, and unknown values fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java

## Purpose
Shared implementation for backup leader and worker roles. It provides executor infrastructure, gRPC messaging serialization/context, backup status tracking, and the common local backup writer.

## Important APIs, Types, And Functions
- Constructor initializes cached executor, scheduled task executor, context dependencies, messaging context, transport timeout, and `BackupTracker`.
- `sendMessageBlocking` sends a Catalyst message over `GrpcMessagingConnection` and waits for acknowledgement.
- `takeBackup` creates the target backup file, streams master state through `BackupManager.backup`, and writes a `.complete` marker.
- `close` shuts down schedulers, messaging context, executors, and resets tracker.

## Control Flow
`takeBackup` resolves the backup parent directory from request or config, chooses root UFS or local UFS based on request options, ensures the directory exists, constructs a timestamped backup name, writes the backup, and deletes the incomplete file if writing fails.

## State And Persistence Behavior
Persistent output is a backup file plus `.complete` marker in UFS or local filesystem. In-memory state includes role closure, executors, messaging context, journal/backup managers, and current backup tracker.

## Dependencies And Integration Points
Integrates `CoreMasterContext`, `BackupManager`, `JournalSystem`, `UfsManager`, `UnderFileSystem`, Alluxio backup configuration, gRPC messaging transport, and Atomix Catalyst serialization.

## Risks And Edge Cases
Failure cleanup attempts to delete only the backup file, not the marker. Local filesystem requests require special UFS creation if root UFS is not local. Interrupted messaging is wrapped as runtime failure.

## Test Signals
Signals include successful backup file and marker creation, parent directory creation, local-filesystem option behavior, cleanup on backup write failure, and executor/context cleanup on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java

## Purpose
Serializable control message used by a backup worker to introduce itself to the backup leader and associate a hostname with the gRPC messaging connection.

## Important APIs, Types, And Functions
- Constructors support Catalyst-required empty creation and hostname creation.
- `getBackupWorkerHostname` returns the worker hostname.
- `setConnection` and `getConnection` attach the inbound `GrpcMessagingConnection` after receipt; the connection is not serialized.
- `writeObject`/`readObject` serialize only the hostname string.

## Control Flow
Workers send this message after establishing a leader connection. The leader handler sets the connection and records hostname by connection in its worker maps.

## State And Persistence Behavior
State is transient message payload and a non-serialized connection reference. No durable persistence is involved.

## Dependencies And Integration Points
Depends on `GrpcMessagingConnection`, Atomix Catalyst serialization, and Guava `MoreObjects`. It is registered by backup messaging contexts in `AbstractBackupRole`.

## Risks And Edge Cases
The connection field is meaningful only after leader-side handler injection; deserialized messages initially have no connection. Null hostname from empty constructor should not be used as a real handshake.

## Test Signals
Signals include correct hostname serialization/deserialization, connection attachment on receipt, and leader worker-map population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java

## Purpose
Serializable control message used by backup workers to report current backup status to the leader.

## Important APIs, Types, And Functions
- Constructors support empty Catalyst deserialization and optional `BackupStatus` payload.
- `getBackupStatus` returns nullable status.
- `writeObject` writes a presence boolean and, when present, serialized `BackupPStatus`.
- `readObject` reconstructs `BackupStatus` from protobuf bytes.

## Control Flow
Worker heartbeat tasks periodically send this message. The leader handler updates `BackupTracker` and adjusts abandon timeout when a status is present. Null status is allowed and effectively acts as an acknowledgement without status update.

## State And Persistence Behavior
State is transient. It carries backup id, state, entry count, URI/error fields embedded in `BackupStatus` serialization but does not persist by itself.

## Dependencies And Integration Points
Depends on Alluxio wire `BackupStatus`, gRPC `BackupPStatus`, Atomix Catalyst serialization, and Guava `MoreObjects`. It is central to delegated backup progress propagation.

## Risks And Edge Cases
Malformed protobuf bytes become runtime deserialization failures. The nullable design requires handlers to avoid assuming status exists.

## Test Signals
Tests should cover null and non-null serialization, status field round-trips, and leader tracker updates from heartbeat messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java

## Purpose
Implements backup behavior while the master is primary. It exposes a backup messaging service to standby workers, initiates backups locally or by delegation, tracks progress, and aborts stale delegated backups.

## Important APIs, Types, And Functions
- `getRoleServices` registers `META_MASTER_BACKUP_MESSAGING_SERVICE`.
- `backup(BackupPRequest, StateLockOptions)` initiates synchronous or asynchronous backup.
- `getBackupStatus` queries the `BackupTracker`.
- `activateWorkerConnection`, `handleHandshakeMessage`, and `handleHeartbeatMessage` manage worker connections.
- `scheduleLocalBackup` locks master state and calls `takeBackup`.
- `scheduleRemoteBackup` suspends a worker, records journal sequence numbers, sends `BackupRequestMessage`, and starts abandon timeout.

## Control Flow
`backup` serializes initiation under `mBackupInitiateLock`, rejects concurrent backups, decides delegation based on HA/config/request options, initializes tracker state and hostname, then schedules local or remote work. Synchronous calls wait for completion; async calls return an initiating status immediately.

## State And Persistence Behavior
Leader state includes current tracker, worker connection set, hostname map, current remote connection, local backup future, heartbeat timeout, and last heartbeat time. Persistent backup files are produced through `AbstractBackupRole.takeBackup` either locally or on a worker.

## Dependencies And Integration Points
Integrates with `StateLockManager`, `JournalSystem` sequence numbers, gRPC messaging service handler, client context interceptor, `BackupTracker`, Alluxio HA configuration, and UFS backup writing.

## Risks And Edge Cases
No standby workers in HA mode causes delegation failure unless `allowLeader` is set. Worker connection loss during delegated backup marks the backup aborted. Heartbeat timeout is rescheduled on each heartbeat and fails stale backups.

## Test Signals
Signals include local backup success/failure, delegation selection, no-worker rejection, bypass delegation, async status behavior, worker loss aborts, heartbeat status propagation, and abandon timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java

## Purpose
Defines the public backup operations supported by backup roles: start a backup and query backup status.

## Important APIs, Types, And Functions
- `backup(BackupPRequest, StateLockOptions)` starts a backup and returns status, with async behavior controlled by request options.
- `getBackupStatus(BackupStatusPRequest)` retrieves the latest or identified backup status.

## Control Flow
This interface does not implement flow, but its contract documents two important behaviors: async requests return once initiated, and HA leaders without standby workers reject delegated backup unless the request allows leader backup.

## State And Persistence Behavior
Implementations persist backup files through role-specific execution and expose status through `BackupStatus`. The interface itself is stateless.

## Dependencies And Integration Points
Depends on gRPC backup request/status types, `StateLockOptions`, Alluxio exceptions, and wire `BackupStatus`. Implemented by `BackupLeaderRole` and rejected by `BackupWorkerRole` for RPC serving.

## Risks And Edge Cases
Callers must understand async status polling and HA delegation semantics. State lock options affect how strongly metadata changes are paused during backup.

## Test Signals
Tests should verify implementations honor sync/async behavior, exception semantics, and status lookup contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java

## Purpose
Serializable leader-to-worker message instructing a standby master to take a delegated backup at a consistent journal point.

## Important APIs, Types, And Functions
- Stores backup UUID, client `BackupPRequest`, and a map of journal names to target sequence numbers.
- `writeObject` serializes UUID string, protobuf request bytes, and journal sequence map.
- `readObject` reconstructs request bytes with `BackupPRequest.parseFrom` and rebuilds the sequence map.

## Control Flow
The leader sends this after successfully suspending a standby and collecting current journal sequence numbers under the state lock. The worker uses the sequence map to catch up before taking the backup.

## State And Persistence Behavior
The message carries transient protocol state. Its journal sequence map is the consistency boundary for delegated backup, while actual persistence happens when the worker writes the backup file.

## Dependencies And Integration Points
Depends on gRPC `BackupPRequest`, Atomix Catalyst serialization, protobuf parsing, Java UUID/map types, and Guava `MoreObjects`. Consumed by `BackupWorkerRole.handleRequestMessage`.

## Risks And Edge Cases
Deserialization failure for the request becomes runtime failure. Map iteration order is not preserved or required, but every journal sequence key must be present for correct catchup.

## Test Signals
Signals include UUID/request/sequence serialization round-trip and worker catchup behavior using the received sequence map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java

## Purpose
Combines backup operation handling with role-specific gRPC service exposure and closeable lifecycle.

## Important APIs, Types, And Functions
- Extends `BackupOps` and `Closeable`.
- `getRoleServices()` returns a map from `ServiceType` to `GrpcService` for services that should be registered while the role is active.

## Control Flow
Implementations choose whether they serve RPCs. The leader role exposes backup messaging service and handles backup RPCs; the worker role exposes no services and rejects direct backup/status RPCs.

## State And Persistence Behavior
The interface is stateless. Implementations manage backup state, messaging connections, executors, and backup file persistence.

## Dependencies And Integration Points
Depends on Alluxio `GrpcService` and `ServiceType`. It is consumed by master role management code to attach backup services appropriate to primary/standby state.

## Risks And Edge Cases
Service maps must be updated when roles change, otherwise stale leader/worker services could remain exposed. Close behavior is part of the contract through `Closeable`.

## Test Signals
Tests should verify leader and worker service maps match role expectations and resources close cleanly on role transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupSuspendMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupSuspendMessage.java

## Purpose
Serializable leader-to-worker message telling a standby master to suspend journal application before a delegated backup request arrives.

## Important APIs, Types, And Functions
- Empty constructor satisfies Catalyst deserialization.
- `writeObject` and `readObject` are no-ops because the message has no payload.
- `toString` uses Guava `MoreObjects`.

## Control Flow
The leader sends this while holding or preparing the state lock in `scheduleRemoteBackup`. The worker handler suspends its journal system and starts a timeout that will resume journals if no backup request follows.

## State And Persistence Behavior
The message itself is stateless. Its handling changes in-memory journal application state on the standby; no data is persisted directly by the message.

## Dependencies And Integration Points
Depends on Atomix Catalyst serialization and is registered in the backup messaging context. It is consumed by `BackupWorkerRole.handleSuspendJournalsMessage`.

## Risks And Edge Cases
Because the message is payload-free, all semantics depend on protocol ordering. If a backup request does not arrive before timeout, the worker resumes journals to avoid indefinite suspension.

## Test Signals
Signals include successful no-payload serialization, worker journal suspension, timeout-based resume, and failure when suspend occurs during another backup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupSuspendMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java

## Purpose
Tracks current and recently finished backup status, entry counts, completion signaling, and failure propagation.

## Important APIs, Types, And Functions
- `reset` initializes `BackupState.None`, counter, and completion future, failing any in-progress backup.
- `getCurrentStatus` returns a defensive copy with current entry count.
- `getStatus(UUID)` returns current matching status, finished status, or `None`.
- `update`, `updateHostname`, `updateBackupUri`, `updateState`, and `updateError` mutate status.
- `waitUntilFinished` blocks until completed or failed.
- `inProgress` checks state and completion future.

## Control Flow
Status updates call `signalIfFinished`. Completed backups set the completion future successfully; failed backups set it exceptionally. Finished statuses are stored by UUID for later lookup. Reset uses a fair lock to serialize replacement.

## State And Persistence Behavior
State is in-memory only: current `BackupStatus`, `SettableFuture`, `AtomicLong` entry counter, fair lock, and concurrent finished-backups map. It does not persist historical statuses beyond process memory.

## Dependencies And Integration Points
Depends on Alluxio backup states/status, exceptions, Guava `SettableFuture`, and `LockResource`. Used by both backup leader and worker roles.

## Risks And Edge Cases
Some update methods mutate `mBackupStatus` without acquiring `mStatusLock`, so thread-safety relies on external sequencing in several paths. Calling `signalIfFinished` repeatedly could attempt to complete an already completed future.

## Test Signals
Tests should cover reset during in-progress backup, completed and failed signaling, timed wait behavior, status copying with entry count, finished status lookup, and concurrent update safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java

## Purpose
Implements backup behavior while a master is standby. It maintains a connection to the primary backup leader, handles suspend and backup request messages, catches up journals, writes delegated backups, sends progress heartbeats, and resumes journals.

## Important APIs, Types, And Functions
- Constructor reads heartbeat/connect/suspend timeout settings and starts leader connection maintenance.
- `getRoleServices` returns no services; direct `backup` and `getBackupStatus` throw because workers do not serve backup RPCs.
- `handleSuspendJournalsMessage` suspends journal application and schedules timeout resume.
- `handleRequestMessage` initializes tracker, starts heartbeat, catches up to requested journal sequences, takes backup, and resumes journals.
- `startHeartbeatThread` periodically sends `BackupHeartbeatMessage`.
- `activateLeaderConnection` registers handlers and sends `BackupHandshakeMessage`.
- `establishConnectionToLeader` repeatedly discovers and connects to the primary.

## Control Flow
The worker continuously retries leader discovery until connected. On suspend, it pauses journal application. On request, it cancels the suspend timeout, transitions tracker through initiating/transitioning/running/completed or failed, and always resumes journals in finally. If leader connection closes, active backup is canceled and connection establishment restarts.

## State And Persistence Behavior
Worker state includes leader connection/listener, backup future, heartbeat future, timeout task, tracker, and suspended journal state. Persistent output is the delegated backup file created by `takeBackup`.

## Dependencies And Integration Points
Integrates `MasterInquireClient`, `GrpcMessagingClient`, `JournalSystem.suspend/catchup/resume`, `CatchupFuture`, backup messages, Alluxio retry policies, and network address utilities.

## Risks And Edge Cases
Failure to resume journals is fatal. A suspend not followed by request times out and resumes journals. If catchup exceeds 30 seconds, backup fails. Leader loss cancels active backup and resets tracker.

## Test Signals
Signals include leader connection retry, handshake delivery, suspend timeout resume, delegated backup success, journal catchup timeout failure, heartbeat propagation, interruption handling, and fatal resume failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockContainerIdGenerator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockContainerIdGenerator.java

## Purpose
Thread-safe in-memory generator for monotonically increasing block container IDs.

## Important APIs, Types, And Functions
- `getNewContainerId()` returns the current ID and increments the atomic counter.
- `getNextContainerId()` and `peekNewContainerId()` return the current next value without incrementing.
- `setNextContainerId(long)` restores or adjusts the next ID.

## Control Flow
All behavior delegates to `AtomicLong`. ID allocation uses `getAndIncrement`; read APIs use `get`; restore uses `set`.

## State And Persistence Behavior
State is the in-memory `AtomicLong`. Persistence must be handled by a higher-level block master journal or checkpoint that calls `setNextContainerId` during restore.

## Dependencies And Integration Points
Implements `ContainerIdGenerable` and is used by block master logic to allocate container IDs for block grouping/allocation metadata.

## Risks And Edge Cases
The generator does not validate monotonic restore values, so setting a lower value could cause ID reuse if callers misuse it. Long overflow is not handled explicitly.

## Test Signals
Tests should verify initial zero, incrementing uniqueness, peek/read behavior, set/restore behavior, and thread-safe uniqueness under concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockContainerIdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java

## Purpose
Defines the central master interface for block metadata, worker metadata, storage capacity/usage reporting, block lifecycle, worker registration/heartbeat, lost block/worker tracking, and container ID generation.

## Important APIs, Types, And Functions
- Capacity and status: `getWorkerCount`, `getCapacityBytes`, `getUsedBytes`, tier maps, unique/replica block counts.
- Worker reporting: live/lost/decommissioned worker info, worker reports, worker addresses, lost storage, rejection/decommission/removal APIs.
- Block lifecycle: `commitBlock`, `commitBlockInUFS`, `getBlockInfo`, `removeBlocks`, `validateBlocks`, lost block reporting and iteration.
- Worker lifecycle: `getWorkerId`, register lease acquire/check/release, `workerRegister`, `workerHeartbeat`, streaming registration APIs, worker ID notification.
- Listener registration APIs announce lost/found/deleted workers and new worker config.

## Control Flow
Implementations coordinate worker RPCs and client queries. Workers first obtain IDs and optional registration leases, register full storage/block state, heartbeat incremental state, and receive commands. Clients query block and cluster storage metadata through service handlers.

## State And Persistence Behavior
Implementations persist block metadata, worker identity mappings, next container ID, and UFS-only committed blocks through journals/checkpoints. Live worker capacity and metrics are runtime state refreshed by registration and heartbeats.

## Dependencies And Integration Points
Extends `Master` and `ContainerIdGenerable`; integrates gRPC request/response types, worker wire types, metrics, journal context, storage tier association, metastore worker info, and report options.

## Risks And Edge Cases
Registration lease correctness affects large worker startup. Duplicate/late heartbeats, lost workers, decommissioning, UFS-only blocks, and invalid block repair are sensitive consistency paths. The visible-for-testing `getWorker` exposes lock-sensitive internals.

## Test Signals
Signals include worker registration/heartbeat flows, lease enforcement, block commit and UFS commit journaling, lost block detection/repair, capacity accounting, reports, listener callbacks, and container ID restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java

## Purpose
gRPC service handler for client-facing block master RPCs: block lookup, cluster capacity/usage, worker listings/reports, lost storage, worker decommissioning, and disabled-worker removal.

## Important APIs, Types, And Functions
- Extends `BlockMasterClientServiceGrpc.BlockMasterClientServiceImplBase`.
- Methods wrap `BlockMaster` calls with `RpcUtils.call`.
- `getBlockMasterInfo` builds `BlockMasterInfo` using requested filters or all fields.
- `getWorkerReport` adapts protobuf options into `GetWorkerReportOptions`.

## Control Flow
Each RPC extracts request/options, calls the corresponding `BlockMaster` method, converts wire objects to protobuf with `GrpcUtils` where needed, and sends the response through the stream observer. Unknown `BlockMasterInfoField` values are logged and skipped.

## State And Persistence Behavior
The handler is stateless aside from its `BlockMaster` reference. Persistence and metadata mutation are delegated to the block master, notably decommission and disabled-worker removal.

## Dependencies And Integration Points
Depends on generated gRPC service classes, `RpcUtils`, `GrpcUtils`, `BlockMaster`, worker report options, protobuf response builders, and SLF4J.

## Risks And Edge Cases
Filtered info requests only populate selected fields, so clients must request what they need. Unknown enum fields are warned rather than failed. Decommission and remove-disabled operations mutate worker eligibility.

## Test Signals
Tests should verify each RPC delegates to the correct `BlockMaster` API, response field mapping, filtered info behavior, exception-to-gRPC conversion through `RpcUtils`, and idempotent disabled-worker removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java

## Purpose
Factory for creating and registering the default `BlockMaster` implementation in the master registry.

## Important APIs, Types, And Functions
- Implements `MasterFactory<CoreMasterContext>`.
- `isEnabled()` always returns true.
- `getName()` returns `Constants.BLOCK_MASTER_NAME`.
- `create(MasterRegistry, CoreMasterContext)` obtains `MetricsMaster`, constructs `DefaultBlockMaster`, registers it as `BlockMaster`, and returns it.

## Control Flow
During `MasterUtils.createMasters`, the service loader invokes this factory. It relies on `MetricsMaster` already being available in the registry, then adds the block master interface mapping.

## State And Persistence Behavior
The factory itself is stateless. The created `DefaultBlockMaster` owns block metadata state and persistence through the provided context.

## Dependencies And Integration Points
Integrates with Alluxio service loading, `MasterRegistry`, `CoreMasterContext`, metrics master, constants, and the default block master implementation.

## Risks And Edge Cases
Parallel master factory creation means dependency ordering on `MetricsMaster` is important. If metrics master is absent, registry lookup will fail during creation.

## Test Signals
Signals include factory enabled/name values, successful registry insertion, correct dependency lookup, and `DefaultBlockMaster` construction with the supplied context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java

## Purpose
gRPC service handler for worker-facing block master RPCs: heartbeats, block commits, UFS commits, worker ID assignment, registration lease acquisition, full and streaming registration, and worker ID notification.

## Important APIs, Types, And Functions
- Extends `BlockMasterWorkerServiceGrpc.BlockMasterWorkerServiceImplBase`.
- `blockHeartbeat` reconstructs added-block maps, converts metrics, and delegates to `workerHeartbeat`.
- `commitBlock` and `commitBlockInUfs` delegate block commit paths.
- `getWorkerId`, `requestRegisterLease`, `registerWorker`, `registerWorkerStream`, and `notifyWorkerId` expose worker lifecycle APIs.
- `reconstructBlocksOnLocationMap` converts flattened `LocationBlockIdListEntry` values to `Block.BlockLocation -> block IDs` maps and fails on duplicate keys.

## Control Flow
RPCs extract request fields, perform lightweight conversions, then call `BlockMaster` via `RpcUtils.call`. Registration enforces `MASTER_WORKER_REGISTER_LEASE_ENABLED`: if enabled, a worker without a lease receives `RegisterLeaseNotFoundException`; successful registration releases the lease.

## State And Persistence Behavior
The handler is stateless. Block/worker metadata updates and journaling occur inside `BlockMaster`. Registration leases are checked and released through the master.

## Dependencies And Integration Points
Depends on generated worker gRPC service classes, Alluxio configuration, `RpcUtils`, `GrpcUtils`, `Metric.fromProto`, protobuf block location types, `RegisterStreamObserver`, and `BlockMaster`.

## Risks And Edge Cases
Large heartbeat/register messages are logged only at debug level. Duplicate location entries trigger `AssertionError`, relying on worker-side deduplication. Lease failures are expected to propagate so workers retry.

## Test Signals
Tests should cover heartbeat conversion, duplicate location rejection, commit delegation, lease-required registration failure/success/release, streaming registration observer behavior, and metric conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java

## Purpose
Small interface for components that allocate unique block container IDs.

## Important APIs, Types, And Functions
- `getNewContainerId()` returns a unique container ID and may throw `UnavailableException`.

## Control Flow
The interface defines no implementation flow. `BlockMaster` extends it, and `BlockContainerIdGenerator` provides a simple atomic implementation.

## State And Persistence Behavior
Implementations decide how to store and persist the next ID. The exception declaration allows implementations backed by unavailable master state or journal context to fail allocation.

## Dependencies And Integration Points
Depends on Alluxio status `UnavailableException`. It is part of the block master API surface used by code that needs container IDs without depending on a concrete implementation.

## Risks And Edge Cases
Callers must handle unavailability and should not assume allocation is purely in-memory. Implementations must prevent reuse across restart and restore.

## Test Signals
Signals include uniqueness, unavailable-state propagation, and correct persisted-next-ID restore for implementations that journal container IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java -->
