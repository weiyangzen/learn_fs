# sources/distributed-fs/ceph-client/tools/testing/selftests/acct/acct_syscall.c

Purpose: kselftest for the `acct()` syscall, checking that process accounting logs a terminated child process.

Important APIs/types/functions: `main()` uses kselftest header/plan/result helpers, `geteuid()`, `fopen()`, `acct()`, `fork()`, `wait()`, `fseek()`, and `ftell()`.

Control flow: requires root or skips. Creates `process_log`, enables accounting to that file, forks a child, parent waits, measures file size, disables accounting, and passes if the file grew. Child falls through returning failure.

State and persistence: creates/overwrites `process_log` in the current working directory and toggles system process accounting until `acct(NULL)` is called.

Dependencies/integration: depends on kernel process accounting support, root privileges, and kselftest reporting. Built by the acct Makefile.

Risks and test signals: the code checks `errno` after `acct(filename)` without clearing it first, so stale errno could cause false error reporting. Cleanup on fork failure disables accounting but does not close the file; successful path closes it.
