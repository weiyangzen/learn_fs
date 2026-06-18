# sources/distributed-fs/ceph-client/tools/perf/tests/parse-events.c

## Purpose
Large table-driven and helper-driven suite validating perf event string parsing. It covers tracepoints, raw/numeric/symbolic events, cache events, breakpoints, modifiers, PMU-qualified events, groups, leader sampling, pinned/exclusive flags, named events, all tracepoints, sysfs PMU events, aliases, and event term parsing.

## Important APIs, Types, and Functions
- Assertion helpers `check_evlist()`/`TEST_ASSERT_EVLIST` and `check_evsel()`/`TEST_ASSERT_EVSEL` format evlists/evsels on failure.
- `num_core_entries()` accounts for wildcard expansion across hybrid/core PMUs.
- Many `test__checkevent_*()` functions validate specific parsed `perf_event_attr` fields: type/config/config1-4, sample type/period, exclude flags, precise IP, breakpoint type/length, pinned/exclusive, names, PMU ownership, group leader/index/member state, and `sample_read`.
- Group validators `test__group1()` through `test__group5()`, `test__group_gh1()` through `test__group_gh4()`, `test__leader_sample1()`, and `test__leader_sample2()` verify event grouping, group modifiers, host/guest modifiers, and sample-read behavior.
- `struct evlist_test` pairs an event string, optional validity predicate, and checker. `test__events[]` and `test__events_pmu[]` are the main matrices.
- `struct terms_test` and `test__checkterms_simple()` validate parsed config terms.
- `test_event()`, `test_events()`, `test_event_fake_pmu()`, `test_term()`, and `test_terms()` are generic drivers.
- `test__pmu_events()` scans sysfs PMU event files and attempts to parse each non-parameterized event.
- `test_alias()` and alias tests validate PMU alias equivalence.

## Control Flow
Suite cases in `tests__parse_events[]` run six lanes. `events2` iterates `test__events[]`, replacing `default_core` placeholders with the detected core PMU name, parses with `__parse_events(..., fake_tp=true)`, and dispatches to the checker. `pmu_events` scans real sysfs PMU event directories, skips special or parameterized entries, parses `pmu/event=name/u`, and for core PMUs also checks mixed legacy/PMU syntax. `pmu_events2` runs the explicit PMU-qualified matrix. `alias` finds a sysfs PMU alias and checks alias/event parse equivalence. `pmu_events_alias2` uses fake PMU parsing for hyphenated aliases. `terms2` parses a comma-separated term string and checks the resulting linked list of `parse_events_term` entries.

## State and Persistence
Most state is in-memory evlists/evsels and parse error objects. Some tests read sysfs and tracing directories, count available tracepoints, inspect PMU event files, and read PMU alias files. No files are written. The suite adapts to platform state through validity predicates such as Intel PT presence, ACR format support, s390 KVM tracepoint availability, and default core PMU format support.

## Dependencies and Integration Points
This is the central test consumer of `parse-events.h`, PMU scanning, tracefs/sysfs helpers, breakpoint constants, evsel formatting, evlist formatting, event term parsing, and fake PMU/fake tracepoint parse modes. Registered as `suite__parse_events` with multiple named test cases and permission/alias skip reasons.

## Risks and Edge Cases
- Many expectations depend on hybrid PMU expansion; `num_core_entries()` and `perf_pmus__num_core_pmus()` are used to avoid single-PMU assumptions.
- Some TODO comments document known behavior: software events are not always grouped with hardware events across multiple PMUs, and group modifiers are not always copied to split group leaders.
- Real sysfs PMU event scanning can skip or fail based on host PMU files, permissions, parameterized events, or event names containing special characters.
- Exact parser names and modifier semantics are tightly encoded; intentional parser changes require coordinated test updates.
- `combine_test_results()` preserves failures over skips and preserves skip if all non-OK results are skips, which affects suite-level status aggregation.

## Test Signals
Passing indicates broad event parser coverage: correct attr fields for individual events, correct group/leader topology, correct modifier semantics, valid term parsing, parseability of host PMU events, alias equivalence, and platform-conditional behavior. Failures include formatted evsel/evlist details and parse error messages.
