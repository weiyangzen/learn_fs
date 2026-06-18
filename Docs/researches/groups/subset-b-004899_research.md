# subset-b-004899 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/wifi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/wifi.h

## Purpose
`wifi.h` is the central shared contract for the legacy `rtlwifi` Realtek mac80211 driver family. It is not an implementation file; it defines hardware constants, firmware command/event formats, register masks, rate identifiers, state enums, shared driver data structures, operation tables, and small inline wrappers used by PCI/USB bus code and chip-specific HALs. Most `rtlwifi` modules include this header to agree on the shape of `struct rtl_priv` and its subobjects.

## Important APIs, types, and state
The top of the file defines common register masks, RF power-change reasons, queue indexes, CAM/key sizes, channel group sizes, firmware H2C/C2H IDs, TX report extractors, WoWLAN pattern limits, and hardware type predicates such as `IS_HARDWARE_TYPE_8822B()`. These constants are consumed throughout descriptor handling, firmware mailbox handling, RF/BB programming, and power management.

The major state containers are `struct rtl_priv` and the structures embedded in it: `rtl_mac` for mac80211-visible link, queue, HT/VHT, BSSID, EDCA, and scanning state; `rtl_hal` for chip identity, firmware buffers, H2C state, interface type, dual-MAC state, and WoWLAN firmware; `rtl_phy` for RF path, channel, bandwidth, IQK, power indexes, per-rate power tables, and calibration backup registers; `rtl_dm` for dynamic mechanism state such as DIG, thermal tracking, CFO, tx power tracking, and antenna training; `rtl_security` for key buffers and CAM bitmap; `rtl_efuse` for EEPROM/efuse-derived board and power data; `rtl_ps_ctl` for IPS/LPS/RF power state and wake reasons; `rtl_stats` and `wireless_stats` for per-packet and aggregate signal/counter data; `rtl_btc_info`, `bt_coexist_info`, and `rtl_btc_ops` for Bluetooth coexistence; and `rtl_hal_ops` plus `rtl_intf_ops` for chip and bus callbacks.

The inline API layer includes `rtl_read_byte/word/dword()`, `rtl_write_byte/word/dword()`, `rtl_write_chunk()`, `rtl_get_bbreg()`, `rtl_set_bbreg()`, `rtl_get_rfreg()`, `rtl_set_rfreg()`, HAL state helpers, SKB header/TID helpers, station lookup helpers, and `calculate_bit_shift()`. These wrappers route all MMIO/USB/PCI register access through `rtlpriv->io` and chip operations through `rtlpriv->cfg->ops`.

## Control flow and integration
Control flow is indirect by design. mac80211 callbacks and bus drivers operate on `struct ieee80211_hw`, recover `struct rtl_priv` with `rtl_priv(hw)`, then use `rtl_hal_ops` for chip-specific hardware work and `rtl_intf_ops` for bus-specific transport. Descriptor fill/query, RF calibration, channel switching, firmware command filling, security CAM programming, rate updates, and debug/BT coexistence are all reached through these callback tables.

## State and persistence behavior
This header describes mostly runtime state. Persistent hardware configuration enters through efuse/EEPROM fields in `rtl_efuse`, firmware images in `rtl_hal`, and WoWLAN pattern state in `rtl_wow_pattern` and `rtl_ps_ctl`. Security state persists only for the live device instance in CAM bitmap/key buffers. Power-save and BT coexistence fields are state machines carried across callbacks, timers, and workqueue activity.

## Dependencies and risks
The file depends on Linux kernel networking, mac80211, firmware loading, USB, completions, and local `debug.h`. Its risk profile is high because structure layout and enum values are shared ABI inside the driver family. A change can silently break descriptor programming, firmware commands, power save, or chip-specific callbacks. The duplicated mask definitions near the top are harmless but indicate historical accumulation. Bitfield structures and packed station data require attention to endian/layout assumptions.

## Test signals
Useful test signals include successful compile across representative `rtlwifi` PCI and USB chip configs, firmware load and C2H/H2C handling, association on 2.4 GHz and 5 GHz, WoWLAN suspend/resume, encryption key install/remove, rate control updates, BT coexistence debug output, and lockdep or KASAN coverage around workqueues, SKB control block use, and register wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/wifi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Kconfig

## Purpose
This Kconfig file declares the build-time configuration surface for the `rtw88` Realtek 802.11ac mac80211 driver family. It separates the common core, transport modules, chip-family helper symbols, concrete adapter symbols, debug options, and LED support.

## Important symbols
`menuconfig RTW88` is the user-visible umbrella tristate and depends on `MAC80211`. Internal symbols include `RTW88_CORE`, `RTW88_PCI`, `RTW88_SDIO`, `RTW88_USB`, chip-family symbols such as `RTW88_8822B`, `RTW88_8822C`, `RTW88_8723X`, `RTW88_8703B`, `RTW88_8723D`, `RTW88_8821C`, `RTW88_88XXA`, `RTW88_8821A`, `RTW88_8812A`, and `RTW88_8814A`. Adapter symbols bind chip and bus support, for example `RTW88_8822BE` selects `RTW88_CORE`, `RTW88_PCI`, and `RTW88_8822B`, while `RTW88_8822BU` selects core, USB, and 8822B.

The adapter coverage includes PCI, SDIO, and USB variants for 8822B/8822C/8723D/8821C, plus 8723CS/8703B, 8821AU/8812AU, and 8814AE/8814AU. `RTW88_DEBUG` and `RTW88_DEBUGFS` add optional debugging. `RTW88_LEDS` defaults to `y` only when the LED class is built-in or compatible with mac80211.

## Control flow and build integration
Kconfig does not run code, but it controls which object lists in the sibling Makefile are reachable. Concrete device symbols use `depends on PCI`, `depends on MMC`, or `depends on USB`, then select the core, transport, and chip-family implementation needed by that adapter. This creates a composable matrix: one core module, one bus module, and one chip module combine into a concrete device module.

## State and persistence behavior
The only persistent behavior is kernel configuration state. Selections become part of `.config` and determine built-in versus module linkage. Because many intermediate symbols are non-prompt tristates, users generally choose adapter symbols rather than low-level core/transport symbols directly.

## Dependencies and integration points
The file integrates with Linux Kconfig, mac80211, bus subsystems (`PCI`, `MMC`, `USB`), `WANT_DEV_COREDUMP`, and LED class support. Its choices must match Makefile object names and source file availability. Device IDs in transport-specific files rely on the corresponding Kconfig symbols being enabled.

## Risks and test signals
The main risk is an incorrect `select` or dependency that lets a device symbol build without its transport or chip support, or prevents valid module combinations. Another risk is LED configuration mismatch when `LEDS_CLASS` and `MAC80211` are configured differently. Test signals include `allyesconfig`/`allmodconfig` builds, targeted builds for each adapter symbol, module names matching help text where promised, and dependency pruning when PCI, MMC, or USB support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the `rtw88` directory to kernel modules and object composition. It defines the common `rtw88_core.o`, per-chip modules, per-adapter bus glue modules, and transport modules for PCI, SDIO, and USB.

## Important build products
`rtw88_core-y` contains the shared implementation: `main.o`, `mac80211.o`, `util.o`, `debug.o`, `tx.o`, `rx.o`, `mac.o`, `phy.o`, `coex.o`, `efuse.o`, `fw.o`, `ps.o`, `sec.o`, `bf.o`, `sar.o`, and `regd.o`. Optional core pieces are `wow.o` under `CONFIG_PM` and `led.o` under `CONFIG_RTW88_LEDS`.

Chip-family modules include `rtw88_8822b.o`, `rtw88_8822c.o`, `rtw88_8723x.o`, `rtw88_8703b.o`, `rtw88_8723d.o`, `rtw88_8821c.o`, `rtw88_88xxa.o`, `rtw88_8821a.o`, `rtw88_8812a.o`, and `rtw88_8814a.o`, usually pairing logic files with generated or static table files. Concrete bus modules include names such as `rtw88_8822be.o`, `rtw88_8822bs.o`, `rtw88_8822bu.o`, `rtw88_8821au.o`, and `rtw88_8814ae.o`. Transport modules are `rtw88_pci.o`, `rtw88_sdio.o`, and `rtw88_usb.o`.

## Control flow and integration
The kernel build system expands `obj-$(CONFIG_...)` and `*-objs` lists. Kconfig selects decide which modules are built; this file decides which compilation units are linked into each module. The common core always includes coexistence and beamforming support (`coex.o`, `bf.o`), while chip modules provide operation tables consumed by the core.

## State and persistence behavior
The Makefile has no runtime state. Build output state is determined by `.config` and by module/built-in linkage decisions. Optional PM and LED source objects are compiled only when their associated configs are active.

## Dependencies and integration points
This file must stay synchronized with `Kconfig`, source filenames, module aliases/device tables in adapter files, and exported symbols between core, chip, and transport modules. It also relies on kernel kbuild conventions for composite object names and conditional object lists.

## Risks and test signals
Risks are mostly build graph breakage: missing an object in a composite module, stale source names, adding a Kconfig symbol without an object rule, or linking an adapter module without its chip/transport dependency. Test signals include targeted `M=drivers/net/wireless/realtek/rtw88` builds for each enabled adapter, modpost symbol checks, module load ordering, and runtime probe on PCI/SDIO/USB variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.c

## Purpose
`bf.c` implements shared beamforming helper logic for `rtw88` chips. It decides whether a connected BSS can use SU or MU beamformee mode, tracks beamformer resource counts, programs common beamforming registers, handles MU group ID table updates, and exposes helper functions for chip-specific wrappers.

## Important APIs and control flow
`rtw_bf_assoc()` runs on association when global beamforming support is enabled. It skips non-5 GHz chips, finds the AP station entry under RCU, compares local VHT beamformee capabilities with peer beamformer capabilities, and chooses MU first, then SU. MU setup fills `bfee->mac_addr`, role, partial AID, and association ID, checks `chip->bfer_mu_max_num`, increments `bf_info.bfer_mu_cnt`, and calls `rtw_chip_config_bfee(..., true)`. SU setup checks `chip->bfer_su_max_num`, records sounding dimensions, allocates a register slot from `bf_info.bfer_su_reg_maping`, increments `bfer_su_cnt`, and calls the same chip hook.

`rtw_bf_disassoc()` reverses the association role by decrementing SU/MU counters, invoking `rtw_chip_config_bfee(..., false)`, and clearing the vif role. `rtw_bf_set_gid_table()` copies `conf->mu_group.membership` and `position` into a `cfg_mumimo_para` and programs the MU tables only when the vif is currently an MU beamformee.

Low-level helpers program hardware registers: `rtw_bf_init_bfer_entry_mu()` writes MU beamformer MAC/PAID/CSI control; `rtw_bf_cfg_sounding()` configures sounding protocol and BF report poll filters; `rtw_bf_cfg_mu_bfee()` loads MU GID/user position tables; `rtw_bf_del_bfer_entry_mu()` and `rtw_bf_del_sounding()` clear MU and sounding state. `rtw_bf_enable_bfee_su()` and `rtw_bf_enable_bfee_mu()` set CSI report parameters and RX filter acceptance, while remove helpers clear the corresponding register slots. `rtw_bf_phy_init()` initializes MU-MIMO control defaults. `rtw_bf_cfg_csi_rate()` switches CSI report rate based on RSSI threshold.

## State and dependencies
Persistent runtime state is split between `struct rtw_vif::bfee` and `struct rtw_dev::bf_info`. `bfee` stores role, peer MAC, partial AID, sounding dimensions, SU register index, and MU AID. `bf_info` stores active MU/SU counts, SU register slot bitmap, and current CSI report rate. Hardware state persists in MAC/BB registers until removed or reinitialized. Dependencies include mac80211 station/BSS data, VHT capability bits, `main.h` beamforming structs, register definitions, chip operation callbacks, and exported symbols used by chip files such as 8822B/8822C/8821C.

## Integration points
mac80211 BSS change handling calls `rtw_bf_assoc()` on association and `rtw_bf_disassoc()` on disassociation. MU group updates enter through `rtw_chip_set_gid_table()`, which is implemented by capable chips as `rtw_bf_set_gid_table()`. Chip-specific operation tables provide `config_bfee` and `cfg_csi_rate`; chips without support leave those hooks NULL.

## Risks and test signals
Counter and bitmap accounting is the main correctness risk: double association/disassociation or missing role checks can underflow counters or leak SU register slots. Capability handling is VHT-only and 5 GHz-gated, so HE/EHT or 2.4 GHz cases are intentionally outside this path. Register programming is chip-sensitive; incorrect CSI parameters can break sounding or rate feedback. Test signals include association with SU/MU-capable APs, MU group changes, disassociation cleanup, repeated roam cycles, debug category `RTW_DBG_BF`, CSI rate changes around RSSI 40, and register traces for `REG_ASSOCIATED_BFMER*`, `REG_MU_TX_CTL`, and `REG_BBPSF_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.h

## Purpose
`bf.h` is the public beamforming interface for the `rtw88` core and chip implementations. It centralizes beamforming register offsets, bit definitions, CSI/sounding enums, parameter structs, function prototypes, and thin chip-operation dispatch helpers.

## Important definitions and APIs
The header defines beamforming register addresses such as `REG_TXBF_CTRL`, `REG_ASSOCIATED_BFMER0_INFO`, `REG_ASSOCIATED_BFMER1_INFO`, `REG_TX_CSI_RPT_PARAM_BW20`, `REG_SND_PTCL_CTRL`, `REG_MU_TX_CTL`, `REG_MU_STA_GID_VLD`, `REG_MU_STA_USER_POS_INFO`, `REG_WMAC_MU_BF_OPTION`, and `REG_WMAC_MU_BF_CTL`. Bit fields cover sounding protocol control, MU retry/table validity, CSI report rate forcing, RX filter bits, and NDP/NDPA behavior.

`enum csi_rsc` selects CSI bandwidth source, and `enum csi_seg_len` selects MU CSI segment length. `struct cfg_mumimo_para` carries MU-MIMO group/user-position table data from mac80211 BSS configuration to hardware programming. `struct mu_bfer_init_para` carries the MU beamformer address, PAID, CSI parameter, AID, and segment length for register initialization.

The declared functions split into association policy (`rtw_bf_assoc`, `rtw_bf_disassoc`), register setup/cleanup (`rtw_bf_init_bfer_entry_mu`, `rtw_bf_cfg_sounding`, `rtw_bf_cfg_mu_bfee`, `rtw_bf_del_bfer_entry_mu`, `rtw_bf_del_sounding`), SU/MU enable and remove helpers, GID table programming, PHY init, and CSI rate adaptation.

## Control flow and integration
The static inline wrappers are the key integration contract. `rtw_chip_config_bfee()` checks `rtwdev->chip->ops->config_bfee` before dispatching to chip-specific enable/remove code. `rtw_chip_set_gid_table()` and `rtw_chip_cfg_csi_rate()` similarly guard optional chip hooks. This allows the core mac80211 path to invoke beamforming operations while unsupported chips safely do nothing.

## State and persistence behavior
The header itself owns no state, but it defines the register and parameter ABI that manipulates persistent device state in `struct rtw_bfee`, `struct rtw_bf_info`, and hardware registers. Register definitions here must match the common Realtek MAC/BB layout expected by `bf.c` and chip-specific wrappers.

## Dependencies and risks
Dependencies include `main.h` structures, `reg.h` register access helpers, Linux bit macros, and chip operation tables. Risks include stale register constants, mismatched bit masks, and unguarded chip callbacks. Since these helpers are included by multiple chip files, changing a prototype or struct layout can break all beamforming-capable chips.

## Test signals
Compile coverage should include chips with populated beamforming hooks and chips with NULL hooks. Runtime signals include successful SU/MU association, GID table updates, CSI report rate changes, debug logs from `RTW_DBG_BF`, and absence of NULL callback crashes on unsupported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.c

## Purpose
`coex.c` implements the `rtw88` Wi-Fi/Bluetooth coexistence policy engine. It collects Wi-Fi and BT state, interprets firmware BT info C2H messages, maintains scoreboard bits, selects antenna/GNT/table/TDMA/RF parameters, handles delayed state decay, and exposes debugfs reporting.

## Main control flow
The central function is `rtw_coex_run_coex()`. It requires `rtwdev->mutex`, exits if the device is not running, updates Wi-Fi link state and RSSI bands, monitors whether BT is enabled, honors manual/stop/IPS/freeze gates, then selects one action path. The decision tree first handles pure 5 GHz, then 2.4 GHz single-port cases: BT disabled, native LPS, game HID, WHQL test, BT relink, inquiry/page, BT idle, Wi-Fi link/scan, connected profile-specific coexistence, or not-connected Wi-Fi.

Profile-specific action functions map current state to antenna path, RF power/gain, coexistence table, and TDMA case. Examples include `rtw_coex_action_bt_hid()`, `rtw_coex_action_bt_a2dp()`, `rtw_coex_action_bt_pan()`, combinations such as `rtw_coex_action_bt_a2dp_pan_hid()`, Wi-Fi states such as `rtw_coex_action_wl_under5g()` and `rtw_coex_action_wl_linkscan()`, and fallback all-off or Wi-Fi-only actions. `rtw_coex_algorithm()` derives the profile algorithm from HFP/HID/A2DP/PAN presence bits.

## Important APIs and state
Exported entry points include power/init functions, IPS/LPS/scan/connect/media/switchband/status notifiers, BT info/HID/FW debug notifiers, BT info queries, scoreboard writes, indirect LTE coexistence register access, delayed-work callbacks, and debugfs display. State lives in `rtwdev->coex`: `coex->stat` stores BT profile bits, counters, scoreboard, TDMA/table state, RSSI-derived flags, power-save flags, mailbox/cache data, HID info, and Wi-Fi busy/link flags; `coex->dm` stores current decisions such as reason, TDMA parameters, table, antenna position, RSSI states, RF power/gain levels, and channel info; `coex->rfe` stores antenna/RFE properties populated by chip callbacks.

BT info processing in `rtw_coex_bt_info_notify()` handles multiple sources: BT IQK, BT scoreboard, H2C 0x60 echo, WL firmware reply, BT response, and BT active reports. It validates length, deduplicates repeated reports, decodes profile and status bits, updates RSSI, relink/inquiry/multilink timers, HID/BLE/A2DP/PAN/HFP state, then runs coexistence. Debugfs helpers request BT patch/supported versions and vendor registers through `rtw_coex_info_request()`, which sends an H2C mailbox query and waits on `coex->wait` for `rtw_coex_info_response()` to queue a response SKB.

## Dependencies and integration points
The module integrates with mac80211 lifecycle callbacks, firmware H2C/C2H helpers in `fw.c`, chip-specific coexistence ops, `ps.c` LPS helpers, BB/RF register access, debugfs, delayed work initialized in `main.c`, and SKB queues/waitqueues in `rtw_dev`. It also uses chip tables for shared/non-shared antenna TDMA and coexistence table cases.

## Risks and test signals
Risks include policy regressions from table/TDMA case changes, stale delayed-work state after disconnect or power transitions, deadlocks if mailbox queries run without `rtwdev->mutex`, scoreboard bit inversion differences across chips, and incorrect BT info decoding. Test signals include BT audio/HID/PAN traffic while Wi-Fi scans, associates, roams, enters LPS/IPS, switches 2.4/5 GHz, and runs high throughput; debugfs `coex_info`; H2C/C2H traces; lockdep for delayed work; and register snapshots for `REG_BT_COEX_TABLE*`, `REG_WIFI_BT_INFO`, LTE coexistence indirect registers, GNT state, and TDMA parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.h

## Purpose
`coex.h` defines the public constants, enums, parameter structs, chip-operation wrappers, exported functions, and small state predicates for the `rtw88` coexistence engine in `coex.c`.

## Important definitions and APIs
The header defines timing constants (`COEX_REQUEST_TIMEOUT`, `COEX_MIN_DELAY`, `COEX_RFK_TIMEOUT`), firmware H2C 0x69 opcodes, TDMA timer types, RSSI state predicates, and response payload extractors. Enums describe BT MP info operations, antenna phases, coexistence run reasons, LTE table types, GNT setup states, external antenna positions/control sources, coexistence algorithms, BT profile bitmaps, Wi-Fi link modes, scoreboard bits, power-save types, RSSI hysteresis states, notifier event types, BT status values, throughput direction, Wi-Fi priority masks, common chip setup commands, indirect register types, PSTDMA type, and BT RSSI encoding type.

Small parameter structs include `coex_table_para` for BT/WL PTA table values, `coex_tdma_para` for five-byte TDMA firmware parameters, `coex_5g_afh_map` for Wi-Fi-to-BT AFH channel mapping, and `coex_rf_para` for Wi-Fi/BT TX power and RX gain decisions.

The inline wrappers dispatch to chip operations: `rtw_coex_set_init()`, `rtw_coex_set_ant_switch()`, `rtw_coex_set_gnt_fix()`, `rtw_coex_set_gnt_debug()`, `rtw_coex_set_rfe_type()`, `rtw_coex_set_wl_tx_power()`, and `rtw_coex_set_wl_rx_gain()`. Function prototypes expose C2H response handling, indirect register access, scoreboard writes, lifecycle notifiers, BT/HID/FW debug notifications, delayed-work handlers, periodic status checks, HID list query, and debugfs display.

## Control flow and integration
This header is included by core, firmware, debug, mac80211, and chip-specific files. It creates a two-layer integration model: generic coexistence policy in `coex.c` calls wrappers, and chip files provide the hardware-specific details through `struct rtw_chip_ops`. External driver code calls the notifiers when mac80211 or firmware state changes; `coex.c` converts those events into table/TDMA/antenna decisions.

## State and persistence behavior
The header itself is stateless, but its enums are persisted in runtime fields inside `struct rtw_coex_stat` and `struct rtw_coex_dm` defined in `main.h`. Scoreboard bit definitions are shared with firmware/BT and persist in `REG_WIFI_BT_INFO`. TDMA, table, antenna, GNT, and RF settings persist in device registers or firmware state until overwritten.

## Dependencies and risks
Dependencies include Linux bit operations, endian helpers, mac80211 types, SKB/workqueue/seq_file declarations through included driver headers, and chip ops. The highest risk is semantic drift between enum values and firmware/chip table expectations. Some inline wrappers assume the corresponding chip op exists, while `rtw_coex_set_ant_switch()` explicitly allows NULL; chip operation tables must be complete for chips that enable BT coexistence.

## Test signals
Compile coverage should include debugfs enabled and disabled, coexistence-capable and Wi-Fi-only chips, and all transport types. Runtime signals include correct calls from scan/connect/media/LPS/IPS paths, valid BT info decoding, debugfs `coex_info` output, no NULL callback crashes, and stable behavior when `rtw_coex_disabled()` or `rtw_coex_active_query_bt_info()` is exercised on chips such as RTL8821A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.h -->
