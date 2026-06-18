<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c

## Purpose
Legacy `usb_phy` provider for NVIDIA Tegra20/Tegra30 USB PHY blocks. It supports UTMI, ULPI, and HSIC, programs PHY timing/PLL/pads/wake detectors, and registers a `struct usb_phy` for controller drivers.

## Important APIs, Types, And Functions
Core state is `struct tegra_usb_phy` plus SoC policy in `struct tegra_phy_soc_config`. `tegra_usb_phy_init()`, `tegra_usb_phy_shutdown()`, `tegra_usb_phy_set_wakeup()`, and `tegra_usb_phy_set_suspend()` are installed into `u_phy`. UTMI paths use `utmip_pad_open/close()`, `utmip_pad_power_on/off()`, `utmi_phy_clk_enable/disable()`, and `utmi_phy_power_on/off()`. ULPI uses `ulpi_phy_power_on/off()`, `devm_otg_ulpi_create()`, and `ulpi_viewport_access_ops`. HSIC uses `uhsic_phy_power_on/off()` and SoC register offsets. Probe parses DT tuning, PMC phandles, clocks, resets, regulators, GPIOs, and shared MMIO resources.

## Control Flow
Probe maps the shared controller/PHY MMIO, reads `dr_mode` and PHY type, obtains `vbus` and `pll_u`, optionally gets PMC regmap, initializes type-specific resources, fills `u_phy`, and calls `usb_add_phy_dev()`. PHY init enables PLL/VBUS, chooses a PLL parent frequency table entry, opens UTMI pads if needed, configures PMC detectors, and powers on the selected PHY. Suspend masks the shared IRQ, powers off/on, then unmasks. Shutdown disables wake, powers off, closes pads, and disables regulator/PLL.

## State And Persistence
Persistent state includes mapped registers, clocks, reset controls, regulator, PHY mode/type, `powered_on`, `wakeup_enabled`, `freq`, `pad_wakeup`, PMC regmap/instance, and global `utmip_pad_count` under `utmip_pad_lock`. Hardware state persists in USB PHY, controller, and PMC registers.

## Dependencies And Integration Points
Depends on OF properties (`phy_type`, `dr_mode`, `nvidia,*` tuning, optional `nvidia,pmc`), regulator, reset, clk, GPIO, regmap, the legacy USB PHY API, and shared Tegra USB controller registers.

## Risks
Shared registers/IRQ require careful masking while reprogramming. UTMI pad refcount imbalance can power down common bias while another PHY uses it. ULPI wake is unsupported. Missing DT tuning or unsupported PLL parent rates fail init. Error unwinding must balance VBUS, PLL, and UTMI pad state.

## Test Signals
Probe all PHY modes, invalid tuning, bad PLL rates, PMC probe deferral, suspend/resume with wake on/off, host/device/OTG modes, shared IRQ wake events, and repeated init/shutdown for pad-count leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c -->
