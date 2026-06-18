# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/WrappedFailoverProxyProvider.java

Purpose: `WrappedFailoverProxyProvider<T>` adapts older implementations of Hadoop `FailoverProxyProvider<T>` into the HDFS `AbstractNNFailoverProxyProvider<T>` hierarchy.

Important APIs/types/functions: delegates `getInterface()`, `getProxy()`, `performFailover()`, and `close()` to the wrapped provider. `useLogicalURI()` returns true by assumption for old implementations.

Control flow: it contains no proxy creation logic of its own; all behavior is delegated.

State and persistence behavior: stores only the wrapped provider reference.

Dependencies and integration points: integrates legacy HA providers with code that expects `AbstractNNFailoverProxyProvider`, especially token-handling checks around logical URIs.

Risks and test signals: the logical-URI assumption can be wrong for unusual legacy providers. Tests should cover delegation and close propagation, and any use site should verify token behavior with wrapped providers.
