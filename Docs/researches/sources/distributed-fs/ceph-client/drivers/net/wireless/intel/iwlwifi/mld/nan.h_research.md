# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.h

Purpose: exposes the MLD NAN interface to mac80211 operation tables and notification dispatch.

Important APIs/types: declares `iwl_mld_nan_supported()`, start/change/stop callbacks taking `struct ieee80211_hw`, `struct ieee80211_vif`, and `struct cfg80211_nan_conf`, plus cluster and discovery-window-end notification handlers and cancellation callbacks.

Control flow: callers use the support helper before registering or accepting NAN operation, then route lifecycle callbacks through `nan.c`. `notif.c` uses the handler and cancellation declarations for `NAN_JOINED_CLUSTER_NOTIF` and `NAN_DW_END_NOTIF`.

State and persistence: no state is stored in the header. Implementations operate on live `struct iwl_mld`, `mld->nan_device_vif`, and aux-station state.

Dependencies and integration: includes cfg80211 and etherdevice headers. It intentionally relies on surrounding includes for `struct iwl_mld`, `struct iwl_rx_packet`, and mac80211 types, matching local driver header style.

Risks and test signals: cancellation callbacks take an `obj_id` even though NAN has no unique id, which is a useful signal for tests around object-type cancellation. Header consumers should verify NAN support before invoking lifecycle paths.
