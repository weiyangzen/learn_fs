# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-emmc.c

## Purpose
Intel Keem Bay eMMC PHY provider. It maps eMMC PHY registers through regmap MMIO, delays clock acquisition until PHY init to avoid circular SDHCI dependency, and powers/calibrates the PHY DLL based on the active eMMC clock rate.

## Important APIs, types, and functions
- `struct keembay_emmc_phy` stores `syscfg` regmap and optional `emmcclk`.
- `keembay_emmc_phy_init()/exit()` get/put optional `emmcclk`.
- `keembay_emmc_phy_power()` powers down first, then for power-on selects frequency range, powers CALIO, polls `CAL_DONE`, enables DLL, and polls `DLL_RDY` unless clock rate is zero.
- `keembay_emmc_phy_power_on()` sets TX delay chain and output tap values before analog power-up.

## Control flow
Probe maps registers, creates regmap, creates one PHY, and registers simple xlate. Init obtains the eMMC clock after the SDHCI clock provider exists. Power-on configures delay fields then calls the common power sequence; power-off clears power/DLL bits.

## State and persistence
Runtime state is the optional clock pointer and PHY register bits. No persistent storage.

## Dependencies and integration points
Uses generic PHY, regmap MMIO, clk, platform MMIO, and OF. Integrates with SDHCI/eMMC via a PHY phandle and late clock lookup.

## Risks and test signals
Risks include optional clock rate zero skipping DLL lock verification, unsupported high rates only warning, and dependency on init being called before power. Test SDHCI probe ordering, 0/low/high clock rates, calibration timeout, DLL timeout, and power cycling.
