# Research: subset-b-004878

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.c

## Purpose
Implements the RTL8192E two-antenna Bluetooth coexistence policy engine for rtlwifi. It receives coexistence lifecycle notifications from the common BT coexistence layer, tracks Bluetooth profile/status information reported by firmware/BT, and applies chip-specific Wi-Fi/BT sharing decisions through H2C commands, BB/RF/MAC register writes, rate masks, aggregation controls, and antenna/spatial-stream configuration. The policy favors 2SS Wi-Fi when coexistence is idle, switches to 1SS or PS-TDMA during active BT profiles, and tunes power, AGC, DAC swing, RF filter, and coexistence tables for SCO/HID/A2DP/PAN combinations.

## Important APIs, Types, And Functions
The exported entry points are `ex_btc8192e2ant_init_hwconfig()`, `ex_btc8192e2ant_init_coex_dm()`, `ex_btc8192e2ant_ips_notify()`, `ex_btc8192e2ant_lps_notify()`, `ex_btc8192e2ant_scan_notify()`, `ex_btc8192e2ant_connect_notify()`, `ex_btc8192e2ant_media_status_notify()`, `ex_btc8192e2ant_special_packet_notify()`, `ex_btc8192e2ant_bt_info_notify()`, `ex_btc8192e2ant_stack_operation_notify()` as declared in the header but not implemented here, `ex_btc8192e2ant_halt_notify()`, `ex_btc8192e2ant_periodical()`, and `ex_btc8192e2ant_display_coex_info()`.

The file owns static singleton state `glcoex_dm_8192e_2ant`/`coex_dm` and `glcoex_sta_8192e_2ant`/`coex_sta`. Decision helpers include `btc8192e2ant_bt_rssi_state()` and `btc8192e2ant_wifi_rssi_state()` for hysteretic RSSI bands, `btc8192e2ant_update_bt_link_info()` for publishing parsed BT profile state to `btcoexist->bt_link_info`, `btc8192e2ant_action_algorithm()` for mapping profile combinations to `BT_8192E_2ANT_COEX_ALGO_*`, and `btc8192e2ant_run_coexist_mechanism()` for the main dispatch.

Hardware/policy writers include `btc8192e2ant_limited_tx()`, `btc8192e2ant_limited_rx()`, `btc8192e2ant_ps_tdma()`, `btc8192e2ant_coex_table_with_type()`, `btc8192e2ant_switch_ss_type()`, `btc8192e2ant_dec_bt_pwr()`, `btc8192e2ant_fw_dac_swing_lvl()`, `btc8192e2ant_ignore_wlan_act()`, `btc8192e2ant_rf_shrink()`, `btc8192e2ant_agc_table()`, and `btc8192e2ant_dac_swing()`. Profile-specific actions include SCO, SCO+PAN, HID, A2DP, A2DP+PAN-HS, PAN-EDR, PAN-HS, PAN+A2DP, PAN+HID, HID+A2DP+PAN, HID+A2DP, inquiry/page, common idle/busy, and all-off paths.

## Control Flow
Initialization enters through `ex_btc8192e2ant_init_hwconfig()`, which calls `btc8192e2ant_init_hwconfig()` to optionally back up RF/register values, configure antenna/PTA/mailbox/counter registers, enable BT clocks, and install the default coexistence table. `ex_btc8192e2ant_init_coex_dm()` then forces coexistence state to a known baseline: PS-TDMA off, FW DAC swing default, no BT power reduction, coexistence table type 0, 2SS Wi-Fi, and software mechanisms disabled.

Runtime information flows primarily through `ex_btc8192e2ant_bt_info_notify()`. It parses C2H BT-info bytes by source, records retry count, BT RSSI, BT-info extension bits, inquiry/page state, and profile flags, resends Wi-Fi channel information if BT reports a reset/lost-info bit, enables auto-reporting when needed, derives `coex_dm->bt_status`, updates busy/limited-DIG flags via `btc_set()`, and immediately runs the coexistence mechanism.

`btc8192e2ant_run_coexist_mechanism()` first exits for manual control or IPS. It selects an algorithm from the BT link profile mix, gives inquiry/page scan priority, handles common states such as Wi-Fi disconnected, BT idle, and Wi-Fi idle with BT busy, then dispatches to a profile-specific action. Each action programs a coordinated bundle of settings: 1SS/2SS selection, TX rate/retry/AMPDU limits, RX aggregation behavior, coexistence table preset, PS-TDMA type, BT power reduction, and optional AGC/RF/DAC changes based on Wi-Fi RSSI, BT RSSI, Wi-Fi bandwidth, and BT retry feedback.

Periodic work in `ex_btc8192e2ant_periodical()` prints version information during early iterations. Without BT auto-reporting it explicitly queries BT info, samples BT counters, and infers BT disable. With auto-reporting it reruns coexistence when Wi-Fi status changes or TDMA auto-adjustment is active. Media-status notifications send 2.4 GHz channel/bandwidth information to BT over H2C 0x66; halt notifies BT to ignore WLAN activity and clears channel information.

## State And Persistence
`struct coex_dm_8192e_2ant` is the desired/applied coexistence state cache. It stores previous/current values for BT power reduction, FW DAC swing, ignore-WLAN-active, PS-TDMA enable/type/parameters, auto-TDMA state, BT auto-report, RF shrink, low-penalty RA, DAC swing, ADC backoff, AGC table, coexistence table registers, limited DIG, backed-up ARFR/retry/AMPDU registers, selected algorithm, BT status, Wi-Fi channel info, spatial-stream type, and current rate/retry limit types. Previous/current fields avoid repeated register/H2C programming unless `FORCE_EXEC` is used.

`struct coex_sta_8192e_2ant` stores observed runtime inputs: profile booleans, IPS/LPS state, priority counters from registers 0x770/0x774, BT RSSI and Wi-Fi RSSI hysteresis states, C2H info history/counters, inquiry/page state, retry count, and BT-info extension. Register backups taken during init are restored when coexistence returns to normal. Hardware state is not persistent across device reset, so init and media notification paths must replay the required PTA, coex table, mailbox, and channel settings.

Several static locals persist between calls: Wi-Fi status-change history, BT disable count, early version-display count, and TDMA adjustment counters. These provide hysteresis but are global to this module instance.

## Dependencies And Integration Points
The file depends on `halbt_precomp.h` for Realtek coexistence types, macros, and helper callbacks. It is integrated through `struct btc_coexist`, which supplies `btc_get`, `btc_set`, register accessors, RF/BT register accessors, `btc_fill_h2c`, debug display hooks, board/stack/BT-link info, manual-control flags, interface type, and auto-report capability. It writes Realtek-specific registers including 0x430/0x434, 0x42a, 0x456, 0x6c0/0x6c4/0x6c8/0x6cc, 0x770/0x774, 0x858, 0x92c/0x930/0x944, RF A 0x1e, and H2C commands 0x60, 0x61, 0x62, 0x63, 0x64, 0x66, and 0x68.

The exported notify functions are called by the rtlwifi coexistence coordinator during power, association, media, special-packet, BT-info, halt, and periodic events. Debug state is exposed through `seq_file` in `ex_btc8192e2ant_display_coex_info()`.

## Risks
The module is a large table-driven state machine encoded as raw register constants and PS-TDMA case numbers. Small changes can disturb firmware/PTA timing or antenna/spatial-stream state. `coex_dm`/`coex_sta` are file-static singletons rather than per-device allocations, which is risky if multiple compatible adapters are active. Some persistent helper state is also static-local and shared.

BT-info parsing copies `length` bytes into fixed `[10]` C2H history arrays without an explicit length clamp in this file, so it depends on upstream message length guarantees. `ex_btc8192e2ant_stack_operation_notify()` is declared in the header but not implemented in this C file, so callers must not require it unless another build unit supplies it. The combination of forced TDMA off during SS switching, explicit `mdelay()` calls, and register backups requires correct sleep/context assumptions from callers. Auto-TDMA relies on BT retry counters and may oscillate if counters are stale or profile classification is wrong.

## Test Signals
Useful validation includes initialization on PCI/USB variants, BT disabled/enabled detection from counters, media connect/disconnect on 2.4 GHz and 5 GHz, BT info for no connection, connected idle, inquiry/page, ACL busy, SCO busy, and mixed profiles. Exercise SCO, HID, A2DP, PAN-EDR, PAN-HS, HID+A2DP, PAN+A2DP, and multi-profile paths while checking H2C 0x60/0x66/0x68 traffic, coex table registers, rate mask updates, RX aggregation controls, MIMO power-save notifications, and restored ARFR/retry/AMPDU registers. Regression signals are firmware mailbox errors, broken association during BT inquiry, audio stutter under A2DP/SCO, Wi-Fi throughput collapse under PAN, and debugfs/seq output showing stale `cur_*` versus hardware register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.h

## Purpose
Defines the RTL8192E two-antenna Bluetooth coexistence contract shared by the chip-specific implementation and the rtlwifi coexistence dispatcher. It names BT-info bit fields, BT-info report sources, BT status states, coexistence algorithm IDs, the two main state structures, and the external notification/display entry points implemented by the companion C file.

## Important APIs, Types, And Functions
The BT-info byte bits identify FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection state. `BTC_RSSI_COEX_THRESH_TOL_8192E_2ANT` provides the hysteresis tolerance used by RSSI state helpers.

`enum bt_info_src_8192e_2ant` identifies reports from Wi-Fi firmware, BT response, and BT active/auto report. `enum bt_8192e_2ant_bt_status` normalizes parsed BT info into non-connected idle, connected idle, inquiry/page, ACL busy, SCO busy, ACL+SCO busy, or max/undefined. `enum bt_8192e_2ant_coex_algo` enumerates the policy branches used by `btc8192e2ant_run_coexist_mechanism()`: SCO, SCO+PAN, HID, A2DP, A2DP+PAN-HS, PAN-EDR, PAN-HS, PAN+A2DP, PAN+HID, HID+A2DP+PAN, and HID+A2DP.

`struct coex_dm_8192e_2ant` is the dynamic mechanism state cache and contains previous/current firmware, software, and hardware coexistence settings plus backups and selected algorithm. `struct coex_sta_8192e_2ant` records observed station/environment state such as BT profile presence, IPS/LPS, counters, RSSI, C2H info, inquiry/page, retry count, and BT-info extensions. The exported `ex_btc8192e2ant_*` prototypes are the integration points for init, power-save notifications, scan/connect/media/special-packet events, BT-info delivery, stack-operation notification, halt, periodic maintenance, and seq-file display.

## Control Flow
The header itself has no control flow, but its declarations mirror the runtime contract. The common coexistence layer calls the `ex_btc8192e2ant_*` functions on lifecycle and wireless events. The implementation uses the enums to convert raw C2H bytes into normalized BT status and algorithm IDs, then records decisions in `coex_dm_8192e_2ant` and observations in `coex_sta_8192e_2ant`.

## State And Persistence
All declared state is plain C data with no locking or ownership annotations in the header. Persistence is by module/global storage in the implementation: previous/current fields survive across notifications and periodic ticks until init, IPS, halt, or reset paths rewrite them. Register backup fields are intended to preserve pre-coexistence Wi-Fi retry/rate/AMPDU settings so normal mode can restore them.

## Dependencies And Integration Points
The header assumes kernel integer/bool types, `BIT*` macros, `struct btc_coexist`, and `struct seq_file` are available from the surrounding rtlwifi coexistence include stack. It is included through `halbt_precomp.h`/chip dispatch code and pairs specifically with `halbtc8192e2ant.c`.

## Risks
The state structures expose many tightly coupled fields without helper accessors, making drift between declarations and implementation easy. The declared `ex_btc8192e2ant_stack_operation_notify()` lacks an implementation in the companion file inspected for this work item, which is a build/API risk if referenced. The C2H history arrays are fixed at 10 bytes and require callers/implementation to bound incoming report length. Because the header does not describe locking, any future multi-adapter or concurrent notification path must handle serialization externally.

## Test Signals
Compile coverage should verify all declared exported functions used by dispatch tables resolve. Runtime debug output should reflect coherent `coex_dm` and `coex_sta` fields after init, BT-info notifications, IPS/LPS transitions, and halt. Boundary tests should include malformed or maximum-length BT-info reports to ensure the fixed history buffers are not overrun by the caller/implementation contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.c

## Purpose
Implements the RTL8723B one-antenna Bluetooth coexistence mechanism. Because Wi-Fi and Bluetooth share one antenna path, this module controls antenna ownership, PTA grants, PS-TDMA timing, Wi-Fi power-save entry/exit, rate/retry constraints, RX aggregation behavior, BT TRx masking, and coexistence table presets in response to Wi-Fi lifecycle events and BT firmware reports. Compared with the 8192E two-antenna module, this file has stronger antenna-path management, AP/multiport handling, scan-special handling, Wi-Fi noise/CCK-lock counters, PnP/RF notifications, and forced LPS/RPWM coordination.

## Important APIs, Types, And Functions
Exported entry points are `ex_btc8723b1ant_power_on_setting()`, `ex_btc8723b1ant_init_hwconfig()`, `ex_btc8723b1ant_init_coex_dm()`, `ex_btc8723b1ant_ips_notify()`, `ex_btc8723b1ant_lps_notify()`, `ex_btc8723b1ant_scan_notify()`, `ex_btc8723b1ant_connect_notify()`, `ex_btc8723b1ant_media_status_notify()`, `ex_btc8723b1ant_special_packet_notify()`, `ex_btc8723b1ant_bt_info_notify()`, `ex_btc8723b1ant_rf_status_notify()`, `ex_btc8723b1ant_halt_notify()`, `ex_btc8723b1ant_pnp_notify()`, `ex_btc8723b1ant_periodical()`, and `ex_btc8723b1ant_display_coex_info()`.

The main state objects are static `glcoex_dm_8723b_1ant`/`coex_dm` and `glcoex_sta_8723b_1ant`/`coex_sta`. Core hardware helpers are `halbtc8723b1ant_set_ant_path()`, `halbtc8723b1ant_ps_tdma()`, `halbtc8723b1ant_set_fw_ps_tdma()`, `halbtc8723b1ant_power_save_state()`, `halbtc8723b1ant_lps_rpwm()`, `halbtc8723b1ant_coex_table_with_type()`, `halbtc8723b1ant_limited_tx()`, `halbtc8723b1ant_limited_rx()`, `halbtc8723b1ant_low_penalty_ra()`, `halbtc8723b1ant_ignore_wlan_act()`, and `halbtc8723b1ant_bt_auto_report()`.

Decision/action helpers include `halbtc8723b1ant_run_coexist_mechanism()`, `halbtc8723b1ant_action_wifi_connected()`, `halbtc8723b1ant_action_wifi_connected_bt_acl_busy()`, `btc8723b1ant_tdma_dur_adj_for_acl()`, `halbtc8723b1ant_action_bt_inquiry()`, `btc8723b1ant_action_wifi_not_conn()`, scan/association/special-packet action variants, `halbtc8723b1ant_action_wifi_multiport()`, `halbtc8723b1ant_action_bt_whck_test()`, `halbtc8723b1ant_action_hs()`, and `halbtc8723b1ant_action_wifi_only()`. Monitoring helpers sample BT priority counters and Wi-Fi CRC counters to infer disabled BT, CCK lock/noisy conditions, profile misclassification, and scan/AP-density inputs.

## Control Flow
`ex_btc8723b1ant_power_on_setting()` runs very early, stops coexistence DM, enables BB access, sets GNT_BT high and WLAN_ACT low, chooses S0/S1 antenna side from interface/efuse information, records antenna position in board info, and writes local registers for firmware visibility. `ex_btc8723b1ant_init_hwconfig()` later enables TBTT/counter statistics, disables PS-TDMA, configures the antenna path for Wi-Fi-only or shared operation, installs the default PTA table, logs key antenna registers, and clears `stop_coex_dm`.

`ex_btc8723b1ant_init_coex_dm()` re-enables coexistence, clears software mechanism state, resets pop-event counters, and queries BT info. BT info reports enter `ex_btc8723b1ant_bt_info_notify()`, which records raw C2H data, detects WHCK test mode, parses retry count, remote-name request, BT RSSI, extension bits, A2DP bitpool, BT TRx mask, and profile bits, repairs BT RF TRx mask registers when needed, resends Wi-Fi channel data after BT reset, enables auto reporting, infers missing HID/PAN profile flags from high/low priority counters, computes `coex_dm->bt_status`, sets BT busy state, and runs the coexistence mechanism.

The main mechanism exits for manual control, stopped DM, IPS, and WHCK test. It marks scans as needing more devices when BT is busy, handles multiport/P2P-GO as a special Miracast-plus-BT case, applies TX/RX limitations and low-penalty RA when BT and Wi-Fi are both active, gives BT inquiry/page and HS mode priority, then chooses not-connected, scan/link/roam, connected idle, connected busy, ACL-busy, SCO/HID, A2DP, PAN, and multi-profile actions. Actions set Wi-Fi native or forced LPS state, PS-TDMA case numbers, antenna path, and coexistence table type.

Scan/connect/media/special-packet notifications temporarily mark Wi-Fi as a high-priority task, force PTA antenna setup to avoid missing scan results, query BT info, and dispatch to special scan/association/DHCP/EAPOL/ARP coexistence actions. Media connect backs up ARFR/retry/AMPDU registers and sends BT channel mask H2C 0x66 for 2.4 GHz; disconnect clears ARP count, CCK priority settings, and CCK-lock history. RF-off, halt, IPS-enter, and PnP-sleep paths hand the antenna to BT, force/disable PS-TDMA, restore native power save, set BT ignore-WLAN-active, and stop coexistence DM as needed.

## State And Persistence
`struct coex_dm_8723b_1ant` persists previous/current antenna position, ignore-WLAN-active, PS-TDMA type/parameters, auto-TDMA state, BT auto-report, LPS/RPWM settings, low-penalty RA, coexistence table registers, backed-up ARFR/retry/AMPDU settings, current algorithm/status, Wi-Fi channel info, ARP count, and an error condition byte. Previous/current fields suppress duplicate H2C/register writes.

`struct coex_sta_8723b_1ant` stores BT disabled/link/profile flags, high-priority link inference, abnormal scan/WHCK/remote-name flags, IPS/LPS, special packet period, priority counters, RSSI, BT TX/RX mask, C2H history/counters, scan AP count, CCK lock state, coex table type, forced LPS state, pop-event count, Wi-Fi CRC counters, wrong-profile count, A2DP bitpool, and chip cut version. Static locals in monitor and TDMA-adjust helpers provide hysteresis across periodic calls.

Hardware state spans antenna control registers, local antenna-position registers, PTA/coex table registers, firmware H2C state, Wi-Fi rate/aggregation controls, BT RF registers, and Wi-Fi LPS/RPWM state. Reset, RF-off/on, PnP sleep/wake, IPS leave, and media changes must replay enough state to avoid stale antenna ownership or stale power-save settings.

## Dependencies And Integration Points
The file depends on `halbt_precomp.h`, the common `struct btc_coexist` operations, rtlwifi debug/seq-file infrastructure, board/stack/BT-link info, interface type and antenna-path metadata, Realtek H2C commands, Wi-Fi link status bits, IOT peer identifiers, and Realtek MAC/BB/RF/BT register maps. It uses H2C commands 0x60, 0x61, 0x63, 0x65, 0x66, 0x68, 0x69, and 0x6e, plus registers such as 0x4c, 0x64, 0x67, 0x765, 0x76e, 0x778, 0x790, 0x92c, 0x930, 0x944, 0x948, 0x6c0/0x6c4/0x6c8/0x6cc, 0x430/0x434, 0x42a, 0x456, and Wi-Fi CRC counters around 0xf84-0xfba.

The exported callbacks are used by the rtlwifi BT coexistence dispatcher for power-on, init, IPS/LPS, scan, association, media, DHCP/EAPOL/ARP, BT-info C2H, RF, halt, PnP, periodic maintenance, and debug display.

## Risks
One-antenna coexistence is highly ordering-sensitive: wrong antenna path or GNT_BT/WLAN_ACT state can break either Wi-Fi or BT immediately. The code uses many raw register constants and PS-TDMA magic numbers, so changes require hardware/firmware validation. Several state variables and TDMA counters are file-static/singleton, which is unsafe for multiple simultaneous RTL8723B devices. `ex_btc8723b1ant_bt_info_notify()` copies `length` bytes into fixed 10-byte C2H arrays without a local clamp, depending on upstream bounds.

The PS-TDMA duration adjustment includes threshold ordering bugs in some conditions: checks such as `a2dp_bit_pool >= 35` before `>= 45` make the `>= 45` branch unreachable in those blocks. The code derives missing HID/PAN profiles from counters, which helps broken BT reports but can also misclassify traffic and choose the wrong table/TDMA case. Power-save transitions intentionally turn TDMA off before entering/leaving LPS, so missed notifications can leave forced LPS or stopped DM state stale. There is a duplicate `ex_btc8723b1ant_pnp_notify()` prototype in the header.

## Test Signals
Exercise power-on and init on USB, PCI, and SDIO antenna configurations; Wi-Fi-only init; IPS enter/leave; RF off/on; PnP sleep/wake; halt; and BT disabled detection. Runtime tests should cover BT no-link, connected idle, inquiry/page, WHCK, HS, SCO/HID, A2DP, PAN, HID+A2DP, A2DP+PAN, HID+A2DP+PAN, Wi-Fi connected idle/busy, scans while disconnected/connected, association/4-way, DHCP/EAPOL/ARP, AP mode, P2P GO/multiport, Cisco/Broadcom IOT peers, high AP-count/noisy environments, and CCK-lock behavior. Signals include correct antenna register values, H2C 0x60/0x65/0x66/0x69/0x6e traffic, stable LPS/RPWM state, restored ARFR/retry/AMPDU settings, seq-file display consistency, and no Wi-Fi scan loss or BT audio/HID stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.h

## Purpose
Defines the RTL8723B one-antenna Bluetooth coexistence data model and external callback interface. It documents the BT-info bit layout, report sources, normalized BT and Wi-Fi status states, coexistence algorithm IDs, dynamic/station state structures, thresholds, and chip-specific notification functions used by the rtlwifi coexistence dispatcher.

## Important APIs, Types, And Functions
BT-info bit macros identify FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection bits. `BT_INFO_8723B_1ANT_A2DP_BASIC_RATE()` extracts the A2DP basic-rate flag from BT-info extension byte 4. `BTC_RSSI_COEX_THRESH_TOL_8723B_1ANT` defines RSSI hysteresis tolerance, and `BT_8723B_1ANT_WIFI_NOISY_THRESH` is the scan/AP-count threshold used as a noisy-environment signal.

`enum _BT_INFO_SRC_8723B_1ANT` names Wi-Fi firmware, BT response, and BT active/auto report sources. `enum _BT_8723B_1ANT_BT_STATUS` normalizes parsed BT status. `enum _BT_8723B_1ANT_WIFI_STATUS` describes Wi-Fi contexts used by TDMA adjustment and action selection: disconnected idle, disconnected association/auth/scan, connected scan, connected special packet, connected idle, and connected busy. `enum _BT_8723B_1ANT_COEX_ALGO` lists profile-combination algorithms, although the C implementation primarily uses status/action helpers rather than a single exported algorithm dispatch table.

`struct coex_dm_8723b_1ant` stores mechanism state: antenna position, ignore-WLAN-active, PS-TDMA, auto-report, LPS/RPWM, low-penalty RA, coexistence table values, backup rate/retry/AMPDU registers, algorithm/status, Wi-Fi channel info, rate mask, ARP count, and error condition. `struct coex_sta_8723b_1ant` stores observed station/environment inputs including BT disabled/profile flags, profile counts, abnormal/WHCK/inquiry/remote-name/high-priority flags, IPS/LPS, counters, RSSI, C2H history, scan AP count, CCK lock/noise data, CRC counters, A2DP bitpool, and chip cut version.

The external callback prototypes cover power-on setup, hardware init, coex-DM init, IPS/LPS, scan/connect/media/special packet, BT-info, RF status, halt, PnP, periodic maintenance, and seq-file display. The header declares `ex_btc8723b1ant_pnp_notify()` twice with different parameter spelling but identical type.

## Control Flow
The header has no executable control flow. It describes a callback-driven module: the common coexistence layer initializes the chip, sends event notifications, supplies BT-info C2H buffers, and requests periodic maintenance/debug output. The implementation stores observations in `coex_sta_8723b_1ant`, records applied decisions in `coex_dm_8723b_1ant`, and uses the declared enums/macros to select one-antenna coexistence behavior.

## State And Persistence
Both state structs are designed for long-lived coexistence state across periodic ticks and event callbacks. Previous/current fields in `coex_dm_8723b_1ant` are persistence hooks for avoiding duplicate hardware writes, while backup fields preserve Wi-Fi rate/retry/AMPDU settings. `coex_sta_8723b_1ant` accumulates counters and history that influence later decisions, including CCK lock, pop events, wrong-profile inference, scan AP count, and forced LPS state.

## Dependencies And Integration Points
The header requires kernel integer/bool types, `BIT`/`BITn` macros, `struct btc_coexist`, and `struct seq_file` from the surrounding rtlwifi include stack. It is paired with `halbtc8723b1ant.c` and the common Realtek BT coexistence dispatcher, which selects these callbacks for RTL8723B one-antenna hardware.

## Risks
The header exposes large mutable structs with no locking, lifetime, or per-device ownership model, mirroring the implementation's static-singleton approach. Fixed 10-byte BT-info history arrays require strict length discipline from C2H callers. The duplicated PnP prototype is harmless to C but signals maintenance drift. Several enum values and fields are implementation-specific magic numbers, so external code should not infer generic semantics without checking the companion implementation.

## Test Signals
Build tests should ensure all prototypes resolve and duplicate declarations remain type-identical. Runtime tests should confirm state fields shown by `ex_btc8723b1ant_display_coex_info()` match BT-info reports, Wi-Fi events, antenna path decisions, LPS/RPWM state, coex table type, CCK lock, and scan AP count. Fuzz or boundary testing of BT-info lengths is useful because the state structure only reserves 10 bytes per report source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.h -->
