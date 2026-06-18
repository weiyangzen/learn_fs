# sources/distributed-fs/ceph-client/net/mac80211/debugfs.c

## Purpose

`debugfs.c` builds the PHY-level mac80211 debugfs tree under the wiphy debugfs directory. It exposes read-only hardware and queue state, low-level driver statistics, and several writable diagnostic controls for AQM/AQL, airtime accounting, forced TX status, hw flag testing, and suspend/resume reset.

## Important APIs, Types, And Functions

The externally visible API is `debugfs_hw_add(struct ieee80211_local *local)`, declared in `debugfs.h`. `mac80211_format_buffer()` is a shared debugfs formatting helper used by key and station debugfs files. Local file operations are generated with `DEBUGFS_READONLY_FILE*` macros and `struct debugfs_short_fops`.

Important read/write handlers include `aqm_read()`/`aqm_write()`, `airtime_flags_read()`/`airtime_flags_write()`, `aql_pending_read()`, `aql_txq_limit_read()`/`aql_txq_limit_write()`, `aql_enable_read()`/`aql_enable_write()`, `force_tx_status_read()`/`force_tx_status_write()`, optional `reset_write()`, `hwflags_read()`/`hwflags_write()`, `misc_read()`, `queues_read()`, and generated low-level stats readers such as `stats_dot11ACKFailureCount_read()`.

## Control Flow

`debugfs_hw_add()` exits if the wiphy debugfs directory is absent, creates `keys`, creates top-level files such as `total_ps_buffered`, `wep_iv`, `rate_ctrl_alg`, `queues`, `misc`, `hwflags`, `force_tx_status`, `aql_enable`, `aql_pending`, `aqm`, `airtime_flags`, `aql_txq_limit`, `aql_threshold`, and creates a `statistics` subdirectory. If `CONFIG_MAC80211_DEBUG_COUNTERS` is enabled, it exposes direct u32 counters; driver stats are always exposed through files that call `drv_get_stats()` under `wiphy_lock()`.

Writable handlers parse small user buffers. `aqm_write()` adjusts global fq limits/quantum. `aql_txq_limit_write()` parses AC/low/high limits, acquires the wiphy lock, updates global AQL limits, and updates stations that still match the old defaults. `aql_enable_write()` toggles the static key used to disable/enable AQL. `hwflags_write()` allows changing the `IEEE80211_HW_STRICT` bit through `strict=...`. `reset_write()` takes RTNL and wiphy locks, calls mac80211 suspend/resume internals, and shuts down all interfaces on resume failure.

## State And Persistence

The debugfs files expose runtime-only fields on `ieee80211_local`: hardware config flags and power levels, WEP IV, fq queue state, AQL counters/limits, airtime flags, pending queues, stop reasons, forced TX status, and optional debug counters. Writes mutate live in-memory behavior and are not persisted across module/device restart.

Locking is mixed by state: fq stats use `fq.lock`, queue stop reasons use `queue_stop_reason_lock`, AQL station limit propagation uses the wiphy lock, and driver statistics use `wiphy_lock()`. Simple scalar writes such as `force_tx_status` and `airtime_flags` are direct debug/test knobs.

## Dependencies And Integration Points

This file depends on debugfs, `ieee80211_i.h`, `driver-ops.h`, `rate.h`, mac80211 fq/AQL structures, PM suspend/resume internals, and optional debug-counter Kconfig. Other debugfs files rely on `mac80211_format_buffer()`. Key debugfs directories created here are consumed by `debugfs_key.c`.

## Risks

Writable debugfs controls can materially change runtime behavior. AQL and AQM inputs have range checks only where explicitly implemented; very large limits or quantum values are accepted. `hwflags_write()` appears inverted by label (`strict=0` sets `STRICT`, `strict=1` clears it), so callers need to verify intended semantics. The reset path is invasive and can shut down all interfaces after resume failure. Statistics and queue reads must avoid buffer overrun as enum sizes evolve; `BUILD_BUG_ON` protects hardware flag name coverage.

## Test Signals

Tests should mount/read debugfs with `CONFIG_MAC80211_DEBUGFS`, verify each file appears under the wiphy directory, exercise AQL/AQM writes with valid and invalid buffers, check station AQL defaults are propagated only when matching old defaults, test reset under `CONFIG_PM`, validate `hwflags` formatting after flag enum changes, and confirm `drv_get_stats()` failures are propagated to readers.
