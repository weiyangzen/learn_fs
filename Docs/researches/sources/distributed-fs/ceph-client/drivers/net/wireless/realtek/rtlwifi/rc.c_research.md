# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.c

## Purpose
Registers lightweight mac80211 rate control `rtl_rc`. Firmware controls actual rates; this code seeds visible rate series, handles low-rate special traffic, sets HT/VHT flags, and starts BA aggregation sessions.

## Important APIs, Types, And Functions
`rtl_rate_control_register()` and `rtl_rate_control_unregister()` expose lifecycle. `rtl_rate_ops` binds `rtl_get_rate()`, `rtl_tx_status()`, allocation/free callbacks, and empty update/init callbacks. `_rtl_rc_get_highest_rix()` chooses rate index; `_rtl_rc_rate_set_series()` fills a series entry; `_rtl_tx_aggr_check()` gates BA start.

## Control Flow
`rtl_get_rate()` chooses rate 0 for special/non-data frames or fills up to four descending attempts. TX status ignores unsuitable frames and starts BA for HT QoS unicast data when TID aggregation is stopped and scan/early-link guards allow it.

## State And Persistence
Per-station `rtl_rate_priv` is allocated and stored in `rtlpriv->rate_priv`. Aggregation state lives in `rtl_sta_info.tids[]`.

## Dependencies And Integration Points
Uses mac80211 rate-control API, station private data, RF type helpers, special-data detection, and aggregation callbacks.

## Risks
Reported rates may not equal firmware-selected rates. VHT paths assume station context. BA start is heuristic and traffic-dependent.

## Test Signals
Register/unregister, rate selection for B/G/A/N/AC and RF chain counts, special DHCP/EAPOL handling, HT/VHT flags, and BA start on sustained QoS data.
