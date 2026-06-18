# sources/distributed-fs/ceph-client/net/wireless/util.c

## Purpose
`util.c` is cfg80211's shared wireless utility implementation. It provides exported helpers for rate selection, channel/frequency conversion, cipher/key validation, 802.11/802.3 frame conversion, A-MSDU parsing, QoS classification, BSS IE lookup, deferred wireless event processing, interface type changes, bitrate calculation for legacy through UHR modes, P2P IE parsing, operating class conversion, interface-combination validation, station/stat allocation helpers, L2 update frames, VHT NSS derivation, and radio/channel validation.

The file is infrastructure code used by cfg80211 core paths and drivers. It contains both pure conversion helpers and state-mutating helpers that operate on `wiphy`, `wireless_dev`, `cfg80211_registered_device`, `net_device`, and `sk_buff`.

## Important APIs And Functions
Rate and channel helpers include `ieee80211_get_response_rate`, `ieee80211_mandatory_rates`, `ieee80211_channel_to_freq_khz`, `ieee80211_freq_khz_to_channel`, `ieee80211_get_channel_khz`, `ieee80211_set_bitrate_flags`, `cfg80211_calculate_bitrate`, and the static HT/DMG/EDMG/VHT/HE/EHT/UHR/S1G bitrate calculators. These encode 802.11 band-specific channel numbering and MCS-to-rate rules.

Security helpers include `cfg80211_supported_cipher_suite`, `cfg80211_valid_key_idx`, and `cfg80211_validate_key_settings`. They enforce key index bounds, pairwise/group key rules, cipher-specific key lengths, sequence length constraints, Extended Key ID rules, IGTK/BIGTK index ranges, beacon protection capability, IBSS RSN behavior, and whether the wiphy advertises the cipher.

Frame and aggregation helpers include `ieee80211_hdrlen`, `ieee80211_get_hdrlen_from_skb`, `ieee80211_get_mesh_hdrlen`, `ieee80211_get_8023_tunnel_proto`, `ieee80211_strip_8023_mesh_hdr`, `ieee80211_data_to_8023_exthdr`, `ieee80211_is_valid_amsdu`, and `ieee80211_amsdu_to_8023s`. They parse 802.11 frame control, DS bits, mesh address extensions, RFC1042/bridge-tunnel SNAP headers, and A-MSDU subframe boundaries.

Cfg80211 state helpers include `cfg80211_upload_connect_keys`, `cfg80211_process_wdev_events`, `cfg80211_process_rdev_events`, `cfg80211_change_iface`, `cfg80211_validate_beacon_int`, `cfg80211_iter_combinations`, `cfg80211_check_combinations`, `cfg80211_get_radio_idx_by_chan`, `cfg80211_get_station`, `cfg80211_remove_link`, `cfg80211_remove_links`, `cfg80211_remove_virtual_intf`, `cfg80211_get_iftype_ext_capa`, `cfg80211_radio_chandef_valid`, and `cfg80211_wdev_channel_allowed`.

IE and channel-class helpers include `cfg80211_get_p2p_attr`, `ieee80211_ie_split_ric`, `ieee80211_fragment_element`, `ieee80211_operating_class_to_band`, `ieee80211_operating_class_to_chandef`, and `ieee80211_chandef_to_operating_class`.

Other exported support includes `cfg80211_classify8021d`, `ieee80211_bss_get_elem`, `ieee80211_get_ratemask`, `ieee80211_get_num_supported_channels`, `cfg80211_free_nan_func`, `cfg80211_link_sinfo_alloc_tid_stats`, `cfg80211_sinfo_alloc_tid_stats`, `rfc1042_header`, `bridge_tunnel_header`, `cfg80211_send_layer2_update`, `ieee80211_get_vht_max_nss`, and `cfg80211_iftype_allowed`.

## Control Flow
Most pure helpers are table or switch driven. Channel conversion selects by nl80211 band and applies standard channel formulas. Bitrate calculation dispatches from `rate_info.flags` to the matching PHY calculator, validates MCS/GI/RU/NSS/bandwidth combinations with warnings, and returns units compatible with cfg80211 station information.

Frame conversion follows strict bounds-first flow. `ieee80211_data_to_8023_exthdr` rejects non-data frames, computes header length plus offset, validates DS-bit combinations against interface type, derives Ethernet source/destination, strips RFC1042 or bridge-tunnel encapsulation where appropriate, pulls the 802.11 header, and writes/pushes an Ethernet header. `ieee80211_amsdu_to_8023s` iterates subframes, validates subframe lengths and padding, detects A-MSDU aggregation injection patterns on the first subframe, optionally reuses the original skb for the last linear subframe, copies or reuses fragments, strips tunnel headers for non-mesh frames, and purges all generated frames on parse/allocation failure.

Event processing drains `wdev->event_list` under `event_lock`, drops the spinlock while invoking heavyweight cfg80211 handlers, dispatches by event type, frees each event, and relocks for the next item. Interface type changes require the wiphy mutex, reject unsupported conversions, leave the old operating mode, process deferred events, purge MLME registrations, clear per-mode/per-link state, call the driver's `change_virtual_intf`, update 4-address/bridging flags, and adjust running interface counts.

Interface-combination validation computes active interface counts and beacon interval GCD data, considers radio-specific combinations when requested, checks DFS radar width and region, subtracts requested iftypes from combination limits, and invokes a caller-provided iterator for each viable combination. `cfg80211_check_combinations` treats no viable combination as `-EBUSY`.

## State And Persistence Behavior
The file mutates several kernel state holders. `ieee80211_set_bitrate_flags` sets mandatory/ERP flags in supported-band bitrate arrays. `cfg80211_upload_connect_keys` uploads saved connect keys to the driver and then frees sensitive key storage. `cfg80211_process_wdev_events` consumes queued events. `cfg80211_change_iface` clears old `wireless_dev` mode/link state, updates `use_4addr`, bridge restrictions, and interface counters. Link removal clears valid-link bits and zeroes link addresses after stopping AP links and calling driver link deletion.

Most frame helpers mutate skb layout in place or construct new skbs. `ieee80211_strip_8023_mesh_hdr` pulls mesh encapsulation and overwrites the Ethernet header. `ieee80211_data_to_8023_exthdr` pulls 802.11/LLC data and pushes or fills an Ethernet header. `ieee80211_amsdu_to_8023s` consumes the original skb by either reusing it or freeing it after queueing output frames.

There is no disk persistence. Sensitive material is handled in memory; connect keys are freed with `kfree_sensitive`. Trace-visible or skb-visible state must be considered separately by callers.

## Dependencies And Integration Points
`util.c` depends on Linux networking and wireless headers, skb/page fragment APIs, VLAN/MPLS/IP DS field helpers, RCU, wiphy locking, cfg80211 core structures from `core.h`, and driver operation wrappers from `rdev-ops.h`. Exported symbols are available to other wireless modules and drivers.

The file integrates with cfg80211 MLME, scan, IBSS, AP, mesh, NAN, and station-management paths. It also bridges kernel wireless state to generic networking behavior through Ethernet header conversion, skb priority classification, L2 update injection, netdev bridge flags, and station statistics.

## Risks And Edge Cases
Frame parsing is security-sensitive. Offsets, subframe lengths, mesh address extension lengths, and tunnel header checks guard against malformed frames and A-MSDU aggregation attacks. Any future changes to pull/copy order must preserve these bounds checks and failure paths that purge partial output.

Cipher validation is policy-sensitive. Extended Key ID, beacon protection, IGTK/BIGTK indexes, WEP/TKIP legacy behavior, pairwise address requirements, and IBSS RSN exceptions are easy to regress. Unknown ciphers are allowed only after driver support is checked; drivers still must validate their private cipher semantics.

MLO support is partial in some legacy paths. Beacon interval calculations explicitly skip valid-links cases for a feature that is not supported with MLO, while link removal is AP-specific. Tests should cover both single-link and multi-link devices so old assumptions about `links[0]` do not leak into MLO paths.

Bitrate calculators intentionally warn and return zero on invalid combinations. Incorrect MCS/RU/GI/bandwidth tables can affect userspace-visible station rates and WEXT compatibility. Operating-class conversion also has unsupported cases such as 80+80 center frequency ambiguity and 6 GHz 320 MHz channelization.

## Test Signals
Unit-style tests should cover channel/frequency round trips across 2.4, 5, 6, 60, S1G, and LC bands; key validation for each cipher and index mode; header length for management/control/data/QoS/HT-control frames; A-MSDU malformed lengths and aggregation-injection detection; QoS mapping for VLAN, IPv4, IPv6, MPLS, and RFC8325 DSCP exceptions; bitrate calculations for representative HT/VHT/HE/EHT/UHR/S1G cases; and interface-combination acceptance/rejection with beacon GCD and DFS constraints. Runtime signals include successful station lookup through driver ops, correct event queue draining, and correct skb output after 802.11-to-802.3 conversion.
