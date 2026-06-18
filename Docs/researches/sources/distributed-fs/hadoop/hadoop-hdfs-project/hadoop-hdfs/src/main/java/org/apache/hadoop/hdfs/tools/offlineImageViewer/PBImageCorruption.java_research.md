## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruption.java

Purpose: `PBImageCorruption` is a value object used by the protobuf image corruption detector to represent one suspicious inode id and the kinds of corruption associated with it.

Important APIs and control flow: the private enum `PBImageCorruptionType` defines output labels for `CORRUPT_NODE` and `MISSING_CHILD`. The constructor requires at least one of the boolean corruption flags and initializes an `EnumSet` plus the corrupt-child count. Mutators add missing-child or corrupt-node aspects and update the count. Accessors return the inode id, a compact type string, and the number of corrupt children. `getType()` concatenates `CorruptNode`, `With`, and `MissingChild` when both aspects are present.

State, persistence, and dependencies: state is inode id, corruption type set, and corrupt-child count. There is no persistence. Dependencies are limited to `EnumSet`.

Integration points: consumed by `PBImageCorruptionDetector` output generation and summary bookkeeping.

Risks and test signals: tests should cover constructor validation, each single corruption type, combined type formatting, updates through mutators, and child-count changes. The type string is presentation logic and should be treated as compatibility-sensitive if downstream tools parse delimited corruption output.
