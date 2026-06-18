<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c

Purpose: Compares two IEEE754 double precision values for MIPS compare predicates.

Important APIs/types/functions: `ieee754dp_cmp(x, y, cmp, sig)` tests comparison bitmasks such as unordered, equal, less-than, and greater-than.

Control flow: Clears exceptions, flushes denormals, sets invalid for signaling comparisons or sNaNs, returns unordered predicate for NaNs, otherwise transforms signed bit patterns into comparable signed magnitudes and tests requested predicate bits.

State and persistence: Updates `ieee754_csr` invalid operation when required.

Dependencies and integration: Used by `cp1emu.c` for old and R6 double compare instructions.

Risks: Signed zero equality and negative ordering depend on the bit transformation.

Test signals: Compare tests should include qNaN/sNaN with quiet/signaling predicates, -0 vs +0, negative ordering, and unordered predicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c -->
