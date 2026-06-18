# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32.java

Purpose: verifies Hadoop's `PureJavaCrc32` matches `java.util.zip.CRC32` and carries benchmark/table-generation utilities for manual performance work.

Important APIs and types: `PureJavaCrc32`, `CRC32`, `Checksum`, single-byte and byte-array `update`, `reset`, `getValue`, nested `Table`, and nested `PerformanceTest`.

Control flow: `testCorrectness` compares initial/reset state, one-byte updates, fixed byte arrays, UTF-8 text, and 10,000 random byte arrays up to 2048 bytes. `checkOnBytes` verifies equality after every single-byte update, after bulk update, and after a partial slice when long enough. `Table` can generate CRC lookup tables from a polynomial. `PerformanceTest` compares throughput across sizes and thread counts while checking resulting CRC values match.

State and persistence: unit state is two checksum instances. Manual table generation can write `table8.txt`; benchmark state is local arrays/threads.

Dependencies and integration points: provides fallback checksum correctness for environments without native CRC acceleration.

Risks: slice handling, reset state, signed byte updates, or table constants can diverge from JDK CRC32. Test signals are repeated value equality against the JDK implementation.
