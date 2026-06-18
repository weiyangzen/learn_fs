# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb3.c

## Purpose
This is a compact generic PHY driver for the R-Car Gen3 USB3 PHY. It initializes clock source selection, optional spread-spectrum clocking, reset sequencing, and VBUS detection for a single USB3 PHY instance.

## Important APIs, Types, And Functions
`struct rcar_gen3_usb3` stores the MMIO base, created PHY, detected availability of `usb3s_clk` and `usb_extal`, and the optional `renesas,ssc-range` property. `rcar_gen3_phy_usb3_init()` is the only generic PHY callback. `write_clkset1_for_usb_extal()`, `rcar_gen3_phy_usb3_enable_ssc()`, and `rcar_gen3_phy_usb3_select_usb_extal()` implement the USB_EXTAL path, PLL multiplier programming, SSC range selection, PHY reset assertion/deassertion, and clock source writes.

## Control Flow
Probe requires a device tree node, maps one register resource, tries to get and briefly enable `usb3s_clk` and `usb_extal` to determine whether each has a nonzero rate, rejects devices with neither clock source available, enables runtime PM, creates a PHY, reads the optional SSC range, sets driver data, and registers a simple OF PHY provider. During PHY init, if USB3S clock is absent and USB_EXTAL is present, the driver programs the USB_EXTAL clock path and optional SSC setting before enabling VBUS detection unconditionally.

## State And Persistence
The driver keeps only static probe-time state: which clock source was usable and the requested SSC range. Hardware state is programmed on `.init` and persists until reset or later reinitialization. Runtime PM is enabled manually and disabled in remove, but no suspend/resume callbacks are supplied here.

## Dependencies And Integration Points
It depends on generic PHY, platform MMIO resources, optional clock providers named `usb3s_clk` and `usb_extal`, DT property `renesas,ssc-range`, runtime PM, and compatible string `renesas,rcar-gen3-usb3-phy`.

## Risks And Test Signals
Unsupported SSC values log an error and skip SSC setup without failing init, so board validation should confirm actual spread-spectrum requirements. Clock detection depends on prepare/enable and nonzero rates, so clock tree mistakes fail probe only when both paths look absent. Test signals include probe acceptance with either clock source, correct fallback to USB_EXTAL when `usb3s_clk` is unavailable, valid SSC ranges 4980/4492/4003, VBUS detection write, and provider resolution by USB3 controller consumers.
