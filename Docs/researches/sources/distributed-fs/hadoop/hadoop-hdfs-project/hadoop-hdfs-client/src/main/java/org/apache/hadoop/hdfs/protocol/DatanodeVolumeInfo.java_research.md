# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeVolumeInfo.java

## Purpose
`DatanodeVolumeInfo` describes locally available storage-volume metrics for a DataNode volume: path, used/free/reserved space, reserved space for replicas, block count, and storage type.

## APIs and Behavior
The constructor initializes mutable private fields, and getters expose all metrics. `getDatanodeVolumeReport()` formats a multi-line report using `StringUtils.byteDesc` for byte values.

## State, Dependencies, and Integration
The class depends on `StorageType` and Hadoop `StringUtils`. It is a reporting DTO; persistence and metric collection occur in DataNode storage components outside this class.

## Risks and Test Signals
The class does not validate negative space values, null paths, or null storage type. Tests should cover report formatting, byte description values, storage type propagation, and edge cases such as zero-capacity or reserved-space-heavy volumes.
