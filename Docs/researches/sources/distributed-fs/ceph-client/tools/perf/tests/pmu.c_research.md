<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c

## Purpose

This selftest validates sysfs PMU format parsing, sysfs event parsing, event name rules, PMU name normalization/comparison, wildcard matching, and user config preservation.

## Research

`test_pmu_get` creates a temporary fake sysfs PMU with `type`, `format`, and `events/test-event` files, then loads it through `perf_pmus__add_test_pmu`; `test_pmu_put` removes the temp tree and deletes the PMU. `test__pmu_format` parses explicit terms and checks exact `config`, `config1`, and `config2` bit packing. `test__pmu_events` parses the fake sysfs event and checks the same packed values. `test__pmu_usr_chgs` verifies `evsel__set_config_if_unset` does not overwrite raw/user-provided fields but fills unset fields. `test__pmu_event_names` walks real sysfs PMU events and enforces all-lower/all-upper naming except legacy cache names. Name tests cover suffix stripping, numeric ordering, and `perf_pmu__wildcard_match`. State includes fake sysfs directories under `/tmp` and global PMU list entries. Dependencies are sysfs helpers, parse-events, file availability, and cleanup. Risks are `system("rm -fr")` path safety, real sysfs naming exceptions, and bitfield expectations if format parser semantics change. Passing signals are exact config values and successful naming/matching assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c -->
