# sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.c

## Purpose

`tp_pmu.c` exposes tracepoints through the generic PMU event-enumeration interface. It discovers tracepoint systems/events under tracefs, reads event IDs and format files, and reports them as PMU events.

## Important APIs, Types, and Functions

Public functions are `tp_pmu__id()`, `tp_pmu__for_each_tp_event()`, `tp_pmu__for_each_tp_sys()`, `perf_pmu__is_tracepoint()`, `tp_pmu__for_each_event()`, `tp_pmu__num_events()`, and `tp_pmu__have_event()`. Internal callbacks skip non-event directory entries and assemble `struct pmu_event_info` with name, encoding description, long format text, PMU name, and tracepoint descriptor.

## Control Flow and State

System iteration opens tracefs `events`, skips control/header directories, and invokes a system callback. Event iteration opens one system directory, skips `enable` and `filter`, and invokes an event callback. Full PMU enumeration reads `id` for encoding and `format` for the long description, replacing tabs with spaces for rendering. Existence checks split `system:event` and verify the ID can be read.

## Dependencies and Integration Points

It depends on tracefs path helpers, `io_dir`, filename read helpers, PMU definitions, and print-events callbacks. It backs `perf list` and tracepoint PMU lookup.

## State and Persistence Behavior

There is no module-owned persistent state. All data is discovered live from tracefs and returned through callbacks.

## Risks and Test Signals

Risks include disappearing tracepoints during iteration, permission failures, long format allocations, malformed names without colons, and tracefs not mounted. Tests should run with tracefs present and absent, enumerate at least one known tracepoint, verify `system:event` encoding, count events, and handle callback early termination.
