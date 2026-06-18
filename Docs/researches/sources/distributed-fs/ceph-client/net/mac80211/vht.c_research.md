# sources/distributed-fs/ceph-client/net/mac80211/vht.c

## Purpose
`vht.c` handles VHT capability negotiation and runtime bandwidth/NSS updates for mac80211 stations. Despite the filename, some helpers now account for HT, HE, EHT, RX OMI, TDLS wider bandwidth, NAN, and MLO link state.

## Important APIs, Types, And Functions
Key functions are `ieee80211_apply_vhtcap_overrides()`, `ieee80211_vht_cap_ie_to_sta_vht_cap()`, `_ieee80211_sta_cap_rx_bw()`, `ieee80211_sta_cap_chan_bw()`, `ieee80211_sta_rx_bw_to_chan_width()`, `_ieee80211_sta_cur_vht_bw()`, `ieee80211_sta_init_nss()`, `__ieee80211_vht_handle_opmode()`, `ieee80211_process_mu_groups()`, `ieee80211_update_mu_groups()`, `ieee80211_vht_handle_opmode()`, and `ieee80211_get_vht_mask_from_cap()`. Important state is in `struct link_sta_info`, `struct ieee80211_sta_vht_cap`, `struct ieee80211_sta_he_cap`, `struct ieee80211_sta_eht_cap`, `struct sta_opmode_info`, and per-link `struct ieee80211_bss_conf`.

## Control Flow
Association/setup flow parses peer VHT IEs with `ieee80211_vht_cap_ie_to_sta_vht_cap()`. It first requires HT support, local VHT support, and at least one 80 MHz-capable channel when an sband is supplied. It copies peer capability/MCS fields, applies local and user override masks, intersects local and peer MCS/NSS support, rejects all-unsupported RX MCS maps, sets the station's current max bandwidth, updates advertised bandwidth, adjusts max A-MSDU length, and recalculates aggregates.

Runtime opmode flow enters through `ieee80211_vht_handle_opmode()`. `__ieee80211_vht_handle_opmode()` interprets the opmode notification's NSS and bandwidth fields, clamps NSS to `capa_nss`, updates `pub->rx_nss`, `cur_max_bandwidth`, and `pub->bandwidth`, notifies cfg80211 about station opmode changes, and returns rate-control change bits. The wrapper then recalculates minimum chandef and notifies rate control.

MU group flow stores group membership/position in link BSS config only when this vif owns MU-MIMO state and the incoming action frame changes the current data.

## State And Persistence
All state is per-station/per-link runtime state. The file mutates VHT capability structures, `link_sta->cur_max_bandwidth`, `link_sta->pub->bandwidth`, `link_sta->capa_nss`, `link_sta->op_mode_nss`, `link_sta->pub->rx_nss`, aggregate limits, and MU group arrays. It does not persist data beyond the station/link lifecycle.

## Dependencies And Integration Points
The file depends on mac80211 internals in `ieee80211_i.h` and rate-control APIs in `rate.h`. It integrates with station setup, association parsing, TDLS state, NAN special cases, MLO link dereferencing, cfg80211 station opmode notifications, BSS/link change notifications, channel-width helpers, and rate-control updates.

## Risks And Edge Cases
This code is full of standards interop exceptions. It intentionally tolerates APs that clear 40 MHz support while operating at 20 MHz, clamps advertised capabilities according to user masks, works around invalid all-`0xffff` VHT RX MCS maps, and uses a second VHT IE to work around Cisco 9115 max-MPDU reporting. Bandwidth helpers have NAN assertions because NAN requires an explicit chandef. Incorrect RX OMI handling can desynchronize advertised RX capability, TX bandwidth, channel context width, and rate control.

## Test Signals
Test with association fixtures covering local/peer VHT capability intersection, override masks, invalid MCS maps, extended NSS bandwidth, TDLS wider-bandwidth rules, HE/EHT bandwidth precedence, opmode NSS/bandwidth updates, cfg80211 opmode notifications, and MU group action frame processing.
