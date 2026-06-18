# sources/distributed-fs/ceph-client/net/mac80211/chan.c

## Purpose

`chan.c` owns mac80211 channel-context lifecycle and assignment. It lets multiple virtual interfaces and MLO links share compatible channel definitions, reserve future channel contexts for channel switch announcements, replace one context with another, and keep driver-visible channel context state synchronized with link/VLAN `bss_conf` pointers. The file is a core integration point between cfg80211 channel validation, mac80211 link state, station bandwidth/rate-control state, radar requirements, and low-level driver callbacks.

## Important APIs, Types, And Functions

The central local helper type is `struct ieee80211_chanctx_user_iter`, which iterates users of a `struct ieee80211_chanctx` across running interfaces, MLO links, reserved links, and NAN scheduled channels. The `for_each_chanctx_user_assigned`, `for_each_chanctx_user_reserved`, and `for_each_chanctx_user_all` macros build on `ieee80211_chanctx_user_iter_next()` and enforce a consistent notion of assigned versus future reserved users.

Public or cross-file entry points include `ieee80211_chanctx_num_assigned()`, `ieee80211_chanctx_refcount()`, `ieee80211_chanreq_identical()`, `ieee80211_is_radar_required()`, `ieee80211_recalc_chanctx_min_def()`, `ieee80211_free_chanctx()`, `ieee80211_recalc_chanctx_chantype()`, `ieee80211_recalc_smps_chanctx()`, `ieee80211_link_copy_chanctx_to_vlans()`, `ieee80211_link_reserve_chanctx()`, `ieee80211_link_unreserve_chanctx()`, `_ieee80211_link_use_channel()`, `ieee80211_link_use_reserved_context()`, `ieee80211_link_change_chanreq()`, `ieee80211_link_release_channel()`, `ieee80211_link_vlan_copy_chanctx()`, and the exported iterator APIs `ieee80211_iter_chan_contexts_atomic()` and `ieee80211_iter_chan_contexts_mtx()`.

Key helpers include `ieee80211_chanreq_compatible()`, `_ieee80211_chanctx_compatible()`, `ieee80211_find_chanctx()`, `ieee80211_find_or_create_chanctx()`, `ieee80211_alloc_chanctx()`, `ieee80211_add_chanctx()`, `ieee80211_del_chanctx()`, `ieee80211_assign_link_chanctx()`, `ieee80211_replace_chanctx()`, and `ieee80211_vif_use_reserved_switch()`.

## Control Flow

Normal channel use starts in `_ieee80211_link_use_channel()`. For active links it checks DFS/radar requirements through cfg80211, validates interface combinations, releases any current channel when not reconfiguring, finds or creates a compatible context, copies the requested `chanreq` into the link and AP VLANs, assigns the link to the driver via `drv_assign_vif_chanctx()`, clears temporary `will_be_used` state if an existing context was reused, and recalculates SMPS and radar state. Inactive links only update their stored `chanreq`.

Context sharing is compatibility-driven. `ieee80211_chanreq_compatible()` combines operational chandefs and AP chandefs, while `_ieee80211_chanctx_compatible()` folds a candidate request across all current users except an optional changing link. `ieee80211_find_chanctx()` skips exclusive and replacement contexts, marks a selected context `will_be_used`, updates its driver-facing chandef through `ieee80211_change_chanctx()`, and returns it for assignment.

Reservation flow starts with `ieee80211_link_reserve_chanctx()`. It tries an existing reservation-compatible context, otherwise creates a new context on an available radio, or builds an in-place replacement pair with `ieee80211_replace_chanctx()`. A later `ieee80211_link_use_reserved_context()` marks the reservation ready and either finalizes direct assignment/reassignment or enters `ieee80211_vif_use_reserved_switch()` for coordinated replacement. The replacement path validates that all users of the old context have reservations ready, optionally calls `drv_switch_vif_chanctx()` for driver-visible swaps, adds/removes driver channel contexts for ctx-less or reassign cases, updates all link pointers and AP VLAN pointers, notifies BSS bandwidth changes, recalculates tx power/chantype/SMPS/radar/min bandwidth, completes CSA work, and finally removes old contexts.

Bandwidth state is recalculated from actual users. `ieee80211_get_chanctx_max_required_bw()` collects max required width from assigned/reserved users and monitor interfaces; `__ieee80211_recalc_chanctx_min_def()` downgrades `conf.min_def` from the configured `def` where possible, except narrow S1G widths and radar-enabled contexts. `ieee80211_chan_bw_change()` updates per-link station bandwidth and calls rate control updates around driver context changes.

## State And Persistence

Channel contexts live in `local->chanctx_list` and are freed with RCU after list removal. Link state persists in `link->conf->chanctx_conf`, `link->conf->chanreq`, reservation fields (`reserved_chanctx`, `reserved`, `reserved_ready`, `reserved_radar_required`), radar state, SMPS mode, and AP VLAN copied `chanctx_conf`/`chanreq` pointers. Context state includes `conf.def`, `conf.ap`, `conf.min_def`, `conf.radar_enabled`, radio index, rx-chain counts, `mode`, `driver_present`, `will_be_used`, `replace_state`, and `replace_ctx`. This is runtime kernel state only; there is no disk persistence.

Most mutation requires the wiphy mutex (`lockdep_assert_wiphy()` is pervasive). Published link and context pointers use RCU access helpers and `rcu_assign_pointer()`, with atomic iterators guarded by `rcu_read_lock()`.

## Dependencies And Integration Points

This file depends on cfg80211 channel helpers (`cfg80211_chandef_*`, DFS checks, radio validation), mac80211 station/rate-control internals, AP VLAN/link structures, NAN scheduling data, WBRF add/remove hooks, and driver wrappers from `driver-ops.h` (`drv_add_chanctx`, `drv_change_chanctx`, `drv_remove_chanctx`, `drv_assign_vif_chanctx`, `drv_unassign_vif_chanctx`, `drv_switch_vif_chanctx`). It also feeds cfg80211 stop-interface handling when reservation finalization fails.

## Risks

The highest-risk behavior is coordinated replacement state. `IEEE80211_CHANCTX_WILL_BE_REPLACED` and `IEEE80211_CHANCTX_REPLACES_OTHER` must stay paired, and all early failures must unreserve links and restore driver contexts correctly. Another risk is stale AP VLAN channel pointers; the code intentionally copies/clears them while the AP link context is still valid. Compatibility calculations rely on all users being visible to the iterator, including NAN and reserved users. Driver callback failures are mixed with `assign_on_failure` and reconfig paths, so callers must understand when mac80211 commits state despite driver errors. A test signal worth watching is that `ieee80211_if_write_link_handler()` in the nearby netdev debugfs code has a typed-data mismatch that could affect link-level debugfs controls that eventually call channel/link operations.

## Test Signals

Useful coverage includes MLO active-link switching, CSA reservation completion for station/AP/mesh/IBSS/OCB, context sharing with AP bandwidth changes and TDLS wider bandwidth, radar-required scan/channel use combinations, monitor interface on/off with `NO_VIRTUAL_MONITOR`, driver failures from add/assign/switch channel-context callbacks, AP VLAN channel release/copy races, NAN scheduled channels, and repeated reserve/unreserve cycles that trigger in-place replacement cleanup.
