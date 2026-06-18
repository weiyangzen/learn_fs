# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4x12-usb2.c

Purpose: Provides Exynos4x12 and Exynos3250 USB2 PHY data and callbacks for the common Samsung USB2 driver. It supports device, host, HSIC0, and HSIC1 on Exynos4x12 and a reduced single-PHY configuration for Exynos3250.

Important APIs and functions: Exports `exynos3250_usb2_phy_config` and `exynos4x12_usb2_phy_config`. Main helpers are `exynos4x12_rate_to_clk()`, `exynos4x12_setup_clk()`, `exynos4x12_isol()`, `exynos4x12_phy_pwr()`, `exynos4x12_power_on_int()`, `exynos4x12_power_off_int()`, `exynos4x12_power_on()`, and `exynos4x12_power_off()`.

Control flow: External power requests use `ext_cnt`; internal shared dependencies use `int_cnt`. Host power-on switches the mode register to host and powers the device PHY internally. Device power-on switches to device when mode switching is supported. HSIC power-on powers device and host dependencies before the HSIC PHY. Power-off unwinds these relationships and switches device mode back to host when needed. Clock setup writes FSEL and common-on bits, with an Exynos3250-specific refclk select option.

State and persistence: Persistent state is held by the common driver counters. Hardware state includes PHY power bits, reset bits, PMU isolation for OTG/HSIC0/HSIC1, mode switch sysreg bits, and clock selection. The comments note empirically corrected reset bit assignments for Exynos4412-like hardware.

Dependencies and integration points: Depends on the common Samsung USB2 driver, MMIO, PMU and system regmaps, and Exynos4x12/3250 SoC configuration. It integrates with USB OTG, host, and HSIC consumers that share physical resources.

Risks: Shared dependency counters must remain balanced; underflow or missed dependency power-off can leave analog blocks on or off incorrectly. Mode switching affects device/host role selection. The hardware reset bit layout intentionally differs from reference manual ordering, making cleanups risky without hardware validation.

Test signals: Device/host role switching, HSIC dependency behavior, repeated nested power requests, counter balance under runtime PM, Exynos3250 single-PHY boot, all supported reference rates, and register traces showing corrected reset bits.
