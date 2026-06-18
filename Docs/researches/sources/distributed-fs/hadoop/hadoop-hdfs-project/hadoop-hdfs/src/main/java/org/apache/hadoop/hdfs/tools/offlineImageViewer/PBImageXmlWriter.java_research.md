<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java

## Purpose
`PBImageXmlWriter` converts a protobuf fsimage into an XML document that preserves the fsimage's major sections: namespace metadata, string-table-dependent inode data, erasure coding policies, inode references/directories, files under construction, snapshots, snapshot diffs, secret manager state, and cache manager state.

## APIs and Types
The public API is construction from `Configuration` and `PrintStream`, `visit(RandomAccessFile)`, and static `createSimpleDateFormat()`. The class exposes many XML tag-name constants. Private dump methods handle each section and protobuf subtype, while `o(tag, value)` emits mangled XML values and compact boolean tags.

## Control Flow
`visit` validates the fsimage, loads summary metadata, prints XML prolog/root/version, sorts sections by `SectionName`, wraps each section input with compression and length limits, then dispatches to section-specific dump methods. Dump methods parse protobuf-delimited records until expected counts or EOF, emitting nested tags for blocks, ACLs, xattrs, quotas, EC schemas, delegation keys/tokens, cache directives, snapshot tables, and diff entries.

## State and Persistence
The writer keeps a `Configuration`, `PrintStream`, UTC `SimpleDateFormat`, and a loaded string table. It writes directly to the supplied stream and does not build persistent intermediate state. Date output is UTC ISO-like with millisecond precision. XAttr values are emitted as UTF-8 text when valid or hex otherwise.

## Dependencies and Integration
It depends on fsimage protobufs, `FSImageUtil`, `FSImageLoader.loadStringTable`, `FSImageFormatPBINode.Loader`, `PBHelperClient`, `XMLUtils`, Hadoop ACL/permission classes, erasure coding schemas, and `VersionInfo`. It is the protobuf-era XML OIV writer rather than the legacy visitor-driven XML writer.

## Risks
The string table must be processed before sections that decode permissions, ACLs, and xattrs; section sorting should provide that ordering, but unknown/new section behavior is limited. Some optional booleans are represented by presence only, which may surprise consumers expecting explicit false values. XML is streamed without recovery; parse or write failures leave truncated output. Secret manager material and delegation token fields are printed, so output handling is security-sensitive. Schema changes require new tag constants and dump logic.

## Test Signals
Tests should validate XML well-formedness, string-table ordering, xattr UTF-8 versus hex output, ACL and permission formatting, EC policy schema options, snapshot diff branches for file and directory diffs, secret/cache manager expected counts, UTC date formatting, and invalid/unknown diff type failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java -->
