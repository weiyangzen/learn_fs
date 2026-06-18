# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalDirAllocator.java

Purpose: exercises `LocalDirAllocator` allocation, recovery, and diagnostic behavior across relative, absolute, and qualified local directory configurations.

Important APIs/types/functions: `LocalDirAllocator`, context key `mapred.local.dir`, `createTmpFileForWrite`, `getLocalPathForWrite`, `getLocalPathToRead`, `getAllLocalPathsToRead`, `removeContext`, `isContextValid`, `DiskErrorException`, and constant `E_NO_SPACE_AVAILABLE`.

Control flow/state/persistence: parameterized tests run the same scenarios for three path forms. They manipulate real directories under `build/test/temp`, switch permissions read-only/read-write, create temp files, inspect allocator current index, and delete buffer directories. Scenarios include read-only first disk, missing dirs, round-robin/randomized distribution, a disk becoming read-only, many allocations, access-check parent creation behavior, absent/empty configs, no side-effect paths from qualified strings, read lookup iteration semantics, context cache removal, invalid blank path, insufficient-space diagnostics, and directory tree recovery after ancestor deletion for unknown and known sizes.

Dependencies/integration points: depends on `LocalFileSystem`, `Shell` chmod commands, platform assumptions excluding Windows for permission-sensitive cases, and Hadoop disk checker behavior.

Risks/test signals: sensitive to platform permission semantics and filesystem free space. It catches stale cached directory health, NPEs from bad config, accidental creation of literal `file:` directories, broken iterator contracts, poor error diagnostics, and recovery regressions from HADOOP-18636/HADOOP-19554.
