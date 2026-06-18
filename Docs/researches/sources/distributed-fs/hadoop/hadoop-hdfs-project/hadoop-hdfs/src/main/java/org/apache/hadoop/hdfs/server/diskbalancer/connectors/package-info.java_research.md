# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/package-info.java

Purpose: package-level documentation for diskbalancer cluster data source connectors.

Important APIs/types/functions: declares package `org.apache.hadoop.hdfs.server.diskbalancer.connectors`; describes `DBNameNodeConnector`, `JsonNodeConnector`, and a test-oriented `NullConnector`.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: frames the connector package as the source-normalization layer feeding `DiskBalancerCluster`.

Risks: mentions a `NullConnector` not in this specific source subset, so readers should look in tests or neighboring source for that implementation.

Test signals: aligns with test connector usage in diskbalancer tests.
