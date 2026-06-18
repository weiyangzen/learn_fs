# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac.c

## Purpose

`mac.c` is the Realtek `rtw89` AX-generation MAC implementation. It is the central hardware-control layer between the common `rtw89` driver, mac80211/cfg80211 runtime objects, firmware H2C/C2H messages, and the chip register map. The file programs DMAC/CMAC blocks, DLE/HFC packet-buffer quotas, power and firmware-download state, VIF port registers, scan/offload event handling, Bluetooth coexistence, beamforming, packet drop, WoW MAC mode, and the AX-generation `struct rtw89_mac_gen_def` operation table exported as `rtw89_mac_gen_ax`.

The code is heavily register-oriented. Most behavior is expressed as small helpers that validate the target MAC block is enabled, write bitfields into `R_AX_*`/`B_AX_*` registers, poll readiness bits, and route errors through `rtw89_err()`, `rtw89_warn()`, or SER notification.

## Important APIs, Types, And Data

- `rtw89_mac_gen_ax`: exported AX MAC-generation definition. It binds register addresses, masks, helper callbacks, firmware-download hooks, DLE/HFC callbacks, beamforming callbacks, scan hooks, EFUSE/PHY-cap hooks, WoW hooks, and debug dump callbacks used by common/chip code.
- `rtw89_mac_size`: exported static size/quota catalogue for DLE/HFC memory layouts. It contains WDE/PLE page sizes, quota tables, reserved quota sizes, and DLE input layouts for PCIe/USB/DLFW/SCC/WOW modes across supported chips.
- `rtw89_mac_mem_base_addrs_ax`: maps `enum rtw89_mac_mem_sel` to indirect memory base addresses for AXIDMA, shared buffers, DMAC/CMAC tables, CAMs, TX FIFOs, CPU local memory, and BE/AX variants.
- `struct rtw89_dev`: main mutable driver state. This file updates `rtwdev->mac`, `rtwdev->hal`, `rtwdev->flags`, `rtwdev->scan_info`, `rtwdev->mcc`, `rtwdev->mlo`, `rtwdev->wow`, `rtwdev->tx_rpt`, and chip/HCI callback state.
- `struct rtw89_chip_info` and `struct rtw89_mac_gen_def`: chip-specific constants and callback dispatch. Many helpers branch on `chip_id`, `chip_gen`, `hci.type`, `dle_type`, firmware features, and chip ops.
- `struct rtw89_vif_link` and `struct rtw89_sta_link`: per-link VIF/station state used to program port registers, MAC IDs, TSF sync, beacon behavior, beamforming, packet drop, retry/time limits, and firmware role/CAM messages.
- `struct rtw89_mac_h2c_info` / `struct rtw89_mac_c2h_info`: synchronous H2C/C2H register-message containers used for PHY capability readout, scheduler TX enable, WoW CPU-IO RX control, and firmware feature requests.
- C2H handler arrays: `rtw89_mac_c2h_ofld_handler`, `rtw89_mac_c2h_info_handler`, `rtw89_mac_c2h_mcc_handler`, `rtw89_mac_c2h_misc_handler`, `rtw89_mac_c2h_mlo_handler`, `rtw89_mac_c2h_mrc_handler`, `rtw89_mac_c2h_wow_handler`, and `rtw89_mac_c2h_ap_handler`.

## Major Function Groups

### Register, LTE, DFI, And SER Debug Helpers

- `rtw89_mac_mem_write()` / `rtw89_mac_mem_read()` perform indirect memory accesses through `filter_model_addr` and `indir_access_addr`.
- `rtw89_mac_check_mac_en_ax()` verifies DMAC or CMAC0/CMAC1 function bits and rejects dead/invalid reads.
- `rtw89_mac_write_lte()` / `rtw89_mac_read_lte()` poll LTE access readiness, then write/read LTE coexistence registers.
- `rtw89_mac_dle_dfi_cfg()`, `rtw89_mac_dle_dfi_quota_cfg()`, and `rtw89_mac_dle_dfi_qempty_cfg()` query WDE/PLE debug interfaces for DLE quota and queue-empty state.
- `rtw89_mac_dump_dmac_err_status()`, `rtw89_mac_dump_cmac_err_status_ax()`, `rtw89_mac_dump_qta_lost_ax()`, and `rtw89_mac_dump_err_status_ax()` dump detailed register snapshots for DMAC, CMAC, DLE, security, dispatcher, HAXI/AXIDMA, MLO/PLRLS, and quota-lost conditions. `rtw89_mac_get_err_status()` receives firmware halt status, normalizes some WCPU scenarios, optionally suppresses known noisy RTL8852C SER logs, dumps firmware/driver state, and clears C2H control bits according to firmware features.
- `rtw89_mac_set_err_status()` sends driver-to-firmware SER control/error requests through `R_AX_HALT_H2C`.

### HFC And DLE Initialization

- `hfc_reset_param()` loads chip/HCI/quota-mode HFC defaults into `rtwdev->mac.hfc_param`.
- `hfc_ch_ctrl()`, `hfc_pub_ctrl()`, `hfc_mix_cfg_ax()`, `hfc_h2c_cfg_ax()`, `hfc_func_en_ax()`, and update/check helpers program HCI flow-control channel/public page limits and update software mirrors from page-info registers.
- `rtw89_mac_hfc_init()` is the public HFC initializer. It disables HFC, programs channels/public/mixed settings, optionally re-enables HFC/H2C, then refreshes channel/public accounting.
- `get_dle_mem_cfg()` selects a `struct rtw89_dle_mem` for the current HCI DLE type and quota mode, while updating `rtwdev->mac.dle_info`.
- `rtw89_mac_dle_init()` validates DLE memory usage against chip FIFO size, disables DLE, enables clocks, programs WDE/PLE page split through `dle_mix_cfg_ax()`, programs quotas, enables DLE, and polls WDE/PLE init readiness.
- `rtw89_mac_resize_ple_rx_quota()` swaps RX PLE quota between SCC and WOW layouts for WoW entry/exit on supported AX chips.
- `rtw89_mac_dle_quota_change()` and `dle_quota_change_ax()` support runtime DBCC quota change by requesting WDE/PLE buffers and enqueueing no-report packets through CPUIO.

### Power, Firmware Download, And MAC Bring-Up

- `rtw89_mac_pwr_on()` / `rtw89_mac_pwr_off()` wrap `rtw89_mac_power_switch()`. Power-on resets power state, runs chip power sequence/callback, reads EFUSE secure data before probe completion, sets POWERON/DMAC/CMAC0 flags, updates BTC scoreboard, and clears AON interrupts. Power-off clears power/FW/CMAC flags, updates scoreboard, and marks PHY entities inactive.
- `rtw89_mac_power_mode_change()` sends RPWM requests for active/deep power states and polls CPWM sequence/status. Exhausted retries log an error and notify SER assertion.
- `rtw89_mac_enable_cpu_ax()` prepares WCPU firmware-download or runtime boot state, clears halt registers, enables CPU clock, records boot reason, and optionally waits for FreeRTOS ready. `rtw89_mac_disable_cpu_ax()` clears FW-ready state, disables WCPU/FWDL/H2C paths, disables watchdog, and toggles platform enable.
- `rtw89_mac_dmac_pre_init()` enables minimal HCI/DMAC functions, initializes DLE in firmware-download mode, and enables HFC H2C flow before firmware download.
- `rtw89_mac_partial_init()` enables HCI DMA TRX, optionally preinitializes BB MCU, performs DMAC preinit, runs HCI preinit, and downloads firmware.
- `rtw89_mac_preinit()` powers on and invokes optional generation-level MAC function enable. `rtw89_mac_init()` completes partial init, enables BB/RF, runs system init, TRX init, feature init, HCI post init, and sends early/offload H2C messages. On failure it powers the device back off.

### DMAC, CMAC, TRX, And Interrupt Initialization

- `sys_init_ax()` enables DMAC, CMAC0, and chip-level function bits.
- `dmac_init_ax()` initializes DLE, preload, HFC, station scheduler, MPDU processing, and security engine.
- `cmac_init_ax()` sequences scheduler, address CAM reset, RX filter, CCA/NAV/spatial reuse, TMAC, TRX protocol, RMAC, common CMAC, PTCL, and CMAC DMA initialization.
- `trx_init_ax()` initializes DMAC and CMAC0, conditionally enables DBCC/CMAC1, enables DMAC/CMAC IMRs, enables top-level error IMRs, and configures host release reports.
- `band1_enable_ax()` handles DBCC CMAC1 enablement: stop scheduler TX, back up MACID sleep/pause registers, force idle, change DLE quota, restore state, resume TX, enable CMAC1, initialize CMAC1, and unisolate BB function bits.
- `enable_imr_ax()` dispatches DMAC or CMAC error-mask programming. Individual IMR helpers program WDRLS, security, MPDU, station scheduler, TX packet control, WDE/PLE, packet-in, dispatcher, CPUIO, BBRPT, scheduler, PTCL, CDMA, PHY interface, RMAC, and TMAC masks.

### VIF, Port, Beacon, And TSF Control

- `rtw89_port_base_ax` and `rtw89_mac_mu_gid_addr_ax` define AX register bases for port configuration and MU-MIMO GID tables.
- `rtw89_mac_port_update()` is the main port reconfiguration sequence. It validates the port, temporarily disables existing function state, clears beacon reports, programs net type, beacon protection, RX/TX enablement by net type, beacon interval/DTIM/HIQ/drop/setup/hold/mask/early/aggregation/BSS color/MBSSID, enables port function, randomizes AP TSF offsets to reduce beacon conflict, and updates beacon parser reporting.
- `rtw89_mac_vif_init()` calls port update, initializes DMAC/CMAC tables for non-secure AX firmware, unpauses the MAC ID, creates firmware role/join state, initializes CAM, sends CAM, and sends default CMAC/DMAC tables.
- `rtw89_mac_vif_deinit()` removes firmware role and CAM state.
- `rtw89_mac_port_get_tsf()` reads TSF low/high registers for a VIF link.
- `rtw89_mac_enable_beacon_for_ap_vifs()` toggles AP beacon TX globally or by channel through helper iteration.
- `rtw89_mac_stop_ap()` disables AP port function and resets randomized TSF bookkeeping.
- `rtw89_mac_set_he_obss_narrow_bw_ru()` scans BSSes on DFS channels and disables HE narrow-bandwidth RU trigger behavior if any neighbor lacks tolerance support. `rtw89_mac_set_he_tb()` disables EHT TB trigger for HE-only links on BE chips.

### C2H Event Handling

- `rtw89_mac_c2h_chk_atomic()` classifies C2H messages that must run in interrupt/atomic context. It also marks scan-offload responses with scan metadata and completes scan stop waits when end-scan notifications arrive.
- `rtw89_mac_c2h_handle()` performs class/function table dispatch and emits an `info_once` message for unsupported handlers.
- Scan offload: `rtw89_mac_c2h_scanofld_rsp()` handles leave/enter op-channel and scan-channel events, stops/wakes mac80211 queues, disables/enables AP beacons on op channel, updates entity channel, triggers/collects NHM measurements, continues segmented scans, or completes scan requests.
- Firmware acknowledgement: `rtw89_mac_c2h_done_ack()` completes PS/offload wait conditions for IPS config, scan channel add/start, BE scan start, and TRX protection. `rtw89_mac_c2h_pkt_ofld_rsp()` completes packet-offload waits.
- Beacon filtering: `rtw89_mac_bcn_fltr_rpt()` reports beacon loss or RSSI threshold notifications to mac80211/cfg80211, while respecting active scan/offchannel/NOA and MCC GO beacon detection.
- MCC/MRC/MLO: handlers parse ack/status/TSF reports and complete the appropriate `rtwdev->mcc.wait` or `rtwdev->mlo.wait` condition.
- TX report: `rtw89_mac_c2h_tx_rpt()` maps firmware SW-defined report slots back to pending SKBs under `tx_rpt->skb_lock`, waits until retry limit is reached for failures, clears the slot, and reports TX status.
- WoW/AP: `rtw89_mac_c2h_wow_aoac_rpt()` copies AOAC wake/security report material into `rtwdev->wow.aoac_rpt`. `rtw89_mac_c2h_pwr_int_notify()` updates remote station PS flags and informs mac80211.

### Coexistence, Beamforming, Per-Station Limits, Packet Drop, And WoW

- `rtw89_mac_coex_init()` / `_v1()` set GPIO/PTA/BTCCA/BTC mode, LTE grant behavior, and PTA direction for legacy and v1 coexistence register models.
- `rtw89_mac_cfg_gnt()` / `_v1()`, `rtw89_mac_cfg_plt_ax()`, `rtw89_mac_cfg_sb()`, `rtw89_mac_get_sb()`, `rtw89_mac_cfg_ctrl_path()` / `_v1()`, `rtw89_mac_get_ctrl_path()`, and `rtw89_mac_get_plt_cnt_ax()` expose grant, packet-latency test, scoreboard, control-path, and counter controls to BTC code.
- Beamforming receive support is initialized by `rtw89_mac_bf_assoc_ax()` when an associated station has beamformer capability. It calls `rtw89_mac_init_bfee_ax()`, programs CSI parameters from HE/VHT capabilities, sets RRSC, controls BFee enable/timer flags, maintains MU GID tables, and dynamically toggles BFee/timer behavior based on traffic levels.
- `rtw89_mac_set_tx_time()` / `get_tx_time()` and `rtw89_mac_set_tx_retry_limit()` / `get_tx_retry_limit()` program or read CCTL/CMAC limits for per-station TX duration and retry count.
- `rtw89_mac_pkt_drop_vif()` iterates stations in a VIF and sends firmware packet-drop H2Cs per access category. `rtw89_mac_ptk_drop_by_band_and_wait()` polls TX queue empty and falls back to band-wide packet-drop H2C when firmware supports it.
- `rtw89_wow_config_mac_ax()` adjusts PLE RX quota, stops/resumes RX header processing, toggles CPU-IO RX, disables sniffer/PPDU/action forwarding on WoW entry, and restores RX/PPDU/forwarding state on exit.
- XTAL SI helpers `rtw89_mac_write_xtal_si_ax()` and `rtw89_mac_read_xtal_si_ax()` perform polled crystal-sideband access with unplug-aware warnings.

## Control Flow Summary

1. Probe/preinit calls `rtw89_mac_preinit()`: power on, optionally enable MAC functions.
2. Main bring-up calls `rtw89_mac_init()`: enable HCI DMA, preinitialize DLE/HFC for firmware download, download firmware, enable BB/RF, enable DMAC/CMAC functions, initialize DLE/HFC/CMAC/TRX/security/IMR state, initialize chip features, run HCI post-init, and send early H2Cs.
3. VIF creation calls `rtw89_mac_add_vif()`/`rtw89_mac_vif_init()`: program port registers, initialize MAC tables, send role/join/CAM/default table H2Cs.
4. Runtime operations call exported helpers for port update, scheduler TX stop/resume, TX queue flush, RTS threshold update, PPDU status, coexistence grants, beamforming, packet drop, WoW mode, and power-mode transitions.
5. Firmware interrupts deliver C2H messages. Atomic classification may complete waits immediately or annotate scan events; normal dispatch then invokes class/function handlers to update scan, beacon, MCC/MRC/MLO, WoW, AP PS, TX report, and wait state.
6. Error/SER flow reads halt C2H state through `rtw89_mac_get_err_status()`, optionally dumps firmware and MAC registers, and sends control requests through `rtw89_mac_set_err_status()`.

## State And Persistence Behavior

This file does not persist data to disk. Its persistence is hardware/firmware and in-memory driver state:

- Hardware register state is programmed throughout DMAC/CMAC/DLE/HFC/port/BTC/BF/WoW paths and survives until reset/power-off or later reconfiguration.
- `rtwdev->flags` records POWERON, DMAC/CMAC function availability, FW ready, BFee enable/timer state, unplugged/changing-interface conditions, and SER log suppression.
- `rtwdev->mac.dle_info` stores selected quota mode, PLE page size/free pages, RX quotas, reserved quota tables, and DLE inputs. `rtwdev->mac.hfc_param` stores configured and observed HFC limits.
- `rtwdev->mac.rpwm_seq_num` and `cpwm_seq_num` track firmware power-management handshake sequencing.
- `rtwdev->hal` is updated from firmware PHY-cap reports with NSS, antenna path, diversity, EHT/MCS capability flags.
- `rtwdev->scan_info` tracks scanning VIF, op/extra-op channels, scan sequence, abort state, channel list, and scan delays.
- `rtwdev->tx_rpt.skbs[]` holds pending SKBs for firmware TX reports and is protected by `skb_lock`.
- `rtwdev->wow.aoac_rpt` receives wake/offload security report material from firmware.
- VIF link fields such as `rand_tsf_done`, `net_type`, `port`, `mac_idx`, `mac_id`, `trigger`, and `chanctx_idx` influence subsequent port, TSF, and packet-drop programming.

## Dependencies And Integration Points

- Local `rtw89` headers: `cam.h`, `chan.h`, `debug.h`, `efuse.h`, `fw.h`, `mac.h`, `pci.h`, `phy.h`, `ps.h`, `reg.h`, `ser.h`, and `util.h`.
- Hardware accessors and bit helpers: `rtw89_read*()`, `rtw89_write*()`, `*_mask()`, `*_set()`, `*_clr()`, `FIELD_PREP`, `FIELD_GET`, `u32_replace_bits`, and chip-specific register helpers such as `rtw89_mac_reg_by_idx()`.
- Firmware paths: `rtw89_fw_download()`, `rtw89_fw_msg_reg()`, scan offload H2Cs, CAM/role/default-table H2Cs, packet-drop H2Cs, firmware logs/debug dumps, and firmware feature checks via `RTW89_CHK_FW_FEATURE`.
- HCI integration: `rtwdev->hci.ops` for pre/post init and error dumps, HCI type-specific power/DLE/HFC behavior, RPWM/CPWM addresses, and DMA mode selection.
- mac80211/cfg80211: VIF/station objects, RCU dereference helpers, BSS iteration, beacon loss/RSSI notification, queue stop/wake, TSF/channel context changes, station PS transitions, and atomic station iteration.
- Chip/PHY/BTC/SER subsystems: chip ops for BB/RF and default tables, PHY NHM and channel assignment, BTC scoreboard/grant/PLT controls, and SER notification/recovery state.

## Risks And Edge Cases

- Register programming is order-sensitive. DLE/HFC/CMAC initialization, DBCC enablement, firmware download preinit, and WoW entry/exit depend on exact sequencing and readiness polling.
- Many paths branch on `chip_id`, `chip_gen`, HCI type, firmware feature bits, and secure boot. Adding a chip variant without complete register/mask tables can silently misprogram hardware.
- Poll timeouts can leave partially initialized hardware. Most init paths return errors, but some side effects remain until reset/power-off.
- `band1_enable_ax()` backs up pause/sleep registers, forces all MACIDs paused/sleeping, and can return before restore/resume if idle or quota change fails. Reviewers should check whether callers rely on later reset for recovery.
- C2H handlers run in mixed atomic/non-atomic contexts. Handlers marked atomic must avoid sleeping and must protect shared state; non-atomic scan handlers perform queue and channel side effects.
- `rtw89_mac_c2h_tx_rpt()` trusts firmware SW-defined report fields within static mask assumptions and manipulates SKB slots under a spinlock. Incorrect report formats for new chips could drop or leak TX status.
- Some handlers are intentionally empty or NULL. Unsupported C2H functions only log once; missing implementations can be hard to notice unless firmware starts sending new events.
- RCU-protected dereferences of VIF/station/link state are common. Any future use of these pointers outside the RCU critical section needs careful lifetime handling.
- Power-off for unplugged devices avoids IO, but many normal helpers still perform register access unless callers check POWERON/UNPLUGGED.
- WoW state rewrites RX quota and forwarding registers. Failures midway through entry/exit can leave RX or report paths disabled until reinitialization.

## Test Signals

- Build coverage: compile the `rtw89` driver with AX chips enabled and warnings treated seriously enough to catch register/mask type mistakes, enum drift, and missing prototypes.
- Probe/init smoke: device probe should complete `rtw89_mac_preinit()` and `rtw89_mac_init()` without `DLE init`, `HCI FC init`, `CMAC init`, `enable IMR`, firmware download, or power-state errors.
- Firmware/SER: trigger or observe SER paths and confirm `rtw89_mac_get_err_status()` reports meaningful DMAC/CMAC register dumps without repeated suppressed RTL8852C noise.
- VIF workflows: add/remove STA/AP/P2P links, change interface type, start/stop AP, and verify port update, beacon TX/RX, TSF sync, CAM role creation/removal, and MACID pause handling.
- Scan offload: run normal, aborted, multi-part, DFS, and 6 GHz-capable scans. Watch queue stop/wake, op-channel AP beacon toggling, NHM trigger/result, and scan completion.
- DBCC and dual-band: enable a DBCC quota mode and confirm CMAC1 enablement, quota change, IMR setup, and CMAC1 RX/TX behavior.
- Power management: exercise IPS/LPS/deep power transitions, RPWM/CPWM sequence checks, wake notification, unplug/power-off, USB boot-mode reset, and WoW entry/exit.
- Coexistence: validate BTC PTA modes, grant control, scoreboard updates, control path switching, and PLT counters across chip variants.
- Beamforming: associate HE/VHT beamformer-capable stations, verify BFee enablement, CSI parameter/RRSC programming, GID table updates, traffic-based BFee monitor toggles, and disassociation cleanup.
- TX reporting and packet drop: stress retry-limit paths, TX report completion, queue flush, per-VIF/band packet-drop H2Cs, and no-packet-drop firmware feature behavior.
