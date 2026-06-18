<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c

## Purpose
Standalone vDSO gettimeofday smoke test using the shared parser and architecture symbol table.

## Important APIs, Types, and Functions
main, getauxval, vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Gets AT_SYSINFO_EHDR, resolves gettimeofday, calls it, prints seconds/useconds, and returns kselftest skip/fail/pass.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Depends on parse_vdso, vdso_config, vdso_call, and kselftest.

## Risks and Edge Cases
Only covers one symbol and does not compare against syscall.

## Test Signals
Pass is a zero return from vDSO gettimeofday.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c -->
