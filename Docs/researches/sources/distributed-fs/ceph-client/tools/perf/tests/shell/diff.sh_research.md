<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh

## Purpose

This shell test validates `perf diff` output for two and three recorded profiles of the same workload.

## Research

The script sources `lib/perf_has_symbol.sh`, requires the `test_loop` symbol in perf's test binary, and uses `perf test -w thloop` as workload. `make_data` records to a supplied temp file and confirms `perf report -q` contains `test_loop`. `test_two_files` creates two profiles and requires `perf diff file1 file2` to show the symbol. `test_three_files` repeats with three profiles. State is three temporary perf.data files and `.old` cleanup. Dependencies are symbol availability, perf record/report/diff, and enough samples in `thloop`. Integration checks diff command-line handling for multiple input files rather than numeric diff correctness. Risks include sampling flakiness, missing symbols, and reuse of global `err` as both function status and test status. Passing signal is symbol presence in diff output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh -->
