<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c

Purpose: Implements double precision maximum and maximum-by-absolute-value operations for MIPS R6.

Important APIs/types/functions: `ieee754dp_fmax(x, y)` and `ieee754dp_fmaxa(x, y)`.

Control flow: Handles sNaN/qNaN precedence, prefers numeric operands over qNaNs, handles infinities and signed zeros, normalizes denormals, then compares signs, exponents, and mantissas. `fmaxa` compares magnitude and resolves ties by sign.

State and persistence: Clears and updates `ieee754_csr` for NaN exceptions.

Dependencies and integration: Called by `cp1emu.c` for `MAX.D` and `MAXA.D`.

Risks: Signed-zero and NaN selection differ from simple greater-than comparisons. File comments mention MIN/MINA wording despite implementing MAX/MAXA.

Test signals: Cover qNaN/sNaN, numeric-vs-NaN, +/-0, +/-inf, equal magnitude opposite signs, denormals, and normal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c -->
