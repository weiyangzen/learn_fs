# sources/distributed-fs/ceph-client/drivers/base/regmap/trace.h

Purpose: this header declares the ftrace event surface for the regmap subsystem. It records scalar register reads/writes, cache reads, raw/bulk data transfers, hardware transfer boundaries, cache state changes, async write lifecycle events, cache sync status, and cache drop regions.

Important APIs, types, and functions: it defines event classes `regmap_reg`, `regmap_bulk`, `regmap_block`, `regmap_bool`, and `regmap_async`, plus concrete events such as `regmap_reg_write`, `regmap_reg_read`, `regmap_reg_read_cache`, `regmap_bulk_write`, `regmap_bulk_read`, `regmap_hw_read_start`, `regmap_hw_read_done`, `regmap_hw_write_start`, `regmap_hw_write_done`, `regcache_sync`, `regmap_cache_only`, `regmap_cache_bypass`, `regmap_async_write_start`, `regmap_async_io_complete`, `regmap_async_complete_start`, `regmap_async_complete_done`, and `regcache_drop_region`.

Control flow: users include the header normally for declarations; exactly one C file defines `CREATE_TRACE_POINTS` before including it to emit tracepoint definitions. Event payloads capture `regmap_name(map)`, register numbers, values, counts, buffer snapshots, flags, and status strings. Bulk events use a dynamic array and print data as hex.

State and persistence: this file stores no runtime state. Tracepoint definitions become kernel instrumentation hooks; when tracing is enabled, emitted event records persist only in the tracing ring buffer according to the active tracing configuration.

Dependencies and integration points: it includes `linux/ktime.h`, `linux/tracepoint.h`, and local `internal.h` for `struct regmap` and `regmap_name()`. `regmap.c` creates the tracepoints; regcache code can emit the cache-related events. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set for `trace/define_trace.h`.

Risks: tracepoint ABI names and field layouts are consumed by tooling, so renaming events or changing fields can break diagnostics. Dynamic buffer capture can expose register contents in traces, so debug access controls matter. Incorrect include guard or `TRACE_INCLUDE_*` setup would break trace generation.

Test signals: building with tracing enabled validates the macro expansion. Runtime tests can enable `regmap:*` events and verify expected start/done pairs around reads, writes, cache-only/bypass transitions, async completion, and cache sync/drop operations.
