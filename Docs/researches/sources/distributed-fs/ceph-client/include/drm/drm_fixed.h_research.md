# sources/distributed-fs/ceph-client/include/drm/drm_fixed.h

Purpose: Provides fixed-point arithmetic helpers used by DRM display code for ratios, timing math, color calculations, and formatted small fixed-point values without floating point.

Important APIs, types, and functions: Defines `fixed20_12` and `dfixed_*` macros/helpers for 20.12 arithmetic; defines 32.32 constants such as `DRM_FIXED_POINT`, `DRM_FIXED_ONE`, masks, epsilon, and almost-one; implements `drm_sm2fixp()`, integer/fixed conversions, rounding/ceil helpers, `drm_fixp_msbset()`, `drm_fixp_mul()`, `drm_fixp_div()`, `drm_fixp_from_fraction()`, and `drm_fixp_exp()`. Also defines Q4 helpers `fxp_q4_from_int()`, `fxp_q4_to_int()`, `fxp_q4_to_int_roundup()`, `fxp_q4_to_frac()`, `FXP_Q4_FMT`, and `FXP_Q4_ARGS()`.

Control flow: Callers convert integer or fractional values into fixed point, perform multiplication/division with overflow-reducing shifts, and convert results back to integers or formatted Q4 output. The exponential helper iteratively sums terms until a fixed tolerance and handles negative exponents by reciprocal division.

State and persistence: Stateless inline arithmetic only. Results may become ABI-visible if used to derive mode timings or property values, but the header itself stores nothing.

Dependencies and integration points: Depends on kernel 64-bit division/math helpers and wordpart extraction. Integrated by DRM drivers and helpers that cannot use floating point in kernel code.

Risks and test signals: Risks include overflow, precision loss from shifting, division by zero, negative rounding surprises, `INT_MIN` absolute-value overflow in fraction conversion, and convergence/runtime issues in `drm_fixp_exp()`. Test positive and negative values, large operands near overflow, small fractions, rounding/ceil boundaries, zero denominators rejected by callers, and Q4 formatting.
