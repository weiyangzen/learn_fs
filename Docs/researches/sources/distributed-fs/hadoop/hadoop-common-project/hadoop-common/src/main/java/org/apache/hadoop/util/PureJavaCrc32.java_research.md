# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32.java

## Purpose
`PureJavaCrc32` preserves Hadoop's public CRC32 class name while delegating normal checksum behavior to the JDK native `java.util.zip.CRC32`, which is faster on modern JVMs.

## Important APIs, Types, And Functions
The class extends `CRC32` and does not override update/reset/value methods. Its Hadoop-specific API is static `mod(long)`, which computes reduction by the CRC32 polynomial using the retained lookup table `T`.

## Control Flow
Checksum operations use inherited JDK behavior. `mod` splits the long into high and low words, indexes four slices of `T` from the low word's bytes, XORs the table results, and XORs the high word.

## State And Persistence
Per-instance checksum state is owned by the superclass. Static table `T` is immutable and retained for polynomial math compatibility. There is no persistence.

## Dependencies And Integration Points
It depends on `java.util.zip.CRC32` and Hadoop annotations. It integrates with Hadoop checksum code expecting the historical `PureJavaCrc32` type and `mod` helper.

## Risks
Behavior now depends on JDK CRC32 implementation, so compatibility must be checked across supported JDKs. The large static table is easy to corrupt mechanically. Subclassing `CRC32` preserves API but may differ from the legacy pure-Java performance/profile assumptions.

## Test Signals
Tests should compare values with known CRC32 vectors, exercise incremental and bulk updates through inherited methods, validate `reset`, and verify `mod(long)` against independently generated polynomial reductions.
