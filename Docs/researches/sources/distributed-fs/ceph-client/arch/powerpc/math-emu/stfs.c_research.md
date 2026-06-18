<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c

## Purpose
Implements emulated single-precision floating store, narrowing a double-format FPR image to a float in user memory.

## Important APIs, types, and functions
`int stfs(void *frS, void *ea)` uses `FP_UNPACK_DP`, `FP_CONV(S, D, ...)`, `_FP_PACK_CANONICAL`, `_FP_PACK_RAW_1_P`, and `copy_to_user`.

## Control flow
The source double is converted to single precision. If there are no trapping exceptions, the raw float is copied to user memory; otherwise the store is suppressed and exception flags are returned.

## State and persistence behavior
User memory is changed on successful non-trapping conversion. FPSCR changes are recorded by caller from returned exceptions.

## Dependencies and integration points
Dispatched for `STFS`, `STFSU`, `STFSX`, and `STFSUX`.

## Risks and edge cases
Trap-enabled exceptions must prevent memory writes. Narrowing conversion, NaN packing, and user faults are key risks.

## Test signals
Expected float bytes in user memory and correct exception/fault returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c -->
