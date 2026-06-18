# sources/distributed-fs/ceph-client/arch/microblaze/lib/udivsi3.S

Purpose: provides unsigned 32-bit divide helper `__udivsi3`.

Important APIs and state: arguments are r5 dividend and r6 divisor despite a misleading comment; result is r3. Saves r29-r31.

Control flow: zero divisor/dividend returns 0. Equal operands return 1. If divisor is greater than dividend, returns 0. Otherwise a shift/subtract loop builds quotient.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned division and exported to modules.

Risks and test signals: comments are inconsistent; behavior should be verified against ABI. Division by zero returns 0. Test 0, equal, divisor larger, high-bit unsigned operands, and random comparisons against C division.
