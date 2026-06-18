# subset-b-008451 research

Grouped research report for fdbrpc load-balancing, locality, replication, simulator, RPC, metrics, and gRPC headers. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.actor.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.actor.h

Purpose: This actor header implements the client-side request load balancer used by fdbrpc interfaces. It chooses endpoints from `MultiInterface`/`ModelInterface`, sends request/reply RPCs, races secondary requests when latency modeling predicts benefit, updates `QueueModel`, and optionally duplicates or verifies reads through TSS and replica comparison paths.

Important APIs/types/functions: `LoadBalancedReply` is the optional reply adapter carrying a server penalty and embedded error. `ModelHolder` is an RAII accounting guard around `QueueModel::addRequest()`/`endRequest()`. `RequestData<Request, Interface, Multi, P>` owns one in-flight request attempt and handles delayed starts, TSS duplication, replica comparison, result classification, and lagging-request model updates. `loadBalance()` is the main actor for robust load-balanced request/reply RPCs. `basicLoadBalance()` is a simpler always-fresh balancer for `ModelInterface`. `tssComparison()` and `replicaComparison()` perform shadow comparison against TSS endpoints and selected storage replicas.

Control flow: `loadBalance()` assigns reply priority, chooses a best and next alternative randomly or from queue measurements, then loops until a reply is accepted or an error is thrown. It skips failed endpoints via `IFailureMonitor`, waits for one endpoint to recover when all alternatives are down, sends a first request, and may send a second request after a model-derived delay if the first is slow and budget remains. Responses are processed by `RequestData::checkAndProcessResultImpl()`, which distinguishes success, retryable overload/broken-promise/maybe-delivered/process-behind cases, future-version backoff signals, and non-retryable errors. On successful read paths it may wait for replica comparison before returning the chosen reply.

State and persistence behavior: There is no durable persistence in this header. Mutable runtime state lives in request-local actor state, `ModelHolder`, and `QueueModel` endpoint records. Destructing an unfinished `RequestData` converts the request into a lagging request actor so the model still receives eventual latency/error information. TSS mismatch detail can be stored in `TSSMetrics::detailedMismatches`, and trace events record mismatch IDs, latency, errors, and distant fallback behavior.

Dependencies and integration points: The code depends on Flow actors/futures, `RequestStream`, `ReplyPromise`, `FailureMonitor`, `QueueModel`, `MultiInterface`, locality distance, simulator policy capabilities, and `TSSComparison` hooks implemented by request/reply types elsewhere. It is tightly integrated with storage server read requests because `resetReply`, `setReplyPriority`, `TSS_doCompare`, `TSS_traceMismatch`, and `LB_mismatchTraceName` are type-specialized.

Risks: The actor mutates and reuses request objects, so every retry/comparison path must reset reply promises before resending. At-most-once callers rely on correct `request_maybe_delivered` propagation. `process_behind`, `future_version`, and server penalty handling directly affect client routing; regressions can create hot spots or retry storms. Replica comparison can turn warning-only comparison into thrown errors for required replica modes, and must always propagate `wrong_shard_server`. Secondary request and lagging-request accounting risks leaks or stale model data if cancellation paths are mishandled.

Test signals: Useful tests include simulated endpoint failures, all-local-failed fallback, overloaded servers with penalties, future-version/process-behind retries, at-most-once broken-promise propagation, distant second-request tracing, TSS mismatch/timeout/error metrics, replica mismatch throws, and lagging-request model cleanup after racing requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.h

Purpose: This is a compatibility include wrapper that exposes the generated/source actor implementation in `LoadBalance.actor.h` under the traditional `LoadBalance.h` name.

Important APIs/types/functions: It defines no new API; every public symbol comes from `LoadBalance.actor.h`, including `loadBalance()`, `basicLoadBalance()`, `LoadBalancedReply`, and comparison helpers.

Control flow: Include-time only. Consumers including this header enter the actor-header include logic, which switches to `LoadBalance.actor.g.h` when compiled with the actor compiler generated output.

State and persistence behavior: None in this file.

Dependencies and integration points: This file is the integration point for code that does not want to include the `.actor.h` path directly. It inherits all actor compiler requirements and dependencies from `LoadBalance.actor.h`.

Risks: Any include-cycle or actor generated-header issue appears here for legacy include users. Because it lacks its own include guard, it relies on `LoadBalance.actor.h` guards.

Test signals: Build coverage is the primary signal: any translation unit including `fdbrpc/LoadBalance.h` should compile in both actor-compiler and non-intellisense paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadPlugin.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadPlugin.h

Purpose: Provides a small templated helper for dynamically loading fdbrpc/Flow plugin objects from shared libraries.

Important APIs/types/functions: `loadPlugin<T>(std::string const& plugin_name)` calls `loadLibrary()`, looks up a `get_plugin` symbol, and asks that symbol for `T::get_plugin_type_name_and_version()`. It returns a `Reference<T>` around the resulting pointer or a null reference.

Control flow: Loading is synchronous and linear: open library, load symbol, call symbol if present, wrap pointer. There is no retry or error detail propagation.

State and persistence behavior: The loaded library handle is not stored by this function; lifetime is delegated to `loadLibrary` implementation and the returned reference-counted plugin object. No durable state is changed.

Dependencies and integration points: Depends on Flow dynamic library helpers and `Reference<T>`. Plugin implementations must export `get_plugin` and support type-name/version negotiation.

Risks: Failure modes collapse to null, so callers must check the returned reference. ABI/version mismatches are pushed into the plugin symbol contract. Library unloading/lifetime is opaque here, so plugin objects must remain valid after `loadPlugin` returns.

Test signals: Tests should cover missing library, missing `get_plugin`, wrong plugin type/version, and a successful plugin returning a reference-counted object.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadPlugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Locality.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Locality.h

Purpose: Defines process classes, locality metadata, process descriptors, and load-balance locality traits used throughout cluster role assignment, replication placement, and endpoint routing.

Important APIs/types/functions: `ProcessClass` stores `ClassType` and `ClassSource`, maps classes to role fitness, serializes class/source enum values, and has static assertions preserving persisted enum numbers. `LocalityData` stores optional string attributes keyed by stable `StringRef`s such as process, zone, machine, data hall, and datacenter IDs. `ProcessData` bundles locality, class, network address, and optional gRPC address. `LBLocalityData` is a trait that detects interfaces with `LocationAwareLoadBalance`, and `loadBalanceDistance()` classifies endpoints as same-machine, same-DC, or distant.

Control flow: `LocalityData` is a map wrapper with getters, setters, descriptions, JSON conversion, and protocol-aware serialization. `ProcessClass` constructors parse strings elsewhere, while this header exposes getters and comparison operators. Load balancers use `LBLocalityData` specialization to extract locality/address from interfaces only when the interface opts in.

State and persistence behavior: `ProcessClass` and `LocalityData` are serialized into cluster metadata and restart info; comments and static assertions make enum stability a hard compatibility contract. `ProcessData` serialization is protocol-version gated for `grpcAddress`.

Dependencies and integration points: Depends on Flow serialization, `NetworkAddress`, and `Standalone<StringRef>`. Integrated by `MultiInterface`, replication locality maps, worker lists, simulator process metadata, status JSON, and role fitness logic.

Risks: Reordering `ClassType` or `ClassSource` breaks persisted data and upgrade tests. Locality serialization requires `ProtocolVersion::hasLocality()`. `LocalityData::isPresent(key, value)` appears inverted in the header (`pos != end ? false : ...`), so callers should be checked carefully if they rely on value-sensitive presence. Missing locality fields degrade placement/load-balance decisions to distant/default behavior.

Test signals: Upgrade serialization tests, role fitness matrix tests, JSON/status output checks, locality-distance tests, and worker-list compatibility tests are the most relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Locality.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/MultiInterface.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/MultiInterface.h

Purpose: Supplies containers for multiple RPC interfaces and probability/locality-aware selection metadata used by load balancing.

Important APIs/types/functions: `KVPair` is an ordered pair by key for description helpers. `ReferencedInterface<T>` wraps an interface and precomputes `LBDistance`. `AlternativeInfo<T>` stores a model interface, probability, cumulative probability, recent busy metric, and update time. `ModelInterface<T>` provides probabilistic selection for `basicLoadBalance()`. `MultiInterface<ReferencedInterface<T>>` stores sorted referenced alternatives and exposes `countBest()`, `get()`, `getInterface()`, `getDistance()`, `getId()`, and `hasInterface()`.

Control flow: `ModelInterface` initializes equal probabilities, then periodically calls `updateProbabilities()` based on recent process busy metrics, bounded by knobs and minimum signal thresholds. `MultiInterface` shuffles alternatives, stable-sorts by locality distance when available, and computes the number of best-distance alternatives.

State and persistence behavior: State is in-memory and reference counted. `ModelInterface` has a recurring future that updates probabilities. There is no serialization support; load functions intentionally assert false for `Reference<MultiInterface<T>>` and `Reference<ModelInterface<T>>`.

Dependencies and integration points: Depends on `FastRef`, `Locality.h`, deterministic random, and Flow knobs. `LoadBalance.actor.h` consumes `MultiInterface` for storage/read routing and `ModelInterface` for basic proxy-style balancing.

Risks: Probability updates require fresh busy metrics; stale metrics abort updates. `MultiInterface<T>` non-referenced constructor asserts false but remains for templating, so correct type wrapping matters. `bestCount` drives locality fallback; incorrect locality traits or sorting can send local requests remotely.

Test signals: Tests should cover locality sort order, `countBest()` for same/different distances, probability normalization bounds, stale busy metric behavior, balance-on-requests vs CPU metric decoding, and serialization attempts failing loudly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/MultiInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Net2FileSystem.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Net2FileSystem.h

Purpose: Declares the production asynchronous file system implementation backed by Net2/IAsyncFile primitives.

Important APIs/types/functions: `Net2FileSystem final : IAsyncFileSystem` overrides `open`, `deleteFile`, `lastWriteTime`, and `renameFile`; exposes static `stop()` and `newFileSystem()` helpers; and optionally exposes actor lineage sampling state.

Control flow: Implementations are elsewhere. Constructors accept an IO timeout and optional file-system path list/string; Linux builds store device IDs and a `checkFileSystem` flag for path/device validation.

State and persistence behavior: The object owns runtime file-system configuration and optional Linux device-id tracking. File methods operate on actual host files and therefore affect durable filesystem state through their implementations.

Dependencies and integration points: Depends on `flow/IAsyncFile.h` and is used where the network layer installs the process-global async file system. It is the production counterpart to simulator file systems.

Risks: Durable delete and rename semantics depend on implementation details outside the header. Linux device checks can reject or classify paths if device IDs are wrong. Static global install/stop APIs can affect all async file users in a process.

Test signals: File open/read/write, durable delete, rename, last-write-time, timeout behavior, multi-path configuration, Linux device-check behavior, and sampling lineage exposure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Net2FileSystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/PerfMetric.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/PerfMetric.h

Purpose: Defines simple serializable performance metric values and lightweight integer/double counters that emit those metrics.

Important APIs/types/functions: `PerfMetric` stores name, format code, numeric value, and averaged flag, with accessors, formatted output, prefixing, and serialization. `PerfIntCounter` and `PerfDoubleCounter` support increment/add, `getMetric()`, `getValue()`, and `clear()`, and can register themselves in caller-provided vectors.

Control flow: Counters accumulate locally until callers read `getMetric()` or clear them. Formatting uses the stored printf-style format string.

State and persistence behavior: Metric values are in-memory but `PerfMetric` serializes through Flow serializer using file identifier `5980618`. Counter objects are not themselves serialized here.

Dependencies and integration points: Depends on Flow BooleanParam, serialization, formatting, and `Averaged` parameter. Used by status/performance reporting surfaces that need a compact metric object independent of the richer `Stats.h` counters.

Risks: Format strings must match numeric value expectations. Vector registration stores raw counter pointers, so counter lifetime must outlive collection use. Averaging semantics are only a flag; consumers must interpret it consistently.

Test signals: Serialization round trips, formatted values, prefixing, integer no-decimal formatting, clear/increment behavior, and pointer registration lifetime in owning collections.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/PerfMetric.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/QueueModel.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/QueueModel.h

Purpose: Declares the client-side queue/latency model used by load balancing to estimate endpoint load, penalize overloaded servers, delay retrying failed/future-version endpoints, and manage TSS endpoint mappings.

Important APIs/types/functions: `TSSEndpointData` maps a storage endpoint to a TSS endpoint and metrics. `QueueData` stores `Smoother smoothOutstanding`, last latency, server penalty, `failedUntil`, future-version backoff state, and optional TSS mapping. `QueueModel` exposes `addRequest()`, `endRequest()`, `getMeasurement()`, TSS update/remove/get methods, secondary-request budget/multiplier fields, and actor collections for lagging requests and TSS comparisons.

Control flow: `loadBalance()` calls `addRequest()` when issuing an attempt and `endRequest()` when a response/error is classified. The model exposes measurements used to choose best/next endpoints and to compute second-request delays. Lagging request and TSS actor collections are fed from load-balance code to keep accounting asynchronous but bounded.

State and persistence behavior: All state is in-memory per client/process. The `data` map is keyed by endpoint token id. Destructor cancels lagging/TSS actor collections. No durable persistence.

Dependencies and integration points: Depends on `Smoother`, Flow knobs, `ActorCollection`, `TSSComparison`, and `FlowTransport::Endpoint`. It is directly integrated with `LoadBalance.actor.h`.

Risks: Incorrect `delta` pairing between `addRequest()` and `endRequest()` corrupts outstanding estimates. Future-version and failed-until backoff influence endpoint exclusion, so bad tuning can underuse healthy replicas. `laggingTSSCompareCount` is declared but not initialized in the constructor in this header, making implementation/constructor initialization worth checking.

Test signals: Model tests should assert outstanding smoothing deltas, penalty updates, latency updates, failure/future-version backoff, endpoint measurement creation, secondary request budget changes, TSS mapping lifecycle, and actor collection cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/QueueModel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/RangeMap.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/RangeMap.h

Purpose: Implements a templated interval map over ordered keys using boundary entries, with optional metric aggregation through Flow's indexed map.

Important APIs/types/functions: `RangeMapRange<Key>` and `rangeMapRange()` represent half-open ranges. Metric functors compute constant/key/value/key-value byte metrics. `RangeMap<Key, Val, Range, Metric, MetricFunc>` exposes iterators whose `begin()`, `end()`, `range()`, and `value()` represent logical intervals, plus `ranges()`, `intersectingRanges()`, `containedRanges()`, `rangeContaining()`, `insert()`, `coalesce()`, `allEqual()`, metric sum helpers, and random/nth range selection.

Control flow: The constructor installs a beginning boundary at default `Key()` and an end sentinel at `endKey`. `insert()` ensures an end boundary carrying the prior value, erases overwritten boundaries, inserts a new begin boundary, and leaves coalescing to callers. Iteration stops before the sentinel. `coalesce()` removes adjacent boundaries with equal values around a key or range.

State and persistence behavior: State is an in-memory `Map<Key, Val, pair_type, Metric>` of boundaries and values. `clearAsync()` delegates to the underlying map. No built-in serialization is provided.

Dependencies and integration points: Depends on Flow `MapPair`, `IndexedSet` map implementation, deterministic random, boost iterator ranges, and key/value types with ordering and equality. Used by higher layers needing compact range ownership/state maps.

Risks: Correctness depends on the sentinel invariant: one extra end boundary always exists. Callers must coalesce when they require no adjacent equal ranges. `rangeContainingKeyBefore()` assumes key-like types with `.size()`, so it is oriented toward string/key ranges. Metric functors assume `key` and `value` have `size()` where used.

Test signals: Boundary insertions at beginning/end, overlapping inserts, empty-range no-op, coalescing, sentinel preservation, iterator decrement before begin/end behavior, random/nth range, and metric sums across inserted ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/RangeMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Replication.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Replication.h

Purpose: Defines locality-indexed sets and maps used by replication policies to select and validate replicas across zones, racks, datacenters, and other locality attributes.

Important APIs/types/functions: `LocalitySet` holds entries plus per-set string-to-int key maps, value arrays, mutable entry arrays, and cached restricted subsets. It exposes `selectReplicas()`, `validate()`, `restrict()`, `getMatches()`, random selection helpers, key/value conversion/text helpers, memory accounting, copy/deep-copy, and cache reporting. `LocalityGroup` is the root set containing `LocalityRecord` objects and the shared value map. `LocalityMap<V>` extends `LocalityGroup` to associate entries with external objects and return selected object pointers.

Control flow: Adding locality data converts string attributes to sorted integer records and updates key/value indexes. Restricting by attribute uses `_cacheArray` when possible; otherwise it scans entries, maps local keys to group keys, builds a derived `LocalitySet`, and caches it. Replica selection delegates to an `IReplicationPolicy`, passing a reference-counted set and accumulating `LocalityEntry` results. `LocalityMap` then maps selected entries back to object pointers.

State and persistence behavior: State is in-memory and reference-counted. Copy can share maps/records, while deep-copy duplicates key/value maps and makes the new set its own locality group. There is no direct serialization here, but it consumes serializable `LocalityData` and policy trees.

Dependencies and integration points: Depends on `Locality.h`, `ReplicationPolicy.h`, and `ReplicationTypes.h`. Higher-level storage recruitment and team-building code uses these structures to enforce fault-domain placement policies.

Risks: The cache stores derived `LocalitySet` references and must be cleared whenever entries or key maps change. Copy vs deep-copy semantics are subtle because `_localitygroup`, `_keymap`, and `_valuemap` may be shared. Random selection mutates `_mutableEntryArray`, so repeated selection behavior depends on prior calls. Attribute names must match policy expectations exactly.

Test signals: Add/restrict/cache hit/miss behavior, policy selection on root and derived sets, copy/deep-copy independence, random exception selection, object mapping in `LocalityMap`, memory accounting, and cache invalidation after clear/add.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Replication.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationPolicy.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationPolicy.h

Purpose: Declares the replication policy tree interface and concrete policy nodes that select/validate locality-aware replica sets.

Important APIs/types/functions: `IReplicationPolicy` defines `name()`, `info()`, `maxResults()`, `selectReplicas()`, `validate()`, `validateFull()`, tracing helpers, attribute-key collection, cached `depth()`/`maxdepth()`, and serialization. `PolicyOne` selects one entry. `PolicyAcross` selects `_count` groups across a given attribute and applies an embedded policy within each group. `PolicyAnd` composes multiple policies and sorts them for selection by max results/depth. `serializeReplicationPolicy()` writes a policy type name plus payload and reconstructs `One`, `Across`, `And`, or null. `dynamic_size_traits<Reference<IReplicationPolicy>>` supports variable-sized serialized policy values.

Control flow: Policy operations recurse down the policy tree. `Across` restricts available servers by attribute values, tracks used values and added results, and applies the embedded policy. `And` runs multiple policies and validates combined requirements. Serialization dispatches by string type name, then calls the concrete policy serializer.

State and persistence behavior: Policies are reference-counted and cache depth/max-depth lazily. Serialization is protocol-sensitive and explicitly warns that `ProtocolVersion::ReplicationPolicy` must be considered for changes. `PolicyAcross` has mutable temporary caches/vectors used during selection.

Dependencies and integration points: Depends on `ReplicationTypes.h`, `LocalitySet` forward declarations, Flow serialization, and `TraceEvent`. Used by storage team selection, recruitment, configuration, and replication validation tooling.

Risks: Adding or renaming policy types is a wire-format change. Cached `_depth`/`_maxdepth` can become stale if mutable policy trees are modified after use. `PolicyAcross::isSingleAcrossOverPolicyOne()` relies on dynamic_cast shape and max-depth. Selection temporary members make thread-safety/reentrancy assumptions important.

Test signals: Policy serialization compatibility, type-name dispatch, `One`/`Across`/`And` selection and validation, attribute-key collection, depth/maxdepth traversal, unavailable/insufficient locality cases, and full validation with `alsoServers`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationPolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationTypes.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationTypes.h

Purpose: Provides the compact integer-backed attribute, value, entry, and record structures that power locality replication maps and policies.

Important APIs/types/functions: `AttribKey`, `AttribValue`, and `LocalityEntry` are small ID wrappers with ordering/equality. `KeyValueMap` stores sorted `(AttribKey, AttribValue)` pairs and supports `getValue()` and `isPresent()` via binary search. `LocalityRecord` attaches a `KeyValueMap` to an entry index. `StringToIntMap` maps strings to stable-in-map integer IDs and supports reverse lookup, clear/copy, and memory accounting. `g_replicationdebug` and `emptyEntryArray` are externs used by replication code.

Control flow: `StringToIntMap::convertString()` assigns IDs incrementally. `KeyValueMap` queries use lower_bound with key or key/value comparators. `LocalityRecord` delegates queries to its map and can produce debug strings.

State and persistence behavior: These are in-memory helper structures; their integer IDs are local to a map/group and are not a global durable encoding. `StringToIntMap` owns the string-ID state used by `LocalityGroup`.

Dependencies and integration points: Depends on Flow types and `LocalityData`. Used by `Replication.h`, `ReplicationPolicy.h`, and replication utilities.

Risks: IDs are only meaningful within their owning maps; mixing keys/values from different groups can produce wrong answers. `lookupString()` returns `"<missing>"` for out-of-range IDs, which is useful for debug but can hide a caller bug. Correctness assumes `KeyValueMap` arrays are sorted before lookup.

Test signals: String-to-ID stability within a map, reverse lookup, sorted key/value lookup, absent-key behavior, memory accounting, and record debug formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationUtils.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationUtils.h

Purpose: Declares replication-policy test and analysis helpers used to evaluate locality policies and generate/filter test locality maps.

Important APIs/types/functions: Exports `convertToTestType()`, `testReplication()`, `ratePolicy()`, `findBestPolicySet()`, `findBestUniquePolicySet()`, overloads of `validateAllCombinations()`, `createTestLocalityMap()`, and `filterLocalityDataForPolicy*()` helpers.

Control flow: Implementations are elsewhere. The declared functions repeatedly apply policies to locality sets, rate uniqueness/failure characteristics, brute-force combinations, and remove locality keys not used by a policy.

State and persistence behavior: No state in the header. Helpers operate on caller-provided `LocalitySet`, `LocalityGroup`, policy references, and locality vectors.

Dependencies and integration points: Depends on `ReplicationTypes.h`, `LocalityData`, `LocalitySet`, `LocalityGroup`, and `IReplicationPolicy`. It is test/support oriented rather than core runtime selection.

Risks: These utilities can be expensive because they test many selections or combinations. Filtering locality data must preserve every attribute a policy actually uses or validation will become unsound.

Test signals: Unit tests around policy rating, best-set discovery, unique-policy selection, all-combinations validation, generated locality maps, and policy-driven locality filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorKillType.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorKillType.h

Purpose: Defines the simulator fault/kill severity enum used by simulation policies and process/machine kill APIs.

Important APIs/types/functions: `simulator::KillType` includes `KillInstantly`, `InjectFaults`, `FailDisk`, `RebootAndDelete`, `RebootProcessAndDelete`, `RebootProcessAndSwitch`, `Reboot`, `RebootProcess`, and `None`.

Control flow: None in this header. The comment states enum order matters because simulation code compares kill types to rank destructiveness.

State and persistence behavior: No state. The enum is part of simulator API contracts and may appear in shutdown futures/signals.

Dependencies and integration points: Used by `simulator.h`, `SimulatorProcessInfo.h`, simulation policies, and fault injection logic.

Risks: Reordering enum values changes severity comparisons. Adding new values requires auditing policy comparison logic and trace/reporting code.

Test signals: Simulation policy tests that downgrade/compare kill types, process shutdown signal behavior, and coverage for every kill mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorKillType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorMachineInfo.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorMachineInfo.h

Purpose: Defines per-machine simulation metadata, including process membership, open files, simulated remote ports, and machine identity.

Important APIs/types/functions: `simulator::MachineInfo` stores the machine process, child processes, open file weak references, deleting/closing file sets, optional machine ID, `remotePortStart`, and `usedRemotePorts`. `getRandomPort()` returns the first unused port from 1000 to 59999 and traces it. `removeRemotePort()` releases a used remote port above the start threshold.

Control flow: Port allocation linearly scans the configured range, records the selected port, and calls `UNREACHABLE()` if exhausted. Removal ignores low ports and erases matching used ports.

State and persistence behavior: Machine state is in-memory simulation state. `openFiles`, deletion/closing sets, and port vectors model durable file and network resources for simulated processes but are not themselves durable outside the simulator.

Dependencies and integration points: Depends on Flow optional/file types and `SimulatorProcessInfo` forward declaration. Used by `ISimulator` implementations and process fault/reboot/file IO simulation.

Risks: Linear port scan can become slow if many ports are used. `UnsafeWeakFutureReference<IAsyncFile>` requires careful lifecycle handling. Port allocation returns `short`, so the 60000 limit is near signed 16-bit overflow concerns; callers should treat it as network port data carefully.

Test signals: Port allocation uniqueness, port removal/reuse, machine process membership after reboot/kill, open-file cleanup, and machine ID locality behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorMachineInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorProcessInfo.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorProcessInfo.h

Purpose: Defines per-process simulation metadata used by the simulator to represent a Flow/FDB process, its network listeners, locality, metrics, fault state, globals, and shutdown signaling.

Important APIs/types/functions: `simulator::ProcessInfo` stores names/folders, machine pointer, addresses, locality, starting class, TD/metric/chaos/histogram collections, listeners, UDP sockets, failed/excluded/cleared/rebooting flags, network connection provider, fault-injection probabilities, disk failure state, UID, protocol version, child processes, and a shutdown `Promise<KillType>`. Methods include `onShutdown()`, `isSpawnedKVProcess()`, `isReliable()`, `isAvailable()`, `isExcluded()`, `isCleared()`, `getReliableInfo()`, `isAvailableClass()`, `getListener()`, process-local global get/set, and `toString()`.

Control flow: Constructor initializes identity and default reliability state. Availability is derived from exclusion plus reliability. `isAvailableClass()` permits only classes suitable for stateful roles. `global()` and `setGlobal()` implement process-local global storage by numeric ID.

State and persistence behavior: This is in-memory simulation state. Data and coordination folder strings point to simulated/real filesystem locations used by simulator implementations. Shutdown is signaled asynchronously with a kill type.

Dependencies and integration points: Depends on network/listener/socket interfaces, metrics, chaos metrics, histograms, `Locality`, machine/kill type headers, deterministic random, and protocol versions. Used by `ISimulator` and simulation fault policies.

Risks: Reliability combines process and machine fault injection; missing machine linkage can change behavior. `getListener()` asserts if the address is not registered. Process globals are untyped `flowGlobalType`, so ID ownership must be consistent. `isAvailableClass()` must stay aligned with role assignment rules.

Test signals: Process construction, shutdown futures, stateful class filtering, fault injection reliability, exclusion/cleared flags, listener registration lookup, child process tracking, global storage, and formatted process description.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorProcessInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Smoother.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Smoother.h

Purpose: Provides reusable exponential and Holt linear smoothing helpers for metrics and queue estimates.

Important APIs/types/functions: `SmootherImpl<T>` implements basic exponential smoothing with `reset()`, `setTotal()`, `addDelta()`, `smoothTotal()`, `smoothRate()`, and `getTotal()`. `Smoother` uses `now()`, while `TimerSmoother` uses `timer()`. `HoltLinearSmootherImpl<T>` implements double exponential smoothing with trend estimation and the same total/rate accessors. `HoltLinearSmoother` and `HoltLinearTimerSmoother` provide clock-specific wrappers.

Control flow: Basic smoothing updates the estimate lazily when callers add deltas or read smoothed values, using elapsed time and e-folding time. Holt smoothing updates estimate and rate snapshots when deltas arrive, then predicts total/rate based on elapsed time and trend.

State and persistence behavior: State is in-memory numeric totals, estimates, rates, and timestamps. No serialization.

Dependencies and integration points: Depends on Flow time functions and `<cmath>`. `QueueModel` uses `Smoother` for smoothed outstanding request counts; metrics code can use timer variants.

Risks: Time values are expected nondecreasing; negative elapsed time would distort estimates. Very small e-folding times can create unstable or near-step behavior. `HoltLinearTimerSmoother` members are private by default in the header, which may limit construction/use unless intentional.

Test signals: Deterministic fake-clock tests for add/set/read, zero elapsed behavior, rate calculation, reset, trend-following behavior, and nondecreasing-time assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Smoother.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Stats.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Stats.h

Purpose: Declares fdbrpc performance counters, collections, latency bands, and latency samples that feed trace events and OTEL metric models.

Important APIs/types/functions: `ICounter` extends `IMetric` with name/value/rate/roughness/reset methods. `CounterCollection` owns groups of counters and can log them to trace events or periodically trace with decoration. `Counter` tracks integer value, interval delta, rate, and roughness; it emits an `Int64MetricHandle`. `SpecialCounter<F>` registers computed integer counters. `LatencyBands` builds threshold counters for latency ranges. `LatencySample` records latency measurements into `DDSketch` and emits tail latencies.

Control flow: Counters register with a collection, accumulate values through increments, and reset interval state after logging. `CounterCollection::traceCounters()` schedules repeated trace logging. `LatencyBands` inserts thresholds and increments matching bands for each measurement. `LatencySample` maintains a sketch and logs periodically.

State and persistence behavior: Runtime metric state is in-memory. Metric data is exported through trace events and OTEL handles rather than durable storage. `CounterCollection` destructor calls `remove()` on counters marked for removal, which is how heap-allocated `SpecialCounter` instances clean up.

Dependencies and integration points: Depends on Flow errors, random, knobs, OTEL metrics, serializer, TDMetric, Swift support, and `DDSketch`. `TSSMetrics` builds on `CounterCollection` and `Counter`.

Risks: Counter lifetime must match collection lifetime; `SpecialCounter` deletes itself via `remove()`. Roughness calculation treats large deltas as repeated events and can be sensitive to interval reset timing. `SpecialCounter` rejects floating return types by static assertion, which can surprise callers. Logging futures must be cancelled/destructed correctly by owners.

Test signals: Counter increment/rate/roughness math, interval reset, trace formatting, skip-trace-on-silent behavior, special counter cleanup, latency band thresholds, DDSketch tail emission, and OTEL metric model compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TSSComparison.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TSSComparison.h

Purpose: Declares the comparison and metric hooks used when load balancing duplicates requests to a testing storage server or compares storage replicas.

Important APIs/types/functions: `DetailedTSSMismatch` stores mismatch ID, timestamp, and trace string. `TSSMetrics` contains counters for requests, stream comparisons, SS/TSS errors, TSS timeouts, mismatches, DDSketch latency distributions for several request kinds, error-code maps, detailed mismatch records, and methods `ssError()`, `tssError()`, `recordLatency()`, `shouldRecordDetailedMismatch()`, `recordDetailedMismatchData()`, and `clear()`. Template declarations `TSS_doCompare`, `LB_mismatchTraceName`, and `TSS_traceMismatch` are implemented for concrete storage request/reply types elsewhere.

Control flow: `LoadBalance.actor.h` increments counters and calls type-specific compare/trace hooks after both source and TSS/replica responses complete. Detailed mismatch recording is rate-limited to a small number per metrics interval.

State and persistence behavior: Metrics and detailed mismatches are in-memory and reference-counted. Detailed mismatch data can be later surfaced through database context or traces; this header itself does not persist it.

Dependencies and integration points: Depends on `Stats.h`, `DDSketch`, and unordered maps. It is the decoupling layer between generic fdbrpc load balancing and storage-specific comparison logic in storage server interface code.

Risks: Missing template specializations cause link/build failures for new request types used with TSS comparison. `shouldRecordDetailedMismatch()` increments the mismatch counter as a side effect. Detailed mismatch vectors can grow within intervals if callers do not clear as expected.

Test signals: Counter increments by error/timeout/mismatch path, latency sketch updates by request type, detailed mismatch throttling/clear, and concrete compare/trace specializations for every request type that enables TSS or replica comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TSSComparison.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TimedRequest.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TimedRequest.h

Purpose: Provides a base/helper carrying the server-side request receipt time for RPC request structs.

Important APIs/types/functions: `TimedRequest` stores `_requestTime`, exposes `requestTime()` with an assertion that it is positive, and `setRequestTime()`. Its constructor records `g_network->timer()` when not running as a client; clients initialize time to zero.

Control flow: Construction decides whether to stamp the request based on `FlowTransport::isClient()`. Consumers can later read the request time after server-side construction or explicit setting.

State and persistence behavior: Only per-request in-memory timestamp state. No serialization is defined in this header; derived request serialization must handle any required timing fields separately if needed.

Dependencies and integration points: Depends on Flow network and `fdbrpc.h` for `FlowTransport`. Request types can inherit or embed it to measure request queue/processing latency.

Risks: Calling `requestTime()` on a client-created object before `setRequestTime()` asserts. The timer source is process-local/simulation aware; comparisons must use compatible clocks.

Test signals: Client vs server constructor behavior, explicit `setRequestTime()`, assertion coverage for unset reads, and latency measurement integration in request handlers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TimedRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TraceFileIO.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TraceFileIO.h

Purpose: Declares debug hooks that track file contents in memory and validate reads/writes/truncates against expected data.

Important APIs/types/functions: `debugFileCheck(context, file, data, offset, length)` validates a block against tracked state. `debugFileSet(context, file, data, offset, length)` updates tracked bytes. `debugFileTruncate(context, file, offset)` invalidates tracked data after a truncate point.

Control flow: Implementations are elsewhere. File IO paths call set/truncate as writes occur and check when reads or validation points occur, including a context string for trace/debug identification.

State and persistence behavior: The tracked file data is in-memory debug state outside this header. It mirrors durable file mutations for validation but is not the real durable store.

Dependencies and integration points: Depends on Flow base types. Integrated with debug/simulation file IO validation paths.

Risks: If file IO paths miss a set/truncate call, later checks can produce false positives. Large tracked files can consume memory depending on implementation. It should remain debug-only or carefully gated in production.

Test signals: Write/read validation, truncate invalidation, offset/length edge cases, context/file separation, and simulation corruption detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TraceFileIO.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/WellKnownEndpoints.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/WellKnownEndpoints.h

Purpose: Centralizes the reserved well-known endpoint token IDs used by FoundationDB RPC services.

Important APIs/types/functions: `enum WellKnownEndpoints` assigns stable token numbers starting at `WLTOKEN_FIRST_AVAILABLE` for client leader registration, leader election, generation register, protocol info, config transaction/follower services, process endpoint, and reserved count. A static assertion pins `WLTOKEN_PROTOCOL_INFO` to `10`.

Control flow: None at runtime beyond enum use. Request streams call `makeWellKnownEndpoint()` or construct `Endpoint::wellKnown()` with these IDs.

State and persistence behavior: No mutable state. Token values are wire/protocol contracts and must remain unique and stable.

Dependencies and integration points: Depends on `fdbrpc.h` for token definitions. Used by generic hostname actors, leader/config services, and process discovery.

Risks: Reordering or reusing values breaks endpoint compatibility across processes/versions. `WLTOKEN_RESERVED_COUNT` must move only when adding new reserved endpoints.

Test signals: Static assertions/build checks, cross-version endpoint discovery, hostname retry to well-known endpoints, and protocol-info endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/WellKnownEndpoints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/fdbrpc.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/fdbrpc.h

Purpose: Defines the core fdbrpc request/reply primitives that bind Flow futures, streams, serialization, endpoints, failure monitoring, and transport delivery.

Important APIs/types/functions: `FlowReceiver` owns endpoint registration and peer references. `NetSAV<T>` receives serialized `ErrorOr<EnsureTable<T>>` replies into a Flow single-assignment variable. `ReplyPromise<T>` is the serializable reply endpoint wrapper. `AcknowledgementReceiver`, `NetNotifiedQueueWithAcknowledgements<T>`, and `ReplyPromiseStream<T>` implement streaming replies with sequence checks and byte acknowledgements. `NetNotifiedQueue<T, IsPublic>` receives request streams, optionally verifying public requests. `RequestStream<T, IsPublic>` sends unreliable messages, reliable `getReply()`, unreliable `tryGetReply()`, reply streams, failure-bounded replies, well-known endpoint registration, and serialization.

Control flow: Local endpoints enqueue directly into local Flow queues; remote endpoints serialize through `FlowTransport::sendUnreliable()` or `sendReliable()`. Reply promises serialize as endpoint tokens, and deserialization creates remote promises plus `networkSender()` for returned futures. `tryGetReply()` races the reply future against failure monitor disconnect/failure signals through `waitValueOrSignal()`. Reply streams exchange an acknowledgement endpoint on first message, enforce monotonically increasing sequence numbers, and throttle senders with `onReady()` based on bytes sent minus acknowledged.

State and persistence behavior: Endpoint registrations, peer references, queue contents, byte counters, and SAV reference counts are in-memory transport state. There is no durable persistence, but endpoint tokens are serialized across the network and are protocol-relevant.

Dependencies and integration points: Depends on Flow futures/queues/serialization/task priorities, `FlowTransport`, `FailureMonitor`, `networkSender`, simulator, and generic actors. Almost every fdbrpc interface struct uses `RequestStream`, `ReplyPromise`, or `ReplyPromiseStream`.

Risks: Reference-count ownership is delicate; destructors remove endpoints or peer references and send broken promises for cancelled streams. Public streams require `T::verify()` or fail static assertion. `ReplyPromiseStream::isError()` appears to return `!queue->isError()`, so users should verify semantics. Sequence mismatch or missing acknowledgement endpoints can break streaming. Reliable send cancellation must be paired on every path.

Test signals: Local and remote request/reply, serialization/deserialization of promises and streams, public request verification rejection, failure monitor unauthorized/disconnect paths, reliable send cancellation, stream acknowledgement throttling, sequence mismatch detection, stream cancellation/broken-promise behavior, and task-priority endpoint creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/fdbrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/genericactors.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/genericactors.h

Purpose: Provides coroutine/actor utility functions used by fdbrpc request/reply flows, especially retrying well-known endpoints, hostname resolution, promise forwarding, broadcasts, stream termination, and failure-raced waits.

Important APIs/types/functions: `retryBrokenPromise()` retries `getReply()` after broken promises. `tryGetReplyFromHostname()` and `retryGetReplyFromHostname()` resolve hostnames to well-known endpoints and clear DNS cache on connection failures. `timeoutWarning()` emits periodic warning signals while waiting. `forwardPromise()` overloads bridge futures to promises/reply promises/promise streams. `broadcast()` and incremental broadcast helpers fan out one result. `PeerHolder` tracks outstanding peer replies. `endStreamOnDisconnect()`, `waitValueOrSignal()`, `sendCanceler()`, and `reportEndpointFailure()` implement lower-level failure handling for fdbrpc primitives.

Control flow: Retry helpers loop, reset reply promises, delay/jitter/back off, and re-resolve hostnames as needed. `waitValueOrSignal()` races a value future with a failure signal and peer disconnect, converting failures into `ErrorOr` results and notifying the failure monitor on broken promises. `sendCanceler()` waits for a reliable reply while cancelling the reliable packet on completion or permanent failure.

State and persistence behavior: No durable state. Runtime state includes retry intervals, held peers, promise references, and DNS cache invalidation through the external `removeCachedDNS()`.

Dependencies and integration points: Includes Flow generic actors/coroutine utilities, `fdbrpc.h`, `WellKnownEndpoints`, `FailureMonitor`, and hostname resolution. It is included at the bottom of `fdbrpc.h`, so these helpers participate in core RPC behavior.

Risks: Retry loops can spin without the jitter/backoff knobs. Hostname cache invalidation must occur only on connection-like failures. `PeerHolder` outstanding reply counts must stay balanced. Error conversion in `waitValueOrSignal()` determines at-most-once retry safety.

Test signals: Broken-promise retry, hostname lookup failure, re-resolution after request_maybe_delivered, timeout warning cadence, promise forwarding success/error, incremental broadcast yielding, stream disconnect termination, peer disconnect handling, and reliable packet cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/genericactors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncGrpcClient.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncGrpcClient.h

Purpose: Provides a Flow-friendly asynchronous wrapper around generated gRPC service stubs when `FLOW_GRPC_ENABLED` is set.

Important APIs/types/functions: `AsyncGrpcClient<ServiceType>` stores an `AsyncTaskExecutor`, gRPC channel, and service stub. It defines RPC member-function pointer aliases for unary, server-streaming, and client-streaming calls. Constructors create insecure or credential-provider-backed channels. `call()` overloads support unary status-with-output, unary response-as-future, and server-streaming response streams.

Control flow: Calls assert they start on the Flow network thread, then post blocking gRPC operations to the executor. Unary calls create a `ThreadReturnPromise`, execute the stub method on a worker, and send either response/status or `grpc_error()`. Server-streaming calls read responses in a loop, cancel the gRPC context if the Flow stream is abandoned, and end with `end_of_stream()` or `grpc_error()`.

State and persistence behavior: Runtime state is the channel, stub, executor, and per-call promises. No durable state.

Dependencies and integration points: Depends on gRPC C++ headers, Flow thread promises, `AsyncTaskExecutor`, and `Credentials`. It bridges blocking gRPC APIs into Flow futures/streams for fdbrpc components that use gRPC.

Risks: Response pointers in the status-with-output overload must remain valid until the worker completes. The client captures `this` in posted work, so client lifetime must outlive in-flight calls. gRPC status details are collapsed to `grpc_error()` in some overloads. Blocking calls on too few executor threads can serialize work.

Test signals: Unary success/status failure, response pointer lifetime, abandoned future/stream behavior, server-streaming end-of-stream, gRPC cancellation, secure/insecure channel creation, and assertion that calls originate from the network thread.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncGrpcClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncTaskExecutor.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncTaskExecutor.h

Purpose: Implements a lightweight Flow-compatible task executor backed by `IThreadPool`, used primarily to offload blocking gRPC work.

Important APIs/types/functions: `IsVoidReturn` is a C++20 concept distinguishing void-return tasks. `AsyncTaskExecutor` creates a generic thread pool with a requested number of receiver threads, stops it in the destructor, and exposes `post()` overloads for non-void tasks returning `Future<R>` and noexcept void tasks returning nothing. Internal `Action<Func>` specializations implement `ThreadAction` for non-void and void tasks.

Control flow: Posting asserts the caller is on the main network thread, wraps the callable in a heap-allocated `ThreadAction`, and submits it to the pool. Non-void actions execute the function, send result through `ThreadReturnPromise`, convert Flow `Error` or unknown exceptions to future errors, then delete themselves. Void actions execute a noexcept function and delete themselves.

State and persistence behavior: State is the executor-owned thread pool and per-action heap objects/promises. No durable state.

Dependencies and integration points: Depends on Flow network-thread checks and `IThreadPool`. Used by `AsyncGrpcClient` and potentially other blocking integrations.

Risks: Void tasks must be nothrow by API constraint; throwing would violate assumptions. Posted lambdas can outlive captured objects. The executor destructor stops the pool, so callers need clear ownership around in-flight tasks. Simulation determinism requires careful thread count choices.

Test signals: Non-void success and exception propagation, void task execution, main-thread assertion, destructor stop behavior, multiple thread execution, and simulation mode with one thread.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncTaskExecutor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/Credentials.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/Credentials.h

Purpose: Defines credential providers for gRPC channels/servers, including insecure credentials and TLS/mTLS credentials with dynamic or static certificate sources.

Important APIs/types/functions: `GrpcCredentialProvider` declares `serverCredentials()`, `clientCredentials()`, and `validate()`. `GrpcInsecureCredentialProvider` returns insecure server/channel credentials. `GrpcTlsCredentialProvider` builds a `FileWatcherCertificateProvider` from `TLSConfig` key/cert/CA paths, configures server mTLS, watches roots and identity pairs, and returns TLS credentials. `GrpcTlsCredentialStaticProvider` uses in-memory key/cert/CA strings through `StaticDataCertificateProvider`, primarily for tests.

Control flow: TLS providers initialize certificate providers and options in constructors. Credential accessors build gRPC server/channel credentials from stored options. `validate()` delegates to provider credential validation.

State and persistence behavior: Dynamic TLS provider watches certificate files and reloads from the filesystem. Static provider stores credential material in memory. No repository/database persistence.

Dependencies and integration points: Enabled only under `FLOW_GRPC_ENABLED`; depends on gRPC experimental TLS APIs, Flow knobs for refresh delay, and `TLSConfig`. Used by gRPC server/client setup, including `AsyncGrpcClient`.

Risks: gRPC experimental APIs and watch behavior can change. mTLS is always required for TLS server options, so clients must present valid certificates. Static provider comments indicate watch calls are still needed even for static data, which is a subtle test/runtime dependency. Credential validation must be checked before accepting configuration.

Test signals: Insecure credentials creation, dynamic provider validation against cert files, certificate rotation, static provider validation, mTLS client rejection without certs, and refresh-delay behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/Credentials.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/networksender.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/networksender.h

Purpose: Implements the coroutine that serializes a reply future back to a remote `ReplyPromise` endpoint.

Important APIs/types/functions: `networkSender<T>(Uncancellable, Future<T> input, Endpoint endpoint, ExplicitVoid = {})` awaits a future and sends either `ErrorOr<EnsureTable<T>>(value)` or an error to the endpoint via `FlowTransport::sendUnreliable()`.

Control flow: Await input; on success send serialized value. On `never_reply`, return without sending. On other Flow errors, assert the error is not `actor_cancelled` and send serialized error.

State and persistence behavior: No state beyond the awaited future and target endpoint. It sends a network message but does not persist data.

Dependencies and integration points: Depends on `FlowTransport`, Flow coroutines, endpoint serialization, and is invoked when deserializing `ReplyPromise<T>` in `fdbrpc.h`.

Risks: It uses unreliable send for replies; higher-level request semantics must handle missing replies/failures. Actor cancellation is asserted as invalid here. `never_reply` intentionally drops the reply, which callers must use only when that behavior is expected.

Test signals: Successful remote reply delivery, error reply delivery, `never_reply` suppression, actor-cancelled assertion coverage, and serialization table compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/networksender.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/sim_validation.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/sim_validation.h

Purpose: Declares simulator-only durability and version-validation debug hooks for checking restored committed versions and version timestamps after failures.

Important APIs/types/functions: Version range functions include `debug_advanceCommittedVersions()`, min/max advance helpers, `debug_setVersionCheckEnabled()`, `debug_removeVersions()`, `debug_versionsExist()`, and restored version checks for exact/min/max. Relocation-duration toggles are `debug_isCheckRelocationDuration()` and `debug_setCheckRelocationDuration()`. Version timestamp hooks are `debug_advanceVersionTimestamp()` and `debug_checkVersionTime()`.

Control flow: Implementations maintain perfectly durable simulator metadata. Production/non-simulation calls have no effect or validation meaning according to the header comment. Callers advance max before commit, min after commit, and check restored versions after recovery/reboot.

State and persistence behavior: State is simulator magic durable metadata, not normal process memory durability. It models what should survive simulated faults.

Dependencies and integration points: Depends on Flow random UID and trace severity. Used by commit/recovery tests and simulator validation policies.

Risks: Missing advance/check calls can hide durability regressions or produce false failures. Checks are meaningful only in simulation, so production code should not rely on them. Severity choice controls whether validation is fatal or warning-like.

Test signals: Simulated commit/reboot/recovery scenarios, min/max restored version checks, disabled checks, removed version state, relocation-duration toggle, and version timestamp consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/sim_validation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/simulator.h -->
## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/simulator.h

Purpose: Declares the main simulation policy and simulator interfaces used to create processes/machines, inject network/disk/process failures, track roles/exclusions, simulate HTTP, and provide a simulated file system.

Important APIs/types/functions: `ISimulationPolicy` defines process-protection, availability, datacenter death, version validation, corruption, swap, capability, and kill-permission hooks. `ISimulator : INetwork` exposes process/machine creation, scheduling (`onProcess`, `onMachine`), kill/reboot APIs at interface/machine/zone/DC/datahall/all scopes, availability and address exclusion queries, network clog/disconnect controls, process/machine lookup/destruction, SimHTTP registration, simulation policy access, protected address tracking, role add/remove/query, cleared/excluded/switched-cluster state, swap disabling, process-global access, and connection-failure disabling helpers. Globals include `g_simulator`, `simulationPolicyHasCapability()`, startup helpers, `DiskParameters`, `waitUntilDiskReady()`, connection failure enable/disable/extend, `getMaxSatelliteLogs()`, and `Sim2FileSystem`.

Control flow: Simulator implementations schedule process actors, enforce policy when killing, mutate role/exclusion/cleared/switch maps with trace events, and route network/file operations through simulated implementations. `simulationPolicyHasCapability()` checks that the network is simulated, a simulator exists, and a policy is installed before querying capabilities. Connection failure helpers manipulate simulator-wide clogging disable windows.

State and persistence behavior: Extensive in-memory simulation state includes current process thread-local pointers, process/machine lists in implementations, role/exclusion/cleared/switch maps, protected addresses, disabled maps, auth keys, corrupted blocks, HTTP handlers, and simulated file-system metadata. `Sim2FileSystem` performs simulated file operations, not host durable operations.

Dependencies and integration points: Depends on Flow networking, histograms, chaos metrics, protocol versions, async files, HTTP, failure monitor, locality, replication policy, and simulator kill types. It is used by simulation tests and by runtime code that needs to branch on simulation capabilities.

Risks: Thread-local `currentProcess` and `isMainThread` are explicitly subtle in a deterministic simulator. Kill-type policy downgrades must preserve fault model invariants. Role/exclusion reference counts must balance. Connection failure disabling can mask important network faults if not re-enabled. Simulation-only state should not leak assumptions into production code.

Test signals: Process/machine lifecycle, kill/reboot scopes, policy protection/downgrade, role add/remove balancing, exclude/include/clear/switch cluster behavior, clog/disconnect/reconnect, connection-failure disable/extend timing, simulated disk delay, SimHTTP registration, simulated file operations, corruption injection, and capability-gated behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/simulator.h -->
