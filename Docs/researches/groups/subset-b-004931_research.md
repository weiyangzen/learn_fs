# subset-b-004931 research

This grouped report covers the Realtek rtw89 PHY and power-save source files assigned to subset-b-004931. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.h

## Purpose
`phy.h` is the central PHY contract for the rtw89 driver. It defines register-table encodings, rate-adaptation masks, dynamic-mechanism thresholds, PHY status IDs, transmit-power table layouts, RF calibration command APIs, generation-specific PHY callbacks, and inline register helpers used by AX and BE chip implementations. It does not implement the large algorithms itself; instead it provides the type, constant, and dispatch surface that ties chip-specific PHY files, firmware C2H/H2C handling, dynamic gain, environment monitoring, rate adaptation, TX power, RFK calibration, and channel information together.

## Important APIs, types, and definitions
- PHY table condition macros such as `get_phy_headline()`, `get_phy_target()`, `get_phy_cond_*()`, `PHY_COND_BRANCH_*`, and `PHY_COND_CHECK` describe conditional register-table parsing keyed by RFE/CV/package fields.
- `RA_MASK_*` constants encode CCK, OFDM, HT, VHT, HE, and EHT rate bitmaps, including 1-4 spatial stream layouts and EHT MCS0-11 subsets.
- CFO, UL TB, antenna diversity, CCX, DIG, PD threshold, EDCCA, NHM, and PHY status constants provide shared thresholds for dynamic PHY mechanisms.
- C2H enums (`rtw89_phy_c2h_ra_func`, `rtw89_phy_c2h_rfk_log_func`, `rtw89_phy_c2h_rfk_report_func`, `rtw89_phy_c2h_dm_func`, `rtw89_phy_c2h_class`) define firmware-to-host PHY message classes and functions.
- PHY status enums (`rtw89_phy_status_ie_type`, `rtw89_phy_status_bitmap`) enumerate parsed PPDU status information elements and packet-status bits.
- TX power structures include `rtw89_txpwr_byrate_cfg`, `rtw89_txpwr_track_cfg`, `rtw89_txpwr_limit_ax`, `rtw89_txpwr_limit_be`, `rtw89_txpwr_limit_ru_ax`, and `rtw89_txpwr_limit_ru_be`, with page-size constants validated by implementation code.
- `struct rtw89_phy_gen_def` is the generation-specific dispatch table. It contains CR base, PHY-status register addresses, CCX/CFO/BB-wrap register sets, address-offset logic, BB gain parsing, preinit hooks, channel-info setup, and TX power programming callbacks.
- Inline helpers `rtw89_phy_write*()`, `rtw89_phy_read*()`, `rtw89_phy_write32_idx()`, generation dispatchers, and TX power unit converters hide CR-base and factor differences.
- RFK declarations (`rtw89_rfk_tbl`, `RTW89_DECLARE_RFK_TBL`, `RTW89_DECL_RFK_*`) encode RF writes, BB writes, set/clear operations, and delays for the RFK parser.
- Function declarations expose PHY initialization, RF read/write variants, rate adaptation, RFK wait operations, C2H handling, CFO tracking, stat/env monitor tracking, DIG, antenna diversity, BSS color, UL TB control, EDCCA, channel-index coding, and NHM control.

## Control flow and state behavior
The header's main runtime pattern is indirect dispatch through `rtwdev->chip->phy_def`. Generic code calls wrappers such as `rtw89_phy_set_txpwr_byrate()`, `rtw89_phy_preinit_rf_nctl()`, or `rtw89_phy_ch_info_init()`, and the active chip generation supplies the actual implementation. Register helpers add `phy_def->cr_base` before MMIO access so AX/BE register maps can share call sites while selecting different base offsets.

PHY-index access is split between simple CR-base helpers and indexed helper declarations implemented elsewhere. `rtw89_bbmcu_write32()` also adjusts addresses for PHY1 if the address is below `0x10000`, then writes through the BBMCU offset. Subband conversion helpers persist no state; they normalize channel subbands into OFDM gain-offset, legacy BB-gain-band, or BE gain-band enums. TX power conversion helpers translate between RF, BB, MAC, and dBm units using per-chip factor fields and clamp dBm-to-MAC output to the signed MAC field range.

Most persistent state described by this header lives in `struct rtw89_dev`: `rtwdev->bb_gain`, `rtwdev->efuse`, `rtwdev->hal`, per-station rate-adaptation state, dynamic-mechanism state, and firmware completion state. The header fixes the memory layout expected by implementation files for TX power pages and RFK descriptors, so changing structure fields or sizes changes how runtime tables are serialized to hardware.

## Dependencies and integration points
`phy.h` includes `core.h` and depends on Linux bitfield helpers, rtw89 core types, channel/rate enums, RF path enums, firmware command structures, and mac80211 types referenced in prototypes. It is included by chip generation files such as `phy_be.c`, broader PHY implementation files, power-save code for `rtw89_phy_dm_reinit()`, and chip-specific table loaders. The exported generation definitions `rtw89_phy_gen_ax`, `rtw89_phy_gen_be`, and `rtw89_phy_gen_be_v1` are selected from `struct rtw89_chip_info`, making this header a key ABI between chip descriptions and generic PHY control.

## Risks and edge cases
- TX power page structures must match hardware page sizes exactly; implementation files rely on `BUILD_BUG_ON()` for BE sizes, but semantic ordering still depends on this header.
- RA masks and PHY status bit positions are protocol/hardware ABI. A wrong bit range can silently disable rates or misclassify received packets.
- Generation callback pointers are mostly assumed present. Missing callbacks in a chip definition can become null calls through inline dispatch.
- The inline CR-base helpers assume `rtwdev->chip->phy_def` is initialized and valid before use.
- Subband-to-gain mappings default to 2 GHz for unknown values, which is safe for switch exhaustiveness but can hide invalid channel state.
- RFK table macros encode opaque command streams; malformed tables can write wrong RF/BB registers without type-system protection.

## Test signals
Good signals include build coverage for all rtw89 chip modules, successful selection of the right `phy_def` at probe, table loading without condition-parser warnings, correct TX power page size assertions, valid RA masks in firmware station updates, PHY C2H dispatch for RA/DM/RFK classes, stable CFO/DIG/EDCCA/NHM watchdog activity, and no null-pointer faults when generic code calls PHY generation dispatchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy_be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy_be.c

## Purpose
`phy_be.c` implements the 802.11be generation-specific PHY definition for rtw89. It supplies BE and BE v1 register maps, BB gain table parsing, RF NCTL preinitialization, BB-wrapper initialization, channel-info setup, RFSI/bandedge controls, and TX power programming for by-rate, rate-offset, regulatory limits, and RU limits up to 320 MHz. The file exports `rtw89_phy_gen_be` and `rtw89_phy_gen_be_v1`, which generic PHY code reaches through `rtwdev->chip->phy_def`.

## Important APIs, types, and functions
- Static register descriptors `rtw89_ccx_regs_be`, `rtw89_ccx_regs_be_v1`, `rtw89_physts_regs_be*`, `rtw89_cfo_regs_be*`, and `rtw89_bb_wrap_regs_be*` map generic CCX, PHY status, CFO, and BB-wrapper operations onto BE register addresses and masks.
- `rtw89_phy0_phy1_offset_be()` and `_be_v1()` calculate PHY1 register offsets for selected register page ranges.
- `union rtw89_phy_bb_gain_arg_be` decodes packed BB gain-table addresses into config type, gain band, path, bandwidth, and subtype fields.
- `rtw89_phy_config_bb_gain_be()` routes BB gain table entries to gain-error, replacement-offset, op1dB, or direct PHY write handling, with bounds checks against path, bandwidth, gain-band, and EFUSE RFE type.
- `rtw89_phy_preinit_rf_nctl_be()` and `_be_v1()` program IQK/DPK resets and clock gates before RF NCTL use, with DBCC-aware PHY1 handling for the non-v1 map.
- BB-wrapper helpers initialize per-MACID power limits, TX path maps, TPU registers, force-control bits, FTM power registers, listen-path state, uplink power thresholds, RFSI QAM/DPD/CIM3K compensation, and bandedge controls.
- Exported `rtw89_phy_bb_wrap_set_rfsi_ct_opt()` and `rtw89_phy_bb_wrap_set_rfsi_bandedge_ch()` are callable by other chip code to update RFSI control and bandedge channel state.
- `rtw89_phy_set_txpwr_byrate_be()`, `rtw89_phy_set_txpwr_offset_be()`, `rtw89_phy_set_txpwr_limit_be()`, and `rtw89_phy_set_txpwr_limit_ru_be()` implement the TX power callbacks installed in the generation definitions.

## Control flow and state behavior
Generation setup is declarative at the bottom of the file: two exported `struct rtw89_phy_gen_def` instances point generic code to the proper register maps and callback functions. BE uses CR base `0x20000`; BE v1 uses base `0x0` with BE4 register names. During PHY initialization, generic code calls `preinit_rf_nctl`, then optional BB-wrapper and channel-info hooks. The BB-wrapper path clears per-MACID limit/path tables, zeroes by-rate/RU/rate-offset power pages, disables force paths, initializes FTM, and applies additional RFSI controls for RTL8922D or uplink power thresholds for RTL8922A. If DBCC is enabled, initialization is repeated for MAC1.

BB gain parsing is table-driven. A packed `reg->addr` is decoded, rejected if out of bounds, and then stored into `rtwdev->bb_gain.be` arrays for LNA/TIA gain error, replacement offsets by bandwidth/subchannel, or op1dB data. Flow-control-looking addresses are rejected, bypass config type is ignored, and config type 4 is only meaningful for EFUSE `rfe_type >= 50`. These writes persist in runtime driver memory rather than immediate hardware except for config type 15, which writes a PHY register.

TX power programming builds contiguous hardware pages. By-rate programming iterates bandwidths from 20 through 320 MHz and NSS 1-3 encodings up to `RTW89_NSS_2`, skips unsupported combinations for CCK and special single-NSS sections, reads signed table entries through `rtw89_phy_read_txpwr_byrate()`, packs four signed bytes per word, and writes via `rtw89_mac_txpwr_write32()`. Limit programming fills `struct rtw89_txpwr_limit_be` for the current channel width using center/primary channel arithmetic, including 40 MHz offset minimum fields, then writes a 76-byte page per NSS. RU limit programming similarly fills 16 RU subchannel slots and writes an 80-byte page per NSS.

## Dependencies and integration points
The file includes `chan.h`, `debug.h`, `mac.h`, `phy.h`, and `reg.h`. It depends on register constants from `reg.h`, channel helpers such as `rtw89_mgnt_chan_get()`, MAC-index helpers such as `rtw89_mac_reg_by_idx()` and `rtw89_mac_check_mac_en()`, MMIO helpers, EFUSE RFE data, chip ID/CID fields, DBCC state, and generic TX power readers. The exported generation definitions are consumed by BE chip descriptions. The exported RFSI helpers integrate with chip-specific channel and RF code that needs to refresh bandedge controls after channel changes.

## Risks and edge cases
- Register maps differ sharply between BE and BE v1; assigning the wrong `phy_def` will write plausible but incorrect addresses.
- Channel arithmetic for 40/80/160/320 MHz assumes valid center channels. Invalid channel descriptors can underflow unsigned channel calculations.
- TX power layouts depend on `struct rtw89_txpwr_limit_be` and `struct rtw89_txpwr_limit_ru_be` byte ordering matching hardware pages.
- `rtw89_phy_bb_wrap_flush_addr()` contains a special RTL8922D CID7025 workaround that only runs when the device is marked running; missed flushes could leave stale MACID power tables.
- BB gain config type 4 is warned for non-eFEM RFE types after falling through to the default case, so table authors need to keep RFE-conditional data aligned.
- RFSI compensation setup is heavily chip-ID gated. New BE chips may need additional handling rather than inheriting RTL8922A/RTL8922D assumptions.

## Test signals
Useful signals include successful probe with `rtw89_phy_gen_be` or `_be_v1`, BB gain table loading without unknown-type warnings, no register access faults during RF NCTL preinit, correct DBCC MAC1 BB-wrapper initialization, channel-info reports after `ch_info_init`, TX power debug logs for by-rate/limit/RU programming on 20/40/80/160/320 MHz channels, regulatory power values matching table data, and stable RTL8922D bandedge/RFSI behavior at 2 GHz, 5 GHz, and 6 GHz edge channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy_be.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.c

## Purpose
`ps.c` implements rtw89 runtime power-save behavior. It coordinates leisure power save (LPS), low-power MAC/HCI modes, idle power save (IPS), Bluetooth coexistence notifications, firmware H2C/C2H acknowledgement checks, P2P Notice of Absence programming, and one-shot NoA duration tracking. The file bridges mac80211 power-save policy and VIF state with Realtek firmware commands and hardware power-mode transitions.

## Important APIs and functions
- `__rtw89_enter_ps_mode()` and `__rtw89_leave_ps_mode()` set or clear `RTW89_FLAG_LOW_POWER_MODE` and call the chip/MAC/HCI power-mode transition path when `rtwdev->ps_mode` is enabled.
- `rtw89_enter_lps()` enters firmware LPS for each link of a VIF, sends RF PS and multi-link/channel information, notifies BTC that radio control is firmware-owned, and optionally enters low-power mode.
- `rtw89_leave_lps()` exits LPS globally, leaves low-power mode first, reinitializes PHY dynamic mechanisms, sends active LPS parameters to station/P2P-client links, restores BTC radio state, applies digital power compensation, and reinitializes TRX protection.
- `rtw89_enter_ips()` and `rtw89_leave_ips()` implement idle power save by deinitializing/reinitializing VIF MAC state around `rtw89_core_stop()` and `rtw89_core_start()`.
- `rtw89_recalc_lps()` enables LPS only for a single station VIF with mac80211 PS enabled and disables it for MCC or non-station/multiple-VIF combinations.
- Firmware check helpers `rtw89_fw_receive_lps_h2c_check()` and `rtw89_fw_leave_lps_check()` validate LPS leave acknowledgement through C2H register features and MAC PS status polling, incrementing `ps_hang_cnt` and notifying SER after repeated hangs.
- P2P functions `rtw89_process_p2p_ps()`, `rtw89_p2p_disable_all_noa()`, `rtw89_p2p_noa_renew()`, `rtw89_p2p_noa_append()`, and `rtw89_p2p_noa_fetch()` maintain firmware NoA state and construct P2P NoA IEs.
- `rtw89_p2p_noa_once_init()`, `_deinit()`, and `_recalc()` manage delayed work that tracks finite NoA windows and restores beacon-filter configuration when the duration ends.

## Control flow and state behavior
LPS entry starts by atomically setting `RTW89_FLAG_LEISURE_PS`; a second entry attempt returns immediately. Each VIF link receives a legacy PS H2C parameter with its MAC ID and `RTW89_LAST_RPWM_PS`. P2P client links suppress the additional low-power MAC/HCI mode because the code keeps `can_ps_mode` false for that role. After link-level commands, the driver sends RF PS info plus one of the firmware-supported LPS channel or multi-link info formats. If requested and allowed, the driver enters low-power mode, which may switch HCI mode on chips whose `low_power_hci_modes` include the current `ps_mode` and when WoWLAN is not active.

LPS leave clears `RTW89_FLAG_LEISURE_PS`; if it was not set, leave is a no-op. The function exits low-power mode first, then calls `rtw89_phy_dm_reinit()` before sending active LPS parameters per station or P2P-client link. The firmware checks persist hang state in `rtwdev->ps_hang_cnt`; successful leave resets it to zero, while repeated timeout or bad-ack paths can trigger SER assertion recovery. Runtime state is kept in device flags, `ps_mode`, `lps_enabled`, per-link MAC IDs, per-link NoA state, and firmware feature flags.

IPS is deeper than LPS. Entry sets `RTW89_FLAG_INACTIVE_PS`, skips shutdown if already powered off, deinitializes all VIF links at the MAC layer, then stops the core. Leave refuses to run if already powered on, starts the core, sets the channel, initializes VIF links again, and clears inactive PS. P2P NoA state is separate: recurring NoA descriptors are pushed to firmware, while finite one-shot windows are calculated against hardware TSF, merged with any still-active previous window, and scheduled as wiphy delayed work to toggle `noa_once->in_duration` and beacon filtering.

## Dependencies and integration points
`ps.c` includes `chan.h`, `coex.h`, `core.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `ps.h`, `reg.h`, `ser.h`, and `util.h`. It integrates with mac80211 queues and NAPI during HCI mode switches, firmware H2C commands for LPS/P2P/beacon filters, MAC power and VIF lifecycle functions, PHY dynamic-mechanism reinitialization, Bluetooth coexistence radio-state notifications, SER recovery, RCU-protected BSS configuration access, TSF reads, and wiphy delayed work. Locking expectations are explicit on public paths that require the wiphy lock.

## Risks and edge cases
- Firmware feature negotiation controls acknowledgement and LPS-info formats. A mismatch can skip necessary checks or send an unsupported command format.
- Leave-LPS polling uses per-MACID bit slicing of `mac->ps_status`; incorrect MAC ID or register definitions can produce false hangs.
- `rtw89_ps_power_mode_change_with_hci()` briefly stops queues, flushes TX work, pauses HCI, switches MAC/HCI mode, and schedules NAPI on leave; ordering regressions can lose or stall packets.
- `rtw89_recalc_lps()` deliberately disables LPS for MCC, multiple VIFs, or non-station roles. New interface combinations need careful policy review.
- IPS leave logs `rtw89_core_start()` failure but still proceeds to channel and VIF initialization, which may rely on lower layers tolerating a failed start.
- One-shot NoA timing truncates delays to `UINT_MAX` microseconds and warns on unhandled far-future begin times; long or wrapped schedules may be approximated.

## Test signals
Signals include successful association with mac80211 PS causing `lps_enabled`, clean LPS enter/leave H2C traces, `ps_hang_cnt` staying at zero, no SER assertion during repeated suspend/resume or PS toggles, queues resuming after HCI low-power mode leave, IPS entry powering down the core only while idle, IPS leave restoring channel and VIF MAC state, BTC radio-state notifications matching LPS transitions, P2P NoA firmware commands matching BSS config, and beacon filtering restored after finite NoA windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.h

## Purpose
`ps.h` declares the rtw89 power-save API implemented by `ps.c`. It exposes LPS, IPS, P2P power-save, NoA IE construction, one-shot NoA tracking, and small hwflags-based IPS helpers to the rest of the driver. The header owns no persistent state; it defines the callable boundary for modules that react to mac80211 configuration changes, VIF lifecycle events, coexistence control, and idle transitions.

## Important APIs and definitions
- `rtw89_enter_lps()` and `rtw89_leave_lps()` are the main leisure power-save entry/exit functions.
- `__rtw89_enter_ps_mode()` and `__rtw89_leave_ps_mode()` are lower-level low-power-mode helpers used by LPS and internal flows.
- `rtw89_leave_ps_mode()` is the public wiphy-lock-asserting leave helper.
- `rtw89_enter_ips()` and `rtw89_leave_ips()` control idle power save around core stop/start.
- `rtw89_set_coex_ctrl_lps()` lets coexistence policy force LPS exit when BTC takes control.
- `rtw89_process_p2p_ps()` and `rtw89_p2p_disable_all_noa()` synchronize P2P NoA firmware state with link BSS configuration.
- `rtw89_p2p_noa_renew()`, `rtw89_p2p_noa_append()`, and `rtw89_p2p_noa_fetch()` manage the local P2P NoA IE buffer attached to a VIF link.
- `rtw89_p2p_noa_once_init()`, `_deinit()`, and `_recalc()` manage delayed-work tracking for finite NoA intervals.
- Inline `rtw89_leave_ips_by_hwflags()` and `rtw89_enter_ips_by_hwflags()` gate IPS transitions on `IEEE80211_CONF_IDLE`; enter additionally refuses to power down while `rtwdev->scanning` is true.

## Control flow and state behavior
The header presents two power-save levels. LPS functions operate while the device is associated and firmware can manage station sleep behavior. IPS functions operate when mac80211 marks the hardware idle and the core can be stopped. The hwflags helpers are convenience wrappers for configuration-change code: leave IPS if the idle flag is set and work needs the device awake; enter IPS when the idle flag remains set, except during scans after remain-on-channel handling.

P2P declarations split recurring NoA firmware programming from local IE construction and one-shot duration tracking. Callers are expected to pass `struct rtw89_vif_link` objects that own the NoA buffers and delayed-work handlers initialized by the implementation.

## Dependencies and integration points
The prototypes depend on rtw89 core forward declarations supplied by including translation units, plus mac80211 types such as `struct ieee80211_bss_conf`, `struct ieee80211_p2p_noa_desc`, and `struct ieee80211_hw`. `ps.h` is included by rtw89 modules that need to enter or leave LPS/IPS in response to mac80211 PS, idle flags, scan state, coexistence control, P2P NoA updates, or device lifecycle events.

## Risks and edge cases
- The double-underscore helpers bypass the public lock assertions; callers must already be in the correct serialized context.
- The inline IPS helpers key entirely on `IEEE80211_CONF_IDLE` plus `rtwdev->scanning`, so callers must update those states before invoking them.
- Since this header does not include the full type definitions itself, include order must provide required struct visibility in C files that dereference fields in the inline helpers.
- P2P NoA callers must pair init/deinit with VIF-link lifetime to avoid delayed work running against stale link state.

## Test signals
Build coverage should catch missing type visibility and prototype drift with `ps.c`. Runtime signals include configuration-change paths entering/leaving IPS from hwflags, scans not entering IPS mid-scan, LPS APIs callable from station PS policy changes, coexistence-triggered LPS exit, and P2P NoA init/deinit running cleanly across VIF link creation and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.h -->
