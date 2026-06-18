# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReport.java

## Purpose
`SnapshotDiffReport` is the client-visible value object returned for an HDFS snapshot diff between two snapshots or between a snapshot and the live directory. It deliberately exposes a compact report of changed relative paths and change types rather than the full NameNode-side inode diff graph. It also carries `DiffStats` counters for snapshot diff processing metrics.

## Important APIs, Types, and Functions
The `DiffType` enum defines the report vocabulary: `CREATE`, `MODIFY`, `DELETE`, and `RENAME`, with printable labels `+`, `M`, `-`, and `R`. `getTypeFromLabel` maps display labels back to enum values and returns `null` for unknown labels, while `parseDiffType` delegates to `valueOf` on an upper-case string and throws for invalid input.

`DiffReportEntry` is the per-change record. It stores a `DiffType`, a byte-array source path relative to the snapshot root, and an optional target path for renames. Constructors accept either already-flattened byte paths or path-component arrays, converting components through `DFSUtilClient.byteArray2bytes`. `toString` prints the label and a `./relative/path` display path; rename entries add ` -> ./target`. `getPathString` maps an empty path to `Path.CUR_DIR`.

The outer class stores `snapshotRoot`, `fromSnapshot`, `toSnapshot`, `diffList`, and `diffStats`. The simple constructor creates zeroed stats. `getLaterSnapshotName` returns `toSnapshot`, and `toString` emits a human-readable report header plus all entries.

`DiffStats` stores directory/file processed and compared counts and total children-listing time. The constructor currently assigns the processed and compared fields from the opposite constructor parameters for dirs and files, so callers and tests should watch for this field-order behavior.

## Control Flow
There is no external I/O or active diff computation in this class. The NameNode-side snapshot machinery constructs `DiffReportEntry` instances and a `SnapshotDiffReport`; clients then access fields or render it. Rendering normalizes `null` or empty snapshot names to "current directory" and otherwise prints "snapshot <name>".

Equality for `DiffReportEntry` checks type plus source and target byte-array content. `hashCode` uses only source and target paths, not the diff type, which is legal but can increase collisions if the same path appears with different types.

## State and Persistence Behavior
Instances are mostly immutable after construction. The list reference is stored directly, so the effective immutability depends on callers not mutating the supplied list. Paths are stored as raw byte arrays and returned directly, so callers can mutate arrays unless they copy them. There is no persistence in this class; persistence/serialization happens through protobuf/PB helper layers and NameNode snapshot code.

## Dependencies and Integration Points
This class depends on `DFSUtilClient` for HDFS byte/string path encoding, Hadoop `Path` constants for `.` and `/`, and shaded Guava `Objects` for hashes. It is constructed from NameNode snapshot diff code such as `SnapshotDiffInfo` and `SnapshotManager`, returned through `ClientProtocol`/`DistributedFileSystem`, and surfaced through WebHDFS JSON utilities and CLI snapshot commands.

## Risks and Edge Cases
Wire and API compatibility depends on stable `DiffType` names and labels. Empty paths are special and render as `.`, while non-empty paths render with a `./` prefix. `getTypeFromLabel` returning `null` can push validation to callers. Direct exposure of mutable byte arrays and list references can surprise clients. The `DiffStats` constructor parameter assignment deserves regression coverage because it can silently swap processed/compared counters.

## Test Signals
Snapshot diff behavior is covered by tests under `hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDiffReport.java`, `TestRenameWithSnapshots`, `TestSnapshotDeletion`, `DFSTestUtil.verifySnapshotDiffReport`, WebHDFS tests in `TestWebHDFS`, and encryption-zone snapshot tests in `TestEncryptionZones`. Useful focused tests would assert label parsing, root/empty path rendering, rename target rendering, equality/hash behavior, and `DiffStats` getter values.
