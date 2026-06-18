<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java

## Purpose
Tests `MD5Hash` serialization, ordering, digest-derived numeric helpers, string conversion, thread safety, and reuse of digest factories after IO failure.

## Important APIs, Types, and Functions
`getTestHash()` builds random MD5 bytes through `MessageDigest`. Tests use `MD5Hash` constructors from byte arrays/string hex, `MD5Hash.digest(String/InputStream)`, `quarterDigest`, `halfDigest`, `hashCode`, `compareTo`, and `TestWritable.testWritable`. `SubjectInheritingThread` runs concurrent construction/equality loops.

## Control Flow and State
`testMD5Hash()` checks all-zero/all-ones/random hashes for writable round trip, equality, ordering, string reconstruction, numeric extraction, hash collision avoidance for nearby values, and concurrent equality. `testFactoryReturnsClearedHashes()` forces an input stream to throw after reads and then asserts later string digest results are still correct.

## Dependencies and Integration Points
Depends on Java security `MessageDigest`, Hadoop thread helper, and writable test utilities. It protects digest use in checksums, block IDs, and metadata comparisons.

## Risks and Test Signals
Risks are signed-byte ordering, digest instance reuse after exceptions, and thread-local/shared state contamination. Signals are exact numeric digest values, equality under concurrency, and digest stability after an injected stream failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java -->
