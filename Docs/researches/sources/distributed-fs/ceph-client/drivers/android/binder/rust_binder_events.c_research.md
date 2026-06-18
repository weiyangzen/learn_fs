# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.c

Purpose: defines string tables and instantiates Rust Binder tracepoints. It supplies human-readable Binder command and return names used by both trace formatting and Rust stats output.

Important APIs/types/functions: `binder_command_strings[]` lists `BC_*` command names from `BC_TRANSACTION` through `BC_REPLY_SG`. `binder_return_strings[]` lists `BR_*` return names through `BR_TRANSACTION_PENDING_FROZEN`. The file defines `CREATE_TRACE_POINTS` and `CREATE_RUST_TRACE_POINTS` before including `rust_binder_events.h`.

Control flow: no dynamic control flow is present. During compilation, the tracepoint macros in the header expand into tracepoint definitions. At runtime, trace and stats code indexes the arrays by `_IOC_NR(cmd)` after bounds checks on the caller side.

State and persistence: the arrays are global const string tables for the module lifetime. They must stay aligned with Binder UAPI numeric command ranges and `stats.rs` count constants.

Dependencies and integration points: includes `rust_binder.h`, which provides opaque Rust pointer layout helpers for the trace header. `stats.rs` imports these arrays through `extern "C"` and converts C strings to Rust `&str` for binder log output.

Risks: missing newer Binder commands or returns means trace output may show `unknown` and stats arrays may not cover the full range. The Rust stats code assumes all pointers within its computed bounds are non-null ASCII C strings, so array/order drift can become unsafe.

Test signals: compile tracepoints, run Binder operations that emit common commands and returns, inspect trace output names, and compare nonzero `binder_logs/stats` counters with expected command names. Adding a UAPI constant should include a stats/trace string-table review.
