# Research: subset-b-008000

This grouped report covers the Ozone container service, replication, streaming, upgrade, protocol, and selected SCM command classes assigned to `subset-b-008000`. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OzoneContainer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OzoneContainer.java

Purpose: composes and owns the datanode container subsystem. It initializes storage volumes, container handlers, the dispatcher, write and read xceiver servers, the server-to-server replication endpoint, scanners, block deletion, disk balancing, stale recovering-container scrubbing, metrics, checksum-tree management, and the witnessed-container metadata store.

Important APIs and functions: the main constructor builds `MutableVolumeSet` instances for data, metadata, and optional DB volumes; creates a `ContainerSet`; installs per-container-type `Handler`s; creates `HddsDispatcher`, `ContainerController`, `XceiverServerRatis`, `XceiverServerGrpc`, `ReplicationServer`, `BlockDeletingService`, and optional `DiskBalancerService`. `buildContainerSet()` starts one `ContainerReader` per data volume, waits for all readers, then validates missing witnessed-container entries. `start(String)` persists the cluster ID layout state, loads containers, starts volume checks, scanners, replication, xceiver channels, deletion, balancing, and scrubbing. `stop()` shuts the same services down and closes metrics/checksum/witnessed metadata resources. Accessors expose reports, volume sets, channels, dispatcher, controller, metrics, and replication server.

Control flow and state: `initializingStatus` prevents duplicate concurrent startup under SCM HA. Startup moves from persisted layout to container loading, immediate volume validation, background service start, xceiver start, and final `INITIALIZED` status. Container reports are pushed through an inline `IncrementalReportSender` synchronized on `containerSet`; immediate reports trigger a heartbeat. Schema V3 finalization controls whether per-volume RocksDB stores are loaded and whether periodic compaction is scheduled.

Dependencies and integration: integrates datanode state machine context, SCM heartbeat/report generation, Ratis/GRPC xceiver servers, security token verification, TLS, volume checker, container scanners, disk balancer, upgrade feature flags, witnessed-container DB, and replication import/export. It is the object other datanode services query for container state and node reports.

Risks and test signals: the highest-risk areas are idempotent multi-call `start`, matching start/stop order, volume failure handling, DB-volume null handling, scanner enablement, and space/accounting changes around replication and deletion. Tests should cover SCM HA repeated startup, failed volume startup, Schema V3 compaction scheduling, container set rebuild with witnessed metadata, report generation for data/meta/db volumes, and clean shutdown after partial startup failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OzoneContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ScanTransientIOUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ScanTransientIOUtil.java

Purpose: identifies scan failures caused only by transient file-descriptor exhaustion so scanner callers can distinguish environmental IO pressure from container corruption.

Important APIs and functions: `scanErrorsAreOnlyTooManyOpenFiles(ScanResult)` returns true only when the scan has at least one error and every error's exception chain matches `too many open files`. `isTooManyOpenFiles(Throwable)` walks up to 64 causes, tracks visited exceptions by identity to avoid cause-cycle loops, and delegates to `matchesTooManyOpenFiles`. Matching checks `FileSystemException.getReason()` first and then the generic exception message, case-normalized with `Locale.ROOT`.

Control flow and state: the class is stateless and final. The only state is local traversal state for cycle detection and a depth limit. A clean scan explicitly returns false, which prevents callers from treating absence of errors as a transient failure.

Dependencies and integration: depends on `ScanResult` and standard Java exception types. It is meant for scanner decision logic in `ozoneimpl` where corruption marking should be avoided for known transient resource exhaustion.

Risks and test signals: matching is message-based and therefore platform/JDK dependent. Tests should cover `FileSystemException` reasons, nested causes, null throwables/messages, cause cycles, mixed transient and non-transient scan errors, and uppercase/localized variants of the target text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ScanTransientIOUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/package-info.java

Purpose: documents the `org.apache.hadoop.ozone.container.ozoneimpl` package as the Ozone main layer that calls into the container layer.

Important APIs and types: no classes or functions are declared here beyond the package declaration. The package contains service composition, container scanning, and container controller implementation classes.

Control flow and state: none locally. The file only provides package-level Javadoc.

Dependencies and integration: used by Javadoc and package metadata tooling. It gives context for `OzoneContainer` and nearby scanner/controller classes.

Risks and test signals: no runtime risk. Build/Javadoc validation should ensure the package declaration remains aligned with the directory path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/AbstractReplicationTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/AbstractReplicationTask.java

Purpose: supplies common lifecycle, priority, timing, and identity fields for datanode-side replication-like tasks executed by `ReplicationSupervisor`.

Important APIs and types: subclasses implement `runTask()`, `getMetricName()`, and `getMetricDescriptionSegment()`. Public accessors expose container ID, queued time, deadline, SCM term, priority, status, and whether the task may run only on in-service datanodes. `Status` enumerates `QUEUED`, `IN_PROGRESS`, `FAILED`, `DONE`, and `SKIPPED`. `setPriority`, `setStatus`, and `setShouldOnlyRunOnInServiceDatanodes` are mutation hooks for subclasses and supervisors.

Control flow and state: status is volatile to be visible across executor and observer threads. The queued timestamp is captured at construction using an injectable `Clock`, which allows deterministic tests. Deadline zero means no deadline. Priority defaults to normal and affects queue ordering through supervisor task runners.

Dependencies and integration: references SCM `ReplicationCommandPriority` and feeds metric names into supervisor counters. `ReplicationTask` is the main concrete subclass in this package.

Risks and test signals: uniqueness semantics are defined by subclasses, not this class. Tests should verify deadline interpretation, queued-time injection, status visibility, priority ordering values, and that out-of-service execution flags are set only for task types that need them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/AbstractReplicationTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerDownloader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerDownloader.java

Purpose: defines the pull-replication download contract for copying a raw container archive from one or more source datanodes into a local working directory.

Important APIs and types: `getContainerDataFromReplicas(long containerId, List<DatanodeDetails> sources, Path downloadDir, CopyContainerCompression compression)` returns the downloaded archive path or null when no source succeeds. The interface extends `Closeable` so implementations can own network clients or thread resources.

Control flow and state: none in the interface. Implementations decide whether to try sources sequentially, in random order, or in parallel.

Dependencies and integration: used by `DownloadAndImportReplicator` before `ContainerImporter.importContainer`. The concrete implementation here is `SimpleContainerDownloader`, which uses `GrpcReplicationClient`.

Risks and test signals: callers expect a complete local tarball and clean failure semantics. Tests for implementations should cover null/default download directories, compression propagation, retry ordering, partial file cleanup, and closing any underlying network clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerDownloader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerImporter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerImporter.java

Purpose: imports a replicated container tarball into local datanode storage, selecting a target volume, validating metadata/checksum state, unpacking through the appropriate container handler, and registering the container in the `ContainerSet`.

Important APIs and functions: `isAllowedContainerImport` rejects imports already in progress or containers already present. `importContainer` guards duplicate imports with `importContainerProgress`, reads the container descriptor via `TarContainerPacker`, verifies the container file checksum, sets the selected `HddsVolume`, clears data-scan timestamp, delegates actual import to `ContainerController.importContainer`, updates volume used space, overwrites missing-container tracking, and schedules an on-demand scan. `chooseNextVolume` asks the configured `VolumeChoosingPolicy` for a volume with reserved space. `getUntarDirectory` builds the `tmp/container-copy` work path under a volume. `getSpaceToReserve` uses actual replicate size when available, otherwise default SCM container size.

Control flow and state: the synchronized `HashSet` `importContainerProgress` is the process-local duplicate-import lock. The tarball is deleted in all paths. Failed imports mark the chosen volume failed through `StorageVolumeUtil.onFailure`.

Dependencies and integration: used by pull replication after download and by push replication request handling after stream completion. It depends on `ContainerDataYaml`, `ContainerUtils`, `TarContainerPacker`, volume selection, `ContainerController`, and `ContainerSet`.

Risks and test signals: space reservation must be balanced by callers, while used-space accounting happens here after successful import. Tests should cover duplicate push/pull races, tarball cleanup on all exceptions, checksum failure, descriptor parse failure, volume failure marking, actual-size reservation, and on-demand scan scheduling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerImporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicationSource.java

Purpose: abstracts the source side of container replication, allowing implementations to prepare and stream a binary representation of a container.

Important APIs and types: `prepare(long containerId)` gives a source implementation a chance to precompute or cache an archive. `copyData(long containerId, OutputStream destination, CopyContainerCompression compression)` writes the full container representation to the destination stream.

Control flow and state: none in the interface. The concrete on-demand implementation does no pre-work and exports directly when `copyData` is invoked.

Dependencies and integration: consumed by `GrpcReplicationService.download` for pull replication and `PushReplicator` for push replication. Compression is passed in so the source and destination agree on archive encoding.

Risks and test signals: callers assume `copyData` writes a complete valid container archive or throws. Tests should exercise missing containers, compression compatibility, stream close behavior, and any implementation-specific caching invalidation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicator.java

Purpose: small strategy interface for executing a `ReplicationTask`.

Important APIs and types: `replicate(ReplicationTask task)` is the only method. Implementations in this package include pull (`DownloadAndImportReplicator`), push (`PushReplicator`), and metric-wrapped (`MeasuredReplicator`) strategies.

Control flow and state: none in the interface. Implementations are responsible for setting the task status and transferred bytes.

Dependencies and integration: `ReplicationTask.runTask()` delegates here, and `ReplicationSupervisor` observes the final task status for counters.

Risks and test signals: a replicator that returns without setting `DONE`, `FAILED`, or `SKIPPED` can skew supervisor metrics. Tests should verify every implementation sets status on success and failure and handles interrupted/network exceptions consistently.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerUploader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerUploader.java

Purpose: abstracts client-side push replication upload setup.

Important APIs and types: `startUpload(long containerId, DatanodeDetails target, CompletableFuture<Void> callback, CopyContainerCompression compression)` opens an `OutputStream` that the caller writes container archive bytes to. The callback completes when the remote side reports upload completion or failure.

Control flow and state: none locally. Implementations must bridge stream writes to the underlying transport and complete the callback exactly once.

Dependencies and integration: used by `PushReplicator`, with `GrpcContainerUploader` as the gRPC implementation.

Risks and test signals: callers block on the callback after copying data. Tests should cover callback completion on remote success/error, stream close propagation, compression field propagation, and cleanup when upload creation fails after a transport client is opened.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerCompression.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerCompression.java

Purpose: enumerates supported compression codecs for container-copy streams and converts between configuration, protobuf, and wrapped Java streams.

Important APIs and functions: enum values are `NO_COMPRESSION`, `GZIP`, `LZ4`, `SNAPPY`, and `ZSTD`. `getConf(ConfigurationSource)` reads `HDDS_CONTAINER_REPLICATION_COMPRESSION` and falls back to no compression on invalid values. `setOn(ConfigurationTarget)` writes the enum to config. `toProto` and `fromProto` convert to `CopyContainerCompressProto`. `wrap(InputStream)` and `wrap(OutputStream)` use Apache Commons Compress except that `NO_COMPRESSION` returns the original stream.

Control flow and state: each enum stores the Commons Compress factory name. Unsupported configured or protobuf values do not fail replication setup; they degrade to no compression.

Dependencies and integration: passed through `GrpcReplicationClient`, `GrpcReplicationService`, `SendContainerOutputStream`, `SendContainerRequestHandler`, `TarContainerPacker`, pull download, and push upload paths.

Risks and test signals: codec availability and framing compatibility are critical because archives are packed and unpacked on different datanodes. Tests should cover each codec, invalid config fallback, null/unknown proto fallback, stream wrapping exception conversion, and mixed source/target compression negotiation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerCompression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerResponseStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerResponseStream.java

Purpose: adapts an `OutputStream` write path to gRPC `CopyContainerResponseProto` messages for pull-replication downloads.

Important APIs and functions: the constructor passes the gRPC `CallStreamObserver`, container ID, and buffer size to `GrpcOutputStream`. `sendPart` builds a response containing container ID, data bytes, EOF flag, current read offset from `getWrittenBytes()`, and chunk length, then calls `onNext`.

Control flow and state: buffering, ready/backpressure waiting, byte counting, and final `onCompleted` are inherited from `GrpcOutputStream`. The offset is computed before the inherited byte counter is incremented, so it represents the starting offset of the message.

Dependencies and integration: created by `GrpcReplicationService.download`; its output is consumed by `GrpcReplicationClient.StreamDownloader`.

Risks and test signals: offset/length correctness and EOF semantics must match the downloader's expectations. Tests should cover multi-chunk streams, exact-buffer-size boundaries, final partial chunk, backpressure delay, and remote cancellation/error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerResponseStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/DownloadAndImportReplicator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/DownloadAndImportReplicator.java

Purpose: implements pull replication by downloading a container archive from source datanodes and importing it locally.

Important APIs and functions: `replicate(ReplicationTask)` skips if the container is already present, reads the configured `CopyContainerCompression`, chooses a target volume using default replication space, downloads into that volume's `container-copy/tmp` directory through `ContainerDownloader`, records downloaded byte size, invokes `ContainerImporter.importContainer`, and sets task status to `DONE` or `FAILED`.

Control flow and state: the method is synchronous and runs inside the replication supervisor executor. It reserves space through `chooseNextVolume`; in `finally`, it decrements committed bytes by default replication space if a volume was selected. Download failure returning null marks the task failed without import.

Dependencies and integration: coordinates `ContainerSet`, `ContainerImporter`, `ContainerDownloader`, `HddsVolume`, and compression config. It is selected for replicate-from-sources commands.

Risks and test signals: the reservation decrement currently uses default space even when actual container size support exists elsewhere; tests should verify reservation balance, source retry behavior, existing-container skip, tarball cleanup delegated to importer, transferred byte accounting, and IO exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/DownloadAndImportReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcContainerUploader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcContainerUploader.java

Purpose: implements `ContainerUploader` by opening a gRPC upload stream to a target datanode and returning an `OutputStream` that sends `SendContainerRequest` messages.

Important APIs and functions: `startUpload` optionally reads the local container's `bytesUsed` from `ContainerController` and sends it in the first request for better target-side reservation. It creates a `GrpcReplicationClient`, wraps the request stream in `WrappedRequestStreamObserver`, creates a `SendContainerOutputStream`, and closes the client when the stream closes. `createReplicationClient` uses the target replication port and security config. `SendContainerResponseStreamObserver` completes the provided future on server completion or error. `WrappedRequestStreamObserver` forwards calls while surfacing response-side errors from `isReady`.

Control flow and state: the upload stream is bidirectional: outgoing archive chunks flow through the returned stream while response observer completes the callback. Transport clients are closed on construction failure and on output close.

Dependencies and integration: used by `PushReplicator`. It depends on gRPC stubs, `ContainerController`, TLS/security config, and `SendContainerOutputStream`.

Risks and test signals: response errors must break producer writes promptly, and client cleanup must occur exactly once. Tests should cover missing local container size, first-message size field, server error before/after writes, callback completion, close cleanup, and wrapped observer propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcContainerUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStream.java

Purpose: provides the shared `OutputStream` to gRPC stream adapter used by both pull download responses and push upload requests.

Important APIs and functions: `write(int)` and `write(byte[], int, int)` buffer data in a protobuf `ByteString.Output` until `bufferSize` is reached. `close()` flushes remaining data with `eof=true`, logs total bytes, calls `onCompleted`, and closes the buffer once. `flushBuffer` waits for readiness, converts the buffer to a `ByteString`, calls subclass `sendPart`, increments `writtenBytes`, and resets the buffer. `waitUntilReady` polls `CallStreamObserver.isReady()` with 10 ms sleeps up to 30,000 tries.

Control flow and state: `closed` is an `AtomicBoolean`; writes after close fail via Guava `Preconditions`. Write exceptions call `streamObserver.onError(ex)` but do not rethrow for the single-byte path. Subclasses supply message construction while this class owns byte counting and backpressure.

Dependencies and integration: parent for `CopyContainerResponseStream` and `SendContainerOutputStream`.

Risks and test signals: polling backpressure can block executor threads for up to five minutes. Tests should cover write bounds, chunk splitting, close idempotence, interruption, readiness timeout, observer errors, and exact `writtenBytes` offsets in subclass messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationClient.java

Purpose: gRPC client for datanode-to-datanode replication download and upload calls.

Important APIs and functions: the constructor builds a `ManagedChannel` with max inbound message size, optional mutual TLS from `SecurityConfig` and `CertificateClient`, no proxy detection, and a generated `IntraDatanodeProtocolServiceStub`. `download` sends a `CopyContainerRequestProto` for a whole container using configured compression, creates a destination tar path, and returns a `CompletableFuture<Path>` completed by `StreamDownloader`. `upload` exposes the generated bidirectional upload stream. `close` shuts the channel down with a five-second termination wait.

Control flow and state: `closed` prevents repeated shutdown. `StreamDownloader` creates parent directories and an output stream at construction, writes each response chunk to the stream, closes and completes on success, and closes/deletes/completes exceptionally on any stream or filesystem error.

Dependencies and integration: used by `SimpleContainerDownloader` and `GrpcContainerUploader`. It depends on generated datanode protocol stubs, Netty gRPC, TLS managers, and container tar naming utilities.

Risks and test signals: partial download cleanup and channel shutdown affect retry safety. Tests should cover TLS and plaintext setup, parent directory creation, onNext write failure deletion, onError cleanup, onCompleted close failure, repeated close, and compression request field propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationService.java

Purpose: server-side gRPC service exposing datanode replication download and upload methods.

Important APIs and functions: `bindServiceWithZeroCopy` rebuilds the generated service definition so upload and download request marshallers use Ratis `ZeroCopyMessageMarshaller`, preserving any other methods unchanged. `download` converts compression from proto, wraps the response observer in `CopyContainerResponseStream`, and asks `ContainerReplicationSource.copyData` to stream the archive. `upload` creates a `SendContainerRequestHandler` that receives pushed archive chunks and imports the result.

Control flow and state: `BUFFER_SIZE` is 1 MiB. Download cleanup closes the output stream and releases the zero-copy request. Upload lifecycle is delegated to the request handler, which also releases per-message zero-copy buffers.

Dependencies and integration: instantiated by `ReplicationServer` with `OnDemandContainerReplicationSource` and `ContainerImporter`. It depends on generated `IntraDatanodeProtocolServiceGrpc` methods and Ratis zero-copy marshalling.

Risks and test signals: zero-copy release must happen even on errors, and server errors must translate to gRPC failures without leaking streams. Tests should cover download success, missing container error, compression conversion, zero-copy service descriptor replacement, upload handler creation, and cleanup when `source.copyData` throws.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/MeasuredReplicator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/MeasuredReplicator.java

Purpose: wraps a `ContainerReplicator` and publishes per-replicator metrics for queue time, runtime, success/failure count, and transferred bytes.

Important APIs and functions: the constructor registers this object with the default metrics system under `ContainerReplicator/<name>`. `replicate` records queue latency from task queued time, delegates replication, measures elapsed time, and updates success or failure gauges/counters based on final task status. `close` unregisters the metric source. Getter methods expose metric fields for tests.

Control flow and state: the wrapper does not alter task behavior or catch delegate exceptions; supervisor still owns exception handling around task execution. Metrics are updated only for `DONE` and `FAILED`, not `SKIPPED`.

Dependencies and integration: can wrap pull or push replicators before they are passed into `ReplicationTask`.

Risks and test signals: metrics registration names must be unique per name, and delegate exceptions may bypass metric updates if not caught upstream. Tests should verify success/failure accounting, transferred bytes on failure, queue-time increment, unregister behavior, skipped-task behavior, and duplicate registration handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/MeasuredReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/OnDemandContainerReplicationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/OnDemandContainerReplicationSource.java

Purpose: simple replication source that exports the current container to a tar stream on demand instead of prebuilding archives.

Important APIs and functions: `prepare` is a no-op. `copyData` resolves the container through `ContainerController`, throws `CONTAINER_NOT_FOUND` if absent, and delegates to `controller.exportContainer` with the container type, ID, destination stream, and `TarContainerPacker` configured for the requested compression.

Control flow and state: stateless apart from the controller reference. Every copy is generated fresh from current container files.

Dependencies and integration: used by `ReplicationServer` for pull downloads and can be passed to `PushReplicator` for source-side push streaming.

Risks and test signals: export consistency depends on the container's state and handler implementation. Tests should cover missing container result codes, compression propagation, output stream failure, and export of closed/quasi-closed/unhealthy containers according to controller policy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/OnDemandContainerReplicationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/PushReplicator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/PushReplicator.java

Purpose: implements push replication by streaming a local container archive directly to a target datanode.

Important APIs and functions: `replicate(ReplicationTask)` reads the target from the task, resolves configured compression, calls `source.prepare`, opens an upload stream through `ContainerUploader`, wraps it in `CountingOutputStream`, copies source data into it, waits for the upload future, records byte count, and marks the task done or failed.

Control flow and state: the method is synchronous and executor-thread blocking. The upload future captures remote import success or failure. Cleanup closes the output stream with `IOUtils.cleanupWithLogger`, even if the stream was already closed by an error.

Dependencies and integration: used for `ReplicateContainerCommand` instances carrying a target datanode. It depends on `ContainerReplicationSource`, `ContainerUploader`, compression config, and `ReplicationTask` status fields.

Risks and test signals: future wait can block if the response observer never completes. Tests should cover target missing/null handling, source copy exceptions, upload open failures, remote error completion, transferred byte accounting on partial failure, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/PushReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationServer.java

Purpose: owns the dedicated datanode-to-datanode gRPC server used for container replication.

Important APIs and functions: the constructor stores security, controller, importer, port, builds a bounded fixed-size `ThreadPoolExecutor`, and calls `init`. `init` creates a `GrpcReplicationService`, installs a tracing interceptor, configures max inbound message size, attaches the executor, and optionally configures mutual TLS with key/trust managers, protocols, ciphers, and provider. `start` starts the gRPC server and records the actual bound port. `stop` shuts down executor and server with bounded waits. `setPoolSize` dynamically resizes the executor. Nested `ReplicationConfig` defines stream limit, queue limit, port, and out-of-service scaling factor with validation.

Control flow and state: server lifecycle is explicit; `OzoneContainer.start` starts it before exposing the port in `DatanodeDetails`. The executor queue is bounded by config, and rejected tasks rely on gRPC/executor behavior. Out-of-service scaling is exposed to supervisor and other components via `ReplicationConfig`.

Dependencies and integration: integrates `ContainerController`, `ContainerImporter`, `OnDemandContainerReplicationSource`, gRPC Netty, Ratis tracing, and datanode security.

Risks and test signals: TLS misconfiguration fails server construction, and shutdown order can leave active streams interrupted. Tests should cover plaintext/TLS init, dynamic port binding, queue limit behavior, invalid config clamping, pool resizing, and graceful stop under active streams.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisor.java

Purpose: schedules, deduplicates, prioritizes, executes, and meters datanode replication tasks.

Important APIs and functions: `Builder` creates default config, clock, and a `ThreadPoolExecutor` backed by `PriorityBlockingQueue`. `addTask` checks queue capacity, initializes metric counters, adds task uniqueness to `inFlight`, increments queue counters, and submits a `TaskRunner`. `nodeStateUpdated` and `setReplicationMaxStreams` resize executor and queue limits, scaling for maintenance/decommission states. Getter methods expose in-flight counts, queue size, max streams, and counters by metric name. `TaskRunner.run` enforces deadline, datanode operational state, and SCM term checks, then sets status to `IN_PROGRESS`, calls `task.runTask`, updates success/failure/skipped/timeout counters, latency metrics, and removes in-flight state.

Control flow and state: `inFlight` is a concurrent set keyed by task equality, preventing duplicate queued/running tasks. Low-priority tasks are submitted but excluded from command queue size counters. Metrics maps are lazily initialized per task metric name. `maxQueueSize` changes when datanode state changes.

Dependencies and integration: consumes `StateContext`, `DatanodeConfiguration`, `ReplicationConfig`, datanode operational state, SCM leader term, and Hadoop metrics rates. It is the execution gate for replication and related reconstruction tasks.

Risks and test signals: early returns in `TaskRunner` leave task status as queued but still decrement counters in finally. Priority ordering depends on `TaskRunner.compareTo`. Tests should cover duplicate task suppression, low-priority exclusion, deadline expiry, out-of-service skip/run flags, stale SCM term skip, exception handling, counter balance, resize order, and latency metric creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorMetrics.java

Purpose: exposes `ReplicationSupervisor` counters and gauges through Hadoop Metrics2.

Important APIs and functions: `create` registers a new metrics source in the default metrics system. `unRegister` removes it. `getMetrics` emits total in-flight, queued, requested, success, failure, timeout, skipped, and max-stream gauges. It also iterates `ReplicationSupervisor.getMetricsMap()` to publish per-task metric families and emits per-task-class in-flight gauges.

Control flow and state: the class is a thin adapter over live supervisor getter methods. It has no internal counters.

Dependencies and integration: used by datanode metrics registration for replication visibility. It depends on Metrics2 `MetricsCollector`, `Interns`, and `DefaultMetricsSystem`.

Risks and test signals: metric name construction is dynamic and can collide if metric names are reused poorly. Tests should verify registration/unregistration, empty metrics map behavior, per-type gauges, and values matching supervisor counters after success, failure, skipped, and timeout runs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationTask.java

Purpose: concrete replication task created from an SCM `ReplicateContainerCommand`.

Important APIs and functions: the main constructor extracts container ID, deadline, term, priority, sources, target, and debug string from the command, and allows execution on out-of-service datanodes when the command has a target, which identifies push replication. `equals` and `hashCode` deduplicate by container ID and target. `runTask` delegates to the injected `ContainerReplicator`. Accessors expose sources, transferred bytes, metric name/description, and target.

Control flow and state: transferred bytes are mutable and appended to `toString` once positive. Pull tasks usually have sources only; push tasks have a target and relaxed in-service restriction.

Dependencies and integration: scheduled by `ReplicationSupervisor` and executed by pull/push replicator implementations. The command object is from `org.apache.hadoop.ozone.protocol.commands`.

Risks and test signals: deduplication treats pull replications of the same container as equal because target is null, but allows separate target-specific push tasks. Tests should cover equality semantics, out-of-service flag for target commands, transferred byte logging, metric names, and delegate invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerOutputStream.java

Purpose: adapts push-replication archive writes to `SendContainerRequest` gRPC messages.

Important APIs and functions: the constructor stores compression and optional total container size in addition to inherited stream state. `sendPart` builds a request with container ID, data, current offset, and compression. It sets the size field only on the first message when a size is available.

Control flow and state: offset and byte counting are inherited from `GrpcOutputStream`. This class does not set an EOF marker; completion is represented by closing the gRPC request stream.

Dependencies and integration: returned by `GrpcContainerUploader.startUpload` and consumed by `PushReplicator`.

Risks and test signals: target-side space reservation depends on first-message size propagation. Tests should verify offset values, size on first chunk only, no size when unknown, compression proto field, multi-buffer splitting, and behavior when first write is larger than the buffer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerRequestHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerRequestHandler.java

Purpose: receives a pushed container archive over gRPC, writes it to a temporary tarball on a selected volume, and imports it when the upload completes.

Important APIs and functions: `onNext` validates message offset, rejects existing/in-progress imports, initializes container ID, compression, reservation size, volume, temp directory, tar path, and output stream on the first message, writes data, advances `nextOffset`, and releases zero-copy buffers. `onError` closes and deletes the partial tarball, reports the gRPC error, and releases committed bytes. `onCompleted` closes output, calls `ContainerImporter.importContainer`, sends an empty success response, completes the response stream, or deletes the tarball and reports an error on import failure.

Control flow and state: `containerId == -1` identifies the uninitialized state. `nextOffset` enforces in-order chunks. `spaceToReserve` is based on the first request's size field when present. Volume committed bytes are decremented in both error and completion paths.

Dependencies and integration: created by `GrpcReplicationService.upload`; relies on `ContainerImporter`, `ContainerUtils`, `HddsVolume`, and Ratis zero-copy marshaller.

Risks and test signals: recursive `onError` from `onNext` can interact with later stream callbacks, and `onCompleted` with no parts returns without completing the response. Tests should cover offset mismatch, duplicate import rejection, first-message size reservation, partial file cleanup, successful import response, marshaller release, and committed-byte balance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerRequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SimpleContainerDownloader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SimpleContainerDownloader.java

Purpose: sequential pull-replication downloader that tries source datanodes one at a time until a container archive download succeeds.

Important APIs and functions: `getContainerDataFromReplicas` defaults a null download directory to the JVM temp `container-copy` directory, shuffles sources, creates a `GrpcReplicationClient` for each datanode, starts `download`, waits for the future, returns the path on first success, and closes each client in a finally block. `shuffleDatanodes`, `createReplicationClient`, and `downloadContainer` are visible for testing. `close` is a no-op.

Control flow and state: the implementation is stateless apart from security/certificate configuration. Interrupted downloads log the error, restore interrupt status, and continue through loop handling as coded.

Dependencies and integration: used by `DownloadAndImportReplicator`, relying on `GrpcReplicationClient` and datanode replication ports.

Risks and test signals: blocking `future.get()` can wait indefinitely if the stream stalls. Tests should cover shuffled retry order, all-sources failure returning null, client close per attempt, default download directory, interrupt status preservation, and partial output cleanup delegated to `StreamDownloader`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SimpleContainerDownloader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/package-info.java

Purpose: documents the `org.apache.hadoop.ozone.container.replication` package as the implementation area for container data replication between datanodes.

Important APIs and types: no executable code is present. The package contains pull and push replication strategies, gRPC transport, source/import abstractions, supervisor scheduling, and metrics.

Control flow and state: none locally.

Dependencies and integration: consumed by Javadoc/package metadata only. It provides context for datanode server-to-server copy infrastructure.

Risks and test signals: no runtime risk. Package declaration should remain aligned with the source tree.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerDestination.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerDestination.java

Purpose: maps streamed logical file names into a single destination root directory.

Important APIs and functions: the constructor stores the root `Path`. `mapToDestination(String name)` resolves the provided name as a path below that root.

Control flow and state: there is no validation or normalization beyond `Path.resolve(Paths.get(name))`. The root field is instance state and not mutated after construction in normal use.

Dependencies and integration: used by `DirstreamClientHandler` through the `StreamingDestination` interface.

Risks and test signals: logical names containing absolute paths or `..` may escape the intended destination depending on platform path semantics. Tests should cover nested names, root resolution, absolute-name handling, and whether callers sanitize server-provided logical names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerDestination.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerSource.java

Purpose: implements `StreamingSource` by walking a subdirectory under a root and returning all regular files for streaming.

Important APIs and functions: `getFilesToStream(String id)` resolves `root/id`, walks the tree with `Files.walk`, filters regular files, and maps each file's logical name to `root.relativize(path).toString()`. IO failures are wrapped in `StreamingException`.

Control flow and state: state is only the root path. The returned map has no defined ordering because it is a `HashMap`.

Dependencies and integration: consumed by `DirstreamServerHandler`, which turns the returned map into a list and streams each entry.

Risks and test signals: nondeterministic order may affect reproducibility, and invalid IDs may escape root if not sanitized. Tests should cover recursive files, empty directories, symlinks according to `Files.walk` behavior, IO errors, interrupted signature compatibility, and path traversal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamClientHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamClientHandler.java

Purpose: Netty inbound handler that receives the custom directory-stream protocol and writes files to a `StreamingDestination`.

Important APIs and functions: `channelRead` casts to `ByteBuf`, calls `doRead`, and releases the buffer. `doRead` alternates between header mode and data mode. Headers are newline-terminated strings in the form `<size> <filename>`; the handler parses size, maps filename to a destination path, creates parent directories, opens a `RandomAccessFile`, and then copies exactly `size` bytes to its `FileChannel`. Extra bytes in a buffer after a file completes are processed recursively. `isAtTheEnd` checks whether the last header equals server `END_MARKER`.

Control flow and state: state fields track header/data mode, accumulated header text, open output file/channel, and remaining bytes. Channel unregister and exception paths close open files.

Dependencies and integration: used by `StreamingClient`. It relies on `DirstreamServerHandler.END_MARKER` and Netty buffer reference counting.

Risks and test signals: the stated protocol comment disagrees with parsing order in one place; actual parsing is size then filename. Tests should cover split headers, multiple files in one buffer, zero-size end marker, malformed headers, destination parent null, partial transfer close, and resource cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamClientHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamServerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamServerHandler.java

Purpose: Netty server handler for the custom directory-stream protocol, reading a requested ID and writing a sequence of file headers and file contents.

Important APIs and functions: `channelRead` reads the first newline-terminated request ID, asks `StreamingSource.getFilesToStream`, and calls `writeOneElement`. `writeOneElement` writes a header `<fileSize> <logicalName>\n`, then a Netty `ChunkedFile`, then either recursively streams the next entry or writes `END_MARKER` and closes the channel. `exceptionCaught` writes an `ERR:` line if possible and closes the channel.

Control flow and state: `headerProcessed` ensures only the first request header is interpreted. File writes are chained through `ChannelFuture` listeners to avoid sending the next file before the current file write is submitted/completed.

Dependencies and integration: installed by `StreamingServer` after `ChunkedWriteHandler`. It consumes `StreamingSource` and produces the format parsed by `DirstreamClientHandler`.

Risks and test signals: empty source maps cause `entriesToWrite.get(0)` failure. Request header parsing for fragmented headers is weak because it does not accumulate partial data across reads. Tests should cover empty directories, fragmented request ID, multiple files, chunked write failure, error response formatting, and end marker newline expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamServerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingClient.java

Purpose: Netty client wrapper that requests a stream ID and stores received files through a `StreamingDestination`.

Important APIs and functions: constructors configure a `Bootstrap`, `NioEventLoopGroup`, receive buffer, keepalive, optional TLS handler, `StringEncoder`, and `DirstreamClientHandler`. `stream(String)` uses a default 200 second timeout. `stream(String, long, TimeUnit)` connects, writes `id + "\n"`, waits for channel close, verifies the handler saw the end marker, and throws `StreamingException` on timeouts or interruption. `close` shuts down the event loop group.

Control flow and state: a single handler instance is tied to the client instance, so repeated streams reuse handler state. The channel is closed in finally if still active.

Dependencies and integration: pairs with `StreamingServer` and `DirstreamServerHandler`. Optional Netty `SslContext` supports TLS.

Risks and test signals: the large fixed event-loop size and reused handler state are notable. Tests should cover success, write timeout, close timeout, missing end marker, interrupted wait, TLS pipeline insertion, repeated stream calls, and close cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingDestination.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingDestination.java

Purpose: destination-side mapping interface for directory streaming.

Important APIs and types: `mapToDestination(String name)` returns the local `Path` where the logical streamed file name should be written.

Control flow and state: none in the interface.

Dependencies and integration: implemented by `DirectoryServerDestination` and called by `DirstreamClientHandler` before creating output files.

Risks and test signals: implementations define security boundaries for streamed filenames. Tests should check path normalization, parent existence creation, and rejection or handling of unsafe logical names in concrete implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingDestination.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingException.java

Purpose: unchecked exception type for the custom streaming package.

Important APIs and functions: constructors wrap an `InterruptedException`, wrap a message plus `IOException`, or carry a message string.

Control flow and state: no state beyond `RuntimeException` fields. Callers convert checked IO/interruption conditions into this unchecked type at API boundaries.

Dependencies and integration: thrown by `DirectoryServerSource`, `StreamingClient`, and `StreamingServer`.

Risks and test signals: because it is unchecked, callers must know which streaming operations may fail at runtime. Tests should verify cause propagation, interrupted status restoration by callers, and message content for timeout and incomplete-stream cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingServer.java

Purpose: Netty server wrapper for raw directory streaming.

Important APIs and functions: constructors store source, port, and optional TLS context. `start` creates boss and worker `NioEventLoopGroup`s, configures a `ServerBootstrap` with backlog 100, optional TLS handler, `ChunkedWriteHandler`, and `DirstreamServerHandler`, binds the port, and records the actual local port. `stop` gracefully shuts down both event loops. `close` delegates to `stop`.

Control flow and state: server groups are initialized on `start`; no guard prevents multiple starts or stopping before start. The bound port may differ from requested port when zero is used.

Dependencies and integration: hosts `DirstreamServerHandler` and serves `StreamingClient` instances. It is separate from the gRPC replication server and is a lower-level raw file stream utility.

Risks and test signals: fixed event-loop sizes and missing lifecycle guards can waste resources or throw null pointer errors. Tests should cover dynamic port binding, TLS pipeline, start/stop lifecycle, interrupted bind, multiple concurrent clients, and stop before start behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingSource.java

Purpose: source-side mapping interface for directory streaming.

Important APIs and types: `getFilesToStream(String id)` returns a map from logical stream names to real local file paths and may throw `InterruptedException`.

Control flow and state: none in the interface.

Dependencies and integration: implemented by `DirectoryServerSource` and consumed by `DirstreamServerHandler`.

Risks and test signals: map ordering affects stream order, and implementations must choose how to handle unsafe IDs. Tests should cover empty maps, deterministic order where required, interruption propagation, and invalid ID handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/package-info.java

Purpose: documents the package as a streaming API with client and server classes for moving raw binary data.

Important APIs and types: no executable declarations beyond the package. The package contains Netty client/server wrappers, handlers, and source/destination interfaces.

Control flow and state: none locally.

Dependencies and integration: Javadoc/package metadata only.

Risks and test signals: no runtime risk; package declaration should remain path-aligned.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ContainerTableSchemaFinalizeAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ContainerTableSchemaFinalizeAction.java

Purpose: upgrade-finalization action that migrates witnessed-container metadata from a previous table definition into the current protobuf-value table.

Important APIs and functions: annotated with `@UpgradeActionHdds(feature = WITNESSED_CONTAINER_DB_PROTO_VALUE, component = DATANODE)`. `execute` obtains the datanode's `WitnessedContainerMetadataStore`, gets the previous `containerIdsTable` and current `CONTAINER_CREATE_INFO_TABLE_DEF`, truncates the current table, iterates previous entries, writes them into the current table using a batch operation, and commits. `truncateCurrentTable` computes first and last keys and uses `deleteRange` plus a final delete for the exclusive end.

Control flow and state: the action is intended to be idempotent after crashes; it clears current data before copying from the previous table. Batch commit is the persistence boundary for the migration copy.

Dependencies and integration: invoked by `DataNodeUpgradeFinalizer` through HDDS layout feature actions. It depends on RocksDB table APIs, `ContainerID`, and witnessed-container metadata definitions.

Risks and test signals: delete range semantics and key ordering are important. Tests should cover empty current table, single-entry current table, multi-entry truncation, previous-table copy, crash/retry idempotence, and codec/RocksDB exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ContainerTableSchemaFinalizeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DataNodeUpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DataNodeUpgradeFinalizer.java

Purpose: datanode-specific layout upgrade finalizer.

Important APIs and functions: the constructor accepts an `HDDSLayoutVersionManager`. `preFinalizeUpgrade` verifies finalization is safe, resets state to `FINALIZATION_REQUIRED` and throws `PREFINALIZE_VALIDATION_FAILED` if not, otherwise moves to `FINALIZATION_IN_PROGRESS`. `canFinalizeDataNode` scans all containers and refuses finalization while any container is `OPEN` or `CLOSING`. `finalizeLayoutFeature` accepts only `HDDSLayoutFeature`, then delegates to `BasicUpgradeFinalizer` with the feature's datanode action and layout storage.

Control flow and state: finalization is gated on container closure, preventing layout transitions while active writes are still possible. Version manager state is the durable finalization cursor managed by the base finalizer.

Dependencies and integration: called by datanode upgrade handling in the state machine. It integrates container controller iteration, layout storage, HDDS feature actions, and Ozone upgrade exceptions.

Risks and test signals: failure to block open containers could corrupt layout migrations; overblocking could stall upgrades. Tests should cover open, closing, closed, quasi-closed, and unhealthy container states; non-HDDS feature rejection; state reset on failed precheck; and action invocation ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DataNodeUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV2FinalizeAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV2FinalizeAction.java

Purpose: finalize action for the first datanode schema-version feature.

Important APIs and functions: annotated for `DATANODE_SCHEMA_V2`. `execute` logs that new containers will use schema version 2 after finalization.

Control flow and state: no local state is changed in this action. The effective schema behavior is controlled elsewhere by `VersionedDatanodeFeatures.SchemaV2.chooseSchemaVersion`.

Dependencies and integration: invoked by HDDS upgrade finalization and indirectly affects future container creation policy through the layout version manager.

Risks and test signals: runtime risk is low because this action only logs. Tests should ensure the annotation binds to the correct feature and that schema selection changes when the layout feature becomes allowed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV2FinalizeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV3FinalizeAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV3FinalizeAction.java

Purpose: finalizes datanode volume layout for Schema V3, where container metadata moves to per-volume RocksDB stores.

Important APIs and functions: annotated for `DATANODE_SCHEMA_V3`. `execute` gets data and DB volume sets, locks the data volume set, creates a DB store for each `HddsVolume` lacking `dbParentDir`, unlocks, then checks `DatanodeConfiguration.getContainerSchemaV3Enabled`. If enabled, it calls `HddsVolumeUtil.loadAllHddsVolumeDbStore`.

Control flow and state: volume DB directory creation occurs regardless of the runtime schema-v3 enabled flag, while DB loading is skipped if the flag is disabled. The write lock protects volume metadata updates during store creation.

Dependencies and integration: used during layout finalization and interacts with `OzoneContainer` startup, which also loads stores when Schema V3 is finalized and enabled.

Risks and test signals: partial DB store creation and lock handling are key. Tests should cover null data volume set rejection, existing DB parent skip, DB volume set null behavior, disabled schema-v3 flag, load failure, and lock release on exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV3FinalizeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ScmHAFinalizeUpgradeActionDatanode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ScmHAFinalizeUpgradeActionDatanode.java

Purpose: finalizes datanode volume layout for SCM HA by ensuring cluster-ID paths exist, often through symlinks to older SCM-ID directories.

Important APIs and functions: annotated for `SCM_HA`. `execute` iterates data volumes under the volume-set write lock and calls `upgradeVolume` for `HddsVolume`s, failing the volume if upgrade returns false. `upgradeVolume` validates cluster ID, lists storage subdirectories, skips unformatted volumes, creates a symlink from `<volume>/<clusterID>` to the sole old directory when needed, accepts already-correct layouts, and rejects inconsistent multi-directory layouts without cluster ID.

Control flow and state: the upgrade mutates filesystem layout, not in-memory container state. It returns boolean success so callers can mark failed volumes for later handling.

Dependencies and integration: coordinated with `VersionedDatanodeFeatures.ScmHA.chooseContainerPathID` and `upgradeVolumeIfNeeded`.

Risks and test signals: symlink creation portability and inconsistent directory detection are high risk. Tests should cover null cluster ID, unformatted volume, one old SCM-ID directory, existing cluster-ID directory, multi-directory with/without cluster ID, IO failure, and volume failure marking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ScmHAFinalizeUpgradeActionDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/UpgradeUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/UpgradeUtils.java

Purpose: small helper for creating datanode layout-version protobuf messages.

Important APIs and functions: `defaultLayoutVersionProto` sets both metadata and software layout versions to `HDDSLayoutVersionManager.maxLayoutVersion()`. `toLayoutVersionProto(int mLv, int sLv)` builds a proto with explicit metadata and software layout versions.

Control flow and state: stateless final utility class with private constructor.

Dependencies and integration: used in protocol registration/version exchange and finalize-new-layout commands where datanodes and SCM communicate layout versions.

Risks and test signals: risk is low, but incorrect defaults can affect upgrade negotiation. Tests should verify max-version defaulting, explicit version fields, and compatibility with `StorageContainerDatanodeProtocolProtos.LayoutVersionProto`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/UpgradeUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/VersionedDatanodeFeatures.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/VersionedDatanodeFeatures.java

Purpose: centralizes datanode behavior switches controlled by finalized HDDS layout features.

Important APIs and functions: `initialize` stores the process-wide `HDDSLayoutVersionManager`; `isFinalized` returns true when no manager is installed, or when the feature is allowed. `SchemaV2.chooseSchemaVersion` returns schema v2 after `DATANODE_SCHEMA_V2`, otherwise v1. `ScmHA.chooseContainerPathID` chooses cluster ID after SCM HA finalization or if the cluster-ID directory already exists; otherwise it requires exactly one pre-finalization directory and returns that name. `ScmHA.upgradeVolumeIfNeeded` invokes SCM HA volume upgrade when finalized but the cluster-ID path is missing. `SchemaV3.chooseSchemaVersion` returns schema v3 only when the feature is finalized and the datanode config enables it, otherwise defers to Schema V2.

Control flow and state: `versionManager` is static mutable global state, with null treated as latest version for tests. Feature methods are pure except `upgradeVolumeIfNeeded`, which may mutate the filesystem through the SCM HA action.

Dependencies and integration: used by container creation, volume path selection, upgrade actions, and `OzoneContainer` startup.

Risks and test signals: global manager state can leak between tests. Tests should reset/initialize manager, verify pre/post-finalization schema choices, SCM HA path selection for cluster/SCM directories, invalid multi-directory errors, disabled Schema V3 fallback, and upgrade-on-demand behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/VersionedDatanodeFeatures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/package-info.java

Purpose: documents the package as containing container-service upgrade-related classes.

Important APIs and types: no executable declarations. The package contains datanode layout finalizers, per-feature finalize actions, and feature-gated utility methods.

Control flow and state: none locally.

Dependencies and integration: Javadoc/package metadata only.

Risks and test signals: no runtime risk; package declaration should remain source-tree aligned.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/package-info.java

Purpose: package-level documentation for generic Ozone-specific classes under `org.apache.hadoop.ozone`.

Important APIs and types: no runtime declarations are present in this file.

Control flow and state: none locally.

Dependencies and integration: used by Javadoc and package metadata. This source tree also includes container-service protocol and upgrade classes under subpackages.

Risks and test signals: no runtime risk. Build/Javadoc checks should ensure the package statement remains correct.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/ReconDatanodeProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/ReconDatanodeProtocol.java

Purpose: protocol marker for datanode communication with Recon, reusing the SCM datanode protocol shape while binding a Recon Kerberos principal.

Important APIs and types: the interface extends `StorageContainerDatanodeProtocol` without adding methods. `@KerberosInfo` points to `OZONE_RECON_KERBEROS_PRINCIPAL_KEY`, and `@InterfaceAudience.Private` marks it internal.

Control flow and state: none locally.

Dependencies and integration: used by RPC/protocol wiring where Recon receives datanode reports and heartbeats using SCM-compatible protobuf messages but distinct service authentication.

Risks and test signals: the main risk is security principal mismatch. Tests should verify RPC binding uses Recon's principal and that all inherited protocol methods remain compatible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/ReconDatanodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerDatanodeProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerDatanodeProtocol.java

Purpose: RPC interface for datanode-to-SCM communication using protobuf request/response types.

Important APIs and functions: `versionID` is 1. `getVersion` returns SCM version information. `sendHeartbeat` sends datanode heartbeat data and returns SCM commands, allowing `TimeoutException`. `register` registers a datanode with extended details, node report, full container report, pipeline report, and layout version info, returning registration response data.

Control flow and state: interface only; implementations own registration, heartbeat state, command generation, and version negotiation.

Dependencies and integration: annotated with SCM Kerberos principal and used by datanode state machine endpoint tasks. It carries `NodeReportProto`, `ContainerReportsProto`, `PipelineReportsProto`, and `LayoutVersionProto` built by `OzoneContainer` and related services.

Risks and test signals: RPC compatibility and protobuf evolution are key. Tests should cover version response conversion, heartbeat timeouts, registration with layout versions, security principal configuration, and compatibility with Recon's inherited interface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerDatanodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerNodeProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerNodeProtocol.java

Purpose: SCM-side node protocol abstraction for datanode state, registration, version exchange, heartbeat processing, and registration checks.

Important APIs and functions: `getVersion` returns a `VersionResponse` from an SCM version request. `register` accepts `DatanodeDetails`, node report, pipeline report, and layout version, returning a `RegisteredCommand`. `processHeartbeat` has a test-only default overload without queue report and the main overload with `CommandQueueReportProto`, returning a list of `SCMCommand`s. `isNodeRegistered` checks registration state.

Control flow and state: interface only. Implementations own node registry state, command queues, and heartbeat side effects.

Dependencies and integration: bridges datanode RPC/protobuf inputs to higher-level SCM command objects. The command queue report integrates with datanode-side supervisor queue metrics.

Risks and test signals: heartbeat command generation must be idempotent and registration-aware. Tests should cover unregistered nodes, queue report influence, version response content, layout-version registration, and default overload compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerNodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/VersionResponse.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/VersionResponse.java

Purpose: higher-level wrapper for SCM software version responses and key/value metadata.

Important APIs and functions: constructors accept version and optional values map. `newBuilder` creates a builder. `getFromProtobuf` converts `SCMVersionResponseProto` key list into a map. `put` and `Builder.addValue` reject duplicate keys. `getProtobufMessage` serializes the version and values to `KeyValue` protobufs. `getValue` reads a value by key. Builder supports `setVersion`, `addValue`, and `build`.

Control flow and state: `values` is mutable in the main object via `put`; builder stores values until build, but passes the map into the constructed response without defensive copy.

Dependencies and integration: used by `StorageContainerNodeProtocol.getVersion` and protocol conversion code for datanode/SCM version negotiation.

Risks and test signals: duplicate handling and map mutability can affect callers. Tests should cover protobuf round trip, duplicate key rejection in both builder and response, missing values, builder mutation after build, and deterministic expectations where value ordering is irrelevant.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/VersionResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CloseContainerCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CloseContainerCommand.java

Purpose: SCM command asking a datanode to close a container in a specific pipeline, optionally forcefully.

Important APIs and functions: constructors store container command ID, `PipelineID`, and force flag. `getType` returns `closeContainerCommand`. `getProto` serializes container ID, command ID, pipeline ID, and force. `getFromProtobuf` reconstructs the command. Accessors expose container ID, pipeline ID, and force. `equals` and `hashCode` compare container, pipeline, and force.

Control flow and state: immutable except inherited SCM command fields and the local force flag set at construction. `toString` includes encoded token, term, deadline, container, pipeline, and force for diagnostics.

Dependencies and integration: sent from SCM to datanodes through heartbeat command responses and handled by datanode pipeline/container logic.

Risks and test signals: protobuf conversion uses `cmdId` as the constructor container ID, matching `getProto` where both are set to `getId`. Tests should cover round trip, force flag, equality, token/term/deadline inherited fields, and pipeline ID conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CloseContainerCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ClosePipelineCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ClosePipelineCommand.java

Purpose: SCM command requesting a datanode to close a Ratis pipeline.

Important APIs and functions: constructors create a new command ID or restore one from protobuf. `getType` returns `closePipelineCommand`. `getProto` serializes command ID and pipeline ID. `getFromProtobuf` reconstructs the command. `getPipelineID` exposes the target pipeline.

Control flow and state: state is the immutable pipeline ID plus inherited SCM command metadata. `toString` includes token, term, deadline, and pipeline.

Dependencies and integration: consumed by datanode xceiver/Ratis pipeline management and transported via SCM heartbeat commands.

Risks and test signals: risk is mostly serialization compatibility. Tests should cover proto round trip, null proto rejection, command ID preservation, pipeline ID conversion, and diagnostic string content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ClosePipelineCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandForDatanode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandForDatanode.java

Purpose: event payload wrapper pairing an `SCMCommand` with its intended datanode destination.

Important APIs and functions: constructors accept either `DatanodeDetails` or `DatanodeID` plus a generic `SCMCommand<T>`. `getDatanodeId` and `getCommand` expose fields. `getId` implements `IdentifiableEventPayload` by returning the command ID.

Control flow and state: immutable wrapper with no side effects.

Dependencies and integration: used in SCM event pipelines where commands are routed to a specific datanode. Generic bound requires protobuf `Message` command payloads.

Risks and test signals: command ID is used as event identity, so duplicate command IDs can collide. Tests should cover construction from details and ID, event ID forwarding, generic command access, and string representation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandForDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandStatus.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandStatus.java

Purpose: represents datanode execution status for an SCM command.

Important APIs and functions: fields store command type, command ID, protobuf status enum, and optional message. `markAsExecuted` and `markAsFailed` update status. `getFromProtoBuf` builds a new status from protobuf. `getProtoBufMessage` serializes fields, including message only when non-null. Nested `CommandStatusBuilder` provides fluent construction.

Control flow and state: status is mutable after construction, while type/cmdId/message are only changed through builder before build. The `getFromProtoBuf` method is an instance method even though it behaves like a converter.

Dependencies and integration: used in datanode heartbeat command status reporting, with `DeleteBlockCommandStatus` extending it for block deletion acknowledgements.

Risks and test signals: null required fields can produce invalid protobuf builders. Tests should cover executed/failed transitions, message omission, protobuf round trip, builder defaults, and subclass override behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CreatePipelineCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CreatePipelineCommand.java

Purpose: SCM command asking datanodes to create a pipeline with specified replication type, factor, members, and priority list.

Important APIs and functions: constructors build a command with default Ratis priority list when datanode count matches `XceiverServerRatis.getDefaultPriorityList`, with all low priorities otherwise, or with a suggested leader assigned high priority. The protobuf constructor restores command ID and priority list. `getProto` serializes pipeline ID, type, factor, datanodes, and priorities. Accessors expose pipeline, node list, priority list, replication type, and factor.

Control flow and state: priority list is initialized at construction and then exposed directly. `toString` includes inherited command metadata and all pipeline creation fields.

Dependencies and integration: consumed by datanode xceiver server setup and sent from SCM during pipeline allocation.

Risks and test signals: priority list length must match datanode list length. Tests should cover default priority selection, suggested leader high priority, protobuf round trip, datanode conversion, non-standard replication factors, and list mutability exposure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CreatePipelineCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlockCommandStatus.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlockCommandStatus.java

Purpose: specialized command status carrying block deletion acknowledgement details.

Important APIs and functions: constructor adds optional `ContainerBlocksDeletionACKProto` to the base command status. `setBlocksDeletionAck` updates the acknowledgement. `getFromProtoBuf` uses the nested builder to restore status plus block deletion ack. `getProtoBufMessage` serializes base status fields and includes block deletion ack and message when present. `DeleteBlockCommandStatusBuilder` extends the base builder with `setBlockDeletionAck`.

Control flow and state: ack is mutable after construction. Other status fields are inherited from `CommandStatus`.

Dependencies and integration: used when datanodes report results of `DeleteBlocksCommand` transactions back to SCM.

Risks and test signals: ack omission can lose per-transaction deletion results. Tests should cover proto round trip with and without ack, message propagation, status transitions inherited from base class, and builder covariance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlockCommandStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlocksCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlocksCommand.java

Purpose: SCM command instructing a datanode to delete blocks represented by one or more deleted-block transactions.

Important APIs and functions: constructors accept transaction lists and optionally restore command ID for protobuf conversion. `blocksTobeDeleted` returns the list. `getType` returns `deleteBlocksCommand`. `getProto` serializes command ID and all transactions. `getFromProtobuf` restores from `DeleteBlocksCommandProto`. `toString` emits transaction IDs, container IDs, local ID counts, and counts.

Control flow and state: the transaction list is stored directly and can be mutable depending on caller list.

Dependencies and integration: sent by SCM based on deleted-block log processing and acknowledged through `DeleteBlockCommandStatus`.

Risks and test signals: mutable transaction lists and large diagnostic strings are notable. Tests should cover empty and multi-transaction round trips, command ID preservation, toString formatting without trailing separators, and list mutation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlocksCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteContainerCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteContainerCommand.java

Purpose: SCM command telling a datanode to delete a container, optionally forcefully and for a specific replica index.

Important APIs and functions: constructors accept raw container ID or `ContainerID` and force flag. `setReplicaIndex` mutates the replica index, defaulting to zero. `getType` returns `deleteContainerCommand`. `getProto` serializes command ID, container ID, force, and replica index. `getFromProtobuf` restores container ID, force, and optional replica index. Accessors expose container ID, force, and replica index.

Control flow and state: unlike many commands, local `containerId` is separate from inherited command ID. `toString` includes inherited metadata and deletion fields.

Dependencies and integration: consumed by datanode container deletion handlers and SCM replica management.

Risks and test signals: protobuf restoration does not preserve `cmdId` into inherited ID because the constructor does not accept it. Tests should verify whether that is intentional, plus force behavior, replica index optionality, container ID round trip, and command ID semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteContainerCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/FinalizeNewLayoutVersionCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/FinalizeNewLayoutVersionCommand.java

Purpose: SCM command asking a datanode to finalize or process a new layout version.

Important APIs and functions: constructors set the finalize flag, `LayoutVersionProto`, and optionally command ID. `getType` returns `finalizeNewLayoutVersionCommand`. `getProto` serializes finalize flag, command ID, and datanode layout version. `getFromProtobuf` restores all fields. `toString` includes inherited command metadata plus finalize flag and layout info.

Control flow and state: local state is the boolean finalize flag and layout proto. There are no accessors in this file beyond protobuf/toString, so consumers likely use the proto form or inherited command handling.

Dependencies and integration: used during SCM-driven datanode upgrade finalization, tying into `DataNodeUpgradeFinalizer` and layout-version reporting.

Risks and test signals: command compatibility depends on correct layout proto fields. Tests should cover protobuf round trip, command ID preservation, finalize true/false behavior, null layout handling, and datanode upgrade command execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/FinalizeNewLayoutVersionCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconcileContainerCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconcileContainerCommand.java

Purpose: SCM command instructing a datanode to reconcile a container replica with peer datanodes.

Important APIs and functions: the constructor uses container ID as command ID so only one reconciliation for a container should be active. `getType` returns `reconcileContainerCommand`. `getProto` serializes container ID and peer datanode protos. `getFromProtobuf` restores peers into a set, or an empty set if none are present. Accessors expose peer datanodes and container ID. Equality and hash code compare only container ID.

Control flow and state: peer set is stored directly and can be mutable depending on the caller. Deduplication ignores peer changes for the same container.

Dependencies and integration: used with `ContainerController.reconcileContainer` and datanode/SCM command transport.

Risks and test signals: equality ignoring peers is intentional for one-at-a-time reconciliation but can suppress updated peer sets. Tests should cover proto round trip, empty peer list, equality semantics, command ID/container ID identity, and peer datanode conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconcileContainerCommand.java -->
