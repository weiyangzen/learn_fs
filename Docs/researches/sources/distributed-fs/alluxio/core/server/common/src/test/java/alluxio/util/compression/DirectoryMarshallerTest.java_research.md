<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java

## Purpose
Parameterized round-trip tests for `DirectoryMarshaller` implementations. It verifies that no-compression, gzip, and tar-gzip directory marshallers can serialize and reconstruct representative directory trees.

## Important APIs, Types, And Functions
- `DirectoryMarshaller.write(Path, OutputStream)` and `read(Path, InputStream)` are the tested contract.
- Parameter set includes `NoCompressionMarshaller`, `GzipMarshaller`, and `TarGzMarshaller`.
- `tarUntarTest` writes to a byte array, deletes the precreated destination directory, reads into that path, and compares trees with `FileUtil.assertDirectoriesEqual`.

## Control Flow
Each test creates a temporary source tree: empty directory, one-file directory, ten-file directory, empty subdirectory, or ten-level nested path with a file at the leaf. The same round-trip helper runs against all configured marshaller implementations.

## State And Persistence Behavior
State is temporary filesystem content plus an in-memory serialized byte array. The reconstructed path is intentionally removed before read to verify marshallers create their destination structure.

## Dependencies And Integration Points
Uses JUnit parameterized execution, temporary folders, Java NIO files, and the shared compression test `FileUtil`. It tests common `DirectoryMarshaller` behavior independent of the underlying archive format.

## Risks And Edge Cases
Important edge cases are empty directories and empty nested directories, because archive implementations can accidentally drop directory entries when no regular files exist. Deep nesting checks relative path handling.

## Test Signals
Passing tests signal each marshaller preserves directory existence, file content, file counts, and nested relative paths across write/read cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/util/compression/DirectoryMarshallerTest.java -->
