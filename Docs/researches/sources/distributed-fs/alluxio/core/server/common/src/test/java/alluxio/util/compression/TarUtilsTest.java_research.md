<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java

## Purpose
Validates `TarUtils` tar-gzip write/read behavior for common directory shapes, compression levels, and large POSIX uid/gid metadata handling.

## Important APIs, Types, And Functions
- `TarUtils.writeTarGz(Path, OutputStream, int)` and `TarUtils.readTarGz(Path, InputStream)` are the tested APIs.
- `tarUntarTest` serializes to memory, deletes the destination directory, extracts, and compares with `FileUtil.assertDirectoriesEqual`.
- `testLargePosixUserAndGroupIds` uses PowerMock to intercept `TarArchiveEntry(File, String)` construction and force large user/group IDs.

## Control Flow
Basic tests create empty, single-file, multi-file, empty-subdirectory, and deeply nested trees. The large-id test verifies tar creation survives metadata values beyond `TarArchiveEntry.MAXID`. `compressionTest` runs levels 0 through 9 and checks that compressed output is smaller than uncompressed output while each archive remains readable.

## State And Persistence Behavior
Uses JUnit temporary directories and in-memory byte arrays. Extracted directories are deleted between compression-level iterations using Alluxio file utilities.

## Dependencies And Integration Points
Depends on Apache Commons Compress tar classes, PowerMock/JUnit runner integration, Java NIO, and the shared compression assertion helper. It covers the tar-gzip backend used by `TarGzMarshaller`.

## Risks And Edge Cases
Tar metadata can fail for large uid/gid values without long-file or big-number handling, so the PowerMock test is a targeted regression signal. The round-trip equality helper has limited nested-file byte checking, so archive content corruption in nested files may need additional direct assertions.

## Test Signals
Passing tests signal tar-gzip can preserve common directory layouts, tolerate large POSIX ids, and honor compression levels enough to shrink compressible input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/TarUtilsTest.java -->
