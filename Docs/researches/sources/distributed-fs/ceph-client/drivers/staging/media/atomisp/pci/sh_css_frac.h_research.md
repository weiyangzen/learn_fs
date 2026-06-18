# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_frac.h

Purpose: `sh_css_frac.h` provides small fixed-point fitting helpers for converting 16-bit host-side signed and unsigned coefficients into the ISP vector element precision. It centralizes the shifts and clamp ranges used by parameter encoders such as MACC table conversion.

Important APIs/types/functions: macros derive signed and unsigned register bit counts from `ISP_VEC_ELEMBITS`, define host-to-ISP shift values, fraction fitting macros, and signed/unsigned ISP min/max ranges. `sDIGIT_FITTING(int v, int a, int b)` right-shifts a signed value from 16-bit precision into ISP precision and clamps it. `uDIGIT_FITTING(unsigned int v, int a, int b)` does the same for unsigned coefficients.

Control flow and state: both helpers are pure inline functions with no persistent state. They compute `fit_shift`, apply the base shift, optionally apply additional fractional-bit reduction, and clamp the result with `clamp_t()`.

Dependencies and integration: it includes `<linux/minmax.h>` and `mamoiada_params.h`, which supplies `ISP_VEC_ELEMBITS`. `sh_css_params.c` uses `sDIGIT_FITTING()` when converting MACC coefficients for ISP pipe version 1. The same formulas must remain aligned with firmware expectations for vector element width.

Risks: the macros assume sensible `a` and `b` values; a negative or unexpectedly large shift count would be undefined in C. Precision loss is deliberate but easy to misapply if callers pass fraction bit counts for a different source format. The signed minimum uses `1 << uISP_REG_BIT`, so integer width and shift validity depend on `ISP_VEC_ELEMBITS`.

Test signals: unit coverage should feed boundary values, negative signed values, maximum unsigned values, and combinations where `fit_shift` is positive, zero, and negative. Parameter tests should compare packed MACC values against known firmware reference tables.
