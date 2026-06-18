# sources/distributed-fs/ceph-client/arch/m68k/lib/udivsi3.S

## Purpose
Provides the exported `__udivsi3` unsigned 32-bit division helper for m68k configurations that need libgcc-style integer division support inside the kernel, especially CPUs without native full-width multiply/divide helpers.

## APIs, Flow, And State
The single public symbol is `__udivsi3`, exported with `EXPORT_SYMBOL`. Arguments are stack-passed dividend/divisor values and the quotient is returned in `d0`. Classic 680x0 code preserves `d2`, handles small divisors with two `divu` 16-bit operations, and handles large divisors by right-shifting dividend/divisor until the divisor fits in 16 bits, computing a tentative quotient, multiplying back, and correcting an overestimate by one. ColdFire builds use a 32-iteration non-restoring division algorithm over `(p,a)` in `d2:d0`, preserving `d2-d4` through a stack frame.

## Dependencies And Integration
Depends on assembler preprocessor label/register prefix macros and `<linux/export.h>`. It is selected by the m68k lib Makefile for `CONFIG_CPU_HAS_NO_MULDIV64` and is called by compiler-generated unsigned division sequences and by `__umodsi3`.

## Risks And Test Signals
Division-by-zero behavior is not guarded here and follows CPU/compiler ABI expectations. The highest-risk logic is quotient correction for large divisors and ColdFire carry handling. Test signals are m68k kernel builds, arithmetic selftests or boot paths using generated unsigned division, and modulo correctness through `__umodsi3`.
