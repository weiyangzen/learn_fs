# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.c

## Purpose
Implements MT7601U MAC-level helpers for MAC address programming, TX/RX rate translation, TX status reporting, protection/TSF/preamble configuration, statistics work, WCID/key programming, RX status construction, and RSSI/beacon monitoring.

## Important APIs, Types, And Functions
Exports `mt7601u_set_macaddr()`, `mt76_mac_tx_rate_val()`, `mt76_mac_wcid_set_rate()`, `mt7601u_mac_fetch_tx_status()`, `mt76_send_tx_status()`, `mt7601u_mac_set_protection()`, `mt7601u_mac_set_short_preamble()`, `mt7601u_mac_config_tsf()`, `mt7601u_mac_work()`, `mt7601u_mac_wcid_setup()`, `mt7601u_mac_set_ampdu_factor()`, `mt76_mac_process_rx()`, `mt76_mac_wcid_set_key()`, and `mt76_mac_shared_key_setup()`.

## Control Flow
TX status reads `MT_TX_STAT_FIFO`, translates rates, fills mac80211 status, and reports no-SKB status under `mac_lock`. RX processing interprets RXWI fields, sets decrypted/stripped flags, leaves PN validation to mac80211 when needed, computes RSSI/rate/band/status, updates beacon/RSSI monitors, and returns MPDU length. Key setup writes WCID key/IV memory and cipher attributes, while shared-key setup writes per-BSS shared key tables. Periodic MAC work accumulates clear-on-read counters and recalculates average AMPDU length.

## State And Persistence
State includes `dev->macaddr`, `dev->stats`, `avg_ampdu_len`, `avg_rssi`, beacon frequency/PHY info, WCID rate/key attributes, hardware key memory, shared key memory, protection registers, TSF/beacon timer state, and RX status fields in SKBs.

## Dependencies And Integration Points
Depends on mac80211 rate/status APIs, register definitions, EEPROM/PHY RSSI helpers, tracepoints, WCID structures, key ciphers, delayed work, and `main.c` callbacks for BSS/key/rate changes.

## Risks
`mt7601u_mac_config_tsf()` computes a new value but does not write it in the enable path in this source, which is a suspicious behavior to validate against surrounding history. Hardware PN validation is intentionally not trusted. Key programming must keep WCID pairwise/shared key attributes synchronized. Clear-on-read stats require periodic accumulation to avoid losing counters.

## Test Signals
Correct RX rates/RSSI/decryption flags, TX status ACK/retry/rate reporting, WPA/WEP/TKIP/CCMP key install/remove, association protection mode changes, AMPDU factor changes with stations, MAC error reset logging, and TSF/beacon timer behavior.
