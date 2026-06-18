<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/AvailableSpaceVolumeChoosingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/AvailableSpaceVolumeChoosingPolicy.java

## Purpose

`AvailableSpaceVolumeChoosingPolicy` chooses a DataNode volume for a new replica while considering free-space imbalance. It prefers high-available-space volumes when volumes diverge beyond a configured threshold, while falling back to round-robin when balanced.

## Important APIs, Types, And Functions

- Implements `VolumeChoosingPolicy<V>` and `Configurable`.
- `setConf` reads balanced-space threshold and preference fraction.
- `chooseVolume(List<V>, long replicaSize, String storageId)` synchronizes per storage type and delegates to `doChooseVolume`.
- `doChooseVolume` builds an `AvailableSpaceVolumeList`, checks balance, and chooses among balanced, high-available, or low-available volume sets.
- Inner `AvailableSpaceVolumePair` snapshots each volume's available space once per choice.

## Control Flow

If no volumes exist, it throws `DiskOutOfSpaceException`. Otherwise it locks only the storage-type-specific lock. Balanced sets use pure round-robin. Imbalanced sets split volumes into low and high groups relative to least available plus threshold. If low volumes cannot fit the replica or a scaled random preference favors high volumes, it chooses high; otherwise low.

## State And Persistence

State includes per-storage-type locks, a `Random`, configured threshold and preference percent, and three round-robin policy instances. The policy persists nothing and only reads volume available-space snapshots.

## Dependencies And Integration Points

It is used by FsDataset volume allocation. It depends on `FsVolumeSpi.getAvailable`, `StorageType`, HDFS volume-choosing config keys, `RoundRobinVolumeChoosingPolicy`, and `DiskOutOfSpaceException`.

## Risks And Edge Cases

Preference values outside the intended range only log warnings, so extreme configs can invert or skew allocation. The scaled probability compensates for different group sizes. Available space is sampled once, so concurrent writes may change reality before allocation. Separate locks allow concurrency across storage types but serialize choices within one type.

## Test Signals

Tests should cover balanced fallback, imbalanced high preference, low-volume selection probability, low volumes lacking replica space, per-storage-type locking, invalid/no volume behavior, warning configs, and deterministic random injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/AvailableSpaceVolumeChoosingPolicy.java -->
