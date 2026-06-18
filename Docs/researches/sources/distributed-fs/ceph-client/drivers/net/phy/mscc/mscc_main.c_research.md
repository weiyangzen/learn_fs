# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_main.c

Purpose: this is the main Microsemi/Microchip VSC85xx PHY driver. It registers phylib drivers for multiple VSC850x/VSC85xx parts, implements common copper PHY behavior, package-level initialization for multi-port devices, firmware patching for embedded 8051 microcontrollers, host SerDes setup, LED and ethtool stats support, Wake-on-LAN, MDIX/downshift tunables, interrupt handling, and integration with the MACsec/PTP helper files.

Important APIs and functions:
- `vsc85xx_probe_common()` allocates `struct vsc8531_private`, configures package joining, stats, LEDs, optional PTP probing, and DT/default LED modes.
- `vsc85xx_config_init()`, `vsc8584_config_init()`, and `vsc8514_config_init()` are the main per-family initialization paths.
- `phy_base_read/write()`, `vsc85xx_csr_read/write()`, `vsc8584_cmd()`, `phy_update_mcb_s6g()`, and `phy_commit_mcb_s6g()` are exported helpers used by PTP, MACsec, and SerDes code.
- `vsc8584_config_pre_init()`, `vsc8574_config_pre_init()`, and `vsc8514_config_pre_init()` apply package-wide analog tuning, firmware patching, microcontroller reset/deassert sequences, and SerDes preparation.
- `vsc8584_handle_interrupt()` dispatches timestamp FIFO interrupts, MACsec rollover interrupts, and link-change events for PTP/MACsec-capable packages.
- The `vsc85xx_driver[]` table binds PHY IDs to callbacks, capabilities, probe routines, and optional remove/link-change hooks.

Control flow: probe allocates private state, optionally computes edge-rate magic from DT, discovers package/base addresses, joins a phylib package, initializes PTP package-wide state once, then registers per-PHY PTP timestamper state when supported. During config init, simple single-PHY devices run RGMII delay setup, MAC interface selection, edge-rate programming, device-specific TR/EEE sequences, soft reset, and LED programming. Multi-port devices take the MDIO bus lock and execute package-wide pre-init only once via `phy_package_init_once()`, including broadcast writes, firmware CRC validation and patching, microcontroller reset control, LCPLL reset, host SerDes mode selection, and COMA release. After unlocking, VSC8584-class devices initialize MACsec, initialize PTP, select copper/SGMII operation, apply RGMII delay programming, soft reset, and LED modes.

State and persistence: `struct vsc8531_private` stores LED modes, stats accumulators, package address, PTP/MACsec pointers, locks, RX timestamp queue, and per-PHY base timestamp address. `struct vsc85xx_shared_private` stores the package-shared GPIO lock. Hardware state includes selected MDIO page, firmware in patch RAM, microcontroller reset/patch vector state, host SerDes mode, CSR/MCB register contents, interrupt masks, LED behavior, WOL MAC/password registers, RGMII delays, and PHY counters. Stats are read-and-accumulated because the hardware counters are narrow and likely clear or roll; the driver returns cumulative software totals.

Dependencies and integration points: integrates with phylib (`struct phy_driver`, page read/write callbacks, package helpers, interrupts, tunables, in-band caps), firmware loader (`request_firmware()` for VSC8584/VSC8574 firmware blobs), OF/DT properties for edge rate and legacy LED modes, Linux LED netdev triggers, ethtool stats/WOL APIs, and the local helper modules `mscc_macsec.c`, `mscc_ptp.c`, and `mscc_serdes.c`. Several low-level functions require the MDIO bus lock and emit diagnostics if called unlocked.

Risks and edge cases:
- Package initialization touches shared registers and uses broadcast writes; incorrect base address detection can affect every PHY in a package.
- Firmware patching failure is sometimes downgraded to a warning, leaving the device in a "non-optimal" state that still probes.
- `vsc85xx_csr_read()` returns `0xffffffff` on timeout, which can be indistinguishable from a valid all-ones register value to careless callers.
- Interrupt setup calls MACsec and PTP interrupt configuration unconditionally, relying on compile-time stubs for disabled features.
- LED DT handling diverges depending on a child `leds` node: when present, legacy properties are ignored and defaults are forced so LED class devices can own policy.
- Some initialization paths are highly order-sensitive around microcontroller reset, patch vectors, and SerDes calibration.

Test signals: boot/probe each supported PHY ID and interface mode; verify package init runs once under concurrent PHY probing; test firmware absent, bad CRC, and successful patch flows; validate SGMII/QSGMII/RGMII interface selection; exercise interrupts with link, MACsec, and timestamp sources; confirm WOL programming and wake; inspect ethtool stats accumulation; test LED class hardware-control get/set and brightness; verify suspend/resume and remove unregister PTP resources on PTP-capable drivers.
