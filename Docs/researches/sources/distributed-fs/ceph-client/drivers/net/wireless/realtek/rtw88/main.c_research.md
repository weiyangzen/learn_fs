# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.c

## Purpose
`main.c` is the shared core for the Realtek `rtw88` wireless driver. It owns module parameters, supported channel/rate metadata, mac80211 registration, core lifecycle, firmware loading and recovery, station/rate setup, scan transitions, per-port register programming, watchdog work, and glue into PHY, firmware, coexistence, security, regulatory, debugfs, LED, SAR, and transport-specific HCI operations. It is transport-neutral: PCI/USB/SDIO call into this file through `rtw_core_init()`, `rtw_chip_info_setup()`, `rtw_register_hw()`, `rtw_core_start()`, and `rtw_core_stop()`.

## Important APIs, Types, and Functions
- Module parameters: `disable_lps_deep`, `support_bf`, and `debug_mask`; global `rtw_edcca_enabled` is shared with PHY debug behavior.
- Hardware capability metadata: `rtw_channeltable_2g`, `rtw_channeltable_5g`, `rtw_ratetable`, `rtw_band_2ghz`, `rtw_band_5ghz`, interface limits/combinations, and HT/VHT capability initializers.
- Lifecycle APIs: `rtw_core_init()`, `rtw_core_deinit()`, `rtw_chip_info_setup()`, `rtw_power_on()`, `rtw_power_off()`, `rtw_core_start()`, `rtw_core_stop()`, `rtw_register_hw()`, and `rtw_unregister_hw()`.
- Station and rate-control APIs: `rtw_sta_add()`, `rtw_sta_remove()`, `rtw_update_sta_info()`, `rtw_desc_to_bitrate()`, `rtw_set_ampdu_factor()`, and BA work scheduling.
- Channel and scan APIs: `rtw_get_channel_params()`, `rtw_update_channel()`, `rtw_set_channel()`, `rtw_core_scan_start()`, `rtw_core_scan_complete()`, and `rtw_core_fw_scan_notify()`.
- Firmware crash handling: `rtw_fw_recovery()`, `rtw_dump_fw()`, `rtw_dump_reg()`, coredump helpers, and reset iterators for keys, stations, and vifs.
- Port/AP helpers: `rtw_vif_port_config()`, `rtw_core_port_switch()`, `rtw_core_check_sta_active()`, and `rtw_core_enable_beacon()`.

## Control Flow
Probe code in a transport module first allocates `ieee80211_hw` and calls `rtw_core_init()`. Core init constructs lists, work items, queues, timers, mutexes, completions, default receive filter state, statistics EWMAs, and begins asynchronous firmware requests. The transport then sets up resources and calls `rtw_chip_info_setup()`, which reads chip parameters, briefly powers MAC/HCI to download firmware for efuse/hardware feature extraction, parses efuse, validates RFE support, normalizes efuse defaults, initializes board power tables, and loads regulatory power data. `rtw_register_hw()` advertises mac80211 capabilities and bands, initializes regulatory/LED/debugfs integration, and registers with mac80211.

Runtime start enters through `rtw_core_start()`: it powers on through the chip operation, enables the security engine, chooses firmware-supported LPS deep modes, writes RCR, schedules the watchdog, and marks `RTW_FLAG_RUNNING`. `rtw_power_on()` is the detailed bring-up: HCI setup, MAC power-on, firmware wait/download, MAC init/postinit, PHY parameter setup, HCI start, H2C general/PHYDM messages, and Bluetooth coexistence power-on configuration. Stop clears running/firmware flags, drops the mutex while synchronously canceling queued work that may need it, reacquires the mutex, and invokes chip power-off.

The watchdog runs every two seconds while running. It updates traffic counters/EWMAs, toggles busy-traffic state, skips dynamic PHY while scanning, forces LPS exit before PHY/coex work, runs coexistence status queries, executes `rtw_phy_dynamic_mechanism()`, adjusts HCI RX aggregation, iterates vifs for CSI rate and per-vif stats reset, checks software beacon loss, and may enter LPS when PS is enabled and traffic/beacon/AP conditions allow it.

Firmware recovery prepares a coredump buffer, dumps firmware crash TLV and chip-specific segments, submits a device coredump, clears MCU test state, clears security CAM entries, removes station/vif driver state, enters IPS, then asks mac80211 to restart hardware.

## State and Persistence Behavior
Most persistent state is in `struct rtw_dev`: firmware state, efuse, HAL, security CAM, traffic stats, regulatory state, coexistence state, dynamic mechanism state, work items, TX queues, LPS config, flags, hardware ports, MAC IDs, WoW state, and LED/debugfs state. This file mutates those fields under `rtwdev->mutex` for mac80211-visible lifecycle and power paths. Firmware objects persist from async request until `rtw_core_deinit()` releases them. Efuse-derived MAC address, RF paths, NSS, RFE, board options, power tables, and regulatory defaults persist for the device lifetime. Watchdog counters and stats are reset each interval. No filesystem persistence is performed; firmware coredumps are handed to the kernel devcoredump framework.

## Dependencies and Integration Points
`main.c` depends on mac80211/cfg80211, firmware loading, devcoredump, kernel workqueues/timers/completions, and many local modules: `fw`, `ps`, `sec`, `mac`, `coex`, `phy`, `reg`, `efuse`, `tx`, `debug`, `bf`, `sar`, `sdio`, and `led`. It calls transport hooks through `rtw_hci_*` and chip-specific hooks through `rtw_chip_ops`. mac80211 integration is via `rtw_ops`, `ieee80211_register_hw()`, vif/sta iterators, TX status, scan/offload features, TDLS flags, WoWLAN caps, and SAR caps.

## Risks
- Lifecycle ordering is fragile: firmware completion, temporary efuse power-on, HCI setup/start/stop, and MAC power transitions must remain synchronized with transport resources.
- `rtw_core_stop()` deliberately unlocks `rtwdev->mutex` around cancellation; changes in called work items can introduce deadlocks or races.
- Firmware recovery removes software state and enters IPS before `ieee80211_restart_hw()`, so missing cleanup can leak MAC IDs, security entries, TXQs, or vif port state.
- Channel/SAR/power-state updates are tightly coupled; invalid channel definitions can trigger warnings or wrong power table selection.
- `rtw_update_sta_info()` contains dense rate-mask logic across CCK/OFDM/HT/VHT, RSSI floors, configured bitrate masks, NSS, STBC, LDPC, and SGI. Regressions show up as poor connectivity rather than immediate crashes.
- The watchdog forces LPS leave before PHY/coex work; mistakes in scan or PS flags can cause power churn, firmware ack timeouts, or missed beacon-loss handling.

## Test Signals
- Probe/register/unregister on supported PCI/USB/SDIO devices without firmware-load leaks or warning splats.
- Association and disassociation with station/AP/TDLS paths, checking MAC ID allocation/release and firmware media status.
- 2.4 GHz and 5 GHz channel changes, including 40/80 MHz primary-center computations and SAR band assignment.
- Firmware crash injection or forced recovery path validating devcoredump creation and mac80211 restart.
- Scan start/complete with random MAC restoration, DIG disable/reset, IPS leave/re-enter, and firmware scan-density completion.
- Traffic watchdog behavior under idle, busy, beacon-loss, and PS-enabled station scenarios.
- Rate-control behavior with HT/VHT, bitrate masks, one-stream mode, STBC/LDPC/SGI capabilities, and RSSI changes.
