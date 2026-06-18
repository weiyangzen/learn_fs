# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/custom_float.h

## Purpose

`custom_float.h` declares a helper that converts DC fixed-point values into hardware-specific custom floating-point register encodings. It is used where display hardware exposes non-IEEE float-like fields.

## Important APIs, Types, And Functions

The single API is `convert_to_custom_float_format(struct fixed31_32 value, const struct custom_float_format *format, uint32_t *result)`. Inputs are a fixed31.32 value and a format description; output is the encoded register value.

## Control Flow

Callers provide a value and target format, then the implementation computes sign/exponent/mantissa according to `custom_float_format` and returns success/failure. The header itself has no executable logic.

## State And Persistence Behavior

No state is stored. The only effect is writing the encoded value through `result`. Hardware persistence occurs later when callers write that result to registers.

## Dependencies And Integration Points

It includes `bw_fixed.h`, `hw_shared.h`, and `opp.h`, which provide fixed-point and format definitions. It integrates with OPP/DPP color, scaling, or other programming paths that require custom register encodings.

## Risks And Edge Cases

Encoding is sensitive to rounding, sign handling, exponent limits, zero, saturation, and format bit widths. A mismatched `custom_float_format` can produce valid-looking but wrong register values. Callers must handle a false return and avoid programming uninitialized `result`.

## Test Signals

Unit tests should cover zero, negative values, smallest/largest representable values, rounding boundaries, overflow/saturation, and each hardware format. Visual color/brightness regressions can indicate conversion errors in integration tests.
