# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/package-info.java

Purpose: package documentation for HDFS Mover.

Important APIs/types/functions: declares package `org.apache.hadoop.hdfs.server.mover`; explains mover as a tiered-storage migration tool that scans paths, checks block placement against storage policy, and moves replicas to satisfy policy.

Control flow: documentation matches `Mover.Processor`: scan paths, detect violations, schedule replica moves.

State and persistence behavior: none directly.

Dependencies and integration points: contextualizes `Mover` and `MoverMetrics` and their relationship to storage policies.

Risks: documentation does not cover EC-specific or pinned-block behavior present in implementation.

Test signals: not directly tested.
