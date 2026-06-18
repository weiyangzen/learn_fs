# sources/distributed-fs/ceph-client/drivers/phy/phy-pistachio-usb.c

This platform driver provides the IMG Pistachio USB2 PHY as a generic PHY. It stores the device, CR_TOP syscon regmap, `usb_phy` clock, and DT-provided `img,refclk` selector.

Probe resolves the `img,cr-top` syscon, gets the `usb_phy` clock, reads the reference-clock selector, creates a PHY, and registers `of_phy_simple_xlate`. `pistachio_usb_phy_power_on()` enables the clock, programs strap refclk selection, validates XO crystal mode requires a 12 MHz clock, maps the clock rate to an FSEL index, writes FSEL, then polls up to 200 ms for both RX PHY and UTMI clock status while also detecting VBUS fault. Power-off disables the clock.

State is held in hardware strap/control/status registers and clock enable state. Dependencies are clk, syscon/regmap, DT binding constants from `phy-pistachio-usb.h`, jiffies timing, and generic PHY. Risks include unsupported clock rates returning `-EINVAL`, polling with manual jiffies loops instead of `read_poll_timeout`, VBUS fault causing bring-up failure, and reliance on board-provided `img,refclk`. Test signals are status bits during power-on; no unit tests.
