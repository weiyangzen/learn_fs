# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/main.c

## Purpose
This file is the MT7921 mac80211 operation layer. It advertises HE capabilities, starts/stops the device, manages interfaces, keys, station state, channel contexts, scans, remain-on-channel, power-save policy, filters, AP mode, SAR, suspend/resume, IPv6 neighbor solicitation offload, channel switch, and rfkill polling.

## Important APIs, Types, And Functions
The central exported object is `const struct ieee80211_ops mt7921_ops`. Shared exports include `mt7921_set_stream_he_caps()`, `__mt7921_start()`, `mt7921_roc_abort_sync()`, `mt7921_set_channel()`, `mt7921_set_runtime_pm()`, `mt7921_mac_sta_add()`, `mt7921_mac_sta_event()`, `mt7921_mac_sta_remove()`, `mt7921_scan_work()`, and `mt7921_set_tx_sar_pwr()`.

Major callback helpers include `mt7921_start/stop`, `mt7921_add_interface`, `mt7921_set_key`, `mt7921_config`, `mt7921_configure_filter`, `mt7921_bss_info_changed`, `mt7921_start_ap/stop_ap`, `mt7921_ampdu_action`, scan/sched-scan helpers, suspend/resume, decap offload, channel context callbacks, managed prepare/complete TX ROC, CSA work/timers, and `mt7921_rfkill_poll()`.

## Control Flow
Start enables MAC firmware, sets channel domain, programs RX path, applies SAR power, resets counters, schedules watchdog work, controls LEDs on MMIO, and starts rfkill polling if firmware supports RF pin events. Interface add allocates an mt76 vif index, adds a firmware dev context, reserves a WCID, initializes WMM and beacon-filter flags, and sets CSA work/timer. BSS changes update slot timing, beacon filter/power-save, association, ERP/EDCA, beacon offload, RSSI monitor, and power state through MCU helpers.

Station add allocates WCIDs and optional WEP station state. Association events add BSS context for station mode, clear WTBL counters, and push station records. Removal aborts ROC, frees pending TX, removes firmware station/BSS state, clears poll list/RSSI, and updates 6 GHz power type. ROC uses a token, waits for firmware grant, arms a timer, and aborts on cancellation or expiry. Channel switching stores `new_ctx`, arms a CSA timer, and applies the new context in work.

## State And Persistence
State spans vif masks, OMAC masks, per-vif WCIDs, WMM index, CSA timer/work, ROC token/grant/timer, scan event list, PM policy bits, beacon-filter flags, monitor/sniffer mode, antenna/chain masks, SAR power, channel context pointers, and per-station aggregation state. Firmware state includes dev/BSS/STA records, keys, BA sessions, channel context, beacon offload, RX filters, sniffer config, RSSI monitor, ROC, and suspend/offload settings.

## Dependencies And Integration Points
The file is tied to mac80211/cfg80211 callbacks, mt76 core station/key/channel helpers, connac MCU commands, `mcu.c`, `mac.c`, mt792x shared PM/reset helpers, ACPI SAR, IPv6, and transport-specific HIF operations.

## Risks
Many callbacks run under the driver mutex and interact with PM wake/sleep; missing wake protection can race firmware sleep. Key deletion intentionally skips some station-mode reassociation cases, which can leave stale firmware keys if disconnect ordering changes. ROC and CSA timers must be canceled on teardown. Channel context handling stores a single `dev->new_ctx`, so concurrent contexts require care. Monitor mode disables runtime/deep sleep and beacon filtering. Station AID is capped at `MT7921_MAX_AID`.

## Test Signals
Cover station/AP/monitor interface lifetimes, WPA/WEP/IGTK keys, association/disassociation, BA start/stop, hardware scan and sched scan, ROC and managed join offchannel, channel switch, SAR/regulatory updates, suspend/resume with GTK rekey, IPv6 NS offload, antenna changes, rfkill polling, beacon offload, and monitor/sniffer toggling. Firmware logs should show matching DEV/BSS/STA/ROC/BA commands and no stale timers after remove.
