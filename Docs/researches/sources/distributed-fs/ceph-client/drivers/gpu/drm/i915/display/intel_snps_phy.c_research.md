# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.c

## Purpose
`intel_snps_phy.c` implements i915 support for Synopsys display PHYs, primarily DG2-era PHYs with per-port MPLLB PLLs. It waits for PHY calibration, manages PSR lane power requests, programs lane signal levels, stores large precomputed MPLLB register tables for DP/eDP/HDMI link rates, selects or computes PLL state for a CRTC/encoder, enables/disables the MPLLB in the modeset sequence, reads back hardware state, derives port clock from register state, and verifies software state against hardware.

## Important APIs, Types, And Functions
- PHY utility entry points: `intel_snps_phy_wait_for_calibration()`, `intel_snps_phy_update_psr_power_state()`, and `intel_snps_phy_set_signal_levels()`.
- Precomputed table groups: `dg2_dp_100_tables`, `dg2_edp_tables`, and `dg2_hdmi_tables`, each containing `struct intel_mpllb_state` records for known link or pixel clocks.
- PLL selection and computation: `intel_mpllb_tables_get()` chooses the table family; `intel_mpllb_calc_state()` copies a matching table record or calls `intel_snps_hdmi_pll_compute_mpllb()` for unmatched HDMI clocks.
- PLL programming: `intel_mpllb_enable()` writes MPLLB CP, divider, SSC, and fractional-N registers, enables the platform PLL register, asserts force-enable, and waits for lock.
- PLL shutdown: `intel_mpllb_disable()` clears PLL enable, clears MPLLB force-enable, and waits for lock/ack clear.
- Readback and verification: `intel_mpllb_calc_port_clock()`, `intel_mpllb_readout_hw_state()`, and `intel_mpllb_state_verify()`.

## Control Flow
At platform startup or resume, `intel_snps_phy_wait_for_calibration()` scans all PHYs and records any SNPS PHY whose DP TX acknowledgment bits fail to clear within 25 ms. During link setup, `intel_snps_phy_set_signal_levels()` asks the encoder for the buffer translation table, derives per-lane DDI levels, and writes main/pre/post cursor values to `SNPS_PHY_TX_EQ()`. PSR power transitions write the lane disable power-state request field only for SNPS encoders.

Modeset PLL state calculation first classifies the output as eDP, DP, or HDMI. DP/eDP require exact table matches by `crtc_state->port_clock`; HDMI first checks the table and then falls back to the algorithm in `intel_snps_hdmi_pll.c`. Enabling writes all MPLLB register fields before asserting PLL enable, then writes the divider register again with `SNPS_PHY_MPLLB_FORCE_EN` so the PLL stays running through lane programming and Type-C disconnect cases. Disabling reverses enable and force-enable, then waits for the lock bit to clear. Readout reads all programmed fields and masks out force-enable because software state intentionally excludes that runtime bit. Verification runs for active DG2 CRTC modeset/fastset commits, reads hardware state, and warns on mismatches for each MPLLB field including firmware-controlled ref range.

## State And Persistence
Most state is static const table data. Runtime mutable state lives in hardware registers, `crtc_state->dpll_hw_state.mpllb`, and `display->snps.phy_failed_calibration`. The MPLLB force-enable bit is a transient runtime addition to the divider register and is stripped during readout. `ref_control` is read for sanity checking but treated as firmware-controlled rather than directly programmed by this file.

## Dependencies And Integration Points
The file integrates with Intel DDI code, DDI buffer translation data, display register access, platform PLL enable registers, PHY/encoder mapping helpers, CRTC atomic state, SNPS register definitions, and the HDMI PLL calculator. It is part of the modeset path for outputs whose PHY uses MPLLB instead of the shared DPLL framework.

## Risks And Edge Cases
The register tables are large magic-value tables; incorrect values can cause PLL unlocks or link instability and are hard to diagnose from code review alone. DP/eDP reject unsupported clocks with `-EINVAL`, while HDMI accepts algorithm-generated values for non-table clocks, creating different failure modes by output type. The hardcoded `if (0)` branch in port-clock calculation means the current implementation always assumes a 100 MHz reference clock there, which must match supported hardware. Force-enable must be applied only after the PLL samples divider values. Calibration failure tracking prevents later output setup on affected PHYs, so false positives can disable working ports. Verification only runs for DG2 active modeset/fastset commits and will not catch every runtime drift.

## Test Signals
Signals include PHY calibration failure masks, per-lane signal level register writes for trained link levels, DP/eDP link-rate table selection at RBR/HBR/UHBR and eDP-specific rates, HDMI table selection and algorithm fallback, PLL lock success after enable, lock clear after disable, readout-derived port clock matching requested port clock, and `intel_mpllb_state_verify()` mismatch warnings. Hardware tests should cover DG2 DP, eDP, HDMI, and Type-C disconnect/reconnect paths.
