<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcUtil.java

## Purpose

`TestCrcUtil.java` validates low-level CRC arithmetic helpers, serialization helpers, and debug string formatting for CRC32 and CRC32C.

## Important APIs, Types, and Functions

It tests `CrcUtil.compose`, `composeWithMonomial`, `getMonomial`, `intToBytes`, `writeInt`, `readInt`, `toSingleCrcString`, `toMultiCrcString`, and multiply-mod behavior. It also includes a `Benchmark` main class for manual arithmetic benchmarking.

## Control Flow

Composition tests compute a full data CRC, compute per-chunk CRCs, then compose them with and without precomputed monomials across multiple chunk sizes and final partial chunks. Zero-length composition is checked as identity. Multiply-mod tests compare optimized arithmetic to a local Galois-field multiply implementation over many random inputs.

## State and Persistence Behavior

State is in-memory random data and byte arrays. The benchmark prints to stdout but persists nothing.

## Dependencies and Integration Points

It integrates with `DataChecksum`, `CrcUtil`, `LambdaTestUtils`, Java random data, and Java functional `LongToIntFunction`.

## Risks and Edge Cases

CRC polynomial arithmetic is easy to break silently. Edge cases include zero-length second CRCs, odd chunk sizes, endian serialization, invalid CRC byte-array lengths, and CRC32 vs CRC32C polynomial selection.

## Test Signals

Signals include equality between full and composed CRCs, exact hex-string formats, invalid-length exceptions, big-endian integer checks, and optimized multiply-mod equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcUtil.java -->
