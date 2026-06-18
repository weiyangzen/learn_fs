# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DataChecksum.java

Purpose: `DataChecksum` wraps chunked checksum algorithms used in DFS data transfer, including header serialization, checksum calculation, and verification.

Important APIs and types: checksum IDs/types include NULL, CRC32, CRC32C, DEFAULT, and MIXED. Factories create instances from type/bytes-per-checksum, byte headers, or `DataInputStream`. Core methods include `writeHeader`, `getHeader`, `writeValue`, `compare`, `update`, `reset`, `verifyChunkedSums`, `calculateChunkedSums`, `equals`, `hashCode`, and nested `ChecksumNull`.

Control flow: factories reject nonpositive bytes-per-checksum and unsupported DEFAULT/MIXED creation. Headers are one type byte plus big-endian bytes-per-checksum. Chunk verification dispatches to native CRC when available and direct/array inputs permit, otherwise computes per chunk, compares stored big-endian ints, throws `ChecksumException` with file position on mismatch, and restores buffer marks/positions. Calculation similarly dispatches native or loops over chunks.

State and persistence behavior: stores checksum type, underlying `Checksum`, bytes-per-checksum, and current bytes in sum. Header and checksum bytes are serialized to streams/buffers; no independent persistence.

Dependencies and integration points: central to HDFS block IO; depends on `CRC32`, `CRC32C`, `NativeCrc32`, `PureJavaCrc32`, `ChecksumException`, and `CrcComposer` mod functions.

Risks: byte order and ByteBuffer mark/position preservation are critical. `newDataChecksum(byte[], offset)` assumes header size availability and maps invalid type to `InvalidChecksumSizeException`. Shared instance use is not thread-safe because `summer` and `inSum` mutate.

Test signals: cover header round trips, invalid type/size, NULL checksum no-op, CRC32/CRC32C known vectors, byte-array and direct-buffer calculate/verify, native and pure-Java paths, mismatch positions including partial chunks, buffer position restoration, equals/hashCode, and current byte count reset.
