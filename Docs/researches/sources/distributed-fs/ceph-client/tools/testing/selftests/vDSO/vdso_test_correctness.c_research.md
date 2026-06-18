<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c

## Purpose
Compares vDSO time/getcpu results with syscall/vsyscall behavior for ordering and correctness.

## Important APIs, Types, and Functions
fill_function_pointers, test_clock_gettime, test_clock_gettime64, test_gettimeofday, test_time, test_getcpu, sys_* wrappers.

## Control Flow
Resolves vDSO symbols, tests supported clock ids plus invalid ids against syscall ordering/error behavior, compares timezone and time return consistency, and iterates CPU affinity to validate getcpu results.

## State and Persistence
Changes process CPU affinity during getcpu checks; no persistent files.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR, parse_vdso, vdso_config, syscalls, /proc/self/maps for x86 vsyscall detection.

## Risks and Edge Cases
Affinity loop stops at first unavailable CPU; invalid-clock errno handling must match vDSO ABI.

## Test Signals
Returns nonzero if any comparison increments nerrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c -->
