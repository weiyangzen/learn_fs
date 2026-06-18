# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.h

Purpose: declares the MLD notification/RX dispatch interface and the object-type vocabulary used to cancel queued async notifications safely.

Important APIs/types: exports normal and RSS RX entry points, async handler work, bulk async cancellation, command-specific handler deletion, and object cancellation. `enum iwl_mld_object_type` includes none, link, station, VIF, ROC, scan, FTM request, and NAN.

Control flow: transport callbacks call `iwl_mld_rx()` or `iwl_mld_rx_rss()`. Teardown paths call `iwl_mld_cancel_async_notifications()`, while object removal paths call `iwl_mld_cancel_notifications_of_object()` with an object type/id pair to prune queued work before object memory disappears.

State and persistence: the header stores no state. It defines the public contract for manipulating `mld->async_handlers_*` state owned by `notif.c`.

Dependencies and integration: forward-declares `struct iwl_mld` and references `struct iwl_op_mode`, `struct napi_struct`, `struct iwl_rx_cmd_buffer`, `struct wiphy`, and firmware packet types supplied by surrounding driver includes.

Risks and test signals: callers must pass a meaningful object type and firmware object id; `IWL_MLD_OBJECT_TYPE_NONE` is explicitly invalid for object cancellation. Tests should ensure all async object handlers use a matching enum and cancellation predicate.
