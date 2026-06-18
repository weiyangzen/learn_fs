# sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c` implements the s390 architecture-specific raw sample dump callback. It validates and prints CPU Measurement Counter Facility diagnostic raw data and PAI crypto/NNPA raw counter records when perf displays raw samples.

## Important APIs, Types, and Functions

The public callback is `evlist__s390_sample_raw`. Internal helpers include `ctrset_size`, `ctrset_valid`, `s390_cpumcfdg_testctr`, `s390_cpumcfdg_dumptrail`, `get_counterset_start`, PMU event-name lookup/cache helpers `get_counter_name_callback`, `get_counter_name_hash_fn`, `get_counter_name_hashmap_equal_fn`, `get_counter_name`, counter dump `s390_cpumcfdg_dump`, PAI validation `s390_pai_all_test`, and PAI dump `s390_pai_all_dump`.

## Control Flow

The callback ignores non-sample events, maps the raw event to an evsel, and returns if no raw data is present. For `PERF_EVENT_CPUM_CF_DIAG`, it ensures the `cpum_cf` PMU is available, validates the raw counter-set byte stream, and dumps counter sets plus trailer. Validation walks big-endian counter-set headers and accepts the known 4-byte padding offset before the trailer. For PAI NNPA or crypto events, it validates minimum record size, finds the PMU by type if needed, then dumps 10-byte event/value records until no full record remains.

Counter names are resolved by scanning PMU event metadata for matching `event=HEX` strings and cached in a static hashmap keyed by constructed event number.

## State and Persistence Behavior

The file maintains a static counter-name cache tied to the last PMU pointer. It mutates `evsel->pmu` lazily when it finds the needed PMU. It writes formatted output to stdout/stderr only and persists no files.

## Dependencies and Integration Points

It depends on perf evlist/evsel mapping, sample raw callback setup from `sample-raw.c`, s390 counter facility ABI structures, PMU metadata iteration, hashmap utilities, color output, and big-endian conversion helpers.

## Risks and Edge Cases

The static cache is not synchronized and assumes one active PMU identity. PAI validation only checks a minimum size, so malformed trailing bytes can be silently ignored by loop bounds. Counter-set parsing depends on raw data alignment and the special 4-byte padding rule. PMU event string parsing assumes `event=%x` appears in metadata. Output-only behavior means errors are reported but do not fail report processing.

## Test Signals

Tests should feed known-good and malformed CPUM_CF raw buffers, trailer padding cases, PAI crypto/NNPA record streams, unknown counter names, PMU cache hit/miss paths, missing evsel/PMU cases, and endian conversion fixtures.
