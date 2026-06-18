<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/StorageLocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/StorageLocation.java

## Purpose

`StorageLocation` encapsulates a DataNode storage URI plus `StorageType`. It parses configured data directories, normalizes file URIs, compares locations, creates block-pool directories, and performs startup health checks.

## Important APIs, Types, And Functions

- `parse(String)` accepts optional `[type]uri` prefixes and defaults to `StorageType.DEFAULT`.
- `parseCapacityRatio(String)` parses same-disk-tiering ratios in `[ratio]uri` format and validates 0..1 bounds.
- `normalizeFileURI(URI)` canonicalizes file-style URIs and removes trailing slash.
- `matchesStorageDirectory` compares against `StorageDirectory`, with special handling for `PROVIDED` storage.
- `makeBlockPoolDir` creates/checks local block-pool directories unless storage is provided.
- Implements `Checkable<CheckContext, VolumeCheckResult>` by running `DiskChecker.checkDir` for local storage.

## Control Flow

Parsing strips storage type prefixes, converts paths through `Path.toUri`, and normalizes file paths. Directory creation obtains the local filesystem and configured permissions, then checks/creates the block-pool current directory. Health checks skip provided storage and check local directory permissions for all other types.

## State And Persistence

The object is immutable with final `storageType` and `baseURI`. Persistent effects occur in `makeBlockPoolDir` and `check`, which can create or validate local filesystem directories. Provided storage locations are treated as always healthy and do not create local block-pool directories.

## Dependencies And Integration Points

It is consumed by DataNode startup, storage directory matching, `StorageLocationChecker`, and block-pool initialization. It depends on `StorageType`, HDFS configuration keys, `StorageDirectory`, `DiskChecker`, `LocalFileSystem`, and `FsPermission`.

## Risks And Edge Cases

`compareTo` compares normalized URI before storage type, so locations with the same URI but different storage type can compare equal. Capacity-ratio parsing removes whitespace and can throw number-format or format errors. `getBpURI` returns null for unsupported URI-to-file conversion.

## Test Signals

Tests should cover path normalization, typed and untyped parsing, provided-storage matching, local block-pool directory creation permissions, health checks, capacity-ratio parsing and invalid ratios, equality/compare behavior, and URI edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/StorageLocation.java -->
