# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/package-info.java

Purpose: top-level package documentation for diskbalancer.

Important APIs/types/functions: no executable code. It explains diskbalancer as a DataNode-local volume balancing feature that computes average data distribution per storage type and moves data from above-average to below-average volumes on live DataNodes.

Control flow: describes the conceptual three-step algorithm: calculate ideal per-volume usage, move from high-load to low-load volumes, and operate against live DataNodes.

State and persistence behavior: none directly; contextualizes generated plan files and DataNode execution state.

Dependencies and integration points: frames the command, connector, data model, planner, and DataNode executor packages.

Risks: docs can lag implementation details such as skip flags, thresholds, and storage-policy interactions.

Test signals: not directly tested.
