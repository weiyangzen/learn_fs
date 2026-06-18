<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c

Purpose: Implements IEEE754-2008 `CLASS.D` classification for double precision values.

Important APIs/types/functions: `ieee754dp_2008class(union ieee754dp x)` returns the 10-bit MIPS class mask.

Control flow: Decodes the operand class and sign, then maps sNaN, qNaN, negative/positive infinity, normal, denormal, and zero to the specified mask bits.

State and persistence: No persistent state; uses decode macros and may log unknown classes.

Dependencies and integration: Called by `cp1emu.c` for R6 `CLASS.D`.

Risks: Unexpected class values return zero after `pr_err`, which would silently report no class.

Test signals: Known bit patterns for NaN, infinities, signed zeros, normals, and denormals should produce the MIPS-defined class mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c -->
