# sources/distributed-fs/ceph-client/net/mac80211/driver-ops.h

## Purpose

`driver-ops.h` is the main inline wrapper layer for mac80211-to-driver callbacks. It normalizes locking assertions, tracepoints, optional-callback fallback returns, AP VLAN remapping, interface-in-driver checks, FIPS restrictions, MLO active-link filtering, debugfs hook stubs, and channel-context driver-present bookkeeping.

## Important APIs, Types, And Functions

The header defines `check_sdata_in_driver()` and `get_bss_sdata()`, declares non-inline wrappers implemented in `driver-ops.c`, and implements many inline wrappers including `drv_tx()`, PM wrappers, `drv_config()`, `drv_vif_cfg_changed()`, multicast/filter configuration, scan/sched-scan wrappers, stats/key sequence helpers, threshold/coverage/antenna/ring parameter wrappers, station add/remove/statistics/rate update wrappers, debugfs driver hook wrappers, channel-context add/remove/change wrappers, AP start/stop, channel-switch callbacks, IBSS join/leave, TX queue wake scheduling, TDLS/NAN/PMSR/TWT/offload wrappers, link activation/TTLM checks, and `drv_set_eml_op_mode()`.

## Control Flow

The common pattern is: assert sleeping/locking where required, map AP VLAN sdata to the owning AP with `get_bss_sdata()`, check the interface is in the driver when applicable, emit a tracepoint, call the driver op only if present, return a default (`0`, `false`, or `-EOPNOTSUPP`) when absent, and emit a return trace. Some wrappers intentionally do not take wiphy assertions because they are used in TX-fast or callback contexts (`drv_tx()`, selected buffered-frame helpers).

Channel context inline wrappers call `add_chanctx`, `remove_chanctx`, and `change_chanctx`, setting or checking `ctx->driver_present`. Debugfs hook wrappers exist only under `CONFIG_MAC80211_DEBUGFS`; otherwise `drv_vif_add_debugfs()` is a no-op and related declarations are absent. `drv_wake_tx_queue()` marks TXQs dirty during reconfig instead of waking them immediately.

## State And Persistence

The header itself stores no persistent state, but inline wrappers mutate live runtime fields such as channel context `driver_present`, TXQ `IEEE80211_TXQ_DIRTY`, and driver-visible configuration. No disk persistence exists.

## Dependencies And Integration Points

It includes FIPS, `net/mac80211.h`, `ieee80211_i.h`, and trace definitions. It is included by almost every mac80211 subsystem that calls drivers, including this group’s `chan.c`, `debugfs.c`, `debugfs_netdev.c`, `debugfs_sta.c`, and `eht.c`.

## Risks

Because wrappers encode driver callback contracts, default return values are semantically important. A missing optional callback may mean success for some operations and unsupported for others. Several NAN wrappers call `check_sdata_in_driver(sdata)` without using the boolean result, so they warn but still call the driver; callers must know this behavior. `drv_set_tid_config()` and `drv_reset_tid_config()` assume corresponding ops exist and do not check optionality. Trace arguments must stay valid even when optional callbacks are absent. FIPS checks in key/rekey paths can make behavior differ by system policy.

## Test Signals

Build coverage should exercise debugfs and non-debugfs variants, PM and non-PM variants, IPv6 variant wrappers, and optional-driver callback combinations. Runtime tests should check lockdep assertions, tracepoint emission, AP VLAN remapping, reconfig TXQ dirty marking, absent callback return codes, channel-context `driver_present` transitions, FIPS key/rekey suppression, and MLO active-link filtering.
