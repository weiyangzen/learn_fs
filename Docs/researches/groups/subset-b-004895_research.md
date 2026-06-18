# Research: subset-b-004895

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.c

## Purpose
This file implements dynamic management for the Realtek RTL8821AE/RTL8812AE PCI wireless driver. It is the runtime feedback loop that adjusts receiver initial gain, CCK packet detection, rate-adaptive masks, EDCA turbo parameters, CFO/crystal-cap tracking, thermal transmit-power tracking, and IQ/LCK calibration. It sits between mac80211 link state/statistics, rtlwifi shared state, chip-specific PHY helpers, firmware H2C commands, and direct MAC/BB/RF register programming.

The file also carries the swing and delta-swing lookup tables used to translate temperature/channel/rate conditions into BB swing or TxAGC compensation. It handles both the single-stream RTL8821AE path and the two-path RTL8812AE path, selecting behavior through `rtlhal->hw_type`, `rtlpriv->phy.rf_type`, and channel/rate state.

## Important APIs, Types, And Functions
Primary public entry points are `rtl8821ae_dm_init()`, `rtl8821ae_dm_watchdog()`, `rtl8821ae_dm_init_edca_turbo()`, `rtl8821ae_dm_init_rate_adaptive_mask()`, `rtl8821ae_dm_check_txpower_tracking_thermalmeter()`, `rtl8821ae_dm_initialize_txpower_tracking_thermalmeter()`, `rtl8821ae_dm_clear_txpower_tracking_state()`, `rtl8821ae_dm_txpower_track_adjust()`, `rtl8821ae_dm_update_init_rate()`, `rtl8821ae_hw_rate_to_mrate()`, `rtl8812ae_dm_txpower_tracking_callback_thermalmeter()`, `rtl8821ae_dm_txpower_tracking_callback_thermalmeter()`, and per-chip `*_dm_txpwr_track_set_pwr()` functions.

The central state is spread across `struct rtl_dm`, `struct dig_t`, `struct rate_adaptive`, `struct rtl_phy`, `struct rtl_hal`, `struct rtl_mac`, `struct rtl_efuse`, `struct false_alarm_statistics`, and `struct rtl_stats`. Important tables include `txscaling_tbl`, `rtl8821ae_txscaling_table`, EDCA per-peer tables, and per-band/per-path delta-swing tables for RTL8812AE and RTL8821AE.

Private control helpers include RSSI aggregation (`rtl8821ae_dm_find_minimum_rssi()`, `rtl8821ae_dm_check_rssi_monitor()`), false alarm sampling/reset (`rtl8821ae_dm_false_alarm_counter_statistics()`), DIG (`rtl8821ae_dm_dig()`), CCK threshold selection (`rtl8821ae_dm_cck_packet_detection_thresh()`), EDCA traffic selection (`rtl8821ae_dm_check_edca_turbo()`), CFO/ATC tracking (`rtl8821ae_dm_dynamic_atc_switch()`), and delta-swing table selection (`rtl8812ae_get_delta_swing_table()`, `rtl8821ae_get_delta_swing_table()`).

## Control Flow
Initialization runs through `rtl8821ae_dm_init()`: it clears LCK-in-progress under `iqk_lock`, initializes common RF-path information, initializes DIG from the current BB IGI register, enables driver-side RA mask control, clears EDCA turbo state, initializes thermal power tracking from efuse thermal meter values, and records the initial ATC/crystal-cap state.

The steady-state loop is `rtl8821ae_dm_watchdog()`. It first asks the hardware ops whether firmware power-save mode is active and whether firmware LPS RF is awake, suppressing dynamic work during P2P power save or RF transitions. Under `rf_ps_lock`, and only when RF is on and firmware is awake, it updates common info, samples false alarms, updates RSSI/FW RSSI reports, runs DIG, adjusts CCK detection thresholds, refreshes RA and basic rate masks, applies EDCA turbo, tracks CFO/ATC, triggers or completes thermal power tracking, and runs delayed IQ calibration after link establishment.

Transmit-power tracking is a two-stage loop. The check function alternates between triggering the RF thermal meter and calling the thermal callback. The callback averages recent thermal samples, computes deltas against previous, LCK, IQK, and efuse baseline values, may run LC/IQ calibration when thresholds are crossed, maps the thermal delta through per-band/per-rate swing tables, updates OFDM/CCK indices, then calls the per-chip set-power function in `MIX_MODE`. `MIX_MODE` clamps BB swing to rate-specific limits and pushes any excess or deficit into TxAGC by calling `rtl8821ae_phy_set_txpower_level_by_path()`.

DIG control samples OFDM/CCK false alarm counters, derives gain bounds from link state, RSSI, number of associated entries, and large-false-alarm recovery state, then writes IGI to path A and optionally path B. EDCA turbo compares interval TX/RX byte deltas and peer vendor to choose uplink or downlink BE parameters. CFO tracking uses `rtldm->cfo_tail[]` and `packet_count` to avoid stale samples, filters one large jump, updates crystal-cap registers when average CFO crosses dynamic thresholds, and restores efuse crystal cap when disconnected.

## State And Persistence
Persistent runtime state lives in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, `rtlpriv->falsealm_cnt`, `rtlpriv->stats`, `rtlpriv->phy`, and efuse-backed defaults. Notable fields include `txpower_track_control`, thermal history and indices, OFDM/CCK swing bases/current indices, remnant TxAGC offsets, `modify_txagc_flag_path_*`, `tm_trigger`, `tx_rate`, RSSI minima/maxima, `one_entry_only`, EDCA byte counters and turbo flags, CFO/crystal-cap history, and `linked_interval`.

State is not persistent across device reset except what is reloaded from efuse and driver structures during init. Hardware effects are direct register writes to BB/RF/MAC registers such as IGI, CCK CCA, EDCA BE, TXSCALE, RF thermal meter, crystal-cap fields, and rate/basic-rate controls through `cfg->ops`. The watchdog clears `num_qry_beacon_pkt` each tick after using it as a signal for weak beacon reception.

## Dependencies And Integration Points
The file depends on rtlwifi core headers (`wifi.h`, `base.h`, `pci.h`, `core.h`), chip headers (`reg.h`, `def.h`, `phy.h`, `dm.h`, `fw.h`, `trx.h`), and Bluetooth coexistence callbacks from `rtl_btc.h`. It calls firmware H2C reporting through `rtl8821ae_fill_h2c_cmd()` for RSSI, rate adaptation through `cfg->ops->update_rate_tbl()`, power/basic-rate hardware ops, PHY calibration and Tx-power helpers in `phy.c`, descriptor helpers for antenna selection, and mac80211 station lookup under RCU.

The watchdog is normally driven by rtlwifi periodic work. RX/TX paths feed it through `rtlpriv->stats`, `rtlpriv->dm.undec_sm_pwdb`, `rtldm->cfo_tail`, `rtldm->packet_count`, and beacon/non-BE debug counters. Firmware C2H rate reports call `rtl8821ae_dm_update_init_rate()`, which updates `rtldm->tx_rate` and immediately reapplies power tracking.

## Risks
Most risk is hardware-state drift: the code directly writes many chip registers and has separate one-path/two-path branches that can silently diverge. Thermal tracking has complex signed/unsigned index arithmetic and uses table sizes as bounds; wrong rate/channel classification can over- or under-compensate power. The RTL8821AE low-temperature branch calls the RTL8812AE set-power helper for one case, which is suspicious even if path A behavior overlaps.

DIG and CCK threshold tuning are sensitive to stale or noisy counters. RSSI monitoring uses static TX/RX byte baselines inside the function, so multiple devices would share those statics if the driver supports more than one instance. EDCA turbo relies on `is_any_nonbepkts` and interval byte deltas, so counter resets or missed watchdog ticks can temporarily program aggressive BE parameters. CFO/crystal-cap adjustment uses sampled packet counters and jump suppression; incorrect bounds or stale CFO tails can move oscillator compensation in the wrong direction.

Concurrency risk centers on `rf_ps_lock`, `iqk_lock`, RCU station lookup, and entry-list locking. Several helpers write hardware outside the narrower locks, so sequencing with power transitions and firmware LPS state is important. Test failures may manifest as reduced throughput, excessive false alarms, association instability, thermal drift, or poor coexistence rather than clean crashes.

## Test Signals
Useful signals include successful association/disassociation in station, AP, adhoc, and mesh modes; stable RSSI reports to firmware; RA mask transitions at high/mid/low RSSI; low and high false-alarm scenarios changing IGI as expected; CCK threshold transitions around 10/25 RSSI and high CCK false alarms; EDCA register changes only under BE-only traffic; thermal meter trigger/callback alternation; Tx power tracking under rising/falling temperature; LCK/IQK threshold behavior; CFO tracking with crystal-cap convergence; and no dynamic work while firmware LPS/RF-off/P2P PS is active.

Hardware-oriented regression tests should monitor BB/RF register traces, firmware H2C logs, throughput and PER, thermal-compensated EVM/power measurements, lockdep, KASAN, and multi-adapter behavior for the static counters in RSSI monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.h

## Purpose
This header defines the dynamic-management contract for the RTL8821AE/RTL8812AE driver. It provides register aliases, threshold constants, table sizes, mode enums, bit masks, and function prototypes used by `dm.c` and by neighboring PHY/FW/TX code that needs dynamic management services.

The header is mostly declarative, but it encodes important hardware policy: which RF/BB/MAC registers dynamic management may touch, what RSSI/false-alarm/thermal thresholds shape control loops, what power-tracking methods exist, and which exported functions other driver units may call.

## Important APIs, Types, And Functions
Register macros are grouped by RF, BB, and MAC pages. Examples include RF thermal/channel registers (`DM_REG_T_METER_11N`, `DM_REG_CHNBW_11N`), DIG/CCA registers (`DM_REG_IGI_A_11AC`, `DM_REG_IGI_B_11AC`, `DM_REG_CCK_CCA_11AC`), false-alarm counters and reset registers, TXAGC/TXIQK/RXIQK registers, EDCA registers, antenna selection registers, and RSSI monitor registers.

Control constants include table lengths (`TXSCALE_TABLE_SIZE`, `OFDM_TABLE_SIZE`, `CCK_TABLE_SIZE`), DIG false-alarm thresholds (`DM_DIG_FA_TH0/1/2`), rate-adaptation states (`DM_RATR_STA_*`), high-power and near-field thresholds, TX power tracking limits, dynamic ATC/CFO thresholds, thermal averaging sizes, and per-chip RF path counts (`MAX_PATH_NUM_8812A`, `MAX_PATH_NUM_8821A`).

Enums include dynamic initial gain operation types, CCA/RF save states, software antenna switch values, and `enum pwr_track_control_method` with `BBSWING`, `TXAGC`, and `MIX_MODE`. The public function prototypes expose DM init/watchdog, DIG/CCA writes, EDCA and RA init, thermal tracking, TX-power set/adjust helpers, rate conversion, C2H rate update support, and descriptor antenna selection.

## Control Flow
This file has no executable flow, but it defines the legal calls used by the runtime flow. Driver initialization can call `rtl8821ae_dm_init()`, EDCA/RA init helpers, and thermal-tracking initialization. Periodic work calls `rtl8821ae_dm_watchdog()` and thermal-meter checks. Firmware C2H rate reports can call `rtl8821ae_dm_update_init_rate()`. PHY or calibration code can call the chip-specific TX-power tracking callbacks and power-set helpers.

The register constants in this header let `dm.c` isolate chip-control logic from raw numeric addresses. They also preserve Realtek naming from older 11n/11ac code paths, which explains the mixed `11N` and `11AC` suffixes even in RTL8821AE code.

## State And Persistence
The header does not allocate state. It defines bit positions and constants that shape state stored elsewhere: `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, efuse fields, and hardware registers. Macros such as `GET_UNDECORATED_AVERAGE_RSSI()` select which RSSI state is authoritative depending on opmode.

Because the constants are compiled into the driver, changes here persist as driver behavior changes across all callers. Incorrect register aliases or threshold values would directly alter hardware programming at runtime.

## Dependencies And Integration Points
`dm.h` is included by `dm.c`, `fw.c`, and other RTL8821AE source files that need DM function prototypes or shared constants. It assumes kernel bit macros such as `BIT`, `GENMASK`, and `BIT_OFFSET_LEN_MASK_32`, mac80211 opmode definitions, and Realtek shared structures from included rtlwifi headers. The function declarations bind this header to `phy.c` calibration APIs, `fw.c` H2C/C2H interactions, and descriptor code in `trx.h`.

The constants also mirror hardware documentation and shared Realtek ODM code conventions. A maintenance change must consider both RTL8821AE one-path and RTL8812AE two-path behavior because one header serves both branches.

## Risks
Header risk is primarily semantic drift. Many register names carry `11N` suffixes while the code programs 11ac hardware paths; changing aliases without verifying call sites can misprogram BB/RF state. Threshold constants are magic hardware-policy values, so apparent cleanups can shift control-loop stability. `MAX_PATH_NUM_8821A` and `MAX_PATH_NUM_8812A` guard loops in `dm.c`; wrong values can cause missed path updates or out-of-bounds state access.

Macro APIs write through raw pointers and assume byte-array command buffers or valid `struct rtl_priv` pointers. `GET_UNDECORATED_AVERAGE_RSSI()` casts its argument and dereferences nested fields, so it is not type-safe. Duplicated constants and old naming also increase the chance that future chip support reuses an incompatible address or threshold.

## Test Signals
Compile coverage is the first signal because this header defines exported prototypes and macro dependencies. Runtime signals should focus on every feature using these constants: DIG register writes, false-alarm counter reads/resets, CCK CCA thresholds, EDCA BE programming, TX power tracking table bounds, thermal meter access, CFO crystal-cap adjustment, and antenna selection. Static analysis should flag unsafe macro use, path-count loops, and any mismatch between declared prototypes and `dm.c` implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.c

## Purpose
This file implements firmware download, firmware mailbox command delivery, power-save/WoWLAN/P2P firmware commands, reserved-page packet download, and C2H rate-report handling for RTL8821AE/RTL8812AE. It bridges rtlwifi/mac80211 state to the chip firmware by writing firmware images into MCU memory, polling firmware readiness bits, serializing H2C commands through HME boxes, and constructing special packets that firmware later transmits for power-save and wake-on-wireless flows.

It supports both normal firmware and WoWLAN firmware, plus two reserved-page layouts: 256-byte pages for RTL8821AE and 512-byte pages for RTL8812AE. Large static byte arrays serve as packet templates for beacon, PS-Poll, null data, QoS null, BT QoS null, ARP response, remote wake control, and GTK extension memory pages.

## Important APIs, Types, And Functions
Firmware lifecycle helpers include `_rtl8821ae_enable_fw_download()`, `_rtl8821ae_write_fw()`, `_rtl8821ae_fw_free_to_go()`, `rtl8821ae_download_fw()`, optional `rtl8821ae_set_fw_related_for_wowlan()`, and `rtl8821ae_firmware_selfreset()`. H2C transport is handled by `_rtl8821ae_check_fw_read_last_h2c()`, `_rtl8821ae_fill_h2c_command()`, and exported `rtl8821ae_fill_h2c_cmd()`.

Command builders include `rtl8821ae_set_fw_pwrmode_cmd()`, `rtl8821ae_set_fw_media_status_rpt_cmd()`, `rtl8821ae_set_fw_ap_off_load_cmd()`, `rtl8821ae_set_fw_wowlan_mode()`, `rtl8821ae_set_fw_remote_wake_ctrl_cmd()`, `rtl8821ae_set_fw_keep_alive_cmd()`, `rtl8821ae_set_fw_disconnect_decision_ctrl_cmd()`, `rtl8821ae_set_fw_global_info_cmd()`, `rtl8812ae_set_fw_rsvdpagepkt()`, `rtl8821ae_set_fw_rsvdpagepkt()`, `rtl8821ae_set_p2p_ps_offload_cmd()`, and `rtl8821ae_c2h_ra_report_handler()`.

Important state comes from `struct rtl_hal` (`pfirmware`, `wowlan_firmware`, sizes, `fw_version`, `fw_ready`, `last_hmeboxnum`, `h2c_setinprogress`, `p2p_ps_offload`, `current_ra_rate`), `struct rtl_ps_ctl` (LPS, WoWLAN, ARP/GTK offload, P2P PS), `struct rtl_mac` (MAC address, BSSID, AID, hidden SSID, P2P role), `struct rtl_security`, and Bluetooth coexistence callbacks.

## Control Flow
`rtl8821ae_download_fw()` chooses normal or WoWLAN firmware from `rtlhal`, reads and skips a Realtek firmware header when the signature matches, clears an old downloaded state if MAC function is enabled, enables firmware download mode, writes the image in 4 KiB pages through `rtl_fw_page_write()`, disables download mode, then polls checksum and firmware-init-ready bits in `_rtl8821ae_fw_free_to_go()`. That helper also sets `MCUFWDL_RDY`, clears `WINTINI_RDY`, self-resets firmware, and waits until firmware reports initialization complete.

H2C command flow starts at `rtl8821ae_fill_h2c_cmd()`, which refuses to send if `fw_ready` is false, copies the command into an 8-byte local buffer, and calls `_rtl8821ae_fill_h2c_command()`. The lower helper serializes against `rtlhal->h2c_setinprogress` under `h2c_lock`, chooses one of four HME boxes using `last_hmeboxnum`, waits until firmware has read the box, writes the base and extension registers depending on command length, advances the box number, and clears the in-progress flag.

Power-save command builders pack small H2C byte arrays through macros from `fw.h`. LPS mode selection accounts for Bluetooth coexistence override, P2P awake intervals, smart PS, RPWM/power state, and records BT-selected power mode. WoWLAN builders configure pattern/magic/disconnect wake, remote wake ARP/GTK/RealWoW flags, keep-alive period, disconnect decision timeout, and AOAC security algorithms.

Reserved-page functions mutate static packet templates with current MAC/BSSID/AID, choose partial or whole reserved-page lengths, allocate an SKB, copy the reserved-page bytes, send them through `rtl_cmd_send_packet()`, then notify firmware of page locations via `H2C_8821AE_RSVDPAGE` and optionally `H2C_8821AE_AOAC_RSVDPAGE`. P2P PS offload updates CTWindow and NoA hardware registers, adjusts start times relative to TSF, updates `rtlhal->p2p_ps_offload`, and sends it as an H2C command. C2H RA reports translate firmware rates with `rtl8821ae_hw_rate_to_mrate()` and feed DM power tracking through `rtl8821ae_dm_update_init_rate()`.

## State And Persistence
Firmware image data is owned by `rtlhal` and not allocated here. This file persists firmware metadata (`fw_version`, `fw_subversion`), H2C mailbox position, H2C in-progress state, firmware readiness and PS state, P2P offload state, and current RA rate. Reserved-page packet templates are static mutable arrays; each call patches addresses/AID into shared template storage before copying to an SKB.

Hardware/firmware persistent effects include MCU download registers, HMEBOX/HMEBOX_EXT mailbox registers, firmware PS mode, WoWLAN/AOAC state, keep-alive/disconnect policy, reserved-page contents in firmware packet memory, NoA registers, and firmware station/rate state affected indirectly by H2C commands. Most of this state is lost on firmware reset and must be replayed by init, WoWLAN, or mac80211 power-save flows.

## Dependencies And Integration Points
The file depends on rtlwifi core register accessors, firmware utilities (`rtl_fill_dummy()`, `rtl_fw_page_write()`), command packet submission (`rtl_cmd_send_packet()`), SKB allocation APIs, endian helpers, mac80211 `ieee80211_hw`, Bluetooth coexistence ops, efuse/security state, and dynamic-management functions from `dm.c`. Command layout and IDs are defined in `fw.h`; register constants come from `reg.h` and `def.h`.

External callers include hardware init and resume paths for firmware download, power management code for LPS/WoWLAN/remote wake/keep-alive commands, AP/P2P flows for offload commands, reserved-page setup during power-save preparation, and firmware C2H dispatch for RA reports.

## Risks
`rtl8821ae_download_fw()` logs firmware readiness failure but returns `0` after `_rtl8821ae_fw_free_to_go()` regardless of `err`; callers that depend on the return value may mark firmware usable even after readiness polling failed. H2C serialization has long busy waits and can return early from timeout paths while relying on later cleanup of `h2c_setinprogress`; mailbox bugs can stall all firmware commands. Command length handling only covers one to seven bytes, so future longer commands need a new transport path.

The reserved-page templates are static mutable buffers, so concurrent calls could race and cross-contaminate MAC/BSSID/AID fields. SKB allocation failure silently returns without H2C location updates. Packet lengths subtract 40 bytes from fixed page totals, so descriptor/header assumptions must match `rtl_cmd_send_packet()` behavior. P2P NoA start-time adjustment mutates `noa_count_type[]` while iterating, which can affect later state. WoWLAN command composition is spread across several commands, so partial failure can leave firmware with inconsistent wake policy.

Hardware compatibility risk is high because RTL8812AE and RTL8821AE share much code but differ in page size, reset bits, RF path count, and firmware behavior. The file also uses hard-coded registers such as `0x5cf`, `0x5E0`-`0x5EC`, and `0x130`, which need hardware documentation when changed.

## Test Signals
Firmware tests should validate normal and WoWLAN image download, header stripping, page writes, checksum report, firmware init ready, self-reset behavior, and failure propagation. H2C tests should cover all four mailbox boxes, extension bytes for four-to-seven byte commands, timeout behavior when firmware does not clear a box, and concurrent command senders under lockdep.

Power-save and WoWLAN signals include correct LPS mode with and without BT control, firmware keep-alive intervals, wake on pattern/magic/disconnect, ARP/GTK offload, AOAC global security algorithms, and reserved-page location commands. Reserved-page validation should inspect transmitted template contents for correct MAC/BSSID/AID and page offsets on both RTL8821AE and RTL8812AE. P2P tests should cover CTWindow, two NoA descriptors, scan/scan-done transitions, GO/client role bits, and TSF-relative start adjustment. C2H tests should confirm RA report rates update `current_ra_rate` and trigger DM power tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.h

## Purpose
This header defines the firmware-facing ABI used by the RTL8821AE/RTL8812AE driver. It contains firmware image limits, download polling constants, firmware-header signature tests, H2C command IDs and payload lengths, firmware power-save bit definitions, command-packing macros, reserved-page location macros, and exported firmware helper prototypes.

The header is the compact contract between C driver code and the closed firmware running on the device MCU. Small layout mistakes here change the bytes written into firmware mailboxes.

## Important APIs, Types, And Functions
Firmware download constants include `FW_8821AE_SIZE`, start/end addresses, 4 KiB page size, polling delay, and polling timeout count. Header-detection macros `IS_FW_HEADER_EXIST_8812()` and `IS_FW_HEADER_EXIST_8821()` identify Realtek firmware signatures after endian conversion.

`enum rtl8821a_h2c_cmd` defines firmware command IDs for reserved pages, media status report, keep-alive, disconnect decision, AP offload, reserved beacon/probe response, power-save mode, P2P PS, WoWLAN, remote wake, AOAC global info, AOAC reserved page, RSSI report, RA mask, and related commands. Payload-length macros define the expected byte counts for each command family.

Power-save macros define RPWM/CPWM state bits, low-power checks, active/RF-off states, and helpers to inspect ACK/clock/RF/interrupt bits. Command-packing macros write individual fields into byte arrays using `u8p_replace_bits()` or direct byte stores. Public prototypes export firmware download, H2C send, self-reset, LPS/media/AP/WoWLAN/remote wake/keep-alive/disconnect/global-info commands, reserved-page download for both 8821 and 8812, P2P PS offload, and C2H RA report handling.

## Control Flow
The header has no runtime flow, but its definitions drive `fw.c`. Firmware download uses size/page/poll constants and signature macros. H2C command builders allocate fixed-size byte arrays using the length macros, fill them with `SET_*` macros, and send them with IDs from `enum rtl8821a_h2c_cmd`. Power-save flows use `FW_PS_*` macros to encode driver and firmware state. Reserved-page flows use `SET_H2CCMD_RSVDPAGE_LOC_*` and AOAC location macros to tell firmware where packet templates were placed.

The conditional `USE_SPECIFIC_FW_TO_SUPPORT_WOWLAN` and `USE_OLD_WOWLAN_DEBUG_FW` definitions affect whether a WoWLAN firmware-redownload helper is declared and how long remote wake control payloads are.

## State And Persistence
No state is allocated in the header. It defines constants and byte layouts for state stored in firmware, hardware registers, `rtlhal`, `rtlps`, and command buffers on the stack. The macros mutate caller-provided arrays in place; their effects persist only after `rtl8821ae_fill_h2c_cmd()` writes them to firmware mailboxes.

Because this is an ABI header, its values are effectively persistent across all compiled driver instances. Any change must match the firmware version loaded by `fw.c`.

## Dependencies And Integration Points
The header includes `def.h` and depends on kernel bit macros, endian helpers, `u8p_replace_bits()`, and Realtek firmware structures. It is included by `fw.c` and `dm.c` and referenced by power management, WoWLAN, P2P, and C2H dispatch code. The exported functions are called from chip init, suspend/resume, LPS, AP/P2P setup, reserved-page setup, and firmware event handling paths.

It also integrates with Bluetooth coexistence indirectly because `rtl8821ae_set_fw_pwrmode_cmd()` packs coexistence-selected values into fields defined here.

## Risks
The main risk is byte-layout mismatch with firmware. Many `SET_*` macros do unguarded pointer arithmetic and direct stores; they assume the caller allocated at least the matching `H2C_..._LEN` bytes. Some command comments and IDs are inherited from older chips, and `H2C_8821AE_P2P_PS_OFFLOAD = 024` is an octal literal in C, so maintainers must treat command IDs carefully. `FW_PWR_STATE_ACTIVE` and `FW_PWR_STATE_RF_OFF` are defined twice, which is harmless only while values remain identical.

Power-save bit names are easy to confuse because 8821AE RPWM values define all-on/RF-on/RF-off states differently from the older 92C macros in the same header. Future firmware command expansion beyond seven H2C bytes would require coordinated changes in both this header and `fw.c` mailbox writing.

## Test Signals
Compile tests should catch prototype drift and missing macro dependencies. Runtime validation should inspect H2C byte arrays for each command ID, especially power mode, WoWLAN, remote wake, keep-alive, AOAC global info, AOAC reserved-page locations, and disconnect decision. Firmware compatibility tests should verify command IDs and lengths against the loaded firmware, including both normal and WoWLAN firmware. Static analysis should check all macro callers allocate buffers of the declared length and do not pass overlapping or too-short arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.h -->
