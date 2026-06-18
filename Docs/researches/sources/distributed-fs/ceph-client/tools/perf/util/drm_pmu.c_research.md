# sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.c

## Purpose
This file implements a perf pseudo-PMU for Linux DRM usage statistics exposed through `/proc/<pid>/fdinfo`. It discovers DRM drivers/events from live file descriptors, exposes those events through perf's PMU listing/parsing interfaces, and reads counters by summing fdinfo values for a selected pid or system-wide view.

## Important APIs, Types, And Functions
Public APIs include `perf_pmu__is_drm()`, `evsel__is_drm()`, `perf_pmus__read_drm_pmus()`, `drm_pmu__exit()`, `drm_pmu__have_event()`, `drm_pmu__for_each_event()`, `drm_pmu__num_events()`, `drm_pmu__config_terms()`, `drm_pmu__check_alias()`, `evsel__drm_pmu_open()`, and `evsel__drm_pmu_read()`. Internal structures are `struct drm_pmu`, `struct drm_pmu_event`, `enum drm_pmu_unit`, `struct minor_info`, and callback argument structs for discovery/read passes.

## Control Flow
Discovery walks numeric `/proc` directories, opens `fd` and lazily `fdinfo`, filters character devices with major 226, deduplicates DRM minors, and parses `drm-driver:` plus recognized `drm-*` statistic lines. Each new driver becomes a pseudo-PMU with a synthetic type in the DRM range, and each statistic name becomes an event indexed by array position. Event parsing sets `attr->config` to that index. Reads either scan a single pid or all pids, match the configured event name in fdinfo, convert units, sum values, and update perf counts.

## State, Dependencies, And Integration
Each `struct drm_pmu` embeds `struct perf_pmu`, owns a dynamic event array, and uses synthetic CPU map `0`. The implementation depends on procfs helpers, `api/io` line reading, `perf_counts`, thread maps, parse-events errors, PMU metadata callbacks, and Linux DRM fdinfo conventions. No kernel perf_event fd is opened; `evsel__drm_pmu_open()` is a no-op because reads are procfs scans.

## Risks And Test Signals
Risks include races while processes exit or close fds, fdinfo format drift, a probable unit typo where `drm-total-cycles-` is registered as bytes instead of cycles, duplicate-minor suppression changing totals, unchecked growth failures in the minor array causing possible out-of-bounds writes, and synthetic PMU type exhaustion. Tests should mock procfs fd/fdinfo trees, verify event discovery/deduplication, parse all unit conversions, validate parse-event errors, compare per-pid and system-wide sums, and exercise disappearing processes/fds.
