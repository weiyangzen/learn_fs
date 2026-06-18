# sources/distributed-fs/lustre-release/lustre/osc/lproc_osc.c

## Purpose

`lproc_osc.c` registers and implements sysfs/debugfs/lprocfs controls for the Lustre Object Storage Client. It exposes runtime tunables for import activation, RPC concurrency, dirty/cache limits, grants, checksums, idle reconnect behavior, page-cache shrinking, and multiple statistics views. The code is administrative/control-plane logic for a live OSC instance rather than data I/O itself.

## Important APIs, Types, and Functions

- Sysfs-style show/store pairs exist for `active`, `max_rpcs_in_flight`, `max_dirty_mb`, `osc_unevict_cached_mb`, grant counters/shrink controls, checksum toggles, resend count, idle timeout/connect, and page-cache shrink.
- Debugfs seq files include `osc_cached_mb`, `unstable_stats`, `io_latency_stats`, `rpc_stats`, and `osc_stats`.
- `ldebugfs_osc_obd_vars[]` names debugfs entries and file operations.
- `osc_attrs[]` lists sysfs attributes installed in the OSC kobject default group.
- `osc_tunables_init()` attaches the lproc/debugfs/sysfs state to an `obd_device`, registers sptlrpc client lproc state, and registers PTLRPC stats.

## Control Flow

Simple show handlers derive `struct obd_device` from the kobject and read fields from `obd->u.cli` or the import under `with_imp_locked()`. Store handlers parse booleans, unsigned integers, or memory strings, validate ranges, take the appropriate spinlock/import lock, update fields, and trigger side effects such as `client_adjust_max_dirty()`, `osc_wake_cache_waiters()`, `osc_schedule_grant_work()`, `ptlrpc_set_import_active()`, or a forced pinger/statfs allocation.

Cache controls expose both read-only counters and active shrink operations. `osc_cached_mb_seq_write()` parses `used_mb:`, computes the number of pages to reclaim, obtains a client LU environment, and calls `osc_lru_shrink()`. `osc_unevict_cached_mb_store()` accepts only `clear`, shrinks the unevictable cache, and then scans the LRU to discard pages or move mlocked pages.

Grant controls report current grant, dirty grant, and lost grant. Writing `cur_grant_bytes` only shrinks grants when the target is below current available grant and the import is fully connected. `grant_shrink_interval` updates the interval and schedules work; `grant_shrink` toggles whether import grant shrink is disabled while respecting negotiated connect flags in the show path.

Statistics seq files format histograms under `cl_loi_list_lock`. `osc_rpc_stats_seq_show()` emits current in-flight and pending page counts plus histograms for pages per RPC, RPCs in flight, offsets, and latencies. Write handlers clear the corresponding histograms and reset initialization timestamps. `osc_io_latency_stats` delegates bucket formatting/clearing to common OBD helpers. `osc_stats` reports and clears lockless read/write byte counters.

Initialization sets `obd->obd_debugfs_vars`, assigns `osc_groups` to the OBD ktype, calls `lprocfs_obd_setup()`, attaches sptlrpc lproc entries, and registers ptlrpc stats. On sptlrpc attach failure it cleans up the lprocfs OBD setup.

## State and Persistence Behavior

This file mutates live in-memory OSC state: `client_obd` concurrency limits, dirty/cache page limits, grant accounting controls, checksum flags, resend counters, import idle timeout/debug flags, import activation state, and stats histograms. It does not persist settings across module unload or reboot. Some writes have immediate behavioral effects on worker pools, grant work, cache waiters, and import state.

## Dependencies and Integration Points

The code depends on Lustre OBD/lprocfs attribute macros, Linux kobject/sysfs and seq_file APIs, OSC internals (`osc_lru_shrink()`, `osc_shrink_grant_to_target()`, request pool population, cache shrink helpers), PTLRPC import/pinger/request APIs, checksum parameter helpers, and common OBD histogram/stat formatting. The `Makefile` links this file into the OSC module, making `osc_tunables_init()` part of OSC device setup.

## Risks and Edge Cases

- Store handlers are administrative attack surface; range checks on RPC counts, dirty MB, idle timeout, and grant targets are important to prevent resource exhaustion or nonsensical state.
- `max_rpcs_in_flight_store()` may over-allocate request pool entries by design under race; tests should verify it remains bounded by pool caps in practice.
- `cur_grant_bytes_store()` returns zero without changing state when target is above current grant, which can surprise scripts expecting `count`.
- Some debugfs write parsers accept a narrow format, such as `used_mb:` or literal `clear`.
- Histograms are formatted while holding `cl_loi_list_lock`; expensive seq output under the spinlock should remain bounded.
- Import access must stay under `with_imp_locked()` or import references must be taken, as done by `active_store()`.

## Test Signals

Tests should cover sysfs parsing and range rejection for all writable attrs, activation/deactivation idempotence, request-pool growth when increasing max RPCs, dirty limit adjustment and waiter wakeup, cache shrink and unevictable clear commands, grant shrink only while fully connected, checksum/resend toggles, idle timeout debug/nodebug/numeric modes, idle connect pinger forcing, histogram show output with empty and populated buckets, histogram clear writes, `osc_tunables_init()` cleanup on sptlrpc attach failure, and presence of every expected sysfs/debugfs entry.
