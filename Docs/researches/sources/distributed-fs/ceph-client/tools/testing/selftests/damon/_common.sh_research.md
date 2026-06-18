# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_common.sh

## Purpose

`_common.sh` provides a minimal shared dependency check for DAMON shell tests.

## Important APIs, Types, and Functions

It defines `check_dependencies()`, which checks effective uid and exits with `$ksft_skip` if not root.

## Control Flow

Shell tests source this file, set `ksft_skip=4`, and call `check_dependencies` before sysfs/module operations.

## State and Persistence Behavior

The script has no persistent state; it only exits on failed prerequisite.

## Dependencies and Integration Points

It depends on callers defining `ksft_skip`. It is used by `sysfs.sh`, `lru_sort.sh`, `reclaim.sh`, and similar DAMON shell tests.

## Risks and Edge Cases

If a caller forgets to define `ksft_skip`, the exit code may be empty or wrong. It checks only root, not DAMON sysfs availability.

## Test Signals

Correct use causes non-root runs to skip instead of fail.
