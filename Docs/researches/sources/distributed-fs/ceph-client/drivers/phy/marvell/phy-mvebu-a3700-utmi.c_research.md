<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c

Purpose: Provides Armada 3700 UTMI USB2 PHY support for both the USB3/USB2 OTG-connected PHY and the host-only USB2 PHY.

Important APIs and types: `struct mvebu_a3700_utmi_caps` distinguishes OTG/USB3-side versus host-side register layout via `usb32`. `struct mvebu_a3700_utmi` stores PHY registers, USB misc syscon regmap, capabilities, and PHY handle. Main callbacks are `mvebu_a3700_utmi_phy_power_on()` and `mvebu_a3700_utmi_phy_power_off()`.

Control flow: Probe maps UTMI registers, resolves `marvell,usb-misc-reg`, selects match-data caps, creates a PHY, powers it off, and registers an OF provider. Power-on programs PLL reference/feedback divisors for 25 MHz boards, enables misc pull-up and clears suspend, powers OTG and disables charger detection/pull-downs for `usb32`, then polls PLL calibration, impedance calibration, squelch calibration, and PLL ready. Power-off clears pull-up and suspend bits and powers down OTG if applicable.

State and persistence: The only software state is caps and regmap handles. PLL and calibration state persists in UTMI hardware. The driver does not cache calibration completion.

Dependencies and integration points: Uses generic PHY, platform MMIO, syscon regmap, and compatible-specific match data. USB controllers consume it through simple PHY phandles.

Risks: `power_off()` reads `USB2_PHY_CTRL(usb32)` from the UTMI MMIO base even though power-on updates that register through the USB misc regmap, which is suspicious if those address spaces differ. Calibration polling can delay up to one second per stage. The code assumes current boards use 25 MHz despite comments about older 40 MHz defaults.

Test signals: Probe both OTG and host compatibles, syscon lookup, USB2 host and OTG enumeration, charger-detection-disabled behavior, calibration timeout injection, and suspend/resume readback of misc pull-up/suspend bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c -->
