<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh

## Purpose

This shell helper lets tests skip when the perf test binary lacks a required symbol.

## Research

`perf_has_symbol` runs `perf test -vv -F "Symbols"` and greps for the requested symbol at end of line, printing whether it exists. `skip_test_missing_symbol` calls it and exits 2 on absence. State is none beyond stdout. Dependencies are perf's Symbols selftest output format and grep character classes. Integration is used by annotate and diff tests before recording workloads that rely on named symbols like `noploop` or `test_loop`. Risks include output format changes, demangled/qualified symbol names not matching the simple end-of-line regex, and a missing symbol causing skip rather than fail even when the workload should be present. Test signal is function return 0 for found symbols or process exit 2 for skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh -->
