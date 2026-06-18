# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sgl_float.h

Purpose: defines the single-precision bit-manipulation API used by all PA-RISC single FP emulation routines and the single-extended format used by fused multiply-add.

Important APIs and macros: it maps generic fields to single fields (`Sgl_sign`, `Sgl_exponent`, `Sgl_mantissa`), provides tests for zero, NaN, infinity, hidden bits, signaling NaNs, and magnitude ordering, and provides mutators for signs, exponents, mantissas, infinities, largest finite values, quiet/signaling NaNs, normalization, denormalization, overflow selection, and pointer copy. The `Sglext_*` family models a 48-bit mantissa extension across two words.

Control flow: macro expansions implement inline arithmetic primitives: shifts, cross-word shifts, alignment with sticky-bit preservation, addition/subtraction with borrow/carry, XOR swapping, normalization loops, and denormalization with tininess checks.

State and persistence: no static runtime state. The header defines the source-level ABI between arithmetic files and the bit encoding from `float.h`.

Dependencies and integration: included by every `sf*.c` file, `frnd.c`, and `fmpyfadd.c`. It depends on lower-level macros and constants such as `SGL_P`, `SGL_BIAS`, `SGL_INFINITY_EXPONENT`, `Sall`, and `Deposit_*`.

Risks: macro side effects, missing braces, and operator precedence can create subtle bugs. `Sglext_denormalize` uses DBL-related constants in one range check, which deserves scrutiny against intended single-extended width. Rounding and tininess behavior are centralized here, so changes have broad blast radius.

Test signals: compile with warning-heavy configs, compare macro operations against reference IEEE encodings, test every arithmetic routine after any header change, and add targeted tests for sticky-bit alignment and denormalization boundary exponents.
