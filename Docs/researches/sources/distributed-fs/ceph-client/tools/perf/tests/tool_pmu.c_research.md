## sources/distributed-fs/ceph-client/tools/perf/tests/tool_pmu.c

Purpose: unit tests for parsing tool PMU events with and without explicit `tool/` PMU name.
Important functions: `do_test`, `test__tool_pmu_without_pmu`, and `test__tool_pmu_with_pmu`.
Control flow: iterates `tool_pmu__for_each_event`, builds either `tool/<event>/` or bare event strings, parses them into an evlist, validates event count, finds an evsel whose PMU is tool PMU, and checks attr config equals the enum value.
State and persistence: evlist and parse error objects are allocated and freed per event.
Dependencies and integration: parser, `tool_pmu__event_to_str`, `perf_pmu__is_tool`, and evsel attr config.
Risks: events with no string are expected to fail parse and count as OK; bare names may parse to additional aliases, so only at least one event is required.
Test signals: suite `Tool PMU` has two cases covering explicit and implicit PMU naming.
