# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc.h

Purpose: common proc selftest helper header with raw PID/TID syscalls, string equality, strict unsigned integer parsing, and safe `readdir` handling.

Important APIs and functions: `sys_getpid()` and `sys_gettid()` call `SYS_getpid` and `SYS_gettid`; `streq()` wraps `strcmp`; `xstrtoull()` parses decimal strings and asserts no errno; `xreaddir()` clears errno and asserts `readdir` failures are real EOF.

Control flow: no standalone control flow; functions are static helpers included in multiple tests.

State and persistence: no persistent state.

Dependencies and integration: central utility for `/proc/self`, `/proc/thread-self`, `/proc/uptime`, and recursive proc read tests.

Risks and test signals: the strict parser asserts on unexpected leading characters and treats a single `0` specially. Misuse on signed or whitespace-prefixed values will abort callers.
