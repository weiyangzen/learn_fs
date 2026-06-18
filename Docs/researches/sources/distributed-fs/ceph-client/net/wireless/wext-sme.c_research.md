# sources/distributed-fs/ceph-client/net/wireless/wext-sme.c

Purpose: provides cfg80211 managed-mode compatibility handlers for WEXT station operations: connect, channel/frequency, ESSID, BSSID/AP, generic IE, and MLME deauth/disassoc.

Important APIs/functions: `cfg80211_mgd_wext_connect()` builds a cfg80211 connect request from cached WEXT state. Setter/getters include `cfg80211_mgd_wext_siwfreq/giwfreq()`, `cfg80211_mgd_wext_siwessid/giwessid()`, `cfg80211_mgd_wext_siwap/giwap()`, `cfg80211_wext_siwgenie()`, and `cfg80211_wext_siwmlme()`.

Control flow: setters validate station interface type, translate WEXT values, disconnect an existing connection when changing channel/SSID/BSSID/IE, update `wdev->wext.connect`, and call `cfg80211_connect()` when there is a non-empty SSID and the netdev is running. Connect duplicates cached keys when a default key implies privacy, preserves previous BSSID when valid, sets default background scan period, and transfers the cached IE pointer/length.

State and persistence: WEXT compatibility state lives in `wireless_dev->wext`: SSID, BSSID, IE, cached keys, previous BSSID, default key, and connect parameters. No durable persistence exists beyond the in-memory wireless device. Multi-link connections are rejected for legacy getters.

Dependencies and integration: bridges WEXT handlers into cfg80211/nl80211 station management and uses cfg80211 connect/disconnect APIs, wiphy locking, RCU BSS element access, Ethernet address helpers, and ARPHRD_ETHER validation.

Risks and test signals: correctness depends on keeping WEXT state synchronized with cfg80211 connection state and avoiding misleading events during immediate reconnects. Tests should cover station-only enforcement, disabled channels, NUL-terminated SSIDs, automatic versus fixed BSSID, IE replacement/freeing, connection while netdev down, cached WEP keys, MLO getter rejection, and MLME reason-code disconnects.
