# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.c

## Purpose
`intel_snps_hdmi_pll.c` computes Synopsys HDMI TMDS PLL register state for i915 display PHYs. It contains fixed-point interpolation and curve-based charge-pump calculations, then emits either DG2-style `struct intel_mpllb_state` values or C10 PHY `struct intel_c10pll_state` byte fields for arbitrary HDMI pixel clocks.

## Important APIs, Types, And Functions
- `struct pll_output_params` is the internal normalized PLL result: spread settings, dividers, charge-pump values, refclk scalar, fractional-N fields, phase-mix enable, multiplier, V2I selection, and VCO frequency bucket.
- `interp()` performs scaled integer interpolation between curve points.
- `get_ana_cp_int_prop()` calculates and clamps analog charge-pump integer/proportional values from VCO frequency, reference clock, V2I point, and curve tables.
- `compute_hdmi_tmds_pll()` is the common algorithm that derives datarate, TX clock divider, VCO, fractional-N quotient/remainder/denominator, multiplier, VCO bucket, and charge-pump settings.
- `intel_snps_hdmi_pll_compute_mpllb()` fills `struct intel_mpllb_state` using DG2/SNPS register field macros and a 100 MHz reference clock.
- `intel_snps_hdmi_pll_compute_c10pll()` fills `struct intel_c10pll_state` using C10 PLL field macros and a 38.4 MHz reference clock.

## Control Flow
Both public compute functions supply PHY-specific curve tables and reference-clock constants, call `compute_hdmi_tmds_pll()`, then pack the normalized results into their target hardware state structure. The common algorithm multiplies `pixel_clock` by 10000 to get data rate, chooses V2I and TX divider based on whether the rate is below the roughly 10 GHz threshold, derives VCO and fractional-N values against the post-scaled reference clock, chooses a curve segment and VCO bucket, computes analog charge-pump values, and returns all register fields through `pll_output_params`.

## State And Persistence
The file has no static mutable state. It writes only into caller-provided PLL state structures. The resulting state persists later when other display code writes the fields to hardware registers; this file itself performs no MMIO.

## Dependencies And Integration Points
It depends on Linux math helpers, register field macros from `intel_cx0_phy_regs.h` and `intel_snps_phy_regs.h`, display PLL state types from `intel_display_types.h`, and the public declarations in `intel_snps_hdmi_pll.h`. `intel_snps_phy.c` calls the MPLLB calculator as a fallback when an HDMI pixel clock is not present in the precomputed DG2 table. C10 PHY code calls the C10 calculator for newer PHY state construction.

## Risks And Edge Cases
The algorithm is entirely fixed-point integer math with large constants, so overflow, unintended truncation, and off-by-one rounding are the main risks. `compute_hdmi_tmds_pll()` assumes the chosen VCO falls into one of the hardcoded curve segments; clocks outside the intended HDMI range could leave an invalid segment default. `do_div()` mutates its dividend, so surrounding calculations must use the intended post-division remainder semantics. The fractional remainder adjustment subtracts `(rem >> 15)`, which is hardware-specific and easy to regress. MPLLB and C10 packing use different field widths and shifts, so any common algorithm change requires verification against both targets.

## Test Signals
Good signals include golden-register tests for common HDMI clocks such as 25.175, 27, 74.25, 148.5, 297, and 594 MHz; comparison with the precomputed DG2 table where entries overlap; C10-specific register byte checks; HDMI modeset tests at table and non-table pixel clocks; and warnings or black-screen regressions around PLL lock failures in the caller.
