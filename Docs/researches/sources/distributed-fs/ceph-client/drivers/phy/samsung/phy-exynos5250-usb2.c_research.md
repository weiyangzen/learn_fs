# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-usb2.c

Purpose: Provides Exynos5250 and Exynos5420 USB2 PHY configuration for the common Samsung USB2 driver. It covers OTG/device, host, and HSIC PHYs, with a reduced Exynos5420 host/HSIC layout.

Important APIs and functions: Exports `exynos5250_usb2_phy_config` and `exynos5420_usb2_phy_config`. Helpers include `exynos5250_rate_to_clk()`, `exynos5250_isol()`, `exynos5250_power_on()`, and `exynos5250_power_off()`. PHY metadata arrays are `exynos5250_phys` and `exynos5420_phys`.

Control flow: Device power-on switches the sysreg mode to device, configures OTG clock/reset/refclk fields, clears sleep/suspend/SIDDQ, pulses resets, and removes isolation. Host/HSIC power-on configures host PHY clock/reset, also configures OTG registers, initializes both HSIC PHY control registers, enables EHCI burst settings, applies OHCI frame settings, and removes host isolation. Power-off re-enables isolation and sets sleep/suspend/SIDDQ or HSIC low-power bits for the selected PHY.

State and persistence: The file relies on common-driver state and writes MMIO registers for host, HSIC, EHCI, OHCI, and OTG control. PMU isolation offset selection depends on whether the active config is Exynos5250 or Exynos5420 and on the PHY id. Mode switch state persists in a system register.

Dependencies and integration points: Depends on `phy-samsung-usb2.h`, common Samsung USB2 code, MMIO, PMU/sysreg regmaps, and Exynos USB host/device controllers. It integrates with EHCI/OHCI/DWC2-style consumers and HSIC devices.

Risks: Host power-on also touches OTG registers and both HSIC controls, so independent consumers are not fully isolated from each other. Exynos5420 uses a different host isolation offset and fewer exposed PHYs. A duplicated macro name for `EXYNOS_5250_HOSTEHCICTRL_FLADJVAL0_MASK` near the FLADJVAL2 comment is suspicious but not used in the active code path. Mode switching can disrupt active role users if calls are unbalanced.

Test signals: Device mode enumeration, host EHCI/OHCI behavior, HSIC device detection, Exynos5420 host isolation offset validation, reference clock variants, sysreg mode switch checks, and repeated runtime PM power cycles.
