<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c

## Purpose

This perf selftest verifies that perf can parse old-kernel event streams where `sample_id_all` is not set. The target case is multiple selected events followed by a non-sample record, where no trailing sample id exists to disambiguate event ownership.

## Research

Important functions are `process_event`, `process_events`, and `test__parse_no_sample_id_all`. `process_event` first feeds `PERF_RECORD_HEADER_ATTR` records to `perf_event__process_attr`, rejects user-private record types, requires an initialized `evlist`, then initializes a `perf_sample` and calls `evlist__parse_sample`. The synthetic test creates two attribute records with ids 1 and 2 plus a `PERF_RECORD_MMAP` record, then validates that the parser does not fail when the mmap record lacks appended id data. State is only in the transient `evlist` built from attr records and the stack-allocated synthetic events. Dependencies are `event.h`, `evlist.h`, `header.h`, and `util/sample.h`. Integration is direct with perf's sample parser and suite registration through `DEFINE_SUITE`. Risks include false regressions if synthetic record sizes stop matching kernel layout, and missed coverage for newer non-sample records. Test signal is `TEST_OK` when all three records parse without relying on `sample_id_all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c -->
