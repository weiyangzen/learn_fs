# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestChecksumFileSystem.java

## Purpose
`TestChecksumFileSystem` validates `ChecksumFileSystem` and `LocalFileSystem` checksum behavior. It checks checksum length math, checksum verification toggles, multi-chunk reads, truncated and corrupted checksum files, stream wrapping, checksum rename behavior, checksum configuration validation, CRC permission propagation, and root operations.

## Important APIs, Types, And Functions
The fixture uses static `LocalFileSystem localFs` rooted under `GenericTestUtils.getTempPath("work-dir/localfs")`. `resetLocalFs()` gets the local filesystem and enables checksum verification. Key methods include `ChecksumFileSystem.getChecksumLength()`, `localFs.getChecksumFile()`, `localFs.getRawFileSystem()`, `FileUtil.copy()`, `localFs.setVerifyChecksum()`, and helper `verifyRename()`.

## Control Flow
Tests first assert checksum length calculations for boundary sizes and huge values. Verification tests write files, read at buffer boundaries around 512 and 1024 bytes, replace or truncate checksum files, expect `ChecksumException`, then disable verification and ensure raw reads succeed. Stream-type tests assert `FSInputChecker` wrapping only when verification is enabled. Rename tests verify checksum files move with data files, stale destination checksum files are removed when the source has none, and checksum files are recreated when present. Configuration tests reject zero/negative bytes-per-checksum. Permission tests ensure CRC file permissions track data-file permissions.

## State And Persistence Behavior
The suite writes local files and `.crc` sidecar checksum files. Some tests deliberately mutate raw files or checksum files behind `LocalFileSystem` to create stale or corrupted checksum state. The root path is reused across tests, so individual tests delete specific paths as needed.

## Dependencies And Integration Points
It integrates `LocalFileSystem`, `ChecksumFileSystem`, raw local filesystem access, checksum stream verification, `FileSystemTestHelper` read/write helpers, `FileUtil`, and local filesystem configuration keys.

## Risks
Tests depend on local filesystem sidecar checksum behavior and are not portable to filesystems without `.crc` files. Some tests use Java `assert` rather than JUnit assertion for CRC existence. The shared static local filesystem can carry configuration state if reset behavior changes.

## Test Signals
Passing shows checksum sidecars are sized, verified, corrupted-detected, ignored when requested, renamed, permission-synchronized, and configured correctly for local checksum filesystems.
