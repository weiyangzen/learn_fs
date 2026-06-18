# Research: subset-b-004830

Grouped source research for Intel iwlwifi MLD scan, station, statistics, thermal, time-sync, TLC, and KUnit test files. Each section preserves the source path and is intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.c

Purpose: Implements MLD UMAC scan orchestration for regular scans, scheduled scans, net-detect style scheduled scans, internal MLO link-selection scans, scan aborts, scan completion reporting, optional 6 GHz passive discovery, and channel survey export to mac80211.

Important APIs and functions: `iwl_mld_regular_scan_start()` starts cfg80211/mac80211 regular scans. `iwl_mld_sched_scan_start()` configures profile filtering and starts periodic firmware scans. `iwl_mld_scan_stop()` aborts active scan types and optionally notifies mac80211. `iwl_mld_int_mlo_scan()` starts internal scans over usable MLO links. Notification handlers process iteration-complete, match-found, start, complete, and channel-survey firmware events. `iwl_mld_alloc_scan_cmd()` allocates version 17 or 18 scan command storage.

Control flow: Scan requests are normalized into `struct iwl_mld_scan_params`, including SSIDs, channels, match sets, random MAC fields, 6 GHz RNR parameters, scan plans, P2P/low-latency decisions, and link ID selection. The command builder picks an unused scan UID, selects a scan timing type from active VIFs and traffic load, builds the probe request template with band-specific IEs and a WFA TPC IE, fills general/schedule/probe/channel command sections, then sends `SCAN_REQ_UMAC`. Completion notifications validate UID ownership, translate firmware status to mac80211 scan or sched-scan callbacks, clear status bits, and trigger MLO link selection after internal scans.

State and persistence: Runtime state lives in `mld->scan`: `status`, `uid_status[]`, `start_tsf`, `fw_link_id`, `pass_all_sched_res`, `last_ebs_failed`, traffic-load snapshots, allocated command buffer metadata, passive-6GHz timing, and last internal MLO scan timestamp. Channel survey data is lazily allocated in `mld->channel_survey` and flattened for `get_survey`. No durable persistence exists, but some timestamps survive firmware restart through the non-zeroed fields in `struct iwl_mld_scan`.

Dependencies and integration points: Depends on mac80211/cfg80211 scan APIs, iwlwifi firmware scan ABI in `fw/api/scan.h`, MLD link/VIF helpers, PHY band conversion helpers, notification wait/cancel helpers, EMLSR/MLO link-selection hooks, and firmware command dispatch through `iwl_mld_send_cmd*`. It feeds mac80211 scan completion, scheduled scan results/stopped notifications, channel survey reporting, and MLO selection.

Risks: UID/status bookkeeping is central; stale `uid_status[]` can misattribute firmware notifications. 6 GHz active/passive logic is dense and sensitive to PSC/non-PSC, hidden SSID, unsolicited probe, BSSID, and short-SSID limits. Abort paths intentionally clear state even if firmware says scan not found. The shared `mld->scan.cmd` buffer requires serialization under the wiphy/mac80211 control path. Survey allocation and indexing must match wiphy band/channel layout. EBS failure state can degrade future scans until reset.

Test signals: Cover command versions 17 and 18, oversized IE/channel rejection, regular scan completion with valid and removed links, scheduled scans with pass-all and match profiles, scan abort not-found behavior, internal MLO scan start/completion, passive 6 GHz enable/skip cases, EBS failure handling, P2P GO respect flags, and survey notifications followed by `get_survey` flattening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.h

Purpose: Declares MLD scan entry points, scan state enums, scan runtime state, and channel survey structures shared by scan implementation, notification dispatch, and mac80211 callbacks.

Important APIs and types: Exports start/stop APIs for regular, scheduled, and internal MLO scans; notification handlers for scan iteration, match, start, completion, and channel survey; `iwl_mld_mac80211_get_survey()`; `iwl_mld_alloc_scan_cmd()`; and `iwl_mld_report_scan_aborted()`. Defines `enum iwl_mld_scan_status`, scheduled-scan pass-all states, `enum iwl_mld_traffic_load`, `struct iwl_mld_scan`, `struct iwl_mld_survey_channel`, and `struct iwl_mld_survey`.

Control flow and integration: The header binds mac80211 operation callbacks, firmware notification dispatch, restart handling, and survey access to `scan.c`. The inline `iwl_mld_scan_max_template_size()` encodes firmware template capacity after driver-added management header and IEs.

State and persistence: `struct iwl_mld_scan` separates restart-zeroed state from command allocation and timing fields that survive firmware restart. Survey structs mirror a compact subset of mac80211 `survey_info`.

Dependencies: Requires firmware scan constants such as `SCAN_OFFLOAD_PROBE_REQ_SIZE`, Linux band counts, MLD core types, and mac80211/cfg80211 types supplied by includers.

Risks: The struct grouping controls restart cleanup semantics; adding fields in the wrong group can preserve stale scan state or lose needed command allocation data. Scan status values are bit masks and must stay compatible with UID status storage.

Test signals: Compile coverage of scan callbacks, restart cleanup, survey callback registration, and command-size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.c

Purpose: Implements firmware session protection requests used to reserve medium time for association and TDLS-style exchanges before normal firmware association scheduling is active.

Important APIs and functions: `iwl_mld_schedule_session_protection()` sends a best-effort protection request. `iwl_mld_start_session_protection()` sends a request and waits for a matching start notification. `iwl_mld_cancel_session_protection()` removes a pending or active session. `iwl_mld_handle_session_prot_notif()` updates VIF session state from firmware notifications.

Control flow: Scheduling resolves the target MLD link, rejects redundant requests when current `end_jiffies` covers the requested minimum, sends `SESSION_PROTECTION_CMD` with add action, and marks `session_requested`. The blocking start path installs a notification wait, schedules protection, waits for `SESSION_PROTECTION_NOTIF`, and succeeds only when the matching link reports a start. Cancellation checks active/requested state, sends remove action, and clears local state.

State and persistence: Per-VIF `session_protect` tracks `end_jiffies`, requested duration in milliseconds, and whether a request is awaiting notification. State is runtime-only and cleared on failure, stop, or cancel. `end_jiffies` uses a nonzero sentinel because zero means inactive.

Dependencies and integration points: Depends on MLD VIF/link lookup, firmware MAC context/session protection ABI, notification wait infrastructure, and wiphy locking. It is used by association and TDLS paths that need medium reservation.

Risks: The code warns when more than one active link exists because session protection is not designed for multi-link operation. Link removal before notification can make firmware IDs stale. A firmware status of zero clears state and can cause a blocking start to return `-EIO`. Time conversions between ms, TU, and jiffies must preserve the intended minimum window.

Test signals: Exercise already-protected `-EALREADY`, matching and nonmatching notifications, timeout, firmware reject, cancellation with no active session, cancellation after request, and link removal/error-before-recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.h

Purpose: Documents and declares the MLD session-protection interface used to request temporary firmware medium ownership around association and TDLS discovery.

Important APIs and types: Defines `struct iwl_mld_session_protect` with `end_jiffies`, `duration`, and `session_requested`; association/minimum protection constants; and declarations for notification handling, schedule, blocking start, and cancel APIs.

Control flow and integration: Consumers can choose fire-and-forget scheduling or a blocking start that waits for firmware confirmation. The header integrates with MLD VIF state and firmware MAC context command definitions.

State and persistence: The struct is embedded in VIF state and is runtime-only. `end_jiffies == 0` means inactive, so implementation uses a nonzero fallback for sessions that would otherwise calculate to zero.

Dependencies: Includes MLD core, host-command helpers, mac80211, and firmware MAC configuration definitions.

Risks: Callers must hold the expected wiphy lock in implementation paths and pass a valid link ID. Multi-link callers need care because implementation warns on more than one active link.

Test signals: Build coverage of all callers plus behavior tests for state transitions after start, reject, timeout, and cancel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.c

Purpose: Implements MLD station lifecycle and firmware station configuration, including per-link station IDs, add/modify/remove commands, duplicate RX data allocation, MPDU counters for EMLSR throughput gating, internal broadcast/multicast/aux/monitor stations, and resource migration when active MLO links change.

Important APIs and functions: `iwl_mld_add_sta()` and `iwl_mld_remove_sta()` manage peer STAs. `iwl_mld_update_all_link_stations()` refreshes firmware STA config. `iwl_mld_update_link_stas()` handles MLO link add/remove transitions. `iwl_mld_fw_sta_id_from_link_sta()` and `iwl_mld_fw_sta_id_mask()` map mac80211 link STAs to firmware IDs. Internal station APIs add/remove bcast, mcast, aux, and monitor stations. `iwl_mld_count_mpdu_rx()` and `iwl_mld_count_mpdu_tx()` update throughput counters.

Control flow: Adding a peer initializes driver-private station state, TXQs, duplicate tracking, MPDU counters, and data antenna state, then adds each active link STA to firmware. Link STA add either reuses preserved IDs during restart or allocates a new FW ID, maps it through RCU pointers, sends `STA_CONFIG_CMD`, and marks it in firmware. Removal flushes and waits for TXQs, removes TXQs and AP keys as needed, sends `STA_REMOVE_CMD`, cancels pending notifications, clears mappings, and frees non-default link STAs through RCU.

State and persistence: `struct iwl_mld_sta` stores station type/state, VIF pointer, duplicate RX data, TID-to-BAID mapping, default and per-link STAs, PTK PN pointers, and MPDU counters. `struct iwl_mld_link_sta` stores restart-zeroed `last_rate_n_flags`, `in_fw`, `signal_avg`, and persistent `fw_id`. FW ID preservation across hardware restart is deliberate so firmware can recover sequence/PN state.

Dependencies and integration points: Uses mac80211 station/link abstractions, MLD VIF/link allocation maps, TXQ helpers, key removal, aggregation/BAID updates, TLC configuration, firmware STA/AUX/remove commands, RCU, wiphy locking, and KUnit static stubs for `iwl_mld_fw_sta_id_mask`.

Risks: RCU pointer updates and FW ID maps must stay in sync; leaks or stale pointers can route notifications to freed link STAs. Error unwind in multi-link add must remove only newly added resources. Command-version conversion in `iwl_mld_send_sta_cmd()` assumes old firmware has exactly one link and no NAN/UHR-only fields. Removing AP keys before STA removal is required by firmware ordering. MPDU counters are per RXQ and use spinlocks; throughput unblock scheduling depends on window reset timing.

Test signals: Cover peer add/remove, restart ID reuse, failed add unwind, multi-link link add/remove transitions, TXQ/key/BAID resource mask changes, internal station queue allocation failure, AP key removal ordering, FW command version 2 vs newer, MPDU counter thresholds, and RCU lookup under notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.h

Purpose: Defines driver-private MLD station data structures and declares peer/internal station lifecycle helpers used across TX, RX, key, aggregation, TLC, and MLO code.

Important APIs and types: Defines duplicate-detection data (`iwl_mld_rxq_dup_data`), per-link station state (`iwl_mld_link_sta`), PTK PN storage, per-link/per-queue MPDU counters, main `iwl_mld_sta`, and internal firmware-only station state (`iwl_mld_int_sta`). Provides dereference/iteration helpers, cleanup helpers, mac80211 private-data casts, and declarations for station add/remove/update, TXQ flush/wait, MPDU counting, internal station add/remove, and link-station updates.

Control flow and integration: `iwl_mld_cleanup_sta()` is an inline cleanup path that removes TXQ private state, validates active-link cleanup, clears FW ID maps, and frees non-default link STAs. The header’s helpers are used by RX duplicate/reorder code, stats/TLC notification handling, key management, aggregation, and interface cleanup.

State and persistence: The zeroed-on-restart groups in station structs separate firmware-runtime fields from state that survives restart. `fw_id` and pointer topology survive so reconfiguration can preserve firmware station identity.

Dependencies: Includes mac80211, MLD core, and TX private helpers. It relies on RCU and the wiphy mutex for safe link station lookup.

Risks: `iwl_mld_cleanup_sta()` assumes failed link removal should be exceptional; if active link state is wrong it warns and force-clears maps. `IWL_NUM_DEFAULT_KEYS` and PN queue sizing must match key code expectations. Callers must not dereference link STAs without the documented lock/RCU protection.

Test signals: Compile and runtime coverage from station lifecycle, RX duplicate detection, stats/TLC notification lookup, MLO link update, and KUnit cleanup scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.c

Purpose: Bridges firmware statistics notifications to mac80211 station statistics, scan traffic-load heuristics, CQM RSSI notifications, MLO low-RSSI scans, EMLSR exits, and PHY channel-load state.

Important APIs and functions: `iwl_mld_request_periodic_fw_stats()` enables/disables periodic operational stats. `iwl_mld_clear_stats_in_fw()` requests on-demand reset notifications. `iwl_mld_mac80211_sta_statistics()` serves mac80211 station statistics. `iwl_mld_handle_stats_oper_notif()` processes operational notifications. `iwl_mld_handle_stats_oper_part1_notif()` is currently a placeholder.

Control flow: On-demand station statistics install waits for operational, part1, and end notifications, send `SYSTEM_STATISTICS_CMD`, fill signal average from per-STA data, then delete handlers so the response is not processed as general periodic data. Periodic notifications process per-link airtime/RSSI, per-STA average energy, and per-PHY channel load. Traffic load is recalculated from elapsed firmware timestamps and airtime, then stored in scan state to influence later scan type selection.

State and persistence: Updates `mld->scan.traffic_load`, each `iwl_mld_link_sta.signal_avg`, each PHY `channel_load_by_us` and averaged `avg_channel_load_not_by_us`, and link CQM RSSI last-event state. State is runtime-only but affects future scan, CQM, and EMLSR decisions.

Dependencies and integration points: Depends on firmware statistics ABI, notification wait infrastructure, station/link mapping, PHY/channel context iteration, scan internal MLO scan trigger, and MLO/EMLSR helpers. It integrates with mac80211 `sta_statistics`, CQM RSSI events, and EMLSR policy.

Risks: On-demand statistics are not EMLSR-ready and intentionally return nothing with more than one active link. Firmware timestamp wrap/short windows can skew traffic load. Per-STA lookup is through RCU/wiphy pointers and must tolerate removed stations. Invalid channel load over 100 is rejected. Signal value zero is treated as invalid and skipped.

Test signals: Cover periodic enable/disable command masks, on-demand wait success/timeout, signal average updates, traffic-load thresholds, CQM high/low hysteresis, low-RSSI MLO scan trigger, EMLSR low-RSSI exit, invalid PHY load rejection, and multi-link station-stat no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.h

Purpose: Declares the MLD firmware statistics control, mac80211 station statistics, and notification handlers.

Important APIs: Exports periodic statistics request, mac80211 station-stat callback, operational and part1 notification handlers, and firmware statistics clear.

Control flow and integration: The declarations connect mac80211 callbacks, RX notification dispatch, startup/shutdown periodic-stat configuration, and scan/EMLSR consumers implemented in `stats.c`.

State and persistence: Header owns no state. Implementations update scan traffic load, link signal averages, and PHY channel-load fields.

Dependencies: Relies on MLD, mac80211, station info, and firmware RX packet types supplied by includers.

Risks: `STATISTICS_OPER_PART1_NOTIF` is declared but implementation is TODO, so consumers must not assume part1 fields are processed.

Test signals: Build coverage for notification tables and mac80211 ops plus behavioral tests for periodic and on-demand stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/Makefile

Purpose: Builds the `iwlmld-tests` KUnit module when `CONFIG_IWLWIFI_KUNIT_TESTS` is enabled.

Important APIs and files: Aggregates `module.o`, `hcmd.o`, `utils.o`, `link.o`, `rx.o`, `agg.o`, and `link-selection.o`; adds the parent MLD directory to include paths; and registers `iwlmld-tests.o` as the config-selected object.

Control flow and integration: Kbuild compiles these test objects into one module that imports iwlwifi namespaces and runs KUnit suites registered by each source file.

State and persistence: No runtime state beyond Kbuild object membership.

Dependencies: Depends on KUnit, iwlwifi KUnit exports, and the parent MLD source include path.

Risks: New test files must be added to `iwlmld-tests-y` or they will silently not run. Include path drift can hide dependency problems.

Test signals: `CONFIG_IWLWIFI_KUNIT_TESTS=y/m` should build this module and list all suites in KUnit output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/agg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/agg.c

Purpose: Provides KUnit coverage for RX reorder-buffer behavior around BAID validity, multicast/non-QoS bypass, old/duplicate sequence handling, sequence-number wrap, holes, buffered release order, and A-MSDU subframe release.

Important APIs and functions: Defines parameterized `reorder_buffer_cases`, `test_reorder_buffer()`, fake static stubs for `iwl_mld_pass_packet_to_mac80211()` and `iwl_mld_fw_sta_id_mask()`, and helpers that build MPDU descriptors, SKBs, BAID state, and reorder buffer contents.

Control flow: Each test case creates an MLD station/VIF, prepares one incoming SKB and descriptor, installs BAID data into `mld->fw_id_to_ba`, invokes `iwl_mld_reorder()` under RCU, then asserts the reorder result, stored count, head sequence number, and exact release order captured by the fake pass-to-mac80211 stub.

State and persistence: Uses test-global `g_released_skbs` and `g_num_released_skbs` to capture releases for a single case. Allocated BAID, SKB, VIF, STA, and MLD state is KUnit-managed and discarded after each case.

Dependencies and integration points: Depends on KUnit, static stubs, KUnit SKB helpers, `utils.c` test setup, production `agg.h`, `rx.h`, and `sta.h`. It validates production reorder semantics without firmware.

Risks: The fake FW STA mask assumes only MLD link pointers set up by utils, not all production validation. Cases use a single queue and BA window size of 64, so multi-queue and nonstandard BA sizes need separate tests.

Test signals: Existing cases are strong signals for in-order, out-of-order, wrap, duplicate, old SN, invalid BAID, multicast, non-QoS, and A-MSDU behavior. Missing signals include timeout release, multiple queues, BA teardown races, and memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/agg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/hcmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/hcmd.c

Purpose: Verifies firmware host-command name metadata used by iwlwifi MLD debug/dispatch paths.

Important APIs and functions: `test_hcmd_names_sorted()` checks every populated command-name array is sorted by command ID. `test_hcmd_names_for_rx()` checks every MLD RX handler command ID resolves to a known command string through `iwl_get_cmd_string()`.

Control flow: The suite iterates exported `iwl_mld_groups` and `iwl_mld_rx_handlers`, using a synthetic `iwl_trans` command-group config for name lookup.

State and persistence: No persistent state. A stack `iwl_trans` is enough for command string lookup.

Dependencies and integration points: Imports the `EXPORTED_FOR_KUNIT_TESTING` namespace, depends on exported command group arrays and RX handler tables from production MLD code, and uses KUnit assertions.

Risks: The tests catch sortedness and unknown names but not semantic correctness of names or handler command IDs. Arrays hidden behind config conditionals may need build-variant coverage.

Test signals: KUnit should fail if new RX handlers lack command names or command arrays are appended out of order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/hcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link-selection.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link-selection.c

Purpose: Provides KUnit coverage for MLO link grading and EMLSR pair eligibility decisions.

Important APIs and functions: `test_link_grading()` validates `iwl_mld_get_link_grade()` under channel-util and active-load inputs. `test_iwl_mld_link_pair_allows_emlsr()` validates `iwl_mld_emlsr_pair_state()` for bandwidth ratio, channel load, low latency, primary-link activity, and same-band restrictions.

Control flow: Tests build synthetic associated MLO/non-MLO VIFs using `utils.c`, attach BSS load IEs or PHY channel load as needed, call production link-selection helpers under the wiphy lock, and compare exact grades or exit-reason bitmasks.

State and persistence: Uses KUnit-allocated VIF/link/chanctx/PHY objects and updates test PHY load fields. State is per-test only.

Dependencies and integration points: Depends on KUnit static stubs, MLD link/interface/PHY/MLO production headers, and shared channel definitions from `utils.h`. It exercises policy logic used by internal MLO scan completion and stats-triggered EMLSR decisions.

Risks: Expected grade values are policy-coupled and will need updates if scoring weights change. The cases cover representative pairs but not every regulatory/channel-width combination or RSSI threshold.

Test signals: Existing tests signal regressions in channel utilization grading, active-link load adjustment, EMLSR channel-load thresholds, low-latency override, bandwidth-ratio gating, and same-band disallow/allow cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link-selection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link.c

Purpose: Tests MLD missed-beacon handling around connection-loss decisions.

Important APIs and functions: Defines parameterized `missed_beacon_cases`, fake `ieee80211_connection_loss()`, and `test_missed_beacon()` which invokes `iwl_mld_handle_missed_beacon_notif()`.

Control flow: Each case creates a firmware missed-beacons notification packet, sets up either an EMLSR association or a non-MLO association, maps the firmware link ID, runs the notification handler under wiphy lock, and asserts whether association state was cleared by the fake connection-loss callback.

State and persistence: Per-test VIF association state is mutated to represent disconnect. No durable state.

Dependencies and integration points: Depends on production link notification handling, firmware MAC config notification layout, static stubbing of mac80211 connection loss, and common KUnit MLD setup helpers.

Risks: Current cases do not yet cover EMLSR-specific output despite the input field; a TODO notes ESR checks. The assertion uses association state as the observable proxy for connection loss.

Test signals: Covers below-threshold missed beacons, high total missed beacons with no since-last-RX loss, and disconnect when since-last-RX loss crosses threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/module.c

Purpose: Supplies module metadata for the aggregate iwlwifi MLD KUnit test module.

Important APIs and functions: Imports the `IWLWIFI` namespace and declares GPL license and module description.

Control flow and integration: No test logic. Kbuild links this object with the suite objects so the module has correct metadata and namespace imports.

State and persistence: No state.

Dependencies: Linux module infrastructure and iwlwifi exported namespace.

Risks: Missing namespace import can break modular KUnit builds if suite files reference iwlwifi exports.

Test signals: Build/load of `iwlmld-tests` confirms metadata is adequate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/rx.c

Purpose: Provides KUnit coverage for RX duplicate detection in `iwl_mld_is_dup()`.

Important APIs and functions: Defines parameterized `is_dup_cases`, helpers to initialize duplicate-data state and RX packet descriptors, and `test_is_dup()` which asserts duplicate decisions and RX status flags.

Control flow: Each case creates a station, seeds one queue of `iwl_mld_rxq_dup_data`, builds an 802.11 header and MPDU descriptor, calls `iwl_mld_is_dup()`, and checks whether the frame is dropped as duplicate plus whether `RX_FLAG_DUP_VALIDATED` or `RX_FLAG_ALLOW_SAME_PN` is set.

State and persistence: Per-test duplicate data stores last sequence and A-MSDU subframe index for a selected TID. State is KUnit-managed and not persistent.

Dependencies and integration points: Depends on production RX duplicate logic, station private data, iwl-trans structures, and utility setup. It models one RX queue.

Risks: Only single-queue duplicate state is exercised. Fragmented frames and hardware-provided duplicate status outside the modeled descriptor fields are not covered here.

Test signals: Existing cases cover control/null/multicast bypass, QoS and non-QoS sequence matching, retry-bit duplicate drops, invalid TID, and A-MSDU same-PN allowance by subframe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.c

Purpose: Provides shared KUnit construction helpers for synthetic MLD, VIF, link, station, channel context, notification packet, EMLSR association, and information-element objects.

Important APIs and functions: `iwlmld_kunit_test_init()` allocates and initializes a minimal `iwl_mld`. Helpers add VIFs, links, chanctxs, STAs, MLO associations, non-MLO associations, EMLSR dual-link associations, packets, elements, and PHY lookup by link.

Control flow: Test init allocates trans/cfg/fw/hw/wiphy, initializes wiphy mutex, calls `iwl_construct_mld()`, seeds firmware capability counts, allocates NVM data and a scan command buffer, and marks firmware running. Association helpers create VIF/link mappings, allocate FW IDs, assign channel contexts under wiphy lock, create authorized AP STAs, and set association state.

State and persistence: All objects are KUnit-allocated and scoped to a test. The helpers populate RCU pointer maps in VIF, STA, MLD, and link structures, plus firmware ID maps used by production functions.

Dependencies and integration points: Depends on KUnit, test-bug helpers, firmware scan/MAC definitions, MLD construction, interface/link/PHY/station allocation helpers, and shared channel definitions in `utils.h`.

Risks: The environment is intentionally partial: no real hw private area, TXQs are TODO, supported interface types are limited, and firmware/radio capabilities are simplified. Tests using these helpers must not assume full opmode-start parity.

Test signals: Provides reusable setup for RX, aggregation, link, and link-selection suites. Helper assertions catch invalid chandefs, missing link/channel pointers, and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.h

Purpose: Declares shared MLD KUnit helper APIs and static channel/channel-definition fixtures.

Important APIs and types: Declares `struct iwl_mld_kunit_link`, allocation assertion macros, VIF/link/chanctx/STA/association helpers, packet creation helper, EMLSR association helper, element generation helper, and PHY lookup helper. Defines reusable 2.4/5/6 GHz channels and a `CHANDEF_LIST` spanning 20 through 320 MHz widths.

Control flow and integration: Test sources include this header to build consistent synthetic mac80211/MLD topologies. `CHANDEF_LIST` also feeds a KUnit chandef-validity suite in `utils.c`.

State and persistence: Header-level static channel and chandef fixtures are compile-time test data.

Dependencies: Requires mac80211 and KUnit test-bug infrastructure; implementation lives in `utils.c`.

Risks: Static channel fixtures use `hw_value` equal to frequency, which is fine for tested policy but not a full hardware-channel model. Helper macros assert allocation success and abort tests, so they are not suitable for negative allocation-path tests.

Test signals: Build and KUnit usage across all MLD suites; invalid chandef definitions are caught by `iwlmld_valid_test_chandefs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.c

Purpose: Implements MLD thermal handling: CT-kill notification and delayed recovery, firmware temperature threshold configuration, Linux thermal zone registration, cTDP cooling-device control, and platform power-budget selection.

Important APIs and functions: `iwl_mld_handle_ct_kill_notif()` enters CT-kill and schedules exit. `iwl_mld_handle_temp_notif()` handles DTS threshold notifications. `iwl_mld_config_temp_report_ths()` sends firmware trip thresholds. Under `CONFIG_THERMAL`, thermal zone ops read temperature and update trips, cooling ops map cooling state to cTDP budget through `iwl_mld_config_ctdp()`. `iwl_mld_thermal_initialize()` and `iwl_mld_thermal_exit()` manage lifecycle.

Control flow: Initialization sets up delayed CT-kill exit work, computes max power budget from RF type and BIOS power limit, and optionally registers thermal cooling and zone devices. CT-kill notifications set ctkill true and schedule a delayed work to clear it. Thermal-zone trip changes compress/sort configured trip temperatures and send them to firmware. Cooling state changes scale linearly from max power budget down to a minimum cTDP budget and send `CTDP_CONFIG_CMD`.

State and persistence: Mutates `mld->power_budget_mw`, `mld->cooling_dev.cur_state/cdev`, `mld->tzone`, and ctkill state. Runtime only; BIOS/ACPI power limit is read during initialization but not persisted by this code.

Dependencies and integration points: Depends on firmware PHY thermal APIs, iwl BIOS power-limit helper, Linux thermal framework, wiphy delayed work and locking, transport RF ID macros, and MLD ctkill state setter.

Risks: Temperature unit conversions cross Celsius, millicelsius, signed 16-bit firmware thresholds, and firmware response values. Thermal callbacks must handle firmware not running. Budget scaling assumes `power_budget_mw >= IWL_MLD_MIN_CTDP_BUDGET_MW`. Registration failure paths set pointers to NULL but thermal-zone enable failure unregisters without explicitly clearing in the shown path.

Test signals: Cover CT-kill enter/exit scheduling, negative temperature rejection, threshold index bounds, trip compression/sort, get-temp response length failure, cTDP state range and budget math, BIOS limit selection, and init/exit with and without `CONFIG_THERMAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.h

Purpose: Declares MLD thermal notification, threshold configuration, cTDP, and lifecycle APIs, with optional Linux thermal-framework state.

Important APIs and types: Under `CONFIG_THERMAL`, defines `struct iwl_mld_cooling_device` and declares `iwl_mld_config_ctdp()`. Always declares temp and CT-kill notification handlers, threshold configuration, thermal initialize, and thermal exit.

Control flow and integration: Included by MLD core setup and notification dispatch so thermal support can be compiled both with and without Linux thermal framework support.

State and persistence: Cooling-device state tracks current cooling state and registered thermal cooling device pointer when enabled.

Dependencies: Includes `iwl-trans.h`, optional `<linux/thermal.h>`, and forward declares `struct iwl_mld`.

Risks: Callers behind `CONFIG_THERMAL` must guard `iwl_mld_config_ctdp()` usage. Non-thermal builds still need CT-kill and firmware threshold handling.

Test signals: Build matrix coverage with `CONFIG_THERMAL=y` and disabled, plus notification dispatch compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.c

Purpose: Implements MLD time-synchronization support for 802.11v timing measurement and FTM frames, pairing queued SKBs with firmware timestamp notifications and reporting adjusted PTP timestamps to mac80211.

Important APIs and functions: `iwl_mld_time_sync_config()` configures the single supported peer/protocol set. `iwl_mld_time_sync_fw_config()` sends firmware configuration. `iwl_mld_deinit_time_sync()` tears down RCU state and queued frames. `iwl_mld_time_sync_frame()` intercepts matching timing/FTM frames. `iwl_mld_handle_time_msmt_notif()` and `iwl_mld_handle_time_sync_confirm_notif()` attach RX/TX timestamps and deliver frames/status.

Control flow: Configuration rejects a different active peer, validates protocol bits, replaces existing state, and sends firmware config. Matching frames are queued on `time_sync->frame_list`. Notification handlers find the first queued SKB matching peer address and dialog token, dropping older unmatched SKBs, convert firmware 10 ns timestamp pairs to adjusted PTP nanoseconds under `ptp_data.lock`, write hardware timestamp fields, and call `ieee80211_rx_napi()` or `ieee80211_tx_status_ext()`.

State and persistence: `struct iwl_mld_time_sync_data` is RCU-protected and stores peer address, active protocol mask, and queued SKBs. Deinit purges the queue and frees via RCU. No durable persistence.

Dependencies and integration points: Depends on MLD command dispatch, PTP adjustment helper, mac80211 frame classifiers/status APIs, SKB queues, RCU, and firmware WNM timing measurement config/notification ABI.

Risks: Firmware supports one peer only; attempts to configure another active peer return `-ENOBUFS`. Queue matching assumes notifications arrive in frame order and drops unmatched queued frames. Dequeue occurs while an RCU read lock is held; teardown must purge safely. Missing notifications leak queued frames until deinit or a later mismatch drains them.

Test signals: Cover peer reconfiguration, invalid protocol mask, FW config failure, RX and TX notification timestamp conversion, dialog-token mismatch drop, missing state notification warning, queue purge on deinit, and concurrent frame enqueue/deinit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.h

Purpose: Defines time-sync runtime state and declares MLD time-sync configuration, frame interception, deinit, and notification handlers.

Important APIs and types: `struct iwl_mld_time_sync_data` holds RCU head, peer address, active protocols, and pending frame queue. APIs configure firmware, configure/replace local state, deinitialize, intercept frames, and handle measurement/confirm notifications.

Control flow and integration: Used by TX/RX paths to queue timing/FTM frames and by firmware notification dispatch to attach timestamps and complete mac80211 delivery.

State and persistence: Time-sync state is RCU-protected and runtime-only. Queued SKBs are owned by this subsystem until notification delivery, drop, or deinit.

Dependencies: Requires Ethernet address size, SKB queue types, RCU, MLD core, and firmware RX packet types via includers.

Risks: Ownership transfer of SKBs is implicit in `iwl_mld_time_sync_frame()` returning true; callers must not free queued frames.

Test signals: Compile coverage plus behavioral tests for accepted/rejected frame ownership and notification completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.c

Purpose: Builds and sends firmware TLC/rate-control configuration for MLD link stations, translates mac80211 HT/VHT/HE/EHT/UHR capabilities into firmware rate bitmaps/flags, handles TLC debug host commands, updates TLC configuration after PHY changes, and processes TLC notifications for last TX rate and A-MSDU limits.

Important APIs and functions: `iwl_mld_config_tlc_link()` configures one link STA. `iwl_mld_config_tlc()` configures all active links for a station. `iwl_mld_tlc_update_phy()` refreshes stations on a link after PHY/channel context changes. `iwl_mld_send_tlc_dhc()` sends TLC debug host commands. `iwl_mld_handle_tlc_notif()` processes rate and A-MSDU updates.

Control flow: TLC config computes max channel width, feature flags, valid chains, SGI support, max MPDU/A-MSDU length, PHY ID, non-HT rates, and HT/VHT/HE/EHT/UHR MCS bitmaps. It then adapts the generic v6 command to firmware command versions 6, 5, or 4 and sends it asynchronously. Notifications validate station ID, update `last_rate_n_flags` from firmware rate encoding, then optionally update max RC A-MSDU and per-TID A-MSDU lengths constrained by TX FIFO sizes.

State and persistence: Updates link STA `last_rate_n_flags`, `link_sta->agg.max_rc_amsdu_len`, `max_tid_amsdu_len[]`, and aggregate recalculation. Reads station state to limit AP-mode channel width before authorization and to disable A-MSDU before association. State is runtime-only.

Dependencies and integration points: Depends on mac80211 capabilities, MLD station/link/PHY helpers, firmware RS/TLC/DHC ABIs, valid antenna helpers, firmware shared memory TX FIFO sizes, and mac80211 aggregate recalculation. It is called from station add/update and PHY change paths.

Risks: Capability translation is standards-dense and easy to regress for EHT/UHR, SMPS static NSS limits, 20 MHz-only cases, 160/320 MHz support, and own-vs-peer MCS intersections. Older command-version conversion requires a single STA bit in `sta_mask`. A-MSDU notification sizes below 2000 are forced off, and sizes above mac80211 max are rejected. Async command send means callers cannot assume immediate firmware state.

Test signals: Cover HT/VHT/HE/EHT/UHR rate bitmap construction, LDPC/STBC/DCM/extra-LTF/UHR flags, SMPS static behavior, firmware command versions 4/5/6, AP pre-authorization 20 MHz limiting, PHY update skipping stations not in FW, TLC notification rate conversion, invalid STA ID, and A-MSDU per-TID FIFO limiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.h

Purpose: Declares MLD TLC/rate-control configuration and notification APIs.

Important APIs: Exports link-level and station-level TLC configuration, TLC notification handling, debug host command send, and PHY-update-triggered TLC refresh.

Control flow and integration: Used by station lifecycle, link/PHY change handling, and RX notification dispatch to keep firmware rate-control state synchronized with mac80211 station/link capabilities.

State and persistence: Header owns no state. Implementations update firmware TLC objects, link last-rate fields, and mac80211 aggregation limits.

Dependencies: Includes MLD core types and relies on mac80211 VIF/BSS/STA types from includers.

Risks: Callers generally need the wiphy lock and valid link/channel context. Misordered calls before station firmware upload are skipped or can warn.

Test signals: Build coverage through station and notification paths plus behavior tests for config and notification handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.h -->
