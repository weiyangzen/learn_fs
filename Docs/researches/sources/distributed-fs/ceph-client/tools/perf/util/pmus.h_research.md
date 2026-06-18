# sources/distributed-fs/ceph-client/tools/perf/util/pmus.h

## Purpose
This header declares the global PMU registry API used to discover, iterate, query, and print PMUs.

## Important APIs, Types, and Functions
It exposes PMU name comparison helpers, registry destruction, find-by-name/type/attr, iteration over all/core/event-matching/wildcard PMUs, event printing, raw PMU event printing, event existence checks, core PMU counts, extended-type support, test PMU insertion, fake PMU access, and first-core-PMU lookup.

## Control Flow
The header has no implementation control flow. Its functions are implemented in `pmus.c`, with individual PMU details delegated to `pmu.c` and specialized PMU providers.

## State and Persistence
No state is declared here, but the API operates on the static global PMU lists owned by `pmus.c`.

## Dependencies and Integration Points
It depends on `struct perf_pmu`, `struct perf_event_attr`, and `struct print_callbacks`. Consumers include event parsing, attr formatting, event listing, tests, and evsel PMU resolution.

## Risks
The API hides lazy global scans, so callers may trigger sysfs reads or event probes unexpectedly. Test helper functions mutate global PMU lists and require cleanup discipline.

## Test Signals
Build coverage should ensure all registry consumers include this header cleanly. Unit tests should validate name comparison and that `perf_pmus__destroy` resets state after using test PMUs.
