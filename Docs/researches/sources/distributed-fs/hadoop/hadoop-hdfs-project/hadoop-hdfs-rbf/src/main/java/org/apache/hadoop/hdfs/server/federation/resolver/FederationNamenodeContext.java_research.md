# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeContext.java

Purpose: `FederationNamenodeContext` abstracts a discovered Namenode registration and its routing metadata.

Important APIs: getters expose RPC, service RPC, lifeline, web scheme/address, nameservice ID, namenode ID, state, last modification time, namespace, block pool, cluster, and related identity/state fields used by resolver comparators and router clients.

Control flow and state: this is a data access interface; concrete State Store records such as `MembershipState` implement it. No persistence exists here, but implementations usually represent State Store membership rows.

Dependencies and integration points: consumed by `NamenodePriorityComparator`, `MembershipNamenodeResolver`, `RBFMetrics`, and router RPC selection paths.

Risks: comparator behavior and cache keys depend on stable getter values. Date modified is used as a tie breaker, so stale or skewed timestamps affect routing priority.

Test signals: contract tests should ensure `MembershipState` supplies all fields used by resolver ordering and metrics serialization.
