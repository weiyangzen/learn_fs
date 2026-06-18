# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_main.c lines 9371-12943

## Scope and Purpose

This chunk covers the late PF-side implementation of the HNS3 `hclge_main.c` driver. It starts inside `hclge_set_mac_addr()` and runs through module registration. The code in this range supplies many of the `hnae3_ae_ops` callbacks used by the NIC, ethtool, SR-IOV, reset, VLAN, MTU, queue reset, Wake-on-LAN, EEPROM, RSS channel, and client lifecycle paths.

The dominant responsibilities in this span are:

- MAC address programming handoff and MII ioctl routing.
- VLAN filter, VF VLAN, port-base VLAN, VLAN offload, and VLAN restore/sync state.
- Hardware table restore after reset for MAC, VLAN, and flow director entries.
- MTU and queue reset commands.
- Pause/frame flow control and link/media helper callbacks.
- NIC/RoCE client instance initialization and teardown.
- PCI, command queue, interrupt, TQP, vport, MAC, VLAN, TM, RSS, FD, PTP, WOL, devlink, and service task initialization/teardown.
- PF/global reset rebuild and state reinitialization.
- VF administrative controls: spoof checking, trust, rate limiting, VLAN cleanup, and SR-IOV disable cleanup.
- Runtime ethtool-style helpers for channels, LEDs, link modes, GRO, SFP EEPROM, link diagnosis, DSCP priority, WOL, PTP timestamping, and hardware stats.
- Final assembly of the `hnae3_ae_ops` table and module init/exit registration.

This is not a self-contained file view: many helpers, data structures, and constants are declared earlier in `hclge_main.c`, companion HNS3 files, and common HNAE3/HCLGE headers. The chunk is nevertheless the integration surface that wires those helpers into the NIC framework.

## Important APIs, Types, and Data

Key local objects and state:

- `struct hclge_dev`: PF device state. This chunk updates `state`, `reset_type`, `reset_level`, `reset_pending`, `rst_stats`, `mps`, `vlan_table`, `vf_vlan_full`, `vport_config_block`, `tm_info.fc_mode`, `fc_mode_last_time`, `gro_en`, `hw.mac.*`, `rss_cfg`, `misc_vector`, `reset_timer`, `service_task`, and client pointers.
- `struct hclge_vport`: PF/VF vport state. This chunk uses `vport_id`, `nic`, `roce`, `back`, `state`, `need_notify`, `vf_info`, `port_base_vlan_cfg`, `txvlan_cfg`, `rxvlan_cfg`, `vlan_list`, `vlan_del_fail_bmap`, `mps`, `alloc_tqps`, `last_promisc_flags`, and `overflow_promisc_flags`.
- `struct hnae3_handle`: callback-facing handle used by NIC, ethtool, and upper HNAE3 layers. Most callbacks convert this to `hclge_vport` via `hclge_get_vport()`.
- `struct hnae3_ae_dev`: bus/device integration object. This chunk uses `pdev`, `priv`, `caps`, `dev_version`, `dev_specs`, and reset/error-request state.
- Firmware command descriptor structs such as `hclge_vlan_filter_ctrl_cmd`, `hclge_vlan_filter_vf_cfg_cmd`, `hclge_vlan_filter_pf_cfg_cmd`, `hclge_vport_vtag_tx_cfg_cmd`, `hclge_vport_vtag_rx_cfg_cmd`, `hclge_reset_tqp_queue_cmd`, `hclge_reset_cmd`, `hclge_query_wol_supported_cmd`, `hclge_wol_cfg_cmd`, `hclge_set_led_state_cmd`, and SFP EEPROM descriptor payloads.
- Bitmaps and lists are persistent in-memory mirrors of firmware state: `hdev->vlan_table[vlan_id]` tracks which vports use a VLAN, `hdev->vf_vlan_full` tracks firmware VF VLAN table exhaustion, `vport->vlan_list` tracks VLANs requested by the stack, and `vport->vlan_del_fail_bmap` tracks delete operations deferred during reset or firmware failure.

Primary exported or callback-visible functions in this chunk:

- MAC/ioctl: `hclge_set_mac_addr()`, `hclge_do_ioctl()`.
- VLAN/filter/offload: `hclge_enable_vport_vlan_filter()`, `hclge_en_hw_strip_rxvtag()`, `hclge_update_port_base_vlan_cfg()`, `hclge_set_vlan_filter()`, `hclge_set_vf_vlan_filter()`, `hclge_rm_vport_all_vlan_table()`, `hclge_uninit_vport_vlan_table()`, `hclge_restore_vport_port_base_vlan_config()`, `hclge_restore_vport_vlan_table()`.
- Reset/restore: `hclge_restore_mac_table_common()`, `hclge_reset_tqp()`, `hclge_reset_prepare_general()`, `hclge_reset_done()`, `hclge_reset_ae_dev()`, `hclge_uninit_ae_dev()`.
- Flow/link/ethtool: `hclge_cfg_flowctrl()`, `hclge_get_pauseparam()`, `hclge_set_pauseparam()`, `hclge_get_ksettings_an_result()`, `hclge_get_media_type()`, `hclge_get_mdix_mode()`, `hclge_get_fw_version()`, `hclge_query_scc_version()`, `hclge_get_channels()`, `hclge_set_channels()`, `hclge_set_led_id()`, `hclge_get_link_mode()`, `hclge_gro_en()`, `hclge_get_module_eeprom()`, `hclge_get_link_diagnosis_info()`, `hclge_get_dscp_prio()`.
- Client/device lifecycle: `hclge_init_client_instance()`, `hclge_uninit_client_instance()`, `hclge_init_ae_dev()`, `hclge_init()`, `hclge_exit()`.
- VF controls: `hclge_set_vf_spoofchk()`, `hclge_set_vf_trust()`, `hclge_set_vf_rate()`, `hclge_clean_vport_config()`.
- WOL: `hclge_get_wol()`, `hclge_set_wol()`.

The chunk concludes with `static const struct hnae3_ae_ops hclge_ops`, `static struct hnae3_ae_algo ae_algo`, and `module_init()`/`module_exit()` hooks.

## MAC Address and MII IOCTL Flow

`hclge_set_mac_addr()` validates the new unicast MAC, programs the pause frame address through `hclge_pause_addr_cfg()`, updates the vport unicast MAC list under `mac_list_lock`, and copies the new address into `hdev->hw.mac.mac_addr` while still holding that lock. The lock is intentionally held across the device-address update so the set-RX-mode path cannot remove the address concurrently. On failure after changing the pause address, non-initial calls try to restore the old pause address.

`hclge_do_ioctl()` routes MII ioctls either through a PHY device (`phy_mii_ioctl()`) or the firmware-backed implementation path (`hclge_mii_ioctl()`) when no `phydev` exists and the device supports PHY implementation commands. `hclge_mii_ioctl()` supports `SIOCGMIIPHY`, `SIOCGMIIREG`, and `SIOCSMIIREG`; all other commands return `-EOPNOTSUPP`.

## VLAN Filter and VLAN Offload Behavior

The VLAN logic has several layers:

- Firmware control toggles: `hclge_set_vlan_filter_ctrl()` reads the current VLAN filter config, adjusts feature bits, and writes it back. `hclge_set_port_vlan_filter_bypass()` is used on devices with port VLAN bypass support.
- Vport filter policy: `hclge_need_enable_vport_vlan_filter()` decides whether a vport's VLAN filtering should be enabled based on port-base VLAN state, trusted VF promiscuous requests, PF user promiscuous mode, requested filter enable, hardware capability bits, and whether nonzero VLAN entries exist in the vport VLAN list.
- State transition: `__hclge_enable_vport_vlan_filter()` compares the computed need against `cur_vlan_fltr_en`, applies hardware changes only when needed, and updates `cur_vlan_fltr_en`. `hclge_enable_vport_vlan_filter()` wraps this under `hdev->vport_lock` while recording `req_vlan_fltr_en`.
- VF-specific table programming: `hclge_set_vf_vlan_filter_cmd()` builds a two-descriptor command with a VF bitmap. `hclge_check_vf_vlan_cmd_status()` treats normal success and some benign missing-entry responses as success, marks `hdev->vf_vlan_full` when firmware reports a full VF VLAN table, and returns `-EIO` for unexpected firmware response codes.
- PF/port VLAN programming: `hclge_set_port_vlan_filter()` computes the VLAN offset bitmap for `HCLGE_OPC_VLAN_FILTER_PF_CFG`. `hclge_need_update_port_vlan()` maintains the in-memory `hdev->vlan_table[vlan_id]` vport bitmap and avoids duplicate add/delete hardware operations.
- Combined hardware update: `hclge_set_vlan_filter_hw()` validates VLAN ID, programs the per-VF table via `hclge_set_vf_vlan_common()`, updates the port-level VLAN table only when the first vport adds or last vport removes the VLAN, and ignores VLAN 0 delete operations.

VLAN TX/RX offload state is stored in `vport->txvlan_cfg` and `vport->rxvlan_cfg`, then pushed through `hclge_set_vlan_tx_offload_cfg()` and `hclge_set_vlan_rx_offload_cfg()`. `hclge_vlan_offload_cfg()` derives these settings from the port-base VLAN state, default VLAN tag/QoS, device generation, and the requested RX VLAN strip state. Port-base VLAN enabled mode causes TX insertion of tag1 and RX stripping/discard behavior to change; disabled mode accepts normal tagged traffic and uses tag2 stripping according to `rx_vlan_offload_en`.

Initialization uses `hclge_init_vlan_config()`:

1. Initialize VF and port VLAN filter state with `hclge_init_vlan_filter()`.
2. Program VLAN protocol types to 802.1Q via `hclge_init_vlan_type()`.
3. Initialize per-vport VLAN offload config.
4. Add VLAN 0 to the PF VLAN filter path.

The code keeps requested VLANs in `vport->vlan_list` using `hclge_add_vport_vlan_table()`, `hclge_add_vport_all_vlan_table()`, `hclge_rm_vport_vlan_table()`, and `hclge_rm_vport_all_vlan_table()`. The `hd_tbl_status` flag records whether a list entry is currently written to hardware. This matters when port-base VLAN is active: user VLAN requests are remembered but not necessarily written to firmware until port-base VLAN is disabled.

## Port-Base VLAN and VF VLAN Control

`hclge_set_vf_vlan_filter()` is the PF-facing callback for configuring a VF's port-base VLAN. It rejects unsupported device versions, invalid VF IDs, VLAN IDs beyond `VLAN_N_VID - 1`, QoS values above 7, and protocols other than 802.1Q. It computes whether the request is no-op, enable, disable, or modify via `hclge_get_port_base_vlan_state()`, then applies it with `hclge_update_port_base_vlan_cfg()`.

`hclge_update_port_base_vlan_cfg()` first updates VLAN offload state. If the VLAN filter entry must change, it either modifies an existing port-base VLAN tag with `hclge_modify_port_base_vlan_tag()` or switches between enabled/disabled entry sets with `hclge_update_vlan_filter_entries()`. Enabling port-base VLAN removes all normal vport VLAN entries from hardware, force-deletes VLAN 0 in the VF table, and adds the new base VLAN. Disabling port-base VLAN force-adds VLAN 0, removes the old base VLAN, and restores all recorded normal VLANs. It then updates `port_base_vlan_cfg.state`, the exposed handle state, old/current VLAN info, `tbl_sta`, and the vport VLAN filter change bit.

For pre-version-3 devices, `hclge_set_vf_vlan_filter()` pushes the port-base VLAN state to a live VF with `hclge_push_vf_port_base_vlan_info()` or records `HCLGE_VPORT_NEED_NOTIFY_VF_VLAN` when the VF is not alive. This makes VF notification state persistent across the alive/un_alive timing window.

`hclge_set_vlan_filter()` is the general add/delete VLAN callback. It records delete failures in `vlan_del_fail_bmap` if reset handling or reset failure is active. When port-base VLAN is disabled, it writes the hardware filter immediately and records `writen_to_tbl = true`; otherwise it only updates the vport VLAN list. Failed deletes are also recorded for later retry. `hclge_sync_vlan_filter()` drains up to `HCLGE_MAX_SYNC_COUNT` delayed delete bits per service pass, removes list entries after successful hardware deletion, and then calls `hclge_sync_vlan_fltr_state()` to reconcile filter enablement.

## Reset Restore and Persistence

Hardware reset paths are designed around in-memory shadow state:

- MAC list entries are converted by `hclge_mac_node_convert_for_reset()`: active entries become `HCLGE_MAC_TO_ADD`, delete-pending entries are removed, and the vport MAC table change bit is set. This ensures service work can repopulate hardware MAC tables after global or IMP reset.
- `hclge_restore_vport_port_base_vlan_config()` iterates all VFs and reprograms port-base VLANs that were enabled before reset. It uses either current or old VLAN info depending on `tbl_sta`, clears the `vlan_table` bit before re-adding, and records whether firmware programming succeeded.
- `hclge_restore_vport_vlan_table()` replays normal VLAN list entries when port-base VLAN is disabled.
- `hclge_restore_hw_table()` coordinates PF MAC restore, VF port-base VLAN restore, PF VLAN restore, flow director restore, and FD user-defined state.

`hclge_reset_prepare_general()` serializes reset preparation with `reset_sem`, sets `HCLGE_STATE_RST_HANDLING`, assigns `reset_type`, and retries `hclge_reset_prepare()` when preparation fails or reset remains pending. It disables the misc vector and command channel before reset completion and increments FLR reset stats for FLR.

`hclge_reset_done()` reenables the misc vector, calls `hclge_reset_rebuild()`, clears `reset_type`, and releases `reset_sem` if it owned the reset-handling state.

`hclge_reset_ae_dev()` is the reset rebuild routine. It sets the device down, clears stats, and for IMP/global resets clears VLAN and UMV shadow tables that firmware has lost. It reinitializes command queues, TQP mapping, MAC/TP port, TSO/GRO, VLAN, traffic manager, RSS, manager table, FD, PTP, error handling, NIC/RoCE error interrupts, vport alive state, spoof checking, VF rates, RX descriptor layout, and WOL. It returns the first hard failure, so reset recovery is all-or-fail for these stages.

## MTU, Queue Reset, Flow Control, and Link Helpers

`hclge_set_vport_mtu()` computes hardware max frame size as MTU plus Ethernet header, FCS, and two VLAN headers. It enforces device max frame size and a minimum/default frame size. VF vports may not exceed PF `hdev->mps`; PF changes may not drop below any VF's stored `mps`. PF MTU changes stop clients, program the MAC max frame size, update PF/vport `mps`, reallocate packet buffers, and bring clients back up.

Queue reset uses two mechanisms. `hclge_reset_rcb()` sends an RCB reset command for the handle's queue range; if firmware reports the command is unsupported it falls back to `hclge_reset_tqp_cmd()`, which resets each global queue ID, polls readiness up to `HCLGE_TQP_RESET_TRY_TIMES`, and deasserts soft reset. PF resets first disable TQPs with `hclge_tqp_enable(handle, false)`.

Pause/flow control code distinguishes link-level pause from priority flow control. `hclge_cfg_pauseparam()` refuses to override PFC mode and otherwise writes MAC pause settings. `hclge_cfg_flowctrl()` resolves advertised pause capabilities through MII helpers when autonegotiation is active, disables pause in half duplex, and applies the result. `hclge_set_pauseparam()` prevents changing autonegotiation through the pause callback, refuses changes during PFC, updates PHY advertised pause, records user-selected `fc_mode_last_time`, and either writes hardware directly or restarts PHY autonegotiation.

Link helper callbacks expose firmware or cached state: `hclge_get_ksettings_an_result()`, `hclge_get_media_type()` with a forced `hclge_update_port_info()`, and `hclge_get_mdix_mode()` for copper PHYs using vendor page/register reads.

## Device and Client Lifecycle

`hclge_init_ae_dev()` is the primary probe path. It allocates `hclge_dev`, initializes locks/semaphores and defaults, enables PCI/DMA/resources, maps BARs, initializes firmware command queues, clears hardware resources, queries capabilities and device specs, configures the device, initializes MSI and misc IRQ, allocates TQPs and vports, maps TQPs, initializes copper PHY/MDIO where needed, initializes UMV space, MAC, TSO/GRO, VLAN, TM scheduler, RSS config/hardware, manager table, flow director, PTP, port info, work/timer state, error handling, RX descriptor advanced layout, WOL, devlink, driver state bits, and finally enables the misc vector and schedules the service task.

The error path unwinds only the stages reached: PTP, MDIO bus, misc IRQ, IRQ vectors, command queue, PCI mappings/regions/device, and the vport lock. Stages initialized without explicit unwind in this visible path rely on earlier failure placement or companion cleanup outside this chunk, which is a maintenance risk if initialization order changes.

`hclge_uninit_ae_dev()` performs device teardown: reset VF rates, clear VF VLANs, mark state as down/removing, cancel reset timer and service work, uninit PTP and RX descriptor layout, remove MAC/FD tables, unregister MDIO, disable misc vector and all hardware interrupts, uninitialize command queue, misc IRQ, devlink, PCI resources, vport VLAN lists, lock, and `ae_dev->priv`.

NIC/RoCE clients are initialized through `hclge_init_client_instance()`. The NIC path calls `client->ops->init_instance()`, marks NIC registered, rejects races with reset by comparing `rst_stats.reset_cnt`, enables NIC hardware error interrupts, and sets the client init flag. The RoCE path checks RoCE support and registered clients, initializes RoCE base info, calls RoCE client init, detects reset races, enables RoCE RAS interrupts, and sets the RoCE client init flag. Both init paths wait out reset handling before invoking client uninit on failure. `hclge_uninit_client_instance()` tears down RoCE first when present, then NIC unless the unregistering client is RoCE-only.

## VF Administrative State

Spoof checking has separate MAC and VLAN hardware controls. `hclge_set_vf_spoofchk()` validates device generation and VF ID, warns when enabling spoof checking while the VF VLAN or UMV MAC tables are full, applies MAC and VLAN spoof hardware config, and records `vport->vf_info.spoofchk`. `hclge_reset_vport_spoofchk()` reapplies spoof settings after reset.

VF trust is an in-memory policy change. `hclge_set_vf_trust()` updates `vport->vf_info.trusted`, marks promiscuous mode changed, and schedules service work. Later `hclge_sync_vport_promisc_mode()` allows trusted VFs to request unicast/multicast promiscuous modes, also considering overflow-promiscuous flags, while untrusted VFs only retain requested broadcast behavior. A successful promiscuous update marks VLAN filter state changed because promiscuity affects whether VLAN filtering should be enabled.

Rate limiting supports only `min_tx_rate == 0` and `max_tx_rate` in `[0, mac.max_speed]`. `hclge_set_vf_rate()` configures the TM queue-set shaper and stores `vf_info.max_tx_rate`. Reset and remove paths either restore stored nonzero rates (`hclge_resume_vf_rate()`) or reset all VF rates to default (`hclge_reset_vf_rate()`).

SR-IOV disable cleanup flows through `hclge_clean_vport_config()`, which calls `hclge_clear_vport_vf_info()` for each VF. That clears vport init/alive state, notification bits, `mps`, VF rate, port-base VLAN, spoof checking, and the entire `vf_info` structure.

## WOL, EEPROM, Channels, LEDs, GRO, and Diagnostics

Wake-on-LAN state is stored in `hdev->hw.mac.wol`. `hclge_init_wol()` checks support, queries supported modes, and writes a default/current config. `hclge_set_wol()` validates requested options against support, records secure-on password bytes when `WAKE_MAGICSECURE` is set, writes firmware config, and clears `wol_current_mode` on firmware failure. `hclge_update_wol()` reapplies this stored config after reset.

RSS/channel callbacks expose maximum channels as `min(pf_rss_size_max, vport->alloc_tqps)`. `hclge_set_channels()` records the requested RSS size, updates TM vport mapping, programs RSS TC mode, and if the user has not supplied an indirection table, rebuilds an even modulo indirection table sized by `dev_specs.rss_ind_tbl_size`.

`hclge_set_led_id()` maps ethtool physical ID active/inactive states to firmware LED on/off commands. `hclge_gro_en()` toggles `hdev->gro_en`, reprograms GRO, and rolls back the field on error. `hclge_get_link_mode()` copies supported and advertising bitmaps from cached MAC state.

SFP EEPROM reads first require fiber media and module presence (`hclge_module_existed()`). `hclge_get_sfp_eeprom_info()` sends a six-descriptor read command, copies data from descriptor 0 and then descriptors 1-5, and returns the actual bytes copied. `hclge_get_module_eeprom()` loops until the requested length is filled or a read returns zero.

`hclge_get_link_diagnosis_info()` is firmware-version gated to devices newer than version 2 and returns a firmware status code. `hclge_get_dscp_prio()` validates DSCP range and exposes the current TC map mode plus DSCP-to-priority mapping, defaulting invalid priorities to 0.

## Dependencies and Integration Points

This chunk depends heavily on:

- Linux kernel networking APIs: `net_device` flags through HNAE3, ethtool callback types, MII/PHY helpers, VLAN constants, link mode bitmaps, workqueues, timers, mutexes, spinlocks, semaphores, bitmaps, PCI, DMA, devm/pcim mapping, IRQs, and module registration.
- HNS3/HNAE3 common command infrastructure: `hclge_cmd_setup_basic_desc()`, `hclge_comm_cmd_reuse_desc()`, `hclge_cmd_send()`, common command queue init/uninit, RSS common helpers, and command opcodes.
- Firmware/hardware feature gates: `hdev->ae_dev->dev_version`, `hdev->ae_dev->caps`, `hnae3_dev_phy_imp_supported()`, `hnae3_dev_roce_supported()`, `hnae3_ae_dev_rxd_adv_layout_supported()`, `hnae3_ae_dev_wol_supported()`, and RAS capability checks.
- Traffic manager, RSS, FD, PTP, devlink, mailbox, PHY/MDIO, and reset helpers implemented elsewhere in the driver.
- Upper clients through `struct hnae3_client` and `struct hnae3_ae_ops`. The `hclge_ops` table is the outward-facing integration contract for the rest of the HNS3 stack.

## Control Flow and State Transitions

Major control paths:

- Probe: `hclge_init()` registers `ae_algo`; later the bus/core calls `.init_ae_dev = hclge_init_ae_dev`, followed by `.init_client_instance` as clients bind.
- Runtime settings: ethtool/netdev callbacks enter via `hclge_ops`, convert `hnae3_handle` to `hclge_vport`, mutate software shadow state, and send one or more firmware commands.
- Service reconciliation: operations that cannot complete during reset or that depend on aggregated vport state set bits such as `HCLGE_VPORT_STATE_VLAN_FLTR_CHANGE`, `HCLGE_VPORT_STATE_PROMISC_CHANGE`, and `HCLGE_VPORT_STATE_MAC_TBL_CHANGE`; service work later synchronizes hardware.
- Reset: reset prepare disables command/misc interrupt paths; reset rebuild recreates hardware state from shadow structures; reset done clears reset state and releases serialization.
- Remove: `.uninit_client_instance` detaches clients; `.uninit_ae_dev` stops timers/work, interrupts, hardware tables, firmware command queues, PCI resources, and in-memory VLAN lists; module exit unregisters the AE algorithm and destroys the workqueue.

Important persistence patterns:

- `vport->vlan_list`, `port_base_vlan_cfg`, `vf_info`, `rxvlan_cfg`, `txvlan_cfg`, WOL info, GRO flag, RSS state, FD state, MAC lists, and VF rate/trust/spoof values are software truth used to reconstruct firmware after reset.
- `tbl_sta`, `hd_tbl_status`, `vlan_del_fail_bmap`, and `vf_vlan_full` describe divergence between software intent and firmware tables.
- Reset handling clears or preserves these mirrors selectively depending on reset scope; IMP/global reset clears hardware-lost tables, while PF reset avoids clearing table state.

## Risks and Edge Cases

- `hclge_reset_prepare_general()` proceeds to disable the misc vector and command channel even if all reset-prepare retries fail. This may be intentional for reset sequencing, but failures before the break leave `reset_sem` handling dependent on the loop state and downstream reset completion.
- VLAN delete during reset returns `-EBUSY` after recording `vlan_del_fail_bmap`. Callers must tolerate the returned failure while the driver later reconciles state.
- `hclge_sync_vlan_filter()` holds `vport_lock` while sending firmware commands. Other paths in this chunk also send commands under that mutex. This simplifies state consistency but can make command latency visible to unrelated vport operations.
- VF VLAN table full handling is asymmetric: add operations may become no-ops once `vf_vlan_full` is set unless spoof checking is enabled. This prevents more firmware churn but can surprise tests that expect every software VLAN list entry to have a hardware entry.
- Port-base VLAN transitions are multi-command sequences with partial-failure windows. The code records `tbl_sta` and old VLAN info, but failed middle steps can leave software/hardware divergence until reset or restore.
- `hclge_get_sfp_eeprom_info()` uses a fixed maximum per firmware request. Bounds depend on descriptor layout constants; any mismatch between firmware response layout and copy lengths would corrupt returned EEPROM data.
- Init and reset paths are long ordered sequences. Adding a new initialized subsystem without matching failure unwind, reset rebuild, and uninit handling can leak resources or lose state across reset.
- `hclge_set_wol()` clears only `wol_current_mode` on firmware failure after having possibly updated secure password fields. A later retry path should be checked if secure-password consistency matters.
- `hclge_set_channels()` allocates a temporary RSS indirection table after updating TM/RSS TC mode. Failure during allocation or later RSS programming can leave partial channel changes depending on earlier helper side effects.
- Many functions rely on device version/capability gates. Tests and future changes need to cover older firmware/device revisions, especially version 1/2 VLAN paths and unsupported RCB/WOL/RXD-advanced-layout commands.

## Test Signals

Useful validation signals for this chunk include:

- MAC address tests: reject zero/broadcast/multicast addresses; verify pause address rollback on failure; verify service task schedules MAC table sync.
- MII/PHY tests: PHY-backed and firmware-backed MII ioctls, unsupported command returns, and no-phy unsupported-device behavior.
- VLAN tests: add/delete VLAN 0 and nonzero VLANs; duplicate adds/deletes; port-base VLAN enable/disable/modify; VF VLAN table full response; spoof-check interaction with full VF VLAN table; VLAN filter enable policy under PF promiscuous mode, trusted VF requests, and VLAN filter modification capability.
- Reset tests: global/IMP reset should clear/replay VLAN/MAC/FD state; PF reset should preserve in-memory table state; reset races during client init should unwind correctly; delayed VLAN deletes should be retried by sync.
- MTU tests: PF MTU lower than VF MPS rejection; VF MTU above PF MPS rejection; max/min frame boundaries; buffer reallocation failure after MAC frame-size programming.
- Queue reset tests: successful RCB reset; unsupported RCB fallback to per-TQP reset; timeout waiting for ready-to-reset; global queue ID conversion.
- Flow-control tests: PFC refusal, autoneg mismatch rejection, PHY pause advertisement, half-duplex pause disable, PHY implementation path without `phydev`.
- Lifecycle tests: probe failure injection at each major stage, matching cleanup; reset rebuild failure injection; module init workqueue allocation failure; uninit after partial client registration.
- VF admin tests: spoof check warnings under full MAC/VLAN tables, trust toggles causing promiscuous resync, VF rate bounds, SR-IOV disable cleanup resetting VLAN/rate/spoof/VF info.
- Ettool helper tests: channel resizing with and without user RSS indirection, LED active/inactive commands, GRO rollback on firmware failure, link mode bitmap copy, MDIX invalid when no PHY.
- WOL/EEPROM tests: unsupported WOL no-op, invalid WOL options, magic secure password programming, WOL restore after reset, fiber-only EEPROM reads, no-module `-ENXIO`, multi-descriptor EEPROM reads crossing the per-command length.

## Cross-Chunk References

The following visible calls require earlier or companion chunks for full behavior:

- MAC table helpers: `hclge_update_mac_node_for_dev_addr()` begins immediately before this chunk; MAC sync and UMV handling are elsewhere.
- Reset service: `hclge_reset_prepare()`, `hclge_reset_rebuild()`, `hclge_reset_timer()`, `hclge_service_task()`, and reset-event helpers are outside this span.
- Hardware setup helpers: `hclge_configure()`, `hclge_init_msi()`, `hclge_misc_irq_init()`, `hclge_alloc_tqps()`, `hclge_alloc_vport()`, `hclge_map_tqp()`, MAC/PHY init, TM/RSS/FD/PTP/devlink setup, and error handling are external to this chunk.
- Netdev/ethtool callbacks mapped in `hclge_ops` such as stats, FEC, RSS tuple, loopback, FD, flower, PTP timestamping, VF MAC/link state, command queue stats, and reset status are implemented outside this visible range.
