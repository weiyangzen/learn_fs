# sources/distributed-fs/ceph-client/mm/damon/tests/sysfs-kunit.h

## Purpose
This header defines a small KUnit suite for the DAMON sysfs layer, enabled by `CONFIG_DAMON_SYSFS_KUNIT_TEST`. It verifies that sysfs target objects can be converted into DAMON runtime targets and appended to a context.

## Important APIs, Types, And Functions
The suite is named `damon-sysfs`. It defines `nr_damon_targets()` to count runtime targets, `__damon_sysfs_test_get_any_pid()` to find an existing PID in a numeric range, and `damon_sysfs_test_add_targets()` as the sole test case.

The test manually allocates `struct damon_sysfs_targets`, `struct damon_sysfs_target`, `struct damon_sysfs_regions`, and `struct damon_ctx`, then calls `damon_sysfs_add_targets()`.

## Control Flow
`damon_sysfs_test_add_targets()` creates a sysfs target array with one target, assigns a found PID, creates an empty regions object, and builds a new DAMON context. It calls `damon_sysfs_add_targets()` and expects one target. Then it changes the sysfs PID to another live PID, calls `damon_sysfs_add_targets()` again, and expects two targets.

The test frees manually allocated sysfs wrappers and destroys the context at the end.

## State And Persistence
All test state is transient. The PID helper briefly obtains and releases PID references only to find candidate numeric PIDs. The actual `damon_sysfs_add_targets()` call is responsible for acquiring PID references for runtime targets.

## Dependencies And Integration Points
The test depends on `sysfs.c` static helpers being visible through inclusion. It requires KUnit and a running system with at least one PID in the probed ranges. It also relies on DAMON core context allocation and target iteration.

## Risks And Edge Cases
The PID range scan may return `-1` if no PID is found; the test does not explicitly skip in that case before assigning it, so behavior depends on `damon_sysfs_add_targets()` failing or finding later PIDs for the second scan.

The test ignores return values from `damon_sysfs_add_targets()` and only checks target counts. It does not validate error handling, PID reference cleanup, region validation, physical address target constraints, or sysfs kobject creation.

## Test Signals
This is narrow positive-path coverage for sysfs-to-runtime target addition. It gives a weak signal that `damon_sysfs_add_targets()` appends targets but does not cover the broader sysfs command or scheme machinery.
