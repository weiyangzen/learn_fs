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
