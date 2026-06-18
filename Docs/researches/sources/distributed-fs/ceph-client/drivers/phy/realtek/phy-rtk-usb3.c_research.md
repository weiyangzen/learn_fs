# sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb3.c

Purpose: Implements Realtek RTD USB3 PHY initialization, calibration toggling, efuse/DT amplitude tuning, optional RX front-end offset correction, and debugfs reporting.

Important APIs/types/functions: Main types are `struct phy_cfg`, `struct phy_parameter`, `struct phy_reg`, and `struct rtk_phy`. PHY ops are `rtk_phy_init()`, `rtk_phy_exit()`, `rtk_phy_connect()`, and `rtk_phy_disconnect()`. Major helpers are `rtk_phy_read()`, `rtk_phy_write()`, `do_rtk_usb3_phy_toggle()`, `do_rtk_phy_init()`, `get_phy_data_by_efuse()`, `update_amplitude_control_value()`, and `parse_phy_data()`.

Control flow: Probe selects and copies the SoC config, fixes `num_phy` to one, maps the MDIO control register, reads DT amplitude controls, reads optional `usb_u3_tx_lfps_swing_trim` nvmem data, updates cached parameter entries, creates the PHY/provider, and registers debugfs. Init writes the parameter table unless default parameters are requested, optionally performs a one-time force-calibration toggle and debug-status check, and may loop through RX offset range adjustments followed by another toggle. Connect/disconnect callbacks rerun the calibration toggle when enabled.

State and persistence: The copied `phy_cfg` is mutable: one-time toggles can clear `do_toggle`, and amplitude/efuse updates alter cached register data. Per-PHY state stores MDIO base and tuning values. MDIO register writes persist in the USB3 PHY until reset or reinit.

Dependencies and integration points: Depends on generic PHY, OF MMIO, nvmem, USB debugfs root, and Realtek DWC USB wrappers. Compatible data covers RTD1295, RTD1319, RTD1319D, RTD1619, and RTD1619B.

Risks: `rtk_phy_read()`/`write()` ignore busy-wait return values after issuing the command, so MDIO timeout failures can be masked. `of_iomap()` is not devm-managed. The port bounds check allows `port == num_phy`. RX offset correction can recurse through `goto do_toggle` and should be verified against hardware convergence.

Test signals: Probe each compatible, verify debugfs output, check efuse and DT amplitude updates at registers 0x20/0x21, run SuperSpeed enumeration and disconnect/reconnect cycles, validate one-time toggle status bit behavior, and force RX offset edge values on RTD1319D.
