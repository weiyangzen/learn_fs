# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/package-info.java

Purpose: package metadata for the RBF fedbalance tool.

Important APIs and types: marks `org.apache.hadoop.hdfs.rbfbalance` as `@InterfaceAudience.Public` and documents FedBalance as a tool for balancing data across federation clusters.

Control flow: no executable logic.

State and persistence: no state.

Dependencies and integration points: applies to `RouterFedBalance`, `RouterDistCpProcedure`, and `MountTableProcedure`, indicating this package is intended for public tool-facing use.

Risks: public audience annotation makes API churn more visible. Test signal is package compilation and documentation generation.
