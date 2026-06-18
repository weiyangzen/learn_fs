<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c

## Purpose
This userspace helper file provides small functions for selftests to change sysctl files while optionally recording the previous value and reporting failures through the test harness.

## Important APIs, Types, and Functions
`sysctl_set()` opens a sysctl path with `fopen(path, "r+")`, optionally reads the old value with `fscanf`, compares it to the requested value, seeks to the start, and writes the new value with `fprintf`. `sysctl_set_or_fail()` wraps it and calls `PRINT_FAIL` from `test_progs.h` on error.

## Control Flow
`sysctl_set` returns `-errno` if open or write fails, `-ENOENT` if old-value reading fails, otherwise 0. It avoids writing when `old_val` is provided and already equals `new_val`. `sysctl_set_or_fail` propagates the error after logging a formatted message.

## State and Persistence
The helper mutates kernel sysctl files, so state persists outside the process until tests restore old values. If `old_val` is supplied, the caller can preserve prior configuration for cleanup.

## Dependencies and Integration Points
It depends on C stdio/errno/string APIs, local `sysctl_helpers.h`, and `test_progs.h` for reporting. It is linked into userspace BPF selftest binaries.

## Risks
The read uses `%s`, so values containing whitespace are not preserved fully. The function does not truncate after writing shorter values unless sysctl semantics handle it. Callers must restore old settings to avoid cross-test contamination.

## Test Signals
Return 0 indicates the sysctl is open and set or already correct. Nonzero return plus `PRINT_FAIL` from the wrapper signals setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c -->
