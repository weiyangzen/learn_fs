# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4210-usb2.c

Purpose: Supplies Exynos4210-specific configuration and power callbacks for the common Samsung USB2 PHY driver. It covers device, host, HSIC0, and HSIC1 PHYs.

Important APIs and functions: The exported data is `exynos4210_usb2_phy_config`. Helpers include `exynos4210_rate_to_clk()`, `exynos4210_isol()`, `exynos4210_phy_pwr()`, `exynos4210_power_on()`, and `exynos4210_power_off()`. Per-PHY metadata is in `exynos4210_phys`.

Control flow: The common driver calls the rate converter for the reference clock and per-instance power callbacks. Power-on clears power-down/suspend/sleep bits, writes the clock FSEL, toggles the relevant reset bits with required delays, then disables PMU isolation for device or host PHYs. Power-off enables PMU isolation first and then sets the PHY power-down bits. Host and HSIC reset masks differ so each physical block and host link path is reset appropriately.

State and persistence: This file persists no private data. It mutates common-driver instance counters indirectly through callbacks and writes the USB PHY MMIO power/clock/reset registers, PMU isolation bits, host floating-prevention register, and reference clock selector.

Dependencies and integration points: Depends on `phy-samsung-usb2.h`, the common Samsung USB2 framework, MMIO accessors, PMU regmap, and Exynos4210 register layout. It integrates with USB device, host, and HSIC controller users selected by DT phandle index.

Risks: Exynos4210 has separate PMU isolation offsets for device and host only; HSIC paths do not use isolation in this helper. Reset bit masks must match the hardware link topology. Power-on sequence order is explicitly important: hardware power before isolation removal.

Test signals: Device and host USB2 enumeration, HSIC0/HSIC1 attached-device detection, reference clock variants 12/24/48 MHz, reset timing stability, PMU isolation transitions, and repeated power-cycle testing through runtime PM.
