## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_lbr.sh

Purpose: x86 Last Branch Record validation for callgraph and branch-stack capture, both sequential and parallel.
Important functions: `ParanoidAndNotRoot`, `lbr_callgraph_test`, `lbr_test`, and `parallel_lbr_test`.
Control flow: skips when CPU PMU branch caps are absent, runs `perf record` with LBR callgraph and branch filters, checks report decoding, verifies every sample has a branch stack, and measures empty stack ratio under threshold. Parallel subtests run several filters simultaneously.
State and persistence: temp perf.data/text files per parent or child process; no persistent state.
Dependencies and integration: requires x86 LBR-capable PMU, `perf test -w thloop`, cycles event, and permissions for system-wide modes.
Risks: parallel tests use relaxed 100% thresholds for some filters to avoid hardware contention false failures; permission gates skip system-wide checks.
Test signals: report success with `--stitch-lbr`, nonzero sample count, branch stack count equal to sample count, and acceptable empty-stack ratio.
