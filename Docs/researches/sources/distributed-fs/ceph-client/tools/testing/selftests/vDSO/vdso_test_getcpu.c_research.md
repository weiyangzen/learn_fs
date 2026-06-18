<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c

## Purpose
Simple vDSO getcpu symbol lookup and call smoke test.

## Important APIs, Types, and Functions
main, getauxval, vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Resolves the configured getcpu symbol, calls it with cpu/node outputs, prints the location, and maps absence/failure to kselftest skip/fail.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR and architecture vDSO getcpu export.

## Risks and Edge Cases
Only validates call success, not cross-check against syscall.

## Test Signals
Pass is vDSO getcpu returning 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c -->
