<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java

## Purpose
`PBImageCorruptionDetector` is an offline image viewer processor that extends `PBImageTextWriter` to detect limited fsimage namespace corruption while producing delimited text output. It focuses on directory-section references to missing inode IDs and directories whose child list contains missing children; it explicitly does not claim exhaustive fsimage validation.

## APIs and Types
The main API is package-visible construction with `PrintStream`, delimiter, and metadata temp path, plus overrides of `getHeader`, `getEntry`, `checkNode`, `buildNamespace`, and `afterOutput`. `OutputEntryBuilder` formats rows with corruption type, id, snapshot flag, parent path/id, name, node/ref/unknown type, and corrupt child count. `CorruptionChecker` records inode IDs from the INode section and reference IDs from the INodeReference section.

## Control Flow
During the first `PBImageTextWriter` pass, `checkNode` delegates directory collection to the superclass and records every inode id. In the directory-section pass, `buildNamespace` saves reference IDs, checks parent existence, stores child-parent relationships, checks child existence, and records parent missing-child corruption counts. During output, only inodes present in `corruptionsMap` produce rows; leftover corruptions without resolvable paths are emitted in `afterOutput`.

## State and Persistence
State is in-memory for corruption detection: a `HashSet` of inode IDs, a `HashSet` of reference IDs, and a `TreeMap<Long, PBImageCorruption>` for deterministic row order of unresolved corruptions. Namespace metadata persistence is inherited from `PBImageTextWriter` and may be memory or LevelDB depending on temp path.

## Dependencies and Integration
It depends on `FsImageProto`, `PBImageTextWriter`, `PBImageCorruption`, `IgnoreSnapshotException`, and Hadoop `Preconditions`. It integrates with OIV DetectCorruption processing and reuses superclass metadata loading, path lookup, and delimited escaping.

## Risks
`buildNamespace` assumes `refIdList` is non-null and that every ref child index is valid; corrupt references outside the list may fail rather than report a row. The output marks unresolved corruptions as `isSnapshot=true` when path/name lookup fails, which is a pragmatic label rather than proof the node came from a snapshot. Detection is intentionally narrow and misses block-level, permission, xattr, quota, and protobuf structural corruption beyond parse failures.

## Test Signals
Tests should cover missing child inode, missing parent inode, combined missing-node plus missing-child corruption, valid reference children, corruptions whose parent path cannot be resolved, custom delimiters, and deterministic ordering of leftover corruption rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java -->
