<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h

## Purpose
Architecture adapter for invoking vDSO functions, with PowerPC register-call handling and a normal direct-call fallback elsewhere.

## Important APIs, Types, and Functions
LOADARGS_1/2/3/5, VDSO_CALL macro.

## Control Flow
On powerpc, loads the function pointer and arguments into ABI registers, branches through ctr, and normalizes error return; on other architectures expands to fn(args).

## State and Persistence
No persistent state; only inline register clobbers during calls.

## Dependencies and Integration Points
Depends on compiler support for GNU statement expressions and powerpc register asm.

## Risks and Edge Cases
Incorrect clobber/register constraints would corrupt calls only on powerpc; non-powerpc has minimal risk.

## Test Signals
vDSO tests compile and execute through VDSO_CALL on target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h -->
