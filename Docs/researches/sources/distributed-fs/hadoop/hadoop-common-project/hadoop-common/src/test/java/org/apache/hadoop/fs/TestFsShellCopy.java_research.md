## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellCopy.java

Purpose: broad tests for FsShell copy commands: `-get`, `-put`, `-copyFromLocal`, `-moveFromLocal`, `-getmerge`, checksum handling, Windows local path parsing, direct writes, lazy-persist overwrite behavior, destination resolution, missing parents, and permission-denied reporting.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, checksum files via `getChecksumFile`, `FsPermission`, `GenericTestUtils.getTempPath`, helpers `checkPut`, `prepPut`, `readFile`, `pathAsString`, and shell commands `-get`, `-put`, `-getmerge`, `-moveFromLocal`, `-copyFromLocal`, `-cat`, `-rm`.

Control flow: setup creates a shared local shell root and source/destination paths; per-test setup recreates a checksum-protected source file. Tests cover copying with/without CRC, corrupted checksum failure, ignoring CRC, file and directory put behavior for existing/missing destinations, Windows path variants, directory-looking destination suffixes, getmerge ordering/newline/skip-empty behavior, moveFromLocal source deletion and conflict handling, direct-copy temp-file behavior, missing parent failures, source permission failures, and lazy-persist direct overwrite rules.

State and persistence: uses local filesystem files, checksum sidecars, working-directory changes, permission mutations, stderr capture, and shared static shell/local FS state.

Dependencies/integration points: local filesystem checksum implementation, shell command parsing, path qualification, platform-specific Windows path support, and permission error propagation.

Risks and test signals: destination resolution is subtle, especially `.` and trailing `/`/`/.`. Permission tests must restore permissions. Checksum tests catch data-integrity regressions, and direct-write tests ensure `._COPYING_` cleanup changes only when expected.
