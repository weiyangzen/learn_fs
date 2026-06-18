# sources/distributed-fs/ceph-client/tools/perf/util/print-events.c

## Purpose
This file coordinates printing of all event categories used by `perf list`: PMU events, raw descriptors, breakpoints, SDT events, metric groups, and libpfm events.

## Important APIs, Types, and Functions
Exports are `print_events`, `print_sdt_events`, `metricgroup__print`, and `is_event_supported`. Internal `struct mep` stores metric printing rows in an rbtree. The `event_type_descriptors` table labels perf event types.

## Control Flow
`print_events` invokes PMU event printing, emits generic raw and breakpoint templates, prints SDT events from build-id probe caches, prints metrics, and delegates libpfm event listing. `is_event_supported` opens a temporary evsel for the requested type/config and retries with `exclude_kernel` and then `exclude_guest` if needed. Metric printing gathers metrics into an ordered rbtree before invoking callbacks.

## State and Persistence
The file does not keep global state. It reads build-id caches, probe caches, PMU tables, and metric tables, and creates temporary evsels/thread maps/rbtrees.

## Dependencies and Integration Points
It depends on PMU registry printing, probe-file/cache code, build-id cache, metricgroup APIs, libpfm stubs/implementation, tracepoint and event parsing helpers, and `struct print_callbacks`.

## Risks
Support probing depends on privileges and kernel policy. `print_sdt_events` returns early without deleting `sdtlist` if build-id listing fails, which is a small cleanup risk. Duplicate SDT names require build-id/path disambiguation, so cache corruption can affect output names.

## Test Signals
Tests should verify callback order, raw/breakpoint templates, metric grouping by semicolon-separated groups, SDT duplicate disambiguation, and support probing retry behavior. Both libpfm-enabled and disabled builds should be covered.
