# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.c

## Purpose

`intel_dpio_phy.c` programs the DPIO display PHY blocks used by Intel Valleyview, Cherryview, Broxton, and Geminilake display outputs. These PHYs back DP/HDMI/DDI ports and are partly controlled through platform display MMIO registers and partly through VLV/CHV IOSF sideband DPIO register accesses. The file owns port-to-PHY/channel mapping, PHY power/reset sequencing, signal swing/de-emphasis programming, lane reset/latency programming, and state verification for the DPIO-specific display hardware.

The implementation is split into two families. The BXT/GLK path uses MMIO-style `intel_de_*()` accessors and tables describing DPIO PHY topology. The VLV/CHV path uses `vlv_dpio_get()`, `vlv_dpio_read()`, `vlv_dpio_write()`, and `vlv_dpio_put()` to access sideband DPIO registers, with separate helpers for common lanes, PCS blocks, and TX lanes.

## Important APIs, Types, And Functions

`struct bxt_dpio_phy_info` is the local topology table type. It records whether a PHY is dual-channel, which other PHY supplies RCOMP/GRC calibration, reset delay, display power-on mask, and the port mapped to each channel. `bxt_dpio_phy_info[]` maps BXT PHY0 to ports B/C and PHY1 to port A. `glk_dpio_phy_info[]` maps GLK PHY0/1/2 to ports B/A/C and adds reset delays and different power-on masks.

`bxt_port_to_phy_channel()` is the main BXT/GLK mapping function. It scans the selected topology table and returns `enum dpio_phy` plus `enum dpio_channel`, warning and falling back to PHY0/CH0 on unexpected ports.

`bxt_dpio_phy_init()`, `_bxt_dpio_phy_init()`, `bxt_dpio_phy_uninit()`, `bxt_dpio_phy_is_enabled()`, and `bxt_dpio_phy_verify_state()` manage BXT/GLK PHY lifecycle. Initialization powers the PHY through `BXT_P_CR_GT_DISP_PWRON`, waits for `PHY_POWER_GOOD` and reserved-bit accessibility, writes RCOMP offsets, power-gating bits, optional copied GRC calibration, optional delay, and releases common reset through `COMMON_RESET_DIS`. Verification rereads the same fields and uses `display->state.bxt_phy_grc` for copied calibration checks.

`bxt_dpio_phy_set_signal_levels()` uses the encoder buffer translation table from `encoder->get_buf_trans()` and per-lane `intel_ddi_level()` values to program BXT margin, unique transition scale, scaling compensation, and de-emphasis. It toggles PCS swing calculation bits before and after writing TX lane fields.

`bxt_dpio_phy_calc_lane_lat_optim_mask()`, `bxt_dpio_phy_set_lane_optim_mask()`, and `bxt_dpio_phy_get_lane_lat_optim_mask()` compute and program the per-lane latency optimization bit used by BXT and related CHV terminology.

`vlv_dig_port_to_channel()`, `vlv_dig_port_to_phy()`, `vlv_pipe_to_phy()`, and `vlv_pipe_to_channel()` are VLV/CHV mapping helpers. They encode the hardware distinction that ports map to PCS/TX channels while pipes map to common-lane PLL resources.

`chv_set_phy_signal_level()`, `chv_data_lane_soft_reset()`, `chv_phy_pre_pll_enable()`, `chv_phy_pre_encoder_enable()`, `chv_phy_release_cl2_override()`, and `chv_phy_post_pll_disable()` implement Cherryview lane programming and sequencing. They cover swing/de-emphasis setup, data lane reset assertion/deassertion, clock distribution, used-clock-channel selection, latency programming, lane stagger programming, CL2 override cleanup, and post-disable clock distribution cleanup.

`vlv_set_phy_signal_level()`, `vlv_phy_pre_pll_enable()`, `vlv_phy_pre_encoder_enable()`, `vlv_phy_reset_lanes()`, and `vlv_wait_port_ready()` implement the older Valleyview path, including group-register signal writes, reset defaults, skew workarounds, used-clock-channel programming, and polling port-ready status.

## Control Flow And State

The BXT/GLK enable path starts with platform topology lookup. If a PHY depends on another PHY's RCOMP calibration, `bxt_dpio_phy_init()` temporarily powers the RCOMP source if needed, initializes the requested PHY, then powers the source back down if it was not originally enabled. `_bxt_dpio_phy_init()` first checks whether the PHY is already enabled and valid. If enabled but verification fails, it reprograms it. This gives the boot/readout path a chance to preserve correct firmware state while repairing invalid register state.

Signal-level programming is invoked after the encoder/CRTC state has a lane count and train-set levels. The function clears PCS swing calculation, writes per-lane TX fields for every active lane, checks for the invalid `UNIQUE_TRANGE_EN_METHOD` plus disabled scaling combination, writes de-emphasis, and restarts swing calculation.

The CHV pre-PLL path asserts soft reset, powers down unused lanes, may force CL2 alive when channel/pipe crossing needs access to the second common lane, sets left/right clock distribution, sets PCS used-clock-channel override based on pipe B or non-B, and writes common-lane used-clock-channel state. The pre-encoder path then lets hardware manage TX FIFO reset source, writes latency optimization and lane stagger values based on port clock and lane count, and deasserts soft reset. Post-disable undoes clock distribution and leaves at least one lane not explicitly powered down so later channel power gating can work.

The VLV sequence is similar but simpler: pre-PLL writes lane reset defaults and skew workaround constants; pre-encoder selects the clock channel and lane clock registers; reset-lanes writes reset values when disabling; `vlv_wait_port_ready()` polls the appropriate DPLL or PHY status register for the selected port.

Persistent state is minimal and hardware-facing. The file writes register state and stores copied BXT GRC calibration in `display->state.bxt_phy_grc`. CHV additionally stores `dig_port->release_cl2_override` so a temporary CL2 powergate override can be released later.

## Dependencies And Integration Points

This file integrates with the i915 display encoder and modeset pipeline through `struct intel_encoder`, `struct intel_crtc_state`, and `struct intel_digital_port`. It relies on DDI buffer translation (`intel_ddi_buf_trans.h`), DP lane count helpers (`intel_dp_unused_lane_mask()`), display power-domain locking, BXT and VLV DPIO register definitions, and sideband access wrappers from `vlv_sideband.h`.

It is closely coupled to `intel_dpll.c` and `intel_dpll_mgr.c`: DPIO PHY setup must match PLL routing, channel selection, and port clock programming. The BXT PLL manager also calls `bxt_port_to_phy_channel()` to program port PLL registers. CHV/VLV PLL code uses the VLV pipe-to-PHY/channel helpers to read and write PLL registers.

## Risks And Edge Cases

The register sequences are timing-sensitive. BXT power-on waits for reserved bits to become readable and for power-good, while GRC calibration waits only 10 ms. Short or reordered waits can lead to inaccessible registers or unstable PHY state.

The BXT RCOMP dependency is easy to break: PHYs without their own resistor copy calibration from another PHY, and verification depends on `display->state.bxt_phy_grc` being read or written consistently. A bad fallback PHY/channel mapping can program the wrong port's PLL or lanes.

CHV channel/pipe crossing is fragile because the common lane normally follows the pipe but PCS/TX follows the port. The CL2 override path is a known special case and must be released exactly once. Lane count branches mean two-lane and four-lane modes program different PCS blocks.

The code contains hardware-workaround constants and comments noting unclear documentation, especially around unique transition scale selection and VLV/CHV skew/clock fields. These should be treated as behavioral requirements rather than cleaned up casually.

## Test Signals

Useful validation comes from modeset tests on BXT/GLK/VLV/CHV hardware or emulation that exercise HDMI and DP on all DPIO ports, one/two/four-lane DP, pipe/port crossing on VLV/CHV, suspend/resume state readout, and repeated enable/disable cycles. Kernel log signals include DDI PHY state mismatch messages, GRC timeout, PHY power-on timeout, port-ready timeout, PLL lock failures from adjacent PLL code, and warnings for unexpected ports or lane counts.
