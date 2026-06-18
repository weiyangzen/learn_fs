# subset-b-008121 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketsResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketsResponse.java

## Purpose
Response envelope for bucket-list APIs. It carries a total count and the returned `BucketObjectDBInfo` collection so Recon callers can render paginated bucket inventory from OM-derived metadata.

## Important APIs, Types, And Functions
declares `BucketsResponse`; key fields include `totalCount`, `buckets`; important methods include `getTotalCount`, `getBuckets`.

## Control Flow
No internal branching; construction is a direct transfer of endpoint-computed count and bucket rows into Jackson-visible fields.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Endpoint tests should assert JSON keys `totalCount` and `buckets`, empty-list handling, and count/list consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketsResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStateResponse.java

## Purpose
Top-level Recon cluster state response aggregating pipeline, datanode, storage, container, namespace, deletion backlog, and service-id counters.

## Important APIs, Types, And Functions
declares `ClusterStateResponse`, `Builder`; key fields include `pipelines`, `totalDatanodes`, `healthyDatanodes`, `storageReport`, `containers`, `missingContainers`, `openContainers`, `deletedContainers`, `volumes`, `buckets`; important methods include `newBuilder`, `build`, `getPipelines`, `getTotalDatanodes`, `getHealthyDatanodes`, `getStorageReport`, `getContainers`, `getVolumes`, `getMissingContainers`, `getOpenContainers`, `getDeletedContainers`, `getBuckets`.

## Control Flow
The builder initializes all counters to zero, requires a non-null `ClusterStorageReport` at build time, and copies mutable builder state into a final response object.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required storage report validation, default zero counters, deleted-dir/key-pending fields, and HA service-id serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStorageReport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStorageReport.java

## Purpose
Cluster-wide storage capacity DTO for logical Ozone and underlying filesystem capacity values.

## Important APIs, Types, And Functions
declares `ClusterStorageReport`, `Builder`; key fields include `capacity`, `used`, `remaining`, `committed`, `minimumFreeSpace`, `reserved`, `filesystemCapacity`, `filesystemUsed`, `filesystemAvailable`, `capacity`; important methods include `getCapacity`, `getUsed`, `getRemaining`, `getCommitted`, `getMinimumFreeSpace`, `getReserved`, `getFilesystemCapacity`, `getFilesystemUsed`, `getFilesystemAvailable`, `newBuilder`, `validate`, `build`.

## Control Flow
The builder validates every numeric field is non-negative and logs, rather than rejects, logical inconsistency where used plus remaining exceeds capacity.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are rejecting negative inputs from upstream metric bugs while only warning on used/remaining/capacity inconsistency, which can still expose contradictory API values.

## Test Signals
Tests should cover negative-value exceptions, warning-only inconsistent totals, and JSON/Jackson compatibility with the no-arg constructor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerBlocksInfoWrapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerBlocksInfoWrapper.java

## Purpose
Wrapper for a container id, local block ids, local id count, and transaction id used by Recon container-block inspection APIs.

## Important APIs, Types, And Functions
declares `ContainerBlocksInfoWrapper`; key fields include `containerID`, `localIDList`, `localIDCount`, `txID`; important methods include `getContainerID`, `setContainerID`, `getLocalIDList`, `setLocalIDList`, `getLocalIDCount`, `setLocalIDCount`, `getTxID`, `setTxID`.

## Control Flow
Default construction creates an empty local-id list, container/count zero, and txID -1; setters are plain mutable DTO accessors.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should check omitted default fields from `JsonInclude`, non-empty block list serialization, and txID sentinel behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerBlocksInfoWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerDiscrepancyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerDiscrepancyInfo.java

## Purpose
Represents Recon/SCM discrepancy details for a container, including key count, pipelines, and where the container exists.

## Important APIs, Types, And Functions
declares `ContainerDiscrepancyInfo`; key fields include `containerID`, `numberOfKeys`, `pipelines`, `existsAt`; important methods include `getContainerID`, `setContainerID`, `getNumberOfKeys`, `setNumberOfKeys`, `getPipelines`, `setPipelines`, `getExistsAt`, `setExistsAt`.

## Control Flow
Mutable bean populated by discrepancy scanners; `existsAt` is excluded from JSON when empty.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify pipeline serialization and empty `existsAt` omission for UI compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerDiscrepancyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefix.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefix.java

## Purpose
Public immutable key for Recon container-to-key prefix indexing. It supports container-only, container plus key prefix, and container plus key version forms.

## Important APIs, Types, And Functions
declares `ContainerKeyPrefix`.

## Control Flow
Static factories delegate to the package-private implementation and `toKeyPrefixContainer` lets code convert only when a real key prefix exists.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover factory overloads, conversion to `KeyPrefixContainer`, and container-only use cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefix.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefixImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefixImpl.java

## Purpose
Package-private immutable implementation shared by `ContainerKeyPrefix` and `KeyPrefixContainer` to represent both lookup directions in Recon container DB indexes.

## Important APIs, Types, And Functions
declares `ContainerKeyPrefixImpl`; key fields include `containerId`, `keyPrefix`, `keyVersion`; important methods include `getContainerId`, `getKeyPrefix`, `getKeyVersion`, `toContainerKeyPrefix`, `toKeyPrefixContainer`, `hashCode`, `equals`.

## Control Flow
Stores container id, key prefix, and key version; conversion to `KeyPrefixContainer` returns null when the key prefix is absent or empty.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are null handling in `hashCode` for container-only keys, equality assumptions across interface views, and callers expecting conversion to always return a key-prefix object.

## Test Signals
Tests should cover equality, conversion, and the null-prefix hashCode risk because `hashCode` calls `keyPrefix.hashCode()` while container-only keys are allowed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefixImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerMetadata.java

## Purpose
Container inventory row for container list APIs, exposing container id, number of keys, and SCM pipeline objects.

## Important APIs, Types, And Functions
declares `ContainerMetadata`; key fields include `containerID`, `numberOfKeys`, `pipelines`; important methods include `getContainerID`, `setContainerID`, `getNumberOfKeys`, `setNumberOfKeys`, `getPipelines`, `setPipelines`.

## Control Flow
Constructed with a container id and then filled by setters; JAXB annotations retain XML field names while Jackson exposes pipelines.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert XML/Jackson names and behavior when pipelines are absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerStateCounts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerStateCounts.java

## Purpose
Simple mutable holder for total, missing, open, and deleted container counts used when building cluster state summaries.

## Important APIs, Types, And Functions
declares `ContainerStateCounts`; key fields include `totalContainerCount`, `missingContainerCount`, `openContainersCount`, `deletedContainersCount`; important methods include `getTotalContainerCount`, `setTotalContainerCount`, `getMissingContainerCount`, `setMissingContainerCount`, `getOpenContainersCount`, `setOpenContainersCount`, `getDeletedContainersCount`, `setDeletedContainersCount`.

## Control Flow
No validation or derived values; callers are responsible for computing the counts consistently from SCM/recon tables.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should focus on services that populate it rather than this bean, plus zero/default behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerStateCounts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainersResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainersResponse.java

## Purpose
Response envelope for container list APIs. The external JSON root is `data`, containing total count, previous pagination key, and container rows.

## Important APIs, Types, And Functions
declares `ContainersResponse`, `ContainersResponseData`; key fields include `containersResponseData`, `totalCount`, `prevKey`, `containers`; important methods include `getContainersResponseData`, `setContainersResponseData`, `getTotalCount`, `getContainers`, `getPrevKey`.

## Control Flow
The default constructor creates zero count, empty container collection, and prevKey zero; non-default construction wraps values in `ContainersResponseData`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert nested JSON shape and pagination `prevKey` semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainersResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/CountStats.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/CountStats.java

## Purpose
Namespace count DTO for volume, bucket, directory, and key totals returned by namespace summary APIs.

## Important APIs, Types, And Functions
declares `CountStats`; key fields include `numVolume`, `numBucket`, `numTotalDir`, `numTotalKey`; important methods include `getNumVolume`, `getNumBucket`, `getNumTotalDir`, `getNumTotalKey`.

## Control Flow
Immutable after construction with JSON property names matching UI expectations such as `numVolume` and `numKey`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover sentinel `-1` conventions at the handler level and JSON property names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/CountStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DUResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DUResponse.java

## Purpose
Disk usage response for namespace DU requests, including aggregate size, replicated size, direct key size, subpath count, and per-subpath usage rows.

## Important APIs, Types, And Functions
declares `DUResponse`, `DiskUsage`; key fields include `status`, `path`, `size`, `sizeWithReplica`, `count`, `duData`, `keySize`, `subpath`, `size`, `sizeWithReplica`; important methods include `getStatus`, `getSize`, `getSizeWithReplica`, `getPath`, `getCount`, `getKeySize`, `getDuData`, `getSize`, `getSubpath`, `getSizeWithReplica`, `isKey`.

## Control Flow
Defaults status to OK, initializes subpaths, and uses -1 sentinels when replica/direct-key accounting is disabled or unavailable.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover status changes, replicated-size sentinel values, `DiskUsage.isKey`, and empty subpath responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DUResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DataNodeMetricsServiceResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DataNodeMetricsServiceResponse.java

## Purpose
Response from datanode metrics collection, especially pending deletion byte metrics per datanode plus collection status and failure counts.

## Important APIs, Types, And Functions
declares `are`, `DataNodeMetricsServiceResponse`, `Builder`; key fields include `status`, `totalPendingDeletionSize`, `pendingDeletionPerDataNode`, `totalNodesQueried`, `totalNodeQueryFailures`, `status`, `totalPendingDeletionSize`, `pendingDeletion`, `totalNodesQueried`, `totalNodeQueryFailures`; important methods include `getStatus`, `getTotalPendingDeletionSize`, `getPendingDeletionPerDataNode`, `getTotalNodesQueried`, `getTotalNodeQueryFailures`, `newBuilder`, `setStatus`, `setTotalPendingDeletionSize`, `setPendingDeletion`, `setTotalNodesQueried`, `setTotalNodeQueryFailures`, `build`.

## Control Flow
Builder copies metric status, totals, per-node rows, queried count, and query failure count without extra validation.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should simulate full, partial, and failed metric collection statuses and verify failure metadata is exposed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DataNodeMetricsServiceResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetadata.java

## Purpose
Detailed datanode row for Recon datanode APIs, combining SCM node state, operational state, heartbeat, storage report, pipeline membership, container counts, version, layout, and network location.

## Important APIs, Types, And Functions
declares `DatanodeMetadata`, `Builder`; key fields include `uuid`, `hostname`, `state`, `opState`, `lastHeartbeat`, `datanodeStorageReport`, `pipelines`, `containers`, `openContainers`, `leaderCount`; important methods include `getHostname`, `getState`, `getOperationalState`, `getLastHeartbeat`, `getDatanodeStorageReport`, `getPipelines`, `getContainers`, `getOpenContainers`, `getLeaderCount`, `getUuid`, `getVersion`, `getSetupTime`.

## Control Flow
`Builder.setDatanode` extracts identity and version fields from `DatanodeInfo`; `build` requires hostname, state, last heartbeat, and storage report.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson inclusion, JAXB/XML, SCM datanode metadata, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are required builder fields not being set, optional fields disappearing from JSON due to inclusion rules, and SCM state/version fields drifting from `DatanodeInfo` semantics.

## Test Signals
Tests should cover required-field null checks, `setDatanode` mapping, optional JSON omission, and stale heartbeat/state rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetrics.java

## Purpose
Small DTO for decommission-related datanode metrics: start time, unclosed pipelines, under-replicated containers, and unclosed containers.

## Important APIs, Types, And Functions
declares `DatanodeMetrics`; key fields include `decommissionStartTime`, `numOfUnclosedPipelines`, `numOfUnderReplicatedContainers`, `numOfUnclosedContainers`; important methods include `getDecommissionStartTime`, `setDecommissionStartTime`, `getNumOfUnclosedPipelines`, `setNumOfUnclosedPipelines`, `getNumOfUnderReplicatedContainers`, `setNumOfUnderReplicatedContainers`, `getNumOfUnclosedContainers`, `setNumOfUnclosedContainers`.

## Control Flow
Mutable setters let decommission status code attach metrics collected from SCM/Recon services.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should check JSON names and numeric type expectations, especially double-valued container metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePendingDeletionMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePendingDeletionMetrics.java

## Purpose
Immutable row describing pending deletion bytes for one datanode, keyed by host name and datanode UUID.

## Important APIs, Types, And Functions
declares `DatanodePendingDeletionMetrics`; key fields include `hostName`, `datanodeUuid`, `pendingBlockSize`; important methods include `getHostName`, `getPendingBlockSize`, `getDatanodeUuid`.

## Control Flow
A `JsonCreator` constructor supports deserialization while public getters expose the three values.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify constructor/Jackson round trip and large byte counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePendingDeletionMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePipeline.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePipeline.java

## Purpose
Compact pipeline descriptor embedded in datanode metadata, carrying pipeline UUID, replication type, replication factor string, and leader node.

## Important APIs, Types, And Functions
declares `DatanodePipeline`; key fields include `pipelineID`, `replicationType`, `replicationFactor`, `leaderNode`; important methods include `getPipelineID`, `getReplicationType`, `getReplicationFactor`, `getLeaderNode`.

## Control Flow
Constructed from a `ReplicationConfig`, turning type and replication into UI-friendly strings.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover Ratis and EC replication string forms and nullable leader handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeStorageReport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeStorageReport.java

## Purpose
Per-datanode storage report mirroring cluster storage metrics plus datanode UUID and hostname.

## Important APIs, Types, And Functions
declares `DatanodeStorageReport`, `Builder`; key fields include `datanodeUuid`, `hostName`, `capacity`, `used`, `remaining`, `committed`, `minimumFreeSpace`, `reserved`, `filesystemCapacity`, `filesystemUsed`; important methods include `getDatanodeUuid`, `getHostName`, `getCapacity`, `getUsed`, `getRemaining`, `getCommitted`, `getMinimumFreeSpace`, `getReserved`, `getFilesystemCapacity`, `getFilesystemUsed`, `getFilesystemAvailable`, `newBuilder`.

## Control Flow
Builder defaults strings to empty, requires hostName non-null, rejects negative metrics, and logs inconsistent used/remaining/capacity totals.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are rejecting negative metrics, allowing warning-only logical inconsistency, and requiring host name while other identity fields may be empty.

## Test Signals
Tests should cover negative validation, host null rejection, warning-only inconsistency, and filesystem metric propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeStorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodesResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodesResponse.java

## Purpose
Datanode list response carrying total count, datanode metadata rows, and optional failed-node error details.

## Important APIs, Types, And Functions
declares `DatanodesResponse`; key fields include `totalCount`, `datanodes`, `failedNodeErrorResponseMap`; important methods include `getTotalCount`, `getDatanodes`, `getFailedNodeErrorResponseMap`, `setFailedNodeErrorResponseMap`.

## Control Flow
Constructors initialize the error map to empty and `JsonInclude.NON_EMPTY` hides it until failures are present.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover normal list output and partial-failure maps from decommission/remove flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodesResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DecommissionStatusInfoResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DecommissionStatusInfoResponse.java

## Purpose
Response object for decommission status of a single datanode, including node details, decommission metrics, and container groups by status/category.

## Important APIs, Types, And Functions
declares `DecommissionStatusInfoResponse`; key fields include `dataNodeDetails`, `datanodeMetrics`, `containers`; important methods include `getDataNodeDetails`, `setDataNodeDetails`, `getDatanodeMetrics`, `setDatanodeMetrics`, `getContainers`, `setContainers`.

## Control Flow
Plain mutable DTO populated by decommission APIs from HDDS `DatanodeDetails`, `DatanodeMetrics`, and container ID maps.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify JSON names and container map grouping for under-replicated, unclosed, or related decommission categories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DecommissionStatusInfoResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletedContainerInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletedContainerInfo.java

## Purpose
DTO for deleted-container reports with container identity, pipeline, key count, state timestamps, used bytes, and replication details.

## Important APIs, Types, And Functions
declares `DeletedContainerInfo`; key fields include `containerID`, `pipelineID`, `numberOfKeys`, `containerState`, `stateEnterTime`, `lastUsed`, `usedBytes`, `replicationConfig`, `replicationFactor`; important methods include `getContainerID`, `getPipelineID`, `getNumberOfKeys`, `getContainerState`, `getStateEnterTime`, `getLastUsed`, `getUsedBytes`, `getReplicationConfig`, `getReplicationFactor`.

## Control Flow
Uses `JsonInclude` to omit default/empty values, so callers can return sparse rows without noisy zeros.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover replication config/factor serialization, omitted defaults, and timestamp/unit consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletedContainerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletionPendingBytesByComponent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletionPendingBytesByComponent.java

## Purpose
Aggregate response for bytes pending deletion, with total bytes and a nested component-to-breakdown map.

## Important APIs, Types, And Functions
declares `DeletionPendingBytesByComponent`; key fields include `total`, `byComponent`; important methods include `getTotal`, `getByComponent`.

## Control Flow
Immutable constructor-only holder; map structure is supplied by the caller and exposed directly.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify nested map JSON shape and that total matches component sums in producing services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletionPendingBytesByComponent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityMetaData.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityMetaData.java

## Purpose
Metadata row for namespace entity listings and heatmap inputs: value label, child/entity count, and read access count.

## Important APIs, Types, And Functions
declares `EntityMetaData`; key fields include `val`, `count`, `readAccessCount`; important methods include `getVal`, `setVal`, `getCount`, `setCount`, `getReadAccessCount`, `setReadAccessCount`.

## Control Flow
Mutable bean with simple Jackson property mapping.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert counts and read-access count population in namespace/heatmap endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityReadAccessHeatMapResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityReadAccessHeatMapResponse.java

## Purpose
Tree node for read-access heatmap responses, containing label/path, size, access count range, color value, and child nodes.

## Important APIs, Types, And Functions
declares `EntityReadAccessHeatMapResponse`; key fields include `label`, `path`, `children`, `size`, `accessCount`, `minAccessCount`, `maxAccessCount`, `color`; important methods include `getLabel`, `getPath`, `getSize`, `getAccessCount`, `getChildren`, `getMinAccessCount`, `getMaxAccessCount`, `getColor`, `equals`, `hashCode`.

## Control Flow
Constructor initializes children to an empty list; equality and hash code compare structural fields so tests can compare expected trees.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover nested tree serialization, min/max/color calculations, and equality with children.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityReadAccessHeatMapResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityType.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityType.java

## Purpose
Namespace entity discriminator and factory for the handler class that implements root, volume, bucket, directory, key, or unknown-path behavior.

## Important APIs, Types, And Functions
declares `EntityType`; important methods include `create`, `create`, `create`, `create`, `create`, `create`, `create`.

## Control Flow
Each enum constant overrides `create` and wires shared Recon namespace/OM/SCM dependencies into the correct handler implementation.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Recon namespace summary. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover path classification integration, especially `UNKNOWN`, and verify each type returns the expected handler class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ExportJob.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ExportJob.java

## Purpose
In-memory state object for asynchronous CSV export jobs, including lifecycle timestamps, progress, file exposure, queue position, and download limits.

## Important APIs, Types, And Functions
declares `ExportJob`, `JobStatus`; key fields include `jobId`, `state`, `status`, `submittedAt`, `startedAt`, `completedAt`, `totalRecords`, `estimatedTotal`, `filePath`, `fileName`; important methods include `getJobId`, `getState`, `getStatus`, `getSubmittedAt`, `getStartedAt`, `getCompletedAt`, `getTotalRecords`, `getEstimatedTotal`, `getFilePath`, `getFileName`, `getErrorMessage`, `getProgressPercent`.

## Control Flow
`setStatus` stamps start/completion times once; `setFilePath` exposes only the filename; `tryReserveDownload` uses an atomic compare-and-set loop to enforce max downloads under concurrency.

## State And Persistence Behavior
State is in-memory job state: lifecycle timestamps, counters, file path/name, and atomic download reservations. It is not itself durable, so restart behavior depends on the export service around it.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are in-memory lifecycle loss on restart, progress overflow/truncation for very large estimates, and callers using `isDownloadAllowed` instead of atomic reservation for enforcement.

## Test Signals
Tests should cover status transitions, progress math, filename extraction, and concurrent download reservation limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ExportJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FeatureProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FeatureProvider.java

## Purpose
Static feature metadata provider for Recon feature availability, currently tracking whether HeatMap should be disabled based on configuration.

## Important APIs, Types, And Functions
declares `FeatureProvider`, `Feature`; key fields include `featureDisableMap`, `featureName`; important methods include `getFeatureName`, `of`, `getFeatureDisableMap`, `getAllDisabledFeatures`, `initFeatureSupport`, `resetInitOfFeatureSupport`.

## Control Flow
`initFeatureSupport` resets the disable map then disables HeatMap when the heatmap feature flag is false or no provider class is configured.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Ozone configuration. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are static mutable feature state shared across tests/process lifetime and `Feature.of` throwing `NoSuchElementException` before its explicit invalid-value error path.

## Test Signals
Tests should cover enabled/disabled config combinations and the `Feature.of` invalid-name path, which currently uses `findFirst().get()` before its explicit error branch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FeatureProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FileSizeDistributionResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FileSizeDistributionResponse.java

## Purpose
Response for namespace file size distribution, carrying an integer bucket array and status.

## Important APIs, Types, And Functions
declares `FileSizeDistributionResponse`; key fields include `fileSizeDist`, `status`; important methods include `getStatus`, `getFileSizeDist`, `setStatus`, `setFileSizeDist`.

## Control Flow
Default construction fills the distribution with zeros using `ReconConstants.NUM_OF_FILE_SIZE_BINS` and status OK.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover default bin count, custom distribution assignment, and error status handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FileSizeDistributionResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalNamespaceReport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalNamespaceReport.java

## Purpose
Small immutable aggregate for namespace-level total used space and total key count.

## Important APIs, Types, And Functions
declares `GlobalNamespaceReport`; key fields include `totalUsedSpace`, `totalKeys`; important methods include `getTotalUsedSpace`, `getTotalKeys`.

## Control Flow
Values are constructor-provided and exposed via Jackson properties.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify aggregation service math and JSON property names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalNamespaceReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalStorageReport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalStorageReport.java

## Purpose
Global storage aggregate for capacity distribution APIs, summarizing filesystem capacity, reserved space, Ozone capacity, used/free/committed space, and minimum free space.

## Important APIs, Types, And Functions
declares `GlobalStorageReport`, `Builder`; key fields include `totalFileSystemCapacity`, `totalReservedSpace`, `totalOzoneCapacity`, `totalOzoneUsedSpace`, `totalOzoneFreeSpace`, `totalOzoneCommittedSpace`, `totalMinimumFreeSpace`, `totalReservedSpace`, `totalOzoneCapacity`, `totalOzoneUsedSpace`; important methods include `getTotalFileSystemCapacity`, `getTotalReservedSpace`, `getTotalOzoneCapacity`, `getTotalOzoneUsedSpace`, `getTotalOzoneFreeSpace`, `getTotalOzoneCommittedSpace`, `getTotalMinimumFreeSpace`, `newBuilder`, `setTotalReservedSpace`, `setTotalOzoneCapacity`, `setTotalOzoneUsedSpace`, `setTotalOzoneFreeSpace`.

## Control Flow
Builder computes `totalFileSystemCapacity` as reserved plus Ozone capacity and validates all totals are non-negative.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover builder validation, derived filesystem capacity, and large cluster totals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalStorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/HealthCheckResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/HealthCheckResponse.java

## Purpose
Simple health response with message and numeric status for Recon health endpoints.

## Important APIs, Types, And Functions
declares `HealthCheckResponse`, `Builder`; key fields include `message`, `status`, `message`, `status`; important methods include `getMessage`, `getStatus`, `build`.

## Control Flow
Builder copies message/status into an immutable response with Jackson properties.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert status/message mapping from health resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/HealthCheckResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/IsoDateAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/IsoDateAdapter.java

## Purpose
JAXB adapter converting epoch-millisecond timestamps to UTC ISO-8601 strings for XML output.

## Important APIs, Types, And Functions
declares `IsoDateAdapter`; key fields include `iso8861Formatter`; important methods include `unmarshal`, `marshal`.

## Control Flow
`marshal` formats an `Instant` at `ZoneOffset.UTC`; `unmarshal` returns null because this adapter is intended for outbound serialization only.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover epoch formatting, UTC timezone, null behavior, and the unsupported inbound path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/IsoDateAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyEntityInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyEntityInfo.java

## Purpose
DTO for key or deleted-directory insight rows, including key/path, state age, logical and replicated size, replication config, creation/modification times, and `isKey` flag.

## Important APIs, Types, And Functions
declares `KeyEntityInfo`; key fields include `key`, `path`, `inStateSince`, `size`, `replicatedSize`, `replicationConfig`, `creationTime`, `modificationTime`, `isKey`; important methods include `getKey`, `getPath`, `getInStateSince`, `getSize`, `getReplicatedSize`, `getReplicationConfig`, `getCreationTime`, `getModificationTime`, `isKey`.

## Control Flow
Default construction sets times to current instant milliseconds and `isKey` true; setters allow insight services to override state and size fields.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, HDDS replication. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover default time behavior, replicated size fields, and JSON omission for null replication config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyEntityInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyInsightInfoResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyInsightInfoResponse.java

## Purpose
Paged response for key insight APIs covering open/deleted/repeated/non-FSO/FSO key collections and aggregate replicated/unreplicated sizes.

## Important APIs, Types, And Functions
declares `KeyInsightInfoResponse`; key fields include `lastKey`, `replicatedDataSize`, `unreplicatedDataSize`, `nonFSOKeyInfoList`, `fsoKeyInfoList`, `repeatedOmKeyInfoList`, `deletedDirInfoList`, `responseCode`; important methods include `getLastKey`, `getReplicatedDataSize`, `getUnreplicatedDataSize`, `getNonFSOKeyInfoList`, `getFsoKeyInfoList`, `getRepeatedOmKeyInfoList`, `getDeletedDirInfoList`, `getResponseCode`.

## Control Flow
Constructor initializes all row lists and status OK; services fill the relevant list and `lastKey` for pagination.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover each list type, aggregate sizes, pagination cursor, and non-empty JSON inclusion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyInsightInfoResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyMetadata.java

## Purpose
Detailed key metadata response for container-to-key and key lookup APIs, including volume/bucket/key path, data size, versions, block ids, and timestamps.

## Important APIs, Types, And Functions
declares `KeyMetadata`, `ContainerBlockMetadata`; key fields include `volume`, `bucket`, `key`, `completePath`, `dataSize`, `versions`, `blockIds`, `creationTime`, `modificationTime`, `containerID`; important methods include `getVolume`, `getBucket`, `getKey`, `getDataSize`, `getCreationTime`, `getModificationTime`, `getVersions`, `getBlockIds`, `getCompletePath`, `getContainerID`, `getLocalID`.

## Control Flow
Maintains sorted version/block maps with nested `ContainerBlockMetadata` rows for container/local block IDs.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify version ordering, block-id grouping, complete path construction, and timestamp serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyObjectDBInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyObjectDBInfo.java

## Purpose
Object DB representation of an OM key for Recon APIs, including volume, bucket, key name, size, location versions, replication, encryption, file flag, and file name.

## Important APIs, Types, And Functions
declares `KeyObjectDBInfo`; key fields include `volumeName`, `bucketName`, `keyName`, `dataSize`, `keyLocationVersions`, `replicationConfig`, `encInfo`, `isFile`, `fileName`; important methods include `getVolumeName`, `getBucketName`, `getKeyName`, `getDataSize`, `getKeyLocationVersions`, `getReplicationConfig`, `isFile`, `getFileName`, `getEncInfo`.

## Control Flow
The `OmKeyInfo` constructor copies only fields needed by Recon/UI from OM metadata; setters support tests and manual composition.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, HDDS replication. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover constructor mapping from `OmKeyInfo`, encrypted keys, directory-vs-file flags, and replication info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyObjectDBInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyPrefixContainer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyPrefixContainer.java

## Purpose
Public immutable view for key-prefix-to-container indexing, complementing `ContainerKeyPrefix`.

## Important APIs, Types, And Functions
declares `KeyPrefixContainer`.

## Control Flow
Static factories delegate to `ContainerKeyPrefixImpl`; `toContainerKeyPrefix` supports reverse conversion for container-centric index code.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover factory overloads, reverse conversion, and key version preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyPrefixContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeysResponse.java

## Purpose
Response envelope for detailed key metadata lists, exposing total count, key rows, and the last key cursor.

## Important APIs, Types, And Functions
declares `KeysResponse`; key fields include `totalCount`, `keys`, `lastKey`; important methods include `getTotalCount`, `getKeys`, `getLastKey`.

## Control Flow
Constructor-only DTO; pagination semantics are supplied by the endpoint.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert last-key pagination and collection/count consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeysResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ListKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ListKeysResponse.java

## Purpose
Namespace list-keys response used by Recon UI/chatbot: status, path, replicated and unreplicated totals, last key cursor, and basic key rows.

## Important APIs, Types, And Functions
declares `ListKeysResponse`; key fields include `status`, `path`, `replicatedDataSize`, `unReplicatedDataSize`, `lastKey`, `keys`; important methods include `getStatus`, `setStatus`, `getReplicatedDataSize`, `setReplicatedDataSize`, `getUnReplicatedDataSize`, `setUnReplicatedDataSize`, `getPath`, `setPath`, `getKeys`, `setKeys`, `getLastKey`, `setLastKey`.

## Control Flow
Defaults status OK and initializes an empty `ReconBasicOmKeyInfo` list; non-empty lists are included in JSON.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover empty directories, pagination, error statuses, and aggregate size totals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ListKeysResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainerMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainerMetadata.java

## Purpose
Metadata for a missing container, including missing-since timestamp, key count, pipeline UUID, and historical replica locations.

## Important APIs, Types, And Functions
declares `MissingContainerMetadata`; key fields include `containerID`, `missingSince`, `keys`, `pipelineID`, `replicas`; important methods include `getContainerID`, `getKeys`, `getReplicas`, `getMissingSince`, `getPipelineID`.

## Control Flow
Constructed from unhealthy-container table records plus `ContainerHistory` rows; JAXB annotations preserve XML field names.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover conversion from missing-container records and replica history output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainerMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainersResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainersResponse.java

## Purpose
Envelope for missing-container APIs with total count and missing-container rows.

## Important APIs, Types, And Functions
declares `MissingContainersResponse`; key fields include `totalCount`, `containers`; important methods include `getTotalCount`, `getContainers`.

## Control Flow
Constructor-only DTO with Jackson property names `totalCount` and `containers`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover empty and paginated missing-container lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainersResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NSSummary.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NSSummary.java

## Purpose
Persisted namespace summary value used by Recon namespace summarization, tracking file counts, logical and replicated sizes, file-size distribution buckets, child directory object IDs, directory name, and parent ID.

## Important APIs, Types, And Functions
declares `NSSummary`; key fields include `numOfFiles`, `sizeOfFiles`, `replicatedSizeOfFiles`, `fileSizeBucket`, `childDir`, `dirName`, `parentId`; important methods include `getNumOfFiles`, `getSizeOfFiles`, `getReplicatedSizeOfFiles`, `getFileSizeBucket`, `getChildDir`, `getDirName`, `addChildDir`, `removeChildDir`, `getParentId`, `toString`.

## Control Flow
Mutable state supports increment/update workflows; child directory set is initialized, add/remove helpers mutate it, and `setDirName` strips trailing slash.

## State And Persistence Behavior
This type is persistence-adjacent: Recon stores or decodes it from OM/Recon metadata representations, so field compatibility and codec/protobuf behavior are part of the durable contract.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are mutable persisted summary drift, incorrect file-size bucket lengths, and child directory set updates going out of sync with OM events.

## Test Signals
Tests should cover serialization/deserialization through Recon tables, child directory mutation, file-size bucket length, and trailing slash normalization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NSSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NamespaceSummaryResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NamespaceSummaryResponse.java

## Purpose
Response for namespace summary lookups, combining path, entity type, count stats, object metadata, and response status.

## Important APIs, Types, And Functions
declares `NamespaceSummaryResponse`, `Builder`; key fields include `path`, `entityType`, `countStats`, `objectDBInfo`, `status`, `path`, `entityType`, `countStats`, `objectDBInfo`, `status`; important methods include `newBuilder`, `getPath`, `getCountStats`, `getEntityType`, `getStatus`, `getObjectDBInfo`, `build`.

## Control Flow
Builder defaults status OK, path empty, and entity type UNKNOWN, then requires non-null path/entityType/status on build.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required fields, invalid path status, and object metadata presence by entity type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NamespaceSummaryResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ObjectDBInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ObjectDBInfo.java

## Purpose
Base object metadata DTO for namespace responses with metadata map, name, quotas, used namespace, creation/modification times, and ACLs.

## Important APIs, Types, And Functions
declares `ObjectDBInfo`; key fields include `metadata`, `name`, `quotaInBytes`, `quotaInNamespace`, `usedNamespace`, `creationTime`, `modificationTime`, `acls`; important methods include `getMetadata`, `getName`, `getQuotaInBytes`, `getQuotaInNamespace`, `getUsedNamespace`, `getCreationTime`, `getModificationTime`, `getAcls`.

## Control Flow
Constructors can populate common fields from OM directory or prefix info; subclasses add volume/bucket-specific data.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover directory/prefix constructor mapping, ACL serialization, and quota sentinel values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ObjectDBInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/OpenKeyBytesInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/OpenKeyBytesInfo.java

## Purpose
Aggregate byte counters for open keys/files, multipart open keys, and their total.

## Important APIs, Types, And Functions
declares `OpenKeyBytesInfo`; key fields include `openKeyAndFileBytes`, `multipartOpenKeyBytes`, `totalOpenKeyBytes`; important methods include `getTotalOpenKeyBytes`, `getOpenKeyAndFileBytes`, `getMultipartOpenKeyBytes`.

## Control Flow
Constructor-only holder; producing services compute the sums from OM open-key and multipart tables.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify total equals component sums and large byte counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/OpenKeyBytesInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ParamInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ParamInfo.java

## Purpose
Mutable cursor/parameter helper for namespace/key insight scans, tracking start prefix, key size threshold, creation date and epoch, replication type, limits, pagination keys, and current count.

## Important APIs, Types, And Functions
declares `ParamInfo`; key fields include `startPrefix`, `keySize`, `creationDate`, `creationDateEpoch`, `replicationType`, `limit`, `prevKey`, `lastKey`, `skipPrevKeyDone`, `currentCount`; important methods include `getStartPrefix`, `getKeySize`, `getCreationDate`, `getCreationDateEpoch`, `getReplicationType`, `getLimit`, `getCurrentCount`, `getPrevKey`, `isSkipPrevKeyDone`, `getLastKey`.

## Control Flow
Constructor converts date strings using `ReconUtils` in the default timezone and stores both text and epoch forms; pagination setters track scan progress.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are timezone-sensitive date parsing, mutable pagination flags, and caller confusion between previous, last, and start prefix cursors.

## Test Signals
Tests should cover date parsing, timezone behavior, invalid dates, limit/current count, and previous/last-key pagination flags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ParamInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelineMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelineMetadata.java

## Purpose
Detailed pipeline DTO for Recon pipeline APIs, including ID, state, leader, datanodes, leader election metrics, replication config, duration, and container count.

## Important APIs, Types, And Functions
declares `PipelineMetadata`, `Builder`; key fields include `pipelineId`, `status`, `leaderNode`, `datanodes`, `lastLeaderElection`, `duration`, `leaderElections`, `replicationType`, `replicationFactor`, `containers`; important methods include `getPipelineId`, `getStatus`, `getLeaderNode`, `getDatanodes`, `getLastLeaderElection`, `getDuration`, `getLeaderElections`, `getReplicationType`, `getReplicationFactor`, `getContainers`, `newBuilder`, `build`.

## Control Flow
Builder defaults leader/duration/election/container fields, requires pipeline id, status, datanodes, and replication type, and derives replication strings from `ReplicationConfig`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required-field validation, Ratis and EC replication strings, and absent leader handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelineMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelinesResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelinesResponse.java

## Purpose
Response envelope for pipeline list APIs with total count and pipeline metadata rows.

## Important APIs, Types, And Functions
declares `PipelinesResponse`; key fields include `totalCount`, `pipelines`; important methods include `getTotalCount`, `getPipelines`.

## Control Flow
Default constructor initializes zero count and an empty list; alternate constructor accepts endpoint-produced values.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert empty output, count consistency, and pipeline row serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelinesResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainerMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainerMetadata.java

## Purpose
DTO for quasi-closed container reports, including container/pipeline identity, key count, state-enter time, expected/actual replica counts, and replica history.

## Important APIs, Types, And Functions
declares `QuasiClosedContainerMetadata`; key fields include `containerID`, `pipelineID`, `keys`, `stateEnterTime`, `expectedReplicaCount`, `actualReplicaCount`, `replicas`; important methods include `getContainerID`, `setContainerID`, `getPipelineID`, `setPipelineID`, `getKeys`, `setKeys`, `getStateEnterTime`, `setStateEnterTime`, `getExpectedReplicaCount`, `setExpectedReplicaCount`, `getActualReplicaCount`, `setActualReplicaCount`.

## Control Flow
Mutable bean with Jackson properties used by quasi-closed container endpoints.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover replica-count deltas at producing service level and JSON property names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainerMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainersResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainersResponse.java

## Purpose
Paged response for quasi-closed container reports with count, first/last pagination keys, and container rows.

## Important APIs, Types, And Functions
declares `QuasiClosedContainersResponse`; key fields include `quasiClosedCount`, `firstKey`, `lastKey`, `containers`; important methods include `getQuasiClosedCount`, `setQuasiClosedCount`, `getFirstKey`, `setFirstKey`, `getLastKey`, `setLastKey`, `getContainers`, `setContainers`.

## Control Flow
Plain mutable response; handlers populate cursor and container list after database scans.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover first/last key pagination and empty result sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainersResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuotaUsageResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuotaUsageResponse.java

## Purpose
Quota usage response exposing allowed quota, used quota, and status.

## Important APIs, Types, And Functions
declares `QuotaUsageResponse`; key fields include `quota`, `quotaUsed`, `responseCode`; important methods include `getQuota`, `getQuotaUsed`, `getResponseCode`, `setQuota`, `setQuotaUsed`, `setResponseCode`.

## Control Flow
Defaults status OK and stores quota values through setters.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover quota exceeded/not-found statuses and byte vs namespace quota producer behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuotaUsageResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ReconBasicOmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ReconBasicOmKeyInfo.java

## Purpose
Lightweight immutable OM key representation optimized for Recon event handling and list-key responses without full key location/ACL payloads.

## Important APIs, Types, And Functions
declares `ReconBasicOmKeyInfo`, `Builder`; key fields include `volumeName`, `bucketName`, `keyName`, `dataSize`, `creationTime`, `modificationTime`, `key`, `path`, `replicatedSize`, `replicationConfig`; important methods include `getCodec`, `getVolumeName`, `getBucketName`, `getKeyName`, `getDataSize`, `getCreationTime`, `getModificationTime`, `getReplicationConfig`, `isFile`, `getReplicatedSize`, `getKey`, `getPath`.

## Control Flow
Provides a decode-only codec from `KeyInfoProtoLight`, protobuf conversion helpers from light and full key protos, replicated-size derivation through `QuotaUtil`, and JSON getters that require `key` and `path` to be set before serialization.

## State And Persistence Behavior
This type is persistence-adjacent: Recon stores or decodes it from OM/Recon metadata representations, so field compatibility and codec/protobuf behavior are part of the durable contract.

## Dependencies And Integration Points
Integrates with Jackson, HDDS replication, OM protobuf. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are serialization failures when `key` or `path` are not set, decode-only codec expectations, replicated-size changes when replication config semantics change, and equality/hashCode using different field sets.

## Test Signals
Tests should cover protobuf conversion, decode-only codec behavior, replicated size for replication configs, directory key naming, and serialization exceptions when key/path are missing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ReconBasicOmKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/RemoveDataNodesResponseWrapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/RemoveDataNodesResponseWrapper.java

## Purpose
Wrapper mapping remove-datanode request categories or IDs to `DatanodesResponse` objects.

## Important APIs, Types, And Functions
declares `RemoveDataNodesResponseWrapper`; key fields include `datanodesResponseMap`; important methods include `getDatanodesResponseMap`, `setDatanodesResponseMap`.

## Control Flow
Initializes an empty map and exposes it with XML/Jackson-friendly accessors, omitting empty values from JSON.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson inclusion, JAXB/XML. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover multiple response groups and empty-map omission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/RemoveDataNodesResponseWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ResponseStatus.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ResponseStatus.java

## Purpose
Shared enum for Recon API response status values: OK, PATH_NOT_FOUND, and TYPE_NOT_APPLICABLE.

## Important APIs, Types, And Functions
declares `ResponseStatus`.

## Control Flow
Used by namespace, DU, quota, file-size, and key-list responses as a compact status discriminator.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert endpoint-specific mapping to these enum values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ResponseStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ScmPendingDeletion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ScmPendingDeletion.java

## Purpose
Aggregate SCM pending deletion metrics: logical block size, replicated block size, and block count.

## Important APIs, Types, And Functions
declares `ScmPendingDeletion`; key fields include `totalBlocksize`, `totalReplicatedBlockSize`, `totalBlocksCount`; important methods include `getTotalBlocksize`, `getTotalReplicatedBlockSize`, `getTotalBlocksCount`.

## Control Flow
Constructor-only DTO with Jackson properties populated by SCM deletion accounting endpoints.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify replicated-vs-logical byte calculations and count consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ScmPendingDeletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/StorageCapacityDistributionResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/StorageCapacityDistributionResponse.java

## Purpose
Composite response for storage utilization distribution, combining global storage, global namespace, used-space breakdown, and per-datanode storage reports.

## Important APIs, Types, And Functions
declares `StorageCapacityDistributionResponse`, `Builder`; key fields include `globalStorage`, `globalNamespace`, `usedSpaceBreakDown`, `dataNodeUsage`, `globalStorage`, `globalNamespace`, `usedSpaceBreakDown`, `dataNodeUsage`; important methods include `getGlobalStorage`, `getGlobalNamespace`, `getUsedSpaceBreakDown`, `getDataNodeUsage`, `newBuilder`, `setGlobalStorage`, `setGlobalNamespace`, `setDataNodeUsage`, `setUsedSpaceBreakDown`, `build`.

## Control Flow
Builder defaults all components to null and simply copies supplied aggregate/list objects into the response.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover complete and partial aggregate responses plus datanode list ordering from the producer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/StorageCapacityDistributionResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainerMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainerMetadata.java

## Purpose
DTO for unhealthy container rows, converting database records into API output with state, unhealthy-since time, expected/actual/delta replica counts, reason, key count, pipeline UUID, and replica history.

## Important APIs, Types, And Functions
declares `UnhealthyContainerMetadata`; key fields include `containerID`, `containerState`, `unhealthySince`, `expectedReplicaCount`, `actualReplicaCount`, `replicaDeltaCount`, `reason`, `keys`, `pipelineID`, `replicas`; important methods include `getContainerID`, `getKeys`, `getReplicas`, `getContainerState`, `getExpectedReplicaCount`, `getActualReplicaCount`, `getReplicaDeltaCount`, `getReason`, `getUnhealthySince`, `getPipelineID`.

## Control Flow
The record constructor copies fields from generated `UnhealthyContainers` POJOs and attaches replica history supplied by callers.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover each unhealthy state, replica delta values, reason propagation, and replica history serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainerMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersResponse.java

## Purpose
Paged response and summary counters for unhealthy containers across missing, under-replicated, over-replicated, mis-replicated, and replica-mismatch states.

## Important APIs, Types, And Functions
declares `UnhealthyContainersResponse`; key fields include `missingCount`, `underReplicatedCount`, `overReplicatedCount`, `misReplicatedCount`, `replicaMismatchCount`, `firstKey`, `lastKey`, `containers`; important methods include `setSummaryCount`, `getMissingCount`, `getUnderReplicatedCount`, `getOverReplicatedCount`, `getMisReplicatedCount`, `getReplicaMismatchCount`, `getLastKey`, `getFirstKey`, `getContainers`, `setFirstKey`, `setLastKey`.

## Control Flow
`setSummaryCount` maps generated schema state enums to the matching counter; first/last keys support pagination.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover every enum branch in `setSummaryCount`, cursor fields, and row collection output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersSummary.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersSummary.java

## Purpose
Small summary row pairing an unhealthy container state string with its count.

## Important APIs, Types, And Functions
declares `UnhealthyContainersSummary`; key fields include `count`, `containerState`; important methods include `getContainerState`, `getCount`.

## Control Flow
Constructor-only immutable holder.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify state labels and counts from summary queries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UsedSpaceBreakDown.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UsedSpaceBreakDown.java

## Purpose
Used-space breakdown for utilization APIs, separating open-key bytes from finalized key bytes.

## Important APIs, Types, And Functions
declares `UsedSpaceBreakDown`; key fields include `openKeyBytes`, `finalizedKeyBytes`; important methods include `getOpenKeyBytes`, `getFinalizedKeyBytes`.

## Control Flow
Constructor-only composition of `OpenKeyBytesInfo` and finalized-byte total.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify aggregate sums and open/finalized split from OM tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UsedSpaceBreakDown.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumeObjectDBInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumeObjectDBInfo.java

## Purpose
Volume metadata DTO extending `ObjectDBInfo` with admin, owner, and volume name fields.

## Important APIs, Types, And Functions
declares `VolumeObjectDBInfo`; key fields include `admin`, `owner`, `volume`; important methods include `getAdmin`, `setAdmin`, `getOwner`, `setOwner`, `getVolume`, `setVolume`.

## Control Flow
The `OmVolumeArgs` constructor copies base object fields plus volume-specific admin/owner/name.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover constructor mapping, ACL/base metadata inheritance, and JSON names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumeObjectDBInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumesResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumesResponse.java

## Purpose
Response envelope for volume list APIs with total count and volume metadata rows.

## Important APIs, Types, And Functions
declares `VolumesResponse`; key fields include `totalCount`, `volumes`; important methods include `getTotalCount`, `getVolumes`.

## Control Flow
Default constructor returns zero count and empty list; alternate constructor accepts endpoint values.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert empty output and count/list consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumesResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/package-info.java

## Purpose
Package-level marker for Recon API type classes under `org.apache.hadoop.ozone.recon.api.types`.

## Important APIs, Types, And Functions
The file only contributes package-level metadata.

## Control Flow
Contains only the package declaration and license header; behavior lives in sibling DTO, enum, and helper classes.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests are not needed for this file directly; package coverage comes from endpoint serialization and DTO tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotConfigKeys.java

## Purpose
Central configuration key registry for the Recon chatbot feature, including enablement, provider/model defaults, API keys/base URLs, execution limits, thread pool/queue sizes, provider model lists, and Anthropic beta header.

## Important APIs, Types, And Functions
declares `ChatbotConfigKeys`; key fields include `OZONE_RECON_CHATBOT_PREFIX`, `OZONE_RECON_CHATBOT_ENABLED`, `OZONE_RECON_CHATBOT_ENABLED_DEFAULT`, `OZONE_RECON_CHATBOT_PROVIDER`, `OZONE_RECON_CHATBOT_PROVIDER_DEFAULT`, `OZONE_RECON_CHATBOT_DEFAULT_MODEL`, `OZONE_RECON_CHATBOT_DEFAULT_MODEL_DEFAULT`, `OZONE_RECON_CHATBOT_TIMEOUT_MS`, `OZONE_RECON_CHATBOT_TIMEOUT_MS_DEFAULT`, `OZONE_RECON_CHATBOT_OPENAI_API_KEY`; important methods include `isChatbotEnabled`.

## Control Flow
`isChatbotEnabled` reads `ozone.recon.chatbot.enabled` from `OzoneConfiguration`; all other members are constants consumed by the chatbot module, endpoint, LLM client, agent, executor, and credential helper.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Ozone configuration, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover default disabled behavior, explicit enablement, config key spelling, and default limits used by dependent classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotException.java

## Purpose
Typed checked exception used to wrap chatbot processing, LLM, and tool execution failures for the endpoint layer.

## Important APIs, Types, And Functions
declares `ChatbotException`.

## Control Flow
Provides message-only and message-plus-cause constructors; no additional state.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify endpoint exception translation preserves messages and causes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotModule.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotModule.java

## Purpose
Guice module binding all chatbot components into Recon dependency injection.

## Important APIs, Types, And Functions
declares `ChatbotModule`; important methods include `configure`.

## Control Flow
`configure` binds `ChatbotEndpoint`, `ChatbotAgent`, `LLMClient`, `LangChain4jDispatcher`, `ToolExecutor`, and `CredentialHelper` as singletons.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with LLM client, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify injector creation and that chatbot components resolve only when the feature is enabled in higher-level wiring.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotModule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotAgent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotAgent.java

## Purpose
Main Recon chatbot orchestrator. It turns a user question into one or more safe internal Recon API calls and asks the configured LLM to summarize the returned data.

## Important APIs, Types, And Functions
declares `ChatbotAgent`, `ToolCall`; key fields include `LIST_KEYS_ENDPOINT_SUFFIX`, `API_V1_ROOT`, `ALLOWED_ENDPOINT_PREFIXES`, `llmClient`, `toolExecutor`, `apiSchema`, `toolSelectionPreamble`, `summarizationPrompt`, `fallbackPromptTemplate`, `maxToolCalls`; important methods include `processQuery`, `getToolCall`, `executeMultipleToolCalls`, `summarizeResponse`, `handleFallback`, `buildToolSelectionPrompt`, `buildSummarizationPrompt`, `buildSummarizationUserPrompt`, `buildClarificationForToolCalls`, `validateToolCallForExecution`, `buildResponseKey`, `createExecutionMetadataMap`.

## Control Flow
`processQuery` validates the query, selects an LLM model, asks the LLM for a typed tool-call JSON envelope, handles documentation/fallback paths, enforces endpoint allowlist and safe listKeys scoping, executes calls through `ToolExecutor`, attaches pagination/limit metadata, and performs a second LLM summarization call.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Ozone configuration, LLM client, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are prompt/schema drift, LLM malformed output, endpoint allowlist gaps, unbounded listKeys scans if safe scope is relaxed, summarization token growth, partial multi-call failures, and leaking internal error detail to users.

## Test Signals
Tests should mock `LLMClient` and `ToolExecutor` for single, multi, documentation, fallback, malformed JSON, disallowed endpoint, listKeys safe-scope, executor failure, and max-tool-call truncation paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotAgent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotUtils.java

## Purpose
Utility class for chatbot endpoint normalization, path canonicalization, allowlist prefix matching, listKeys scope checks, robust JSON extraction from LLM prose, integer parsing, JSON parsing, classpath resource loading, and HTTP response stream reading.

## Important APIs, Types, And Functions
declares `ChatbotUtils`; key fields include `API_V1_ROOT`; important methods include `normalizeEndpoint`, `canonicalizeEndpointPath`, `matchesAllowedPrefix`, `isBucketScopedListKeysPrefix`, `extractFirstJsonObject`, `parsePositiveInt`, `extractStringField`, `estimateRecordCount`, `parseJsonSafely`, `loadResourceFromClasspath`, `readInputStream`, `readErrorStream`.

## Control Flow
Security helpers reject blank, scheme-bearing, and path-traversal endpoints outside `/api/v1`; JSON extraction uses brace counting with string/escape awareness rather than a regex.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Recon chatbot tool execution, HTTP client I/O. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are path canonicalization bypasses, prefix boundary mistakes, malformed LLM JSON, silently empty classpath resources, and stream reads that concatenate lines without delimiters.

## Test Signals
Tests should cover path traversal, query-string stripping, prefix boundaries, bucket-scoped start prefixes, nested JSON extraction, malformed JSON, classpath misses, and error stream reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotUtils.java -->
