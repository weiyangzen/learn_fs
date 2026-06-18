# Research: subset-b-008123

This grouped report covers the Recon SCM, security, SPI, and selected SPI implementation files listed for `subset-b-008123`. Each file section is source-tree-aligned and bounded by the required markers for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerManager.java

Purpose: `ReconContainerManager` is Recon's subclass of SCM `ContainerManagerImpl`. It adapts SCM container state management for a passive Recon process that learns containers from DataNode reports and SCM RPCs instead of allocating containers itself.

Important APIs and types: the constructor wires the SCM container table, `PipelineManager`, `StorageContainerServiceProvider`, `ContainerHealthSchemaManager`, `ReconContainerMetadataManager`, HA stubs, sequence IDs, and pending replica ops. `checkAndAddNewContainer` and `checkAndAddNewContainerBatch` verify missing containers against SCM and add them. `transitionOpenToClosing` updates lifecycle state and the local `pipelineToOpenContainer` counter. `addNewContainer` persists a `ContainerInfo` into the SCM state manager and optionally adds the container to a pipeline. Replica APIs override `updateContainerReplica` and `removeContainerReplica` to maintain historical replica placement.

Control flow: FCR and ICR handlers call `checkAndAddNewContainerBatch` before delegating to shared SCM report processing. The batch path partitions replicas into known and unknown containers. Unknown IDs are verified through `StorageContainerServiceProvider.getExistContainerWithPipelinesInBatch`; verified entries are added through `addNewContainer`. Known containers are checked for Recon-specific OPEN-to-CLOSING pre-processing before the parent handlers apply normal state-machine logic. OPEN containers with non-OPEN healthy replicas are finalized to CLOSING so Recon does not keep stale OPEN state after SCM has progressed.

State and persistence: SCM container metadata is stored in the RocksDB table supplied by `ReconSCMDBDefinition.CONTAINERS` through the inherited state manager. Recon also keeps `replicaHistoryMap`, a concurrent in-memory map from container ID to datanode ID and `ContainerReplicaHistory`; first sightings and removals are flushed into the Recon container metadata DB via `ReconContainerMetadataManager`. `flushReplicaHistoryMapToDB` persists all in-memory history on shutdown. `pipelineToOpenContainer` tracks open-container counts per pipeline for APIs; it is updated on add and OPEN-to-CLOSING transitions.

Dependencies and integration points: depends on SCM classes for lifecycle validation, pipeline state, replica storage, and container state transitions; depends on Recon DB managers for historical and health metadata; depends on `StorageContainerServiceProvider` for authoritative SCM verification. `ReconStorageContainerSyncHelper` calls `transitionOpenToClosing`, `deleteContainer`, `updateContainerState`, and `addNewContainer` during targeted SCM sync. API endpoints use `getAllContainerHistory`, `getLatestContainerHistory`, and the open-container map.

Risks and edge cases: `checkAndAddNewContainerBatch` groups via `parallelStream` while calling `containerExist`; existence and add are still non-atomic, so `addNewContainer` must tolerate duplicate races. OPEN containers without pipelines are recorded but cannot update pipeline tracking, which may affect open-container counts. Replica history writes can fail silently at debug level, leaving only in-memory data until shutdown. `upsertContainerHistory` updates state/checksums but only sets `bcsId` on new entries, so later BCS changes may rely on the in-memory merge path unless persisted elsewhere.

Test signals: direct SCM facade and integration tests reference container sync paths (`TestReconStorageContainerManagerFacade`, `TestReconSCMContainerSyncIntegration`), and API tests exercise container history/open-count behavior (`TestContainerEndpoint`, `TestOpenContainerCount`). Strong tests should cover duplicate add races, null-pipeline non-OPEN adds, OPEN-to-CLOSING counter decrement, and shutdown flushing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportHandler.java

Purpose: this handler customizes SCM's full container report handling for Recon by ensuring Recon learns any containers missing from its local SCM DB before normal FCR processing runs.

Important APIs and types: it extends `ContainerReportHandler`, overrides `getLogger`, and overrides `onMessage(ContainerReportFromDatanode, EventPublisher)`. It casts `getContainerManager()` to `ReconContainerManager` and uses `ContainerReplicaProto` entries from the full report.

Control flow: on each full report, the handler extracts the report's replica list, calls `ReconContainerManager.checkAndAddNewContainerBatch`, and then invokes `super.onMessage` so SCM's shared report processor can update replicas and lifecycle state. This ordering is important because the parent handler expects containers to exist locally.

State and persistence: the handler owns no durable state. Persistence happens indirectly through `ReconContainerManager`, which writes container entries, pipeline membership, and replica history to Recon's RocksDB-backed managers.

Dependencies and integration points: registered in `ReconStorageContainerManagerFacade` under `SCMEvents.CONTAINER_REPORT` using a fixed thread pool with affinity shared with ICR events. It integrates with `ReconContainerReportQueue`, which can merge adjacent ICRs but preserves FCR ordering.

Risks and edge cases: the unconditional cast requires the facade to supply a `ReconContainerManager`. If SCM verification of missing containers fails, parent processing may still see unknown containers and log or skip according to shared SCM behavior. Large FCRs rely on the batch path in `ReconContainerManager` for scalability.

Test signals: no isolated test was found for this class, but container report behavior is indirectly covered by Recon SCM and container endpoint tests. Useful focused tests would verify "add before super" behavior for unknown containers and that exceptions from the add path do not corrupt later report handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportQueue.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportQueue.java

Purpose: `ReconContainerReportQueue` customizes SCM's `ContainerReportQueue` so Recon can coalesce adjacent incremental container reports in the same queue slot.

Important APIs and types: the constructor delegates queue size to the parent. `mergeIcr(ContainerReport, List<ContainerReport>)` checks the last queued report type and calls `mergeReport` when the last item is an ICR.

Control flow: enqueue logic in the parent calls `mergeIcr`. Recon merges a new ICR only with the most recent queued ICR, preventing repeated ICR events from creating unnecessary queue pressure while avoiding merges across other report types.

State and persistence: no durable state. The only state is the in-memory queue owned by the parent class and the mutable `ContainerReport` payload created by `mergeReport`.

Dependencies and integration points: `ReconUtils.initContainerReportQueue` is used by `ReconStorageContainerManagerFacade` to create report queues for the fixed-affinity executor handling FCR/ICR events.

Risks and edge cases: merging only the last ICR is simple but assumes parent queue ordering remains meaningful. If `mergeReport` grows very large, a burst from one datanode can still create a large single payload. FCRs are not merged, preserving full-report semantics.

Test signals: no direct class test was found. Tests should cover adjacent ICR merge, no merge when the previous item is an FCR, and preservation of report type ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDatanodeProtocolServer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDatanodeProtocolServer.java

Purpose: this class exposes Recon's DataNode-facing protocol by subclassing SCM's datanode protocol server and substituting Recon-specific binding, protocol, metrics, and authorization policy.

Important APIs and types: it implements `ReconDatanodeProtocol`, returns `ProtocolMessageMetrics` named `ReconDatanodeProtocol`, uses `OZONE_RECON_DATANODE_ADDRESS_KEY`, binds with `HddsServerUtil.getReconDataNodeBindAddress`, returns `ReconPolicyProvider`, and exposes `ReconDatanodeProtocolPB`.

Control flow: constructed by `ReconStorageContainerManagerFacade` with the facade as the SCM implementation and its `EventQueue` as the publisher. Parent server code handles RPC lifecycle; this subclass supplies the Recon-specific overrides.

State and persistence: no local persistence. Runtime RPC metrics are created for protocol message accounting.

Dependencies and integration points: feeds datanode heartbeats, reports, node reports, and pipeline reports into the event queue configured by the facade. Authorization integrates with Hadoop `PolicyProvider` through `ReconPolicyProvider`.

Risks and edge cases: incorrect address configuration can cause DataNodes to report to the wrong endpoint. The constructor passes `null` for the optional dependency accepted by the SCM parent; compatibility depends on the parent continuing to allow this mode. Policy coverage is only for the Recon datanode protocol.

Test signals: endpoint and SCM facade tests generally mock or instantiate the facade rather than this server directly. Focused tests should validate address-key selection, protocol class, and policy provider when Hadoop security is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDatanodeProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDeadNodeHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDeadNodeHandler.java

Purpose: `ReconDeadNodeHandler` extends SCM's dead-node processing with Recon-specific reconciliation against SCM and immediate refresh of health/pipeline background tasks.

Important APIs and types: constructor accepts `NodeManager`, `PipelineManager`, `ContainerManager`, `StorageContainerServiceProvider`, a container-health `ReconScmTask`, and `PipelineSyncTask`. `onMessage(DatanodeDetails, EventPublisher)` is the main hook.

Control flow: the handler first delegates to `DeadNodeHandler` for normal SCM node/pipeline/container cleanup. It then pulls all SCM nodes through `scmClient.getNodes`, matches by UUID, updates Recon node operational state if SCM has a record, and triggers `containerHealthTask.initializeAndRunTask()` plus `pipelineSyncTask.initializeAndRunTask()`.

State and persistence: state changes happen through `ReconNodeManager.updateNodeOperationalStateFromScm`, which updates in-memory node status and datanode details; pipeline and container-health tasks persist through their own managers and SQL/DB tables.

Dependencies and integration points: registered for `SCMEvents.DEAD_NODE` by the facade. It depends on the SCM service provider for authoritative node operational state and on background tasks to recompute derived health data after the node transition.

Risks and edge cases: `getNodes()` fetches the full SCM node list and scans it on each dead-node event, which may be costly in large clusters. If SCM lacks the node, Recon logs a warning and proceeds with task triggers. Exceptions skip both task refreshes because all post-super work is in one try block.

Test signals: no direct test was found. Good coverage would mock SCM node states, assert operational-state correction, and verify health/pipeline tasks are triggered after dead events and not before parent processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDeadNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconIncrementalContainerReportHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconIncrementalContainerReportHandler.java

Purpose: Recon's ICR handler ensures newly reported containers are known locally before SCM's incremental report logic processes replica updates.

Important APIs and types: extends `IncrementalContainerReportHandler`, overrides `getLogger`, and overrides `onMessage(IncrementalContainerReportFromDatanode, EventPublisher)`. Uses inherited `getDatanodeDetails` and `processICR`.

Control flow: `onMessage` resolves the reporting datanode; if missing, it returns. It then calls `ReconContainerManager.checkAndAddNewContainerBatch` on ICR replicas. On success, it delegates to `processICR` with the resolved datanode; on exception, it logs and returns without applying the ICR.

State and persistence: no owned state. Container additions, lifecycle updates, and replica history are persisted through `ReconContainerManager` and inherited SCM processing.

Dependencies and integration points: registered by the facade under `SCMEvents.INCREMENTAL_CONTAINER_REPORT` using the same affinity executor pool as FCR handling, so FCR-first ordering by datanode can be maintained by the dispatcher/executor setup.

Risks and edge cases: unlike the FCR handler, an exception during pre-add aborts the whole ICR. This avoids parent processing unknown containers but can drop valid replica changes in the same ICR. The cast to `ReconContainerManager` assumes facade wiring.

Test signals: indirect integration tests cover SCM container sync; a focused ICR test should cover unknown container backfill, null datanode early return, and error behavior when SCM verification fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconIncrementalContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNewNodeHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNewNodeHandler.java

Purpose: `ReconNewNodeHandler` persists newly registered DataNodes into Recon's SCM node DB asynchronously from the event path.

Important APIs and types: implements `EventHandler<DatanodeDetails>`, stores a `ReconNodeManager`, and implements `onMessage(DatanodeDetails, EventPublisher)`.

Control flow: when `SCMEvents.NEW_NODE` fires, the handler calls `nodeManager.addNodeToDB`. Errors are logged and not rethrown, so event processing continues.

State and persistence: writes `DatanodeDetails` keyed by `DatanodeID` to the `NODES` column family in `ReconSCMDBDefinition`.

Dependencies and integration points: registered by `ReconStorageContainerManagerFacade`. Works with `ReconNodeManager.register`, which handles in-memory registration and may update existing DB entries; this handler covers the new-node DB insert after registration.

Risks and edge cases: failures leave a node in memory but absent from DB, so it may be lost across restart until it re-registers. The class stores its manager in a mutable non-final field, but it is initialized once in practice.

Test signals: no direct test was found. Useful tests would assert DB insertion on event and non-fatal logging on `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNewNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNodeManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNodeManager.java

Purpose: `ReconNodeManager` is Recon's persistent node manager. It subclasses SCM's `SCMNodeManager` but restricts commands and stores DataNode identity in Recon's SCM DB.

Important APIs and types: constructors accept `OzoneConfiguration`, `SCMStorageConfig`, event queue/publisher, `NetworkTopology`, the `NODES` table, layout manager, and optionally `ReconContext`. Key methods include `loadExistingNodes`, `addNodeToDB`, `processHeartbeat`, `register`, `updateNodeOperationalStateFromScm`, `reinitialize`, `removeNode`, and `sendFinalizeToDatanodeIfNeeded`.

Control flow: on startup, `loadExistingNodes` iterates the persisted node table and registers each node in memory using max layout versions. Heartbeats update `datanodeHeartbeatMap`; if a node is new or has not refreshed within three Recon heartbeat intervals, Recon asks it to re-register. Command processing only passes `reregisterCommand` to the parent and filters all other commands. Registration updates the DB for already-known nodes, delegates to parent registration, and updates `ReconContext` health based on topology validity.

State and persistence: durable state is `nodeDB`, a RocksDB table keyed by `DatanodeID`. Runtime state includes inherited node state structures and `datanodeHeartbeatMap`. `removeNode` deletes both parent in-memory state and DB entry. `reinitialize` swaps the table handle after SCM snapshot replacement and reloads nodes.

Dependencies and integration points: used by the facade, DataNode protocol server, node report handler, stale/dead/new-node handlers, pipeline manager, placement policy, and Recon APIs. `ReconDeadNodeHandler` calls `updateNodeOperationalStateFromScm` to align operational state with authoritative SCM.

Risks and edge cases: `loadExistingNodes` calls `register` with null reports; parent assumptions must remain compatible. `datanodeHeartbeatMap` is a `HashMap` accessed from heartbeat/event threads without synchronization, which is a concurrency risk. Only reregister commands are allowed, so any future command needed by Recon must be explicitly added. Invalid topology errors update global health and return an error response rather than throwing.

Test signals: API and SCM facade tests instantiate or mock the facade that owns this manager. Focused tests should cover restart reload from `NODES`, heartbeat reregister threshold, command filtering, invalid topology health updates, and concurrent heartbeat safety.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineFactory.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineFactory.java

Purpose: this factory prevents Recon from creating or reading pipelines through SCM's pipeline provider path. Recon is a passive observer and should only ingest pipelines from SCM.

Important APIs and types: extends `PipelineFactory`, installs a defaulted map with `ReconPipelineProvider`, and defines provider methods for `create`, `createForRead`, and `close`.

Control flow: any attempt to create a pipeline or create a read pipeline throws `UnsupportedOperationException` with a clear Recon-specific message. `close` is a no-op.

State and persistence: no state or persistence. Its role is behavioral enforcement for `ReconPipelineManager`.

Dependencies and integration points: constructed by `ReconPipelineManager.newReconPipelineManager` and passed into `PipelineManagerImpl`. Normal Recon pipeline additions bypass creation and use `ReconPipelineManager.addPipeline` with SCM-supplied protobufs.

Risks and edge cases: if inherited SCM manager code unexpectedly calls `createForRead`, Recon will fail fast. This is intentional but can surface during upstream SCM behavior changes. The no-op close means pipeline removal must be handled by manager state operations.

Test signals: no direct test was found. Tests should assert all create paths throw and that manager initialization with this factory still permits SCM-sourced pipeline insertion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineManager.java

Purpose: `ReconPipelineManager` is Recon's passive pipeline metadata manager, backed by SCM's pipeline state machinery but with creation disabled and explicit SCM-sourced initialization.

Important APIs and types: `newReconPipelineManager` builds a `PipelineStateManagerImpl` from the pipeline table, node manager, HA/Ratis stubs, and DB transaction buffer, then uses `ReconPipelineFactory`. `initializePipelines`, `removeInvalidPipelines`, `addPipeline`, and `addContainerToPipeline` are the Recon-specific methods.

Control flow: `initializePipelines` takes the SCM pipeline list, adds missing pipelines, updates existing state and creation timestamp, then removes pipelines that are present locally but absent from SCM. Invalid non-closed pipelines are first marked closed before `closePipeline` and `deletePipeline`. `addPipeline` acquires a write lock and inserts the SCM protobuf if absent. `addContainerToPipeline` forces container association through the state manager.

State and persistence: pipeline state is persisted in the `PIPELINES` column family provided by `ReconSCMDBDefinition`. Container membership in pipelines is maintained through the inherited pipeline state manager. Reinitialization occurs indirectly from the facade after SCM DB snapshot replacement.

Dependencies and integration points: used by report handlers, stale/dead handlers, `PipelineSyncTask`, `ReconContainerManager`, and container/pipeline API surfaces. It depends on `ReconPipelineFactory` to prevent active SCM behavior.

Risks and edge cases: `pipelinesFromScm.contains(p)` relies on `Pipeline.equals`; if equality includes mutable fields, invalid-removal decisions may be surprising. Removing absent pipelines may lose historical pipeline metadata Recon might otherwise display. Forced container-to-pipeline association bypasses some parent validation to match passive ingestion needs.

Test signals: pipeline behavior is indirectly covered by SCM facade and sync tests. Focused tests should cover add idempotency, state/timestamp refresh, invalid pipeline removal, and forced container association.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineReportHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineReportHandler.java

Purpose: this handler processes DataNode pipeline reports in Recon, backfilling unknown pipelines from SCM before applying shared SCM report updates.

Important APIs and types: extends `PipelineReportHandler`, stores a `StorageContainerServiceProvider`, and overrides `processPipelineReport(PipelineReport, DatanodeDetails, EventPublisher)`.

Control flow: on a pipeline report, it derives `PipelineID`. If the pipeline is unknown locally, it calls `scmServiceProvider.getPipeline`; if SCM returns a remote `PipelineNotFoundException`, it rethrows that condition. Once the pipeline exists, it marks the reporting datanode and leader ID using inherited helpers. ALLOCATED pipelines are opened when the pipeline becomes healthy.

State and persistence: unknown pipelines fetched from SCM are persisted by `ReconPipelineManager.addPipeline`. Reported datanode and leader information are stored in the in-memory/persistent pipeline state managed by the parent.

Dependencies and integration points: registered by the facade for `SCMEvents.PIPELINE_REPORT`; works with `ReconPipelineManager`, `ReconSafeModeManager`, and SCM context. It is one of the ways Recon learns pipelines missed during startup or sync.

Risks and edge cases: an unknown pipeline that no longer exists in SCM produces a not-found path and may drop the report. Network or SCM RPC errors propagate to the event handler. Healthy transition from ALLOCATED to OPEN mirrors SCM behavior but in a passive context.

Test signals: no direct test was found. Useful tests should mock SCM pipeline lookup success, remote not-found unwrapping, and ALLOCATED healthy opening.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPolicyProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPolicyProvider.java

Purpose: `ReconPolicyProvider` supplies Hadoop service ACL metadata for Recon's datanode protocol.

Important APIs and types: extends `PolicyProvider`, exposes singleton `getInstance` through `MemoizedSupplier`, and returns one `Service` mapping `OZONE_RECON_SECURITY_CLIENT_DATANODE_CONTAINER_PROTOCOL_ACL` to `ReconDatanodeProtocol.class`.

Control flow: `ReconDatanodeProtocolServer.getPolicyProvider` returns this singleton. Hadoop RPC authorization calls `getServices` and receives a new array copy of the static service list.

State and persistence: no mutable state or persistence beyond the memoized singleton.

Dependencies and integration points: integrates with Hadoop security authorization and Recon's datanode RPC server. The ACL key comes from Recon config constants.

Risks and edge cases: only the datanode protocol is listed; additional Recon RPC protocols would need explicit service entries. Misconfigured ACLs affect DataNode communication with Recon.

Test signals: no direct test was found. A focused security test should assert that the service list contains exactly the Recon datanode protocol and expected ACL key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSCMDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSCMDBDefinition.java

Purpose: `ReconSCMDBDefinition` defines Recon's SCM RocksDB schema by extending SCM's DB schema with a Recon-specific node table and database name/location.

Important APIs and types: declares `RECON_SCM_DB_NAME`, `NODES`, `DATANODE_ID_CODEC`, `COLUMN_FAMILIES`, singleton `get`, `getName`, and `getLocationConfigKey`. `NODES` maps `DatanodeID` to `DatanodeDetails`.

Control flow: callers use `ReconSCMDBDefinition.get()` when creating/opening DB stores. The definition combines `SCMDBDefinition.get().getMap()` with `NODES`, so inherited SCM tables and Recon's node table are available from one DB.

State and persistence: defines persisted column families, not runtime state. The DB name is `recon-scm.db`; location is controlled by `OZONE_RECON_SCM_DB_DIR`.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade` to create and reopen DB stores, by `ReconNodeManager` for nodes, by `ReconContainerManager` for node lookups and containers, by `ReconPipelineManager` for pipelines, and by `SequenceIdGenerator`.

Risks and edge cases: schema compatibility depends on upstream `SCMDBDefinition`; adding the `NODES` table must not collide with upstream column family names. `DelegatedCodec` stores `DatanodeID` as UUID string; any format drift affects old DB reads.

Test signals: SCM facade tests indirectly exercise DB creation. Dedicated schema tests should assert all inherited SCM tables plus `nodes` are present and that DB location/name are Recon-specific.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSCMDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSafeModeManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSafeModeManager.java

Purpose: this is Recon's minimal `SafeModeManager` implementation. It tracks whether Recon SCM tasks should be considered in safe mode without implementing SCM's full safe-mode rule engine.

Important APIs and types: implements `SafeModeManager`, stores an `AtomicBoolean inSafeMode`, exposes `getInSafeMode`, and adds `setInSafeMode`.

Control flow: the facade creates this manager and passes it to pipeline report handling and `ReconSafeModeMgrTask`. On startup, regular Recon SCM tasks are started only if `getInSafeMode` is false.

State and persistence: one in-memory boolean, defaulting to true. There is no durable safe-mode state.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade`, `ReconPipelineReportHandler`, and `ReconSafeModeMgrTask`. It is a passive gate for tasks rather than a full SCM safety subsystem.

Risks and edge cases: default true means tasks will not start until another component clears safe mode. There are no listeners, rule details, or persisted transition records. External code must manage transitions correctly.

Test signals: no direct test was found. Tests should cover default state, setter visibility, and facade behavior when safe mode is true or false at startup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconScmTask.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconScmTask.java

Purpose: `ReconScmTask` is the abstract base for Recon background tasks that maintain SCM-derived metadata, such as pipeline sync, container health, and container size counts.

Important APIs and types: constructor obtains a `ReconTaskStatusUpdater` by task name. `start`, `stop`, `isRunning`, `canRun`, `getTaskName`, `getTaskStatusUpdater`, `initializeAndRunTask`, `run`, and `runTask` define the lifecycle.

Control flow: `start` creates a daemon thread named by the task class and runs the subclass `run` loop. `stop` clears `running` and notifies waiters. `initializeAndRunTask` records run start/completion around a single `runTask` invocation, used by event handlers for immediate recomputation.

State and persistence: runtime state is `taskThread` and volatile `running`. Persistent task status is delegated to `ReconTaskStatusUpdater`, which records timing/status in Recon task status storage.

Dependencies and integration points: extended by `PipelineSyncTask`, `ContainerHealthTask`, and `ContainerSizeCountTask`. `ReconStorageContainerManagerFacade` starts/stops tasks, while stale/dead handlers call `initializeAndRunTask` for immediate refresh.

Risks and edge cases: `isRunning` can return true for an alive thread even if `running` is false. `stop` does not interrupt the thread; subclasses must observe `canRun` and wait/notify correctly. `initializeAndRunTask` does not record failure completion if `runTask` throws unless callers handle it.

Test signals: task-specific tests cover subclasses such as `TestContainerHealthTask`. Base-class tests should cover lifecycle idempotency, daemon thread creation, and status updater calls around manual runs and exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconScmTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStaleNodeHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStaleNodeHandler.java

Purpose: `ReconStaleNodeHandler` extends SCM stale-node handling with an immediate pipeline metadata refresh in Recon.

Important APIs and types: extends `StaleNodeHandler`, stores `PipelineSyncTask`, and overrides `onMessage(DatanodeDetails, EventPublisher)`.

Control flow: the handler delegates to the parent stale-node logic, then calls `pipelineSyncTask.initializeAndRunTask`. Exceptions from the task are logged and swallowed.

State and persistence: no local state beyond the task reference. Parent logic updates node/pipeline runtime state; the pipeline sync task persists or updates pipeline metadata through its own manager.

Dependencies and integration points: registered by the facade for `SCMEvents.STALE_NODE`. It couples node liveness transitions to pipeline reconciliation because stale datanodes can affect pipeline health and membership.

Risks and edge cases: every stale-node event can trigger a full pipeline sync task, which may be expensive under churn. If the task fails, Recon logs but does not retry within this handler.

Test signals: no direct test was found. Useful tests should verify parent invocation order and that pipeline sync is triggered once per stale event with failure logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStaleNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageConfig.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageConfig.java

Purpose: `ReconStorageConfig` specializes SCM storage metadata for Recon, including Recon identity and the SCM-issued certificate serial number.

Important APIs and types: extends `SCMStorageConfig` with node type `RECON`. Constants are `RECON_CERT_SERIAL_ID` and `RECON_ID`. Methods include `setReconCertSerialId`, `setReconId`, `getReconId`, `getNodeProperties`, `getReconCertSerialId`, and `unsetReconCertSerialId`.

Control flow: the constructor uses `ReconUtils.getReconDbDir` and Recon storage config keys to locate storage. During initialization, `getNodeProperties` ensures a Recon UUID exists and includes the cert serial ID if present. `setReconId` refuses changes after storage is initialized.

State and persistence: properties are stored in the SCM storage version file via inherited `getStorageInfo`. Persisted values include Recon UUID and optional certificate serial ID.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade` to set cluster ID in `ReconContext` and by `ReconCertificateClient` to identify Recon to SCM's CA and retrieve existing certificate serial state.

Risks and edge cases: if `getReconId` is null, `getNodeProperties` generates a new UUID; operators must preserve the version file to keep a stable identity. Certificate serial management must stay consistent with certificate client callbacks.

Test signals: upgrade and initialization tests use the facade/storage path indirectly. Focused tests should cover UUID generation, initialized-state rejection, cert serial persistence/unset, and storage-dir resolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerManagerFacade.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerManagerFacade.java

Purpose: this facade is Recon's lightweight implementation of `OzoneStorageContainerManager`. It wires node, pipeline, container, datanode RPC, SCM snapshot, targeted container sync, replication-health, and Recon background tasks into a passive SCM-like service.

Important APIs and types: key fields include `ReconDatanodeProtocolServer`, `EventQueue`, `SCMContext`, `ReconContext`, `ReconNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `StorageContainerServiceProvider`, `ReconSafeModeManager`, `ReconReplicationManager`, and `ReconStorageContainerSyncHelper`. It defines `ScmDbSnapshotSyncStatus`, `ScmDbSnapshotSyncPhase`, and response DTOs for trigger/status/cancel. Public APIs include `start`, `join`, `stop`, `updateReconSCMDBWithNewSnapshot`, `triggerScmDbSnapshotSync`, `getScmDbSnapshotSyncStatus`, `cancelScmDbSnapshotSync`, `triggerSCMContainerSync`, and SCM manager getters.

Control flow: construction creates Recon SCM config overrides, storage config, DB store, layout manager, HA stubs, sequence ID generator, node/pipeline/container managers, datanode RPC server, report handlers, pipeline/node handlers, container-health/size tasks, pipeline sync task, safe-mode task, and event queue registrations. `start` optionally initializes the SCM DB from a snapshot based on count drift, starts periodic container sync with an atomic guard, starts RPC, starts the safe-mode manager task, and starts regular tasks only when out of safe mode. `stop` shuts down RPC, tasks, event queue, managers, flushes replica history, unregisters metrics, shuts down snapshot executor, and closes the DB store.

State and persistence: active SCM metadata lives in `recon-scm.db` using `ReconSCMDBDefinition`. Snapshot refresh preserves Recon's `NODES` table from the old DB, closes the old store, renames the snapshot to `recon-scm.db`, opens a new store, reinitializes sequence IDs, pipeline manager, container manager, and node manager, then cleans up the old DB. Runtime guards use `AtomicBoolean isSyncDataFromSCMRunning` to serialize snapshot and container sync operations. Snapshot trigger state is guarded by `scmSnapshotLock` and records status, phase, timestamps, cancel allowance, task start flag, and last error.

Dependencies and integration points: `StorageContainerServiceProvider` supplies SCM pipelines, containers, nodes, counts, and DB checkpoints. `ReconStorageContainerSyncHelper` performs incremental targeted reconciliation. Event handlers integrate with SCMEvents. `TriggerDBSyncEndpoint` uses snapshot trigger/status/cancel APIs. API endpoint tests and health tasks use the manager getters. SQL/JOOQ dependencies support container health and size tasks.

Risks and edge cases: one atomic flag serializes both periodic container sync and snapshot replacement; this avoids DB races but can reject manual triggers during long operations. Cancellation is allowed only during checkpoint download and becomes unavailable once DB initialization starts. Snapshot DB replacement closes the old store before opening the new one; failure after close can leave managers needing careful recovery. The facade returns null for several full SCM services (`BlockManager`, metadata store, HA manager, sequence generator through interface), so callers must understand Recon's limited SCM surface.

Test signals: `TestReconStorageContainerManagerFacade`, `TestReconSCMContainerSyncIntegration`, and `TestTriggerDBSyncEndpoint` exercise trigger behavior, concurrent sync rejection, runtime exceptions, and endpoint DTOs. Additional tests should stress snapshot failure recovery, node preservation during DB swap, safe-mode gating, and metrics updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerManagerFacade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerSyncHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerSyncHelper.java

Purpose: this helper performs targeted incremental reconciliation between authoritative SCM container state and Recon's local container metadata. It focuses on states Recon can safely converge without active SCM ownership: OPEN, QUASI_CLOSED, CLOSED, and DELETED.

Important APIs and types: constructed with `StorageContainerServiceProvider`, `OzoneConfiguration`, `ReconContainerManager`, and `ReconScmContainerSyncMetrics`. Main API is `syncWithSCMContainerInfo`. Internals include `syncContainersForState`, `reconcileExistingContainer`, `reconcileToQuasiClosed`, `reconcileToClosed`, `syncDeletedContainers`, `processDeletedPage`, `retireContainerToDeleted`, `batchedAddMissingContainers`, `addContainerInfoFallback`, `getContainerCountPerCall`, and `safeContainerWithPipelineBatchSize`.

Control flow: a sync cycle scans OPEN add-only from `pass2OpenStartContainerId`, then full paginated QUASI_CLOSED and CLOSED scans, then a DELETED ID scan. For each live-state page, absent containers are fetched in bounded `ContainerWithPipeline` sub-batches and added; present containers are reconciled forward through valid local transitions. DELETED sync scans only SCM's DELETED list, never DELETING, and drives existing Recon containers through minimal valid transitions to DELETED in one call sequence. Missing non-OPEN containers can be added via `getListOfContainerInfos` fallback without a pipeline.

State and persistence: `pass2OpenStartContainerId` is an in-memory monotonic cursor for OPEN scans. Container lifecycle updates and additions persist through `ReconContainerManager`. Metrics store per-state drift and duration plus overall facade status. There is no durable cursor, so OPEN add-only scans restart from ID 1 after Recon restart.

Dependencies and integration points: invoked by `ReconStorageContainerManagerFacade` periodically and through manual `triggerSCMContainerSync`. It relies on `StorageContainerServiceProvider` RPCs for counts, ID pages, CWP batches, and fallback infos. It relies on `ReconContainerManager.transitionOpenToClosing` to keep open-container pipeline counts correct.

Risks and edge cases: the OPEN cursor skips existing higher IDs after a cycle and is not persisted; it assumes OPEN IDs increase monotonically and that later transitions will catch missed containers in non-OPEN states. Batch-size calculations protect Hadoop IPC limits for ID and CWP payloads, but misestimated proto sizes could still matter at very large scale. DELETED retirement logs only sampled transitions. Fallback adds are intentionally disabled for OPEN containers because pipeline tracking would be incomplete.

Test signals: `TestReconStorageContainerManagerFacade` and `TestReconSCMContainerSyncIntegration` reference facade-triggered sync. Important coverage includes state transition matrices, CWP sub-batching at IPC limits, fallback for non-OPEN containers with no viable pipeline, DELETED retirement from every source state, and metric updates on partial failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageContainerSyncHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.recon.scm`.

Important APIs and types: no APIs are declared; it only supplies Javadoc package text.

Control flow: none.

State and persistence: none.

Dependencies and integration points: the package contains Recon's passive SCM facade, managers, handlers, storage config, policy provider, and sync helpers. The current package comment says the classes handle OM snapshot recovery and checkpoints, which appears stale for an SCM package.

Risks and edge cases: stale package documentation can mislead maintainers and generated docs. The actual package is SCM-oriented, not OM snapshot recovery.

Test signals: no tests apply directly. Documentation review should update the package description to match the SCM responsibilities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/ReconCertificateClient.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/ReconCertificateClient.java

Purpose: `ReconCertificateClient` specializes the default HDDS certificate client for the Recon component so Recon can request and renew certificates from SCM CA as a RECON node.

Important APIs and types: extends `DefaultCertificateClient`, defines `COMPONENT_NAME = "recon"`, stores cluster ID and Recon ID from `ReconStorageConfig`, overrides `configureCSRBuilder`, `sign`, and `getLogger`.

Control flow: `configureCSRBuilder` starts from the parent CSR builder, derives a subject from current short user and local canonical hostname, sets CA=false, attaches the current key pair and security config, and returns the builder. `sign` builds `NodeDetailsProto` with host name, cluster ID, Recon UUID, and node type RECON, then calls `getCertificateChain` on the SCM security client.

State and persistence: certificate serial persistence is delegated to `DefaultCertificateClient` through the constructor's current serial ID and `saveCertIdCallback`; `ReconStorageConfig` stores that serial ID. This class keeps only identity strings.

Dependencies and integration points: depends on `SCMSecurityProtocolClientSideTranslatorPB`, `SecurityConfig`, `ReconStorageConfig`, and Hadoop UGI. It is part of Recon's secure startup and certificate lifecycle.

Risks and edge cases: local hostname or UGI lookup failures become `CertificateException` with CSR error. The TODO notes certificate retrieval from multiple SCMs is not implemented. Subject format changes can affect certificate expectations. Stable Recon ID depends on storage metadata.

Test signals: no direct test was found. Tests should mock SCM security client signing, verify RECON node details, assert CSR subject/key/config fields, and cover hostname/UGI failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/ReconCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/package-info.java

Purpose: package documentation for Recon security facilities.

Important APIs and types: no executable APIs; the package contains `ReconCertificateClient` in this subset.

Control flow: none.

State and persistence: none.

Dependencies and integration points: package-level Javadoc feeds generated docs and signals that security-related Recon classes live here.

Risks and edge cases: broad but accurate package text. If more authn/authz classes move here, the package docs may need more detail.

Test signals: no tests apply directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/HddsDatanodeServiceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/HddsDatanodeServiceProvider.java

Purpose: marker interface intended as an SPI abstraction for accessing DataNode endpoints from Recon.

Important APIs and types: declares no methods.

Control flow: none in this file.

State and persistence: none.

Dependencies and integration points: currently only a type placeholder. Future implementations could be bound through Guice like the OM, SCM, and metrics providers.

Risks and edge cases: an empty SPI can confuse readers because it defines no contract. Adding methods later will be a source-compatible but implementation-breaking change for any classes that already implement it.

Test signals: no tests apply until behavior is added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/HddsDatanodeServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/MetricsServiceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/MetricsServiceProvider.java

Purpose: `MetricsServiceProvider` abstracts Recon's access to external metrics systems such as JMX and Prometheus.

Important APIs and types: declares `getMetricsResponse(String api, String queryString)`, `getMetricsInstant(String queryString)`, and `getMetrics(String queryString)`. Return types are `HttpURLConnection`, `List<Metric>`, and `List<Map<String,Object>>`.

Control flow: implementations choose how to build URLs, authenticate, parse response payloads, and map metrics to Recon API shapes.

State and persistence: no state in the interface. Implementations hold endpoint/config/client state but do not persist metrics here.

Dependencies and integration points: implemented by `JmxServiceProviderImpl` and `PrometheusServiceProviderImpl`. API resources can depend on this SPI without knowing the backend.

Risks and edge cases: the interface mixes raw connection access with parsed metrics, and implementations return empty lists for unsupported query styles. Callers must know which method is meaningful for the selected provider.

Test signals: tests should be implementation-specific, verifying URL construction, HTTP status handling, parser behavior, and unsupported method behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/MetricsServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/OzoneManagerServiceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/OzoneManagerServiceProvider.java

Purpose: this SPI abstracts Recon's synchronization and metadata access to Ozone Manager.

Important APIs and types: declares `start`, `stop`, `getOMMetadataManagerInstance`, and `triggerSyncDataFromOMImmediately`. It returns `OMMetadataManager` for local metadata access.

Control flow: implementations own background sync lifecycle and manual sync triggering. The interface exposes only coarse start/stop plus metadata manager access.

State and persistence: no interface state. Implementations update Recon's local OM RocksDB snapshot and derived task state.

Dependencies and integration points: implemented by `OzoneManagerServiceProviderImpl`; bound by the Recon controller module and used by Recon server/API paths that need OM metadata.

Risks and edge cases: no status API is exposed here, so callers can trigger sync but cannot observe detailed progress through the SPI. `stop` throws generic `Exception`, pushing cleanup error handling to callers.

Test signals: implementation tests should cover scheduler lifecycle, immediate trigger behavior, and metadata manager availability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/OzoneManagerServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconContainerMetadataManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconContainerMetadataManager.java

Purpose: this unstable SPI defines Recon DB operations for container-to-key metadata, container counts, container listings, reverse key-prefix lookups, and container replica history.

Important APIs and types: operations include `reinitWithNewContainerDataFromOm`, staged-manager creation, `reinitialize`, batch stores for container-key mappings and container key counts, replica history stores, count stores/increments, lookup APIs, iterators, deletion APIs, table accessors, and `commitBatchOperation`. Key types include `ContainerKeyPrefix`, `KeyPrefixContainer`, `ContainerMetadata`, `ContainerReplicaHistory`, `DatanodeID`, `DBStore`, `Table`, `TableIterator`, and `SeekableIterator`.

Control flow: OM reprocess tasks can rebuild mappings in bulk or via batches. API paths can page by container, key prefix, or reverse key-prefix index. Container manager code uses replica history methods to persist DataNode sightings and removal information.

State and persistence: implementations persist multiple Recon container metadata tables in RocksDB. Batch APIs allow atomic writes through `BatchOperation`/`RDBBatchOperation`. Staged managers support task reinitialization against a staged Recon DB before swap.

Dependencies and integration points: used by namespace/container tasks, Recon APIs, and `ReconContainerManager`. Codecs in this subset (`ContainerKeyPrefixCodec`, `KeyPrefixContainerCodec`) define key serialization for two of the tables.

Risks and edge cases: this is a broad interface with deprecated and current deletion paths. Callers must maintain consistency between forward mappings, reverse mappings, per-container counts, and total count. Iterator methods expose low-level table access and require caller-side close discipline.

Test signals: manager implementation tests should cover batch atomicity, staged reinitialization, forward/reverse lookup consistency, pagination, replica history merge behavior, deprecated deletion compatibility, and count drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconContainerMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconFileMetadataManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconFileMetadataManager.java

Purpose: `ReconFileMetadataManager` defines DB operations for file-size bucket counts used by Recon file metadata tasks and APIs.

Important APIs and types: staged-manager creation, `reinitialize`, `batchStoreFileSizeCount`, `batchDeleteFileSizeCount`, `getFileSizeCount`, `getFileCountTable`, `commitBatchOperation`, and `clearFileCountTable`. Key type is `FileSizeCountKey`; values are `Long`.

Control flow: tasks write or clear file count buckets during incremental processing or full reprocess. Callers use batch operations for atomic updates, then commit through the manager.

State and persistence: implementations persist a RocksDB table keyed by file-size bucket descriptors. Staged managers allow rebuilding counts outside the active DB.

Dependencies and integration points: used by Recon tasks that compute file-size distributions from OM metadata. Integrates with `ReconDBProvider` for active DB switching.

Risks and edge cases: bucket consistency depends on callers deleting old bucket entries and storing new ones in the same batch when files change. `clearFileCountTable` is destructive and should be restricted to reprocess flows.

Test signals: tests should cover batch store/delete, clear behavior, staged manager use, and reinitialize after DB provider swap.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconFileMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconGlobalStatsManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconGlobalStatsManager.java

Purpose: this SPI defines persistence for global Recon statistics, keyed by string and valued by `GlobalStatsValue`.

Important APIs and types: `getStagedReconGlobalStatsManager`, `reinitialize`, `batchStoreGlobalStats`, `getGlobalStatsValue`, `getGlobalStatsTable`, and `commitBatchOperation`.

Control flow: Recon tasks store derived global stats in batches, consumers read by key or table, and reprocess flows can use staged managers before active DB replacement.

State and persistence: implementations write to a RocksDB table of global stats. Batch operations support atomic multi-stat updates.

Dependencies and integration points: used by OM-derived tasks and dashboards for aggregate counts and sizes. Relies on `ReconDBProvider` for active/staged DB management.

Risks and edge cases: string keys are a loose contract; collisions or renames can break consumers. No delete or clear method is exposed in this interface, so stale stats require implementation-specific handling or overwrites.

Test signals: tests should cover staged reinitialization, batch commits, missing-key reads, and key naming compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconGlobalStatsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconNamespaceSummaryManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconNamespaceSummaryManager.java

Purpose: `ReconNamespaceSummaryManager` defines DB operations for namespace summary records keyed by object ID.

Important APIs and types: staged-manager creation, `reinitialize`, `clearNSSummaryTable`, deprecated `storeNSSummary`, batch store/delete, direct delete, `getNSSummary`, and `commitBatchOperation`. Value type is `NSSummary`.

Control flow: namespace summary tasks update object summaries through batch APIs during OM event consumption or reprocess. API endpoints read summaries by object ID for namespace views.

State and persistence: implementations persist NSSummary records in Recon RocksDB. Staged managers and clear operations support full rebuilds.

Dependencies and integration points: used by namespace summary tasks and namespace API endpoints for volume/bucket/directory/key aggregation.

Risks and edge cases: stale summaries can remain if delete events are missed or batch delete/store ordering is wrong. The deprecated direct store API suggests callers should prefer batch operations for consistency.

Test signals: the repository has many namespace endpoint tests (`TestNSSummaryEndpoint*`, disk usage ordering tests) that indirectly validate summary persistence. Manager-specific tests should cover staged rebuilds and delete semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconNamespaceSummaryManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/StorageContainerServiceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/StorageContainerServiceProvider.java

Purpose: this SPI abstracts Recon's RPC access to authoritative SCM state.

Important APIs and types: exposes pipeline listing/lookup, single and batched container-with-pipeline lookup, SCM node listing, total and per-state container counts, SCM DB snapshot retrieval, ID-only paginated container listing by lifecycle state, and full `ContainerInfo` paginated listing by state. Key types include `Pipeline`, `ContainerWithPipeline`, `ContainerID`, `ContainerInfo`, `HddsProtos.Node`, lifecycle states, and `DBCheckpoint`.

Control flow: Recon managers call this SPI when they need SCM as source of truth: startup pipeline initialization, report-time container/pipeline backfill, dead-node state verification, full SCM DB snapshot refresh, and targeted container sync.

State and persistence: the interface owns no state. Implementations talk to SCM and may materialize downloaded DB checkpoints on local disk.

Dependencies and integration points: implemented by `StorageContainerServiceProviderImpl` outside this subset and bound by `ReconControllerModule`. Heavily used by `ReconStorageContainerManagerFacade`, `ReconStorageContainerSyncHelper`, `ReconContainerManager`, `ReconPipelineReportHandler`, and `ReconDeadNodeHandler`.

Risks and edge cases: call semantics differ by payload size: ID-only APIs are intended for hot-path pagination, while full info/CWP APIs are targeted. `getSCMDBSnapshot` returns nullable checkpoint without throwing checked exceptions, so callers must validate. Batch CWP lookup can omit containers whose pipelines cannot be resolved, requiring fallback logic for non-OPEN states.

Test signals: SCM sync tests should mock this interface extensively for counts, pages, batch omissions, snapshots, and exceptions. Contract tests for the implementation should verify pagination inclusivity and lifecycle filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/StorageContainerServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ContainerKeyPrefixCodec.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ContainerKeyPrefixCodec.java

Purpose: `ContainerKeyPrefixCodec` serializes `ContainerKeyPrefix` keys for the container-to-key-prefix table.

Important APIs and types: singleton `get`, `toPersistedFormat`, `fromPersistedFormat`, `copyObject`, `getTypeClass`. It uses `LongCodec`, UTF-8, underscore delimiter, `ArrayUtils`, and `StringUtils`.

Control flow: serialization writes the 8-byte container ID first. If a key prefix is present, it appends `_` plus UTF-8 key prefix. If key version is not -1, it appends `_` plus 8-byte version. Deserialization assumes the full persisted form exists: first 8 bytes container ID, bytes between delimiters for key prefix, and final 8 bytes for version.

State and persistence: no mutable state. The byte format controls RocksDB key ordering and seek behavior for `ContainerKeyPrefix` tables.

Dependencies and integration points: used by Recon container metadata DB definitions/implementations. Prefix-seek keys may serialize with only container ID or missing version, but the deserializer is designed for complete DB entries.

Risks and edge cases: key prefixes containing underscores are safe because deserialization uses fixed first/last byte positions, but malformed or prefix-only raw data cannot be deserialized correctly. `copyObject` returns the same instance, assuming immutability. Serialization with key prefix but version -1 produces a form that `fromPersistedFormat` does not explicitly support.

Test signals: codec tests should cover full round trip, container-only prefix seek serialization, key prefixes with underscores/UTF-8, malformed byte arrays, and ordering expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ContainerKeyPrefixCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/JmxServiceProviderImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/JmxServiceProviderImpl.java

Purpose: this provider implements `MetricsServiceProvider` for Hadoop/Ozone JMX endpoints.

Important APIs and types: constructor stores `ReconUtils`, endpoint URL, `URLConnectionFactory`, and `OzoneConfiguration`. `getMetricsResponse` builds a query URL. `getMetrics` returns JMX `beans` as a list of maps. `getMetricsInstant` returns an empty list because JMX does not use Recon's `Metric` time-series shape here.

Control flow: endpoint trailing slash is trimmed. `getMetricsResponse` formats `<endpoint>?<api>=<queryString>` and calls `ReconUtils.makeHttpCall` with Kerberos determined from `HDDS_DATANODE_HTTP_AUTH_TYPE`. Private `getMetrics` runs as login user, checks for successful HTTP status, parses JSON using Hadoop `JsonUtils`, and returns the `beans` list when present.

State and persistence: no persistence. Holds HTTP client/config state and endpoint.

Dependencies and integration points: used wherever Recon is configured to fetch metrics from JMX rather than Prometheus. Uses Hadoop security utilities for SPNEGO/Kerberos execution.

Risks and edge cases: generic casts from JSON can fail if endpoint response shape changes. Non-success responses return empty lists without detailed exception. Query parameters are string-formatted without URL encoding. Kerberos detection uses datanode HTTP auth type.

Test signals: tests should cover URL trimming/construction, Kerberos flag behavior, successful beans parsing, non-success response handling, and unsupported instant-query empty result.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/JmxServiceProviderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/KeyPrefixContainerCodec.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/KeyPrefixContainerCodec.java

Purpose: `KeyPrefixContainerCodec` serializes reverse index keys from key prefix to key version and container ID.

Important APIs and types: singleton `get`, `supportCodecBuffer`, `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, delimiter helpers, and `copyObject`. Uses `CodecBuffer` for efficient buffered serialization in addition to byte arrays.

Control flow: serialization writes UTF-8 key prefix, optionally `_` plus 8-byte key version, and optionally `_` plus 8-byte container ID. `fromCodecBuffer` supports partial forms by finding delimiters from the end: no delimiter means key-prefix-only; one delimiter means prefix plus version; two delimiters means full key/version/container. `fromPersistedFormat` assumes full form and slices based on fixed trailing long sizes.

State and persistence: no mutable state. The byte format defines RocksDB reverse-index key layout and enables prefix seeks by key prefix and version.

Dependencies and integration points: used by Recon container metadata manager implementations for key-prefix-to-container lookup, particularly APIs that answer which containers hold a key prefix.

Risks and edge cases: delimiter search skips backward by `Long.BYTES`, which is tailored to the binary long suffix layout; malformed data can parse incorrectly. Byte-array deserialization is less flexible than buffer deserialization and expects full entries. `copyObject` returns the same instance.

Test signals: tests should cover buffer and byte-array round trips, partial seek key serialization, key prefixes containing underscores, empty buffer exception, malformed suffixes, and ordering compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/KeyPrefixContainerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/OzoneManagerServiceProviderImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/OzoneManagerServiceProviderImpl.java

Purpose: `OzoneManagerServiceProviderImpl` is Recon's OM synchronization engine. It keeps a local Recon OM metadata DB current by downloading full OM snapshots and applying incremental RocksDB WAL update batches from OM.

Important APIs and types: implements `OzoneManagerServiceProvider`. Constructor wires `OzoneConfiguration`, `ReconOMMetadataManager`, `ReconTaskController`, `ReconUtils`, `OzoneManagerProtocol`, `ReconContext`, and `ReconTaskStatusUpdaterManager`. Key methods include `start`, `stop`, `triggerSyncDataFromOMImmediately`, `getOzoneManagerSnapshotUrl`, `getOzoneManagerDBSnapshot`, `updateReconOmDBWithNewSnapshot`, `getAndApplyDeltaUpdatesFromOM`, `innerGetAndApplyDeltaUpdatesFromOM`, `syncDataFromOM`, `executeFullSnapshot`, `checkAndValidateReconDbPermissions`, and `getCurrentOMDBSequenceNumber`.

Control flow: startup starts the tar extractor and OM metadata manager, recovers from startup DB errors by fetching a full snapshot, starts Recon OM tasks, checks for task sequence drift, queues task reinitialization when needed, then schedules periodic sync. Sync chooses full snapshot when local sequence is absent; otherwise it loops fetching deltas until lag falls below threshold. Each delta request retrieves update batches, iterates RocksDB write batches through `OMDBUpdatesHandler` to collect events, commits them to Recon RocksDB, updates task status, feeds events to `ReconTaskController`, and may queue reinitialization on buffer overflow or task failures. Delta failures fall back to full snapshot unless interrupted.

State and persistence: local OM metadata is persisted through `ReconOMMetadataManager` and RocksDB. Full snapshots are downloaded from OM HTTP(S), extracted under Recon OM snapshot DB directory, validated for SST files, and swapped into the metadata manager. Task status for `OmSnapshotRequest` and `OmDeltaRequest` records run status and last sequence. Metrics are recorded in `OzoneManagerSyncMetrics` and `ReconSyncMetrics`. `isSyncDataFromOMRunning` serializes sync operations.

Dependencies and integration points: uses OM RPC (`getDBUpdates`, `getServiceList`), OM HTTP checkpoint endpoint, Hadoop security login user execution, `URLConnectionFactory`, `TarExtractor`, RocksDB managed write batches, Recon task controller, and Recon context health errors. It is bound through `OzoneManagerServiceProvider` and supplies `OMMetadataManager` to consumers.

Risks and edge cases: immediate trigger restarts the scheduler and tar extractor; races with current sync are guarded only by `isSyncDataFromOMRunning`. Snapshot extraction cleanup deletes previous snapshot and staging directories, so interrupted downloads must be handled carefully. `sstFiles` is logged after `listFiles`; if null, streaming over it would fail, although earlier code only checks null for logging. Query URL construction and SPNEGO depend on OM HTTP config. Delta apply commits raw write batches and task event consumption must remain sequence-consistent.

Test signals: OM/Recon task tests should cover full snapshot fallback, delta loop lag threshold, interrupted delta/snapshot behavior, task status updates, reinitialization queue results, permissions validation, leader URL selection, and metrics increments. API endpoint tests indirectly depend on the local OM metadata manager this provider maintains.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/OzoneManagerServiceProviderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/PrometheusServiceProviderImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/PrometheusServiceProviderImpl.java

Purpose: this provider implements `MetricsServiceProvider` for Prometheus HTTP API queries.

Important APIs and types: constructor reads `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT`, stores `URLConnectionFactory` and `ReconUtils`, and trims trailing slash. `getMetricsResponse`, static `getEndpointConfigKey`, `getMetricsInstant`, and private `getMetrics` implement the Prometheus path. General `getMetrics(String)` returns an empty list.

Control flow: `getMetricsResponse` builds `<endpoint>/api/v1/<api>?<queryString>` and performs an HTTP call without Kerberos. `getMetricsInstant` uses API `query`. The parser checks successful HTTP status, parses JSON with Jackson, requires status `success`, reads `data.resultType`, chooses `value` for vector or `values` for matrix, converts timestamp/value pairs into `TreeMap<Double,Double>`, and wraps metadata plus values in `Metric`.

State and persistence: no persistence. Holds endpoint/client utilities only.

Dependencies and integration points: used by Recon metrics APIs when Prometheus is configured. Depends on Prometheus response schema and Recon's `Metric` type.

Risks and edge cases: returns `null` metrics when a successful response has empty result or unsupported shape, so callers must handle null as well as empty. Query strings are not URL encoded. The code assumes timestamps are `Double` and values are numeric strings. Non-success status logs errors but does not throw.

Test signals: tests should cover endpoint trimming, URL construction, vector and matrix parsing, empty result behavior, Prometheus error payload logging, and HTTP failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/PrometheusServiceProviderImpl.java -->
