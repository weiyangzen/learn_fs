# sources/distributed-fs/ceph-client/arch/xtensa/lib/divsi3.S

Purpose: Implements exported signed 32-bit division helper `__divsi3`.

Important APIs, types, and functions: `__divsi3`, hardware `quos` path, software absolute-value/normalize/subtract loop, `do_nsau`, loop-option macros, `ill` plus `DIV0` marker, and `EXPORT_SYMBOL`.

Control flow: Uses hardware divide when available. Otherwise computes sign, converts operands to unsigned magnitudes, handles divisor 0/1 and dividend<divisor special cases, performs shift-subtract division, reapplies sign, and triggers an illegal instruction with a marker for divide-by-zero.

State and persistence: Register-only arithmetic; divide-by-zero transfers control to exception handling.

Dependencies and integration: Compiler-emitted signed division, `traps.c` divide-by-zero recognition, and Xtensa core feature macros for DIV32/NSA/LOOPS.

Risks: Software path correctness across `INT_MIN`, divisor zero, and normalization; marker must remain recognizable by `check_div0()`.

Test signals: Signed division tests including positive/negative pairs, `INT_MIN / -1`, divisor one, divisor zero trap, and builds without DIV32/NSA/LOOPS.
