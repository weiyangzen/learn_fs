## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageLoader.java

Purpose: `FSImageLoader` loads protobuf fsimage sections into memory and provides JSON-producing namespace query methods used by the Web processor.

Important APIs and control flow: `load(inputFile)` checks the fsimage magic, loads the `FileSummary`, sorts sections by `SectionName`, and reads `STRING_TABLE`, `INODE`, `INODE_REFERENCE`, and `INODE_DIR`. Inodes are stored as serialized byte arrays sorted by id; directories map parent inode id to child ids, resolving reference children through the reference section. Query methods resolve paths via `lookup`, binary-search inodes via `fromINodeId`, and format WebHDFS-compatible JSON for file status, listings, content summaries, xattrs, and ACLs.

State, persistence, and dependencies: persistent input is the fsimage file; runtime state is `stringTable`, sorted `inodes`, and `dirmap`. It depends on fsimage protobuf classes, `FSImageUtil`, `FSImageFormatPBINode.Loader`, `JsonUtil`, ACL/XAttr types, and Guava-like Hadoop third-party collections.

Integration points: `FSImageHandler` calls these methods for offline WebHDFS. `FileDistributionCalculator` independently reads protobuf image sections and does not use this loader.

Risks and test signals: tests should cover path lookup, root and empty directories, symlinks, erasure-coded files, xattr filtering and not-found errors, ACL loading, recursive content summaries, and reference children. `fromINodeId` returns `null` when missing, so callers can throw later `NullPointerException`; corrupted images should have explicit tests. Memory use scales with all inode byte arrays and directory maps.
