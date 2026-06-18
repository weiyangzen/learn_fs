<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c

## Purpose
Nolibc-compatible x86 standalone smoke test for vDSO gettimeofday symbol lookup and call.

## Important APIs, Types, and Functions
main, getauxval(AT_SYSINFO_EHDR), vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Gets the vDSO base, resolves gettimeofday for the architecture table, calls it, prints the result, and returns skip/fail/pass via kselftest codes.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Built specially with nolibc flags on x86 and links parse_vdso.c.

## Risks and Edge Cases
Only tests a single symbol and skips when absent; output time is informational.

## Test Signals
Pass is ret==0 from the vDSO gettimeofday call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c -->
