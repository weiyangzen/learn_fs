# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tint.c

Purpose: converts a single-precision value to a signed 32-bit integer according to current rounding mode.

Important APIs/functions: `ieee754sp_tint(union ieee754sp x)` returns integer values, `ieee754si_indef()` for NaNs, and `ieee754si_overflow(xs)` for infinities/out-of-range values.

Control flow: clears exceptions, classifies/flushes, rejects NaN/inf with invalid, handles zero, permits the exact `-2^31` corner, shifts mantissas left for large exponents, otherwise extracts residue/round/sticky/odd bits and applies RN/RZ/RU/RD rounding. Post-round overflow sets invalid.

State and persistence: mutates FCR31 exception flags for invalid and inexact.

Dependencies and integration: used by CVT.W.S, ROUND/TRUNC/CEIL/FLOOR paths with rounding mode set by higher-level emulator code.

Risks and test signals: test `-2^31`, just-overflowing positives/negatives, NaN/inf invalid, fractional ties-to-even, directed rounding, tiny values, and inexact flag behavior.
