# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotStatus.java

## Purpose
`SnapshotStatus` is client-side metadata for an individual snapshot. It wraps the snapshot directory's `HdfsFileStatus`, the numeric snapshot ID, deletion state, and parent path bytes, and provides formatting for `dfs lsSnapshottableDir`-style output.

## Important APIs, Types, and Functions
Constructors either build a directory `HdfsFileStatus` from primitive metadata or accept a prebuilt `HdfsFileStatus`. `getSnapshotID`, `isDeleted`, `getDirStatus`, `getParentFullPath`, and `setParentFullPath` expose the fields. `getFullPath` builds a `Path` under `<parent>/.snapshot/<localName>`, using `/` for null or empty parent paths.

`print` computes column widths across an array of statuses and emits permission, replication, owner, group, length, modification time, snapshot ID, deletion status, and snapshot path. `getSnapshotPath` constructs `.snapshot` paths, inserting a separator if the snapshottable directory path lacks a trailing slash. `getParentPath` strips the `.snapshot` portion when present.

## Control Flow
The main behavior is path construction and formatted printing. `print` first scans all rows for maximum field widths, then formats each row with a `SimpleDateFormat` of `yyyy-MM-dd HH:mm`. Null or empty input arrays print a blank line.

## State and Persistence Behavior
`dirStatus`, `snapshotID`, and `isDeleted` are final. `parentFullPath` is mutable via `setParentFullPath` and is returned directly as a byte array. The class does not persist state itself; it is populated from NameNode RPC responses and consumed by CLI/admin code.

## Dependencies and Integration Points
It depends on `HdfsFileStatus.Builder`, `FsPermission`, `HdfsFileStatus.Flags`, `DFSUtilClient`, `Path`, and `HdfsConstants.DOT_SNAPSHOT_DIR`. It integrates with client protocol calls that list snapshots and with shell/admin output formatting.

## Risks and Edge Cases
`getParentPath` assumes `.snapshot` is preceded by a separator and returns `substring(0, index - 1)`; malformed paths where `.snapshot` starts at index 0 would be unsafe. `print` calls `DFSUtilClient.bytes2String(status.parentFullPath)` without the null/empty guard used in `getFullPath`, so callers should supply populated parent paths before printing. Mutable parent bytes can affect later path rendering.

## Test Signals
Snapshot shell command tests and snapshot listing tests provide integration coverage. Focused tests should verify root parent handling, deleted vs active printing, `getSnapshotPath` separator behavior, `getParentPath` for paths with and without `.snapshot`, and printing with null/empty arrays.
