# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/main.c

## Purpose
Provides the MT7601U mac80211 operation table and callback implementations for start/stop, interface lifetime, channel config, RX filters, BSS changes, station add/remove, scan notifications, key setup, RTS threshold, AMPDU actions, and rate table updates.

## Important APIs, Types, And Functions
The exported object is `const struct ieee80211_ops mt7601u_ops`. Key callbacks are `mt7601u_start()`, `mt7601u_stop()`, `mt7601u_add_interface()`, `mt7601u_remove_interface()`, `mt7601u_config()`, `mt76_configure_filter()`, `mt7601u_bss_info_changed()`, `mt7601u_sta_add()`, `mt7601u_sta_remove()`, `mt7601u_set_key()`, `mt76_ampdu_action()`, `mt76_sta_rate_tbl_update()`, and `mt7601u_set_rts_threshold()`.

## Control Flow
Start enables MAC TX/RX and schedules MAC/calibration work. Stop cancels work and stops the MAC. Interface add programs the device MAC address if changed, reserves a group WCID, and initializes vif private state. Station add allocates a WCID, writes WCID address/attributes, publishes RCU pointer, and updates AMPDU factor; removal reverses it. BSS changes program BSSID, basic rates, TSF, protection, preamble, slot time, and calibration. Key setup selects hardware-supported ciphers, updates WCID and shared key memory, or falls back to software for unsupported ciphers.

## State And Persistence
State includes `wcid_mask`, RCU `dev->wcid[]`, vif group WCID, station WCID, MAC address, RX filter bits, scan state bit, calibration work, BSSID/protection/rate/slot registers, hardware key tables, and per-station aggregation sequence state.

## Dependencies And Integration Points
Depends on mac80211 callbacks, MT7601U MAC/PHY/DMA/TX helpers, WCID register definitions, scan calibration helpers, and cipher/key APIs.

## Risks
The driver supports station mode only, but some comments mention AP-style group WCID assumptions. WCID allocation is local and limited to 119. The RX filter helper inverts mac80211 filter flags into drop bits and must keep `total_flags` consistent. AMPDU actions directly manipulate WCID BA bits and send BARs.

## Test Signals
Station association/disassociation, channel changes, scan start/complete calibration restore, RX filter toggles in monitor/promisc-like modes, WPA/WEP/TKIP/CCMP key install/remove, AMPDU RX/TX start/stop, and rate table updates reflected in TXWI rates.
