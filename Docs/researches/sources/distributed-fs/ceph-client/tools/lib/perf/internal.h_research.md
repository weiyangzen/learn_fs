<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/internal.h

## Purpose
This private libperf header declares the internal logging function and convenience macros used by implementation files.

## Important APIs, Types, and Functions
- `libperf_print(enum libperf_print_level level, const char *format, ...)` is printf-annotated for compile-time format checking.
- `__pr(level, fmt, ...)` prefixes messages with `libperf: `.
- `pr_err`, `pr_warning`, `pr_info`, `pr_debug`, `pr_debug2`, and `pr_debug3` map to the corresponding libperf print levels.

## Control Flow and State
The macros evaluate to calls into the configured libperf print path. The effective sink is controlled by `libperf_init` from the public core API.

## Dependencies and Integration Points
It includes `perf/core.h`. `mmap.c` uses debug macros for ring-buffer diagnostics and warnings. Other libperf implementation files can use the same private logging surface.

## Risks and Test Signals
Logging macros must not evaluate side effects unexpectedly beyond normal printf argument evaluation. Since they always prefix messages, callers should avoid duplicating prefixes. Tests install a `vfprintf` callback and therefore exercise the print path whenever warnings/debug output is emitted, though most tests do not assert log text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/internal.h -->
