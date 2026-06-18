# sources/distributed-fs/ceph-client/tools/perf/util/color.h

Purpose: declares color constants, thresholds, global color policy, and formatting helpers for perf output.

Important APIs/types: `COLOR_MAXLEN`, ANSI color constants, `MIN_GREEN`, `MIN_RED`, `PERF_COLOR_DELETE_LINE`, extern `perf_use_color_default`, color formatting functions, and config parser.

Control flow: callers use wrappers instead of raw `fprintf`/`snprintf` when output should respect perf color policy.

State and persistence: exposes mutable global `perf_use_color_default`.

Dependencies and integration: includes compiler printf annotations, stdio, and stdarg. Shared by reporting, UI, stat, and callchain value formatting.

Risks: visible length and byte length differ when color is enabled. Varargs helper call sites must match expected types.

Test signals: format checking and color/no-color output comparisons.
