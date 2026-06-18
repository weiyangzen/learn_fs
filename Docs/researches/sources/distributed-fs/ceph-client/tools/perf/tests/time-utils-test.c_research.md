## sources/distributed-fs/ceph-client/tools/perf/tests/time-utils-test.c

Purpose: unit tests for parsing absolute and percentage-based perf time ranges.
Important types/functions: `struct test_data`, `test__parse_nsec_time`, `test__perf_time__parse_str`, `test__perf_time__parse_for_ranges`, and `test__time_utils`.
Control flow: validates nanosecond conversion from decimal seconds, parses explicit start/end ranges, then constructs synthetic sessions with first/last sample times to test percentage slices and `perf_time__ranges_skip_sample`.
State and persistence: heap-allocated range arrays from `perf_time__parse_for_ranges` are freed per case.
Dependencies and integration: `parse_nsec_time`, `perf_time__parse_str`, `perf_time__parse_for_ranges`, `perf_time__ranges_skip_sample`, and `perf_session`/`evlist` first-last sample metadata.
Risks: boundary expectations are exact and cover inclusive endpoints; overflow-edge value uses max u64 decimal.
Test signals: all explicit/percentage ranges parse and skip/keep sample timestamps as expected.
