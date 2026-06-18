# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.c

## Purpose

`sun8i_ui_scaler.c` programs the GSU scaler used by Allwinner UI layers on DE2/DE3 mixers. It selects the correct scaler unit base, converts DRM 16.16 scale/phase values to hardware 20-bit fractional values, writes input/output sizes and steps, and loads horizontal filter coefficients.

## Important APIs, Types, and Functions

- `lan2coefftab16`: 15 sets of 16 filter coefficients derived from Allwinner BSP code.
- `sun8i_ui_scaler_base()`: computes the UI scaler MMIO base after accounting for VI scaler units and DE2 vs DE3 unit sizes.
- `sun8i_ui_scaler_coef_index()`: maps hardware scale step to a coefficient-table set.
- `sun8i_ui_scaler_enable(struct sun8i_layer *layer, bool enable)`: writes GSU enable and coefficient-ready bits.
- `sun8i_ui_scaler_setup(...)`: writes size, step, phase, and horizontal coefficients.

## Control Flow

Callers compute source/destination dimensions, scale, and phase from DRM plane state, then invoke `sun8i_ui_scaler_setup()` before enabling the unit. Setup derives the scaler base from layer channel and configuration, shifts phase and scale from 16 fractional bits to 20 fractional bits, writes output/input sizes and H/V step/phase registers, selects a coefficient block from `hscale`, and writes 16 horizontal coefficients. Enable then toggles `SUN8I_SCALER_GSU_CTRL`.

## State and Persistence Behavior

The file has no heap state. Persistent state is entirely in hardware registers. Coefficient tables are static read-only data. Repeated setup calls overwrite the same scaler unit for the layer's channel; disable clears the control register.

## Dependencies and Integration Points

It depends on `sun8i_ui_scaler.h` and `sun8i_vi_scaler.h` for constants and the VI scaler base/size definitions used to offset UI scalers. It integrates with `sun8i_ui_layer_update_coord()` and regmap-backed mixer MMIO.

## Risks and Edge Cases

- Base calculation depends on `cfg->vi_scaler_num` and channel ordering; wrong mixer configuration maps writes to the wrong scaler.
- Only horizontal coefficients are explicitly loaded; hardware may use fixed/default vertical coefficients, but this should be confirmed for supported SoCs.
- Scale-to-coefficient mapping is coarse and table-bound; extreme down/up scaling relies on atomic min/max checks.
- Width/height macros subtract one, so zero dimensions would underflow if DRM checks failed.

## Test Signals

Tests should validate base offsets for DE2 and DE3 configurations, coefficient index boundaries, scale and phase conversion from 16.16 to hardware 20-bit fractions, equal-size fractional-phase scaling, and disable clearing the control register.
