<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java

## Purpose
`PBImageTextWriter` is the abstract base for OIV processors that emit one text entry per resolvable inode from a protobuf fsimage. Because protobuf fsimage sections are not ordered for path reconstruction, it performs two metadata-loading passes before producing rows.

## APIs and Types
Subclasses implement `getEntry(String parent, INode inode)`, `getHeader()`, and `afterOutput()`. Protected/package hooks include `checkNode`, `buildNamespace`, `getPermission`, `getStoragePolicy`, `getErasureCodingPolicyName`, `putDirChildToMetadataMap`, `getNodeName`, `getParentId`, `serialOutStream`, `printIfNotEmpty`, and static `mergeFiles`. `MetadataMap` abstracts inode-parent and directory-name storage, with `InMemoryMetadataDB` and `LevelDBMetadataMap` implementations.

## Control Flow
`visit(filePath)` verifies fsimage format, loads the file summary, sorts sections by protobuf section order, loads the string table and inode reference section, scans INode sections to save directory names, scans INodeDirectory sections to build child-parent relationships, syncs metadata, then rescans inode data for output. Output is serial unless multiple threads, a real parallel output path, and multiple INodeSub sections are available. Parallel output writes each subsection to a temp file, validates parsed count against expected inode count from the first subsection, writes the header to the destination, and appends temp files in order.

## State and Persistence
The superclass owns `SerialNumberManager.StringTable`, output stream, delimiter, source filename, thread settings, and an erasure-coding xattr sentinel. In-memory metadata stores `Dir` objects and parent maps; LevelDB metadata creates two DBs under the supplied base directory and batches writes in groups of 1024 with a 16K-entry directory path LRU cache. Snapshot/reference paths that cannot be resolved are represented by `IgnoreSnapshotException` and skipped.

## Dependencies and Integration
It depends on NameNode fsimage protobuf classes, `FSImageUtil`, `FSImageFormatPBINode`, `FSImageFormatProtobuf.SectionName`, `SerialNumberManager`, LevelDB JNI/IQ80 APIs, Hadoop `Path`, xattr helpers, and Hadoop IO utilities. It is the shared engine for delimited text and corruption detection processors.

## Risks
LevelDB path cache recursion is synchronized but all reads share LevelDB handles; parallel output calls metadata lookups concurrently, so metadata implementation assumptions matter. `append(String)` uses CSV escaping and newline replacement but not full delimiter-aware quoting for arbitrary custom delimiters. Snapshot inodes are silently skipped except for aggregate warnings. Parallel mode leaves a partially written destination if merge fails after header creation. Recursive path construction can be expensive or stack-heavy for very deep trees despite caching.

## Test Signals
Tests should cover serial and parallel output equivalence, in-memory versus LevelDB metadata, root path and empty-name handling, missing parent/reference snapshot skips, string-table permission resolution, storage policy and EC xattr decoding, temp file cleanup after merge, malformed subsection count detection, and escaping of commas, delimiters, CRLF, and LF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java -->
