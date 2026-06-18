# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/short_splice_read.sh

## Purpose
Regression test for splice handling on procfs/sysfs pseudo-files, including short reads and removed fallback behavior.

## Important APIs, types, and functions
Defines `expect_success()`, `expect_failure()`, `do_splice()`, and `test_splice()`. Uses helper `splice_read`, `cat`, `grep`, `cut`, and `modprobe test_module`.

## Control flow
`test_splice()` reads a file normally, derives full content and first two characters, then compares helper-spliced 4096-byte and 2-byte reads. The script expects splice failure for `/proc/<pid>/limits` and `/proc/<pid>/comm`, success for selected `/proc/sys/*` files, loads `test_module` if needed, and expects success for sysfs attribute and binary attribute files under `/sys/module/test_module`.

## State and persistence
Maintains aggregate `ret`; may load `test_module`. No files are written.

## Dependencies and integration points
Requires procfs, sysfs, `test_module`, and the `splice_read` helper built by the Makefile.

## Risks
The comments mention historical behavior changes after splice fallback removal; expectations are specific to current kernel behavior. File contents can change during comparison, especially proc/sys values. Requires module loading for sysfs checks.

## Test signals
Each case reports `ok` or `FAIL` to stderr; final exit is the accumulated failure count.
