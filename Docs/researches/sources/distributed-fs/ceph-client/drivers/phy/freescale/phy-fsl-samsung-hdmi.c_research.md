# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-samsung-hdmi.c

## Purpose
Samsung HDMI 2.0 transmitter PHY driver for NXP i.MX8MP. It registers a clock provider named `hdmi_pclk`; clock rate selection programs the HDMI PHY PLL using a large fractional lookup table or calculated integer PMS values, then waits for PLL lock.

## Important APIs, types, and functions
- `struct fsl_samsung_hdmi_phy` stores device, MMIO registers, APB/ref clocks, clock hardware, and current PLL configuration.
- `phy_pll_cfg[]` is the fixed table of known fractional-divider pixel clock settings.
- `fsl_samsung_hdmi_phy_find_pms()` searches integer P/M/S dividers with VCO constraints.
- `fsl_samsung_hdmi_phy_find_settings()` chooses exact table match, calculated integer match, or closest available setting within 22.25-297 MHz.
- `fsl_samsung_hdmi_phy_configure()` writes common PHY registers, PLL dividers, lock detector parameters, mode-done bit, and polls `REG34_PLL_LOCK`.
- Runtime PM suspend/resume disables/re-enables APB clock and restores `cur_cfg`.

## Control flow
Probe maps registers, enables the APB clock, gets the ref clock, initializes runtime PM active state, registers a common-clock provider, then releases runtime PM. Clock consumers call determine/set rate. `set_rate()` finds settings and invokes the register programming sequence; resume replays that sequence if a configuration was active.

## State and persistence
Persistent state is only the cached `cur_cfg` pointer used for recalc and resume restore. The calculated config is a static global updated for non-table rates, so concurrent devices would share it. Hardware state lives in PHY registers and APB clock state.

## Dependencies and integration points
Uses common clock framework, platform MMIO, PM runtime, APB/ref clocks, and OF clock provider registration. It integrates with the HDMI display pipeline as a pixel clock source rather than as a generic PHY object.

## Risks and test signals
Risks include global `calculated_phy_pll_cfg` sharing across instances, lookup edge cases around table bounds, integer divider approximation quality, and APB runtime PM sequencing during clock ops. Test exact CEA modes, non-table modes, invalid out-of-range rates, runtime suspend/resume with active mode, and PLL lock timeout behavior.
