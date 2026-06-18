# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-emmc.c

## Purpose
Intel Lightning Mountain eMMC PHY provider. It uses a syscon regmap to configure drive impedance, output tap delay, PHY power, frequency selection, calibration, and DLL lock based on eMMC clock rate.

## Important APIs, types, and functions
- `struct intel_emmc_phy` stores syscfg regmap and optional eMMC clock.
- `intel_emmc_phy_init()/exit()` get/put optional `emmcclk` at PHY init time to avoid SDHCI clock-provider cycles.
- `intel_emmc_phy_power()` powers down, computes frequency select from clock rate, powers up, polls `CALDONE`, enables DLL, and polls `DLLRDY`.
- `intel_emmc_phy_power_on()` sets 50-ohm drive and tap delay before power.

## Control flow
Probe gets `intel,syscon`, creates one PHY, and registers simple xlate. Init obtains clock. Power-on writes impedance/delay and analog power sequence. Power-off powers analog blocks down.

## State and persistence
Runtime state is regmap bits and cached clock pointer. No persistent state.

## Dependencies and integration points
Generic PHY, syscon/regmap, clk, OF platform. Used by eMMC/SDHCI consumers.

## Risks and test signals
Risks include high-rate only warning/clamping, dependence on init-before-power ordering, and lack of zero-rate special-case compared with Keem Bay. Test clock rates across FRQSEL ranges, calibration/DLL timeout, SDHCI probe ordering, and power cycles.
