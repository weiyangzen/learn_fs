# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_bench.c

## Purpose
`fs_bench.c` is a Landlock filesystem benchmark. It builds a very deep directory tree with one Landlock rule per directory and repeatedly performs file creation attempts from the deepest directory to measure the cost of expensive Landlock path-walk checks. It can disable Landlock with `-L` to provide a baseline.

## Important APIs, Types, And Functions
Important functions are `usage()`, `build_directory()`, `remove_recursively()`, and `main()`. It uses `landlock_create_ruleset()`, `landlock_add_rule()`, `landlock_restrict_self()`, `LANDLOCK_CREATE_RULESET_VERSION`, filesystem access rights `LANDLOCK_ACCESS_FS_IOCTL_DEV`, `WRITE_FILE`, and `MAKE_REG`, `LANDLOCK_RULE_PATH_BENEATH`, `prctl(PR_SET_NO_NEW_PRIVS)`, `mkdirat()`, `openat()`, `unlinkat()`, `times()`, and `CLOCKS_PER_SEC`.

## Control Flow
`main()` parses `-h`, `-L`, `-d D`, and `-n N`, prints benchmark parameters, records starting CPU times, calls `build_directory()`, runs `num_iterations` `openat(curr, "file.txt", O_CREAT | O_TRUNC | O_WRONLY, 0600)` attempts, records ending CPU times, prints system/user clock deltas, closes the deepest directory FD, and removes the generated tree. `build_directory()` optionally checks Landlock ABI >= 7, creates a ruleset handling write/make/ioctl rights, walks down `depth` nested `d` directories, adding an `IOCTL_DEV`-only rule for each current directory before creating the next child, then enforces the ruleset. `remove_recursively()` opens down to the deepest parent and removes `d` directories while walking back upward.

## State, Persistence, And Dependencies
The benchmark creates a nested `d/d/...` directory tree in the current working directory and removes it at the end. When Landlock is enabled it also creates a ruleset and enforces it on the process after tree creation, which should deny `MAKE_REG`/`WRITE_FILE` at the deepest directory and make each `openat()` fail with `EACCES`. It depends on Landlock ABI 7 or newer, writable current directory, enough path depth/inodes for the requested `-d`, and CPU time accounting through `times()`.

## Integration Points
The Makefile builds this as `fs_bench` alongside the Landlock tests, but it is a benchmark rather than a kselftest harness binary. It provides performance signals for Landlock filesystem access-check refactors and can be run manually with different depths and iteration counts.

## Risks
The default `-d 10000` creates a very deep tree and can be slow or fail on filesystem/path traversal limits. The check `if (fd == 0)` in the Landlock-enabled loop appears intended to detect success but only treats descriptor 0 as success; successful opens returning any other non-negative FD would be closed without error, weakening the assertion. If an error other than `EACCES` follows a prior syscall that left `errno` unchanged, diagnostics could be misleading. Cleanup assumes the expected directory shape and can fail if interrupted or run from a restricted/unexpected directory.

## Test Signals
Benchmark output reports system/user clocks and clocks per second. With Landlock enabled, every file creation should fail with `EACCES`; without `-L`, successful opens provide the baseline. With `-L`, successful opens provide the baseline. Cleanup success leaves no nested `d` tree behind.
