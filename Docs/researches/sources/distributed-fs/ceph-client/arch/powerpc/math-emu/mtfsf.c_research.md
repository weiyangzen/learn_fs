<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c

## Purpose
Implements move to FPSCR fields from an FPR image.

## Important APIs, types, and functions
`int mtfsf(unsigned int FM, u32 *frB)` computes a field mask from `FM`, merges `frB[1]` into `__FPU_FPSCR`, clears summary bits, and recomputes VX/FEX summaries.

## Control flow
Fast paths handle `FM == 1` and `FM == 0xff`; otherwise the mask is expanded nibble-by-nibble. The resulting FPSCR preserves unmasked fields and derives summary bits from detailed exception/status and enable bits.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSF`, with exception summary semantics consumed by later FP emulation.

## Risks and edge cases
Mask expansion and summary-bit recomputation are subtle; wrong bit order changes user-visible FPSCR fields.

## Test signals
Field-selective FPSCR updates, VX/FEX summary correctness, and reserved bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c -->
