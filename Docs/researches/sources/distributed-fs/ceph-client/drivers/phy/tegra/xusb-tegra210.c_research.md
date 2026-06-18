# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra210.c` Research

## Purpose

This file implements the Tegra210 XUSB padctl backend. It is the most feature-rich file in this group: it handles USB2 UTMI, HSIC, PCIe UPHY lanes, SATA UPHY lanes, USB3 SuperSpeed mapping over PCIe/SATA lanes, PLL bring-up, PMC-backed sleepwalk, wake-event programming, role-switch VBUS/ID overrides, fake USB3 companion ports for device/OTG-only USB2 ports, and noirq suspend context save/restore.

## Important APIs, Types, and Functions

- `struct tegra210_xusb_fuse_calibration` caches USB2 HS current, termination, and RPD fuse values.
- `struct tegra210_xusb_padctl_context` stores key mux/capability registers across suspend.
- `struct tegra210_xusb_padctl` embeds common padctl state, a PMC `regmap`, fuse calibration, and saved context.
- `tegra210_pex_uphy_enable()` and `tegra210_sata_uphy_enable()` perform PLL/reset/calibration/lock sequencing for PCIe and SATA UPHY groups.
- `tegra210_uphy_init()` and `tegra210_uphy_deinit()` coordinate UPHY group bring-up/down and AUX LP0 clamp state.
- `tegra210_pmc_utmi_enable_phy_sleepwalk()` and `tegra210_pmc_hsic_enable_phy_sleepwalk()` program PMC USB sleepwalk state for UTMI and HSIC.
- `tegra210_usb2_phy_power_on()` / `_off()`, `tegra210_hsic_phy_power_on()` / `_off()`, and `tegra210_usb3_phy_power_on()` / `_off()` are the main PHY power paths.
- `tegra210_usb2_phy_set_mode()` drives OTG role changes through VBUS/ID override and VBUS regulator state.
- `tegra210_utmi_port_reset()` detects battery-charger ZIP/ZIN bits and toggles VBUS override as a port reset signal.
- `tegra210_xusb_padctl_soc` exports the SoC descriptor with USB2, HSIC, and USB3 port ops plus supply names.

## Control Flow

Probe allocates `struct tegra210_xusb_padctl`, reads fuse calibration from `TEGRA_FUSE_SKU_CALIB_0` and `TEGRA_FUSE_USB_CALIB_EXT_0`, and optionally finds the PMC phandle/regmap named `"usb_sleepwalk"`. Common pad setup creates USB2, HSIC, PCIe, and SATA pads; lane mux programming temporarily asserts IDDQ through lane ops for UPHY lanes; common port setup maps USB2/HSIC ports directly and maps USB3 ports through `tegra210_usb3_map`.

PCIe/SATA PHY init calls `tegra210_uphy_init()` under the padctl lock. That enables PCIe and SATA PLLs if present, performs manual PLL calibration and RCAL polling unless hardware sequencing is already enabled, switches PLLs to hardware control, starts hardware sequences, and deasserts AUX LP0 clamps. SuperSpeed PHY power-on then maps the SS port to its USB2 companion, writes UPHY USB3 electrical tuning registers, and releases per-port ELPG clamps.

USB2 init enables host-mode VBUS and assigns the shared USB2 bias pad to XUSB. USB2 power-on handles fake USB3 port unclamping when the common layer assigned one, programs squelch/disconnect levels, role-specific port capability, fuse-calibrated current and RPD/termination, charger VREG settings, and shared bias tracking through the `trk` clock with a pad reference count. Power-off reverses fake-port ELPG state and powers down the shared bias pad when the count reaches zero. OTG mode changes ground ID and enable regulator for host, set VBUS override for device, or clear both for none.

HSIC power-on applies trim/tuning, clears HSIC power-down bits, enables the tracking clock, runs HSIC tracking timers, then disables the clock. PMC sleepwalk for UTMI/HSIC copies active electrical parameters into PMC registers, configures saved line state, staged pull-up/pull-down behavior, wake match values, and line wake enables. ELPG wake helpers program sticky wake event and interrupt-enable bits for UTMI, HSIC, and SuperSpeed lanes.

## State and Persistence

The driver persists fuse-derived calibration in memory, PMC sleepwalk settings in PMC registers, UPHY PLL enable state in `pcie->enable` and `sata->enable`, USB2 shared bias state in `usb2->enable`, and fake USB3 port assignment in common USB2 port state. Noirq suspend deinitializes UPHY, saves USB2 pad mux, USB2 port capability, SS port map, and USB3 pad mux, then resume restores the muxes while temporarily asserting IDDQ on UPHY lanes before reinitializing UPHY. Remote wake detection reads ELPG wake interrupt/event bits.

## Dependencies and Integration Points

Dependencies include generic PHY, clocks, reset controls, regulators, Tegra clock helpers (`tegra210_plle_*`, `tegra210_xusb_pll_*`, `tegra210_sata_pll_*`), Tegra fuse data, PMC regmap via device tree, common XUSB padctl data structures, and device-tree lane/port definitions. It integrates with the common driver through pad/lane/port/padctl ops and with USB role switching through the common USB2 port mode callback.

## Risks and Edge Cases

- PLL bring-up has multiple timeout loops; failures can leave resets/clocks partially unwound and should be validated on all mux combinations.
- PMC sleepwalk is optional: missing `nvidia,pmc` or missing `"usb_sleepwalk"` regmap leaves sleepwalk ops returning `-EOPNOTSUPP`.
- Fake USB3 port handling is necessary for device/OTG USB2 ports without a companion; bad DT port counts can exhaust fake ports and fail setup in the common layer.
- `tegra210_hsic_phy_power_off()` reads `HSIC_PADX_CTL0` but writes the modified power-down bits to `HSIC_PADX_CTL1`, which looks suspicious and may prevent proper HSIC power-down.
- `tegra210_sata_pad_probe()` stores a reset but never obtains `sata->pll`, while `tegra210_sata_uphy_enable()` calls `clk_prepare_enable(sata->pll)`; this depends on external initialization or is a potential null/invalid clock path.
- Role switching calls `regulator_is_enabled()` and disable without checking all return paths, so regulator providers with strict semantics need runtime coverage.

## Test Signals

Useful signals include Tegra210 builds, DT validation for USB2/HSIC/PCIe/SATA lanes and PMC phandle, UPHY PLL lock and RCAL success without timeout logs, USB3 lane-to-port mapping for PCIe and SATA lanes, fake USB3 port assignment for peripheral/OTG USB2 ports, HSIC bring-up/power-down, runtime usb-role-switch host/device/none transitions, UTMI port reset behavior on ZIP/ZIN, suspend/resume with UTMI/HSIC/SS wake, and absence of ELPG clamp ordering regressions.
