## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellReturnCode.java

Purpose: validates FsShell exit codes and diagnostics for chmod/chown/chgrp, invalid copy sources, nonexistent glob removal, invalid default FS fallback, interrupted command execution, and owner/group argument validation.

Important APIs/types/functions: `FsShell`, `FsShellPermissions.Chown/Chgrp`, `FsCommand`, `PathData`, `CommandFactory`, `LocalFileSystemExtn`, `RawLocalFileSystemExtn`, `InterruptedIOException`, `HADOOP_SHELL_MISSING_DEFAULT_FS_WARNING_KEY`, `FS_DEFAULT_NAME_KEY`, and stderr capture through `ByteArrayOutputStream`.

Control flow: setup registers an extended local filesystem whose raw layer records owner/group changes. `testChmod`, `testChown`, and `testChgrp` create files and assert exit codes for existing paths, missing paths, and globs; helper `change` also verifies owner/group changes. Diagnostic tests check `-get` invalid source output, `-rm` with/without `-f`, and `-ls file:///` despite an invalid default FS. `testInterrupt` registers a custom command that throws `InterruptedIOException` on files and expects exit 130. Fake Chown/Chgrp classes test parser validity for user/group names, including Windows-specific spaces.

State and persistence: creates local test files, mutates static owner/group maps in the raw FS extension, captures/restores stderr, and uses static shell/configuration objects.

Dependencies/integration points: command exit-code aggregation, glob expansion, shell permissions commands, local FS owner/group APIs, default FS resolution, and interrupt mapping to shell exit code 130.

Risks and test signals: exit codes must reflect any failed argument, not just the last item. Diagnostics must avoid `null`. Argument validation differs on Windows. Static owner/group maps could leak if paths overlap, but test paths are scoped under a temp root.
