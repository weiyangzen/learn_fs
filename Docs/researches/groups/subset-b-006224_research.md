<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ethtool.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ethtool.c

## Purpose
Provides mac80211's netdev `ethtool_ops` implementation. It exposes generic driver information through cfg80211, ring parameter get/set hooks through low-level driver operations, and a merged statistics view containing mac80211 station/survey counters plus driver-specific ethtool strings and stats.

## Important APIs, Types, and Functions
The exported integration point is `ieee80211_ethtool_ops`, installed by interface setup code as the default ethtool operations for mac80211 netdevs. `ieee80211_set_ringparam()` and `ieee80211_get_ringparam()` translate ethtool ring requests to `drv_set_ringparam()` and `drv_get_ringparam()` while holding the wiphy lock. `ieee80211_get_sset_count()`, `ieee80211_get_strings()`, and `ieee80211_get_stats()` combine the fixed `ieee80211_gstrings_sta_stats` names with driver-provided `drv_get_et_*()` data. `ieee80211_get_regs_len()` and `ieee80211_get_regs()` advertise no register dump but report the wiphy hardware version.

## Control Flow
Ring changes reject `rx_mini_pending` and `rx_jumbo_pending`, then call the driver with only TX/RX pending counts. Stats collection zeroes the fixed mac80211 section, locks the wiphy, and either resolves the managed BSSID station or iterates all local stations belonging to the netdev. For each station it fills packet/byte/retry/drop counters through `sta_set_sinfo()` and local `sta_info` fields. It then resolves the current channel from the link channel context or monitor channel, scans driver survey indexes with `drv_get_survey()` until the matching channel is found, fills channel/noise/time counters or `-1` sentinels, verifies the fixed length, and appends driver-specific ethtool stats after `STA_STATS_LEN`.

## State and Persistence
The file owns no durable state. It reads persistent mac80211 state from `ieee80211_local`, `ieee80211_sub_if_data`, `sta_info`, channel contexts, monitor configuration, and driver survey state. The fixed string table and `STA_STATS_LEN` define a stable ABI-like ordering for the mac80211 stats prefix.

## Dependencies and Integration Points
Depends on cfg80211 ethtool helpers, mac80211 private structures from `ieee80211_i.h`, station helpers from `sta_info.h`, and driver operation wrappers from `driver-ops.h`. It integrates with `iface.c` via `netdev_set_default_ethtool_ops()`, with low-level hardware drivers through `drv_get_ringparam()`, `drv_set_ringparam()`, `drv_get_et_sset_count()`, `drv_get_et_strings()`, `drv_get_et_stats()`, and `drv_get_survey()`, and with cfg80211 bitrate formatting through `cfg80211_calculate_bitrate()`.

## Risks
The fixed stats string order must stay synchronized with the data indexes, especially the survey tail length. Survey lookup is linear and treats any driver error before the matching channel as no survey data. Signal and noise values are cast into unsigned `u64` slots, so user space must understand ethtool's raw numeric representation. The non-station path repeatedly starts at index zero and accumulates multiple STAs into the same fixed fields, which is intentional but can surprise consumers expecting per-peer rows. Locking expectations depend on all station and driver helper calls being safe under the wiphy guard.

## Test Signals
Useful signals are `ethtool -S` output with the fixed mac80211 names followed by driver-specific names, ring parameter get/set error paths for mini/jumbo rings, station-mode stats against an associated BSSID, AP/IBSS stats aggregated over multiple peer STAs, monitor-only survey reporting, and driver survey failures producing channel zero and `-1` time/noise sentinels. Compile-time signal comes from `WARN_ON(i != STA_STATS_LEN)` catching drift between strings and data population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c -->
# sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c

## Purpose
Implements FILS authenticated encryption for association and reassociation request/response frame bodies. It applies AES-SIV using CMAC-derived synthetic IVs and AES-CTR encryption so FILS-protected IEs after the FILS Session element can be encrypted and authenticated against station/AP addresses and nonces.

## Important APIs, Types, and Functions
The public functions are `fils_encrypt_assoc_req()` and `fils_decrypt_assoc_resp()`, declared in `fils_aead.h` and used by managed MLME association code. Internal crypto helpers are `gf_mulx()` for S2V doubling in GF(2^128), `aes_s2v()` for RFC-style AES-CMAC S2V derivation, `aes_siv_encrypt()` for IV plus ciphertext output, and `aes_siv_decrypt()` for CTR decrypt followed by S2V verification. The functions use `struct ieee80211_mgd_assoc_data` fields `fils_nonces`, `fils_kek`, and `fils_kek_len`.

## Control Flow
Encryption identifies whether the SKB is association or reassociation, locates the FILS Session extension element, and sets the encrypted region to the bytes after that element through the end of the frame. It builds five AAD vectors: STA address, AP/BSSID address, STA nonce, AP nonce, and the management frame region from capability information through the FILS Session element inclusive. It appends one AES block of space to the SKB for the SIV and encrypts in place at `encr`.

Decryption validates the response length, locates the FILS Session element, constructs the mirrored AAD order for response frames, ensures the encrypted data includes at least a synthetic IV block, decrypts the ciphertext into the same buffer, verifies the recomputed S2V against the frame IV, and subtracts the AES block from the caller's frame length. Failures are reported with `-EINVAL`, crypto-layer errors, or allocation errors, with MLME debug logs on malformed/decrypt-failed responses.

## State and Persistence
The file stores no persistent state. Per-call state includes stack arrays of AAD pointers/lengths, temporary CMAC blocks, a duplicated plaintext buffer for encrypt-side CTR overlap safety, and allocated skcipher requests. Persistent inputs live in association state: FILS nonces and KEK remain in `ieee80211_mgd_assoc_data` for the ongoing MLME exchange.

## Dependencies and Integration Points
Depends on kernel crypto APIs for AES-CMAC and `ctr(aes)`, scatterlists, `crypto_xor()`, unaligned big-endian helpers, SKB mutation, cfg80211 element parsing, and MLME debug logging. It integrates with `mlme.c` when transmitting FILS association requests and receiving FILS association responses. The exact AAD ordering follows FILS frame semantics, so callers must pass frames with intact addresses, nonces, FILS Session element, and association capability fields.

## Risks
`aes_siv_decrypt()` computes `iv_c_len - AES_BLOCK_SIZE` before its own length check; current callers check `crypt_len >= AES_BLOCK_SIZE`, so direct future callers must preserve that precondition. Encryption calls `skb_put()` before invoking crypto and does not roll back the length on later crypto failure. In-place encrypt/decrypt depends on the SIV layout and temporary plaintext copy on encryption; changes to buffer ownership could break overlap assumptions. Key length is split in half without local validation beyond crypto setkey failures. Authentication is highly sensitive to AAD ordering, FILS Session length, and nonce layout.

## Test Signals
Strong tests would use FILS association request/response vectors with known KEK/nonces, malformed or missing FILS Session elements, tampered ciphertext/IV/AAD returning `-EINVAL`, short encrypted response bodies, reassociation request offsets, allocation or crypto algorithm failure injection, and verification that successful response decrypt reduces `frame_len` by exactly `AES_BLOCK_SIZE`. Integration signals are successful FILS association in managed mode and MLME debug messages for bad AP responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h -->
# sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h

## Purpose
Declares the FILS AEAD entry points used by mac80211 managed association code to encrypt outgoing FILS association requests and decrypt incoming FILS association responses.

## Important APIs, Types, and Functions
`fils_encrypt_assoc_req(struct sk_buff *skb, struct ieee80211_mgd_assoc_data *assoc_data)` mutates an association request SKB in place by adding AES-SIV overhead and encrypting FILS-protected payload bytes. `fils_decrypt_assoc_resp(struct ieee80211_sub_if_data *sdata, u8 *frame, size_t *frame_len, struct ieee80211_mgd_assoc_data *assoc_data)` decrypts and authenticates a response buffer in place and updates the effective frame length. The header relies on types provided by including translation units, primarily SKB, `ieee80211_sub_if_data`, and `ieee80211_mgd_assoc_data`.

## Control Flow
This header has no control flow beyond include guards. It forms the compile-time contract between FILS crypto implementation and MLME callers.

## State and Persistence
No state is declared here. The stateful contract is that `assoc_data` must already contain the FILS KEK and both nonces for the active association attempt, and callers must treat input frame buffers as mutable.

## Dependencies and Integration Points
Included by `fils_aead.c` and used by managed association code in `mlme.c`. It depends indirectly on `ieee80211_i.h` definitions for the association data structure and on `skbuff` declarations from surrounding includes.

## Risks
The prototypes do not encode key/nonce readiness, minimum frame size, or SKB tailroom expectations; these are runtime obligations. Because the implementation mutates buffers in place, accidental reuse of the original plaintext/ciphertext buffer after failure would be a caller bug. Any future standalone includer may need forward declarations or additional includes if it does not already see the involved struct names.

## Test Signals
Header-level signal is compile coverage from `mlme.c` and `fils_aead.c`. Behavioral signals belong to `fils_aead.c`: successful FILS association, malformed frame rejection, and crypto-authentication failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/he.c -->
# sources/distributed-fs/ceph-client/net/mac80211/he.c

## Purpose
Handles High Efficiency (802.11ax/HE) station capability parsing, HE operation and spatial reuse propagation into BSS configuration, 6 GHz capability updates, and exported OMI bandwidth transition helpers for drivers.

## Important APIs, Types, and Functions
`_ieee80211_he_cap_ie_to_sta_he_cap()` parses peer HE capabilities against a caller-supplied local capability set; `ieee80211_he_cap_ie_to_sta_he_cap()` selects local capabilities for the VIF type and band. `ieee80211_he_op_ie_to_bss_conf()` and `ieee80211_he_spr_ie_to_bss_conf()` copy HE operation and spatial reuse parameters into `vif->bss_conf`. `ieee80211_update_from_he_6ghz_capa()` applies 6 GHz SMPS and MPDU/AMSDU limits to a link station. `ieee80211_prepare_rx_omi_bw()` and `ieee80211_finalize_rx_omi_bw()` are exported GPL APIs used by drivers to stage and finalize peer RX bandwidth changes advertised through OMI.

## Control Flow
HE capability parsing first clears the public station HE capability and exits if the peer IE or local HE support is absent. It validates the variable HE IE length by computing MCS/NSS and PPE sizes, copies the fixed capability element, copies the present MCS/NSS fields, conditionally copies PPE thresholds, marks `has_he`, updates bandwidth, and applies 6 GHz capability if present on 6 GHz. It intersects peer RX/TX MCS maps with local TX/RX support for 80 MHz, then handles 160 MHz and 80+80 MHz only if both sides support each width; otherwise it disables the peer MCS maps and clears unsupported width bits.

HE operation conversion zeroes the BSS HE operation before copying params and NSS set. Spatial reuse conversion zeroes OBSS-PD state, copies control, then walks optional fields according to presence bits. OMI prepare/finalize enforce paired staging: narrowing bandwidth updates TX-facing bandwidth and rate control first, widening updates RX/channel-context first, and finalize applies the complementary side plus channel-context or rate-control recalculation.

## State and Persistence
Persistent state is held in `link_sta->pub->he_cap`, `link_sta->pub->he_6ghz_capa`, `link_sta->pub->bandwidth`, `link_sta->cur_max_bandwidth`, aggregate `max_amsdu_len`, OMI staging fields (`rx_omi_bw_staging`, `rx_omi_bw_tx`, `rx_omi_bw_rx`), and `vif->bss_conf` HE operation/spatial reuse structs. The file itself has no global mutable state.

## Dependencies and Integration Points
Depends on `ieee80211_i.h`, rate-control helpers, cfg80211/nl80211 HE definitions, station aggregate recalculation, channel-context recalculation, tracepoints, and RCU/wiphy dereference helpers. Integrates with managed, mesh, and cfg80211 station update paths that call HE capability parsing; with BSS configuration notification paths that consume `vif->bss_conf.he_oper` and `he_obss_pd`; and with drivers through exported OMI bandwidth APIs.

## Risks
Variable-length HE IE parsing relies on helper size calculations and one indexed byte used for PPE size; malformed lengths must be rejected before copying optional data. MCS intersection direction is asymmetric and easy to regress by swapping own RX/TX against peer TX/RX. OMI helpers require strict prepare/finalize pairing and warn if staging fields diverge; missed finalize can leave rate control or channel context temporarily inconsistent. The 6 GHz SMPS switch has no explicit default assignment outside enumerated values, relying on known field encodings.

## Test Signals
Good tests cover HE IE lengths with and without PPE thresholds, local support absent, 160 and 80+80 capability intersection, 6 GHz max MPDU/SMPS mapping, HE operation reset when IE is absent, SPR optional field combinations, and OMI narrowing/widening sequences that verify rate-control updates and channel-context recalculation order. Runtime signals include changed station bandwidth, `IEEE80211_RC_BW_CHANGED` callbacks, trace API events, and aggregate max AMSDU recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/he.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ht.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ht.c

## Purpose
Implements HT (802.11n) capability negotiation, user capability overrides, block-ack session lifecycle work, DELBA and SMPS action frame handling, and channel-width notification updates for mac80211 stations and links.

## Important APIs, Types, and Functions
`ieee80211_apply_htcap_overrides()` applies configured HT masks for managed and IBSS interfaces. `ieee80211_ht_cap_ie_to_sta_ht_cap()` converts peer HT Capabilities IEs into `link_sta->pub->ht_cap` intersected with local support. `ieee80211_sta_tear_down_BA_sessions()` and `ieee80211_ba_session_work()` coordinate RX/TX BA start/stop state across TIDs. `ieee80211_send_delba()` and `ieee80211_process_delba()` transmit and consume DELBA action frames. `ieee80211_send_smps_action()`, `ieee80211_request_smps()`, and `ieee80211_smps_mode_to_smps_mode()` handle SMPS requests and action encoding. `ieee80211_ht_handle_chanwidth_notif()` reacts to peer channel width notifications.

## Control Flow
Capability overrides first rewrite MCS masks according to user masks, then disable or enable selected capability bits and constrain AMPDU factor/density. HT IE conversion exits to an empty capability if the peer IE or local HT support is absent, applies local overrides for station/adhoc modes, masks symmetric capability bits, handles asymmetric STBC, copies AMPDU parameters and peer TX MCS metadata, computes usable RX MCS masks based on local TX stream capability, preserves MCS 32 when both sides support it, sets max AMSDU length, and recalculates aggregate limits. It then updates public HT capability, current/public bandwidth based on link channel width and HT40 support, and SMPS mode for AP/AP_VLAN/NAN peers.

BA teardown iterates all TIDs to stop RX and TX aggregation and, for station destruction, cancels pending BA work and completes pending stop callbacks. The BA worker handles expired RX timers, requested RX stops, offloaded RX start/stop management, pending TX aggregation starts after fragment queues drain, and deferred start/stop callbacks. DELBA processing decodes TID/initiator and stops the appropriate RX or TX BA session. SMPS action transmission builds an HT action frame, requests TX status, stores link and mode in `status_data`, and sends on TID 7.

## State and Persistence
Persistent state is stored in per-interface override fields (`u.mgd.ht_capa`, `u.ibss.ht_capa` and masks), `link_sta->pub->ht_cap`, `link_sta->pub->bandwidth`, `link_sta->cur_max_bandwidth`, `link_sta->pub->smps_mode`, station aggregate state under `sta->ampdu_mlme`, TXQ fragment queues, and managed link `driver_smps_mode`. The file uses wiphy locking, RCU link lookups, station locks, and fq locks to coordinate concurrent TX aggregation and queue state.

## Dependencies and Integration Points
Depends on kernel 802.11 definitions, mac80211 private structures, station aggregation helpers implemented elsewhere, rate control, cfg80211 station opmode notification, driver RC update hooks, and management TX helpers from `ieee80211_i.h`. It is used by MLME association, IBSS peer updates, mesh peer links, cfg80211 station update code, block-ack action handling, debugfs SMPS controls, and driver-facing exported `ieee80211_request_smps()`.

## Risks
HT override behavior must remain aligned with hardware registration masks as noted in the source comment. Capability negotiation is dense, especially MCS stream limits, unequal modulation, STBC asymmetry, and MCS 32 handling. BA worker correctness depends on bitmaps, fragment queue draining, `synchronize_net()`, and not starting aggregation while `WLAN_STA_BLOCK_BA` is set. TXQ stop flags during fragmented TX are race-sensitive. SMPS status_data packs link and mode into a limited bitfield. Channel-width notification must keep rate control and cfg80211 opmode reporting synchronized.

## Test Signals
Signals include HT association/IBSS/mesh peers with overridden MCS and capability bits, HT20/HT40 bandwidth transitions, AMPDU start/stop under active fragmented TX, RX BA timer expiry, DELBA initiator/recipient cases, SMPS action status handling, and cfg80211 `STA_OPMODE_MAX_BW_CHANGED` notifications. Kernel warnings in capability/default width handling, BA destruction cleanup, and SMPS invalid modes are important regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ibss.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ibss.c

## Purpose
Implements mac80211 IBSS/ad-hoc MLME behavior: joining or creating an IBSS, building and updating beacon/probe-response data, scanning and merging with compatible IBSS networks, maintaining peer station entries, processing IBSS management frames, handling channel switch announcements and DFS constraints, and leaving/cleanup.

## Important APIs, Types, and Functions
External entry points are `ieee80211_ibss_join()`, `ieee80211_ibss_leave()`, `ieee80211_ibss_work()`, `ieee80211_ibss_rx_queued_mgmt()`, `ieee80211_ibss_rx_no_sta()`, `ieee80211_ibss_notify_scan_completed()`, `ieee80211_ibss_setup_sdata()`, `ieee80211_ibss_csa_beacon()`, `ieee80211_ibss_finish_csa()`, and `ieee80211_ibss_stop()`. Important internal helpers include `ieee80211_ibss_build_presp()`, `__ieee80211_sta_join_ibss()`, `ieee80211_sta_join_ibss()`, `ieee80211_ibss_add_sta()`, `ieee80211_update_sta_info()`, `ieee80211_rx_bss_info()`, `ieee80211_ibss_process_chanswitch()`, `ieee80211_sta_find_ibss()`, `ieee80211_sta_merge_ibss()`, and `ieee80211_sta_create_ibss()`.

## Control Flow
Join setup validates frequency offset, DFS requirements, interface combinations, configured BSSID/channel, privacy/control-port flags, basic rates, beacon interval, custom IEs, HT overrides, and initial link parameters, then enters `IEEE80211_IBSS_MLME_SEARCH` and queues interface work. In search state, the worker finishes delayed station insertions, looks for a matching cfg80211 BSS, joins it if found, creates directly for fixed BSSID plus fixed channel, triggers scans if needed, or creates a new IBSS after the join timeout.

Joining resets TSF, flushes peers on BSSID change, leaves any old IBSS in the driver, drops the old RCU probe response, checks beaconing and DFS legality, acquires a channel context, builds a probe response/beacon template, updates BSS config, starts beaconing, calls `drv_join_ibss()`, informs cfg80211 of the BSS and join, starts the merge timer, and brings carrier up. Probe response building emits SSID, supported rates, DS params on 2 GHz, IBSS params, optional CSA, extended rates, configured IEs, HT/VHT capability and operation IEs when allowed, and WMM info when QoS queues exist.

RX management dispatch handles probe requests by replying from the current template, beacons/probe responses by parsing elements and updating BSS/peer state, open-system auth by sending a compatibility response, deauth by destroying the peer, and spectrum management channel switch actions by parsing CSA elements. BSS info processing updates station rates/capabilities, informs cfg80211 BSS cache, and merges into an IBSS with a higher TSF when SSID/privacy/channel rules permit. Joined-state work expires inactive peers, scans for merge candidates only when no active peers exist, and reschedules the merge timer.

## State and Persistence
Persistent IBSS state lives in `sdata->u.ibss`: timers, CSA drop work, `last_scan_completed`, `basic_rates`, fixed BSSID/channel flags, privacy/control-port/DFS flags, BSSID, SSID, custom IE buffer, chandef, join request timestamp, RCU `presp`, HT override fields, incomplete station list, lock, and SEARCH/JOINED state. Related persistent state is in `sdata->vif.bss_conf`, `sdata->deflink`, cfg80211 BSS cache, `sta_info` entries, and driver channel context/beacon state. RCU is used for beacon/probe-response replacement, while the incomplete station list is protected by `incomplete_lock`.

## Dependencies and Integration Points
Depends on cfg80211 BSS cache, scan requests, DFS/regulatory checks, channel contexts, driver operations (`drv_join_ibss()`, `drv_leave_ibss()`, `drv_reset_tsf()`, `drv_tx_last_beacon()`), station allocation/insertion/destruction, rate control, HT/VHT element builders and parsers, management TX helpers, WMM defaults, and interface work/timer infrastructure. It integrates with cfg80211 join/leave callbacks in `cfg.c`, scan completion in `scan.c`, RX no-station paths in `rx.c`, queued management dispatch and work setup in `iface.c`, and channel switch plumbing in cfg80211/mac80211 channel management.

## Risks
IBSS behavior is timing- and state-machine-sensitive: scans, merge timers, TSF comparisons, and join timeout creation can race with user leave or channel changes. CSA handling intentionally disconnects on unsupported or unsafe switches and must correctly mark DFS radar events. Regulatory downgrade from wider channels to 20 MHz can surprise users but is required for beacon legality. The code caps IBSS stations at 128 and does not evict least-recently-used entries. Incomplete station insertion crosses IRQ/RX context and work context, so cleanup on disconnect/leave is important. The cfg80211 BSS channel update in CSA is explicitly noted as questionable. Probe request validation assumes a leading SSID IE. Custom IE allocation failure during join silently leaves `ie_len` zero if `kmemdup()` fails.

## Test Signals
High-value tests exercise fixed and non-fixed BSSID/channel joins, scan-to-join, timeout-to-create, merge into higher-TSF IBSS, leave cleanup, carrier and cfg80211 join notifications, probe request responses for wildcard and matching SSID, inactive peer expiration with RSN/control-port authorization, incomplete station promotion from RX no-sta, CSA beacon creation/finalization, DFS channel rejection without userspace control, unsupported CSA disconnect, HT/VHT capability propagation in IBSS peers, and station cap at `IEEE80211_IBSS_MAX_STA_ENTRIES`. Runtime signals include `sdata_info()` join/scan/create logs, cfg80211 BSS cache updates, driver join/leave callbacks, and timer/work rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ibss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ieee80211_i.h -->
# sources/distributed-fs/ceph-client/net/mac80211/ieee80211_i.h

## Purpose
Defines mac80211's private internal interfaces and state structures. It is the central header that connects cfg80211-facing operations, interface state, link state, station/BSS handling, scan/channel context management, TX/RX pipelines, MLME, IBSS, mesh, NAN, HT/VHT/HE/EHT/UHR capability handling, queue control, and KUnit-visible internals.

## Important APIs, Types, and Functions
Core structures include `ieee80211_local` for per-hardware mac80211 state, `ieee80211_sub_if_data` for each virtual interface, `ieee80211_link_data` for per-link state, `ieee80211_bss` for mac80211-private BSS cache data, `ieee80211_tx_data` and `ieee80211_rx_data` for TX/RX handler context, `beacon_data` and probe/FILS discovery response containers, `ieee80211_if_managed`, `ieee80211_if_ibss`, `ieee80211_if_mesh`, `ieee80211_if_ocb`, `ieee80211_if_nan`, and `txq_info`.

Key enums and macros define status-data packing, connection modes and bandwidth limits, parse errors, scan flags/states, queue stop reasons, channel-context modes and replacement states, TXQ flags, interface flags, and KUnit export visibility. Important inline helpers include `vif_to_sdata()`, `IEEE80211_DEV_TO_SUB_IF()`, `IEEE80211_WDEV_TO_SUB_IF()`, link iteration macros, `ieee80211_get_sband()`, `ieee80211_get_link_sband()`, `hw_to_local()`, `to_txq_info()`, queue stop/wake wrappers, `ieee80211_tx_skb()` wrappers, and element parser wrappers.

## Control Flow
The header does not implement one runtime flow; it declares the control surface used across mac80211. Major declared flows include managed auth/assoc/deauth/disassoc and station work, IBSS join/leave/work/RX/CSA, OCB and mesh work, scan request/completion, off-channel and management TX, channel switch/color change, interface add/remove/open/stop, link setup/teardown, TX fast/slow paths, HT/BA/SMPS, VHT/HE/S1G/EHT/UHR capability conversion, spectrum channel-switch parsing, suspend/resume/reconfigure, power save, queue control, station auth frame helpers, probe request/IE construction, channel context allocation/reservation/release, TDLS operations, and optional KUnit-only entry points.

## State and Persistence
`ieee80211_local` persists hardware-wide objects: embedded `ieee80211_hw`, fair queue and CoDel state, active TXQs, queue stop reasons, interface lists, scan state, channel contexts, station tables and counters, pending queues, rate control, WEP contexts, monitor state, power-save state, work/timer/tasklet objects, debugfs state, and hardware flags such as suspend/reconfigure/WoWLAN. `ieee80211_sub_if_data` persists per-netdev/per-wireless-dev keys, queues, work items, rate masks, beacon masks, interface-type union state, default and RCU link pointers, debugfs entries, drop counters, and embedded public `ieee80211_vif`. `ieee80211_if_ibss` stores the ad-hoc MLME state researched in `ibss.c`; `ieee80211_mgd_assoc_data` stores FILS KEK/nonces used by `fils_aead.c`; `link_data` stores channel context, CSA, SMPS, power, DFS, and AP/managed link data.

## Dependencies and Integration Points
This header depends on Linux kernel core headers, cfg80211/mac80211 public APIs, radiotap, fq/codel, KUnit visibility, and local headers `key.h`, `sta_info.h`, `debug.h`, and `drop.h`. It is included broadly by mac80211 implementation files and supplies prototypes for cfg80211 operations, MLME, scan, channel, TX/RX, aggregation, capability parsing, and interface lifecycle code. It also declares `extern const struct ethtool_ops ieee80211_ethtool_ops`, connecting `ethtool.c` to interface setup, and includes the prototypes for IBSS, HT, and HE functions covered by this subset.

## Risks
Because this is a private umbrella header, structure layout changes have broad blast radius across mac80211 and drivers that interact with embedded public objects. Concurrency contracts are implicit in fields and helpers: many pointers are RCU-protected, station lists and channel contexts require the wiphy mutex, TXQ/queue state uses spinlocks, and workers must respect suspend/reconfigure guards. Flexible-array and "keep last" layout requirements in `ieee80211_sub_if_data`, `txq_info`, and `ieee80211_chanctx` are easy to break. Status-data packing, queue stop reason refcounting, and link iteration macros rely on precise bit and loop semantics. KUnit visibility macros intentionally change linkage for selected functions and must stay aligned with tests.

## Test Signals
Compile coverage across mac80211 is the first signal for this header. Behavioral signals come from KUnit suites under `net/mac80211/tests` for element parsing, channel-mode determination, management frame protection, TPE subchannel/PSD helpers, and S1G TIM logic. Runtime regression signals include interface add/remove and type-change tests, managed association with FILS/HT/HE, IBSS join/leave/CSA, scan and remain-on-channel flows, queue stop/wake accounting, suspend/resume reconfiguration, station aggregation lifecycle, and debugfs/cfg80211 control paths. Lockdep, RCU stall reports, KASAN, and WARN_ONs are especially important because this header defines the shared state and synchronization assumptions rather than isolated algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ieee80211_i.h -->
