# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAProxyFactory.java

Purpose: `HAProxyFactory<T>` decouples HA failover providers from the concrete RPC proxy creation mechanism, allowing client-side `ClientProtocol` and server-side protocol factories to share the same provider logic.

Important APIs/types/functions: two `createProxy` overloads create proxies with or without an `AtomicBoolean fallbackToSimpleAuth`. The default `setAlignmentContext(AlignmentContext)` is a no-op for factories that do not support observer-read alignment.

Control flow: `AbstractNNFailoverProxyProvider.createProxyIfNeeded()` calls the full overload when a proxy is first needed. Observer-read providers call `setAlignmentContext()` before proxies are created.

State and persistence behavior: interface only; implementations choose whether to store state such as alignment context.

Dependencies and integration points: links `Configuration`, `InetSocketAddress`, `UserGroupInformation`, `AlignmentContext`, and HA providers. It is central to constructing NameNode RPC client stubs.

Risks and test signals: implementations must honor security fallback and alignment parameters consistently. Tests should cover factory use through providers rather than only direct mocks.
