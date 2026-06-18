# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestStat.java

Purpose: tests Hadoop's shell-backed `Stat` parser and execution wrapper for Linux/FreeBSD output, symlink handling, sticky bits, locale environment, and real local symlink status.

Important APIs/types/functions: `Stat`, `parseExecResult`, `getFileStatusForTesting`, `getFileStatus`, `FileStatus`, `FileSystem.enableSymlinks`, `createSymlink`, and `Stat.isAvailable`.

Control flow/state/persistence: a static `Stat` is initialized for `/dummypath`. Inner `StatOutput` feeds canned command output for missing paths, directories, files, symlinks, and sticky directories and asserts parsed status flags. Runtime tests assume `stat` availability, expect missing path failure, assert `LANG=C`, create a local directory and symlink, and compare status of target vs link.

Dependencies/integration points: depends on OS-specific `stat` output formats, symlink support, local FS, and locale-controlled command execution.

Risks/test signals: catches parser drift across GNU/BSD outputs, symlink-vs-target confusion, sticky-bit parsing errors, and missing locale isolation that could localize command output.
