# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestPathData.java

Purpose: JUnit 5 tests for `PathData`, the shell path wrapper used by Hadoop FS shell commands. It verifies construction from strings/URIs, filesystem binding, directory listing string forms, glob expansion, local `File` conversion, Windows path handling, unreadable directory failures, and preservation of original path text in cases where `Path` normalizes URIs.

Important APIs/types/functions: `PathData(String, Configuration)`, `PathData.expandAsGlob`, `PathData.getDirectoryContents`, `PathData.toFile`, `FileSystem.getLocal`, `FileSystem.setDefaultUri`, `FsPermission`, `Shell.WINDOWS`, `PlatformAssumptions.assumeWindows`, and helpers `checkPathData` and `sortedString`.

Control flow: `initialize` creates a local test root, strips the scheme from the qualified root so shell paths remain absolute local paths, sets the working directory, and creates `d1`/`d2` fixtures. Tests then instantiate `PathData` against relative, absolute, qualified, current-directory, and Windows-style inputs. Glob tests assert returned `PathData.toString()` values, including relative backtracking from `d1` to `../d2/*`. Cleanup deletes the root and closes the filesystem.

State/persistence: Persistent state is limited to temporary local filesystem content under `GenericTestUtils.getTestDir("testPD")`; permissions are temporarily changed to `000` for one unreadable-directory test and restored before cleanup. The test mutates `conf` default URI and local FS working directory.

Dependencies/integration: Integrates `PathData` with Hadoop `LocalFileSystem`, Hadoop `Path`, shell globbing, path qualification, and platform-specific Windows parsing. It is an integration-style unit test because real local FS state and permissions are used.

Risks: The unreadable-directory test depends on permission behavior and may be weak on platforms/filesystems that do not enforce POSIX bits. Windows tests are gated by assumptions. The `file:///tmp` assertion explicitly tracks current `Path` URI normalization and may need updates if `Path` behavior changes.

Test signals: Assertions cover exact string preservation, `stat` existence and directory status, sorted directory contents, glob result ordering-independent equality, `IOException` on invalid/unreadable paths, and platform-specific raw Windows `File` conversion.
