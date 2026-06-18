<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c

## Purpose

`svghelper.c` implements the low-level SVG writer used by perf timeline-style tools. It converts perf timestamps, CPU slots, scheduler states, frequency states, wakeups, interrupt points, and IO spans into SVG rectangles, lines, circles, text, titles, and descriptions. The file is not a general SVG library; it is a stateful renderer with fixed layout constants and perf-specific assumptions about nanosecond timestamps, CPU topology, and timeline rows.

## Important APIs, Types, and Functions

The public entry points are declared in `svghelper.h`. `open_svg()` opens the output file, initializes `first_time`, `last_time`, page width, total height, and CSS classes. `svg_close()` terminates and closes the SVG. Timeline drawing functions include `svg_box()`, `svg_ubox()`, `svg_lbox()`, `svg_fbox()`, `svg_blocked()`, `svg_running()`, `svg_waiting()`, `svg_process()`, `svg_cstate()`, `svg_pstate()`, `svg_wakeline()`, `svg_partial_wakeline()`, `svg_interrupt()`, `svg_text()`, `svg_time_grid()`, `svg_io_legenda()`, and `svg_legenda()`. `svg_build_topology_map()` builds an optional CPU display-order map from `struct perf_env`.

Important file-global state includes `svgfile`, `first_time`, `last_time`, `total_height`, `max_freq`, `turbo_frequency`, `topology_map`, and exported globals `svg_page_width`, `svg_highlight`, and `svg_highlight_name`. The internal `struct topology` stores parsed sibling-core and sibling-thread masks as local `cpumask_t` arrays.

## Control Flow and Data Flow

Callers first invoke `open_svg()` with CPU count, extra row count, and timestamp bounds. The renderer rounds `first_time` down to a 100 ms boundary, enlarges `svg_page_width` for long recordings, writes XML/SVG headers, and emits CSS classes for process, sample, IO, wait, CPU, p-state, and c-state elements. Subsequent drawing calls are no-ops if `svgfile` is not open.

Timestamp coordinates flow through `time2pixels()`, which scales nanoseconds between `first_time` and `last_time` into the current page width. CPU coordinates flow through `cpu2y()`, optionally remapped by `topology_map`, then scaled by `SLOT_MULT` and `SLOT_HEIGHT`. Duration labels are produced by `time_to_string()`. `svg_running()` and `svg_process()` select the highlighted sample class based on duration or process-name matching. `svg_pstate()` normalizes frequency against `max_freq`, while `svg_cstate()` maps idle state depth to CSS class `c1` through `c6`.

Topology construction parses NUL-separated sibling maps from `perf_env`, converts each CPU-list string with `perf_cpu_map__new()`, fills bitmaps, then scans core groups and thread groups to assign display slots.

## State and Persistence Behavior

The persistent output is the SVG file written to disk. Rendering state is process-global and supports only one active SVG at a time. `svg_page_width`, `svg_highlight`, and `svg_highlight_name` are exported mutable knobs, so caller configuration persists across rendering calls. `svg_build_topology_map()` allocates `topology_map` and does not free a previously allocated map in this file, making it effectively process-lifetime state. `cpu_model()` reads `/proc/cpuinfo` and cpufreq sysfs on demand and updates global `max_freq`.

## Dependencies and Integration Points

The code depends on Linux bitmap helpers, perf CPU map APIs, `struct perf_env`, `/proc/cpuinfo`, and `/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies`. It integrates with perf visualization code that has already interpreted scheduling or IO events and only needs an SVG emission backend. It also integrates with perf environment capture because topology ordering uses `env->sibling_cores`, `env->sibling_threads`, and `env->nr_cpus_online`.

## Risks and Edge Cases

`time2pixels()` divides by `last_time - first_time`, so equal start/end times would break scaling. Caller-provided strings are written into XML text, title, and desc nodes without escaping except for a few literal arrow labels, so process names or backtraces containing XML metacharacters can corrupt output. `normalize_height()` returns `0.100` for heights at or above `0.75`, which is surprising and should be tested before changing because it may be a bug or an intentional visual cap. Many drawing functions assume valid row and CPU indices; out-of-range CPU IDs can index `topology_map` unsafely. File-global state makes the API unsuitable for concurrent SVG writers.

## Test Signals

Useful tests include generating a small timeline with known timestamp bounds and checking SVG dimensions, CSS class presence, and expected coordinate scaling. Regression tests should cover highlight-by-duration, highlight-by-process-name, IO boxes, wake lines in both directions, c-state clamping above C6, p-state formatting including turbo frequency, and topology remapping from a synthetic `perf_env`. Negative tests should cover zero-duration recordings, failed output open, missing cpufreq sysfs, and process names/backtraces requiring XML escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/svghelper.c -->
