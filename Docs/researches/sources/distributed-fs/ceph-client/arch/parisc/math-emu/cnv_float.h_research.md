# sources/distributed-fs/ceph-client/arch/parisc/math-emu/cnv_float.h

Purpose: provides macro primitives for conversions among single/double floating-point and signed/unsigned fixed-point formats. It is a shared dependency for `fcnv*` files.

Important APIs/types/functions: macros cover exponent rebiasing (`Sgl_to_dbl_exponent`, `Dbl_to_sgl_exponent`), mantissa extraction/deposition, inexact tests, round-to-nearest rules, integer construction (`Int_from_*`, `Dint_from_*`, `Duint_from_*`), two-word integer arithmetic, and `Find_ms_one_bit()`.

Control flow: there are no functions; callers expand macros inline. Conversion files first classify ranges, then use these macros to shift mantissas into destination integer or float layouts, compute guard/sticky/odd bits, round according to `Rounding_mode()`, and set destination words.

State and dependencies: mutates macro arguments and uses `Fpustatus_register` via rounding-mode/status macros from `float.h`. Depends heavily on `sgl_float.h`, `dbl_float.h`, bitfield helpers from `fpbits.h`, and C integer widths.

Risks: many macros evaluate and mutate arguments multiple times and require caller-provided temporaries. Several shift expressions depend on ranges being prevalidated by callers. Parentheses are sparse because this is legacy macro code, making it easy to introduce precedence bugs.

Test signals: exhaustive boundary tests around `SGL_FX_MAX_EXP`, `DBL_FX_MAX_EXP`, zero, denormals, NaNs, infinities, half-ulp tie cases, negative-to-unsigned conversions, and every rounding mode.
