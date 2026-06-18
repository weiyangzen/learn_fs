<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/Crc32PerformanceTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/Crc32PerformanceTest.java

## Purpose

`Crc32PerformanceTest.java` is a command-line performance benchmark comparing CRC32 and CRC32C implementations over direct and heap `ByteBuffer` inputs.

## Important APIs, Types, and Functions

It defines the `Crc32` interface with implementations `Native`, `NativeC`, `Zip`, `ZipC`, `PureJava`, and `PureJavaC`; constructor state `dataLengthMB`, `trials`, `direct`, `crcs`; and helpers `run`, `main`, `newData`, `computeCrc`, overloaded `doBench`, `BenchResult`, `secondsElapsed`, and `printSystemProperties`.

## Control Flow

Construction selects benchmark targets based on Java version and native CRC availability. `run` prints environment data, warms up each target, then benchmarks byte-per-CRC sizes from 32 bytes to 64 KiB and thread counts from one to sixteen. Worker threads repeatedly call `verifyChunked`, reset buffer marks, record MB/s, and average results.

## State and Persistence Behavior

Benchmark state is in memory: random data buffers, computed checksum buffers, target class list, and timing results. Output is printed to `System.out` in JIRA-table style; nothing is persisted.

## Dependencies and Integration Points

It integrates with `DataChecksum`, `NativeCrc32`, `PureJavaCrc32`, `PureJavaCrc32C`, `Shell`, `GenericTestUtils`, SLF4J logging, Java reflection, and `java.util.zip`.

## Risks and Edge Cases

Results are environment-sensitive and not deterministic unit-test evidence. Direct-buffer native paths differ from array paths. Reflection requires public no-arg constructors, and failed worker threads surface only when `BenchResult.getMbps()` is read.

## Test Signals

This is primarily a manual benchmark. Correctness signals include checksum verification without `ChecksumException`, support for heap/direct buffers, native availability gating, and JVM/system property output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/Crc32PerformanceTest.java -->
