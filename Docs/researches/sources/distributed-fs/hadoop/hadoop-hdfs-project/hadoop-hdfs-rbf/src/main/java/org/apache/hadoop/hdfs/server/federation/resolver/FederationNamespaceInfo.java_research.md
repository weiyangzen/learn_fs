# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamespaceInfo.java

Purpose: immutable value object for a federated namespace, carrying block pool ID, cluster ID, and nameservice ID while extending `RemoteLocationContext`.

Important APIs: constructor accepts block pool, cluster, and nameservice. `getNameserviceId`, `getDest`, and `getSrc` return the nameservice ID for routing-context compatibility. Additional getters expose cluster and block pool. `equals`, `hashCode`, and `compareTo` order by nameservice, then cluster, then block pool.

Control flow and state: no mutable state after construction. It is used in sets and maps for namespace fan-out and metrics aggregation.

Dependencies and integration points: returned by `ActiveNamenodeResolver.getNamespaces`, used by `RBFMetrics`, `ErasureCoding`, and router RPC clients invoking concurrent operations across namespaces.

Risks: equality includes all three IDs, so inconsistent State Store namespace metadata can create duplicate-looking nameservice entries. `getDest`/`getSrc` returning nameservice ID is convenient but can surprise code expecting a path.

Test signals: equality/hash/compare ordering, TreeSet behavior, and fan-out maps keyed by `FederationNamespaceInfo`.
