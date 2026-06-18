# sources/distributed-fs/ceph-client/net/mac80211/nan.c

Purpose: implements mac80211 NAN schedule handling for local NAN interfaces and peer NAN schedule installation. It bridges cfg80211 NAN schedule objects into mac80211 channel contexts, driver notifications, and NAN data interface carrier state.

Important APIs and functions: `ieee80211_nan_set_local_sched()` is the main local schedule update entry. It validates channel/blob limits, backs up the current schedule, maps requested schedule indexes to existing or newly allocated `ieee80211_nan_channel` objects, uses `ieee80211_nan_use_chanctx()` to claim shared channel contexts, sends `BSS_CHANGED_NAN_LOCAL_SCHED`, and rolls back on allocation or chanctx failures. `ieee80211_nan_sched_update_done()` completes deferred updates exported to drivers. Peer-side work is in `ieee80211_nan_set_peer_sched()`, `ieee80211_nan_init_peer_channel()`, `ieee80211_nan_init_peer_map()`, and `ieee80211_nan_free_peer_sched()`. Carrier gating uses `ieee80211_nan_has_common_slots()`, `ieee80211_nan_update_ndi_carrier()`, and `ieee80211_nan_update_peer_ndis_carrier()`.

Control flow: local schedule updates first remove or mark removed channels, then add/update channels, rebuild the slot schedule, notify the driver, and update all NAN data interface carriers unless the update is deferred. Deferred completion updates carriers, clears `deferred`, removes channels that were kept alive for peer notification ordering, recalculates SMPS, clears the removed bitmap, and reports completion to cfg80211.

State and persistence: state lives in `sdata->vif.cfg.nan_sched`, `sdata->u.nan.removed_channels`, `sta->sta.nan_sched`, chanctx pointers, and netdev carrier state. There is no durable storage; all state is in-kernel and protected by the wiphy lock plus RCU dereferences where needed.

Dependencies and integration points: depends on cfg80211 NAN structs, mac80211 channel context helpers, station lists, driver ops `drv_vif_cfg_changed()` and `drv_nan_peer_sched_changed()`, and cfg80211 completion notification. Integration risk is high around chanctx lifetime because peer maps store pointers into variable-length schedule arrays and local channels store `chanctx_conf` pointers.

Risks: rollback has to restore schedule arrays, availability blobs, channel contexts, and SMPS state consistently. Removing a local channel must rewrite all peer schedule pointers before compacting the peer channel array. Deferred NSS reductions intentionally delay SMPS recalculation, so missed completion would leave stale receive-chain requirements and carrier state.

Test signals: exercise local schedule add/update/remove, deferred updates, failure rollback from chanctx allocation, peer schedules with compatible and incompatible channels, peer map compaction after local removal, and NDI carrier transitions when common slots appear or disappear.
