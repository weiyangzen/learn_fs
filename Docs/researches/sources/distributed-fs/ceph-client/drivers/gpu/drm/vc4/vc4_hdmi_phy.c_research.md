# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_phy.c

## Purpose

`vc4_hdmi_phy.c` programs the HDMI transmit PHY for three hardware families. The original VC4 path performs basic reset/RNG toggling. The VC5 path computes PLL/VCO parameters, range measurement offsets, lane amplitude/termination settings, clock word selection, and lane swaps. The VC6 path programs a newer PHY with different PLL registers, lane current/termination bitfields, and power-up controls.

## Important APIs, Types, and Functions

- VC4 exports: `vc4_hdmi_phy_init()`, `vc4_hdmi_phy_disable()`, `vc4_hdmi_phy_rng_enable()`, and `vc4_hdmi_phy_rng_disable()`.
- VC5 exports: `vc5_hdmi_phy_init()`, `vc5_hdmi_phy_disable()`, `vc5_hdmi_phy_rng_enable()`, and `vc5_hdmi_phy_rng_disable()`.
- VC6 exports: `vc6_hdmi_phy_init()` and `vc6_hdmi_phy_disable()`. The disable function is currently empty.
- VC5 helpers: `phy_get_vco_freq()`, `phy_get_cp_current()`, `phy_get_rm_offset()`, `phy_get_vco_gain()`, `phy_get_settings()`, `phy_get_channel_settings()`, and `vc5_hdmi_reset_phy()`.
- VC6 helpers: `vc6_phy_get_vco_freq()`, `vc6_phy_get_settings()`, `vc6_phy_get_channel_settings()`, and `vc6_hdmi_reset_phy()`.
- Tuning tables: `vc5_hdmi_phy_settings[]` maps TMDS ranges to pre-emphasis/main driver/resistance/termination per data and clock lane; `vc6_hdmi_phy_settings[]` maps rates to packed lane current, FFE, slew, bias, source, tap, and termination fields.

## Control Flow

The top-level HDMI encoder enable path calls the variant `phy_init()` after clocks and runtime PM are ready. VC4 init toggles reset bits and leaves the PHY active; disable asserts reset. VC5 init computes VCO selection/divider from the TMDS character rate, resets and powers down RNG, releases lane resets, configures range measurement, PLL calibration, PLL control, RM format, TMDS word select, charge pump/VCO gain, per-lane amplitude and termination, lane swap routing from `variant->phy_lane_mapping`, then toggles PLL reset bits to start the PLL. VC5 disable resets the PHY; RNG helpers clear/set the RNG power-down bit.

VC6 init computes an 8-12 GHz VCO divider, resets/powers down the PHY, writes a fixed block of PLL misc calibration values, configures 54 MHz reference clock, reset state, RM offset, VCO divider, PLL post divider, per-lane control words for three data lanes and the clock lane, TMDS word select, HDMI lane/bias/LDO/background power-up, PLL power-up, and PLL reset release. VC6 disable currently does nothing, which leaves cleanup to higher-level blanking/power paths.

## State and Persistence

The file stores only static tuning tables and uses live state from `struct vc4_hdmi`, especially `variant->phy_lane_mapping`, `hw_lock`, and the connector state's `hdmi.tmds_char_rate`. All hardware state is persisted only in PHY MMIO registers until reset, runtime suspend, or power removal. Every exported function takes `hw_lock` around writes; helpers that write expect the lock to be held.

## Dependencies and Integration Points

This file depends on `vc4_hdmi.h`, `vc4_hdmi_regs.h`, and `vc4_regs.h` for state, register access, and bitfield helpers. It is not a standalone PHY framework driver; the HDMI core calls it through variant callbacks. It depends on the register base tables in `vc4_hdmi_regs.h` matching the selected SoC generation and on `vc4_hdmi.c` enabling clocks/runtime PM before PHY MMIO access.

## Risks and Edge Cases

- PHY programming is table-driven and frequency-sensitive; off-by-one TMDS ranges or bad fallback to the last table entry can affect signal integrity.
- `phy_get_vco_freq()` and `vc6_phy_get_vco_freq()` rely on simple divider search and multiplication by 10 for TMDS bit rate, so unusual rates should be checked for overflow and valid hardware range.
- Lane mapping differs between BCM2711 HDMI0 and HDMI1; wrong `phy_lane_mapping` silently swaps physical lanes.
- VC6 contains many fixed magic PLL constants with little local explanation; regression testing on real BCM2712 hardware is important.
- `vc6_hdmi_phy_disable()` is empty, so power leakage or stale PHY state could be hidden by other disable paths.
- MMIO access triggers KUnit failures through the register accessors, so unit tests must avoid calling these functions directly without mocks.

## Test Signals

Best signals are HDMI link stability across TMDS rates from low pixel clocks to 4K60, analyzer eye/clock behavior, hotplug after repeated enable/disable, audio startup/shutdown RNG toggling on VC5, lane mapping validation on both HDMI ports, and BCM2712-specific suspend/resume or blank/unblank tests. Build coverage should include all exported prototypes referenced by variants.
