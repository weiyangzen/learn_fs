<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java

## Purpose

`VolumeFailureSummary` summarizes failed DataNode storage locations, the last failure time, and estimated lost capacity.

## Important APIs and types

Fields are `String[] failedStorageLocations`, `lastVolumeFailureDate` in epoch milliseconds, and `estimatedCapacityLostTotal` in bytes. Getters expose all three.

## Control flow

DataNodes include this summary in heartbeats and lifelines. The NameNode uses it for DataNode health, admin reporting, and capacity accounting.

## State and persistence behavior

The value is transient but reports persistent/local volume failure state. The failed-location array is not defensively copied.

## Dependencies and integration points

It integrates with `DatanodeProtocol.sendHeartbeat`, `DatanodeLifelineProtocol.sendLifeline`, DataNode volume checkers, and NameNode health reporting.

## Risks and test signals

Risks include mutable array exposure, unsorted or duplicate locations despite the getter comment, negative/unknown capacity estimates, and clock skew in failure dates. Tests should cover empty/no-failure summaries, multiple failed volumes, lost-capacity aggregation, and heartbeat/lifeline serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java -->
