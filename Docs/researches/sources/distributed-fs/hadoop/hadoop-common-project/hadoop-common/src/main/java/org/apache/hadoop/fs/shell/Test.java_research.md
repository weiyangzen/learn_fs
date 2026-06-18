# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Test.java

Purpose: implements `-test`, a shell-style predicate command whose result is conveyed by exit status.

Important APIs and types: `processOptions()`, `processPath()`, `testAccess()`, and `processNonexistentPath()`. Supported flags are `-e`, `-d`, `-f`, `-s`, `-z`, `-w`, and `-r`.

Control flow: option parsing requires exactly one flag and one path. Existing paths are evaluated against status or `fs.access()` for read/write. A failed predicate or nonexistent path sets `exitCode = 1`; success leaves the inherited success code.

State and persistence: no mutation. State is the selected flag and exit code.

Dependencies and integration: uses `PathData`, `FsAction`, and catches `AccessControlException`/`FileNotFoundException` for access probes.

Risks: only one predicate can be tested per invocation. Access checks depend on filesystem `access()` implementation. Nonexistent path does not print an error through `processNonexistentPath()`, matching test-style semantics.

Test signals: cover every flag, no flag, multiple flags, nonexistent path, access granted/denied, file/directory type checks, zero/nonzero sizes, and exit-code-only behavior.
