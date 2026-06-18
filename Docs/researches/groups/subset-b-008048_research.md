# Research Group: subset-b-008048

This grouped report covers SCM pipeline, safe mode, security, and server tests from Apache Ozone HDDS SCM. Each section is bounded for deterministic reconciliation into the requested per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateManagerImpl.java

## Purpose
`TestPipelineStateManagerImpl` verifies the persisted and in-memory behavior of `PipelineStateManagerImpl`: pipeline admission, duplicate rejection, query indexes by replication config/state, state transitions, container membership, and removal constraints. It is an integration-style unit test around a real SCM metadata table backed by a temporary `DBStore`, with mocked SCM HA and node-management collaborators.

## Important APIs, Types, and Functions
- `PipelineStateManagerImpl.newBuilder()` wires `SCMDBDefinition.PIPELINES`, a Ratis server, `NodeManager`, and the SCM DB transaction buffer.
- `PipelineStateManager` methods under test include `addPipeline`, `getPipeline`, `getPipelines`, `updatePipelineState`, `addContainerToPipeline`, `removeContainerFromPipeline`, `getContainers`, and `removePipeline`.
- Helper methods `createDummyPipeline`, `openPipeline`, `finalizePipeline`, `deactivatePipeline`, and `removePipeline` centralize construction and state transitions.
- `Pipeline`, `PipelineID`, `ContainerID`, `ReplicationConfig`, `RatisReplicationConfig`, and `HddsProtos.Pipeline` are the main data objects crossing protobuf and domain boundaries.

## Control Flow
Setup creates an isolated SCM configuration and RocksDB store, then builds a fresh state manager for each test. Tests add pipelines as protobuf messages, optionally mutate them through `updatePipelineState`, and then assert query or mutation behavior against the manager. The broadest tests create matrices of RATIS and STAND_ALONE pipelines for every replication factor and every pipeline state, then check that indexed queries return exact counts and matching type/state fields. Cleanup paths finalize and remove generated pipelines.

## State and Persistence Behavior
The test intentionally uses the real pipeline table from `SCMDBDefinition`, so pipeline metadata is persisted through the test DB store and transaction buffer path rather than only held in memory. It confirms duplicate pipeline IDs are rejected, closed pipelines can be removed only after legal state/container conditions, and container membership is associated with the pipeline in the manager state. It also checks idempotent state transitions for already-open and already-closed pipelines.

## Dependencies and Integration Points
Dependencies include `SCMHAManagerStub`, `MockNodeManager`, `DBStoreBuilder`, `SCMTestUtils`, and Ozone replication config/protobuf classes. The integration point of highest importance is the conversion between `Pipeline` domain objects and `HddsProtos.Pipeline` via `getProtobufMessage(ClientVersion.CURRENT_VERSION)`.

## Risks and Edge Cases
The tests cover mismatched replication factor versus node count, duplicate IDs, removed pipeline access, container addition after removal, attempts to remove non-closed/non-empty pipelines, and idempotent finalize/open transitions. A risk not deeply covered is restart recovery: the test uses persistent tables but does not rebuild a second manager from the same DB after writes.

## Test Signals
Strong signals are exact query counts across type/factor/state combinations, assertion of exception messages for invalid operations, and explicit verification that container sets track additions/removals. The tests are sensitive to future enum additions because they iterate all `ReplicationFactor` and `PipelineState` values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateMap.java

## Purpose
`TestPipelineStateMap` validates the lightweight `PipelineStateMap` count indexes for standalone, Ratis, and EC pipelines. It ensures open and closed pipelines are counted independently by exact `ReplicationConfig`.

## Important APIs, Types, and Functions
- `PipelineStateMap.addPipeline`, `updatePipelineState`, and `getPipelineCount` are the focus.
- `MockPipeline.createPipeline`, `createRatisPipeline`, and `createEcPipeline` provide representative pipelines.
- `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `ECReplicationConfig` exercise config equality and index bucketing.

## Control Flow
The test creates three groups of pipelines: standalone, Ratis, and EC. In each group it adds multiple open pipelines and marks one pipeline closed. It then asserts open and closed counts for each replication config, including a zero-count EC config that was never added.

## State and Persistence Behavior
This is in-memory state only. It validates that updates move a pipeline between state buckets without losing replication-config grouping.

## Dependencies and Integration Points
The file integrates with `MockPipeline` helpers and the production `PipelineStateMap` type. It is a focused regression test for indexing behavior used by state managers and pipeline managers.

## Risks and Edge Cases
The main edge case is exact EC replication config matching: EC(3,2) has counts while EC(6,3) returns zero. The test does not cover deletion, duplicate adds, or concurrent updates.

## Test Signals
The assertions provide a compact signal that state transitions update count indexes correctly across all supported replication families represented in SCM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineProvider.java

## Purpose
`TestRatisPipelineProvider` validates Ratis pipeline allocation behavior under node health, pipeline-per-node limits, explicit node lists, exclusions, placement policy selection, and space requirements. It checks both successful pipeline construction and error messages when no suitable nodes are available.

## Important APIs, Types, and Functions
- `RatisPipelineProvider.create(...)`, `createForRead(...)`, and explicit-node overloads are the main APIs.
- `MockRatisPipelineProvider`, `MockNodeManager`, `PipelineStateManagerImpl`, `SCMHAManagerStub`, and the SCM pipeline table provide an SCM-like test environment.
- Config keys include `OZONE_DATANODE_PIPELINE_LIMIT`, `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`, `OZONE_SCM_CONTAINER_SIZE`, and `OZONE_DATANODE_RATIS_VOLUME_FREE_SPACE_MIN`.
- Helpers `assertPipelineProperties`, `createPipelineAndAssertions`, `addPipeline`, and `createContainerReplicas` define reusable expectations.

## Control Flow
Initialization creates a real DB store, a mock node manager with configurable pipeline quota, a state manager, and a mock Ratis provider. Basic tests create factor ONE and THREE pipelines, add them to state and node managers, and assert properties and limited overlap. Other tests saturate selected datanodes with open or closed pipelines, configure placement policy and limits, or inflate required space so pipeline creation must fail.

## State and Persistence Behavior
Pipelines are added to both `PipelineStateManager` and `MockNodeManager` to mirror SCM state and node-to-pipeline engagement. The provider itself produces allocated pipelines unless explicit nodes are supplied, in which case pipelines are open. Per-datanode engagement and state of existing open/closed pipelines directly affect future placement.

## Dependencies and Integration Points
The provider integrates with node status filtering, pipeline placement policy, replication configs, container replica read pipelines, and SCM configuration. Rack-scatter placement is tested by setting the placement implementation class. Space checks depend on container size and Ratis metadata free-space config.

## Risks and Edge Cases
Covered risks include reuse of identical datanode sets, excluded node enforcement, default and explicit per-DN pipeline limits, insufficient data or metadata space, and behavior when only closed-pipeline members remain available. The tests also protect specific exception text, making them sensitive to message changes.

## Test Signals
High-value signals are no full overlap when alternatives exist, exact exception messages for limit exhaustion, and confirmed fallback to closed-pipeline members when open members are saturated. Parameterized limit cases guard both one- and two-pipeline-per-node quota behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSimplePipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSimplePipelineProvider.java

## Purpose
`TestSimplePipelineProvider` verifies standalone pipeline creation, both with provider-selected nodes and with explicitly supplied nodes. It ensures standalone pipelines are immediately open and have node counts matching their replication factor.

## Important APIs, Types, and Functions
- `SimplePipelineProvider.create(StandaloneReplicationConfig)` and `create(config, nodes)` are the core APIs.
- The setup uses `MockNodeManager`, `PipelineStateManagerImpl`, `SCMHAManagerStub`, and the SCM pipeline table.
- `createListOfNodes` builds arbitrary datanode lists for explicit-node creation.

## Control Flow
Each test initializes an SCM-like state manager and provider. The factor test creates THREE and ONE standalone pipelines, persists them into the state manager, and asserts type, replication factor, state, and node count. The explicit-node test bypasses node selection and asserts the same properties.

## State and Persistence Behavior
For provider-selected pipelines, the test adds protobuf pipeline records to `PipelineStateManager`. The provider returns `OPEN` standalone pipelines, unlike Ratis creation paths that often start as `ALLOCATED`.

## Dependencies and Integration Points
The provider depends on `NodeManager` for selecting nodes and on `PipelineStateManager` for awareness of existing pipelines. It integrates with `StandaloneReplicationConfig` and the pipeline protobuf conversion path.

## Risks and Edge Cases
The file covers factors ONE and THREE but not invalid node counts or lack of healthy nodes. It assumes standalone pipelines should not need a later open transition.

## Test Signals
The assertions are straightforward regression signals for standalone pipeline shape and state, especially the difference that standalone pipelines are open immediately.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSimplePipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSortedList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSortedList.java

## Purpose
`TestSortedList` stress-tests the custom `SortedList` collection against a Java `ArrayList` sorted with `Collections.sort`. It verifies insertion ordering, removal behavior, identity-preserving iteration, and duplicate-removal semantics under randomized operations.

## Important APIs, Types, and Functions
- `SortedList.add(element, weight)`, `remove`, `iterator`, `size`, and `isEmpty` are exercised through `List` semantics.
- Nested `Element` implements `Comparable` by weight and unique value while `hashCode` intentionally returns only weight.
- Static helpers `add`, `remove`, `assertLists`, and `assertOrdering` compare `SortedList` to a reference list.

## Control Flow
The main test runs 2,000 random operations. It adds elements 60 percent of the time and removes from either the Java list or `SortedList` otherwise. After every mutation, it asserts both containers have the same size, same ordering, same element containment, and same object identity sequence.

## State and Persistence Behavior
State is in-memory only. The random static `id` and `Random` drive operation variety, and each inserted element has a stable weight/value ordering key.

## Dependencies and Integration Points
The test depends only on JUnit, AssertJ, Java collections, and `SortedList`. It is a low-level utility test for pipeline package internals.

## Risks and Edge Cases
The test catches ordering errors with duplicate weights, stale index removal, and equality/hash collisions because `hashCode` is not unique. Randomness is useful for coverage but can make failures non-reproducible because no seed is fixed.

## Test Signals
Strong signals include bidirectional removal checks and `assertSame` during iteration, which means `SortedList` must preserve the actual element objects, not equivalent replacements.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSortedList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableECContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableECContainerProvider.java

## Purpose
`TestWritableECContainerProvider` validates how `WritableECContainerProvider` chooses or creates writable EC containers and pipelines. It covers capacity limits based on healthy volumes, minimum pipeline counts, exclusion handling, stale container/pipeline cleanup, pipeline closing when no writable container remains, and excluded datanode forwarding.

## Important APIs, Types, and Functions
- `WritableECContainerProvider.getContainer(size, repConfig, owner, ExcludeList)` is the main API.
- `WritableECContainerProviderConfig` controls minimum pipelines and pipeline-per-volume factor.
- `PipelineChoosePolicy` implementations tested are `RandomPipelineChoosePolicy`, `HealthyPipelineChoosePolicy`, and `CapacityPipelineChoosePolicy`.
- `MockPipelineManager`, `MockNodeManager`, mocked `ContainerManager`, `ExcludeList`, `ECReplicationConfig`, and `ContainerInfo` are key collaborators.

## Control Flow
Parameterized tests create the provider for each choose policy. Setup creates a node topology, DB store, HA manager, mock pipeline manager, and mocked container manager whose `getMatchingContainer` creates and registers a container for a pipeline. Tests request containers repeatedly to fill expected pipeline limits, then assert later requests reuse existing containers. Other tests exclude pipelines, containers, or datanodes, simulate pipeline/container lookup failures, and verify provider decisions.

## State and Persistence Behavior
Pipeline and container state is maintained through `MockPipelineManager` and a local `Map<ContainerID, ContainerInfo>`. The provider adds containers to pipelines through the mocked container-manager answer. Tests mutate `usedBytes`, remove containers from pipelines, and assert that exhausted or inconsistent pipelines transition to `CLOSED`.

## Dependencies and Integration Points
The provider integrates with pipeline manager creation, container manager matching and lookup, node healthy-volume counts, topology-aware node manager initialization, and choose-policy selection. It also depends on SCM container size config to determine EC stripe space requirements.

## Risks and Edge Cases
Covered cases include all pipelines excluded, all containers excluded, soft-limit creation when exclusions prevent reuse, creation failure propagation, RocksDB creation failure, missing pipeline/container while reusing, open pipelines with removed containers, closed containers in excluded pipelines, and explicit excluded datanode pass-through. One notable behavior is that pipeline limits count all open pipelines, not only those surviving the current exclude filter.

## Test Signals
The suite gives broad regression coverage across three policies with the same provider contract. High-value signals are distinct-container allocation until the configured limit, reuse after limit, closure of stale pipelines, and Mockito verification that `createPipeline` receives the correct excluded nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableECContainerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableRatisContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableRatisContainerProvider.java

## Purpose
`TestWritableRatisContainerProvider` verifies the simpler Ratis writable-container selection path: prefer a writable container in an existing open pipeline, skip pipelines without matching containers, create a new pipeline/container when necessary, and propagate failures when creation cannot provide a container.

## Important APIs, Types, and Functions
- `WritableRatisContainerProvider.getContainer` is the core API.
- Mocks for `PipelineManager` and `ContainerManager` define existing pipelines, matching-container responses, and pipeline creation.
- Helpers `existingPipelines`, `pipelineHasContainer`, `createNewContainerOnDemand`, and `throwWhenCreatePipeline` encode the test scenarios.

## Control Flow
The tests first set up mocked open pipeline lists for `RatisReplicationConfig(THREE)`. If a pipeline has a matching container, the provider returns it and does not create a pipeline. If no usable container exists, `createPipeline` is expected, followed by a second open-pipeline scan that returns the new container. Failure test makes `createPipeline` throw `SCMException`.

## State and Persistence Behavior
There is no real persistence; state is Mockito stubbing plus an `AtomicLong` for container IDs. Verification of call counts is the main state signal.

## Dependencies and Integration Points
The class integrates with `RandomPipelineChoosePolicy`, `PipelineManager.getPipelines(repConfig, OPEN, emptySet, emptySet)`, `ContainerManager.getMatchingContainer`, and `PipelineManager.createPipeline(repConfig)`.

## Risks and Edge Cases
The repeated test runs 100 times to catch random policy ordering problems when one pipeline lacks a container. Exclude-list behavior is not explored beyond the no-exclusion constant.

## Test Signals
The exact Mockito verifications distinguish reuse from creation: existing-container paths call `getPipelines` once and never create, while creation paths call `getPipelines` twice and create once.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableRatisContainerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestCapacityPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestCapacityPipelineChoosePolicy.java

## Purpose
`TestCapacityPipelineChoosePolicy` validates that capacity-aware pipeline selection favors pipelines whose datanodes have lower used capacity. It constructs a controlled four-datanode scenario where each possible three-node pipeline has a predictable relative score.

## Important APIs, Types, and Functions
- `CapacityPipelineChoosePolicy.init(NodeManager)` and `choosePipeline` are under test.
- `NodeManager.getNodeStat` returns synthetic `SCMNodeMetric` values.
- `MockPipeline.createPipeline` and `MockRatisPipelineProvider.markPipelineHealthy` prepare selectable pipelines.

## Control Flow
The test mocks four datanode metrics with increasing used values. It builds four pipelines, each missing a different datanode. It calls `choosePipeline` 1,000 times and counts selections, then asserts the expected ranking from least-used aggregate membership to most-used aggregate membership.

## State and Persistence Behavior
Selection state is in-memory and probabilistic/weighted. No SCM persistence is involved.

## Dependencies and Integration Points
This test connects pipeline choice to node capacity metrics exposed by `NodeManager`, and to healthy pipeline marking expected by choose policies.

## Risks and Edge Cases
The test validates relative ordering over many runs instead of exact counts, making it robust to weighted randomness while still catching inverted ranking. It does not test null metrics, empty lists, or unhealthy pipelines.

## Test Signals
The ordered selection-count assertions protect the intended policy behavior: the pipeline containing lower-used datanodes should be chosen more frequently.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestCapacityPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestPipelineChoosePolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestPipelineChoosePolicyFactory.java

## Purpose
`TestPipelineChoosePolicyFactory` verifies that SCM loads the correct pipeline choose policy for replicated and EC requests, and falls back to defaults when configured classes are missing or invalid.

## Important APIs, Types, and Functions
- `PipelineChoosePolicyFactory.getPolicy(nodeManager, scmConfig, isEC)` is the main API.
- Defaults `OZONE_SCM_PIPELINE_CHOOSE_POLICY_IMPL_DEFAULT` and `OZONE_SCM_EC_PIPELINE_CHOOSE_POLICY_IMPL_DEFAULT` are asserted.
- Nested `DummyImpl` has an invalid constructor; `DummyGoodImpl` is a valid policy implementation.
- `ScmConfig.setPipelineChoosePolicyName` and `setECPipelineChoosePolicyName` drive configuration.

## Control Flow
Setup loads `ScmConfig` from a default `OzoneConfiguration` and creates a mock node manager. Tests request default policies, configure a valid EC policy, configure invalid constructor classes, and configure nonexistent classes. Assertions compare exact policy classes.

## State and Persistence Behavior
No persistence is involved. State consists of mutable `ScmConfig` policy-class names.

## Dependencies and Integration Points
The test covers reflective class loading and policy initialization against a `NodeManager`. It is important for operational config compatibility because bad class names should not prevent SCM from choosing a default policy.

## Risks and Edge Cases
The class checks invalid constructor and class-not-found fallback, but not class-cast errors or constructor exceptions thrown from a valid signature. It asserts fallback rather than exception for these invalid configurations.

## Test Signals
The exact class identity assertions provide a clear regression signal for default and EC-specific policy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestPipelineChoosePolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestRoundRobinPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestRoundRobinPipelineChoosePolicy.java

## Purpose
`TestRoundRobinPipelineChoosePolicy` validates deterministic round-robin selection across stable and changing pipeline availability lists. It protects the policy's moving index behavior when available pipelines are added or removed.

## Important APIs, Types, and Functions
- `RoundRobinPipelineChoosePolicy.init(NodeManager)` and `choosePipeline` are under test.
- `MockPipeline.createPipeline` and `MockRatisPipelineProvider.markPipelineHealthy` produce four healthy pipelines.
- `verifySelectedCountMap` checks exact per-pipeline selection counts.

## Control Flow
Setup creates four datanodes and four pipelines, each containing three datanodes. The first test calls `choosePipeline` 100 times with all pipelines and expects exact modulo ordering and equal counts. The second test mutates the available-pipeline list from one pipeline to four, then removes one, checking the expected offset and distribution after each phase.

## State and Persistence Behavior
The policy maintains in-memory selection position across calls and across different input lists. No persistent SCM state is touched.

## Dependencies and Integration Points
The test integrates with `PipelineChoosePolicy` interface expectations and mock pipeline health marking used by production policies.

## Risks and Edge Cases
The key risk is incorrect index handling when the candidate list changes. This test covers growing and shrinking lists, but not empty lists or concurrent access.

## Test Signals
Exact expected pipeline identity for every call makes this a strong behavioral lock for deterministic round-robin semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestRoundRobinPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/TestLeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/TestLeaderChoosePolicy.java

## Purpose
`TestLeaderChoosePolicy` verifies leader-election policy loading inside `RatisPipelineProvider`. It confirms the default policy class and the failure behavior for a nonexistent configured policy.

## Important APIs, Types, and Functions
- `RatisPipelineProvider.getLeaderChoosePolicy` is inspected.
- `ScmConfigKeys.OZONE_SCM_PIPELINE_LEADER_CHOOSING_POLICY` configures the policy class.
- `MinLeaderCountChoosePolicy` is the expected default.

## Control Flow
The default test constructs a provider with mocked node manager, state manager, event publisher, and empty SCM context, then asserts the policy class. The invalid-class test sets a bogus class name and expects provider construction to throw `RuntimeException`.

## State and Persistence Behavior
No persistence is used. Configuration controls construction-time policy selection.

## Dependencies and Integration Points
This test binds `RatisPipelineProvider` initialization to leader choose policy configuration and `SCMContext`.

## Risks and Edge Cases
Unlike pipeline choose policy factory tests, invalid leader policy configuration is expected to fail hard. The test does not cover a valid custom implementation.

## Test Signals
The test provides a narrow but important signal that default Ratis leader selection remains min-leader-count based and invalid configuration is not silently ignored.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/TestLeaderChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRuleTest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRuleTest.java

## Purpose
`AbstractContainerSafeModeRuleTest` is a shared test suite for container safe-mode rules. Subclasses provide RATIS or EC-specific rule construction and mocked containers, while this base verifies refresh behavior, container filtering, report processing, duplicate handling, metrics, and validation modes.

## Important APIs, Types, and Functions
- Abstract hooks `getReplicationType`, `createRule`, and `mockContainer` make the suite reusable for `RatisContainerSafeModeRule` and `ECContainerSafeModeRule`.
- `AbstractContainerSafeModeRule.refresh`, `validate`, `process`, `getCurrentContainerThreshold`, `getTotalNumberOfContainers`, `getMinReplica`, and `setValidateBasedOnReportProcessing` are under test.
- Mocks include `ContainerManager`, `ConfigurationSource`, `EventQueue`, `SCMSafeModeManager`, and `SafeModeMetrics`.

## Control Flow
Setup mocks container listings by replication type and deleted state, and configures `getContainer` lookups by ID. Tests create containers in various lifecycle states, construct a rule, call `refresh` or `process` with synthetic node registration reports, and assert thresholds or validation results. Metrics tests capture refresh durations and refresh counts.

## State and Persistence Behavior
The rule's state is in-memory: tracked containers, reported datanodes/replicas, validation mode, and computed threshold. Container manager state is represented by mutable lists. No DB persistence is involved.

## Dependencies and Integration Points
The suite integrates safe-mode rules with `ContainerManager` lifecycle filtering, `SCMDatanodeProtocolServer.NodeRegistrationContainerReport`, datanode IDs, and `SafeModeMetrics`.

## Risks and Edge Cases
Covered risks include deleted container removal on refresh, closed/quasi-closed handling, all-open/all-closed edge cases, duplicate reports from the same report object, skipped refresh when already valid, and validating from report processing rather than manager state. It also verifies min-replica-dependent processing by sending the required number of distinct reports.

## Test Signals
This base class is a high-value cross-rule contract: any subclass failing lifecycle filtering, duplicate suppression, metrics, or validation mode semantics will fail the inherited tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRuleTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestDataNodeSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestDataNodeSafeModeRule.java

## Purpose
`TestDataNodeSafeModeRule` validates the datanode-count safe-mode rule. It checks both report-processing validation and direct `NodeManager` validation against the configured minimum datanode count.

## Important APIs, Types, and Functions
- `DataNodeSafeModeRule.validate`, `setValidateBasedOnReportProcessing`, and event handling for `SCMEvents.NODE_REGISTRATION_CONT_REPORT` are central.
- Config key `HDDS_SCM_SAFEMODE_MIN_DATANODE` sets the threshold.
- `SafeModeMetrics.getCurrentRegisteredDatanodesCount` is verified.

## Control Flow
`setup` creates an `OzoneConfiguration`, real `EventQueue`, mocked `NodeManager`, mocked safe-mode manager, and real metrics. Tests fire node registration reports through the event queue and wait for log output showing registered/required counts. The NodeManager mode test disables report-processing validation and stubs healthy-node lists before calling `validate`.

## State and Persistence Behavior
State is in-memory: a set/count of registered datanodes and metrics gauges. No persistent SCM state is used.

## Dependencies and Integration Points
The rule integrates with SCM event dispatch, datanode registration reports, `NodeManager.getNodes(NodeStatus.inServiceHealthy())`, and safe-mode metrics.

## Risks and Edge Cases
The tests cover zero initial nodes, partial registration below threshold, crossing the threshold, and validation from manager state rather than event history. Duplicate datanode reports are not explicitly tested here.

## Test Signals
The log wait plus metrics count assertion ensures both user-visible status and metrics are updated as registrations arrive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestDataNodeSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestECContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestECContainerSafeModeRule.java

## Purpose
`TestECContainerSafeModeRule` applies the shared `AbstractContainerSafeModeRuleTest` contract to EC containers. It ensures EC-specific minimum replica logic and lifecycle filtering satisfy the same safe-mode expectations.

## Important APIs, Types, and Functions
- Constructs `ECContainerSafeModeRule`.
- Provides `ReplicationType.EC`.
- Mocks `ContainerInfo` with `ECReplicationConfig(3, 2)`, nonzero keys, lifecycle state, and container IDs.

## Control Flow
All concrete test execution is inherited from the abstract base. This subclass only supplies EC rule construction and EC-flavored mocked container metadata.

## State and Persistence Behavior
No persistent state is used. Mocked containers expose EC replication config and lifecycle state to the inherited tests.

## Dependencies and Integration Points
The subclass connects `ECContainerSafeModeRule` to `ContainerManager`, `EventQueue`, and `SCMSafeModeManager` through the inherited fixture.

## Risks and Edge Cases
The inherited tests cover refresh, duplicate reports, state filtering, and report-processing validation. EC-specific variation is the minimum replica value derived from data/parity config.

## Test Signals
This file is a compact but important signal that the generic safe-mode container rule contract is valid for EC replication, not only RATIS.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestECContainerSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestHealthyPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestHealthyPipelineSafeModeRule.java

## Purpose
`TestHealthyPipelineSafeModeRule` validates the safe-mode exit rule requiring enough healthy Ratis/THREE pipelines. It covers no-pipeline behavior, pipeline report events, mixed replication factors, dynamic threshold growth, and unhealthy datanode rejection.

## Important APIs, Types, and Functions
- `HealthyPipelineSafeModeRule.validate`, `getHealthyPipelineThresholdCount`, and `getCurrentHealthyPipelineCount` are key APIs.
- The tests build `PipelineManagerImpl`, `MockRatisPipelineProvider`, `MockNodeManager`, `SCMSafeModeManager`, `SCMMetadataStoreImpl`, and `EventQueue`.
- Config keys include `HDDS_SCM_SAFEMODE_PIPELINE_CREATION`, `HDDS_SCM_SAFEMODE_HEALTHY_PIPELINE_THRESHOLD_PCT`, and `HDDS_SCM_SAFEMODE_MIN_DATANODE`.
- `firePipelineEvent` sends `SCMEvents.OPEN_PIPELINE`.

## Control Flow
Each test creates an SCM-like manager stack, creates pipelines before safe mode starts, opens them, marks them healthy, starts `SCMSafeModeManager`, then inspects the registered rule from `SafeModeRuleFactory`. Pipeline events are fired to advance rule state. The dynamic threshold test opens additional pipelines after initial validation, marks their nodes dead, verifies validation drops, then restores health and re-fires events.

## State and Persistence Behavior
Pipeline metadata is persisted in a temporary SCM metadata store. Rule state tracks reported/healthy pipeline IDs and thresholds. Node health state in `MockNodeManager` is mutated to simulate dead and recovered datanodes.

## Dependencies and Integration Points
The rule integrates pipeline manager state, open-pipeline events, node manager health, safe-mode manager lifecycle, and `SafeModeRuleFactory` global registration.

## Risks and Edge Cases
Covered edges include zero pipelines immediately satisfying the rule, ignoring Ratis/ONE pipelines for the Ratis/THREE threshold, requiring event reports before validation, increasing thresholds when more pipelines appear, and logging/rejecting pipelines with unhealthy or unregistered nodes. The tests manually stop metadata stores but do not always close pipeline managers.

## Test Signals
Strong signals include `GenericTestUtils.waitFor` on validation, explicit threshold-count assertions, and log capture when a pipeline is ignored due to bad datanode health.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestHealthyPipelineSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestOneReplicaPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestOneReplicaPipelineSafeModeRule.java

## Purpose
`TestOneReplicaPipelineSafeModeRule` verifies the safe-mode rule requiring enough Ratis/THREE pipelines to have at least one datanode report. It covers pure factor-THREE pipelines, mixed factor-ONE and factor-THREE pipelines, and direct validation without report processing.

## Important APIs, Types, and Functions
- `OneReplicaPipelineSafeModeRule.validate`, `getReportedPipelineIDSet`, `getCurrentReportedPipelineCount`, and `setValidateBasedOnReportProcessing` are central.
- `PipelineManagerImpl`, `MockRatisPipelineProvider`, `MockNodeManager`, `SCMSafeModeManager`, and `SafeModeRuleFactory` provide the SCM context.
- `firePipelineEvent` builds `PipelineReportsProto` per datanode and fires `SCMEvents.PIPELINE_REPORT`.

## Control Flow
Setup creates requested numbers of Ratis/THREE and Ratis/ONE pipelines before starting safe mode. Tests fire reports for all but one factor-THREE pipeline, verify the rule remains false and logs reported counts, then fire the final report and wait for validation. Mixed tests prove factor-ONE reports do not satisfy the factor-THREE rule. The non-report-processing test uses mocks to make a pipeline first return an empty node set and then a non-empty node set.

## State and Persistence Behavior
Pipelines are stored in a temporary SCM metadata store through `PipelineManagerImpl`. Rule state tracks reported pipeline IDs. The event helper derives datanode-to-pipeline membership from `MockNodeManager` maps.

## Dependencies and Integration Points
The rule integrates with datanode heartbeat pipeline reports, pipeline manager queries by replication config and state, node-to-pipeline maps, and safe-mode manager metrics/logging.

## Risks and Edge Cases
Key edge cases include ignoring factor-ONE pipelines, threshold ceil behavior for 90 percent of seven pipelines, pipeline-not-found during report construction, and direct manager-state validation when report processing is disabled.

## Test Signals
Log-captured reported counts and final `waitFor(rule.validate())` provide strong evidence that only qualifying factor-THREE pipeline reports advance the rule.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestOneReplicaPipelineSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestRatisContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestRatisContainerSafeModeRule.java

## Purpose
`TestRatisContainerSafeModeRule` applies the shared container safe-mode rule contract to Ratis containers. It verifies that Ratis replication uses the generic container safe-mode behavior with `RatisReplicationConfig(THREE)`.

## Important APIs, Types, and Functions
- Constructs `RatisContainerSafeModeRule`.
- Provides `ReplicationType.RATIS`.
- Mocks `ContainerInfo` with `RatisReplicationConfig.getInstance(THREE)`, nonzero keys, lifecycle state, and IDs.

## Control Flow
All test behavior is inherited from `AbstractContainerSafeModeRuleTest`. This subclass supplies Ratis-specific rule creation and mock container metadata.

## State and Persistence Behavior
State is in-memory through mocks and inherited rule internals. No DB is used.

## Dependencies and Integration Points
The subclass connects the Ratis rule to `ContainerManager`, `EventQueue`, `SCMSafeModeManager`, and safe-mode metrics in the inherited fixture.

## Risks and Edge Cases
The inherited suite covers lifecycle filtering, refresh, duplicate reports, min-replica processing, and validation mode. The Ratis-specific risk is ensuring the min-replica and config assumptions match factor THREE.

## Test Signals
The file guarantees the abstract safe-mode container contract is continuously exercised for the primary Ratis replication path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestRatisContainerSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeManager.java

## Purpose
`TestSCMSafeModeManager` is the main integration test suite for SCM safe mode. It verifies safe-mode entry/exit, container thresholds for Ratis and EC, datanode prechecks, pipeline rules, state-machine readiness, invalid threshold configuration, safe-mode disabling, pipeline creation gating, metrics, rule status text, and periodic logging shutdown.

## Important APIs, Types, and Functions
- `SCMSafeModeManager.start`, `getInSafeMode`, `forceExitSafeMode`, `getPreCheckComplete`, `validateSafeModeExitRules`, `getRuleStatus`, and `getSafeModeMetrics` are central.
- Rule classes retrieved through `SafeModeRuleFactory` include `RatisContainerSafeModeRule`, `ECContainerSafeModeRule`, `HealthyPipelineSafeModeRule`, `OneReplicaPipelineSafeModeRule`, and `StateMachineReadyRule`.
- Helpers `testContainerThreshold`, `testECContainerThreshold`, `firePipelineEvent`, `checkHealthy`, and `checkOpen` simulate SCM events.
- The fixture uses `SCMMetadataStoreImpl`, `PipelineManagerImpl`, `MockNodeManager`, `MockRatisPipelineProvider`, `ContainerManagerImpl`, `EventQueue`, and `SCMContext`.

## Control Flow
Setup creates common config with safe-mode pipeline creation disabled and a temporary metadata store. Tests build container lists, set lifecycle state/key counts, configure mocked or real container managers, start the safe-mode manager, fire node-registration/container-registration/pipeline-report events, and wait for metrics or state transitions. Parameterized tests vary container counts, datanode counts, pipeline counts, threshold percentages, and EC data/parity combinations.

## State and Persistence Behavior
Some tests use mocked container managers with in-memory lists; EC tests persist containers into the metadata table and use `ContainerManagerImpl`. Pipeline tests persist pipeline records through `PipelineManagerImpl`. Safe-mode manager state includes current safe-mode flag, precheck completion, validated rules, metrics gauges, periodic logger task, and thresholds derived from config and current SCM state.

## Dependencies and Integration Points
This suite exercises integration among SCM event queue, node manager, pipeline manager, container manager, Ratis HA stubs, SCM context/state machine readiness, metrics, and `SafeModeRuleFactory`. It also checks server-facing status text used in logs and rule status maps.

## Risks and Edge Cases
Covered risks include zero containers, empty and non-empty closed containers, open containers excluded from threshold, empty closed containers excluded, EC requiring data-block-number reports, invalid threshold percentages outside [0,1], safe mode disabled by config, no datanode requirement, precheck gating before pipeline creation, force-exit and normal-exit periodic logging cleanup, and leader state-machine readiness. The tests are timing-sensitive due to event processing and periodic logging waits.

## Test Signals
The strongest signals are end-to-end safe-mode exit waits, exact metrics threshold/current values, rule status substring checks, and verification that final logs show `OUT_OF_SAFE_MODE` and stopped periodic logging. Parameterized pipeline threshold tests protect interactions between healthy-pipeline and one-replica-pipeline rules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeRuleFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeRuleFactory.java

## Purpose
`TestSafeModeRuleFactory` validates initialization and loaded-rule counts for the singleton `SafeModeRuleFactory`. It also ensures accessing the factory before initialization is illegal.

## Important APIs, Types, and Functions
- `SafeModeRuleFactory.initialize`, `getInstance`, `addSafeModeManager`, `getSafeModeRules`, and `getPreCheckRules` are under test.
- Reflection resets the private static `instance` field for the illegal-state test.
- `initializeSafeModeRuleFactory` supplies mocked `SCMSafeModeManager`, pipeline/container/node managers, and a real event queue.

## Control Flow
The first test clears the singleton and asserts `getInstance` throws. The loaded-rule tests initialize the factory, attach a safe-mode manager, and assert hardcoded counts: five safe-mode rules and one precheck rule.

## State and Persistence Behavior
State is singleton/global JVM state only. No persistence is used.

## Dependencies and Integration Points
The factory depends on configuration, SCM context, event queue, pipeline manager, container manager, node manager, and safe-mode metrics. This file is sensitive to factory initialization order across tests.

## Risks and Edge Cases
The test explicitly handles prior initialization by resetting the singleton. Hardcoded rule counts are brittle but intentionally document current factory behavior until rules are loaded differently.

## Test Signals
Failures signal either unexpected rule-set changes or unsafe singleton access before initialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeRuleFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/package-info.java

## Purpose
`package-info.java` provides package-level documentation for `org.apache.hadoop.hdds.scm.safemode` test classes. It labels the package as SCM safe mode tests.

## Important APIs, Types, and Functions
No executable APIs, types, or functions are declared. The only functional content is the package declaration.

## Control Flow
There is no control flow.

## State and Persistence Behavior
There is no state or persistence behavior.

## Dependencies and Integration Points
The file integrates with Java package documentation tooling and keeps the safe-mode test package documented.

## Risks and Edge Cases
The only practical risk is stale or too-generic package documentation if the package scope changes.

## Test Signals
No test signal is provided directly; it supports documentation and package metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/security/TestRootCARotationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/security/TestRootCARotationManager.java

## Purpose
`TestRootCARotationManager` validates root CA rotation scheduling, configuration validation, immediate versus scheduled rotation, leader-status reactions, and post-processing cleanup through stateful service storage.

## Important APIs, Types, and Functions
- `RootCARotationManager` construction, `start`, `stop`, `notifyStatusChanged`, and `setRootCARotationHandler` are exercised.
- Config keys include `HDDS_X509_CA_ROTATION_ENABLED`, `HDDS_X509_CA_ROTATION_CHECK_INTERNAL`, `HDDS_X509_CA_ROTATION_TIME_OF_DAY`, `HDDS_X509_RENEW_GRACE_DURATION`, `HDDS_X509_CA_ROTATION_ACK_TIMEOUT`, `HDDS_X509_EXPIRED_CERTIFICATE_CHECK_INTERVAL`, and `HDDS_X509_ROOTCA_CERTIFICATE_POLLING_INTERVAL`.
- `SCMCertificateClient`, `CertificateCodec`, `SelfSignedCertificate`, `StatefulServiceStateManager`, and `RootCARotationHandlerImpl` are important collaborators.
- `generateX509Cert` creates test CA certificates.

## Control Flow
Setup builds security configuration in a temp metadata directory, creates an SCM certificate client, and mocks `StorageContainerManager`, HA manager, sequence generator, security protocol server, SCM context, handler, and stateful service manager. Property tests construct managers with invalid and valid configs. Rotation tests create short-lived CA certs, set schedule times, start the manager, notify status changes, and capture logs to confirm rotation. Post-processing test simulates persisted rotation state, toggles leader status, and waits for post-processing logs and state deletion.

## State and Persistence Behavior
The test uses real certificate files under the temp security directory for one post-processing path and mocked stateful configuration storage for persisted rotation metadata. Manager state includes scheduled monitor task, post-processing flag, leader-active behavior, and root certificate server setup. The certificate client stores current CA certificate in memory.

## Dependencies and Integration Points
This test integrates SCM security, certificate codec, SCM HA/Ratis access, service manager, stateful service config, sequence IDs, and root certificate serving. It depends on log messages to observe asynchronous scheduler behavior.

## Risks and Edge Cases
Covered risks include invalid duration parsing, check interval longer than grace period, invalid time-of-day format, disabled auto-rotation ignoring invalid values, immediate rotation when scheduled time is too late for the grace window, scheduled rotation at a future time, leader change disabling monitor tasks, and deleting stateful config after post-processing completes.

## Test Signals
Strong signals are expected exceptions for bad config, counted log occurrences for a single scheduled rotation, immediate-rotation log checks, and verification that `deleteConfiguration` is called once after post-processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/security/TestRootCARotationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMBlockProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMBlockProtocolServer.java

## Purpose
`TestSCMBlockProtocolServer` verifies block-protocol datanode sorting relative to a client and allocation-time ordering of pipeline nodes. It focuses on network topology awareness for both datanode clients and edge/non-datanode clients.

## Important APIs, Types, and Functions
- `SCMBlockProtocolServer.sortDatanodes` and `allocateBlock` are under test.
- `ScmBlockLocationProtocolServerSideTranslatorPB.sortDatanodes` tests the protobuf service path.
- Inner `BlockManagerStub.allocateBlock` creates random open Ratis/THREE pipelines for allocation tests.
- Helpers `getNetworkNames`, `nodeAddress`, and `assertRackOrder` encapsulate topology assertions.

## Control Flow
Setup creates an SCM with static rack mapping for ten datanodes and two edge nodes, starts SCM, exits safe mode, registers datanodes, and captures the block protocol server and translator. Sorting tests call the server for each datanode client and each edge node. Additional test cases cover illegal client addresses, unknown requested nodes, and all-unknown requested nodes. Allocation test requests multiple blocks with a client machine and asserts any client-local datanode appears first and same-rack nodes are ordered before other-rack nodes.

## State and Persistence Behavior
SCM is a real test instance with temp metadata, but the block manager is a stub. Node registration populates SCM node manager topology state. Allocated blocks are generated on demand and not persisted by the stub.

## Dependencies and Integration Points
The test integrates SCM startup, static network topology mapping, node manager registration, block protocol server, protobuf translator, and block manager allocation. It uses `ClientVersion.CURRENT_VERSION` for the translator call.

## Risks and Edge Cases
Covered edge cases include client specified by IP/hostname setting, non-datanode clients that still have topology mapping, illegal client identifiers, unknown node network names mixed with known ones, and all unknown nodes returning an empty response. Allocation ordering is checked without assuming every pipeline contains the client datanode.

## Test Signals
The rack-order assertions protect locality behavior: client node first when present, same-rack nodes before cross-rack nodes, and unknown nodes filtered from service responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMBlockProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMCertStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMCertStore.java

## Purpose
`TestSCMCertStore` validates SCM certificate-store listing and expired-certificate removal. It ensures valid certificates can be stored and listed by role, and expired entries are removed while non-expired entries remain.

## Important APIs, Types, and Functions
- `SCMCertStore.Builder`, `storeValidCertificate`, `listCertificate`, and `removeAllExpiredCertificates` are tested.
- `SCMMetadataStoreImpl` provides the backing metadata store.
- A mocked `SCMRatisServer` returns the underlying invoker implementation to bypass HA proxying.
- `generateX509Cert` and `CertificateTestUtils.createSelfSignedCert` create certificates.

## Control Flow
Setup creates a temp metadata directory, security config, RSA key pair, SCM metadata store, and SCM cert store. Listing test stores SCM, OM, and datanode certificates, then checks list sizes. Expiration test stores expired and non-expired SCM/non-SCM certs, checks list sizes before cleanup, runs removal, and checks counts after cleanup.

## State and Persistence Behavior
Certificates are persisted in SCM metadata tables through `SCMCertStore`. Key directory creation mirrors expected security layout. The test closes the metadata store after each run.

## Dependencies and Integration Points
The file integrates certificate generation, SCM metadata, Ratis invoker proxying, and node-type role filtering. It documents current behavior where listing OM certs returns all valid certs, not only OM.

## Risks and Edge Cases
Covered risks include multiple certs with increasing counts, role-specific SCM listing, current broad OM/DN listing behavior, and expiration cleanup across SCM and non-SCM certificates. Pagination beyond a small limit is not tested.

## Test Signals
The list-size checks before and after cleanup provide a direct regression signal for certificate persistence and expired removal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMCertStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMClientProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMClientProtocolServer.java

## Purpose
`TestSCMClientProtocolServer` validates selected SCM client protocol behavior: SCM decommission error handling, read-only admin authorization, container listing compatibility, container count lookup, and pagination ordering without duplicates.

## Important APIs, Types, and Functions
- `SCMClientProtocolServer.listContainer`, `getContainerCount`, and access through `StorageContainerLocationProtocolServerSideTranslatorPB.decommissionScm` are tested.
- `StorageContainerManager.checkAdminAccess` is exercised through the real SCM instance.
- Helpers `mockStorageContainerManager`, `newContainerWithLastUsedTime`, and `newContainerInfoForTest` provide container-manager stubs.

## Control Flow
Setup starts a real test SCM with read-only administrator config and exits safe mode. Decommission test calls the translator with the current SCM ID and asserts the response contains "Cannot remove current leader." Admin test creates a UGI for the read-only admin and verifies read access succeeds but write access throws. Listing/count tests use a standalone `SCMClientProtocolServer` with mocked SCM/container manager. Pagination test creates out-of-order container IDs with increasing last-used times and repeatedly calls `listContainer` using the last returned ID plus one as the next start.

## State and Persistence Behavior
The real SCM setup uses temp metadata and is stopped after tests. Mocked container listing state is in-memory. Pagination behavior depends on sorted container ID output, not insertion order.

## Dependencies and Integration Points
The class integrates client protocol server, protobuf translator, SCM HA context, admin ACL configuration, UGI, reconfiguration handler, container manager, and legacy list-container API accepting replication factor.

## Risks and Edge Cases
Covered risks include attempting to decommission the current leader, read-only admin incorrectly receiving write authority, legacy list-container compatibility, count lookup by lifecycle state, and duplicate/skip bugs in ID-based pagination. It does not test remote authorization contexts or multiple SCM peers.

## Test Signals
The pagination test is a strong regression signal: expected IDs `[5, 10, 100]` and uniqueness ensure `listContainer` sorts and advances by container ID correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMClientProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMContainerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMContainerMetrics.java

## Purpose
`TestSCMContainerMetrics` verifies that `SCMContainerMetrics` exports Hadoop metrics gauges for container lifecycle states and total container count.

## Important APIs, Types, and Functions
- `SCMContainerMetrics.getMetrics` is under test.
- `SCMMXBean.getContainerStateCount` supplies lifecycle-state counts.
- `MetricsCollector`, `MetricsRecordBuilder`, `MetricsInfo`, and `Interns.info` are mocked/verified.

## Control Flow
The test stubs a state-count map for OPEN, CLOSING, QUASI_CLOSED, CLOSED, DELETING, DELETED, and RECOVERING. It calls `getMetrics` and verifies `addGauge` calls for each exported metric except RECOVERING, plus `TotalContainers`.

## State and Persistence Behavior
There is no persistence. Metrics are generated from an in-memory map returned by the MXBean.

## Dependencies and Integration Points
The class integrates the SCM MXBean with Hadoop Metrics2 collection. Metric names and descriptions are part of the observable contract.

## Risks and Edge Cases
The test confirms total count includes all states in the map, including RECOVERING, even though no explicit recovering gauge is verified. It would catch metric renames, missing gauges, or total miscalculation.

## Test Signals
Exact `verify(...).addGauge(...)` assertions lock down emitted metric names, descriptions, and values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMContainerMetrics.java -->
