## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_callgraph_fp.sh

Purpose: aarch64-specific check that frame-pointer callgraphs include expected `leaf`, `parent`, and `leafloop` frames.
Important behavior: skips non-aarch64, missing DWARF unwind support, or missing `leafloop` symbol; records `perf test -w leafloop` with `--call-graph fp -e cycles//u --user-callchains`.
Control flow: prints a short script sample for immediate diagnostics, then flattens script output and greps for the expected ordered frame sequence.
State and persistence: temp perf.data is removed by trap.
Dependencies and integration: relies on perf workload symbols and callchain unwinding.
Risks: unwind support is checked even though fp mode is used; symbol names and stack formatting are strict.
Test signals: regex match for `perf -> leaf -> parent -> leafloop`.
