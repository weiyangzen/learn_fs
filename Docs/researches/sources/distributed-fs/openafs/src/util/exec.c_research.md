# sources/distributed-fs/openafs/src/util/exec.c

Purpose: Implements helper logic for re-executing an alternate variant of the current program, for example a DAFS versus non-DAFS or architecture-specific executable.

Important APIs and functions: Public `afs_exec_alt(int argc, char **argv, const char *prefix, const char *suffix)` constructs an alternate `argv[0]` by inserting a prefix before the basename and appending a suffix. Private `construct_alt()` performs the basename manipulation.

Control flow and state: `afs_exec_alt()` normalizes null prefix/suffix to empty strings, rejects an empty prefix plus empty suffix with `EINVAL`, allocates a new argv vector, duplicates all arguments, and calls `execvp()`. On success it never returns. On failure it preserves `errno`, frees duplicated arguments except the alternate program string, and returns that allocated string for caller diagnostics.

Dependencies and integration: Uses roken/libc memory and process APIs. This is useful in command-line tools that can delegate to sibling binaries without manually reconstructing command lines.

Risks and test signals: The function assumes `argc` and `argv` are valid and that `argv[0]` is non-null. Callers must free the returned alternate program name on failure. There are no direct tests in this subset; behavior is usually tested through tools that attempt alternate executable dispatch.
