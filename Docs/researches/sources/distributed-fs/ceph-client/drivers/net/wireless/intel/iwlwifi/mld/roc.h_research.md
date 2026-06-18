# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.h

Purpose: declares the MLD remain-on-channel interface used by mac80211 operations and notification dispatch.

Important APIs/types: `iwl_mld_start_roc()` starts a ROC on a requested channel/duration/type, `iwl_mld_cancel_roc()` cancels it for a VIF, and `iwl_mld_handle_roc_notif()` handles firmware completion/start notifications.

Control flow: mac80211 operation tables call start/cancel; `notif.c` dispatches `ROC_NOTIF` to the handler and can cancel queued async ROC notifications by object id/activity.

State and persistence: no state is defined here. Implementation uses `mld_vif->roc_activity`, aux station state, and async notification queue state.

Dependencies and integration: includes mac80211 and relies on local MLD structures from surrounding includes. ROC is tightly coupled to MLO EMLSR blocking and aux station management.

Risks and test signals: callers should hold the expected wiphy serialization. Tests should verify the activity value passed to notification cancellation matches firmware activity encoding.
