# Research: subset-b-004886

Grouped research for the rtl8192d common layer and rtl8192de PCI-specific layer. Each section preserves the source path in its title and is delimited for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.c

Purpose: Implements shared RTL8192D dynamic-management routines used by the rtl8192de/rtl8192du family. The file covers thermal transmit-power tracking, RX gain tracking, false-alarm counter harvesting, DIG initial-gain tuning, CCK packet-detection thresholds, Cisco early-mode handling, EDCA turbo switching, and rate-adaptive-mask initialization.

Important APIs/functions: `rtl92d_dm_initialize_txpower_tracking()` initializes the `rtl_priv->dm` tracking flags. `rtl92d_dm_check_txpower_tracking_thermal_meter()` alternates between triggering RF thermal-meter measurement and running `rtl92d_dm_txpower_tracking_callback_thermalmeter()`. `rtl92d_dm_false_alarm_counter_statistics()` snapshots OFDM/CCK false-alarm counters and resets them. `rtl92d_dm_find_minimum_rssi()`, `rtl92d_dm_write_dig()`, and `rtl92d_dm_dig()` maintain DIG state. `rtl92d_dm_init_edca_turbo()` and `rtl92d_dm_check_edca_turbo()` manage BE EDCA tuning. `rtl92d_dm_init_rate_adaptive_mask()` chooses firmware/driver rate-mask behavior.

Control flow: Thermal tracking reads `RF_T_METER`, averages recent samples, compares against EEPROM thermal baselines and prior LCK/IQK/RX-gain values, and conditionally recalculates OFDM swing, CCK swing, RX gain, IQK, and LCK. DIG runs after false-alarm collection: it updates station connected/disconnected state, adjusts IGI by false-alarm thresholds, raises a temporary lower bound on abnormal false-alarm bursts, writes OFDM AGC cores, then updates CCK PD thresholds on 2.4 GHz. EDCA turbo compares delta RX/TX unicast byte counts and switches BE parameters between uplink/downlink settings unless non-BE traffic or frameburst disable forces restoration through `set_hw_reg(HW_VAR_AC_PARAM)`.

State and persistence: State is in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->falsealm_cnt`, `rtlpriv->stats`, `rtlpriv->ra`, `rtlpriv->phy.iqk_matrix`, and `rtlpriv->efuse` calibration fields. The file writes persistent device runtime registers, not filesystem state. Several `static` locals in EDCA tracking (`last_txok_cnt`, `last_rxok_cnt`) are process-global, so multi-device behavior depends on shared driver assumptions.

Dependencies and integration: Depends on common rtlwifi helpers, register definitions, `rtl92d_phy_*` calibration helpers, RF register access, `cfg->ops->phy_lc_calibrate`, `cfg->ops->phy_iq_calibrate`, and `cfg->ops->set_hw_reg`. It is called by rtl8192de watchdog initialization and periodic watchdog code, and exported for bus-specific modules.

Risks: Register math is tightly coupled to RTL8192D tables and cut/band/internal-PA behavior. The RX gain mapping indexes `index_mapping[idx]` from EEPROM thermal minus tracked RX gain without a local bounds check. EDCA `static` counters are not per-adapter. Several paths assume current band and RF path counts are already initialized. Thermal callback performs many BB/RF writes and must not race power-save or band-switch sequences.

Test signals: Validate with driver build, sparse/lock-context checks, firmware watchdog traces, association on 2.4/5 GHz, thermal drift tests that trigger LCK/IQK, false-alarm/DIG logs under noisy RF, throughput tests that flip EDCA turbo, and multi-interface dual-MAC operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.h

Purpose: Declares the shared RTL8192D dynamic-management constants, state enums, and exported function prototypes consumed by bus-specific drivers.

Important APIs/types: Defines DM disable bits (`HAL_DM_DIG_DISABLE`, `HAL_DM_HIPWR_DISABLE`), OFDM/CCK swing table sizes, DIG false-alarm thresholds, TX high-power levels, DM ownership modes, near-field thresholds, and enums for 1R CCA, RF save state, and software antenna switching. Exposes tx power tracking, false alarm, RSSI, DIG, EDCA turbo, and rate-adaptive-mask functions.

Control flow: The header has no runtime flow but describes the callable lifecycle: initialize DM, periodically collect false alarms and RSSI, run DIG/EDCA, and trigger thermal power tracking.

State and persistence: No storage by itself. Constants govern how `rtl_priv->dm`, `rtl_priv->dm_digtable`, and `rtl_priv->ra` are interpreted in `dm_common.c` and rtl8192de-specific DM.

Dependencies and integration: Included by rtl8192d common implementation and rtl8192de DM/hardware paths. Requires kernel bit macros and rtlwifi type declarations from prior includes.

Risks: Threshold values are hardware-tuned magic numbers. Header guard name and API naming are RTL92D-specific; changing constants affects power, sensitivity, and rate-control behavior across all users.

Test signals: Compile coverage across rtl8192d common and rtl8192de modules, plus runtime checks for DIG, EDCA, and power-tracking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.c

Purpose: Provides shared RTL8192D firmware download, firmware readiness, self-reset, and host-to-controller command mailbox helpers.

Important APIs/functions: `rtl92d_is_fw_downloaded()` checks `REG_MCUFWDL`. `rtl92d_enable_fw_download()` toggles MCU download mode. `rtl92d_write_fw()` writes firmware pages. `rtl92d_fw_free_to_go()` waits for checksum and sets `MCUFWDL_RDY`. `rtl92d_firmware_selfreset()` resets the 8051 firmware core. `rtl92d_fw_init()` waits for MAC0/MAC1 firmware ready bits. `rtl92d_fill_h2c_cmd()` serializes H2C mailbox writes. `rtl92d_set_fw_joinbss_report_cmd()` wraps the join-BSS report command.

Control flow: Firmware download enables CPU/download registers, writes up to page-sized firmware chunks, disables download mode, polls checksum report, marks firmware ready, then polls MAC-specific ready bytes. H2C command flow first refuses RF-off states, acquires `h2c_lock` to serialize `h2c_setinprogress`, waits for firmware to clear the selected HME box, writes normal or extended mailbox bytes depending on command length, advances the 4-box ring, and clears the in-progress flag.

State and persistence: Hardware state lives in `REG_MCUFWDL`, `REG_SYS_FUNC_EN`, `REG_HMETFR`, `REG_HMEBOX_*`, and ready registers. Driver state lives in `rtlhal->last_hmeboxnum` and `rtlhal->h2c_setinprogress`. No on-disk persistence.

Dependencies and integration: Uses rtlwifi register I/O, PCI/base/efuse helpers, firmware layout constants from `fw_common.h`, command IDs from RTL8192D definitions, and power state from `rtl_ps_ctl`. Called by rtl8192de firmware download, DM RSSI report, reserved-page setup, and hardware join-BSS handling.

Risks: Busy waits and polling limits can cause slow initialization or command loss when firmware is hung. `rtl92d_write_fw()` warns on more than 8 pages but continues. H2C only accepts command lengths 1-5. Incorrect RF-off gating or missing lock release would break firmware commands. USB reset has extra interrupt masking and timing, so shared changes can affect multiple buses.

Test signals: Firmware load success, checksum-ready logs, MAC0/MAC1 ready polling, H2C command traces for join, RSSI, power mode, and reserved pages, plus suspend/resume and dual-MAC firmware-sharing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.h

Purpose: Defines RTL8192D firmware layout constants, firmware-header accessors, rate-mask H2C packing, and shared firmware function prototypes.

Important APIs/types: `FW_8192D_START_ADDRESS`, page size, and polling timeout describe firmware transfer. `IS_FW_HEADER_EXIST()` recognizes supported firmware signatures. Header macros decode little-endian signature/version/subversion fields. `struct rtl92d_rate_mask_h2c` packs the 32-bit rate mask/RAID word and MACID/short-GI byte used by rate adaptation commands.

Control flow: Header macros are used by rtl8192de firmware download before stripping a 32-byte header, and by hardware rate-mask updates before calling `rtl92d_fill_h2c_cmd(H2C_RA_MASK, ...)`.

State and persistence: No storage; it defines the binary layout of firmware headers and H2C payloads. Packing and endian annotations are important because payload bytes are written directly to firmware mailboxes.

Dependencies and integration: Requires kernel bitfield helpers, `enum version_8192d`, `struct rtl_priv`, and `struct ieee80211_hw` from surrounding rtlwifi headers. Used by common firmware code, rtl8192de firmware code, and common hardware rate-control code.

Risks: Header signature checks include 8192C/8188C-compatible values as well as 8192D values; tightening this could reject accepted firmware. Any struct layout or mask change changes firmware ABI.

Test signals: Build-time type/layout checks, firmware version logging, successful `H2C_RA_MASK` commands, and association throughput across 11b/g/n rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.c

Purpose: Implements shared RTL8192D hardware management: generic HW variable get/set, LLT writes, hardware security, EEPROM/efuse parsing, rate-table/rate-mask updates, channel access settings, GPIO radio switch checks, and CAM key programming.

Important APIs/functions: `rtl92d_get_hw_reg()`/`rtl92d_set_hw_reg()` handle common `HW_VAR_*` requests. `rtl92d_llt_write()` writes linked-list table entries. `rtl92d_enable_hw_security_config()` enables hardware crypto. `rtl92d_read_eeprom_info()` reads chip version, autoload state, MAC/PHY mode, MAC addresses, channel plan, and TX power data. `rtl92d_update_hal_rate_tbl()` selects firmware RA mask or hardware ARFR table. `rtl92d_gpio_radio_on_off_checking()` tracks hardware radio switch state. `rtl92d_set_key()` maps mac80211 keys to CAM entries.

Control flow: EEPROM flow reads chip version from `REG_SYS_CFG`, determines EEPROM/efuse boot from `REG_9346CR`, fetches hwinfo, updates cut version from efuse, configures MAC/PHY mode, programs MAC address, parses TX power/thermal/regulatory data, and chooses a channel plan. Rate control computes supported rate bitmaps from mac80211 station capabilities, current band, wireless mode, RF type, MIMO power-save, RSSI level, and bandwidth; with `useramask` it sends `H2C_RA_MASK`, otherwise it writes `REG_ARFR0`. Key programming clears all CAM entries, deletes empty keys, or adds WEP/group/pairwise keys at default, broadcast, AP-free, or fixed pairwise positions.

State and persistence: Fills `rtl_efuse` power tables, thermal and regulatory values, `rtl_hal` version/macphymode/band fields, `rtl_phy` TX-power dependencies, `rtl_pci` RCR through bus-specific wrappers, `rtl_ps_ctl` RF switch state, and `rtlpriv->sec` key buffers. Device state persists only until reset/poweroff.

Dependencies and integration: Depends on rtlwifi CAM, efuse, regulatory, PCI, firmware H2C, DM, and PHY common helpers. Bus-specific rtl8192de code wraps common get/set for PCI-only variables. mac80211 station capabilities and nl80211 interface modes drive rate and key behavior.

Risks: Autoload failure path only logs in `rtl92d_read_eeprom_info()` and does not call adapter-info parsing, so callers must tolerate default/uninitialized values. TX-power parsing is offset-heavy and covers both 2.4/5 GHz groups. Rate-mask logic special-cases `macid` 0/1 and short-GI behavior. Hardware radio switch uses locks and mutable power-state flags; races with IPS/SW RF changes can suppress transitions. CAM key indexing is sensitive for AP mode and default-key modes.

Test signals: EEPROM/efuse dump logs, MAC address programming, TX power table validation per channel, association in STA/AP/ADHOC modes, hardware crypto with WEP/TKIP/AES, RF kill switch toggles, rate-mask H2C traces, and RCR/filter correctness under Cisco/IOT cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.h

Purpose: Declares the shared RTL8192D hardware helper API used by bus-specific implementations.

Important APIs/types: Exposes beacon stop/resume, common hardware get/set, LLT write, security configuration, QoS reset, EEPROM read, HAL rate update, channel access update, GPIO RF switch check, and CAM key setup.

Control flow: The API is intended to be called from bus-specific initialization, mac80211 callbacks, rate-control updates, key setup, and power-management paths. The header itself has no runtime logic.

State and persistence: Functions mutate hardware registers and driver structures such as `rtl_efuse`, `rtl_hal`, `rtl_phy`, `rtl_ps_ctl`, and `rtlpriv->sec`; no header-local state.

Dependencies and integration: Included by rtl8192d common users and rtl8192de hardware code. Requires `ieee80211_hw`, `ieee80211_sta`, and rtlwifi enums/types from surrounding includes.

Risks: Function prototypes expose raw pointers for values and keys, so caller type/length discipline is essential. Common helpers assume bus-specific wrappers supply PCI/USB-specific register and interrupt behavior when needed.

Test signals: Compile coverage and smoke tests through rtl8192de `rtl_hal_ops` paths that call these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/main.c

Purpose: Supplies module metadata for the shared RTL8192D common-routines object.

Important APIs/functions: Uses `MODULE_AUTHOR`, `MODULE_LICENSE`, and `MODULE_DESCRIPTION`. There are no callable driver routines in this file.

Control flow: No runtime control flow besides normal kernel module metadata registration performed by the module macros.

State and persistence: No driver state. Metadata is embedded in the built module object.

Dependencies and integration: Includes `../wifi.h` and `<linux/module.h>`. Built as part of the `rtl8192d-common` object by the adjacent Makefile, supporting bus-specific drivers such as rtl8192de.

Risks: Low. Metadata changes affect module introspection and licensing only.

Test signals: Kernel module build and `modinfo` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.c

Purpose: Implements shared RTL8192D PHY/RF helpers for RF serial access, BB/RF register definitions, TX-power index application, IQK/LCK calibration support, scan-time DIG pause/resume, MAC/PHY mode configuration, and channel-group mapping.

Important APIs/functions: `rtl92d_phy_query_rf_reg()` and `rtl92d_phy_set_rf_reg()` perform masked RF reads/writes. `rtl92d_phy_init_bb_rf_register_definition()` initializes path-specific register addresses. `rtl92d_store_pwrindex_diffrate_offset()` stores PHY_REG_PG power offsets. `rtl92d_phy_set_txpower_level()` calculates channel-adjusted CCK/OFDM power and calls RF6052 writers. `rtl92d_phy_enable_rf_env()`/`restore_rf_env()`, register save helpers, ADDA/MAC calibration setup, `rtl92d_phy_calc_curvindex()`, `rtl92d_phy_reset_iqk_result()`, `rtl92d_phy_set_io_cmd()`, and MAC/PHY mode helpers are exported to bus-specific PHY code.

Control flow: RF access serializes through `rtl92d_pci_lock()` for PCI, reads HSSI parameter/readback registers or writes LSSI address/data fields. TX-power flow converts the requested channel through `channel_all`, pulls EEPROM power indexes from `rtl_efuse`, optionally stores current CCX indexes, writes CCK power on 2.4 GHz, and always writes OFDM power. IO commands pause scan-time DM by backing up IGI and forcing a high/USB-specific IGI, or resume by restoring IGI and TX power. MAC/PHY mode flow writes `REG_MAC_PHY_CTRL_NORMAL` and derives RF type/band/current band by single/dual MAC mode and interface index.

State and persistence: Initializes `rtlphy->phyreg_def[]`, `mcs_offset`, `pwrgroup_cnt`, default initial gains, frame sync defaults, current TX power indexes, IQK matrix defaults, `current_io_type`, `set_io_inprogress`, `rf_type`, and `rtlhal` band/version fields. Writes BB/RF registers but no disk state.

Dependencies and integration: Depends on `dm_common` for DIG writes, `rf_common` for RF6052 TX-power programming, `reg.h` BB/RF register constants, channel5g data from shared definitions, and rtlwifi BB/RF access helpers. Called during hardware init, table loading, channel changes, IQK/LCK, scan handling, and EEPROM parsing.

Risks: Channel-to-index helpers assume valid inputs and use `channel_all` indices rather than raw channel numbers in several places. RF register accesses are timing-sensitive and rely on correct path definitions. `rtl92d_phy_get_chnlgroup_bypg()` is not exported unlike most helpers but is used within RF common. IO pause/resume changes DIG immediately and can affect scan sensitivity. The header includes duplicate sparse-only declarations around inline lock helpers.

Test signals: RF register read/write sanity, BB/RF table loading, channel switch over 2.4/5 GHz, TX power per channel and bandwidth, scan performance, IQK matrix reset/reload, sparse lock-context checks, and dual-MAC MAC/PHY mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.h

Purpose: Declares shared RTL8192D PHY/RF constants, enums, lock helpers, and calibration/TX-power/MACPHY functions.

Important APIs/types: Defines target channel counts, IQK constants, baseband and RF content enums, CCK/page-A lock helpers for dual-interface PCI, RF query/set, BB/RF register-definition initialization, TX-power setup, RF environment save/restore, calibration register save/restore, curve-index calculation, IQK reset, IO command handling, MAC/PHY mode setup, channel grouping, coexistence RF-page setup, and PCI RF lock helpers.

Control flow: Inline helpers conditionally lock only for PCI dual-interface cases and no-op for USB. The exported declarations describe setup flow from hardware initialization through calibration and channel/power updates.

State and persistence: No header-owned state. Helpers operate on `rtl_priv` locks and `rtl_phy`/`rtl_hal` state.

Dependencies and integration: Requires rtlwifi type definitions, `enum radio_path`, `enum io_type`, and interface constants. Included by shared DM/RF/HW and rtl8192de PHY/HW code.

Risks: The same function names appear as `static inline` definitions plus external declarations to satisfy sparse, which is unusual but intentional. Lock helper behavior depends on `rtlhal.interface` and `interfaceindex`; wrong initialization can skip required protection.

Test signals: Compile and sparse context-balance checks, plus runtime RF access on PCI and USB builds if both are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/reg.h

Purpose: Defines the RTL8192D register map, firmware/EEPROM offsets, bit masks, rate constants, interrupt masks, CAM constants, BB/RF register addresses, and helper macros used throughout the driver.

Important APIs/types: Major groups cover system configuration (`REG_SYS_*`, `REG_APS_FSMCO`, `REG_MCUFWDL`), MACTOP/firmware mailboxes, TX/RX DMA, PCIe DBI/descriptors, protocol/rate/aggregation, EDCA/beacon/TSF, WMAC/RCR/security, efuse/EEPROM layout, RCR/SECCFG/power bits, LLT operation fields, rate bitmaps, interrupt masks, TXAGC/IQK registers, and RF6052 register addresses. Helper macros pack LLT fields and define masks like `BLSSIREADBACKDATA`, `RF_CHNLBW`, `RF_T_METER`.

Control flow: No executable flow, but constants drive all control sequences in firmware download, MAC init, LLT init, RF power, rate control, beacon handling, descriptor setup, key programming, and calibration.

State and persistence: Represents hardware and efuse address contracts. EEPROM/efuse offsets describe persistent device calibration and identity storage; runtime registers describe volatile device state.

Dependencies and integration: Included by almost every rtl8192d/rtl8192de source file. Relies on kernel `BIT`, `BIT0`, `BIT1`, `GENMASK`, and rtlwifi rate/queue conventions.

Risks: Mistyped values directly corrupt hardware sequencing. Some definitions are compatibility aliases for 8192C naming and some use raw numeric offsets later in C files, so consistency matters. EEPROM offsets and default power constants are critical for regulatory TX power. Interrupt masks reuse names across normal/extended status bits.

Test signals: Build coverage, hardware init traces, efuse reads, firmware mailbox operation, interrupt handling, RF calibration, TX power table programming, and descriptor/rate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.c

Purpose: Implements shared RF6052 bandwidth and TX-power programming for RTL8192D.

Important APIs/functions: `rtl92d_phy_rf6052_set_bandwidth()` sets RF channel bandwidth bits. `rtl92d_phy_rf6052_set_cck_txpower()` computes and writes CCK TXAGC values. `rtl92d_phy_rf6052_set_ofdm_txpower()` computes OFDM/MCS write values by power base, regulatory mode, bandwidth, channel group, and RF path, then writes TXAGC registers.

Control flow: Bandwidth setting updates cached `rtlphy->rfreg_chnlval[]` and `RF_CHNLBW` bits for each active path. CCK power builds per-path replicated byte values from requested power levels, special-cases active scanning and regulatory mode, applies offset tables when allowed, clamps to `RF6052_MAX_TX_PWR`, then writes split CCK registers. OFDM power derives OFDM and MCS bases from EEPROM differences, selects regulatory write values for Realtek performance, Realtek regulatory groups, better regulatory zero offset, or customer limits, clamps each byte, writes A/B path TXAGC registers, and adjusts adjacent fallback bytes for the final MCS groups.

State and persistence: Consumes `rtl_efuse` regulatory and power-group tables, `rtl_phy->mcs_offset`, `pwrgroup_cnt`, current bandwidth, RF type, and scan state. Writes BB TXAGC and RF bandwidth registers.

Dependencies and integration: Called by `rtl92d_phy_set_txpower_level()` and bus-specific channel/bandwidth code. Uses register constants from `reg.h` and channel grouping from `phy_common.c`.

Risks: Regulatory branch behavior is subtle; changing offsets can violate power limits or reduce throughput. CCK scan behavior uses max power unless regulatory nonzero enables normal levels. OFDM path assumes two RF paths for write loops even when RF type limits active streams. Byte-level clamping and special fallback writes must match hardware expectations.

Test signals: Per-rate TX power register dumps across channels/bandwidths/regulatory modes, active scan behavior, RF bandwidth switch tests, and radiated power/regulatory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.h

Purpose: Declares shared RF6052 bandwidth and TX-power programming entry points.

Important APIs/types: Exposes `rtl92d_phy_rf6052_set_bandwidth()`, `rtl92d_phy_rf6052_set_cck_txpower()`, and `rtl92d_phy_rf6052_set_ofdm_txpower()`.

Control flow: No runtime flow; callers use these functions after EEPROM power tables, RF paths, current channel, and current bandwidth are initialized.

State and persistence: Functions declared here mutate RF/BB registers and `rtlphy->rfreg_chnlval[]`; the header owns no state.

Dependencies and integration: Included by PHY common and RF implementation. Requires `ieee80211_hw` and kernel integer types.

Risks: API accepts raw power-level byte arrays; callers must provide at least path A/B entries and a valid channel. Wrong call order can program invalid TX power.

Test signals: Compile coverage and TX-power/channel-change tests via `rtl92d_phy_set_txpower_level()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.c

Purpose: Implements shared RX descriptor parsing, PHY status interpretation, RSSI/EVM smoothing, and generic descriptor set/get helpers for RTL8192D.

Important APIs/functions: `rtl92d_rx_query_desc()` converts a hardware RX descriptor and optional PHY status into `rtl_stats` plus mac80211 `ieee80211_rx_status`. `rtl92d_set_desc()` sets TX/RX ownership, next descriptor address, RX buffer address/length/EOR. `rtl92d_get_desc()` reads descriptor ownership, buffer address, and packet length. Internal helpers decode CCK/OFDM PHY status, smooth UI RSSI/link quality, update PWDB, and classify BSSID/self/beacon packets.

Control flow: RX descriptor parsing extracts packet length, driver-info size, buffer shift, CRC/ICV, encryption, MCS/rate, AMPDU flags, timestamp, bandwidth and HT flags, then populates mac80211 rate/frequency/band/flags. If PHY status is present, it locates driver info in the skb, decodes CCK or OFDM power/quality, checks frame addresses against BSSID and local MAC, updates smoothed RSSI/PWDB/link-quality state for self or beacon packets, and sets `rx_status->signal`.

State and persistence: Updates `rtlpriv->stats` smoothing windows, RSSI percentages, SNR, EVM, signal strength/quality, `rtlpriv->dm.undec_sm_pwdb`, and per-packet `rtl_stats`. Descriptor writes hand ownership to hardware with memory barriers; no disk persistence.

Dependencies and integration: Depends on descriptor bit helpers from `trx_common.h`, rtlwifi base/stats helpers, mac80211 headers, `rtl_signal_scale_mapping()`, `rtlwifi_rate_mapping()`, and `rtl_efuse`/`rtl_mac` identity state. Bus-specific TX/RX paths call these through ops.

Risks: skb offsets rely on descriptor `rx_drvinfo_size` and `rx_bufshift` being valid. PHY CCK/OFDM formulas are hardware-specific. Address parsing assumes enough frame header bytes after descriptor stripping. Descriptor ownership uses `wmb()`; ordering bugs can cause DMA races. `rx_status->signal = recvsignalpower + 10` differs from raw dBm.

Test signals: RX under CCK/OFDM/HT, CRC/ICV failure handling, encrypted packet flagging, AMPDU first/subsequent packets, RSSI/link-quality stability, descriptor DMA ring recycling, and mac80211 rate/band reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.h

Purpose: Defines RTL8192D TX/RX descriptor bitfield helpers, RX PHY info layout, encryption enum, early-mode helpers, and shared descriptor API prototypes.

Important APIs/types: Provides `set_tx_desc_*`, `get_tx_desc_*`, `get_rx_desc_*`, `set_rx_desc_*`, and `set_earlymode_*` inline helpers using little-endian bitfield accessors. Defines `enum rtl92d_rx_desc_enc` and packed `struct rx_fwinfo_92d` containing gain, PWDB, CFO, EVM, SNR, CSI, SGI, RXSC, and interference fields.

Control flow: Header helpers are invoked by shared RX parsing and bus-specific TX descriptor fill code to set DMA ownership, queue selection, rate, security, RTS/CTS, aggregation, buffer addresses, and status extraction.

State and persistence: No header-owned state. The helpers read/write DMA descriptors shared with hardware, so their effects persist in descriptor rings until overwritten.

Dependencies and integration: Requires kernel little-endian bit helpers and rtlwifi descriptor names from surrounding code. Used by common TRX parsing and rtl8192de TX path.

Risks: Bit positions must match hardware exactly. Packed PHY layout depends on endianness bitfields. Missing barriers in callers would make ownership changes unsafe; this header only supplies primitives.

Test signals: Descriptor dump comparison, TX/RX DMA correctness, HT/SGI/bandwidth flags, encryption status, early-mode aggregation, and sparse/endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/Makefile

Purpose: Defines the rtl8192de PCI module object composition for Kbuild.

Important APIs/types: `rtl8192de-objs` lists `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8192DE) += rtl8192de.o` wires the aggregate object to the kernel config symbol.

Control flow: Build-system only. Kbuild links the listed objects into `rtl8192de.o` when `CONFIG_RTL8192DE` is enabled.

State and persistence: No runtime state. It controls build outputs.

Dependencies and integration: Integrates with the parent rtlwifi Kbuild and depends on rtl8192d common support through source includes and symbol exports.

Risks: Omitting an object drops required ops, tables, or module registration. Object order can matter for duplicate/static initialization only in limited cases, but missing table/phy/trx objects would break linking.

Test signals: Kernel build with `CONFIG_RTL8192DE=m/y` and successful module link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.c

Purpose: Implements rtl8192de-specific dynamic-management initialization and watchdog flow around shared RTL8192D DM helpers.

Important APIs/functions: `rtl92de_dm_init()` initializes driver-owned DM mode, DIG bounds, dynamic TX power, EDCA turbo, rate adaptive mask, and power tracking. `rtl92de_dm_watchdog()` gates periodic DM work on RF/power-save state. Internal helpers handle dynamic TX high-power level selection and PWDB RSSI reporting to firmware.

Control flow: Init sets `dm_type = DM_TYPE_BYDRIVER`, calls common DIG init, sets DIG gain min/max, then initializes dynamic TX power, EDCA, RA mask, and thermal tracking. Watchdog exits unless RF is on, firmware power-save is treated awake, and RF change is not in progress. When allowed, it reports PWDB to firmware/register, collects false alarms, finds minimum RSSI, runs DIG, adjusts dynamic TX power, and checks EDCA turbo.

State and persistence: Mutates `rtlpriv->dm.dynamic_txpower_enable`, `last_dtp_lvl`, `dynamic_txhighpower_lvl`, `dm_type`, `useramask`, `undec_sm_pwdb`, `entry_min_undec_sm_pwdb`, and `dm_digtable` thresholds. Dynamic TX power may call `rtl92d_phy_set_txpower_level()` to write runtime TX power registers.

Dependencies and integration: Depends on rtl8192d common DM/PHY/FW helpers, rtlwifi core/base, mac80211 link/opmode state, current band/channel, and firmware H2C command support. The sw/ops layer calls these during init and watchdog.

Risks: `fw_current_inpsmode` and `fwps_awake` are hard-coded local values in this file, so actual firmware power-save status is not consulted here. Dynamic TX power thresholds differ for 2.4/5 GHz and use smoothed PWDB; incorrect PWDB can over-reduce transmit power. Thermal tracking call is commented out in watchdog.

Test signals: Watchdog traces during link/unlink, TX power level transitions near thresholds, firmware RSSI report command, DIG false-alarm response, and EDCA changes under uplink/downlink traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.h

Purpose: Declares rtl8192de dynamic-management entry points.

Important APIs/types: Exposes `rtl92de_dm_init()` and `rtl92de_dm_watchdog()`.

Control flow: Header-only declaration for initialization and periodic watchdog scheduling.

State and persistence: No local state; declared functions mutate `rtl_priv` DM and hardware registers.

Dependencies and integration: Included by rtl8192de `dm.c`, `hw.c`, and module ops setup. Requires `struct ieee80211_hw` declarations from surrounding includes.

Risks: Header guard uses `__RTL92C_DM_H__`, a naming carryover that is harmless unless colliding with another included header.

Test signals: Compile coverage and ops wiring to DM init/watchdog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.c

Purpose: Implements rtl8192de PCI firmware download coordination and reserved-page packet upload for firmware power-save/offload features.

Important APIs/functions: `rtl92d_download_fw()` strips a firmware header, coordinates dual-MAC firmware download through global locks and a register in-progress bit, resets running 8051 firmware when needed, downloads firmware, and waits for common firmware init. `_rtl92d_cmd_send_packet()` sends a command/reserved packet through the beacon queue. `rtl92d_set_fw_rsvdpagepkt()` builds beacon, PS-Poll, null data, and probe response reserved pages and reports page locations to firmware.

Control flow: Firmware download checks firmware buffer availability, parses version/subversion, skips a 32-byte header when recognized, then under `globalmutex_for_fwdownload` checks whether firmware is already downloaded or another MAC is downloading. It waits up to 5000 500-us intervals for the other MAC, otherwise marks download in progress via register `0x1f[5]`. It self-resets RAM firmware if `REG_MCUFWDL[7]`, enables download, writes firmware pages, disables download, runs checksum/ready, clears the in-progress bit, and finally calls `rtl92d_fw_init()`. Reserved page setup patches static packet templates with current MAC/BSSID/AID, allocates an skb, queues it through the beacon TX descriptor, polls beacon queue, and sends `H2C_RSVDPAGE`.

State and persistence: Uses `rtlhal->pfirmware`, `fwsize`, `fw_version`, `fw_subversion`, global firmware-download mutexes, register `0x1f[5]`, beacon TX ring queue/descriptors, and static `reserved_page_packet`. Runtime firmware receives reserved page locations; no disk state.

Dependencies and integration: Depends on common firmware helpers, PCI rings/descriptors, rtlwifi skb/queue helpers, mac80211 MAC/BSSID state, and H2C command IDs. Called from rtl8192de hardware initialization and join-BSS handling.

Risks: Static `reserved_page_packet` is modified in place for the current interface, so concurrent dual-interface calls could race unless higher-level sequencing prevents it. `_rtl92d_cmd_send_packet()` dequeues and frees an existing beacon skb unconditionally. Firmware download relies on magic register `0x1f[5]` for inter-MAC arbitration. Returning `1` when firmware buffer is absent blends normal errno and boolean-style errors.

Test signals: Firmware load on cold boot and second MAC, timeout when firmware missing/hung, join/reserved-page H2C traces, suspend/resume, beacon queue integrity, and power-save null/PS-Poll offload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.h

Purpose: Declares rtl8192de firmware download and reserved-page upload functions.

Important APIs/types: Exposes `rtl92d_download_fw()` and `rtl92d_set_fw_rsvdpagepkt()`.

Control flow: No runtime logic; these functions are called during hardware initialization and join/power-save setup.

State and persistence: No local state. Declared functions mutate firmware registers, firmware RAM, TX rings, and H2C state.

Dependencies and integration: Included by rtl8192de firmware and hardware code. Requires `ieee80211_hw` and boolean type definitions from surrounding includes.

Risks: Header guard name contains doubled underscores around `FW`, but remains unique enough locally. API returns `int` for firmware download but callers treat nonzero as failure.

Test signals: Compile/link coverage through `rtl92de_hw_init()` and `HW_VAR_H2C_FW_JOINBSSRPT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.c

Purpose: Implements rtl8192de PCI hardware operations: DBI access, HW variable handling, MAC/LLT initialization, full hardware initialization, network type and BSSID filters, interrupt masks, poweroff/card disable, beacon registers, and suspend/resume register preservation.

Important APIs/functions: Public functions include `rtl92de_read_dword_dbi()`, `rtl92de_write_dword_dbi()`, `rtl92de_get_hw_reg()`, `rtl92de_set_hw_reg()`, `rtl92de_hw_init()`, `rtl92de_set_network_type()`, `rtl92de_set_check_bssid()`, `rtl92d_linked_set_reg()`, interrupt enable/disable/update/recognized, `rtl92de_card_disable()`, beacon register setters, `rtl92de_suspend()`, and `rtl92de_resume()`. Key internals include `_rtl92de_llt_table_init()`, `_rtl92de_init_mac()`, `_rtl92de_hw_configure()`, `_rtl92de_poweroff_adapter()`, and beacon control helpers.

Control flow: Hardware init marks adapter initializing, resets IQK, initializes MAC under `globalmutex_for_power_and_efuse`, downloads firmware, enables early mode/RDG as configured, loads MAC/BB/RF tables, applies BB/RF post-configuration, enables CCK/OFDM, configures protocol/EDCA/beacon/rate defaults, resets CAM, enables hardware security, captures original PHY values, programs TX power, enables ASPM backdoor, initializes DM, runs LCK, and waits for dual-MAC RF LO readiness before marking init ready. Card disable stops link/beacons, updates LEDs, halts TX/RX DMA, turns RF/BB off, resets MAC, then runs a poweroff adapter sequence that resets firmware, GPIO/LED, PLL/SPS/XTAL, and PCIe suspend state.

State and persistence: Maintains `rtlpci->reg_bcn_ctrl_val`, `receive_config`, `transmit_config`, descriptor DMA base registers, irq masks/enabled flag, `being_init_adapter`, `init_ready`, `up_first_time`, ASPM support, `rtlhal->macphyctl_reg`, firmware mailbox state, RF power state, `mac->link_state`, TSF, and beacon interval. Writes large sets of volatile registers; suspend stores/restores `REG_MAC_PHY_CTRL_NORMAL`.

Dependencies and integration: Depends on rtl8192d common register, firmware, DM, HW, and PHY helpers plus rtl8192de PHY/RF/SW/LED/TRX table modules. Tied to rtlwifi PCI ring structures, mac80211 interface modes, global Realtek locks, power-save code, and CAM/security helpers.

Risks: Initialization is highly ordered; moving firmware, BB/RF table, CAM, TX power, or DM steps can break hardware. LLT setup has different page maps for single vs dual MAC. Multiple magic registers are written by literal offsets. `rtl92de_set_beacon_related_registers()` disables interrupts but does not re-enable them in that function. Poweroff behavior differs by interface index and dual-MAC mode. DBI access uses fixed delays with no completion polling.

Test signals: Cold boot, firmware load, descriptor DMA addresses, interrupt delivery, STA/AP/ADHOC mode switching, beaconing/TSF correction, BSSID filtering, hardware crypto, suspend/resume, RF kill/card disable, dual-MAC mode, and `init_ready` failure logs around RF LO polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.h

Purpose: Declares rtl8192de PCI hardware operation entry points.

Important APIs/types: Exposes hardware get/set, interrupt recognition and mask control, initialization and card disable, network type/BSSID/beacon controls, DBI read/write, suspend/resume, and linked-channel IQK check.

Control flow: Header declarations support the rtl8192de ops table in `sw.c` and calls across firmware/DM/PHY code.

State and persistence: No header state. Functions manipulate PCI rings, hardware registers, interrupts, RF state, and cached suspend register values.

Dependencies and integration: Requires `ieee80211_hw`, `rtl_int`, `nl80211_iftype`, and kernel integer types. Included by rtl8192de hardware and ops setup.

Risks: Raw value-pointer API mirrors rtlwifi core and depends on callers passing the correct type for each `HW_VAR`. Interrupt functions must be paired correctly by bus layer.

Test signals: Compile/link coverage through rtl8192de HAL ops and runtime init/interrupt/network-mode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.c

Purpose: Implements rtl8192de software LED control through LED configuration registers.

Important APIs/functions: `rtl92de_sw_led_on()` and `rtl92de_sw_led_off()` write `REG_LEDCFG1/2` for LED pins. `_rtl92ce_sw_led_control()` maps high-level LED actions to on/off. `rtl92de_led_control()` gates LED changes based on RF-off reason and dispatches control actions.

Control flow: LED-on handles GPIO0 as no-op, LED0 by setting LEDCFG2 bits with device-ID special handling for `0x8176`/`0x8193`, and LED1 by writing LEDCFG2 from LEDCFG1-derived state. LED-off uses open-drain policy for LED0 and a fixed off bit for LED1. High-level control turns LED on for power-on/link/no-link and off for power-off. TX/RX/site-survey/link actions are ignored when RF is off for reasons beyond power save.

State and persistence: Reads `rtlpriv->efuse.eeprom_did`, `rtlpriv->ledctl.sw_led0`, `rtlpriv->ledctl.led_opendrain`, and `rtl_ps_ctl->rfoff_reason`. Mutates volatile LEDCFG registers only.

Dependencies and integration: Depends on rtlwifi LED enums/control modes, PCI/wifi structures, power-save state, and RTL8192D register definitions. Called from hardware init, media-status changes, and poweroff paths via `cfg->ops->led_control`.

Risks: LED1-on reads `REG_LEDCFG1` but writes `REG_LEDCFG2`, matching existing code but worth preserving carefully. Default switch cases log errors for unsupported pins. RF-off gating can suppress expected visual state changes during manual RF off.

Test signals: LED behavior on power on/off, link/no-link, RF kill, open-drain boards, and device IDs 0x8176/0x8193.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.h

Purpose: Declares rtl8192de LED control entry points.

Important APIs/types: Exposes `rtl92de_sw_led_on()`, `rtl92de_sw_led_off()`, and `rtl92de_led_control()`.

Control flow: No runtime logic. Callers use low-level pin controls or high-level LED action control.

State and persistence: No header state; functions write LED registers and read `rtl_priv` LED/power state.

Dependencies and integration: Requires `ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode` declarations. Included by rtl8192de LED and hardware code.

Risks: Header guard uses `__RTL92CE_LED_H__`, a carryover from a related chipset; collision risk is low unless both headers are included with the same guard name.

Test signals: Compile/link through `cfg->ops->led_control` and direct hardware LED state tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.h -->
