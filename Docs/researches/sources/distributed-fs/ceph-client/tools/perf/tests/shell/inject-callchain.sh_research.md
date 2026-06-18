<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh

## Purpose

This shell test verifies `perf inject --convert-callchain` can convert DWARF callchains to regular callchains without changing report output except for inlined-function differences.

## Research

The script skips if DWARF support is unavailable. It records `perf test -w noploop` with high frequency and DWARF call graph, runs `perf inject -i "$TESTDATA" --convert-callchain -o "$TESTDATA.new"`, produces quiet no-children reports for both original and converted data, then diffs them. Differences beginning with removed lines are allowed only when they mention `(inlined)`; any other removed difference fails. State is a temporary perf.data pair and report outputs. Dependencies are DWARF unwind support, perf inject, report stability, and sufficient samples. Risks include legitimate formatting differences beyond inlining, sampling nondeterminism between report generation not recording, and DWARF collection permissions. Passing signal is no non-inlined report differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh -->
