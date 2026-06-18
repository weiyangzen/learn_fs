# File Research: sources/cow-pools/bcachefs-tools/fs/debug/tests.h

## Purpose

Declares the optional test harness API.

## Main Interfaces

When `CONFIG_BCACHEFS_TESTS` is enabled, exports:

- `int bch2_btree_perf_test(struct bch_fs *, const char *, u64, unsigned);`

When tests are disabled, it exports no fallback function.

## Notes

This header keeps sysfs test invocation conditional and avoids exposing test code in non-test builds.
