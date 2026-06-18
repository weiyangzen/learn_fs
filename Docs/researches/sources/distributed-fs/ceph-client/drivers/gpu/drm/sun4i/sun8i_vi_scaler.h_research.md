# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.h

## Purpose

`sun8i_vi_scaler.h` defines VSU scaler address constants, scale limits, register offsets, control bits, DE3+ scale-mode constants, edge/angle helper macros, and public setup/enable APIs.

## Important APIs, Types, and Definitions

- Unit bases and sizes: `DE2_VI_SCALER_UNIT_BASE/SIZE`, `DE3_VI_SCALER_UNIT_BASE/SIZE`, and `DE33_VI_SCALER_UNIT_BASE`.
- Scale constants: min/max scale, 20-bit scale/phase fractional widths, coefficient count of 32, and size packing macro.
- Register macros for VSU control, DE3+ scale mode and thresholds, luma/chroma input sizes, steps, phases, and coefficient banks.
- Control bits: `SUN8I_SCALER_VSU_CTRL_EN` and `COEFF_RDY`.
- Scale modes: UI, normal, and edge-directed scaling.
- `sun8i_vi_scaler_enable()` and `sun8i_vi_scaler_setup()` public APIs.

## Control Flow and State

The header defines the hardware register contract used by `sun8i_vi_scaler.c` and layer code. It stores no software state, but its constants directly determine atomic scale bounds and register address computation.

## Dependencies and Integration Points

It includes DRM FourCC definitions and `sun8i_mixer.h`. It integrates with VI layer atomic checks, DE33 UI scaling, and mixer type/channel configuration.

## Risks and Edge Cases

- Scale limits assume DRM 16.16 rectangles and hardware 20-bit fields.
- `SUN50I_SCALER_VSU_*_SHIFT()` masks use `& 0xF` after shifting; if these unused macros become used, reviewers should confirm the intended mask position.
- Register-bank offsets must match hardware across DE2, DE3, and DE33.

## Test Signals

Compile tests should catch prototype drift. Register tests should validate VSU offsets and coefficient bank spacing. Atomic tests should verify accepted scale ranges match hardware behavior.
