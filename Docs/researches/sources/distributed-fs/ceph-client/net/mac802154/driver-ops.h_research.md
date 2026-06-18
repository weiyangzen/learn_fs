# sources/distributed-fs/ceph-client/net/mac802154/driver-ops.h

## Purpose
`driver-ops.h` centralizes inline wrappers around low-level `struct ieee802154_ops` driver callbacks. The wrappers provide tracepoints, optional-callback validation, sleep assertions, local state updates, and common start/stop filtering setup.

## Important APIs, Types, And Functions
Wrappers include `drv_xmit_async()`, `drv_xmit_sync()`, address-filter setters `drv_set_pan_id()`, `drv_set_extended_addr()`, `drv_set_short_addr()`, `drv_set_pan_coord()`, `drv_set_promiscuous_mode()`, lifecycle `drv_start()` and `drv_stop()`, and PHY/MAC setters `drv_set_channel()`, `drv_set_tx_power()`, `drv_set_cca_mode()`, `drv_set_lbt_mode()`, `drv_set_cca_ed_level()`, `drv_set_csma_params()`, and `drv_set_max_frame_retries()`.

## Control Flow
Simple wrappers call `might_sleep()`, trace input, call the driver callback, trace return, and return the result. Optional operations return `-EOPNOTSUPP` with `WARN_ON(1)` if absent.

`drv_start()` first programs hardware address filters when `IEEE802154_HW_AFILT` is set, then maps the requested filtering level to hardware promiscuous/frame-field behavior. For lower filtering levels it may enable hardware promiscuous mode and fall back `local->phy->filtering` to `IEEE802154_FILTERING_NONE`; for frame-field filtering it disables promiscuous mode when supported and records `IEEE802154_FILTERING_4_FRAME_FIELDS`. It sets `local->started = true`, executes a memory barrier, then calls `ops->start()`.

`drv_stop()` calls `ops->stop()`, disables/enables the tasklet to synchronize queued tasklet work, executes a barrier, and clears `local->started`.

## State And Persistence
The wrappers mutate runtime `local->phy->filtering` and `local->started`. Address-filter setters pass temporary `struct ieee802154_hw_addr_filt` values to the driver but do not update `local->addr_filt`; callers own that state.

## Dependencies And Integration Points
The header depends on `net/mac802154.h`, RTNL-related context, `ieee802154_i.h`, and `trace.h`. It is used by cfg, iface, TX, scan, beacon, and association code to call hardware drivers consistently.

## Risks And Edge Cases
`drv_start()` sets `local->started = true` before `ops->start()` returns; if the driver fails, callers receive an error but `started` remains true unless higher-level rollback corrects behavior. Filtering fallback is intentionally conservative but may not match hardware that can support richer filtering than the current generic mapping. Wrappers WARN when optional ops are missing, so feature probes must avoid calling unsupported operations in normal control flow.

## Test Signals
Tracepoint tests, fake-driver callback tests, start failure handling, filtering-level mapping, missing optional ops, and stop/tasklet synchronization are useful signals.
