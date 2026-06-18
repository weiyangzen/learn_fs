# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ClientHAProxyFactory.java

Purpose: `ClientHAProxyFactory<T>` is the client-side `HAProxyFactory` implementation that creates NameNode `ClientProtocol` RPC proxies for HA providers.

Important APIs/types/functions: `setAlignmentContext(AlignmentContext)` stores optional client/server state-alignment context. The main `createProxy(...)` overload delegates to `NameNodeProxiesClient.createProxyWithAlignmentContext` when an alignment context is present, otherwise to `createNonHAProxyWithClientProtocol`. The legacy overload without `fallbackToSimpleAuth` delegates to the full overload with null fallback.

Control flow: HA providers call this factory during lazy proxy creation. The `withRetries` parameter is accepted by the interface but this implementation passes fixed `false` to `NameNodeProxiesClient` in both creation branches.

State and persistence behavior: only mutable state is the optional `alignmentContext`, set before proxy creation by observer-read providers.

Dependencies and integration points: integrates with `NameNodeProxiesClient`, `UserGroupInformation`, and Hadoop IPC alignment contexts used for observer reads and router observer reads.

Risks and test signals: incorrect alignment-context propagation can break observer-read consistency. Tests should verify proxy creation branch selection with and without an alignment context and that fallback-to-simple-auth is passed through.
