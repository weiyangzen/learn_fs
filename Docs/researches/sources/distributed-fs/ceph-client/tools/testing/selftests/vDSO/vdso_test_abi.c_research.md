<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c

## Purpose
Full vDSO ABI presence and call smoke test for gettimeofday, clock_gettime/time64, clock_getres/time64, time, across a clock-id plan.

## Important APIs, Types, and Functions
vdso_test_gettimeofday, vdso_test_clock_gettime*, vdso_test_clock_getres*, vdso_test_time, VDSO_TEST_PLAN.

## Control Flow
Initializes parser, sets a 38-test kselftest plan, resolves each symbol, calls supported vDSO functions for multiple clock ids, compares clock_getres against syscall, and records pass/skip/fail per symbol/clock.

## State and Persistence
No persistent state; reads time from vDSO and syscall.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR, vdso_config symbol table, parse_vdso, syscalls for comparison, and kselftest.

## Risks and Edge Cases
Clock support varies by architecture/kernel, so many paths can skip; plan count must stay synchronized with tested cases.

## Test Signals
Pass/skip/fail lines in KTAP are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c -->
