# sources/distributed-fs/ceph-client/net/mac80211/trace.c

## Purpose
This file instantiates mac80211 tracepoints and, when message tracing is enabled, provides formatted logging wrappers that mirror mac80211 debug/info/error messages into trace events.

## Important APIs, types, and functions
- `CREATE_TRACE_POINTS` before including `trace.h` and `trace_msg.h` causes the Linux tracepoint definitions declared in those headers to be emitted in this translation unit.
- `__sdata_info()`, `__sdata_dbg()`, `__sdata_err()`, and `__wiphy_dbg()` are compiled under `CONFIG_MAC80211_MESSAGE_TRACING`.
- Each message wrapper builds a `struct va_format`, optionally prints through `pr_info`, `pr_debug`, `pr_err`, or `wiphy_dbg`, and always emits the matching `trace_mac80211_*` event.

## Control flow
The file is excluded from sparse checker processing through `#ifndef __CHECKER__`, because tracepoint macros are intentionally macro-heavy. During normal builds it includes cfg80211, driver ops, debug declarations, then defines and includes the trace headers. Message wrapper calls originate from macros in `debug.h`; they collect variadic arguments, set `vaf.va`, perform optional printk-style logging, emit a trace event, and then end the varargs scope.

## State and persistence
There is no durable state. Tracepoints are static kernel instrumentation objects generated at build time, and message wrapper state is stack-local `va_list`/`va_format` data. Emitted trace records persist only in the kernel tracing buffers configured by the runtime tracing subsystem.

## Dependencies and integration points
The file depends on Linux module and tracepoint infrastructure, cfg80211/mac80211 types, `driver-ops.h`, `debug.h`, `trace.h`, and `trace_msg.h`. It is the central instantiation point for trace events consumed by ftrace/perf/BPF-style tracing. The message wrappers integrate with `sdata_info`, `sdata_dbg`, `sdata_err`, and `wiphy_dbg` macros in `debug.h`.

## Risks and edge cases
Varargs must remain valid through both printk and trace assignment. Message tracing changes logging cost when enabled because strings are formatted into trace buffers even if ordinary debug printing is suppressed. The sparse exclusion means static-analysis coverage is weaker for this file. Tracepoint header include order and `CREATE_TRACE_POINTS` placement are fragile and must follow kernel tracepoint conventions.

## Test signals
Build success with tracing enabled verifies tracepoint instantiation. Runtime signals include visible events under the `mac80211` and `mac80211_msg` trace systems and correct duplication of debug messages into trace buffers when `CONFIG_MAC80211_MESSAGE_TRACING` is set.
