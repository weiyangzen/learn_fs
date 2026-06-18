# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-sata.c

Purpose: Implements the Exynos5250 SATA SerDes/PHY provider. It powers PMU isolation, programs SATA PHY registers, sends an I2C tuning command to the external SATA PHY component, and waits for PLL lock.

Important APIs and functions: `exynos_sata_phy_probe()` maps registers, resolves PMU syscon and I2C client phandle, enables the `sata_phyctrl` clock, creates the generic PHY, and registers the provider. PHY operations are `exynos_sata_phy_init()`, `exynos_sata_phy_power_on()`, and `exynos_sata_phy_power_off()`. `wait_for_reg_status()` polls PLL lock using jiffies.

Control flow: Probe holds a reference to the I2C device and enables the PHY control clock for the lifetime of the provider. Power-on/off toggles `EXYNOS5_SATAPHY_PMU_ENABLE`. Init enables PMU power, sequences reset bits, sets high-speed Gen3 mode, marks PHY calibrated, sends `{0x3a, 0x0b}` over I2C, cycles common reset, and waits for `PHSTATM_PLL_LOCKED`.

State and persistence: `struct exynos_sata_phy` stores the generic PHY, clock, MMIO base, PMU regmap, and I2C client. Hardware state persists in PMU enable, SATA reset/mode/control registers, and I2C-programmed SerDes state. The I2C device reference is released only on probe failure in this code path.

Dependencies and integration points: Depends on generic PHY, platform MMIO, PMU syscon/regmap, I2C core, OF phandle lookup, clocks, and Exynos5250 SATA host integration.

Risks: Polling uses a tight jiffies loop without sleep. The fixed I2C payload is hardware-specific and failure aborts init. Probe defers if the I2C client is not ready. Clock lifetime is broad: enabled at probe and disabled only on probe failure through local labels. Wrong PMU or I2C phandles prevent SATA bring-up.

Test signals: SATA host link-up at supported speeds, PLL lock status, I2C transaction success, PMU enable/disable checks, probe defer ordering with I2C adapter/client, and repeated PHY init/power cycles.
