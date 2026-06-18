# subset-b-006234 Research

Grouped code research for selected mac80211 utility, VHT, WBRF, WEP/WME/WPA crypto/QoS files and mac802154 configuration/interface support. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/util.c -->
# sources/distributed-fs/ceph-client/net/mac80211/util.c

## Purpose
`util.c` is mac80211's broad shared utility layer. It exports driver-facing helpers for frame timing, queue stop/wake control, interface/station iteration, work scheduling, RSSI and timestamp reporting, TXQ depth, radar notification, and NAN state. It also contains internal helpers for authentication/deauthentication frame construction, probe request IE construction, WMM defaults, hardware restart/resume reconfiguration, HT/VHT/HE/EHT/UHR capability and operation element construction/parsing, channel definition downgrades, P2P NoA tracking, DTIM/short-beacon recalculation, radio-mask/interface-combination checks, and transmit-power-envelope clearing.

## Important APIs, Types, And Functions
Exported helpers include `wiphy_to_ieee80211_hw()`, `ieee80211_generic_frame_duration()`, `ieee80211_rts_duration()`, `ieee80211_ctstoself_duration()`, queue APIs such as `ieee80211_stop_queue()`, `ieee80211_wake_queue()`, `ieee80211_stop_queues()`, `ieee80211_queue_stopped()`, interface/station iterators such as `ieee80211_iterate_interfaces()`, `ieee80211_iterate_active_interfaces_atomic()`, `__ieee80211_iterate_interfaces()`, `ieee80211_iterate_stations_atomic()`, and `__ieee80211_iterate_stations()`, plus `wdev_to_ieee80211_vif()`, `ieee80211_vif_to_wdev()`, `ieee80211_queue_work()`, `ieee80211_queue_delayed_work()`, `ieee80211_ave_rssi()`, `ieee80211_calculate_rx_timestamp()`, `ieee80211_radar_detected()`, `ieee80211_update_p2p_noa()`, `ieee80211_parse_p2p_noa()`, `ieee80211_txq_get_depth()`, and `ieee80211_vif_nan_started()`.

Internally important functions include `__ieee80211_wake_queue()`, `__ieee80211_stop_queue()`, `_ieee80211_wake_txqs()`, `__ieee80211_flush_queues()`, `ieee80211_set_wmm_default()`, `ieee80211_send_auth()`, `ieee80211_send_deauth_disassoc()`, `ieee80211_put_preq_ies_band()`, `ieee80211_build_probe_req()`, `ieee80211_reconfig()`, `ieee80211_handle_reconfig_failure()`, capability builders such as `ieee80211_ie_build_ht_cap()`, `ieee80211_ie_build_vht_cap()`, `ieee80211_put_he_cap()`, `ieee80211_put_eht_cap()`, `ieee80211_put_uhr_cap()`, operation parsers such as `ieee80211_chandef_vht_oper()`, `ieee80211_chandef_he_6ghz_oper()`, and combination helpers such as `ieee80211_check_combinations()`.

## Control Flow
Queue flow centers on `local->queue_stop_reason_lock`. Stop paths increment or set per-queue reason counters and set bits in `queue_stop_reasons`; wake paths decrement counters, clear reason bits, schedule pending TX handling, and wake TXQs immediately or through `wake_txqs_tasklet` depending on the reason. `__ieee80211_flush_queues()` temporarily stops selected queues for flush/drop, purges station TXQs on drop, calls the driver flush operation when present, and wakes queues afterward.

Reconfiguration flow in `ieee80211_reconfig()` is a large ordered restart/resume state machine. It handles WoWLAN resume shortcuts, starts the driver, restores thresholds, LEDs, monitor and ordinary interfaces, channel contexts, hardware config, filters, BSS/link notifications, AP beacons, NAN state, stations, keys, MLO active links, scheduled scans, aggregation cleanup, remain-on-channel work, queued interface work, queue wakeups, station restart notifications, virtual monitor recreation, and PM resume completion. Failure flow clears reconfiguration flags, aborts scan state, tells cfg80211 about scheduled scan end, marks interfaces/channel contexts as absent from the driver, and lets cfg80211 bring interfaces down.

Frame-element flow uses skb tailroom checks before appending IEs. Probe request building splits caller-supplied IEs into standards-defined insertion points around SSID/rates/request, DS params, HT, VHT, HE, EHT, HE 6 GHz, and UHR capability elements. Channel operation parsers derive `cfg80211_chan_def` from HT/VHT/HE/EHT/S1G operation data and validate the final chandef through cfg80211.

## State And Persistence
All state is kernel runtime state: `ieee80211_local`, `ieee80211_sub_if_data`, link data, station data, queue stop counters/bitmaps, pending skbs, workqueues, tasklets, scan state, channel contexts, link BSS config, and per-interface flags. Nothing persists across module/device lifecycle. Some exported helpers mutate shared state: queue reasons, TXQ dirty flags, link conf QoS parameters, RSSI EWMA reads, NoA descriptors, DTIM counters, channel definitions, and reconfiguration flags.

## Dependencies And Integration Points
The file depends on `net/mac80211.h`, `cfg80211`, `driver-ops.h`, `rate.h`, `mesh.h`, `wme.h`, `led.h`, and `wep.h`. It integrates tightly with driver callbacks (`drv_start`, `drv_stop`, `drv_tx`, `drv_flush`, `drv_conf_tx`, `drv_add_interface`, `drv_add_chanctx`, `drv_sta_state`, `drv_reconfig_complete`, NAN callbacks, and BSS/link change notifications), cfg80211 validation/notification APIs, the mac80211 rate-control layer, mesh/IBSS/AP/station code, scan/scheduled-scan code, key reinstallation, LED triggers, DFS/radar handling, and public mac80211 driver exports.

## Risks And Edge Cases
The queue wake path can release and reacquire `queue_stop_reason_lock` through `_ieee80211_wake_txqs()`, so callers must preserve the current convention of calling wake immediately before unlocking. Queue reason refcounts are guarded with WARN-and-reset logic for underflow, but mismatched stop/wake callers can still cause premature queue wake or stuck queues.

`ieee80211_reconfig()` has a large blast radius and many partial rollback paths. Bugs here can leave interfaces marked running but not uploaded to hardware, channel contexts with wrong `driver_present` state, keys tainted, scheduled scans incorrectly reported, or MLO active links restored in the wrong order. Several branches intentionally WARN on impossible interface types rather than recover.

Capability and operation builders/parsers depend on exact skb sizing, endian conversion, frequency/channel mapping, and spec-specific bandwidth encodings. Unsupported 320 MHz or S1G-width combinations usually WARN and downgrade or reject. `ieee80211_ie_len_eht_cap()` contains an unreachable `return 0` after its computed return, a harmless but visible maintenance signal.

## Test Signals
Useful test signals are mac80211 KUnit tests for element parsing/building, cfg80211 chandef validation, simulated driver restart/resume tests, queue stop/wake tracing, DFS CAC/radar event tests, scan IE length assertions, and crypto/WMM TX path tests that exercise helpers called from this file. Runtime tracepoints for queue stop/wake, radar, driver operations, and cfg80211 notifications are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/vht.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/vht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wbrf.c -->
# sources/distributed-fs/ceph-client/net/mac80211/wbrf.c

## Purpose
`wbrf.c` bridges mac80211 channel usage to AMD ACPI WBRF, the Wi-Fi Band Exclusion interface. It detects whether the parent device supports WBRF producer notifications and adds/removes frequency ranges for active WLAN channel definitions.

## Important APIs, Types, And Functions
The public functions are `ieee80211_check_wbrf_support()`, `ieee80211_add_wbrf()`, and `ieee80211_remove_wbrf()`. Internal helpers are `get_chan_freq_boundary()` and `get_ranges_from_chandef()`. Important types are `struct ieee80211_local`, `struct cfg80211_chan_def`, `struct wbrf_ranges_in_out`, and ACPI WBRF record operations `WBRF_RECORD_ADD` and `WBRF_RECORD_REMOVE`.

## Control Flow
Support detection reads `local->hw.wiphy->dev.parent` and sets `local->wbrf_supported` from `acpi_amd_wbrf_supported_producer()`. Add/remove calls return immediately when unsupported, convert the supplied chandef into one or two frequency ranges, and call `acpi_amd_wbrf_add_remove()` on the parent device. `80+80` MHz channel definitions produce two ranges; other widths produce one.

## State And Persistence
The only local state is the boolean `local->wbrf_supported`. The actual exclusion records are external ACPI/platform state managed by the WBRF subsystem and are added or removed by matching calls during channel-use transitions.

## Dependencies And Integration Points
This file depends on `linux/acpi_amd_wbrf.h`, `linux/units.h`, cfg80211 chandef width helpers, and mac80211 local state. It is integrated by channel context/channel switch paths that notify WBRF when WLAN operating ranges become active or inactive.

## Risks And Edge Cases
The code assumes a valid wiphy parent device after support detection; add/remove do not recheck `dev` for NULL. Frequency conversion multiplies MHz to kHz to Hz in `u64`, which is safe for WLAN frequencies but depends on callers passing MHz units. Correct add/remove pairing is essential; leaked WBRF records can leave stale platform exclusion ranges.

## Test Signals
Useful tests/mock traces verify support detection with missing wiphy/parent, 20/40/80/160/320 MHz range boundaries, 80+80 dual ranges, and balanced ACPI add/remove calls during channel assignment and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wbrf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wep.c -->
# sources/distributed-fs/ceph-client/net/mac80211/wep.c

## Purpose
`wep.c` implements mac80211 software WEP encryption/decryption and IV insertion/removal. It supports both full software crypto and hardware-assisted cases where mac80211 only reserves or generates IV space.

## Important APIs, Types, And Functions
Public entry points are `ieee80211_wep_init()`, `ieee80211_wep_encrypt_data()`, `ieee80211_wep_encrypt()`, `ieee80211_wep_decrypt_data()`, `ieee80211_crypto_wep_decrypt()`, and `ieee80211_crypto_wep_encrypt()`. Internal helpers include `ieee80211_wep_weak_iv()`, `ieee80211_wep_get_iv()`, `ieee80211_wep_add_iv()`, `ieee80211_wep_remove_iv()`, `ieee80211_wep_decrypt()`, and `wep_encrypt_skb()`. It uses `struct arc4_ctx`, `struct ieee80211_key`, TX/RX data wrappers, and skb head/tail manipulation.

## Control Flow
Initialization seeds `local->wep_iv` randomly. TX flow sets the Protected bit on all skbs, then either performs full software WEP or inserts IV/IV space for hardware. Software encryption inserts a 4-byte IV after the 802.11 header, skips weak RC4 IVs, appends a 4-byte ICV, builds RC4 key material as IV plus secret key, CRC32s the plaintext, and ARC4-encrypts payload plus ICV.

RX flow only handles data and authentication frames. If hardware did not decrypt, it linearizes the skb, validates the Protected bit and frame length, checks key index, builds the RC4 key from the received IV and key, decrypts payload plus ICV, validates CRC32, trims ICV, and removes IV. If hardware decrypted but did not strip IV/ICV, it removes those fields according to RX flags.

## State And Persistence
State is runtime only. `local->wep_iv` monotonically changes for TX IV generation. `local->wep_tx_ctx` and `local->wep_rx_ctx` are temporary ARC4 contexts zeroed after use. The skb is modified in place by pushing IVs, appending/trimming ICVs, and moving headers.

## Dependencies And Integration Points
The file depends on CRC32, ARC4, random bytes, unaligned access, skb helpers, `ieee80211_i.h`, and key definitions. It integrates with the mac80211 TX/RX crypto handler chain, shared-key authentication frame construction in `util.c`, hardware key flags such as `GENERATE_IV` and `PUT_IV_SPACE`, and RX status flags such as `DECRYPTED`, `IV_STRIPPED`, and `ICV_STRIPPED`.

## Risks And Edge Cases
WEP is cryptographically obsolete; this code is compatibility support. Correct headroom/tailroom is mandatory, with failures causing TX drops. Weak-IV skipping only handles known FMS-style weak IVs and does not make WEP secure. RX removes IV/ICV even when software ICV verification fails, so callers must drop on the returned failure. Hardware flag combinations must match actual driver behavior or IV/ICV fields can be duplicated or left in payload.

## Test Signals
Test signals include known-answer WEP encrypt/decrypt vectors, weak-IV skip behavior, key-index mismatch drops, short frame drops, hardware-decrypted IV/ICV stripping combinations, shared-key auth transaction encryption, and skb headroom/tailroom failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wep.h -->
# sources/distributed-fs/ceph-client/net/mac80211/wep.h

## Purpose
`wep.h` declares the internal mac80211 WEP software crypto interface used by TX/RX handlers and authentication-frame helpers.

## Important APIs, Types, And Functions
It exposes `ieee80211_wep_init()`, raw data helpers `ieee80211_wep_encrypt_data()` and `ieee80211_wep_decrypt_data()`, skb-level `ieee80211_wep_encrypt()`, and handler entry points `ieee80211_crypto_wep_decrypt()` and `ieee80211_crypto_wep_encrypt()`. It includes `ieee80211_i.h` and `key.h`, so callers see `struct ieee80211_local`, `struct ieee80211_key`, `struct ieee80211_rx_data`, and `struct ieee80211_tx_data`.

## Control Flow
The header has no control flow. It separates WEP implementation details in `wep.c` from callers in the broader mac80211 TX/RX and management-frame code.

## State And Persistence
No state is stored in the header. Declared functions operate on runtime mac80211 local/key/TX/RX state and mutate skbs.

## Dependencies And Integration Points
This header is included by `wep.c` and other mac80211 files that need WEP helpers, notably authentication frame construction and TX/RX crypto handler setup. It depends on skb and Linux integer types.

## Risks And Edge Cases
Because the header exposes low-level raw data helpers, callers must pass correctly sized buffers with ICV tailroom and correct RC4 key material. Misuse bypasses skb-level IV/key-index validation.

## Test Signals
Compilation coverage is the primary header-level signal. Functional coverage comes from WEP TX/RX tests and callers using `ieee80211_wep_encrypt()` for shared-key authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wme.c -->
# sources/distributed-fs/ceph-client/net/mac80211/wme.c

## Purpose
`wme.c` maps packets and existing 802.11 frames to WMM/802.11e access categories, downgrades traffic when admission control or reserved TIDs require it, and writes QoS control fields before transmission.

## Important APIs, Types, And Functions
The exported internal table is `ieee802_1d_to_ac[8]`. Public functions are `ieee80211_select_queue_80211()`, `ieee80211_select_queue()`, and `ieee80211_set_qos_hdr()`. Internal helpers include `wme_downgrade_ac()`, `ieee80211_fix_reserved_tid()`, and `ieee80211_downgrade_queue()`. Important state includes `skb->priority`, station WME capability, `sdata->wmm_acm`, managed-mode TSPEC admission state, `sta->reserved_tid`, `sdata->qos_map`, `sdata->noack_map`, and mesh QoS bits.

## Control Flow
For already formed 802.11 frames, `ieee80211_select_queue_80211()` sets a hash, sends non-reorderable or single-queue hardware to queue 0, maps non-data to VO, non-QoS data to BE, extracts TID from QoS control for QoS data, and then runs downgrade logic.

For Ethernet-style payloads, `ieee80211_select_queue()` determines whether QoS applies from mesh/OCB requirements or station WME support. Non-QoS frames force BE priority for WPA/11i MIC correctness. Control-port frames use priority 7. Other frames use `cfg80211_classify8021d()` with an optional QoS map and then admission/reserved-TID downgrade.

`ieee80211_set_qos_hdr()` updates the QoS control field unless the frame was injected. It preserves unrelated QoS bits, writes TID and no-ack policy, sets `IEEE80211_TX_CTL_NO_ACK` for multicast or configured no-ack TIDs, and handles mesh control-present bits.

## State And Persistence
The file mutates only per-packet state (`skb->priority`, QoS control bytes, TX info flags). Persistent policy comes from runtime interface and station fields configured elsewhere.

## Dependencies And Integration Points
It depends on netdevice/skbuff, packet classifier helpers, cfg80211 QoS mapping, mac80211 station/interface state, mesh helpers, and TX handler code that calls queue selection and QoS header setup before encryption and driver transmission.

## Risks And Edge Cases
Admission-control downgrade loops can end at BK when an AP marks all lower ACs as requiring admission, an intentional workaround. Reserved TID remapping is local and must stay aligned with aggregation/session reservation logic. Injected frames preserve existing QoS bytes but still honor no-ack policy, so packet injection tests need to account for changed TX flags. Incorrect priority handling can break TKIP/WPA MIC calculation or reorder-sensitive traffic.

## Test Signals
Useful tests cover 802.1D-to-AC mapping, DSCP/QoS-map classification, control-port priority, WMM ACM downgrade with and without TSPEC admission, reserved TID remapping, mesh QoS byte preservation, injected no-ack handling, and single-queue hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wme.h -->
# sources/distributed-fs/ceph-client/net/mac80211/wme.h

## Purpose
`wme.h` declares mac80211's internal WME queue-selection and QoS-header helpers.

## Important APIs, Types, And Functions
It declares `ieee80211_select_queue_80211()`, `ieee80211_select_queue()`, and `ieee80211_set_qos_hdr()`. The declarations expose dependencies on `struct ieee80211_sub_if_data`, `struct sta_info`, `struct sk_buff`, and `struct ieee80211_hdr`.

## Control Flow
The header contains no executable flow. Its functions are implemented in `wme.c` and called by TX path code after packet classification/frame construction and before final transmission/encryption stages.

## State And Persistence
No state is defined here. The declared helpers mutate skb priority, QoS control bytes, and TX flags at runtime.

## Dependencies And Integration Points
The header includes `ieee80211_i.h` and netdevice definitions, tying it to mac80211 internal TX state. It is included by `util.c` and TX path files that need queue/QoS decisions.

## Risks And Edge Cases
The header-level risk is API misuse: callers must pass an skb containing the expected frame format for either Ethernet-style classification or already formed 802.11 classification.

## Test Signals
Compilation and TX path tests using queue selection are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wpa.c -->
# sources/distributed-fs/ceph-client/net/mac80211/wpa.c

## Purpose
`wpa.c` implements mac80211 software WPA/WPA2/WPA3-era crypto handlers for TKIP Michael MIC, TKIP encryption/decryption, CCMP/GCMP data protection, and BIP AES-CMAC/AES-GMAC management frame protection. It also coordinates with hardware crypto offload by generating IV/MMIE space only when driver key flags require it.

## Important APIs, Types, And Functions
Public handler entry points are `ieee80211_tx_h_michael_mic_add()`, `ieee80211_rx_h_michael_mic_verify()`, `ieee80211_crypto_tkip_encrypt()`, `ieee80211_crypto_tkip_decrypt()`, `ieee80211_crypto_ccmp_encrypt()`, `ieee80211_crypto_ccmp_decrypt()`, `ieee80211_crypto_gcmp_encrypt()`, `ieee80211_crypto_gcmp_decrypt()`, `ieee80211_crypto_aes_cmac_encrypt()`, `ieee80211_crypto_aes_cmac_decrypt()`, `ieee80211_crypto_aes_gmac_encrypt()`, and `ieee80211_crypto_aes_gmac_decrypt()`.

Internal helpers include `tkip_encrypt_skb()`, `ccmp_gcmp_aad()`, `ccmp_special_blocks()`, `ccmp_pn2hdr()`, `ccmp_hdr2pn()`, `gcmp_special_blocks()`, `gcmp_pn2hdr()`, `gcmp_hdr2pn()`, `bip_aad()`, `bip_ipn_set64()`, and `bip_ipn_swap()`. Important state lives in `struct ieee80211_key` cipher unions (`tkip`, `ccmp`, `gcmp`, `aes_cmac`, `aes_gmac`), atomic TX PN counters, RX PN replay windows, skb control blocks, and RX status flags.

## Control Flow
TKIP TX first adds a Michael MIC for data frames when needed, possibly forcing software crypto for injected MIC-failure tests. `tkip_encrypt_skb()` then inserts the TKIP IV, increments TX PN, optionally appends ICV, and either leaves encryption to hardware or calls TKIP software encryption. TKIP RX verifies/decrypts IV/ICV, updates per-security-index IV state, and separately verifies/removes Michael MIC or reports cfg80211 MIC failures.

CCMP/GCMP TX inserts an 8-byte header when software IV/space is needed, increments the atomic PN, writes PN to header format, builds AAD and nonce/special blocks, appends MIC for software crypto, and calls AES-CCM/AES-GCM helpers. RX validates frame type, header length, station presence, PN replay ordering unless hardware already validated it, decrypts/verifies MIC in software when needed, updates RX PN, stores fragment PN, then removes cipher header and MIC.

BIP TX appends MMIE, increments IPN, and computes AES-CMAC or AES-GMAC MIC over masked management header AAD plus frame body/MMIE unless hardware will generate the MMIE. BIP RX validates MMIE shape, checks IPN replay, verifies MIC when hardware did not, updates RX PN, and trims MMIE.

## State And Persistence
State is runtime key state only. TX uses `atomic64_inc_return(&key->conf.tx_pn)` for unique packet numbers. RX maintains per-key replay counters, MIC/ICV error counters, and latest accepted PN/IPN arrays. The skb is modified in place by pushing cipher headers, appending MIC/MMIE/ICV, trimming trailers, and moving 802.11 headers back over removed cipher headers.

## Dependencies And Integration Points
The file depends on TKIP, AES-CCM, AES-CMAC, AES-GMAC, AES-GCM helpers, crypto constant-time comparison, cfg80211 MIC failure reporting, RX drop reason enums, key flags, and mac80211 TX/RX handler sequencing. It integrates with hardware crypto via flags such as `GENERATE_IV`, `PUT_IV_SPACE`, `GENERATE_IV_MGMT`, `PUT_MIC_SPACE`, `GENERATE_MMIC`, `GENERATE_MMIE`, RX flags like `DECRYPTED`, `PN_VALIDATED`, `MIC_STRIPPED`, and `ALLOW_SAME_PN`, and station/link address handling for management frames.

## Risks And Edge Cases
Replay protection is sensitive to byte order and per-queue/security-index selection. Incorrect hardware flags can double-insert or omit IV/MIC/MMIE fields. CCMP/GCMP management frames with unicast addresses can use `rx->link_addrs` for AAD/nonce computation, so MLO/link-address plumbing must be correct. TKIP MIC failure handling intentionally reports through cfg80211 and can trigger countermeasures. Many paths require linear skbs or sufficient headroom/tailroom and drop on allocation/format failures.

## Test Signals
Strong tests include known-answer TKIP/CCMP/GCMP/BIP vectors, PN replay and same-PN exception tests, hardware-offload flag matrix tests, MIC failure injection/reporting, short frame and malformed MMIE drops, management-frame AAD with link addresses, fragment PN storage, and skb headroom/tailroom failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wpa.h -->
# sources/distributed-fs/ceph-client/net/mac80211/wpa.h

## Purpose
`wpa.h` declares the internal mac80211 WPA/TKIP/CCMP/GCMP/BIP TX and RX crypto handler interface implemented by `wpa.c`.

## Important APIs, Types, And Functions
It declares handler functions for Michael MIC, TKIP, CCMP, AES-CMAC BIP, AES-GMAC BIP, and GCMP: `ieee80211_tx_h_michael_mic_add()`, `ieee80211_rx_h_michael_mic_verify()`, `ieee80211_crypto_tkip_encrypt()`, `ieee80211_crypto_tkip_decrypt()`, `ieee80211_crypto_ccmp_encrypt()`, `ieee80211_crypto_ccmp_decrypt()`, `ieee80211_crypto_aes_cmac_encrypt()`, `ieee80211_crypto_aes_cmac_decrypt()`, `ieee80211_crypto_aes_gmac_encrypt()`, `ieee80211_crypto_aes_gmac_decrypt()`, `ieee80211_crypto_gcmp_encrypt()`, and `ieee80211_crypto_gcmp_decrypt()`.

## Control Flow
The header has no control flow. The TX/RX handler pipeline includes these functions depending on selected cipher and frame type.

## State And Persistence
No state is stored in the header. Declared functions operate on runtime `struct ieee80211_tx_data`, `struct ieee80211_rx_data`, keys, stations, and skbs.

## Dependencies And Integration Points
The header includes Linux skb/types and `ieee80211_i.h`. It is consumed by mac80211 crypto/TX/RX orchestration code that selects cipher-specific handlers.

## Risks And Edge Cases
Callers must pass handlers only when `tx->key`/`rx->key` and cipher context are suitable. The `mic_len` arguments for CCMP and AES-CMAC must match the cipher variant or frame parsing/trimming will be wrong.

## Test Signals
Compilation plus cipher-specific TX/RX tests in `wpa.c` consumers provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/wpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/Kconfig -->
# sources/distributed-fs/ceph-client/net/mac802154/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_MAC802154`, the generic IEEE 802.15.4 SoftMAC networking stack for devices that implement only PHY-level behavior.

## Important APIs, Types, And Functions
The symbol is `MAC802154`, a tristate option named "Generic IEEE 802.15.4 Soft Networking Stack (mac802154)". It depends on `IEEE802154` and selects `CRC_CCITT`, `CRYPTO`, `CRYPTO_AUTHENC`, `CRYPTO_CCM`, `CRYPTO_CTR`, and `CRYPTO_AES`.

## Control Flow
Kconfig controls whether the mac802154 object set is built in, built as a module, or omitted. There is no runtime control flow in this file.

## State And Persistence
The selected config persists in the kernel build configuration. Runtime state is created by the compiled mac802154 module/files.

## Dependencies And Integration Points
The selected crypto dependencies support link-layer security implementation in `llsec.c` and related cfg/iface hooks. The `IEEE802154` dependency ensures the common WPAN/cfg802154 infrastructure exists.

## Risks And Edge Cases
The help text explicitly warns that the implementation is not certified or feature complete. Disabling required crypto selects would break LLSEC build/runtime behavior, so dependency changes require full build coverage.

## Test Signals
Build matrix coverage should include `MAC802154=y`, `MAC802154=m`, and disabled, with IEEE802154 enabled. Module load/unload and LLSEC crypto availability are useful integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/Makefile -->
# sources/distributed-fs/ceph-client/net/mac802154/Makefile

## Purpose
The Makefile builds the mac802154 composite object when `CONFIG_MAC802154` is enabled.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MAC802154) += mac802154.o` gates the module/built-in object. `mac802154-objs` lists `main.o`, `rx.o`, `tx.o`, `mac_cmd.o`, `mib.o`, `iface.o`, `llsec.o`, `util.o`, `cfg.o`, `scan.o`, and `trace.o`. `CFLAGS_trace.o := -I$(src)` supplies trace include path handling.

## Control Flow
There is no runtime control flow. Kbuild aggregates the listed objects into `mac802154.o`.

## State And Persistence
Build output depends on the kernel configuration and object list. No runtime state is defined here.

## Dependencies And Integration Points
The object list ties together registration (`main.o`), RX/TX, MAC commands, MIB, interface creation, LLSEC, cfg802154 ops, scanning, and tracepoints into one module.

## Risks And Edge Cases
Missing a new source file from `mac802154-objs` can compile cleanly only if no references require it, leaving features absent. Trace include path changes can break trace event generation.

## Test Signals
Build tests with `CONFIG_MAC802154=m/y` and tracepoint generation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/cfg.c -->
# sources/distributed-fs/ceph-client/net/mac802154/cfg.c

## Purpose
`cfg.c` implements the `cfg802154_ops` bridge between nl802154/cfg802154 user requests and mac802154 internals. It handles virtual interface creation/removal, suspend/resume, PHY settings, per-interface MAC parameters, scans, beaconing, association/disassociation, and optional experimental LLSEC table operations.

## Important APIs, Types, And Functions
The exported object is `mac802154_config_ops`. Important functions include `ieee802154_add_iface()`, `ieee802154_del_iface()`, `ieee802154_set_channel()`, `ieee802154_set_cca_mode()`, `ieee802154_set_cca_ed_level()`, `ieee802154_set_tx_power()`, `ieee802154_set_pan_id()`, `ieee802154_set_short_addr()`, CSMA/retry/LBT/ACK setters, `mac802154_trigger_scan()`, `mac802154_abort_scan()`, `mac802154_send_beacons()`, `mac802154_stop_beacons()`, `mac802154_associate()`, and `mac802154_disassociate()`. PM hooks are `ieee802154_suspend()` and `ieee802154_resume()` under `CONFIG_PM`.

Experimental LLSEC callbacks wrap `mac802154_llsec_*` functions under `sdata->sec_mtx` for key, device, device-key, security-level, and parameter operations.

## Control Flow
Most setters assert RTNL, compare the requested value to current software state, call a driver operation when hardware-backed, and update software state only on success. Channel changes reject attempts while scanning or beaconing and update PHY duration calculations after a successful driver channel set.

Suspend holds/synchronizes queues and stops hardware if any interface is open, then marks `local->suspended`. Resume restarts hardware with the current filtering level/address filter when needed, releases the queue, and clears suspended state.

Association allocates a parent PAN device, preloads PAN ID filtering for hardware address-filter devices so association responses are not dropped, performs the association exchange, optionally installs the assigned short address in hardware, and commits `wpan_dev` parent/PAN/short-address state. Disassociation handles either parent or child relationships, sends notification frames, removes child list entries, resets local parent/PAN/short address when leaving a parent, and restores max associations.

## State And Persistence
Runtime state lives in `wpan_phy`, `wpan_dev`, `ieee802154_local`, and `ieee802154_sub_if_data`. The file mutates current channel/page, CCA mode, ED threshold, TX power, PAN ID, short address, CSMA/backoff/retry/LBT/ACK defaults, association parent/children lists, and LLSEC tables. None persists beyond device/module lifetime.

## Dependencies And Integration Points
The file depends on cfg802154/nl802154, RTNL locking, `driver-ops.h`, `ieee802154_i.h`, scan/beacon/MAC-command helpers, and LLSEC implementation. It is registered by mac802154 main code through `mac802154_config_ops` and called from nl802154/cfg802154 control paths.

## Risks And Edge Cases
Setters that only update software state do not call driver ops even when hardware could later need the value; startup in `iface.c` must replay supported hardware-backed parameters. Association rollback resets PAN ID on failures but short-address rollback after a later failure depends on the failure point. Disassociation from a parent sends child notifications and deletes list nodes without decrementing `nchildren` in the parent path, which should be checked against cfg802154's child accounting expectations. PM resume returns immediately on `drv_start()` failure before releasing held queues or clearing suspended state.

## Test Signals
Tests should cover RTNL assertions, channel change rejection during scan/beacon, successful and failed driver setter paths, PM suspend/resume with open and closed devices, association rollback at each failure point, disassociation parent/child paths, LLSEC mutex wrapping, and module build with/without `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/cfg.h -->
# sources/distributed-fs/ceph-client/net/mac802154/cfg.h

## Purpose
`cfg.h` declares the mac802154 cfg802154 operations table for registration by the rest of the stack.

## Important APIs, Types, And Functions
It exposes `extern const struct cfg802154_ops mac802154_config_ops;`, implemented in `cfg.c`.

## Control Flow
The header has no control flow. It provides a single symbol declaration.

## State And Persistence
No state is stored here. The declared ops table is static constant data in `cfg.c`.

## Dependencies And Integration Points
Consumers include mac802154 registration code that attaches the ops table to the WPAN PHY/cfg802154 layer.

## Risks And Edge Cases
Header risk is limited to declaration drift if `cfg.c` changes the symbol type or name.

## Test Signals
Compilation and successful WPAN PHY registration through cfg802154 are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/driver-ops.h -->
# sources/distributed-fs/ceph-client/net/mac802154/driver-ops.h

## Purpose
`driver-ops.h` centralizes inline wrappers around low-level `struct ieee802154_ops` driver callbacks. The wrappers provide tracepoints, optional-callback validation, sleep assertions, local state updates, and common start/stop filtering setup.

## Important APIs, Types, And Functions
Wrappers include `drv_xmit_async()`, `drv_xmit_sync()`, address-filter setters `drv_set_pan_id()`, `drv_set_extended_addr()`, `drv_set_short_addr()`, `drv_set_pan_coord()`, `drv_set_promiscuous_mode()`, lifecycle `drv_start()` and `drv_stop()`, and PHY/MAC setters `drv_set_channel()`, `drv_set_tx_power()`, `drv_set_cca_mode()`, `drv_set_lbt_mode()`, `drv_set_cca_ed_level()`, `drv_set_csma_params()`, and `drv_set_max_frame_retries()`.

## Control Flow
Simple wrappers call `might_sleep()`, trace input, call the driver callback, trace return, and return the result. Optional operations return `-EOPNOTSUPP` with `WARN_ON(1)` if absent.

`drv_start()` first programs hardware address filters when `IEEE802154_HW_AFILT` is set, then maps the requested filtering level to hardware promiscuous/frame-field behavior. For lower filtering levels it may enable hardware promiscuous mode and fall back `local->phy->filtering` to `IEEE802154_FILTERING_NONE`; for frame-field filtering it disables promiscuous mode when supported and records `IEEE802154_FILTERING_4_FRAME_FIELDS`. It sets `local->started = true`, executes a memory barrier, then calls `ops->start()`.

`drv_stop()` calls `ops->stop()`, disables/enables the tasklet to synchronize queued tasklet work, executes a barrier, and clears `local->started`.

## State And Persistence
The wrappers mutate runtime `local->phy->filtering` and `local->started`. Address-filter setters pass temporary `struct ieee802154_hw_addr_filt` values to the driver but do not update `local->addr_filt`; callers own that state.

## Dependencies And Integration Points
The header depends on `net/mac802154.h`, RTNL-related context, `ieee802154_i.h`, and `trace.h`. It is used by cfg, iface, TX, scan, beacon, and association code to call hardware drivers consistently.

## Risks And Edge Cases
`drv_start()` sets `local->started = true` before `ops->start()` returns; if the driver fails, callers receive an error but `started` remains true unless higher-level rollback corrects behavior. Filtering fallback is intentionally conservative but may not match hardware that can support richer filtering than the current generic mapping. Wrappers WARN when optional ops are missing, so feature probes must avoid calling unsupported operations in normal control flow.

## Test Signals
Tracepoint tests, fake-driver callback tests, start failure handling, filtering-level mapping, missing optional ops, and stop/tasklet synchronization are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/driver-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/ieee802154_i.h -->
# sources/distributed-fs/ceph-client/net/mac802154/ieee802154_i.h

## Purpose
`ieee802154_i.h` is the central private header for mac802154. It defines core local/interface state, state bits, inline conversion helpers, queue helper prototypes, MLME/TX/RX/MIB/LLSEC/cfg/scan/beacon/association interfaces, and interface lifecycle declarations.

## Important APIs, Types, And Functions
Important types are `enum ieee802154_ongoing`, `struct ieee802154_local`, `enum ieee802154_sdata_state_bits`, and `struct ieee802154_sub_if_data`. `ieee802154_local` owns the public hardware object, driver ops, address filter, WPAN PHY, open count, interface list/mutex, workqueues, IFS timer, scan/beacon request state, async RX MAC-command/beacon work, association state, started/suspended flags, ongoing bitmap, tasklet, skb queue, synchronous TX state, and TX result.

`ieee802154_sub_if_data` owns list membership, embedded `wpan_dev`, local pointer, netdev pointer, default/required filtering levels, running state bits, cached name, LLSEC mutex, and LLSEC state.

Inline helpers include `hw_to_local()`, `IEEE802154_DEV_TO_SUB_IF()`, `IEEE802154_WPAN_DEV_TO_SUB_IF()`, `ieee802154_sdata_running()`, `ieee802154_get_mac_cmd()`, and ongoing-state checks `mac802154_is_scanning()`, `mac802154_is_beaconing()`, and `mac802154_is_associating()`.

## Control Flow
The header itself only has inline helper flow. `ieee802154_get_mac_cmd()` validates that an skb is a MAC command frame, pulls the MAC command payload, and returns the command ID. Ongoing-state helpers test bits in `local->ongoing`. The rest of the header declares cross-file control paths for RX, TX, queue hold/release, MLME operations, MIB/LLSEC access, scan/beacon workers, association/disassociation handling, and interface add/remove.

## State And Persistence
The structures define all major mac802154 runtime state. There is no persistent storage; state exists while the WPAN PHY, local object, interfaces, and netdevs exist.

## Dependencies And Integration Points
This private header includes Linux interrupt/mutex/hrtimer support, cfg802154, mac802154, nl802154, IEEE802.15.4 netdev definitions, and `llsec.h`. It is included by most mac802154 implementation files and connects the driver-facing, cfg802154-facing, netdev-facing, and MLME/security submodules.

## Risks And Edge Cases
Because this header defines shared private state, field semantics must stay consistent across many files. The interface list is documented as protected by RTNL, `iflist_mtx`, and RCU depending on context; misuse can race netdev removal. `local->ongoing` serializes scan/beacon/association state by bits and must be maintained carefully by workers. `ieee802154_get_mac_cmd()` pulls data from the skb, so callers must account for skb cursor mutation.

## Test Signals
Build coverage across all mac802154 files, lockdep/RCU testing for interface list iteration/removal, queue hold/release tests, scan/beacon/association state-bit tests, and LLSEC concurrent access tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/ieee802154_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/iface.c -->
# sources/distributed-fs/ceph-client/net/mac802154/iface.c

## Purpose
`iface.c` implements mac802154 net_device lifecycle, interface creation/removal, WPAN and monitor netdev operations, MAC address/ioctl handling, hardware startup settings, concurrent-interface checks, IEEE 802.15.4 header creation/parsing, LLSEC parameter synchronization, and netdev rename tracking.

## Important APIs, Types, And Functions
Externally used functions include `mac802154_wpan_update_llsec()`, `ieee802154_if_add()`, `ieee802154_if_remove()`, `ieee802154_remove_interfaces()`, `ieee802154_iface_init()`, and `ieee802154_iface_exit()`. Netdev operations are `mac802154_wpan_open()`, `mac802154_slave_close()`, `ieee802154_subif_start_xmit`, `ieee802154_monitor_start_xmit`, `mac802154_wpan_ioctl()`, and `mac802154_wpan_mac_addr()`. Header operations are `ieee802154_header_create()`, `mac802154_header_create()`, and `mac802154_header_parse()`. Setup helpers include `ieee802154_setup_hw()`, `ieee802154_check_concurrent_iface()`, `ieee802154_if_setup()`, and `ieee802154_setup_sdata()`.

## Control Flow
Interface creation allocates a netdev with `ieee802154_if_setup()`, reserves headroom, allocates a name, chooses ARPHRD type by nl802154 iftype, sets device/net namespace, initializes `sdata` and embedded `wpan_dev`, performs type-specific setup, registers the netdev, and appends it to `local->interfaces` under `iflist_mtx` with RCU list semantics. Removal deletes from the list, synchronizes RCU, and unregisters the netdev.

Open flow checks concurrent running interfaces. Non-monitor interfaces cannot run concurrently with another non-monitor interface, and monitor coexistence requires identical MAC-layer settings when a single PHY setting would be shared. The first open interface replays hardware-backed settings with `ieee802154_setup_hw()` and starts the driver with the interface's required filtering. Close flow aborts scan/beacon activity when active, stops the netdev queue, decrements `open_count`, clears running state, and stops hardware when the last interface closes.

Header creation builds IEEE 802.15.4 frame control, sequence numbers, security fields from LLSEC params and skb control block overrides, source/destination addressing, and validates payload length against maximum payload. The generic netdev header path assumes extended addresses and intra-PAN addressing for datagram sockets. Header parse extracts a long source address when present.

## State And Persistence
Runtime state includes `local->open_count`, `sdata->state`, `sdata->required_filtering`, `local->addr_filt`, `wpan_dev` addressing/default MAC parameters, LLSEC params, netdev address fields, lowpan child address synchronization, and cached `sdata->name`. State exists only while netdevs/local PHY exist.

## Dependencies And Integration Points
The file depends on Linux netdevice APIs, nl802154/cfg802154, IEEE802.15.4 header helpers, `driver-ops.h`, LLSEC, MLME ops, TX entry points from `tx.c`, scan/beacon helpers, RTNL, RCU, and the netdevice notifier chain. It is the primary bridge between user-visible network interfaces and the mac802154 local/driver stack.

## Risks And Edge Cases
`mac802154_wpan_ioctl()` supports a debugging SIOCSIFADDR path and refuses changes while running, but still offers an older ioctl-based address path that can diverge from netlink expectations. `mac802154_wpan_mac_addr()` must keep lowpan device MAC addresses in sync and rejects changes while either WPAN or lowpan is running. `ieee802154_if_remove()` returns early if the global interface list is empty, but it does not explicitly verify the target is present before deletion in non-empty lists. `mac802154_slave_open()` sets the running bit before hardware setup and clears it on failure; first-open driver start failures must not leave `local->started` inconsistent with `driver-ops.h`.

Header creation depends on skb headroom and correct LLSEC parameter state. Security override combinations can reject frames when security is globally disabled or a zero security level is forced. Payload length is checked after pushing the header, so callers see an error after skb mutation.

## Test Signals
Tests should cover interface add/remove for node/coord/monitor, open/close first and last interface, concurrent monitor/non-monitor compatibility, driver setup failure rollback, ioctl and MAC address validation, lowpan address propagation, LLSEC parameter update calls, secure and insecure header creation, payload-too-large errors, header parse on malformed packets, netdev rename notifications, and RCU/list cleanup under unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/iface.c -->
