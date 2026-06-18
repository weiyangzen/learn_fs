# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestXDR.java

Purpose: Serialization stress/performance-style test for XDR integer and hyper-long read/write loops.

Important APIs/types/functions: `XDR`, `writeInt`, `readInt`, `writeLongAsHyper`, `readHyper`, `asReadOnlyWrap`, and constant `WRITE_VALUE`.

Control flow: `testPerformance` writes and reads `8 << 20` integers, then writes and reads the same count of hyper longs, asserting every decoded value equals 23.

State and persistence: large in-memory XDR buffers only.

Dependencies/integration points: Hadoop ONC/RPC XDR encoding layer.

Risks: heavy memory/CPU for a unit test; named as performance but asserts correctness; lacks edge cases for negative values, padding, and variable opaque fields.

Test signals: catches bulk buffer growth, wrapping, and repeated primitive serialization/deserialization regressions.
