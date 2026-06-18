# subset-b-008120 Research

This grouped report covers the exact source files assigned to `subset-b-008120`. Each source file has its own marker-delimited section so the report can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java

## Purpose

`ExportJobManager` is a Guice singleton that owns asynchronous CSV/TAR export jobs for unhealthy-container records. It lets Recon submit, track, cancel, and delete exports while serializing database cursor access through a single-thread executor.

## Important APIs and Types

The main public API is `submitJob(String state)`, `getJob`, `getAllJobs`, `getQueuePosition`, `cancelJob`, and `shutdown`. It stores `ExportJob` instances keyed by job id, uses `ExportJob.JobStatus` transitions, and queries `ContainerHealthSchemaManager` using `ContainerSchemaDefinition.UnHealthyContainerStates`. Output is split into CSV parts of 500,000 records and archived via `Archiver.create`.

## Control Flow

Construction resolves the export directory from `ozone.recon.export.directory` or `{ozone.recon.db.dir}/exports`, creates it, and deletes stale directories and `.tar` files from previous Recon runs. `submitJob` rejects duplicate states already queued, running, or completed, enforces total queue size, adds the job to tracker/queue, and submits `executeExport`. The worker removes the job from `jobQueue`, marks it running, counts expected records, streams the jOOQ cursor into CSV files, archives the job directory, deletes temporary CSVs, and marks the job completed. Cancellation removes queued jobs, cancels their `Future`, marks failures, and deletes partial artifacts and final TARs.

## State and Persistence

In-memory state is held in concurrent maps plus a synchronized `LinkedHashMap` queue. Persistent state is only the local export directory: temporary job folders and final `.tar` files. Jobs do not persist across Recon process restart, and startup cleanup intentionally removes prior artifacts.

## Dependencies and Integration Points

It integrates with Recon server config, `ReconUtils` for DB directory fallback, container health persistence, jOOQ cursors, Apache Commons `FileUtils`, and lifecycle cleanup through `@PreDestroy`. API endpoints that expose export operations depend on this manager to coordinate job status and file lifecycle.

## Risks and Edge Cases

`submitJob` creates a `Future` even for all accepted jobs, so `runningTasks` contains queued tasks as well as active work. Duplicate-state checks include completed jobs until the user deletes them, which is intentional but can surprise clients. `valueOf(job.getState())` is case-sensitive and invalid states fail inside the worker rather than at submission. `Future.cancel(true)` can interrupt export, but archive creation and file I/O interruption behavior depends on called libraries. The single synchronized queue avoids nested locking, but `ExportJob` itself must be safe for concurrent reads by REST callers.

## Test Signals

Useful tests cover configured/default export directory selection, startup cleanup, duplicate-state rejection, queue limit, queue positions, cancellation before and during cursor iteration, multi-part CSV generation, TAR cleanup, invalid state handling, and shutdown interrupt behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java

## Purpose

`FeaturesEndpoint` exposes Recon feature-gating metadata under `/features`, currently the admin-only `/disabledFeatures` API.

## Important APIs and Types

The endpoint is a JAX-RS resource annotated with `@Path("/features")`, `@Produces(APPLICATION_JSON)`, and `@AdminOnly`. Its only operation, `getDisabledFeatures`, returns `FeatureProvider.getAllDisabledFeatures()` as the response entity.

## Control Flow

Requests enter `getDisabledFeatures`, which asks `FeatureProvider` for all disabled features, logs them, and returns HTTP 200. Any exception is wrapped as a `WebApplicationException` with HTTP 500.

## State and Persistence

The class stores injected `OzoneConfiguration`, but the current method does not read it. It has no persistence and no mutable endpoint state.

## Dependencies and Integration Points

It integrates with Recon's admin authorization filter via `@AdminOnly`, with `FeatureProvider.Feature` DTOs for UI/API clients, and with JAX-RS exception handling.

## Risks and Edge Cases

The logger is initialized with `HeatMapServiceImpl.class`, so log category ownership is misleading. Because `ozoneConfiguration` is unused, future feature gating may need cleanup or tests to detect stale injection. The endpoint trusts `FeatureProvider` to return serializable feature data.

## Test Signals

Tests should assert admin-only binding, JSON shape for enabled/disabled feature lists, and HTTP 500 behavior when `FeatureProvider` fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java

## Purpose

`InternalOnly` is a runtime marker annotation for endpoint classes that depend on internal Recon service components and should not be available as public API surfaces.

## Important APIs and Types

The annotation targets types and is retained at runtime. It requires two attributes: `feature()` and `description()`.

## Control Flow

There is no direct control flow in the annotation. Runtime behavior depends on resource scanners or filters elsewhere that inspect this annotation.

## State and Persistence

No state or persistence exists.

## Dependencies and Integration Points

It integrates with Java reflection, JAX-RS resource registration, and Recon feature/documentation logic that may hide or label internal endpoints.

## Risks and Edge Cases

The annotation itself does not enforce access control. Any endpoint marked `InternalOnly` still needs registration/filter logic to act on it.

## Test Signals

Compilation plus a resource-registration test that verifies annotated classes are treated as internal is the key signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java

## Purpose

`MetricsProxyEndpoint` proxies Recon UI/API metric requests to the configured external metrics provider, normally Prometheus.

## Important APIs and Types

The endpoint is mounted at `/metrics/{api}`. `getMetricsResponse` receives the API path component and current query string, obtains an `HttpURLConnection` from `MetricsServiceProvider`, and streams the provider response to `HttpServletResponse` using NIO channels.

## Control Flow

If a provider exists, the method calls `getMetricsResponse(api, query)`. Successful 2xx responses stream `connection.getInputStream`; non-2xx provider responses set Recon's response status to 502 and stream `connection.getErrorStream`. If no provider is configured, Recon sends a 502 with the Prometheus endpoint config key in the message.

## State and Persistence

The endpoint stores only the injected provider reference. It persists nothing.

## Dependencies and Integration Points

It depends on `MetricsServiceProviderFactory`, `MetricsServiceProvider`, and `PrometheusServiceProviderImpl` constants/config. It is an integration bridge between Recon's REST namespace and Prometheus-compatible HTTP APIs.

## Risks and Edge Cases

The path parameter allows arbitrary provider API suffixes supported by the provider implementation. Error streams may be null for some `HttpURLConnection` failures, which would make channel creation fail. It does not copy content type or headers from Prometheus, only body and coarse status behavior. Provider connections must enforce their own timeout behavior.

## Test Signals

Tests should mock 2xx and non-2xx provider responses, null provider behavior, query-string forwarding, large body streaming, and missing error-stream handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java

## Purpose

`NSSummaryEndpoint` exposes admin-only namespace summary APIs under `/namespace` for entity summaries, disk usage, quota usage, and file-size distribution.

## Important APIs and Types

The main APIs are `/summary`, `/usage`, `/quota`, and `/dist`. Responses use `NamespaceSummaryResponse`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`. The endpoint delegates all path-specific work to `EntityHandler.getEntityHandler`.

## Control Flow

Each operation rejects missing or empty `path` with HTTP 400. If Recon OM metadata initialization is incomplete, it returns an initializing response rather than querying tables. Otherwise it constructs an `EntityHandler` from the namespace summary manager, OM metadata manager, SCM, and path, then calls the matching handler method.

## State and Persistence

The endpoint holds injected managers only. Data comes from Recon's OM metadata snapshot tables and namespace summary store; no endpoint-local state is written.

## Dependencies and Integration Points

It is the primary REST entry point for the handler hierarchy in `api.handlers`, and uses `ReconUtils.isInitializationComplete` as a readiness gate. `StorageDistributionEndpoint` also calls `getDiskUsage("/", false, true, false)` to compute finalized replicated bytes.

## Risks and Edge Cases

The APIs return HTTP 200 for path-not-found or initializing states when represented in the body, while only malformed empty paths return HTTP 400. Handler behavior differs sharply by bucket layout. Recursive aggregation relies on namespace summary materialization being current with OM DB.

## Test Signals

Tests should cover root, volume, bucket, directory, key, unknown path, initializing state, layout-specific paths, `files`, `replica`, and `sortSubPaths` options, quota type-not-applicable responses, and stale/missing NSSummary rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java

## Purpose

`NodeEndpoint` serves `/datanodes` APIs for datanode inventory, safe removal from Recon state, and decommission-status reporting.

## Important APIs and Types

`getDatanodes` returns `DatanodesResponse` with `DatanodeMetadata`, storage reports, pipeline metadata, leader counts, and open-container counts. `removeDatanodes` accepts a JSON list of UUIDs and returns grouped removed/failed/not-found results. Decommission APIs return details for all or one decommissioning datanode.

## Control Flow

Inventory loops over `ReconNodeManager.getAllNodes`, builds storage reports from `SCMNodeStat` and filesystem usage, resolves node health, pipelines, pipeline leaders, and container counts. Removal validates non-null/non-empty UUIDs, resolves each node, requires it to be DEAD, checks for open containers and open pipelines, then calls `nodeManager.removeNode`. Decommission reporting queries SCM for `DECOMMISSIONING` nodes, filters by uuid/ip, reads decommission metrics JSON, and includes container lists per datanode.

## State and Persistence

Most APIs are read-only views of Recon's in-memory SCM/node managers and SCM protocol. `removeDatanodes` mutates Recon node manager state and its nodes table in Recon DB through `ReconNodeManager.removeNode`.

## Dependencies and Integration Points

It depends on `ReconNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `StorageContainerLocationProtocol`, SCM node/container/pipeline types, `DecommissionUtils`, and client versioned SCM calls.

## Risks and Edge Cases

Removal catches all exceptions around the whole loop, so one unexpected error aborts the entire request. Open container/pipeline checks are best-effort and tolerate missing container/pipeline manager entries with warnings. Decommission metrics parsing returns partial maps when SCM metrics are missing. `getStorageReport` calls `nodeManager.getNodeStat(datanode).get()` without a null check.

## Test Signals

Tests should cover inventory with missing pipeline leaders, missing node state, filesystem stats, successful and failed removals, DEAD-only enforcement, open pipeline/container blocks, invalid UUID lists, not-found UUIDs, decommission filtering by uuid/ip, and absent metrics JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java

## Purpose

`OMDBInsightEndpoint` backs Recon's key insight APIs under `/keys`: open keys/files, open MPU summary, pending-deletion keys/directories, deleted directory summary, and filtered key listing.

## Important APIs and Types

Important endpoints include `/open`, `/open/summary`, `/open/mpu/summary`, `/deletePending/summary`, `/deletePending`, `/deletePending/dirs`, `/deletePending/dirs/summary`, and `/listKeys`. It uses `KeyInsightInfoResponse`, `ListKeysResponse`, `KeyEntityInfo`, `ReconBasicOmKeyInfo`, `ParamInfo`, and OM table types including `OmKeyInfo` and `RepeatedOmKeyInfo`.

## Control Flow

Open-key listing validates bucket-level `startPrefix`, scans non-FSO open keys from the legacy open-key table if requested, then scans FSO open files after converting name paths to object-id paths and recursively gathering subpaths from namespace summaries. Deleted-key listing scans the deleted table with prefix/prevKey pagination. Deleted-directory listing delegates to `ReconGlobalMetricsService`. `/listKeys` requires bucket-level or deeper prefixes, gates on OM initialization, then scans legacy and FSO basic key tables with filters for replication type, creation date, and size.

## State and Persistence

The endpoint writes no state. It reads Recon's OM RocksDB mirror, global stats table, and namespace summary table. Pagination state is returned through `lastKey` and accepted as `prevKey`.

## Dependencies and Integration Points

It integrates with `ReconOMMetadataManager`, `ReconGlobalStatsManager`, `ReconNamespaceSummaryManagerImpl`, `ReconGlobalMetricsService`, `BucketHandler`, `ReconUtils`, and `ReconResponseUtils`. It shares FSO path semantics with namespace handlers.

## Risks and Edge Cases

The endpoint mutates `ParamInfo.startPrefix` while scanning FSO subpaths, so callers must not reuse the object expecting the original prefix. `prevKey` is consumed across non-FSO and FSO scans in `/open`, which can make mixed-layout pagination subtle. `validateStartPrefix` only checks bucket-level shape, not existence. `convertStartPrefixPathToObjectIdPath` can throw `NullPointerException` if volume or bucket lookup returns null. `retrieveKeysFromTable` limits by total `results.size`, so prior legacy results constrain FSO scans.

## Test Signals

Coverage should include open-key filtering combinations, invalid start prefixes, FSO directory recursion, empty and no-match responses, deleted table pagination, deleted-dir summary, list-key filters, creation-date parsing through `ParamInfo`, service-not-ready handling, and pagination across mixed legacy/FSO results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java

## Purpose

`PendingDeletionEndpoint` provides admin-only pending-deletion metrics across datanodes, SCM, and OM via `/pendingDeletion`.

## Important APIs and Types

The single public method `getPendingDeletionByComponent(component, limit)` dispatches `component=dn`, `scm`, or `om`. DN responses come from `DataNodeMetricsServiceResponse`; SCM responses use `ScmPendingDeletion`; OM responses are a map from `ReconGlobalMetricsService.calculatePendingSizes`.

## Control Flow

The endpoint validates `component`, normalizes it, and switches by value. DN requests reject `limit < 1`, return HTTP 200 when metric collection is finished, and HTTP 202 while collection is still pending/running. SCM requests call `scmClient.getDeletedBlockSummary`, map total block size, replicated size, and count, return 204 for null summary, and return `-1` sentinel values on exception. OM requests compute pending key and directory sizes from Recon global/namespace state.

## State and Persistence

No endpoint-local state exists. DN metrics may reflect state collected asynchronously by `DataNodeMetricsService`; SCM metrics come from live SCM protocol; OM metrics come from Recon persisted tables.

## Dependencies and Integration Points

It integrates with `ReconGlobalMetricsService`, `DataNodeMetricsService`, and `StorageContainerLocationProtocol`.

## Risks and Edge Cases

SCM failures are hidden behind HTTP 200 with `-1` fields, while DN invalid limits use HTTP 400 and in-progress states use HTTP 202. Clients must understand this mixed error model. A null SCM summary becomes 204 with no entity.

## Test Signals

Tests should cover required component validation, component aliases/case normalization, DN limit validation and status mapping, SCM success/null/failure behavior, and OM pending-size calculation failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java

## Purpose

`PipelineEndpoint` exposes `/pipelines` metadata for all Recon-known SCM pipelines, including optional Ratis leader-election metrics.

## Important APIs and Types

`getPipelines` returns `PipelinesResponse` containing `PipelineMetadata` records. Each record includes pipeline id, datanodes, duration, state, replication config, leader node, container count, leader election count, and last leader election elapsed time when metrics are configured.

## Control Flow

The endpoint iterates `ReconPipelineManager.getPipelines`, copies nodes, computes age from creation timestamp, best-effort resolves leader host and container count, then optionally builds a Ratis group id from the UUID suffix and queries the metrics provider for election metrics.

## State and Persistence

The endpoint is read-only. Pipeline state comes from Recon SCM in-memory managers, and metrics come from the external metrics provider.

## Dependencies and Integration Points

It depends on `ReconPipelineManager`, `MetricsServiceProviderFactory`, `MetricsServiceProvider`, Ratis metric names, and `PipelineMetadata` DTOs.

## Risks and Edge Cases

The group-id derivation assumes the Ratis metric label uses `group-<last UUID segment uppercase>`. Metric values are cast to `TreeMap<Double, Double>`, so provider shape changes can fail at runtime. Leader or container-count failures are logged and produce partial metadata.

## Test Signals

Tests should cover no metrics provider, provider query success/failure, leader lookup failure, container-count failure, group-id derivation, and stable serialization of replication configs and datanode lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java

## Purpose

`ReconGlobalMetricsService` centralizes global OM-derived storage counters used by key insight, pending deletion, and storage distribution APIs.

## Important APIs and Types

It exposes `getOpenKeySummary`, `getDeletedKeySummary`, `getMPUKeySummary`, `getPendingForDeletionDirInfo`, and `calculatePendingSizes`. It reads `GlobalStatsValue` records named by `OmTableInsightTask`, deleted directory entries from `ReconOMMetadataManager.getDeletedDirTable`, and `NSSummary` rows for directory sizes.

## Control Flow

Summary methods fetch global stats keys for count, replicated size, and unreplicated size and return zeroes on `IOException`. Deleted-directory listing optionally seeks to `prevKey`, skips it once, iterates until `limit`, converts each `OmKeyInfo` into `KeyEntityInfo`, accumulates replicated/unreplicated totals using namespace summary sizes, and records `lastKey`. `calculatePendingSizes` combines replicated pending directory size with deleted-key replicated size and uses `-1` sentinels if either side fails.

## State and Persistence

The service is a singleton but holds no mutable state. It reads persisted Recon global stats, OM deleted-dir table, and namespace summary tables.

## Dependencies and Integration Points

It integrates with `ReconGlobalStatsManager`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `OmTableInsightTask`, and key insight DTOs. `OMDBInsightEndpoint`, `PendingDeletionEndpoint`, and `StorageDistributionEndpoint` use it.

## Risks and Edge Cases

Global stats can be stale relative to OM table scans. Deleted-dir pagination requires `prevKey` to exist exactly or returns an empty response. `getMPUKeySummary` uses key name `totalDataSize` rather than `totalUnreplicatedDataSize`, so clients must account for the naming difference. Directory size lookup returns zero if NSSummary is missing.

## Test Signals

Tests should cover missing global stats, IOException fallback, deleted-dir table null, prevKey exact and missing behavior, limit handling including `-1`, namespace summary missing rows, and `calculatePendingSizes` sentinel behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java

## Purpose

`ServiceNotReadyException` is a lightweight runtime exception used by Recon APIs to signal that an internal service or metadata source is not initialized enough to satisfy a request.

## Important APIs and Types

It extends `RuntimeException` and provides a single message constructor.

## Control Flow

The class has no internal branching. Callers such as `OMDBInsightEndpoint.getListKeysResponse` can catch it specially and convert it to a service-unavailable response with an initializing body.

## State and Persistence

It carries only the exception message and has no persistence.

## Dependencies and Integration Points

It integrates with endpoint error handling where checked exceptions would be awkward through helper paths.

## Risks and Edge Cases

As an unchecked exception, it must be caught at appropriate API boundaries or it will become a generic 500. Its semantics rely on consistent use by lower-level helpers.

## Test Signals

Tests should assert API translation to HTTP 503 where the exception is intentionally caught, and generic error behavior where it is not.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java

## Purpose

`StorageDistributionEndpoint` provides admin-only cluster storage distribution and a CSV download combining datanode capacity with pending-deletion metrics.

## Important APIs and Types

`getStorageDistribution` returns `StorageCapacityDistributionResponse` with `DatanodeStorageReport`, `GlobalStorageReport`, `GlobalNamespaceReport`, and `UsedSpaceBreakDown`. `/download` returns either metric-collection status or a CSV built from `DatanodePendingDeletionMetrics` joined with current datanode storage reports.

## Control Flow

The main GET collects datanode reports, sums them into global storage, obtains open-key/MPU bytes, calculates namespace metrics from pending OM sizes, finalized replicated DU at root, and key counts, then builds the response. Download first asks `DataNodeMetricsService` for collected metrics; if unfinished it returns HTTP 202 JSON, otherwise it joins metrics by datanode UUID, builds CSV headers and column extractors, derives a UTC filename from cluster id and timestamp, and delegates to `ReconUtils.downloadCsv`.

## State and Persistence

The endpoint has no mutable state. It reads live Recon node-manager state, Recon global stats, namespace summaries through `NSSummaryEndpoint`, DataNodeMetricsService collected state, and Recon context cluster id.

## Dependencies and Integration Points

It integrates with SCM node stats, `ReconGlobalMetricsService`, `ReconGlobalStatsManager`, `NSSummaryEndpoint`, `DataNodeMetricsService`, and CSV download utilities.

## Risks and Edge Cases

`calculateNamespaceMetrics` stores pending sizes in local variables but does not put them back into the returned map, so fallback code mentioning those keys is not reflected in the response builder. Finalized bytes are computed by invoking another endpoint method and casting the entity to `DUResponse`; changes to that endpoint can break storage distribution. Download maps metrics to views even when the storage report is missing, using `-1` fields. Main response catches broad exceptions and returns HTTP 500 text.

## Test Signals

Tests should cover aggregation consistency from one datanode snapshot, missing node stats, root DU failure, missing global stats, pending-size failure, CSV unfinished/finished/missing-data paths, cluster-id fallback, and CSV column values for missing reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java

## Purpose

`TaskStatusService` is a JAX-RS endpoint for exposing the last recorded status rows for Recon background tasks.

## Important APIs and Types

The class is mounted at `/task` and produces JSON. `GET /task/status` calls `ReconTaskStatusDao.findAll()` and returns a list of generated `ReconTaskStatus` POJOs.

## Control Flow

Requests enter `getTaskStats`, read all rows from `RECON_TASK_STATUS` through the injected DAO, and return HTTP 200 with the raw result list. There is no filtering, pagination, readiness check, or explicit exception handling.

## State and Persistence

The endpoint holds an injected `ReconTaskStatusDao`. It is read-only from the endpoint perspective, but data comes from Recon's SQL task status table populated by background tasks.

## Dependencies and Integration Points

It integrates with jOOQ-generated DAO/POJO classes under `org.apache.ozone.recon.schema.generated.tables` and the Recon task framework that updates task status rows.

## Risks and Edge Cases

The endpoint returns every task row without paging, so response size grows with task count. DAO failures propagate as generic server errors. Because the generated POJO shape is exposed directly, schema changes can affect clients.

## Test Signals

Tests should verify DAO delegation, JSON serialization of `ReconTaskStatus`, empty-table behavior, DAO exception mapping, and route registration at `/task/status`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java

## Purpose

`TriggerDBSyncEndpoint` exposes manual trigger and status APIs for Recon's OM and SCM DB synchronization flows.

## Important APIs and Types

Endpoints include `GET /triggerdbsync/om`, `POST /triggerdbsync/scm/snapshot`, `GET /triggerdbsync/scm/snapshot/status`, and `POST /triggerdbsync/scm/snapshot/cancel`. It uses `OzoneManagerServiceProvider` and `ReconStorageContainerManagerFacade`.

## Control Flow

The OM trigger calls `triggerSyncDataFromOMImmediately` and returns HTTP 200. The SCM snapshot trigger calls `reconScm.triggerReconDbSyncWithScm()` and returns the facade result. Status and cancel similarly call the facade and return its response object.

## State and Persistence

The endpoint itself is stateless. It triggers background synchronization that can update Recon's OM/SCM metadata stores and reads/cancels SCM snapshot sync state from the facade.

## Dependencies and Integration Points

It integrates with Recon's OM service provider and SCM facade, and is likely intended for operational/admin use.

## Risks and Edge Cases

There is no explicit error handling; provider/facade exceptions propagate through JAX-RS. The OM operation is exposed as GET despite causing side effects, which can surprise caches or automated probes.

## Test Signals

Tests should assert endpoint-to-provider delegation, side-effect behavior, facade response propagation, exception mapping, and authorization/route configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java

## Purpose

`UtilizationEndpoint` exposes file-size and container-size distribution counts from Recon persistence under `/utilization`.

## Important APIs and Types

`/fileCount` returns `FileCountBySize` rows filtered by volume, bucket, and optional file size upper bound. `/containerCount` returns `ContainerCountBySize` rows filtered by a normalized container-size upper bound. It uses `ReconFileMetadataManager`, `ContainerCountBySizeDao`, `UtilizationSchemaDefinition`, and jOOQ.

## Control Flow

For exact volume+bucket+fileSize requests, it directly looks up a `FileSizeCountKey`. Otherwise it iterates the RocksDB file-count table and filters records in Java. Container counts normalize the upper bound with `ReconUtils.getContainerSizeUpperBound`; positive inputs query by id, while non-positive inputs return all positive-count records.

## State and Persistence

The endpoint is read-only. File counts come from a RocksDB table managed by `ReconFileMetadataManager`; container counts come from the SQL/jOOQ utilization schema.

## Dependencies and Integration Points

It depends on Recon file metadata tasks that populate file count buckets and container utilization tasks that populate the jOOQ table.

## Risks and Edge Cases

Partial file filters require a full table scan. `fileSize <= 0` with volume and bucket scans all sizes rather than rejecting. Container-size normalization means the returned row may not match the raw requested bound. Errors are logged and returned as generic HTTP 500 without body.

## Test Signals

Tests should cover exact and filtered file-count lookup, empty/zero counts, iterator closure, volume-only and bucket-only filters, container upper-bound normalization, all-positive container rows, and persistence exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java

## Purpose

`VolumeEndpoint` exposes paginated Recon OM volume metadata.

## Important APIs and Types

`GET /volumes` accepts `limit` and `prevKey` query parameters using Recon defaults and returns `VolumesResponse` containing `VolumeObjectDBInfo` objects.

## Control Flow

The endpoint calls `omMetadataManager.listVolumes(prevKey, limit)`, maps each `OmVolumeArgs` into a `VolumeObjectDBInfo`, and returns the result count plus list. IO failures produce HTTP 500.

## State and Persistence

It is read-only and depends on Recon's OM volume table mirror.

## Dependencies and Integration Points

It integrates with `ReconOMMetadataManager`, `OmVolumeArgs`, and volume response DTOs.

## Risks and Edge Cases

Pagination behavior depends on `listVolumes` interpreting `prevKey` consistently with OM DB ordering. Negative or excessive limits rely on upstream/default handling. The endpoint imports `StringUtils` for prevKey defaults and does no readiness check.

## Test Signals

Tests should cover default pagination, explicit `prevKey`, limit boundaries, empty tables, DTO mapping, and IOException response handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java

## Purpose

`ReconAdminFilter` enforces admin-only access for servlet paths or resources protected by Recon's admin filter wiring.

## Important APIs and Types

It implements `javax.servlet.Filter`. `doFilter` extracts the request principal, creates a remote `UserGroupInformation`, checks authorization with `ReconServer.isAdmin`, and either continues the chain or returns HTTP 403.

## Control Flow

If authorization is disabled according to `OzoneSecurityUtil.isAuthorizationEnabled(conf)`, `hasPermission` returns true and all authenticated/principal-bearing requests are allowed. If a principal exists and is admin, the request proceeds. Otherwise the filter logs a rejection and sets status 403.

## State and Persistence

The filter holds injected `ReconServer` and `OzoneConfiguration`. It has no persistence.

## Dependencies and Integration Points

It integrates with servlet filter chains, Hadoop `UserGroupInformation`, Recon admin resolution, and Ozone security configuration.

## Risks and Edge Cases

When authorization is disabled but `userPrincipal` is null, the filter still rejects because the allow path is only entered inside `if (userPrincipal != null)`. It sets 403 but does not write an error body. It assumes upstream authentication has already populated a principal when needed.

## Test Signals

Tests should cover authz enabled admin/non-admin, authz disabled with and without principal, null principal rejection, status code, and filter-chain invocation count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java

## Purpose

`ReconAuthFilter` adapts Hadoop's `ProxyUserAuthenticationFilter` for Recon HTTP authentication using Recon-specific configuration prefixes.

## Important APIs and Types

It implements `Filter`, builds auth parameters with `AuthenticationFilterInitializer.getFilterConfigMap(conf, OZONE_RECON_HTTP_AUTH_CONFIG_PREFIX)`, creates a Jetty `FilterHolder`, and initializes `ProxyUserAuthenticationFilter` with a delegated `FilterConfig`.

## Control Flow

During `init`, it builds and initializes the Hadoop auth filter. During `doFilter`, it logs the request URL at debug level and delegates all authentication behavior to `hadoopAuthFilter.doFilter`.

## State and Persistence

It stores the injected configuration and the initialized Hadoop auth filter. It persists nothing.

## Dependencies and Integration Points

It integrates with Hadoop HTTP authentication, proxy-user handling, Jetty filter metadata, servlet contexts, and Recon HTTP auth config keys.

## Risks and Edge Cases

`destroy` does not call `hadoopAuthFilter.destroy`, so delegated cleanup may be skipped. If `doFilter` is called before successful init, `hadoopAuthFilter` is null. All parameter semantics are inherited from Hadoop's auth filter.

## Test Signals

Tests should verify config-prefix extraction, init parameter forwarding, delegation to proxy-user filter, debug URL handling, and lifecycle cleanup expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.recon.api.filters` as the package for filters applied to Recon API endpoints.

## Important APIs and Types

It declares only package-level Javadoc and the package statement.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state or persistence exists.

## Dependencies and Integration Points

The file contributes package documentation for Javadoc and source organization around `ReconAuthFilter` and `ReconAdminFilter`.

## Risks and Edge Cases

The only risk is documentation drift if filters are added beyond endpoint security filters.

## Test Signals

Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java

## Purpose

`BucketEntityHandler` implements namespace summary, disk usage, quota, and file-size distribution behavior for bucket-level paths.

## Important APIs and Types

It extends `EntityHandler` and uses a layout-specific `BucketHandler`. It returns `BucketObjectDBInfo`, `CountStats`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`.

## Control Flow

Summary resolves the bucket object id, counts recursive directories and keys from `NSSummary`, and returns bucket metadata from the OM bucket table. DU loads the bucket NSSummary, adds child-directory disk usage rows, optionally adds direct keys through `BucketHandler.handleDirectKeys`, sorts if requested, and returns aggregate size values. Quota reads the bucket's quota and total namespace size. Distribution recursively accumulates file-size buckets.

## State and Persistence

No state is written. Reads come from OM bucket table and Recon namespace summary table.

## Dependencies and Integration Points

It is created by `EntityType.BUCKET` through `EntityHandler` and delegates layout-sensitive direct-key behavior to `FSOBucketHandler`, `LegacyBucketHandler`, or `OBSBucketHandler`.

## Risks and Edge Cases

An empty bucket with no NSSummary returns a mostly empty DU response. Child NSSummary lookups are not null-checked before dereferencing. Quota calculation uses unreplicated total size, while root quota uses replicated size. Sorting is limited by `DISK_USAGE_TOP_RECORDS_LIMIT`.

## Test Signals

Tests should cover empty buckets, child directories, direct file listing, replica DU, sorting, quota values, missing bucket metadata, and all bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java

## Purpose

`BucketHandler` is the abstract strategy layer that hides bucket-layout differences from namespace entity handlers.

## Important APIs and Types

Subclasses implement `determineKeyPath`, `calculateDUUnderObject`, `handleDirectKeys`, `getDirObjectId`, `getBucketLayout`, `getKeyInfo`, and `getDirInfo`. Static helpers include `buildSubpath`, `getKeyName`, and two `getBucketHandler` factories.

## Control Flow

The factory reads `OmBucketInfo` and returns an FSO, legacy, or OBS handler. Legacy buckets are routed to `LegacyBucketHandler` only when `OmConfig.Keys.ENABLE_FILESYSTEM_PATHS` is true; otherwise they are treated as object-store buckets through `OBSBucketHandler`.

## State and Persistence

The base class stores injected namespace and OM metadata managers. It writes nothing and reads volume/bucket IDs from OM metadata tables.

## Dependencies and Integration Points

It is used by `EntityHandler`, `OMDBInsightEndpoint`, and all entity handlers needing layout-specific path resolution or direct-key DU.

## Risks and Edge Cases

Factory behavior depends on OM configuration availability; if configuration is null it creates a default `OzoneConfiguration`, which can alter legacy semantics. Unsupported bucket layouts return null and become unknown paths. `bucketExists` uses skip-cache table reads.

## Test Signals

Tests should assert factory selection for FSO, legacy with filesystem paths on/off, OBS, null bucket info, unsupported layout, and helper path formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java

## Purpose

`DirectoryEntityHandler` handles namespace APIs for directory-level paths in FSO or legacy filesystem-style buckets.

## Important APIs and Types

It returns directory `ObjectDBInfo`, recursive `CountStats`, `DUResponse`, type-not-applicable quota, and file-size distributions.

## Control Flow

Summary resolves the directory object id through the bucket handler, counts descendant directories and files, and maps directory metadata. DU reads the directory NSSummary, emits child-directory rows, optionally appends direct keys, sorts rows, and sets direct key size plus optional replicated size. Distribution recursively accumulates from the directory object id.

## State and Persistence

No writes occur. Reads come from namespace summary, OM directory/key tables through bucket handlers, and OM metadata managers.

## Dependencies and Integration Points

It depends on `BucketHandler` for object-id lookup and direct-key enumeration. `NSSummaryEndpoint` invokes it after `EntityHandler` classifies a path as `DIRECTORY`.

## Risks and Edge Cases

Missing directory NSSummary is treated as an empty directory. Child NSSummary rows are dereferenced without null checks. `Paths.get(dirName).getFileName()` can be null and is converted to an explicit `NullPointerException`. Quota is not applicable for directories.

## Test Signals

Tests should cover empty directories, nested child directories, direct files, replica DU, sorted and unsorted responses, file-size distribution, missing child summaries, and layout-specific directory object ids.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java

## Purpose

`EntityHandler` is the abstract dispatcher and shared aggregation base for Recon namespace summary paths.

## Important APIs and Types

It defines abstract methods for summary, DU, quota, and distribution responses. Static `getEntityHandler` classifies paths as root, volume, bucket, directory, key, or unknown. Helpers include recursive `getTotalFileSizeDist`, `getTotalDirCount`, `getTotalKeyCount`, `getTotalSize`, `parseRequestPath`, `parseObjectStorePath`, and `normalizePath`.

## Control Flow

Classification normalizes the input path, parses names, checks root and volume existence, resolves the bucket handler, and delegates key-path classification to bucket layout strategies. For object-store buckets it preserves slash-containing key names via `parseObjectStorePath`; other layouts split each path component.

## State and Persistence

Instances store managers, bucket handler, normalized path, and parsed names. They read OM metadata and namespace summary tables but do not write.

## Dependencies and Integration Points

It is the central integration point between `NSSummaryEndpoint`, `EntityType` factory methods, `BucketHandler`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, and SCM.

## Risks and Edge Cases

`parseRequestPath` returns `['']` for some empty strings, so callers rely on earlier validation. `parseObjectStorePath` effectively returns up to three parts and its null branch is unreachable for Java `split` with limit 3. Recursive distribution still walks children even though key count and size are materialized. Unknown handling constructs an `UnknownEntityHandler` with null path, which relies on default layout normalization not being dereferenced in response methods.

## Test Signals

Tests should cover path normalization, root handling, missing volume/bucket, object-store slash keys, legacy filesystem path mode, FSO directory/key classification, recursion helpers, and unknown path responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java

## Purpose

`FSOBucketHandler` implements bucket strategy logic for file-system-optimized buckets, where directories and files are keyed by volume id, bucket id, parent object id, and name.

## Important APIs and Types

It implements path classification, directory object-id lookup, file lookup, directory lookup, direct-key DU, and replicated DU calculation. It uses OM directory and file tables and `NSSummary` materialized totals.

## Control Flow

Construction resolves and stores volume and bucket object IDs. `determineKeyPath` walks path components from the bucket id, checking the directory table at each component and the file table for the leaf when no directory exists. `handleDirectKeys` seeks the file table by object-id prefix and emits direct child files. `getDirObjectId` walks directory table rows up to a cutoff.

## State and Persistence

The handler stores volumeId and bucketId only. It reads OM metadata and namespace summary tables; no writes occur.

## Dependencies and Integration Points

It is selected for `BucketLayout.FILE_SYSTEM_OPTIMIZED` by `BucketHandler` and supports namespace entity handlers plus key insight FSO path conversion.

## Risks and Edge Cases

Missing intermediate directories return UNKNOWN; missing leaf directory and file also returns UNKNOWN. `getDirObjectId` silently returns the last found object id if an intermediate component is missing, so callers depend on prior classification. Direct-key enumeration assumes RocksDB prefix ordering. `getDirInfo` requires at least volume/bucket/dir.

## Test Signals

Tests should cover nested directories, leaf files, missing intermediates, empty directories, direct-file DU with and without replica/listing, directory object-id cutoff, and object-id prefix seek boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java

## Purpose

`KeyEntityHandler` implements namespace APIs for a single key/file path.

## Important APIs and Types

It returns `NamespaceSummaryResponse` with `KeyObjectDBInfo`, `DUResponse` for the key's size, type-not-applicable quota, and type-not-applicable file-size distribution.

## Control Flow

Summary maps the `OmKeyInfo` returned by the bucket handler into `KeyObjectDBInfo` and reports zero child keys with directory/bucket/volume counts set to not-applicable values. DU reads the key, returns data size, and optionally replicated size. Quota and distribution return `TYPE_NOT_APPLICABLE`.

## State and Persistence

It writes nothing and reads the key from the appropriate OM key/file table via `BucketHandler.getKeyInfo`.

## Dependencies and Integration Points

It is created by `EntityHandler` when a layout-specific `BucketHandler.determineKeyPath` returns `KEY`.

## Risks and Edge Cases

`getDuResponse` does not null-check `keyInfo`, relying on prior classification. Object metadata shape depends on `KeyObjectDBInfo` and layout-specific key names.

## Test Signals

Tests should cover FSO, legacy, and OBS key lookup, replica DU, missing key after classification race, and type-not-applicable responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java

## Purpose

`LegacyBucketHandler` implements filesystem-style namespace behavior for legacy buckets when filesystem paths are enabled.

## Important APIs and Types

It uses the legacy key table, directory-marker keys, `OmKeyInfo`, `NSSummary`, and `DUResponse.DiskUsage`. It returns `BucketLayout.LEGACY`.

## Control Flow

`determineKeyPath` removes trailing slash, builds `/vol/bucket/key`, seeks the key table, and classifies exact match as KEY or exact match with trailing slash as DIRECTORY. `handleDirectKeys` seeks under a bucket or directory prefix, skips deeper descendants and directory markers, and optionally emits direct key rows. `getDirObjectId` builds the directory marker key ending in slash and returns its object id.

## State and Persistence

The handler stores volume, bucket, and bucket info. It reads key table and namespace summaries, with no writes.

## Dependencies and Integration Points

It is selected only for legacy buckets when OM filesystem paths are enabled. Entity handlers rely on it to make legacy marker directories look like directories.

## Risks and Edge Cases

Directory detection requires a marker key with a trailing slash. `getDirInfo` constructs only a minimal `OmDirectoryInfo` with `names[2]`, so deeper directory metadata can be imprecise. Direct-key depth filtering is string-split based and can be sensitive to path normalization. Missing directory marker throws `IOException`.

## Test Signals

Tests should cover exact key, marker directory, unknown path, nested direct-key filtering, marker skipping, directory object-id lookup, and legacy mode selection via config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java

## Purpose

`OBSBucketHandler` implements object-store bucket behavior, treating bucket contents as flat keys without directory support.

## Important APIs and Types

It uses the object-store key table, `OmKeyInfo`, `NSSummary`, and `DUResponse.DiskUsage`, and returns `BucketLayout.OBJECT_STORE`.

## Control Flow

`determineKeyPath` builds `/vol/bucket/key`, seeks the key table, and returns KEY only on exact match. `handleDirectKeys` seeks all keys under `/vol/bucket/`, emits every key if requested, and computes replicated direct-key totals. Directory lookup methods throw `UnsupportedOperationException`.

## State and Persistence

The handler stores volume, bucket, and bucket info. It reads OM key and namespace summary tables only.

## Dependencies and Integration Points

It is selected for `OBJECT_STORE` buckets and for legacy buckets when filesystem paths are disabled. Entity path parsing preserves slash-containing key names for this layout.

## Risks and Edge Cases

Because object-store keys may contain slashes, clients can see subpaths that are object names rather than directories. Directory APIs are invalid by design. Direct-key listing ignores `normalizedPath` when setting subpath and returns the raw object name.

## Test Signals

Tests should cover exact flat key lookup, slash-containing object names, unknown pseudo-directory paths, direct-key listing, replica DU, and unsupported directory calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java

## Purpose

`RootEntityHandler` implements namespace APIs for the root path `/` across all volumes and buckets.

## Important APIs and Types

It returns root `NamespaceSummaryResponse`, aggregate `DUResponse`, cluster-wide quota, and file-size distribution. It reads `OmVolumeArgs`, `OmBucketInfo`, optional root `OmPrefixInfo`, `SCMNodeStat`, and `NSSummary` rows.

## Control Flow

Summary lists all volumes and buckets, recursively counts directories and keys under every bucket, and includes root prefix metadata if present. DU iterates volumes and their buckets, sums materialized sizes, optionally calculates replicated bucket DU through layout-specific bucket handlers, emits per-volume rows, and sorts if requested. Quota uses SCM total capacity and root replicated DU. Distribution folds all bucket distributions.

## State and Persistence

No writes occur. Data comes from OM metadata tables, namespace summaries, and live SCM node stats.

## Dependencies and Integration Points

It is selected by `EntityHandler` for `/` and uses `BucketHandler` factories for replica-aware DU across layouts.

## Risks and Edge Cases

Replica-aware root DU can be expensive because it visits every bucket. Missing namespace summaries lower aggregate counts/sizes. Quota used is replicated bytes, unlike some lower-level quota handlers. Root prefix metadata may be absent and returns an empty object.

## Test Signals

Tests should cover empty clusters, multiple volumes/buckets, replica and non-replica DU, sorting limits, prefix metadata presence/absence, quota capacity, and distribution aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java

## Purpose

`UnknownEntityHandler` returns consistent path-not-found responses for namespace paths that cannot be resolved.

## Important APIs and Types

It implements all `EntityHandler` response methods by returning `ResponseStatus.PATH_NOT_FOUND` and, for summary, `EntityType.UNKNOWN`.

## Control Flow

There is no lookup logic. Each API method constructs the corresponding response DTO and sets the not-found status.

## State and Persistence

No state is written or read beyond base construction.

## Dependencies and Integration Points

It is created by `EntityHandler.getEntityHandler` when volume, bucket, directory, or key lookup fails.

## Risks and Edge Cases

The constructor passes null path and bucket handler to the base class; current methods do not use normalized path, but future additions must avoid dereferencing it. Endpoints usually wrap these responses in HTTP 200.

## Test Signals

Tests should cover unknown summary, DU, quota, and distribution bodies and verify endpoint HTTP semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java

## Purpose

`VolumeEntityHandler` implements namespace APIs for volume-level paths.

## Important APIs and Types

It returns `VolumeObjectDBInfo`, aggregate `CountStats`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse` for all buckets under a volume.

## Control Flow

Summary lists buckets under the volume and accumulates recursive directory/key counts. DU builds one row per bucket, sums materialized sizes, optionally calculates replicated DU through each bucket's `BucketHandler`, and sorts rows. Quota reads volume quota and sums unreplicated bucket sizes. Distribution aggregates file-size buckets from all child buckets.

## State and Persistence

The handler writes nothing. It reads OM volume/bucket tables and namespace summary rows.

## Dependencies and Integration Points

It is selected by `EntityHandler` after confirming volume existence. It uses `BucketHandler` only when replica-aware DU is requested.

## Risks and Edge Cases

Replica-aware DU can be expensive for many buckets. Missing bucket summaries reduce totals. Volume quota usage is unreplicated while root quota usage is replicated, so clients must understand the unit difference.

## Test Signals

Tests should cover empty volume, multiple buckets, replica DU, sorting, quota, missing volume metadata, distribution aggregation, and bucket layout mix.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/package-info.java

## Purpose

This package descriptor documents the handler package for different namespace entity and bucket types.

## Important APIs and Types

It declares package-level Javadoc and the `org.apache.hadoop.ozone.recon.api.handlers` package.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state or persistence exists.

## Dependencies and Integration Points

The package groups `EntityHandler`, concrete entity handlers, and bucket layout strategies used by `NSSummaryEndpoint` and key insight APIs.

## Risks and Edge Cases

Documentation can drift if new handler categories are added.

## Test Signals

Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.recon.api` as the package containing Recon API endpoint classes.

## Important APIs and Types

It contains only package-level Javadoc and the package declaration.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state or persistence exists.

## Dependencies and Integration Points

The file contributes source organization and generated documentation for Recon REST API classes.

## Risks and Edge Cases

The package description is broad and may become too generic as endpoints and services evolve.

## Test Signals

Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java

## Purpose

`AclMetadata` is a JSON DTO representing a single Ozone ACL in Recon API responses.

## Important APIs and Types

Fields are `type`, `name`, `scope`, and `aclList`, exposed through Jackson `@JsonProperty`. A builder enforces non-null type, name, and scope. Static helpers convert one or many `OzoneAcl` instances.

## Control Flow

`fromOzoneAcl` returns null for null input; otherwise it uppercases ACL type and scope strings, copies the ACL name, copies ACL rights strings, and builds the DTO. `fromOzoneAcls` streams a list through that converter.

## State and Persistence

The DTO is immutable after builder construction in normal use, though fields are not declared final. It persists nothing.

## Dependencies and Integration Points

It is used by object metadata DTOs such as `BucketObjectDBInfo` and likely volume/key metadata wrappers to serialize ACLs.

## Risks and Edge Cases

`fromOzoneAcls` does not null-check the list and will include null entries if the input contains null ACLs. The builder does not require `aclList`, so responses may contain null ACL lists.

## Test Signals

Tests should cover conversion from user/group ACLs, null ACL input, null ACL list handling, uppercase type/scope, and builder non-null enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java

## Purpose

`BucketObjectDBInfo` is the Recon API DTO for detailed bucket metadata read from OM DB.

## Important APIs and Types

It extends `ObjectDBInfo` and adds volume name, storage type, versioning flag, used bytes, snapshot used bytes, encryption info, default replication config, source volume/bucket, bucket layout, and owner. The `OmBucketInfo` constructor populates inherited metadata, quotas, namespace usage, timestamps, ACLs, and bucket-specific fields.

## Control Flow

The no-arg constructor supports serialization frameworks. The `OmBucketInfo` constructor performs a direct field mapping, including `AclMetadata.fromOzoneAcls`. Getters and setters expose all added fields except snapshot used bytes has only a getter in this file.

## State and Persistence

The object is a response DTO and does not persist data. Source persistence is OM bucket metadata.

## Dependencies and Integration Points

It is returned by `BucketEntityHandler` inside `NamespaceSummaryResponse` and depends on OM helper types such as `BucketEncryptionKeyInfo`, `BucketLayout`, `StorageType`, and `DefaultReplicationConfig`.

## Risks and Edge Cases

If `OmBucketInfo.getAcls()` is null, ACL conversion will throw. The DTO exposes encryption and replication helper objects directly, so JSON shape depends on those classes. Snapshot used bytes lacks a setter, which may matter for deserialization tests.

## Test Signals

Tests should verify full field mapping from `OmBucketInfo`, ACL serialization, linked bucket source fields, encryption and replication JSON shape, layout and owner fields, and null optional metadata behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java -->
