# subset-b-004837 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.c

## Purpose

`sta.c` is the non-MLD iwlwifi MVM station-management implementation. It owns the host-side representation of mac80211 stations in firmware station IDs, sends `ADD_STA`, `REMOVE_STA`, `ADD_STA_KEY`, BAID, SCD queue, and channel-switch related commands, and maintains the driver state needed by TX/RX fast paths. It bridges mac80211 station lifecycle callbacks to firmware station table entries and also manages internal stations used for auxiliary scan/ROC, sniffer, broadcast, and multicast traffic.

The file also implements Dynamic Queue Allocation for older TX APIs and TVQM queue allocation for newer TX APIs. Its queue logic decides when a station/TID gets a dedicated queue, when queues are shared, how inactive queues are reclaimed, and how queues are restored after firmware restart.

## Important APIs, types, and functions

Key public station lifecycle APIs are `iwl_mvm_find_free_sta_id()`, `iwl_mvm_sta_init()`, `iwl_mvm_add_sta()`, `iwl_mvm_sta_send_to_fw()`, `iwl_mvm_rm_sta()`, `iwl_mvm_rm_sta_id()`, and `iwl_mvm_sta_del()`. Firmware station table state is tracked through `mvm->fw_id_to_mac_id[]`, with normal stations stored as RCU pointers and internal stations represented by `ERR_PTR(-EINVAL)`.

Queue APIs include `iwl_mvm_sta_ensure_queue()`, `iwl_mvm_add_new_dqa_stream_wk()`, `iwl_mvm_tvqm_enable_txq()`, and `iwl_mvm_realloc_queues_after_restart()`. Legacy DQA helpers include `iwl_mvm_find_free_queue()`, `iwl_mvm_sta_alloc_queue()`, `iwl_mvm_get_shared_queue()`, `iwl_mvm_redirect_queue()`, `iwl_mvm_remove_inactive_tids()`, and `iwl_mvm_inactivity_check()`.

Aggregation and reorder handling is centered on `iwl_mvm_sta_rx_agg()`, `iwl_mvm_sta_tx_agg_start()`, `iwl_mvm_sta_tx_agg_oper()`, `iwl_mvm_sta_tx_agg_stop()`, `iwl_mvm_sta_tx_agg_flush()`, `iwl_mvm_fw_baid_op()`, and the RX reorder buffer helpers. Key installation/removal is handled by `iwl_mvm_set_sta_key()`, `iwl_mvm_remove_sta_key()`, `iwl_mvm_update_tkip_key()`, `iwl_mvm_send_sta_key()`, and `iwl_mvm_send_sta_igtk()`.

Power-save and traffic-blocking helpers include `iwl_mvm_sta_modify_ps_wake()`, `iwl_mvm_sta_modify_sleep_tx_count()`, `iwl_mvm_rx_eosp_notif()`, `iwl_mvm_sta_modify_disable_tx_ap()`, `iwl_mvm_modify_all_sta_disable_tx()`, and `iwl_mvm_csa_client_absent()`.

## Control flow

Adding a station starts with station ID allocation unless firmware restart is in progress, in which case the previous ID is reused. `iwl_mvm_sta_init()` initializes the embedded `struct iwl_mvm_sta`, per-TID queue state, duplicate RX data, rate-scaling state, and legacy queue reservation. `iwl_mvm_sta_send_to_fw()` builds the firmware `ADD_STA` command from mac80211 capabilities: bandwidth, RX NSS, SMPS mode, aggregation density/size, AID, U-APSD ACs, station type, and legacy queue mask. After successful firmware addition, the station is published in `fw_id_to_mac_id[]` under RCU.

Removing a station drains firmware traffic, flushes the station queues, waits for queues to empty, clears drain state, disables per-TID TX queues, releases reserved queue state, runs common AP/TDLS cleanup in `iwl_mvm_sta_del()`, sends `REMOVE_STA`, and clears the RCU map. Internal stations follow the same firmware commands but use `iwl_mvm_int_sta` and fixed queues for aux/sniffer/broadcast/multicast roles.

Legacy DQA queue allocation first tries management queues for management TID, then reserved station queues, then free data queues, then inactive queue reclamation, and finally shared queues. Shared queues disable aggregation for active TIDs on that queue and may redirect the scheduler FIFO to the lowest-priority AC represented. Inactive cleanup scans all queue TIDs, skips queues with queued frames or active BA state, unshares single-TID queues, and changes queue ownership if the owner TID was removed.

TX aggregation starts by reserving or validating a queue, recording SSN, and returning whether mac80211 can send ADDBA immediately or must wait for the queue to empty. Operational start marks `IWL_AGG_ON`, configures SCD aggregation window where supported, enables firmware aggregation through `ADD_STA`, and updates rate-scaling aggregation limits. Stop/flush paths clear state, notify mac80211, drain/flush hardware queues when needed, and disable firmware aggregation.

RX aggregation allocates firmware BAID sessions. On new RX APIs it allocates per-RXQ reorder buffers, initializes timers, stores BAID data in `mvm->baid_map[]` under RCU, and synchronizes RX queues before removal. A session timer calls mac80211 BA timeout handling if firmware traffic has not refreshed `last_rx`.

Key setup selects station ID from a station, AP station, or AP multicast station, assigns or reuses firmware key offsets, formats cipher-specific flags and PN state, and sends `ADD_STA_KEY` or `MGMT_MCAST_KEY`. Removal clears the key table, updates LRU-like deletion counters, and sends invalidation commands. TKIP update can send an asynchronous updated phase-1 key.

## State and persistence

Persistent driver state includes `mvm->fw_id_to_mac_id[]`, `mvm->queue_info[]`, `mvm->tvqm_info[]`, `mvm->fw_key_table`, `mvm->fw_key_deleted[]`, `mvm->rx_ba_sessions`, `mvm->baid_map[]`, and status bits for restart/CSA. Per-station state lives in `struct iwl_mvm_sta`: firmware station ID, MAC context color, queue mask, reserved queue, per-TID sequence/reclaim/aggregation data, TID-to-BAID map, key PN storage, duplicate detection state, sleep state, TX-disable state, and rate-scaling data.

Queue and aggregation state persists across firmware restart by reusing station IDs and re-enabling queues with `iwl_mvm_realloc_queues_after_restart()`. New TX API queues are reallocated by transport, while legacy DQA queues are re-enabled with the saved TXQ IDs. Some counters, especially sequence tracking on gen2, are intentionally reset or masked to match firmware behavior.

## Dependencies and integration points

This file depends on mac80211 station/TXQ/key/BA APIs, firmware command structures from `fw-api.h`, transport TXQ primitives, rate scaling, RCU synchronization, the MVM mutex, per-station spinlocks, notification synchronization, and MLD equivalents for paths delegated when `mvm->mld_api_is_used` is true. It is called from station state transitions, TX path queue activation, TX reclaim/BA notifications, RX reorder handling, AP power-save hooks, TDLS/CSA handling, and key configuration callbacks.

## Risks

The highest risk is state skew between mac80211, driver maps, transport queues, and firmware station table entries. Queue reuse is especially delicate: stale `txq_id`, missing `synchronize_net()`, incorrect shared-queue ownership, or incomplete aggregation disabling can cause frames to be sent to freed or misconfigured queues. Firmware API version gates are also risk-heavy because the file supports old SCD/DQA, new TX API/TVQM, old and new RX BAID APIs, station API variants, and key-command versions.

Security-sensitive risks include incorrect PN conversion, key slot reuse, multicast/pairwise selection, TKIP MIC handling, and invalid station lookup during GTK/IGTK removal. RX reorder data is freed under RCU and synchronized RX queue notifications; bugs there can produce use-after-free or leaked buffered frames. Restart paths intentionally skip some firmware removals, so they must keep local state consistent enough for mac80211 reconfiguration.

## Test signals

Useful signals include KUnit or mock firmware command tests for ADD/REMOVE station command contents, queue allocation/reclaim/share cases, restart reallocation, BAID allocation/removal, key slot LRU behavior, and PN formatting. Runtime validation should exercise AP/client/TDLS/internal stations, firmware restart, queue exhaustion, aggregation start/stop/flush, RX BA timeout, U-APSD EOSP, CSA absent handling, WEP/TKIP/CCMP/GCMP/IGTK keys, and both legacy and new TX/RX firmware APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.h

## Purpose

`sta.h` is the station-management contract for the MVM driver. It documents the station table model, DQA queue policy, internal station roles, AP power-save behavior, firmware restart assumptions, and exposes the data structures and APIs implemented by `sta.c` and newer MLD station code.

## Important APIs and types

The main types are `enum iwl_mvm_agg_state`, `struct iwl_mvm_tid_data`, `struct iwl_mvm_key_pn`, `struct iwl_mvm_rxq_dup_data`, `struct iwl_mvm_link_sta`, `struct iwl_mvm_sta`, `struct iwl_mvm_int_sta`, and `struct iwl_mvm_sta_state_ops`. `struct iwl_mvm_sta` is embedded in mac80211 station private data and stores per-station queue masks, firmware IDs, aggregation state, key PN state, duplicate detection, power-save state, TX disable state, rate-scaling link data, and MLO link station pointers. `struct iwl_mvm_int_sta` is the reduced representation for firmware-only stations.

Public prototypes cover station add/update/remove, queue restoration, key install/remove/update, RX/TX aggregation, internal station management, broadcast/multicast station setup, AP power-save controls, disable-TX handling, CSA cancellation, and MLD-specific station and queue APIs.

## Control flow and state model

The header describes station creation through mac80211 `sta_state`, firmware publication through `ADD_STA`, and RCU lookup through `fw_id_to_mac_id`. It establishes the locking split: `mvm->mutex` serializes station table writers, RCU protects fast readers, and `mvm_sta->lock` protects per-station sequence and BA/TID state reachable from softirq and response paths.

DQA documentation records the queue allocation policy: some queues remain static, dynamic queues are allocated on demand by RA/TID, management traffic is treated as TID 8, new stations reserve a data queue, and exhausted pools can force per-station shared queues. Restart documentation states that embedded mac80211 private station data survives firmware reset and must be reinitialized or reused carefully.

## Dependencies and integration points

The header depends on Linux spinlocks, wait queues, mac80211 station/vif/key types, `iwl-trans.h` for TID count, firmware station limits from `fw-api.h`, and rate-scaling types from `rs.h`. It is included by station implementation, TX/RX paths, MAC state handlers, TDLS, thermal/disable-TX users, and MLD station code.

## Risks

Because this header defines shared state layout, changes can break assumptions in interrupt/softirq paths, firmware restart, MLD link handling, and station private data sizing. The documented locking rules are essential; bypassing them can corrupt sequence counters, BA state, key PN pointers, or RCU station lookups. Non-MLO and MLO link fields coexist, so callers must use the correct `deflink` or link-indexed pointer.

## Test signals

Compile coverage across MLD and non-MLD builds is the first signal. Behavioral tests should cover station lifecycle, queue allocation, restart reconfiguration, AP power-save, aggregation transitions, key install/remove, and internal station setup. Static analysis should verify RCU annotations and spinlock-protected fields are used consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tdls.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tdls.c

## Purpose

`tdls.c` manages Tunneled Direct Link Setup support for MVM, with emphasis on TDLS peer tracking, firmware TDLS configuration, TDLS discovery protection, and TDLS channel-switch state. It coordinates mac80211 TDLS operations with firmware commands and the MVM time-event/session-protection layer.

## Important APIs and functions

Peer lifecycle helpers are `iwl_mvm_teardown_tdls_peers()`, `iwl_mvm_tdls_sta_count()`, and `iwl_mvm_recalc_tdls_state()`. Channel-switch functions include `iwl_mvm_tdls_channel_switch()`, `iwl_mvm_tdls_cancel_channel_switch()`, `iwl_mvm_tdls_recv_channel_switch()`, `iwl_mvm_rx_tdls_notif()`, and delayed work `iwl_mvm_tdls_ch_switch_work()`. Internal helpers `iwl_mvm_tdls_check_action()`, `iwl_mvm_tdls_config_channel_switch()`, and `iwl_mvm_tdls_update_cs_state()` implement the channel-switch state machine.

## Control flow

TDLS peer teardown scans firmware station IDs under `mvm->mutex`, filters valid TDLS stations, and asks mac80211 to issue teardown operations. Recalculation counts peers for a VIF, updates power when the first peer is added or last peer removed, and sends `TDLS_CONFIG_CMD` when firmware advertises TDLS channel-switch capability.

TDLS discovery protection schedules session protection for two DTIM periods, using the newer session-protection command when available and legacy time events otherwise. Channel switch setup validates the requested action against current state and peer identity, finds the mac80211 station, chooses the requested peer channel or base channel, embeds the TDLS action frame and TX command metadata, sends `TDLS_CHANNEL_SWITCH_CMD`, and updates `mvm->tdls_cs` state. Firmware notifications move the state to active and schedule delayed retry/return work; cancellation clears the stored peer template and may wait a DTIM for PHY return to base channel.

## State and persistence

TDLS channel-switch state is stored in `mvm->tdls_cs`: current state, current firmware station ID, peer station ID, peer channel definition, initiator flag, operating class, copied template SKB, timing IE offset, and request timestamp. Only one switching peer is supported at a time. The state machine protects against stale responses, competing peers, duplicate requests, and invalid move-channel actions.

## Dependencies and integration points

The file depends on mac80211 TDLS APIs, firmware `TDLS_CONFIG_CMD` and `TDLS_CHANNEL_SWITCH_CMD`, MVM station lookup from `fw_id_to_mac_id`, channel formatting helpers, TX command setup helpers, and time-event/session-protection APIs. It integrates with station removal, power management, and delayed work on `system_percpu_wq`.

## Risks

The main risks are stale or conflicting TDLS action frames, single-peer assumptions, copied SKB lifetime, and races between cancellation, firmware notifications, station removal, and delayed retry work. Channel selection depends on valid chandef or base-channel RCU access. Incorrect state transitions can leave the PHY off-channel too long or repeatedly retry a failed peer.

## Test signals

Tests should cover peer count/power-update transitions, firmware config generation, discovery protection duration, outgoing and incoming channel-switch requests/responses, stale timestamp rejection, peer mismatch rejection, cancellation during active switch, station removal during TDLS work, and fallback between session-protection and legacy protection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tdls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/testmode.h

## Purpose

`testmode.h` defines the nl80211 testmode attribute and command IDs understood by the MVM driver testmode implementation. It is a small shared contract rather than executable code.

## Important APIs and types

`enum iwl_mvm_testmode_attrs` defines nested testdata attributes: command selector, NoA duration, and beacon-filter state. `enum iwl_mvm_testmode_commands` defines `IWL_MVM_TM_CMD_SET_NOA` for GO NoA testing and `IWL_MVM_TM_CMD_SET_BEACON_FILTER` for toggling beacon filtering.

## Control flow, state, and dependencies

The file has no control flow or persistent state. It depends only on consumers using the enum values consistently when parsing `NL80211_ATTR_TESTDATA`. The command handlers elsewhere translate these enum values into driver or firmware operations.

## Risks

The risk is ABI drift: changing enum order or max values can break userspace test tools. Attribute validation must be strict in the consumer because this header does not encode type policy beyond comments.

## Test signals

Test signals are compile coverage and testmode parser tests that reject unknown attributes, require `IWL_MVM_TM_ATTR_CMD`, validate u32 payloads, and exercise NoA/beacon-filter command dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/Makefile

## Purpose

This Makefile wires the MVM KUnit test module into the kernel build. It builds `module.o` and `hcmd.o` into `iwlmvm-tests.o` when `CONFIG_IWLWIFI_KUNIT_TESTS` is enabled.

## APIs, control flow, and dependencies

The file uses standard kbuild variables: `iwlmvm-tests-y` lists objects in the composite test module, and `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS)` conditionally includes it. It depends on the surrounding iwlwifi kbuild context and the KUnit config symbol.

## Risks and test signals

Risks are minimal but include forgotten object additions when new KUnit files are added or missing config dependencies. The signal is a successful kernel/KUnit build with `CONFIG_IWLWIFI_KUNIT_TESTS=y` or `m`, and successful loading/running of the `iwlmvm-tests` suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/hcmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/hcmd.c

## Purpose

`hcmd.c` contains a KUnit test for MVM host-command name metadata. It verifies that command-name arrays are sorted by command ID, which supports deterministic lookup behavior in debug/trace helpers.

## Important APIs and control flow

`test_hcmd_names_sorted()` iterates over `iwl_mvm_groups[]`, skips empty arrays, and checks each adjacent command ID with `KUNIT_EXPECT_LE()`. The file registers the case in `hcmd_names_cases`, wraps it in `struct kunit_suite hcmd_names`, and exposes it via `kunit_test_suite()`.

## State, dependencies, and integration

The test has no persistent state. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace, includes `<kunit/test.h>`, `<iwl-trans.h>`, and `../mvm.h`, and depends on exported `iwl_mvm_groups` and `iwl_mvm_groups_size` metadata from the driver.

## Risks and test signals

The test catches unsorted command-name tables but does not verify names, coverage completeness, duplicate IDs, or group ordering. A passing KUnit run for suite `iwlmvm-hcmd-names` is the primary signal; failures identify a table index where command IDs are out of order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/hcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/module.c

## Purpose

`module.c` is boilerplate for the MVM KUnit test module. It supplies module metadata so the composite `iwlmvm-tests` object has a GPL license and a description.

## APIs, control flow, and state

The file includes `<linux/module.h>` and uses `MODULE_LICENSE("GPL")` and `MODULE_DESCRIPTION("kunit tests for iwlmvm")`. It has no functions, runtime control flow, or persistent state.

## Dependencies, risks, and test signals

It depends on kbuild linking it with the actual test objects. The main risk is missing or wrong license metadata, which can affect symbol access and module loading. The validation signal is successful build/load of the KUnit test module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.c

## Purpose

`time-event.c` implements firmware time-event orchestration for MVM. Time events and session-protection commands reserve channel presence for association, P2P remain-on-channel, hotspot/AUX ROC, and channel-switch absence periods. The file tracks event lifetimes, handles firmware notifications, cleans up off-channel queues and temporary stations, and reports readiness/expiration to mac80211.

## Important APIs and functions

Public APIs include `iwl_mvm_protect_session()`, `iwl_mvm_stop_session_protection()`, `iwl_mvm_schedule_session_protection()`, `iwl_mvm_rx_session_protect_notif()`, `iwl_mvm_start_p2p_roc()`, `iwl_mvm_stop_roc()`, `iwl_mvm_rx_roc_notif()`, `iwl_mvm_rx_time_event_notif()`, `iwl_mvm_cleanup_roc_te()`, `iwl_mvm_roc_done_wk()`, `iwl_mvm_remove_time_event()`, `iwl_mvm_te_clear_data()`, `iwl_mvm_schedule_csa_period()`, and `iwl_mvm_remove_csa_period()`.

Important helpers include `iwl_mvm_time_event_send_add()` for legacy `TIME_EVENT_CMD` add/response handling, `__iwl_mvm_remove_time_event()` for synchronized teardown across legacy TE/session-protection/ROC command variants, `iwl_mvm_te_handle_notif()` for start/end notification dispatch, and `iwl_mvm_roc_duration_and_delay()` for DTIM-aware AUX ROC scheduling.

## Control flow

Legacy time-event add first records `te_data` under `time_event_lock`, registers a notification waiter for the command response so the UID is captured in RX context, sends `TIME_EVENT_CMD`, and clears state on failure. If the caller needs to wait for start, it also waits for `TIME_EVENT_NOTIFICATION`. Start notifications mark `running`, compute `end_jiffies`, and notify mac80211 for P2P ROC or CSA. End notifications expire ROC, trigger cleanup work, handle station association failures, and clear the event.

Session-protection-capable firmware uses `SESSION_PROTECTION_CMD` and `SESSION_PROTECTION_NOTIF` instead of legacy TEs. The code reuses `time_event_data.id` for session-protection configuration IDs. Non-P2P notifications maintain association/session state and can trigger connection loss if protection ends before association/beacon reception. P2P notifications map to remain-on-channel ready/expired callbacks.

ROC control supports several firmware paths: legacy P2P_DEVICE TEs, session-protection P2P ROC, generic `ROC_CMD`, and AUX/hotspot time events. Stop paths select the matching removal command, set status bits if cleanup must run before start notification arrives, flush aux or P2P queues, remove temporary internal/broadcast stations, and leave PHY context cached when useful.

CSA scheduling removes any association protection that would conflict, sends a `TE_CHANNEL_SWITCH_PERIOD` absence event, and on start either completes AP NoA/CSA timing or disables TX for station-mode CSA. Failure paths flag AP CSA failure or report connection loss for station mode.

## State and persistence

State lives in `struct iwl_mvm_time_event_data` instances on VIFs and the `mvm->time_event_list` / `mvm->aux_roc_te_list`. Fields include UID, firmware ID/config ID, VIF pointer, duration, running flag, and estimated end time. Driver-wide status bits `IWL_MVM_STATUS_ROC_P2P_RUNNING` and `IWL_MVM_STATUS_ROC_AUX_RUNNING` gate off-channel TX and cleanup. `mvmvif->roc_activity` tracks `ROC_CMD` activities. `mvm->csa_vif` links CSA NoA completion to the affected interface.

## Dependencies and integration points

The file depends on firmware notification waits, MVM command send helpers, mac80211 remain-on-channel and CSA APIs, station/broadcast/aux cleanup, binding/link management, P2P over AUX capability checks, and firmware debug triggers. Locking uses `mvm->mutex` for command-level serialization and `time_event_lock` for event list/state mutation.

## Risks

The main risks are races between command response, start/end notification, explicit removal, VIF removal, and cleanup work. The code deliberately handles notifications arriving after cancellation and stop calls before start notifications, but wrong status-bit or `te_data` handling can leak off-channel queues, leave temporary stations in firmware, or drop valid TX. Firmware API branching is complex: legacy TE, session protection, HOT_SPOT, and ROC_CMD paths must remove the same logical operation differently. Association protection failure handling can trigger connection loss, so false failure interpretation has user-visible impact.

## Test signals

Validation should include association protection success, timeout, extension, and cancellation; P2P ROC normal and management-TX flows; AUX/hotspot ROC duration clamping around DTIM; stop-before-start races; VIF removal with pending ROC; CSA AP and STA flows; firmware notification failure statuses; and both legacy time-event and session-protection firmware capabilities. Debug traces `IWL_DEBUG_TE`, mac80211 ready/expired callbacks, queue flushes, and absence of leaked `te_data` entries are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.h

## Purpose

`time-event.h` documents the MVM time-event abstraction and declares the public API for reserving channel presence, remain-on-channel operations, channel-switch absence periods, and session protection.

## Important APIs

The header exposes legacy time-event/session APIs `iwl_mvm_protect_session()`, `iwl_mvm_stop_session_protection()`, `iwl_mvm_remove_time_event()`, `iwl_mvm_te_clear_data()`, and `iwl_mvm_rx_time_event_notif()`. ROC APIs are `iwl_mvm_start_p2p_roc()`, `iwl_mvm_stop_roc()`, `iwl_mvm_rx_roc_notif()`, `iwl_mvm_cleanup_roc_te()`, and `iwl_mvm_roc_done_wk()`. CSA/session-protection APIs are `iwl_mvm_schedule_csa_period()`, `iwl_mvm_remove_csa_period()`, `iwl_mvm_schedule_session_protection()`, and `iwl_mvm_rx_session_protect_notif()`. `iwl_mvm_te_scheduled()` is a small inline helper that treats nonzero UID as scheduled.

## Control flow and state

The header-level documentation explains the firmware flow: send `TIME_EVENT_CMD`, capture a UID from the response, and then process start/end notifications. It abstracts those details for callers that need association protection or off-channel availability. The declared functions operate on `struct iwl_mvm_time_event_data` fields stored elsewhere, primarily on VIF objects.

## Dependencies and integration

It includes `fw-api.h` and `mvm.h`, so it is tightly bound to firmware command IDs and core MVM/VIF structures. Callers include association code, TDLS discovery protection, remain-on-channel operations, CSA handling, and VIF cleanup paths.

## Risks and tests

The header itself has little logic, but its comments describe timing-sensitive behavior. API misuse risks include calling without required locks, forgetting to stop protection, or treating `iwl_mvm_te_scheduled()` as proof the event started rather than proof a UID exists. Compile tests plus functional ROC/session/CSA tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.c

## Purpose

`time-sync.c` supports firmware-assisted timestamping for 802.11 timing measurement and FTM frames. It queues a pending management frame, matches firmware time measurement notifications by peer and dialog token, converts firmware 10 ns timestamps into adjusted PTP time, and reports the completed frame through mac80211 RX or TX status paths.

## Important APIs and functions

Public functions are `iwl_mvm_init_time_sync()`, `iwl_mvm_time_sync_msmt_event()`, `iwl_mvm_time_sync_msmt_confirm_event()`, and `iwl_mvm_time_sync_config()`. Internal helpers `iwl_mvm_is_skb_match()`, `iwl_mvm_time_sync_find_skb()`, and `iwl_mvm_get_64_bit()` match frames and combine high/low timestamp words.

## Control flow and state

Initialization sets up `mvm->time_sync.frame_list`. TX/RX code queues candidate frames through the inline helper in the header. When a measurement event arrives, the code dequeues frames until it finds one matching the notification peer address and dialog token, discarding obsolete frames. RX measurement events fill `skb_hwtstamps(skb)->hwtstamp` with T2 and `IEEE80211_SKB_RXCB(skb)->ack_tx_hwtstamp` with T3, then inject the frame via `ieee80211_rx_napi()`. Confirmation events fill TX hwtstamp T1 and ACK hwtstamp T4, then report via `ieee80211_tx_status_ext()`.

Configuration validates firmware capability, enforces a single active peer unless reconfiguring the same address, validates the protocol mask for TM/FTM only, sends `WNM_80211V_TIMING_MEASUREMENT_CONFIG_CMD`, updates active state and peer address on success, and purges queued frames when disabling.

## Dependencies and integration

The file depends on firmware time-sync notifications and config command structures, mac80211 SKB timestamp/status APIs, PTP adjustment via `iwl_mvm_ptp_get_adj_time()`, and action-frame parsers `ieee80211_is_timing_measurement()` / `ieee80211_is_ftm()`.

## Risks

Only one SKB is expected in the queue, but the code tolerates extra frames by dropping nonmatches. Risks include losing timestamps if notifications arrive after queue purge, matching the wrong frame if dialog tokens collide with the same peer, accepting only one active peer, and unit conversion mistakes from 10 ns firmware timestamps to nanoseconds. The frame-list queue must be purged when disabling to avoid stale reports.

## Test signals

Tests should cover config capability rejection, unsupported protocol mask rejection, second-peer rejection, disable purge, RX and TX notification matching, obsolete SKB discard, FTM versus timing-measurement dialog token extraction, and timestamp conversion through the PTP adjustment function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.h

## Purpose

`time-sync.h` declares the MVM time-sync API and provides the inline frame filter/queue helper used by TX/RX paths before firmware timestamp notifications arrive.

## Important APIs

It declares initialization, measurement event handling, confirmation event handling, and configuration: `iwl_mvm_init_time_sync()`, `iwl_mvm_time_sync_msmt_event()`, `iwl_mvm_time_sync_msmt_confirm_event()`, and `iwl_mvm_time_sync_config()`. The inline `iwl_mvm_time_sync_frame()` checks whether a frame belongs to the configured peer and is a timing-measurement or FTM action frame; matches are appended to `mvm->time_sync.frame_list` and ownership is transferred to the time-sync completion path.

## State, dependencies, and risks

State is external in `struct iwl_time_sync_data`, especially `peer_addr` and `frame_list`. The header depends on `mvm.h` and Linux 802.11 helpers. The risk is ownership confusion: if the inline returns true, the caller must not free or continue normal processing of the SKB. Matching only by peer address and frame type is intentionally broad; dialog-token matching happens later in `time-sync.c`.

## Test signals

Compile coverage plus unit tests for frame classification, peer matching, queue insertion, and nonmatching frame passthrough validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tt.c

## Purpose

`tt.c` implements MVM thermal throttling, critical-temperature kill, firmware temperature measurement, thermal-zone/cooling-device integration, and cTDP power-budget commands. It reacts to firmware temperature notifications or Linux thermal framework requests by changing radio operation: CT-kill state, dynamic SMPS, TX protection, TX backoff, and configurable thermal trip thresholds.

## Important APIs and functions

Temperature and CT-kill APIs include `iwl_mvm_temp_notif()`, `iwl_mvm_ct_kill_notif()`, `iwl_mvm_get_temp()`, `iwl_mvm_enter_ctkill()`, `iwl_mvm_tt_handler()`, and delayed work `check_exit_ctkill()`. Throttling actions are implemented by `iwl_mvm_tt_tx_backoff()`, `iwl_mvm_tt_tx_protection()`, and `iwl_mvm_tt_smps_iterator()`. cTDP and thermal framework integration uses `iwl_mvm_ctdp_command()`, `iwl_mvm_send_temp_report_ths_cmd()`, thermal-zone callbacks, cooling-device callbacks, `iwl_mvm_thermal_initialize()`, and `iwl_mvm_thermal_exit()`.

## Control flow

Firmware temperature notifications are parsed by `iwl_mvm_temp_notif_parse()`. If thermal throttling is host-managed, changed temperatures update `mvm->temperature` and call `iwl_mvm_tt_handler()`. If throttling is firmware-managed, threshold-crossing notifications update the Linux thermal zone when configured. CT-kill notifications enter hardware CT-kill state immediately.

`iwl_mvm_tt_handler()` compares the current temperature with configured thresholds. It enters/exits CT-kill, toggles dynamic SMPS on station interfaces, enables/disables TX protection per station, computes TX backoff from threshold table, and logs transition into or out of throttling. `check_exit_ctkill()` periodically restarts enough firmware state to read temperature for host-managed CT-kill and exits CT-kill once the exit threshold is reached.

`iwl_mvm_get_temp()` chooses between command-response temperature measurement and older notification-wait flow based on firmware command version. cTDP commands linearly map Linux cooling state to a firmware power budget between a minimum budget and a BIOS/default maximum. Thermal-zone registration exposes firmware-managed trips; cooling-device registration exposes cTDP states.

## State and persistence

State is stored in `mvm->thermal_throttle`: threshold parameters, throttle flag, dynamic SMPS flag, min/current TX backoff, CT-kill delayed work, and max power budget. Driver-wide state includes `mvm->temperature`, `mvm->temperature_test`, CT-kill status bit, thermal-zone trip array, cooling-device current state, and initialization status. Firmware commands persist TX backoff, cTDP budget, and temperature reporting thresholds until changed or reset.

## Dependencies and integration points

The file depends on firmware PHY operation commands and notifications, MVM firmware start/stop helpers, station TX protection, SMPS updates, BIOS power limit retrieval, Linux thermal framework under `CONFIG_THERMAL`, delayed work, and notification waits. It integrates with runtime firmware state and must avoid temperature polling when firmware is not regular/running.

## Risks

Thermal code is high impact because mistakes can leave hardware transmitting while overheated or stuck in CT-kill. Threshold hysteresis must be correct to avoid oscillation. Host-managed CT-kill temporarily starts/stops firmware to read temperature, so failures reschedule rather than clearing CT-kill. cTDP budget calculation must respect BIOS/default bounds. Thermal framework callbacks must reject invalid states and avoid firmware commands when firmware is unavailable. Test mode suppresses automatic temperature updates and CT-kill exit scheduling, which can surprise generic thermal tests.

## Test signals

Validation should cover notification parsing, negative temperature clamping, command-response and notification-based temperature measurement, CT-kill entry/exit/reschedule behavior, dynamic SMPS and TX protection threshold hysteresis, TX backoff table selection, firmware-managed thermal trip updates, cTDP state-to-budget mapping, BIOS power-limit bounds, thermal-zone trip sorting, cooling-device callbacks, and initialization/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tt.c -->
