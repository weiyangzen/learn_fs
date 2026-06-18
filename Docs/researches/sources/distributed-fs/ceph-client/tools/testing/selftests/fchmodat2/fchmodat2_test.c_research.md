# sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/fchmodat2_test.c

## Purpose
Tests `fchmodat2(2)` behavior on regular files and symlinks, especially `AT_SYMLINK_NOFOLLOW`.

## Important APIs, Types, And Functions
Uses raw syscall wrapper `sys_fchmodat2()`, `mkdtemp`, `openat`, `symlinkat`, `fstatat(AT_SYMLINK_NOFOLLOW)`, `unlinkat`, and kselftest helpers. Structures/functions include `struct testdir`, `setup_testdir()`, `cleanup_testdir()`, `expect_mode()`, `test_regfile()`, and `test_symlink()`.

## Control Flow
Each test creates a temporary directory containing `regfile` and `symlink`. The regular-file test chmods with no flags and with `AT_SYMLINK_NOFOLLOW`, checking target modes. The symlink test chmods through the symlink, checks target changed while symlink mode remains default, then tries nofollow chmod on the symlink itself and passes or skips depending on filesystem support.

## State And Persistence
Creates `/tmp/ksft-fchmodat2.XXXXXX`, a file, and a symlink, then removes them.

## Dependencies And Integration Points
Requires `__NR_fchmodat2`, filesystem support for symlink mode changes for full pass, and kselftest.

## Risks
The symlink nofollow path can legitimately fail on filesystems such as xfs or btrfs, so the test skips that case. Cleanup error path references `testdir->dfd` before assignment in one branch, but fatal setup failure exits.

## Test Signals
Two planned results: regular file pass if modes become `0100640` then `0100600`; symlink pass or skip depending on nofollow support.
