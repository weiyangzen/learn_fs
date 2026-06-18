# sources/distributed-fs/ceph-client/tools/perf/util/drm_pmu.h

## Purpose
This header declares the DRM pseudo-PMU interface used by perf PMU discovery, event parsing, opening, and reading paths. It documents that DRM metrics come from Linux DRM usage stats rather than hardware perf events.

## Important APIs And Types
The header exposes PMU lifecycle/query functions (`drm_pmu__exit()`, `drm_pmu__have_event()`, `drm_pmu__for_each_event()`, `drm_pmu__num_events()`), parse integration (`drm_pmu__config_terms()`, `drm_pmu__check_alias()`), classification helpers (`perf_pmu__is_drm()`, `evsel__is_drm()`), discovery (`perf_pmus__read_drm_pmus()`), and evsel operations (`evsel__drm_pmu_open()`, `evsel__drm_pmu_read()`).

## Control Flow And Integration
Perf PMU enumeration calls `perf_pmus__read_drm_pmus()` to append DRM pseudo-PMUs. Parse-event code checks event names and configures `perf_event_attr.config` through the DRM helpers. Runtime count collection uses the evsel helpers; open is intentionally a no-op and read performs procfs-backed accumulation.

## State And Persistence
Opaque state is stored behind `struct perf_pmu` in the implementation's container type. Consumers should treat DRM PMUs as synthetic PMUs identified by type range and should not expect kernel file descriptors or normal perf_event mmap/read behavior.

## Risks And Test Signals
Risks are mostly contract mismatches with generic PMU code that assumes kernel-backed events. Tests should ensure DRM PMUs are recognized by type, event iteration supplies unit/scale metadata, parse aliases reject invalid terms, and read paths update `perf_counts_values` consistently with other software PMU readers.
