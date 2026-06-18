# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/IPFailoverProxyProvider.java

Purpose: `IPFailoverProxyProvider<T>` supports HA deployments where an external virtual IP or DNS name moves between NameNodes, so the client uses one RPC address and infrastructure performs failover.

Important APIs/types/functions: the constructor builds a single `NNProxyInfo` from `DFSUtilClient.getNNAddress(uri)`. `getProxy()` lazily creates and returns that single proxy. `performFailover()` is intentionally a no-op. `close()` closes the single proxy if created. `useLogicalURI()` returns false.

Control flow: retry policies handle connection resets after virtual-IP movement; this provider does not switch internal targets.

State and persistence behavior: keeps one `NNProxyInfo<T>` and its cached proxy. No logical-token cloning is performed by this provider because it does not use a logical URI.

Dependencies and integration points: integrates with HDFS URI address parsing, Hadoop RPC, and retry policies such as failover-on-network-exception.

Risks and test signals: using it with a non-resolvable URI or without proper external failover breaks availability. Tests should cover no-op failover, lazy single-proxy creation, close behavior, and `useLogicalURI=false` token handling.
