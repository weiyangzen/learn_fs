# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.c

## Purpose
`thunder_bgx.c` is the Thunder BGX/RGX physical MAC driver. It probes BGX/RGX PCI functions, discovers LMAC modes configured by firmware, initializes SGMII/XAUI-family MAC blocks, manages link state via PHY callbacks or polling, exports services used by the NIC PF for VF-facing operations, maintains per-LMAC DMAC multicast filters, configures PFC/timestamping/loopback, and reports BGX hardware counters.

## Important APIs, Types, and Functions
Exported APIs include `bgx_get_map`, `bgx_get_lmac_count`, `bgx_get_lmac_link_state`, `bgx_get_lmac_mac`, `bgx_set_lmac_mac`, `bgx_set_dmac_cam_filter`, `bgx_set_xcast_mode`, `bgx_reset_xcast_mode`, `bgx_lmac_rx_tx_enable`, `bgx_config_timestamping`, `bgx_lmac_get_pfc`, `bgx_lmac_set_pfc`, `bgx_get_rx_stats`, `bgx_get_tx_stats`, and `bgx_lmac_internal_loopback`. Internal state is modeled with `struct bgx`, `struct lmac`, and `struct dmac_map`.

## Control Flow and Integration
Probe enables PCI resources, maps BGX registers, determines node/BGX id and maximum LMAC count, registers the BGX in the global `bgx_vnic` array, initializes RGX/XCV when applicable, reads LMAC mode/lane/training state from firmware-programmed registers, allocates dummy netdevs for PHY linkage, initializes ACPI or OF PHY/MAC data, clears global MAC filter/steering state, registers interrupts, and enables each LMAC. LMAC enable chooses SGMII/QSGMII/RGMII or XAUI/XFI/XLAUI/KR initialization, configures FCS/pad/min packet behavior, allocates DMAC filter tracking, connects PHYs when present, or starts periodic link polling.

Link changes flow through either `bgx_lmac_handler` from PHYLIB or `bgx_poll_for_link`/`bgx_poll_for_sgmii_link`. SGMII changes temporarily disable RX/TX, wait for idle, reprogram speed/duplex slot timing, then restore packet flow. XAUI-family links check SPU/SMU status and may reinitialize on receive faults. VF multicast/promiscuous requests are mediated by exported xcast/filter functions and program BGX CAM entries only after tracking per-VF references.

## State and Persistence
State is volatile and global within the module: `bgx_vnic[]`, `max_bgx_per_node`, total `lmac_count`, per-BGX register base and flags, per-LMAC MAC address, type, lane mapping, training/autoneg flags, current/last link settings, PHY pointer, workqueue, and DMAC filter reference map. Hardware registers hold MAC configuration, counters, filter CAMs, pause settings, timestamp enablement, and interrupt state.

## Dependencies and Risks
The file depends on PCI, ACPI, OF/MDIO, PHYLIB, netdevice dummy devices, `nic.h`, `nic_reg.h`, `thunder_bgx.h`, and `thunder_xcv.c` exported symbols for RGX. Risks include global indexing assumptions across nodes and BGX ids, cleanup on partial probe failures, races between VF filter changes and link/MAC reconfiguration, PHY reference lifetime in deferred probe, firmware-dependent LMAC mode discovery, and polling workqueue teardown correctness.

## Test Signals
Useful signals are probe/remove on CN81xx/CN83xx/CN88xx and RGX variants, ACPI and DT PHY discovery including `-EPROBE_DEFER`, link up/down at 10/100/1000/10000/40000 modes, PFC get/set, timestamp enable/disable, loopback, multicast filter reference sharing across VFs, BGX counter reads, TX underflow interrupt recovery, and repeated module unload during active link polling.
