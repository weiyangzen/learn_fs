## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetFileBlockLocations.java

Purpose: validates `FileSystem.getFileBlockLocations(FileStatus, start, len)` parameter checks and coverage invariants for a local/default filesystem file.

Important APIs/types/functions: `FileSystem.getFileBlockLocations`, `BlockLocation`, `FileStatus`, `FSDataOutputStream`, `GenericTestUtils.getTempPath`, `Path.getFileSystem`, and local helper `oneTest`.

Control flow: setup creates a 4 MiB file by writing 1 KiB zero buffers until the target length. `testFailureNegativeParameters` expects `IllegalArgumentException` for negative start or length. `testGetFileBlockLocations1` checks deterministic ranges before, within, and beyond EOF. `testGetFileBlockLocations2` runs 1000 random start/end pairs. `oneTest` normalizes range order, obtains locations, sorts by offset/length, and asserts the returned locations cover the requested interval clipped to file length, or return empty when starting beyond EOF.

State and persistence: creates and deletes a temp file per test and closes the filesystem in teardown.

Dependencies/integration points: filesystem block location implementation, local/default FS file creation, and block-location range semantics.

Risks and test signals: random testing can expose edge cases but is nondeterministic due to `System.nanoTime` seeding. Invariants focus on coverage rather than exact block layout, making the test portable across filesystems.
