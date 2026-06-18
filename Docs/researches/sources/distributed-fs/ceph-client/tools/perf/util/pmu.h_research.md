# sources/distributed-fs/ceph-client/tools/perf/util/pmu.h

## Purpose
This header defines the PMU data model and public PMU operations used across perf event parsing, listing, selection, validation, and output.

## Important APIs, Types, and Functions
Core types are `struct perf_pmu`, `struct perf_pmu_caps`, `struct perf_pmu_info`, `struct pmu_event_info`, and `struct perf_pmu_format`. It defines PMU kind/type ranges for kernel perf-event PMUs, DRM, HWMON, tool, and fake PMUs. The header declares PMU configuration, alias checking, format packing, event iteration, matching, sysfs path helpers, caps parsing, deletion, and `perf_pmu__kind`.

## Control Flow
The header is declarative, with one inline classifier `perf_pmu__kind` that maps a PMU type value to an enum range. Runtime behavior is implemented mainly in `pmu.c` and consumed by `pmus.c`, parse-events, and print-events.

## State and Persistence
`struct perf_pmu` stores persistent in-process state for each discovered PMU: names, type, core/uncore flags, auxtrace flag, format list, alias hashmap, event-table pointer, alias counters, caps, CPU map, config masks, missing-feature flags, and memory-event descriptors.

## Dependencies and Integration Points
It depends on Linux bitmaps/lists/perf ABI, parse-events, generated pmu-events tables, map symbols, and memory-event definitions. It is the shared contract between PMU discovery, event parser, PMU printer, tool PMUs, hwmon, DRM, and architecture-specific code.

## Risks
The structure is broad and mutable, so initialization discipline matters. Fields such as `sysfs_aliases_loaded`, `cpu_aliases_added`, and `config_masks_computed` gate lazy work and can cause stale behavior if not reset in tests. Type range changes must stay aligned with `perf_pmu__kind`.

## Test Signals
Header-level signals are build coverage and ABI consistency. Unit tests can validate type classification, fake PMU behavior, initialized list heads, and that call sites do not dereference optional fields before initialization.
