<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py

## Purpose

This Python test runner validates perf event attributes emitted through `PERF_TEST_ATTR` against configparser-based expectation files.

## Research

`data_equal` supports exact, wildcard, and `|` alternatives. Exceptions `Fail`, `Notest`, and `Unsup` classify failures, skips, and unsupported perf exits. `Event` stores expected/result event terms and compares all configured perf_event_attr fields. `Test` loads a test file's `[config]`, arch/auxv/kernel gates, expected `[event*]` sections, optional base event inheritance, and then runs perf with `PERF_TEST_ATTR=<tempdir>`. It reloads generated `event*` files, resolves `group_fd` links by fd, and compares expected-to-result and result-to-expected, including group relationships. It can restore a too-low `perf_event_max_sample_rate`. `run_tests` iterates selected files; `main` handles options. State is temp directories containing perf-emitted attr files and optional sysctl sample-rate writes. Dependencies are configparser files under `shell/attr`, perf's `PERF_TEST_ATTR` instrumentation, auxv output, platform release, and root permission for sample-rate restoration. Risks include broad `except` handling, possible `sys.exit` without imported sys in `read_json`-like paths absent here, sysctl mutation, and strict term list needing updates for new attr fields. Passing signal is no unmatched expected/result events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py -->
