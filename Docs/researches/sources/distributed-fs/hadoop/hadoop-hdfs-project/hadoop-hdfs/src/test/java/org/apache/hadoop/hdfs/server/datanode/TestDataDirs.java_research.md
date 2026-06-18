# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataDirs.java

## Purpose
`TestDataDirs` validates parsing of `dfs.datanode.data.dir` storage locations, storage type filters based on filesystem, and capacity-ratio parsing for storage locations.

## Important APIs, Types, and Functions
- `DataNode.getStorageLocations(Configuration)` parses configured DataNode data directories.
- `StorageLocation.parseCapacityRatio` parses `[ratio]path` entries.
- Storage types under test include `DISK`, `SSD`, `RAM_DISK`, `NVDIMM`, and `ARCHIVE`.
- `DF` is used to discover the filesystem for `/home` in filesystem-filter tests.

## Control Flow and Behavior
`testDataDirParsing` checks a mixed string with storage type case variants, whitespace, an incomplete `[disk]` entry, and NVDIMM. It then verifies an unknown storage type throws `IllegalArgumentException`, and that entries without explicit type default to DISK. `testDataDirFileSystem` skips macOS, configures DISK and ARCHIVE paths, then filters ARCHIVE out when its configured filesystem does not match and includes it when the configured filesystem equals the actual one. `testCapacityRatioForDataDir` parses valid ratios and checks failures for missing ratios and out-of-range ratios.

## State and Persistence
The tests parse path strings and inspect local filesystem identity for one path. They do not create DataNode storage directories.

## Dependencies and Integration Points
The test integrates `DFS_DATANODE_DATA_DIR_KEY`, `StorageLocation`, `StorageType`, `Path`, local disk filesystem detection through `DF`, and platform checks through `Shell.MAC`.

## Risks and Edge Cases
Covered risks include case-insensitive storage types, whitespace between type and URI, incomplete URI segments, bad media types, default storage type selection, storage type filesystem filtering, malformed capacity ratio config, and ratios outside `[0, 1]`.

## Test Signals
Signals are parsed list sizes, exact storage types and URIs, expected exception messages, and filesystem-filtered location counts.
