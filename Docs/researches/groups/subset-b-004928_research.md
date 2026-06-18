# Research Group: subset-b-004928

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac.h

## Purpose

`mac.h` is the central MAC-layer contract for the Realtek `rtw89` wireless driver. It defines register/memory layout constants, MAC-generation dispatch hooks, public MAC APIs, and inline helpers used by core, firmware, power-save, WoW, debug, and chip-specific files. The file deliberately separates common call sites from AX/BE hardware differences through `struct rtw89_mac_gen_def`, with `rtw89_mac_gen_ax` and `rtw89_mac_gen_be` supplied by implementation files.

## Important APIs, Types, And Constants

- Hardware selection and forwarding enums include `rtw89_mac_hwmod_sel`, `rtw89_mac_fwd_target`, frame type selectors, DLE/PLE port and queue IDs, quota IDs, firmware C2H classes/functions, MCC/MRC statuses, WoW firmware states, and MAC error codes.
- Memory and CAM definitions map symbolic selectors in `enum rtw89_mac_mem_sel` to AX/BE SRAM windows such as AXIDMA, shared buffer, DMAC table, address CAM, security CAM, BSSID CAM, BA CAM, beacon IE CAMs, TXD/TXDATA FIFOs, CPU local memory, WD page, and MLD table.
- `struct rtw89_mac_size_set` groups the driver's common DLE/HFC size, quota, reserved quota, and DLE input presets. The exported `rtw89_mac_size` object is used by initialization and quota-selection code outside this header.
- `struct rtw89_mac_gen_def` is the key polymorphic interface. It contains register offsets and many function pointers for system/TRX init, DLE/HFC setup, firmware download, efuse parsing, CPU IO, coex grant/PLT, TX power register mapping, scan offload, WoW MAC configuration, error dumps, and beamforming association.
- Inline register helpers, including `rtw89_mac_reg_by_idx()`, `rtw89_mac_reg_by_port()`, and the `rtw89_read/write*_port*()` wrappers, centralize band and port address translation. BE chips use `RTW89_MAC_BE_BAND_REG_OFFSET`; AX chips use their own offset from the generation definition.
- Public MAC APIs declared here cover power on/off, partial/pre/full init, DLE/HFC/preload init, VIF and port management, TSF operations, beacon/AP control, BB/RF enablement, C2H handling, scheduler stop/resume, RX filtering, coexistence, control-path switching, beamforming, MU-EDCA, TX power accessors, packet drop, DLE quota changes, reserved quota lookup, and CPU IO RX movement.
- TX report helpers (`rtw89_tx_rpt_init()`, `rtw89_is_tx_rpt_skb()`, `rtw89_tx_rpt_tx_status()`, `rtw89_tx_rpt_skb_add()`, `rtw89_tx_rpt_skbs_purge()`) bridge firmware TX completion reports back to mac80211 status reporting.

## Control Flow And Dispatch

Most common code calls a small inline wrapper in this header, which then dispatches through `rtwdev->chip->mac_def`. Examples include MAC enable checks, PPDU status, PHY reports, EDCCA mode, coexistence PLT, beamforming association, TX power CR lookup, XTAL SI access, scan offload, and secure IDMEM sharing. This lets shared files such as `mac.c`, `fw.c`, `wow.c`, `ps.c`, `ser.c`, `debug.c`, and `mac80211.c` avoid open-coded chip-generation branches.

Register flow is similarly centralized. Callers supply a base register and band or port identity; helpers derive the physical register using the generation-specific band offset and the `struct rtw89_port_reg` table. This is important for DBCC/MLO paths where the same logical operation may need CMAC0 or CMAC1 programming.

TX reporting flow is local to the header because it is performance-sensitive and small: transmit setup assigns a 4-bit firmware report sequence number from `rtwdev->tx_rpt.sn`; SKBs needing status are stored in the indexed `tx_rpt->skbs` array under `skb_lock`; a collision on the same sequence number is treated as late firmware reporting and the old SKB is completed as dropped; purge drains all pending SKBs with drop status.

## State And Persistence Behavior

This header does not own persistent storage, but it defines the state surfaces other modules mutate:

- `rtwdev->chip->mac_def` chooses AX or BE behavior for the lifetime of the device.
- `rtwdev->hal.rx_fltr`, `rtwdev->dbcc_en`, `rtwdev->hci`, `rtwdev->mac.hfc_param`, `rtwdev->mac.dle_info`, and `rtwdev->mac.qta_mode` are read or indirectly modified through declared APIs and generation callbacks.
- Device flags such as `RTW89_FLAG_BFEE_MON`, power/function flags, SER handling, and firmware-ready state gate helper behavior.
- `rtwdev->tx_rpt` persists outstanding TX-status SKB pointers until firmware completion, collision replacement, or purge.
- Hardware state is persistent in MMIO registers, CAMs, DLE quota tables, and firmware-owned tables; this header's API boundaries are the common entry points for configuring those resources.

## Dependencies And Integration Points

`mac.h` includes `core.h`, `fw.h`, and `reg.h`, so it depends on core device/vif/sta data structures, firmware command types, and register definitions. It exposes symbols consumed by `mac.c`, `mac_be.c`, `mac80211.c`, chip files such as `rtw8922a.c` and `rtw8922d.c`, and support modules including firmware, WoW, SER, power save, debugfs, PHY, coexistence, and CAM/security code. It also integrates directly with mac80211 through SKB control blocks and `ieee80211_tx_status_irqsafe()` in TX report helpers.

## Risks And Edge Cases

- `struct rtw89_mac_gen_def` is a wide vtable; missing optional callbacks must be checked before use. Some wrappers guard NULL callbacks, while others assume the chip definition is complete.
- Register offset helpers are correctness-critical. A wrong band offset, port index, or generation-specific register base can silently program the wrong CMAC.
- `rtw89_mac_mem_base_addrs()` special-cases RTL8922D security CAM; adding new memory selectors or chip variants requires keeping this mapping synchronized with `enum rtw89_mac_mem_sel`.
- TX report sequence numbers are only 4 bits. The collision handling avoids leaks but can report older SKBs as dropped when firmware reports are delayed or queue pressure is high.
- `rtw89_mac_chk_preload_allow()` currently always returns false after the HCI/chip check comment, so any future preload enablement must be intentional and retested for BE/PCIe devices.
- Inline helpers touch MMIO and mac80211 status paths; they must only be called under the locking and power-state assumptions documented by their callers.

## Test Signals

- Build coverage should include AX and BE chip files because this header's vtable shape must match all generation definitions.
- Runtime smoke tests should cover interface add/remove, STA association/disassociation, scan offload, WoW suspend/resume, DBCC/MLO link activation, and TX-status reporting.
- Debug and fault-injection signals include SER recovery, DLE quota lost dumps, TX report purge/collision behavior, PPDU status enable/disable, and RX filter changes across CMAC0/CMAC1.
- Static checks should flag missing generation callbacks, enum/table size mismatches, and unsafe NULL callback assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac80211.c

## Purpose

`mac80211.c` exports `rtw89_ops`, the driver's `struct ieee80211_ops` implementation. It translates Linux mac80211 callbacks into rtw89 core, MAC, firmware, PHY, channel-context, security CAM, scan, WoW, and coexistence operations. It is the main boundary between kernel wireless framework events and the driver's internal `rtw89_dev`, `rtw89_vif`, `rtw89_vif_link`, `rtw89_sta`, and `rtw89_sta_link` state machines.

## Important APIs And Functions

- TX entry points: `rtw89_ops_tx()` sends SKBs through `rtw89_core_tx_write()` and kicks the selected queue, while `rtw89_ops_wake_tx_queue()` schedules mac80211 TXQs onto `rtwdev->txq_wq`.
- Device lifecycle: `rtw89_ops_start()`, `rtw89_ops_stop()`, and `rtw89_ops_config()` enter/leave IPS/LPS, react to idle transitions, and apply channel changes through channel entity helpers.
- VIF lifecycle: `rtw89_ops_add_interface()`, `rtw89_ops_remove_interface()`, and `rtw89_ops_change_interface()` allocate/release MAC IDs and hardware ports, initialize `rtw89_vif`, create the idle link, register MAC role state with hardware, and notify Bluetooth coexistence.
- Link helpers: `__rtw89_ops_add_iface_link()` initializes per-link work items, P2P NoA state, BSSID/mac address, channel context defaults, and calls `rtw89_mac_add_vif()`. `__rtw89_ops_remove_iface_link()` cancels work, deinitializes P2P NoA, notifies role stop, and removes the MAC VIF.
- STA lifecycle: `__rtw89_ops_sta_add()`, `__rtw89_ops_sta_assoc()`, `__rtw89_ops_sta_disassoc()`, `__rtw89_ops_sta_disconnect()`, and `__rtw89_ops_sta_remove()` map mac80211 station-state transitions to rtw89 link add/assoc/disassoc/disconnect/remove and MAC ID ownership rules.
- BSS/AP callbacks: `rtw89_ops_vif_cfg_changed()`, `rtw89_ops_link_info_changed()`, `rtw89_ops_start_ap()`, `rtw89_ops_stop_ap()`, and `rtw89_ops_set_tim()` update BSSID CAM, beacon content, CQM/beacon filters, HE BSS color, MU group tables, 6 GHz TPE power, AP firmware role state, and beacon work.
- EDCA/rate/control callbacks: `rtw89_ops_conf_tx()`, `rtw89_ops_ampdu_action()`, `rtw89_ops_set_bitrate_mask()`, `rtw89_ops_sta_rc_update()`, `rtw89_ops_set_rts_threshold()`, and `rtw89_ops_set_tid_config()` update firmware EDCA, MU-EDCA registers, aggregation state, BA CAM, RA masks, RTS threshold, and per-TID policy.
- Scan/channel callbacks: software scan start/complete, hardware scan/cancel, add/remove/change/assign/unassign/switch channel contexts, channel-switch beacon, and remain-on-channel operations all route into `fw.c`, `chan.c`, and ROC helpers.
- MLO callbacks: `rtw89_ops_can_activate_links()`, `rtw89_ops_change_vif_links()`, and `rtw89_ops_change_sta_links()` validate link counts, stage firmware link transitions, add/remove per-link VIF and STA objects, and reapply association/security state.
- Power-management callbacks under `CONFIG_PM`: suspend/resume integrate with WoW, track-work cancellation/restart, wakeup enablement, and GTK rekey data storage.

## Control Flow

The normal interface path is: mac80211 calls `add_interface`; the driver leaves IPS, enables beacon filter flags if firmware supports them, acquires a MAC ID and port bitmap entry, initializes `rtw89_vif`, adds it to `rtwvifs_list`, creates the idle link, calls `__rtw89_ops_add_iface_link()`, then recalculates low power state. Removal reverses this flow by cancelling ROC/link work, removing link MAC state, unsetting the link, releasing port/MAC ID, clearing monitor-mode tracking, and entering IPS if allowed.

STA state follows mac80211's state machine. `NOTEXIST -> NONE` allocates and initializes station/link state. `AUTH -> ASSOC` associates AP/TDLS peers immediately, while station-mode AP association is deferred until BSS info is available. `ASSOC -> AUTH` disassociates, `AUTH -> NONE` disconnects and frees pending BA/ROC TX work, and `NONE -> NOTEXIST` removes link state and releases MAC IDs for AP/TDLS peers.

Scan flow is explicit about concurrency: hardware scan is rejected without firmware scan-offload support, while already scanning, or while off-channel. It leaves LPS/IPS, initializes scan state, sends firmware offload, and aborts local state if firmware offload fails. Several paths abort active scans before AP start, remain-on-channel, disconnect handling, or link changes to keep firmware/mac80211 state coherent.

MLO link changes use a two-phase process. `can_activate_links()` validates link capacity, leaves LPS, and stores a transition record in `rtwvif->ml_trans`. `change_vif_links()` optionally snapshots old link configuration under RCU for removal, leaves IPS, aborts scans, notifies firmware for adding/removing links at the right phase, removes old links, synchronizes and frees the snapshot, adds new links or recreates the idle link, and re-enters IPS. `change_sta_links()` mirrors this for station links and reapplies association, BSS programming, and pairwise security CAM attachments.

## State And Persistence Behavior

- Driver-wide lists/bitmaps include `rtwdev->rtwvifs_list`, `rtwdev->hw_port`, MAC ID allocation state, `rtwdev->total_sta_assoc`, scan state, `pure_monitor_mode_vif`, workqueues, and power-save flags.
- VIF state includes MAC address, off-channel/ROC state, traffic stats, P2P NoA state, per-link array, idle link fallback, MLO mode, transition record, and optional RCU snapshot of old link configs.
- VIF-link state includes port, MAC index, channel context assignment, BSSID, TX queue parameters, beacon/CSA/MCC work items, general packet list, regulatory 6 GHz power, and TSF/beacon sync counters.
- STA state includes main MAC ID, per-link array, ROC queue, AMPDU map/params, pairwise security CAM bitmap, disassociation flag, and TDLS accounting.
- Hardware/firmware persistence is updated through MAC CAMs, BSSID CAM, BA CAM, security CAM, CMAC/DMAC firmware tables, EDCA/MU-EDCA registers, beacon templates, scan offload state, and WoW offload state.

## Dependencies And Integration Points

This file includes `cam.h`, `chan.h`, `coex.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `ps.h`, `reg.h`, `sar.h`, `ser.h`, `util.h`, and `wow.h`. It depends on mac80211/cfg80211 objects such as `ieee80211_hw`, `ieee80211_vif`, `ieee80211_bss_conf`, `ieee80211_sta`, TXQs, channel contexts, scan requests, AMPDU parameters, bitrate masks, survey info, and WoWLAN configuration. `rtw89_ops` is exported and later duplicated/customized during core registration.

## Risks And Edge Cases

- Many callbacks assume the wiphy lock, and most assert it. Calling equivalent helpers outside that context risks races with mac80211 link and station state.
- Link lookups can fail during MLO transitions; the file logs and returns `-ENOLINK` or exits, but callers must tolerate partial transitions.
- `rtw89_ops_change_interface()` removes and re-adds the interface in place. Failure can leave the original type already removed, so recovery depends on mac80211's handling of the failed change.
- 6 GHz AP start is rejected with `-EOPNOTSUPP`; callers need coverage for this policy.
- Key removal flushes software, HCI, and MAC queues before deleting security CAM entries. Missing a flush can expose use-after-key or encrypted-frame ordering bugs.
- Hardware scan, remain-on-channel, AP start, and link changes all abort scans; regressions here tend to show up as stuck scan state or firmware/off-channel mismatch.
- MLO removal uses an RCU snapshot of old link configs and synchronous `synchronize_rcu()`. Ordering is important because removal helpers may dereference old configs while mac80211 will free them after callback return.

## Test Signals

- Interface add/remove/change for station, AP, P2P, monitor, and TDLS paths; verify MAC ID/port release under failure.
- STA state transition tests including station-mode deferred association, AP peers, TDLS peers, disassociation, and removal.
- Scan tests covering firmware unsupported fallback, concurrent scan rejection, scan abort on disconnect/AP/ROC/link change, and successful hardware offload.
- MLO tests for active link validation, adding/removing VIF links, adding/removing STA links, pairwise key reattachment, and idle-link restoration when `new_links` is zero.
- Security tests for SET_KEY/DISABLE_KEY, queue flush ordering, pairwise CAM map preservation across link changes, and EAPOL coexistence notification.
- Power tests for IPS/LPS transitions around config, scan, VIF lifecycle, suspend/resume WoW, and rfkill polling while not running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac_be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac_be.c

## Purpose

`mac_be.c` is the BE-generation MAC implementation for the `rtw89` driver. It fills `rtw89_mac_gen_be`, the BE instance of the generation dispatch table declared in `mac.h`, and implements BE-specific register programming for RTL8922A/RTL8922D style devices. The file covers memory maps, port register bases, HFC/DLE configuration, DMAC/CMAC bring-up, firmware CPU boot/download status, DBCC/band1 enablement, coexistence grants, PPDU/PHY reporting, beamformee setup, error dumping, TX queue empty checks, scan-offload hooks, efuse hooks, and WoW MAC preparation.

## Important APIs, Tables, And Functions

- Static tables `rtw89_mac_mem_base_addrs_be`, `rtw89_port_base_be`, and `rtw89_mac_mu_gid_addr_be` provide BE memory window bases, per-port register bases, and MU group ID register addresses.
- HFC functions `hfc_get_mix_info_be()`, `hfc_h2c_cfg_be()`, `hfc_mix_cfg_be()`, and `hfc_func_en_be()` read/program BE page accounting, precedence thresholds, public/WP page limits, and HCI flow-control enables.
- DLE functions `dle_func_en_be()`, `dle_clk_en_be()`, `dle_mix_cfg_be()`, `chk_dle_rdy_be()`, `wde_quota_cfg_be()`, `ple_quota_cfg_be()`, `dle_buf_req_be()`, `set_cpuio_be()`, and `dle_quota_change_be()` implement BE WDE/PLE page size, bounds, quota, buffer request, CPU queue operation, and DBCC quota update behavior.
- Power/firmware functions `rtw89_mac_reset_pwr_state_be()`, `rtw89_mac_disable_cpu_be()`, `rtw89_mac_fwdl_enable_wcpu_be()`, `fwdl_get_status_be()`, and `rtw89_fwdl_check_path_ready_be()` reset MAC power state, hold/restart WCPU/DCPU-related state, set firmware download enables, boot WCPU, and decode firmware-download state.
- Bring-up functions `dmac_func_en_be()`, `cmac_share_func_en_be()`, `cmac_pwr_en_be()`, `cmac_func_en_be()`, `sys_init_be()`, `mac_func_en_be()`, `dmac_init_be()`, `cmac_init_be()`, and `trx_init_be()` sequence BE hardware initialization.
- CMAC init substeps cover scheduler, address CAM reset, RX filters, NAV, spatial reuse, TMAC, TRX protocol, RMAC, response packet control, common sub-band programming, protocol aggregation/CTS behavior, and CMAC DMA queue routing.
- DBCC and band1 functions `band1_enable_be()`, `band1_disable_be()`, `dbcc_enable_be()`, and `dbcc_bb_ctrl_be()` control second-band CMAC/BB power, DLE quota changes, preload, IMR, and firmware notification.
- Exported/shared helpers include `rtw89_mac_cfg_gnt_v2()`, `rtw89_mac_cfg_gnt_v3()`, `rtw89_mac_cfg_ctrl_path_v2()`, `rtw89_mac_stop_sch_tx_v2()`, `rtw89_mac_resume_sch_tx_v2()`, and `rtw89_mac_cfg_phy_rpt_be()`.
- Beamforming helpers `rtw89_mac_init_bfee_be()`, `rtw89_mac_set_csi_para_reg_be()`, `rtw89_mac_csi_rrsc_be()`, and `rtw89_mac_bf_assoc_be()` program BE beamformee response, CSI parameters, and CSI rate report selection from peer HT/VHT/HE capabilities.
- Diagnostics include `rtw89_mac_dump_qta_lost_be()`, `rtw89_mac_dump_cmac_err_status_be()`, `rtw89_mac_dump_err_status_be()`, dispatcher dumps, and `mac_is_txq_empty_be()`.

## Control Flow

System initialization starts through the generation callback `sys_init_be()`: enable DMAC functions, enable shared CMAC functions, power CMAC0, enable CMAC0 functions, and leave chip-specific function enable as a no-op. `mac_func_en_be()` is the recovery/resume-style variant that re-enables DMAC/shared CMAC and then conditionally re-enables any CMAC whose function-enable bit is already present in `R_BE_FEN_RST_ENABLE`.

TRX initialization is layered. `trx_init_be()` calls `dmac_init_be()` for common DMAC resources, then `cmac_init_be()` for CMAC0. If the quota mode is DBCC, it enables band1 through DLE quota migration, preload, CMAC1 power/function enable, CMAC1 initialization, BB1 reset control, and CMAC1 IMR. It then enables DMAC/CMAC0 IMRs, writes the top-level error IMRs, configures host release reports, and applies chip-specific response signature behavior.

`dmac_init_be()` sequences DLE init, preload init, HFC init, STA scheduler, MPDU processing, security engine, TX packet control, and MLO table init. Each substep validates DMAC availability where needed and returns immediately on the first failure with a targeted log message.

`cmac_init_be()` sequences scheduler, address CAM, RX filter, CCA, NAV, spatial reuse, TMAC, TRX protocol, RMAC, response packet control, common sub-band setup, protocol aggregation, and CMAC DMA setup. Most substeps validate the requested CMAC with `rtw89_mac_check_mac_en()` and derive band-specific registers through `rtw89_mac_reg_by_idx()`.

Firmware boot flow sets firmware download enable bits in `set_cpu_en()`, clears stale SER/debug/handshake registers in `wcpu_on()`, configures clock/watchdog/boot mode/boot reason, toggles WCPU reset/hold bits, and optionally waits for FreeRTOS readiness when not in download mode. Firmware download status is decoded from `R_BE_WCPU_FW_CTRL` and mapped to common `RTW89_FWDL_*` states.

WoW MAC configuration stops host RX, disables sniffer mode, moves RX through CPU IO, disables PPDU status, clears forwarding/action/trigger registers, and marks WoW not ready on entry. On exit it restores CPU IO RX, clears host RX stop, attempts to restore RX filtering, and re-enables PPDU status.

## State And Persistence Behavior

- BE generation state is exposed through the exported `rtw89_mac_gen_be` table and selected by chip files such as RTL8922A/RTL8922D through `chip->mac_def`.
- Device flags track DMAC/CMAC function/power readiness, firmware readiness, unplugged state, and SER handling. `rtw89_mac_check_mac_en_be()` relies on these flags instead of reading hardware directly.
- `rtwdev->mac.hfc_param`, `rtwdev->mac.dle_info`, and `rtwdev->mac.qta_mode` are read or updated by HFC/DLE init and quota paths.
- Hardware state persists in BE registers for HFC page thresholds, WDE/PLE page sizes and quotas, scheduler enablement, CAM resets, security engine, MLO table, CMAC power/function bits, IMRs, PPDU/PHY report settings, coexistence grants, XTAL SI values, and WoW forwarding controls.
- Per-peer beamforming state is derived from mac80211 link-station capabilities under RCU and then persisted in CMAC CSI/beamformee registers.

## Dependencies And Integration Points

The file includes `debug.h`, `efuse.h`, `fw.h`, `mac.h`, and `reg.h`. It depends heavily on register definitions, bitfield macros, common MAC orchestration in `mac.c`, firmware scan/offload functions in `fw.c`, efuse functions in `efuse.c`, HCI error dump callbacks, and chip-specific constants in `rtwdev->chip`. The BE generation table wires this implementation into common call sites used by core initialization, firmware download, WoW, scan, SER, debugfs, PHY/TX power code, and mac80211-triggered beamforming association.

## Risks And Edge Cases

- Hardware programming order is critical. DLE/HFC/STA scheduler/MPDU/security/MLO initialization failures short-circuit, so partial hardware state can exist until higher layers recover or power-cycle.
- Several branches are chip-specific (`RTL8922A` versus `RTL8922D`, plus `RTL8922D_CID7090`); new BE variants must audit every conditional register layout and mask difference.
- `rtw89_mac_check_mac_en_be()` trusts software flags. If flags drift from real hardware state after SER, suspend, or failed init, later register operations may be skipped or attempted incorrectly.
- DLE page-size constraints reject WDE 256-byte pages and PLE 64-byte pages. Bad quota/size data from common tables will fail initialization.
- DBCC enablement changes DLE quotas and powers CMAC1/BB1. Failure in the middle can leave band1 partially enabled; the caller must handle recovery.
- `rtw89_mac_get_txpwr_cr_be()` rejects CMAC1 addresses in SCC mode and suppresses logs during SER handling. TX power callers must handle false returns.
- WoW resume uses `rtw89_write32_set(rtwdev, R_BE_RX_FLTR_OPT, R_BE_RX_FLTR_OPT)`, which looks unusual because the register address is also used as the set mask; this deserves scrutiny in behavior tests.
- Error dump functions read many registers conditionally based on top-level ISR bits; dump quality depends on the hardware still being accessible and CMAC flags reflecting real state.

## Test Signals

- Boot/init tests on RTL8922A and RTL8922D covering power reset, firmware download status, DLE/HFC init, CMAC0 init, DBCC CMAC1 init, and IMR enablement.
- HCI matrix tests for PCIe, USB, and SDIO DMA mode programming in `rtw89_mac_dmac_func_pre_en_be()`, plus POH versus STF release-report setup.
- DLE/HFC tests for page size rejection, quota programming, CPU IO buffer request, queue operation timeout, quota-update timeout, and TX queue empty detection.
- Scan/WoW tests verifying BE scan callback wiring, WoW entry/exit register effects, CPU IO RX movement, PPDU status toggling, and host RX stop clearing.
- Beamforming association tests with peers advertising no BF, HT, VHT, HE, SU BF, MU BF, LDPC/STBC, and varied sounding dimensions.
- SER/error tests for L0/L1/DMAC/CMAC/RXI300 dump paths, `rtwdev->hci.ops->dump_err_status()`, and software flag consistency after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac_be.c -->
