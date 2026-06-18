<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c

Purpose: Supports Armada CP110 COMPHY lanes for PCIe, SATA, USB3 host/device, and several Ethernet SerDes modes. It prefers firmware SMC configuration and falls back to in-kernel legacy programming for a subset of Ethernet modes.

Important APIs and types: `struct mvebu_comphy_priv` holds MMIO base, system-controller regmap, clocks, device, and physical base passed to firmware. `struct mvebu_comphy_lane` stores lane id, mode/submode, and selected port. `mvebu_comphy_cp110_modes[]` is the lane/port/mode matrix. Key functions include `mvebu_comphy_smc()`, `mvebu_comphy_get_fw_mode()`, `mvebu_comphy_power_on()`, `mvebu_comphy_power_on_legacy()`, and `mvebu_comphy_set_mode()`.

Control flow: Probe resolves syscon, maps the COMPHY resource, tries to enable management and AXI clocks for compatibility, records the physical base, creates lane PHYs, and registers a custom xlate that records the port argument. `set_mode` normalizes 1000Base-X to SGMII, validates the lane/port/mode combination, and treats PCIe submode as width. Power-on builds a firmware parameter encoding mode, port, speed, polarity, and width, then calls `COMPHY_SIP_POWER_ON`. On firmware failure or unsupported call, it falls back to selector programming and legacy Ethernet sequences for SGMII/2500Base-X/RXAUI/10GBASE-R. Legacy paths program muxes, reset lanes, configure PLL/rate/DFE/equalization/training registers, poll PLL and RX init, then assert digital reset. Power-off similarly tries firmware first and clears resets/selectors in legacy fallback.

State and persistence: Lane mode, submode, and port are cached until changed. Hardware configuration is persistent in COMPHY and system-controller registers or firmware-owned state. Clocks are enabled for the device lifetime unless probe fails.

Dependencies and integration points: Integrates with ARM SMCCC firmware services, generic PHY consumers, CP110 syscon, named clocks, OF lane child nodes, and Ethernet/PCIe/SATA/USB controller phandles.

Risks: Firmware support level determines behavior; unsupported SMC calls leave Linux fallback available only for Ethernet modes, not SATA/USB/PCIe. Lane/port matrix errors can silently route PHYs incorrectly. PCIe width uses the `submode` integer. Clock initialization failures except defer are tolerated, which preserves DT compatibility but can hide hardware setup issues.

Test signals: Firmware and legacy paths, all lane/port combinations, SGMII/2500Base-X/RXAUI/5G/10G Ethernet links, PCIe width encoding, USB3 host/device, SATA, SMC error fallback, PLL/RX timeout handling, and suspend/resume after hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c -->
