# Research Report: subset-b-007477

Grouped source research for HDFS utility, HA proxy, network topology, data-transfer, SASL, layout, cache directive, snapshot, and exception classes. Each source file section is marker-delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSUtil.java

Purpose: Provides a large HDFS-internal utility surface for path validation and byte conversions, NameNode and nameservice address discovery, HA/federation configuration handling, HTTP/HTTPS server setup, SSL credential loading, protobuf RPC registration, protected-directory checks, delegation-token decoding, file-status flag construction, and transfer-rate metrics. It centralizes many compatibility behaviors shared by NameNode, DataNode, clients, tools, routers, journal nodes, and tests.

Important APIs and types: `getSecureRandom()` exposes a thread-local `SecureRandom`. `ServiceComparator` and `StaleAndSlowComparator` order `DatanodeInfo` instances by service, maintenance, stale, and slow-node state. Path helpers include `isValidName()`, `isValidNameForComponent()`, `byteArray2PathString()`, `strings2PathString()`, `path2String()`, `getPathComponents()`, and `bytes2byteArray()`. Configuration/address helpers include `addKeySuffixes()`, `getRpcAddressesForNameserviceId()`, `getAllNnPrincipals()`, `getJournalNodeAddresses()`, `getBackupNodeAddresses()`, `getSecondaryNameNodeAddresses()`, `getNNServiceRpcAddresses()`, `getNNServiceRpcAddressesForCluster()`, `getNNLifelineRpcAddressesForCluster()`, `getAddressesForNsIds()`, `flattenAddressMap()`, `addressMapToString()`, `getInternalNsRpcUris()`, `getNameServiceUris()`, `getNameServiceIdFromAddress()`, `getInfoServer()`, `getBindAddress()`, `getSuffixIDs()`, and `createUri()`. Server/security helpers include `addInternalPBProtocol()`, deprecated `addPBProtocol()` overloads, `getHttpPolicy()`, `loadSslConfiguration()`, `loadSslConfToHttpServerBuilder()`, `getHttpServerTemplate()`, `getPassword()`, `createKeyProviderCryptoExtension()`, and `decodeDelegationToken()`. Namespace helpers include `checkProtectedDescendants()`, `getFlags()`, `isParentEntry()`, `addTransferRateMetric()`, and `getTransferRateInBytesPerSecond()`.

Control flow: Address discovery generally walks configured nameservices and namenode ids, resolves suffixed keys in preference order, falls back to generic/default addresses where allowed, and throws explicit configuration errors when mandatory backup, secondary, or NameNode addresses are absent. HA-aware URI discovery first checks whether a nameservice can use a logical URI via `HAUtil.useLogicalUri`; otherwise it resolves concrete service/client RPC addresses and suppresses lower-priority duplicates. HTTP endpoint resolution reverse-matches RPC addresses to nameservice/NN suffixes, selects HTTP or HTTPS keys based on the configured policy, and substitutes wildcard bind hosts with the NameNode host. Web server construction sanitizes filter initializer configuration, installs HDFS auth filters, adds HTTP and/or HTTPS endpoints, and loads SSL material through the credential provider aware password path.

State and persistence behavior: Most state is transient and configuration-derived. `getHttpPolicy()` normalizes the configured policy string back into the `Configuration`. `setGenericConf()` mutates the runtime `Configuration` by copying suffixed keys to generic keys. `loadSslConfiguration()` builds a separate SSL-only configuration from the configured resource and copies client-auth policy. `checkProtectedDescendants()` reads protected-directory state from `FSDirectory` and throws before namespace mutation. Transfer-rate metrics are pushed into `DataNodeMetrics`; no long-lived state is stored in `DFSUtil` beyond the thread-local random and static CLI help option objects.

Dependencies and integration points: Depends heavily on `DFSUtilClient`, `DFSConfigKeys`, `HAUtil`, `NameNode`, `HdfsServerConstants`, `FSDirectory`, `INodesInPath`, `HttpServer2`, `HttpConfig`, Hadoop RPC and protobuf engines, security/UGI/token APIs, KMS key provider APIs, `DataNodeMetrics`, and Hadoop `Path`/`FileSystem` APIs. It is called from NameNode/DataNode bootstrap, HA and federation tooling, web server initialization, fsimage/edit loading, namespace mutation checks, HDFS shell/admin tools, and metrics paths.

Risks: This file is high blast-radius because configuration fallback order and suffix logic determine which NameNode endpoints every daemon or client uses. `bytes2String(byte[], int, int)` ignores its offset/length parameters and delegates the full array, so callers expecting slice decoding would get surprising behavior. `getNameServiceId()` indexes the result of `getSuffixIDs(...)` without a null check, making invalid multi-nameservice local-address configuration fail abruptly. Wildcard substitution, SSL password lookup, and filter initializer rewriting affect security posture. Protected-directory checks depend on lexicographic subset boundaries and correct non-empty directory checks. Transfer-rate conversion can still overflow when casting huge double rates to long.

Test signals: Unit tests should cover component/path validation, byte path round trips, `byteArray2PathString` offsets and absolute paths, address maps for single NN, HA, federation, internal nameservices, domain-name resolution enabled/disabled, suffix reverse matching with duplicates, HTTP/HTTPS policy normalization, wildcard host substitution, SSL config warnings/password loading, protected directory deletion/rename cases, delegation token decode, status flag combinations, and transfer-rate edge cases with zero, negative, and sub-nanosecond durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DeprecatedUTF8.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DeprecatedUTF8.java

Purpose: Wraps the deprecated `org.apache.hadoop.io.UTF8` class so HDFS code can keep using legacy UTF8 serialization without local `@SuppressWarnings("deprecation")` annotations at each call site. It is a compatibility shim for old wire/storage formats.

Important APIs and types: `DeprecatedUTF8` extends `UTF8` and provides default, `String`, and copy constructors. Static `readString(DataInput)` and `writeString(DataOutput, String)` delegate directly to the deprecated `UTF8` string helpers.

Control flow: There is no independent logic. Construction and serialization flow immediately through the superclass or static `UTF8` methods.

State and persistence behavior: Instances inherit mutable string/byte state from `UTF8`. The static helpers read and write legacy UTF8-encoded values to Hadoop `DataInput`/`DataOutput`, so the persistence behavior is exactly the deprecated Hadoop UTF8 format.

Dependencies and integration points: Depends on Hadoop `UTF8` and Java data streams. It is intended for package-internal HDFS code that must read old edit/fsimage or protocol encodings.

Risks: Keeping the wrapper can hide continued dependence on a deprecated encoding. Any behavior differences, size limits, or malformed input handling come from `UTF8`. Replacing it with standard UTF-8 requires compatibility checks for persisted data.

Test signals: Serialization compatibility tests should compare bytes produced by `DeprecatedUTF8.writeString` and `UTF8.writeString`, read legacy strings from historical images/edits, and compile with deprecation warnings suppressed only inside this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DeprecatedUTF8.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HAUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HAUtil.java

Purpose: Provides HDFS HA helper logic for detecting HA configuration, deriving the local and peer NameNode ids, cloning configuration for other HA NameNodes, deciding whether logical URIs are required, locating the current active NameNode, opening proxies to every NameNode in a nameservice, and checking whether at least one NameNode is active.

Important APIs and functions: `isHAEnabled()` checks HA by counting configured RPC addresses for a nameservice. `usesSharedEditsDir()` detects shared edits configuration. `getNameNodeId()`, `getNameNodeIdFromAddress()`, `getNameNodeIdOfOtherNodes()`, and `getConfForOtherNodes()` resolve HA node identity and peer configs. `shouldAllowStandbyReads()` and `setAllowStandbyReads()` expose standby-read configuration. `useLogicalUri()` probes the failover proxy provider. `getAddressOfActive()` finds the active NameNode address for a `DistributedFileSystem`. `getProxiesForAllNameNodesInNameservice()` returns `ClientProtocol` or generic protocol proxies for all NNs. `isAtLeastOneActive()` probes proxies by calling `getFileInfo("/")`.

Control flow: Local ID resolution first trusts `dfs.ha.namenode.id`, then matches the local address against suffixed RPC address keys through `DFSUtil.getSuffixIDs`. Peer config generation removes HA-independent generic keys, then calls `NameNode.initializeGenericKeys()` per other NN. Active-address lookup forces client resolution with `fs.exists("/")`, then either scans all HA proxies for `HAServiceState.ACTIVE` or returns the non-HA DFSClient proxy address. Active checks treat `StandbyException` as expected and aggregate unexpected IO failures with `MultipleIOException`.

State and persistence behavior: This class stores no persistent state. It reads and mutates passed `Configuration` objects only in `setAllowStandbyReads()` and the cloned configs in `getConfForOtherNodes()`. RPC proxy creation opens client-side resources that callers must manage according to normal Hadoop RPC lifecycle.

Dependencies and integration points: Depends on `DFSUtil`, `DFSUtilClient`, `NameNodeProxies`, `NameNodeProxiesClient`, `NameNode`, HA failover proxy providers, Hadoop RPC, `DistributedFileSystem`, `ClientProtocol`, UGI, and HA service state exceptions. It is used by HDFS HA administration, NameNode startup, tests, and client/tool paths that need to address all NameNodes.

Risks: Misconfigured suffixes can produce null or ambiguous IDs and fail startup. `getAddressOfActive()` connects directly to the then-active NN and is explicitly fragile across later failover. `getProxiesForAllNameNodesInNameservice()` creates non-HA proxies, so callers must expect standby responses. Configuration cloning must keep HA-independent keys unset or peer configs may point back to the current node.

Test signals: HA tests should cover explicit and inferred NN ids, multiple nameservices, missing/duplicate local address matches, peer config cloning, logical URI detection with and without failover providers, active address lookup through failover, standby-read flags, all-NN proxy creation for generic protocols, and `isAtLeastOneActive()` behavior for active, all-standby, and mixed IOException cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HAUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HDFSPolicyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HDFSPolicyProvider.java

Purpose: Registers HDFS IPC protocol interfaces with Hadoop service authorization by mapping each protocol class to the ACL configuration key that controls access to it.

Important APIs and types: `HDFSPolicyProvider` extends `PolicyProvider`. The static `hdfsServices` array maps ACL keys to `ClientProtocol`, `ClientDatanodeProtocol`, `DatanodeProtocol`, `InterDatanodeProtocol`, `NamenodeProtocol`, `QJournalProtocol`, `InterQJournalProtocol`, `HAServiceProtocol`, `ZKFCProtocol`, refresh/get-user-mapping protocols, `GenericRefreshProtocol`, `DatanodeLifelineProtocol`, and `ReconfigurationProtocol`. `getServices()` returns that array.

Control flow: There is no dynamic control flow beyond returning the prebuilt array to the service authorization framework.

State and persistence behavior: The service map is static in-memory metadata. Effective authorization state comes from `CommonConfigurationKeys` ACL values loaded by Hadoop RPC/service authorization.

Dependencies and integration points: Integrates with Hadoop `PolicyProvider`, `Service`, common security ACL keys, HDFS client/server/qjournal protocols, HA protocols, and admin refresh protocols. It is consumed during RPC server authorization setup.

Risks: Missing a protocol leaves it without the intended service ACL mapping; mapping a protocol to the wrong key can over- or under-authorize RPC access. The returned array is not defensively copied, so accidental mutation by a caller would affect later consumers.

Test signals: Service authorization tests should verify every HDFS RPC protocol is present with the expected ACL key, secure RPC startup loads this provider, and admin refresh/reconfiguration/lifeline protocols enforce their configured ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HDFSPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HdfsDtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HdfsDtFetcher.java

Purpose: Implements the `DtFetcher` SPI for HDFS delegation token acquisition. It lets generic token-fetching tools obtain HDFS tokens without compile-time coupling to a specific filesystem implementation.

Important APIs and functions: `getServiceName()` returns `hdfs`. `isTokenRequired()` delegates to `UserGroupInformation.isSecurityEnabled()`. `addDelegationTokens(Configuration, Credentials, String, String)` normalizes an HDFS URL, opens a `FileSystem`, requests a delegation token for the renewer, adds it to `Credentials`, and returns it.

Control flow: If the supplied URL lacks the `hdfs` scheme prefix, the method prepends `hdfs://`. It creates the filesystem from the URI and configuration, calls `getDelegationToken`, errors if null, then stores the token under its service.

State and persistence behavior: The fetcher itself is stateless. Successful calls mutate the supplied `Credentials` by adding the token. Any persistent token storage is handled by the caller that owns those credentials.

Dependencies and integration points: Depends on Hadoop `DtFetcher`, `FileSystem`, `Credentials`, UGI, token APIs, `HdfsConstants.HDFS_URI_SCHEME`, and runtime SPI discovery. `WebHdfsDtFetcher` and `SWebHdfsDtFetcher` reuse this implementation with different schemes.

Risks: URL normalization is simple prefix checking; malformed authorities can still flow to `FileSystem.get`. A null token is escalated as an IOException after logging. The filesystem object is not explicitly closed here, relying on `FileSystem` caching/lifecycle.

Test signals: Token fetch tests should cover secure vs insecure `isTokenRequired`, URLs with and without scheme, token addition to credentials, null token failure, invalid URI handling, and SPI lookup for the HDFS service name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HdfsDtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/NameNodeProxies.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/NameNodeProxies.java

Purpose: Creates RPC proxy objects for communicating with NameNodes and related NameNode-hosted protocols, selecting HA failover proxies for logical URIs and direct non-HA proxies for concrete NameNode addresses.

Important APIs and functions: `createProxy()` builds an HA or non-HA `ProxyAndInfo<T>`. `createNonHAProxy()` creates direct proxies for `ClientProtocol`, `JournalProtocol`, `NamenodeProtocol`, `GetUserMappingsProtocol`, `RefreshUserMappingsProtocol`, `RefreshAuthorizationPolicyProtocol`, `RefreshCallQueueProtocol`, `InMemoryAliasMapProtocol`, and combined `BalancerProtocols`. Protocol-specific helpers instantiate protobuf PB proxies and client-side translators. `createNameNodeProxy()` sets `ProtobufRpcEngine2` and calls `RPC.getProtocolProxy`.

Control flow: `createProxy()` asks `NameNodeProxiesClient.createFailoverProxyProvider()` whether the URI is logical/HA. Without a provider it resolves the concrete NN address and creates a direct proxy with the current user; with a provider it delegates HA proxy construction. Direct proxy creation builds a delegation-token service from the NN address, dispatches on the requested protocol class, optionally wraps `NamenodeProtocol` in retry policies for `getBlocks` and `getAccessKeys`, and combines client and namenode protocols for balancer use.

State and persistence behavior: This class is stateless. Created proxies hold network connections, retry policy wrappers, token-service metadata, and optional alignment context supplied by the caller. `Configuration` is modified transiently by setting protocol engines for PB interfaces.

Dependencies and integration points: Depends on `NameNodeProxiesClient`, `NameNodeHAProxyFactory`, HA failover provider classes, Hadoop RPC, `ProtobufRpcEngine2`, protocol PB interfaces/translators, security/UGI, `SecurityUtil`, `RetryProxy`, `RetryPolicies`, `ProxyCombiner`, and `AlignmentContext`. It is central to DFSClient, balancer, journal, alias map, and admin command RPC setup.

Risks: Unsupported protocol classes throw `IllegalStateException`; adding a new NameNode protocol requires updating this dispatch table. Incorrect retry wrapping can change admin/client behavior. Fallback-to-simple-auth and alignment context must be passed only where supported. Direct proxies bypass HA failover, so callers must choose the creation path correctly.

Test signals: Tests should create proxies for each supported protocol, verify HA logical URI selection, non-HA token service construction, retry wrappers for namenode protocol methods, balancer protocol combination, fallback-to-simple-auth propagation, alignment context propagation, unsupported protocol failure, and correct PB engine selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/NameNodeProxies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/SWebHdfsDtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/SWebHdfsDtFetcher.java

Purpose: Specializes `HdfsDtFetcher` for secure WebHDFS (`swebhdfs`) delegation token fetching while reusing the base token acquisition implementation.

Important APIs and functions: Overrides `getServiceName()` to return `WebHdfsConstants.SWEBHDFS_SCHEME`.

Control flow: All token fetch flow is inherited from `HdfsDtFetcher`; only URL scheme normalization changes to `swebhdfs://`.

State and persistence behavior: Stateless. Successful inherited fetches mutate supplied `Credentials` by adding the returned token.

Dependencies and integration points: Depends on `WebHdfsConstants.SWEBHDFS_SCHEME`, `HdfsDtFetcher`, and the Hadoop token fetcher SPI. It is discovered by generic token-fetching tools for SWebHDFS URLs.

Risks: The class declares an unused logger, but behavior risk is primarily inherited from `HdfsDtFetcher`. Scheme mismatch would route secure WebHDFS token requests incorrectly.

Test signals: SPI/service-name tests should verify `swebhdfs` is advertised and inherited token fetching prepends the secure WebHDFS scheme when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/SWebHdfsDtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/WebHdfsDtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/WebHdfsDtFetcher.java

Purpose: Specializes `HdfsDtFetcher` for WebHDFS (`webhdfs`) delegation token fetching while reusing the base token acquisition implementation.

Important APIs and functions: Overrides `getServiceName()` to return `WebHdfsConstants.WEBHDFS_SCHEME`.

Control flow: All token fetch flow is inherited from `HdfsDtFetcher`; only URL scheme normalization changes to `webhdfs://`.

State and persistence behavior: Stateless. Successful inherited fetches mutate supplied `Credentials` by adding the returned token.

Dependencies and integration points: Depends on `WebHdfsConstants.WEBHDFS_SCHEME`, `HdfsDtFetcher`, and the Hadoop token fetcher SPI. It is discovered by token-fetching tools for WebHDFS URLs.

Risks: The class declares an unused logger. Functional risk is inherited URL/token handling plus correct scheme registration.

Test signals: SPI/service-name tests should verify `webhdfs` is advertised and inherited token fetching uses the WebHDFS scheme for scheme-less URLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/WebHdfsDtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSNetworkTopology.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSNetworkTopology.java

Purpose: Extends Hadoop `NetworkTopology` with HDFS-specific storage-type-aware random DataNode selection for block placement. It can choose a random node under a scope while requiring a specific `StorageType` and honoring excluded scopes/nodes.

Important APIs and functions: `getInstance(Configuration)` instantiates the configured topology implementation and initializes it with `DFSTopologyNodeImpl.FACTORY`. `chooseRandomWithStorageType()` is the main storage-aware selector. `chooseRandomWithStorageTypeTwoTrial()` first tries the inherited fast `chooseRandom` path and falls back to storage-aware weighted selection if the sampled node lacks the requested storage. Visible-for-testing `chooseRandomWithStorageType(scope, excludedScope, excludedNodes, type)` contains core availability accounting. Private `chooseRandomWithStorageTypeAndExcludeRoot()` and `getEligibleChildren()` perform recursive weighted descent.

Control flow: Selection normalizes `~scope` into a root search plus excluded scope, validates scope/excluded-scope containment, resolves the scope node, handles leaf DataNodes directly, computes available count by subtracting excluded subtree and excluded node storage-type counts, and returns null when no eligible nodes remain. For inner nodes, it recursively descends; racks choose uniformly from eligible DataNode children, while non-rack inner nodes choose a child weighted by subtree storage counts and continue.

State and persistence behavior: The class reads topology state maintained by `NetworkTopology` and `DFSTopologyNodeImpl`; it does not persist state itself. A static `Random` supplies selection randomness. The inherited `netlock` read lock protects selection against topology mutation.

Dependencies and integration points: Depends on HDFS `DatanodeDescriptor` storage-type metadata, `DatanodeInfo`, Hadoop `Node`/`NodeBase`/`NetworkTopology`, `StorageType`, `DFSConfigKeys`, and reflection-based topology implementation selection. It integrates with block placement policies that need storage-type constraints.

Risks: Correctness depends on `DFSTopologyNodeImpl` storage counts staying synchronized with add/remove/update events. Excluded nodes may arrive as `DatanodeInfo`, forcing path reconstruction and lookup; stale or mismatched names can under-subtract exclusions. Weighted random counts must not include excluded subtrees or zero-count children. The static `Random` is shared and not cryptographic, which is acceptable for placement but relevant for reproducibility.

Test signals: Tests should cover storage-aware selection by rack and multi-level topology, `~scope` exclusions, excluded DataNode and excluded inner-node cases, `DatanodeInfo` exclusion lookup, no-eligible-node null returns, two-trial fast-path success/fallback, uniformity/weight sanity, and concurrent add/remove under topology locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSNetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSTopologyNodeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSTopologyNodeImpl.java

Purpose: Implements the HDFS-specific inner topology node that augments `InnerNodeImpl` with per-subtree storage-type counts. These counts allow `DFSNetworkTopology` to select DataNodes by `StorageType` without scanning the whole topology.

Important APIs and types: `FACTORY` creates `DFSTopologyNodeImpl` inner nodes for topology initialization. `getSubtreeStorageCount(StorageType)` reads aggregate counts. Overridden `add(Node)` and `remove(Node)` maintain topology children and storage counts. `childAddStorage(String, StorageType)` and `childRemoveStorage(String, StorageType)` propagate storage-type count changes from descendants. `getChildrenStorageInfo()` exposes internal count maps for tests.

Control flow: `add()` validates descendant and DataNode type. If the current node is the direct parent, it inserts or replaces the DataNode, initializes child storage info, increments aggregate counts, or updates existing storage info on duplicate add. Otherwise it creates/fetches the next ancestor inner node, recurses, increments leaf count, updates the child-name count map, and increments aggregate counts. `remove()` mirrors this process, decrementing counts and removing empty inner child nodes. Storage update callbacks adjust child and aggregate counts then recurse to the parent.

State and persistence behavior: State is in-memory topology metadata: inherited `children`, `childrenMap`, `numOfLeaves`, and two maps, `childrenStorageInfo` and `storageTypeCounts`. Counts represent number of DataNodes in the subtree that expose each storage type, not number of physical volumes. There is no disk persistence, but this state is long-lived in the NameNode block manager topology.

Dependencies and integration points: Depends on `DatanodeDescriptor` for storage type membership, Hadoop topology `InnerNodeImpl`/`InnerNode`/`Node`, and `StorageType`. It is used by `DFSNetworkTopology` through the factory.

Risks: Count synchronization is delicate across duplicate adds, storage-type changes, removals, and empty inner-node cleanup. `updateExistingDatanode()` mutates a map while iterating over its key set, which is a concurrency/iteration risk in standard Java collections if removal occurs during iteration. Some methods assume callers synchronize or hold topology locks; direct calls without locking can race. Count semantics may be wrong if future placement needs per-storage-instance counts rather than per-DataNode type presence.

Test signals: Tests should add/remove DataNodes with one and multiple storage types, duplicate-add with changed types, child storage add/remove callbacks, multi-level subtree counts, empty inner-node removal, invalid node type rejection, non-descendant rejection, and integration with storage-aware random selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSTopologyNodeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DomainPeerServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DomainPeerServer.java

Purpose: Implements a `PeerServer` backed by a Unix domain socket for local HDFS data-transfer or short-circuit style connections.

Important APIs and functions: Constructors bind/listen on `DomainSocket.getEffectivePath(path, port)` or wrap an existing `DomainSocket`. `getBindPath()` returns the socket path. `setReceiveBufferSize()` and `getReceiveBufferSize()` manipulate domain socket receive buffer attributes. `accept()` accepts a `DomainSocket` and wraps it in `DomainPeer`. `getListeningString()`, `close()`, and `toString()` provide server metadata and cleanup.

Control flow: Accept blocks on `sock.accept()`, then attempts to construct a `DomainPeer`. If peer construction fails, the partially created peer or raw accepted socket is closed before rethrowing.

State and persistence behavior: Holds one bound `DomainSocket`. The socket file/path persists according to `DomainSocket` behavior until closed/unlinked by that layer. No additional state is stored.

Dependencies and integration points: Depends on Hadoop native `DomainSocket`, `DomainPeer`, and the `PeerServer` interface. It integrates with DataNode peer accept paths that can use domain sockets instead of TCP.

Risks: Domain socket availability and path permissions are platform-dependent. Close logs and suppresses close errors after catching them. Buffer attribute support depends on the native implementation. Failure cleanup must close accepted sockets to avoid descriptor leaks.

Test signals: Tests should bind effective paths, accept local domain clients, verify receive buffer attributes, force `DomainPeer` construction failure for cleanup, close idempotently, and validate listening strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DomainPeerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/PeerServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/PeerServer.java

Purpose: Defines the common server-side abstraction for accepting HDFS data-transfer peers, independent of whether the underlying transport is TCP or Unix domain sockets.

Important APIs and functions: `setReceiveBufferSize(int)`, `getReceiveBufferSize()`, `accept()`, `getListeningString()`, and `close()` form the contract implemented by `TcpPeerServer` and `DomainPeerServer`.

Control flow: This interface has no implementation logic. Implementations block in `accept()` until a connection arrives or a configured timeout/error occurs.

State and persistence behavior: No state in the interface. Implementations own sockets or other listening resources and must free them in `close()`.

Dependencies and integration points: Extends `Closeable` and uses `Peer`, `IOException`, and `SocketTimeoutException`. DataNode server code can work against this transport-neutral interface.

Risks: Implementations must keep buffer-size semantics and close behavior consistent. Callers must be prepared for `SocketTimeoutException` separately from other IO failures.

Test signals: Interface-level tests are integration tests that run the same accept/buffer/close expectations against TCP and domain socket implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/PeerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/TcpPeerServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/TcpPeerServer.java

Purpose: Implements a TCP-backed `PeerServer` for HDFS DataNode data-transfer connections, including both regular and pre-bound secure-server-socket construction.

Important APIs and functions: The normal constructor creates a `ServerSocket` or `ServerSocketChannel`-backed socket depending on write-timeout needs, then binds via `Server.bind`. The secure constructor wraps `SecureResources.getStreamingSocket()`. `getStreamingAddr()` returns the bound IP and port. `setReceiveBufferSize()`, `getReceiveBufferSize()`, `accept()`, `getListeningString()`, `close()`, and `toString()` implement `PeerServer`.

Control flow: Normal construction selects channel-backed sockets when socket write timeout is positive, binds with configured backlog, and later `accept()` converts accepted sockets to Hadoop `Peer` objects using `DFSUtilClient.peerFromSocket`.

State and persistence behavior: Holds one `ServerSocket`, either created locally or supplied by secure DataNode startup. No additional persistent state is kept.

Dependencies and integration points: Depends on Java networking, Hadoop IPC `Server.bind`, `DFSUtilClient.peerFromSocket`, `SecureDataNodeStarter.SecureResources`, and `PeerServer`. It is used by DataNode xfer server setup.

Risks: Secure mode depends on the pre-bound socket lifecycle from privileged startup. `getStreamingAddr()` uses `getHostAddress()` and local port, which may differ from advertised hostnames. Close logs and suppresses close errors. Channel-backed socket choice must match write-timeout behavior expected by peers.

Test signals: Tests should bind normal and secure sockets, verify backlog/bind address, accept a TCP client and produce a `Peer`, check receive buffer sizing, verify streaming address for wildcard/specific binds, and close under active/idle states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/TcpPeerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/BlockListAsLongs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/BlockListAsLongs.java

Purpose: Encodes and decodes DataNode block reports efficiently as packed protobuf `ByteString` buffers while preserving compatibility with the old long-array block report format. It avoids repeated boxed protobuf longs during large block reports.

Important APIs and types: Static factories include `decodeBuffer()`, `decodeBuffers()`, `decodeLongs()`, `encode()`, `readFrom()`, `writeTo()`, and `builder()`. Abstract methods expose `getNumberOfBlocks()`, `getBlocksBuffer()`, `getBlockListAsLongs()`, and an iterator. `Builder` writes replicas as four varints: block id, bytes, generation stamp, and replica state. `BufferDecoder` iterates packed ByteString reports and can transcode to legacy longs. `LongsDecoder` iterates legacy reports and can transcode to packed buffers. `BlockReportReplica` extends `Block` and implements `Replica` with replica state.

Control flow: Builders write each replica with zig-zag block id encoding and unsigned varints for length/generation/state, counting finalized replicas for legacy conversion. `readFrom()` parses a small protobuf envelope with field 1 `numBlocks` and field 2 `blocksBuf`. `BufferDecoder.iterator()` reuses a single `BlockReportReplica` object while reading four fields per block and masking reserved bits. Legacy decoding reads finalized block triples, validates the `-1,-1,-1` delimiter, then reads under-construction block triples plus state.

State and persistence behavior: Instances hold immutable or effectively immutable encoded buffers plus counts; `BufferDecoder` lazily computes and caches `numFinalized` when transcoding. The serialized form is a compatibility-sensitive wire format between DataNodes and NameNodes. Iterators reuse a mutable `BlockReportReplica`, so returned objects should not be retained without copying.

Dependencies and integration points: Depends on HDFS `Block`, DataNode `Replica`, `ReplicaState`, protobuf `ByteString`/coded streams, IPC maximum data length configuration, and DataNode volume interfaces for unsupported `Replica` methods. It integrates with block report RPC serialization/deserialization.

Risks: Encoded format changes are wire-compatibility sensitive. Iterator object reuse can surprise callers who store references. Size limits must be set on coded streams to avoid oversized data. Legacy delimiter validation catches malformed long arrays, but malformed packed buffers surface as `IllegalStateException` during iteration. Masks reserve upper bits for future use; incorrect masking can corrupt block length or state.

Test signals: Tests should cover empty reports, packed encode/decode round trip, chunking via `getBlocksBuffers()`, protobuf `readFrom`/`writeTo`, legacy finalized and under-construction reports, delimiter failure, max data length limits, iterator reuse expectations, reserved upper-bit masking, and transcoding between packed and long formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/BlockListAsLongs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirective.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirective.java

Purpose: Represents a NameNode cache directive: a path to cache, replication factor, owning cache pool, expiry time, computed cache statistics, and intrusive-list membership in the pool.

Important APIs and types: Constructors accept `CacheDirectiveInfo` or explicit id/path/replication/expiry. Getters expose id, path, replication, pool, expiry time, and formatted expiry. `toInfo()`, `toStats()`, and `toEntry()` convert internal state to protocol objects. Statistics methods reset or add bytes/files needed/cached and propagate deltas to the owning `CachePool`. Intrusive collection methods `insertInternal`, `setPrev`, `setNext`, `removeInternal`, `getPrev`, `getNext`, and `isInList` maintain list links.

Control flow: Construction validates positive id and replication and non-null path. `toInfo()` always emits an absolute expiration. `toStats()` computes `hasExpired` from current wall-clock time. Add-stat methods increment directive counters and immediately update pool counters. Intrusive insertion records the pool from the list, and removal clears pool and links.

State and persistence behavior: Persistent NameNode in-memory state includes immutable id/path/replication/expiry, mutable pool pointer, mutable stats, and intrusive prev/next links. Cache directive persistence to fsimage/edit logs is handled elsewhere through info objects; this class converts to protocol records for that process.

Dependencies and integration points: Depends on `CacheDirectiveInfo`, `CacheDirectiveStats`, `CacheDirectiveEntry`, `CachePool`, Hadoop `Path`, `DFSUtil.dateToIso8601String`, `IntrusiveCollection`, and `Preconditions`. It integrates with NameNode cache manager and cache pool directive lists.

Risks: Stats updates assume `pool` is non-null; calling add methods before insertion or after removal would fail. Equality/hashCode are id-only, so id uniqueness is required. Wall-clock expiry checks are time-sensitive. Intrusive list assertions may be disabled at runtime, reducing misuse detection.

Test signals: Tests should cover construction validation, conversion to info/stats/entry, expiry status before/after expiry, stat propagation to `CachePool`, reset behavior, intrusive insert/remove/link navigation, id-based equality, and operations attempted outside a pool list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirective.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/FSLimitException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/FSLimitException.java

Purpose: Defines filesystem limit exceptions for HDFS namespace constraints, specifically path component length and maximum directory item count. These exceptions derive from `QuotaExceededException` so callers can handle namespace limits consistently with quota failures.

Important APIs and types: `FSLimitException` is the abstract base. `PathComponentTooLongException` records the offending child name and parent path and formats a limit/length message. `MaxDirectoryItemsExceededException` records the directory path and formats a limit/items message.

Control flow: Constructors populate inherited quota/count/path fields. `getMessage()` builds user-facing explanations using the stored values.

State and persistence behavior: Exception instances carry quota, count, path, and child-name fields for the duration of error handling or RPC serialization. No persistent state is changed.

Dependencies and integration points: Depends on `QuotaExceededException` and HDFS namespace validation paths in `FSDirectory`/NameNode operations. Annotated public/evolving because clients may see these failures.

Risks: Message formatting is part of user/admin diagnostics. Protected no-arg/string constructors exist for serialization but can produce incomplete messages if used incorrectly. The child name is mutable only through construction, so accurate caller values matter.

Test signals: Tests should trigger path component length and directory item limit violations, verify exception types and messages, RPC propagation to clients, and serialization/deserialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/FSLimitException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutFlags.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutFlags.java

Purpose: Defines the feature-flag section protocol for HDFS fsimage/edit layout streams. Current production behavior supports no independent flags and rejects any non-empty feature flag section.

Important APIs and functions: `read(DataInputStream)` reads an int length and requires it to be zero. `write(DataOutputStream)` writes zero. The constructor is private.

Control flow: Reading throws `IOException` for negative lengths or positive lengths, with positive values treated as unsupported flags requiring software upgrade. Writing always emits a zero-length feature flag section.

State and persistence behavior: The only persisted value is the zero integer written to layout streams. No in-memory state is stored.

Dependencies and integration points: Depends on Java data streams. It is tied to layout feature `ADD_LAYOUT_FLAGS` and fsimage/edit log readers/writers.

Risks: Any future feature-flag support must extend this format without breaking old readers. Rejecting positive lengths is deliberate compatibility behavior; changing it changes upgrade semantics. Negative length rejection protects malformed/corrupt input.

Test signals: Tests should read/write zero, reject negative length, reject positive length, and verify fsimage/edit loading behavior around layout versions that include flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutVersion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutVersion.java

Purpose: Tracks HDFS layout-version feature history and provides helpers for building feature maps, checking whether a layout version supports a feature, and deriving current/minimum-compatible layout versions.

Important APIs and types: `BUGFIX_HDFS_2991_VERSION` marks a historical edit-log workaround. `LayoutFeature` is the interface implemented by layout feature enums. `Feature` enumerates pre-rolling-upgrade layout changes from quotas through protobuf fsimage and extended ACL support, including reserved release versions. `FeatureInfo` stores layout version, ancestor version, minimum compatible version, description, reserved status, and special features. `updateMap()`, `supports()`, `getCurrentLayoutVersion()`, `getMinimumCompatibleLayoutVersion()`, and `getString()` are the main helpers.

Control flow: `updateMap()` starts with existing features, checks that features are listed in non-increasing minimum-compatible layout-version order, copies the ancestor feature set for each new layout version, adds any special features, then adds the feature itself. `supports()` looks up a version's sorted feature set. Current and minimum-compatible versions are derived from the last non-reserved feature in the supplied enum array.

State and persistence behavior: This class does not persist state directly, but its constants define compatibility contracts for NameNode/DataNode storage directories, fsimage, and edit logs. Maps passed to `updateMap()` are mutated with layout-version-to-feature-set entries.

Dependencies and integration points: Depends on Java collections and is extended/used by NameNode and DataNode layout version classes. Feature entries correspond to on-disk layout changes in HDFS storage and edit/fsimage formats.

Risks: Feature ordering, ancestor links, and reserved markers are upgrade-critical. A wrong layout version can make newer software misread old storage or allow unsafe downgrade/rolling-upgrade behavior. `updateMap()` throws assertion errors for ordering issues, which are build/test signals rather than recoverable runtime errors.

Test signals: Tests should validate complete feature maps, support checks for representative versions, current/minimum-compatible version derivation excluding reserved entries, ancestor/special feature inheritance, ordering assertion failures, and historical compatibility such as `BUGFIX_HDFS_2991_VERSION` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RecoveryInProgressException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RecoveryInProgressException.java

Purpose: Signals that block replica recovery is already in progress. It lets callers distinguish concurrent recovery conflicts from generic IO failures.

Important APIs and types: `RecoveryInProgressException` extends `IOException` and exposes a single message constructor.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Exception state is the message and inherited stack trace. No persistent state is modified.

Dependencies and integration points: Used by HDFS block recovery paths where a second recovery attempt should be rejected or retried later.

Risks: Overusing generic `IOException` handling can hide the specific recovery-in-progress condition. Message quality matters for diagnostics.

Test signals: Tests should trigger concurrent replica recovery and assert this exception type is propagated or translated correctly to clients/callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RecoveryInProgressException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeException.java

Purpose: Represents rolling-upgrade-specific HDFS failures. It gives upgrade control paths a typed IOException for invalid or unsupported rolling upgrade operations.

Important APIs and types: `RollingUpgradeException` extends `IOException` and exposes a message constructor.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Exception state is the message and stack trace only.

Dependencies and integration points: Used by NameNode/DataNode rolling upgrade code and administrative APIs.

Risks: Generic catch blocks may flatten it to an ordinary IO failure, losing upgrade-specific context. Messages should identify the invalid upgrade state/action.

Test signals: Rolling upgrade tests should assert this type for invalid prepare/finalize/rollback states and verify RPC/client propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotException.java

Purpose: Represents snapshot-related failures in HDFS namespace operations.

Important APIs and types: `SnapshotException` extends `IOException` and provides message, cause, and message-plus-cause constructors.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Carries exception message/cause/stack trace. No persistent state is changed.

Dependencies and integration points: Used by snapshot creation, deletion, rename, listing, and snapshot-diff paths to report invalid snapshot operations.

Risks: Because it is public-looking and not annotated private here, client compatibility of constructors and messages matters. Wrapped causes should be preserved for diagnosing namespace failures.

Test signals: Snapshot tests should assert this type for duplicate snapshots, invalid snapshot roots, deletion constraints, diff errors, and cause-preserving constructor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotInfo.java

Purpose: Carries snapshot metadata for protocol/JMX/UI style consumers, including a nested bean representation used for snapshot status exposure.

Important APIs and types: `SnapshotInfo` stores snapshot name, root, creation time string, protobuf permission, owner, and group with final getters and `toString()`. Nested `Bean` stores snapshot ID, snapshot directory, modification time, and a status string derived from deletion marking.

Control flow: Construction stores supplied immutable fields. `Bean` maps `isMarkedAsDeleted` to status `DELETED` or `ACTIVE`.

State and persistence behavior: Instances are immutable value carriers except for referenced protobuf object immutability. They do not modify namespace state; they serialize/expose snapshot metadata gathered elsewhere.

Dependencies and integration points: Depends on `AclProtos.FsPermissionProto` and HDFS snapshot management/reporting paths. The bean shape is likely consumed by JSON/JMX-style reflection.

Risks: Time fields use different representations between `SnapshotInfo` (`String`) and `Bean` (`long`), so consumers must not conflate them. `toString()` includes permission/owner/group details. Status is stringly typed and must stay consistent with external expectations.

Test signals: Tests should verify getters, string rendering, permission propagation, bean status for active/deleted snapshots, and JSON/JMX serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/UnregisteredNodeException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/UnregisteredNodeException.java

Purpose: Reports attempts by unregistered NameNode-adjacent servers or DataNodes to access the NameNode, including storage UUID conflicts where a different DataNode claims an existing storage identity.

Important APIs and types: Constructors accept `JournalInfo`, `NodeRegistration`, or a conflicting `DatanodeID` plus stored `DatanodeInfo`, and format diagnostic messages.

Control flow: No custom flow beyond selecting the message for each registration failure case.

State and persistence behavior: Exception state is diagnostic text and stack trace. No registration state is changed by the exception itself.

Dependencies and integration points: Depends on `JournalInfo`, `NodeRegistration`, `DatanodeID`, and `DatanodeInfo`. Used by NameNode registration, heartbeat, block report, and journal protocol validation.

Risks: Message construction exposes node identifiers and must be accurate for operators diagnosing duplicate UUID/storage conflicts. Generic IOException handling may obscure registration-specific remediation.

Test signals: Tests should attempt unregistered journal/node access, duplicate DataNode UUID/storage reporting, and verify exception messages and RPC propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/UnregisteredNodeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlackListBasedTrustedChannelResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlackListBasedTrustedChannelResolver.java

Purpose: Implements a trusted-channel resolver that trusts peers unless their IP address appears in configured fixed or variable blacklists. It can apply separate server-side and client-side blacklist settings.

Important APIs and configuration: Extends `TrustedChannelResolver`. Config keys define fixed blacklist file paths, variable blacklist enable flags, variable file paths, and cache refresh seconds for server and client. Defaults point to `/etc/hadoop/fixedBlackList` and `/etc/hadoop/blackList`. `setConf()` builds `CombinedIPList` instances. `isTrusted()` checks the local host against the client blacklist. `isTrusted(InetAddress)` checks a peer address against the server blacklist.

Control flow: `setConf()` loads server fixed/variable settings first, then uses the server fixed/variable defaults as client fallbacks unless client keys override them. Variable lists are enabled only when the corresponding boolean is true; cache seconds are converted to milliseconds. Trust checks invert membership in the blacklist.

State and persistence behavior: Holds two in-memory `CombinedIPList` objects that may reload variable files according to cache expiry. Trust policy is persisted externally in configured list files and Hadoop configuration.

Dependencies and integration points: Depends on `TrustedChannelResolver`, `CombinedIPList`, `Configuration`, and `InetAddress`. Used by data-transfer SASL code to skip handshakes for trusted channels when configured.

Risks: `UnknownHostException` in client-side local-host lookup returns trusted, which is permissive. Missing or stale blacklist files can unintentionally trust peers. Client fallback behavior may reuse server file paths if client keys are absent. Trusting blacklisted logic directly affects whether SASL/encryption wrapping is skipped.

Test signals: Tests should cover fixed and variable blacklist membership, server/client separate config, cache refresh, disabled variable lists, unknown local host behavior, default paths, and integration with SASL trusted-channel bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlackListBasedTrustedChannelResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Receiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Receiver.java

Purpose: Implements the server-side parser/dispatcher for HDFS `DataTransferProtocol` operations. It reads the protocol version and operation code, parses the corresponding protobuf request, continues tracing context, converts protobuf fields to HDFS domain objects, and invokes abstract protocol methods implemented by subclasses.

Important APIs and functions: `initialize(DataInputStream)` stores the input stream. `readOp()` validates `DATA_TRANSFER_VERSION` and reads an `Op`. `processOp(Op)` dispatches to handlers for read, write, replace, copy, block checksum, block group checksum, transfer, short-circuit FD request/release, and shared-memory request. Private handlers parse `OpReadBlockProto`, `OpWriteBlockProto`, `OpTransferBlockProto`, `OpRequestShortCircuitAccessProto`, `ReleaseShortCircuitAccessRequestProto`, `ShortCircuitShmRequestProto`, `OpReplaceBlockProto`, `OpCopyBlockProto`, `OpBlockChecksumProto`, and `OpBlockGroupChecksumProto`.

Control flow: Each handler reads a vint-prefixed protobuf from the stream, starts a trace scope if trace info is present, converts block/token/datanode/storage/checksum/caching fields with `PBHelperClient` and `DataTransferProtoUtil`, calls the corresponding `DataTransferProtocol` method, and closes the trace scope in `finally`. Write and transfer operations convert target arrays and storage types with lengths matched to targets; block group checksum builds a `StripedBlockInfo`.

State and persistence behavior: Persistent instance state is only the current `DataInputStream` and tracer reference. Per-operation state is transient protobuf/domain objects. The invoked protocol methods perform actual block IO, checksum, transfer, or short-circuit state changes elsewhere.

Dependencies and integration points: Depends on `DataTransferProtocol`, generated data-transfer protobufs, `PBHelperClient`, tracing APIs, `CachingStrategy`, `ExtendedBlock`, `DatanodeInfo`, `StorageType`, `StripedBlockInfo`, block tokens, short-circuit shared-memory slot IDs, and checksum options. Subclasses such as DataNode transfer receivers supply concrete operation implementations.

Risks: Version mismatch aborts before protobuf parsing. Any mismatch between protobuf field defaults and method expectations can change wire behavior; optional caching, lazy persist, pinning, storage IDs, and trace fields require careful defaults. Trace scopes must close on all exceptions. `processOp` must be updated when adding new protocol operations.

Test signals: Protocol tests should feed each op with valid and malformed protobufs, verify version mismatch errors, default optional fields, tracing continuation/closure, storage type and target length conversion, striped checksum conversion, short-circuit request variants, unknown op failure, and subclass method argument correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Receiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/WhitelistBasedTrustedChannelResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/WhitelistBasedTrustedChannelResolver.java

Purpose: Implements a trusted-channel resolver that trusts only IP addresses present in configured fixed or variable whitelists. It supports separate server-side peer trust and client-side local trust settings.

Important APIs and configuration: Extends `TrustedChannelResolver`. Config keys define fixed whitelist file paths, variable whitelist enable flags, variable whitelist paths, and cache seconds for server and client. Defaults point to `/etc/hadoop/fixedwhitelist` and `/etc/hadoop/whitelist`. `setConf()` creates `CombinedIPWhiteList` instances. `isTrusted()` checks the local host against the client whitelist. `isTrusted(InetAddress)` checks a peer address against the server whitelist.

Control flow: `setConf()` reads server list configuration, then client list configuration using server values as fallbacks. Variable lists are optional and cache intervals are stored in milliseconds. Trust checks return membership in the whitelist.

State and persistence behavior: Holds server and client `CombinedIPWhiteList` objects that may refresh variable files after cache expiry. Policy persists in Hadoop configuration and external whitelist files.

Dependencies and integration points: Depends on `TrustedChannelResolver`, `CombinedIPWhiteList`, `Configuration`, and `InetAddress`. Used by data-transfer SASL/encryption logic to decide trusted-channel bypass.

Risks: `UnknownHostException` in client local-host lookup returns false, which is fail-closed. Missing whitelist files can force SASL/encryption on all channels. Client fallback paths can unintentionally mirror server whitelist config. Because trust bypasses negotiation, whitelist contents are security-sensitive.

Test signals: Tests should cover fixed/variable whitelist membership, server/client config separation, cache refresh, unknown local host fail-closed behavior, default paths, absent files, and integration with SASL trusted-channel bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/WhitelistBasedTrustedChannelResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/package-info.java

Purpose: Declares the `org.apache.hadoop.hdfs.protocol.datatransfer` package as containing HDFS data transfer protocol classes and marks the package interface stability as evolving.

Important APIs and types: The file applies `@InterfaceStability.Evolving` to the package and imports `InterfaceStability`.

Control flow: No runtime control flow; this is package metadata compiled into package annotations.

State and persistence behavior: No state. The annotation communicates API compatibility expectations to developers and generated docs.

Dependencies and integration points: Depends on Hadoop classification annotations. It documents the package containing `Receiver`, trusted channel resolvers, protocol helpers, and data-transfer operation types.

Risks: Annotation changes affect compatibility messaging but not runtime behavior. Removing the file would lose package-level stability metadata.

Test signals: Build/javadoc/package annotation checks can verify the package annotation is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/InvalidMagicNumberException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/InvalidMagicNumberException.java

Purpose: Signals that a SASL data-transfer negotiation did not begin with the expected magic number, and records whether the failed handshake was for encryption.

Important APIs and types: `InvalidMagicNumberException` extends `IOException`. The constructor formats the received value against `DataTransferSaslUtil.SASL_TRANSFER_MAGIC_NUMBER` and stores `handshake4Encryption`. `isHandshake4Encryption()` exposes that flag.

Control flow: Created by SASL negotiation code immediately after reading an unexpected magic number.

State and persistence behavior: Carries the formatted message, stack trace, and boolean handshake context for error handling. No persistent state is changed.

Dependencies and integration points: Depends on `DataTransferSaslUtil.SASL_TRANSFER_MAGIC_NUMBER` and is thrown by `SaslDataTransferServer`/related SASL paths when peers speak the wrong preamble or an old/non-SASL protocol.

Risks: The magic number is logged/formatted in hex; diagnostics depend on accurately preserving the received value. The encryption flag affects client/server interpretation of fallback or error behavior.

Test signals: Tests should feed invalid magic numbers for encrypted and non-encrypted handshakes, assert message contents and `isHandshake4Encryption()`, and verify caller error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/InvalidMagicNumberException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferServer.java

Purpose: Performs server-side SASL negotiation for inbound HDFS DataTransferProtocol connections. It supports encrypted data transfer using data encryption keys, general SASL quality-of-protection negotiation using block tokens, trusted-channel bypass, privileged-port bypass, customized callback handling, cipher-option negotiation, and specific error responses for invalid keys/tokens.

Important APIs and types: The constructor accepts `DNConf` and `BlockPoolTokenSecretManager`. `receive(Peer, OutputStream, InputStream, int, DatanodeID)` is the entry point and returns an `IOStreamPair`, possibly wrapped by SASL or cipher streams. Private `getEncryptedStreams()` handles the encryption-key handshake. `getSaslStreams()` handles general SASL protection. `PasswordFunction` and `SaslServerCallbackHandler` supply passwords to the SASL server and delegate unknown callbacks to an optional `CustomizedCallbackHandler`. `getEncryptionKeyFromUserName()`, `buildServerPassword()`, and `deserializeIdentifier()` derive passwords from encrypted-handshake usernames or block token identifiers. `doSaslHandshake()` executes the two-step SASL exchange and cipher negotiation. `getNegotiatedQOP()` exposes the last negotiated QOP for tests.

Control flow: `receive()` first enforces the DataNode configuration decision tree: encrypted transfer always uses encrypted handshake unless the channel is already secure/trusted; insecure clusters skip SASL; secure clusters on privileged ports skip SASL; secure unprivileged clusters with a SASL properties resolver perform general SASL; testing-only insecure secure-port bypass skips; otherwise it throws configuration failure. Handshake reads and validates the SASL magic number, reads an initial SASL message that may carry dynamic QOP secret/BPID, creates a server participant, evaluates client responses, reads client cipher options, completes SASL, optionally negotiates a cipher suite for privacy QOP, sends the final response plus wrapped cipher option, and returns either cipher streams or SASL-wrapped streams.

State and persistence behavior: Persistent instance state is `dnConf`, `blockPoolTokenSecretManager`, and test-only `negotiatedQOP`. Handshake state is transient: SASL participant, dynamic properties, callbacks, cipher options, and stream wrappers. It does not persist tokens/keys; it retrieves passwords or encryption keys from the secret manager.

Dependencies and integration points: Depends on `DataTransferSaslUtil` helpers, Java SASL callbacks, Hadoop `SaslPropertiesResolver`, UGI/security utilities, `BlockPoolTokenSecretManager`, `BlockTokenIdentifier`, `DNConf`, `TrustedChannelResolver`, `Peer`, `IOStreamPair`, `CipherOption`, `DatanodeID`, customized callback handlers, and data-transfer encryptor protobuf statuses. It integrates directly with the DataNode xfer server before `Receiver` processes data-transfer ops.

Risks: The handshake decision tree is security-critical; a wrong trusted-channel or privileged-port decision can skip protection. `doSaslHandshake()` mutates both `saslProps` and `dynamicSaslProps` when a secret QOP arrives, so shared property maps must not leak unintended QOP changes. Username parsing for encryption requires exactly keyId, blockPoolId, and nonce. Invalid key/token errors are deliberately specialized so clients can refresh credentials; generic errors may not trigger the right retry. Cipher negotiation must wrap the option before sending and create matching stream pairs. The test-only `negotiatedQOP` is overwritten by concurrent handshakes if the server instance is shared.

Test signals: Tests should cover encrypted transfer, general SASL with auth/int/privacy QOP, trusted secure-channel bypass, trusted resolver bypass, insecure cluster bypass, privileged-port bypass, invalid unprivileged secure configuration, malformed magic number, malformed encryption username, expired/invalid encryption key, expired/invalid block token, customized callback invocation, dynamic QOP secret handling, cipher suite negotiation success/failure, stream wrapping mode, and concurrent handshakes observing `negotiatedQOP` only as test state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferServer.java -->
