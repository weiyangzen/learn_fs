# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c

## Purpose

This driver registers SM8250 LPASS glitch-free mux clocks for AONCC and AUDIOCC. These muxes select between TX, VA, WSA, and RX MCLK/NPL parent paths used by codec and LPASS audio hardware without modeling rate generation locally.

## Important APIs, types, and functions

The driver defines `lpass_gfm`, `clk_gfm`, `clk_gfm_get_parent()`, `clk_gfm_set_parent()`, `clk_gfm_ops`, six static muxes, AON and AUDIO onecell data, `lpass_gfm_data`, and `lpass_gfm_clk_driver_probe()`. Each `clk_gfm` has a mux register offset, mask, two firmware-named parents, `CLK_SET_RATE_PARENT`, and `CLK_OPS_PARENT_ENABLE`.

## Control flow, state, and persistence

Probe gets match data for AONCC or AUDIOCC, maps MMIO, enables runtime PM, creates PM clock support, adds all PM clocks from DT, computes each mux's effective MMIO address, registers each mux clock, and publishes the onecell provider. State is the single mux bit per registered clock and runtime PM clock votes; no persistent software state exists after registration.

## Dependencies and integration points

The file depends on SM8250 LPASS AONCC/AUDIOCC binding IDs, firmware-named parent clocks, runtime PM and PM clock integration, and LPASS codec/audio consumers. It matches `"qcom,sm8250-lpass-aoncc"` and `"qcom,sm8250-lpass-audiocc"`.

## Risks and test signals

Several muxes share the same register bit, so parent changes must match hardware grouping and codec expectations. Missing PM clocks or parent firmware names prevent probe or later parent enables. Test by binding both compatibles, switching each mux parent, checking `clk_summary`, running RX/TX/VA/WSA audio paths, and validating runtime PM suspend/resume with parent clocks enabled.
