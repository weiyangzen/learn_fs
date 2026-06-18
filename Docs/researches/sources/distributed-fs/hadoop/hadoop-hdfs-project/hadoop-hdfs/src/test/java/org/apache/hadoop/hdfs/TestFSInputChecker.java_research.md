# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSInputChecker.java

## Purpose

`TestFSInputChecker.java` exercises checksum-aware input stream reads for HDFS and local filesystems. The complete 382-line file was read. It verifies reads, seeks, skips, checksum verification toggling, `seek` plus read behavior, and explicit local checksum/data corruption detection.

## Important APIs, Types, and Functions

Key APIs are `FSDataInputStream`, `FSDataOutputStream`, `FileSystem`, `LocalFileSystem`, `ChecksumException`, `IOUtils.readFully`, `IOUtils.skipFully`, `FsPermission`, and `MiniDFSCluster`. Constants set tiny checksum and block geometry: `BYTES_PER_SUM=10`, `BLOCK_SIZE=20`, `HALF_CHUNK_SIZE=5`, and `FILE_SIZE=39`. Helpers include `writeFile`, `checkReadAndGetPos`, `checkSeek`, `checkSkip`, `testChecker`, `testFileCorruption`, `checkFileCorruption`, `testSeekAndRead`, and `readAndCompare`.

## Control Flow

`testFSInputChecker` seeds expected bytes, configures HDFS block and checksum sizes, runs the checker against HDFS with checksum verification enabled and disabled, then repeats against `LocalFileSystem` and adds corruption checks. `checkReadAndGetPos` reads across checksum and block boundaries while checking `getPos`. `checkSeek` probes checksum-aligned, non-aligned, same-chunk, and EOF seeks. `checkSkip` validates successful skips and exact `EOFException` messages for over-skips. Local corruption rewrites either the `.crc` sidecar or the data file through `RandomAccessFile` and expects `ChecksumException`.

## State and Persistence Behavior

The tests create temporary `try.dat` files and local `.crc` sidecars, then delete them. HDFS state is transient MiniDFSCluster block data. The class keeps per-test expected bytes, actual buffers, stream handle, and deterministic random state.

## Dependencies and Integration Points

It covers `FSInputChecker` behavior indirectly through HDFS and local filesystem streams, local checksum sidecar handling, HDFS checksum configuration, and shared Hadoop IO utilities.

## Risks and Edge Cases

Risks include off-by-one positions around checksum chunks, incorrect skip EOF accounting, stale checksum verification flags on `FileSystem`, and local corruption paths that must throw checksum errors without masking other IO failures.

## Test Signals

Signals are byte-for-byte comparisons with buffer erasure after checks, exact stream positions, expected `EOFException` messages, `markSupported=false`, no cleanup leftovers, and positive `ChecksumException` detection for corrupted checksum and data files.
