# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32C.java

## Purpose
`PureJavaCrc32C` preserves Hadoop's historical CRC32C checksum type while delegating checksum operations to JDK `CRC32C`, which is final and therefore wrapped rather than subclassed.

## Important APIs, Types, And Functions
The class implements `Checksum`. It delegates `update(int)`, `update(byte[])`, `update(byte[],int,int)`, `update(ByteBuffer)`, `getValue`, and `reset` to a private `CRC32C delegate`. Static `mod(long)` uses a retained CRC32C polynomial table `T`.

## Control Flow
All mutable checksum operations are direct pass-through calls to the delegate. `mod` mirrors the CRC32 version but uses the Castagnoli polynomial table.

## State And Persistence
Instance state lives inside the delegate. Static lookup table data is immutable. No persistent state exists.

## Dependencies And Integration Points
It depends on `java.util.zip.Checksum`, `CRC32C`, `ByteBuffer`, and Hadoop annotations. It integrates with Hadoop checksum paths that require CRC32C but still reference the older `PureJavaCrc32C` class.

## Risks
JDK `CRC32C` availability and behavior are now part of the contract. ByteBuffer update semantics, including position advancement, follow JDK behavior. Static polynomial data must stay exact for `mod` compatibility.

## Test Signals
Tests should cover standard CRC32C vectors, byte-array slices, ByteBuffer updates, reset behavior, multiple update forms producing identical values, and `mod(long)` consistency with generated CRC32C polynomial arithmetic.
