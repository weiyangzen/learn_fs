# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/package-info.java

Purpose: package descriptor for Router-Based Federation metrics.

Important APIs: applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.metrics`, documenting that the package reports Router-based Federation metrics.

Control flow and state: no executable logic, mutable state, or persistence.

Dependencies and integration points: classification annotations communicate API compatibility expectations to developers and downstream consumers.

Risks: only documentation/annotation drift. The package-level privacy/evolving status is the important contract.

Test signals: none at runtime; source checks may verify package annotations or generated docs.
