## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsOptions.java

Purpose: tests `Options.ChecksumOpt.processChecksumOpt` merging rules for default checksum options, optional custom options, and bytes-per-checksum overrides.

Important APIs/types/functions: `Options.ChecksumOpt`, `DataChecksum.Type.CRC32`, `DataChecksum.Type.CRC32C`, `processChecksumOpt`, `getChecksumType`, and `getBytesPerChecksum`.

Control flow: the test builds a default CRC32/512 option, processes null custom options with and without explicit bytes-per-checksum, processes an empty custom option that should inherit defaults, then processes a CRC32C/2048 option with and without an explicit `4096` bytes-per-checksum override.

State and persistence: all state is in memory and immutable option-like objects.

Dependencies/integration points: checksum option processing is consumed by filesystem create paths, so this test protects caller/default merging semantics before lower-level data checksum creation.

Risks and test signals: regressions can select the wrong checksum algorithm or block size, affecting compatibility and data verification. The helper assertions keep the expected type and bytes-per-checksum pair explicit for every case.
