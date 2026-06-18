# subset-b-008015 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaLoader.java

## Purpose
`NodeSchemaLoader` is the parsing and validation utility for SCM network topology schema files. It accepts either XML or YAML input, normalizes the result into an ordered root-to-leaf `List<NodeSchema>`, and returns that list with the topology `enforcePrefix` flag in `NodeSchemaLoadResult`.

## Important APIs, Types, And Functions
`getInstance()` exposes a process-wide singleton. `loadSchemaFromFile()` resolves an absolute/relative filesystem path first, then falls back to the context class loader. `loadSchemaFromStream()` dispatches by filename extension. XML parsing flows through `loadSchema()`, `loadLayoutVersion()`, `loadLayersSection()`, `loadTopologySection()`, and `parseLayerElement()`. YAML parsing uses `YamlUtils.loadAs(..., NodeSchema.class)` and follows the first sublayer chain.

## Control Flow
XML files must have one `<configuration>`, one `<layoutversion>` equal to `1`, one `<layers>`, and one `<topology>`. Layer definitions are parsed into a map keyed by layer id, then topology `<path>` orders those ids and verifies the path starts with `ROOT`, ends with `LEAF_NODE`, and has the same depth as the layer set. YAML files are expected to deserialize into a root `NodeSchema` and then a linear first-child path.

## State, Persistence, And Dependencies
The loader is stateless except for a non-synchronized volatile singleton. It reads schema files/resources only and persists nothing. It depends on secure XML parsing via `XMLUtils.newSecureDocumentBuilderFactory()`, Apache Commons helpers, `YamlUtils`, `NodeSchema`, `NetConstants`, and DOM APIs.

## Integration Points
`NodeSchemaManager` uses this class during SCM network topology initialization. The resulting schema list drives path completion, network levels, and topology costs used by placement and sorting code.

## Risks
The singleton initialization is not fully synchronized, though duplicate instances are harmless because the class holds no mutable parse state. YAML parsing only follows `getSublayer().get(0)`, so branching schemas are ignored. XML duplicate detection uses `schemas.containsValue(schema)`, so it depends on `NodeSchema.equals()` semantics. A bad YAML extension such as `.yml` falls through to XML parsing because only `.yaml` is recognized.

## Test Signals
Useful tests cover missing files, classpath resource loading, invalid layout versions, duplicate root/leaf layers, prefix enforcement failures, bad topology paths, YAML root/leaf validation, and `.yaml` versus XML dispatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaManager.java

## Purpose
`NodeSchemaManager` is the runtime holder for network topology schema metadata. It initializes schemas from configuration or tests, stores them from root to leaf, exposes level costs, completes partial paths when prefix enforcement is enabled, and converts protobuf network nodes back into in-memory topology nodes.

## Important APIs, Types, And Functions
`init(ConfigurationSource)` reads `OZONE_SCM_NETWORK_TOPOLOGY_SCHEMA_FILE`; `init(String)` directly loads a file; test-only `init(NodeSchema[], boolean)` injects schemas. `getMaxLevel()` and `getCost(int)` expose topology metadata. `complete(String)` fills missing inner levels using schema default names. `fromProtobuf(HddsProtos.NetworkNode)` dispatches to `DatanodeDetails` or `InnerNodeImpl`.

## Control Flow
Initialization delegates to `NodeSchemaLoader`, copies the returned schema list, records `enforcePrefix`, and sets `maxLevel` to the number of schema layers. `complete()` normalizes the input path, returns `null` when prefixes are not enforced, returns the original path when already complete, otherwise scans input components against inner-node schema prefixes and inserts defaults for missing levels before appending the leaf component.

## State, Persistence, And Dependencies
State is held in process fields: `allSchema`, `enforcePrefix`, and `maxLevel`. There is no persistence beyond the loaded schema file. Dependencies include SCM config keys, topology utilities, Guava `Preconditions`, protobuf models, and datanode/topology conversion classes.

## Integration Points
The manager is the shared schema authority for SCM topology-aware placement and RPC reporting. `ScmBlockLocationProtocolClientSideTranslatorPB` reconstructs network topology trees from protobufs that use the same `Node` model.

## Risks
Singleton creation is not synchronized. Methods assume `init()` has been called; otherwise `allSchema` and `maxLevel` can be invalid. `complete()` uses string splitting on normalized paths and returns `null` on ambiguous paths, so callers need a fallback. The method returns the original `path` when complete rather than the normalized path.

## Test Signals
Tests should exercise config-based loading, injected schemas, prefix and non-prefix completion, invalid level cost requests, protobuf conversion for datanodes and inner nodes, and behavior before initialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java

## Purpose
The package declaration documents `org.apache.hadoop.hdds.scm.net` as the network topology package for Ozone/SCM.

## Important APIs, Types, And Functions
This file exports no runtime API. It gives package-level JavaDoc context for classes such as `NodeSchemaLoader`, `NodeSchemaManager`, `Node`, `InnerNode`, and topology utility implementations in the same package.

## Control Flow
There is no executable control flow.

## State, Persistence, And Dependencies
There is no state or persistence. The only dependency is the Java package declaration.

## Integration Points
Package documentation appears in generated JavaDocs and helps group topology schema, node tree, and network path code.

## Risks
The comment is broad and does not describe schema loading, prefix enforcement, or protobuf conversion details, so readers need the concrete class docs for operational behavior.

## Test Signals
No runtime tests are applicable; JavaDoc/package generation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocol.java

## Purpose
`ScmBlockLocationProtocol` is the public Java RPC contract for clients that need SCM block placement, block deletion, SCM identity, HA membership, datanode sorting, and network topology retrieval.

## Important APIs, Types, And Functions
The interface is `Closeable`, Kerberos-protected with the SCM principal, and exposes `versionID = 1L` for Hadoop RPC compatibility. Core methods include `allocateBlock(...)`, `deleteKeyBlocks(...)`, `getScmInfo()`, `addSCM(...)`, `sortDatanodes(...)`, and `getNetworkTopology()`. Deprecated overloads translate proto replication type/factor into `ReplicationConfig`.

## Control Flow
The interface itself has no server-side implementation, but its default methods funnel older allocation signatures into the newer `ReplicationConfig`-based allocation path and optionally pass a client machine for topology sorting.

## State, Persistence, And Dependencies
There is no local state. The API depends on replication configs, SCM metadata, `AllocatedBlock`, `ExcludeList`, Ozone block group deletion result types, datanode details, and topology `InnerNode`.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` implements this interface for protobuf RPC. OM and other clients use it to allocate blocks and delete key block groups. The protocol pairs with `ScmBlockLocationProtocolPB` on the wire.

## Risks
Compatibility depends on preserving `versionID` and semantic behavior of deprecated overloads. The allocation API throws both IO and timeout-related failures across implementations, and callers must supply sensible exclude lists and replication configs.

## Test Signals
Contract tests should verify default overload translation, EC/Ratis/standalone allocation semantics through the translator/server pair, delete result mapping, SCM info retrieval, topology tree retrieval, and Kerberos/protocol annotation compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocol.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocol.java

## Purpose
`StorageContainerLocationProtocol` is the broad client-facing SCM container and admin RPC contract. It covers container allocation/listing/deletion, container replicas, datanode administration, pipelines, SCM info and leadership, safe mode, replication manager, container balancer, upgrade finalization, container tokens, metrics, reconciliation, and container report suppression.

## Important APIs, Types, And Functions
The interface is `Closeable`, Kerberos-protected, and keeps `versionID = 1L` for Hadoop RPC reflection. `ADMIN_COMMAND_TYPE` identifies commands that should run on every SCM instance, while `FOLLOWER_READABLE_COMMAND_TYPES` identifies safe-mode queries that can target followers. The API uses `ContainerWithPipeline`, `ContainerInfo`, `ContainerListResult`, `Pipeline`, `ReplicationManagerReport`, `StatusAndMessages`, `Token<?>`, and many protobuf response types.

## Control Flow
As an interface, control flow is defined by method contracts. Overloads move callers from legacy replication factor APIs toward `ReplicationConfig`. Some methods are read-only lookups, while others mutate SCM state or coordinate HA/cluster operations such as decommissioning, leadership transfer, safe mode exit, and balancer start/stop.

## State, Persistence, And Dependencies
No local state exists in this file. The backing SCM implementation persists container, pipeline, node, deleted-block, secret-token, and HA state. Dependencies span `hdds` client configs, datanode and container models, protobuf command types, Apache Commons `Pair`, and Ozone upgrade types.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` implements this interface and maps each method into `StorageContainerLocationProtocolProtos.Type`. CLI/admin tools, OM, datanodes, balancer tooling, and security/token flows use this contract to communicate with SCM.

## Risks
This interface is high blast-radius: adding or changing methods requires translator, server-side, protobuf, retry/failover, and compatibility updates. Admin command routing semantics are encoded here and consumed by the translator. Deprecated methods must remain harmless for older clients.

## Test Signals
Strong tests include method-to-proto routing, all overload combinations for container listing, follower-targeted safe-mode reads, multi-SCM admin fan-out, EC and replicated allocation, token issuance, upgrade finalization status mapping, and compatibility checks for `versionID`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java

## Purpose
This package-level JavaDoc identifies `org.apache.hadoop.hdds.scm.protocol` as the home of SCM protocol interfaces.

## Important APIs, Types, And Functions
The file exports no executable API. Its main referenced artifacts are `ScmBlockLocationProtocol` and `StorageContainerLocationProtocol`, which define the Java-side contracts used by protobuf translators and SCM server implementations.

## Control Flow
There is no control flow.

## State, Persistence, And Dependencies
There is no state, persistence, or external dependency beyond the package declaration.

## Integration Points
The package documentation groups public SCM RPC contract classes for generated JavaDocs and source navigation.

## Risks
The summary is intentionally minimal and does not distinguish block-location and container-location protocols.

## Test Signals
No runtime tests are needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolClientSideTranslatorPB.java

## Purpose
This class is the protobuf client-side implementation of `ScmBlockLocationProtocol`. It converts Java block-location API calls into wrapped `SCMBlockLocationRequest` protobuf messages, sends them through a retry/failover proxy, converts protobuf responses back to domain objects, and normalizes SCM error statuses into `SCMException`.

## Important APIs, Types, And Functions
The constructor accepts `SCMBlockLocationFailoverProxyProvider` and `OzoneConfiguration`, builds a Hadoop `RetryProxy`, and computes `ratisByteLimit` as 90% of the SCM HA Raft appender queue byte limit. `allocateBlock()`, `deleteKeyBlocks()`, `getScmInfo()`, `addSCM()`, `sortDatanodes()`, and `getNetworkTopology()` implement the protocol. Helper methods include `createSCMBlockRequest()`, `submitRequest()`, `handleError()`, `submitDeleteKeyBlocks()`, and recursive `setParent()`.

## Control Flow
Every RPC creates a wrapper with command type, current client version, and trace ID. Allocation validates positive size, encodes Ratis/standalone/EC replication fields, submits `AllocateScmBlock`, and maps returned block IDs and pipelines. Block deletion batches `KeyBlocks` so each submit stays under the computed byte budget. Topology retrieval reconstructs an `InnerNodeImpl` tree and then restores parent links recursively.

## State, Persistence, And Dependencies
State is limited to the RPC proxy, failover provider, and byte limit. It persists nothing. Dependencies include protobuf classes, replication config subclasses, tracing utilities, Hadoop `RetryProxy`, SCM failover provider, `Pipeline`, `AllocatedBlock`, and topology node classes.

## Integration Points
OM and other clients use this translator behind the Java block protocol. It relies on `ScmBlockLocationProtocolPB` for the wire service and `SCMBlockLocationFailoverProxyProvider` for HA behavior.

## Risks
Unsupported replication types throw before RPC. Delete batching depends on serialized protobuf sizes and leaves room for headers by using a fixed 0.9 factor. `handleError()` maps enum ordinals directly to `SCMException.ResultCodes`, so enum ordering compatibility matters. `setParent()` assumes tree nodes are mutable and represented by `InnerNodeImpl`.

## Test Signals
Tests should cover request fields for Ratis, standalone, and EC allocation; delete batching around the byte threshold; non-OK status mapping; trace ID propagation; topology parent restoration; close behavior; and failover retry integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolPB.java

## Purpose
`ScmBlockLocationProtocolPB` is the Hadoop RPC protobuf service interface for SCM block-location operations.

## Important APIs, Types, And Functions
It extends `ScmBlockLocationProtocolService.BlockingInterface` generated from protobuf and adds Hadoop annotations: `@ProtocolInfo` with protocol name `org.apache.hadoop.hdds.scm.protocol.ScmBlockLocationProtocol` and version `1`, `@KerberosInfo` using the SCM principal config key, and private interface audience.

## Control Flow
There is no implementation in this file. Hadoop RPC invokes the generated blocking `send` method through implementations and client translators.

## State, Persistence, And Dependencies
The interface holds no state. It depends on generated protobuf service classes, SCM config constants, Hadoop protocol annotations, and Kerberos metadata.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` creates retry proxies of this type. Server-side SCM protobuf translators implement the same blocking interface.

## Risks
Changing the protocol name or version is wire-incompatible with Hadoop RPC clients. Annotation drift can break Kerberos principal resolution.

## Test Signals
Compatibility tests should assert protocol name/version and successful RPC proxy construction against an SCM block service.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolClientSideTranslatorPB.java

## Purpose
This class is the protobuf client-side implementation of `StorageContainerLocationProtocol`. It maps the large Java SCM container/admin API onto `ScmContainerLocationRequest` messages, applies HA routing rules, and converts responses into container, pipeline, admin, balancer, upgrade, token, and metrics domain objects.

## Important APIs, Types, And Functions
Constructors accept `SCMContainerLocationFailoverProxyProvider` and optional `ScmNodeTarget`. `submitRequest()` builds common wrappers with command type, client version, and trace ID. `submitRpcRequest()` routes follower-readable commands to a target SCM node when requested, sends admin commands to all SCM proxies, and sends ordinary commands through the retry proxy. The class implements allocation, lookup, listing, datanode admin, pipeline lifecycle, safe mode, replication manager, container balancer, datanode usage, upgrade finalization, container token, metrics, reconcile, and suppress APIs.

## Control Flow
Most methods validate inputs, build a command-specific protobuf request, call `submitRequest(Type, builderConsumer)`, and map the response. Allocation handles EC separately and sets factor one for backward compatibility. Listing combines optional state, type, replication config, and suppression filters. Admin commands are faned out across all proxies, retaining only the last response. Deprecated deleted-block methods return empty/zero; the deprecated factor-based list call throws unsupported.

## State, Persistence, And Dependencies
State is the retry proxy, failover provider, and optional target SCM node. There is no persistence. Dependencies are extensive: generated storage container protobufs, HDDS container/pipeline/datanode models, tracing, Hadoop `RetryProxy`/`RPC`, protobuf token helpers, Ozone upgrade status, and Apache Commons `Pair`.

## Integration Points
This is the main client translator for SCM admin and container operations. It depends on `StorageContainerLocationProtocolPB` for wire calls and `SCMContainerLocationFailoverProxyProvider` for HA. CLI tools and OM/admin callers exercise these methods.

## Risks
The class is broad and sensitive to protobuf field naming and command-type drift. Admin fan-out ignores all but the last response. `getExistContainerWithPipelinesInBatch()` swallows IO failures and returns an empty list. Some TODOs call out incomplete error handling. Follower targeting is limited to the command set declared in the protocol interface.

## Test Signals
Tests should verify every public method maps to the expected `Type` and request field, follower targeting and admin fan-out behavior, validation failures, EC versus replicated request encoding, safe-mode map conversion, balancer option validation, upgrade status conversion, token decoding, and unsupported deprecated calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolPB.java

## Purpose
`StorageContainerLocationProtocolPB` is the Hadoop RPC protobuf service interface for SCM storage-container and admin operations.

## Important APIs, Types, And Functions
It extends generated `StorageContainerLocationProtocolService.BlockingInterface` and adds Hadoop `@ProtocolInfo` for `org.apache.hadoop.hdds.scm.protocol.StorageContainerLocationProtocol` version `1`, SCM Kerberos principal metadata, and private interface audience.

## Control Flow
There is no executable implementation. Clients call the generated blocking `submitRequest` through retry proxies; servers implement the generated service contract.

## State, Persistence, And Dependencies
No state is stored. Dependencies are generated protobuf service classes, Hadoop RPC annotations, and SCM config constants.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` creates retry proxies of this type, and SCM exposes a matching protobuf server translator.

## Risks
The protocol name and version are compatibility-critical. Any mismatch between this interface and the Java protocol/translator can break client-server negotiation.

## Test Signals
Signals include successful Hadoop RPC proxy creation, protocol version negotiation, and Kerberos principal resolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java

## Purpose
This package-level JavaDoc identifies `org.apache.hadoop.hdds.scm.protocolPB` as containing client-side storage container protocol classes.

## Important APIs, Types, And Functions
There is no executable API. The package groups protobuf protocol interfaces and client-side translators for SCM block and container location RPC.

## Control Flow
No control flow exists in this file.

## State, Persistence, And Dependencies
There is no state or persistence.

## Integration Points
Generated documentation uses this package description to group the protobuf RPC adapter layer between Java SCM protocols and generated protobuf services.

## Risks
The package description is narrower than the current package, which includes both block and container protocol PB types.

## Test Signals
No runtime tests are applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMBlockLocationFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMBlockLocationFailoverProxyProvider.java

## Purpose
This class specializes the generic SCM failover proxy provider for the block-location protobuf protocol.

## Important APIs, Types, And Functions
The constructor calls `SCMFailoverProxyProviderBase` with `ScmBlockLocationProtocolPB.class`, the configuration source, and no explicit UGI. `getLogger()` returns the class logger. `getProtocolAddress(SCMNodeInfo)` selects `getBlockClientAddress()`.

## Control Flow
All meaningful proxy creation, retry, and failover behavior is inherited. This class only chooses which SCM endpoint field should be used for block client RPC.

## State, Persistence, And Dependencies
No extra state is introduced beyond the base class. It depends on SCM node info and the block PB interface.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` uses this provider to create a retry proxy for block allocation and deletion calls.

## Risks
Incorrect block-client address configuration prevents proxy construction. Because no UGI is passed, the base class uses the current user.

## Test Signals
Tests should assert that block client addresses are loaded and that inherited failover can cycle between block protocol endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMBlockLocationFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMClientConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMClientConfig.java

## Purpose
`SCMClientConfig` defines typed SCM client retry and RPC timeout configuration under the `hdds.scmclient` prefix.

## Important APIs, Types, And Functions
Annotated fields include `hdds.scmclient.rpc.timeout`, `hdds.scmclient.max.retry.timeout`, `hdds.scmclient.failover.max.retry`, and `hdds.scmclient.failover.retry.interval`. Getters expose timeout, max retry timeout, retry count, and retry interval. Setters support configuration object binding.

## Control Flow
`getRetryCount()` derives an effective count from `maxRetryTimeout / retryInterval` and returns the larger of that value and configured retry count. `setRpcTimeOut()` attempts to cap overly large timeouts but checks the existing field before setting the new value.

## State, Persistence, And Dependencies
State is in-memory config object fields. Persistence is external via Ozone configuration. Dependencies are HDDS config annotations and time units.

## Integration Points
`SCMFailoverProxyProviderBase` reads this object to configure RPC timeout, retry count, and retry interval for all SCM client proxy providers.

## Risks
The `setRpcTimeOut()` cap appears ineffective for a too-large incoming `timeOut` because it tests `rpcTimeOut` rather than `timeOut`, then assigns `timeOut`. Bad retry interval values can affect retry-count math.

## Test Signals
Tests should verify config binding, effective retry count calculation, timeout capping behavior, and integration with failover retry policy delays.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMContainerLocationFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMContainerLocationFailoverProxyProvider.java

## Purpose
This class specializes generic SCM failover for `StorageContainerLocationProtocolPB` clients.

## Important APIs, Types, And Functions
The constructor passes the container PB interface, configuration, and optional `UserGroupInformation` to the base class. `getProtocolAddress(SCMNodeInfo)` selects `getScmClientAddress()`.

## Control Flow
All retry, lazy proxy construction, close, and leader failover behavior is inherited from `SCMFailoverProxyProviderBase`.

## State, Persistence, And Dependencies
No additional state is held. Dependencies include SCM node info, the storage container PB interface, and Hadoop UGI.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` uses this provider for ordinary retry-proxy calls, all-SCM admin fan-out via `getProxies()`, and targeted follower-readable calls via `getProxyForNode()`.

## Risks
Misconfigured SCM client addresses break container/admin operations. Caller-provided UGI controls RPC identity; null falls back to current user.

## Test Signals
Tests should verify address selection, UGI propagation, targeted proxy lookup, and inherited failover with container protocol calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMContainerLocationFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMFailoverProxyProviderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMFailoverProxyProviderBase.java

## Purpose
`SCMFailoverProxyProviderBase` implements common Hadoop `FailoverProxyProvider` behavior for SCM protobuf clients. It loads SCM HA node endpoints, lazily creates RPC proxies, tracks the current SCM node, implements round-robin and leader-hint failover, and supplies retry policy logic to Hadoop `RetryProxy`.

## Important APIs, Types, And Functions
Subclasses provide `getLogger()` and `getProtocolAddress(SCMNodeInfo)`. Public methods include `getProxy()`, `getProxies()`, `getProxyForNode()`, `performFailover()`, `performFailoverToAssignedLeader()`, `getSCMNodeIds()`, `getSCMProxyInfoList()`, `close()`, and `getRetryPolicy()`. Internal helpers load configs, create RPC proxies through `RPC.getProtocolProxy()`, and print retry messages.

## Control Flow
Construction resolves UGI, protocol version, SCM node info, endpoint maps, initial node, and retry config. `getProxy()` lazily creates the current node proxy. `performFailover()` switches to an assigned leader when known or rotates round-robin. The retry policy delegates retry/failover decisions to `SCMHAUtils`, records suggested leaders from `ServerNotLeaderException`, and emits user-facing retry messages only when another attempt will occur.

## State, Persistence, And Dependencies
State includes endpoint maps, cached `ProxyInfo` objects, node-id order, current node, retry settings, UGI, and `updatedLeaderNodeID`. There is no persistence. Dependencies include SCM HA utilities, Hadoop IPC/RPC, protobuf RPC engine, UGI, NetUtils, legacy Hadoop config conversion, and retry policy classes.

## Integration Points
All concrete SCM client providers inherit this behavior: block location, container location, SCM security, and secret-key protocols. Translators wrap these providers in Hadoop `RetryProxy`.

## Risks
Most methods are synchronized, but `updatedLeaderNodeID` is not volatile and retry callbacks can be multi-threaded. `System.err.printf` is a deliberate user-facing side effect. `getProxies()` creates every proxy and returns values from a hash map, so fan-out ordering is not deterministic. Config errors surface as runtime exceptions during proxy creation or construction.

## Test Signals
Tests should cover HA config loading, unknown node lookup, lazy creation, close stopping proxies, leader hint matching by host:port, retry action selection, no-failover retriable exceptions, round-robin behavior, and retry message content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMFailoverProxyProviderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMProxyInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMProxyInfo.java

## Purpose
`SCMProxyInfo` is a small value holder for one SCM RPC endpoint: service id, node id, address string, and resolved/unresolved socket address.

## Important APIs, Types, And Functions
The constructor requires a non-null `InetSocketAddress`, records string and object forms, and logs a warning when the address is unresolved. Getters expose address, service id, and node id. `toString()` returns a compact node-id/address pair.

## Control Flow
Construction performs validation and unresolved-address warning. There is no other branching.

## State, Persistence, And Dependencies
State is immutable fields. There is no persistence. Dependencies are `InetSocketAddress`, `Objects`, and SLF4J logging.

## Integration Points
`SCMFailoverProxyProviderBase` stores `SCMProxyInfo` per node id, uses it to create RPC proxies, match server-not-leader suggested leaders, and log configured endpoints.

## Risks
`rpcAddrStr` uses `InetSocketAddress.toString()`, which can include unresolved formatting. The warning is informational; unresolved addresses may still fail later at RPC connection time.

## Test Signals
Tests should verify constructor null rejection, unresolved warnings, getter values, and string formatting used in failover logs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMProxyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMSecurityProtocolFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMSecurityProtocolFailoverProxyProvider.java

## Purpose
This class adapts generic SCM failover to the SCM security protobuf protocol.

## Important APIs, Types, And Functions
The constructor passes `SCMSecurityProtocolPB.class`, configuration, and optional UGI to the base provider. `getProtocolAddress()` selects `SCMNodeInfo.getScmSecurityAddress()`.

## Control Flow
All runtime behavior is inherited. This class only binds the protocol type and security endpoint.

## State, Persistence, And Dependencies
No extra state exists. Dependencies include `SCMSecurityProtocolPB`, SCM node info, UGI, and logging.

## Integration Points
Certificate and security clients use this provider to communicate with SCM security endpoints in HA deployments.

## Risks
Security RPCs depend on correct security-address config and UGI. Any mismatch can block certificate/key operations.

## Test Signals
Tests should verify security address selection and inherited failover/retry behavior against security protocol proxies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMSecurityProtocolFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SecretKeyProtocolFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SecretKeyProtocolFailoverProxyProvider.java

## Purpose
This generic provider adapts SCM failover to protobuf secret-key protocol blocking interfaces.

## Important APIs, Types, And Functions
The class is parameterized as `<T extends SCMSecretKeyProtocolService.BlockingInterface>`. Its constructor accepts configuration, UGI, and the concrete proxy class, then delegates to the base provider. It selects `SCMNodeInfo.getScmSecurityAddress()` as the endpoint.

## Control Flow
Retry, proxy creation, and failover are inherited from `SCMFailoverProxyProviderBase`.

## State, Persistence, And Dependencies
No extra state exists. It depends on generated secret-key protobuf service interfaces, SCM node info, UGI, and logging.

## Integration Points
Secret-key clients use this provider to fetch current and historical symmetric keys from SCM security endpoints. `SingleSecretKeyProtocolProxyProvider` extends it to disable failover for a fixed SCM node.

## Risks
Generic typing must match the generated blocking interface used by the caller. It shares the same security endpoint as SCM security protocol, so config errors affect both.

## Test Signals
Tests should verify generic proxy construction, security address selection, failover behavior, and compatibility with concrete secret-key service interfaces.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SecretKeyProtocolFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SingleSecretKeyProtocolProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SingleSecretKeyProtocolProxyProvider.java

## Purpose
`SingleSecretKeyProtocolProxyProvider` is a secret-key protocol provider pinned to one SCM node, intentionally disabling failover.

## Important APIs, Types, And Functions
The constructor records a fixed `scmNodeId` after initializing the parent provider. `getCurrentProxySCMNodeId()` always returns that id. `performFailover()` and `performFailoverToAssignedLeader()` are no-ops. `getLogger()` returns this class logger.

## Control Flow
Proxy retrieval still uses the inherited lazy creation path, but the current node id is fixed. Retry callbacks cannot move to another SCM node.

## State, Persistence, And Dependencies
The only added state is the fixed SCM node id. There is no persistence. Dependencies are the generic secret-key protocol service class, configuration, and UGI.

## Integration Points
This provider is used when secret-key access must be directed at a particular SCM rather than the HA leader/failover set.

## Risks
If the pinned node is unavailable or stale, retries cannot fail over. The constructor still loads all SCM configs through the base class, so the fixed id must exist in the loaded map.

## Test Signals
Tests should verify no failover occurs, the fixed node is used after retry callbacks, and unknown/misconfigured fixed nodes fail clearly when proxy creation is attempted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SingleSecretKeyProtocolProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/package-info.java

## Purpose
The package JavaDoc identifies `org.apache.hadoop.hdds.scm.proxy` as containing SCM proxy-related classes.

## Important APIs, Types, And Functions
There is no executable API. The package groups failover proxy providers, endpoint metadata, and SCM client retry configuration.

## Control Flow
There is no control flow.

## State, Persistence, And Dependencies
There is no state or persistence.

## Integration Points
Generated JavaDocs use this description for the SCM client HA/proxy package.

## Risks
The summary is broad and omits the distinction between block, container, security, and secret-key proxy providers.

## Test Signals
No runtime tests are applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretKey.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretKey.java

## Purpose
`OzoneSecretKey` wraps an asymmetric key pair with Ozone master-key metadata for delegation and block token signing.

## Important APIs, Types, And Functions
The constructor accepts key id, expiry date, `KeyPair`, and certificate serial id. Getters expose key id, expiry, private/public keys, cert serial id, and encoded key bytes. `equals()` and `hashCode()` compare key id, expiry, and key material.

## Control Flow
There is no complex flow: construction validates the key pair, splits it into private/public fields, and accessors return stored values.

## State, Persistence, And Dependencies
State is in-memory private/public key material plus metadata. Persistence is external. Dependencies include Java security keys and Apache Commons builders.

## Integration Points
`OzoneSecretManager` creates and stores the current `OzoneSecretKey` from `CertificateClient` key material and certificate serials. Token secret managers use it to sign identifiers.

## Risks
The method name `getEncodedPubliceKey()` is misspelled but part of current API. `equals()` compares `PrivateKey`/`PublicKey` objects while `hashCode()` uses encoded bytes; provider-specific equality could differ from encoding equality. Certificate serial id is not included in equality/hash.

## Test Signals
Tests should verify construction, encoded key getters, equality/hash behavior across equivalent key pairs, and compatibility with `OzoneSecretManager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretManager.java

## Purpose
`OzoneSecretManager` is an abstract asymmetric-token secret manager. It signs token identifiers with the current certificate private key, tracks token/key sequence numbers, starts/stops against a `CertificateClient`, and updates signing material when certificates renew.

## Important APIs, Types, And Functions
It extends Hadoop `SecretManager<T>` and implements `CertificateNotification`. Key methods are `createPassword(byte[], PrivateKey)`, `createPassword(T)`, abstract `renewToken()` and `cancelToken()`, sequence/key incrementors, `start(CertificateClient)`, `stop()`, `notifyCertificateRenewed()`, and accessors for lifetimes, service, current key, cert client, and sequence numbers.

## Control Flow
`start()` asserts the manager is not running, stores the certificate client, creates the initial `OzoneSecretKey` from current key/cert, registers for renewal notifications, and marks running. `notifyCertificateRenewed()` logs serial mismatches and replaces the current key from renewed material. `createPassword(T)` signs identifier bytes with the current private key and returns null if identifier serialization fails.

## State, Persistence, And Dependencies
State includes `SecurityConfig`, token lifetimes, service name, certificate client, running flag, `AtomicReference<OzoneSecretKey>`, current key id, and token sequence number. It persists nothing directly. Dependencies include Java `Signature`, certificate/key APIs, Hadoop tokens, and Ozone security exceptions.

## Integration Points
Concrete delegation/block token managers extend this base. It integrates with `CertificateClient` renewal callbacks and `SecurityConfig.getSignatureAlgo()`.

## Risks
`createPassword(T)` can return null on `IOException`, which may surface later. `getCertSerialId()` assumes a current key exists. Renewal mismatch checks only log and still update. Stop only flips a flag and does not unregister notification receivers.

## Test Signals
Tests should cover start/stop state, initial key creation, signature algorithm failures, sequence increments, renewal callback key replacement, mismatch logging, and concrete renew/cancel implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/package-info.java

## Purpose
This package JavaDoc marks `org.apache.hadoop.hdds.security` as containing HDDS security-related classes.

## Important APIs, Types, And Functions
The file exports no runtime API. It groups key/security primitives such as `OzoneSecretKey`, `OzoneSecretManager`, SSL helpers, symmetric secret-key management, and token classes.

## Control Flow
There is no control flow.

## State, Persistence, And Dependencies
There is no state or persistence.

## Integration Points
Used by JavaDoc and source navigation for HDDS security code.

## Risks
The package comment is high-level and does not document the split between asymmetric certificate-backed and symmetric key token flows.

## Test Signals
No runtime tests are applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/KeyStoresFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/KeyStoresFactory.java

## Purpose
`KeyStoresFactory` defines the abstraction for components that create and expose SSL key managers and trust managers for HDDS clients and servers.

## Important APIs, Types, And Functions
The nested `Mode` enum distinguishes `CLIENT` and `SERVER`. `init(Mode, boolean)` initializes key/trust material and may throw IO or security exceptions. `destroy()` releases resources. `getKeyManagers()` and `getTrustManagers()` return arrays for SSL context construction.

## Control Flow
There is no implementation in this interface. Implementations decide how to load, reload, and destroy keystore/truststore resources.

## State, Persistence, And Dependencies
The interface has no state. Implementations may use disk or in-memory stores. Dependencies are Java SSL manager types and security exception classes.

## Integration Points
TLS-enabled HDDS services use implementations to construct SSL contexts. The reloadable key/trust managers in this package are likely returned through this abstraction.

## Risks
Callers must respect initialization ordering; getters before `init()` may be invalid depending on implementation. `requireClientAuth` is ignored in client mode by contract.

## Test Signals
Implementation tests should verify client/server mode initialization, client-auth behavior, SSLContext compatibility, cleanup, and error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/KeyStoresFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509KeyManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509KeyManager.java

## Purpose
`ReloadingX509KeyManager` is an `X509ExtendedKeyManager` that can rebuild its in-memory key manager when certificate material changes, allowing TLS endpoints to use renewed private keys and certificate chains without reconstructing the whole component.

## Important APIs, Types, And Functions
The constructor takes keystore type, component name, private key, and trust chain, and initializes an atomic delegate. It overrides all client/server alias, chain, and private-key methods. `notifyCertificateRenewed()` reloads from `CertificateClient`. Internal `init()` builds an in-memory `KeyStore`, inserts the key entry under `componentName + "_key"`, initializes `KeyManagerFactory`, and stores current material. `isAlreadyUsing()` compares private key and certificate serials.

## Control Flow
Most methods delegate to `keyManagerRef.get()`. `chooseEngineClientAlias()` includes a fallback to the known alias when the delegate returns null, working around native Netty/tc-native stale accepted-issuer behavior during certificate refresh. Renewal callbacks call `init()` and swap the atomic reference only when material changed.

## State, Persistence, And Dependencies
State includes keystore type, alias, current private key, current trust chain, and `AtomicReference<X509ExtendedKeyManager>`. The keystore is in-memory only with an empty password. Dependencies include Java SSL/security APIs and `CertificateClient` notification.

## Integration Points
`DefaultCertificateClient` and SSL context builders use this manager for dynamically renewed mTLS key material.

## Risks
The fallback alias can select a certificate even when the delegate could not match requested principals. `getCertificateChain()` and `getPrivateKey()` lowercase aliases for JDK behavior. Logging full certificate text may be verbose. `isAlreadyUsing()` compares serial sets, not chain order.

## Test Signals
Tests should cover initial key manager creation, delegate alias methods, null alias fallback, certificate renewal reload/no-op, alias lowercase handling, and SSL handshake behavior after renewal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509KeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509TrustManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509TrustManager.java

## Purpose
`ReloadingX509TrustManager` is a reloadable `X509TrustManager` that rebuilds an in-memory trust manager when root CA material changes.

## Important APIs, Types, And Functions
The constructor accepts truststore type and root CA certificates. `checkClientTrusted()`, `checkServerTrusted()`, and `getAcceptedIssuers()` delegate to the current trust manager. `notifyCertificateRenewed()` pulls root CA certificates from `CertificateClient`, falling back to all CA certs when root CA set is empty, then reloads. Internal `init()` constructs a new in-memory `KeyStore`, inserts certs by serial id, and initializes `TrustManagerFactory`.

## Control Flow
Trust checks delegate and log certificate subject principals on failures before rethrowing. Reloading is skipped when the new certificate set has the same serials as the current set. Successful reload swaps `trustManagerRef`.

## State, Persistence, And Dependencies
State includes truststore type, atomic trust manager reference, and the current root CA certificate list. No disk persistence is used. Dependencies include Java SSL/security APIs, certificate notification, and SLF4J.

## Integration Points
Certificate clients register this manager for CA rotation events so long-running TLS endpoints trust renewed or rotated CA chains.

## Risks
If `trustManagerRef` is null and `chain` is empty/null, error construction can access `chain[0]`. Certificate equality is by serial only, not issuer or encoded bytes. Exceptions in renewal are wrapped in runtime exceptions with a fixed reload message.

## Test Signals
Tests should cover initial accepted issuers, client/server trust success and failure logging, reload on changed serials, no-op reload on same serials, empty root set fallback, and null/empty chain behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509TrustManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/package-info.java

## Purpose
This package JavaDoc marks `org.apache.hadoop.hdds.security.ssl` as containing SSL-related classes.

## Important APIs, Types, And Functions
There is no runtime API. The package groups SSL keystore factory abstractions and reloadable X509 key/trust managers.

## Control Flow
There is no control flow.

## State, Persistence, And Dependencies
There is no state or persistence.

## Integration Points
Used by JavaDoc and source navigation for TLS support code.

## Risks
The description is minimal and does not mention certificate-renewal support.

## Test Signals
No runtime tests are applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyClient.java

## Purpose
`DefaultSecretKeyClient` composes separate signer and verifier clients into the combined `SecretKeyClient` interface for components that need both current-key signing and historical-key verification.

## Important APIs, Types, And Functions
It delegates `getCurrentSecretKey()`, `start()`, and `stop()` to a `SecretKeySignerClient`, and delegates `getSecretKey(UUID)` to a `SecretKeyVerifierClient`. Static `create()` wires `DefaultSecretKeySignerClient` and `DefaultSecretKeyVerifierClient` around a `SecretKeyProtocol`.

## Control Flow
There is no independent logic beyond delegation. `start()` only starts the signer side because the verifier cache initializes in its constructor.

## State, Persistence, And Dependencies
State is two delegate references. There is no direct persistence. Dependencies include `SecretKeyProtocol`, configuration, and SCM security exceptions.

## Integration Points
OM/SCM/datanode components can use this combined client when they both issue and verify short-lived symmetric-key tokens.

## Risks
The local variable in `create()` is named `singerClient`, a typo with no behavioral impact. Verifier resources are not stopped because it has no lifecycle method.

## Test Signals
Tests should verify delegation, factory wiring, signer startup/stop behavior, and verifier exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeySignerClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeySignerClient.java

## Purpose
`DefaultSecretKeySignerClient` fetches and caches the current SCM symmetric secret key for token signing, then periodically refreshes it after the configured rotation interval.

## Important APIs, Types, And Functions
The constructor accepts `SecretKeyProtocol` and thread name prefix. `start()` loads the initial key with retry and schedules polling. `getCurrentSecretKey()` returns the cached key and requires initialization. `refetchSecretKey()` forces a refresh check. `stop()` shuts down the scheduled executor. Helpers include `loadInitialSecretKey()`, `scheduleSecretKeyPoller()`, and synchronized `checkAndRefresh()`.

## Control Flow
Initial load retries `SECRET_KEY_NOT_INITIALIZED` with exponential backoff up to 100 retries. Polling computes next rotation from the cached key creation time plus rotate duration. Once the key is older than the rotate duration, it fetches SCM's current key and updates the atomic cache if changed.

## State, Persistence, And Dependencies
State is an atomic cached key, daemon thread factory, scheduled executor, and protocol reference. No persistence is local. Dependencies include secret-key config parsing, Hadoop retry policies, `RetriableTask`, and SCM secret-key exceptions.

## Integration Points
`DefaultSecretKeyClient` uses this for signer-side behavior. Token secret managers use the current key returned here to sign container/block tokens.

## Risks
If scheduled refresh throws `UncheckedIOException`, the scheduled task may stop depending on executor behavior. Negative initial delay can schedule immediately but should be tested. Long initial retry window can delay service startup. Cache access before `start()` throws `NullPointerException` via `requireNonNull`.

## Test Signals
Tests should cover initial retry on not-initialized, fail-fast on other errors, scheduled refresh timing, forced refetch, cache update/no-op, executor shutdown, and get-before-start failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeySignerClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyVerifierClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyVerifierClient.java

## Purpose
`DefaultSecretKeyVerifierClient` fetches historical symmetric secret keys from SCM on demand and caches them locally for token verification.

## Important APIs, Types, And Functions
The constructor builds a Guava `LoadingCache<UUID, Optional<ManagedSecretKey>>` using expiry and rotation durations from `SecretKeyConfig`. `getSecretKey(UUID)` retrieves a key or null and converts IO/SCM security failures into `SCMSecurityException`.

## Control Flow
Cache sizing estimates how many valid keys can exist as `expiry / rotate + 1`, doubles that to retain recently expired keys, and uses a TTL twice the key expiry duration. Cache misses call `secretKeyProtocol.getSecretKey(id)`.

## State, Persistence, And Dependencies
State is the loading cache. There is no persistence. Dependencies include Guava cache, `SecretKeyProtocol`, duration parsing, and SCM security exception types.

## Integration Points
Datanode/token verifier paths use this client to retrieve the specific key referenced by a token's secret-key UUID.

## Risks
If rotate duration is zero or misconfigured, cache size calculation can divide by zero. Optional-empty results are cached, so a key that appears later may remain absent until TTL expiry. The log says TTL is `expiryDuration` though the actual cache expiry is doubled.

## Test Signals
Tests should cover cache hits/misses, null key caching, exception conversion, cache size/TTL calculation, and behavior with invalid duration configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyVerifierClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/LocalSecretKeyStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/LocalSecretKeyStore.java

## Purpose
`LocalSecretKeyStore` persists managed symmetric secret keys to a local JSON file so SCM can reload valid keys across restarts.

## Important APIs, Types, And Functions
The constructor takes a file path and configures Jackson with Java time support and ISO date serialization. `load()` returns an empty list if the file is absent, otherwise deserializes `ManagedSecretKeyDto` entries. `save(Collection)` creates the file/directories, maps keys to DTOs, and writes all entries with `SequenceWriter`. `ManagedSecretKeyDto` stores UUID, creation/expiry times, algorithm, and encoded key bytes.

## Control Flow
`save()` calls `createSecretKeyFiles()`, which creates parent directories/file when needed and sets owner read/write POSIX permissions. Load and save are synchronized.

## State, Persistence, And Dependencies
State is the target path and object mapper. Persistence is the JSON secret-key file with `OWNER_READ` and `OWNER_WRITE` permissions. Dependencies include Jackson, Java crypto key specs, Java NIO file APIs, and POSIX permissions.

## Integration Points
`SecretKeyStateImpl` calls `save()` whenever replicated key state changes, and `SecretKeyManager` calls `load()` during initialization.

## Risks
POSIX permissions may fail on non-POSIX filesystems. Writes are not atomic, so interruption can corrupt the file. The JSON contains raw encoded secret keys and relies on filesystem permissions for protection. Deserialization errors throw `IllegalStateException`.

## Test Signals
Tests should cover absent file loads, round-trip serialization, permission setting, parent directory creation, malformed file behavior, synchronization under concurrent calls, and non-POSIX platform behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/LocalSecretKeyStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/ManagedSecretKey.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/ManagedSecretKey.java

## Purpose
`ManagedSecretKey` wraps a symmetric `SecretKey` with UUID, creation time, expiry time, signing/verification helpers, and protobuf serialization.

## Important APIs, Types, And Functions
Getters expose id, key, creation, and expiry. `isExpired()` compares expiry to now. `sign(byte[])` and `sign(TokenIdentifier)` compute HMAC via `Mac`. `isValidSignature(...)` compares expected and provided signatures with `MessageDigest.isEqual()`. `toProtobuf()` and `fromProtobuf()` convert to generated `ManagedSecretKey` messages.

## Control Flow
`getMac()` caches one `Mac` instance per thread id in a concurrent map, then each signing call initializes that `Mac` with the secret key and signs the data. Equality and hash code are based only on UUID.

## State, Persistence, And Dependencies
State is immutable key metadata and key material plus a per-thread `Mac` cache. Persistence is via protobuf or `LocalSecretKeyStore` DTOs. Dependencies include Java crypto, UUID/time APIs, protobuf byte strings, and Ozone protobuf utilities.

## Integration Points
`SecretKeyManager` generates these keys; signer/verifier clients distribute and cache them; short-lived token managers/verifiers use signing and verification.

## Risks
The raw `ConcurrentHashMap` uses no generic value type in construction. Per-thread `Mac` cache can grow with many transient threads. Equality by UUID ignores key material differences for the same id. Encoded key bytes are serialized over protobuf and local JSON.

## Test Signals
Tests should cover signing/verification, constant-time mismatch path, expiry, protobuf round trip, equality semantics, concurrent signing, and invalid algorithm behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/ManagedSecretKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyClient.java

## Purpose
`SecretKeyClient` is the combined interface for components that both sign with the current secret key and verify using historical keys.

## Important APIs, Types, And Functions
It extends `SecretKeySignerClient` and `SecretKeyVerifierClient` without adding methods.

## Control Flow
There is no control flow in this interface.

## State, Persistence, And Dependencies
The interface has no state. Implementations may cache keys or manage background refresh and persistence.

## Integration Points
`DefaultSecretKeyClient` composes remote signer/verifier clients, while `SecretKeyManager` implements this interface directly for SCM's local key authority.

## Risks
Consumers should be aware that signer and verifier lifecycle semantics differ; `start()` and `stop()` come from signer side only.

## Test Signals
Implementation tests should verify both inherited contracts through the combined type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyConfig.java

## Purpose
`SecretKeyConfig` resolves configuration for symmetric secret-key lifecycle management: local file path, rotation duration, expiry duration, HMAC algorithm, and rotation check interval.

## Important APIs, Types, And Functions
The constructor builds `localSecretKeyFile` from metadata dir, component name, key dir, and file name config keys. Static parsers `parseExpiryDuration()`, `parseRotateDuration()`, and `parseRotateCheckDuration()` read configured durations in milliseconds. Getters expose resolved values.

## Control Flow
Construction reads config keys with defaults and converts durations to `Duration`. It first tries `HDDS_METADATA_DIR_NAME`, falling back to `OZONE_METADATA_DIRS`.

## State, Persistence, And Dependencies
State is immutable resolved config. Persistence is external through the local file path consumed by `LocalSecretKeyStore`. Dependencies are HDDS config constants, `ConfigurationSource`, paths, durations, and time units.

## Integration Points
`SecretKeyManager`, `DefaultSecretKeySignerClient`, and `DefaultSecretKeyVerifierClient` all use these parsed values to manage key generation, polling, caching, and storage.

## Risks
Missing metadata directory can produce an invalid path or null handling issue depending on `Paths.get(...)`. Invalid zero/negative durations can break rotation or cache math because this class does not validate them.

## Test Signals
Tests should cover default resolution, metadata fallback, component-specific path building, duration parsing, algorithm selection, and invalid/missing config handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyManager.java

## Purpose
`SecretKeyManager` is SCM's local manager for symmetric secret-key lifecycle: initialize from persisted state, generate keys, rotate keys, expose current/historical keys, and update replicated key state.

## Important APIs, Types, And Functions
Constructors accept `SecretKeyState`, `SecretKeyStore`, durations, and algorithm or a `SecretKeyConfig`. `checkAndInitialize()` loads non-expired persisted keys or generates a first key. `checkAndRotate(boolean force)` rotates when forced or current key age reaches the rotation duration. `getCurrentSecretKey()`, `getSecretKey(UUID)`, `getSortedKeys()`, and `reinitialize()` expose state.

## Control Flow
Initialization is synchronized and idempotent. It filters expired keys from the store, generates a new key if none remain, then calls `state.updateKeys()`. Rotation first initializes if needed, then creates a new key, filters out expired old keys, appends the new key, and updates state. Key generation uses `KeyGenerator.getInstance(algorithm)`, random UUID, current time, and expiry time.

## State, Persistence, And Dependencies
State is delegated to `SecretKeyState`; persistence is through `SecretKeyStore` invoked by state. The manager holds rotation/validity durations and a `KeyGenerator`. Dependencies include SCM exceptions and Java crypto/time APIs.

## Integration Points
SCM exposes this manager through secret-key protocol APIs. `SecretKeyState.updateKeys()` is annotated for Ratis replication, so rotations propagate to all SCMs.

## Risks
No validation ensures validity duration exceeds rotation duration. `getCurrentSecretKey()` may return null before initialization. `KeyGenerator` is stored and used inside synchronized methods; algorithm misconfig fails construction.

## Test Signals
Tests should cover first initialization, reload with expired filtering, forced and time-based rotation, no-op rotation, state persistence calls, reinitialization from leader snapshots, and invalid algorithm handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeySignerClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeySignerClient.java

## Purpose
`SecretKeySignerClient` defines the signer-side API for components that need the current symmetric secret key to sign tokens or data.

## Important APIs, Types, And Functions
`getCurrentSecretKey()` is the required method. Default lifecycle hooks `start(ConfigurationSource)`, `stop()`, and `refetchSecretKey()` are no-ops for simple implementations.

## Control Flow
There is no interface control flow. Implementations such as `DefaultSecretKeySignerClient` use `start()` to prefetch and schedule refreshes.

## State, Persistence, And Dependencies
The interface has no state. It depends on `ConfigurationSource` and may throw `IOException` during startup.

## Integration Points
`ContainerTokenSecretManager` and other token signers use this API to access signing keys. `SecretKeyClient` extends it.

## Risks
Default no-op lifecycle methods mean callers cannot assume every implementation prefetches or refreshes keys unless documented.

## Test Signals
Implementation tests should verify initialization requirements, current key availability, refresh behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeySignerClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyState.java

## Purpose
`SecretKeyState` defines the replicated state holder contract for SCM-managed symmetric keys.

## Important APIs, Types, And Functions
It extends `SCMHandler`, exposes `getCurrentKey()`, `getKey(UUID)`, `getSortedKeys()`, replicated `updateKeys(List<ManagedSecretKey>)`, and `reinitialize(List<ManagedSecretKey>)`. `getType()` returns `SCMRatisProtocol.RequestType.SECRET_KEY`.

## Control Flow
The interface itself has no implementation. The `@Replicate` annotation on `updateKeys()` instructs SCM HA machinery to replicate key updates.

## State, Persistence, And Dependencies
State is implementation-defined. Dependencies include managed keys, SCM HA handler/replication annotations, and SCM exceptions.

## Integration Points
`SecretKeyManager` updates this state during initialization and rotation. SCM Ratis dispatch uses `getType()` to route replicated secret-key requests.

## Risks
Implementations must keep current, sorted, and id-indexed views consistent and durable. Replication failures surface as `SCMException`.

## Test Signals
Tests should verify replication annotation handling, request type, current key semantics, key lookup, sorted order, and snapshot reinitialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStateImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStateImpl.java

## Purpose
`SecretKeyStateImpl` is the default in-memory and persisted implementation of `SecretKeyState`.

## Important APIs, Types, And Functions
It uses a `ReadWriteLock` to guard `sortedKeys`, `currentKey`, and `keyById`. `getCurrentKey()`, `getKey(UUID)`, and `getSortedKeys()` acquire the read lock. `updateKeys()` and `reinitialize()` call `updateKeysInternal()`, which sorts keys newest-first, sets the current key, builds the UUID map, and saves to `SecretKeyStore`.

## Control Flow
Updates acquire the write lock, replace all derived views atomically, persist the sorted list, then release. Reads return current field references under the read lock. `getKey()` returns null if the state has not been initialized.

## State, Persistence, And Dependencies
State is in-memory key views plus the backing `SecretKeyStore`. Persistence happens on every update/reinitialize via `keyStore.save(sortedKeys)`. Dependencies include locks, stream collectors, and logging.

## Integration Points
`SecretKeyManager` owns lifecycle decisions but delegates actual state updates and persistence here. In production, this object is expected to be behind SCM replication proxying for annotated updates.

## Risks
`getSortedKeys()` can return null before initialization. `updateKeysInternal()` assumes `newKeys` is non-empty; otherwise `sortedKeys.get(0)` fails. Returned `sortedKeys` is immutable but key objects contain key material.

## Test Signals
Tests should verify initial null behavior, update ordering, current key selection, UUID lookup, persistence calls, reinitialize behavior, empty-list failure, and concurrent read/write safety.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStateImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStore.java

## Purpose
`SecretKeyStore` abstracts persistence for managed symmetric secret keys.

## Important APIs, Types, And Functions
It declares `load()` to return persisted managed keys and `save(Collection<ManagedSecretKey>)` to persist a key collection.

## Control Flow
There is no implementation control flow. `LocalSecretKeyStore` provides the local JSON-backed implementation.

## State, Persistence, And Dependencies
The interface has no state. Implementations define persistence medium and durability behavior.

## Integration Points
`SecretKeyManager` loads from a store during initialization. `SecretKeyStateImpl` saves to a store after key updates and reinitialization.

## Risks
The contract does not specify atomicity, ordering, encryption, or whether expired keys should be returned; callers perform filtering/sorting as needed.

## Test Signals
Implementation tests should verify round-trip persistence, failure handling, empty store behavior, and durability guarantees.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyVerifierClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyVerifierClient.java

## Purpose
`SecretKeyVerifierClient` defines the verifier-side API for resolving the symmetric key identified by a token.

## Important APIs, Types, And Functions
`getSecretKey(UUID)` returns a nullable `ManagedSecretKey` and may throw `SCMSecurityException`.

## Control Flow
There is no implementation flow in this interface.

## State, Persistence, And Dependencies
The interface has no state. Dependencies are UUIDs, nullable annotation, managed keys, and SCM security exceptions.

## Integration Points
Short-lived token verifiers call this API using the secret-key id embedded in token identifiers. `DefaultSecretKeyVerifierClient` implements remote cached lookup; `SecretKeyManager` implements local SCM lookup.

## Risks
Callers must handle null results as missing/unknown keys and distinguish them from thrown security/IO failures.

## Test Signals
Implementation tests should cover successful key resolution, missing key null returns, and exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyVerifierClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/package-info.java

## Purpose
This package JavaDoc explains Ozone's symmetric secret-key subsystem for signing and verifying tokens such as block and container tokens.

## Important APIs, Types, And Functions
It points readers to `ManagedSecretKey`, `SecretKeyState`, `SecretKeyStore`, `LocalSecretKeyStore`, and `SecretKeyManager`, and references the HDDS-7733 design.

## Control Flow
There is no executable flow, but the documentation describes the conceptual flow: SCM generates/manages/distributes keys; signers and verifiers use the same key material.

## State, Persistence, And Dependencies
The file has no runtime state. It documents replicated key state and persistent key storage as package concepts.

## Integration Points
The package ties together SCM key lifecycle, OM/SCM token signing, and datanode token verification.

## Risks
The JavaDoc uses HTML tags and an external design link; drift can occur if the implementation evolves beyond the described component set.

## Test Signals
No runtime tests apply, but documentation should stay consistent with package APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenException.java

## Purpose
`BlockTokenException` is the block-token-specific exception type in the SCM security layer.

## Important APIs, Types, And Functions
It extends `SCMSecurityException` and provides constructors for message-only, message-plus-cause, and cause-only cases.

## Control Flow
There is no custom flow; constructors delegate to the superclass.

## State, Persistence, And Dependencies
No state beyond inherited exception fields. No persistence. Dependency is `SCMSecurityException`.

## Integration Points
`BlockTokenVerifier` throws this exception when a token lacks required permission for a datanode block command.

## Risks
The exception carries no specialized error code in these constructors, so callers rely on type/message unless the superclass supplies defaults.

## Test Signals
Tests should verify constructor message/cause propagation and handling by token verification call paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenVerifier.java

## Purpose
`BlockTokenVerifier` verifies short-lived block tokens for datanode container commands, including service matching and access-mode authorization.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenVerifier<OzoneBlockTokenIdentifier>`. Static `getTokenService()` converts `BlockID` or `ContainerBlockID` to the token service string. Overrides include `isTokenRequired()`, `createTokenIdentifier()`, `getService()`, and `verify()`.

## Control Flow
Token requirement is true only when block tokens are enabled and `HddsUtils.requireBlockToken(cmdType)` says the command requires one. `getService()` extracts the block id from the command and requires it to be non-null. `verify()` maps read-only commands to `READ`, delete block/chunk to `DELETE`, and all others to `WRITE`, then checks the token identifier contains that access mode.

## State, Persistence, And Dependencies
State is inherited from the short-lived verifier: security config and secret-key verifier client. No persistence. Dependencies include datanode command protobufs, block IDs, HDDS token utility methods, access-mode protobufs, and symmetric key verification.

## Integration Points
Datanode command handling uses this verifier to authenticate block operations. It composes with other verifiers through `CompositeTokenVerifier`.

## Risks
Access-mode classification depends on `HddsUtils.isReadOnly()` and explicit delete command checks; new command types must be classified correctly. Missing block IDs trigger `NullPointerException` via `Objects.requireNonNull`.

## Test Signals
Tests should cover token-required command matrix, READ/WRITE/DELETE permission checks, service string matching, missing block id behavior, disabled block-token mode, and invalid signature/expired token paths inherited from the base verifier.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/CompositeTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/CompositeTokenVerifier.java

## Purpose
`CompositeTokenVerifier` runs multiple `TokenVerifier` delegates for a single datanode command.

## Important APIs, Types, And Functions
The constructor copies a provided delegate list into an internal `LinkedList`. `verify(Token<?>, ContainerCommandRequestProtoOrBuilder)` iterates over delegates and calls each verifier.

## Control Flow
Verification is sequential. The first delegate throwing `SCMSecurityException` aborts the chain; otherwise all verifiers must pass.

## State, Persistence, And Dependencies
State is the delegate list. There is no persistence. Dependencies are Hadoop tokens, datanode command protobufs, and SCM security exceptions.

## Integration Points
Container command handling can combine block token, container token, and other token verifiers without embedding knowledge of each verifier type.

## Risks
Delegate ordering matters for error surface and cost. The list is mutable internally but not exposed. Passing null delegates or null list is not guarded.

## Test Signals
Tests should verify all delegates are invoked on success, iteration stops on first failure, ordering, empty delegate behavior, and null input handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/CompositeTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenGenerator.java

## Purpose
`ContainerTokenGenerator` defines how SCM/container code creates tokens authorizing operations on a container.

## Important APIs, Types, And Functions
`generateEncodedToken(ContainerID)` creates a URL-encoded token for the current user. `generateToken(String, ContainerID)` creates a Hadoop token for an explicit user. The `DISABLED` implementation returns an empty encoded string and an empty `Token`.

## Control Flow
The interface has no implementation flow except the disabled singleton's no-op behavior.

## State, Persistence, And Dependencies
No state in the interface; disabled singleton is stateless. Dependencies are `ContainerID` and Hadoop `Token`.

## Integration Points
`ContainerTokenSecretManager` implements this interface for enabled token generation. `StorageContainerLocationProtocol.getContainerToken()` exposes token acquisition over SCM RPC.

## Risks
Callers must handle disabled mode's empty token values. `generateEncodedToken()` may throw unchecked IO wrappers by contract.

## Test Signals
Tests should verify disabled behavior, enabled token generation via `ContainerTokenSecretManager`, URL encoding, and current-user lookup failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenIdentifier.java

## Purpose
`ContainerTokenIdentifier` is the short-lived token identifier for container-scoped operations.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenIdentifier`, defines kind `HDDS_CONTAINER_TOKEN`, stores a `ContainerID`, and provides constructors with owner/container/expiry and optional secret-key UUID. Serialization uses `ContainerTokenSecretProto` in `getBytes()`, `write()`, `readFields()`, and `readFromByteArray()`. `getService()` returns the container id string.

## Control Flow
Serialization writes the protobuf bytes containing owner, secret-key id, expiry millis, and container id. Deserialization parses the protobuf and restores those fields. Equality delegates to the superclass and compares `containerID` with `==`.

## State, Persistence, And Dependencies
State is inherited owner/expiry/secret key id plus container id. Persistence is token byte serialization. Dependencies include protobuf container-token secret messages, Ozone protobuf UUID utilities, Hadoop `Text`, and `ContainerID`.

## Integration Points
`ContainerTokenSecretManager` creates these identifiers. Short-lived token verifiers read them to validate container token service, expiry, and signature.

## Risks
`equals()` uses reference equality for `ContainerID`, which may be wrong if equal IDs are distinct objects. `hashCode()` includes expiry but not container id directly, which may be inconsistent with equality intent. `readFields()` requires `DataInputStream` with mark support and casts `DataInput`.

## Test Signals
Tests should cover protobuf round trip, token kind/service, equality/hash behavior for equivalent container IDs, readFields input assumptions, and secret-key id preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenSecretManager.java

## Purpose
`ContainerTokenSecretManager` creates and signs short-lived container tokens using the current symmetric secret key.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenSecretManager<ContainerTokenIdentifier>` and implements `ContainerTokenGenerator`. The constructor takes token lifetime and `SecretKeySignerClient`. `createIdentifier()` builds a `ContainerTokenIdentifier`. `generateEncodedToken()` uses the current Hadoop user and URL-encodes the generated token. `generateToken(String, ContainerID)` signs an identifier through the base class.

## Control Flow
Token generation derives expiry via `getTokenExpiryTime()`, creates an identifier, then delegates signing to the inherited `generateToken(identifier)`. Current-user lookup and token encoding IO failures are wrapped in `UncheckedIOException`.

## State, Persistence, And Dependencies
State is inherited token lifetime and signer client. No direct persistence. Dependencies include Hadoop UGI, container IDs, Hadoop tokens, and symmetric signer clients.

## Integration Points
SCM uses this manager to issue container tokens through `StorageContainerLocationProtocol.getContainerToken()` and other token generator call sites. Datanodes verify resulting identifiers with symmetric key verifiers.

## Risks
Current-user resolution can fail in unusual security contexts. The generated identifier constructor does not set secret-key id directly; correctness depends on the base secret manager assigning it during signing.

## Test Signals
Tests should cover explicit-user and current-user generation, encoded token round trip, unchecked IO wrapping, expiry calculation, and signature verification with the current managed secret key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenSecretManager.java -->
