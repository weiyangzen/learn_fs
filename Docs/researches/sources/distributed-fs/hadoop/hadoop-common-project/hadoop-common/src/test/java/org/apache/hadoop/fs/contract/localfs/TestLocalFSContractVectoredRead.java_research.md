# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractVectoredRead.java

## Purpose
`TestLocalFSContractVectoredRead` runs the generic vectored-read suite against local FS and adds checksum/statistics regression coverage.

## Important APIs, Types, And Functions
It is a parameterized class over buffer type, extends `AbstractContractVectoredReadTest`, creates `LocalFSContract`, and defines `testChecksumValidationDuringVectoredRead()`, `testChecksumValidationDuringVectoredReadSmallFile()`, `tesChecksumVectoredReadBoundaries()`, and an override of `testVectoredReadMultipleRanges()`. `validateCheckReadException()` corrupts the raw file after creating a checksummed local file. `assertionsWithinTestVectoredReadMultipleRanges()` verifies stream and global bytes-read counters.

## Control Flow
The checksum tests create a file through `LocalFileSystem` so a checksum file is generated, run `readVectored()` and validate futures, then overwrite the data through raw local FS and expect `ChecksumException` during result validation. The multiple-range override records global bytes-read before the inherited test, then checks vectored operation count and byte counters.

## State And Persistence
`initialBytesRead` records global filesystem byte count. Test files and checksum side files are local temporary state.

## Dependencies And Integration Points
It depends on `FSDataInputStream.readVectored()`, `FileRange`, local checksum files, `ContractTestUtils.validateVectoredReadResult()`, IOStatistics counters, and `FileSystem.getAllStatistics()`.

## Risks
Checksum validation through vectored reads is easy to bypass if reads use raw data incorrectly. Global statistics are process-wide and may include CRC-file reads, so assertions use lower bounds rather than exact values.

## Test Signals
Signals are successful vectored reads with valid checksums, `ChecksumException` after raw corruption, one vectored operation counter increment, and bytes-read counters increasing by at least requested range lengths.
