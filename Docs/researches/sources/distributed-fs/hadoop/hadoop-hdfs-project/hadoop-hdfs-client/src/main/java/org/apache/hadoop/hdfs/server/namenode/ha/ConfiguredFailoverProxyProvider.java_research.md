# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ConfiguredFailoverProxyProvider.java

Purpose: `ConfiguredFailoverProxyProvider<T>` is the standard HA provider for logical HDFS URIs backed by multiple configured NameNode RPC addresses.

Important APIs/types/functions: constructors load proxies using `DFS_NAMENODE_RPC_ADDRESS_KEY` or a caller-specified address key. `getProxy()` returns the current lazily-created proxy. `performFailover()` advances to the next configured proxy through `incrementProxyIndex()`. `close()` closes every instantiated proxy using `Closeable` when possible or `RPC.stopProxy` otherwise. `useLogicalURI()` returns true.

Control flow: the provider keeps `currentProxyIndex`; normal calls use the current proxy until retry/failover policy invokes `performFailover`, then the index wraps modulo proxy count.

State and persistence behavior: stores a final list of `NNProxyInfo<T>` and mutable current index. Proxies are created on demand and retained until `close()`.

Dependencies and integration points: depends on `AbstractNNFailoverProxyProvider`, Hadoop RPC, and the NameNode address config key. It is the inner provider for observer reads and router configured failover.

Risks and test signals: ordering affects load distribution and failover behavior; resource cleanup must close all proxies created over provider lifetime. Tests should cover index wraparound, lazy creation, randomized address ordering via base class, custom address keys, and close behavior for `Closeable` versus RPC proxies.
