# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/hybrid.c

## Purpose
This file tests perf event parsing on x86 hybrid-PMU systems. It verifies that parser output correctly represents PMU-qualified hardware events, event groups mixing hardware/software/raw events, modifiers, raw events, cache aliases, and explicit PMU config terms.

## Important APIs, Types, and Functions
The core data type is `struct evlist_test`, containing an event string, optional validity predicate, and checker callback. `test__hybrid_events[]` enumerates ten parser cases such as `cpu_core/cycles/`, grouped `cpu_core` events, mixed `cpu-clock` groups, raw `r1a`, `cpu_core/r1a/`, explicit `config/config1/config2/period`, `LLC-loads`, and a group containing both `cycles` and `cpu-cycles`.

Checker helpers inspect parsed `struct evlist` and `struct evsel` objects: `test_config()` masks `attr.config`, `test_perf_config()` handles `struct perf_evsel`, `test_hybrid_type()` extracts PMU type bits, and the `test__hybrid_*` functions assert event count, event type, config, hybrid PMU type, modifiers, and group leader relationships.

## Control Flow
For each table entry, `test_event()` allocates an evlist, initializes `parse_events_error`, calls `parse_events()`, prints parser diagnostics on failure, maps trace-event access errors to `TEST_SKIP`, otherwise runs the checker, then cleans up. `test_events()` preserves failure over later results and preserves skip when previous entries skipped but later entries pass. `test__hybrid()` skips non-hybrid systems where `perf_pmus__num_core_pmus() == 1`.

## State and Persistence
There is no durable state. Runtime state consists of allocated evlists, evsels, parser error structures, and PMU lookups. Every evlist is deleted before returning from `test_event()`.

## Dependencies and Integration Points
The file depends on perf parser APIs, evlist/evsel internals, PMU discovery, and perf UAPI event type/config constants. `arch-tests.c` registers it as the `"x86 hybrid"` suite with a skip reason of `"not hybrid"`.

## Risks and Edge Cases
The test encodes assumptions about hybrid PMU names beginning with `cpu_`, PMU type packing into `attr.config`, and specific parser behavior for aliases and groups. It runs only meaningful checks on hybrid hosts; non-hybrid systems skip. Event parser behavior involving trace-event permissions can return skip, so parser regressions must be distinguished from environment restrictions. If PMU alias names change, the string fixtures may fail while lower-level event encoding remains valid.

## Test Signals
Passing output means all ten event strings parse and the evlist structure matches expected type/config/group semantics. Failures identify the table index and event string. Skip is expected on non-hybrid machines or when parser errors are solely due to inaccessible trace events.
