# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-mod0.c

## Purpose
This legacy provider implements MOD0-style module clocks, A13 MBUS, A10/A80 MMC clocks, and MMC sample/output phase subclocks.

## Important APIs, Types, And Functions
Important functions/data include `sun4i_a10_get_mod0_factors()`, `sun4i_a10_mod0_data`, early and platform-driver registration for `allwinner,sun4i-a10-mod0-clk`, A80 MOD0 data, A13 MBUS critical setup, `struct mmc_phase`, `mmc_get_phase()`, `mmc_set_phase()`, `sunxi_mmc_setup()`, and A10/A80 MMC OF declarations.

## Control Flow
MOD0 setup maps registers and calls `sunxi_factors_register()`. The platform driver covers cases where MFD resources are not available during early `CLK_OF_DECLARE`. MMC setup registers the main factors clock plus two phase clocks in a onecell provider.

## State And Persistence
State is factor register fields, gate/mux bits, and phase delay fields. MBUS is registered critical to avoid accidental disable.

## Dependencies And Integration Points
It depends on legacy `clk-factors`, CCF, OF/platform mapping, and spinlocks. It integrates with storage, module peripherals, MBUS, and MMC host drivers.

## Risks
MOD0 clocks only divide, so requests above the parent are clamped. MMC phase calculations assume parent/grandparent rates form a clean divider. The dual early/platform registration path prevents missing clocks but must avoid duplicate registration on the same node.

## Test Signals
Test MOD0 peripheral rates, A13 MBUS stability, A10/A80 MMC card I/O, phase set/get, and MFD-instantiated mod0 probe.
