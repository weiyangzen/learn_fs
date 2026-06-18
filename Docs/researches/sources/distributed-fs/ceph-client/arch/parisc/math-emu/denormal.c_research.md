# sources/distributed-fs/ceph-client/arch/parisc/math-emu/denormal.c

Purpose: converts wrapped underflow results into denormalized single or double values when underflow traps are disabled, applying the requested rounding mode and reporting whether the result is inexact.

Important APIs/types/functions: `sgl_denormalize(unsigned int *sgl_opnd, boolean *inexactflag, int rmode)` and `dbl_denormalize(unsigned int *dbl_opndp1, unsigned int *dbl_opndp2, boolean *inexactflag, int rmode)`.

Control flow: each function copies the operand words, derives the true underflow exponent by subtracting `SGL_WRAP` or `DBL_WRAP`, saves the sign, and calls the corresponding macro denormalizer to shift the significand and produce guard/sticky/inexact state. If inexact, it rounds for `ROUNDPLUS`, `ROUNDMINUS`, or `ROUNDNEAREST`, restores the sign, writes the result words back, and updates `*inexactflag`.

State and dependencies: only mutates pointed-to operands and inexact flag. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and PA-RISC shift/bit macros.

Risks: correctness hinges on the wrapped exponent convention used by trap paths. Rounding after denormalization can cross back into normal range, so guard/sticky logic must match hardware. The functions do not validate operand class; callers must pass wrapped underflow results.

Test signals: underflow tests with traps disabled across all rounding modes, exact versus inexact denormal results, sign preservation for positive/negative tiny values, and comparisons against hardware or high-precision software references.
