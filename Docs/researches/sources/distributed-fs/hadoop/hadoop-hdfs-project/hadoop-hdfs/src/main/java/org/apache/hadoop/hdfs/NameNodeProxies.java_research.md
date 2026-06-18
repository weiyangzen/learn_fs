# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/NameNodeProxies.java

Purpose: Creates RPC proxy objects for communicating with NameNodes and related NameNode-hosted protocols, selecting HA failover proxies for logical URIs and direct non-HA proxies for concrete NameNode addresses.

Important APIs and functions: `createProxy()` builds an HA or non-HA `ProxyAndInfo<T>`. `createNonHAProxy()` creates direct proxies for `ClientProtocol`, `JournalProtocol`, `NamenodeProtocol`, `GetUserMappingsProtocol`, `RefreshUserMappingsProtocol`, `RefreshAuthorizationPolicyProtocol`, `RefreshCallQueueProtocol`, `InMemoryAliasMapProtocol`, and combined `BalancerProtocols`. Protocol-specific helpers instantiate protobuf PB proxies and client-side translators. `createNameNodeProxy()` sets `ProtobufRpcEngine2` and calls `RPC.getProtocolProxy`.

Control flow: `createProxy()` asks `NameNodeProxiesClient.createFailoverProxyProvider()` whether the URI is logical/HA. Without a provider it resolves the concrete NN address and creates a direct proxy with the current user; with a provider it delegates HA proxy construction. Direct proxy creation builds a delegation-token service from the NN address, dispatches on the requested protocol class, optionally wraps `NamenodeProtocol` in retry policies for `getBlocks` and `getAccessKeys`, and combines client and namenode protocols for balancer use.

State and persistence behavior: This class is stateless. Created proxies hold network connections, retry policy wrappers, token-service metadata, and optional alignment context supplied by the caller. `Configuration` is modified transiently by setting protocol engines for PB interfaces.

Dependencies and integration points: Depends on `NameNodeProxiesClient`, `NameNodeHAProxyFactory`, HA failover provider classes, Hadoop RPC, `ProtobufRpcEngine2`, protocol PB interfaces/translators, security/UGI, `SecurityUtil`, `RetryProxy`, `RetryPolicies`, `ProxyCombiner`, and `AlignmentContext`. It is central to DFSClient, balancer, journal, alias map, and admin command RPC setup.

Risks: Unsupported protocol classes throw `IllegalStateException`; adding a new NameNode protocol requires updating this dispatch table. Incorrect retry wrapping can change admin/client behavior. Fallback-to-simple-auth and alignment context must be passed only where supported. Direct proxies bypass HA failover, so callers must choose the creation path correctly.

Test signals: Tests should create proxies for each supported protocol, verify HA logical URI selection, non-HA token service construction, retry wrappers for namenode protocol methods, balancer protocol combination, fallback-to-simple-auth propagation, alignment context propagation, unsupported protocol failure, and correct PB engine selection.
