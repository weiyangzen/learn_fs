<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java

## Purpose
`PBImageDelimitedTextWriter` renders each inode from a protobuf fsimage as one delimited text row, similar to recursive HDFS listing output, with optional storage policy and erasure coding policy columns.

## APIs and Types
It extends `PBImageTextWriter` and implements `getEntry`, `getHeader`, and no-op `afterOutput`. Constructors select delimiter/temp metadata storage and optional storage policy, EC policy, thread count, parallel output path, and configuration. The nested `OutputEntryBuilder` extracts file, directory, and symlink metadata into row fields.

## Control Flow
For each inode, `getEntry` builds a `Path` from parent path and inode name, then `OutputEntryBuilder` switches on inode type. Files contribute replication, mtime, atime, preferred block size, block count, file size, permissions, ACL marker, storage policy, and optional EC policy by ID. Directories contribute mtime, quotas, directory permission prefix, ACL marker, storage policy from xattrs, and optional EC policy xattr name. Symlinks contribute permission and times but not target text.

## State and Persistence
The writer holds booleans for optional columns and an `ErasureCodingPolicyManager` initialized only when EC output is requested with a non-null `Configuration`. All namespace metadata, xattr decoding, and permission string-table access are inherited from `PBImageTextWriter`; this class persists no data.

## Dependencies and Integration
It depends on `FSImageLoader.getFileSize`, `ErasureCodingPolicyManager`, `FsImageProto.INodeSection`, `Path`, `PermissionStatus`, and `HdfsConstants`. It is an OIV text processor implementation backed by the two-pass superclass scanner.

## Risks
`SimpleDateFormat` uses the default JVM timezone, so output is environment-dependent. Symlink targets are not included despite inode-specific metadata extraction. Directory calls to `dir.getXAttrs()` rely on protobuf default behavior when xattrs are absent. EC policy names may remain `-` if the manager does not know an ID.

## Test Signals
Useful tests compare header/row column count under optional flags, exercise file/directory/symlink inodes, verify ACL plus suffix, storage-policy xattr decoding, EC policy ID and xattr policy name paths, CSV escaping inherited from the superclass, and stable path construction for root and empty names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java -->
