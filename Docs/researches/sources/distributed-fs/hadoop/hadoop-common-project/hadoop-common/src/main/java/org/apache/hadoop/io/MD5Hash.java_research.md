# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MD5Hash.java

Purpose: `MD5Hash` is a stable `WritableComparable` representation of a 16-byte MD5 digest, with helpers for digest creation, hex conversion, partial numeric digest extraction, equality, hashing, and raw byte comparison.

Important APIs and types: `MD5_LEN` fixes digest length. A thread-local `MessageDigest` avoids repeated MD5 construction. Constructors create zeroed, hex-derived, or byte-array-backed hashes. `readFields`, `write`, and static `read` implement Writable format. `digest(...)` overloads hash byte arrays, `InputStream`, `String`, `UTF8`, and arrays of byte arrays. `halfDigest()` and `quarterDigest()` expose the first 8 or 4 bytes as numeric values. Nested `Comparator` compares serialized digest bytes directly.

Control flow: digest helpers reset a thread-local `MessageDigest`, update it with the requested data, and wrap the resulting 16 bytes. Hex parsing validates 32 characters and converts each nibble; `toString()` emits lowercase hex. Writable reads fill the existing digest array and writes emit the raw 16 bytes.

State and persistence: each instance holds a mutable `byte[] digest`; the byte-array constructor stores the caller's array rather than copying it, and `getDigest()` exposes that array. Persistent representation is exactly the 16 digest bytes. The static comparator registration affects Hadoop's global Writable comparator registry.

Dependencies and integration points: depends on Java security `MessageDigest`, Hadoop `UTF8`, `WritableComparator`, and `WritableComparable`. It is suitable for file checksums, partitioning keys, and compact hash IDs inside Hadoop serialization.

Risks and test signals: MD5 is not collision-resistant for adversarial security use, so callers must not use it as a modern trust primitive. Additional risks include mutable digest aliasing, unchecked `RuntimeException` for bad hex characters, and `digest(byte[][], start, len)` applying the same slice to every array. Tests should cover hex round trips, invalid length/characters, stream hashing, comparator ordering, exposed-array mutation, and digest equality/hash behavior.
