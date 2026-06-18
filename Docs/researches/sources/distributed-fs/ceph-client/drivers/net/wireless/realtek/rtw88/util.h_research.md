## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.h

Purpose: utility declarations and inline/macros for rtw88 iteration and 802.11 BSSID extraction.

Important APIs/types: macros wrap atomic mac80211 iterators for active interfaces, stations, and keys: `rtw_iterate_vifs_atomic`, `rtw_iterate_stas_atomic`, `rtw_iterate_keys`, and `rtw_iterate_keys_rcu`. Prototypes expose non-atomic `rtw_iterate_vifs()` and `rtw_iterate_stas()`. `get_hdr_bssid()` chooses addr1 for ToDS, addr2 for FromDS, otherwise addr3.

Control flow and state: `get_hdr_bssid()` is a small frame-control branch used by RX address matching. The iterator macros forward directly into mac80211 and do not add state.

Dependencies and integration: included by RX, WoWLAN, firmware/key paths, and other code needing station/VIF/key iteration. It depends on mac80211 frame helpers and `struct rtw_dev`.

Risks and test signals: incorrect BSSID selection breaks per-VIF RX stat/RSSI updates, especially in AP/client direction cases. Iterator choice matters for locking context. Test with station and AP modes, ToDS/FromDS frames, lockdep, and key iteration during WoWLAN setup.
