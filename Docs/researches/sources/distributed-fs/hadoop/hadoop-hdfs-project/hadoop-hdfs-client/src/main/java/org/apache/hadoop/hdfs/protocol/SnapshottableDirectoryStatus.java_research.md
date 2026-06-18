# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshottableDirectoryStatus.java

## Purpose
`SnapshottableDirectoryStatus` is metadata for a directory on which snapshots are enabled. It reports ordinary directory status plus snapshot count/quota and parent path, and provides CLI-friendly formatting and a JMX/JSON-friendly nested bean.

## Important APIs, Types, and Functions
`COMPARATOR` sorts statuses by parent path bytes, then local name bytes, using `DFSUtilClient.compareBytes`. Constructors either build an `HdfsFileStatus` from primitive fields or accept a prebuilt one. Getters expose snapshot count, quota, parent path, and directory status.

`getFullPath` handles the root directory specially: null/empty parent plus empty local name becomes `/`; otherwise it builds either `new Path(localName)` or `new Path(parent, localName)`. `print` formats rows with directory permission, replication, owner, group, length, modification time, snapshot number, snapshot quota, and full path. The nested `Bean` exposes path, snapshot number/quota, modification time, short permission, owner, and group.

## Control Flow
The class is mostly declarative. `print` does a width pre-scan, builds a format string, and prints each status. `COMPARATOR` is used by callers that need deterministic output ordering.

## State and Persistence Behavior
Fields are final and there is no local persistence. As with other HDFS protocol DTOs, byte-array parent paths are returned directly and not defensively copied. It is serialized through RPC/PB conversion elsewhere.

## Dependencies and Integration Points
It depends on `HdfsFileStatus`, `FsPermission`, `DFSUtilClient`, and Hadoop `Path`. It is returned by NameNode/client protocol methods for listing snapshottable directories and consumed by DFS shell/admin display and metrics/JMX-style bean conversion.

## Risks and Edge Cases
Root handling is explicit and should not be regressed. The comparator assumes non-null parent path arrays. Direct byte-array exposure allows mutation by consumers. Formatting depends on `HdfsFileStatus` values being non-null enough for width calculation.

## Test Signals
Snapshot command tests and snapshottable-directory listing tests are the primary integration signals. Unit tests should cover comparator ordering, root path construction, null/empty parent path behavior, quota/count formatting, and bean field projection.
