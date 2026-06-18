# sources/distributed-fs/ceph-client/net/mac80211/driver-ops.c

## Purpose

`driver-ops.c` implements non-inline mac80211 wrappers around selected low-level driver callbacks. These wrappers enforce mac80211 state checks, locking expectations, tracepoints, fallback behavior, debugfs hook management, MLO link handling, and driver-present bookkeeping for channel contexts.

## Important APIs, Types, And Functions

Implemented wrappers include `drv_start()`, `drv_stop()`, `drv_add_interface()`, `drv_change_interface()`, `drv_remove_interface()`, `drv_sta_state()`, `drv_sta_set_txpwr()`, `drv_link_sta_rc_update()`, `drv_conf_tx()`, `drv_get_tsf()`, `drv_set_tsf()`, `drv_offset_tsf()`, `drv_reset_tsf()`, `drv_assign_vif_chanctx()`, `drv_unassign_vif_chanctx()`, `drv_switch_vif_chanctx()`, `drv_ampdu_action()`, `drv_link_info_changed()`, `drv_set_key()`, `drv_change_vif_links()`, and `drv_change_sta_links()`.

## Control Flow

Most functions begin with `might_sleep()` and `lockdep_assert_wiphy()`, validate `IEEE80211_SDATA_IN_DRIVER` through `check_sdata_in_driver()`, emit a `trace_drv_*` event, call the optional or required driver operation, emit a return trace, and then update mac80211 bookkeeping. `drv_start()` sets `local->started` before invoking the driver start op, using a memory barrier so RX can proceed, and rolls back on error. `drv_stop()` calls the stop op, drains the tasklet by disable/enable, then clears `started`.

Interface wrappers block invalid AP VLAN/monitor cases, set/clear `IEEE80211_SDATA_IN_DRIVER`, and add/remove driver debugfs entries. Station-state handling supports both the modern `sta_state` callback and fallback `sta_add`/`sta_remove` transitions between AUTH and ASSOC, including rate-table upload after successful fallback add.

Channel-context wrappers skip emulated monitor assignment cases, ignore inactive links, validate `driver_present`, and call assign/unassign/switch operations. `drv_switch_vif_chanctx()` updates `driver_present` on new/old contexts after successful swap mode. MLO link-change wrappers remove driver debugfs for links being removed before calling the driver and add it back for links being added after success, except during reconfig/resume.

## State And Persistence

The wrappers mutate live runtime state: `local->started`, `sdata->flags`, `sta->uploaded` in fallback paths, channel `driver_present`, and driver debugfs subdirectories for vifs, links, and link stations. No persistent storage is used.

## Dependencies And Integration Points

This file depends on `net/mac80211.h`, mac80211 internal state, tracepoints, `driver-ops.h`, `debugfs_sta.h`, and `debugfs_netdev.h`. It is called broadly from channel management, interface lifecycle, station lifecycle, key management, TSF debugfs, aggregation, and MLO active-link code.

## Risks

Wrappers are correctness gates between mac80211 and drivers. Missing `check_sdata_in_driver()` checks can call drivers for removed interfaces; over-strict checks can suppress needed cleanup during reconfig failure. `drv_start()` temporarily sets `started` before driver success, so error paths and concurrent RX assumptions depend on the barrier and rollback. Debugfs recreation in `drv_remove_interface()` must not run for the virtual monitor interface. MLO link debugfs remove/add ordering must match driver link-change success/failure or stale driver files can remain. FIPS gating in `drv_set_key()` prevents driver key programming entirely.

## Test Signals

Test with drivers that implement and omit optional callbacks, fallback station add/remove paths, reconfig/resume link-change paths, inactive MLO links, monitor and AP VLAN edge cases, FIPS enabled key setting, channel-context switch modes, and tracepoint expectations. Fault injection in driver callbacks should verify state rollback and debugfs lifecycle behavior.
