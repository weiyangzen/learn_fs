# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsConstants.java

## Purpose
`HdfsConstants` centralizes HDFS protocol constants and enums used across clients, NameNode RPCs, storage policies, leases, snapshots, safe mode, rolling upgrade, datanode reports, and re-encryption.

## APIs and Behavior
Constants include quota sentinel values, URI scheme, storage-policy IDs/names, snapshot/reserved path components, grandfather generation/inode IDs, delegation-token HA prefix, protocol names, read/write timeouts, and lease soft limit. Enums include `StoragePolicy` with ID mapping, `SafeModeAction`, `StoragePolicySatisfierMode` with case-insensitive map lookup, `RollingUpgradeAction` with empty-string query mapping, `UpgradeAction`, `DatanodeReportType`, and `ReencryptAction`.

## State, Dependencies, and Integration
The class is final-ish through a protected hidden constructor and has static state for enum lookup maps. It depends on `Path`, client config keys, and `StringUtils`. Nearly every HDFS client protocol layer uses these constants for wire values and user-visible behavior.

## Risks and Test Signals
Storage-policy numeric IDs and quota sentinel values are compatibility-sensitive. Tests should cover enum string parsing, invalid storage-policy IDs returning null, snapshot path constants, HA token prefix use, timeout expectations, and safe-mode/rolling-upgrade action mapping from CLI input.
