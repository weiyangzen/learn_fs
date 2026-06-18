# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWinUtils.java

Purpose: Windows-only integration tests for Hadoop's `winutils.exe` helper commands. The file validates filesystem permissions, ownership, symlinks/readlink behavior, group lookup, and Windows job/task creation through `Shell.execCommand()`.

Important APIs/types/functions: `setUp()` calls `assumeWindows()`, creates `TEST_DIR`, and resolves `Shell.getWinUtilsPath()`. Helpers include `requireWinutils()`, `writeFile()`, `readFile()`, `chmod()`, `chmodR()`, `ls()`, `lsF()`, `assertPermissions()`, `testChmodInternal()`, `testNewFileChmodInternal()`, `testChmodInternalR()`, `chown()`, and `assertOwners()`. Test methods cover `ls`, `groups`, `chmod`, directory permission behavior, `chown`, symlink rejection, `readlink`, and task creation with resource limits.

Control flow: Each test shells out to `winutils` with a temporary file tree, then parses command output or filesystem side effects. Permission tests set ACL-like modes and verify read/write/execute failures or formatted `ls` permissions. Recursive chmod constructs nested directories/files and checks directory execute handling. Task tests create command scripts or direct commands, then assert output files/strings or expected `Shell.ExitCodeException` codes for bad parameters and resource-limit failures.

State and persistence behavior: Test state is under a per-class temp directory from `GenericTestUtils`; `tearDown()` deletes it with `FileUtil.fullyDelete()`. The tests mutate real Windows ACLs, owner/group metadata, symlinks, and scheduled/job-object behavior. Some assertions rely on Windows-specific semantics, such as deletion succeeding without parent write permission and traverse-check bypassing execute permission.

Dependencies and integration points: Depends on `Shell`, `FileUtil`, Commons IO `FileUtils`, AssertJ, JUnit timeouts, and the native `winutils.exe` binary. It is a broad integration gate for Hadoop-on-Windows compatibility and native helper packaging.

Risks: Platform and environment sensitivity is high: tests require Windows, functional `winutils.exe`, appropriate privileges for symlink/chown/task operations, and localized group names matching expectations. The test parses command output with simple delimiters, so output format changes in `winutils` are breaking. Some resource-limit checks depend on Java command availability and OS behavior.

Test signals: Successful command output tokens, exact permission strings, expected access-denied IOExceptions, owner/group formatted values, symlink path echoes, `readlink` exit code `1` for invalid inputs, task proof-file creation, and exit code `1639` for bad task parameters provide coverage.
