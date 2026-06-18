# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystem.java

Purpose: broad regression suite for `LocalFileSystem` and `RawLocalFileSystem` through the `FileSystem` abstraction, covering CRUD, working directory, checksum sidecars, statistics, builder APIs, rename semantics, buffered reads, and platform path behavior.

Important APIs/types/functions: `FileSystem.getLocal`, `RawLocalFileSystem`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileUtil.copy`, `reportChecksumFailure`, `setTimes`, `BufferedFSInputStream`, `createFile`/`openFile` builders, `FSDataOutputStreamBuilder`, `Statistics`, `CreateFlag`, `Options.ChecksumOpt`, and mocked file status for pipe-like files.

Control flow/state/persistence: setup forces `fs.file.impl` to `LocalFileSystem`, resets the test root, and teardown restores writability, deletes temp content, and re-enables stat. Tests create local files/directories, copy/rename/delete them, read data, manipulate permissions, induce checksum quarantine by making an ancestor non-writable, set timestamps, perform randomized seek/read verification, test directory rename overwrite/move cases, strip URI fragments during resolution, verify append stream position, handle non-file/non-directory path listing, validate builder defaults/options, and assert byte statistics include CRC sidecar IO for classic and builder APIs.

Dependencies/integration points: integrates local FS with checksum FS wrappers, raw local streams, statistics accounting, Mockito spies/mocks, platform assumptions, and builder option validation.

Risks/test signals: high-value regression coverage for local IO semantics. Signals include CRC byte accounting mismatches, checksum failure quarantine path regressions, random seek/read corruption, rename semantics changes, builder unsupported mandatory keys, fragment leakage, Windows path inconsistencies, and pipe-file status handling.
