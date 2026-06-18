# subset-b-007995 Research

Grouped source research for Apache Ozone datanode endpoint state transitions, standalone and Ratis container transport servers, container DB/storage utilities, and volume scan helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java

## Purpose

`RunningDatanodeState` is the active datanode state that drives communication with SCM and passive endpoints such as Recon. It belongs to the datanode state-machine layer and is responsible for scheduling the endpoint-specific handshake/registration/heartbeat tasks while the datanode remains in the RUNNING state. The complete 235-line file was read for this report.

## Important APIs, Types, and Functions

The class implements `DatanodeState` and exposes `onEnter()`, `onExit()`, `execute(ExecutorService)`, `await(long, TimeUnit)`, and `clear()`. Its constructor receives `ConfigurationSource`, `SCMConnectionManager`, and `StateContext`. `buildEndPointTask(EndpointStateMachine)` maps endpoint states to `VersionEndpointTask`, `RegisterEndpointTask`, or `HeartbeatEndpointTask`. `computeNextContainerState(List<Future<EndPointStates>>)` converts endpoint task results into the next `DatanodeStateMachine.DatanodeStates`.

## Control Flow

`execute` builds an `ExecutorCompletionService`, scans the current endpoints from `SCMConnectionManager`, and submits one wrapper task per endpoint with a bounded wait against the endpoint's own executor. `GETVERSION` also forces the parent datanode's next heartbeat time to now so registration can follow immediately. `await` polls for the number of endpoint tasks that were actually submitted, bounded by the caller's timeout, then asks `computeNextContainerState` whether any endpoint returned `SHUTDOWN`. Timeout exceptions from endpoint work are logged as warnings and do not alone force datanode shutdown.

## State and Persistence Behavior

This class owns transient scheduler state only: `ecs` and `executingEndpointCount`. It does not persist data. Endpoint transitions are stored in `EndpointStateMachine`, while datanode-level state changes go through `StateContext`. The endpoint count is captured during `execute` because endpoint membership can change through reconfiguration before `await`.

## Dependencies and Integration Points

It integrates with `SCMConnectionManager`, `StateContext`, `DatanodeStateMachine`, `EndpointStateMachine`, and the three endpoint task classes in `states.endpoint`. It also depends on endpoint executor services, heartbeat/recon heartbeat frequencies in `StateContext`, and parent datanode container/details accessors.

## Risks and Edge Cases

If `buildEndPointTask` returns null, the code treats the endpoint as shutdown and moves the whole datanode toward shutdown. The wrapper computes `heartbeatFrequency` for passive endpoints but uses `context.getHeartbeatFrequency()` in the actual timeout, which is worth regression coverage if passive/recon timing semantics are important. Partial completion in `await` means late endpoint futures are ignored for that cycle. Interrupted waits restore interrupt status but still return RUNNING unless a collected result requested shutdown.

## Test Signals

Useful tests cover task selection for GETVERSION/REGISTER/HEARTBEAT, endpoint timeout logging without shutdown, shutdown propagation from any endpoint result, endpoint-count stability when connection manager membership changes, immediate heartbeat scheduling after GETVERSION/reregister, and passive endpoint timing expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.container.common.states.datanode` as the package for datanode state transition classes. The complete 20-line file was read.

## Important APIs, Types, and Functions

The file exports no Java types or methods. It contains only the package-level Javadoc and the `package` declaration.

## Control Flow

There is no executable control flow. The documentation says this package contains files guiding datanode transitions from Init to Running to Shutdown.

## State and Persistence Behavior

No runtime state or persistence is owned by this file.

## Dependencies and Integration Points

The package-info participates in generated Javadocs and package-level organization for classes such as `RunningDatanodeState`.

## Risks and Edge Cases

The only risk is stale documentation if state names or transition ownership changes.

## Test Signals

Compile and Javadoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java

## Purpose

`HeartbeatEndpointTask` builds and sends a datanode heartbeat to an SCM endpoint, attaches queued reports/actions, and converts SCM heartbeat responses into datanode command queue work. It is the steady-state endpoint task for `EndpointStateMachine.EndPointStates.HEARTBEAT`. The complete 534-line file was read.

## Important APIs, Types, and Functions

The class implements `Callable<EndpointStateMachine.EndPointStates>`. Public construction is through `newBuilder()` and `Builder` setters for endpoint, config, datanode details, context, and optional layout version manager. `call()` is the main entry point. Helper methods include `addReports`, `addContainerActions`, `addPipelineActions`, `addQueuedCommandCounts`, `processResponse`, `processCommonCommand`, `processReregisterCommand`, and `putBackIncrementalReports`.

## Control Flow

`call` locks the endpoint, checks that datanode details were set, builds `SCMHeartbeatRequestProto` with datanode identity and layout version, then adds all currently available reports from `StateContext`, pending container and pipeline actions up to configured limits, and queued SCM command counts. It sends the heartbeat through `rpcEndpoint.getEndPoint().sendHeartbeat`. A successful response is validated against the datanode UUID, updates leader SCM term when present, decodes each SCM command by type, and enqueues command objects into `StateContext`. A `reregisterCommand` moves the endpoint back to GETVERSION and triggers an immediate heartbeat cycle. `IOException` does not drop incremental data: command status and incremental container reports are put back into context for retry.

## State and Persistence Behavior

The task keeps only per-call request state and configured max action counts. Heartbeat side effects are on `EndpointStateMachine` last-success/missed counters, `StateContext` report/action/command queues, SCM term tracking, and parent heartbeat timing. It does not write persistent storage directly.

## Dependencies and Integration Points

Dependencies include SCM datanode protocol protobufs, `HDDSLayoutVersionManager`, `StateContext`, datanode details, many `SCMCommand` subclasses, and configuration keys `HDDS_CONTAINER_ACTION_MAX_LIMIT` and `HDDS_PIPELINE_ACTION_MAX_LIMIT`. It integrates with report producers through `StateContext.getAllAvailableReports(address)` and with command executors through `context.addCommand`.

## Risks and Edge Cases

`addReports` uses protobuf descriptor full names to match arbitrary report messages to heartbeat fields, so schema changes require care. Unknown command types throw `IllegalArgumentException`, which can fail the task. Incremental report retry covers only command status and incremental container reports; cumulative reports are intentionally not put back. Builder validation misses a null `context` check even though the constructor and call path require it. Response UUID mismatch is a hard precondition failure.

## Test Signals

Tests should verify report descriptor placement, action limit behavior, queue-count serialization, command decoding for every switch branch, reregister state transition and immediate heartbeat trigger, incremental report put-back on IOException, term/token/deadline propagation to commands, and failure behavior for mismatched UUID or unknown command type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java

## Purpose

`RegisterEndpointTask` registers a datanode with SCM after version negotiation. It sends datanode identity plus full node/container/pipeline reports, validates SCM's registration response, updates local datanode network identity when SCM supplies it, and advances the endpoint to heartbeat. The complete 286-line file was read.

## Important APIs, Types, and Functions

The class is final and implements `Callable<EndpointStateMachine.EndPointStates>`. Main APIs are `newBuilder()`, the `Builder` setters, `call()`, `getDatanodeDetails()`, and `setDatanodeDetails(DatanodeDetails)`. The visible-for-testing constructor accepts `EndpointStateMachine`, `OzoneContainer`, `StateContext`, and optional `HDDSLayoutVersionManager`.

## Control Flow

`call` first shuts down the endpoint if datanode details are absent. It locks the endpoint, runs only when the endpoint state is REGISTER, builds layout version information, fetches full container, node, and pipeline reports from `OzoneContainer`, then calls `rpcEndPoint.getEndPoint().register(...)`. The response is validated for datanode UUID, nonblank cluster ID, and success error code. Optional hostname/IP and network name/location from SCM are copied into `DatanodeDetails`. The endpoint then moves to its next state, missed heartbeats are reset, and heartbeat frequency is configured differently for passive endpoints versus SCM endpoints.

## State and Persistence Behavior

The class does not write persistent storage directly. It mutates endpoint state, endpoint missed heartbeat counters, datanode identity fields, and heartbeat frequency settings in `StateContext`. Persistent volume/container state is only read through report generation.

## Dependencies and Integration Points

It depends on SCM datanode protocol protobufs, `EndpointStateMachine`, `OzoneContainer`, `DatanodeDetails`, `StateContext`, and `HDDSLayoutVersionManager`. The registration reports couple it to `ContainerController`, node report construction, and pipeline server reporting.

## Risks and Edge Cases

SCM response validation is intentionally strict and can fail the task via Ratis `Preconditions`. IOException is logged but leaves the endpoint in REGISTER for retry. The builder requires a config argument but the built task does not otherwise use it, so tests should preserve the builder contract if refactoring. A null context is checked but the error message says container is missing, which can obscure diagnostics.

## Test Signals

Tests should cover missing datanode shutdown, successful register response advancing to heartbeat, SCM-supplied hostname/IP/network update, passive and active heartbeat frequency configuration, invalid cluster ID/error code/UUID failures, and IOException retry semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java

## Purpose

`VersionEndpointTask` performs the initial SCM GETVERSION RPC for an endpoint. For active SCM endpoints it validates SCM/cluster IDs, checks and prepares datanode storage volumes, starts container services with the cluster ID, then advances the endpoint to registration. The complete 136-line file was read.

## Important APIs, Types, and Functions

The class implements `Callable<EndpointStateMachine.EndPointStates>`. Its constructor receives `EndpointStateMachine`, `ConfigurationSource`, and `OzoneContainer`. `call()` runs the version flow. `checkVolumeSet(MutableVolumeSet, String, String)` validates each `StorageVolume` through `StorageVolumeUtil.checkVolume`.

## Control Flow

`call` locks the endpoint and only executes when state is GETVERSION. It calls SCM `getVersion(null)`, stores the parsed `VersionResponse` in the endpoint, and for non-passive endpoints extracts `SCM_ID` and `CLUSTER_ID`. Both values are required. It checks DB volumes first, then HDDS data volumes, failing individual volumes through the `MutableVolumeSet` if consistency checks fail. If all volumes in a set fail, it throws `DiskOutOfSpaceException`. After volume checks, it starts `OzoneContainer` with the cluster ID and advances the endpoint to its next state. Disk out-of-space or bind failures put the endpoint into SHUTDOWN; IOExceptions are logged for retry.

## State and Persistence Behavior

This task can create/format volume `VERSION` files, working directories, cluster/SCM compatibility links, and temporary directories through `StorageVolumeUtil`. It also starts container services, mutates endpoint version and state, and resets missed heartbeat count.

## Dependencies and Integration Points

It integrates with SCM endpoint RPC, `VersionResponse`, `OzoneContainer`, both DB and data `MutableVolumeSet`s, `StorageVolumeUtil`, and `DiskChecker.DiskOutOfSpaceException`. Passive endpoints skip volume checks and container start.

## Risks and Edge Cases

Volume checks run under a write lock and may mark volumes failed while iterating. A completely failed volume set shuts down the endpoint. Passive endpoints do not validate local storage in this path. `Objects.requireNonNull` on SCM/cluster IDs turns missing version values into runtime failures rather than a protocol result.

## Test Signals

Tests should cover active versus passive behavior, successful volume formatting/start, failed individual volume handling, all-volumes-failed shutdown, GETVERSION skipped in other endpoint states, missing SCM/cluster values, and BindException/DiskOutOfSpace shutdown behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.container.common.states.endpoint` as the package containing RPC endpoint transition code. The complete 20-line file was read.

## Important APIs, Types, and Functions

No types or methods are defined; the artifact contains only Javadoc and the package declaration.

## Control Flow

No executable flow exists.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It documents the package holding `VersionEndpointTask`, `RegisterEndpointTask`, and `HeartbeatEndpointTask`.

## Risks and Edge Cases

The only risk is stale package documentation if endpoint transition ownership changes.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/package-info.java

## Purpose

This package descriptor identifies `org.apache.hadoop.ozone.container.common.states` as the common datanode-state package. The complete 19-line file was read.

## Important APIs, Types, and Functions

No Java types or executable functions are declared.

## Control Flow

There is no control flow.

## State and Persistence Behavior

No runtime state or persistence exists.

## Dependencies and Integration Points

The descriptor anchors package-level documentation for state interfaces and implementations below this package.

## Risks and Edge Cases

Documentation can become stale if state machine classes are moved.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java

## Purpose

`GrpcXceiverService` is the datanode gRPC service implementation for container command RPCs. It wraps `XceiverClientProtocolServiceGrpc`, replaces the streaming `send` request marshaller with a Ratis zero-copy marshaller, and dispatches each client command into `ContainerDispatcher`. The complete 160-line file was read.

## Important APIs, Types, and Functions

The class extends `XceiverClientProtocolServiceGrpc.XceiverClientProtocolServiceImplBase`. Main APIs are `bindServiceWithZeroCopy()`, static `addZeroCopyMethod(...)`, and overridden `send(StreamObserver<ContainerCommandResponseProto>)`. It owns a `ZeroCopyMessageMarshaller<ContainerCommandRequestProto>` and uses `RandomAccessFileChannel` for streaming block reads.

## Control Flow

`bindServiceWithZeroCopy` copies the generated service definition, replaces only the `send` method request marshaller, and leaves other methods unchanged. `send` returns a `StreamObserver` that processes each incoming `ContainerCommandRequestProto`. `ReadChunk` gets a release-supporting `DispatcherContext`; `ReadBlock` is routed to `dispatcher.streamDataReadOnly` with a reusable `RandomAccessFileChannel`; all other commands call `dispatcher.dispatch` and emit one response. Each request is released from the zero-copy marshaller in `finally`, and the dispatcher context release hook is invoked when present.

## State and Persistence Behavior

The service holds dispatcher and marshaller references. Each stream observer owns a closed flag and a block-file channel, closing it on error or completion. Persistence belongs to the dispatcher and lower container handlers, not this service.

## Dependencies and Integration Points

It integrates with generated datanode protobuf gRPC service bindings, Ratis shaded gRPC classes, `ZeroCopyMessageMarshaller`, `ContainerDispatcher`, `DispatcherContext`, and random-access file channels used for read streaming.

## Risks and Edge Cases

`context` is only created for `ReadChunk`, so `ReadBlock` streaming receives null context in this implementation. Any dispatcher exception closes the stream and propagates `onError`. Cancelled gRPC status is intentionally ignored in `onError`; other errors are logged. Missing release calls would leak zero-copy buffers, so the `finally` path is important.

## Test Signals

Tests should cover service definition replacement for `send`, zero-copy release on success and exception, read-block streaming path, normal dispatch path, cancelled error handling, idempotent close on concurrent terminal callbacks, and release-supported `ReadChunk` context behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java

## Purpose

`XceiverServerGrpc` is the standalone, non-Ratis datanode container transport server. It creates and manages the Netty gRPC server, TLS configuration, read executor pools, IPC port registration, standalone pipeline reporting, and direct dispatcher submission. The complete 267-line file was read.

## Important APIs, Types, and Functions

The class implements `XceiverServerSpi`. Public APIs include the constructor, `start()`, `stop()`, `getIPCPort()`, `getServerType()`, `submitRequest(...)`, `isExist(...)`, and `getPipelineReport()`. It owns `Server`, `ContainerDispatcher`, `ThreadPoolExecutor` for chunk reads, `EventLoopGroup`, `DatanodeDetails`, and port state.

## Control Flow

The constructor chooses a configured or random IPC port, sizes read executors from configured read threads per volume times storage directory count, chooses epoll or NIO Netty event loops, builds a `GrpcXceiverService`, installs tracing interceptors, sets message size and connection keepalive/idle policy, and optionally enables gRPC TLS from `CertificateClient`. `start` starts the server, resolves random port assignment, and records the standalone port in `DatanodeDetails`. `stop` shuts down read executors, server, and event loop group. `submitRequest` imports tracing context, dispatches the command directly, and throws `StorageContainerException` on non-success responses.

## State and Persistence Behavior

The class owns transport lifecycle state (`isStarted`, port fields, executor/event-loop objects). It does not persist container data directly; `ContainerDispatcher` owns command persistence.

## Dependencies and Integration Points

Dependencies include Ozone config keys, `DatanodeConfiguration`, `HddsServerUtil`, Netty/gRPC shaded Ratis classes, OpenTelemetry tracing, `SecurityConfig`, `CertificateClient`, and `ContainerDispatcher`.

## Risks and Edge Cases

If `poolSize / 10` becomes zero for event-loop construction, behavior depends on Netty constructors and config assumptions. TLS setup exceptions are logged but do not abort server construction, which can matter in secure deployments. `start` maps bind failures by inspecting the IOException message for `"Failed to bind to address"`. `stop` waits only five seconds for executors/server shutdown.

## Test Signals

Tests should verify random and fixed port assignment, datanode port registration, TLS-enabled builder behavior, submitRequest error translation, pipeline report identity, bind failure mapping to `BindException`, executor shutdown interrupt handling, and epoll/NIO branch configuration where practical.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java

## Purpose

`XceiverServerSpi` defines the common datanode container transport-server contract implemented by standalone gRPC and Ratis servers. The complete 96-line interface was read.

## Important APIs, Types, and Functions

Required methods are `start`, `stop`, `getIPCPort`, `getServerType`, `submitRequest`, `isExist`, and `getPipelineReport`. Default no-op or nullable extension points are `addGroup(pipelineId, peers)`, `addGroup(pipelineId, peers, priorityList)`, `removeGroup`, and `getStorageReport`.

## Control Flow

There is no implementation flow except default no-op methods. Concrete servers implement lifecycle, request submission, pipeline membership, and reporting.

## State and Persistence Behavior

The interface owns no state. Implementations may manage network sockets, Ratis groups, log directories, and container persistence through dispatchers.

## Dependencies and Integration Points

It exposes protocol types from HDDS/Ozone protobufs, `DatanodeDetails`, `ContainerCommandRequestProto`, `PipelineReport`, and metadata storage reports. It is used by higher-level datanode services without needing to know the replication transport.

## Risks and Edge Cases

Default `getStorageReport` returns null, so callers must tolerate missing metadata storage reports. Group-management defaults are no-op, which is correct for standalone but dangerous if a Ratis implementation forgets to override them.

## Test Signals

Contract tests should exercise both implementations through this SPI, especially submit failure semantics, pipeline existence/report behavior, and default method assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/package-info.java

## Purpose

This package descriptor documents the container transport server package. The complete 20-line file was read.

## Important APIs, Types, and Functions

It defines no Java types beyond the package declaration.

## Control Flow

No executable control flow exists.

## State and Persistence Behavior

No runtime state or persistence is present.

## Dependencies and Integration Points

It documents classes such as `XceiverServerSpi`, `XceiverServerGrpc`, and `GrpcXceiverService`.

## Risks and Edge Cases

Only stale documentation risk exists.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java

## Purpose

`CSMMetrics` registers Hadoop metrics for a single Ratis container state machine and records operation counts, failure counts, byte counts, cache behavior, queueing, and latency. The complete 265-line file was read.

## Important APIs, Types, and Functions

The class is annotated with `@Metrics` and is created via `create(RaftGroupId)`. Public methods increment counters for write/query/read/apply operations and failures, bytes written/committed, start-transaction verification failures, data cache hits/misses/evictions, pending apply transactions, and latency samples. `getRaftGroupId()` is exported as a metric. `unRegister()` removes the metrics source.

## Control Flow

Construction creates a `MetricsRegistry` and allocates per-`ContainerProtos.Type` `MutableRate` instances for latency and queueing delay. `create` registers a source named `CSMMetrics` plus the raft group id. State-machine code calls the increment/record methods at transaction start, write state-machine data completion, apply completion, read fallback, and failure paths.

## State and Persistence Behavior

All state is in memory inside Hadoop metrics objects. No durable persistence occurs. The source is scoped by raft group id and should be unregistered when a state machine closes.

## Dependencies and Integration Points

It integrates with `DefaultMetricsSystem`, `MetricsRegistry`, `MutableCounterLong`, `MutableRate`, Ratis `RaftGroupId`, and `ContainerStateMachine`.

## Risks and Edge Cases

Metrics source names include `gid.toString()`, so duplicate registration for the same group would conflict. `pendingApplyTransactions` is decremented by `incr(-1)`, which assumes counter implementations allow negative increments. Per-command enum maps allocate rates for all command types, including rarely used ones.

## Test Signals

Tests should verify registration/unregistration names, counter increments for success and failure paths, per-type latency/queue rates, cache hit/miss/eviction counters, and pending-apply increment/decrement balance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java

## Purpose

`ContainerStateMachine` is the Ratis `StateMachine` implementation that applies replicated Ozone container commands. It separates read-only queries, `WriteChunk` state-machine data writes, and committed metadata/application operations; maintains snapshot state for containers created in a pipeline; and coordinates dispatcher execution with Ratis log ordering. The complete 1360-line file was read.

## Important APIs, Types, and Functions

The class extends `BaseStateMachine`. Important lifecycle methods are `initialize`, `takeSnapshot`, `loadSnapshot`, `persistContainerSet`, `close`, and `notifyGroupRemove`. Ratis data-plane methods include `startTransaction(RaftClientRequest)`, `startTransaction(LogEntryProto, RaftPeerRole)`, `write`, `flush`, `read`, `query`, `stream`, `link`, `applyTransaction`, `notifyTermIndexUpdated`, `truncate`, and leadership/failure notifications. Nested helpers include `TaskQueueMap`, `Context`, and `WriteFutures`.

## Control Flow

Leader `startTransaction` validates the container command, clears encoded tokens before logging, rejects operations against finalized blocks, splits `WriteChunk` payload bytes into state-machine data while logging a metadata-only command, and records pending apply metrics. Follower/log replay `startTransaction` reconstructs the full request by combining log metadata with state-machine data. `write` only handles `WriteChunk`: it optionally caches data on the leader, dispatches the WRITE_DATA stage through a per-block chunk executor, records bytes written, and completes a raft future. `applyTransaction` removes stale cached data, builds an APPLY_TRANSACTION context, acquires a semaphore bounding pending apply work, submits the command to a per-container task queue for ordering, updates last-applied indexes only on healthy success, and marks the state machine unhealthy on serious failures. `query` dispatches read-only commands directly. `read` returns state-machine data from the transaction, leader cache, or disk by dispatching a temporary `ReadChunk` command for slow followers. `stream` and `link` integrate Ratis data stream writes with `KeyValueStreamDataChannel`.

## State and Persistence Behavior

Persistent Ratis state is a snapshot file containing `Container2BCSIDMapProto`, written from `container2BCSIDMap` and loaded at initialization to rebuild missing-container validation. Write chunk bytes are not persisted in the Ratis log entry; they are written directly through the dispatcher and temporarily retained in `stateMachineDataCache` for follower replication. `applyTransactionCompletionMap` tracks contiguous completed log indexes before updating last applied. `unhealthyContainers` and `stateMachineHealthy` stop further writes after serious data or apply failures. `containerTaskQueues` preserves per-container apply order.

## Dependencies and Integration Points

This class is tightly coupled to Apache Ratis state-machine APIs, `XceiverServerRatis`, `ContainerDispatcher`, `ContainerController`, `KeyValueStreamDataChannel`, HDDS/Ozone protobuf command types, `ResourceCache`, `TaskQueue`, and `CSMMetrics`. It calls back to `XceiverServerRatis` for follower slowness, no-leader, apply failure, log failure, snapshot-install, group add/remove, and leader-change events.

## Risks and Edge Cases

The state machine intentionally becomes unhealthy on most write/apply/read-state-machine failures, leading to pipeline close or server division close. Some container results (`CONTAINER_NOT_OPEN`, `CLOSED_CONTAINER_IO`, `CHUNK_FILE_INCONSISTENCY`) are tolerated. Long-running write detection cancels all pending write chunks for the group. The snapshot contains metadata for validation but cannot be used for follower catch-up, so install-snapshot notifications trigger pipeline close. Cache eviction policy and `waitOnBothFollowers` affect whether slow followers can read data from cache or must read from disk. `notifyLogFailed` calls `TermIndex.valueOf(failedEntry)` even when `failedEntry` may be null, which deserves defensive test coverage.

## Test Signals

Tests should cover WriteChunk data/log splitting, token clearing, finalized-block rejection, per-container apply ordering, semaphore release on success and failure, tolerated versus fatal result handling, snapshot write/load and missing-container validation, cache hit/miss/disk-read follower paths, long-running write cancellation, `flush` waiting on prior write futures, leader stepdown cache eviction, group removal quasi-close behavior, and callbacks that trigger pipeline-close actions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java

## Purpose

`DispatcherContext` carries transport-specific execution metadata from gRPC/Ratis server code into `ContainerDispatcher` and command handlers. It identifies the operation phase, write-chunk stage, Ratis term/index, container-to-BCSID map, start time, and optional release hook. The complete 266-line file was read.

## Important APIs, Types, and Functions

Static singleton accessors cover common non-Ratis handle operations: read chunk/block, write chunk, get small file, and put small file. `WriteChunkStage` values are `WRITE_DATA`, `COMMIT_DATA`, and `COMBINED` with `isWrite()`/`isCommit()` helpers. `Op` values distinguish handle, state-machine read/write/apply, stream init/link, and null operations. `Op.readFromTmpFile()` and `Op.validateToken()` encode handler policy. Builder methods set stage, term, log index, container map, and release support.

## Control Flow

The file is mostly data construction. Callers create a builder for an `Op`, optionally set Ratis metadata and stage, then pass the context to `ContainerDispatcher`. Dispatcher or lower layers can inspect `DispatcherContext.op(context)` safely when context is null. Release support is opt-in; `setReleaseMethod` asserts support, and `release()` invokes the stored hook if present.

## State and Persistence Behavior

Each instance is immutable except the volatile `releaseMethod`. It persists no data, but carries a mutable map reference for container BCSID tracking when supplied by the Ratis state machine.

## Dependencies and Integration Points

It integrates with `ContainerDispatcher`, gRPC read contexts, `ContainerStateMachine`, Ratis `TermIndex`, and token-validation logic in container handlers.

## Risks and Edge Cases

The static singleton contexts do not support release hooks and have default term/index zero. `validateToken()` returns false for apply/write/read state-machine data and stream link because tokens were validated earlier; using the wrong op can skip needed token validation. The container map is not copied, so callers share mutation semantics.

## Test Signals

Tests should verify token-validation policy by op, write-stage helper semantics, null-safe `op`, release assertion and invocation, and that Ratis contexts carry term/index/container map into command handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java

## Purpose

`LocalStream` adapts a local `StateMachine.DataChannel` plus executor into a Ratis `StateMachine.DataStream` for datanode stream writes. The complete 55-line file was read.

## Important APIs, Types, and Functions

The package-private class implements `StateMachine.DataStream` with `getDataChannel()`, `cleanUp()`, and `getExecutor()`. Its constructor receives a data channel and executor.

## Control Flow

`cleanUp` requires the channel to be a `KeyValueStreamDataChannel`; otherwise it returns an exceptional future. For expected channels, it asynchronously calls `KeyValueStreamDataChannel.cleanUp()` on the provided executor.

## State and Persistence Behavior

The class only stores references. Actual stream data persistence and cleanup are owned by `KeyValueStreamDataChannel`.

## Dependencies and Integration Points

It is created by `ContainerStateMachine.stream` and later checked by `ContainerStateMachine.link`. It integrates with Ratis stream APIs and key-value container stream data channels.

## Risks and Edge Cases

A null or incompatible executor/channel will fail asynchronously or by class check. Cleanup assumes the executor remains alive through stream cleanup.

## Test Signals

Tests should cover successful cleanup for `KeyValueStreamDataChannel`, exceptional cleanup for unexpected channel types, executor usage, and link/cleanup lifecycle with `ContainerStateMachine`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java

## Purpose

`RatisServerConfiguration` exposes configuration binding for Ratis server snapshot retention. The complete 47-line file was read.

## Important APIs, Types, and Functions

The class is annotated `@ConfigGroup(prefix = "hdds.ratis.server")`. It defines `numSnapshotsRetained` with `@Config(key = "hdds.ratis.server.num.snapshots.retained", type = INT, defaultValue = "5", tags = STORAGE)`, plus getter and setter.

## Control Flow

There is no complex flow. Ozone configuration binding populates the field, and `XceiverServerRatis.newRaftProperties()` reads it to set `RaftServerConfigKeys.Snapshot.setRetentionFileNum`.

## State and Persistence Behavior

The class holds in-memory configuration only. Snapshot files retained or deleted are controlled by Ratis using this value.

## Dependencies and Integration Points

It depends on HDDS config annotations and integrates with `XceiverServerRatis`.

## Risks and Edge Cases

Invalid or low values could remove diagnostic snapshots earlier than expected. Because the key repeats the group prefix in the annotation, config binding behavior should be verified against existing HDDS config conventions.

## Test Signals

Tests should verify default binding to 5, custom value binding, and propagation into Ratis snapshot retention properties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java

## Purpose

`XceiverServerRatis` is the datanode container transport server for RATIS replication. It owns the local `RaftServer`, creates `ContainerStateMachine` instances per pipeline, manages Ratis ports and properties, accepts local command submissions, tracks active pipelines, and reports or closes pipelines on Ratis failure signals. The complete 992-line file was read.

## Important APIs, Types, and Functions

Primary APIs include `newXceiverServerRatis`, `start`, `stop`, `submitRequest`, `addGroup`, `removeGroup`, `isExist`, `getPipelineReport`, `getMinReplicatedIndex`, `getRaftPeersInPipeline`, and notification handlers invoked by `ContainerStateMachine`. Configuration helpers include `newRaftProperties`, `assignPorts`, `setUpRatisStream`, `setStateMachineDataConfigurations`, `setRaftSegmentAndWriteBufferSize`, `setPendingRequestsLimits`, and TLS parameter creation. `ActivePipelineContext` tracks whether this datanode is leader and whether a close action is pending.

## Control Flow

Construction assigns client/admin/server ports, optionally using separate Ratis ports depending on datanode version, enables data stream if configured, creates chunk executors, builds Ratis properties, and constructs a recover-mode `RaftServer` with a state-machine registry. `start` prestarts chunk writer threads, starts Ratis, and records actual bound ports back into `DatanodeDetails`, including datastream port when enabled. `submitRequest` wraps a container command as a `RaftClientRequest`, submits it to the local server with a timeout, and raises not-leader or state-machine exceptions. `addGroup` builds a Ratis group from pipeline peers and priority list; `removeGroup` removes it while either deleting or preserving logs. Failure handlers translate slowness, no leader, apply failure, log failure, and snapshot-install notifications into SCM pipeline close actions and immediate heartbeat triggers.

## State and Persistence Behavior

Persistent state is primarily Ratis log/snapshot storage under configured datanode Ratis directories. `shouldDeleteRatisLogDirectory` controls whether removed group logs are deleted or renamed/preserved. Runtime state includes port fields, `activePipelines`, chunk executor pools, a generated Ratis client id, and request call id counter.

## Dependencies and Integration Points

The class integrates with Apache Ratis server/group-management APIs, Ozone config keys, `DatanodeRatisServerConfig`, `RatisHelper`, `ContainerDispatcher`, `ContainerController`, `StateContext`, tracing, TLS certificate clients, and SCM pipeline actions/reports.

## Risks and Edge Cases

Misconfigured log appender byte limits larger than segment size are rejected by assertion. Pipeline-close triggering assumes `activePipelines.get(groupId)` is present when context exists. Snapshot installation is intentionally treated as fatal to the pipeline because snapshots do not contain enough data for catch-up. `submitRequest` is local and times out by config, so callers must handle `IOException` wrapping timeout or execution failures. TLS parameters are null when security/TLS is disabled.

## Test Signals

Tests should cover fixed/random/separate port assignment, Ratis property generation for log sizes, state-machine data caching, snapshot retention and data stream options, TLS parameter creation, add/remove group behavior and log-retention flags, submitRequest reply exception mapping, pipeline report leader flag updates, immediate heartbeat on pipeline close, and failure notification paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/package-info.java

## Purpose

This package descriptor documents Ratis-backed container transport server implementation classes. The complete 19-line file was read.

## Important APIs, Types, and Functions

No executable types or functions are declared.

## Control Flow

No runtime flow exists.

## State and Persistence Behavior

No state or persistence is owned by the descriptor.

## Dependencies and Integration Points

It documents the package containing `XceiverServerRatis`, `ContainerStateMachine`, `DispatcherContext`, and related Ratis helpers.

## Risks and Edge Cases

Only stale documentation risk exists.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java

## Purpose

`ContainerCache` is a singleton LRU cache of schema-v2-style per-container RocksDB `ReferenceCountedDB` handles. It prevents excessive DB open/close churn, provides per-DB-path locking, and closes handles only when their reference count reaches zero. The complete 239-line file was read.

## Important APIs, Types, and Functions

The class extends Apache Commons `LRUMap`. Public methods include `getInstance(ConfigurationSource)`, `getDB(...)`, `removeDB(String)`, `addDB(String, ReferenceCountedDB)`, `shutdownCache()`, and testing `getMetrics()`. It overrides `removeLRU(LinkEntry)`. Internally it uses a global `ReentrantLock`, `Striped<Lock>` keyed by DB path, and `cleanupDb`.

## Control Flow

`getInstance` initializes cache size and lock stripes from Ozone config and registers metrics. `getDB` validates container id, locks the path stripe, checks the map under the global lock, returns and increments an existing open DB, removes closed entries, or opens a new uncached datanode store through `BlockUtils`. After opening, it rechecks the map to avoid duplicate handles, cleans the extra handle if another thread inserted one, then caches and increments the selected handle. LRU eviction calls `cleanupDb` and only removes entries whose handle can be closed.

## State and Persistence Behavior

Runtime state is the LRU map and reference counters. Persistent state is the RocksDB store opened at `containerDBPath`; this class manages handle lifetime but not schema contents. `shutdownCache` attempts to clean every DB and then clears the map.

## Dependencies and Integration Points

It depends on `BlockUtils.getUncachedDatanodeStore`, `ReferenceCountedDB`, Ozone cache config keys, Guava striped locks, Commons `LRUMap`, and `ContainerCacheMetrics`.

## Risks and Edge Cases

Callers must close returned `ReferenceCountedDB` handles exactly once; leaks prevent eviction cleanup, while double close trips the refcount precondition. Extending raw `LRUMap` loses generic type safety. The static metrics/cache lifecycle can conflict with tests or multiple datanode instances in one JVM. `removeDB` increments remove metrics nowhere despite a metrics method existing.

## Test Signals

Tests should cover cache hit/miss/refcount increments, concurrent same-path open deduplication, LRU eviction blocked by positive refcount, cleanup after close, removal of already closed handles, shutdown behavior, metrics increments, and configured cache size/stripe count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java

## Purpose

`ContainerCacheMetrics` registers Hadoop metrics for `ContainerCache` DB-handle activity: open/close latency, cache hits/misses, get/remove operations, and evictions. The complete 109-line file was read.

## Important APIs, Types, and Functions

The class is final and created through `create()`. It provides increment methods for DB get/remove, hits, misses, evictions, and latency samples, plus getters for the counter values.

## Control Flow

`create` registers a `ContainerCacheMetrics` source in the default metrics system. `ContainerCache` invokes the increment methods during get, miss/hit, open/close, and LRU removal paths.

## State and Persistence Behavior

Metrics are in-memory only and exported through Hadoop metrics. There is no explicit unregister method in this class.

## Dependencies and Integration Points

It uses `DefaultMetricsSystem`, `MetricsSystem`, `MutableRate`, and `MutableCounterLong`, and is held statically by `ContainerCache`.

## Risks and Edge Cases

The metrics source name is fixed, so repeated singleton resets in tests can hit duplicate registration problems. `incNumDbRemoveOps` exists but `ContainerCache.removeDB` does not call it in this source version.

## Test Signals

Tests should verify metrics registration, all counter increments, latency sample calls from cache open/close, and singleton/test lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java

## Purpose

`ContainerInspectorUtil` centralizes startup-time container inspector registration and execution by container type. It currently wires `KeyValueContainerMetadataInspector` for key-value containers. The complete 86-line file was read.

## Important APIs, Types, and Functions

The static `INSPECTORS` map is keyed by `ContainerProtos.ContainerType` and stores lists of `ContainerInspector`. Public static methods are `load()`, `unload()`, `isReadOnly(ContainerType)`, and `process(ContainerData, DatanodeStore)`.

## Control Flow

Static initialization creates an inspector list for every container type and adds the key-value metadata inspector to `KeyValueContainer`. `load` and `unload` iterate all inspectors. `isReadOnly` returns false if any inspector for that type is mutating. `process` dispatches a container and its store to each inspector registered for the container's type.

## State and Persistence Behavior

The utility owns only static inspector lists. Persistence effects depend on individual inspectors; the key-value metadata inspector may inspect or repair metadata depending on its own mode.

## Dependencies and Integration Points

It depends on `ContainerInspector`, `ContainerData`, `DatanodeStore`, protobuf container types, and `KeyValueContainerMetadataInspector`.

## Risks and Edge Cases

The map assumes every enum value is present from static initialization. Adding new container types without inspectors is safe but no-op. Inspector load/unload/process exceptions are not caught here and can propagate to startup paths.

## Test Signals

Tests should verify key-value inspector registration, read-only aggregation, process dispatch by type, load/unload invocation, and behavior with container types that have no inspectors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java

## Purpose

`ContainerLogger` writes compact, long-retention container replica event records to the dedicated Log4j logger named `ContainerLog`. It captures successful state changes, import/export/recovery/reconcile/move events, and failure events without flooding the main datanode log. The complete 218-line file was read.

## Important APIs, Types, and Functions

Public static log methods include `logOpen`, `logClosing`, `logQuasiClosed`, `logClosed`, `logUnhealthy`, `logLost`, `logDeleted`, `logImported`, `logExported`, `logRecovered`, `logChecksumUpdated`, `logReconciled`, and `logMoveSuccess`. Private `getMessage` overloads build pipe-separated fields.

## Control Flow

Each public method formats a container message after the related event succeeds and logs at info, warn, or error level depending on severity. Base fields are container ID, replica index, BCSID, state, volume, and data checksum. Specialized methods append reasons, old/new checksums, peer details, move source/destination, size, and elapsed time.

## State and Persistence Behavior

No Java state is persisted by the class. Persistence is the configured Log4j appender for `ContainerLog`.

## Dependencies and Integration Points

It depends on `ContainerData`, `ScanResult`, `DatanodeDetails`, `StorageVolume`, Log4j, and `HddsUtils.checksumToString`. It is intended for container lifecycle code paths after successful transitions.

## Risks and Edge Cases

Logging before an operation succeeds would produce misleading history; the class documentation explicitly warns against that. Peer `toString()` and volume `toString()` content affect log stability. Multi-field message formatting uses `" | "`, so appended fields should avoid ambiguous embedded separators when possible.

## Test Signals

Tests should verify formatting fields, log levels for each event class, checksum update/reconcile messages, move-success details, and that lifecycle callers invoke these methods only after successful state changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java

## Purpose

`DatanodeStoreCache` is a singleton cache for schema-v3 per-disk `DatanodeStore` handles. Unlike `ContainerCache`, schema v3 shares one RocksDB instance per disk, so raw DB close is centralized at cache shutdown or explicit removal. The complete 125-line file was read.

## Important APIs, Types, and Functions

Public methods include `getInstance()`, testing `setMiniClusterMode`, `addDB`, `getDB`, `removeDB`, `shutdownCache`, and `size`. The map key is the container DB absolute path and values are `RawDB`.

## Control Flow

`getDB` first checks a concurrent map, then synchronizes on the cache object for double-checked creation. It opens a `DatanodeStoreSchemaThreeImpl` in read-write mode, wraps it in `RawDB`, and stores it. `removeDB` removes and stops the store if present. `shutdownCache` either skips clearing in mini-cluster mode, logging remaining keys, or stops every store and clears the map.

## State and Persistence Behavior

Runtime state is `datanodeStoreMap` and `miniClusterMode`. Persistent state is the per-disk RocksDB store; the cache manages handle lifetime and does not alter metadata by itself.

## Dependencies and Integration Points

It depends on `DatanodeStoreSchemaThreeImpl`, `RawDB`, `ConfigurationSource`, and schema-v3 block/metadata code that calls `BlockUtils.addDB` or store cache accessors.

## Risks and Edge Cases

Mini-cluster mode intentionally leaks cache entries across shutdown to support test cluster lifetimes, which can surprise tests that expect full cleanup. Creation is synchronized globally rather than per path. `addDB` uses `putIfAbsent` and does not close or reject a supplied duplicate handle.

## Test Signals

Tests should cover double-checked creation, remove/stop behavior, shutdown behavior with and without mini-cluster mode, duplicate `addDB`, IOException wrapping during open, and cache size tracking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java

## Purpose

`DiskCheckUtil` performs low-level storage directory health checks for existence, permissions, and actual read/write/delete behavior. It also supports test injection of disk-check implementations. The complete 208-line file was read.

## Important APIs, Types, and Functions

Static APIs are `checkExistence`, `checkPermissions`, `checkReadWrite`, `setTestImpl`, and `clearTestImpl`. `DiskChecks` is an injectable interface with default-success methods. `DiskChecksImpl` contains production checks.

## Control Flow

`checkExistence` verifies the directory exists. `checkPermissions` checks read, write, and execute permissions and logs every missing permission before returning a single failure. `checkReadWrite` creates a random test file in the supplied test directory, writes random bytes through `FileUtils.newOutputStreamForceAtClose`, reads the same number of bytes back, compares content, and deletes the file. Each failure logs a volume-specific error and returns false.

## State and Persistence Behavior

The only persistent side effect is a temporary `disk-check-<uuid>` file that should be deleted after a successful check. Failure paths can leave the test file behind when delete is not reached or delete fails. The active implementation is static mutable test state.

## Dependencies and Integration Points

It depends on Java file APIs, Ratis `FileUtils`, and storage volume scanners/checkers that call these utilities. Tests can inject failure behavior through `DiskChecks`.

## Risks and Edge Cases

If `fis.read(readBytes)` returns a short read even though more bytes are available, the method treats it as failure; for local files this is usually acceptable. Delete failure marks the disk unhealthy. Static test implementation must be cleared to avoid cross-test contamination. The SyncFailedException log message says "Could sync" instead of "Could not sync".

## Test Signals

Tests should cover missing directory, each permission bit, write/read content mismatch, short read, delete failure, injected implementations, cleanup/reset of test impl, and leftover temporary file handling on failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java

## Purpose

`HddsVolumeUtil` contains HDDS data-volume helpers for resolving the `hdds` root, initializing schema-v3 per-disk DB stores, loading DB stores for all HDDS volumes, and mapping dedicated DB volumes to data volumes. The complete 142-line file was read.

## Important APIs, Types, and Functions

Public APIs are `getHddsRoot(String)`, `initPerDiskDBStore(String, ConfigurationSource, boolean)`, and `loadAllHddsVolumeDbStore(MutableVolumeSet, MutableVolumeSet, boolean, Logger)`. Private helpers are `loadVolume` and `mapDbVolumesToDataVolumesIfNeeded`.

## Control Flow

`getHddsRoot` appends `HddsVolume.HDDS_VOLUME_DIR` unless the path already ends in it. `initPerDiskDBStore` opens or formats an uncached schema-v3 store and registers it through `BlockUtils.addDB`. `loadAllHddsVolumeDbStore` first maps DB volumes to data volumes using storage IDs, then runs `volume.loadDbStore(readOnly)` asynchronously for each HDDS volume and waits for all futures. Failures call `StorageVolumeUtil.onFailure` and log the failed volume.

## State and Persistence Behavior

The utility can create/open per-disk RocksDB stores and update `HddsVolume` objects with their associated `DbVolume`. It does not store state of its own. Persistent DB initialization is delegated to `BlockUtils` and volume implementations.

## Dependencies and Integration Points

It depends on `HddsVolume`, `DbVolume`, `MutableVolumeSet`, `BlockUtils`, `DatanodeStore`, `OzoneConsts.SCHEMA_V3`, and `StorageVolumeUtil` conversion/failure helpers.

## Risks and Edge Cases

`getHddsRoot` uses a suffix check rather than path-segment comparison, so unusual paths ending in the same string are accepted. Asynchronous load uses the common ForkJoin pool via `CompletableFuture.runAsync`, so large volume counts share global executor resources. `join` propagates unchecked exceptions if `loadVolume` ever throws beyond its catch block.

## Test Signals

Tests should cover root resolution, schema-v3 DB initialization in read-only and read-write modes, DB-volume-to-HDDS-volume mapping by storage ID, failed load invoking volume failure handling, and logging/timing with multiple volumes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java

## Purpose

`RawDB` is a thin `DBHandle` wrapper for schema-v3 per-disk datanode stores. Its key behavior is that `close()` intentionally does nothing because individual container operations must not close a shared per-disk RocksDB handle. The complete 40-line file was read.

## Important APIs, Types, and Functions

The class extends `DBHandle`, has a constructor accepting `DatanodeStore` and DB path, and overrides `close()`.

## Control Flow

There is no operational flow beyond construction and no-op close.

## State and Persistence Behavior

It stores the underlying `DatanodeStore` and path via `DBHandle`. Persistence is managed by the store and by `DatanodeStoreCache`, which eventually calls `store.stop()`.

## Dependencies and Integration Points

It integrates with `DatanodeStoreCache` and schema-v3 block code that expects a `DBHandle` but must not own the shared store lifecycle.

## Risks and Edge Cases

Generic code that assumes `DBHandle.close()` releases resources will not release schema-v3 stores when passed `RawDB`. That is intentional but must remain documented.

## Test Signals

Tests should verify close is no-op, cache removal/shutdown stops the underlying store, and callers do not rely on try-with-resources to close schema-v3 shared DBs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java

## Purpose

`ReferenceCountedDB` wraps a per-container `DatanodeStore` with reference counting so `ContainerCache` can share handles safely and close them only when unused. The complete 93-line file was read.

## Important APIs, Types, and Functions

The class extends `DBHandle`. Public methods are `getReferenceCount`, `incrementReference`, `decrementReference`, `cleanup`, `close`, and `isClosed`.

## Control Flow

Callers receive a handle from `ContainerCache.getDB`, which increments the reference. `close` decrements the count and asserts it does not go negative. `cleanup` stops the underlying store when it is already closed or the reference count is zero; otherwise it returns false so eviction/removal can be blocked. Trace logging can include stack traces on refcount changes.

## State and Persistence Behavior

Runtime state is an `AtomicInteger` reference count. Persistent DB contents live in the wrapped store. `cleanup` stops the store, closing RocksDB resources, but does not delete on-disk data.

## Dependencies and Integration Points

It depends on `DBHandle`, `DatanodeStore`, Guava preconditions, and `ContainerCache`.

## Risks and Edge Cases

Reference leaks keep DBs open and block cache eviction. Double close triggers a precondition failure. `cleanup` calls `getStore().stop()` if the store exists and is closed or refcount is zero; callers should not pass null stores. Trace stack capture is expensive and should stay trace-only.

## Test Signals

Tests should cover increment/decrement, negative refcount prevention, cleanup false with active references, cleanup true at zero references, already-closed store behavior, and integration with cache eviction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java

## Purpose

`StorageVolumeUtil` provides common storage-volume helpers for VERSION file validation, volume UUID generation, volume consistency checks, failure scheduling, and typed volume list conversion. The complete 277-line file was read.

## Important APIs, Types, and Functions

Public APIs include `onFailure`, `getHddsVolumesList`, `getDbVolumesList`, `getVersionFile`, `generateUuid`, property validators for storage ID, cluster ID, datanode UUID, creation time, layout version, `getProperty`, and `checkVolume`. Constants include `VERSION_FILE` and storage ID prefix `DS-`.

## Control Flow

Validation helpers read required properties and throw `InconsistentStorageStateException` for missing, mismatched, future/negative creation time, or layout-version mismatch. `checkVolume` formats the volume if necessary, lists root files, chooses the correct working directory under the cluster ID or legacy SCM ID, upgrades SCM HA symlinks when needed, creates a working directory for first-use volumes, tolerates extra files only when a cluster ID directory exists, and creates volume-level temporary directories. Failures are logged and return false.

## State and Persistence Behavior

`checkVolume` may create or update VERSION files, working directories, SCM-HA compatibility symlinks, and tmp directories. `generateUuid` creates new storage IDs. `onFailure` schedules async volume checks through a mutable volume set.

## Dependencies and Integration Points

It integrates with `StorageVolume`, `HddsVolume`, `DbVolume`, `MutableVolumeSet`, `VolumeSet`, `HDDSVolumeLayoutVersion`, `VersionedDatanodeFeatures.ScmHA`, `OzoneConsts`, and startup `VersionEndpointTask` volume checks.

## Risks and Edge Cases

The root-file-count logic is sensitive to unexpected files in volume roots. Existing SCM-ID layouts depend on SCM HA feature helpers to choose and upgrade paths correctly. Typed list conversion uses unchecked casts. Invalid creation time depends on local system clock.

## Test Signals

Tests should cover property validation, mismatched cluster/datanode IDs, layout mismatch, first-format volume, legacy SCM ID layout before/after SCM HA finalization, extra root files with and without cluster dir, tmp-dir creation failure, failure scheduling, and typed list conversion assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java

## Purpose

`DatanodeDBProfile` selects and memoizes managed RocksDB options for datanode metadata stores based on storage profile. It ensures column family options can be reused across containers and configures block cache size from datanode metadata RocksDB settings. The complete 156-line file was read.

## Important APIs, Types, and Functions

The abstract API exposes `getDBOptions()` and `getColumnFamilyOptions(ConfigurationSource)`. `getProfile(DBProfile)` returns `SSD` or `Disk` profile instances. Nested `SSD` and `Disk` delegate to `StorageBasedProfile`, which holds an `AtomicReference<Supplier<ManagedColumnFamilyOptions>>` and a base `DBProfile`.

## Control Flow

`getProfile` maps `SSD` to SSD options, and `DISK`/`TEST` to disk options. `StorageBasedProfile.getColumnFamilyOptions` creates a memoized supplier for options, installs it atomically once, and returns the shared value. Option creation gets base column-family options, marks them reused, and replaces table format config with a block-based table config using a configured `ManagedLRUCache` when config is present.

## State and Persistence Behavior

State is in-memory memoized RocksDB options and block cache objects. Persistent DB data is not touched here, but the returned options affect RocksDB behavior for datanode stores.

## Dependencies and Integration Points

It depends on HDDS `DBProfile`, managed RocksDB option wrappers, `ManagedLRUCache`, `MemoizedSupplier`, and config keys `HDDS_DATANODE_METADATA_ROCKSDB_CACHE_SIZE`.

## Risks and Edge Cases

Because column-family options are memoized per storage profile, the first configuration used controls later calls for that profile in the JVM. That is efficient for production but can surprise tests with different configs. Unsupported DB profiles throw `IllegalArgumentException`.

## Test Signals

Tests should verify profile mapping, DBOptions delegation, one-time memoization, configured block cache size, reused flag behavior, null-config fallback, and unsupported profile exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/package-info.java

## Purpose

This package descriptor documents datanode DB utility classes. The complete 21-line file was read.

## Important APIs, Types, and Functions

No executable APIs are defined.

## Control Flow

No runtime flow exists.

## State and Persistence Behavior

No state or persistence is owned.

## Dependencies and Integration Points

It documents the package containing `DatanodeDBProfile` and related DB helpers.

## Risks and Edge Cases

Only stale documentation risk exists.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/package-info.java

## Purpose

This package descriptor documents common container utility classes. The complete 19-line file was read.

## Important APIs, Types, and Functions

It defines no executable types.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is present.

## Dependencies and Integration Points

It documents utility classes such as `ContainerCache`, `StorageVolumeUtil`, `DiskCheckUtil`, and `ContainerLogger`.

## Risks and Edge Cases

Only stale package documentation risk exists.

## Test Signals

Compile/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java

## Purpose

`AsyncChecker` is a generic interface for scheduling asynchronous health checks against `Checkable` targets, used by datanode volume-checking infrastructure. The complete 62-line file was read.

## Important APIs, Types, and Functions

The interface is parameterized as `<K, V>`. `schedule(Checkable<K,V> target, K context)` returns an `Optional<ListenableFuture<V>>` when a check is accepted. `shutdownAndWait(long, TimeUnit)` cancels executing checks and waits for termination.

## Control Flow

Implementations decide whether a target can be scheduled and return an absent optional when not scheduled. Shutdown is expected to first attempt graceful cancellation, then forceful cancellation, waiting after both attempts.

## State and Persistence Behavior

The interface owns no state. Implementations typically own executor services and in-flight check maps. There is no persistence.

## Dependencies and Integration Points

It depends on Guava `ListenableFuture`, HDFS `Checkable`, `ExecutorService` semantics, and datanode volume checker classes.

## Risks and Edge Cases

Callers must handle `Optional.empty()` without assuming a check is in progress. Implementations need careful duplicate scheduling and shutdown semantics to avoid leaking checks or blocking datanode shutdown.

## Test Signals

Implementation tests should cover accepted and rejected schedules, future completion, duplicate target handling, graceful and forceful shutdown, timeout behavior, and interrupt propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java

## Purpose

`AvailableSpaceFilter` selects `HddsVolume`s that have enough hard-min-free available space to create a new container and records rejected volumes for diagnostics. The complete 84-line file was read.

## Important APIs, Types, and Functions

The class implements `Predicate<HddsVolume>`. Constructor input is `requiredSpace`. Main methods are `test(HddsVolume)`, package-private `foundFullVolumes()`, `mostAvailableSpace()`, and `toString()`.

## Control Flow

`test` reads a volume's `StorageLocationReport`, computes hard-limit available space as remaining minus committed minus `vol.getFreeSpaceToSpare(capacity)`, compares it to `requiredSpace`, updates per-volume metrics, tracks the maximum available amount seen, adds rejected reports to `fullVolumes`, and returns eligibility. If the volume is above the hard limit but inside the softer reported spare band, it increments a soft-band metric.

## State and Persistence Behavior

The filter stores `fullVolumes` and `mostAvailableSpace` for the scan instance. It persists nothing. Metrics side effects occur on `VolumeInfoMetrics` if present.

## Dependencies and Integration Points

It depends on `HddsVolume`, `StorageLocationReport`, and volume info metrics. It is used by volume/container placement code when selecting space for a new container.

## Risks and Edge Cases

The comparison is strict `available > requiredSpace`; exactly equal space is rejected. The filter is stateful and not thread-safe; reuse across independent scans can mix diagnostics. Negative committed/remaining anomalies can produce misleading availability.

## Test Signals

Tests should cover hard-limit rejection, exact-equality rejection, soft-band metric increments, full-volume list/toString, most-available tracking, null metrics handling, and state reset by using new filter instances.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java

## Purpose

`BackgroundVolumeScannerMetrics` registers Hadoop metrics for background volume scanning: volumes scanned in the last iteration, scan iteration count, data/metadata volume scans, and skipped iterations. The complete 119-line file was read.

## Important APIs, Types, and Functions

The class is annotated with `@Metrics` and created via `create()`. It exposes getters and mutators for `numVolumesScannedInLastIteration`, `numScanIterations`, `numDataVolumeScans`, `numMetadataVolumeScans`, and `numIterationsSkipped`, plus `unregister()`.

## Control Flow

`create` registers a metrics source named after the class. Scanner code sets the last-iteration gauge, increments scan iteration count, increments data and metadata scan counters by count, and increments skipped iterations when minimum scan gap prevents work. `unregister` removes the source from the default metrics system.

## State and Persistence Behavior

All state is in-memory metrics. No persistent data is written.

## Dependencies and Integration Points

It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableGaugeLong`, and `MutableCounterLong`, and integrates with background volume scanner code.

## Risks and Edge Cases

The metrics source name is fixed, so only one scanner metrics instance can be registered cleanly per metrics system unless previous instances unregister. Counter increments accept caller-supplied counts without validation.

## Test Signals

Tests should verify registration/unregistration, gauge set/get, each counter increment, skipped iteration count, and lifecycle behavior across repeated create calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java -->
