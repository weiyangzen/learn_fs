# sources/distributed-fs/ceph-client/drivers/android/binder/stats.rs

Purpose: tracks Binder command (`BC_*`) and return (`BR_*`) counters for global and per-process binder logs.

Important APIs/types/functions: `BC_COUNT` and `BR_COUNT` size arrays from the highest supported UAPI command/return numbers. `GLOBAL_STATS` is a static `BinderStats`. `BinderStats` stores relaxed atomic arrays and provides `new`, `inc_bc`, `inc_br`, and `debug_print`. The internal `strings` module imports C `binder_command_strings` and `binder_return_strings` and converts indexed C strings to Rust `&str`.

Control flow: Binder command handling calls `inc_bc`; return writing through `BinderReturnWriter::write_code` calls `inc_br` for both global and process stats. `debug_print` iterates counters and prints only nonzero entries with names resolved from the C arrays.

State and persistence: counters are in-memory atomics for the module/process lifetime. Global stats persist while the module is loaded; per-process stats live inside each `Process`.

Dependencies and integration points: depends on Binder UAPI constants from `defs`, kernel `_IOC_NR`, seq-file output, and the string tables in `rust_binder_events.c`. `rust_binder_main.rs` includes global and per-process stats in binderfs log output.

Risks: relaxed atomics are appropriate for approximate counters but not for synchronization. The C string conversion is unsafe and assumes every in-range table entry is a valid nul-terminated ASCII string; table length/order must match `BC_COUNT` and `BR_COUNT`. Commands beyond the current max are silently ignored.

Test signals: issue representative Binder commands and returns, read `binder_logs/stats`, and verify nonzero named counters for global and process sections. Add-UAPI tests should fail or be reviewed when new `BC_*`/`BR_*` constants exceed the configured counts.
