# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/FileHandle.java

## Purpose
`FileHandle.java` represents the opaque NFS file handle returned to clients and sent back on later operations.

## Important APIs, Types, and Functions
- Default constructor leaves `handle` null for later deserialization.
- `FileHandle(long fileId, int namenodeId)` builds a 32-byte handle with file id in bytes 0-7, namenode id in bytes 8-11, and zeros afterward.
- `FileHandle(long)` defaults namenode id to 0.
- `FileHandle(String)` builds a 32-byte MD5-derived handle with first 16 bytes zero and last 16 bytes digest of the UTF-8 string.
- `serialize(XDR)` writes handle length and fixed opaque bytes.
- `deserialize(XDR)` verifies length, reads fixed opaque bytes, and extracts file id and namenode id.
- `getFileId()`, `getNamenodeId()`, `getContent()`, `toString()`, `equals()`, `hashCode()`, and `dumpFileHandle()` expose and compare handle data.

## Control Flow and State
The object caches decoded `fileId` and `namenodeId` for numeric handles. Deserialization mutates a default instance. String-derived handles do not set meaningful file id/namenode id fields.

## Dependencies and Integration Points
It uses ONCRPC `XDR`, Java `MessageDigest`, `ByteBuffer`, and SLF4J. NFS mount and NFSv3 procedure implementations use file handles as stable references to filesystem objects.

## Risks and Edge Cases
`serialize()` assumes `handle` is non-null. `deserialize()` verifies 32 bytes even though `Nfs3Constant.NFS3_FHSIZE` permits up to 64 bytes, reflecting Hadoop's chosen handle layout. MD5 unavailability leaves `handle` null. `getContent()` protects immutability with a clone.

## Test Signals
Needed tests include numeric handle round-trip, string handle stability, equality/hash behavior, invalid XDR length, and null-handle safety.
