# sources/distributed-fs/ceph-client/net/wireless/chan.c

## Purpose
This file implements cfg80211 channel definition construction, validation, compatibility checks, DFS/CAC state helpers, regulatory beacon checks, and channel usability decisions across legacy, HT/VHT/EHT, 6 GHz, 60 GHz EDMG, and S1G modes.

## Important APIs, types, and functions
Key exports include `cfg80211_chandef_create()`, `nl80211_chan_width_to_mhz()`, `cfg80211_chandef_valid()`, `cfg80211_chandef_primary()`, `cfg80211_chandef_compatible()`, `cfg80211_set_dfs_state()`, `cfg80211_set_cac_state()`, `cfg80211_chandef_dfs_required()`, `cfg80211_chandef_dfs_usable()`, `cfg80211_chandef_dfs_cac_time()`, `cfg80211_chandef_usable()`, `cfg80211_reg_check_beaconing()`, `cfg80211_any_usable_channels()`, and `wdev_chandef()`.

Internal helpers validate puncturing bitmaps for 80/160/320 MHz, strict 6 GHz center frequencies, control-channel placement, EDMG bandwidth/channel combinations, S1G subchannels and primary siblings, DFS permissive P2P GO operation, NO_IR relaxations, and active beaconing interfaces.

## Control flow
Validation starts with structural checks: non-null channel, frequency offset below 1000 kHz, width family compatibility, center frequency rules, channel 14 restrictions, EDMG validity, S1G fields, and puncturing bitmap validity. Usability then overlays wiphy capabilities and channel flags: HT/VHT/EHT capability checks, 6 GHz special handling, 320 MHz EHT iftype data, prohibited flags such as disabled/no-OFDM/no-width, and per-subchannel availability.

DFS flow checks every non-punctured subchannel. `cfg80211_chandef_dfs_required()` returns a bit for the chandef width when AP-like iftypes need CAC. `cfg80211_chandef_dfs_available()` verifies radar channels are already available or usable with DFS offload. Beaconing checks first ensure the chandef is usable, then consider DFS availability and regulatory NO_IR relaxations before returning permission.

## State and persistence
The file mutates per-channel in-memory state: `dfs_state`, `dfs_state_entered`, and `cac_start_time`. It reads live `wiphy->wdev_list` state to decide if interfaces are beaconing or if concurrent DFS/IR relaxations are valid. No durable storage exists.

## Dependencies and integration points
It depends on cfg80211 public structures, regulatory helpers, `rdev_get_channel()`, wiphy feature bits, netdev/wdev mode state, and tracepoints. It feeds nl80211 validation, AP/mesh/IBSS channel setup, radar handling, and monitor-channel operations.

## Risks
Regulatory correctness is the main risk: invalid center frequencies, puncturing masks, DFS transitions, or NO_IR relaxations can permit illegal operation or reject valid channels. Multi-link and multi-radio state increases the chance of stale `wdev` assumptions. S1G, EDMG, and EHT 320 MHz rules are specialized and need targeted tests.

## Test signals
KUnit tests should cover every width, 6 GHz alignment, 80+80 adjacency rejection, puncturing validity, primary channel extraction, chandef compatibility, S1G/EDMG usable checks, DFS required/usable/available states, beacon relaxations, and active-interface subchannel detection.
