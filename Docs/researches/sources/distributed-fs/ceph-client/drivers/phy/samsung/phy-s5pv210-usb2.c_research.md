# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-s5pv210-usb2.c

Purpose: Supplies S5PV210 USB2 PHY data and callbacks for the common Samsung USB2 driver. It supports device and host PHY instances.

Important APIs and functions: Exports `s5pv210_usb2_phy_config`. Helpers are `s5pv210_rate_to_clk()`, `s5pv210_isol()`, `s5pv210_phy_pwr()`, `s5pv210_power_on()`, and `s5pv210_power_off()`. Per-instance metadata is `s5pv210_phys`.

Control flow: The common driver calls the rate converter for 12/24/48 MHz reference clocks. Power-on clears PMU isolation and powers/resets the selected PHY. Power-off sets power-down bits and then re-enables PMU isolation. Device and host choose different power and reset masks.

State and persistence: No private runtime state is defined here. Hardware state persists in USB PHY power/clock/reset registers and PMU isolation bits at `S5PV210_USB_ISOL_OFFSET`.

Dependencies and integration points: Depends on the common Samsung USB2 driver, MMIO accessors, PMU regmap, and S5PV210 USB device/host consumers.

Risks: Only three reference rates are supported. Clock writing uses `drv->ref_reg_val` directly to `S5PV210_UPHYCLK`, so common-driver conversion must already encode the correct bits. Power/isolation ordering differs from some Exynos variants and should not be mechanically refactored without hardware testing.

Test signals: S5PV210 device and host USB enumeration, 12/24/48 MHz reference clocks, PMU isolation bit changes, reset timing, and repeated power cycles.
