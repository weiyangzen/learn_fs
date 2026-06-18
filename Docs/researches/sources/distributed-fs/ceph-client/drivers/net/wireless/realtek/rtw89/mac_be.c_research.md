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
