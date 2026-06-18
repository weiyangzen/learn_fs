# sources/distributed-fs/ceph-client/drivers/phy/phy-lpc18xx-usb-otg.c

This driver provides a generic PHY for the internal USB OTG PHY on NXP LPC18xx/43xx. It stores a created PHY, one clock, and a syscon regmap in `struct lpc18xx_usb_otg_phy`.

Probe obtains the parent syscon regmap, gets the unnamed PHY clock, creates a managed PHY with init/exit/power callbacks, stores private data, and registers `of_phy_simple_xlate`. `lpc18xx_usb_otg_phy_init()` sets the PHY clock to 480 MHz and prepares it. `power_on()` enables the clock and clears `LPC18XX_CREG_CREG0_USB0PHY` in `CREG0`, because the bit is active-disable. `power_off()` sets that bit and disables the clock. Exit unprepares the clock.

State persistence is limited to clock preparation/enable state and the syscon bit. Dependencies are clk, syscon/regmap, generic PHY, platform driver, and OF. Integration is a simple one-PHY provider for USB controller phandles. Risks include assuming the parent node is the syscon, fixed 480 MHz rate, and possible clock leak if power-off regmap update fails after enable was active. Test signals are driver probe and USB controller operation; no local unit test exists.
