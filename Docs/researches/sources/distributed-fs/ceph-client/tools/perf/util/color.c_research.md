# sources/distributed-fs/ceph-client/tools/perf/util/color.c

Purpose: centralizes ANSI color emission for perf text output and percent/value threshold coloring.

Important APIs/functions: `color_vsnprintf`, `color_vfprintf`, `color_snprintf`, `color_fprintf`, `get_percent_color`, `percent_color_fprintf`, `value_color_snprintf`, `percent_color_snprintf`, and `percent_color_len_snprintf`.

Control flow: helpers lazily auto-detect color when `perf_use_color_default < 0`, based on TTY or pager state. They wrap formatted output in color/reset sequences only when enabled. Percent helpers classify absolute values by `MIN_RED` and `MIN_GREEN`.

State and persistence: global `perf_use_color_default` stores auto/forced color policy.

Dependencies and integration: uses Linux `scnprintf`/`vscnprintf`, `isatty`, pager state, math `fabs`, and constants from `color.h`. Used by report/stat/callchain formatting.

Risks: auto-detection is sticky and based on the first stream used. Return values intentionally exclude color escape length for some paths. Varargs helpers assume exact argument types.

Test signals: TTY, pager, non-TTY, forced colors, threshold edges, snprintf truncation, and visible width assumptions.
