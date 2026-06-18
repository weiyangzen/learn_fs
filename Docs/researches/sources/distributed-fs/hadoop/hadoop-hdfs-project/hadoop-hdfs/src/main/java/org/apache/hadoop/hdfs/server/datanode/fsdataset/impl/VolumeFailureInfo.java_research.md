# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/VolumeFailureInfo.java

## Purpose

`VolumeFailureInfo` is an immutable value object describing a failed DataNode storage volume. It records the failed `StorageLocation`, failure timestamp, and estimated lost capacity.

## Important APIs, Control Flow, and State

The constructors allow callers to omit capacity, in which case lost capacity defaults to zero for failures discovered before capacity can be queried. Getters expose `getFailedStorageLocation`, `getFailureDate`, and `getEstimatedCapacityLost`.

There is no control flow beyond construction and getters, and no persistence in this class. Instances are held by dataset/volume-list code and surfaced through metrics/JMX such as failed storage locations, last failure time, and capacity lost.

## Dependencies, Integration, Risks, and Tests

The only non-JDK dependency is `StorageLocation`. Integration points are failure tracking in `FsVolumeList`/dataset metrics and `FSDatasetMBean`.

Risks are low, but callers must use consistent epoch-millisecond timestamps and understand that zero capacity can mean unknown rather than no loss. Tests should cover both constructors and metric aggregation consumers.
