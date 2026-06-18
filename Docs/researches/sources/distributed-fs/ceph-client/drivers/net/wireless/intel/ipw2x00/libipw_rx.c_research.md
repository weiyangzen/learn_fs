# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_rx.c

## Purpose
Implements libipw receive-side 802.11 processing. It handles monitor delivery, duplicate drops, optional host decryption, fragment reassembly, MSDU MIC verification, IV/ICV stripping for hardware crypto, 802.11-to-Ethernet decapsulation, scan/beacon/probe parsing, QoS IE parsing, network cache maintenance, and management-frame callback dispatch.

## Important APIs, Types, and Functions
Exported functions are `libipw_rx` and `libipw_rx_mgt`. Important internal helpers include monitor delivery, fragment-cache find/get/invalidate, `libipw_is_eapol_frame`, MPDU/MSDU decrypt wrappers, QoS element readers and converters, `libipw_parse_info_param`, `libipw_handle_assoc_resp`, `libipw_network_init`, `is_same_network`, `update_network`, `is_beacon`, and `libipw_process_probe_response`. Static SNAP headers implement RFC1042 and bridge-tunnel decapsulation.

## Control Flow
`libipw_rx()` receives an SKB containing an on-air 802.11 frame. It validates frame length/header length, updates Wireless Extensions spy stats, routes monitor-mode frames directly as `ETH_P_80211_RAW`, selects a crypto context from the IV key index, drops protected frames without a usable key, drops duplicate sequence-control values, derives Ethernet source/destination from ToDS/FromDS bits, filters non-data/null data subtypes, decrypts protected MPDUs, reassembles fragments in a four-entry cache, verifies MSDU-level crypto such as TKIP MIC, rejects unexpected unencrypted payloads except EAPOL, optionally strips hardware-left IV/ICV/MIC bytes, converts LLC/SNAP to Ethernet-II or 802.3 length form, updates netdev stats, and submits via `netif_rx()`. `libipw_rx_mgt()` dispatches management subtypes to driver callbacks and processes beacons/probe responses into the network cache.

## State and Persistence Behavior
RX mutates `ieee->prev_seq_ctl`, `ieee->frag_cache`, netdev RX/drop stats, `ieee->ieee_stats`, spy data, and crypto replay/MIC state. Management parsing updates or allocates entries from `network_free_list` into `network_list`, preserving `last_associate`, QoS active state, and old parameter count while replacing rates, stats, IEs, channel, capability, and 802.11h metadata. Cache replacement evicts the oldest scanned network when the fixed pool is exhausted.

## Dependencies and Integration Points
Depends on SKB APIs, netdevice stats, Wireless Extensions spy, crypto ops from `libipw_crypto_*`, IEEE 802.11 constants, `libipw_geo` for scan output consumers, and driver callbacks in `struct libipw_device`. ipw2100/ipw2200 feed data and management frames from hardware RX handlers into this file.

## Risks
Fragment reassembly is small and tasklet-assumed; stale or malicious fragments can consume entries until the two-second timeout. Duplicate detection uses one previous sequence-control value for the interface, which is simple and may over-drop in mixed traffic. Information-element parsing accepts malformed AP behavior by breaking instead of failing. Hardware crypto stripping relies on `ieee->sec.encode_alg[keyidx]` matching firmware output. In-place decrypt and decapsulation require strict length checks.

## Test Signals
Plain, WEP, TKIP, and CCMP RX; bad key, replay, ICV, and MIC failures; EAPOL exceptions; fragmented protected and unprotected frames; QoS data; monitor mode; RFC1042 and bridge-tunnel payloads; malformed IEs; scan cache insert/update/evict/age; beacon/probe/association callbacks; spy threshold events; hardware-decrypt IV stripping; and netif_rx drop accounting are key signals.
