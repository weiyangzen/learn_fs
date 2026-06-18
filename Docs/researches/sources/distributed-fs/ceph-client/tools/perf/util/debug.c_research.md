# sources/distributed-fs/ceph-client/tools/perf/util/debug.c

## Purpose

`debug.c` implements perf's general debug, verbose, quiet, trace-dump, and stack-dump support. It centralizes debug output routing, optional timestamps, raw event dumping, sublevel debug-option parsing, libapi print hooks, and backtrace reporting.

## Important APIs, Types, and Functions

Global controls include `verbose`, `quiet`, `dump_trace`, `debug_ordered_events`, `debug_data_convert`, `debug_peo_args`, `debug_kmaps`, and `debug_type_profile`. Public functions include `debug_file()`, `debug_set_file()`, `debug_set_display_time()`, `veprintf()`, `eprintf()`, `eprintf_time()`, `pr_stat()`, `dump_printf()`, `trace_event()`, `perf_debug_option()`, `perf_quiet_option()`, `perf_debug_setup()`, `__dump_stack()`, `dump_stack()`, and `sighandler_dump_stack()`.

## Control Flow

`veprintf()` emits only when the selected variable meets the requested level, routing to UI helpline or the debug file. Time-prefixed helpers print wall-clock or perf timestamp prefixes. `trace_event()` dumps raw binary event bytes only when `dump_trace` is set. `perf_debug_option()` parses comma/sublevel options and adjusts libtraceevent log level. Quiet mode sets all debug values to disabled. Stack dumping builds a live machine/thread model when possible, resolves each frame to symbol/source, and falls back to `backtrace_symbols_fd()` if available.

## State and Persistence Behavior

State is process-global and not persisted across perf runs. `_debug_file` defaults lazily to stderr with a warning if not configured. Signal handling prints a stack, restores the default handler, and re-raises the signal.

## Dependencies and Integration Points

The module integrates with perf UI, color output, binary printers, event and symbol resolution, source-line lookup, libtraceevent logging, libapi debug hooks, and optional execinfo backtrace support. `debug.h` macros route most perf diagnostics here.

## Risks and Edge Cases

Stack dumping from a signal handler uses non-async-safe operations by design and documents that risk. Debug routing changes under browser UI unless `debug=stderr` is requested. Quiet mode must reset bool-like debug globals to zero after setting sublevel values to `-1`. Lazy debug-file initialization can recurse through warning macros if changed carelessly.

## Test Signals

Tests should cover verbose thresholds, debug suboptions, quiet mode suppression, timestamp display, stderr override with browser UI, raw event dump formatting, libtraceevent log-level adjustment, stack dumping with and without backtrace support, and signal handler re-raise behavior.
