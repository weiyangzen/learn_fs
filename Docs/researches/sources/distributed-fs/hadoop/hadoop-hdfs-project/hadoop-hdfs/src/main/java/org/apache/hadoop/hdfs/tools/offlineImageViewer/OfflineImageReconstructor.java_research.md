## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageReconstructor.java

Purpose: `OfflineImageReconstructor` is the ReverseXML implementation for protobuf fsimages. It reads XML produced by the PB image writer and writes a binary fsimage plus `.md5`.

Important APIs and control flow: `run(inputPath, outputPath)` deletes stale output, opens UTF-8 XML input and a digesting counted output stream, calls `processXml`, then saves the MD5. The constructor creates a secure StAX reader and registers `SectionProcessor` handlers for Name, ErasureCoding, INode, SecretManager, CacheManager, SnapshotDiff, INodeReference, INodeDirectory, FilesUnderConstruction, and Snapshot sections. `processXml` validates `<version>`, writes the magic header, processes each required section once, writes the generated string table after other sections, then writes `FileSummary` and its length.

State, persistence, and dependencies: state includes output byte count, section offsets, `FileSummary.Builder`, a generated string table, latest string id, and a date parser. Dependencies include fsimage protobufs, `PBImageXmlWriter` tag constants, StAX, MD5 utilities, ACL/XAttr encoding masks, and protobuf builders.

Integration points: called by `OfflineImageViewerPB` for processor `ReverseXML`; it is the inverse of PB XML output.

Risks and test signals: round-trip XML-to-image tests should cover every section, ACLs, xattrs, erasure coding, snapshots, cache manager data, string-table limits, layout-version mismatch, unknown/duplicate sections, and MD5 generation. A concrete code risk is in `CacheManagerSectionProcessor`: it loads per-pool/per-directive nodes but calls `processPoolXml(node)` and `processDirectiveXml(node)` instead of passing the local entry node, which can break cache-manager reconstruction and should have targeted tests.
