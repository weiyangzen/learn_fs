<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c

## Purpose

This selftest synthesizes perf sample records for every supported `PERF_SAMPLE_*` bit and verifies parsing reproduces the original `perf_sample` fields, including read formats, regs, stacks, branch stacks, and AUX data.

## Research

`samples_same` conditionally compares fields based on `sample_type`, `read_format`, and endian-swap expectations. `do_test` fills a rich `perf_sample`, computes the expected sample event size, allocates a padded event buffer, calls `perf_event__synthesize_sample`, verifies the written size by checking untouched `0xff` tail bytes, then parses via `evsel__parse_sample`. For branch stacks it repeats parsing with `needs_swap` and checks known big/little-endian flag values. `test__sample_parsing` requires updates when new sample bits exceed `PERF_SAMPLE_WEIGHT_STRUCT`, tests each sample bit alone, iterates read-format variants for `PERF_SAMPLE_READ`, and tests all bits together with mutually exclusive weight variants. State is only synthetic stack/heap data. Dependencies include sample synthesis, evsel sample size calculation, branch-stack flag encoding, and register mask helpers. Risks are brittle assumptions around new sample bits, endian flag constants, and read-format LOST handling. Passing signal is exact structural equality for every exercised sample layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c -->
