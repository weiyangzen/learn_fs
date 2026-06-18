# Research: subset-b-007993

Grouped research for Apache Ozone datanode container common helpers, implementation, interfaces, and report publishers. Each section is source-tree aligned for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java

Purpose: static utility surface for container-layer error conversion, datanode ID persistence and recovery, container metadata file checksums, file/path derivation, pending-delete counters, tar archive naming, and volume free-space enforcement.

Important APIs and control flow: `logAndReturnError` maps `StorageContainerException` to `ContainerCommandResponseProto` and logs closed/open-state failures at debug while warning on others. Datanode identity flows through `writeDatanodeDetailsTo`, `readDatanodeDetailsFrom`, YAML parsing via `DatanodeIdYaml`, fallback recovery from volume `VERSION` files, and final protobuf compatibility fallback. `verifyContainerFileChecksum` recomputes YAML checksums with the right container YAML representer, including EC replica-index handling. `getChunkDir`, `getContainerFile`, `retrieveContainerIdFromTarName`, `getPendingDeletionBlocks`, and `getPendingDeletionBytes` are shared by container IO, archiving, and block deletion. `assertSpaceAvailability` enforces hard minimum free space and records soft/hard metrics.

State and persistence: writes and rewrites the datanode ID file, reads `VERSION` properties, and mutates `ContainerData` checksum fields during verification. Disk behavior is sensitive to file deletion/recreation and directory creation failures.

Dependencies and integration: integrates with `DatanodeDetails`, `HddsServerUtil`, `HddsVolume`, `StorageVolumeUtil`, `ContainerDataYaml`, `KeyValueContainerData`, `ContainerSet`, `VolumeInfoMetrics`, and protobuf response builders.

Risks and test signals: recovery creates a minimal `DatanodeDetails` from UUID only, so tests should cover hostname/IP absence after corrupt ID files. `getContainerIDFromFile` parses a path returned by `getContainerNameFromFile`, which includes parent path and can fail if callers pass unexpected file layout. Checksum tests should cover disabled verification, stale checksum, EC replica index inclusion, and missing chunk directories. Space tests should assert hard rejection, metric increments, and soft-band metric behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java

Purpose: YAML serializer/deserializer for `datanode.id`, converting between `DatanodeDetails` and a SnakeYAML-compatible bean while respecting HDDS layout-version gated ports.

Important APIs and control flow: `createDatanodeIdFile` builds a flow-style YAML writer, converts details through `getDatanodeDetailsYaml`, and delegates atomic-style dumping to `YamlUtils.dump`. `readDatanodeIdFile` loads `DatanodeDetailsYaml`, validates that UUID is present, rebuilds `DatanodeDetails` with UUID, host, IP, certificate serial, persisted operational state, state expiry, ports, and initial/current versions. The nested `DatanodeDetailsYaml` bean exposes getters and setters needed by SnakeYAML field introspection.

State and persistence: persisted fields are UUID, network identity, certificate serial, persisted op state and expiry, port map, and layout versions. `getDatanodeDetailsYaml` instantiates `DatanodeLayoutStorage` to filter out ports whose `DatanodeDetails.Port.Name` enum field has `BelongsToHDDSLayoutVersion` newer than the local layout.

Dependencies and integration: used by `ContainerUtils` for datanode ID read/write. It depends on `DatanodeLayoutStorage`, `HDDSLayoutFeature`, reflection on `DatanodeDetails.Port.Name`, `YamlUtils`, and protobuf `NodeOperationalState`.

Risks and test signals: malformed YAML, empty files, absent UUID, invalid UUID strings, invalid persisted op-state names, and unsupported port enum names should be covered. Reflection failures log and continue, which can silently omit layout filtering for unknown enum fields. Layout-gated ports need upgrade tests to ensure old layout versions do not persist ports that old software cannot read.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java

Purpose: small value object and IO helper for datanode volume `VERSION` files.

Important APIs and control flow: the constructor captures storage ID, cluster ID, datanode UUID, creation time, and layout version. `createProperties` maps those values to `OzoneConsts` property keys. `createVersionFile` writes the properties to the supplied file through `IOUtils.writePropertiesToFile`; `readFrom` reads an existing file into `Properties` via `IOUtils.readPropertiesFromFile`.

State and persistence: this class owns the on-disk property format for datanode volume identity. It does not validate values beyond storing them as strings, so callers are responsible for semantic checks such as UUID shape, cluster matching, and layout compatibility.

Dependencies and integration: `ContainerUtils.recoverDatanodeDetailsFromVersionFile` reads this format when the datanode ID file is corrupt or unavailable. Volume initialization and upgrade code can use it to persist storage identity.

Risks and test signals: tests should verify exact property names, round-trip read/write, missing keys, invalid numeric layout/ctime strings handled by consumers, and IO failures. Since `readFrom` returns raw `Properties`, downstream code must not assume all required fields are present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java

Purpose: reporting helper that summarizes a batch of `DeletedBlocksTransaction` entries for logging and metrics around block deletion.

Important APIs and control flow: `getFrom` wraps a list in a private constructor. Construction iterates every transaction, records transaction ID to retry count, counts transactions whose retry count is positive, aggregates local block counts by container ID, and records total block count. Public accessors expose transaction count, block count, retry transaction count, container count, comma-separated transaction IDs, and a compact `txId(count)` summary. `toString` expands each transaction with tx ID, processed count, container ID, and local IDs.

State and persistence: all state is in-memory and derived from the provided transaction list. There is no defensive copy of `blocks`, so later mutations to the list or protobuf objects can affect `toString` semantics.

Dependencies and integration: used by deletion paths to make SCM delete transaction batches human-readable. Depends on Guava `Maps`, protobuf `DeletedBlocksTransaction`, streams, and Hadoop `StringUtils`.

Risks and test signals: transaction ID ordering is based on hash-map key iteration and should not be treated as stable. Tests should cover duplicate container IDs, retry counts, empty batches, duplicated transaction IDs, and string rendering of local ID lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java

Purpose: datanode-side wrapper for generating block and container tokens when security and token features are enabled.

Important APIs and control flow: the constructor checks block-token and container-token flags from `SecurityConfig`, treats a non-null `SecretKeySignerClient` as security availability, obtains the current short user name, and creates `OzoneBlockTokenSecretManager` and/or `ContainerTokenSecretManager` with the configured expiry. `getBlockToken` grants READ, WRITE, and DELETE modes for a `BlockID` and length when the manager exists. `getContainerToken` creates a container token when enabled. `encode` converts non-null Hadoop tokens to URL strings.

State and persistence: no disk persistence. Runtime state consists of optional token secret managers and the short user name. When security or token modes are disabled, methods return null tokens.

Dependencies and integration: integrates with SCM/datanode security classes, `SecretKeySignerClient`, Hadoop `UserGroupInformation`, `BlockID`, and `ContainerID`. Callers must tolerate null token outputs.

Risks and test signals: tests should cover all combinations of security client present/absent and block/container token flags. Token expiry should follow block token expiry config for both token types. Null returns are intentional but risky for callers that blindly encode or attach tokens.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java

Purpose: package documentation for container common helper classes.

Important APIs and control flow: no executable code. It declares `org.apache.hadoop.ozone.container.common.helpers` and describes it as containing protocol buffer helper classes and utilities used by implementation code.

State and persistence: none.

Dependencies and integration: the package contains utility classes such as `ContainerUtils`, datanode identity helpers, token helpers, and deletion summaries that support the container implementation layer.

Risks and test signals: no unit tests are needed for this file. Documentation spelling and package declaration consistency are the only relevant maintenance checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java

Purpose: background datanode service that selects closed or quasi-closed containers with pending deleted blocks and schedules `BlockDeletingTask` workers.

Important APIs and control flow: constructors configure `BackgroundService`, choose a `ContainerDeletionChoosingPolicy` from config, register dynamic reconfiguration callbacks, and create metrics. `getTasks` calls `chooseContainerForBlockDeletion`, builds one task per selected container, and records chosen block/container counts. `chooseContainerForBlockDeletion` streams over the `OzoneContainer` `ContainerSet`, filters containers with pending deletion, checks deletion eligibility, totals pending block counts and bytes, and delegates final selection to the policy. `isDeletionAllowed` rejects unsupported container types, non-closed states, invalid origin pipeline IDs, and Ratis containers whose close index is not replicated across all peers.

State and persistence: service state is scheduled executor configuration, metrics, and references to container set and checksum tree manager. It does not directly persist deletes; tasks do. Reconfiguration shuts down and restarts the service with new interval, timeout, and worker count.

Dependencies and integration: integrates with `OzoneContainer`, `XceiverServerRatis`, `PipelineID`, `DatanodeConfiguration`, deletion policies, `ContainerUtils`, `BlockDeletingTask`, and `ContainerChecksumTreeManager`.

Risks and test signals: tests should cover Ratis gating by min replicated index, invalid or absent pipeline IDs, EC containers with empty origin pipeline IDs, reconfiguration restart without deadlock, and metrics for pending bytes/counts. The policy only supports `KeyValueContainer`; new container types require both utility and task builder extensions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java

Purpose: abstract in-memory representation of container metadata that is persisted in `.container` files and reported to SCM.

Important APIs and control flow: constructors initialize type, ID, layout version, metadata, OPEN state, max size, origin pipeline/node, zero checksum, and unset data checksum. Abstract hooks provide container paths, metadata paths, protobuf export, and BCSID. State methods are synchronized and include open/closing/closed/quasi/unhealthy checks plus transitions. Space accounting uses `commitSpace`, `releaseCommitSpace`, `incrWriteBytes`, and `updateWriteStats` to track committed volume bytes and used space. Checksum handling zeroes the checksum field, dumps YAML, and hashes the resulting metadata. Scan timestamp setters bridge serialized epoch milliseconds and transient `Optional<Instant>`.

State and persistence: persistent YAML fields include type, ID, layout version, state, metadata, max size, checksum, scan timestamp, origin pipeline, and origin node. Runtime-only state includes volume reference, statistics, committed-space flag, immediate close action flag, empty marker, replica index, and transient scan time.

Dependencies and integration: used by all container implementations, `ContainerDataYaml`, reports, scanners, deletion policies, dispatcher close logic, and volume accounting. Depends on `HddsVolume`, protobuf container messages, SnakeYAML, and `ContainerUtils`.

Risks and test signals: committed-space arithmetic must be tested around writes, overwrites that grow files, close transitions, and null volumes in tests. `getDataChecksum` returns 0 when unset, so callers must use `needsDataChecksum` if they need to distinguish absent checksum from real zero. YAML checksum stability depends on field order and representer behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java

Purpose: comparator for ordering containers for data scans.

Important APIs and control flow: `INSTANCE` exposes a reusable comparator. `compare` reads each container's `ContainerData.lastDataScanTime`, sorts unscanned containers before scanned containers, sorts scanned containers by oldest timestamp first, and breaks all ties by container ID.

State and persistence: no state beyond the singleton comparator. It consumes timestamps persisted through `ContainerData` but does not mutate them.

Dependencies and integration: used by `ContainerSet.getContainerIterator(HddsVolume)` to produce per-volume scan order. Depends on the `Container` interface and `ContainerData` scan timestamp API.

Risks and test signals: tests should cover both Optional-empty timestamps, one empty and one present, equal timestamps with ID tie-breaks, and stable behavior when containers are on the same volume. Since it reads mutable container data, concurrent timestamp updates can change ordering between list construction and scan execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java

Purpose: YAML codec for `.container` metadata files, currently supporting key-value containers.

Important APIs and control flow: `createContainerFile` obtains the right YAML instance, computes and writes the metadata checksum, and dumps through `YamlUtils`. `readContainerFile`, `readContainer(byte[])`, and `readContainer(InputStream)` load YAML using field access and convert SnakeYAML failures or empty files to `IOException`. `getYamlForContainerType` builds a representer filtered to `KeyValueContainerData` YAML fields and optionally includes `replicaIndex`. The custom constructor maps the key-value YAML tag into `KeyValueContainerData`, manually restores DB type, metadata path, chunks path, metadata map, checksum, scan timestamp, state, schema version, and replica index. A custom integer constructor returns all YAML integers as `Long` to avoid type variance.

State and persistence: this file defines which `ContainerData` fields are persisted and how new fields must be explicitly restored. Null properties are omitted during dumping.

Dependencies and integration: used by container creation/update, `ContainerUtils` checksum verification, import/export packing, and persistence recovery. Depends on SnakeYAML internals, `KeyValueContainerData`, `OzoneConsts`, and protobuf container state.

Risks and test signals: any added YAML field requires updates to both the representer field list and constructor mapping. Tests should cover empty files, malformed YAML, missing required keys, replica index presence/absence, scan timestamp restoration, integer widths, and checksum round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java

Purpose: enum describing chunk-file layout versions for containers.

Important APIs and control flow: `FILE_PER_CHUNK` maps a chunk to a file named by chunk name and is deprecated. `FILE_PER_BLOCK` maps all chunks of a block to a single `<localID>.block` file and is the default. `getContainerLayoutVersion` looks up by numeric version, `getAllVersions` exposes all enum values, and `getConfiguredVersion` reads the configured enum while falling back to default on invalid config. Instance `getChunkFile` resolves file paths either from a provided chunk directory or from `ContainerData` via `ContainerUtils.getChunkDir`.

State and persistence: layout version number and description are persisted in container metadata and determine on-disk chunk layout. The enum itself is immutable.

Dependencies and integration: used by `ContainerData`, `ContainerDataYaml`, key-value container IO, and block/chunk handlers. Depends on `BlockID`, configuration source, SCM config keys, and container utility path validation.

Risks and test signals: tests should cover both layout path derivations, invalid config fallback, unknown persisted layout returning null, and behavior when the chunk directory is missing. New layouts require backward-compatible YAML and chunk lookup handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java

Purpose: concurrent registry of datanode containers, missing-container IDs, recovering containers, metadata-store create info, and on-demand scan routing.

Important APIs and control flow: factory methods build read-only or read-write sets. `addContainer` rejects IDs marked missing unless overwrite is requested, inserts into a `ConcurrentSkipListMap`, persists create info, removes missing state, tracks recovering timeout entries, and registers the container with its volume. `updateContainer` swaps map entries and adjusts volume membership. Removal variants remove fully, memory-only, or mark missing before removal to prevent accidental recreation. `getContainerWithWriteLock` retries when DiskBalancer or other code swaps the container instance during lock acquisition. `getContainerReport` snapshots containers and synchronizes report construction to linearize FCR/ICR. `handleVolumeFailures` marks affected containers missing, logs loss, refreshes a full report, and triggers heartbeat. `buildMissingContainerSetAndValidate` compares Ratis snapshot BCSIDs with loaded containers and marks stale containers unhealthy.

State and persistence: in-memory concurrent maps/sets store live, missing, and recovering IDs. Optional `WitnessedContainerMetadataStore` persists `ContainerCreateInfo` rows and deletes them on full removal. Volume membership is updated on add/update/remove.

Dependencies and integration: central to dispatcher, block deletion, scanners, reports, volume failure handling, and metadata stores.

Risks and test signals: concurrency tests should exercise map swaps while locks are acquired, missing-container recreation prevention, failed-volume iteration while map mutates, report linearization, and BCSID validation. Metadata-store failures surface as `StorageContainerException` and should be tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java

Purpose: datanode container command dispatcher bridging transport/Ratis requests to container-type handlers while enforcing tokens, state rules, space checks, metrics, audit, close actions, and scan triggers.

Important APIs and control flow: `dispatch` wraps `dispatchRequest` in `OzoneProtocolMessageDispatcher`. The request path records metrics by command/stage, validates tokens when requested by `DispatcherContext`, handles Ratis snapshot BCSID bookkeeping, rejects writes to missing containers, implicitly creates key-value containers for write/put paths when absent, rejects missing non-create operations, checks volume space and queues close actions, obtains the handler, invokes `handler.handle`, records latency, marks containers unhealthy on non-ignorable write failures, triggers scans, updates Ratis BCSID maps after `PutBlock`/`PutSmallFile`, and emits audit events. `validateContainerCommand` is the leader-side preflight for Ratis log creation. Streaming methods route direct data-channel and read-only stream operations to handlers.

State and persistence: dispatcher owns handler map, cluster ID propagation, protocol metrics, slow-operation threshold, token verifier, and references to `ContainerSet` and `StateContext`. It indirectly persists container creation, unhealthy state, and BCSID updates through handlers and container data.

Dependencies and integration: integrates with all container command protobufs, `Handler`, `ContainerSet`, `StateContext`, Ratis `DispatcherContext`, audit infrastructure, OpenTelemetry spans, token verifier, metrics, and volume set.

Risks and test signals: tests should cover implicit creation conditions, EC replica index propagation, missing-container rejection, token failure mapping, close action deduplication, volume-full write rejection, unhealthy marking only for non-ignorable failures, BCSID map updates, audit parameters, and slow-operation units. `streamDataReadOnly` mixes millisecond timing with nanosecond threshold naming, so performance audit expectations need care.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java

Purpose: deletion policy that randomizes the order of candidate containers before the shared selection template allocates a delete-block budget.

Important APIs and control flow: extends `ContainerDeletionChoosingPolicyTemplate` and implements `orderByDescendingPriority` by calling `Collections.shuffle(candidateContainers)`. The inherited template filters positive pending-delete counts, caps each selected container by remaining block budget, and returns `ContainerBlockInfo` entries.

State and persistence: no persistent state. Random ordering is process-local and non-deterministic.

Dependencies and integration: selectable via the `BlockDeletingService` policy configuration. Depends on the template contract and `ContainerData` pending-delete counters through inherited logic.

Risks and test signals: because default shuffle randomness is not injectable, deterministic unit tests should focus on budget accounting through the template or use statistical/containment assertions. Operationally, random selection can reduce hot spots but may delay large pending-delete backlogs compared with top-N ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java

Purpose: immutable datanode storage/volume usage report with protobuf and JMX representations.

Important APIs and control flow: builder captures ID, failed flag, capacity, SCM-used, remaining, committed, free-space-to-spare, storage type, path, reserved bytes, filesystem capacity, and filesystem available bytes. Getters implement `StorageLocationReportMXBean` and expose additional fields. `getUsableSpace` delegates to `VolumeUsage`. `getProtoBufMessage` serializes full storage reports, while `getMetadataProtoBufMessage` serializes the metadata subset. `getFromProtobuf` rebuilds a report from optional protobuf fields. Static conversion methods map between Hadoop `StorageType` and HDDS protobuf storage type.

State and persistence: immutable after construction. It represents sampled volume state, not long-lived persisted state. Protobuf serialization is used in heartbeat reports.

Dependencies and integration: used by volume reports, node reports, JMX, and SCM heartbeat paths. Depends on Hadoop storage type, protobuf report messages, `VolumeUsage`, and MXBean interface.

Risks and test signals: tests should cover every storage type mapping in both directions, illegal enum values, optional protobuf fields missing, failed-volume string rendering, and `getUsableSpace` with committed/reserved/free-space-to-spare values. Builder does not enforce required fields, so null storage type or location can fail later during serialization or `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java

Purpose: default deletion policy that prioritizes containers with the most pending deletion blocks.

Important APIs and control flow: extends `ContainerDeletionChoosingPolicyTemplate`. Its comparator sorts `ContainerData` descending by `ContainerUtils.getPendingDeletionBlocks`, then inherited selection consumes the configured block budget across the ordered list.

State and persistence: stateless. The effective order depends on live pending-deletion counters from container metadata/statistics.

Dependencies and integration: used by `BlockDeletingService` as the default policy when no custom policy is configured. Depends on `ContainerUtils` and the template's budget selection.

Risks and test signals: tests should verify descending priority, partial selection of the last container when its pending count exceeds remaining budget, empty candidate behavior, and unsupported container-type filtering in upstream service. Containers with equal pending counts retain sort-dependent relative order and should not be assumed deterministic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/package-info.java

Purpose: package documentation for Ozone container common implementation classes.

Important APIs and control flow: no executable code. It declares `org.apache.hadoop.ozone.container.common.impl` and documents that the package contains Ozone container implementation.

State and persistence: none.

Dependencies and integration: covers implementation classes such as `ContainerSet`, `ContainerData`, `HddsDispatcher`, layout definitions, deletion policies, and storage reports.

Risks and test signals: no runtime tests. Documentation should stay aligned with package contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java

Purpose: closeable abstraction for iterating blocks inside a container type.

Important APIs and control flow: implementers expose `hasNext`, positioning methods `seekToFirst` and `seekToLast`, and `nextBlock`, which returns the next block or throws `NoSuchElementException`/`IOException` when appropriate. Extending `Closeable` makes resource cleanup part of the contract.

State and persistence: interface only. Implementations usually wrap metadata DB iterators and therefore carry cursor state and open resources.

Dependencies and integration: used by container implementations and block listing/scanning/deletion logic that should not depend on a concrete metadata store.

Risks and test signals: implementation tests should cover cursor movement, empty stores, resource closure, IO exceptions, and whether `nextBlock` returns null or throws at end according to the implementation's documented behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java

Purpose: primary container abstraction for lifecycle, metadata, reports, import/export, scanning, locking, and data movement.

Important APIs and control flow: lifecycle methods create, delete, update, mark for close/delete/unhealthy, quasi-close, close, and update delete transaction/BCSID. Data APIs import/export through `ContainerPacker`, copy directories, expose the `.container` file, and report protobuf replica state. Scan APIs separate metadata scan, data scan eligibility, and throttled/cancelable data scan. Lock APIs expose explicit read/write lock acquisition, interruptible variants, unlock, and ownership checks.

State and persistence: interface only, but implementations are expected to persist metadata updates and lifecycle state to container files and metadata stores. Locking contract is central to safe concurrent writes, scans, and state transitions.

Dependencies and integration: implemented by key-value containers and consumed by `ContainerSet`, `Handler`, `HddsDispatcher`, scanners, import/export tools, and report publishers.

Risks and test signals: implementation tests should cover persistence after every lifecycle transition, force update behavior, lock ownership and interruptibility, scan behavior by state, import/export round trips, and BCSID/delete transaction updates. Callers must know whether methods require caller-held locks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java

Purpose: pluggable policy interface for selecting containers to process during background block deletion.

Important APIs and control flow: `chooseContainerForBlockDeletion` receives a block budget and map of candidate `ContainerData`, and returns `ContainerBlockInfo` values with selected containers and per-container delete counts. `isValidContainerType` defaults to accepting only `KeyValueContainer`.

State and persistence: interface only. Implementations should be stateless or thread-safe because `BlockDeletingService` may run periodically with shared service state.

Dependencies and integration: configured and invoked by `BlockDeletingService`, with default implementations in `TopNOrderedContainerDeletionChoosingPolicy` and `RandomContainerDeletionChoosingPolicy`.

Risks and test signals: custom policies must preserve the meaning of the block budget and avoid returning unsupported container types or zero-delete containers. Tests should cover type filtering, budget exhaustion, empty candidates, and deterministic ordering where required.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java

Purpose: template implementation that handles common delete-budget selection while subclasses provide candidate ordering.

Important APIs and control flow: final `chooseContainerForBlockDeletion` null-checks the candidate map, copies values into an ordered list, calls subclass `orderByDescendingPriority`, and iterates until the block budget reaches zero. Each selected container gets `min(remainingBudget, pendingDeletionBlocks)` blocks and is wrapped in `ContainerBlockInfo`. It logs selected containers at debug and aggregate selection at info.

State and persistence: no persistent state. It uses live pending-delete counters from `ContainerData`.

Dependencies and integration: base class for random and top-N policies used by `BlockDeletingService`. Depends on `ContainerUtils.getPendingDeletionBlocks`.

Risks and test signals: if `blockCount` starts at zero or negative, no containers should be selected but the current code still copies/orders candidates; tests should document behavior. Logging message reports original chosen blocks and remaining block count, not original budget in the denominator, which may confuse operators. Subclasses must order in descending priority as expected by the template.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java

Purpose: bridge contract from transport/Ratis layers to concrete container handlers.

Important APIs and control flow: implementations dispatch protobuf commands with optional `DispatcherContext`, validate commands before Ratis execution, initialize and shut down metrics/services, build missing-container state from snapshot BCSIDs, look up handlers by container type, and propagate cluster ID. Default streaming methods throw unsupported operation exceptions unless overridden.

State and persistence: interface only. Implementations such as `HddsDispatcher` maintain handler maps, metrics, container set references, and state-context interactions.

Dependencies and integration: consumed by Xceiver/Ratis server paths and implemented by `HddsDispatcher`.

Risks and test signals: dispatcher implementations need tests for validation versus execution differences, handler lookup failures, lifecycle idempotency, streaming unsupported paths, and correct use of `DispatcherContext` during Ratis apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java

Purpose: optional startup/debug tool interface for inspecting or repairing containers.

Important APIs and control flow: `load` activates inspector behavior from configuration, `unload` disables it, `isReadOnly` declares whether `process` mutates containers, and `process` handles one container plus its `DatanodeStore`. The contract explicitly permits parallel processing across containers and requires implementations to batch log output and be thread-safe across calls.

State and persistence: interface only. Implementations may persist repairs to container metadata stores or only log diagnostics depending on read-only status.

Dependencies and integration: used during datanode startup/container loading workflows. Operates on `ContainerData` and `DatanodeStore`.

Risks and test signals: mutating inspectors are high-risk and need tests for idempotency, parallel execution, per-container serialization, and recovery from store errors. Read-only inspectors should prove they do not change metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java

Purpose: abstraction for choosing physical paths for container placement and reporting storage locations.

Important APIs and control flow: `getContainerPath` returns a base path for a new container and metadata, `getDataPath` returns a data path for a specific container name, `getLocationReport` returns storage usage reports, and `shutdown` performs clean resource release.

State and persistence: interface only. Implementations likely hold volume lists, selection policy state, and sampled usage data.

Dependencies and integration: used by container creation and node reporting. Report type is `StorageLocationReport`.

Risks and test signals: tests should cover no available volumes, failed volumes, path creation errors, deterministic data path derivation, report freshness, and clean shutdown under exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java

Purpose: JMX-facing subset of container location manager reporting.

Important APIs and control flow: exposes `getLocationReport`, returning `StorageLocationReportMXBean[]` and allowing `IOException`.

State and persistence: interface only. It reflects current volume status and does not persist data.

Dependencies and integration: implemented by location/volume managers that publish storage reports through JMX.

Risks and test signals: JMX tests should cover report serialization, failed volume visibility, exception propagation, and compatibility of MXBean-friendly return types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java

Purpose: archive pack/unpack contract for moving complete container contents and descriptors through a single stream.

Important APIs and control flow: `unpackContainerData` extracts archive data to temporary and destination directories while returning the descriptor bytes instead of writing the descriptor. `pack` writes chunk data, metadata DB, and descriptor to a destination stream. `unpackContainerDescriptor` reads just the descriptor from an archive. Default `persistCustomContainerState` reads descriptor bytes through `ContainerDataYaml`, sets the target container state, and updates metadata at a custom metadata path.

State and persistence: implementations persist archive extraction outputs and descriptor state. The default method mutates container state and delegates persistence through `container.update`.

Dependencies and integration: used by `Container` import/export methods and handlers. Depends on `ContainerDataYaml` and protobuf container states.

Risks and test signals: archive tests should cover descriptor-only reads, partial extraction cleanup, custom state persistence, null descriptor handling, metadata preservation, and mismatches between descriptor metadata and target container paths. The default method reads original metadata but applies state to the target container data before update, so implementations must define update semantics clearly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java

Purpose: abstract closeable holder for a container metadata DB store and its path.

Important APIs and control flow: constructor captures `DatanodeStore` and container DB path. Getters expose both. `cleanup` defaults to true and can be overridden by concrete handles. It implements Ratis `UncheckedAutoCloseable`, leaving close behavior to subclasses.

State and persistence: holds references to a metadata store and DB path; does not itself persist or close. Subclasses own actual resource lifetime.

Dependencies and integration: used by container metadata-store cache/handle code that needs a common DB handle type.

Risks and test signals: concrete implementations should be tested for close idempotency, cleanup semantics, and path/store consistency. The base class returning true for cleanup can hide missing cleanup implementations if callers assume it performed work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java

Purpose: abstract per-container-type command handler used by `HddsDispatcher`.

Important APIs and control flow: the static factory currently maps `KeyValueContainer` to `KeyValueHandler`. The base class stores config, datanode ID, `ContainerSet`, `VolumeSet`, metrics, cluster ID, and ICR sender. `sendICR` and `sendDeferredICR` skip RECOVERING containers and otherwise publish immediate or deferred incremental reports. Abstract methods cover command handling, stream channels, import/export, stop, lifecycle transitions, checksum updates, unhealthy/quasi/closed states, delete, reconcile, delete block/unreferenced data, finalized block tracking, copy, import from temp container data, and streaming block reads.

State and persistence: handlers are responsible for mutating and persisting container state, metadata, checksum files, block deletes, and ICR side effects. The base class only holds references and cluster ID.

Dependencies and integration: central integration point between dispatcher and concrete key-value container implementation. Depends on checksum managers, Ratis data channels, tar packer, report sender, volume set, metrics, and operation clients.

Risks and test signals: handler implementations require broad tests for each command type, ICR behavior, RECOVERING skip, checksum update atomicity, delete safety, reconciliation, and stream reads/writes. Adding a new container type requires extending the factory and likely the YAML/layout utilities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java

Purpose: common result contract for container scan outcomes.

Important APIs and control flow: exposes `hasErrors`, `isDeleted`, and `getErrors`, where errors are `ContainerScanError` entries.

State and persistence: interface only. Implementations represent scan outcome state and may be used to drive persistent lifecycle transitions such as marking containers unhealthy or deleted.

Dependencies and integration: consumed by `Handler.markContainerUnhealthy` and implemented by metadata/data scan result classes in `ozoneimpl`.

Risks and test signals: scan result implementations should be tested for deleted-without-errors, errors-with-deleted, immutable error lists, and correct translation into handler state changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java

Purpose: JMX-safe contract exposing storage location usage fields.

Important APIs and control flow: getters expose storage ID, failed status, capacity, SCM-used bytes, remaining bytes, committed bytes, configured free-space-to-spare, storage location, and storage type name.

State and persistence: interface only. Implemented by immutable `StorageLocationReport`.

Dependencies and integration: used by volume/location managers to expose reports through MXBean APIs without leaking protobuf or Hadoop storage type objects.

Risks and test signals: compatibility tests should ensure implementing classes expose stable getter names and MXBean-compatible return types. Fields beyond this interface, such as reserved and filesystem capacity, are not visible through this MXBean contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java

Purpose: policy interface for choosing a datanode volume to store a new container replica.

Important APIs and control flow: `chooseVolume` receives a list of available `HddsVolume` instances and the maximum container size, and returns a selected volume or throws `IOException` when disks are unavailable or full. The interface declares that implementations must be thread-safe.

State and persistence: interface only. Implementations may maintain counters or random state but must guard them for concurrent container creation.

Dependencies and integration: used by `Container.create` implementations and handlers during container placement.

Risks and test signals: tests for implementations should cover empty lists, failed/full volumes, reserved-space constraints, fairness or ordering policy, concurrent calls, and max-size overflow/edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/package-info.java

Purpose: package documentation for container common interfaces.

Important APIs and control flow: no executable code. It declares `org.apache.hadoop.ozone.container.common.interfaces` and states that the package contains common Ozone container interfaces.

State and persistence: none.

Dependencies and integration: frames contracts implemented by key-value containers, dispatchers, location managers, packers, handlers, volume policies, and scan results.

Risks and test signals: no runtime tests. Maintain package declaration and documentation consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/package-info.java

Purpose: high-level package documentation for the common container layer.

Important APIs and control flow: no executable code. Documentation identifies core abstractions as containers, keys, and chunks, and explains that Ozone uses them to build volumes, buckets, and keys.

State and persistence: none.

Dependencies and integration: establishes conceptual context for subpackages `helpers`, `impl`, `interfaces`, and `report`.

Risks and test signals: no runtime tests. Documentation should remain aligned with any future abstraction changes, especially if new container types or non-key-value models are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java

Purpose: scheduled publisher for command status reports sent to SCM in datanode heartbeats.

Important APIs and control flow: `getReportFrequency` lazily reads the command status report interval, verifies it is not lower than SCM heartbeat interval, and caches it. `getReport` iterates the `StateContext` command status map, adds every status to a `CommandStatusReportsProto`, removes non-PENDING entries from the map, and returns null if no statuses are present.

State and persistence: maintains cached interval. Mutates the shared command status map by draining completed or failed statuses after reporting.

Dependencies and integration: extends `ReportPublisher`, uses `StateContext.getCommandStatusMap`, `CommandStatus`, and protobuf `CommandStatusReportsProto`.

Risks and test signals: map iteration plus removal depends on the map supporting concurrent removal; tests should use the real map type. Frequency validation, empty report returning null, pending retention, executed/failure removal, and duplicate report avoidance should be covered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java

Purpose: scheduled full container report publisher for SCM heartbeat state.

Important APIs and control flow: `getReportFrequency` lazily reads and validates the container report interval against heartbeat interval, then adds a random delay up to the interval to avoid synchronized datanode report bursts. `getReport` delegates to `StateContext.getFullContainerReportDiscardPendingICR`, which creates a full report and discards pending incremental container reports.

State and persistence: caches interval only. It refreshes report state in `StateContext` through base publisher behavior.

Dependencies and integration: extends `ReportPublisher`, uses `HddsServerUtil`, Apache Commons `RandomUtils.secure`, and container report protobufs.

Risks and test signals: tests should cover interval validation, random delay bounds, full report generation, and pending ICR discard semantics. Random delay can make scheduler timing tests flaky unless controlled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java

Purpose: generic interface for publishing incremental container reports.

Important APIs and control flow: `send` publishes immediately and may trigger heartbeat. `sendDeferred` defaults to `send`, but implementations can override it to queue the report until the next scheduled heartbeat.

State and persistence: interface only. Implementations likely mutate `StateContext` pending ICR queues.

Dependencies and integration: used by `Handler` to notify SCM of container state changes or defer reports when no state change occurred.

Risks and test signals: implementations should test immediate heartbeat triggering, deferred queue behavior, deduplication, exception handling, and behavior for recovering containers as filtered by `Handler`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java

Purpose: scheduled node report publisher for datanode IO and volume state.

Important APIs and control flow: `getReportFrequency` lazily reads the node report interval and verifies it is at least heartbeat interval. `getReport` navigates from `StateContext` to the parent state machine, container service, and `getNodeReport`.

State and persistence: only cached interval. Reports are pushed to `StateContext` by the base class.

Dependencies and integration: extends `ReportPublisher`, relies on datanode state machine/container report generation and protobuf `NodeReportProto`.

Risks and test signals: tests should cover interval validation, null/failed parent container paths, IO exception propagation to base logger, and correct refresh of full reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java

Purpose: scheduled pipeline report publisher for SCM heartbeat state.

Important APIs and control flow: `getReportFrequency` lazily reads the configured pipeline report interval, ensures it is not below heartbeat interval, and adds a random delay up to the interval to reduce report synchronization. `getReport` delegates to the container service pipeline report.

State and persistence: caches interval. No direct persistence.

Dependencies and integration: extends `ReportPublisher`, uses `StateContext` parent container service, `PipelineReportsProto`, `HddsServerUtil`, and secure random delay.

Risks and test signals: tests should assert interval validation, random delay bounds, and that pipeline reports are refreshed as full reports by the base publisher. Random delay should be isolated in scheduler tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java

Purpose: lifecycle manager for configured report publishers and their shared scheduled executor.

Important APIs and control flow: private construction stores `StateContext`, publisher list, and creates a daemon scheduled thread pool sized to the publisher count with optional thread name prefix. `init` initializes each publisher with the context and executor. `shutdown` shuts down the executor and waits up to five seconds, restoring interrupt status if interrupted. The builder owns a `ReportPublisherFactory`, accumulates publisher instances or report classes, records state context and thread prefix, and validates context during `build`.

State and persistence: owns executor service and publisher list. No disk persistence; it changes report scheduling state.

Dependencies and integration: used by datanode state machine startup to wire node, container, command status, and pipeline publishers.

Risks and test signals: tests should cover zero publishers, executor thread naming, shutdown interrupt handling, missing state context validation, factory publisher addition, direct publisher addition, and repeated init/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java

Purpose: abstract scheduled report publisher base class.

Important APIs and control flow: `init` stores context/executor and schedules `run` at a fixed rate using `getReportFrequency` for both initial delay and period. `run` skips publishing when executor is shut down or datanode state is SHUTDOWN. `publishReport` calls subclass `getReport`; command status reports are added as incremental reports, while all other reports refresh full report state. IO exceptions are logged. Subclasses provide frequency and report generation.

State and persistence: holds config, context, and executor references. It mutates `StateContext` report queues/full report slots.

Dependencies and integration: base for node, container, command status, and pipeline publishers. Depends on protobuf `Message`, `StateContext`, and datanode state enum.

Risks and test signals: `getReport` may return null; tests should verify `StateContext` handling or whether null reports should be skipped by future changes. Frequency is evaluated twice during init, which can produce different random delays for publishers that add jitter. Shutdown-state skipping and IO logging should be tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java

Purpose: maps protobuf report classes to concrete `ReportPublisher` implementations.

Important APIs and control flow: constructor stores configuration and initializes a map for `NodeReportProto`, `ContainerReportsProto`, `CommandStatusReportsProto`, and `PipelineReportsProto`. `getPublisherFor` looks up the publisher class, throws when no mapping exists, instantiates it reflectively with a no-arg constructor, injects config, and returns it.

State and persistence: in-memory immutable-ish mapping after construction. No persistence.

Dependencies and integration: used by `ReportManager.Builder.addPublisherFor` during datanode report manager assembly.

Risks and test signals: tests should cover all known mappings, unknown report class failures, configuration injection, and reflection failure if a publisher lacks a public no-arg constructor. `Class.newInstance` is deprecated and wraps failures broadly, so error messages may be less precise.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java

Purpose: package documentation for datanode report publishing to SCM.

Important APIs and control flow: no executable code. The documentation explains that datanode state is split into multiple heartbeat reports, names `ReportPublisherFactory`, `ReportManager`, and `ReportPublisher`, describes how to add a new report, and includes a sequence diagram for construction, initialization, periodic publishing, heartbeat transfer, and shutdown.

State and persistence: none.

Dependencies and integration: documents the integration between `DatanodeStateMachine`, `ReportManager`, `ReportPublisher`, and SCM heartbeat RPC.

Risks and test signals: no runtime tests. Documentation should be updated when new report types are added, the scheduling model changes, or report flow differs from the sequence diagram.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->
