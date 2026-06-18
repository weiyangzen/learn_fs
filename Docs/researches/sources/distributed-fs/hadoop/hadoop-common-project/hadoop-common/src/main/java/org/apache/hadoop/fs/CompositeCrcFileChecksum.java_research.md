## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CompositeCrcFileChecksum.java

Purpose: `CompositeCrcFileChecksum` is a HDFS-limited, unstable `FileChecksum` implementation for a four-byte composite CRC. It records the CRC integer, the `DataChecksum.Type`, and bytes-per-CRC metadata so callers can identify both the checksum value and the data checksum parameters that produced it.

Important APIs and types: `LENGTH` is fixed at four bytes. `getAlgorithmName()` returns `"COMPOSITE-" + crcType.name()`, `getLength()` returns `LENGTH`, `getBytes()` serializes the int through `CrcUtil.intToBytes`, and `getChecksumOpt()` returns `Options.ChecksumOpt`. Writable methods `readFields` and `write` persist only the CRC integer.

Control flow, state, and persistence: construction initializes all fields. The wire format is intentionally minimal: only `crc` is read/written, so callers must preserve `crcType` and `bytesPerCrc` through construction or surrounding protocol context. `toString()` renders the algorithm name and a zero-padded hex CRC.

Dependencies and integration: it extends the abstract `FileChecksum` equality/hash contract and uses Hadoop utility classes `CrcUtil` and `DataChecksum`. HDFS checksum paths can return this type where composite CRCs are computed over block-level data.

Risks and test signals: the main risk is incomplete Writable reconstruction because `crcType` and `bytesPerCrc` are not serialized here. Tests should cover algorithm naming, byte order, `ChecksumOpt`, equality inherited from `FileChecksum`, and round trips in the actual protocol that supplies the missing metadata.
