<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c

Purpose: Provides a USB PHY driver for Marvell Berlin2 and Berlin2CD/Q. It programs PLL, analog, RX, and TX tuning registers and registers a single generic PHY for USB controller consumers.

Important APIs and types: `struct phy_berlin_usb_priv` carries the MMIO base, reset control, and compatible-selected PLL divider. `phy_berlin_usb_power_on()` is the only PHY callback. `phy_berlin_pll_dividers[]` supplies different divider values through OF match data.

Control flow: Probe maps the resource, obtains the reset control, loads match-data PLL divider, creates a PHY, and registers `of_phy_simple_xlate`. Power-on resets the PHY block, writes PLL divider and PLL control bits, configures analog VCO/test settings, RX squelch/disconnect/filter parameters, TX voltage/amplitude, impedance calibration settings, and final drive/slew masks.

State and persistence: The driver keeps only immutable tuning choices and the reset line. Register state persists in hardware after `power_on`; there is no explicit power-off callback to undo or reset the block.

Dependencies and integration points: Uses generic PHY, reset framework, platform MMIO, OF match data, and USB controller phandles. Compatible strings distinguish Berlin2 from Berlin2CD/Q divider setup.

Risks: There is no polling for PLL lock or calibration completion, so failed hardware bring-up can surface only later in the USB controller. `device_get_match_data()` is assumed non-NULL. Repeated TX control writes deliberately pulse calibration-related fields, so reordering may break analog setup.

Test signals: Probe on both compatible strings, reset assertion/deassertion traces, USB host/device enumeration, high-speed signal quality, repeated PHY power-on through controller reset, and register dumps confirming divider selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c -->
