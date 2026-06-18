# sources/distributed-fs/ceph-client/arch/parisc/math-emu/hppa.h

Purpose: supplies low-level double-word shift macros used by PA-RISC floating-point emulation headers.

Important APIs: `Shiftdouble(left, right, amount, dest)` handles constant shifts between two 32-bit words. `Variableshiftdouble` and `Variable_shift_double` handle variable shifts below 32 bits; the former masks the left operand's high bit, while the latter uses the raw left word.

Control flow: macro-only, expanding into one assignment or a small `if` sequence. These helpers are used to move bits between significand words, extension words, and guard/sticky accumulators during normalization, alignment, rounding, and denormalization.

State and persistence: no state is retained. The macros mutate only the destination expression supplied by callers.

Dependencies and integration: included by `float.h` or format-specific headers. `sgl_float.h`, `dbl_float.h`, arithmetic routines, and fused multiply-add code depend on these macros for exact cross-word shifts.

Risks: callers must honor the documented shift ranges; zero or 32 in the wrong macro can produce undefined behavior. Because these are macros, side-effect arguments can be dangerous. `Variableshiftdouble` and `Variable_shift_double` differ subtly in high-bit treatment.

Test signals: verify all supported shift amounts for representative pairs, especially amount 1, 4, 8, 24, 28, 31, and variable amount zero. Compare results against a 64-bit reference model in normalization and right-alignment cases.
