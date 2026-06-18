# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/rename_attack_test.c

Purpose: stress-tests `RESOLVE_BENEATH` and `RESOLVE_IN_ROOT` against a concurrent rename-exchange attack that attempts to make a relative path escape its starting directory.

Important APIs/functions: `setup_testdir()` creates a temporary root with `a/c` and `b`. `spawn_attack()` forks a child that continuously calls `renameat2(..., RENAME_EXCHANGE)` swapping `a/c` and `b`. `test_rename_attack()` performs 400000 open attempts against a deeply nested `c/../../...` victim path and classifies results.

Control flow: `main()` plans two tests and calls `test_rename_attack()` for `RESOLVE_BENEATH` and `RESOLVE_IN_ROOT`. Each run opens `a` as the starting dirfd, launches the rename loop, then calls `sys_openat2()` when supported or `openat()` fallback otherwise. It counts `-EAGAIN`, `-EXDEV`, other errors, successes, and escapes; any escape fails the test. The attacker is killed at the end.

State and persistence: creates a temporary directory under `/tmp` and a child process. It does not remove the temporary tree explicitly. It mutates directory names in a tight loop while the parent performs lookups.

Dependencies/integration: depends on `renameat2(RENAME_EXCHANGE)`, openat2 resolver semantics, procfs-based fd comparison from `fdequal()`, and scheduler timing. It is built with sanitizers via the Makefile.

Risks: race tests can be sensitive to CPU scheduling and sanitizer overhead. If openat2 is unsupported, the fallback openat path is expected to show vulnerability potential but the test still labels the resolver mode names; this path is primarily diagnostic.

Test signals: prints non-escape counters and a pass/fail line reporting number of escapes over 400000 runs. Any kselftest fail/error exits nonzero.
