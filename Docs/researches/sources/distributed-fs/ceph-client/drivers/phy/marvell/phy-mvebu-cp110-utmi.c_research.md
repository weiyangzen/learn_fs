<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c

Purpose: Implements CP110 UTMI USB2 PHY support for two ports, including host/peripheral muxing, PLL sharing, per-port analog tuning, and optional D+/D- lane swapping.

Important APIs and types: `struct mvebu_cp110_utmi` stores UTMI MMIO, system-controller regmap, device, and ops. `struct mvebu_cp110_utmi_port` stores port id, USB data role, and `swap_dx`. Main helpers are `mvebu_cp110_utmi_port_setup()`, `mvebu_cp110_utmi_phy_power_on()`, and `mvebu_cp110_utmi_phy_power_off()`.

Control flow: Probe resolves `marvell,system-controller`, maps registers, iterates child ports, validates `reg`, derives role via `of_usb_get_dr_mode_by_phy()`, permits only one peripheral port, reads parent `swap-dx-lanes`, creates each PHY, and powers it off. Power-on first powers the port off, configures the device mux if peripheral, sets test suspend/select, waits for power down, programs PLL dividers, impedance threshold, TX amplitude, squelch, charger-detect voltages, and D+/D- swap, powers up the port in syscon, clears test select, then polls impedance calibration, PLL calibration, and PLL ready before enabling the shared PLL bit. Power-off clears the port power bit and powers down the shared PLL only if no port remains active.

State and persistence: Role, port id, and swap setting are per-port software state. Shared PLL state is inferred from syscon port bits at power-off rather than refcounted in software.

Dependencies and integration points: Uses generic PHY, syscon regmap, USB OF role helpers, child DT nodes, and a parent-level `swap-dx-lanes` property. Consumers are USB host/device controllers.

Risks: `regmap_test_bits()` error handling is minimal; negative errors are treated as non-active and may allow PLL shutdown. Role conflicts are downgraded to host mode rather than failing probe. Power-on modifies the global USB device mux, so dual-role board descriptions must be precise.

Test signals: Two-port probe, host/peripheral mux selection, one-device-only fallback, D+/D- swap boards, simultaneous port use with shared PLL retention, calibration timeout paths, and USB2 enumeration after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c -->
