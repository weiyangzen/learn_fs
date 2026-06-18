# subset-b-004880 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.c

## Purpose
Implements the RTL8821A two-antenna Bluetooth/Wi-Fi coexistence policy engine. It translates Wi-Fi link state, Bluetooth C2H status bytes, RSSI, traffic counters, power-save state, and profile combinations into register writes, coexistence table selections, firmware H2C commands, PS-TDMA schedules, antenna ownership, and rate/power shaping.

## Important APIs, Types, and Functions
The exported `ex_btc8821a2ant_*` functions are the chip-specific callbacks reached through `halbtcoutsrc.c`: hardware init, firmware preload, coexistence DM init, debug display, IPS/LPS/scan/connect/media/special-packet notifications, BT-info C2H notification, halt, PnP, and periodical maintenance. Static state lives in `coex_dm_8821a_2ant` and `coex_sta_8821a_2ant` from the matching header. Core helpers include `btc8821a2ant_bt_rssi_state()`, `btc8821a2ant_wifi_rssi_state()`, `btc8821a2ant_action_algorithm()`, `btc8821a2ant_run_coexist_mechanism()`, `btc8821a2ant_ps_tdma()`, `btc8821a2ant_tdma_duration_adjust()`, `btc8821a2ant_coex_table_with_type()`, and profile actions for SCO, HID, A2DP, PAN EDR/HS, and profile mixtures.

## Control Flow
Initialization backs up RF register `0x1e`, configures antenna/PTA registers (`0x4c`, `0x974`, `0xcb7`, `0x790`, `0x76e`, `0x778`, `0x40`), writes a default coexistence table, and resets firmware/software mechanisms. Runtime entry points mostly update flags or issue H2C channel information, while `ex_btc8821a2ant_bt_info_notify()` parses BT status bytes, updates profile booleans and BT status, sets shared `bt_info` flags, then calls `btc8821a2ant_run_coexist_mechanism()`. The periodical path either queries BT info when auto reporting is enabled or samples BT/Wi-Fi counters and reruns policy when Wi-Fi state changed or automatic TDMA adjustment is active.

`btc8821a2ant_run_coexist_mechanism()` exits for manual control, applies all-off plus ignore-WLAN-active for 5 GHz, skips under IPS, handles BT inquiry/page and Wi-Fi link-process cases first, then detects multi-port Wi-Fi. Otherwise it selects a coexistence algorithm from the active BT profiles and dispatches to profile-specific action functions. Common idle/non-connected cases are handled before profile actions. Profile actions select coexistence tables, LPS/RPWM behavior, BT power reduction, FW DAC swing, PS-TDMA type, RF register settings, and retry penalty behavior. `btc8821a2ant_tdma_duration_adjust()` uses static counters and BT retry count to widen or shrink Wi-Fi time in the TDMA schedule.

## State and Persistence Behavior
State is module-static and shared across all invocations for this chip path: previous/current coexistence decisions, RSSI hysteresis buckets, BT profile status, BT/Wi-Fi counters, cached C2H buffers, PS-TDMA parameters, and version-display counters. Hardware state persists in device registers and firmware H2C state until changed or reset. `pre_*` and `cur_*` fields suppress repeated writes unless `FORCE_EXEC` is used. IPS enter moves Wi-Fi toward standby/off settings, while IPS leave and PnP wake reinitialize hardware and query BT info. No state is persisted outside driver memory and device registers.

## Dependencies and Integration Points
Depends on `struct btc_coexist` callbacks for register IO, RF/BB access, H2C command submission, power-save control, and state queries. Uses enums and structures from `halbtcoutsrc.h` and `halbtc8821a2ant.h`, RTL debug macros, kernel delay `mdelay()`, and Realtek register conventions. It is selected by `halbtcoutsrc.c` only for RTL8821 hardware with two BTDM antennas, and it reports diagnostics through `seq_file`.

## Risks and Test Signals
Risks include large table-driven magic values with little validation, static global state unsuitable for multiple simultaneous devices, blocking `mdelay(30)` in DAC swing updates, many duplicate branches that may hide missing policy differences, and direct firmware/register dependencies. `btc8821a2ant_action_a2dp()` declares `ap_num` but never reads it before `ap_num >= 10`, making that branch unreachable. `ex_btc8821a2ant_media_status_notify()` also tests an unfilled `ap_num`, so channel-width signaling always follows the `< 10` path. BT info parsing copies up to `length` into a fixed 10-byte per-source buffer with no explicit local bound.

Useful test signals are debugfs/seq output fields for current algorithm, PS-TDMA bytes, coexistence table registers, high/low-priority counters, BT C2H buffers, and Wi-Fi channel H2C data. Functional tests should cover 2.4 GHz versus 5 GHz, IPS/LPS enter/leave, BT inquiry/page, SCO/HID/A2DP/PAN combinations, BT auto-report off/on, multi-port Wi-Fi, high/low Wi-Fi and BT RSSI thresholds, and repeated TDMA adjustment under changing retry counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.h

## Purpose
Defines the RTL8821A two-antenna coexistence contract: BT status bit masks, RSSI thresholds, BT-info sources, coexistence algorithms, dynamic-management state, station/runtime state, and exported notification APIs used by the generic coexistence dispatcher.

## Important APIs, Types, and Functions
Important constants include `BT_INFO_8821A_2ANT_B_*` bit definitions for C2H BT status byte interpretation, `BTC_RSSI_COEX_THRESH_TOL_8821A_2ANT`, and Wi-Fi/BT RSSI thresholds used to shift between two-antenna TDMA and one-antenna-like PS-TDMA behavior. `enum _BT_INFO_SRC_8821A_2ANT` identifies Wi-Fi firmware, BT response, and BT active auto-report sources. `enum _BT_8821A_2ANT_BT_STATUS` normalizes BT idle, connected idle, ACL busy, SCO busy, and mixed states. `enum _BT_8821A_2ANT_COEX_ALGO` enumerates SCO, HID, A2DP, PAN HS/EDR, and profile-mix algorithms.

`struct coex_dm_8821a_2ant` caches the current and previous coexistence decisions: firmware mechanisms, PS-TDMA bytes and adjustment state, BT auto-report state, low-penalty retry, DAC swing, table register values, limited DIG, algorithm, BT status, Wi-Fi channel H2C bytes, and LPS/RPWM values. `struct coex_sta_8821a_2ant` stores observed state: profile booleans, IPS/LPS state, priority counters, BT RSSI, C2H buffers/counters, retry count, BT extension info, Wi-Fi CRC counters, selected coexistence table type, forced LPS flag, and version-display counter. The public declarations are the `ex_btc8821a2ant_*` callbacks consumed by `halbtcoutsrc.c`.

## Control Flow
This header has no runtime flow, but it shapes the flow in `halbtc8821a2ant.c`: BT C2H bits update `coex_sta`, `coex_sta` plus RSSI thresholds choose an algorithm, and `coex_dm` records the programmed mechanism to avoid redundant writes. External notifications all enter through declared `ex_btc8821a2ant_*` functions.

## State and Persistence Behavior
The structures are intended as long-lived driver-private state, but the implementation instantiates them as static globals in the C file. Previous/current pairs in `coex_dm_8821a_2ant` act as a write-coalescing cache. C2H arrays preserve recent BT info per source for diagnostics.

## Dependencies and Integration Points
Depends on `struct btc_coexist`, `struct seq_file`, `u8/u32/bool`, and bit macros supplied by the surrounding Realtek/kernel headers. It is included through the BT coexistence precompiled include path and is tightly coupled to the generic enums in `halbtcoutsrc.h`.

## Risks and Test Signals
The header exposes many numeric algorithm and bit encodings without type-safe wrappers, so C2H parsing or table dispatch can silently drift if firmware encodings change. The fixed 10-byte C2H buffers require callers to bound lengths. Tests should validate bit-to-profile decoding, RSSI threshold hysteresis, each algorithm enum path, and diagnostic output for every stored field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.c

## Purpose
Provides RTL8822B Wi-Fi-only hardware setup for systems without active Bluetooth coexistence control. It configures baseband registers so Wi-Fi owns or selects the proper antenna path and grant signals.

## Important APIs, Types, and Functions
Exports `ex_hal8822b_wifi_only_hw_config()`, `ex_hal8822b_wifi_only_scannotify()`, `ex_hal8822b_wifi_only_switchbandnotify()`, and `hal8822b_wifi_only_switch_antenna()`. All use `struct wifi_only_cfg` and the inline `halwifionly_phy_set_bb_reg()` wrapper from `halbtcoutsrc.h`.

## Control Flow
Hardware configuration writes a fixed register sequence: BB control at `0x4c`, software control at `0xcb4`, antenna mux at `0x974`, `0x1990`, `0xcbc`, debug/grant selection at `0x70`, and grant registers `0x1704`/`0x1700`. Scan and switch-band notifications both delegate to `hal8822b_wifi_only_switch_antenna()`, which writes `0xcbc[9:8]` to select the 5 GHz or 2.4 GHz antenna path.

## State and Persistence Behavior
There is no file-local state. State persists only in programmed BB registers. The behavior is idempotent for repeated notifications with the same band.

## Dependencies and Integration Points
Depends on `halbt_precomp.h`, `struct wifi_only_cfg`, and Realtek BB register access through `rtl_set_bbreg()`. It is intended to be called by the generic Wi-Fi-only path in `halbtcoutsrc.c`/`rtl_btc.c`, although the current generic `exhalbtc_init_hw_config_wifi_only()` and notification wrappers are stubbed in this source set, so integration depends on other build variants or future dispatch wiring.

## Risks and Test Signals
The register sequence is all magic values, so incorrect RFE or board assumptions can break antenna selection. Current upstream glue may not call these functions, making this file dead unless another path dispatches it. Test signals are BB register readback after Wi-Fi-only init, scan and band switch on 2.4/5 GHz, RF throughput by band, and grant signal observation (`gnt_wl=1`, `gnt_bt=0`) on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.h

## Purpose
Declares the RTL8822B Wi-Fi-only coexistence/antenna configuration entry points.

## Important APIs, Types, and Functions
The header declares hardware configuration, scan notification, band-switch notification, and antenna switch helpers for `struct wifi_only_cfg`: `ex_hal8822b_wifi_only_hw_config()`, `ex_hal8822b_wifi_only_scannotify()`, `ex_hal8822b_wifi_only_switchbandnotify()`, and `hal8822b_wifi_only_switch_antenna()`.

## Control Flow
This header has no executable flow. It lets a Wi-Fi-only dispatcher initialize RTL8822B hardware and call the same antenna-switch helper for scan and band-change events.

## State and Persistence Behavior
No state is declared here. Persistent effects are BB register writes performed by the C implementation.

## Dependencies and Integration Points
Depends on `struct wifi_only_cfg` and `u8` being visible before inclusion, normally through `halbt_precomp.h`/`halbtcoutsrc.h`. It integrates with the generic Wi-Fi-only context allocated by `rtl_btc_init_variables_wifi_only()`.

## Risks and Test Signals
The header does not indicate valid `is_5g` values beyond `u8`; misuse can silently choose the 2.4 GHz path for zero and 5 GHz for nonzero. Tests should compile-check inclusion ordering and exercise both notification declarations through the generic Wi-Fi-only path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.c

## Purpose
Implements the generic Realtek BT coexistence glue layer. It binds a `btc_coexist` context to `rtl_priv`, exposes hardware/register/H2C callbacks to chip-specific coexistence modules, translates rtlwifi/mac80211 state into `BTC_GET_*` results, applies `BTC_SET_*` side effects, and dispatches lifecycle notifications to the correct chip/antenna implementation.

## Important APIs, Types, and Functions
Key helpers are `halbtc_get()` and `halbtc_set()`, the callback table initializers `exhalbtc_initlize_variables()` and `exhalbtc_initlize_variables_wifi_only()`, adapter binding `exhalbtc_bind_bt_coex_withadapter()`, and notification wrappers `exhalbtc_*_notify()`. Register access callbacks include byte/word/dword MMIO, BB/RF access, local register writes, H2C fill, BT mailbox operations, BT register set/get placeholders, and BT MP query helpers for firmware version, AFH map, BLE scan data, supported features, and forbidden slots.

## Control Flow
`rtl_btc.c` allocates a coexistence context, calls `exhalbtc_initlize_variables()`, then binds it to the adapter. Binding derives chip interface, BT chip type, antenna count, antenna position, single-antenna path, package type, RFE type, and defaults. Later wrappers check availability and manual-control state, normalize rtlwifi events into BTC notification enums, temporarily leave low power when needed, dispatch by hardware type and antenna count, and restore low-power behavior.

The `halbtc_get()` switch reads current Wi-Fi connection, scan, link, roam, 4-way, band, AP mode, encryption, B mode, RSSI, bandwidth, traffic direction, firmware version, link status, BT patch/features, IQK counters, channel, AP count, and LPS mode. `halbtc_set()` mutates shared BT/coexistence state and triggers actions such as LPS enter/leave, aggregation update, low-power disable, and RA mask update. BT MP operations send H2C command `0x67` and optionally wait for `bt_mp_comp`, which is completed by `rtl_btc_btmpinfo_notify()`.

## State and Persistence Behavior
State is kept in `struct btc_coexist`: bind flag, adapter pointer, board info, BT info, stack info, link info, manual/initialized flags, statistics counters, last power-mode command, completion object, and callback function pointers. Wi-Fi-only mode uses `struct wifi_only_cfg`. Register and firmware writes persist in hardware. Aggregation changes are rate-limited by a static `pre_time`, and BT query results are cached in `bt_info`.

## Dependencies and Integration Points
Depends on `rtl_priv`, `rtl_mac`, `rtl_phy`, `rtl_hal`, mac80211 opmodes/link states, Realtek register accessors, firmware H2C ops, LPS helpers, AMPDU update, hardware-type macros, and all chip-specific `ex_btc*` functions. It is the central integration point between `rtl_btc.c` and files such as `halbtc8821a2ant.c`.

## Risks and Test Signals
Several hooks are stubs or TODOs: Wi-Fi-only init/notifications, BT register read, PHYDM version/counters, low-power transitions, P2P link status, and debug statistics/link sections. LPS helpers include comments questioning whether blocking is allowed in the current context. `halbtc_get()` returns false for unsupported queries but many callers may not inspect the return value. BT MP response parsing relies on external completion and fixed command sequencing. Tests should verify every wrapper dispatches to the expected chip path, manual control suppresses notifications, low-power transitions do not sleep in invalid contexts, C2H timeout behavior, aggregation rate limiting, and debug output consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.h

## Purpose
Defines the generic BT coexistence interface shared by rtlwifi front-end code and chip-specific coexistence algorithms. It provides enums, constants, state structures, callback signatures, macros for retrieving contexts, and Wi-Fi-only support types.

## Important APIs, Types, and Functions
The header defines antenna paths, RF paths, coexistence modes, RSSI states and helper macros, Wi-Fi roles/frequencies/bandwidth/traffic direction, notification enums, BT operation opcodes and request numbers, `BTC_GET_*` and `BTC_SET_*` request IDs, debug display IDs, and rate constants. `struct btc_board_info`, `btc_bt_info`, `btc_stack_info`, `btc_statistics`, `btc_bt_link_info`, and especially `struct btc_coexist` form the shared runtime contract. `struct btc_coexist` contains board facts, BT/Wi-Fi state caches, counters, power-mode bytes, a completion for BT MP commands, and callback pointers for MMIO, BB/RF, H2C, debug, get/set, BT register access, and BT information queries. Wi-Fi-only mode is represented by `struct wifi_only_cfg` and `struct wifi_only_haldata`.

## Control Flow
This file is declarative, but it establishes the callback pattern: generic wrappers call chip modules through `exhalbtc_*`; chip modules call back into the generic layer through `btc_get`, `btc_set`, register accessors, and H2C helpers. Wi-Fi-only helpers use `halwifionly_phy_set_bb_reg()` to map a `wifi_only_cfg` adapter back to `rtl_set_bbreg()`.

## State and Persistence Behavior
The header defines all state containers but does not allocate them. `btc_coexist` state is per allocated context, while some chip modules add their own static state. State persists for the lifetime of the rtlwifi adapter context and is freed by `rtl_btc_deinit_variables()`.

## Dependencies and Integration Points
Includes `../wifi.h` and depends on Realtek hardware enums, `rtl_priv`, `seq_file`, `completion`, `enum dm_info_query`, and kernel integer/boolean types. It is included by `rtl_btc.h`, `halbtcoutsrc.c`, and chip-specific coexistence files.

## Risks and Test Signals
The interface is broad and weakly typed: `btc_get`/`btc_set` use `u8` request IDs and `void *` buffers, so type mismatches are compile-time invisible. Many constants mirror firmware encodings and register policy magic values. Tests should include compile coverage for all callback signatures, get/set type correctness, initialization of every function pointer before chip code runs, Wi-Fi-only context setup, and bounds for BT temporary buffers and C2H data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.c

## Purpose
Provides the rtlwifi-facing BT coexistence operations table and thin wrappers around the generic coexistence core. It is the adapter-level API used by the rest of rtlwifi to allocate/deallocate coexistence contexts, notify power/link/scan events, consume C2H BT information, and query coexistence decisions such as limited DIG, LPS/RPWM, AMPDU control, and EDCA behavior.

## Important APIs, Types, and Functions
`rtl_btc_operation` initializes `struct rtl_btc_ops` with all public wrappers. Allocation helpers create either `struct btc_coexist` or `struct wifi_only_cfg` with `kzalloc_obj()`, and deinit frees both possible contexts. Public functions include `rtl_btc_init_variables()`, `rtl_btc_init_variables_wifi_only()`, `rtl_btc_init_hw_config()`, all notification wrappers, `rtl_btc_btinfo_notify()`, `rtl_btc_btmpinfo_notify()`, `rtl_btc_is_limited_dig()`, `rtl_btc_is_disable_edca_turbo()`, `rtl_btc_is_bt_disabled()`, `rtl_btc_get_ampdu_cfg()`, `rtl_btc_display_bt_coex_info()`, `rtl_btc_get_ops_pointer()`, `mgnt_link_status_query()`, and `rtl_get_hwpg_bt_exist()`.

## Control Flow
Initialization allocates the context, initializes generic callbacks through `exhalbtc_initlize_variables()`, and binds the adapter. Hardware config reads efuse BT existence, passes `wifi_only` to `exhalbtc_init_hw_config()`, then initializes coexistence DM. Notifications check context presence and forward to `exhalbtc_*`; IPS leave additionally sends a synthetic scan-start/finish pair to refresh coexistence state. Wi-Fi-only scan and band-switch wrappers derive `is_5g` from current or requested band and call Wi-Fi-only generic wrappers. `rtl_btc_btmpinfo_notify()` parses extended C2H responses from BT firmware, updates cached BT firmware/version/AFH/BLE/device information, and completes the BT MP wait.

## State and Persistence Behavior
This file owns the lifetime of `rtlpriv->btcoexist.btc_context` and `wifi_only_context`. It records last power-mode command bytes in `btc_coexist`, cached BT MP response fields, and EDCA register `0x504` when BT HS uplink/downlink policy is applied. Null contexts return safe defaults.

## Dependencies and Integration Points
Depends on `../wifi.h`, `halbt_precomp.h`, `rtl_btc.h`, Linux module/vmalloc headers, `rtl_priv`, `rtl_btc_ops`, firmware C2H definitions, and generic `exhalbtc_*` functions. It exports `rtl_btc_get_ops_pointer()` for driver registration and module metadata for the rtlwifi core.

## Risks and Test Signals
`rtl_btc_get_ampdu_cfg()` writes `*reject_agg` and `*ctrl_agg_size` in the null-context branch without null checks even though the non-null branch checks each pointer. `rtl_btc_is_disable_edca_turbo()` always returns true and writes EDCA magic values when current value differs. `rtl_btc_is_bt_disabled()` comments that `bt_disabled` appears never initialized or set. BT MP parsing assumes adequate packet length for all sequence cases after only checking `length >= 4`; several cases read bytes beyond four. Tests should cover null-context callers, short C2H packets for every sequence, IPS synthetic scan behavior, EDCA write policy, wifi-only context setup, and module ops table completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.h

## Purpose
Declares the rtlwifi-facing BT coexistence API implemented by `rtl_btc.c`, plus hardware parameter accessors and the link-status query helper.

## Important APIs, Types, and Functions
The header declares lifecycle functions, normal and Wi-Fi-only hardware init, IPS/LPS/scan/connect/media/periodic/halt/BT-info/special-packet/band-switch notifications, coexistence state queries, AMPDU config retrieval, debug display, power-mode recording, and `rtl_btc_get_ops_pointer()`. It also declares efuse/hardware package accessors for BT existence/type/antenna/path/package and `mgnt_link_status_query()`.

## Control Flow
This header has no executable flow. It defines the call surface used by rtlwifi core and chip drivers to reach coexistence behavior, with all implementation routed through `rtl_btc.c` and then `halbtcoutsrc.c`.

## State and Persistence Behavior
No state is declared directly. The functions operate on `struct rtl_priv`, which contains the allocated BT coexistence contexts and cached board information.

## Dependencies and Integration Points
Includes `halbt_precomp.h`, which supplies `struct btc_coexist`, `enum rt_media_status`, `struct rtl_priv`, and related Realtek definitions. The exported ops pointer integrates with the broader rtlwifi driver ops setup.

## Risks and Test Signals
Because this is a broad wrapper API, signature drift between `rtl_btc_ops`, this header, and `rtl_btc.c` would break runtime dispatch. Tests should compile-check every declaration, verify all ops-table members are populated, and exercise both normal coexistence and Wi-Fi-only notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.c

## Purpose
Implements hardware security CAM management for rtlwifi. It resets software security state, programs encryption keys into CAM entries, deletes/invalidates/empties CAM entries, and tracks free pairwise CAM slots for station MAC addresses.

## Important APIs, Types, and Functions
Exports `rtl_cam_reset_sec_info()`, `rtl_cam_add_one_entry()`, `rtl_cam_delete_one_entry()`, `rtl_cam_reset_all_entry()`, `rtl_cam_mark_invalid()`, `rtl_cam_empty_entry()`, `rtl_cam_get_free_entry()`, and `rtl_cam_del_entry()`. The main internal helper is `rtl_cam_program_entry()`, which writes the eight CAM content words for one entry through `WCAMI` and `RWCAM` mapped registers.

## Control Flow
`rtl_cam_add_one_entry()` validates the key ID, builds the CAM config word from valid bit, encryption algorithm, default-key flag, and key ID, then calls `rtl_cam_program_entry()`. Programming iterates CAM content indices from 7 down to 0. Entry 0 packs config and the first two MAC bytes, entry 1 packs the remaining MAC bytes, and entries 2-5 pack the 128-bit key; entries 6-7 are reserved but still written from key offsets implied by the loop. Delete writes zero to the first content word for the key ID. Reset all writes `BIT(31)|BIT(30)` to `RWCAM`. Mark invalid and empty write config-like content based on current pairwise encryption algorithm. Free-entry management scans entries 4 through `TOTAL_CAM_ENTRY - 1`, preserving entries 0-3 for default keys.

## State and Persistence Behavior
Software state lives in `rtlpriv->sec`: encryption algorithms, key buffers/lengths, pairwise key pointer, `hwsec_cam_bitmap`, and `hwsec_cam_sta_addr`. Hardware state persists in the CAM until entries are overwritten, invalidated, emptied, or globally reset. `rtl_cam_get_free_entry()` sets the bitmap and stores the station MAC; `rtl_cam_del_entry()` clears matching bitmap bits and addresses, but hardware removal is expected through separate CAM delete/empty calls.

## Dependencies and Integration Points
Depends on `wifi.h`, `cam.h`, `rtl_priv()`, `rtl_write_dword()`, hardware register maps `WCAMI`/`RWCAM`/`SEC_CAM_*`, Ethernet address helpers, Realtek debug macros, and exported symbols for other rtlwifi modules. It integrates with mac80211 key installation/removal paths in the driver.

## Risks and Test Signals
`rtl_cam_add_one_entry()` only rejects `ul_key_id == TOTAL_CAM_ENTRY`, not greater values. `rtl_cam_delete_one_entry()` ignores `mac_addr` and uses `ul_key_id` as the entry index. `rtl_cam_mark_invalid()` sets `BIT(15)`, which is named `CFG_VALID`, so its semantics are suspicious for an invalidation helper. `rtl_cam_empty_entry()` also leaves bit 15 set in entry 0. Bitmap updates are not locally locked, so callers must serialize key operations. Tests should cover pairwise versus default keys, all encryption algorithms, full CAM allocation, duplicate station lookup, deletion bitmap clearing, hardware readback after reset/empty/delete, and invalid key IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.h

## Purpose
Declares rtlwifi hardware security CAM constants and functions for programming, deleting, resetting, and allocating CAM key entries.

## Important APIs, Types, and Functions
Defines `CAM_CONTENT_COUNT` as eight words per entry, `CFG_VALID`, `PAIRWISE_KEYIDX`, `CAM_PAIRWISE_KEY_POSITION`, and `CAM_CONFIG_NO_USEDK`. Public APIs mirror `cam.c`: reset all entries, add/delete one entry, mark invalid, empty an entry, reset software security info, get a free pairwise entry, and delete a tracked station entry.

## Control Flow
The header has no runtime flow. It exposes the CAM operations to key-management code and other rtlwifi modules.

## State and Persistence Behavior
No state is declared directly. Functions operate on `struct ieee80211_hw` and mutate `rtlpriv->sec` plus hardware CAM registers.

## Dependencies and Integration Points
Depends on kernel/driver definitions for `struct ieee80211_hw`, `u8`, `u32`, and `BIT()`. It is included by `cam.c` and by rtlwifi code that installs or removes encryption keys.

## Risks and Test Signals
The header provides low-level entry-index APIs without range annotations, so misuse can corrupt reserved/default CAM entries. Tests should compile-check all users, enforce index bounds in callers, and verify pairwise entries start at `CAM_PAIRWISE_KEY_POSITION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.h -->
