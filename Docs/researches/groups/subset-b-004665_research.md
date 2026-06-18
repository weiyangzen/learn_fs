# Research: subset-b-004665

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_ethss.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_ethss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_sgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_sgmii.c

## Purpose
`netcp_sgmii.c` provides the small SGMII register helper layer used by the TI KeyStone NetCP Ethernet subsystem. It resets SGMII ports, toggles runtime reset, reports port link state, and programs SGMII control/advertisement values for MAC-MAC autonegotiation, MAC-PHY, forced MAC-MAC, and fiber-style modes.

The file is not a standalone driver. It is called by `netcp_ethss.c` during slave open/stop and periodic link polling.

## Important APIs, Types, And Functions
The exported helper APIs are `netcp_sgmii_reset()`, `netcp_sgmii_rtreset()`, `netcp_sgmii_get_port_link()`, and `netcp_sgmii_config()`. All take a mapped SGMII base pointer and a zero-based port number.

Internal helpers are `sgmii_write_reg()`, `sgmii_read_reg()`, and `sgmii_write_reg_bit()`. Register address macros calculate per-port offsets with `SGMII_OFFSET()`, using a separate formula for ports 2 and 3 so callers can pass the appropriate base for SGMII 3/4 windows.

Important register bits are `SGMII_SRESET_RESET`, `SGMII_SRESET_RTRESET`, `SGMII_REG_STATUS_LOCK`, `SGMII_REG_STATUS_LINK`, `SGMII_REG_STATUS_AUTONEG`, and `SGMII_REG_CONTROL_AUTONEG`.

## Control Flow
`netcp_sgmii_reset()` sets the soft-reset bit in the per-port reset register and busy-waits until hardware clears it. There is no timeout in this loop, so it assumes the SGMII block is responsive.

`netcp_sgmii_rtreset()` reads the reset register, returns the previous runtime-reset bit value, sets or clears the bit according to the caller, writes the result, and issues a write memory barrier. `netcp_ethss.c` uses this to hold non-XGMII ports in reset while stopping and to release them while opening.

`netcp_sgmii_get_port_link()` reads the status register and returns `1` when `SGMII_REG_STATUS_LINK` is set, otherwise `0`.

`netcp_sgmii_config()` first translates the `link-interface` value into MR advertisement and control register values. It supports `SGMII_LINK_MAC_MAC_AUTONEG`, `SGMII_LINK_MAC_PHY`, `SGMII_LINK_MAC_PHY_NO_MDIO`, `SGMII_LINK_MAC_MAC_FORCED`, and `SGMII_LINK_MAC_FIBER`; unsupported values trigger `WARN_ONCE()` and `-EINVAL`. The function clears control, waits up to 1000 one-to-two millisecond sleeps for SerDes PLL lock, logs an error if lock is absent, writes advertisement and control, then waits up to 1000 short sleeps for link and, when autoneg is enabled, autoneg completion.

## State And Persistence Behavior
The file maintains no software state. It mutates memory-mapped SGMII registers. Reset, runtime reset, advertisement, and control settings persist in hardware until changed or reset. Link state is read directly from hardware each time.

## Dependencies And Integration Points
The file includes `netcp.h` for link-interface constants, MMIO helpers, bit macros, sleeps, and warning/logging infrastructure. Its only consumers in this work item are `netcp_ethss.c` helper paths: `gbe_sgmii_config()`, `gbe_sgmii_rtreset()`, and `netcp_ethss_update_link_state()`.

The base pointer passed by `netcp_ethss.c` differs by hardware generation and slave index through `SGMII_BASE()`, so the offset math here relies on the caller selecting the right window for ports 0/1 versus 2/3.

## Risks And Edge Cases
`netcp_sgmii_reset()` can spin forever if hardware never clears the reset bit. `netcp_sgmii_config()` logs PLL lock failure but still proceeds to program advertisement/control and returns success even if final link/autoneg polling times out. Callers therefore cannot distinguish a failed link setup from a slow or absent link by return code.

The port offset logic is compact but sensitive to caller assumptions. Passing a port greater than expected or the wrong SGMII base can program the wrong register window. Interface constants must stay aligned with `netcp.h` and device-tree `link-interface` values.

## Test Signals
Test with SGMII MAC-PHY, MAC-PHY no-MDIO, forced MAC-MAC, MAC-MAC autoneg, and fiber configurations. Hardware or emulation tests should confirm reset completion, runtime reset bit preservation/return value, PLL lock logging, link/autoneg polling, and correct port offset selection for ports 0 through 3. Watch for "serdes PLL not locked" and `WARN_ONCE` invalid-interface messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_sgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_xgbepcsr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_xgbepcsr.c

## Purpose
`netcp_xgbepcsr.c` initializes the TI KeyStone XGBE PCS-R/SerDes block used by the NetCP 10G Ethernet subsystem. It applies fixed PHY-B CMU, lane, and common-lane register programming sequences, enables the PLL and two XGMII lanes, waits for PLL lock, enables XGMII ports in the switch registers, and performs a short link-lane recovery check.

This is a hardware bring-up helper for `netcp_ethss.c`; it exports only `netcp_xgbe_serdes_init()`.

## Important APIs, Types, And Functions
`struct serdes_cfg` stores register offset, value, and mask triples. Static configuration arrays `cfg_phyb_1p25g_156p25mhz_cmu0`, `cfg_phyb_10p3125g_156p25mhz_cmu1`, `cfg_phyb_10p3125g_16bit_lane`, `cfg_phyb_10p3125g_comlane`, and `cfg_cm_c1_c2` encode the hard-coded SerDes setup.

The public entry point is `netcp_xgbe_serdes_init(void __iomem *serdes_regs, void __iomem *xgbe_regs)`. It checks whether COMLANE appears active, toggles POR reset if needed, and then calls `netcp_xgbe_serdes_config()`.

Configuration helpers include `netcp_xgbe_serdes_cmu_init()`, `netcp_xgbe_serdes_lane_config()`, `netcp_xgbe_serdes_com_enable()`, `netcp_xgbe_serdes_lane_enable()`, `netcp_xgbe_serdes_pll_disable()`, `netcp_xgbe_serdes_pll_enable()`, `netcp_xgbe_wait_pll_locked()`, and `netcp_xgbe_serdes_enable_xgmii_port()`.

Lane diagnostics and recovery helpers include `netcp_xgbe_serdes_read_tbus_val()`, `netcp_xgbe_serdes_write_tbus_addr()`, `netcp_xgbe_serdes_read_select_tbus()`, `netcp_xgbe_serdes_reset_cdr()`, `netcp_xgbe_check_link_status()`, and `netcp_xgbe_serdes_check_lane()`.

## Control Flow
`netcp_xgbe_serdes_init()` reads SerDes offset `0xa00`. If any low COMLANE bits are set, it logs a debug reset message and calls `netcp_xgbe_reset_serdes()`, which toggles `POR_EN` in `PCSR_CPU_CTRL_OFFSET` with short sleeps. It then enters `netcp_xgbe_serdes_config()`.

`netcp_xgbe_serdes_config()` disables the PLL, applies CMU0 and CMU1 arrays, applies the lane configuration array to both lanes with a `0x200 * lane` stride, disables per-lane autonegotiation and link training, applies common-lane configuration, applies CM/C1/C2 setup for both lanes, enables the PLL, writes lane enable/rate values for both lanes, and waits up to 500 ms for both SGMII status lock bits in the XGBE switch register block.

If PLL lock succeeds, the function writes `0x03` to the XGBE control register to enable both XGMII ports, then calls `netcp_xgbe_serdes_check_lane()`. Lane checking calls `netcp_xgbe_check_link_status()` up to two times separated by 100 ms. That routine checks loss, PCS-R block lock, block error saturation, and a small state machine per lane. When block errors are saturated or block lock is missing, it can reset CDR if TBUS DLPF appears out of center; when link is good it forces signal detect on.

`netcp_xgbe_serdes_config()` returns the PLL-lock result. The later lane-check timeout is logged but not propagated because the return value remains the PLL result.

## State And Persistence Behavior
There is no persistent software state. All state is in hardware registers: CMU/lane/common-lane SerDes programming, PLL enable, lane enable/rate registers, XGBE control bits, PCS-R block error counters, signal-detect overrides, CDR reset bits, and POR state.

The lane-check function keeps local `current_state[2]` and `lane_down[2]` arrays only for the duration of initialization. The static configuration tables are immutable driver data.

## Dependencies And Integration Points
The file includes `netcp.h` for MMIO, bit, timing, and logging helpers. It is integrated from `netcp_ethss.c` in the XGBE probe path after XGBE subsystem, switch-module, and SerDes resources are mapped.

The code assumes a two-lane PHY-B layout, 156.25 MHz reference clock, 10.3125G lane configuration, and XGBE switch status offsets at `XGBE_SGMII_1_OFFSET` and `XGBE_SGMII_2_OFFSET`. Comments call out some EVM plus RTM-BOC-specific equalization settings.

## Risks And Edge Cases
The configuration is fixed and board-specific. Different reference clocks, lane counts, PHY variants, or board loss characteristics may need different magic values. `PHY_A(serdes)` is hard-coded to `0`, so only the PHY-B TBUS path is active.

PLL lock failure returns `-ETIMEDOUT`, but lane link failure after PLL lock is not propagated to the caller. This means probe can continue even when `netcp_xgbe_serdes_check_lane()` times out. The lane check itself retries only twice, so it is a weak readiness signal.

`MASK_WID_SH(w, s)` uses `1 << w`, which is safe for the current small widths but would overflow if reused for 32-bit masks. TBUS addressing remaps lane select values for two-lane PHY-B; extending to other layouts requires care.

## Test Signals
Hardware validation should confirm SerDes init on cold boot and after an already-active COMLANE reset, PLL lock within 500 ms, XGMII control enabling both ports, PCS-R block lock on both lanes, block error counter clearing, and stable link after repeated probe/remove cycles. Useful logs include "XGBE serdes not locked: time out", "XGBE: timeout waiting for serdes link up", lane-down debug messages, and CDR centering debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_xgbepcsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.c

## Purpose
`tlan.c` is the Linux netdevice driver for legacy Texas Instruments ThunderLAN-based Ethernet adapters, including Compaq Netelligent/NetFlex PCI and EISA devices and selected Olicom boards. It discovers PCI and EISA devices, allocates descriptor rings, reads MAC addresses from serial EEPROM, drives the ThunderLAN host/DIO/MII/EEPROM register interfaces, manages PHY reset/autonegotiation/link monitoring, handles interrupts, transmits and receives frames, exposes MII ioctls and basic ethtool EEPROM access, and supports suspend/resume.

The file is a complete classic Ethernet driver with custom DMA descriptor rings rather than a phylib-driven modern design.

## Important APIs, Types, And Functions
Module parameters are `aui[]`, `duplex[]`, `speed[]`, and `debug`. These select per-board media behavior and debug masks. `board_info[]` describes supported board labels, adapter flags, and EEPROM MAC offsets. `tlan_pci_tbl[]` maps PCI IDs to `board_info` entries.

The main private state type is `struct tlan_priv` from `tlan.h`. It stores PCI/netdev pointers, coherent descriptor storage, RX/TX ring pointers and DMA addresses, ring indexes, PHY state, timers, adapter metadata, media settings, selected PHY addresses, spinlock, and timeout work item.

Driver lifecycle functions are `tlan_probe()`, `tlan_init_one()`, `tlan_probe1()`, `tlan_remove_one()`, `tlan_eisa_probe()`, `tlan_eisa_cleanup()`, and `tlan_exit()`. Netdevice operations are `tlan_open()`, `tlan_close()`, `tlan_start_tx()`, `tlan_tx_timeout()`, `tlan_get_stats()`, `tlan_set_multicast_list()`, and `tlan_ioctl()`. Optional netpoll uses `tlan_poll()`.

Interrupt handling uses `tlan_handle_interrupt()` plus the `tlan_int_vector[]` table, dispatching to `tlan_handle_tx_eof()`, `tlan_handle_stat_overflow()`, `tlan_handle_rx_eof()`, `tlan_handle_dummy()`, `tlan_handle_tx_eoc()`, `tlan_handle_status_check()`, and `tlan_handle_rx_eoc()`.

Hardware setup and ring helpers include `tlan_init()`, `tlan_start()`, `tlan_stop()`, `tlan_reset_lists()`, `tlan_free_lists()`, `tlan_read_and_clear_stats()`, `tlan_reset_adapter()`, `tlan_finish_reset()`, and `tlan_set_mac()`.

PHY, MII, and EEPROM routines include `tlan_phy_detect()`, `tlan_phy_power_down()`, `tlan_phy_power_up()`, `tlan_phy_reset()`, `tlan_phy_start_link()`, `tlan_phy_finish_auto_neg()`, `tlan_phy_monitor()`, `__tlan_mii_read_reg()`, `tlan_mii_read_reg()`, `__tlan_mii_write_reg()`, `tlan_mii_write_reg()`, `tlan_mii_send_data()`, `tlan_mii_sync()`, `tlan_ee_send_start()`, `tlan_ee_send_byte()`, `tlan_ee_receive_byte()`, and `tlan_ee_read_byte()`.

## Control Flow
Module initialization registers the PCI driver and then scans EISA slots. If no PCI or EISA devices were installed, it unregisters the PCI driver and returns `-ENODEV`. EISA probing checks slot IDs, enable state, IRQ encoding, reserves the I/O region, and calls the shared `tlan_probe1()` path.

`tlan_probe1()` enables PCI and reserves I/O resources when `pdev` is present, allocates an Ethernet netdev, selects board metadata from PCI driver data or EISA ID, sets DMA mask, finds an I/O BAR for PCI, records IRQ/base/revision, applies module or legacy `mem_start` media parameters, initializes timeout work and the spinlock, calls `tlan_init()`, and registers the netdev. EISA devices are linked onto `tlan_eisa_devices` for manual cleanup.

`tlan_init()` allocates one coherent DMA block for RX and TX `struct tlan_list` descriptors, aligns the RX list to 8 bytes, places TX descriptors immediately after RX descriptors, reads six MAC bytes from EEPROM at the board-specific offset, swaps bytes for Olicom boards using offset `0xf8`, assigns the hardware address, turns carrier off, installs netdev and ethtool ops, and sets the watchdog timeout.

Opening the device requests the shared IRQ, initializes the primary timer and media timer, reads the ThunderLAN revision, and calls `tlan_start()`. `tlan_start()` resets descriptor lists, clears stats, resets the adapter, and wakes the queue. Closing calls `tlan_stop()`, frees the IRQ, and frees all SKBs/DMA mappings in the rings.

Transmit starts in `tlan_start_tx()`. If the PHY is not online, the skb is dropped as successfully consumed. Otherwise the skb is padded to minimum Ethernet size, mapped for DMA, stored in the next TX descriptor, and the descriptor is marked ready under `priv->lock`. If TX is idle, the driver writes the descriptor DMA address to `TLAN_CH_PARM` and issues `TLAN_HC_GO`; otherwise it links the previous descriptor's `forward` pointer. The skb pointer is hidden in descriptor buffer slots 8 and 9 by `tlan_store_skb()`.

Interrupt handling reads `TLAN_HOST_INT`, extracts the interrupt type, acknowledges the host interrupt register, calls the vector handler, and writes an ACK command when the handler returns nonzero bits. TX EOF processing walks completed descriptors, unmaps and frees SKBs, updates byte stats, marks descriptors unused, restarts queued TX if an end-of-channel occurred, and pulses the activity LED. RX EOF processing walks completed RX descriptors, allocates replacement SKBs, unmaps and delivers received SKBs through `netif_rx()`, remaps replacements, appends descriptors back to the ring, restarts RX on EOC, and pulses the activity LED.

Status-check interrupts handle two different paths. Adapter-check interrupts stop the queue, log the adapter error from `TLAN_CH_PARM`, clear stats, issue adapter reset, schedule timeout work, and suppress normal ACK. Network status checks clear DIO status bits and, for internal PHY interrupts, adjust polarity swap in `TLAN_TLPHY_CTL` when needed.

Reset and link bring-up are timer-driven. `tlan_reset_adapter()` asserts adapter reset, disables interrupts, clears address/hash registers, configures NetConfig, loads timers/thresholds, unresets MII, disables TX/RX EOC interrupts on newer chips, detects PHYs, selects bit-rate/AUI/full-duplex behavior, powers down managed PHYs, or finishes reset immediately for unmanaged PHYs. Timers then sequence PHY power-up, PHY reset, link start, autonegotiation finish, and final reset completion.

`tlan_finish_reset()` enables NET_CMD/NET_MASK/MAX_RX, reads PHY IDs/status, reports link details for National Semiconductor PHYs, enables internal PHY interrupts, programs AREG0 with the netdev MAC, enables host interrupts, starts the RX channel with `TLAN_HC_GO | TLAN_HC_RT`, sets link LED/carrier, and applies multicast filters. If link is inactive it retries after ten seconds.

## State And Persistence Behavior
Persistent host-visible configuration is limited to module parameters and netdevice settings. Runtime state lives in `struct tlan_priv`: descriptor rings, ring heads/tails, DMA addresses, PHY selection, media choices, timers, carrier state, and stats. Hardware state is programmed into I/O port registers, DIO internal registers, MII PHY registers, EEPROM reads, descriptor lists, and adapter command registers.

Descriptor rings persist while the netdev exists. RX SKBs are allocated and DMA-mapped in `tlan_reset_lists()` and recycled by RX EOF; TX SKBs remain mapped until TX EOF or ring free. Hardware statistics registers clear as a side effect of reading; the driver accumulates them into `dev->stats` only when `record` is true.

The serial EEPROM is read for MAC and ethtool dump access; the driver does not write EEPROM. PHY link and media behavior are volatile and renegotiated after reset, link loss, timeout, suspend/resume, or internal/external PHY switching.

## Dependencies And Integration Points
The file depends on `tlan.h`, PCI, EISA, DMA mapping, netdevice, etherdevice, MII ioctl helpers, timers, workqueues, spinlocks, I/O port accessors, and module infrastructure. It integrates with the kernel through `struct pci_driver`, `struct net_device_ops`, `struct ethtool_ops`, `SIMPLE_DEV_PM_OPS`, shared IRQ handling, netpoll when enabled, and legacy MII ioctls (`SIOCGMIIPHY`, `SIOCGMIIREG`, `SIOCSMIIREG`).

Hardware integration is strongly tied to ThunderLAN DIO registers, host command/status registers, descriptor format, internal PHY registers, external MII devices, and Microchip-style serial EEPROM signaling over `TLAN_NET_SIO`.

## Risks And Edge Cases
This is legacy I/O-port hardware with hand-rolled MII, EEPROM, timers, and DMA rings. Concurrency relies on `priv->lock` across IRQ, ioctl, timer, and EEPROM/MII paths; lock ordering or missed locking can corrupt serial bus transactions or ring state.

Several paths assume PCI device context even for EISA. DMA allocation/free calls use `priv->pci_dev->dev`, so EISA cleanup and init paths are sensitive to how `pci_dev` is represented. Probe and cleanup error paths must avoid freeing coherent memory when allocation failed.

RX refill can run out of memory. If replacement SKB allocation fails, the code reuses the descriptor after `drop_and_reuse` without having unmapped/delivered the old SKB, which avoids immediate allocation failure but requires careful descriptor state preservation. TX ring full returns `NETDEV_TX_BUSY` after stopping the queue, and TX timeout resets rings and adapter.

`netcp`-style phylib abstractions are not used; this driver bit-bangs MII and manually interprets autonegotiation. PHY reset/autoneg timers can retry indefinitely on inactive link. Internal/external PHY switching for `TLAN_ADAPTER_USE_INTERN_10` is subtle, especially around AUI, forced speed/duplex, and link-loss recovery.

Descriptor SKB pointer storage splits an `unsigned long` into two 32-bit descriptor fields. It is intended to work on 64-bit kernels via `upper_32_bits()`, but any descriptor format changes or hardware use of those buffer slots would break pointer recovery.

## Test Signals
Build coverage should include PCI, EISA, suspend/resume, netpoll, and 32-bit/64-bit configurations. Runtime tests need real or emulated ThunderLAN hardware: PCI probe/remove, EISA scan/cleanup, EEPROM MAC read and ethtool EEPROM dump, open/close, TX/RX traffic, multicast/promiscuous/allmulti modes, MII ioctl reads/writes, link autonegotiation, forced speed/duplex/AUI, link loss/recovery, suspend/resume, and watchdog timeout recovery.

Useful logs and counters include the probe banner and installed-device counts, adapter error logs, "PHY reset timeout", "Starting autonegotiation", "Autonegotiation complete", "Link inactive, will retry", TX/RX EOC counts, TX busy counts, carrier transitions, and absence of DMA mapping leaks or stuck queues under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.h

## Purpose
`tlan.h` defines the hardware constants, descriptor formats, private driver state, adapter flags, register offsets, interrupt codes, PHY/MII definitions, and inline I/O helpers used by the ThunderLAN driver in `tlan.c`.

It is the hardware contract for the driver: descriptor sizes, ring lengths, DIO access semantics, MII register definitions, EEPROM constants, and multicast hash calculation all live here.

## Important APIs, Types, And Macros
`struct tlan_adapter_entry` describes vendor/device IDs, labels, flags, and address offsets for adapter tables. The implementation uses a local `struct board` with similar fields, but the flags originate here: `TLAN_ADAPTER_UNMANAGED_PHY`, `TLAN_ADAPTER_BIT_RATE_PHY`, `TLAN_ADAPTER_USE_INTERN_10`, and `TLAN_ADAPTER_ACTIVITY_LED`.

Descriptor types are `struct tlan_buffer` and `struct tlan_list`. A list has a `forward` DMA pointer, `c_stat`, `frame_size`, and ten buffer descriptors. Ring sizing constants are `TLAN_NUM_RX_LISTS`, `TLAN_NUM_TX_LISTS`, `TLAN_BUFFERS_PER_LIST`, `TLAN_MIN_FRAME_SIZE`, and `TLAN_MAX_FRAME_SIZE`.

`struct tlan_priv` is the netdevice private state used by `tlan.c`. It stores netdev/PCI pointers, coherent descriptor storage, RX/TX descriptor and buffer DMA metadata, ring indexes, PHY status and timers, board metadata, module parameter selections, selected PHY addresses, ThunderLAN revision/full-duplex state, spinlock, and timeout work.

Register definitions cover EISA IDs/config registers, host registers (`TLAN_HOST_CMD`, `TLAN_CH_PARM`, `TLAN_DIO_ADR`, `TLAN_HOST_INT`, `TLAN_DIO_DATA`), internal DIO registers (`TLAN_NET_CMD`, `TLAN_NET_SIO`, `TLAN_NET_STS`, `TLAN_NET_MASK`, `TLAN_NET_CONFIG`, address/hash/stat registers, LED, max RX, interrupt disable), interrupt type values, generic MII registers, and ThunderLAN-specific PHY registers.

Inline helpers are `tlan_dio_read8()`, `tlan_dio_read16()`, `tlan_dio_read32()`, `tlan_dio_write8()`, `tlan_dio_write16()`, `tlan_dio_write32()`, `tlan_clear_bit()`, `tlan_get_bit()`, `tlan_set_bit()`, and `tlan_hash_func()`.

## Control Flow Role
The header does not implement the driver lifecycle, but its inline helpers define how all DIO register access works: write the internal register address to `base + TLAN_DIO_ADR`, then read or write the appropriately offset `TLAN_DIO_DATA` byte/word/dword lane. `tlan.c` uses this throughout reset, stats, multicast, MAC programming, PHY control, and LED handling.

Ring-control macros and bits drive TX/RX flow. `TLAN_CSTAT_READY`, `TLAN_CSTAT_FRM_CMP`, `TLAN_CSTAT_EOC`, `TLAN_CSTAT_UNUSED`, and `TLAN_LAST_BUFFER` are the status and buffer markers that the TX/RX interrupt handlers interpret. `CIRC_INC()` advances ring heads/tails with wraparound.

Timer constants identify the staged reset/link state machine used by `tlan_timer()`: activity LED, PHY power down/up, PHY reset, link start, autonegotiation finish, and final reset completion.

`tlan_hash_func()` maps a multicast Ethernet address to a six-bit ThunderLAN hash-table index. `tlan_set_multicast_list()` uses the first three multicast addresses in address registers and hashes the rest into `TLAN_HASH_1`/`TLAN_HASH_2`.

## State And Persistence Behavior
The header defines in-memory state layout but does not allocate it. `struct tlan_priv` persists for the life of an allocated netdevice. Descriptor lists point to DMA-coherent memory allocated by `tlan.c`; their status words are shared state between CPU and adapter hardware.

The many register constants correspond to volatile hardware state. EEPROM constants describe a 256-byte serial EEPROM read by the driver, but no write helpers are declared here.

## Dependencies And Integration Points
The header depends on Linux I/O, types, and netdevice headers. It is included by `tlan.c` and expects a `debug` variable in scope for `TLAN_DBG()`. It defines fallback PCI IDs for Olicom devices when generic PCI headers do not provide them.

The inline I/O helpers are tied to x86-style I/O port accessors (`inb/outb/inw/outw/inl/outl`) and ThunderLAN DIO address/data semantics. MII constants are duplicated locally rather than using only modern `linux/mii.h` names, reflecting the driver's legacy register programming style.

## Risks And Edge Cases
The header is dense with hardware magic values. Incorrect bit definitions affect reset, interrupts, PHY state, descriptor ownership, and stats accounting. `TLAN_DBG()` references a global `debug`, so it is not a generic reusable macro outside the driver implementation context.

The descriptor format reserves ten buffer slots, while `tlan.c` uses slots 8 and 9 to store SKB pointers. Any hardware interpretation of those slots, or a future descriptor format change, would break this convention. `tlan_dio_write32()` adds `(internal_addr & 0x2)` to `TLAN_DIO_DATA`, matching the existing driver behavior but requiring correct alignment assumptions.

`tlan_hash_func()` is optimized bit arithmetic for a specific six-bit hash. It must remain compatible with the hardware multicast hash table; substituting a standard CRC multicast hash would be wrong for this device.

## Test Signals
Compile tests should catch missing PCI ID definitions, structure layout issues, and access to `debug` from `TLAN_DBG()`. Runtime validation comes indirectly through `tlan.c`: DIO reads/writes should return expected revision and stats registers, descriptors should transition through READY/FRM_CMP/EOC states, MII register accesses should work for internal and external PHYs, multicast hash filtering should admit expected multicast traffic, and ring wraparound through `CIRC_INC()` should remain stable under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Kconfig

## Purpose
This Kconfig file defines the Toshiba Ethernet vendor menu and the selectable Toshiba/PS3 network drivers under it. It gates Toshiba driver visibility through `NET_VENDOR_TOSHIBA` and exposes symbols for the PS3 Gelic Ethernet driver, optional PS3 wireless support, and the Toshiba TC35815 PCI Ethernet driver.

## Important APIs, Types, And Functions
The configuration symbols are `NET_VENDOR_TOSHIBA`, `GELIC_NET`, `GELIC_WIRELESS`, and `TC35815`.

`NET_VENDOR_TOSHIBA` is a bool menu gate labeled "Toshiba devices". It defaults to `y` and depends on `(PCI && MIPS) || PPC_PS3` according to Kconfig operator precedence.

`GELIC_NET` is a tristate "PS3 Gigabit Ethernet driver" depending on `PPC_PS3` and selecting `PS3_SYS_MANAGER`. `GELIC_WIRELESS` is a bool depending on `GELIC_NET && WLAN` and selecting `WIRELESS_EXT`. `TC35815` is a tristate depending on `PCI && MIPS` and selecting `PHYLIB`.

## Control Flow
Kconfig first evaluates whether the Toshiba vendor menu is visible. If `NET_VENDOR_TOSHIBA` is enabled, users can select `GELIC_NET` for PS3 Ethernet, optionally enable `GELIC_WIRELESS`, or select `TC35815` on MIPS PCI systems. The selected symbols then drive object inclusion in the sibling Makefile.

## State And Persistence Behavior
The persistent state is kernel configuration: built-in, module, or disabled choices for `GELIC_NET` and `TC35815`, plus boolean choices for `NET_VENDOR_TOSHIBA` and `GELIC_WIRELESS`. No runtime state is defined here.

## Dependencies And Integration Points
The file integrates directly with `drivers/net/ethernet/toshiba/Makefile`: `CONFIG_GELIC_NET` builds `ps3_gelic.o`, `CONFIG_GELIC_WIRELESS` contributes `ps3_gelic_wireless.o` to that composite object, and `CONFIG_TC35815` builds `tc35815.o`.

It depends on architecture/platform symbols `PPC_PS3`, `PCI`, and `MIPS`, networking symbol `WLAN`, and selects subsystem support `PS3_SYS_MANAGER`, `WIRELESS_EXT`, and `PHYLIB`.

## Risks And Edge Cases
The vendor gate dependency mixes `&&` and `||`; current Kconfig precedence makes it equivalent to `(PCI && MIPS) || PPC_PS3`. Changing parentheses could hide PS3 options or expose Toshiba PCI options on unintended platforms.

`GELIC_WIRELESS` is a bool rather than a tristate and depends on `GELIC_NET`; wireless code is compiled into the Gelic composite object when enabled. Disabling the vendor menu hides all child options without changing their source files.

## Test Signals
Configuration tests should check PS3 builds with `GELIC_NET=y/m`, PS3 wireless enabled with `WLAN`, MIPS PCI builds with `TC35815=y/m`, and non-PS3 non-MIPS visibility. Verify selected dependencies appear in generated `.config` and that the Makefile includes the expected objects for built-in and module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Makefile

## Purpose
This Makefile wires Toshiba Ethernet Kconfig symbols to built objects. It builds the PS3 Gelic composite driver, optionally adds its wireless component, and builds the Toshiba TC35815 driver.

## Important APIs, Types, And Functions
The key build variables are `obj-$(CONFIG_GELIC_NET)`, `gelic_wireless-$(CONFIG_GELIC_WIRELESS)`, `ps3_gelic-objs`, and `obj-$(CONFIG_TC35815)`.

`ps3_gelic-objs` always includes `ps3_gelic_net.o` when `CONFIG_GELIC_NET` selects the composite object. It appends `$(gelic_wireless-y)`, which resolves to `ps3_gelic_wireless.o` when `CONFIG_GELIC_WIRELESS=y`.

`obj-$(CONFIG_TC35815)` adds `tc35815.o` as built-in or module according to the tristate value.

## Control Flow
During kernel build evaluation, `CONFIG_GELIC_NET=y` links `ps3_gelic.o` into built-in objects; `CONFIG_GELIC_NET=m` builds it as a module. `ps3_gelic.o` is composed from `ps3_gelic_net.o` plus optional wireless support. `CONFIG_TC35815` independently controls `tc35815.o`.

## State And Persistence Behavior
The Makefile has no runtime state. Its persistent effect is build output selection based on `.config`.

## Dependencies And Integration Points
This file is the build companion to `drivers/net/ethernet/toshiba/Kconfig`. It depends on that file to restrict invalid symbol combinations. It integrates with the kernel kbuild composite-object convention where `<module>-objs` lists member objects for a module or built-in composite.

## Risks And Edge Cases
Because `GELIC_WIRELESS` is bool, `gelic_wireless-y` only appends wireless code when built-in to the composite object; this matches the Kconfig dependency on `GELIC_NET`. If `GELIC_WIRELESS` were ever changed to tristate, this Makefile would need adjustment to handle `m` semantics correctly.

The PS3 Gelic module name is `ps3_gelic`, not `ps3_gelic_net`, so packaging and module-loading tests should use the composite name.

## Test Signals
Build matrix checks should confirm `CONFIG_GELIC_NET=m` produces `ps3_gelic.ko`, `CONFIG_GELIC_WIRELESS=y` includes `ps3_gelic_wireless.o` in that composite, `CONFIG_GELIC_WIRELESS=n` omits it, and `CONFIG_TC35815=m` produces `tc35815.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Makefile -->
