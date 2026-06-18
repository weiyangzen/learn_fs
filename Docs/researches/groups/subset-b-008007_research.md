# Research: subset-b-008007

Grouped research for Apache Ozone HDDS container-service tests, streaming tests, upgrade tests, protocol command tests, test resources, and crypto module POMs. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannersAbstract.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannersAbstract.java

Purpose: Abstract JUnit/Mockito base for container scanner test classes, defining the behavioral contract every scanner implementation must satisfy: scan-gap skipping, previously/unscanned handling, unhealthy detection, metrics, shutdown, volume failure, checksum update failure, and volume-scan triggering.

Important APIs/types/functions: `TestContainerScannersAbstract`, mocked `Container<ContainerData>` fixtures (`healthy`, `openContainer`, `openCorruptMetadata`, `corruptData`, `deletedContainer`), `ContainerScannerConfiguration`, `ContainerController`, `setScannedTimestampOld`, `setScannedTimestampRecent`, `verifyContainerMarkedUnhealthy`, `mockKeyValueContainer`, and `setContainers`. `mockContainerController` wires test fixtures through `ContainerTestUtils.setupMockContainer`.

Control flow: `setup` creates lenient mocks, enables scanning, sets scan intervals to zero, and installs a mock controller. Timestamp helpers force data scan eligibility around `CONTAINER_SCAN_MIN_GAP_DEFAULT`. `mockKeyValueContainer` uses a real `KeyValueContainer.shouldScanData` call on a Mockito mock to exercise concrete container-state filtering. `setContainers` changes controller iteration results for volume and global scans.

State and persistence behavior: Maintains an in-memory collection returned by controller mocks and an `AtomicLong` sequence for stable unique container IDs. No disk persistence occurs except mocked volume path exposure.

Dependencies and integration points: Depends on Ozone container scan result helpers, `HddsVolume`, key-value container data, JUnit abstract tests, and Mockito verification modes. Subclasses inherit required test methods and shared fixture state.

Risks and test signals: Lenient Mockito can mask unused or stale stubbing. Timestamp tests depend on wall-clock `Instant.now`. The file is a high-value signal for scanner contract regressions because every scanner subclass must implement the same abstract tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannersAbstract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestDataScanResult.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestDataScanResult.java

Purpose: Unit tests for `DataScanResult`, validating healthy, unhealthy metadata, direct data-error, and deleted-container result shapes.

Important APIs/types/functions: `DataScanResult.fromErrors`, `DataScanResult.unhealthyMetadata`, `DataScanResult.deleted`, `MetadataScanResult.fromErrors`, `ContainerMerkleTreeWriter`, and `ContainerMerkleTreeTestUtils.buildTestTree`.

Control flow: Tests build results from empty, singleton, and repeated errors. Assertions cover `hasErrors`, `isDeleted`, `getErrors`, `toString`, and merkle tree ownership/content. Metadata failure and deletion paths must produce an empty merkle tree, while data-error construction preserves the provided tree instance.

State and persistence behavior: Pure in-memory value-object testing; no persistent state. Static `TREE` is reused across tests.

Dependencies and integration points: Uses Ozone scan error factories and checksum merkle tree utilities. This connects scanner result modeling to checksum persistence expectations without invoking scanners.

Risks and test signals: The tests catch regressions where deleted or metadata-failed scans accidentally carry stale checksum trees, and where `toString` loses operator-facing error counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestDataScanResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestMetadataScanResult.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestMetadataScanResult.java

Purpose: Unit tests for `MetadataScanResult`, covering healthy empty-error results, unhealthy error aggregation, and deleted-container representation.

Important APIs/types/functions: `MetadataScanResult.fromErrors`, `MetadataScanResult.deleted`, `ContainerTestUtils.getMetadataScanError`, and JUnit assertions.

Control flow: Each test constructs one result and asserts error flags, deletion flags, error-list size, and human-readable `toString` content. Two-error aggregation verifies plural count handling.

State and persistence behavior: Pure immutable-result testing; no filesystem or database state.

Dependencies and integration points: Supports scanner tests by validating the result objects that metadata scanners return to container controllers and on-demand/background scanners.

Risks and test signals: Good regression coverage for distinguishing deletion from corruption. It does not validate error ordering or specific `ContainerScanError` fields beyond count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestMetadataScanResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOnDemandContainerScanner.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOnDemandContainerScanner.java

Purpose: Concrete test suite for `OnDemandContainerScanner`, exercising asynchronous single-container scans, deduplication, metrics, shutdown, checksum updates, unhealthy marking, and volume-failure behavior.

Important APIs/types/functions: `OnDemandContainerScanner.scanContainer`, `scanContainerWithoutGap`, `shutdown`, `OnDemandScannerMetrics`, `ContainerController.markContainerUnhealthy`, `updateDataScanTimestamp`, `updateContainerChecksum`, `DataTransferThrottler`, `Canceler`, and inherited fixtures from `TestContainerScannersAbstract`.

Control flow: Setup constructs the scanner from shared config/controller. Tests submit scans, wait on returned `Future`s when present, and verify scanner behavior. Duplicate tests block `scanData`/`scanMetaData` behind latches and assert the second scheduling returns `Optional.empty`. Shutdown tests interrupt a long scan and ensure no false unhealthy mark. Rescan tests move a mock container into `UNHEALTHY` and verify subsequent scans count differently.

State and persistence behavior: Maintains scanner executor state, in-flight container IDs, metrics source registration in `DefaultMetricsSystem`, scan timestamps, and checksum update calls. No real persistence, but controller calls model persisted timestamp/checksum writes.

Dependencies and integration points: Integrates scanner result classes, container controller, metrics system, volume failure flags, and logging (`LogCapturer`) for volume scan trigger messages.

Risks and test signals: Strong concurrency signal for duplicate suppression and shutdown interruption. Wall-clock scan-gap tests can be timing-sensitive. The timestamp test appears to rescan `healthy` while verifying `deletedContainer` timestamp was never updated, relying on fixture behavior rather than directly scanning deleted first.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOnDemandContainerScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java

Purpose: Tests `OzoneContainer` container-map rebuild, node report generation, committed-space reconstruction, missing-container tracking, and disk-full container creation failures across schema/layout variants.

Important APIs/types/functions: `ContainerTestVersionInfo.ContainerTest`, `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, `KeyValueContainer`, `KeyValueContainerData`, `OzoneContainer.buildContainerSet`, `gatherContainerUsages`, `getNodeReport`, `BlockUtils.getDB`, and helper methods `addBlocks`, `verifyCommittedSpace`, `mockHddsVolume`.

Control flow: `initTest` configures layout/schema, `setup` creates volume sets and DB instances, then tests format volumes, create containers, write block/chunk metadata into RocksDB tables, restart/rebuild `OzoneContainer`, and compare container counts, committed bytes, usage, and missing ID sets. Node report tests configure metadata/Ratis/container DB directories and assert report list sizes. Disk-full test consumes all volume capacity then expects `StorageContainerException` with `DISK_OUT_OF_SPACE`.

State and persistence behavior: Writes real temporary container directories and RocksDB metadata; deletes some container directories to validate missing-container persistence in `ContainerSet`. Committed-space expectations are tracked in `commitSpaceMap`.

Dependencies and integration points: Exercises storage volumes, schema V3 DB setup, key-value container layout, node reports, and low-level metadata tables.

Risks and test signals: Good integration signal for upgrade/restart-like rebuild paths. Random datanode IP and temporary disk usage can create environmental sensitivity. Mock-volume usage checks decouple container ID iteration from actual volume internals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestScanTransientIOUtil.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestScanTransientIOUtil.java

Purpose: Tests transient scan I/O classification, specifically "Too many open files" detection in exception messages and scan-error collections.

Important APIs/types/functions: `ScanTransientIOUtil.isTooManyOpenFiles`, `scanErrorsAreOnlyTooManyOpenFiles`, `MetadataScanResult.fromErrors`, `ContainerScanError`, and `FailureType`.

Control flow: Unit tests feed `FileSystemException`, `FileNotFoundException`, nested `IOException`, unrelated `IOException`, all-transient scan errors, mixed errors, and empty results into the utility and assert boolean classification.

State and persistence behavior: Pure classification tests. `File` instances are placeholders and not read.

Dependencies and integration points: Protects scanner behavior that should treat file-descriptor exhaustion differently from durable corruption or missing files.

Risks and test signals: Message matching can be platform-sensitive. The mixed-error test ensures transient-only classification is not broadened accidentally.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestScanTransientIOUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStreamTest.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStreamTest.java

Purpose: Abstract reusable test suite for gRPC-backed `OutputStream` implementations that frame byte writes into protobuf messages.

Important APIs/types/functions: `GrpcOutputStreamTest<T>`, `createSubject`, `verifyPart`, `CallStreamObserver<T>`, `ByteString`, `getRandomBytes`, and helper write/concat methods.

Control flow: Tests mix single-byte writes and byte-array writes, exact buffer fills, buffer overflow into multiple responses, write-after-close rejection, and close completion. `verifyResponses` captures all `onNext` messages, slices expected byte ranges by configured buffer size, and requires each data field to be a `LiteralByteString`.

State and persistence behavior: In-memory random buffers and mocked stream observer only. `subject.close()` must emit `onCompleted` once.

Dependencies and integration points: Base class is extended by `TestCopyContainerResponseStream` and `TestSendContainerOutputStream`, enforcing identical framing semantics for download and upload streams.

Risks and test signals: Random buffer sizes/data broaden coverage but make exact reproduction less direct. It catches subtle copy/concat regressions in protobuf payload construction and post-close state handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorSchedulingBenchmark.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorSchedulingBenchmark.java

Purpose: Manual scheduling-efficiency benchmark for `ReplicationSupervisor`; it is intentionally not named as a normal `Test*` class but contains a JUnit method for ad hoc validation.

Important APIs/types/functions: `ReplicationSupervisor.newBuilder`, `ReplicationTask`, `ReplicateContainerCommand.fromSources`, `ContainerReplicator`, `MockDatanodeDetails`, `Time.monotonicNow`, and resource-lock maps.

Control flow: Builds two source datanodes, per-datanode volume locks, and local destination locks. A synthetic replicator randomly locks a remote volume for download and a local disk for import, waiting one second each. The benchmark schedules 100 tasks and asserts total runtime under 100 seconds.

State and persistence behavior: No real container persistence; only synchronized lock objects and console output simulate constrained disks.

Dependencies and integration points: Models interaction between supervisor scheduling and remote/local disk contention.

Risks and test signals: Uses `Object.wait(1000)` without notifications as a sleep mechanism and random source/disk selection, so timing can be noisy. Useful for manual regression checks, not deterministic CI signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorSchedulingBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerImporter.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerImporter.java

Purpose: Tests `ContainerImporter` duplicate protection, in-progress tracking, checksum consistency validation, imported-container scanning, failure-triggered volume handling, and reset of last scan time.

Important APIs/types/functions: `ContainerImporter.importContainer`, `getImportContainerProgress`, `getKeyValueContainerData`, `getPacker`, `ContainerController.importContainer`, `ContainerSet.scanContainer`, `StorageVolumeUtil.onFailure`, `TarContainerPacker`, and `ContainerDataYaml`.

Control flow: Setup builds a real `MutableVolumeSet`, `ContainerSet`, and spy/mocked controller. Tests reject an existing container, reject a second import while the first is blocked on a semaphore, force inconsistent container checksums, import a tar descriptor and verify scanner invocation, mock import failure to verify volume failure callback, and assert imported data scan timestamp becomes empty.

State and persistence behavior: Creates real temporary tar files containing `container.yaml`. Tracks import-in-progress IDs in the importer and mutates `KeyValueContainerData` scan timestamp.

Dependencies and integration points: Integrates tar packing, volume choosing, controller import, volume failure utility, and container-set on-demand scanning.

Risks and test signals: Strong signal for duplicate/import-progress races and cleanup. Some paths use spies and static mocking, so internal method names are coupled to tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerImporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerCompression.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerCompression.java

Purpose: Validates the `CopyContainerCompression` enum's protobuf conversion, configuration binding, fallback behavior, and stream wrapping round trip.

Important APIs/types/functions: `CopyContainerCompression.toProto`, `fromProto`, `setOn`, `getConf`, `getDefaultCompression`, `wrap(OutputStream)`, `wrap(InputStream)`, and config key `HDDS_CONTAINER_REPLICATION_COMPRESSION`.

Control flow: Parameterized enum tests assert conversion and config round trip for every compression value. Invalid config string returns the default. I/O test writes random bytes through compression output, checks compressed bytes differ for compression modes, then reads through the matching input wrapper and verifies full restoration.

State and persistence behavior: Uses byte-array streams only; no persisted files.

Dependencies and integration points: Shared by copy/download and send/upload replication streams to negotiate compression consistently with protobuf and `OzoneConfiguration`.

Risks and test signals: Good compatibility signal for new enum values. Small 16-byte payloads may not expose buffering edge cases for every compression codec.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerCompression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerResponseStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerResponseStream.java

Purpose: Concrete `GrpcOutputStreamTest` for `CopyContainerResponseStream`, the server-to-client download response stream.

Important APIs/types/functions: `CopyContainerResponseStream`, `CopyContainerResponseProto`, inherited gRPC stream tests, and `verifyPart`.

Control flow: `createSubject` constructs a response stream with observer, container ID, and buffer size from the base class. `verifyPart` checks each protobuf response carries the expected container ID, read offset, length, and data bytes.

State and persistence behavior: In-memory observer messages only.

Dependencies and integration points: Ensures download streaming semantics match the abstract framing contract used by replication downloads.

Risks and test signals: Relies on the abstract suite for most coverage. It catches field-mapping regressions in offsets and lengths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerResponseStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestDownloadAndImportReplicator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestDownloadAndImportReplicator.java

Purpose: Tests that `DownloadAndImportReplicator` releases reserved committed space when download/import replication fails.

Important APIs/types/functions: `DownloadAndImportReplicator.replicate`, `SimpleContainerDownloader.getContainerDataFromReplicas`, `ContainerImporter`, `MutableVolumeSet`, `HddsVolume.getCommittedBytes`, `ReplicationTask`, and container size config.

Control flow: Setup builds real volume/importer infrastructure with mocked downloader. The test blocks downloader failure behind a semaphore after space reservation, verifies committed bytes rise by twice the container max size, releases the failure, then waits for committed bytes to return to the initial value.

State and persistence behavior: Uses a temporary data volume and committed-byte accounting. No successful container import is persisted.

Dependencies and integration points: Couples downloader failure handling to importer reservation semantics and volume accounting.

Risks and test signals: Uses async `CompletableFuture` and wait loops, so timeout tuning matters. It is a focused guard against leaked reservations after failed replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestDownloadAndImportReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcContainerUploader.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcContainerUploader.java

Purpose: Tests `GrpcContainerUploader` lifecycle around starting uploads, response callbacks, errors, and client closure.

Important APIs/types/functions: `GrpcContainerUploader.startUpload`, `GrpcReplicationClient.upload`, `SendContainerRequest`, `SendContainerResponse`, `CompletableFuture<Void>` callback, and `CallStreamObserver`.

Control flow: A subject subclass injects a mocked `GrpcReplicationClient`. Success returns an observer whose `onNext` sends a normal response. Error test sends response observer `onError` after data is written. Immediate-error test has `upload` throw. All paths verify client closure, and error paths verify callback exceptional completion or thrown exception.

State and persistence behavior: In-memory streams and futures; no disk state.

Dependencies and integration points: Covers push replication upload handshake and failure propagation into `PushReplicator` completion futures.

Risks and test signals: `NoopObserver` always ready and does not exercise backpressure. Strong signal for resource cleanup on normal and exceptional paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcContainerUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcReplicationService.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcReplicationService.java

Purpose: Integration tests for replication gRPC service download and push-upload paths using real `ReplicationServer`, container controller, volume, and key-value container setup.

Important APIs/types/functions: `ReplicationServer`, `GrpcReplicationService.download`, `SimpleContainerDownloader`, `GrpcContainerUploader`, `PushReplicator`, `OnDemandContainerReplicationSource`, `ContainerImporter.importContainer`, `CopyContainerRequestProto`, and `CopyContainerResponseProto`.

Control flow: `init` creates datanode details with replication ports, a real container, controller, mocked importer, and starts a replication server. `testDownload` downloads a closed container into a temp directory and checks generated tar naming. `testUpload` pushes a container to the same datanode and verifies importer receives the ID. `closesStreamOnError` injects a source that throws during copy and verifies response stream completion.

State and persistence behavior: Creates real temporary volume/container data and downloads one tar-like file into a temp directory. `pushContainerId` records imported ID through a mocked importer.

Dependencies and integration points: Exercises gRPC server/client, security config, datanode ports, container controller, downloader, uploader, and push replicator end to end.

Risks and test signals: Network port and temporary filesystem behavior can be environment-sensitive. Strong signal for protocol compatibility and stream cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcReplicationService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestMeasuredReplicator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestMeasuredReplicator.java

Purpose: Tests metric accounting wrapper `MeasuredReplicator` for success/failure counts, transferred bytes, replication duration, failure duration, success duration, and queue time.

Important APIs/types/functions: `MeasuredReplicator.replicate`, `AbstractReplicationTask.Status`, metric getters for success/failure bytes and times, and `ReplicationTask.getQueued`.

Control flow: Setup installs a delegate replicator that marks odd container IDs done, even IDs failed, sets transferred bytes to ID * 1024, and sleeps by container ID milliseconds. Tests execute tasks and assert counters/timers include only the correct status class. Queue-time test overrides `getQueued` to one second in the past.

State and persistence behavior: Metrics are in-memory and closed after each test.

Dependencies and integration points: Provides coverage for supervisor-visible metrics around any `ContainerReplicator` implementation.

Risks and test signals: Sleep-based timing assertions may be slow or slightly noisy but use lower bounds. The tests guard against mixing success/failure byte and time counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestMeasuredReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestPushReplicator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestPushReplicator.java

Purpose: Tests push-based container replication status handling, compression propagation, and upload stream cleanup.

Important APIs/types/functions: `PushReplicator.replicate`, `ContainerReplicationSource.copyData`, `ContainerUploader.startUpload`, `CopyContainerCompression`, `ReplicationTask`, and `SpyOutputStream`.

Control flow: Helper builds mocked source/uploader and captures the completion future and compression. Success parameterizes all compression values, completes the future normally, and expects task `DONE`. Failure completes the future exceptionally, or throws during copy, and expects task `FAILED`. Every path asserts the output stream closes exactly once.

State and persistence behavior: No persistent data; stream closure and task status are the state under test.

Dependencies and integration points: Covers config-to-compression handoff between push replicator, upload stream, and data source.

Risks and test signals: Does not cover partial data writes or remote backpressure. Strong signal for cleanup and status correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestPushReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationConfig.java

Purpose: Tests `ReplicationServer.ReplicationConfig` configuration parsing, defaulting, and bounds enforcement.

Important APIs/types/functions: `ReplicationConfig.getReplicationMaxStreams`, `getOutOfServiceFactor`, config keys `REPLICATION_STREAMS_LIMIT_KEY` and `REPLICATION_OUTOFSERVICE_FACTOR_KEY`, and constants for defaults/min/max.

Control flow: Tests valid values, invalid negative stream limit fallback, out-of-service factor clamping below min/above max, exact boundary acceptance, and default object creation from an empty `OzoneConfiguration`.

State and persistence behavior: In-memory configuration only.

Dependencies and integration points: Drives `ReplicationSupervisor` pool and queue scaling behavior, especially during decommission/maintenance states.

Risks and test signals: Good guard for operational config safety. It does not test live reconfiguration directly; that appears in `TestReplicationSupervisor`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationSupervisor.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationSupervisor.java

Purpose: Comprehensive behavioral suite for `ReplicationSupervisor`, covering task lifecycle, metrics, deduplication, deadlines, SCM term filtering, EC reconstruction, reconciliation, priority ordering, queue limits, and dynamic thread-pool scaling.

Important APIs/types/functions: `ReplicationSupervisor`, `ReplicationSupervisorMetrics`, `ReplicationTask`, `ECReconstructionCoordinatorTask`, `ReconcileContainerTask`, `ReplicateContainerCommand`, `ReconstructECContainersCommand`, `ReconcileContainerCommand`, `ReplicationServer.ReplicationConfig`, `DatanodeConfiguration`, `StateContext`, `FakeReplicator`, `FakeECReconstructionCoordinator`, `BlockingTask`, and `OrderedTask`.

Control flow: Tests use direct executors for deterministic immediate execution, a discarding executor for stalled in-flight tasks, and a single-thread executor for queue-size checks. Normal/duplicate/failure tests assert request, success, failure, skipped, in-flight, queue, and container counts. Deadline tests fast-forward a `TestClock`; obsolete SCM term tasks are dropped. Multiple-replication tests mix replication and EC tasks and verify per-metric-name counters. Reconciliation tests validate success/failure/timeout metrics and duplicate reconcile command deduplication by container ID. Priority ordering blocks the executor, queues NORMAL and LOW tasks at different logical times, then validates priority-before-age order. State update tests verify stream-limit scaling for maintenance/decommission and queue limit doubling.

State and persistence behavior: Uses in-memory `ContainerSet` plus temporary tar metadata for import reserve-space tests. `ReplicationSupervisor` tracks in-flight queues, metrics, request timing, and dedupe keys. Some tests create real `MutableVolumeSet` committed-byte state.

Dependencies and integration points: Integrates replication commands, EC reconstruction, datanode operational state, container import/download, volume accounting, metrics collection, and SCM term context.

Risks and test signals: This is the central regression suite for replication scheduling. Timing and async wait loops can be flaky if executor behavior changes. The fake replicators assume same-thread execution in several tests, so executor choice is part of the contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationSupervisor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerOutputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerOutputStream.java

Purpose: Concrete `GrpcOutputStreamTest` for `SendContainerOutputStream`, the upload stream used for push replication.

Important APIs/types/functions: `SendContainerOutputStream`, `SendContainerRequest`, `CopyContainerCompression`, inherited stream framing tests, and `verifyPart`.

Control flow: Base tests verify byte framing. `usesCompression` parameterizes every compression enum, writes one buffer, closes the stream, and verifies the emitted request includes container ID, offset zero, data, and the compression proto.

State and persistence behavior: In-memory observer messages only.

Dependencies and integration points: Ensures push upload requests carry correct framing and compression metadata for `SendContainerRequestHandler`.

Risks and test signals: Good field-level protocol signal. Does not exercise actual compressed payload transformation because the tested stream records compression metadata and data bytes in request construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerRequestHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerRequestHandler.java

Purpose: Tests server-side handling of pushed container data, especially duplicate rejection and committed-space reservation/release across normal completion and failures.

Important APIs/types/functions: `SendContainerRequestHandler.onNext`, `onCompleted`, `ContainerImporter.isAllowedContainerImport`, `chooseNextVolume`, `importContainer`, `getRequiredReplicationSpace`, `getDefaultReplicationSpace`, `SendContainerRequest`, and `SendContainerResponse`.

Control flow: Setup creates real volume/importer infrastructure and spies the importer. Existing-container test adds a container then verifies `onError` receives `StorageContainerException(CONTAINER_EXISTS)`. Parameterized reservation tests cover null, zero, normal 2GB, and overallocated 20GB size fields. They assert committed bytes rise on first request and return to initial values on completion, on `onNext` import denial, and when `importContainer` throws during completion. Overallocated test compares explicit size reservation against default reservation.

State and persistence behavior: Uses real `MutableVolumeSet` committed-byte accounting and temporary directories. Handler tracks selected target volume and temporary received data until completion.

Dependencies and integration points: Bridges gRPC upload protocol, importer capacity planning, volume reservation, and response observer error propagation.

Risks and test signals: Strong leak-prevention coverage for reservation cleanup. It does not inspect the temporary file contents beyond request creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerRequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSimpleContainerDownloader.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSimpleContainerDownloader.java

Purpose: Tests `SimpleContainerDownloader` source selection, retry across failed datanodes, async/direct failure handling, randomization, and client closure.

Important APIs/types/functions: `SimpleContainerDownloader.getContainerDataFromReplicas`, `shuffleDatanodes`, `createReplicationClient`, `downloadContainer`, `GrpcReplicationClient.close`, and nested `TestingContainerDownloader`.

Control flow: A testing subclass returns completed paths named after selected datanodes, throws immediately for configured failed datanodes, or returns futures that fail asynchronously. Happy path uses first datanode when shuffle is disabled. Failure tests verify fallback to the next datanode. Random-selection test runs many iterations and expects the second datanode to appear at least once. All clients are verified closed.

State and persistence behavior: No real downloads; returned `Path` encodes datanode UUID. Temporary directory is passed but not populated by the test subclass.

Dependencies and integration points: Supports pull replication robustness and resource cleanup around gRPC clients.

Risks and test signals: Random-selection test is probabilistic but extremely low false-failure probability. It validates retry behavior without testing actual network transfer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSimpleContainerDownloader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java

Purpose: Package-level documentation for tests under `org.apache.hadoop.ozone.container.replication`.

Important APIs/types/functions: Declares the package and contains the package Javadoc "Tests for the container replication."

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Provides Javadoc grouping for replication test package.

Risks and test signals: No runtime behavior. Useful only for documentation/package identity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestDirstreamClientHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestDirstreamClientHandler.java

Purpose: Tests `DirstreamClientHandler` parsing of directory streaming protocol chunks and validation of malformed file headers.

Important APIs/types/functions: `DirstreamClientHandler.doRead`, `isAtTheEnd`, `DirectoryServerDestination`, Netty `ByteBuf`, and invalid-format parameter provider.

Control flow: Tests stream messages containing file-size/name headers, content bytes, and `END`, split across header boundaries, inside headers, second headers, and content. Valid cases assert written file contents and end state. Invalid cases pass malformed headers and expect `IllegalArgumentException` containing "Invalid file name format".

State and persistence behavior: Writes streamed file contents into a temporary destination directory.

Dependencies and integration points: Covers client-side protocol parser used by `StreamingClient` and directory destination writer.

Risks and test signals: Strong parser boundary coverage. It validates header format but not path traversal or nested directory names in this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestDirstreamClientHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestStreamingServer.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestStreamingServer.java

Purpose: Integration tests for directory streaming server/client, including plain streaming, SSL streaming, missing stream IDs, timeout handling, and channel cleanup on timeout.

Important APIs/types/functions: `StreamingServer`, `StreamingClient`, `DirectoryServerSource`, `DirectoryServerDestination`, `StreamingException`, Netty `SslContext`, `SelfSignedCertificate`, and `streamDir`.

Control flow: Tests create source/destination subdirectories, write one file, start a server on port 0, stream a subdir through a client, and compare bytes. SSL test builds server/client SSL contexts with a self-signed certificate. Failure test streams a missing ID and expects runtime failure. Timeout tests override `getFilesToStream` to sleep longer than the client timeout and assert an exception, including a no-try-with-resources client path that explicitly closes after checking timeout message.

State and persistence behavior: Uses temporary source and destination directories and writes real file contents.

Dependencies and integration points: Exercises network server startup, client connection, directory source/destination, optional TLS, and timeout/channel lifecycle.

Risks and test signals: Network and timing tests can be environment-sensitive. The channel-leak test documents a previous bug class around `await()` timeout handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestStreamingServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/package-info.java

Purpose: Package-level documentation for `org.apache.hadoop.ozone.container.stream` tests.

Important APIs/types/functions: Declares the package and Javadoc "Unit tests for streaming."

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadoc/package identity for streaming tests.

Risks and test signals: No runtime test behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDataNodeStartupSlvLessThanMlv.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDataNodeStartupSlvLessThanMlv.java

Purpose: Tests datanode startup rejection when stored metadata layout version exceeds the software layout version.

Important APIs/types/functions: `DatanodeStateMachine`, `DatanodeLayoutVersion` directory constant `DATANODE_LAYOUT_VERSION_DIR`, `HDDSLayoutVersionManager.maxLayoutVersion`, `UpgradeTestUtils.createVersionFile`, and `DatanodeDetails`.

Control flow: Creates metadata layout directory under a temp folder, configures `OZONE_METADATA_DIRS`, writes a VERSION file with MLV = max SLV + 1, constructs `DatanodeStateMachine`, and asserts `IOException` message ends with the expected MLV > SLV text.

State and persistence behavior: Writes a real VERSION file in a temp metadata directory.

Dependencies and integration points: Guards upgrade layout storage compatibility at datanode startup.

Risks and test signals: Strong safety signal for downgrade/incompatible metadata detection. Message suffix assertion couples to exception text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDataNodeStartupSlvLessThanMlv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToContainerIdsTable.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToContainerIdsTable.java

Purpose: Tests upgrade from HBase support layout to witnessed container DB proto table schema for container create info.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `ContainerTableSchemaFinalizeAction`, `WitnessedContainerMetadataStore`, `WitnessedContainerDBDefinition.CONTAINER_CREATE_INFO_TABLE_DEF`, `ContainerCreateInfo`, `ContainerID`, `StringCodec`, and `UpgradeTestHelper`.

Control flow: Starts SCM RPC and a pre-finalized datanode at `HBASE_SUPPORT`, creates a container, verifies old table name `containerIds` stores state as a string, closes the container, finalizes, and verifies the new proto table is selected and contains `ContainerCreateInfo` with state `OPEN`. Retry test manually executes finalize action with extra dummy rows, removes dummy old-table rows, then finalizes and verifies the new table count is reconciled to one.

State and persistence behavior: Uses real metadata DB tables and temporary datanode storage. Table migration state persists across finalize action calls.

Dependencies and integration points: Exercises upgrade finalization, container dispatcher commands, SCM endpoint setup, and witnessed container metadata store.

Risks and test signals: Strong migration idempotency signal. Tests depend on old table name/string codec details and close containers before finalize to satisfy upgrade preconditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToContainerIdsTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToHBaseSupport.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToHBaseSupport.java

Purpose: Tests behavior gates around finalizing from `HADOOP_PRC_PORTS_IN_DATANODEDETAILS` to `HBASE_SUPPORT`.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `HDDSLayoutFeature.HBASE_SUPPORT`, `ContainerDispatcher`, `UpgradeTestHelper.putBlock`, `finalizeBlock`, `closeContainer`, and `ContainerProtos.Result.UNSUPPORTED_REQUEST`.

Control flow: Each test starts SCM and a pre-finalized datanode, creates a container, attempts a feature-gated operation before finalization and expects `UNSUPPORTED_REQUEST`, closes the container, finalizes, creates a new container, and verifies the same operation succeeds after finalization. Covered gates are incremental chunk list support and block finalization.

State and persistence behavior: Real temp datanode metadata/volume state and container writes through dispatcher.

Dependencies and integration points: Validates layout-feature gating across container command dispatch, not just version flags.

Risks and test signals: Good compatibility signal for pre-finalized clusters. It assumes containers must be closed before finalization can proceed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToHBaseSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToSchemaV3.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToSchemaV3.java

Purpose: Broad upgrade suite for transitioning datanode container schema V2 to schema V3 and DB-volume handling, parameterized with schema V3 enabled and disabled.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `VersionedDatanodeFeatures.SchemaV3.isFinalizedAndEnabled`, `DatanodeConfiguration.CONTAINER_SCHEMA_V3_ENABLED`, `HDDSLayoutFeature.DATANODE_SCHEMA_V3`, `HddsVolume`, `DbVolume`, `DatanodeLayoutStorage`, and `UpgradeTestHelper`.

Control flow: Tests DB creation on data volumes and configured DB volumes, creation during finalize for existing formatted volumes, idempotent double finalize, adding HDDS/DB volumes after finalize, schema choice for new writes after restart, reads during concurrent finalization, and finalize failure rollback/readability. `testWrite` first writes schema V2 data with V3 disabled, restarts after finalization with a selected flag, writes another container, and asserts expected schema. Failure test mocks DB creation failure, catches finalize exception, then verifies old V2 data remains readable before and after restart.

State and persistence behavior: Creates real layout storage, volume directories, DB parent directories, container data, and SCM endpoint state. Mutates config between restarts to model cluster rollout.

Dependencies and integration points: Integrates datanode layout manager, volume sets, DB volumes, container dispatcher, datastream config, SCM RPC, and schema feature gates.

Risks and test signals: High-value upgrade and data-safety coverage. Many tests are integration-heavy and can be sensitive to filesystem timing, restart semantics, and feature-flag interpretation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToSchemaV3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/UpgradeTestHelper.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/UpgradeTestHelper.java

Purpose: Shared utility class for datanode upgrade tests, reducing boilerplate for starting/restarting pre-finalized datanodes, configuring volumes, and dispatching container commands.

Important APIs/types/functions: `startPreFinalizedDatanode`, `restartDatanode`, `callVersionEndpointTask`, `addHddsVolume`, `addDbVolume`, `dispatchRequest`, `readChunk`, `putBlock`, `addContainer`, `deleteContainer`, `closeContainer`, and `finalizeBlock`.

Control flow: Startup helper writes layout storage with requested metadata layout version, closes any prior DSM, starts a new `DatanodeStateMachine`, asserts MLV, and calls the version endpoint task to obtain SCM/cluster IDs. Restart helper preserves datanode details, optionally sets DB parent dirs, validates MLV exact or lower-bound, and calls version endpoint. Command helpers construct requests via `ContainerTestHelper`, dispatch them, and assert expected results.

State and persistence behavior: Mutates `OzoneConfiguration` volume path lists, creates temporary HDDS/DB volume directories, initializes datanode layout storage, and sends real dispatcher commands that create/write/close/delete containers.

Dependencies and integration points: Central integration layer for SCM RPC, endpoint state machine, Ozone container, container dispatcher, pipelines, and upgrade feature tests.

Risks and test signals: Helper correctness is critical because multiple upgrade suites inherit its assumptions. Random container IDs can collide theoretically. Assertions inside helpers make failures concise but can hide intermediate protocol details.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/UpgradeTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/protocol/commands/TestReconstructionECContainersCommands.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/protocol/commands/TestReconstructionECContainersCommands.java

Purpose: Tests `ReconstructECContainersCommand` validation and protobuf round-trip behavior for erasure-coded container reconstruction commands.

Important APIs/types/functions: `ReconstructECContainersCommand`, nested `DatanodeDetailsAndReplicaIndex`, `ECReplicationConfig`, `getProto`, `getFromProtobuf`, `DatanodeDetails.getFromProtoBuf`, and `UnsafeByteOperations.unsafeWrap`.

Control flow: One test constructs mismatched missing-index and target-datanode counts and expects `IllegalArgumentException`. Round-trip test builds five source datanodes with replica indexes, two targets, missing indexes `{1,2}`, and EC 3-2 config; asserts `toString` includes missing indexes, proto fields match originals, and reconstructed command equals original semantic fields.

State and persistence behavior: Pure in-memory command/protobuf testing.

Dependencies and integration points: Supports SCM-to-datanode EC reconstruction command protocol consumed by EC reconstruction tasks/supervisor.

Risks and test signals: Strong serialization compatibility signal. It does not verify command execution, only construction and conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/protocol/commands/TestReconstructionECContainersCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/resources/ozone-site.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/resources/ozone-site.xml

Purpose: Test resource configuration overriding selected datanode storage behavior for container-service tests.

Important APIs/types/functions: XML Hadoop/Ozone configuration with properties `hdds.datanode.du.factory.classname` and `hdds.datanode.volume.min.free.space`.

Control flow: Loaded by test configuration mechanisms as a site override. It sets disk usage factory to `org.apache.hadoop.hdds.fs.MockSpaceUsageCheckFactory$None` and minimum free space to `0MB`.

State and persistence behavior: No runtime state itself; affects tests by disabling real disk usage checks and free-space floor constraints.

Dependencies and integration points: Integrates with Hadoop configuration loading and Ozone datanode volume space accounting.

Risks and test signals: Useful for deterministic tests, but it can hide production-like disk-space behavior if tests unintentionally rely on this resource.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/resources/ozone-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/crypto-api/pom.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/crypto-api/pom.xml

Purpose: Maven module descriptor for `hdds-crypto-api`, the HDDS cryptographic API artifact.

Important APIs/types/functions: Maven coordinates inherit parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact ID `hdds-crypto-api`, module name/description, and property `maven.test.skip=true`.

Control flow: Maven build metadata only. No dependencies are declared in this module.

State and persistence behavior: Defines build-time artifact identity and test-skip behavior; no runtime persistence.

Dependencies and integration points: Participates in the parent HDDS reactor as the API surface for cryptographic functions. Empty dependency section suggests interfaces/classes in the module are expected to avoid module-level external dependencies.

Risks and test signals: `maven.test.skip=true` means module-local tests are not run, which can hide API regressions unless covered by downstream modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/crypto-api/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/crypto-default/pom.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/crypto-default/pom.xml

Purpose: Maven module descriptor for `hdds-crypto-default`, the default HDDS cryptographic implementation artifact.

Important APIs/types/functions: Maven coordinates inherit parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact ID `hdds-crypto-default`, module name/description, and property `maven.test.skip=true`.

Control flow: Maven build metadata only. No explicit dependencies are declared.

State and persistence behavior: Defines artifact identity and test-skip behavior; no runtime state.

Dependencies and integration points: Intended as default implementation counterpart to HDDS crypto API, integrated through the parent reactor.

Risks and test signals: No module-local tests are run and no dependencies are declared here, so correctness depends on implementation files elsewhere or downstream integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/crypto-default/pom.xml -->
