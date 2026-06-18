<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c

## Purpose
Implements double-precision fused-style multiply-add emulation for `frA * frC + frB`.

## Important APIs, types, and functions
`int fmadd(void *frD, void *frA, void *frB, void *frC)` uses soft-fp double declarations, `FP_MUL_D`, `FP_ADD_D`, and `__FP_PACK_D`.

## Control flow
Operands are unpacked, invalid multiply zero-by-infinity is flagged, intermediate `T=A*C` is computed, opposite-sign infinities between `T` and `B` raise `EFLAG_VXISI`, then `T+B` is packed.

## State and persistence behavior
Destination FPR image and exception flags are updated.

## Dependencies and integration points
Called by `do_mathemu` for `FMADD`.

## Risks and edge cases
The implementation uses separate multiply then add macros, so exact fused-rounding semantics depend on soft-fp macro behavior. Invalid infinity cases are explicitly handled.

## Test signals
Result bits and VXIMZ/VXISI exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c -->
