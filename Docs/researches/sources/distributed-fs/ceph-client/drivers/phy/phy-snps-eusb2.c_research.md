# sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c

This Synopsys eUSB2 HS PHY driver supports Qualcomm SM8550 and Samsung Exynos2200 variants using `snps_eusb2_phy_drvdata` for clock names and SoC-specific register initialization. It also composes with an optional repeater PHY.

Probe maps MMIO, gets an optional reset, bulk clocks, identifies the `ref` clock, gets `vdd` and `vdda12` regulators, optionally obtains a repeater through `devm_of_phy_optional_get()`, creates a generic PHY, and registers a provider. Init enables regulators, initializes the repeater, enables clocks, asserts/deasserts PHY reset, then dispatches to variant `phy_init`. Exynos setup programs reset bits, repeater mode, reference-clock PLL fields for 19.2/20/24/26/48 MHz, TX tuning, IDDQ, and PHY enable. Qualcomm setup programs override controls, PLL fields for 19.2/38.4 MHz, TX defaults, suspend controls, SIDDQ, POR, and override release. `set_mode` forwards mode to the repeater.

State includes current mode, resources, and hardware register state. Dependencies are clk/reset/regulator, MMIO, generic PHY, and optional repeater integration. Risks include tight 5 us status polling in the repeater partner, unsupported ref clocks, error unwind correctness across repeater/clocks/regulators, and no runtime PM. Test signals are probe/init errors and downstream USB enumeration.
