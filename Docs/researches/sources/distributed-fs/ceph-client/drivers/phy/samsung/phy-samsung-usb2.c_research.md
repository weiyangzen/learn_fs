# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.c

Purpose: core Samsung S5P/Exynos USB 1.1/2.0 generic PHY provider. It binds DT compatibles to SoC-specific `samsung_usb2_phy_config` tables defined elsewhere, allocates one `struct phy` per configured sub-PHY, and provides shared clock, regulator, syscon, and MMIO plumbing.

Important APIs, types, and functions: `samsung_usb2_phy_power_on()` and `samsung_usb2_phy_power_off()` implement the exported `phy_ops`; `samsung_usb2_phy_xlate()` maps the phandle argument index to `drv->instances[index].phy`; `samsung_usb2_phy_probe()` maps the PHY MMIO resource, PMU syscon, optional system syscon, clocks named `phy` and `ref`, optional `vbus`, and registers the provider. The OF table selects configs for Exynos3250, Exynos4210, Exynos4x12, Exynos5250, Exynos5420, and S5PV210 behind Kconfig guards.

Control flow: probe requires DT, match data, MMIO resource 0, a `samsung,pmureg-phandle`, and clocks. If `cfg->rate_to_clk` exists it converts the reference clock rate into `drv->ref_reg_val`. It then creates each instance with `devm_phy_create()`, sets bus width to 8, attaches instance driver data, and registers the custom xlate. Power-on enables optional VBUS, prepares main and ref clocks, then calls the SoC-specific `power_on()` callback under `drv->lock`; errors unwind regulator and clocks in reverse order. Power-off runs the callback under the same spinlock, disables clocks, and disables VBUS.

State and persistence: runtime state is per-platform-device in `struct samsung_usb2_phy_driver` plus a flexible array of instances. Persistent hardware state is in PMU/sysreg/PHY registers written by the SoC callbacks. `ref_rate` and `ref_reg_val` cache derived clock information. The spinlock serializes register sequences shared by multiple PHY instances.

Dependencies and integration points: generic PHY framework, platform driver core, common clock, optional regulator, regmap/syscon, and SoC-specific config objects declared in the sibling header. DT consumers use an index cell to choose a sub-PHY. `suppress_bind_attrs` prevents runtime bind/unbind from sysfs, reducing risk around shared hardware state.

Risks: `samsung_usb2_phy_xlate()` directly reads `args->args[0]` and assumes a valid cell count from DT binding. Optional VBUS failures other than probe deferral are silently treated as no regulator. Callback failures during power-off leave clocks/regulator enabled because the function returns early. Hardware callback code must be IRQ-safe enough for spinlock context and must not sleep.

Test signals: build coverage for each Kconfig combination; DT binding tests for phandle cell count and compatible match data; boot/probe logs for missing syscons/clocks; USB host/device enumeration across each SoC config; suspend/resume or repeated power cycle tests to catch unbalanced clocks/regulators and shared-register races.
