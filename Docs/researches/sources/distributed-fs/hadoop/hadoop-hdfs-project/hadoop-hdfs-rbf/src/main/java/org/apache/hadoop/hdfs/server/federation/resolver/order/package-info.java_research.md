# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/package-info.java

Purpose: package descriptor for destination-order resolvers.

Important APIs: applies private/evolving annotations to `org.apache.hadoop.hdfs.server.federation.resolver.order` and documents that the package decides which destination should be used first when federated locations resolve to multiple subclusters.

Control flow and state: no executable logic.

Dependencies and integration points: documents the relationship between multi-destination `PathLocation`s and ordering policy implementations.

Risks: annotation/documentation drift only.

Test signals: none at runtime.
