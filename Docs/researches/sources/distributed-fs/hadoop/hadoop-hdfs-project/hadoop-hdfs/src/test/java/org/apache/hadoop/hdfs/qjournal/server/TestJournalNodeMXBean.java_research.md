# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeMXBean.java

Purpose: Tests JMX/MXBean exposure of JournalNode status, host identity, version, cluster IDs, start time, and storage information.

Important APIs/types/functions: `JournalNodeMXBean`, platform `MBeanServer`, ObjectName `Hadoop:service=JournalNode,name=JournalNodeInfo`, `getJournalsStatus`, `getHostAndPort`, `getClusterIds`, `getStorageInfos`, and Jetty JSON.

Control flow: Starts a one-node MiniJournalCluster, reads MXBean attributes before formatting, formats journal `ns1`, compares JSON status to `jn.getJournalsStatus()`, verifies host/port, cluster IDs, start time, version, and storage info, then restarts without formatting and checks persisted status remains visible.

State and persistence behavior: Formatted storage contains namespace ID, cluster ID, and creation time. Restart-without-format proves status survives daemon restart.

Dependencies and integration points: JournalNode JMX registration, JSON status generation, and MiniJournalCluster storage lifecycle.

Risks: Wrong MXBean data breaks monitoring and operational diagnosis.

Test signals: Passing validates MXBean parity with JournalNode methods and persistent storage reporting.
