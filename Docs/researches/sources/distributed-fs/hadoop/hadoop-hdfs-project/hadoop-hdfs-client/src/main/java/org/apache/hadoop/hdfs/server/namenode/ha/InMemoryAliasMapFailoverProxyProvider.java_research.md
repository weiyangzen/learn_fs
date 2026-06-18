# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/InMemoryAliasMapFailoverProxyProvider.java

Purpose: `InMemoryAliasMapFailoverProxyProvider<T>` is a specialized configured failover provider for HDFS provided-storage in-memory alias map RPC endpoints.

Important APIs/types/functions: its constructor delegates to `ConfiguredFailoverProxyProvider` with `DFS_PROVIDED_ALIASMAP_INMEMORY_RPC_ADDRESS` instead of the standard NameNode RPC address key.

Control flow: all failover behavior is inherited: lazy proxy creation, index advancement on failover, and close of instantiated proxies.

State and persistence behavior: inherits proxy list/index state from `ConfiguredFailoverProxyProvider`; no extra fields.

Dependencies and integration points: integrates with alias-map client configuration for provided storage and the generic HA provider framework.

Risks and test signals: misusing the standard NameNode key would connect to the wrong service. Tests should verify it reads alias-map addresses and inherits logical URI/token behavior.
