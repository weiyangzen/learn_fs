# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/EtagChecksum.java

Purpose: Hadoop `FileChecksum` implementation that represents an object-store ETag as checksum bytes.

Important APIs, types, and functions: constructors, `getAlgorithmName()`, `getLength()`, `getBytes()`, `write()`, `readFields()`, `equals()`, `hashCode()`, and `toString()` methods.

Control flow: the ETag string is encoded as UTF-8 bytes for checksum APIs and serialized through Hadoop writable methods. It is intended for change detection rather than cross-store content equivalence.

State and persistence: stores a mutable ETag string, defaulting to empty. Persists through Hadoop `Writable` serialization.

Dependencies and integration points: extends `FileChecksum`; uses `DataInput`, `DataOutput`, and UTF-8. Used by object-store filesystems that expose remote ETag metadata through Hadoop checksum APIs.

Risks and test signals: ETags are not cryptographic content checksums and multipart/object-store semantics vary. Tests should cover empty/default values, serialization round trip, UTF-8 bytes, equality/hash, and algorithm name compatibility.
