# sources/distributed-fs/ceph-client/arch/parisc/math-emu/frnd.c

Purpose: implements floating-point round-to-integer for single and double precision via `sgl_frnd` and `dbl_frnd`. Quad precision is documented as unimplemented elsewhere.

Important APIs and types: both functions accept a source pointer, unused null pointer, destination pointer, and FP status pointer. They use `Sgl_*`, `Dbl_*`, and conversion helper macros from `cnv_float.h` to inspect inexact, round, and sticky bits.

Control flow: each routine first returns infinities and quiet NaNs, quieting signaling NaNs or trapping invalid if configured. If the unbiased exponent already covers all fraction bits, it returns the input unchanged. Otherwise it shifts the significand down to an integer, checks discarded bits, rounds according to the current mode, shifts back, and rebuilds the exponent. Values with absolute value below one become signed zero or signed one depending on rounding mode and half-way rules.

State and persistence: no persistent local state. The destination receives the rounded FP encoding; `Set_invalidflag` and `Set_inexactflag` may mutate the status register unless traps return early.

Dependencies and integration: called from `fpudispatch.c` class 0 `FRND`/`FRMD` decode for single and double formats. Depends on the same status/trap conventions as other math-emu routines.

Risks: half-way handling for `ROUNDNEAREST` depends on correct sticky-bit macros, and negative near-zero values rely on preserving the sign while zeroing exponent/mantissa. Large exponents must avoid unnecessary shifts.

Test signals: cover positive and negative fractions below one, exact integers, half-way cases, odd/even ties, all rounding modes, signaling NaNs, quiet NaNs, infinities, and inexact trap behavior.
