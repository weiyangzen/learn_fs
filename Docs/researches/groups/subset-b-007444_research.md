# Research: subset-b-007444

This grouped report covers Hadoop HDFS Router-Based Federation metrics, resolver, destination ordering, and selected router connection/erasure-coding support files. Each section is source-tree aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RBFMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RBFMetrics.java

Purpose: `RBFMetrics` is the Router-Based Federation metrics/JMX collector. It implements `RouterMBean` and `FederationMBean`, registers `Router` and `FederationState` MBeans, registers a Metrics2 source named `RBFActivity`, and exposes router identity, state-store records, namespace capacity, datanode/block counters, token/security information, safemode state, and JSON summaries for Namenodes, nameservices, mount table records, and routers.

Important APIs and functions: the constructor wires `Router`, `ActiveNamenodeResolver`, `StateStoreService`, `MembershipStore`, `MountTableStore`, and `RouterStore`, then reads knobs such as datanode report timeout, `getNodeUsage` enablement, and top token owner count. Public MBean methods include `getNamenodes`, `getNameservices`, `getMountTable`, `getRouters`, aggregate capacity/count getters, `getNodeUsage`, router build/identity getters, delegation-token getters, and safemode helpers. Private helpers aggregate active membership stats, fetch namespace metadata, serialize `BaseRecord` fields by reflection, and format timestamps.

Control flow and state: most methods are read-only snapshots over the state store or router runtime. JSON methods fetch records, sort them for deterministic output, enrich fields such as heartbeat age or used space, and return `"{}"` or `"[]"` on store absence or IO failure. Aggregate metrics call `getActiveNamenodeRegistrations`, which resolves the first prioritized Namenode per namespace via `ActiveNamenodeResolver`. `getNodeUsage` optionally fans out through `RouterRpcServer` and supports async RPC through `syncReturn`.

Dependencies and integration points: this class sits between Metrics2/JMX, the Router service, state-store record stores, `MembershipStats`, Router security manager, and Router RPC server. It depends on the resolver package for current Namenode selection and on store protocol request/response classes for record enumeration.

Risks: reflection-based JSON export can break if record getter names or return types behave unexpectedly and throws `IllegalArgumentException` per field. Aggregation assumes the first resolver result is the desired active or most eligible Namenode. Many errors are logged and converted to zero/empty output, which is safe for UI availability but can mask monitoring regressions. `getDateString` treats input as Java milliseconds despite a stale comment saying seconds. Async `getNodeUsage` depends on correct `syncReturn` pairing.

Test signals: existing coverage should exercise JMX registration/close, empty or unavailable stores, JSON output for membership/mount/router records, big integer capacity aggregation, `getNodeUsage` disabled/enabled paths, token metrics with null security manager, and reflection serialization. `@VisibleForTesting` exposes `setEnableGetDNUsage` and `getDateString`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RBFMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RouterMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RouterMBean.java

Purpose: `RouterMBean` defines the private evolving JMX surface for router-specific information exported by `RBFMetrics`.

Important APIs: it declares getters for router start time, version, compile date/info, host/port, router ID/status, cluster IDs, block pool IDs, current delegation-token count, safemode text, security enablement, top token owners, federation rename job count, and scheduler job count.

Control flow and state: this is a pure interface with no state or persistence. Its behavior is supplied by `RBFMetrics`, which registers it as a `StandardMBean` under the Router domain.

Dependencies and integration points: only Hadoop classification annotations are imported. The method names are part of JMX naming, so callers and dashboards depend on these exact getter signatures.

Risks: adding/removing methods changes the JMX contract. Return values are deliberately simple strings, booleans, ints, and longs, so richer structured data has to be encoded by the implementation.

Test signals: tests should validate that `RBFMetrics` implements every method and that MBean registration exposes expected attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RouterMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMBean.java

Purpose: `StateStoreMBean` is the JMX contract for State Store operation metrics.

Important APIs: it exposes operation counts and average latencies for reads, writes, failures, and removes: `getReadOps`, `getReadAvg`, `getWriteOps`, `getWriteAvg`, `getFailureOps`, `getFailureAvg`, `getRemoveOps`, and `getRemoveAvg`.

Control flow and state: this is a stateless interface. `StateStoreMetrics` implements the methods by reading Metrics2 `MutableRate` snapshots.

Dependencies and integration points: Hadoop private/evolving annotations mark the management contract. State store drivers and monitoring code indirectly depend on these names.

Risks: these methods expose last Metrics2 interval stats rather than lifetime totals, because the implementation calls `lastStat`. Consumers must understand the rolling-window semantics.

Test signals: validate that `StateStoreMetrics` updates operation rates and that JMX getters reflect samples after read/write/remove/failure increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMetrics.java

Purpose: `StateStoreMetrics` implements State Store Metrics2 and JMX metrics for transaction latency/count, per-record cache sizes, location cache counters, and cache loading durations.

Important APIs and state: `create(Configuration)` registers a Metrics2 source. `addRead`, `addWrite`, `addRemove`, and `addFailure` append latency samples to `MutableRate`s. Getter methods expose sample count and mean from the last stats interval. `setCacheSize` lazily creates `MutableGaugeInt`s keyed as `Cache<name>Size`; `setLocationCache` lazily creates `MutableGaugeLong`s; `setCacheLoading` lazily creates `MutableRate`s keyed as `Cache<name>Load`. `getCacheLoadMetrics` and `reset` are visible for testing.

Control flow and persistence: metrics are process-local, held in Metrics2 mutable objects and not persisted. `shutdown` shuts down `DefaultMetricsSystem` and resets rates. The protected no-arg constructor supports test/proxy creation but leaves fields dependent on Metrics2 injection.

Dependencies and integration points: State Store drivers call the add/set methods. `MountTableResolver.loadCache` writes location cache access/miss counters through this class. Metrics2 annotations and registry tags expose session/process metadata.

Risks: `shutdown` calls global `DefaultMetricsSystem.shutdown`, which can affect more than just this source in embedded tests. `reset` assumes `reads/writes/removes/failures` are non-null. Cache metric maps are not synchronized; expected use is metrics-thread friendly but concurrent lazy creation can race.

Test signals: cover operation sample counts/averages, dynamic gauge creation and updates, cache load rate creation, `reset`, and interactions from mount table cache metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/package-info.java

Purpose: package descriptor for Router-Based Federation metrics.

Important APIs: applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.metrics`, documenting that the package reports Router-based Federation metrics.

Control flow and state: no executable logic, mutable state, or persistence.

Dependencies and integration points: classification annotations communicate API compatibility expectations to developers and downstream consumers.

Risks: only documentation/annotation drift. The package-level privacy/evolving status is the important contract.

Test signals: none at runtime; source checks may verify package annotations or generated docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/ActiveNamenodeResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/ActiveNamenodeResolver.java

Purpose: `ActiveNamenodeResolver` is the real-time resolver contract for finding eligible Namenodes by nameservice or block pool and for publishing Namenode liveness/state into the State Store.

Important APIs: callers can mark an address unavailable or active, get prioritized Namenode contexts for a nameservice with optional observer-first ordering, get contexts by block pool, register heartbeat/status reports, list active namespaces, list disabled namespaces, set the parent router ID, and rotate cached priority after a bad target.

Control flow and state: interface only. `MembershipNamenodeResolver` is the implementation in this subset and uses State Store membership/disabled namespace records plus in-memory caches.

Dependencies and integration points: used by `RouterRpcServer` to choose target Namenodes, `NamenodeHeartbeatService` to register reports, `RBFMetrics` for namespace aggregation, and `ErasureCoding` for all-namespace fan-out.

Risks: the contract allows `null` lists in the implementation despite comments saying empty lists, so callers must defensively handle both. Ordering semantics are central to failover and observer reads.

Test signals: implementation tests should cover active/observer/standby/unavailable priority, disabled namespace filtering, block-pool lookup, cache rotation, and heartbeat registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/ActiveNamenodeResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeContext.java

Purpose: `FederationNamenodeContext` abstracts a discovered Namenode registration and its routing metadata.

Important APIs: getters expose RPC, service RPC, lifeline, web scheme/address, nameservice ID, namenode ID, state, last modification time, namespace, block pool, cluster, and related identity/state fields used by resolver comparators and router clients.

Control flow and state: this is a data access interface; concrete State Store records such as `MembershipState` implement it. No persistence exists here, but implementations usually represent State Store membership rows.

Dependencies and integration points: consumed by `NamenodePriorityComparator`, `MembershipNamenodeResolver`, `RBFMetrics`, and router RPC selection paths.

Risks: comparator behavior and cache keys depend on stable getter values. Date modified is used as a tie breaker, so stale or skewed timestamps affect routing priority.

Test signals: contract tests should ensure `MembershipState` supplies all fields used by resolver ordering and metrics serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeServiceState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeServiceState.java

Purpose: enum representing Namenode service state in federation. Its declaration order is the resolver priority order.

Important APIs: states include high-priority routable states such as `ACTIVE`, `OBSERVER`, and `STANDBY`, plus degraded/admin states such as `UNAVAILABLE`, `EXPIRED`, and `DISABLED`. `getState(HAServiceState)` maps HA protocol states to federation states, returning `ACTIVE`, `OBSERVER`, or `STANDBY`.

Control flow and state: stateless enum. `NamenodePriorityComparator` uses enum ordering directly, so any reordering changes routing behavior.

Dependencies and integration points: bridges HA service state from Namenode monitoring into State Store membership records and router selection.

Risks: declaration order is behavioral. Missing or new HA states default to standby-style handling unless mapping is updated. `EXPIRED` and `DISABLED` need explicit filtering/marking in resolver logic.

Test signals: assert HA mapping and priority comparator ordering, especially observer-read behavior and disabled namespace marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeServiceState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamespaceInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamespaceInfo.java

Purpose: immutable value object for a federated namespace, carrying block pool ID, cluster ID, and nameservice ID while extending `RemoteLocationContext`.

Important APIs: constructor accepts block pool, cluster, and nameservice. `getNameserviceId`, `getDest`, and `getSrc` return the nameservice ID for routing-context compatibility. Additional getters expose cluster and block pool. `equals`, `hashCode`, and `compareTo` order by nameservice, then cluster, then block pool.

Control flow and state: no mutable state after construction. It is used in sets and maps for namespace fan-out and metrics aggregation.

Dependencies and integration points: returned by `ActiveNamenodeResolver.getNamespaces`, used by `RBFMetrics`, `ErasureCoding`, and router RPC clients invoking concurrent operations across namespaces.

Risks: equality includes all three IDs, so inconsistent State Store namespace metadata can create duplicate-looking nameservice entries. `getDest`/`getSrc` returning nameservice ID is convenient but can surprise code expecting a path.

Test signals: equality/hash/compare ordering, TreeSet behavior, and fan-out maps keyed by `FederationNamespaceInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamespaceInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FileSubclusterResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FileSubclusterResolver.java

Purpose: `FileSubclusterResolver` is the router contract for resolving a global federation path to one or more remote subcluster paths and for listing mount children.

Important APIs: `getDestinationForPath` returns a `PathLocation`, `getMountPoints` lists immediate child mount names under a path, and `getDefaultNamespace` exposes fallback namespace. The static `getMountPoints(String, Set<String>)` computes direct children from mounted path keys.

Control flow and state: interface only, with one static helper. `MountTableResolver` implements the contract using State Store mount table records and an in-memory path tree.

Dependencies and integration points: used on the `RouterRpcServer` request path to translate client HDFS paths before invoking Namenodes. Multi-destination resolution integrates with the `resolver.order` package.

Risks: path normalization and direct-child computation must match mount table semantics. Incorrect fallback/default namespace behavior can route requests outside configured mounts.

Test signals: child mount listing for root/non-root paths, default namespace behavior, and thrown `RouterResolveException` when no mount and default namespace disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FileSubclusterResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MembershipNamenodeResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MembershipNamenodeResolver.java

Purpose: `MembershipNamenodeResolver` implements `ActiveNamenodeResolver` and `StateStoreCache` using State Store membership and disabled-nameservice records.

Important APIs and state: it holds lazy `MembershipStore` and `DisabledNameserviceStore` handles, a router ID for heartbeat registration, and two concurrent caches: nameservice plus observer-first flag to Namenode contexts, and block pool ID to contexts. `loadCache` refreshes underlying stores then clears both caches. `registerNamenode` converts `NamenodeStatusReport` into `MembershipState` and optional `MembershipStats`, then sends a heartbeat. `getNamespaces` filters disabled namespace IDs.

Control flow: lookup methods first check caches, query membership records on miss, filter expired/unavailable depending on parameters, sort by `NamenodePriorityComparator`, optionally move/shuffle observers ahead, mark disabled namespaces, and cache results. `updateNameNodeState` finds the matching membership record by nameservice/RPC address and writes an active/unavailable state update, invalidating affected caches. `rotateCache` demotes an inaccessible Namenode unless an active target is present.

Dependencies and integration points: State Store stores/protocols, `MembershipState`, `MembershipStats`, resolver comparator/state enum, and Router heartbeat services. Metrics and Router RPC paths depend on its priority results.

Risks: implementation sometimes returns `null` for no eligible Namenodes. `cacheNS` stores the mutable `result` list rather than the unmodifiable wrapper, and `rotateCache` casts cached lists to mutable lists. Observer shuffling is deliberate nondeterminism. Cache invalidation for block pool is broad because namespace-to-block-pool lookup is costly.

Test signals: cache refresh invalidation, active/unavailable updates, observer-first shuffling, disabled namespace filtering, heartbeat stats mapping, null/empty result handling, and rotate-cache behavior when active entries exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MembershipNamenodeResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableManager.java

Purpose: `MountTableManager` is the management interface for router mount table CRUD and cache refresh operations.

Important APIs: methods map to protocol request/response pairs for adding, updating, removing, retrieving, listing, refreshing, and validating mount table entries. It is a resolver-side contract consumed by router admin paths and State Store-backed managers.

Control flow and state: no implementation here. Persistence is expected in State Store mount table records through implementing classes.

Dependencies and integration points: store protocol classes under `org.apache.hadoop.hdfs.server.federation.store.protocol` and admin tooling such as `RouterAdmin`.

Risks: this is an administrative API contract; response/result semantics must stay stable for CLI and service callers. Validation and refresh behavior are implementation-defined.

Test signals: implementer tests should cover each request/response operation, authorization if applied elsewhere, State Store failure propagation, and cache refresh side effects in `MountTableResolver`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableResolver.java

Purpose: `MountTableResolver` implements path-to-subcluster resolution over State Store mount table records. It maps global federation paths to `PathLocation` objects and serves the hot Router RPC path.

Important APIs and state: constructors accept configuration plus optional `Router` or `StateStoreService`, configure optional Guava `locationCache`, register as an external State Store cache, and initialize default nameservice fallback. Mutable state includes an initialized/disabled flag, `TreeMap<String, MountTable>` path tree, cache hit/miss counters, default nameservice settings, and a read/write lock. Public APIs add/remove/refresh entries, load cache, clear, resolve paths, list mount points/mounts, and expose test knobs.

Control flow: `loadCache` refreshes the store cache, fetches all entries from `/`, calls `refreshEntries`, and publishes location-cache counters to `StateStoreMetrics`. `refreshEntries` atomically diffs new entries against the tree, removes stale entries leaf-first, adds/updates changed entries, and invalidates affected cache entries. `getDestinationForPath` verifies initialization, normalizes trash paths, consults or populates the path cache, and rewrites trash results back to the original path. `lookupLocation` finds the deepest mount and builds remote paths or falls back to the default namespace.

Dependencies and integration points: State Store `MountTableStore`, router config keys, `RouterAdmin` path normalization, `FileSystem` trash path conventions, `StateStoreMetrics`, and `RemoteLocation`/`PathLocation` data types.

Risks: this base resolver rejects multi-destination mount entries; callers need `MultipleDestinationMountTableResolver` for that. Cache invalidation is path-sensitive and must cover descendants and default-location entries. `verifyMountTable` fails when disabled or not initialized. Trash processing depends on current remote user. Default namespace fallback can hide missing mount coverage if enabled.

Test signals: mount add/remove/update invalidation, deepest mount matching, trash path processing, default namespace enabled/disabled, cache metrics, concurrent reads/writes, and multi-destination rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MultipleDestinationMountTableResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MultipleDestinationMountTableResolver.java

Purpose: extends `MountTableResolver` to support mount table entries with multiple destinations and to prioritize those destinations by policy.

Important APIs and state: constructor registers `OrderedResolver` implementations in an `EnumMap`: `HASH`, `LOCAL`, `RANDOM`, `HASH_ALL`, `SPACE`, and `LEADER_FOLLOWER`. `getDestinationForPath` delegates to the base resolver, then, for multi-destination results, asks the configured ordered resolver for the first namespace and returns a prioritized `PathLocation`.

Control flow: no persistence beyond inherited mount tree/cache. Ordering is applied per resolution after base path translation. Test helpers allow injecting/retrieving policy resolvers.

Dependencies and integration points: integrates the mount resolver with the `resolver.order` package and `Router` service for policies that need runtime data.

Risks: missing resolver mapping logs an error and leaves original order. Policy failure returning null also leaves original ordering. Order policies can be nondeterministic (`RANDOM`, probabilistic `SPACE`, observer/local runtime data).

Test signals: each `DestinationOrder` should reorder as expected, unknown/missing resolver behavior, and inheritance of base resolver path/trash/default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MultipleDestinationMountTableResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodePriorityComparator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodePriorityComparator.java

Purpose: comparator for ordering Namenode contexts within the same namespace.

Important APIs: `compare` first compares `FederationNamenodeServiceState` enum values, then `compareModDates` reverse-sorts by `getDateModified` so the newest record wins within a state.

Control flow and state: stateless serializable comparator. It relies on the enum declaration order for state priority.

Dependencies and integration points: used by `MembershipNamenodeResolver` to rank membership records returned by the State Store.

Risks: timestamp subtraction is cast to `int`, which can overflow for large millisecond differences. Enum order changes are routing changes. Expired filtering happens before comparator use, not inside it.

Test signals: ordering across active/observer/standby/unavailable states and newest-first tie breaking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodePriorityComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodeStatusReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodeStatusReport.java

Purpose: mutable status DTO populated by Namenode monitoring and consumed by `MembershipNamenodeResolver.registerNamenode`.

Important APIs and state: stores nameservice/namenode IDs, cluster/block pool IDs, RPC/service/lifeline/web endpoints, HA state, safemode, datanode counts, storage/block/file stats, corrupt/low-redundancy metrics, SPS count, and validity flags. Setters include `setHAServiceState`, `setNamespaceInfo`, `setSafeMode`, `setDatanodeInfo`, `setNamesystemInfo`, `setNamenodeInfo`, and `setRegistrationValid`. Getters expose all values for membership/stat construction.

Control flow: `getState` derives federation state: invalid registration becomes `UNAVAILABLE`; valid HA state maps through `FederationNamenodeServiceState.getState`; otherwise it defaults to `ACTIVE`. Stats validity is toggled by datanode or namesystem setters.

Dependencies and integration points: bridges `NamespaceInfo` and HA protocol state into federation membership records. `MembershipNamenodeResolver` copies values into `MembershipState` and `MembershipStats`.

Risks: default values are empty strings or `-1`, so callers must respect validity flags before persisting stats. `setNamenodeInfo` does not set `statsValid` by itself. If HA state is unavailable but registration is valid, defaulting to active is optimistic.

Test signals: state derivation for validity combinations, statsValid transitions, membership stats field mapping, and string representation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodeStatusReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/PathLocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/PathLocation.java

Purpose: immutable-ish mapping from a global federation source path to one or more remote destinations plus a destination ordering policy.

Important APIs: constructors accept source path, destinations, and optional `DestinationOrder` defaulting to `HASH`. `prioritizeDestination` returns a new `PathLocation` with a selected namespace moved first. Getters expose source path, destination namespaces, destinations, order, multi-destination flag, and default location.

Control flow and state: wraps destination lists as unmodifiable at construction and when reordering. `orderedNamespaces` preserves relative order except moving matching namespace(s) to the front. `getDefaultLocation` throws if no valid first destination exists.

Dependencies and integration points: created by mount resolvers and consumed by Router RPC paths and ordered resolvers.

Risks: `getNamespaces` returns a `HashSet`, so random resolver order is intentionally not stable. If multiple destinations share a nameservice, `addFirst` can reverse their relative order. Source path may be null for default namespace fallback.

Test signals: prioritization, multi-destination behavior, default location errors, string rendering with order suffix, and immutability of destination lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/PathLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RemoteLocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RemoteLocation.java

Purpose: value object representing a concrete destination in a remote namespace, including destination path and original federation source path.

Important APIs: constructors support namespace-only, namespace plus explicit namenode, and copying namespace/namenode from an existing location with a new path. `getNameserviceId` appends `-namenodeId` when present, while `getDest` and `getSrc` return remote and federation paths.

Control flow and state: immutable fields, no persistence. The copy-with-path constructor is used for trash path rewrites.

Dependencies and integration points: extends `RemoteLocationContext`, used in `PathLocation`, mount table destinations, router RPC remote invocation, and metrics mount-table summaries.

Risks: `getNameserviceId` conflates nameservice and namenode when `namenodeId` is present, which is intended for specific routing but can surprise policy code expecting only namespace IDs. Copy constructor sets both source and destination to the new path.

Test signals: string formatting, nameservice/namenode rendering, and trash-copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RemoteLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterGenericManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterGenericManager.java

Purpose: small management interface for generic Router operations not specific to mount table or Namenode resolution.

Important API: `refreshSuperUserGroupsConfiguration` refreshes superuser proxy group mappings and returns success or throws `IOException`.

Control flow and state: interface only; implementation owns actual configuration reload and persistence, if any.

Dependencies and integration points: likely exposed through router admin/RPC management paths and security/proxy-user configuration handling.

Risks: success boolean plus exception can lead to ambiguous handling if implementations use both. Refresh affects authorization behavior for RBF.

Test signals: implementation tests should verify config reload, error propagation, and admin permission checks where enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterGenericManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterResolveException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterResolveException.java

Purpose: checked exception indicating `FileSubclusterResolver` could not resolve a path.

Important API: constructor accepts an error message and extends `IOException` with a serial version UID.

Control flow and state: no mutable state. `MountTableResolver.lookupLocation` throws it when no mount matches and default namespace reads/writes are disabled.

Dependencies and integration points: propagates through Router RPC path resolution as an IO failure.

Risks: callers may treat it generically as `IOException`, so diagnostic messages are important.

Test signals: no-default-namespace path resolution should throw this specific type and message should include the unresolved path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterResolveException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/AvailableSpaceResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/AvailableSpaceResolver.java

Purpose: multi-destination ordering policy that biases first destination selection toward subclusters with more available space.

Important APIs and state: extends `RouterResolver<String, SubclusterAvailableSpace>`. It reads `available-space-resolver.balanced-space-preference-fraction` from config, defaulting to `0.6`, and uses `SubclusterSpaceComparator` with a shared `Random`. `getSubclusterInfo` loads all membership registrations and maps namespace to available space. `chooseFirstNamespace` gathers destination namespace space info, sorts probabilistically, and returns the first namespace.

Control flow: mapping refresh is inherited from `RouterResolver` and can run asynchronously. Comparator usually orders higher available space first, but flips based on configured probability to avoid absolute placement.

Dependencies and integration points: relies on `MembershipStore` and `MembershipState.getStats().getAvailableSpace`. Used by `MultipleDestinationMountTableResolver` for `DestinationOrder.SPACE`.

Risks: missing namespace mapping yields null elements and comparator failures. Duplicate membership records for a namespace overwrite earlier entries. Probabilistic comparator can be non-transitive because each compare samples randomness, which may make sort results unstable.

Test signals: config validation for preference range, preference warning below 0.5, namespace selection with mocked stats, and behavior when membership stats are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/AvailableSpaceResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/DestinationOrder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/DestinationOrder.java

Purpose: enum of policies for ordering multiple mount table destinations.

Important APIs: values are `HASH`, `LOCAL`, `RANDOM`, `HASH_ALL`, `SPACE`, and `LEADER_FOLLOWER`. `FOLDER_ALL` identifies policies that require directory creation across all subclusters: `HASH_ALL`, `RANDOM`, `SPACE`, and `LEADER_FOLLOWER`.

Control flow and state: stateless enum with one static `EnumSet`.

Dependencies and integration points: `MountTable` records carry a destination order; `MultipleDestinationMountTableResolver` maps enum values to `OrderedResolver` implementations; router write paths can use `FOLDER_ALL` semantics.

Risks: adding a new enum requires resolver registration and folder/write semantics review. Comments are part of the admin-facing policy meaning.

Test signals: resolver map coverage for every enum value and folder-all behavior for directory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/DestinationOrder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashFirstResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashFirstResolver.java

Purpose: variant of consistent-hash ordering that hashes only the immediate child under the mount point.

Important APIs: overrides `getFirstNamespace` to trim the full path to at most one component below `PathLocation.getSourcePath`, then delegates to `HashResolver`. Private `trimPathToChild` handles parent equality, slash joining, and root-like cases.

Control flow and state: no extra state beyond inherited hash-ring cache. Trimming ensures an entire first-level subtree maps to the same namespace.

Dependencies and integration points: used for `DestinationOrder.HASH`, while `HashResolver` itself is used for `HASH_ALL`.

Risks: correctness depends on source path normalization. If `sourcePath` is null, this policy would fail; multi-destination mount entries should have non-null source paths.

Test signals: trimming examples such as `/a/b/c` under `/a`, exact parent path, trailing slash parent, and hash stability across children below the same first component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashFirstResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashResolver.java

Purpose: `OrderedResolver` that selects the first namespace by consistent hashing over the request path.

Important APIs and state: maintains a concurrent map from namespace-set hash to `ConsistentHashRing`. `getFirstNamespace` normalizes temporary file names with `extractTempFileName`, obtains a hash ring for `loc.getNamespaces`, and returns the ring location. Temp patterns handle `.COPYING`, `._COPYING_`, `.tmp`, `_temp`, UUID `_temporary`, and MapReduce attempt temporary paths.

Control flow: hash ring creation is cached per namespace set hash. Temporary name extraction concatenates non-null regex capture groups from the matched alternative so temp writes hash like final target names.

Dependencies and integration points: used by multi-destination resolver policies and Hadoop federation consistent-hash utility.

Risks: cache key uses only `namespaces.hashCode`, so rare set hash collisions can reuse the wrong ring. Temp regex behavior is complex and should be guarded by tests. Namespace set order is irrelevant to hashing but affects hash-code collision risk.

Test signals: temp name extraction matrix, stable namespace selection for same path/set, different namespace set ring creation, and null return logging when ring lookup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LeaderFollowerResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LeaderFollowerResolver.java

Purpose: ordering policy for disaster-tolerant leader/follower mount entries where the first configured destination is the leader.

Important API: `getFirstNamespace` returns `loc.getDefaultLocation().getNameserviceId`, logging and returning null on failure.

Control flow and state: stateless; all ordering meaning comes from administrator-provided destination order in the mount table.

Dependencies and integration points: registered for `DestinationOrder.LEADER_FOLLOWER` in `MultipleDestinationMountTableResolver`. Directory creation semantics include this order in `FOLDER_ALL`.

Risks: no health or space check is performed; failover is left to later sequential invocation behavior. Misordered mount entries make the wrong cluster leader.

Test signals: first destination selection, empty destination failure, and preservation of configured order after prioritization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LeaderFollowerResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LocalResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LocalResolver.java

Purpose: `RouterResolver` policy that prefers the subcluster local to the RPC caller, based on datanode/namenode address mappings.

Important APIs: `getSubclusterInfo` merges datanode-to-subcluster data from Namenode datanode reports with namenode-host mappings from `MembershipStore`. `chooseFirstNamespace` uses `Server.getRemoteAddress` to map the client address to a namespace. `getDatanodesSubcluster` runs as the login user and supports async router RPC via `syncReturn`. `getNamenodesSubcluster` maps hostnames, resolved IPs, and local loopback to namespace IDs.

Control flow and state: mapping refresh is inherited and throttled by `RouterResolver`. The resolver returns null when it cannot map the caller.

Dependencies and integration points: `RouterRpcServer`, `MembershipStore`, `DatanodeStorageReport`, `MembershipState`, Hadoop RPC server remote address, UGI privileged action, and Guava `HostAndPort`.

Risks: expensive datanode report fan-out, DNS/hostname mismatches, null `dnMap` not explicitly checked before iteration, and local address mapping assumptions. Async calls must pair correctly with `syncReturn`.

Test signals: mocked client address mapping, datanode report mapping, namenode hostname/IP mapping including 127.0.0.1, no RPC server behavior, and refresh throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LocalResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/OrderedResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/OrderedResolver.java

Purpose: common policy interface for choosing the first namespace when a `PathLocation` has multiple destinations.

Important API: `getFirstNamespace(String path, PathLocation loc)` returns the namespace ID to prioritize, or null if no decision can be made.

Control flow and state: interface only. Implementations are hash, local, random, space-biased, and leader/follower strategies.

Dependencies and integration points: invoked by `MultipleDestinationMountTableResolver`, which rewrites destination order through `PathLocation.prioritizeDestination`.

Risks: returning null leaves original order and logs errors at the caller. Implementations must use namespace identifiers compatible with `RemoteLocation.getNameserviceId`.

Test signals: resolver implementations should be tested through this interface and through multi-destination mount resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/OrderedResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RandomResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RandomResolver.java

Purpose: `OrderedResolver` that randomly chooses a namespace among a location's destination namespaces.

Important API: `getFirstNamespace` validates the namespace set with `CollectionUtils.isEmpty`, chooses an index with `ThreadLocalRandom`, and returns the indexed element via Guava `Iterables`.

Control flow and state: stateless and intentionally nondeterministic. The source path is ignored.

Dependencies and integration points: registered for `DestinationOrder.RANDOM`; `DestinationOrder.FOLDER_ALL` includes random because folders may need to exist everywhere.

Risks: `PathLocation.getNamespaces` uses a `HashSet`, so index-to-namespace ordering is arbitrary before random selection. Randomness complicates tests and reproducibility.

Test signals: empty/null location returns null and logs; repeated calls should only return configured namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RandomResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RouterResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RouterResolver.java

Purpose: abstract base for ordering policies that need Router/State Store runtime data and cache a subcluster mapping.

Important APIs and state: stores `Router`, minimum update period from config, a cached `subclusterMapping`, and `lastUpdated`. `getFirstNamespace` refreshes mapping then delegates to `chooseFirstNamespace`. Subclasses implement `getSubclusterInfo(MembershipStore)` and `chooseFirstNamespace`.

Control flow: `updateSubclusterMapping` is synchronized. On stale or missing data it starts a `SubjectInheritingThread` to fetch mapping. The first call blocks with `join` until initialized; later refreshes are asynchronous. `getMembershipStore` obtains the registered `MembershipStore` from the Router State Store.

Dependencies and integration points: base for `LocalResolver` and `AvailableSpaceResolver`. It interacts with Router, Router RPC server, State Store service, and membership store.

Risks: asynchronous refresh writes `subclusterMapping` and `lastUpdated` without volatile fields, though synchronized entry gives partial protection for scheduling. If router or state store is null, subclasses may see null mappings. Thread creation per refresh can be costly under many resolver instances.

Test signals: first-call blocking initialization, refresh throttling, stale refresh behavior, null state store handling, and subclass mapping visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RouterResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/package-info.java

Purpose: package descriptor for destination-order resolvers.

Important APIs: applies private/evolving annotations to `org.apache.hadoop.hdfs.server.federation.resolver.order` and documents that the package decides which destination should be used first when federated locations resolve to multiple subclusters.

Control flow and state: no executable logic.

Dependencies and integration points: documents the relationship between multi-destination `PathLocation`s and ordering policy implementations.

Risks: annotation/documentation drift only.

Test signals: none at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/package-info.java

Purpose: package descriptor for federation resolvers.

Important APIs: package-level private/evolving annotations and documentation identify resolvers as performance-sensitive components used in the `RouterRpcServer` request path. It names `ActiveNamenodeResolver` and `FileSubclusterResolver` as principal resolver contracts.

Control flow and state: no executable logic.

Dependencies and integration points: documentation-level integration with Router RPC, State Store, and federation path/name resolution.

Risks: typo/documentation drift only, but package privacy/evolving status guides compatibility expectations.

Test signals: none at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionContext.java

Purpose: wraps a Namenode RPC proxy and tracks concurrent use, recent activity, and closure for a `ConnectionPool`.

Important APIs and state: stores `ProxyAndInfo<?>`, active thread count, closed flag, last active timestamp, active-window constant of 30 seconds, and max concurrency per connection from configuration. `isActive`, `isActiveRecently`, `isClosed`, `isUsable`, `isIdle`, `getClient`, `release`, and `close` are synchronized. `getClient` reserves the connection by incrementing thread count.

Control flow: a caller obtains the proxy through `getClient` and must call `release`. `close(false)` logs if closing with active handlers but still closes to avoid leaks after removal from a pool; `RPC.stopProxy` shuts down the underlying proxy.

Dependencies and integration points: used by `ConnectionPool` and `ConnectionManager`, wraps Hadoop RPC proxies created by `ConnectionPool.newConnection`.

Risks: missing `release` leaks active count and reduces usability. `isActiveRecently` starts true until 30 seconds after construction because `lastActiveTs` defaults to 0 only if monotonic time is below window early in process; normally it becomes false after uptime exceeds the window. Forced close can interrupt active callers.

Test signals: concurrency limit, reserve/release count, idle/active/recent flags, close behavior with active users, and proxy shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionManager.java

Purpose: owns all Router-to-Namenode connection pools, asynchronous connection creation, and periodic cleanup.

Important APIs and state: configuration controls pool max size, minimum active ratio, creator queue size, pool cleanup period, and connection cleanup period. State includes a map of `ConnectionPoolId` to `ConnectionPool`, read/write lock, bounded creator queue, `ConnectionCreator` thread, cleanup executor, `RouterStateIdContext`, and running flag. Public methods start/close the manager, get a connection, expose pool/connection counts, and render JSON.

Control flow: `getConnection` rejects calls when stopped, looks up or creates a pool under locks, advances the pool alignment context with client state ID, asks the pool for a connection, and queues async pool growth if the chosen connection is null or unusable. `CleanupTask` periodically removes stale pools or asks `cleanup(pool)` to close idle excess connections. `ConnectionCreator` takes pools from the queue and creates a new connection only if below max size and recent active ratio justifies growth.

Dependencies and integration points: `ConnectionPool`, `ConnectionPoolId`, `RouterStateIdContext`, `PoolAlignmentContext`, UGI, and Router RPC clients.

Risks: `running` is not volatile but typically controlled by lifecycle thread. Queue dedup uses `contains(pool)` on object identity and may race. Cleanup closes pools under read lock and removes under write lock later. If all connections are busy, `getConnection` can return a busy connection rather than null, relying on per-connection concurrency checks.

Test signals: lazy pool creation, stopped-manager behavior, async creator queue saturation, pool cleanup timing, connection cleanup active-ratio logic, JSON counters, and close shutting down all pools/threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionNullException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionNullException.java

Purpose: checked exception indicating the router could not obtain a non-null connection.

Important API: constructor accepts a message and extends `IOException`.

Control flow and state: no mutable state. Used by higher router RPC code when connection acquisition fails.

Dependencies and integration points: complements `ConnectionManager.getConnection`, which can return null when stopped or unable to provide a usable proxy.

Risks: generic IO handling can hide the specific connection-pool failure unless the message is clear.

Test signals: router RPC client paths should throw or propagate this when connection context is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionNullException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPool.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPool.java

Purpose: maintains multiple RPC proxy connections for one user/token set, Namenode address, and protocol so the Router can multiplex requests across sockets.

Important APIs and state: stores configuration, `ConnectionPoolId`, target address, UGI, protocol, copy-on-write volatile connection list, round-robin client index, socket index for multi-socket mode, min/max sizes, min active ratio, last active time, multi-socket flag, and `PoolAlignmentContext`. `PROTO_MAP` maps public protocols to protobuf protocol and translator classes. Methods get/add/remove/close connections, count active/idle/recent connections, render JSON, and create new RPC connections.

Control flow: constructor creates minimum connections. `getConnection` first returns any usable connection; if none, it returns a round-robin connection even if busy so the manager can decide whether to grow the pool. `addConnection` and `removeConnections` replace the volatile list with a new copy. `newConnection` configures protobuf RPC engine, retry policy, socket, SASL if needed, optional `FederationConnectionId`, translator client, and token service, then wraps it in `ConnectionContext`.

Dependencies and integration points: Hadoop IPC/RPC, protobuf translators, `ClientProtocol`, `NamenodeProtocol`, refresh/get-user-mapping protocols, UGI/tokens, retry config, and alignment context.

Risks: `newProtoClient` can return null after logging, producing a `ConnectionContext` with a null client if not guarded by caller. Copy-on-write list avoids iterator locking but callers can observe stale snapshots. Unsupported protocols throw `IllegalStateException`. Multi-socket identity depends on incrementing socket index.

Test signals: protocol mapping, min connection creation, round-robin fallback, copy-on-write add/remove, only idle removals, multi-socket connection IDs, security-enabled SASL path, and JSON/debug counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPoolId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPoolId.java

Purpose: identity key for a Router connection pool, combining Namenode address, UGI, UGI token IDs, and protocol.

Important APIs and state: constructor caches `ugi.toString()` because it is expensive. `hashCode`, `equals`, `compareTo`, and `toString` include sorted token identifier byte arrays. `getUgi` is visible for testing.

Control flow and persistence: immutable identity object. Token IDs are recomputed on each hash/equality/compare call from current UGI tokens, while the UGI string is cached.

Dependencies and integration points: keys the `ConnectionManager` pool map and JSON output.

Risks: because token IDs are read dynamically, mutating UGI tokens after insertion can change hash/equality behavior and break map lookup. `equals` compares token list string forms while `hashCode` appends the list object; both use sorted contents but rely on consistent conversion.

Test signals: equality/hash/compare with same user/address/protocol, differing tokens, token order independence, and mutation risk if UGI tokens change after construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPoolId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/DFSRouter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/DFSRouter.java

Purpose: command-line entry point for starting an HDFS Router-Based Federation `Router`.

Important APIs: `main` handles help, logs startup/shutdown message, constructs `Router`, registers a composite-service shutdown hook at priority 30, loads configuration, initializes, and starts the router. `getConfiguration` creates `HdfsConfiguration` and adds FedBalance default/site resources.

Control flow and state: static utility class with private constructor. On any throwable during startup, logs and exits via `ExitUtil.terminate(1, e)`.

Dependencies and integration points: Hadoop CLI conventions, `DFSUtil.parseHelpArgument`, `ShutdownHookManager`, `Router`, and FedBalance config resources.

Risks: startup failures terminate the JVM. Resource loading includes FedBalance XMLs, so router behavior can be affected by those configs. No explicit blocking loop is in this class; lifecycle is owned by `Router` services.

Test signals: help argument handling, configuration resource inclusion, shutdown hook registration, and failure path termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/DFSRouter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ErasureCoding.java

Purpose: Router RPC helper implementing ClientProtocol erasure-coding operations over federated namespaces.

Important APIs: all methods wrap a `RemoteMethod` and invoke through `RouterRpcClient`. Cluster-wide operations fan out to `namenodeResolver.getNamespaces`: get/list policies, codecs, add/remove/enable/disable policies, topology verification, and block group stats. Path-specific operations resolve path locations through `RouterRpcServer.getLocationsForPath`: get/set/unset erasure coding policy.

Control flow: read/write operations call `rpcServer.checkOperation` with appropriate `OperationCategory`. Concurrent namespace calls merge arrays or stats where needed. Path writes use concurrent or sequential invocation depending on `rpcServer.isInvokeConcurrent(src)`. Topology verification returns the first unsupported result, otherwise the first namespace result, and throws if no namespace is available.

Dependencies and integration points: `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `FederationNamespaceInfo`, `RemoteLocation`, erasure-coding protocol classes, and `RouterRpcServer.merge`.

Risks: all-namespace writes assume policy operations should be applied everywhere. Codec maps are merged with later entries overwriting same keys. Typo in no-namespace error message is user-visible. Sequential path read returns first successful policy based on path location order.

Test signals: operation category checks, all-namespace fan-out and merge behavior, path concurrent/sequential switching, no-namespace topology error, unsupported topology short-circuit, and EC block group stats merge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ErasureCoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationConnectionId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationConnectionId.java

Purpose: extends Hadoop IPC `Client.ConnectionId` with a socket index so a Router can create multiple distinct physical sockets for the same user/protocol/address.

Important APIs and state: constructor delegates normal connection identity fields to the superclass and stores `index`. `hashCode` appends superclass hash and index; `equals` first requires superclass equality, then requires matching index for another `FederationConnectionId`.

Control flow and persistence: immutable identity object. Used only when multi-socket connection pooling is enabled in `ConnectionPool.newConnection`.

Dependencies and integration points: Hadoop IPC client, retry policy, UGI, configuration, and connection pool socket index.

Risks: equality with a plain superclass `ConnectionId` returns false after superclass equality because the object is not a `FederationConnectionId`, intentionally preventing socket coalescing. Index reuse would collapse sockets.

Test signals: equality/hash differences for different indexes, equality with identical base fields and index, and non-equality against plain `ConnectionId`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationConnectionId.java -->
