# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_ethss.c

## Purpose
`netcp_ethss.c` implements the TI KeyStone NetCP Ethernet subsystem modules for 1G GBE, newer GBE NU/2U, and 10G XGBE switch hardware. It binds Ethernet subsystem device-tree nodes into NetCP module callbacks, maps the correct register layout for each hardware generation, initializes ALE/CPTS/statistics state, and attaches individual Linux netdevices to slave ports.

The file is the operational bridge between the generic `netcp` data path and the KeyStone Ethernet switch blocks. It handles port reset/configuration, SGMII/XGMII/RGMII link tracking, ALE address and VLAN programming, ethtool statistics, PHY-backed link settings, optional hardware timestamping, TX/RX NetCP hooks, secondary slave ports, and module registration for both `netcp-gbe` and `netcp-xgbe`.

## Important APIs, Types, And Functions
The central state containers are `struct gbe_priv`, `struct gbe_intf`, and `struct gbe_slave`. `gbe_priv` owns subsystem-wide device state: mapped register bases, version-specific register offsets, ALE/CPTS pointers, timer, statistics arrays, TX pipe, active interfaces, secondary ports, and hardware timestamp flags. `gbe_intf` binds one netdevice to a slave and TX pipe. `gbe_slave` represents a logical/physical switch port, PHY handle, link interface, MAC control value, timestamp controls, and per-port register bases.

Hardware layout structs include `xgbe_*_regs`, `gbenu_*_regs`, and `gbe_*_regs` plus offset structs used by `GBE_REG_ADDR()`. Large `struct netcp_ethtool_stat` tables map GBE 1.3/1.4, GBENU, and XGBE hardware statistics registers into ethtool strings and 64-bit accumulated counters.

NetCP module lifecycle entry points are `gbe_probe()`, `gbe_attach()`, `gbe_open()`, `gbe_close()`, `gbe_release()`, and `gbe_remove()`, shared by `gbe_module` and `xgbe_module`. Version-specific setup is split into `get_gbe_resource_version()`, `set_gbe_ethss14_priv()`, `set_gbenu_ethss_priv()`, and `set_xgbe_ethss10_priv()`.

Operational helpers include `gbe_slave_open()`, `gbe_slave_stop()`, `gbe_port_reset()`, `gbe_port_config()`, `gbe_sgmii_config()`, `gbe_sgmii_rtreset()`, `gbe_init_host_port()`, `netcp_ethss_update_link_state()`, `netcp_ethss_link_state_action()`, `gbe_adjust_link()`, `xgbe_adjust_link()`, and `netcp_ethss_timer()`.

Address, VLAN, and receive-mode APIs exposed to NetCP are `gbe_add_addr()`, `gbe_del_addr()`, `gbe_add_vid()`, `gbe_del_vid()`, and, for the two-port GBE variant, `gbe_set_rx_mode()`. Timestamp integration is through `gbe_hwtstamp_get()`, `gbe_hwtstamp_set()`, `gbe_txtstamp_mark_pkt()`, `gbe_rxtstamp()`, `gbe_register_cpts()`, and `gbe_unregister_cpts()` when `CONFIG_TI_CPTS` is enabled.

## Control Flow
Module initialization registers two primary NetCP modules: `netcp-gbe` and `netcp-xgbe`. During `gbe_probe()`, the driver validates the device-tree node, chooses maximum slave count from compatible strings, reads `tx-channel`, optional `tx-queue`, and `enable-ale`, maps hardware resources, initializes version-specific register offsets and stats tables, initializes the NetCP TX pipe, counts configured interface nodes, initializes optional secondary ports, creates the CPSW ALE, creates CPTS if present, starts the host port, resets statistics baselines, and starts a half-second timer for link/stat polling.

For `gbe` nodes, probing first maps the subsystem register block and reads `ss_version`; version 1.4 uses `set_gbe_ethss14_priv()`, while NU/2U uses `set_gbenu_ethss_priv()`. For `xgbe` nodes, `set_xgbe_ethss10_priv()` maps subsystem, switch-module, and SerDes resources, then calls `netcp_xgbe_serdes_init()`. Each setup path fills register-base pointers, ALE/CPTS offsets, host-port offsets, stats register bases, stats masks, and register-offset tables according to hardware generation.

`gbe_attach()` is called per interface netdevice. It allocates `gbe_intf` and a private `gbe_slave`, calls `init_slave()` against the interface node, copies the subsystem TX pipe into the interface pipe, installs `keystone_ethtool_ops`, links the interface into `gbe_intf_head`, and returns the per-interface private pointer.

`gbe_open()` configures runtime data-path state. It selects directed-to-port tagging for XGBE and NetCP 1.5/NU hardware, chooses switch destination based on ALE bypass, stops any previous slave state, disables priority elevation, enables statistics, sets switch control including FCS removal for MU hardware, opens the slave, registers TX and RX hooks, marks the slave open, immediately updates link state, and registers CPTS on first timestamp-capable open.

`gbe_slave_open()` configures the physical port. Non-2U SGMII ports are reset/configured and released from runtime reset, the EMAC is soft-reset, RX length and MAC control are written, the slave MAC is programmed, ALE forwarding and broadcast entries are installed, and PHYs are connected for SGMII/RGMII/XGMII MAC-PHY modes using `of_phy_connect()`. The adjust-link handler then calls back into `netcp_ethss_update_link_state()`.

Link state combines hardware-side link and PHY state. SGMII uses `netcp_sgmii_get_port_link()`, 2U RGMII reads `rgmii_status`, and PHY state comes from `phy->link` when a PHY exists. `atomic_xchg()` suppresses duplicate transitions. On link up, `netcp_ethss_link_state_action()` writes MAC control, enables ALE forwarding, and turns carrier on for non-MAC-PHY forced modes; on link down it clears MAC control, disables ALE forwarding, and turns carrier off for those same modes.

Transmit and receive integration is hook-based. `gbe_txhook()` assigns `p_info->tx_pipe` to the interface TX pipe and optionally arms CPTS TX timestamp completion. `gbe_rxhook()` performs CPTS RX timestamping if not already completed by a PHY. `gbe_close()` reverses the open path by unregistering CPTS, stopping the slave, unregistering NetCP hooks, clearing `open`, and resetting link state to invalid.

The periodic `netcp_ethss_timer()` polls open primary interfaces and secondary slave ports for link changes, then accumulates hardware stats under `hw_stats_lock`. Version 1.4 hardware has only two visible stats windows for four modules, so `gbe_update_stats_ver14()` flips `GBE_STATS_CD_SEL` to read A/B and C/D pairs.

## State And Persistence Behavior
All driver state is runtime kernel memory, devm-managed where possible. Register mappings, TX pipe ownership, slave lists, ALE/CPTS objects, stats arrays, and active VLAN bitmaps live for the module instance. Per-interface state lives from `attach` to `release`; per-port link state is stored in `atomic_t link_state` and `slave->open`.

Hardware state is programmed into Ethernet subsystem registers, ALE tables, SGMII/SerDes blocks, PHYs, and CPTS. ALE address entries, VLAN entries, port forwarding state, timestamp control registers, and switch control are persistent only until reset or reconfiguration. Hardware counters are accumulated into 64-bit software counters using 32-bit previous snapshots so ethtool reads survive register wrap while the driver instance lives.

Timestamp enablement is subsystem-wide in `gbe_priv->rx_ts_enabled` and `tx_ts_enabled`, but timestamp register programming is per slave through `gbe_hwtstamp()`. CPTS registration is reference-counted by `cpts_registered` so multiple open interfaces share one PHC registration.

## Dependencies And Integration Points
This file depends on the NetCP core (`netcp.h`), CPSW ALE (`cpsw_ale.h`), CPSW helpers (`cpsw.h`), CPTS (`cpts.h`), Linux OF/MDIO/PHY APIs, ethtool, VLAN, PTP classification, and timestamping APIs.

It calls helper functions exported from sibling files: `netcp_sgmii_reset()`, `netcp_sgmii_config()`, `netcp_sgmii_rtreset()`, `netcp_sgmii_get_port_link()`, and `netcp_xgbe_serdes_init()`. Device-tree bindings are central: compatible strings select hardware generation, resource indexes select register blocks, `interfaces` children define netdev-backed slave ports, `secondary-slave-ports` define non-netdev switch ports, and child `cpts` data configures the timestamp clock.

Netdevice integration is through ethtool ops, PHY ioctl forwarding, carrier state, PHY link-ksettings get/set, and NetCP module callbacks for open/close/address/VLAN/ioctl/hwtstamp. ALE integration controls learning, bypass, flooding, multicast, unicast, VLAN membership, and promiscuous-mode behavior.

## Risks And Edge Cases
Hardware-version branching is high risk. The same source drives several incompatible register layouts and stats window behaviors; wrong offsets or version detection can corrupt unrelated registers. GBE 1.4 stats require explicit visibility switching, and changing stats table sizes or module indexes can break ethtool output or counter accumulation.

Link mode handling has multiple special cases. SGMII/RGMII/XGMII MAC-PHY links use PHY callbacks, while MAC-MAC or no-MDIO modes use switch-side status and carrier handling. 2U RGMII bypasses SGMII reset/config and reads a different status register. Secondary ports attach PHYs to a dummy netdev and must not leak those PHY connections or dummy netdevs.

`gbe_set_rx_mode()` clears ALE entries and toggles learn/no-source-update across all ports for promiscuous mode. Timeout or ALE semantic changes can leave flooding or learning in an unexpected state. Address and VLAN additions replicate entries across active VLANs, so ordering between VLAN changes and address list updates matters.

Timestamping must coexist with PHY timestamp engines. The driver intentionally defers when `phy_has_txtstamp()`, `phy_has_rxtstamp()`, or `phy_has_hwtstamp()` is true. Incorrect detection can duplicate timestamps or hide hardware support. The CPTS disabled stubs return `-EOPNOTSUPP`, so callers must tolerate timestamp features disappearing by config.

Cleanup paths require care: `gbe_remove()` alerts if interfaces remain attached, stops the timer, releases CPTS/ALE/TX pipe, and frees secondary ports. Failure during probe after secondary-port setup must call `free_secondary_ports()`.

## Test Signals
Build coverage should include `CONFIG_TI_CPTS` enabled and disabled, GBE, GBENU/2U, and XGBE-compatible device-tree configurations, and PHY modes SGMII, RGMII, XGMII, MAC-MAC, and no-MDIO variants. Runtime validation should verify probe resource mapping, interface attach/open/close/release, carrier transitions, secondary-port PHY monitoring, ALE address and VLAN programming, promiscuous-mode toggling, FCS removal capability on MU hardware, and module unload cleanup.

Useful signals include ethtool stats increasing without discontinuities across 32-bit wraps, ethtool link-ksettings round trips, successful PTP `get_ts_info` and hwtstamp set/get when CPTS is present, TX/RX timestamp delivery, `phy_print_status()` link logs, absence of "unreleased ethss interfaces present", and no SerDes/SGMII lock errors during XGBE/SGMII open.
