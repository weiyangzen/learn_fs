# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.h

## Purpose

`sun8i_ui_scaler.h` declares UI scaler limits, register offsets, control bits, size encoding, and setup/enable functions for the Allwinner GSU scaler.

## Important APIs, Types, and Definitions

- `DE2_UI_SCALER_UNIT_SIZE` and `DE3_UI_SCALER_UNIT_SIZE`: per-unit address spacing.
- `SUN8I_UI_SCALER_SCALE_MIN` / `SCALE_MAX`: atomic scaling bounds expressed for DRM 16.16 inputs.
- `SUN8I_UI_SCALER_SCALE_FRAC` and `PHASE_FRAC`: hardware fractional widths.
- `SUN8I_SCALER_GSU_*`: control, size, step, phase, and horizontal coefficient register macros.
- `SUN8I_SCALER_GSU_CTRL_EN` and `COEFF_RDY`: control bits.
- `sun8i_ui_scaler_enable()` and `sun8i_ui_scaler_setup()`: public scaler controls.

## Control Flow and State

The header is consumed by the UI layer implementation. It defines register computations from a scaler base; the C file computes that base and writes the registers. No runtime state is declared here beyond the implicit hardware state encoded by the macros.

## Dependencies and Integration Points

It includes `sun8i_mixer.h` for `struct sun8i_layer` and mixer configuration. The scale bounds are used by DRM atomic plane checks in `sun8i_ui_layer.c`.

## Risks and Edge Cases

- The scale bounds and fractional constants must remain consistent with DRM's 16.16 source rectangles and the hardware's 20-bit scaler fields.
- Register macros assume valid base addresses and coefficient indices.
- The header lacks an include guard comment with the symbol name but is otherwise guarded.

## Test Signals

Compile and static analysis should catch prototype drift. Unit-style tests or register traces should cover register offset calculations and scale-bound acceptance/rejection in atomic checks.
