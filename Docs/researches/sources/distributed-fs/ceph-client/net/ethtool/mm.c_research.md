# sources/distributed-fs/ceph-client/net/ethtool/mm.c

## Purpose
This file implements netlink MAC Merge (`MM_GET`/`MM_SET`) support and exports a generic software verification state machine for drivers that lack hardware verification for frame preemption/MAC Merge.

## Important APIs, Types, And Functions
The netlink side uses `struct mm_reply_data`, `ethnl_mm_get_policy`, `ethnl_mm_set_policy`, `mm_prepare_data()`, `mm_put_stats()`, `mm_fill_reply()`, `mm_state_to_cfg()`, `ethnl_set_mm_validate()`, `ethnl_set_mm()`, and `ethnl_mm_request_ops`. Exported driver helpers are `__ethtool_dev_mm_supported()`, `ethtool_dev_mm_supported()`, `ethtool_mmsv_init()`, `ethtool_mmsv_get_mm()`, `ethtool_mmsv_set_mm()`, `ethtool_mmsv_stop()`, `ethtool_mmsv_link_state_handle()`, and `ethtool_mmsv_event_handle()`.

## Control Flow
GET requires `get_mm`, initializes stats, calls driver `get_mm`, optionally calls `get_mm_stats`, and emits administrative state, verification state, timing, fragment sizes, and requested stats. SET fetches current state, derives a mutable config, applies supplied booleans and numeric fields, validates verify time against device maximum, enforces verification requires TX enabled and TX requires pMAC enabled, then calls `set_mm()`.

The software verifier uses a timer and event callbacks. `ethtool_mmsv_apply()` either configures pMAC/TX immediately when verification is disabled or starts a verify/retry process. The timer sends Verify mPackets up to the retry limit and activates TX after a Response event marks verification succeeded.

## State And Persistence
Netlink request state is transient. Persistent MAC Merge state lives in drivers or in `struct ethtool_mmsv`: flags for pMAC, TX, verification, verify time, retry count, status, timer, lock, device pointer, and ops. Timer state must be stopped before hardware state loss.

## Dependencies And Integration Points
The file depends on `ethtool_ops::{get_mm,set_mm,get_mm_stats}` and `struct ethtool_mmsv_ops` driver callbacks for configuring pMAC/TX and sending mPackets. `pause.c` calls `__ethtool_dev_mm_supported()` when users request eMAC/pMAC pause statistics.

## Risks And Edge Cases
The verifier mixes timer context, interrupt context, and task context under a spinlock. Drivers must call `ethtool_mmsv_stop()` during stop/suspend and must supply events accurately; otherwise TX may remain inactive or verification may be reported incorrectly. SET validation does not allow enabling TX without pMAC, and requests exceeding `max_verify_time` are rejected. Stats are omitted field-by-field when left at `ETHTOOL_STAT_NOT_SET`.

## Test Signals
Useful tests include GET/SET validation, stats omission, device support probing under RTNL, verifier retry-to-failed behavior, Response-to-succeeded behavior, link-down reset behavior, and driver callback ordering for pMAC before verification.
