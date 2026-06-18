# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.c

Purpose: this file converts SPL fixed31_32 values into a caller-specified compact custom floating-point bit layout. It is used by scaler programming paths that need register encodings with configurable mantissa, exponent, and optional sign bits.

Important functions and control flow: `spl_convert_to_custom_float_format()` is the public entry point. It calls `spl_build_custom_float()` to normalize a fixed-point value, derive sign, mantissa, and exponent, then calls `spl_setup_custom_float()` to pack fields into a `uint32_t`. Zero returns all fields zero. Negative values are converted to magnitude and only preserve negativity if the format supports `sign`. Values below one are left-shifted until normalized, with underflow producing zero exponent/mantissa. Large values are right-shifted until they fit below the maximum mantissa range. Packing copies mantissa bits first, exponent bits after them, and sign after exponent.

State and persistence: there is no static mutable state and no allocation. The function mutates only caller-provided out parameters and returns `true` even for clamped/underflow-style cases.

Dependencies and integration: it depends on `spl_debug.h`, `spl_custom_float.h`, and fixed-point arithmetic helpers (`spl_fixpt_*`). `dc_spl.c` uses it for EASF matrix coefficient register fields.

Risks and tests: the format fields drive shifts such as `1 << (bits + 1)`, so invalid or oversized bit counts can overflow C integer shifts. Verification masks assert and clamp if mantissa/exponent exceed masks, but the API does not report these as failures. Negative input with `format->sign == false` silently becomes nonnegative. Tests should cover zero, positive/negative values, underflow below exponent range, high values requiring exponent growth, no-sign formats, maximum mantissa/exponent boundaries, and exact bit packing for known fixed-point inputs.
