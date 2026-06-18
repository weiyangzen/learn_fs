# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.c

## Purpose

`sun8i_vi_scaler.c` programs the VSU scaler used by Allwinner VI layers, and by DE33 UI layers for RGB scaling. It provides filter coefficient tables, scaler base selection for DE2/DE3/DE33, coefficient selection, enable control, scale mode selection, luma/chroma size and step programming, chroma phase adjustment for YUV420, and coefficient loading.

## Important APIs, Types, and Functions

- Coefficient tables: `lan3coefftab32_left/right`, `lan2coefftab32`, `bicubic8coefftab32_left/right`, and `bicubic4coefftab32`.
- `sun8i_vi_scaler_base()`: selects scaler base from mixer type and layer channel.
- `sun8i_vi_scaler_coef_index()`: maps scale step to one of 15 coefficient blocks.
- `sun8i_vi_scaler_set_coeff()`: chooses luma/chroma coefficient families based on subsampling and writes Y horizontal, Y vertical, chroma horizontal, and chroma vertical coefficient registers.
- `sun8i_vi_scaler_enable(struct sun8i_layer *layer, bool enable)`: writes VSU enable and coefficient-ready bits.
- `sun8i_vi_scaler_setup(...)`: converts DRM scale/phase values, selects DE3+ scale mode, writes sizes, steps, phases, chroma parameters, and coefficients.

## Control Flow

Layer code computes dimensions and 16.16 scale/phase values, then calls setup. Setup derives the hardware base, shifts scale and phase into 20-bit fractional units, packs input/output sizes, computes chroma phases, selects DE3+ UI or normal scale mode depending on subsampling, writes luma output/input/step/phase registers, writes chroma input size and scaled steps using format `hsub`/`vsub`, writes chroma phases, and calls `sun8i_vi_scaler_set_coeff()`. Enable then toggles the VSU control register.

## State and Persistence Behavior

Software state is static read-only coefficient data only. Hardware scaler registers persist per channel until overwritten or disabled. `sun8i_vi_scaler_enable(false)` clears the control register but does not clear size, phase, or coefficient registers.

## Dependencies and Integration Points

The file depends on `sun8i_vi_scaler.h`, `drm_format_info` subsampling fields, mixer configuration (`de_type`, channel), regmap writes, and layer code in both `sun8i_vi_layer.c` and DE33 paths in `sun8i_ui_layer.c`.

## Risks and Edge Cases

- `sun8i_vi_scaler_set_coeff()` accepts `vstep` but uses `hstep` again for vertical coefficient selection. If vertical and horizontal scale ratios differ, vertical filters may be selected from the wrong ratio.
- Y horizontal coefficients are always loaded from lanczos-like tables even when chroma/subsampled paths select bicubic tables; this appears intentional for luma but should be validated.
- YUV420 chroma vertical phase subtracts a quarter-scale offset using unsigned arithmetic; small phases can wrap by design or bug depending on hardware expectations.
- Chroma sizes use integer `src_w / hsub` and `src_h / vsub`; caller alignment is required for subsampled formats.
- DE33 base calculation uses `DE33_CH_SIZE` from mixer configuration headers; mismatched channel size constants corrupt register targeting.
- Zero dimensions would underflow size macros if upstream DRM checks failed.

## Test Signals

Regression tests should cover anisotropic scaling to detect the `vstep`/`hstep` coefficient-selection risk, all subsampling modes, YUV420 phase behavior, DE2/DE3/DE33 base offsets, UI-mode vs normal-mode selection, enable/disable writes, and visual output for RGB and YUV crops with fractional phases.
