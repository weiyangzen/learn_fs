# sources/distributed-fs/ceph-client/tools/perf/util/pmus.c

## Purpose
This file manages the global collection of discovered PMUs. It lazily scans sysfs and tool-provided PMU sources, separates core PMUs from other PMUs, sorts and deduplicates names, finds PMUs by name/type/attr, and prints PMU event catalogs.

## Important APIs, Types, and Functions
Exports include `perf_pmus__find`, `perf_pmus__find_by_type`, `perf_pmus__find_by_attr`, scan functions, `perf_pmus__print_pmu_events`, `perf_pmus__print_raw_pmu_events`, `perf_pmus__have_event`, `perf_pmus__num_core_pmus`, `perf_pmus__supports_extended_type`, test PMU adders, `perf_pmus__fake_pmu`, and `perf_pmus__destroy`.

## Control Flow
`perf_pmus__find` first checks loaded lists, then selectively scans core, other, tool, hwmon, or DRM PMUs based on the requested name. `pmu_read_sysfs` opens the event source devices directory, creates PMUs through `perf_pmu__lookup`, adds placeholder core PMUs if needed, adds tool/hwmon/DRM PMUs, sorts lists, and marks type groups as read. Printing first counts all events, copies event metadata into a sortable array, sorts by topic/core/PMU/name, suppresses duplicates, and calls print callbacks.

## State and Persistence
The file owns static `core_pmus`, `other_pmus`, `read_pmu_types`, and cached extended-type support state. All state is in-process and reset by `perf_pmus__destroy`.

## Dependencies and Integration Points
It depends on sysfs PMU lookup in `pmu.c`, tool PMUs, hwmon, DRM, print callbacks, event support probing, list sorting, pthread once, and parse helpers for PMU name suffixes.

## Risks
Lazy scanning and static caches can leak cross-test assumptions if not destroyed. PMU suffix deduplication is architecture-sensitive, especially for decimal versus hexadecimal suffixes. Extended hardware type support is cached once and depends on opening real events successfully.

## Test Signals
Synthetic sysfs tests should verify scan order, core placeholder creation, suffix sorting, duplicate suppression, wildcard scans, attr fallback to first core PMU, and destroy/reset behavior. Runtime tests should cover hybrid core PMUs and unsupported extended types.
