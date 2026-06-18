<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c

## Purpose

`phy-mxs-usb.c` is the Freescale/NXP MXS/i.MX USB PHY driver. It powers and resets USB PHY blocks, handles SoC-specific errata, controls clocks/regulators/PLL, tunes TX calibration from DT, manages wakeup and suspend behavior, detects charger type through anatop registers, and registers a legacy USB2 PHY.

## Important APIs, Types, and Functions

`struct mxs_phy_data` stores SoC quirk flags; `struct mxs_phy` stores the USB PHY, clock, SoC data, anatop/SIM regmaps, port ID, TX calibration mask/value, and 3.0 V regulator. Important functions include `mxs_phy_init()`, `mxs_phy_shutdown()`, `mxs_phy_suspend()`, `mxs_phy_set_wakeup()`, `mxs_phy_on_connect()`, `mxs_phy_on_disconnect()`, charger detection helpers, `mxs_phy_probe()`, `mxs_phy_remove()`, and system PM helpers.

## Control Flow

Probe maps the PHY resource, gets the clock, optional anatop and SIM syscon regmaps, parses TX calibration properties, reads `usbphy` alias as port ID, fills legacy PHY callbacks, gets SoC match data and optional `phy-3p0` regulator, sets wakeup capability, and registers the PHY. Init delays for clock switching, enables the clock, optionally powers i.MX7ULP PLL, resets the PHY block, enables regulator, powers up, sets auto clock/power bits, applies IP fixes and charger-detect disable, and writes TX calibration. Shutdown clears wake/auto bits, powers down, gates clock, disables PLL/regulator, and disables the clock.

Suspend powers down most PHY circuits and gates the clock, with a low-speed/VBUS exception and PHY2 hardware-clock-control exception. Resume re-enables clock, ungates, and powers up. Wakeup toggles PHY wake bits and may force line disconnect through anatop loopback registers. Charger detection performs data-contact, primary, and secondary detection sequences.

## State and Persistence Behavior

State is per-device plus hardware registers in PHY, anatop, SIM, regulator, and clock frameworks. TX calibration derived from DT persists in PHY TX register after init. Wakeup, disconnect-line, PLL, and charger-detect states persist until changed.

## Dependencies and Integration Points

The driver depends on STMP reset helpers, platform MMIO, clocks, syscon/regmap, OF match data and aliases, regulators, USB PHY callbacks, and i.MX/MXS analog register conventions.

## Risks and Test Signals

This source tree has visible textual defects: duplicated `void __iomem *base;` in probe and an extra comment terminator in charger-disable code, both strong build-failure signals. Functional risks include quirk flag mismatch, port ID errors, anatop absent paths, charger-detect timing, and clock gating around wake. Tests should include build/static analysis, every compatible string, optional anatop/SIM/regulator paths, TX calibration bounds, init/shutdown, suspend/resume low-speed and high-speed devices, wakeup enable/disable, connect/disconnect notifications, charger SDP/CDP/DCP detection, and probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c -->
