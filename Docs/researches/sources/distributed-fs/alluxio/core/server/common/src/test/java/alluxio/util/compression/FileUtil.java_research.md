<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java

## Purpose
Provides a small assertion helper shared by compression tests to compare an original filesystem tree with a reconstructed tree after archive extraction.

## Important APIs, Types, And Functions
- `assertDirectoriesEqual(Path path, Path reconstructed)` walks the original tree, checks each corresponding reconstructed path exists, verifies file-vs-directory type, compares bytes for file inputs, and finally checks total entry counts match.

## Control Flow
The helper traverses `path` with `Files.walk`, relativizes each source entry, resolves it under `reconstructed`, and performs JUnit assertions. It increments an `AtomicLong` for original entry count, then separately walks the reconstructed tree to ensure no extra entries were produced.

## State And Persistence Behavior
No persistent state is kept. It reads bytes from test-created files and relies on temporary directories owned by the caller.

## Dependencies And Integration Points
Uses JUnit assertions, Java NIO walking and byte reads, and `AtomicLong` to mutate a count from inside a lambda. It is consumed by `TarUtilsTest`, `ParallelZipUtilsTest`, and `DirectoryMarshallerTest`.

## Risks And Edge Cases
The file-content branch checks `path.toFile().isFile()` rather than `subPath.toFile().isFile()`, so when the root is a directory it primarily verifies existence/type/count rather than content for every nested file. That makes the helper weaker for directory round trips than intended.

## Test Signals
The helper's passing assertions signal structural equality and, for root-file inputs, byte equality. Compression tests should be interpreted with the noted nested-file content limitation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/FileUtil.java -->
