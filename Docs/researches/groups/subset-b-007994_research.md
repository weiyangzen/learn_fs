# subset-b-007994 Research Report

Grouped research for Apache Ozone datanode state-machine and command-handler files. Each file section is source-tree-aligned and wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeConfiguration.java

## Purpose
`DatanodeConfiguration` is the annotated HDDS datanode configuration bean for container-service runtime behavior. It centralizes limits and tunables for command queues, close/delete executors, block deletion, volume health checks, disk free-space thresholds, RocksDB schema/logging/compaction behavior, read-thread sizing, and gRPC backlog.

## Important APIs and Types
The class extends `ReconfigurableConfig` and is annotated with `@ConfigGroup(prefix = "hdds.datanode")`. Public getters and setters expose values used by `DatanodeStateMachine`, command handlers, volume checks, RocksDB helpers, and container IO paths. Notable APIs include `validate()`, `getMinFreeSpace(capacity)`, `getHardLimitMinFreeSpace(capacity)`, `getSoftBandMinFreeSpaceWidth(capacity)`, `getCommandQueueLimit()`, `getBlockDeleteThreads()`, `getBlockDeleteQueueLimit()`, `getDeleteContainerTimeoutMs()`, and schema/RocksDB accessors.

## Control Flow
The configuration framework populates fields from `@Config` annotations and invokes `@PostConstruct validate()`. Validation normalizes invalid values, logs warnings, and calls `validateMinFreeSpace()` to enforce ratio bounds and keep the hard-limit ratio no greater than the soft/reporting ratio.

## State and Persistence Behavior
This file is in-memory configuration state only, but its values control persistent side effects elsewhere: datanode ID writes, container metadata updates, RocksDB delete-transaction tables, and volume failure policy. Free-space thresholds feed storage reports and local write rejection; block deletion values determine retry and locking pressure.

## Dependencies and Integration Points
It depends on HDDS config annotations, `StorageSize`, `DurationFormatUtils`, and `ReconfigurableConfig`. `DatanodeStateMachine` consumes it when constructing command executors and the replication supervisor. `DeleteBlocksCommandHandler`, `DeleteContainerCommandHandler`, disk-check services, RocksDB options, and volume selection use its values.

## Risks
Misconfigured queue sizes and thread counts can either drop commands or overrun datanode resources. Disk-check sliding windows are sensitive: if shorter than the periodic interval, sparse failures may be missed. Free-space hard-limit and soft-limit ratios affect write availability and SCM capacity planning. One setter is named `getVolumeHealthCheckFileSize(int)` despite mutating state, which is easy to misuse.

## Test Signals
Test coverage should verify `validate()` fallback behavior, ratio clamping, free-space calculations, disk-check window guards, executor/queue values, and reconfigurable block deletion limit behavior. Existing `@VisibleForTesting` methods indicate expected unit checks around soft-band width and hard-limit ratio.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeQueueMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeQueueMetrics.java

## Purpose
`DatanodeQueueMetrics` publishes Hadoop metrics for datanode queue depths: pending SCM commands in `StateContext`, queued commands inside registered handlers, incremental report queues, container action queues, and pipeline action queues per endpoint.

## Important APIs and Types
The class is a singleton `MetricsSource` registered as `DatanodeQueueMetrics`. `create(DatanodeStateMachine)` registers it with `DefaultMetricsSystem`; `unRegister()` clears and unregisters it. `getMetrics()` emits gauges using `MetricsRecordBuilder`. Endpoint-aware maps are maintained by `addEndpoint()` and `removeEndpoint()`.

## Control Flow
Construction initializes metrics names for every `SCMCommandProto.Type` in both state-context and dispatcher namespaces. On each scrape, it asks `StateContext.getCommandQueueSummary()`, `CommandDispatcher.getQueuedCommandCount()`, and endpoint queue-size maps on the context, then emits gauges.

## State and Persistence Behavior
State is process-local metrics metadata and the static singleton. No durable state is written. Endpoint maps must track `StateContext.addEndpoint/removeEndpoint` or stale gauges can remain.

## Dependencies and Integration Points
It integrates with Hadoop metrics2, `EnumCounters`, and `DatanodeStateMachine`. `StateContext` calls `addEndpoint()` and `removeEndpoint()` when endpoints change. `DatanodeStateMachine.close()` unregisters it.

## Risks
The singleton can return an existing instance for a different state machine in tests or embedded deployments if not unregistered. Metric names are generated from host names and command names; unusual host strings may create awkward metric identifiers. Concurrent endpoint changes are not explicitly synchronized inside this class.

## Test Signals
Tests should assert singleton lifecycle, endpoint map growth and shrink, queue gauge values for both context and dispatcher queues, and clean unregister behavior during datanode shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeQueueMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeStateMachine.java

## Purpose
`DatanodeStateMachine` is the top-level container-service runtime coordinator. It constructs the datanode container stack, SCM connection manager, state context, command dispatcher, report manager, replication/reconstruction services, metrics, upgrade finalizer, and the daemon loops for heartbeats and command processing.

## Important APIs and Types
Key public APIs are `startDaemon()`, `stopDaemon()`, `close()`, `triggerHeartbeat()`, `join()`, `getQueuedCommandCount()`, `finalizeUpgrade()`, `queryUpgradeStatus()`, and accessors for context, container, dispatcher, supervisor, layout state, metrics, and executors. The nested `DatanodeStates` enum defines `INIT`, `RUNNING`, and `SHUTDOWN` with monotonic transition checks.

## Control Flow
The constructor wires all dependencies, creates bounded command-handler executors, registers command handlers, builds report publishers, and registers queue/netty metrics. `startDaemon()` creates a high-priority daemon thread running `startStateMachineThread()`. That loop initializes reports and the command processor, then repeatedly calls `StateContext.execute()` at heartbeat frequency. The command processor is a separate daemon that drains `StateContext.getNextCommand()` and invokes `CommandDispatcher.handle()`, sleeping until after the next heartbeat when idle.

## State and Persistence Behavior
The class owns lifecycle state via `StateContext`. It persists upgrade/layout state through `DatanodeLayoutStorage` and `DataNodeUpgradeFinalizer`, while container persistence is delegated to `OzoneContainer` and command handlers. Shutdown closes replication metrics, EC metrics, endpoint RPCs, the container, handlers, metrics, and executors.

## Dependencies and Integration Points
It integrates with `OzoneContainer`, `SCMConnectionManager`, `StateContext`, `ReportManager`, all command handlers, `ReplicationSupervisor`, pull/push replicators, EC reconstruction, certificate and secret-key clients, layout-version management, and reconfiguration.

## Risks
Constructor wiring has broad blast radius; missing a handler means SCM commands are logged as unknown. The command processor is single-threaded before dispatch, so a blocking synchronous handler can delay all commands. The uncaught exception handler for command processing restarts the thread, but repeated failures could spin. Shutdown ordering must avoid leaving async handlers or RPC endpoints alive.

## Test Signals
Tests should cover daemon start/stop, heartbeat triggering, `DatanodeStates` transition rules, handler registration, queue summary merging, executor resizing, constructor behavior under missing SCM address config, and shutdown cleanup of metrics and services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachine.java

## Purpose
`EndpointStateMachine` holds state for one SCM or Recon RPC endpoint. It tracks endpoint state transitions, missed heartbeat count, version response, last successful heartbeat, passive/active type, and exposes this data through JMX.

## Important APIs and Types
The class implements `Closeable` and `EndpointStateMachineMBean`. Public methods include `lock()/unlock()`, `getVersion()/setVersion()`, `getState()/setState()`, `getExecutorService()`, `incMissed()`, `zeroMissedCount()`, `logIfNeeded(Exception)`, `setPassive()`, `getLastSuccessfulHeartbeat()`, and `getType()`. The `EndPointStates` enum moves through `GETVERSION`, `REGISTER`, `HEARTBEAT`, and `SHUTDOWN`.

## Control Flow
State-specific endpoint tasks use the endpoint lock and single-thread executor to serialize calls. Missed communications call `logIfNeeded()`, which throttles SCM warnings by `getLogWarnInterval(conf)` and Recon warnings by ten times that interval, then increments the missed count.

## State and Persistence Behavior
All state is in memory. Closing shuts down the RPC translator and endpoint executor. Last heartbeat is stored as a `ZonedDateTime` and exposed as epoch seconds for JMX.

## Dependencies and Integration Points
It wraps `StorageContainerDatanodeProtocolClientSideTranslatorPB`, detects Recon via `ReconDatanodeProtocolPB`, and is created by `SCMConnectionManager`. Endpoint tasks in the states/endpoint package advance the enum and update version/heartbeat state.

## Risks
`setState()` has no transition validation, so callers must preserve legal progression. `getType()` assumes the endpoint translator is available and exposes the underlying proxy. Executor shutdown is not awaited. Logging duration is computed from missed count times SCM heartbeat interval, also for Recon.

## Test Signals
Tests should validate enum progression, missed-count throttling, passive endpoint type, JMX getters, close behavior, and state/version updates during simulated version/register/heartbeat task flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachineMBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachineMBean.java

## Purpose
This interface defines the JMX view of a single datanode endpoint connection to SCM or Recon.

## Important APIs and Types
It exposes `getMissedCount()`, `getAddressString()`, `getState()`, `getVersionNumber()`, `getLastSuccessfulHeartbeat()`, and `getType()`. The state type is `EndpointStateMachine.EndPointStates`.

## Control Flow
There is no implementation control flow in the interface. `EndpointStateMachine` implements it, and `SCMConnectionManagerMXBean.getSCMServers()` returns a list of these views for management tooling.

## State and Persistence Behavior
No state is stored here. The interface shape determines what endpoint state can be observed over JMX.

## Dependencies and Integration Points
It is coupled to `EndpointStateMachine.EndPointStates` and the Hadoop JMX/MBeans registration path in `SCMConnectionManager`.

## Risks
Any incompatible signature changes affect JMX clients. Returning enum values rather than strings can expose implementation names as management contract.

## Test Signals
Tests should check that `EndpointStateMachine` satisfies this contract and that `SCMConnectionManager` returns endpoint beans through its MXBean.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachineMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManager.java

## Purpose
`SCMConnectionManager` owns the set of SCM and Recon RPC endpoint state machines used by the datanode. It creates protocol proxies, wraps them in endpoint state holders, exposes them over JMX, and closes them during shutdown or reconfiguration.

## Important APIs and Types
Public APIs include `addSCMServer()`, `addReconServer()`, `removeSCMServer()`, `getValues()`, `getSCMServers()`, `getNumOfConnections()`, `close()`, and explicit read/write lock methods. It implements `Closeable` and `SCMConnectionManagerMXBean`.

## Control Flow
The constructor registers an `HddsDatanode:SCMConnectionManager` MBean and reads the RPC timeout. Add methods take the write lock, reject duplicates, set the correct protobuf RPC engine, create an RPC proxy with retry policy, wrap the proxy in `StorageContainerDatanodeProtocolClientSideTranslatorPB`, create an `EndpointStateMachine`, mark it passive for Recon or active for SCM, and store it. Removal closes but does not force endpoint state to `SHUTDOWN`, avoiding false fatal shutdown signals from in-flight tasks.

## State and Persistence Behavior
The endpoint map is in-memory and guarded by a read/write lock. There is no durable persistence. Closing cleans endpoint RPC resources and unregisters the MBean.

## Dependencies and Integration Points
It depends on Hadoop RPC, retry policies, UGI, NetUtils, HDDS server utility config, and `EndpointStateMachine`. `InitDatanodeState` adds endpoints; running endpoint tasks iterate `getValues()`; `StateContext` separately tracks endpoint queues.

## Risks
Endpoint creation performs network/RPC setup under the write lock. If `StateContext.addEndpoint()` fails after adding an SCM server, the connection manager and context can diverge. `getValues()` returns a snapshot, so callers must tolerate concurrent removals. JMX registration failure behavior depends on `MBeans.register`.

## Test Signals
Tests should cover duplicate add, SCM vs Recon passive flag, removal without setting shutdown, close/unregister behavior, lock-protected snapshots, retry policy construction, and JMX server list shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManagerMXBean.java

## Purpose
This interface defines the JMX management view for the datanode SCM connection manager.

## Important APIs and Types
The single method `getSCMServers()` returns `List<EndpointStateMachineMBean>`, allowing management clients to inspect endpoint addresses, states, missed counts, versions, heartbeat timestamps, and type.

## Control Flow
No control flow is implemented here. `SCMConnectionManager` implements it and registers itself as an MBean in its constructor.

## State and Persistence Behavior
No state is stored in the interface. It shapes the observable endpoint collection contract.

## Dependencies and Integration Points
It depends on `EndpointStateMachineMBean` and the MBeans registration in `SCMConnectionManager`.

## Risks
Changing the method name or return type can break JMX consumers and dashboards. The method name says SCM servers, but implementations include Recon endpoints too.

## Test Signals
Tests should assert that the registered connection-manager MBean exposes all active SCM and Recon endpoint MBeans through this method.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/StateContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/StateContext.java

## Purpose
`StateContext` is the mutable runtime context shared by the datanode state machine, endpoint tasks, report publishers, and command processing. It tracks datanode state, queued SCM commands, full and incremental reports, container and pipeline actions, command status, endpoint-specific queues, heartbeat intervals, and leader SCM term filtering.

## Important APIs and Types
Core APIs include `execute()`, `getTask()`, `addCommand()`, `getNextCommand()`, `refreshFullReport()`, `addIncrementalReport()`, `getAllAvailableReports()`, `putBackReports()`, `addContainerActionIfAbsent()`, `getPendingContainerAction()`, `addPipelineActionIfAbsent()`, `getPendingPipelineAction()`, command-status methods, endpoint add/remove methods, heartbeat frequency configuration, and queue-size accessors. Nested `PipelineActionMap` and `PipelineKey` deduplicate and retain close-pipeline actions until the local pipeline disappears.

## Control Flow
`DatanodeStateMachine` calls `execute()` each heartbeat cycle. The context creates the correct state task (`InitDatanodeState` or cached `RunningDatanodeState`), invokes enter/execute/await/exit hooks, enforces executor availability, advances allowed states, and marks fatal shutdown when a non-graceful task returns `SHUTDOWN`. Reports are drained per endpoint by heartbeat tasks: full reports are controlled by per-endpoint ready flags, and incremental reports are removed as returned.

## State and Persistence Behavior
Most state is process memory. Command statuses for delete-block commands are retained in `cmdStatusMap` so heartbeat reports can return ACKs. The leader SCM term is initialized after a majority of active SCM endpoints reach heartbeat state and commands are available, then stale-term commands are dropped. Full reports keep only the latest message per type; incremental reports and actions are endpoint-specific queues.

## Dependencies and Integration Points
It integrates with `DatanodeStateMachine`, `SCMConnectionManager`, `RunningDatanodeState`, `InitDatanodeState`, report manager publishers, endpoint heartbeat/register/version tasks, `OzoneContainer`, `ClosePipelineCommandHandler`, and protobuf report/action/command types.

## Risks
Concurrency is mixed: a `ReentrantLock` protects command queue operations, some maps are synchronized manually, some are concurrent, and endpoint sets are unsynchronized in some paths. Full report ready flags must be maintained for every endpoint and report type. Leader-term initialization delays command processing until majority heartbeat conditions are met, which is correct for HA but can look like a stalled queue if endpoints do not advance.

## Test Signals
Tests should cover state transitions, task lifecycle hooks, executor-unavailable warnings, report drain and put-back ordering, full-report ready flags, ICR discard during full container reports, endpoint queue initialization/removal, command queue limits, stale leader-term filtering, command status updates, and pipeline action deduplication/retention.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/StateContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CloseContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CloseContainerCommandHandler.java

## Purpose
Handles SCM close-container commands by moving local containers toward closed state, either through the write channel for active pipelines or directly/quasi-closed when the pipeline is absent.

## Important APIs and Types
Implements `CommandHandler` for `SCMCommandProto.Type.closeContainerCommand`. The constructor creates a bounded fixed `ThreadPoolExecutor`. `handle()` schedules async work, `getContainerCommandRequestProto()` builds an internal CloseContainer request, and metrics/queue/thread-pool accessors expose runtime behavior.

## Control Flow
`handle()` increments queued count and runs a task. The task fetches datanode details, casts `CloseContainerCommand`, gets the target container, calls `controller.markContainerForClose()`, then switches on container state. For `OPEN` or `CLOSING`, it submits a write-channel close request if the pipeline exists; otherwise force closes or quasi-closes. `QUASI_CLOSED` force commands close the container. `CLOSED` is a no-op, and unhealthy/invalid states are ignored.

## State and Persistence Behavior
Container state transitions are delegated to `ContainerController` and the write channel, which persist container metadata/state as appropriate. The handler itself stores invocation, queued count, executor, and latency metric only.

## Dependencies and Integration Points
It depends on `OzoneContainer`, `ContainerController`, `XceiverServerSpi` write channel, datanode details, tracing token propagation, and Ratis `NotLeaderException` handling.

## Risks
`CompletableFuture.runAsync` with a bounded executor can throw if the queue is full; unlike some handlers, this code does not catch `RejectedExecutionException` around submission. Force-close semantics differ sharply from quasi-close behavior. Missing containers are treated as informational rather than failure.

## Test Signals
Tests should verify state-dependent close behavior, encoded token propagation, NotLeader handling, missing container behavior, queue count decrement on completion, executor metrics, and rejection behavior when the queue is full.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CloseContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ClosePipelineCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ClosePipelineCommandHandler.java

## Purpose
Handles SCM close-pipeline commands by removing Ratis or write-channel pipeline groups locally and, for Ratis, requesting peer datanodes to remove the Raft group.

## Important APIs and Types
Implements `CommandHandler` for `closePipelineCommand`. It uses an injected `Executor`, a `BiFunction<RaftPeer, GrpcTlsConfig, RaftClient>`, `MutableRate`, and a concurrent `pipelinesInProgress` set. `isPipelineCloseInProgress(UUID)` is used by `StateContext` to expose in-progress pipeline closes.

## Control Flow
`handle()` deduplicates by pipeline UUID. It schedules async work, fetches the write channel, checks if the pipeline exists, and for `XceiverServerRatis` collects peers and sends group-management `remove()` calls to peers before removing the local group. `GroupMismatchException` is treated as benign because another datanode may have closed the group already. Completion decrements queue count and clears the in-progress marker.

## State and Persistence Behavior
Persistent effects are in the write-channel/Ratis group storage and optional Ratis log directory deletion. Handler state is in-memory deduplication and metrics.

## Dependencies and Integration Points
It integrates with `XceiverServerSpi`, `XceiverServerRatis`, Ratis `RaftClient`, `RatisHelper`, TLS config from `OzoneContainer`, and command queue metrics.

## Risks
Peer remove calls happen best-effort; IO failures are logged but local remove still proceeds. The queue count is manually adjusted and must stay balanced on rejection and completion. In-progress deduplication prevents duplicate work but also means a stuck task suppresses later commands for that pipeline until completion.

## Test Signals
Tests should cover duplicate suppression, Ratis peer removal, local `removeGroup`, benign group-mismatch handling, rejection cleanup, queue count accuracy, and `isPipelineCloseInProgress()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ClosePipelineCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandDispatcher.java

## Purpose
`CommandDispatcher` maps SCM command protobuf types to the datanode command handlers that implement them. It is the single dispatch point after commands leave `StateContext`.

## Important APIs and Types
The private constructor validates handler uniqueness and creates `CommandHandlerMetrics`. Public APIs include `handle(SCMCommand<?>)`, `stop()`, `getQueuedCommandCount()`, test accessors for selected handlers, `getClosePipelineCommandHandler()`, and the nested `Builder`.

## Control Flow
`DatanodeStateMachine` builds a dispatcher by adding handlers and setting container, context, and connection manager. `handle()` looks up the handler by `command.getType()`, increments command metrics, invokes the handler, and logs unknown commands or handler exceptions without rethrowing.

## State and Persistence Behavior
The dispatcher stores an in-memory handler map and metrics source. It does not persist data. `stop()` delegates shutdown to each handler and unregisters command-handler metrics.

## Dependencies and Integration Points
It depends on `CommandHandler`, `CommandHandlerMetrics`, `OzoneContainer`, `StateContext`, and `SCMConnectionManager`. It feeds `DatanodeQueueMetrics` through `getQueuedCommandCount()`.

## Risks
Unknown command types are dropped after logging. Handler exceptions are swallowed, so command-specific failure reporting must happen inside handlers. Duplicate handlers fail constructor build. Missing required builder fields fail with `Objects.requireNonNull`.

## Test Signals
Tests should assert duplicate handler rejection, unknown command logging, handler invocation by type, metrics increment, stop delegation, and queue counter aggregation for all registered handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandHandler.java

## Purpose
`CommandHandler` is the common interface for all datanode handlers of SCM commands.

## Important APIs and Types
Implementations must provide `handle()`, `getCommandType()`, invocation and latency metrics, and `getQueuedCount()`. Optional APIs include `stop()`, `getThreadPoolMaxPoolSize()`, and `getThreadPoolActivePoolSize()`. The default `updateCommandStatus()` updates command status in `StateContext` and logs if no entry exists.

## Control Flow
`CommandDispatcher` invokes `handle()` after selecting by `getCommandType()`. Async handlers use `getQueuedCount()` for queue metrics and override `stop()` to drain or stop internal executors.

## State and Persistence Behavior
The interface has no state. The default command-status helper mutates `StateContext.cmdStatusMap`, which is later reported back to SCM in command status reports.

## Dependencies and Integration Points
It ties handlers to `SCMCommandProto.Type`, `SCMCommand`, `OzoneContainer`, `StateContext`, and `SCMConnectionManager`. It also defines the metric contract consumed by `CommandHandlerMetrics` and `DatanodeQueueMetrics`.

## Risks
No return value or checked exception contract exists for `handle()`, so failures are usually logged and handled asynchronously. Implementations must keep metrics and queue counts consistent manually.

## Test Signals
Tests should validate the default status update helper, default thread-pool values, and that each concrete handler reports the command type it is registered under.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CreatePipelineCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CreatePipelineCommandHandler.java

## Purpose
Handles SCM create-pipeline commands by creating a local write-channel group and propagating Ratis group creation to peer datanodes.

## Important APIs and Types
Implements `CommandHandler` for `createPipelineCommand`. It uses injected Ratis client factory and executor, per-pipeline in-progress deduplication, queue/invocation counts, and latency metrics.

## Control Flow
`handle()` casts the command, deduplicates by pipeline UUID, schedules async work, checks if the local write channel already has the pipeline, constructs a `RaftGroup` from peer datanodes and priorities, calls `server.addGroup()`, then sends group-management `add()` to peer Raft servers except itself. `AlreadyExistsException` is benign.

## State and Persistence Behavior
Persistent state changes happen in the write channel/Ratis group storage. The handler maintains only in-memory queue count, invocation count, metrics, and in-progress UUID set.

## Dependencies and Integration Points
It uses `OzoneContainer.getWriteChannel()`, `RatisHelper`, `RaftClient`, peer `DatanodeDetails`, TLS config, and `PipelineID`.

## Risks
Peer group creation is best-effort: IO failures are warnings after local add may have succeeded. The in-progress marker must be cleared on all completion and rejection paths. Existing local groups cause a silent no-op, which is idempotent but can hide partial peer propagation.

## Test Signals
Tests should verify local add, peer propagation, duplicate suppression, already-exists handling, rejection cleanup, queue count decrement, and behavior when the pipeline already exists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CreatePipelineCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteBlocksCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteBlocksCommandHandler.java

## Purpose
`DeleteBlocksCommandHandler` processes SCM delete-block commands by marking block metadata for asynchronous deletion and updating delete-block command status ACKs back to SCM.

## Important APIs and Types
Implements `CommandHandler` for `deleteBlocksCommand`. It owns a bounded `LinkedBlockingQueue<DeleteCmdInfo>`, a daemon `DeleteCmdWorker`, a fixed transaction executor, `ProcessTransactionTask`, `DeleteBlockTransactionExecutionResult`, schema-specific `SchemaHandler`s, and `BlockDeletingServiceMetrics`. Test-visible APIs include `executeCmdWithRetry()`, `submitTasks()`, `getSchemaHandlers()`, `getBlockDeleteMetrics()`, and `setPoolSize()`.

## Control Flow
`handle()` enqueues a delete command; if the queue is full, it marks the command failed with an empty ACK. The worker drains queued commands and calls `processCmd()`. Processing summarizes transactions, records metrics, submits per-transaction tasks, retries lock-acquisition failures once, builds a `ContainerBlocksDeletionACKProto`, and updates the `DeleteBlockCommandStatus` as executed or failed.

## State and Persistence Behavior
For key-value containers, each transaction tries to acquire the container write lock with a configured timeout. It rechecks `ContainerSet` after locking to avoid acting on stale container objects after DiskBalancer moves. Schema v1 moves block entries to deleting keys and deletes unreferenced files; schemas v2 and v3 write delete-transaction tables using different key types. Metadata updates include latest delete transaction ID, pending delete block count, and optionally pending delete bytes after layout-feature finalization.

## Dependencies and Integration Points
It integrates with `ContainerSet`, `KeyValueContainerData`, `BlockUtils`, `DeleteTransactionStore`, RocksDB batch operations, `VersionedDatanodeFeatures`, command status reports, block deletion metrics, and `OzoneContainer` dispatchers.

## Risks
This is concurrency and persistence sensitive. Lock timeouts lead to one retry, then failed transaction ACKs. Duplicate and out-of-order transaction logic is based on in-memory container delete transaction ID. Schema-specific table keys must match container DB layout. Queue overflow fails the command immediately. Errors in `processCmd()` still run the status updater in `finally`, but an ACK may be null on failure.

## Test Signals
Tests should cover queue overflow status, schema v1/v2/v3 marking, duplicate and out-of-order transactions, lock timeout retry, stale container after DiskBalancer move, metadata counter updates, pending-byte feature gating, command ACK contents, worker shutdown, and executor resizing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteBlocksCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteContainerCommandHandler.java

## Purpose
Handles SCM delete-container commands by scheduling container deletion on a bounded executor.

## Important APIs and Types
Implements `CommandHandler` for `deleteContainerCommand`. It tracks invocation count, timeout count, queue size, executor pool sizes, and latency. The protected constructor allows injecting a clock and executor for tests.

## Control Flow
`handle()` casts the command and submits `handleInternal()` to the executor. Rejected submissions are logged and dropped. `handleInternal()` checks the command deadline with the injected `Clock`, ignores stale SCM leader terms using `StateContext.getTermOfLeaderSCM()`, then calls `ContainerController.deleteContainer(containerID, force)`.

## State and Persistence Behavior
Container deletion and metadata/file cleanup are delegated to `ContainerController`. The handler only stores counters and metrics. Deadline expiration increments `timeoutCount`.

## Dependencies and Integration Points
It integrates with `OzoneContainer.getController()`, `DeleteContainerCommand`, `StateContext` leader-term tracking, and datanode configuration for thread and queue sizing.

## Risks
Rejected commands are logged but no command status is updated. Term filtering relies on the context term having been initialized. A command that waits too long is skipped so SCM can resend, which depends on SCM retry behavior. Force delete can remove containers in states that normal delete would reject at lower layers.

## Test Signals
Tests should cover deadline skip, stale-term skip, force flag propagation, rejection handling, queue and active pool metrics, timeout count, and graceful executor stop.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/FinalizeNewLayoutVersionCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/FinalizeNewLayoutVersionCommandHandler.java

## Purpose
Handles SCM finalization commands that tell the datanode to finalize a new layout version after an upgrade.

## Important APIs and Types
Implements `CommandHandler` for `finalizeNewLayoutVersionCommand`. It reads `FinalizeNewLayoutVersionCommandProto`, checks `DatanodeStateMachine.getLayoutVersionManager().getUpgradeState()`, and invokes `DatanodeStateMachine.finalizeUpgrade()` when finalization is required.

## Control Flow
The handler runs synchronously in the command processor thread. It increments invocation count, checks the boolean `finalizeNewLayoutVersion`, verifies the local upgrade state is `FINALIZATION_REQUIRED`, and calls finalization. Exceptions are logged and not rethrown.

## State and Persistence Behavior
Persistent effects are in the upgrade finalizer and layout-version storage. The handler itself only stores metrics.

## Dependencies and Integration Points
It integrates with datanode layout-version management, `DataNodeUpgradeFinalizer`, SCM upgrade protocol commands, and command-handler metrics.

## Risks
Because it is synchronous, slow finalization setup could delay other command dispatching. Exceptions only log, so SCM must continue sending finalization commands until state converges. Multiple commands are guarded by checking upgrade state.

## Test Signals
Tests should verify finalization is invoked only when the command flag is true and state is `FINALIZATION_REQUIRED`, idempotent repeated command behavior, exception logging, and metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/FinalizeNewLayoutVersionCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconcileContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconcileContainerCommandHandler.java

## Purpose
Handles SCM reconcile-container commands by submitting a reconciliation task that compares and repairs a local container replica against peer replicas.

## Important APIs and Types
Implements `CommandHandler` for `reconcileContainerCommand`. It holds a `ReplicationSupervisor` and `DNContainerOperationClient`. `handle()` creates `ReconcileContainerTask`, while metric methods proxy supervisor counters under `ReconcileContainerTask.METRIC_NAME`.

## Control Flow
The dispatcher invokes `handle()`, which casts the command, constructs a task with the container controller and datanode operation client, and queues it in the supervisor. Actual network checks and repair flow are handled by `ReconcileContainerTask`.

## State and Persistence Behavior
This handler has no durable state. Reconciliation side effects are delegated to the task and container controller. Queue state lives in `ReplicationSupervisor`.

## Dependencies and Integration Points
It integrates with the checksum/reconciliation package, `DNContainerOperationClient`, `OzoneContainer.getController()`, and the shared replication supervisor lane.

## Risks
No local validation beyond cast occurs. Failures and backpressure depend entirely on supervisor/task behavior. It shares supervisor resources with replication and EC tasks, so starvation or queue limits matter outside this file.

## Test Signals
Tests should assert task construction, supervisor submission, command type, metric-name propagation, and queued/invocation/latency values from the supervisor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconcileContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconstructECContainersCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconstructECContainersCommandHandler.java

## Purpose
Handles SCM EC reconstruction commands by submitting erasure-coded reconstruction tasks to the replication supervisor.

## Important APIs and Types
Implements `CommandHandler` for `reconstructECContainersCommand`. It stores `ConfigurationSource`, `ReplicationSupervisor`, and `ECReconstructionCoordinator`. `handle()` creates `ECReconstructionCommandInfo` and `ECReconstructionCoordinatorTask`. Metrics proxy supervisor values using `ECReconstructionCoordinatorTask.METRIC_NAME`.

## Control Flow
Command dispatch synchronously creates the reconstruction task and queues it with the supervisor. EC reconstruction execution, downloads, reconstruction, and writes are performed by the coordinator task outside this handler.

## State and Persistence Behavior
No durable state is written directly. Reconstruction task execution can create or repair EC container replicas via the coordinator.

## Dependencies and Integration Points
It integrates with `ECReconstructionCoordinator`, `ECReconstructionCommandInfo`, `ReplicationSupervisor`, and SCM EC command protobuf wrappers. The state machine constructs it once so tests can mock it in mini-cluster scenarios.

## Risks
No validation or queue handling is local; all backpressure and failures are supervisor-level. Reconstruction can be resource-heavy, so metrics and queue counts are important operational signals.

## Test Signals
Tests should verify command casting, task submission, metric proxy values, config accessor, and behavior under supervisor queue saturation if applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconstructECContainersCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/RefreshVolumeUsageCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/RefreshVolumeUsageCommandHandler.java

## Purpose
Handles SCM refresh-volume-usage commands by forcing all datanode volumes to refresh usage accounting.

## Important APIs and Types
Implements `CommandHandler` for `refreshVolumeUsageInfo`. It keeps invocation count and latency metrics. `handle()` calls `container.getVolumeSet().refreshAllVolumeUsage()`.

## Control Flow
The handler runs synchronously in the command processor thread. It logs receipt, increments invocation count, refreshes all volume usage, and records elapsed time.

## State and Persistence Behavior
It does not persist data directly. It refreshes in-memory or cached usage information in the volume set, which affects subsequent reports and volume selection.

## Dependencies and Integration Points
It depends on `OzoneContainer.getVolumeSet()` and the volume-set implementation. It participates in command-handler and queue metrics with zero internal queue.

## Risks
Synchronous refresh could delay command processing if volume usage scanning is slow. Exceptions are not caught locally, but `CommandDispatcher` catches handler exceptions and logs them.

## Test Signals
Tests should verify command type, invocation count, `refreshAllVolumeUsage()` call, latency metric update, and dispatcher-level exception handling for volume-set failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/RefreshVolumeUsageCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReplicateContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReplicateContainerCommandHandler.java

## Purpose
Handles SCM replicate-container commands by creating a replication task using either pull/download replication or push/upload replication.

## Important APIs and Types
Implements `CommandHandler` for `replicateContainerCommand`. It stores a `ReplicationSupervisor`, a download `ContainerReplicator`, a push `ContainerReplicator`, and proxies metrics under `ReplicationTask.METRIC_NAME`.

## Control Flow
`handle()` casts the command, reads source datanodes, target datanode, and container ID, validates that at least sources or target exist, picks pull replication when target is null or push replication when target is present, creates `ReplicationTask`, and adds it to the supervisor.

## State and Persistence Behavior
The handler has no durable state. Actual container import/export and metadata changes happen inside the selected replicator and task.

## Dependencies and Integration Points
It integrates with `ReplicationSupervisor`, `ReplicationTask`, pull and push `ContainerReplicator` implementations, and SCM replication commands. It shares supervisor capacity with EC reconstruction and reconciliation tasks.

## Risks
Invalid commands throw `IllegalArgumentException`, which is caught by the dispatcher and logged. Replicator selection depends only on target presence, so command semantics must remain consistent. Queue pressure is external to this handler.

## Test Signals
Tests should verify pull vs push selection, precondition failure for missing sources and target, supervisor task submission, metric proxy values, and command type registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReplicateContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/SetNodeOperationalStateCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/SetNodeOperationalStateCommandHandler.java

## Purpose
Handles SCM set-node-operational-state commands by persisting the datanode operational state and notifying services that depend on node state.

## Important APIs and Types
Implements `CommandHandler` for `setNodeOperationalStateCommand`. It stores configuration, a replication-supervisor state consumer, an optional disk-balancer state consumer, invocation count, and latency metric. Private helpers `persistUpdatedDatanodeDetails()` and `persistDatanodeDetails()` write the updated datanode ID file.

## Control Flow
`handle()` validates command type, extracts `SetNodeOperationalStateCommandProto`, copies the current `DatanodeDetails`, updates persisted operation state and expiry, writes it to the configured datanode ID file, updates the live `DatanodeDetails`, notifies disk balancer if present, notifies replication supervisor, and records latency.

## State and Persistence Behavior
This handler directly persists `DatanodeDetails` to the datanode ID file via `ContainerUtils.writeDatanodeDetailsTo()`. It also mutates the in-memory `DatanodeDetails` after a successful write.

## Dependencies and Integration Points
It integrates with `HddsServerUtil.getDatanodeIdFilePath()`, `ContainerUtils`, `ReplicationSupervisor.nodeStateUpdated`, optional disk balancer service, and SCM operational-state commands.

## Risks
Persistence failure is logged but not propagated, and service consumers are still notified after the catch block. The TODO notes duplicate persistence logic with `HddsDatanodeService` and `InitDatanodeState`. If write succeeds but later mutation or notification fails, state can diverge.

## Test Signals
Tests should verify file persistence, in-memory state update, expiry propagation, disk balancer optional callback, supervisor callback, wrong command type handling, and behavior when persistence throws.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/SetNodeOperationalStateCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java

## Purpose
Package documentation for `org.apache.hadoop.ozone.container.common.statemachine.commandhandler`.

## Important APIs and Types
The package contains `CommandHandler`, `CommandDispatcher`, and concrete SCM command handlers for close/delete container, close/create pipeline, delete blocks, replication, EC reconstruction, reconciliation, volume usage refresh, layout finalization, and node operational-state persistence.

## Control Flow
The package-level role is to receive commands drained from `StateContext` by `DatanodeStateMachine`, dispatch by protobuf command type, and either execute synchronously or enqueue work in specialized executors/supervisors.

## State and Persistence Behavior
Persistence is implemented by individual handlers, especially container state changes, block delete metadata, datanode ID file updates, and upgrade finalization. The package marker itself has no state.

## Dependencies and Integration Points
The package integrates the state machine with `OzoneContainer`, SCM protocol command wrappers, Ratis pipelines, replication supervisor, EC reconstruction coordinator, volume sets, and layout finalization.

## Risks
The package boundary contains both quick synchronous commands and resource-heavy async commands. Handler registration in `DatanodeStateMachine` must remain aligned with SCM command types.

## Test Signals
Package-level tests should focus on dispatcher coverage for every supported command type and handler-specific queue/metrics behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/package-info.java

## Purpose
Package documentation for the datanode state-machine package. It describes the container-service state flow as start through get-version, register, running, and shutdown, and notes that the state machine also handles command processing.

## Important APIs and Types
Important types in the package include `DatanodeStateMachine`, `StateContext`, `SCMConnectionManager`, `EndpointStateMachine`, queue metrics, MXBeans, and datanode configuration.

## Control Flow
At runtime, the state machine initializes SCM/Recon connections, advances endpoint states through version/register/heartbeat tasks, sends reports, receives SCM commands, and dispatches command handling.

## State and Persistence Behavior
Persistent side effects are delegated to runtime classes: datanode ID file persistence, layout-version storage, container state/metadata changes, and command ACK state. The package file itself has no state.

## Dependencies and Integration Points
This package is the bridge between HDDS datanode service lifecycle, SCM protocol endpoints, report publishing, command handlers, Ozone container storage, metrics, and JMX.

## Risks
The package comment is shorter than the current implementation and still mentions `GetVersion` and `Register` as package-level state flow while the datanode enum itself is `INIT/RUNNING/SHUTDOWN`; endpoint tasks carry the finer-grained endpoint states.

## Test Signals
Documentation consistency should be checked against the actual datanode and endpoint state enums when state transitions evolve.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/DatanodeState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/DatanodeState.java

## Purpose
`DatanodeState<T>` is the lifecycle interface for executable datanode state tasks.

## Important APIs and Types
Implementations must define `onEnter()`, `onExit()`, `execute(ExecutorService)`, and `await(long, TimeUnit)`. The generic return type `T` is the next state type, used by datanode tasks as `DatanodeStateMachine.DatanodeStates`. `clear()` is a default no-op cleanup hook.

## Control Flow
`StateContext.execute()` obtains the current task, calls `onEnter()` when entering a state, calls `execute()` with the state-machine executor, waits through `await()`, runs `onExit()` on state transition, sets the new state, and finally invokes `clear()`.

## State and Persistence Behavior
The interface stores no state. Implementations may hold futures or resources and may trigger persistence, such as `InitDatanodeState` writing datanode details.

## Dependencies and Integration Points
It integrates `StateContext` with concrete datanode states under `states.datanode` and uses Java executor/future timeout primitives.

## Risks
The interface notes `execute()` is unsafe to call concurrently; callers must serialize it. Implementations must handle `await()` timeout and cleanup correctly or the state machine can stall.

## Test Signals
Tests should exercise `StateContext.execute()` against fake implementations to verify lifecycle hook order, transition handling, timeout propagation, and `clear()` invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/DatanodeState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/InitDatanodeState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/InitDatanodeState.java

## Purpose
`InitDatanodeState` performs datanode startup initialization for SCM and Recon connections, endpoint registration in `StateContext`, and datanode ID persistence.

## Important APIs and Types
It implements both `DatanodeState` and `Callable<DatanodeStateMachine.DatanodeStates>`. Key methods are `call()`, `persistContainerDatanodeDetails()`, `execute()`, and `await()`. It holds `SCMConnectionManager`, `ConfigurationSource`, `StateContext`, and the submitted future.

## Control Flow
`execute()` submits the instance to the state-machine executor. `call()` resolves SCM addresses from configuration, returns `SHUTDOWN` on invalid or empty address lists, postpones initialization by returning the current state when any SCM address is unresolved, adds SCM endpoints to the connection manager and context, optionally adds Recon, persists datanode details, and returns the next datanode state.

## State and Persistence Behavior
The state persists `DatanodeDetails` to the configured datanode ID file using `ContainerUtils.writeDatanodeDetailsTo()`. If persistence fails, it sets context state to `SHUTDOWN`. Endpoint state is added in both `SCMConnectionManager` and `StateContext`.

## Dependencies and Integration Points
It depends on `HddsServerUtil.getSCMAddressForDatanodes()`, `getReconAddressForDatanodes()`, datanode ID file config, `SCMConnectionManager`, and `StateContext`. It is selected by `StateContext.getTask()` when the datanode state is `INIT`.

## Risks
SCM endpoints are added before datanode ID persistence, so a persistence failure can leave endpoint resources created during shutdown. If adding an endpoint to the connection manager succeeds but context addition fails later, state can diverge. Unresolved SCM addresses postpone all initialization.

## Test Signals
Tests should cover invalid/empty SCM address shutdown, unresolved-address retry behavior, SCM and Recon endpoint additions, datanode ID file write success and failure, future submission/await, and next-state transition to `RUNNING`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/InitDatanodeState.java -->
