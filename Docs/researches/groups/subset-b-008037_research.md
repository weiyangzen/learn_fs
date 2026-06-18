# subset-b-008037 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java

Purpose: `PipelineStateMap` is the non-thread-safe in-memory index behind SCM pipeline state. It stores `PipelineID -> Pipeline`, `PipelineID -> sorted ContainerID set`, and an optimized `ReplicationConfig -> open pipeline list` cache used by common allocation queries.

Important APIs and types: Core methods are `addPipeline`, `addContainerToPipeline`, `addContainerToPipelineSCMStart`, `getPipeline`, `getPipelines` overloads, `getPipelineCount`, `getContainers`, `removePipeline`, `removeContainerFromPipeline`, and `updatePipelineState`. It depends on `Pipeline`, `PipelineID`, `PipelineState`, `ReplicationConfig`, `ContainerID`, `DatanodeDetails`, and the pipeline exceptions.

Control flow: Adding a pipeline validates node count against required replication nodes, rejects duplicate IDs, creates an empty container set, and indexes open pipelines by replication config. Query methods either read the open-pipeline cache or scan all pipelines and then filter by replication config, state, excluded datanodes, and excluded pipeline IDs. State updates replace the immutable pipeline object via builder and maintain the open-pipeline cache.

State and persistence behavior: This class persists nothing itself; durability is supplied by higher-level managers. Its invariant is that every pipeline has both a `pipelineMap` entry and a `pipeline2container` entry. The SCM-start container-add path deliberately tolerates open containers attached to already closed pipelines because SCM DB flush ordering can leave that state after restart.

Dependencies and integration points: `PipelineStateManagerImpl` owns synchronization and persistence around this map. Container allocation, close pipeline handling, safe mode rules, and pipeline reports rely on its state-specific queries and container membership. The open-pipeline cache is a performance-sensitive integration point.

Risks: Callers must hold appropriate locks because the map and cached lists are thread-unsafe. Removing a pipeline requires closed state but does not check whether containers remain. Any equality/hash behavior change on `Pipeline` could affect removal from `query2OpenPipelines`.

Test signals: Useful tests assert duplicate detection, state-cache updates across ALLOCATED/OPEN/CLOSED transitions, exclude filtering, SCM restart container attachment, closed-pipeline removal rejection, and returned collection copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java

Purpose: `RatisPipelineProvider` creates and closes Ratis replication pipelines for SCM. It selects datanodes, enforces configured pipeline limits, chooses an optional suggested leader, and publishes create/close pipeline commands to datanodes.

Important APIs and types: The provider extends `PipelineProvider<RatisReplicationConfig>` and implements `create` overloads, `createForRead`, and `close`. It uses `NodeManager`, `PipelineStateManager`, `PlacementPolicy`, `PipelinePlacementPolicyFactory`, `LeaderChoosePolicyFactory`, `SCMContext`, `CreatePipelineCommand`, `ClosePipelineCommand`, and `SCMEvents.DATANODE_COMMAND`.

Control flow: `create` first checks global or per-datanode Ratis pipeline limits for factor THREE. Factor ONE chooses unused nodes directly, while factor THREE excludes datanodes already at their pipeline engagement limit before calling placement. It then chooses a suggested leader, builds an ALLOCATED pipeline, stamps the SCM leader term on a `CreatePipelineCommand`, and fires that command to each datanode. `close` similarly sends a term-stamped `ClosePipelineCommand` to all pipeline members.

State and persistence behavior: This class builds `Pipeline` objects but does not add them to state or persist them; the manager that called it owns that. It reads pipeline and node state to enforce limits, uses configuration for container and Ratis-volume free-space thresholds, and embeds the current SCM term in datanode commands.

Dependencies and integration points: It integrates placement policy, node health, HA context, event publishing, and leader-selection policy. `WritableRatisContainerProvider` depends on the manager path that uses this provider to create a pipeline before allocating containers.

Risks: Pipeline limit calculations combine active, closed, factor ONE, and healthy node counts and can block creation if counters are stale. The method mutates the `excludedNodes` list when adding engagement exclusions, which is risky if callers pass a shared mutable list. Command publication assumes SCM is leader and the event queue will deliver commands reliably.

Test signals: Tests should cover factor ONE and THREE placement, limit enforcement, leader policy selection, exclusion of engaged datanodes, event publication counts and command terms, and close command fan-out.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java

Purpose: `RatisPipelineUtils` currently contains one package-private helper that finds other open or non-closed Ratis factor THREE pipelines sharing the same datanode set as a supplied pipeline.

Important APIs and types: `checkPipelineContainSameDatanodes(PipelineStateManager, Pipeline)` queries `RatisReplicationConfig.getInstance(ReplicationFactor.THREE)`, filters out the input pipeline ID, ignores CLOSED pipelines, and uses `Pipeline.sameDatanodes`.

Control flow: The method reads all Ratis THREE pipelines from the state manager, streams through them, applies the ID, state, and datanode-set filters, and returns a collected list.

State and persistence behavior: There is no state or persistence here. The function is a derived query over the pipeline state manager's current view.

Dependencies and integration points: It is used by pipeline management logic that detects duplicate datanode groupings and increments related metrics. It depends on `Pipeline.sameDatanodes` rather than list order.

Risks: It only checks Ratis factor THREE, so future replication configs need separate logic. It treats ALLOCATED and OPEN duplicates as relevant but skips only CLOSED; stale non-closed pipelines can therefore suppress or flag creation.

Test signals: Tests should verify same datanodes in different order are matched, self is excluded, CLOSED matches are skipped, and non-Ratis or non-THREE pipelines are ignored.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java

Purpose: `SCMPipelineMetrics` exposes SCM pipeline-manager counters and latency metrics through Hadoop Metrics2. It tracks pipeline allocation, creation, destruction, report handling, duplicate-datanode-pipeline detection, per-pipeline block allocations, and creation latency.

Important APIs and types: Static lifecycle methods are `create` and `unRegister`. Runtime methods include `createPerPipelineMetrics`, `removePipelineMetrics`, `incNumBlocksAllocated`, the `incNumPipeline...` counters, `updatePipelineCreationLatencyNs`, `getTotalNumBlocksAllocated`, and `getMetrics`. It uses `MetricsRegistry`, `MutableCounterLong`, `MutableRate`, `DefaultMetricsSystem`, and `Interns.info`.

Control flow: `create` registers a singleton metrics source. `getMetrics` snapshots global counters and every per-pipeline counter into the collector. Per-pipeline counters are created with names that encode pipeline type, replication config, and pipeline ID.

State and persistence behavior: Metrics are process-local and not persisted. `numBlocksAllocated` is a `ConcurrentHashMap`, so per-pipeline metric mutation can proceed concurrently with snapshots and pipeline cleanup.

Dependencies and integration points: Pipeline manager code calls these methods during lifecycle transitions, report processing, and block allocation. Metrics names are externally visible to monitoring systems.

Risks: Singleton lifecycle means tests must unregister to avoid leaked state. Per-pipeline metric cardinality can grow if removal is missed. `incNumBlocksAllocated` silently ignores missing pipeline metrics, which avoids failures but can hide lifecycle ordering bugs.

Test signals: Metrics tests should assert singleton reuse, source unregister, counter increments, per-pipeline metric names, total block allocation sums, latency updates, and removal of closed pipeline counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java

Purpose: `SimplePipelineProvider` creates standalone pipelines. Unlike Ratis, standalone pipelines are immediately OPEN and do not require datanode create or close commands.

Important APIs and types: It extends `PipelineProvider<StandaloneReplicationConfig>` and implements `create` overloads, `createForRead`, and an empty `close`. It uses `pickNodesNotUsed`, `InsufficientDatanodesException`, `PipelineID.randomId`, and `PipelineState.OPEN`.

Control flow: The main `create` gets available unused nodes, verifies there are enough for the requested replication factor, shuffles them, and builds an OPEN pipeline with the first required nodes. The read path creates a pipeline from the datanodes present in replicas.

State and persistence behavior: No state is persisted by this provider. It returns pipeline objects to the pipeline manager, which owns indexing and persistence.

Dependencies and integration points: It integrates with `NodeManager` through the base provider's node picking and is routed through `PipelineFactory` and writable-container allocation for standalone replication.

Risks: The `excludedNodes` and `favoredNodes` parameters are ignored in the main create path. `close` is intentionally a no-op, so callers must not expect datanode cleanup commands for standalone pipelines.

Test signals: Tests should cover insufficient datanode exceptions, node count and state on created pipelines, random selection not exceeding requested factor, read pipeline construction from replicas, and no-op close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java

Purpose: `SortedList` is a package-private list-like container optimized for many elements with comparatively few integer weights. It stores elements in a `TreeMap<Integer, List<E>>` so iteration and indexed access are ordered by weight.

Important APIs and types: Supported operations are `size`, `isEmpty`, `add(E, int weight)`, `get`, `remove(int)`, `contains`, `remove(Object)`, `removeAll`, `clear`, `iterator`, and `toString`. Most mutating and array/list-view methods from `List` throw `UnsupportedOperationException`.

Control flow: Adding an element appends it to the bucket for its weight. `get` and indexed `remove` walk buckets in ascending weight order while subtracting bucket sizes. Object removal scans buckets, removes empty buckets, and decrements the element count only when removal succeeds.

State and persistence behavior: State is in-memory only: a sorted bucket map plus a separate `numElements` counter. The class is explicitly not thread-safe.

Dependencies and integration points: It is a low-level utility for pipeline placement code where datanodes or candidates are weighted by current pipeline counts. Its `Class<E>` constructor argument protects `contains/remove` from matching unrelated object types.

Risks: It implements `List` but many standard operations are unsupported, so generic callers can fail at runtime. The custom iterator's `hasNext` only checks the current bucket iterator, so consumers must rely on standard next progression and avoid structural mutation during iteration. Empty-list handling for unsupported or index methods must be tested.

Test signals: Tests should verify sorted-by-weight iteration, stable bucket insertion order for equal weights, indexed get/remove, object removal and bucket cleanup, removeAll counts, type mismatch contains behavior, and expected unsupported operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java

Purpose: `WritableContainerFactory` is the replication-type router for block allocation. It returns a writable `ContainerInfo` by delegating to Ratis/standalone or EC providers based on the requested `ReplicationConfig`.

Important APIs and types: The constructor wires providers from `StorageContainerManager`: `WritableRatisContainerProvider` for RATIS and STAND_ALONE, and `WritableECContainerProvider` for EC. `getContainer(long, ReplicationConfig, String, ExcludeList)` is the public dispatch method.

Control flow: Construction reads SCM configuration, creates the EC provider config object, calculates configured container size, and registers the EC config with the reconfiguration handler. `getContainer` switches on replication type and casts EC configs to `ECReplicationConfig`.

State and persistence behavior: The factory holds provider instances only. It does not persist containers or pipelines; delegated managers do. EC provider configuration is reconfigurable after registration.

Dependencies and integration points: It integrates block allocation with `PipelineManager`, `ContainerManager`, `NodeManager`, pipeline choose policies, `StorageContainerManager`, and dynamic reconfiguration.

Risks: STAND_ALONE currently shares the Ratis writable provider path, which is intentional but easy to misread. Invalid replication types fail with `IOException`. EC requests rely on the runtime type of `repConfig`.

Test signals: Tests should assert routing by replication type, invalid-type errors, EC config registration, configured container size propagation, and exclude-list forwarding to providers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java

Purpose: `WritableContainerProvider` defines the provider contract used by `WritableContainerFactory` to obtain a writable container for a new block.

Important APIs and types: Its single method is `getContainer(long size, T repConfig, String owner, ExcludeList excludeList)`. Implementations return an open `ContainerInfo` that can fit the requested block or throw `IOException`.

Control flow: The interface leaves selection, pipeline creation, container matching, and exclusion handling to implementations such as `WritableRatisContainerProvider` and `WritableECContainerProvider`.

State and persistence behavior: No state exists in the interface. Implementations mediate persisted state through `PipelineManager` and `ContainerManager`.

Dependencies and integration points: It is the abstraction between SCM block allocation and replication-specific writable container selection. It carries the owner and exclusion contract used by retry and placement paths.

Risks: The contract says returned containers must be open and large enough, but that is not enforceable at compile time. Implementations must consistently honor excluded datanodes, pipelines, and containers.

Test signals: Shared provider tests should validate capacity checks, owner matching, exclusion handling, exception behavior when no container can be allocated, and interaction with pipeline creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java

Purpose: `WritableECContainerProvider` selects or creates writable containers for erasure-coded block groups. It maintains an open EC pipeline pool sized by configured minimums and healthy volume count, and it assumes one open container per EC pipeline.

Important APIs and types: Public API is `getContainer`. Key helpers are `getMaximumPipelines`, `allocateContainer`, `pipelineIsExcluded`, `getContainerFromPipeline`, `containerHasSpace`, and nested `WritableECContainerProviderConfig`. It uses `NodeManager`, `PipelineManager`, `ContainerManager`, `PipelineChoosePolicy`, `ECReplicationConfig`, and `ExcludeList`.

Control flow: `getContainer` first calculates the maximum open pipelines. Under provider synchronization, it tries to allocate a fresh pipeline/container if the current open count is below the limit. If not, it chooses among existing open pipelines using the policy, synchronizes per pipeline ID, fetches the associated container, closes pipelines with no suitable container or insufficient space, skips excluded resources, updates last-used time, and returns. If all existing pipelines fail, it may raise the limit up to healthy node count for a final allocation attempt.

State and persistence behavior: The provider itself persists nothing. Pipeline and container creation, opening, closing, and lookup are delegated to SCM managers. Reconfigurable config state includes minimum EC pipelines and pipeline-per-volume factor; validation normalizes negative factors back to default.

Dependencies and integration points: It depends on accurate healthy volume counts, pipeline state, container used bytes, and container size configuration. It integrates with the EC pipeline choose policy and SCM reconfiguration handler.

Risks: Open count is updated locally after closing unsuitable pipelines and can diverge from concurrent manager state. Synchronizing on `pipeline.getId()` only coordinates callers that use the same ID object equality path. A null container after new pipeline creation is treated defensively as an error even though placement should have checked space.

Test signals: Tests should cover minimum and volume-derived limits, negative factor validation, fresh allocation, existing pipeline reuse, exclusion of container/pipeline/datanode, close-on-full or missing container, last-used updates, and final limit expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java

Purpose: `WritableRatisContainerProvider` selects a writable container from open Ratis or standalone pipelines and creates or waits for a pipeline if none can currently serve the request.

Important APIs and types: Public API is `getContainer`. Helpers include private `getContainer`, `findPipelinesByState`, and `selectContainer`. It uses `PipelineManager`, `ContainerManager`, `PipelineChoosePolicy`, `PipelineRequestInformation`, `ReplicationConfig`, `ExcludeList`, and `SCMException`.

Control flow: The provider first tries to find an OPEN pipeline and matching container under the pipeline manager read lock. If none is found, it asks the pipeline manager to create a pipeline and waits for it to become ready. If creation fails with `SCMException`, it looks for ALLOCATED pipelines and waits for one of them to open. Finally it retries container selection and throws an `IOException` with the recorded failure reason if no container can be allocated.

State and persistence behavior: This class holds no durable state. The read lock protects the selection of open pipelines and matching containers against concurrent pipeline updates. Persistent pipeline/container state is held by the managers.

Dependencies and integration points: It is the normal Ratis and standalone block-allocation path from `WritableContainerFactory`. It relies on the choose policy to order candidate pipelines and on `ContainerManager.getMatchingContainer` for owner, size, and excluded container filtering.

Risks: If an exclude list filters all pipelines, the provider intentionally retries without exclusions, which can conflict with caller expectations after retries. Available pipeline lists are mutated while selecting. Failures during wait for allocated pipelines can hide the original creation failure in the final reason string.

Test signals: Tests should cover reuse of open pipelines, pipeline creation and wait paths, fallback to ALLOCATED pipelines, exclusion fallback behavior, read-lock acquisition, policy-driven selection, and final exception messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java

Purpose: `CapacityPipelineChoosePolicy` biases writable-container allocation toward less utilized pipelines using the "power of two choices" strategy: choose two healthy random candidates and pick the one with lower node utilization.

Important APIs and types: It implements `PipelineChoosePolicy` with `init`, `choosePipeline`, and `choosePipelineIndex`. It uses `NodeManager.getNodeStat`, `SCMNodeMetric`, and an inner `CapacityPipelineComparator`.

Control flow: `choosePipeline` asks `HealthyPipelineChoosePolicy` for two candidate pipelines, compares their sorted datanode utilization metrics, and returns the lower-utilization pipeline. Metrics for each pipeline are gathered from nodes, sorted, pushed into a stack-like deque, and compared node by node.

State and persistence behavior: The only state is the initialized `NodeManager` and the composed health policy. It does not persist decisions.

Dependencies and integration points: The policy plugs into SCM's pipeline choose factory and is used by writable container selection. Its behavior depends on node usage metrics being current.

Risks: If the input list is empty, the nested random policy can fail. Null node metrics are filtered out, so incomplete node stats can make comparisons shorter or tie unexpectedly. `choosePipelineIndex` copies the input list and then uses `indexOf`, relying on pipeline equality.

Test signals: Tests should cover lower-utilization selection, same-pipeline comparison, null metrics, unhealthy candidate fallback through the health policy, empty input behavior, and index mapping back to the original list.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java

Purpose: `HealthyPipelineChoosePolicy` wraps random selection with a health preference. It keeps choosing random pipelines until it finds a healthy one, and returns the last unhealthy candidate as fallback if none are healthy.

Important APIs and types: It implements `PipelineChoosePolicy` with `choosePipeline` and `choosePipelineIndex`, delegates to `RandomPipelineChoosePolicy`, and checks `Pipeline.isHealthy()`.

Control flow: The method mutates the supplied candidate list by removing unhealthy selected pipelines until a healthy pipeline is found or the list is empty. `choosePipelineIndex` protects callers by copying the input before mutation and then resolving the chosen pipeline against the original list.

State and persistence behavior: No persistent state exists. Runtime state is only the random policy instance.

Dependencies and integration points: It is used directly or as a component of capacity-based selection. It depends on pipeline health state being up to date.

Risks: Direct callers of `choosePipeline` may be surprised that the input list is modified. Empty lists return `null` via fallback, and downstream policies must handle that. Returning one unhealthy fallback can still allocate against an unhealthy pipeline if callers do not recheck.

Test signals: Tests should cover healthy selection, all-unhealthy fallback, list mutation in direct calls, non-mutation through `choosePipelineIndex`, and empty-list behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java

Purpose: `PipelineChoosePolicyFactory` instantiates the configured pipeline choose policy for regular or EC allocation, falling back to default random policies when configured classes fail.

Important APIs and types: `getPolicy(NodeManager, ScmConfig, boolean forEC)` reads `ScmConfig` policy class names, validates assignability to `PipelineChoosePolicy`, constructs with a no-arg constructor, and calls `init(NodeManager)`.

Control flow: The factory loads a class by name, attempts construction, and returns the initialized policy. If loading or construction fails for a non-default configured class, it logs the failure and retries the appropriate default. If the default itself fails, the exception is rethrown.

State and persistence behavior: The factory is stateless and persists nothing.

Dependencies and integration points: It is used during SCM initialization to wire block allocation policies. The configured class must be on the classpath, implement `PipelineChoosePolicy`, and expose a no-argument constructor.

Risks: Reflection errors become either `SCMException` for missing constructors or runtime exceptions for instantiation failures. Fallback can hide misconfiguration unless logs are monitored. Defaults for EC and non-EC currently both use random selection.

Test signals: Tests should cover valid custom policy loading, invalid class fallback, non-assignable class rejection, missing no-arg constructor errors, default failure propagation, and separate EC policy configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java

Purpose: `RandomPipelineChoosePolicy` selects a pipeline uniformly at random from the candidate list.

Important APIs and types: It implements `PipelineChoosePolicy.choosePipeline` and `choosePipelineIndex`, using `ThreadLocalRandom`.

Control flow: `choosePipelineIndex` returns `-1` for an empty list or a random integer in `[0, size)`. `choosePipeline` immediately indexes into the list using the returned index.

State and persistence behavior: The policy is stateless and stores no decisions.

Dependencies and integration points: It is the default policy from `PipelineChoosePolicyFactory` and the delegate used by `HealthyPipelineChoosePolicy`.

Risks: Calling `choosePipeline` with an empty list throws because it uses index `-1`; callers that may have no candidates should use or check `choosePipelineIndex` first. It ignores size, owner, utilization, and health unless composed by another policy.

Test signals: Tests should assert valid index ranges, empty-list `-1` from `choosePipelineIndex`, exception behavior for direct empty `choosePipeline`, and broad distribution sanity if needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java

Purpose: `RoundRobinPipelineChoosePolicy` selects candidate pipelines in cyclic order. The class comment positions it mainly as a debugging and testing policy.

Important APIs and types: It implements `PipelineChoosePolicy.choosePipeline` and synchronized `choosePipelineIndex`, maintaining `nextPipelineIndex`.

Control flow: Each index selection normalizes `nextPipelineIndex` modulo list size, returns the current index, then increments the counter. `choosePipeline` indexes into the list with that result.

State and persistence behavior: The only state is the in-memory next index. It is not persisted, so order restarts with the object.

Dependencies and integration points: It can be selected through the policy factory for deterministic spreading across available pipelines.

Risks: Empty lists cause division by zero in `choosePipelineIndex`. The index is global to the policy instance, not keyed by replication config or owner, so changing candidate lists can produce non-obvious ordering.

Test signals: Tests should cover cyclic selection, synchronized concurrent calls, behavior when the candidate list shrinks, and explicit empty-list failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/package-info.java

Purpose: This package descriptor documents that the package contains pipeline choosing algorithms.

Important APIs and types: It declares package `org.apache.hadoop.hdds.scm.pipeline.choose.algorithms`.

Control flow: There is no executable logic.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The package is consumed by SCM policy factory configuration and writable-container allocation paths.

Risks: Minimal. The main risk is documentation drift if policy classes move or expand.

Test signals: No direct tests are needed beyond compilation and package-level documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java

Purpose: `DefaultLeaderChoosePolicy` deliberately does not suggest a Ratis leader. Returning `null` lets Ratis elect a leader without SCM-imposed priority.

Important APIs and types: It extends `LeaderChoosePolicy` and implements `chooseLeader(List<DatanodeDetails>)` by returning `null`.

Control flow: Construction passes `NodeManager` and `PipelineStateManager` to the base class. Leader choice ignores the datanode list.

State and persistence behavior: No mutable or persisted state exists beyond the base references.

Dependencies and integration points: `RatisPipelineProvider` interprets `null` as a create command without suggested leader. The policy can be selected via `LeaderChoosePolicyFactory`.

Risks: Deployments expecting leader balancing should use a different policy. Tests must distinguish "no suggested leader" from an error.

Test signals: Tests should assert null leader return and that create commands omit suggested leader when this policy is configured.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java

Purpose: `LeaderChoosePolicy` is the abstract base for policies that may suggest a Ratis leader from selected datanodes.

Important APIs and types: It stores `NodeManager` and `PipelineStateManager`, exposes protected getters, and defines abstract `chooseLeader(List<DatanodeDetails>)`.

Control flow: Concrete subclasses implement all choice behavior. The base only supplies manager access.

State and persistence behavior: The base holds references to current SCM managers and persists nothing.

Dependencies and integration points: `LeaderChoosePolicyFactory` constructs subclasses, and `RatisPipelineProvider` consumes their output while building create commands and pipeline metadata.

Risks: Subclasses can return `null`; callers must treat that as a valid "no suggestion" path. Manager references may reflect changing cluster state during selection.

Test signals: Subclass tests should verify access to manager state and caller handling of both concrete datanode and null leader choices.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java

Purpose: `LeaderChoosePolicyFactory` instantiates the configured Ratis pipeline leader choose policy.

Important APIs and types: `getPolicy(ConfigurationSource, NodeManager, PipelineStateManager)` reads `OZONE_SCM_PIPELINE_LEADER_CHOOSING_POLICY`, defaults to `MinLeaderCountChoosePolicy`, requires a `(NodeManager, PipelineStateManager)` constructor, and returns a constructed policy.

Control flow: The factory obtains the class through configuration, looks up the required constructor, logs the selected type, and invokes it. Missing constructor is converted to `SCMException`; constructor invocation failures become runtime exceptions.

State and persistence behavior: The factory is stateless and persists nothing.

Dependencies and integration points: It is called by `RatisPipelineProvider` during provider construction. Custom policies must be classpath-visible and implement the expected constructor signature.

Risks: Unlike `PipelineChoosePolicyFactory`, there is no fallback after an invalid configured class once configuration resolves it. Provider construction wraps exceptions in `RuntimeException`, which can fail SCM startup.

Test signals: Tests should cover default policy creation, custom policy creation, missing constructor errors, non-policy class rejection via config, and startup failure propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java

Purpose: `MinLeaderCountChoosePolicy` balances suggested Ratis leaders by choosing the datanode with the fewest current non-closed pipelines where it is already the suggested leader.

Important APIs and types: It extends `LeaderChoosePolicy` and uses `NodeManager.getPipelines(DatanodeDetails)`, `PipelineStateManager.getPipeline`, `Pipeline.getSuggestedLeaderId`, and `PipelineID`.

Control flow: `chooseLeader` builds a count map for input datanodes, scans each datanode's pipeline IDs, increments the count for non-closed pipelines whose suggested leader ID matches the datanode, and returns the datanode with the smallest count.

State and persistence behavior: The policy stores no derived state. It reads live node and pipeline manager state.

Dependencies and integration points: `RatisPipelineProvider` writes the returned datanode into pipeline metadata and `CreatePipelineCommand`. The policy depends on previous pipelines preserving suggested leader IDs.

Risks: Ties are resolved by map iteration order, which is not explicitly stable. Missing pipeline IDs from node manager are logged at debug and ignored. It balances suggested leaders, not actual Ratis elected leaders.

Test signals: Tests should cover minimum-count selection, closed pipeline exclusion, missing pipeline tolerance, tie behavior, and command metadata containing the chosen leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/package-info.java

Purpose: This package descriptor documents that the package contains leader choosing algorithms.

Important APIs and types: It declares package `org.apache.hadoop.hdds.scm.pipeline.leader.choose.algorithms`.

Control flow: There is no executable logic.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The package is used by leader choice factory configuration and Ratis pipeline creation.

Risks: Minimal, limited to documentation drift.

Test signals: Compilation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java

Purpose: This package descriptor states that Ozone supports different pipeline kinds, such as Ratis, Simple, or other protocols, and that pipeline managers reside in this package.

Important APIs and types: It declares package `org.apache.hadoop.hdds.scm.pipeline`.

Control flow: There is no executable logic.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The documented package contains the SCM pipeline lifecycle, allocation, provider, metric, and policy integration classes.

Risks: Minimal. The grammar in the comment is slightly rough and could drift from the actual package contents.

Test signals: Compilation and generated Javadocs are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java

Purpose: `SCMSecurityProtocolServerSideTranslatorPB` is the protobuf RPC server-side adapter for SCM security operations: certificate issuance, certificate lookup/listing, CA retrieval, root CA retrieval, and expired certificate cleanup.

Important APIs and types: It implements `SCMSecurityProtocolPB`, exposes `submitRequest` and `processRequest`, and delegates to `SCMSecurityProtocol`. Helper methods include `getDataNodeCertificate`, `getOMCertificate`, `getSCMCertificate`, `getCertificate` overloads, `getCACertificate`, `listCertificate`, `getRootCACertificate`, `listCACertificate`, `getAllRootCa`, and `removeExpiredCertificates`.

Control flow: `submitRequest` rejects non-leader SCMs by triggering a Ratis not-leader exception, then invokes `OzoneProtocolMessageDispatcher`. `processRequest` builds an OK response, switches on command type, populates the matching response proto, marks unsupported CRL/revoke operations as internal errors, and converts `IOException` to protocol status and message.

State and persistence behavior: The translator persists nothing directly. Certificate and CA state lives behind `SCMSecurityProtocol`. It uses SCM storage config to decide whether SCM HA/root CA fields are valid and includes root CA data only when needed.

Dependencies and integration points: It integrates SCM HA leader checks, Ratis exception translation, security protocol implementations, `ProtocolMessageMetrics`, and protobuf response status conventions.

Risks: Status mapping uses enum ordinal alignment between `SCMSecurityException` error codes and protobuf `Status`, which is fragile if enums diverge. Some operations are explicitly unsupported but still present in the switch. HA checks differ between SCM certificate and root CA requests.

Test signals: Tests should cover leader rejection, every certificate command, root CA inclusion in HA mode, non-HA errors, unsupported operations, expired removal, all-root-CA listing, and exception-to-status/message mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java

Purpose: `ScmBlockLocationProtocolServerSideTranslatorPB` adapts block-location protobuf RPCs to the SCM block-location implementation. It covers block allocation, key-block deletion, SCM info, adding SCMs, datanode sorting, and network topology retrieval.

Important APIs and types: It implements `ScmBlockLocationProtocolPB` with `send` and `processMessage`. Helpers include `allocateScmBlock`, `deleteScmKeyBlocks`, `getScmInfo`, `getAddSCMResponse`, `sortDatanodes`, and `getClusterTree`. It converts `ReplicationConfig`, `ExcludeList`, `AllocatedBlock`, `BlockGroup`, and `DeleteBlockGroupResult`.

Control flow: `send` requires SCM leadership and dispatches through `OzoneProtocolMessageDispatcher`. `processMessage` switches on command type, applies an EC upgrade-finalization gate to block allocation, builds command-specific responses, and maps `IOException` to status. Allocation verifies that the implementation returns as many blocks as requested.

State and persistence behavior: The translator has no durable state. Allocated block and deletion state is managed by `ScmBlockLocationProtocol`. It passes client version into pipeline and datanode protobuf conversions for compatibility.

Dependencies and integration points: It integrates OM/client block allocation with SCM container and pipeline state, upgrade finalization, HA leader checks, topology sorting, and protocol metrics.

Risks: EC allocation is blocked until layout finalization allows EC support. `sortDatanodes` wraps IO failures in `ServiceException` while most switch failures become response statuses, so callers see mixed error styles. Allocation treats partial success as an exception after the implementation has potentially allocated some blocks.

Test signals: Tests should cover leader rejection, EC pre-finalization rejection, partial allocation failure, correct pipeline protobuf ports, delete result conversion, add-SCM status, datanode sort conversion, topology serialization, and exception status mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java

Purpose: `SecretKeyProtocolServerSideTranslatorPB` is the server-side protobuf adapter for SCM symmetric secret-key APIs used by datanodes and OMs.

Important APIs and types: It implements `SecretKeyProtocolDatanodePB` and `SecretKeyProtocolOmPB`. It dispatches `GetCurrentSecretKey`, `GetSecretKey`, `GetAllSecretKeys`, and `CheckAndRotate` to `SecretKeyProtocolScm`. It converts `ManagedSecretKey` objects and protobuf UUIDs.

Control flow: `submitRequest` enforces SCM leadership, then dispatches with metrics. `processRequest` switches on command type and returns the appropriate nested response. IO failures are checked for Ratis not-leader cases and then converted to protobuf status and message.

State and persistence behavior: Key state and rotation persistence live behind `SecretKeyProtocolScm`. This translator has only references to the implementation, SCM, and dispatcher.

Dependencies and integration points: It integrates SCM HA checks, security protocol RPCs, OM/datanode key consumers, `ProtobufUtils`, `ManagedSecretKey.toProtobuf`, and protocol message metrics.

Risks: `getSecretKey` returns an empty response when a key is not found instead of an explicit not-found status if the implementation returns null. Status mapping depends on enum ordinal alignment with `SCMSecretKeyException`.

Test signals: Tests should cover current-key retrieval, lookup by UUID, missing-key response shape, all-key listing, forced and non-forced rotation, leader rejection, and exception status mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocolServerSideTranslatorPB.java

Purpose: `StorageContainerLocationProtocolServerSideTranslatorPB` is the broad SCM client/admin protobuf adapter for container, pipeline, node, safe mode, replication manager, balancer, upgrade, deleted-block, metrics, and SCM HA operations.

Important APIs and types: It implements `StorageContainerLocationProtocolPB` and delegates to `StorageContainerLocationProtocol`. `submitRequest` handles leader/follower command admission and legacy-client EC filtering. `processRequest` switches over dozens of command types. Helper methods convert containers, container-with-pipeline batches, tokens, pipeline lifecycle calls, node queries, safe-mode status, replication manager state, container balancer arguments, decommission/maintenance operations, usage reports, container counts, replica lists, deleted-block summaries, leadership transfer, metrics, reconciliation, ID listing, and suppression.

Control flow: Non-leader SCMs reject commands unless they are admin or follower-readable. For clients older than EC support, selected read responses are inspected after dispatch and rejected if container or pipeline protos contain EC replication configs. Allocation and pipeline creation also block EC requests before the EC layout feature is finalized. Most command cases build an OK response directly and let `IOException` escape as `ServiceException` after Ratis exception checking.

State and persistence behavior: The translator persists nothing directly. All durable container, pipeline, node-admin, upgrade, balancer, deleted-block, and suppression state is owned by the implementation. It does preserve client-version compatibility by selecting versioned protobuf conversion paths and by honoring legacy list-container factor fields separately from newer replication-config filters.

Dependencies and integration points: This file is a central integration point between clients/admin tools and SCM managers. It depends on HA leader state, layout version manager, protocol metrics, token conversion, datanode protobuf conversion, container/pipeline protobuf conversion, safe-mode rule status, node admin errors, balancer option parsing, and upgrade finalization status conversion.

Risks: The switch is large, so adding a command requires consistent leader policy, version compatibility, request field handling, and response wiring. EC compatibility checks happen after implementation work, which is safe for reads but still means the work was done before rejecting the response. Several errors are surfaced as `ServiceException` rather than embedded response statuses. Deprecated deleted-block methods remain exposed.

Test signals: Tests should cover follower-readable and admin command admission, legacy EC response rejection, EC pre-finalization allocation/pipeline rejection, every conversion helper for representative inputs, close-container already-closed/closing statuses, balancer optional field precedence, decommission error conversion, list-container legacy and modern filters, list-container-IDs pagination, and Ratis exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java

Purpose: This package descriptor documents the RPC/protobuf translator classes for SCM protocol.

Important APIs and types: It declares package `org.apache.hadoop.hdds.scm.protocol`.

Control flow: There is no executable logic.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The package contains server-side translators between protobuf RPC interfaces and SCM implementation interfaces.

Risks: Minimal, limited to documentation drift as protocol classes are added.

Test signals: Compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java

Purpose: `AbstractContainerSafeModeRule` is the shared base for Ratis and EC container safe-mode exit rules. It requires a configured percentage of closed or quasi-closed, non-empty containers to have their minimum replica count reported before SCM exits safe mode.

Important APIs and types: Subclasses implement `getContainerType` and `handleReportedContainer`. The base manages `initializeRule`, `reinitializeRule`, `process`, `validate`, `refresh`, `cleanup`, `isMissing`, `getCurrentContainerThreshold`, and status text. It uses `ContainerManager`, `ContainerID`, `ContainerInfo`, `NodeRegistrationContainerReport`, and `SafeModeMetrics`.

Control flow: Initialization snapshots closed/quasi-closed containers of the subclass type with keys, records each container's minimum required nodes, sets total count, and publishes the threshold metric. Processing maps container reports to IDs and delegates per-reported-container handling to subclasses. Validation either checks the report-driven threshold or, when report processing is disabled, scans manager state for any closed container with too few replicas.

State and persistence behavior: Runtime state is a concurrent map of containers still missing enough reports plus atomic totals and counters. `reinitializeRule` removes DELETED containers because datanodes will not report them during registration. The rule reads persisted SCM container state through `ContainerManager` but does not write it.

Dependencies and integration points: The rule subscribes to `SCMEvents.CONTAINER_REGISTRATION_REPORT` through `SafeModeExitRule`, updates safe-mode metrics, and is orchestrated by `SCMSafeModeManager`.

Risks: The status text says "at least N reported replica" even though Ratis and EC interpret N differently. New containers after datanode registration are intentionally not added during refresh. `isMissing` ignores containers no longer found, which is pragmatic but can hide state inconsistencies.

Test signals: Tests should cover threshold calculation, filtering by state/type/key count, report-driven counter updates in subclasses, deleted-container refresh, fallback validation against live replicas, metrics updates, cleanup, and invalid cutoff configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java

Purpose: `DataNodeSafeModeRule` exits once enough in-service healthy datanodes have registered with SCM.

Important APIs and types: It extends `SafeModeExitRule<NodeRegistrationContainerReport>`, listens to `SCMEvents.NODE_REGISTRATION_CONT_REPORT`, uses `NodeManager`, `NodeStatus.inServiceHealthy`, and tracks `DatanodeID` values in a set.

Control flow: The constructor reads `HDDS_SCM_SAFEMODE_MIN_DATANODE`, sets the threshold metric, and initializes the registration set. `process` adds the reporting datanode ID, updates the count, increments the metric only for first-time registrations, and logs progress. `validate` either uses report-driven count or queries `NodeManager` directly when report processing is disabled.

State and persistence behavior: Runtime state is the registered datanode set and count. No durable state is written. `refresh` is a no-op because the rule does not snapshot SCM DB state.

Dependencies and integration points: It is one of the safe-mode precheck/exit rules built by `SafeModeRuleFactory` and reported by `SCMSafeModeManager`.

Risks: `cleanup` clears the set but not `registeredDns`, so status text after cleanup may retain the old count. Datanode identity uniqueness depends on stable `DatanodeID`. The direct validation path can pass even if registration events were missed.

Test signals: Tests should cover unique registration counting, duplicate report suppression, metric increments, configured threshold, direct node-manager validation path, cleanup behavior, and status text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java

Purpose: `ECContainerSafeModeRule` specializes the container safe-mode rule for erasure-coded containers, requiring reports from at least the EC replication config's minimum number of distinct datanodes.

Important APIs and types: It extends `AbstractContainerSafeModeRule`, returns `ReplicationType.EC`, and tracks per-container datanode IDs in `ecContainerDNsMap`.

Control flow: For each reported container still in the missing-container map, the rule records the reporting datanode in a per-container concurrent map. Once the distinct datanode count reaches the container's minimum replica value, it removes the container, increments the satisfied count, and updates the EC replica-reported metric.

State and persistence behavior: Runtime state includes the base missing-container map plus EC per-container datanode-report maps. Cleanup clears both. No durable state is written.

Dependencies and integration points: It depends on EC `ReplicationConfig.getMinimumNodes()` values captured by the base class and datanode registration reports sent during SCM startup.

Risks: It counts distinct datanodes, not EC replica indexes, so multiple reported indexes on one datanode still count once. Stale entries in `ecContainerDNsMap` remain until cleanup even after a container is satisfied. Missing-container initialization excludes empty containers.

Test signals: Tests should cover distinct datanode counting, duplicate datanode reports, threshold satisfaction at minimum nodes, metrics increments, cleanup of EC maps, and behavior when a reported container is not tracked.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java

Purpose: `HealthyPipelineSafeModeRule` requires enough open Ratis factor THREE pipelines to be healthy before SCM exits safe mode, allowing write traffic to resume safely.

Important APIs and types: It extends `SafeModeExitRule<Pipeline>`, listens for `SCMEvents.OPEN_PIPELINE`, and uses `PipelineManager`, `NodeManager`, `SCMContext`, `FinalizationManager`, `RatisReplicationConfig`, `NodeStatus`, and `SafeModeMetrics`.

Control flow: Initialization snapshots open Ratis THREE pipelines and sets a threshold as the max of configured percentage and a minimum derived from min datanodes divided by three. Event processing ignores non-Ratis/THREE pipelines, duplicates, wrong node counts, and pipelines whose datanodes are missing or not in-service healthy; valid pipelines increment counters and leave the unprocessed set. Validation bypasses the rule during upgrade finalization when new pipelines should not be created, otherwise either checks event counters or queries the pipeline manager directly.

State and persistence behavior: Runtime state includes threshold count, current healthy count, processed IDs, and unprocessed IDs. The rule reads live pipeline and node state but writes only metrics and logs.

Dependencies and integration points: It is coordinated by `SCMSafeModeManager`, depends on pipeline open events from pipeline management, and gates SCM service startup behavior through safe-mode status.

Risks: The event-driven path requires all three pipeline nodes to be present in the pipeline object and healthy at processing time. Thresholds can change during refresh as open pipeline counts change. It balances safety with upgrade finalization by bypassing when pipeline creation is intentionally disabled.

Test signals: Tests should cover threshold math, finalization bypass, non-Ratis and non-THREE skipping, duplicate reports, unhealthy/missing datanode rejection, direct validation path, refresh behavior, metrics, and status samples.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java

Purpose: `OneReplicaPipelineSafeModeRule` requires a configured percentage of pre-existing open Ratis factor THREE pipelines to have at least one datanode report them, ensuring read availability for open containers before safe-mode exit.

Important APIs and types: It extends `SafeModeExitRule<PipelineReportFromDatanode>`, listens to `SCMEvents.PIPELINE_REPORT`, uses `PipelineManager`, `PipelineReport`, `PipelineID`, `RatisReplicationConfig`, and `SafeModeMetrics`.

Control flow: Initialization snapshots current open Ratis THREE pipeline IDs and calculates the threshold. Processing iterates reported pipeline IDs, resolves each pipeline, filters to open Ratis THREE pipelines in the original snapshot, and counts each pipeline only once. When report processing is disabled, validation updates the reported set by scanning open pipelines with non-empty node sets.

State and persistence behavior: Runtime state is the original pipeline ID set, reported pipeline ID set, threshold, and current count. It reads live pipeline state but persists nothing.

Dependencies and integration points: It is part of SCM safe-mode exit and receives pipeline reports from datanode heartbeat dispatch. It complements the healthy-pipeline rule by requiring at least one report for old pipelines.

Risks: It only counts pipelines present during initialization; newly created open pipelines are intentionally excluded until refresh. `cleanup` clears reported IDs but leaves counters and old IDs. Missing pipelines in reports are silently ignored.

Test signals: Tests should cover initial threshold calculation, single counting across duplicate reports, filtering by replication factor and open state, pipeline-not-found tolerance, direct validation path, refresh reset, metrics, and status sample output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java

Purpose: `RatisContainerSafeModeRule` specializes the container safe-mode rule for Ratis containers. It treats one reported replica as the minimum requirement.

Important APIs and types: It extends `AbstractContainerSafeModeRule`, returns `ReplicationType.RATIS`, and implements `handleReportedContainer`.

Control flow: On a reported container, it looks up the base map's minimum replica value. If the container is still tracked, it removes it, asserts that the minimum replica value is exactly one, increments the satisfied count, and updates the one-replica metric.

State and persistence behavior: Runtime state is inherited from the base class. The class writes no durable state.

Dependencies and integration points: It depends on Ratis container replication configs having `getMinimumNodes() == 1` for safe-mode read availability and on datanode container registration reports.

Risks: The Ratis precondition assertion will fail if a future Ratis config reports a different minimum node count. Duplicate reports after removal are ignored. Empty containers are excluded by the base initializer.

Test signals: Tests should cover first report satisfying a tracked container, duplicate reports no-op, assertion of minimum replica one, metric increments, and base threshold behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java

Purpose: `SCMSafeModeManager` coordinates SCM startup safe mode. It tracks rule validation, precheck completion, safe-mode exit, periodic status logging, safe-mode metrics, and notifications to delayed SCM services.

Important APIs and types: It implements `SafeModeManager` and exposes `start`, `stop`, `validateSafeModeExitRules`, `forceExitSafeMode`, `refresh`, `refreshAndValidate`, `getInSafeMode`, `getRuleStatus`, `getPreCheckComplete`, `reconfigureLogInterval`, and nested enum `SafeModeStatus`. It uses `SafeModeRuleFactory`, `SafeModeExitRule`, `SCMServiceManager`, `SCMContext`, `SafeModeMetrics`, and `EventQueue`.

Control flow: Construction initializes rule factory, records exit and precheck rules, creates metrics, and optionally disables safe mode immediately. `start` records entry time and starts periodic logging. Rule validation moves state from INITIAL to PRE_CHECKS_PASSED when all precheck rules pass, then to OUT_OF_SAFE_MODE when all rules pass. Exiting safe mode updates context, stops logging, notifies services, and records duration. Refresh methods either rebuild rule state or rebuild and validate immediately.

State and persistence behavior: State is process-local: atomic status, rule maps, validated rule sets, metrics, log scheduler, and entry timestamp. No durable state is written, but the rules read SCM DB-backed manager state during refresh and validation.

Dependencies and integration points: It is the central safe-mode service used by SCM startup, service gating, protocol status APIs, and metrics. It notifies `SCMServiceManager` when prechecks pass or safe mode exits, and updates `SCMContext` for cluster-wide status.

Risks: The rule factory is singleton-based, so initialization order and tests must isolate it. Periodic logging calls every rule's status text, which may query managers and produce expensive logs. `forceExitSafeMode` bypasses rule validation. `getCurrentContainerThreshold` hard-casts the Ratis rule by name and is marked temporary.

Test signals: Tests should cover disabled safe mode, precheck transition, final exit transition, service notifications, forced exit duration recording, refresh and refresh-and-validate behavior, periodic logger start/stop/reconfiguration, metrics unregister, and rule status reporting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java -->
