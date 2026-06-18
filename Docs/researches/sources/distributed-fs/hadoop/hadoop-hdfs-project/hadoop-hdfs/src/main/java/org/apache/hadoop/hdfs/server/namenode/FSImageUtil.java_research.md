## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageUtil.java

Purpose: small utility for recognizing and opening protobuf FSImage files. It defines the protobuf image magic header, validates container version/layout support from the tail summary, and wraps section streams with configured compression codecs.

Important APIs: `MAGIC_HEADER` is the UTF-8 bytes for `HDFSIMG1`; `FILE_VERSION` is the supported on-disk container version. `checkFileFormat(RandomAccessFile)` verifies minimum file length and leading magic bytes. `loadSummary(RandomAccessFile)` reads the last four bytes as summary length, reads the preceding delimited `FileSummary`, validates `ondiskVersion`, and requires the summary layout version to support `Feature.PROTOBUF_FORMAT`. `wrapInputStreamForCompression(Configuration, String, InputStream)` returns the original stream for an empty codec name or creates the configured image codec input stream.

Control flow: callers position or open a `RandomAccessFile`, call `checkFileFormat` to reject short or non-protobuf images, then call `loadSummary` to parse the summary from the file tail. Section readers pass the summary codec string to `wrapInputStreamForCompression` before parsing protobuf records.

State and persistence behavior: this class has no internal mutable state. It encodes container-level persistence constants and validates summary fields that control all protobuf section parsing. `loadSummary` uses a fixed four-byte length suffix and treats nonpositive length as an `IOException`.

Dependencies and integration points: used by `FSImageFormatProtobuf.Loader`, offline image viewer tools such as `FSImageLoader`, `PBImageTextWriter`, and `FileDistributionCalculator`, and any code that needs to inspect protobuf fsimage sections. It depends on `FsImageProto.FileSummary`, `NameNodeLayoutVersion`, `LayoutVersion.Feature.PROTOBUF_FORMAT`, `FSImageCompression`, Hadoop `CompressionCodec`, and `Configuration`.

Risks: `checkFileFormat` consumes bytes from the current file position and does not rewind, so callers must account for file position before subsequent reads. A corrupt or extreme summary length can seek before the file start or allocate a large byte array; validation only rejects nonpositive lengths and unsupported versions. Compression codec class names in the summary are trusted through `FSImageCompression.createCompression`, so missing codecs fail load. The utility validates protobuf-format feature support but does not enforce exact layout-version equality; that is caller policy.

Test signals: tests should cover short files, wrong magic, valid magic, negative or zero summary length, unsupported on-disk version, unsupported layout version, uncompressed stream pass-through, compressed stream wrapping with configured codecs, and offline viewer parsing of summary/sections.
