# sources/distributed-fs/ceph-client/rust/kernel/print.rs

## Purpose
Implements Rust printk support, including severity macros, continuation logging, `%pA` formatting bridge support, and lightweight once-only logging macros.

## APIs, Types, and Functions
`rust_fmt_argument` is the C-callable `%pA` formatter for `fmt::Arguments`. `format_strings` generates static `_printk` format strings for each kernel log level. Hidden helpers `call_printk` and `call_printk_cont` invoke `_printk`. Public macros include `pr_emerg!`, `pr_alert!`, `pr_crit!`, `pr_err!`, `pr_warn!`, `pr_notice!`, `pr_info!`, `pr_debug!`, `pr_cont!`, `do_once_lite!`, and `pr_*_once!`. `OnceLite` is a relaxed atomic call-once primitive.

## Control Flow, State, and Persistence
Print macros build `fmt::Arguments` outside the unsafe call and pass the module prefix plus fixed format string to `_printk` when `CONFIG_PRINTK` is enabled. `pr_debug!` is gated by `debug_assertions`. `do_once_lite!` creates a static `OnceLite` in `.data..once`; the first caller swaps state to complete and runs the closure, while later callers return without synchronization guarantees.

## Dependencies and Integration
Depends on generated printk bindings, `RawFormatter`, the Rust formatting system, atomic wrappers, module-generated `__LOG_PREFIX`, and kernel printk `%pA` integration. It is re-exported through the prelude and used pervasively by Rust kernel code.

## Risks and Test Signals
Risks include unsafety in `%pA` pointer interpretation, module prefix lifetime/null-termination assumptions, no dynamic-debug support for `pr_debug!`, relaxed `OnceLite` being mistaken for a synchronization primitive, and behavior differences when `CONFIG_PRINTK` is disabled. Test signals include printk macro compile tests, once-only concurrent stress, `%pA` formatting tests with bounded buffers, and builds with/without `CONFIG_PRINTK` and `testlib`.
