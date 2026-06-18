# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/NameNodeProxiesClient.java

`NameNodeProxiesClient` creates NameNode RPC proxies for HDFS clients, hiding the split between direct non-HA NameNode addresses and logical HA nameservices with failover providers.

`ProxyAndInfo` bundles a proxy, delegation-token service, and address. Factory methods include `createProxyWithClientProtocol()`, `createProxyWithLossyRetryHandler()`, `createFailoverProxyProvider()`, `getFailoverProxyProviderClass()`, `createHAProxy()`, `createNonHAProxyWithClientProtocol()`, and `createProxyWithAlignmentContext()`.

`createProxyWithClientProtocol()` tries to create a failover provider; without one it builds a physical address token service and a non-HA protobuf translator, with optional retry wrapping. With HA it creates a `RetryProxy` using failover-on-network-exception policy and logical or physical token service based on provider behavior. Provider creation uses reflection, wraps legacy providers, rejects logical URIs with non-default ports, and propagates fallback-to-simple-auth state. Non-HA protobuf creation sets `ProtobufRpcEngine2`, selects default retry policy, optionally installs `ClientGSIContext` for router observer reads, and returns a `ClientNamenodeProtocolTranslatorPB`.

The class is stateless; connection and failover state live in RPC proxies and providers. Dependencies include HA failover providers, `ClientHAProxyFactory`, `RetryProxy`, `RetryPolicies`, `RPC`, `ProtobufRpcEngine2`, NameNode protobuf translator classes, `SecurityUtil`, `HAUtilClient`, `UserGroupInformation`, and optional alignment contexts.

Risks include reflection failure wrapping, port validation for logical URIs, lossy retry being HA-only and returning null otherwise, default retry policy controlling all non-HA methods, and observer-read context only being created when none is supplied. Test signals include HA/non-HA proxy creation, legacy provider wrapping, class-not-found handling, logical URI port rejection, fallback auth propagation, lossy retry creation, token service shape, and alignment context selection.
