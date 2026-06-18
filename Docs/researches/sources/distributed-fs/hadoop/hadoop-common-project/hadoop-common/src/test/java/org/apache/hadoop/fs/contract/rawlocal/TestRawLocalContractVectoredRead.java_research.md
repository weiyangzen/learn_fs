# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractVectoredRead.java

## Purpose
`TestRawLocalContractVectoredRead` runs the generic vectored-read contract suite against raw local FS for each configured buffer type.

## Important APIs, Types, And Functions
It is parameterized with `@ParameterizedClass`/`@MethodSource("params")`, extends `AbstractContractVectoredReadTest`, forwards the buffer type to `super`, and creates `RawlocalFSContract`.

## Control Flow
All vectored-read scenarios are inherited: range validation, data reads, buffer allocation mode, EOF behavior, and result validation run against raw local files.

## State And Persistence
No local fields beyond inherited parameterized state. Raw local test files are temporary.

## Dependencies And Integration Points
It exercises raw local `FSDataInputStream.readVectored()` without checksum wrappers.

## Risks
Direct/raw reads do not perform checksum validation, so this test complements but does not replace local FS checksum tests.

## Test Signals
Signals are correct data buffers for all ranges and buffer types, plus expected range/EOF exceptions.
