# Research: subset-b-008003

Work item `subset-b-008003` covers Apache Ozone HDDS container-service test sources under `org/apache/hadoop/ozone/container/common`. Each section below preserves the exact source path and is wrapped for reconciliation into one per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerSet.java

## Purpose
`TestContainerSet` is a JUnit 5 test suite for `ContainerSet`, the in-memory datanode registry of container IDs to `Container<?>` instances. It verifies core map semantics, report/list APIs, per-volume indexes, on-demand scan delegation, and the write-lock acquisition protocol used when concurrent disk-balancer-style remapping may swap a container instance.

## Important APIs, Types, And Functions
- `ContainerSet.addContainer`, `getContainer`, `removeContainer`, `containerCount`, `listContainer`, `getContainerReport`, `getContainerMapIterator`, and iterable support are exercised with `KeyValueContainer` and `KeyValueContainerData`.
- `getContainerIterator(HddsVolume)` and `containerCount(HddsVolume)` are tested through mocked `HddsVolume` instances that maintain a `ConcurrentSkipListSet<Long>` of container IDs via `addContainer` and `removeContainer`.
- `registerOnDemandScanner`, `scanContainer`, and `scanContainerWithoutGap` integrate with `OnDemandContainerScanner`.
- `getContainerWithWriteLock` is tested via Mockito spies to simulate stable mappings, removed mappings, remapped containers, and retry exhaustion.
- `ContainerLayoutTestInfo.ContainerTest` runs most tests over supported `ContainerLayoutVersion` variants.

## Control Flow
The tests build containers with deterministic IDs and alternating open/closed states. Basic map tests add a container, assert duplicate insert raises `StorageContainerException`, retrieve by ID, and remove it. Iterator tests traverse both the `ContainerSet` iterable and map iterator and validate state by ID parity. Listing tests request a window from a start ID and assert returned IDs are ascending. Volume tests attach `KeyValueContainerData` to mocked volumes and assert per-volume iterators/counts reflect additions and removals. Scan tests first call scan methods without a scanner, then register a mocked scanner and verify only existing containers trigger scanner callbacks. Write-lock tests drive `getContainerWithWriteLock` through repeated `getContainer` responses to prove it locks the candidate, rechecks map identity after lock acquisition, unlocks stale candidates, retries swaps, and returns `null` after `maxContainerMapSwapRetries()`.

## State And Persistence Behavior
The suite focuses on in-memory state rather than disk persistence. `ContainerSet` is expected to maintain a main ID map and secondary volume indexes. `KeyValueContainerData` carries persisted-style metadata such as state, volume reference, max size, layout, and last data scan time; the tests use these fields to verify ordering and reporting but do not create container directories. Last-scan ordering requires never-scanned containers to sort before scanned containers, then by scan time and container ID tie-break.

## Dependencies And Integration Points
The file depends on Ozone container types (`KeyValueContainer`, `KeyValueContainerData`, `ContainerData`), HDDS protobufs (`ContainerReportsProto`, `ContainerProtos`), mocked `HddsVolume`, and `OnDemandContainerScanner`. `ContainerImplTestUtils.newContainerSet()` is the local test factory. Integration points under test include datanode container reporting, scanner scheduling, and volume-aware container lookup.

## Risks And Edge Cases
Important risk coverage includes duplicate container insertion, missing container lookup/removal, scanner calls for non-existent IDs, stale per-volume indexes after removal, scan-time ordering instability, and write-lock leaks when a container is removed or swapped during acquisition. The write-lock tests are especially concurrency-sensitive: they assert the caller receives a locked live object and stale locks are released.

## Test Signals
Strong behavioral signals are present for map semantics, iterator ordering, report count, list pagination, per-volume counts, scanner dispatch, and lock retry correctness. The tests use mocks heavily and do not exercise real disk persistence or multi-threaded races, but the simulated swap sequences encode the expected concurrency contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestHddsDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestHddsDispatcher.java

## Purpose
`TestHddsDispatcher` validates the datanode container command dispatcher for write/read chunk flows, implicit container creation, checksum validation, token verification, disk-full handling, close-container action generation, and min-free-space enforcement. It acts as an integration-style test around `HddsDispatcher`, `Handler` instances, `ContainerSet`, `MutableVolumeSet`, container metrics, and datanode state context.

## Important APIs, Types, And Functions
- `HddsDispatcher.dispatch`, `setClusterId`, `getContainer`, and `createContainer` are the central production APIs.
- Request helpers create `ContainerCommandRequestProto` messages for `WriteChunk`, `ReadChunk`, `PutSmallFile`, `PutBlock`, `ListBlock`, and `CreateContainer`.
- `createDispatcher` constructs a real `MutableVolumeSet`, formats/starts volumes, builds handlers for every `ContainerType` using `Handler.getHandlerForContainerType`, and optionally installs a `TokenVerifier`.
- Disk-space tests use `HddsVolume`, `MockSpaceUsageSource`, `MockSpaceUsageCheckFactory`, `DatanodeConfiguration` free-space keys, and volume stats counters.
- Heartbeat/action integration uses `StateContext.addContainerActionIfAbsent` and `DatanodeStateMachine.triggerHeartbeat`.

## Control Flow
The dispatcher is usually initialized with temporary datanode and metadata directories, a random SCM ID, and handlers backed by a fresh `ContainerSet`. The normal write path sends `WriteChunk`, verifies success, reads the chunk back, optionally commits it with `PutBlock`, and lists block metadata. One test verifies that a `WriteChunk` can implicitly create a missing container, while commit-stage write without a container returns `CONTAINER_NOT_FOUND`. Failure tests spy on `createContainer` to return `DISK_OUT_OF_SPACE` and assert the dispatcher logs creation failure. Duplicate tests send the same write and put-block requests repeatedly and assert idempotent success and a single block entry. Malformed put-block data returns `MALFORMED_REQUEST` without marking the container unhealthy. Checksum tests enable chunk data validation and verify write/read checksum paths and `PutSmallFile`. Token tests enumerate dispatcher contexts that must skip verification for internal Ratis stages and contexts that must call the verifier.

## State And Persistence Behavior
The tests create real temporary volume directories and container files through `MutableVolumeSet`, `HddsVolume`, and `KeyValueContainer.create`. Container state transitions matter: implicitly created containers remain open, already-existing create requests must not mark containers unhealthy, malformed requests must not poison the container, and near-full containers trigger close actions. Disk-space tests update cached usage with `incrementUsedSpace` so local enforcement reads the same cache used by production code. The dispatcher also updates metrics counters for soft-band and hard-limit write requests.

## Dependencies And Integration Points
This suite integrates container command protobuf builders, `BlockID`, checksum utilities, Ratis `DispatcherContext`, token verification, Ozone configuration, volume choosing policies, `ContainerChecksumTreeManager`, `StateContext`, `ContainerMetrics`, and mocked datanode details. It covers the handoff from command dispatch into type-specific handlers and from disk/full conditions into SCM-facing container actions and heartbeat triggers.

## Risks And Edge Cases
Covered risks include idempotent duplicate writes, implicit creation failure, container-not-found at commit stage, checksum enforcement, malformed block metadata, overfull containers, volume hard free-space rejection, soft free-space telemetry, and accidental token checks during internal state-machine phases. A subtle risk is heartbeat throttling: repeated full-container writes should enqueue actions but not trigger unbounded immediate heartbeats per container.

## Test Signals
The file provides strong integration signals because it uses real volume setup for most paths. Assertions cover response result codes, data round trips, logs, container health flags, action counts, heartbeat counts, token verifier invocation, and volume stats metrics. It does not fully simulate concurrent dispatcher calls or all command types, but it covers high-risk write-path behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestHddsDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestStorageLocationReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestStorageLocationReport.java

## Purpose
`TestStorageLocationReport` verifies that `StorageLocationReport` serializes filesystem-level capacity fields into `StorageReportProto` and can reconstruct them from protobuf.

## Important APIs, Types, And Functions
- `StorageLocationReport.newBuilder()` sets ID, path, `StorageType`, capacity, SCM used bytes, remaining bytes, committed bytes, free-space-to-spare, reserved bytes, filesystem capacity, and filesystem available bytes.
- `getProtoBufMessage()` emits `StorageReportProto`.
- `StorageLocationReport.getFromProtobuf` parses protobuf back into a report object.

## Control Flow
The test builds a report with both logical storage accounting and filesystem capacity/available values. It asserts the proto has `fsCapacity` and `fsAvailable` populated, then parses it and verifies all expected numeric fields survived the round trip.

## State And Persistence Behavior
There is no persistent state. The behavior under test is a serialization contract between the datanode's local volume report model and SCM heartbeat protobufs.

## Dependencies And Integration Points
The file depends on Hadoop `StorageType`, HDDS `StorageReportProto`, and the local `StorageLocationReport` builder/parser. It integrates with heartbeat storage reporting because these proto fields are consumed by SCM.

## Risks And Edge Cases
The covered risk is silent loss of filesystem capacity/available fields when converting to/from protobuf. It does not cover unset optional fields, negative values, or builder validation.

## Test Signals
The signal is narrow but precise: it proves new filesystem fields are included in protobuf and parsed back alongside existing capacity, used, remaining, reserved, and spare-space fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestStorageLocationReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/package-info.java

## Purpose
This `package-info.java` supplies package documentation for `org.apache.hadoop.ozone.container.common.impl` test classes, describing the package as datanode container related test cases.

## Important APIs, Types, And Functions
No executable API is declared. The only Java element is the package declaration and Javadoc package comment.

## Control Flow
There is no runtime control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The file integrates only with Java package documentation and test-source organization.

## Risks And Edge Cases
Risk is limited to stale or misleading package documentation if package responsibilities change.

## Test Signals
No tests are defined; the file only contributes documentation metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/interfaces/TestHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/interfaces/TestHandler.java

## Purpose
`TestHandler` verifies container handler lookup through `HddsDispatcher` and `Handler.getHandlerForContainerType`. It ensures the known key-value container type resolves to `KeyValueHandler` and an invalid protobuf enum value resolves to `null`.

## Important APIs, Types, And Functions
- `Handler.getHandlerForContainerType` builds handlers by `ContainerProtos.ContainerType`.
- `HddsDispatcher.getHandler` retrieves handlers from the dispatcher map.
- `VolumeChoosingPolicyFactory.getPolicy`, `ContainerChecksumTreeManager`, `ContainerMetrics`, mocked `ContainerSet`, and mocked `VolumeSet` support handler creation.

## Control Flow
`setup` creates an `OzoneConfiguration`, mocked container/volume state, a mock datanode context, metrics, and a handler map for all known container types. The test then constructs `HddsDispatcher` with those handlers. `testGetKeyValueHandler` asks for `KeyValueContainer` and asserts the returned instance is a `KeyValueHandler`. `testGetHandlerForInvalidContainerType` uses `ContainerType.forNumber(2)` as a sentinel invalid value, asserts it is still `null`, and verifies dispatcher lookup with `null` returns `null`.

## State And Persistence Behavior
The file uses no persistent storage. Runtime state is the dispatcher handler map and global `ContainerMetrics`, which is removed in `tearDown`.

## Dependencies And Integration Points
The test depends on protobuf enum numbering, `HddsDispatcher`, `Handler`, `KeyValueHandler`, metrics lifecycle, checksum manager construction, and helper context from `ContainerTestUtils`. It protects the integration between protobuf container types and concrete datanode container handlers.

## Risks And Edge Cases
The invalid enum test intentionally guards against new `ContainerType` values occupying number 2; if a new type is added, this test should fail so handler mapping expectations are revisited. It also checks dispatcher null tolerance.

## Test Signals
The signals are direct type and null assertions. Coverage is narrow and does not execute handler methods, but it is useful for handler factory mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/interfaces/TestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.container.common` test utilities as SCM testing and mocking utilities.

## Important APIs, Types, And Functions
No classes, methods, or constants are declared.

## Control Flow
There is no runtime control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The file contributes package-level Javadoc to the test source tree only.

## Risks And Edge Cases
Risk is limited to documentation drift as package contents evolve.

## Test Signals
No executable test signal is present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportManager.java

## Purpose
`TestReportManager` checks that `ReportManager` initializes registered report publishers with the configured `StateContext` and an internal `ScheduledExecutorService`.

## Important APIs, Types, And Functions
- `ReportManager.newBuilder(conf)` creates the builder.
- `setStateContext`, `addPublisher`, `build`, and `init` define the tested setup path.
- `ReportPublisher.init(StateContext, ScheduledExecutorService)` is verified on a mock publisher.

## Control Flow
The test creates a dummy context and dummy publisher, adds the publisher to a builder, builds the manager, calls `init`, and verifies the publisher receives exactly one initialization call with the context and any scheduled executor.

## State And Persistence Behavior
There is no persistence. The state under test is the manager's publisher list and executor initialization.

## Dependencies And Integration Points
This test links report scheduling to `StateContext`, which later supplies heartbeat reports. It depends on Mockito and `OzoneConfiguration`.

## Risks And Edge Cases
The main risk covered is forgetting to initialize added publishers. It does not verify executor shutdown or multiple publishers, but the single-publisher check confirms the builder-to-init path.

## Test Signals
The signal is a Mockito verification of publisher initialization count and arguments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisher.java

## Purpose
`TestReportPublisher` validates base `ReportPublisher` scheduling behavior and command-status report generation. It verifies periodic execution, full-report refresh into `StateContext`, and `CommandStatusReportPublisher` handling of pending/executed command statuses.

## Important APIs, Types, And Functions
- `ReportPublisher.init` schedules the publisher at fixed rate.
- `ReportPublisher.run` calls subclass `getReport` and pushes the result to `StateContext.refreshFullReport`.
- `DummyReportPublisher` overrides `getReportFrequency` and `getReport`, counting invocations.
- `CommandStatusReportPublisher.getReport` reads `StateContext.getCommandStatusMap` and builds command status protobuf reports.
- `CommandStatus.CommandStatusBuilder`, `SCMCommandProto.Type`, and `CommandStatus.Status` provide report content.

## Control Flow
One test verifies `init` calls `scheduleAtFixedRate` with initial delay and frequency. Scheduling tests use a daemon `ScheduledExecutorService`, sleep long enough for one or two runs, then shut down the executor and assert no more report calls happen. `testPublishReport` verifies a scheduled run refreshes the full report in `StateContext`. The command-status test starts with an empty map and expects `null`, inserts one pending delete-block command and one executed close-container command, then asserts the report contains two statuses.

## State And Persistence Behavior
State is in-memory: scheduled executor tasks, a report invocation counter, and a concurrent command-status map. No persistent storage is used.

## Dependencies And Integration Points
The suite depends on Hadoop executor helpers, Guava `ThreadFactoryBuilder`, protobuf `Message`, `StateContext`, and command status model classes. It verifies the link between datanode command execution status and heartbeat report publication.

## Risks And Edge Cases
Covered risks include publisher not scheduling, scheduled execution continuing after shutdown, `StateContext` not receiving reports, empty command status maps producing empty/no reports, and command statuses not being included. Timing-based sleeps can be somewhat brittle but frequencies are short and assertions are simple.

## Test Signals
Signals include schedule verification, invocation counts before/after shutdown, `refreshFullReport` verification, and command status count assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisherFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisherFactory.java

## Purpose
`TestReportPublisherFactory` verifies that `ReportPublisherFactory` maps known heartbeat report protobuf classes to the correct publisher implementations and rejects unsupported classes.

## Important APIs, Types, And Functions
- `ReportPublisherFactory.getPublisherFor(Class<?>)` is the method under test.
- Known mappings checked are `ContainerReportsProto` to `ContainerReportPublisher` and `NodeReportProto` to `NodeReportPublisher`.
- Unsupported `HddsProtos.DatanodeDetailsProto` should throw a `RuntimeException`.

## Control Flow
Each positive test creates an `OzoneConfiguration`, asks the factory for a publisher by report class, and asserts the concrete class and retained configuration. The negative test requests a publisher for an unrelated protobuf class and asserts the exception message contains the expected diagnostic.

## State And Persistence Behavior
There is no persistence. The only state is the factory's mapping and each publisher's configuration reference.

## Dependencies And Integration Points
The factory integrates report protobuf types with scheduled publisher classes used by datanode heartbeats. The test depends on AssertJ/JUnit and HDDS protobuf classes.

## Risks And Edge Cases
The main risk is broken or stale class-to-publisher mapping, especially when new report types are added. Unsupported class handling is also covered.

## Test Signals
The test gives direct class equality, config equality, and exception-message signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisherFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/package-info.java

## Purpose
This package descriptor documents the report test package as containing tests for report publishers that generate SCM heartbeat reports.

## Important APIs, Types, And Functions
No executable API is present.

## Control Flow
There is no runtime control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The file provides package-level Javadoc for report publisher tests.

## Risks And Edge Cases
Risk is limited to documentation drift.

## Test Signals
No executable tests are defined.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestDatanodeConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestDatanodeConfiguration.java

## Purpose
`TestDatanodeConfiguration` verifies configuration binding, validation, defaults, and derived calculations for datanode container-service settings. It covers delete thread counts, disk check timing, failed-volume tolerances, block-delete worker intervals, min-free-space soft/hard thresholds, Ratis log appender wait time, and gRPC socket backlog.

## Important APIs, Types, And Functions
- `OzoneConfiguration.getObject(DatanodeConfiguration.class)` and `setFromObject` drive config binding.
- Constants under test include container delete threads, periodic disk checks, failed volume tolerances, disk check min gap/timeout, block delete worker interval, min free-space bytes/percent/hard-percent, and gRPC backlog.
- `DatanodeConfiguration.getMinFreeSpace`, `getHardLimitMinFreeSpace`, and `getSoftBandMinFreeSpaceWidth` implement derived disk-space behavior.
- `ContainerTestUtils.newXceiverServerRatis(...).newRaftProperties()` checks Ratis appender wait config integration.

## Control Flow
Positive and negative tests populate an `OzoneConfiguration`, bind it to `DatanodeConfiguration`, and assert valid values survive while invalid zero/negative values fall back to defaults. Default-value tests unset test-module overrides, capture logs, and assert no invalid-ratio warnings. Free-space tests vary fixed byte thresholds and percentages over several capacities, including the case where hard-limit ratio exceeds soft/reporting ratio. Ratis tests set `DatanodeRatisServerConfig.logAppenderWaitTimeMin`, write it back, and assert resulting Raft properties. gRPC tests assert default, configured, and setter values.

## State And Persistence Behavior
There is no persistence, but the suite validates configuration state materialization and derived capacity calculations used later by volume reporting and write enforcement. The Ratis path checks generated in-memory `RaftProperties`.

## Dependencies And Integration Points
The test depends on HDDS/Ozone configuration annotations, `DatanodeRatisServerConfig`, `MockPipeline`, Ratis `RaftServerConfigKeys`, and `ContainerTestUtils`. It integrates datanode config values with disk-space policy and Xceiver/Ratis server configuration.

## Risks And Edge Cases
Covered risks include invalid config values silently breaking runtime behavior, negative disk check durations, invalid min-free-space ratios outside `[0,1]`, byte and percent thresholds interacting incorrectly, hard threshold exceeding soft threshold, and gRPC backlog not honoring config. The default test includes a non-ASCII stray character in a comment only; executable behavior is unaffected.

## Test Signals
Signals are direct assertions on bound values, default fallback values, derived byte calculations for multiple capacities, log absence for defaults, and Ratis property equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestDatanodeConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestSCMConnectionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestSCMConnectionManager.java

## Purpose
`TestSCMConnectionManager` verifies that removing an SCM server unregisters the endpoint from the manager without mutating the endpoint state's lifecycle value.

## Important APIs, Types, And Functions
- `SCMConnectionManager.addSCMServer`, `removeSCMServer`, `getValues`, and `close` are used.
- `EndpointStateMachine.setState` and `getState` are used to set and verify `HEARTBEAT`.

## Control Flow
The test creates a connection manager in try-with-resources, adds one SCM address, obtains the created endpoint, sets its state to `HEARTBEAT`, removes the SCM server, and asserts the manager has no endpoints while the removed endpoint object still reports `HEARTBEAT`.

## State And Persistence Behavior
State is in-memory endpoint registration and endpoint state. There is no persistence.

## Dependencies And Integration Points
The test depends on `OzoneConfiguration`, `SCMConnectionManager`, `EndpointStateMachine`, and Java `InetSocketAddress`. It protects connection-manager behavior used by datanode endpoint state transitions.

## Risks And Edge Cases
The covered edge case is removal being mistaken for endpoint shutdown. This matters if external code still observes an endpoint object after removal.

## Test Signals
Signals are manager collection emptiness and preserved endpoint state equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestSCMConnectionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestStateContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestStateContext.java

## Purpose
`TestStateContext` validates `StateContext`, the datanode state-machine context that stores reports, actions, command queues, leader SCM term, endpoint queues, and task execution state. It checks both heartbeat-facing data queues and datanode-state execution safeguards.

## Important APIs, Types, And Functions
- Report APIs: `refreshFullReport`, `addIncrementalReport`, `putBackReports`, `getAllAvailableReports`, `getAllAvailableReportsUpToLimit`, `getFullContainerReportDiscardPendingICR`, `getContainerReports`, `getNodeReport`, and `getPipelineReports`.
- Action APIs: `addPipelineActionIfAbsent`, `getPendingPipelineAction`, `addContainerAction`, and `getPendingContainerAction`.
- Command APIs: `addCommand`, `getNextCommand`, `getCommandQueueSummary`, `setTermOfLeaderSCM`, and `getTermOfLeaderSCM`.
- Execution APIs: `execute`, `getTask`, `isThreadPoolAvailable`, and state getters/setters.
- Mock report creation uses protobuf `Message` descriptors and special handling for `IncrementalContainerReportProto`.

## Control Flow
Report tests create contexts with two SCM endpoints, refresh many full reports, add many incremental reports, and assert queue behavior per endpoint. Full reports keep only the latest instance and are sent to each endpoint, while incremental reports are queued and dequeued. `putBackReports` only requeues accepted incremental/report status types for the target endpoint. One flow confirms getting a full container report discards pending ICRs. Action tests add pipeline close actions and container close actions, proving duplicate pipeline actions are suppressed and pipeline actions remain pending until the datanode no longer reports that pipeline. Execution tests create custom `DatanodeState` tasks to ensure shutdown cannot transition back to running, saturated executors prevent execute/await, and awaiting is skipped until thread-pool capacity exists. Command tests count queued command types and validate newer SCM terms advance the context while older-term commands are dropped.

## State And Persistence Behavior
All state is in-memory but central to datanode behavior: per-endpoint report queues, latest full reports, incremental report queues, action queues, command queues, leader SCM term, and current datanode state. No disk persistence is used. Queue draining and requeueing are persistence-like semantics for heartbeat retry reliability.

## Dependencies And Integration Points
The suite integrates with datanode state machine states, protobuf heartbeat report/action types, `OzoneContainer` pipeline reporting, `ContainerSet.getContainerReport`, `SCMCommand` subclasses, executor services, Guava direct executor, and Ozone test waiting utilities. It protects the boundary between report publishers, heartbeat tasks, command handlers, and state-machine transitions.

## Risks And Edge Cases
High-value edge cases include report duplication, lost incremental reports, full container reports not clearing stale ICRs, non-existent endpoints, duplicate pipeline close actions, pipeline action dequeuing before the pipeline is actually gone, restart after shutdown, executor saturation, command summary accuracy, and stale SCM leader-term command rejection.

## Test Signals
Signals are queue count maps by protobuf descriptor name, per-endpoint report availability, action list sizes, executor availability assertions, command type counters, and term/command queue assertions. The tests are mostly mock-based but exercise intricate in-memory control flow.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestStateContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerCommandHandler.java

## Purpose
`TestCloseContainerCommandHandler` verifies datanode handling of SCM close-container commands across pipeline presence, force-close flags, already-closed containers, missing containers, and handler thread-pool sizing.

## Important APIs, Types, And Functions
- `CloseContainerCommandHandler.handle`, `getQueuedCount`, and `getThreadPoolMaxPoolSize` are under test.
- `ContainerController.markContainerForClose` and `ContainerSet` supply container lookup and lifecycle management.
- `Handler.markContainerForClose`, `quasiCloseContainer`, and `closeContainer` are verified.
- `XceiverServerSpi.isExist` and `submitRequest` represent pipeline/Ratis write-channel integration.
- Helpers create close commands with known/unknown pipelines and force flags.

## Control Flow
Setup creates a `KeyValueContainer` bound to a random pipeline, adds it to `ContainerSet`, wires a `ContainerController` with a mocked handler, and configures the mocked write channel to recognize one pipeline and reject another. Tests submit close commands, wait until the handler queue drains, and verify handler/write-channel side effects. With an existing pipeline, the container is marked closing and a close request is submitted to the write channel. Without a pipeline, it is marked and then quasi-closed. Force close without a pipeline closes directly; force close with an existing pipeline still submits through the pipeline and does not close locally immediately. Already closed containers are no-ops. Missing and explicitly missing containers throw `ContainerNotFoundException` when marking for close.

## State And Persistence Behavior
The file uses in-memory `ContainerSet` and container data state. It validates state transitions through mocked handler methods rather than real disk mutation. Queue state is observed through `getQueuedCount`.

## Dependencies And Integration Points
The test depends on Ozone command classes, `PipelineID`, `XceiverServerSpi`, `ContainerController`, `Handler`, `KeyValueContainer`, and container layout parameterization. It protects SCM command handling at the boundary between local container state and Ratis pipeline closure.

## Risks And Edge Cases
Covered risks include closing through a missing pipeline, force close semantics, quasi-closed force-close behavior, idempotent close of already closed containers, missing-container errors, and asynchronous queue completion. The difference between force-close with and without a live pipeline is a key semantic risk.

## Test Signals
Signals are Mockito method verifications, exception message containment, and queue-drain waits. Thread-pool size is asserted as 1.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestClosePipelineCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestClosePipelineCommandHandler.java

## Purpose
`TestClosePipelineCommandHandler` verifies Ratis pipeline close command handling, idempotency when a pipeline is already absent, and duplicate-suppression while a close is in progress.

## Important APIs, Types, And Functions
- `ClosePipelineCommandHandler.handle`, `isPipelineCloseInProgress`, and `getInvocationCount` are under test.
- `XceiverServerRatis.isExist`, `removeGroup`, `getRaftPeersInPipeline`, `getShouldDeleteRatisLogDirectory`, and `getServer` are mocked.
- `RaftClient.getGroupManagementApi` and `GroupManagementApi.remove` represent peer-side group removal.
- `RatisHelper.toRaftPeer` and `toRaftPeerId` convert datanode identities.

## Control Flow
The main close test creates a three-node pipeline where the current datanode is one member. The handler removes the local Ratis group and calls the group-management API for the other two peers, passing deletion flags derived from the write channel. The idempotency test sets `isExist` to false and verifies no remove operations happen. The pending-close test blocks the first `removeGroup` call using latches, submits a duplicate command for the same pipeline, releases the first call, and asserts only one invocation was processed and the in-progress flag is cleared.

## State And Persistence Behavior
State under test is local in-memory duplicate tracking for pipeline UUIDs and Ratis group membership side effects. Actual Ratis logs are not persisted, but the delete-log-directory flag is passed through and verified.

## Dependencies And Integration Points
This file integrates SCM close-pipeline commands with `OzoneContainer` write channel, Ratis server/group APIs, `SCMConnectionManager`, and `StateContext`. It is a boundary test for local and remote Ratis group cleanup.

## Risks And Edge Cases
Covered risks include duplicate command execution, removing a non-existent pipeline, in-progress flag leaks, and incorrect propagation of log directory deletion behavior to remote peer removals.

## Test Signals
Signals are `removeGroup` call counts, `GroupManagementApi.remove` call counts and arguments, in-progress boolean assertions, executor termination, and invocation count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestClosePipelineCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCreatePipelineCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCreatePipelineCommandHandler.java

## Purpose
`TestCreatePipelineCommandHandler` verifies Ratis pipeline creation command handling and idempotency when a pipeline already exists locally.

## Important APIs, Types, And Functions
- `CreatePipelineCommandHandler.handle` is the command entry point.
- `XceiverServerSpi.isExist` and `addGroup` represent local pipeline group creation.
- `RaftClient.getGroupManagementApi` and `GroupManagementApi.add` represent remote peer group creation.
- `CreatePipelineCommand` carries `PipelineID`, replication type/factor, and datanode list.

## Control Flow
Setup creates mocks for `OzoneContainer`, connection manager, Raft client, and group manager. The creation test builds a three-datanode RATIS pipeline, mocks local absence, calls the handler, verifies local `addGroup` with a zero priority list, and verifies group creation on the two non-local peers. The idempotency test mocks local existence and asserts neither local nor remote group addition is invoked.

## State And Persistence Behavior
State is Ratis group membership, mocked through write-channel and group-management APIs. No persistent data is written in the test.

## Dependencies And Integration Points
The test integrates SCM pipeline creation commands, Ozone write channel, Ratis group management, datanode context, and command handler executor behavior. Mockito lenient settings support broad setup without strict unused-stub failures.

## Risks And Edge Cases
Covered risks include duplicate pipeline creation, failing to add remote peer groups, and incorrect priority-list construction. It does not cover failures from Ratis APIs.

## Test Signals
Signals are direct verification of local `addGroup`, remote `add`, and zero calls under idempotent existing-pipeline conditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCreatePipelineCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteBlocksCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteBlocksCommandHandler.java

## Purpose
`TestDeleteBlocksCommandHandler` validates delete-block command execution, schema-handler dispatch, retry behavior, lock timeout handling, queue saturation status, duplicate transaction accounting, and stale container-data retry behavior.

## Important APIs, Types, And Functions
- `DeleteBlocksCommandHandler.executeCmdWithRetry`, `submitTasks`, `handle`, `stop`, `getSchemaHandlers`, and nested `DeleteCmdWorker` are tested.
- `SchemaHandler.handle` is replaced with test handlers for schema V1, V2, and V3.
- `DeleteBlocksCommand`, `DeletedBlocksTransaction`, `DeleteBlockTransactionResult`, and `CommandStatus` model SCM delete-block work and acknowledgements.
- `KeyValueContainerData.incrPendingDeletionBlocks`, `updateDeleteTransactionId`, and duplicate detection update container deletion state.
- `DatanodeConfiguration` block delete queue limit and worker interval are exercised.

## Control Flow
Setup creates a mocked `OzoneContainer`, a `ContainerSet` with closed key-value containers attached to a mocked volume, a spy `DeleteBlocksCommandHandler`, and schema handler spies keyed by schema version. Basic execution builds a transaction for an existing container and asserts the matching schema handler runs once and returns success. Timeout tests manually hold a container write lock: one case leaves it locked so that transaction fails after retry while another transaction succeeds; another releases the lock after the first submit so retry succeeds. Exception handling stubs `submitTasks` to include a failed future followed by success and asserts execution continues. Queue-full handling sets a small delete queue limit, sends more commands than capacity, and expects early statuses `PENDING` then later statuses `FAILED` with empty block deletion ACKs. Duplicate transaction tests execute identical and older transaction IDs to ensure success is idempotent and pending deletion counters are not double-counted for the same transaction content. The stale-container test spies `ContainerSet.getContainer` to return an old replica, then a new replica, proving the first stale attempt skips schema handling and retry handles the live replica.

## State And Persistence Behavior
The suite exercises in-memory container deletion state that would later drive block deletion persistence: pending deletion block count, pending deletion bytes, and last delete transaction ID. It also checks container write locks, command status map behavior through `StateContext`, and queue capacity. No actual block files are deleted; schema handlers simulate metadata mutation.

## Dependencies And Integration Points
Dependencies include `ContainerTestVersionInfo` schema parameterization, `ContainerLayoutVersion`, `BlockDeletingServiceMetrics`, `StateContext`, `DatanodeStateMachine`, `SCMConnectionManager`, `HddsVolume`, and protobuf delete transaction/result types. The test protects integration between SCM delete-block commands, container locking, schema-specific DB mutation, metrics, and heartbeat command-status reporting.

## Risks And Edge Cases
Critical covered risks include lock leaks/timeouts, retry not happening, failure of one future aborting all results, queue saturation not reporting failure, duplicate SCM transactions inflating deletion counters, older transactions being incorrectly skipped, and DiskBalancer-style container map swaps causing stale metadata mutation.

## Test Signals
Signals include schema-handler invocation counts, submit retry counts, result success flags by transaction ID, block-delete metrics, command status values, ACK result counts, pending block/byte counters, and stale-replica handler exclusion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteBlocksCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerCommandHandler.java

## Purpose
`TestDeleteContainerCommandHandler` verifies asynchronous delete-container command handling, deadline expiration, SCM leader-term filtering, and queue-size limiting.

## Important APIs, Types, And Functions
- `DeleteContainerCommandHandler.handle`, `getTimeoutCount`, and `getInvocationCount` are tested.
- `ContainerController.deleteContainer(containerId, force)` is the side effect under verification.
- `DeleteContainerCommand.setDeadline` and `setTerm` provide command metadata.
- `StateContext.getTermOfLeaderSCM` controls term acceptance.
- `TestClock` allows deterministic deadline advancement.

## Control Flow
Setup creates a test clock, mocked Ozone container/controller/context, and a default SCM term. The expiration test creates three commands, advances the clock so the first deadline is expired but the second is still valid and the third has no deadline, then verifies only valid/no-deadline commands reach the controller. Term tests execute a command only when its term matches the current leader term and drop it when the context has a newer term. Queue-size testing blocks the single worker with a lock, submits many duplicate commands with queue size one, and verifies only one delete reaches the controller while extra submissions are ignored/limited.

## State And Persistence Behavior
The handler tracks invocation and timeout counters plus executor queue state. Real container deletion persistence is mocked behind `ContainerController`.

## Dependencies And Integration Points
The test depends on Java executors/latches, Guava `ThreadFactoryBuilder`, Ozone `DeleteContainerCommand`, `StateContext`, and controller APIs. It protects command-handler integration with leader-term state and async worker queues.

## Risks And Edge Cases
Covered risks include executing expired SCM commands, accepting stale-term commands, unbounded queue growth, duplicate queued deletes, and deadline-free commands being dropped accidentally.

## Test Signals
Signals are controller invocation counts, timeout count, invocation count, and latch-based confirmation of async execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconcileContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconcileContainerCommandHandler.java

## Purpose
`TestReconcileContainerCommandHandler` verifies datanode handling of reconcile-container commands, including task submission, incremental container report emission, and metrics delegation through the replication supervisor.

## Important APIs, Types, And Functions
- `ReconcileContainerCommandHandler.handle`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, `getAverageRunTime`, and `getMetricsName` are tested.
- `ReconcileContainerCommand` identifies containers to reconcile.
- `ReplicationSupervisor.addTask` is mocked to immediately run `ReconcileContainerTask`.
- `IncrementalReportSender<Container>` captures generated container reports.
- `ContainerController`, `KeyValueHandler`, `ContainerChecksumTreeManager`, and `DNContainerOperationClient` support task execution.

## Control Flow
Initialization creates three key-value containers with block metadata and DB paths under temporary directories, adds them to a `ContainerSet`, wires a real `KeyValueHandler` into a `ContainerController`, and mocks the supervisor to execute tasks synchronously. The report test sends reconcile commands for known containers and one unknown container. It expects reports for all known containers and no report for the unknown ID. The metrics test sends known commands, stubs supervisor metrics for the handler's metric name, and asserts invocation, queued, total runtime, average runtime, and metric-name values.

## State And Persistence Behavior
The test creates temporary metadata/DB paths and block metadata, so it is closer to persistence-facing behavior than a pure mock. The reconciliation operation emits container reports with non-zero data checksum values. Actual remote reconciliation is mocked.

## Dependencies And Integration Points
The file integrates command handling with replication supervisor tasks, checksum/reconcile task infrastructure, key-value handler/report generation, container controller, incremental report sender, and metrics. Layout parameterization covers container layout variants.

## Risks And Edge Cases
Covered risks include missing ICR emission after reconcile, unknown containers producing bogus reports, metric-name drift, queued count not reflecting supervisor state, and incomplete checksum reporting. The test notes current checksum implementation is incomplete and uses a mocked/non-zero checksum.

## Test Signals
Signals are captured report map size/content, non-zero data checksum assertions, invocation counts, and supervisor-backed metric values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconcileContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconstructECContainersCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconstructECContainersCommandHandler.java

## Purpose
`TestReconstructECContainersCommandHandler` verifies metrics and task-submission behavior for EC container reconstruction commands.

## Important APIs, Types, And Functions
- `ReconstructECContainersCommandHandler.handle`, `getCommandType`, `getMetricsName`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, and `getAverageRunTime` are tested.
- `ReconstructECContainersCommand` carries container ID, source datanodes with replica indexes, target datanodes, missing indexes, and `ECReplicationConfig`.
- `ReplicationSupervisor.addTask` is the handoff to execution.
- `CommandHandlerMetrics.create` exposes metrics for command handlers.

## Control Flow
Setup creates mocked supervisor, EC coordinator, Ozone container, state context, and connection manager. The test builds a command with EC 3-2 replication, five sources, two targets, and missing indexes. It handles one command, asserts the metric name matches `ECReconstructionCoordinatorTask.METRIC_NAME`, stubs supervisor request count to one, and checks invocation count. It then handles five more commands, stubs supervisor counters, and verifies capped/derived handler metrics and that the metrics collector emits one record.

## State And Persistence Behavior
No persistent state is used. Handler state is metrics/invocation accounting; actual reconstruction work is delegated and mocked.

## Dependencies And Integration Points
Dependencies include EC replication config, protobuf `ByteString` for missing indexes, `ECReconstructionCoordinator`, `ReplicationSupervisor`, `CommandHandlerMetrics`, and SCM command types. It protects metrics integration for reconstruction work.

## Risks And Edge Cases
Covered risks include wrong metric name, missing task submission, metrics not reflecting supervisor counters, and metrics source not registering records. It does not validate reconstruction data movement.

## Test Signals
Signals are invocation counts, queued/total/average runtime values, metric-name equality, and metrics collector record count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconstructECContainersCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReplicateContainerCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReplicateContainerCommandHandler.java

## Purpose
`TestReplicateContainerCommandHandler` verifies metrics and task-submission accounting for container replication commands, including both pull-from-sources and push-to-target command forms.

## Important APIs, Types, And Functions
- `ReplicateContainerCommandHandler.handle`, `getCommandType`, `getMetricsName`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, and `getAverageRunTime` are under test.
- `ReplicateContainerCommand.fromSources` and `toTarget` create download and push replication commands.
- `ReplicationSupervisor.addTask` accepts replication tasks.
- `ContainerReplicator` mocks represent download and push implementations.
- `CommandHandlerMetrics.create` registers metrics for the handler map.

## Control Flow
The test creates a handler with mocked supervisor and replicators, registers command metrics, and sends one source-based command to check metric name and initial invocation count. It then sends additional source-based and target-based commands, stubs supervisor metrics for `ReplicationTask.METRIC_NAME`, and asserts invocation count, queued count, total runtime, average runtime, and that metrics collection produces one record.

## State And Persistence Behavior
No container data is persisted. The test validates handler accounting and delegation state only.

## Dependencies And Integration Points
Dependencies include `ReplicationSupervisor`, `ContainerReplicator`, `ReplicationTask`, `CommandHandlerMetrics`, Ozone command models, and SCM command type registration. It protects metrics integration for replication work regardless of direction.

## Risks And Edge Cases
Covered risks include metrics name drift, push commands not counted with source commands, supervisor metrics not surfacing through the handler, and metrics source registration issues.

## Test Signals
Signals include invocation count, supervisor-derived queued/runtime metrics, and metrics collector record count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReplicateContainerCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java

## Purpose
This package descriptor documents the command-handler test package.

## Important APIs, Types, And Functions
No executable APIs are declared.

## Control Flow
There is no runtime control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The file contributes Javadoc package metadata for command handler tests.

## Risks And Edge Cases
Risk is limited to documentation drift.

## Test Signals
No executable test signal is present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/datanode/TestRunningDatanodeState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/datanode/TestRunningDatanodeState.java

## Purpose
`TestRunningDatanodeState` verifies `RunningDatanodeState.await` timing behavior while endpoint tasks are still executing versus when completed endpoint tasks are available.

## Important APIs, Types, And Functions
- `RunningDatanodeState.await`, `setExecutorCompletionService`, and `setExecutingEndpointCount` are under test.
- `ExecutorCompletionService` supplies endpoint task completion events.
- `EndpointStateMachine.EndPointStates.SHUTDOWN` is used as the completed task result.

## Control Flow
The test creates a mocked `SCMConnectionManager` returning two endpoint state machines, injects a completion service backed by a fixed thread pool, submits two tasks blocked on a future, and sets executing endpoint count to the pool size. A first `await(500ms)` call should wait at least 500ms because no task completes. After completing the first future, it submits two already-completing shutdown tasks and calls `await(500ms)` again; this time it should return before 500ms.

## State And Persistence Behavior
State is in-memory execution count and completion-service queue state. There is no persistence.

## Dependencies And Integration Points
The test depends on endpoint state machines, SCM connection manager, Java futures/executors, and Hadoop `Time.monotonicNow`. It protects the running datanode state's scheduling loop behavior.

## Risks And Edge Cases
Covered risk is `await` always sleeping for the full timeout even when endpoint tasks complete, or returning too early while all tasks are blocked. Timing assertions are inherently sensitive but use broad 500ms boundaries.

## Test Signals
Signals are elapsed-time assertions before and after future completion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/datanode/TestRunningDatanodeState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/TestHeartbeatEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/TestHeartbeatEndpointTask.java

## Purpose
`TestHeartbeatEndpointTask` verifies datanode heartbeat request assembly and response command handling. It checks report inclusion, container actions, command queue reports, leader SCM term updates, and decoding of reconstruct/reconcile commands from SCM heartbeat responses.

## Important APIs, Types, And Functions
- `HeartbeatEndpointTask.call` sends heartbeat requests and processes responses.
- Builder API `HeartbeatEndpointTask.newBuilder` wires config, datanode details, `StateContext`, layout version manager, and endpoint state machine.
- `StateContext` supplies reports/actions and receives commands.
- `StorageContainerDatanodeProtocolClientSideTranslatorPB.sendHeartbeat` is mocked to capture requests and return responses.
- Protobufs under test include `SCMHeartbeatRequestProto`, `SCMHeartbeatResponseProto`, `NodeReportProto`, `ContainerReportsProto`, `CommandStatusReportsProto`, `ContainerAction`, and `CommandQueueReportProto`.
- Commands tested include `ReconstructECContainersCommand` and `ReconcileContainerCommand`.

## Control Flow
Command-response tests mock SCM to return a heartbeat response containing either reconstruct-EC or reconcile-container command protobufs. After `call`, the context command summary should include one command of the returned type. Request-assembly tests populate the context with no reports, node report, container report, command status report, container action, or all reports/actions. They capture the outgoing heartbeat and assert the corresponding optional fields and repeated counts are present or absent. The all-reports test also stubs queued command counts for every `SCMCommandProto.Type` and asserts the heartbeat contains a command queue report with matching types and counts. The no-report test also returns a newer SCM term and verifies `StateContext` updates its leader term.

## State And Persistence Behavior
State is the in-memory heartbeat context: report queues, command queues, container action queues, and leader SCM term. No data is persisted. Report retrieval may drain queues depending on report type.

## Dependencies And Integration Points
The test integrates heartbeat endpoint logic with SCM protocol translator, datanode details, layout version manager, `StateContext`, command queue counters, EC replication config, and container action protobufs. It is a key boundary test between datanode state and SCM heartbeat protocol.

## Risks And Edge Cases
Covered risks include missing reports in heartbeat requests, accidental inclusion of absent reports, command status/action omission, incorrect command queue report counts, failure to update SCM term, and failure to enqueue newly introduced reconstruct/reconcile commands. It does not cover network exceptions or endpoint state transitions after heartbeat failure.

## Test Signals
Signals include captured heartbeat field presence/count assertions, command queue summary counters, term equality, command queue report type/count matching, and command response decoding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/TestHeartbeatEndpointTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java

## Purpose
This package descriptor documents the endpoint state test package as container states endpoint tests.

## Important APIs, Types, And Functions
No executable API is declared.

## Control Flow
There is no runtime control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The file contributes package-level Javadoc for endpoint-state tests.

## Risks And Edge Cases
Risk is limited to package documentation drift.

## Test Signals
No executable test signal is present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/package-info.java -->
