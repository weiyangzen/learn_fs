# Research: subset-b-006231

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/sta_info.c -->
## sources/distributed-fs/ceph-client/net/mac80211/sta_info.c

Purpose: implements mac80211 station object lifetime, lookup, insertion, removal, power-save buffering, airtime accounting, MLO link management, and cfg80211 station-info export. `sta_info` instances are the in-kernel persistent representation of peers across managed, AP, IBSS, mesh, TDLS, NAN, and MLO use cases.

Important APIs and functions: `sta_info_alloc()` / `sta_info_alloc_with_link()` allocate a private `struct sta_info` plus public `struct ieee80211_sta`, link-sta storage, TXQs, rate-control state, fragment cache, power-save queues, and default rates. `sta_info_insert()` / `sta_info_insert_rcu()` validate device state and uniqueness, insert into `local->sta_hash`, `local->link_sta_hash`, and `local->sta_list`, notify drivers through `drv_sta_state()`, add debugfs, and publish cfg80211 new-station events. `__sta_info_destroy()`, `sta_info_destroy_addr()`, `sta_info_destroy_addr_bss()`, `__sta_info_flush()`, and `ieee80211_sta_expire()` remove stations using a two-part teardown split by `synchronize_net()`. Lookup helpers include `sta_info_get()`, `sta_info_get_bss()`, `sta_info_get_by_addrs()`, `link_sta_info_get_bss()`, `ieee80211_find_sta()`, and `ieee80211_find_sta_by_ifaddr()`.

Control flow: allocation initializes static fields and per-link state, then insertion performs uniqueness and running-interface checks before making the station RCU-visible. Insertion blocks BA sessions while the station is partially constructed, pushes state transitions to the driver, then clears `WLAN_STA_BLOCK_BA`. State transitions are centralized in `_sta_info_move_state()` and enforce the valid sequence `NONE <-> AUTH <-> ASSOC <-> AUTHORIZED`; upward transitions can fail in the driver, downward transitions must not. Destruction first blocks and tears down BA sessions, synchronizes RX queues, removes station and link hash entries, handles TDLS off-channel cancellation, unlinks from lists, and notifies `drv_sta_pre_rcu_remove()`. After `synchronize_net()`, it tears down BA again, clears keys/TIM, walks state down, notifies cfg80211 deletion, destroys debugfs and fragments, purges queues, and frees memory.

State and persistence behavior: station state is in RCU hash/list membership, `_flags`, `sta_state`, `uploaded`, `dead`, `removed`, per-link `valid_links`, driver-visible `struct ieee80211_sta`, per-link stats, rate-control data, A-MPDU MLME arrays, PS queues, filtered TX queues, TIM bitmap bits, and removed-link accumulated stats. Power-save state persists in `WLAN_STA_PS_STA`, `WLAN_STA_PS_DRIVER`, `WLAN_STA_PS_DELIVER`, `driver_buffered_tids`, `txq_buffered_tids`, `ps_tx_buf[]`, `tx_filtered[]`, and `local->total_ps_buffered`; `sta_info_recalc_tim()` updates AP/mesh TIM bits and optional driver `set_tim`. MLO link operations allocate, activate, remove, and account link stats while keeping aggregate A-MSDU limits consistent across active links.

Dependencies and integration points: depends on rhashtable/rhltable, RCU, wiphy mutex locking, cfg80211 station notifications, driver ops (`drv_sta_state`, `drv_change_sta_links`, `drv_flush_sta`, `drv_sync_rx_queues`, `drv_set_tim`, `drv_sta_notify`), rate control, debugfs, mesh peer management, NAN helpers, TXQ/FQ scheduling, AQL airtime accounting, BA-session code, and fast TX/RX caches. Exported driver APIs include station lookup, power-save blocking/EOSP helpers, buffered-TID notification, airtime registration, aggregate recalculation, and lockdep checks.

Risks and edge cases: lifetime correctness depends on respecting RCU and wiphy mutex rules; callers using `sta_info_get()` must already have protection after the helper drops its internal RCU section. Destroy is intentionally two-phased to avoid use-after-free with TX/RX, BA work, and drivers. TIM bit handling is sensitive to AP_LINK_PS driver behavior and local PS queue accounting. MLO link removal accumulates stats before clearing links; missing that would make station reports regress. Power-save release has ordering constraints across filtered frames, PS buffers, driver-buffered TIDs, MoreData/EOSP, and service-period flags. TDLS teardown and off-channel states must be cleared before freeing peers.

Test signals: this file is indirectly covered by KUnit tests in this group through `sta_info.h` flag helpers in `tests/mfp.c`, and by broader mac80211 tests that exercise station state, power save, TDLS, and cfg80211 reporting. Strong validation signals are lockdep under wiphy/RCU, KASAN/KCSAN during station churn, AP power-save interoperability, MLO link add/remove, TDLS setup/teardown, and rate-control/airtime accounting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/sta_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/sta_info.h -->
## sources/distributed-fs/ceph-client/net/mac80211/sta_info.h

Purpose: declares mac80211 internal station data structures, flags, aggregation state, fast-path caches, mesh state, per-link stats, fragment cache, station lifecycle APIs, power-save APIs, MLO link APIs, and compact rate-stat encoding helpers.

Important APIs/types: `enum ieee80211_sta_info_flags` defines authentication, association, authorization, power-save, TDLS, BA-blocking, encryption, fast-path, mesh, and offload flags manipulated through `set_sta_flag()`, `clear_sta_flag()`, and test helpers. `struct tid_ampdu_tx` and `struct tid_ampdu_rx` represent TX/RX BA session state and are RCU-managed. `struct sta_ampdu_mlme` stores per-TID aggregation arrays, timers, bitmaps, and work. `struct link_sta_info` contains per-link address, hash node, keys, TX/RX/status stats, bandwidth/OMI state, debugfs, and public `ieee80211_link_sta`. `struct sta_info` is the full private station object wrapping public `ieee80211_sta`.

Control flow and state model: the header documents that allocated stations are caller-owned until insertion, then owned by global hash/list state until destruction. `sta_info_move_state()` and `sta_info_pre_move_state()` move through station states before or after insertion. Lookup functions are RCU/wiphy protected. Flush, expire, and destroy APIs remove stations; PS delivery APIs release buffered traffic; stats APIs fill cfg80211 structures. Link APIs allocate/free/activate/remove MLO links and keep the public link pointers synchronized.

State and persistence behavior: persistent fields include `_flags`, `sta_state`, `uploaded/dead/removed`, link pointer array, default link, removed-link aggregate stats, PTKs/GTKs, rate-control pointers, TXQs, A-MPDU state, power-save queues and TID bitmaps, airtime/AQL counters, fragment cache, fast TX/RX RCU pointers, mesh state, TDLS chandef, and per-link TX/RX/status counters. The public `struct ieee80211_sta` is kept last and exposes driver-visible station data.

Dependencies and integration points: includes Linux list/workqueue/rhashtable/u64 stats support, Ethernet helpers, bitfield helpers, and local `key.h`. APIs are consumed across mac80211 TX, RX, MLME, TDLS, mesh, aggregation, rate control, debugfs, and driver-facing code.

Risks and edge cases: direct manipulation of `WLAN_STA_AUTH`, `WLAN_STA_ASSOC`, and `WLAN_STA_AUTHORIZED` through generic flag helpers is warned against because those flags mirror station-state transitions. Aggregation arrays require RCU and locking discipline. `sta_info_get_by_idx()` is explicitly marked broken, signaling that indexed station lookup is not a reliable stable API. Per-link stats and removed-link accumulation are easy to misreport if new fields are added without updating aggregation/reporting code.

Test signals: compile-time structure and macro coverage comes from mac80211 builds; `tests/mfp.c` directly uses `set_sta_flag()` and raw association bit state; TDLS and status files depend heavily on these declarations. Additional confidence comes from lockdep, sparse RCU checking, and KUnit suites that include `../sta_info.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/sta_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/status.c -->
## sources/distributed-fs/ceph-client/net/mac80211/status.c

Purpose: processes driver TX status reports for mac80211, including IRQ-safe queueing, filtered-frame recovery, retry/accounting updates, radiotap monitor injection, ACK status reporting to cfg80211/socket users, rate-control feedback, packet-loss detection, airtime completion, and TX skb cleanup.

Important APIs/functions: exported entry points are `ieee80211_tx_status_irqsafe()`, `ieee80211_tx_status_skb()`, `ieee80211_tx_status_ext()`, `ieee80211_tx_rate_update()`, `ieee80211_report_low_ack()`, `ieee80211_free_txskb()`, and `ieee80211_purge_tx_queue()`. Internal helpers include `ieee80211_handle_filtered_frame()`, `ieee80211_add_tx_radiotap_header()`, `ieee80211_report_ack_skb()`, `ieee80211_report_used_skb()`, `ieee80211_lost_packet()`, `ieee80211_tx_get_rates()`, and `ieee80211_tx_monitor()`.

Control flow: IRQ-safe status enqueues SKBs onto reliable or unreliable local queues and schedules the tasklet, dropping excess unreliable statuses. Normal status handling computes retry counts, updates per-station counters, handles ACK/no-ACK/loss paths, feeds rate control and mesh metrics, and either delegates full 802.11 SKBs to `__ieee80211_tx_status()` or frees/queues hardware-encap SKBs directly. `__ieee80211_tx_status()` handles QoS TID detection, BAR retry bookkeeping, filtered-frame requeueing, SNMP counters, dynamic PS nullfunc ACK handling, reporting to completion consumers, monitor injection, and final free-list/kfree handling.

State and persistence behavior: updates `sta->deflink.status_stats` retry, failed, lost, ACK timestamp, ACK signal, and per-TID MSDU retry/failure counters; updates TX rate snapshots; clears service-period flags on EOSP; decrements AQL pending airtime; records pending BAR SSNs for failed BAR frames; mutates local debug counters and LED state; consumes IDR ack-status registrations; and optionally stores or resends TDLS teardown SKBs through managed-interface teardown state.

Dependencies and integration points: depends on `sta_info` lookup and PS flags, rate control, mesh metrics, cfg80211 control-port/probe/mgmt TX status APIs, monitor interfaces, radiotap format definitions, LED helpers, WME/TID mapping, TDLS teardown handling, dynamic PS timers, AQL airtime, and driver feature flags such as `REPORTS_TX_ACK_STATUS`, `REPORTS_LOW_ACK`, `HAS_RATE_CONTROL`, and hardware 802.11 encapsulation.

Risks and edge cases: filtered-frame handling assumes driver/RX/TX-status ordering around AP power-save transitions; incorrect ordering can drop or mis-buffer frames. Radiotap length/headroom calculations must match emitted fields. `status->info == NULL`, `skb == NULL`, aggregated frames without full status, no-ack transmissions, injected frames, multicast frames, and hardware-encap paths all bypass different pieces of accounting. ACK status IDR removal must happen exactly once. Packet-loss notifications intentionally skip drivers that report low ACK themselves.

Test signals: no direct KUnit file in this group targets `status.c`, but related behavior is exercised by station power-save, TDLS teardown, monitor TX status, rate-control, and cfg80211 ACK-status tests. Useful runtime signals are retry/loss counters, radiotap TX monitor output, TDLS teardown resend behavior, AQL underflow warnings, and dynamic power-save nullfunc ACK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tdls.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tdls.c

Purpose: implements mac80211 Tunneled Direct Link Setup support for managed stations, including TDLS management frame construction, setup/confirm/teardown/discovery handling, peer authorization state, channel-context/protection recalculation, driver/user operation notifications, and TDLS channel-switch request/response processing.

Important APIs/functions: externally visible functions include `ieee80211_tdls_mgmt()`, `ieee80211_tdls_oper()`, `ieee80211_tdls_oper_request()`, `ieee80211_tdls_channel_switch()`, `ieee80211_tdls_cancel_channel_switch()`, `ieee80211_process_tdls_channel_switch()`, `ieee80211_teardown_tdls_peers()`, `ieee80211_tdls_handle_disconnect()`, and `ieee80211_tdls_peer_del_work()`. IE builders include extended capabilities, supported channels, regulatory classes, WMM params, link ID, setup start/confirm IEs, and channel-switch IEs.

Control flow: management requests validate TDLS support and managed association. Setup requests ensure only one pending peer setup, require a peer station on success paths, flush queues, store `tdls_peer`, build and transmit encapsulated TDLS frames, and schedule delayed cleanup if setup does not complete. Teardown stops queues, flushes direct packets, sends teardown, clears peer-auth state, and wakes queues. `ieee80211_tdls_oper()` handles userspace enable/disable-link operations by authorizing peers, recalculating channel/protection state, destroying peers on disable, and clearing pending setup tracking. Channel switch builds driver templates with timing IE offsets, validates peer support, calls driver channel-switch ops, and maintains `WLAN_STA_TDLS_OFF_CHANNEL`.

State and persistence behavior: mutates managed-interface `tdls_peer`, delayed peer deletion work, teardown skb/original skb fields, station TDLS flags (`TDLS_PEER_AUTH`, `TDLS_INITIATOR`, `TDLS_CHAN_SWITCH`, `TDLS_OFF_CHANNEL`, `TDLS_WIDER_BW`), `sta->tdls_chandef`, station bandwidth, HT protection bits, and SMPS request work. It builds SKBs with precise IE ordering and stores channel-switch templates only long enough for driver handoff.

Dependencies and integration points: depends on cfg80211 TDLS APIs, station lookup/destruction, MLME managed state, rate/channel helpers, regulatory beacon permissions, driver ops for TDLS discover protection/channel switch/cancel/receive, queue stop/wake/flush, HT/VHT/HE/EHT capability builders, and status.c teardown ACK fallback. It integrates with AP/base-channel context recalculation and cfg80211 user notifications.

Risks and edge cases: TDLS setup concurrency is intentionally restricted to one peer; stale `tdls_peer` cleanup must run on failed setup. IE ordering with `extra_ies` split points is interoperability-sensitive. Wider-bandwidth upgrades must obey regulatory constraints and peer capabilities. Channel-switch parsing infers band from operating class/channel combinations and rejects forbidden or malformed requests. Teardown relies on queue flushing and optional ACK-status resend through the AP; failure can leave direct traffic or peer state inconsistent.

Test signals: direct KUnit coverage is absent in this subset, but strong validation includes TDLS setup/teardown/discovery interop, malformed IE parsing, channel-switch request/response tests, regulatory-denied channel tests, queue-stop flushing checks, and status.c teardown resend behavior. Runtime debug messages under `tdls_dbg()` provide useful traces for peer state and channel-switch decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tdls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/Makefile -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/Makefile

Purpose: builds the mac80211 KUnit test module when `CONFIG_MAC80211_KUNIT_TEST` is enabled.

Important APIs/targets: assigns `mac80211-tests-y` to include `module.o`, `util.o`, `elems.o`, `mfp.o`, `tpe.o`, `chan-mode.o`, and `s1g_tim.o`, then adds `mac80211-tests.o` to `obj-$(CONFIG_MAC80211_KUNIT_TEST)`.

Control flow and state: this is declarative kbuild state only. Object order controls which compilation units are linked into the KUnit module; runtime suite registration happens inside each test source through `kunit_test_suite()`.

Dependencies and integration points: depends on the kernel kbuild system, KUnit, the local `util` test harness, and exported-for-KUnit mac80211 symbols.

Risks and edge cases: adding a test source without listing it here means the suite will not run. Removing `module.o` would drop module metadata. The list currently includes `tpe.o`, which is outside this work item but part of the same test module.

Test signals: successful build of `CONFIG_MAC80211_KUNIT_TEST=m/y` and KUnit discovery of all named suites are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/chan-mode.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/chan-mode.c

Purpose: KUnit parameterized tests for `ieee80211_determine_chan_mode()`, verifying how mac80211 selects or downgrades connection mode and bandwidth from AP IEs, hardware strictness, userspace membership-selector handling, and HT/VHT/HE/EHT capability requirements.

Important APIs/types: `struct determine_chan_mode_case` captures case parameters and expected outcomes. `test_determine_chan_mode()` builds synthetic BSS IEs for supported rates, HT/VHT capabilities and operation, HE capabilities/operation, and EHT capabilities/operation, then calls `ieee80211_determine_chan_mode()`. It uses `T_SDATA(test)` from `util.h`, KUnit parameter generation via `KUNIT_ARRAY_PARAM_DESC`, and suite registration as `mac80211-mlme-chan-mode`.

Control flow: each case seeds `struct ieee80211_conn_settings`, optional hardware flags (`IEEE80211_HW_STRICT`, `IEEE80211_HW_DISALLOW_PUNCTURING`), capability masks, userspace selectors, and a fake `cfg80211_bss`. The parser runs under RCU, returned elements are freed if valid, and assertions compare either expected `-EINVAL` or resulting `conn.mode` and `conn.bw_limit`.

State and persistence behavior: all state is per-test and allocated through KUnit. It mutates test sdata masks and local hardware flags but does not persist beyond test lifetime. The fake BSS IE blob is copied into KUnit-managed memory.

Dependencies and integration points: depends on `net/cfg80211.h`, KUnit, local test utility fixtures, exported mac80211 channel-mode internals, and constants for membership selectors and HT/VHT/HE/EHT operation encodings.

Risks and edge cases covered: unsupported basic membership selectors, userspace override of unknown selectors, strict HT/VHT capability masking, AP basic MCS requirements exceeding client streams, all-zero VHT/HE basic-rate workaround behavior, EHT MCS-7 NSS limitations, EHT-required failure, and bandwidth downgrade when puncturing is disallowed.

Test signals: passing suite confirms deterministic downgrade/error behavior for representative EHT/HE/VHT/HT cases. It does not cover every operating class/channel layout or malformed IE length, so parser fuzzing and MLME integration tests remain useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/chan-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/elems.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/elems.c

Purpose: KUnit coverage for mac80211 element parsing, specifically defragmentation of nested EHT Multi-Link Element data and per-STA profile fragments.

Important APIs/functions: `mle_defrag()` constructs an skb containing an EHT basic MLE with a complete per-STA profile and many SSID elements, fragments both the STA profile and outer MLE using `ieee80211_fragment_element()`, then calls `ieee802_11_parse_elems_full()`. The suite is registered as `mac80211-element-parsing`.

Control flow: the test allocates and pads an skb, writes the MLE and nested profile fields manually, fragments inner and outer elements, fills `ieee80211_elems_parse_params`, parses, asserts a non-NULL result, and checks that `ml_basic`, `ml_basic_len`, `prof`, and `sta_prof_len` match expected reconstructed lengths. It frees parsed output and skb.

State and persistence behavior: all state is local to the KUnit test. The parser result is heap allocated and explicitly freed; the skb is freed at the end.

Dependencies and integration points: depends on KUnit, `../ieee80211_i.h`, exported-for-KUnit parser helpers, skb APIs, unaligned little-endian writes, and EHT MLE constants. This test supports MLME scan/association parsing paths that consume fragmented MLEs.

Risks and edge cases: validates that fragmentation does not lose nested profile data or return NULL unexpectedly. It does not exhaustively cover malformed fragments, multiple profiles, all link IDs, or memory-pressure failures beyond allocation asserts.

Test signals: passing test indicates basic nested MLE defragmentation remains intact after parser changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/elems.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/mfp.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/mfp.c

Purpose: parameterized KUnit tests for management frame protection acceptance/drop decisions in `ieee80211_drop_unencrypted_mgmt()`.

Important APIs/types: `struct mfp_test_case` describes whether a peer station exists, whether MFP/association/decryption/unicast is present, frame subtype/category/action, and expected `ieee80211_rx_result`. `accept_mfp()` builds a synthetic management skb and invokes the RX helper. Suite name is `mac80211-mfp`.

Control flow: each test zeroes a static `sta_info`, optionally sets `WLAN_STA_MFP` and raw `WLAN_STA_ASSOC`, allocates an skb, marks RX decrypted/protected state when requested, adjusts destination address for unicast/multicast, appends action or reason payload, then asserts the drop/continue result.

State and persistence behavior: no persistent state beyond the static station reused after `memset`. It uses station flags from `sta_info.h` but does not insert the station into global tables.

Dependencies and integration points: depends on KUnit, KUnit skb helpers, `../ieee80211_i.h`, `../sta_info.h`, RX status control block flags, WLAN category/action constants, and exported-for-KUnit RX management filtering.

Risks and edge cases covered: public action acceptance for unknown/non-MFP peers, dropping unicast public action when MFP should use protected dual, protected-dual rejection without decrypted MFP, deauth/disassoc allowed before keys are set, and robust non-public action behavior before/after association. One case labelled disassoc uses `IEEE80211_STYPE_DEAUTH`, so it may not independently cover the disassociation subtype.

Test signals: passing suite confirms core MFP filtering matrix. Additional integration tests should cover real key installation, multicast robust management frames, and full RX path sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/mfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/module.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/module.c

Purpose: provides module metadata for the mac80211 KUnit test module.

Important APIs: includes `<linux/module.h>` and declares `MODULE_LICENSE("GPL")` plus `MODULE_DESCRIPTION("tests for mac80211")`.

Control flow and state: no executable logic, persistent state, init, or exit functions are defined. It exists so linked KUnit object files have standard module metadata.

Dependencies and integration points: built through the local tests Makefile into `mac80211-tests.o` when `CONFIG_MAC80211_KUNIT_TEST` is enabled.

Risks and edge cases: missing or incompatible license metadata can affect module loading and symbol access. Otherwise this file is intentionally minimal.

Test signals: compile and module-load/KUnit discovery are sufficient validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/s1g_tim.c -->
## sources/distributed-fs/ceph-client/net/mac80211/tests/s1g_tim.c

Purpose: KUnit tests for S1G TIM Partial Virtual Bitmap decoding via `ieee80211_s1g_check_tim()`, covering block bitmap, single AID, open-ended block, and inverse forms based on IEEE 802.11 annex examples.

Important APIs/functions: helpers `BC()`, `tim_begin()`, `tim_end()`, `pvb_add_block_bitmap()`, `pvb_add_single_aid()`, `pvb_add_olb()`, `fill_bitmap()`, `fill_bitmap_inverse()`, and `check_all_aids()` build TIM IEs and compare expected AID membership. `dump_tim_bits()` emits diagnostic bit-level logs. Suite name is `mac80211-s1g-tim`.

Control flow: each test constructs an in-stack TIM IE buffer, appends one S1G PVB encoding mode, builds an expected bitmap for AIDs 1 through `MAX_AID`, optionally dumps encoding details, and checks every AID with `ieee80211_s1g_check_tim()`. Six cases cover normal and inverse variants for block, single, and OLB encodings.

State and persistence behavior: state is entirely per-test stack data plus KUnit log output. No global mac80211 state is mutated.

Dependencies and integration points: depends on Linux IEEE 802.11 definitions, KUnit, `kunit/test-bug.h`, bitmap helpers, S1G TIM encoding constants, and the production S1G TIM decoder.

Risks and edge cases: verifies positive and inverse membership semantics across the supported encoding modes, but notes that ADE mode is optional and not supported by mac80211. Coverage is bounded to `MAX_AID` 128 and synthetic single-block style examples, so larger AID ranges and malformed/truncated TIMs remain separate concerns.

Test signals: passing suite gives targeted confidence that S1G TIM decoding matches the constructed annex-style examples and inverse semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/s1g_tim.c -->
