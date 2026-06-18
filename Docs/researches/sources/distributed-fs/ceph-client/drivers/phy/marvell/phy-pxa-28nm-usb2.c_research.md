<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c

Purpose: Implements the Marvell/PXA1928 28 nm USB2 PHY, including PLL, TX/RX, digital, OTG, calibration polling, VBUS validity override, and analog shutdown.

Important APIs and types: `struct mv_usb2_phy` stores PHY, platform device, base, and clock. `wait_for_reg()` polls hardware status. Main callbacks are `mv_usb2_phy_28nm_init()`, `mv_usb2_phy_28nm_power_on()`, `mv_usb2_phy_28nm_power_off()`, and `mv_usb2_phy_28nm_exit()`.

Control flow: Probe obtains clock and MMIO, creates the PHY, and registers the provider. Init enables the clock, programs PLL divider/ICP/LPF fields, powers PLL by register, powers TX analog, sets TX amplitude, RX squelch, digital sync/filter settings, powers OTG by register, then waits for PLL/impedance calibration, RX squelch calibration, and PLL ready. Power-on sets overwrite and VBUS/AVALID/BVALID bits in `PHY_28NM_CTRL_REG3`. Exit powers down PLL, TX analog, OTG, and disables the clock.

State and persistence: Clock and analog power persist from init until exit. VBUS override state is intended to be controlled by power-on/off.

Dependencies and integration points: Uses generic PHY, an unnamed clock, platform MMIO, and `marvell,pxa1928-usb-phy`. USB controllers use the PHY lifecycle callbacks.

Risks: `mv_usb2_phy_28nm_power_off()` appears to use `readl(...) | ~(mask)` instead of clearing the mask with `& ~mask`, which sets most bits and likely corrupts `CTRL_REG3`. Calibration failures disable the clock but leave already-programmed registers. There is no explicit PLL lock polling after later power-on.

Test signals: Init calibration on real hardware, VBUS override behavior, power-off register readback to catch the mask bug, USB enumeration, timeout injection, and clock enable balance through init failure and exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c -->
