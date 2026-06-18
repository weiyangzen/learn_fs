# sources/distributed-fs/ceph-client/tools/perf/tests/expand-cgroup.c

## Purpose
Tests that an existing `evlist` can be expanded across multiple cgroups without changing the original event ordering, names, or group membership semantics. It exercises default events, explicit grouped events, libpfm events when enabled, and metric-derived events.

## Important APIs, Types, and Functions
- `test_expand_events(struct evlist *evlist)` is the shared verifier. It snapshots original event names, original grouping state, and first-event `nr_members`, calls `evlist__expand_cgroup(evlist, "A,B,C", false)`, then checks expanded entries are grouped by cgroup and repeat the original event sequence.
- `expand_default_events()` builds `evlist__new_default(&target, false)`.
- `expand_group_events()` parses `{cycles,instructions}` after setting `symbol_conf.event_group = true`.
- `expand_libpfm_events()` calls `parse_libpfm_events_option()` with `"CYCLES"` and treats an empty evlist as libpfm unavailable.
- `expand_metric_events()` uses `find_core_metrics_table("testarch", "testcpu")` and `metricgroup__parse_groups_test()` for metric `CPI`.
- The test uses `struct evlist`, `struct evsel`, `struct cgroup`, `struct target`, `struct option`, and parse-event/metric/libpfm helper APIs.

## Control Flow
`test__expand_cgroup_events()` runs the four constructors in sequence. Each constructor creates an evlist, populates it, invokes `test_expand_events()`, then deletes the evlist. The core verifier first stores event names before expansion, records whether the original first event was a group and how many members it had, expands against cgroups `A`, `B`, and `C`, then walks the resulting evlist. It expects `original_event_count * 3` entries, with `ev_name[i % original_count]` and `cgrp_name[i / original_count]`. For the first event in each cgroup block it verifies group status and member count match the original.

## State and Persistence
State is in-memory only: the evlist is mutated by `evlist__expand_cgroup()`, temporary event-name strings are allocated and freed, and `symbol_conf.event_group` is set for grouped/libpfm cases. No files are written. The libpfm path depends on build/runtime support and can short-circuit before expansion if no event was created.

## Dependencies and Integration Points
The test integrates with perf event parsing (`parse_events()`), metric parsing (`metricgroup__parse_groups_test()`), libpfm parsing (`parse_libpfm_events_option()`), cgroup expansion, and the perf test suite registration via `DEFINE_SUITE("Event expansion for cgroups", expand_cgroup_events)`.

## Risks and Edge Cases
- `symbol_conf.event_group` is global state and is not restored locally; other tests must tolerate the suite environment or reset global symbol configuration.
- The verifier assumes expansion order is cgroup-major with event order preserved inside each cgroup.
- The libpfm branch treats an empty evlist as a non-fatal unavailable path, so a disabled libpfm build does not actually exercise expansion for that case.
- Only first-event group metadata is checked; deeper per-member leader relationships are indirectly covered by group member counts but not exhaustively validated.

## Test Signals
Failures report count, event-name, cgroup-name, group-flag, or group-member mismatches via `pr_debug()` and `TEST_ASSERT_*`. A passing suite signals that default, grouped, libpfm-enabled, and metric-generated evlists remain structurally coherent after cgroup expansion.
