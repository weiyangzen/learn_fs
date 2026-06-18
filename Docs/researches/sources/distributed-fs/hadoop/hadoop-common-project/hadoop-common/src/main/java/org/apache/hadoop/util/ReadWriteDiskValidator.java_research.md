# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidator.java

## Purpose
`ReadWriteDiskValidator` verifies a directory by checking directory validity, writing random bytes to a temporary file, reading them back, comparing content, and recording latency/failure metrics.

## Important APIs, Types, And Functions
The class implements `DiskValidator` and exposes `NAME = "read-write"` plus `checkStatus(File dir)`. It uses `ReadWriteDiskValidatorMetrics`, `DiskChecker.checkDir`, `Files.createTempFile`, `Files.write`, `Files.readAllBytes`, and `DiskErrorException`.

## Control Flow
`checkStatus` gets the metrics object for the directory, rejects non-directories, delegates permission/existence checks to `DiskChecker`, creates a temp file in the target directory, writes 16 random bytes while timing microseconds, reads the file while timing microseconds, compares byte arrays, and deletes the temp file in `finally`. IO failures and content mismatch increment failure metrics and throw `DiskErrorException`.

## State And Persistence
The validator has no instance state. A static `Random` supplies test bytes. It creates and deletes one temp file; failures during deletion are reported as disk-check failures.

## Dependencies And Integration Points
It integrates with Hadoop's disk validator framework and metrics2 through `ReadWriteDiskValidatorMetrics`.

## Risks
The random generator is shared but `Random` is thread-safe enough through synchronization in modern JDK internals; contention is possible. Deletion failure masks prior success as a disk failure. The 16-byte write tests basic IO, not capacity, fsync, or sustained performance.

## Test Signals
Tests should cover valid directories, non-directories, permission failures, read/write corruption simulation, metrics latency updates, failure counter updates, and cleanup failure behavior.
