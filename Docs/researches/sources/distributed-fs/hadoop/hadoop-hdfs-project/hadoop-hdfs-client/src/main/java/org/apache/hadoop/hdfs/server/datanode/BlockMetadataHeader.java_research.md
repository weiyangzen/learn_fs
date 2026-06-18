# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockMetadataHeader.java

## Purpose

`BlockMetadataHeader.java` reads and writes the fixed header at the start of HDFS DataNode block metadata files. That header records a metadata version and the `DataChecksum` definition used for block CRC chunks.

## Important APIs, Types, and Functions

The class declares `VERSION = 1`, stores final `version` and `DataChecksum checksum`, and exposes `getVersion`, `getChecksum`, `readDataChecksum(FileInputStream,int,File)`, `readDataChecksum(DataInputStream,Object)`, `preadHeader(FileChannel)`, `readHeader(DataInputStream)`, `readHeader(FileInputStream)`, `readHeader(RandomAccessFile)`, testing constructor, testing `writeHeader(DataOutputStream, BlockMetadataHeader)`, public `writeHeader(DataOutputStream, DataChecksum)`, and `getHeaderSize`.

## Control Flow

Sequential readers wrap streams as buffered `DataInputStream`, read the version short, parse a checksum header using `DataChecksum.newDataChecksum`, and wrap EOF or invalid checksum-size failures as `CorruptMetaHeaderException`. `readDataChecksum` warns if the on-disk version differs from `VERSION` but still returns the checksum. `preadHeader` reads exactly the header size from a `FileChannel` at positional offsets without changing channel position, then decodes version bytes and checksum bytes. `readHeader(RandomAccessFile)` seeks to zero and reads the fixed header buffer.

## State and Persistence Behavior

Instances are immutable holders for header data. Persistent behavior is the on-disk metadata header: two bytes of version plus the checksum header size reported by `DataChecksum`. Writers emit version `1` by default and then delegate checksum header serialization to `DataChecksum`.

## Dependencies and Integration Points

Dependencies include Java file/stream/channel APIs, `DataChecksum`, `InvalidChecksumSizeException`, SLF4J logging, and `CorruptMetaHeaderException`. It integrates with DataNode block metadata file readers/writers and client short-circuit read paths that need metadata header parsing without disturbing file-channel position.

## Risks and Edge Cases

Truncated or corrupt metadata files must throw `CorruptMetaHeaderException` rather than generic EOF/checksum-size failures. `preadHeader` loops while the buffer has remaining bytes and treats non-positive reads as corruption. Version mismatch is only a warning, so later code must tolerate checksum formats. `RandomAccessFile` reading changes file position by seeking to zero. Header size must stay aligned with `DataChecksum.getChecksumHeaderSize()`.

## Test Signals

Tests should cover valid header write/read round trips, short/truncated files for each read path, invalid checksum type/size bytes, version mismatch logging behavior, positional read preserving channel position, and header-size expectations.
