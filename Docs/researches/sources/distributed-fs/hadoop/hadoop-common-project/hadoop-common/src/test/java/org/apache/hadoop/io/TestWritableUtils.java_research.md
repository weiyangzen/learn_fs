<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java

Purpose: Boundary tests for variable-length integer encoding and `readVIntInRange`.

Important APIs/types/functions: `testValue(int val, int vintlen)` writes a value with `WritableUtils.writeVInt`, reads with `readVInt`, and compares expected byte length through buffer length, `getVIntSize`, and `decodeVIntSize`. `testReadInRange(long val, int lower, int upper, boolean expectSuccess)` writes a VLong and verifies `readVIntInRange` succeeds or throws.

Control flow: `testVInt` enumerates positive and negative thresholds around one-byte and multi-byte vint encodings: 12, 127, -112, -113, -128, 128, -129, 255, -256, 256, -257, 65535, -65536, 65536, -65537. It then checks inclusive range success, above-range failure, lower-bound zero success, negative failure, and too-large long failure.

State and persistence behavior: all state is in-memory `DataOutputBuffer`/`DataInputBuffer` byte arrays. Logging prints buffer bytes only under debug.

Dependencies and integration points: depends on `WritableUtils`, `BytesWritable`, `DataOutputBuffer`, `DataInputBuffer`, SLF4J, and JUnit assertions. This is core coverage for Hadoop's compact binary integer encoding shared by many Writables.

Risks and edge cases: `testReadInRange` catches any `IOException` as expected when `expectSuccess` is false and does not inspect message or exception subtype. The suite covers ints and one large long but does not exercise all long encoding boundaries.

Test signals: confirms byte-size calculation and decoding agree with actual serialized size, and that range enforcement rejects out-of-range and overflow values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java -->
