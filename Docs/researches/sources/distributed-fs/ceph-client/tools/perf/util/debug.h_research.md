# sources/distributed-fs/ceph-client/tools/perf/util/debug.h

## Purpose

`debug.h` declares perf's debug-printing API and common diagnostic macros used across the perf utility code.

## Important APIs, Types, and Functions

The header declares global debug controls, `pr_err`, `pr_warning`, `pr_warning_once`, `pr_info`, `pr_debug`, `pr_debugN`, `pr_debug2_peo`, timestamped ordered-event macros, UI warning/error functions, `dump_printf()`, `trace_event()`, `pr_stat()`, `eprintf*()`, debug option helpers, debug-file setters, stack dump helpers, and `STRERR_BUFSIZE`.

## Control Flow

Most behavior is macro expansion into `eprintf()` or `eprintf_time()`, with one-shot warnings implemented through function-local static flags. `pr_debug2_peo` uses `debug_peo_args` to force perf-event-open traces at level 0 or normal debug level 2.

## State and Persistence Behavior

The header exposes process-global debug variables owned by `debug.c`. One-shot warning macros create static state at each call site. No persistent state is written.

## Dependencies and Integration Points

It depends on stdarg/stdbool/stdio and Linux compiler annotations. It is included throughout perf and forms the stable interface between local modules and `debug.c`.

## Risks and Edge Cases

Macros evaluate formatting arguments only when called into functions, but callers must still avoid side effects in macro arguments where normal C evaluation applies. Call-site static state in `*_once` macros is per expansion. Debug global semantics mix integer levels and bool-like flags, so quiet/setup code must handle both.

## Test Signals

Build tests should validate printf-format checking. Runtime tests should verify once-only warnings, ordered-event timestamp macros, perf-event-open debug routing, UI warning macros, and quiet/verbose interaction.
