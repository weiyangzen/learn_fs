<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java

## Purpose
Tests `ParallelZipUtils` directory compression/decompression behavior and verifies that nonzero compression levels reduce archive size for compressible input.

## Important APIs, Types, And Functions
- `ParallelZipUtils.compress(Path, OutputStream, int, int)` writes an archive using a thread count and compression level.
- `ParallelZipUtils.decompress(Path, String, int)` reconstructs a destination path from a zip file.
- `zipUnzipTest` creates a temporary zip file, deletes the precreated extraction directory, decompresses, and compares with `FileUtil.assertDirectoriesEqual`.

## Control Flow
Round-trip tests cover empty, one-file, ten-file, empty-subdirectory, and deeply nested trees. `compressionTest` loops compression levels 0 through 9, records the size at level 0 and later levels, verifies each archive can decompress, cleans each extracted tree and zip, then asserts compressed output is smaller than uncompressed output.

## State And Persistence Behavior
State is temporary directories and temporary zip files under JUnit's `TemporaryFolder`. Cleanup uses Alluxio `FileUtils.deletePathRecursively` and `FileUtils.delete` in the compression-level loop.

## Dependencies And Integration Points
Uses Java NIO, file output streams, JUnit, Alluxio file utilities, and the shared compression `FileUtil`. It validates the parallel zip utility that may be used by snapshot or backup packaging paths.

## Risks And Edge Cases
The test exercises directory entries and deep nesting, but inherits the helper's limited nested-file content check. Compression-size assertions can be sensitive to archive metadata overhead for very small inputs, though the repeated string is chosen to be compressible.

## Test Signals
Passing tests signal zip round-trip structure preservation across representative trees and functional compression-level handling where compressed levels produce smaller files than level 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/ParallelZipUtilsTest.java -->
