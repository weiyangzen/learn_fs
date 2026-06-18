# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestChecksumSupport.java

## Purpose
`TestChecksumSupport` validates mapping from the S3A checksum configuration string to AWS SDK `ChecksumAlgorithm` enum values.

## Important APIs, Types, and Functions
- Tests `ChecksumSupport.getChecksumAlgorithm(Configuration)`.
- Uses `CHECKSUM_ALGORITHM` configuration key.
- Parameterized over supported SDK enum names `CRC32`, `CRC32_C`, `SHA1`, `SHA256`, and `CRC64_NVME`.
- Helper `assertChecksumAlgorithm()` sets the config and asserts the expected enum.

## Control Flow
The parameterized test verifies direct enum-name strings. Dedicated tests verify aliases `CRC32C`/`CRC32_C` and `CRC64NVME`/`CRC64_NVME`. Null/unset config returns `null`. An invalid string raises `IllegalArgumentException`.

## State and Persistence Behavior
All state is in memory in short-lived `Configuration` objects. No persistence or network interactions occur.

## Dependencies and Integration Points
The class integrates S3A configuration parsing with AWS SDK checksum algorithm enums, ensuring user-facing configuration strings map to request-factory checksum behavior.

## Risks and Edge Cases
Adding new supported algorithms in the SDK may require expanding the enum source list or aliases. Invalid values intentionally fail fast.

## Test Signals
Passing confirms checksum config accepts supported names and aliases, treats unset as no checksum algorithm, and rejects invalid input.
