# Research group subset-b-007426

This grouped report covers Hadoop HDFS client-side DataNode/NameNode protocol DTOs, HA proxy providers, short-circuit local-read support, and utility helpers. Each source file has a marker-bounded section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkStatus.java

Purpose: `DiskBalancerWorkStatus` is a private, unstable DTO used by DataNode disk balancer status RPCs to report the currently submitted plan, its high-level result, and the per-volume move work items currently in progress. It is primarily a Jackson-serializable envelope around `Result`, `planID`, `planFile`, and a list of `DiskBalancerWorkEntry` records.

Important APIs/types/functions: constructors support empty creation, direct `Result`/plan fields, prebuilt `List<DiskBalancerWorkEntry>`, and parsing the current-state JSON list. `toJsonString()`, `currentStateString()`, and static `parseJson(String)` provide serialization/deserialization. `addWorkEntry()` guards null entries with `Preconditions.checkNotNull`. `Result` enumerates `NO_PLAN`, `PLAN_UNDER_PROGRESS`, `PLAN_DONE`, and `PLAN_CANCELLED` with integer values for protocol/UI compatibility. Nested `DiskBalancerWorkEntry` stores `sourcePath`, `destPath`, and a `DiskBalancerWorkItem`, with JavaBean accessors for Jackson.

Control flow: the object is populated by DataNode disk-balancer code as work starts or progresses, then serialized through static `ObjectMapper`/`ObjectReader` instances. The JSON-list constructor parses a serialized list of work entries via `READER_WORKENTRY`, while whole-object parsing uses `READER_WORKSTATUS`. There is no background execution here; it is a passive status model.

State and persistence behavior: state is in memory until serialized to JSON for RPC/query output. `currentState` is mutable and final only at the field-reference level, so callers can append via `addWorkEntry()` or mutate the returned list. `MAPPER_WITH_INDENT_OUTPUT` is used only for readable current-state output; whole-object JSON is compact.

Dependencies and integration points: depends on Jackson, Hadoop `Preconditions`, and `DiskBalancerWorkItem`. It integrates with the disk balancer status and plan query path in the DataNode, and its nested shape is part of the diagnostic JSON surface consumed by CLI/admin tools.

Risks and test signals: because the current-state list is exposed directly, callers can mutate it without validation. JSON compatibility depends on bean-style getters and default constructor on `DiskBalancerWorkEntry`; renames would affect clients. Tests should cover round-trip JSON for each constructor path, result enum integer values, null rejection in `addWorkEntry`, and parsing of embedded `DiskBalancerWorkItem` JSON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaNotFoundException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaNotFoundException.java

Purpose: `ReplicaNotFoundException` is a DataNode-side `IOException` that signals a requested block replica is absent or not in the expected state for append/recovery operations.

Important APIs/types/functions: it exposes standard message constants for non-RBW, unfinalized, non-existent, and unexpected-generation-stamp replicas. The `ExtendedBlock` constructor builds a user-oriented message including `POSSIBLE_ROOT_CAUSE_MSG`, which points at benign balancer/removal scenarios and advises log inspection. A default constructor and raw-message constructor support generic IOException usage.

Control flow: callers throw this exception when a block lookup or state check fails. The exception itself contains no branching beyond message construction; downstream control is in DataNode/DFSClient recovery code that treats it as an I/O failure.

State and persistence behavior: immutable exception state is carried in the inherited message/cause fields. The static message constants are part of the diagnostic contract used by callers and tests.

Dependencies and integration points: depends on `ExtendedBlock` from HDFS protocol. It integrates with block append, recovery, and replica lookup paths in the DataNode.

Risks and test signals: message text is operationally significant because admins and tests may match it. Tests should assert construction with `ExtendedBlock`, preservation of provided custom messages, and inclusion of the possible-root-cause hint for block-based construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/NotReplicatedYetException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/NotReplicatedYetException.java

Purpose: `NotReplicatedYetException` is a private/evolving `IOException` used by NameNode operations when a file has not yet reached enough DataNode replicas to satisfy an operation.

Important APIs/types/functions: it contains a single `String` constructor and inherits all behavior from `IOException`.

Control flow: NameNode code throws it as a typed transient condition. Callers can catch this exact type to retry or surface a clearer client error rather than treating it as an arbitrary I/O failure.

State and persistence behavior: no custom state beyond the exception message and `serialVersionUID`.

Dependencies and integration points: depends only on Hadoop classification annotations and Java `IOException`. It integrates with file creation/close/replication checks in NameNode code.

Risks and test signals: the main risk is losing typed catch behavior if replaced with a generic exception. Tests should exercise NameNode paths that throw this when replication preconditions are not met and verify client retry/error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/NotReplicatedYetException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/RetryStartFileException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/RetryStartFileException.java

Purpose: `RetryStartFileException` is a private `IOException` indicating that file creation preconditions failed due to a transient condition and that the create/start-file operation should be retried later.

Important APIs/types/functions: it provides a default constructor with a canonical retry message and an overload accepting a custom message.

Control flow: NameNode file creation paths throw it to distinguish retryable transient precondition failures from permanent validation errors.

State and persistence behavior: no custom mutable state; exception message is the only payload.

Dependencies and integration points: depends on Java `IOException` and Hadoop `InterfaceAudience`. It integrates with client retry policies around start-file/create-file RPCs.

Risks and test signals: the exception must remain typed for retry policy discrimination. Tests should verify callers translate this into retry rather than surfacing a hard failure and that custom messages remain intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/RetryStartFileException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeModeException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeModeException.java

Purpose: `SafeModeException` is a private/evolving `IOException` thrown when a NameNode is in safe mode and namespace modifications cannot proceed.

Important APIs/types/functions: it has a single message constructor and a stable `serialVersionUID`.

Control flow: namespace-modifying RPC implementations throw it while safe mode is active. Client layers and admin tools use the type/message to explain why write operations are blocked.

State and persistence behavior: exception state is limited to the inherited message. It does not query safe-mode state itself.

Dependencies and integration points: depends on Hadoop classification annotations and Java `IOException`. It integrates with NameNode safe-mode checks across create, delete, rename, and similar operations.

Risks and test signals: message clarity matters for operators, and typed behavior matters for clients. Tests should cover representative write RPCs in safe mode and verify this exception is propagated or wrapped consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeModeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/AbstractNNFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/AbstractNNFailoverProxyProvider.java

Purpose: `AbstractNNFailoverProxyProvider<T>` is the base implementation for HDFS NameNode HA `FailoverProxyProvider`s. It centralizes configuration cloning, UGI capture, IPC retry settings, lazy proxy construction, NameNode address discovery, optional domain-name expansion, randomized proxy ordering, and delegation-token cloning for logical URIs.

Important APIs/types/functions: subclasses implement `useLogicalURI()`, `getProxy()`, `performFailover()`, and `close()`. `NNProxyInfo<T>` extends `ProxyInfo<T>` by adding an `InetSocketAddress` and cached `HAServiceState`. `createProxyIfNeeded()` lazily resolves unresolved addresses when `dfs.client.failover.lazy.resolved` is enabled and creates the RPC proxy via `HAProxyFactory`. `getProxyAddresses()` reads configured NameNode addresses with `DFSUtilClient.getAddresses`, optionally resolves domains through `DomainNameResolver`, shuffles based on `getRandomOrder()`, and clones delegation tokens for concrete addresses. `setFallbackToSimpleAuth()`/`getFallbackToSimpleAuth()` propagate security fallback state.

Control flow: construction clones the supplied `Configuration`, records interface/factory/current user, and maps HDFS failover retry keys to generic IPC retry keys. Subclasses request proxy lists or single addresses, then call `createProxyIfNeeded()` in their `getProxy()` implementations. Proxy construction failures are logged and rethrown as `RuntimeException`.

State and persistence behavior: state is in-memory only: configuration copy, interface class, factory, UGI, fallback auth flag, and per-proxy cached address/state. Delegation-token cloning mutates current user token aliases so tokens for a logical URI can authenticate against physical NameNode addresses.

Dependencies and integration points: integrates with Hadoop RPC retry infrastructure, `HAProxyFactory`, `DFSUtilClient`, `HAUtilClient`, `NetUtils`, `DomainNameResolverFactory`, and `UserGroupInformation`. Subclasses in the same package use it for configured HA, IP failover, observer reads, request hedging, and alias-map failover.

Risks and test signals: misconfigured URI hosts or address keys fail at runtime. Lazy DNS and domain-name expansion can multiply targets and alter ordering. Security regressions around token cloning are high impact. Tests should cover address discovery, random-order precedence between generic and per-nameservice keys, lazy resolution, resolve-to-FQDN behavior, delegation-token aliases, and proxy creation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/AbstractNNFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ClientHAProxyFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ClientHAProxyFactory.java

Purpose: `ClientHAProxyFactory<T>` is the client-side `HAProxyFactory` implementation that creates NameNode `ClientProtocol` RPC proxies for HA providers.

Important APIs/types/functions: `setAlignmentContext(AlignmentContext)` stores optional client/server state-alignment context. The main `createProxy(...)` overload delegates to `NameNodeProxiesClient.createProxyWithAlignmentContext` when an alignment context is present, otherwise to `createNonHAProxyWithClientProtocol`. The legacy overload without `fallbackToSimpleAuth` delegates to the full overload with null fallback.

Control flow: HA providers call this factory during lazy proxy creation. The `withRetries` parameter is accepted by the interface but this implementation passes fixed `false` to `NameNodeProxiesClient` in both creation branches.

State and persistence behavior: only mutable state is the optional `alignmentContext`, set before proxy creation by observer-read providers.

Dependencies and integration points: integrates with `NameNodeProxiesClient`, `UserGroupInformation`, and Hadoop IPC alignment contexts used for observer reads and router observer reads.

Risks and test signals: incorrect alignment-context propagation can break observer-read consistency. Tests should verify proxy creation branch selection with and without an alignment context and that fallback-to-simple-auth is passed through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ClientHAProxyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ConfiguredFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ConfiguredFailoverProxyProvider.java

Purpose: `ConfiguredFailoverProxyProvider<T>` is the standard HA provider for logical HDFS URIs backed by multiple configured NameNode RPC addresses.

Important APIs/types/functions: constructors load proxies using `DFS_NAMENODE_RPC_ADDRESS_KEY` or a caller-specified address key. `getProxy()` returns the current lazily-created proxy. `performFailover()` advances to the next configured proxy through `incrementProxyIndex()`. `close()` closes every instantiated proxy using `Closeable` when possible or `RPC.stopProxy` otherwise. `useLogicalURI()` returns true.

Control flow: the provider keeps `currentProxyIndex`; normal calls use the current proxy until retry/failover policy invokes `performFailover`, then the index wraps modulo proxy count.

State and persistence behavior: stores a final list of `NNProxyInfo<T>` and mutable current index. Proxies are created on demand and retained until `close()`.

Dependencies and integration points: depends on `AbstractNNFailoverProxyProvider`, Hadoop RPC, and the NameNode address config key. It is the inner provider for observer reads and router configured failover.

Risks and test signals: ordering affects load distribution and failover behavior; resource cleanup must close all proxies created over provider lifetime. Tests should cover index wraparound, lazy creation, randomized address ordering via base class, custom address keys, and close behavior for `Closeable` versus RPC proxies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ConfiguredFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAProxyFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAProxyFactory.java

Purpose: `HAProxyFactory<T>` decouples HA failover providers from the concrete RPC proxy creation mechanism, allowing client-side `ClientProtocol` and server-side protocol factories to share the same provider logic.

Important APIs/types/functions: two `createProxy` overloads create proxies with or without an `AtomicBoolean fallbackToSimpleAuth`. The default `setAlignmentContext(AlignmentContext)` is a no-op for factories that do not support observer-read alignment.

Control flow: `AbstractNNFailoverProxyProvider.createProxyIfNeeded()` calls the full overload when a proxy is first needed. Observer-read providers call `setAlignmentContext()` before proxies are created.

State and persistence behavior: interface only; implementations choose whether to store state such as alignment context.

Dependencies and integration points: links `Configuration`, `InetSocketAddress`, `UserGroupInformation`, `AlignmentContext`, and HA providers. It is central to constructing NameNode RPC client stubs.

Risks and test signals: implementations must honor security fallback and alignment parameters consistently. Tests should cover factory use through providers rather than only direct mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAProxyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/IPFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/IPFailoverProxyProvider.java

Purpose: `IPFailoverProxyProvider<T>` supports HA deployments where an external virtual IP or DNS name moves between NameNodes, so the client uses one RPC address and infrastructure performs failover.

Important APIs/types/functions: the constructor builds a single `NNProxyInfo` from `DFSUtilClient.getNNAddress(uri)`. `getProxy()` lazily creates and returns that single proxy. `performFailover()` is intentionally a no-op. `close()` closes the single proxy if created. `useLogicalURI()` returns false.

Control flow: retry policies handle connection resets after virtual-IP movement; this provider does not switch internal targets.

State and persistence behavior: keeps one `NNProxyInfo<T>` and its cached proxy. No logical-token cloning is performed by this provider because it does not use a logical URI.

Dependencies and integration points: integrates with HDFS URI address parsing, Hadoop RPC, and retry policies such as failover-on-network-exception.

Risks and test signals: using it with a non-resolvable URI or without proper external failover breaks availability. Tests should cover no-op failover, lazy single-proxy creation, close behavior, and `useLogicalURI=false` token handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/IPFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/InMemoryAliasMapFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/InMemoryAliasMapFailoverProxyProvider.java

Purpose: `InMemoryAliasMapFailoverProxyProvider<T>` is a specialized configured failover provider for HDFS provided-storage in-memory alias map RPC endpoints.

Important APIs/types/functions: its constructor delegates to `ConfiguredFailoverProxyProvider` with `DFS_PROVIDED_ALIASMAP_INMEMORY_RPC_ADDRESS` instead of the standard NameNode RPC address key.

Control flow: all failover behavior is inherited: lazy proxy creation, index advancement on failover, and close of instantiated proxies.

State and persistence behavior: inherits proxy list/index state from `ConfiguredFailoverProxyProvider`; no extra fields.

Dependencies and integration points: integrates with alias-map client configuration for provided storage and the generic HA provider framework.

Risks and test signals: misusing the standard NameNode key would connect to the wrong service. Tests should verify it reads alias-map addresses and inherits logical URI/token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/InMemoryAliasMapFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProvider.java

Purpose: `ObserverReadProxyProvider<T>` is an HA provider that sends eligible read-only `ClientProtocol` calls to Observer NameNodes while sending writes and fallback calls to the active NameNode. It preserves read-after-write consistency by syncing with the active through `msync()` and a `ClientGSIContext`.

Important APIs/types/functions: constructors wrap a configurable inner failover provider, create an `AlignmentContext`, set it on the factory, load all NameNode proxies, and create a dynamic proxy using `ObserverReadInvocationHandler`. `isRead(Method)` accepts methods annotated `@ReadOnly` unless `activeOnly=true`. `getHAServiceStateWithTimeout()` probes NameNode HA state through a bounded thread pool. `initializeMsync()` performs the first active `msync()`, and `autoMsyncIfNecessary()` enforces `observer.auto-msync-period`. `changeProxy()` rotates current observer candidate and refreshes cached HA state.

Control flow: `getProxy()` returns a single wrapper proxy. Invocation checks whether observer reads are enabled, the method is read-only, and observer probing is due. It initializes or refreshes msync state, then loops through all NameNode proxies. Non-observers are counted and skipped. Observer invocation success returns immediately. Interrupted exceptions are not retried. `ObserverRetryOnActiveException` breaks to active. Other exceptions are passed through `observerRetryPolicy`; fatal ones are thrown, retriable ones rotate to the next proxy. If no observer succeeds, the call is invoked on the inner active failover proxy and successful active calls update `msynced`/`lastMsyncTimeMs`.

State and persistence behavior: in-memory state includes `msynced`, `lastMsyncTimeMs`, `currentIndex`, `currentProxy`, `lastProxy` for tests, observer probe timestamps, cached HA states in `NNProxyInfo`, and the probing thread pool. No durable state is written. `close()` closes observer proxies, nulls shared proxy fields to avoid double close, closes the inner provider, and shuts down the probe pool.

Dependencies and integration points: integrates with `ClientProtocol`, `ReadOnly`, `ClientGSIContext`, Hadoop retry annotations (`Idempotent`, `AtMostOnce`), `RetryPolicies.failoverOnNetworkException`, `RemoteException`, `StandbyException`, `ObserverRetryOnActiveException`, and `BlockingThreadPoolExecutorService`. It depends on correct NameNode HA state responses and alignment-context support in proxy creation.

Risks and test signals: consistency depends on initial/periodic msync and correct annotation of read methods. Probe timeout defaults to disabled, so unresponsive NameNodes can delay reads unless configured. `lastObserverProbeTime` suppresses repeated full scans when no observers exist. Tests should cover read/write routing, observer-disabled proxy interfaces, activeOnly methods, msync period values `-1/0/>0`, observer retry-on-active behavior, probe timeout/cancellation, no-observer fallback throttling, close behavior, and concurrent `changeProxy()` races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProviderWithIPFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProviderWithIPFailover.java

Purpose: `ObserverReadProxyProviderWithIPFailover<T extends ClientProtocol>` combines observer-read routing over physical NameNode addresses with active failover through a configured virtual IP URI.

Important APIs/types/functions: the default constructor creates an `IPFailoverProxyProvider` using `dfs.client.failover.ipfailover.virtual-address.<nameservice>`. `getFailoverVirtualIP()` validates and parses that URI. `cloneDelegationTokenForVirtualIP()` clones the logical nameservice token to the virtual-IP address. `useLogicalURI()` returns true even though the inner active provider is IP-based.

Control flow: observer-read behavior is inherited from `ObserverReadProxyProvider`. Active fallback and writes go through the virtual IP provider, while observer scans use configured physical NameNode addresses from the superclass.

State and persistence behavior: no additional persistent state. It mutates current user token aliases for the virtual IP.

Dependencies and integration points: integrates with HA virtual-IP deployments, `HAUtilClient` token cloning, and `ClientProtocol` observer-read routing.

Risks and test signals: missing virtual-IP config throws `IllegalArgumentException` at construction. Token cloning must include the virtual IP or secure clients can fail after failover. Tests should cover missing/malformed virtual URI, token alias creation, logical URI reporting, and correct active fallback target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProviderWithIPFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ReadOnly.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ReadOnly.java

Purpose: `ReadOnly` is a runtime-retained method annotation used by HDFS HA client code to identify RPCs that can be routed to Observer NameNodes.

Important APIs/types/functions: annotation attributes are `atimeAffected`, `activeOnly`, and `isCoordinated`, all defaulting to false. `activeOnly=true` excludes an otherwise read-like method from observer routing. `isCoordinated=true` indicates server-side processing should wait for state alignment if behind the client.

Control flow: `ObserverReadProxyProvider` and `RouterObserverReadProxyProvider` inspect the annotation at invocation time. Server-side RPC handling can also inspect coordination metadata.

State and persistence behavior: annotation metadata is retained at runtime and inherited; there is no mutable state.

Dependencies and integration points: integrates with HDFS `ClientProtocol` method declarations, observer-read clients, and state-alignment logic.

Risks and test signals: incorrect annotation can route a mutating or active-only operation to observers, or unnecessarily force active routing. Tests should verify representative annotated methods are classified as expected and that `activeOnly` prevents observer use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ReadOnly.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RequestHedgingProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RequestHedgingProxyProvider.java

Purpose: `RequestHedgingProxyProvider<T>` sends an initial RPC concurrently to all configured NameNode proxies and uses the first successful response, then sticks to that proxy until failover is requested. It is designed for HA setups where the active should respond while standbys throw `StandbyException`.

Important APIs/types/functions: extends `ConfiguredFailoverProxyProvider`. `getProxy()` builds a wrapper dynamic proxy around `RequestHedgingInvocationHandler`. The handler maintains `targetProxies` and volatile `currentUsedProxy`. It captures Hadoop RPC call ID/retry/external-handler context before submitting worker calls and restores/clears call state in the parent thread. `performFailover()` records the currently used proxy in `toIgnore` and rebuilds the handler on the next `getProxy()`.

Control flow: first invocation double-checks `currentUsedProxy`. If more than one target remains, it creates a fixed thread pool, submits one callable per target, and returns the first successful result from `CompletionService`. Failed results are unwrapped and collected; one failure is rethrown directly and multiple failures are wrapped in `MultiException`. Subsequent invocations call only `currentUsedProxy`. With one target, it invokes directly without a thread pool. `toIgnore` removes the previously active proxy after failover.

State and persistence behavior: maintains an in-memory wrapper `currentUsedHandler`, volatile `toIgnore`, and per-handler active proxy. No durable state. Each first hedged invocation creates and shuts down an executor.

Dependencies and integration points: integrates with Hadoop RPC `Client` call identity, `RPC.getConnectionIdForProxy`, `RemoteException`, `StandbyException`, and `MultiException`. It relies on configured socket timeouts because concurrent calls can otherwise block.

Risks and test signals: mutating `targetProxies.remove(toIgnore)` alters the handler's map and can leave no valid proxies after repeated failovers. `performFailover()` assumes a current handler/proxy exists. Hedged calls amplify load and require correct call ID propagation. Tests should cover first-success selection, all-standby failures, single-target optimization, failover ignore behavior, no-target error, connection ID before and after selection, and executor shutdown on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RequestHedgingProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadConfiguredFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadConfiguredFailoverProxyProvider.java

Purpose: `RouterObserverReadConfiguredFailoverProxyProvider<T>` is a thin router observer-read provider variant that uses `ConfiguredFailoverProxyProvider` as its inner proxy rather than IP failover.

Important APIs/types/functions: its constructor passes a new configured failover provider to `RouterObserverReadProxyProvider`.

Control flow: all invocation, msync, close, and failover behavior is inherited. Reads receive router-oriented auto-msync wrapping; actual target selection follows configured failover.

State and persistence behavior: no extra state beyond inherited wrapper/inner provider state.

Dependencies and integration points: integrates router observer-read consistency logic with logical nameservice configured NameNode addresses.

Risks and test signals: coverage should ensure it chooses configured failover rather than the router provider default `IPFailoverProxyProvider`, and that logical URI/token behavior comes from the configured inner provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadConfiguredFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadProxyProvider.java

Purpose: `RouterObserverReadProxyProvider<T>` wraps an inner failover provider to inject automatic `msync()` calls before read-only RPCs when using routers with observer reads. It does not choose observer NameNodes itself; it prepares client state alignment before forwarding to the inner proxy.

Important APIs/types/functions: constructors create `ClientGSIContext`, set it on the factory, create a dynamic proxy with `RouterObserverReadInvocationHandler`, read `observer.auto-msync-period.<nameservice>`, and enable observer-read behavior only for `ClientProtocol`. `autoMsyncIfNecessary()` performs active `msync()` when the configured period is 0 or elapsed. `isRead(Method)` mirrors observer-read classification by checking `@ReadOnly` and excluding `activeOnly`.

Control flow: `getProxy()` returns the wrapper. Each invocation auto-msyncs before read-only methods when enabled, invokes `innerProxy.getProxy().proxy`, unwraps `InvocationTargetException`, and returns the result. Failover and close delegate to `innerProxy`.

State and persistence behavior: keeps `alignmentContext`, `innerProxy`, `wrapperProxy`, `observerReadEnabled`, `autoMsyncPeriodMs`, and volatile `lastMsyncTimeMs`. No durable state.

Dependencies and integration points: integrates with routers, `ClientProtocol.msync`, `ReadOnly`, `ClientGSIContext`, and either IP or configured failover inner providers.

Risks and test signals: unlike `ObserverReadProxyProvider`, there is no initial msync flag, so negative auto-msync disables sync entirely and positive periods compare against `-1` on the first read. Tests should cover auto-msync period semantics, non-ClientProtocol disabling, activeOnly methods, exception unwrapping, connection ID delegation, and close/failover delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/WrappedFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/WrappedFailoverProxyProvider.java

Purpose: `WrappedFailoverProxyProvider<T>` adapts older implementations of Hadoop `FailoverProxyProvider<T>` into the HDFS `AbstractNNFailoverProxyProvider<T>` hierarchy.

Important APIs/types/functions: delegates `getInterface()`, `getProxy()`, `performFailover()`, and `close()` to the wrapped provider. `useLogicalURI()` returns true by assumption for old implementations.

Control flow: it contains no proxy creation logic of its own; all behavior is delegated.

State and persistence behavior: stores only the wrapped provider reference.

Dependencies and integration points: integrates legacy HA providers with code that expects `AbstractNNFailoverProxyProvider`, especially token-handling checks around logical URIs.

Risks and test signals: the logical-URI assumption can be wrong for unusual legacy providers. Tests should cover delegation and close propagation, and any use site should verify token behavior with wrapped providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/WrappedFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReport.java

Purpose: `DataNodeUsageReport` is a private/unstable value object for DataNodes to report throughput and operation timing metrics to the NameNode.

Important APIs/types/functions: fields include bytes written/read per second, write/read time deltas, blocks written/read per second, and timestamp. `EMPTY_REPORT` is the preferred sentinel for no data. The nested `Builder` offers fluent setters and `build()`. Getters expose all metrics. `equals`, `hashCode`, and `toString` support comparison and diagnostics.

Control flow: callers build reports from sampled counters, often via `DataNodeUsageReportUtil`, then include them in heartbeat/report protocol messages.

State and persistence behavior: effectively immutable after builder construction, though fields are not final and the package-private no-arg constructor supports default/sentinel creation. No persistence; values are serialized through surrounding protocol layers.

Dependencies and integration points: integrates with DataNode-to-NameNode usage reporting and diagnostics. It has no external library dependencies beyond annotations.

Risks and test signals: `hashCode()` collapses long sums into int and is suitable only for hash collections, not uniqueness. Tests should cover builder field assignment, `EMPTY_REPORT`, equality/hash consistency, and string output for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReportUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReportUtil.java

Purpose: `DataNodeUsageReportUtil` converts cumulative DataNode metrics into interval usage reports by comparing current counters with the previous sample.

Important APIs/types/functions: `getUsageReport(...)` accepts cumulative byte, time, block-operation counters and `timeSinceLastReport`; it returns the previous report if the interval is zero, otherwise builds a new `DataNodeUsageReport` with per-second deltas and time deltas. Helper methods calculate bytes/block ops per second and read/write time deltas.

Control flow: on nonzero interval, it builds a report, stores all raw current counters as baselines, stores `lastReport`, and returns the new report. On zero interval, it initializes `lastReport` to `EMPTY_REPORT` if needed and returns it without updating baselines.

State and persistence behavior: mutable in-memory baselines make this utility stateful and intended for single DataNode reporter use. Timestamp uses `Time.monotonicNow()`.

Dependencies and integration points: depends on `DataNodeUsageReport` and Hadoop `Time`. It integrates with heartbeat/report generation.

Risks and test signals: `timeSinceLastReport` is treated as seconds by calculation despite the name not encoding units; callers must pass matching units. Counter resets can produce negative rates. The class is not synchronized. Tests should cover first zero interval, baseline updates, delta math, negative/reset behavior, and repeated calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReportUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorage.java

Purpose: `DatanodeStorage` describes a single storage volume/resource on a DataNode, including stable storage ID, state, and HDFS `StorageType`.

Important APIs/types/functions: `State` values are `NORMAL`, `READ_ONLY_SHARED`, and `FAILED`. Constructors default to normal/default storage or accept all fields. `generateUuid()` creates `DS-<uuid>` IDs. `isValidStorageId()` validates that format. Equality and hash code are based only on `storageID`.

Control flow: DataNodes construct storage records for reports; NameNode-side code compares and indexes them by storage ID.

State and persistence behavior: immutable final fields. Storage IDs are expected to persist across DataNode restarts in higher-level storage metadata, though this class only carries the value.

Dependencies and integration points: depends on `StorageType` and Java `UUID`. Used by `StorageReport`, block placement, storage policy, and DataNode storage registration/reporting.

Risks and test signals: equality ignores state and type, so two records with the same ID but different state/type compare equal. `equals` assumes non-null storage IDs. Tests should cover UUID generation/validation, equality semantics, and read-only-shared behavior in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorageReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorageReport.java

Purpose: `DatanodeStorageReport` groups a `DatanodeInfo` with that DataNode's per-storage `StorageReport[]`.

Important APIs/types/functions: constructor sets both final fields; getters return the datanode info and storage report array.

Control flow: produced by NameNode/reporting APIs when clients or admin commands request storage-level cluster state.

State and persistence behavior: shallowly immutable; the array reference is final but contents can be mutated by callers.

Dependencies and integration points: depends on HDFS `DatanodeInfo` and local `StorageReport`. Integrates with storage reports, balancing, and admin diagnostics.

Risks and test signals: array exposure can allow external mutation. Tests should verify consumers handle empty arrays and multiple storage reports per DataNode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/OutlierMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/OutlierMetrics.java

Purpose: `OutlierMetrics` captures latency outlier details for slow peer reports: median, median absolute deviation, upper latency threshold, and actual observed latency.

Important APIs/types/functions: constructor initializes four `Double` values; getters expose them. `equals` and `hashCode` use Apache Commons builders.

Control flow: DataNode slow-peer detectors construct these metrics and package them in `SlowPeerReports`.

State and persistence behavior: immutable final fields. No local persistence.

Dependencies and integration points: depends on Apache Commons Lang builders and Hadoop annotations. Integrated into slow peer diagnostics sent from DataNode to NameNode.

Risks and test signals: `Double` values may be null because no validation occurs; equality uses exact `Double` comparison rather than tolerance. Tests should cover equality/hash behavior, null handling if supported, and serialization through slow-peer protocol conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/OutlierMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowDiskReports.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowDiskReports.java

Purpose: `SlowDiskReports` carries DataNode-reported slow disk diagnostics to the NameNode as a map from disk base path to operation latency metrics.

Important APIs/types/functions: `EMPTY_REPORT` is the no-entry sentinel. `create(Map)` returns the sentinel for null/empty input or a new report otherwise. `getSlowDisks()` and `haveSlowDisks()` expose contents. `DiskOp` enumerates `METADATA`, `READ`, and `WRITE`, maps to protocol string values, and can parse via `fromValue`.

Control flow: DataNode callers build a map of disk path to per-operation latency and pass it through heartbeat/report conversion. NameNode should expose the values diagnostically without comparing across DataNodes.

State and persistence behavior: final map reference but no defensive copy; caller mutations can alter the report. No durable state in this class.

Dependencies and integration points: depends on shaded Guava `ImmutableMap` for sentinel and protocol conversion code that maps `DiskOp` names to protobuf reports.

Risks and test signals: mutable map exposure can surprise consumers. `DiskOp.fromValue` returns null for unknown values, requiring callers to guard. Tests should cover null/empty sentinel behavior, equality independent of map identity, disk op string round trips, and protocol conversion with all operation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowDiskReports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowPeerReports.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowPeerReports.java

Purpose: `SlowPeerReports` carries DataNode-reported diagnostics about peer DataNodes that appear slow, keyed by peer DataNode UUID and valued by `OutlierMetrics`.

Important APIs/types/functions: `EMPTY_REPORT` is the no-entry sentinel. `create(Map)` returns the sentinel for null/empty maps. `getSlowPeers()`, `haveSlowPeers()`, `equals`, and `hashCode` expose and compare the report.

Control flow: DataNode metrics code constructs reports and sends them to NameNode, where values should be treated as opaque diagnostics rather than cross-node comparable metrics.

State and persistence behavior: final map reference but no defensive copy; contents are mutable if the caller's map is mutable.

Dependencies and integration points: depends on shaded Guava `ImmutableMap`, `OutlierMetrics`, and DataNode heartbeat/report protocol conversion.

Risks and test signals: map mutability can affect equality and report contents after creation. Tests should cover sentinel behavior, equality/hash, and conversion of `OutlierMetrics` through the wire representation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowPeerReports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReport.java

Purpose: `StorageReport` is a per-storage utilization report containing a `DatanodeStorage`, failure flag, capacity, DFS/non-DFS usage, remaining bytes, block-pool usage, block-pool usage percentage, and mount path.

Important APIs/types/functions: constructors support optional mount. `EMPTY_ARRAY` provides a no-report sentinel. Getters expose all fields; `getRemaining()` clamps negative values to zero. `blockPoolUsagePercent` is computed at construction as zero for non-positive capacity or `bpUsed * 100 / capacity`.

Control flow: DataNodes create reports for each storage and NameNodes aggregate them in `DatanodeStorageReport` and cluster metrics.

State and persistence behavior: immutable final fields. No local persistence.

Dependencies and integration points: depends on `DatanodeStorage`. Integrates with DataNode storage reporting, capacity accounting, balancer/admin UIs, and storage policy logic.

Risks and test signals: values are accepted as supplied, so inconsistent capacity/used/remaining can propagate. The clamped remaining getter hides negative raw values from consumers. Tests should cover percentage calculation, zero/negative capacity, negative remaining clamp, mount propagation, and failed storage reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/package-info.java

Purpose: `package-info.java` documents and annotates the `org.apache.hadoop.hdfs.server.protocol` package as containing classes that communicate information between DataNode and NameNode.

Important APIs/types/functions: applies `@InterfaceAudience.LimitedPrivate({"HDFS"})` and `@InterfaceStability.Evolving` at package level.

Control flow: none; this is metadata only.

State and persistence behavior: no runtime state beyond package annotations available to tooling/reflection.

Dependencies and integration points: integrates with Hadoop's audience/stability annotation system and documentation generation.

Risks and test signals: changes affect API classification and compatibility promises. Test signal is mostly static checks or generated docs, not runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ClientMmap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ClientMmap.java

Purpose: `ClientMmap` is a closeable client reference to a memory-mapped short-circuit replica region.

Important APIs/types/functions: constructor stores the owning `ShortCircuitReplica`, `MappedByteBuffer`, and whether the mmap added a no-checksum anchor. `getMappedByteBuffer()` returns the mapped buffer. `close()` removes the no-checksum anchor if anchored, unreferences the replica, and nulls the replica field to make close idempotent.

Control flow: callers obtain it from `ShortCircuitReplica.getOrCreateClientMmap()`. Closing releases cache/reference-count resources and may allow eviction.

State and persistence behavior: holds an in-memory mapped buffer and a mutable replica reference used to prevent double release. It does not unmap directly; unmapping is controlled by `ShortCircuitCache`/`ShortCircuitReplica`.

Dependencies and integration points: depends on `ShortCircuitReplica` and Java NIO `MappedByteBuffer`. It integrates with block reader mmap access and no-checksum anchoring.

Risks and test signals: failure to close leaks replica references and anchors, preventing slot release/munmap. Tests should cover anchored and unanchored close, double close, and reference-count effects in the cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ClientMmap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShm.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShm.java

Purpose: `DfsClientShm` is the DFSClient-specific shared-memory segment used for short-circuit reads. It extends `ShortCircuitShm` and reacts to associated UNIX domain socket closure by invalidating slots.

Important APIs/types/functions: constructor receives `ShmId`, shared-memory stream, owning `EndpointShmManager`, and `DomainPeer`. `isDisconnected()` reports DataNode connection loss. `handle(DomainSocket)` implements `DomainSocketWatcher.Handler`: unregisters the segment, marks it disconnected, invalidates all allocated slots, and frees immediately if no slots remain.

Control flow: `DfsClientShmManager` creates it after receiving an shm file descriptor from the DataNode and registers it with `DomainSocketWatcher`. When the socket closes, watcher callback invalidates all slots so replicas using them become stale.

State and persistence behavior: in-memory `disconnected` flag is synchronized. Slot validity lives in the shared mmap segment. No durable persistence.

Dependencies and integration points: integrates `ShortCircuitShm`, `DfsClientShmManager.EndpointShmManager`, `DomainPeer`, `DomainSocket`, and `DomainSocketWatcher`.

Risks and test signals: lock ordering matters because watcher callbacks interact with the manager. Tests should cover socket-close invalidation, free-on-empty, stale slot detection by `ShortCircuitReplica`, and no double-disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShmManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShmManager.java

Purpose: `DfsClientShmManager` manages all DFSClient shared-memory segments used for short-circuit replica validity and anchoring communication with DataNodes.

Important APIs/types/functions: public `allocSlot(...)` allocates a `ShortCircuitShm.Slot` for a DataNode/block, creating per-DataNode `EndpointShmManager`s on demand. `freeSlot(Slot)` returns slots. `close()` marks the manager closed and closes the `DomainSocketWatcher`. Nested `EndpointShmManager` tracks `full` and `notFull` shared-memory segments, `disabled`, and `loading`. It can allocate from existing segments, request a new segment using `Sender.requestShortCircuitShm`, register the segment with the watcher, free slots, unregister segments, and shut down segment domain sockets.

Control flow: slot allocation holds the manager lock, tries existing `notFull` segments, waits on `finishedLoading` if another thread is fetching a segment, or releases the lock to request a new segment from the DataNode. Success transfers ownership of the provided `DomainPeer` to the manager and registers watcher callbacks. Unsupported DataNodes set `disabled` and return null. Slot free unregisters the slot, moves segments between full/notFull, frees disconnected empty segments, or shuts down empty live segments so watcher cleanup occurs.

State and persistence behavior: all state is in memory. A `ReentrantLock` protects the DataNode map, segment maps, `closed`, `disabled`, and `loading`. Shared-memory slot bits are stored in mmap’d segment memory. Visitor APIs expose copies of per-DataNode map references for tests.

Dependencies and integration points: integrates with `DataTransferProtocol.requestShortCircuitFds`, protobuf `ShortCircuitShmResponseProto`, `PBHelperClient`, `DomainPeer`, `DomainSocketWatcher`, `DatanodeInfo`, and `ExtendedBlockId`. Used by `ShortCircuitCache.allocShmSlot` and slot release paths.

Risks and test signals: deadlock risk is explicitly managed by not taking watcher locks while holding manager lock. New-segment request paths must correctly signal waiting allocators on all exits. DataNode unsupported responses disable future attempts. Tests should cover concurrent allocators, unsupported/error responses, peer ownership flag, immediate disconnect after watcher registration, full/notFull transitions, freeing stale segments, close behavior, and visitor state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShmManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DomainSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DomainSocketFactory.java

Purpose: `DomainSocketFactory` decides whether UNIX domain sockets can be used for local DataNode communication and creates/caches domain-socket path usability state.

Important APIs/types/functions: `PathState` distinguishes `UNUSABLE`, `SHORT_CIRCUIT_DISABLED`, and `VALID`, with flags for data-transfer and short-circuit usability. `PathInfo` carries effective path and state, with `NOT_CONFIGURED` sentinel. Constructor validates feature/config/native availability and creates an expiring Guava cache. `getPathInfo()` checks configured path, feature enablement, native loading, local address, effective path, and cached state. `createSocket()` connects and sets receive timeout, marking paths unusable on failure. Disable methods update cache state; `clearPathMap()` is for tests.

Control flow: clients ask for path info before domain-socket reads. If valid, they call `createSocket`; failures are cached for `pathExpireSeconds` to avoid repeated attempts.

State and persistence behavior: path states are in-memory and expire after configured disable interval. No durable state.

Dependencies and integration points: depends on DFS client short-circuit configuration, `DomainSocket`, `DFSUtilClient.isLocalAddress`, Hadoop `PerformanceAdvisory`, and Guava cache. It gates both short-circuit local reads and domain-socket data traffic.

Risks and test signals: incorrect local-address detection or cache state can disable short-circuit reads unexpectedly. Empty domain socket path with enabled feature throws `HadoopIllegalArgumentException`. Tests should cover feature combinations, native load failure, non-local addresses, effective path formatting by port, failure caching/expiry, and short-circuit-only disable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DomainSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitCache.java

Purpose: `ShortCircuitCache` is the central client cache for short-circuit local read resources: replica file descriptors, memory maps, invalid-token failures, and shared-memory slots communicating replica validity with DataNodes.

Important APIs/types/functions: `fromConf()` builds cache sizing/lifetime values from `ShortCircuitConf`. `fetchOrCreate(ExtendedBlockId, ShortCircuitReplicaCreator)` coordinates concurrent replica loading via `Waitable<ShortCircuitReplicaInfo>`. `ref()`/`unref()` manage replica reference counts. `purge()`, `trimEvictionMaps()`, and `CacheCleaner` maintain eviction and staleness. `getOrCreateClientMmap()` serializes mmap creation/retry per replica. `allocShmSlot()`, `freeSlot()`, and `scheduleSlotReleaser()` connect to `DfsClientShmManager`. `SlotReleaser` sends `releaseShortCircuitFds` to the DataNode and frees or tears down the segment.

Control flow: `fetchOrCreate` first tries existing waitables up to three retries, fetching and ref-counting valid replicas. If none exists, it installs a waitable, releases the lock, calls the creator, then stores/provides the result. `fetch()` waits for in-progress creation, returns invalid-token results, purges stale replicas, and retries on purged/stale entries. `unref()` purges closed/stale replicas, decrements references, closes when count reaches zero, or makes refcount-one replicas evictable. Cleaner periodically demotes old mmapped replicas to the regular eviction list and purges expired non-mmapped replicas. Close purges evictable replicas, shuts down executors, and closes the shm manager.

State and persistence behavior: guarded by a `ReentrantLock`: `replicaInfoMap`, eviction maps keyed by nanosecond timestamps, size/lifetime limits, `closed`, and `outstandingMmapCount`. Replica refcounts start at 2 for cache plus requester. Mmap state is stored on `ShortCircuitReplica.mmapData` as null, `Condition`, `MappedByteBuffer`, or failure timestamp. No durable cache state exists.

Dependencies and integration points: integrates with `ShortCircuitReplica`, `ShortCircuitReplicaInfo`, `DfsClientShmManager`, `DomainSocket`, protobuf data-transfer release messages, `Waitable`, `InvalidToken`, `RetriableException`, and HDFS read statistics through consumers. It is used by local block readers to reuse file descriptors and memory maps.

Risks and test signals: this class is concurrency-sensitive. Incorrect refcount/purge order can leak FDs or close in-use replicas. `pathToDomainSocket` is used by the single-threaded releaser executor and assumes no concurrent access outside that executor. Mmap retry timing must wake waiters. Tests should cover concurrent fetch/create, stale replica purge/retry, invalid-token caching behavior, eviction size/lifetime limits, mmap success/failure/retry, anchored mmap close, slot release success/failure, close shutdown timeouts, and visitor-observed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplica.java

Purpose: `ShortCircuitReplica` represents cached local file descriptors and optional shared-memory slot for an HDFS block replica used by short-circuit local reads.

Important APIs/types/functions: constructor stores block key, data/meta streams, cache, creation time, slot, and reads `BlockMetadataHeader`, accepting only version 1. `isStale()` checks slot validity when a slot exists or falls back to age threshold. `addNoChecksumAnchor()`/`removeNoChecksumAnchor()` manage slot anchors. `hasMmap()`, `munmap()`, and `loadMmapInternal()` handle mmap state. `close()` munmaps, closes streams, and schedules slot release. Accessors expose streams, metadata, key, slot, and `getOrCreateClientMmap()`.

Control flow: created by cache loader, handed to block readers, referenced/unreferenced through `ShortCircuitCache`. When no longer referenced and purged, `close()` releases all resources. Staleness is checked by cache before reuse and on unref.

State and persistence behavior: fields include immutable identity/resources plus cache-protected mutable `mmapData`, `purged`, `refCount`, and `evictableTimeNs`. The underlying file descriptors and mmap are OS resources; slot state is shared memory.

Dependencies and integration points: integrates with `ExtendedBlockId`, `BlockMetadataHeader`, `ShortCircuitCache`, `ShortCircuitShm.Slot`, `NativeIO.POSIX.munmap`, and `IOUtilsClient`.

Risks and test signals: metadata version mismatch fails construction. `close()` requires `refCount == 0` and `purged == true`. Slot-based staleness is safer than time-based fallback; no-slot replicas depend on configured threshold. Tests should cover metadata header validation, slot and time staleness, anchor add/remove, mmap limits/errors, close preconditions, and scheduled slot release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplicaInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplicaInfo.java

Purpose: `ShortCircuitReplicaInfo` is a small result wrapper for short-circuit replica creation/fetching. It can represent success, invalid block token, or generic no-replica failure.

Important APIs/types/functions: constructors create empty failure, replica success, or `InvalidToken` result. Getters expose `ShortCircuitReplica` and `InvalidToken`. `toString()` includes whichever payload is present.

Control flow: `ShortCircuitCache` stores instances in waitables and returns them to callers. Invalid-token results are surfaced distinctly from generic load failure.

State and persistence behavior: immutable final fields, no persistence.

Dependencies and integration points: depends on `ShortCircuitReplica` and `SecretManager.InvalidToken`. Integrates with block reader creation and cache coordination.

Risks and test signals: empty result has both fields null, so callers must distinguish it from invalid-token failure. Tests should cover all constructors and `ShortCircuitCache` behavior for invalid token versus null replica.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplicaInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitShm.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitShm.java

Purpose: `ShortCircuitShm` manages a mmap’d shared-memory segment used by DFSClient and DataNode to communicate short-circuit replica validity and anchoring state.

Important APIs/types/functions: `ShmId` uniquely identifies a segment with random hi/lo longs and comparable ordering. `SlotId` identifies a slot by segment ID and index. `Slot` wraps a 64-byte slot and manipulates volatile flag/anchor bits through `sun.misc.Unsafe`: valid, anchorable, anchored count, add/remove anchor. Segment methods include `allocAndRegisterSlot`, `registerSlot`, `getSlot`, `unregisterSlot`, `slotIterator`, `isEmpty`, `isFull`, and `free()`.

Control flow: construction validates NativeIO, non-Windows, Unsafe availability, computes usable length from the stream size, mmaps the file descriptor read/write, and initializes slot arrays/bitsets. Allocation finds the first clear bit, clears/makes-valid the slot, and records it. Registration validates externally initialized slots. Free munmaps the entire segment.

State and persistence behavior: Java state includes segment ID, base address, mmapped length, slot array, and allocation bitset. Slot flags live in native shared memory and are modified atomically with CAS. Segment lifetime is tied to OS mmap; no disk persistence is intended.

Dependencies and integration points: depends on Hadoop `NativeIO.POSIX`, `InvalidRequestException`, `ExtendedBlockId`, `Shell`, Commons builders, Guava primitives, and `Unsafe`. Used by `DfsClientShm`, `DfsClientShmManager`, `ShortCircuitReplica`, and DataNode shared-memory protocol counterparts.

Risks and test signals: uses internal `Unsafe` and native mmap, so platform support matters. Anchor count masks use low 31 bits while comments describe wider fields; behavior should be treated as protocol-specific. `slotIterator` warns about concurrent safety limits. Tests should cover small segment rejection, unsupported platform/native cases, random/comparable IDs, slot allocation/fullness, invalid registration, valid/anchorable/anchor CAS behavior, unregister preconditions, and munmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitShm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteArrayManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteArrayManager.java

Purpose: `ByteArrayManager` abstracts allocation/recycling of byte arrays with optional pooling and per-size allocation limits for HDFS client buffers.

Important APIs/types/functions: `leastPowerOfTwo(int)` rounds sizes and detects overflow. `Conf` configures count threshold, max arrays per length, and counter reset period. `newInstance(Conf)` returns unlimited allocation when config is null or pooled `Impl` otherwise. `Counter` and `CounterMap` track per-size allocation frequency with time resets. `FixedLengthManager` blocks allocation when `numAllocated >= maxAllocated`, recycles arrays into `freeQueue`, and notifies waiters on recycle. `ManagerMap` creates per-length managers after threshold. `Impl.newByteArray()` rounds to min 32/power-of-two, creates a manager only after threshold, and returns empty singleton for size zero. `release()` recycles into an existing manager if one exists.

Control flow: below threshold, allocations use new arrays. Once repeated allocations for a size exceed threshold, a `FixedLengthManager` starts limiting and recycling that rounded size. `allocate()` waits while at capacity; `release()` decreases allocated count and may enqueue the array.

State and persistence behavior: all state is in memory and synchronized at component granularity. Debug logging uses a thread-local `StringBuilder`.

Dependencies and integration points: depends on Hadoop `Time`, `Preconditions`, `HadoopIllegalArgumentException`, and SLF4J. Used by HDFS client code that wants bounded buffer allocation under high concurrency.

Risks and test signals: callers must release arrays to avoid blocked waiters. Releasing arrays not allocated by the manager can lower `numAllocated`, intentionally clamped to zero, which affects limit accounting. Power-of-two overflow throws. Tests should cover rounding, zero-length singleton, threshold transition, blocking/unblocking, recycle queue sizing, stale counter reset, and release of unmanaged arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteArrayManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteBufferOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteBufferOutputStream.java

Purpose: `ByteBufferOutputStream` adapts a `ByteBuffer` to the `OutputStream` API.

Important APIs/types/functions: constructor stores the target buffer. `write(int)` writes one byte via `ByteBuffer.put`. `write(byte[], int, int)` writes a byte range via `ByteBuffer.put(byte[], off, len)`.

Control flow: all writes advance the underlying buffer position and rely on `ByteBuffer` for bounds checking.

State and persistence behavior: no additional state beyond the target buffer; all data is stored in the caller-supplied buffer.

Dependencies and integration points: depends on Java NIO and is used where APIs require an `OutputStream` but HDFS code wants to fill an existing `ByteBuffer`.

Risks and test signals: `ByteBufferOverflowException` is unchecked and can escape despite `OutputStream` signatures declaring `IOException`. Tests should cover single/bulk writes, position advancement, and overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteBufferOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileReader.java

Purpose: `CombinedHostsFileReader` reads JSON-based DataNode include/exclude/admin configuration into `DatanodeAdminProperties[]`.

Important APIs/types/functions: `readFile(String)` parses the modern top-level JSON array format with Jackson. On `JsonMappingException`, it falls back to legacy concatenated-object parsing with `ObjectReader.readValues`. Empty files warn and return an empty array. `readFileWithTimeout(String, int)` runs `readFile` inside a `SubjectInheritingThread`/`FutureTask` and throws `IOException` on timeout, interruption, or execution failure.

Control flow: modern parse is attempted when file length is positive. Legacy parse collects all parsed objects and logs a warning; invalid legacy parse logs and returns whatever was collected, usually empty. Timeout wrapper starts a thread, waits bounded time, cancels on timeout, and maps several failure modes to an IOException message.

State and persistence behavior: stateless utility. Reads UTF-8 files from local filesystem; no writes.

Dependencies and integration points: depends on Jackson, `DatanodeAdminProperties`, Java NIO, and `SubjectInheritingThread` for security context propagation. Used by NameNode host refresh/admin state handling.

Risks and test signals: invalid legacy JSON is logged but not rethrown, which can silently produce empty configuration. `readFileWithTimeout` maps execution failures to a timeout-flavored IOException. Tests should cover modern array format, legacy format, empty file, invalid JSON, timeout cancellation, and subject inheritance where relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileWriter.java

Purpose: `CombinedHostsFileWriter` writes JSON-based DataNode admin host configuration from a set of `DatanodeAdminProperties`.

Important APIs/types/functions: `writeFile(String, Set<DatanodeAdminProperties>)` creates a Jackson `ObjectMapper`, opens the target path as UTF-8, and writes the set as JSON.

Control flow: single-pass serialization in a try-with-resources writer.

State and persistence behavior: stateless utility that persists the supplied set to the local filesystem. Ordering follows the provided set's iteration order.

Dependencies and integration points: depends on Jackson, Java NIO, and `DatanodeAdminProperties`. It complements `CombinedHostsFileReader` for admin tooling.

Risks and test signals: set iteration order can make output nondeterministic for unordered sets. It does not create parent directories or write atomically. Tests should cover UTF-8 output, round-trip with the reader, empty set, and deterministic behavior when ordered sets are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ECPolicyLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ECPolicyLoader.java

Purpose: `ECPolicyLoader` loads user-defined HDFS erasure-coding policies from an XML configuration file.

Important APIs/types/functions: `loadPolicy(String)` resolves the file, returns empty list when missing, and wraps parser/IO/SAX failures in `RuntimeException`. `loadECPolicies(File)` parses secure XML and enforces `<configuration>`, `<layoutversion>`, `<schemas>`, and `<policies>`. `loadLayoutVersion()` validates version 1. `loadSchemas()` parses unique `ECSchema`s by id. `loadPolicies()` parses policy elements and skips duplicate policies with a warning. `getPolicyFile()` requires relative/classpath URLs to be local file URLs. `loadSchema()` maps `<k>`/`<m>` to ECSchema option names. `loadPolicy(Element, Map)` resolves schema references and positive integer cell size.

Control flow: loading is strict for structural errors and unknown elements under schemas/policies. Schema duplicates throw; policy duplicates warn. Missing schema or non-positive/invalid cell size throws.

State and persistence behavior: stateless loader; all data is returned as a list of `ErasureCodingPolicy`. No caching.

Dependencies and integration points: depends on secure `XMLUtils`, DOM APIs, `ECSchema`, and `ErasureCodingPolicy`. Integrates with NameNode/client configuration paths for custom EC policy definition.

Risks and test signals: `getPolicyFile` constructs `new URL(policyFilePath)` for non-absolute paths, so plain relative filesystem paths may fail unless passed as URL-like values. Error wrapping loses original exception cause. Tests should cover valid config, missing file, bad root/version/missing sections, duplicate schema/policy behavior, k/m alias mapping, schema reference failure, bad cell size, non-file URL rejection, and secure XML parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ECPolicyLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/IOUtilsClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/IOUtilsClient.java

Purpose: `IOUtilsClient` contains client-side cleanup and read-statistics helpers.

Important APIs/types/functions: `cleanupWithLogger(Logger, Closeable...)` closes each non-null closeable and logs any thrown `Throwable` at debug level. `updateReadStatistics(ReadStatistics, int, BlockReader)` delegates to the overload using `blockReader.isShortCircuit()` and network distance. The overload increments short-circuit, local, or remote byte counts when `nRead > 0`.

Control flow: cleanup intentionally suppresses all close failures. Statistics updates ignore zero/negative reads, then classify by short-circuit first, network distance zero second, remote otherwise.

State and persistence behavior: stateless utility; mutates caller-provided `ReadStatistics`.

Dependencies and integration points: depends on `BlockReader`, `ReadStatistics`, SLF4J, and Java `Closeable`. Used throughout HDFS client cleanup/error paths and read accounting.

Risks and test signals: suppressing `Throwable` is appropriate for cleanup but can hide serious errors if used outside exception cleanup paths. Tests should cover null closeables, thrown `IOException`/runtime error suppression, and statistics classification for short-circuit/local/remote/zero-byte reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/IOUtilsClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/LongBitFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/LongBitFormat.java

Purpose: `LongBitFormat` describes and manipulates a named fixed-width bit field inside a `long` record.

Important APIs/types/functions: constructor takes field name, previous field, bit length, and minimum value, deriving offset, max value, and mask. `retrieve(long)` extracts the field. `combine(long, long)` validates against min/max and inserts the value into the record. `Enum` is a small interface exposing field length. Getters expose min and length.

Control flow: callers typically chain field definitions by passing the previous `LongBitFormat`, then use `combine` and `retrieve` for compact record packing.

State and persistence behavior: immutable and serializable. Packed values are stored in caller-owned long records.

Dependencies and integration points: no Hadoop dependencies beyond package placement. Used by HDFS code that packs multiple numeric fields into inode/block metadata longs.

Risks and test signals: max is computed as `(-1L) >>> (64 - LENGTH)`, so length 64 and invalid lengths need careful treatment. Error messages contain the typo `Illagal`, which tests may not want to rely on. Tests should cover chained offsets, min/max validation, replacing existing field bits, retrieval, and boundary lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/LongBitFormat.java -->
