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
