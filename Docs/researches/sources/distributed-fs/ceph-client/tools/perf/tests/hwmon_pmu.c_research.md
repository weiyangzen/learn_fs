# sources/distributed-fs/ceph-client/tools/perf/tests/hwmon_pmu.c

## Purpose
Tests perf's hwmon PMU filename parser and event parsing for simulated hwmon sysfs data, both with explicit PMU names and alias-only event names.

## Important APIs, Types, and Functions
- `test_events[]` defines two temperature events, aliases `temp1`/`temp2`, and expected `union hwmon_pmu_event_key` values.
- `test_pmu_get()` creates a temporary hwmon directory tree under `/tmp`, writes a `name` file plus `temp*_label` and `temp*_input` files, then registers it with `perf_pmus__add_test_hwmon_pmu()`.
- `test_pmu_put()` removes the temporary directory, unlinks the PMU from the global PMU list, and deletes it.
- `do_test()` parses either `hwmon_a_test_hwmon_pmu/<event>/` or the alias/name alone and verifies the resulting evsel uses the expected PMU and config.
- `test__parse_hwmon_filename()` table-tests filename decomposition into type, number, item, alarm flag, and parse success.

## Control Flow
The suite has three test cases. The filename parser case iterates fixed valid and invalid filenames and checks returned fields. The PMU parsing cases build the fake PMU, then for each event parse both canonical event name and alias, once without explicit PMU name and once with explicit PMU name. The parse result must include an evsel for `hwmon_a_test_hwmon_pmu` whose config equals the packed type/number key.

## State and Persistence
The test creates and deletes temporary directories/files under `/tmp/perf-hwmon-pmu-test-*`. It also mutates the process-global PMU list by adding a test PMU and removing it in cleanup. No persistent artifact is intended after `test_pmu_put()`.

## Dependencies and Integration Points
Integrates with `hwmon_pmu.h`, perf PMU registration/scanning, `parse_events()`, and the test suite table `suite__hwmon_pmu`.

## Risks and Edge Cases
- `test_pmu_put()` shells out through `system("rm -fr ...")`; the generated temp path is controlled by `mkdtemp()` but still makes cleanup dependent on shell behavior.
- The error path in `test_pmu_get()` calls `test_pmu_put(dir, hwm)` even when `hwm` can be `NULL`, which would be unsafe if reached as written.
- Alias-only parsing may match multiple events; the test allows `nr_entries >= 1` in that mode and scans for the target PMU.

## Test Signals
Passing proves hwmon filenames parse correctly and synthetic hwmon PMU events/aliases resolve to the expected config. Failures include parse-event error dumps and field mismatch diagnostics.
