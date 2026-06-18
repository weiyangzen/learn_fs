## sources/distributed-fs/ceph-client/tools/perf/tests/shell/top.sh

Purpose: tests noninteractive `perf top --stdio` against a spinning workload.
Important function: `test_basic_perf_top`.
Control flow: starts `perf test -w thloop 20`, runs `timeout 5s perf top --stdio -d 1 -e cpu-clock -p PID` with stdin held open by `sleep`, kills the workload, then greps output for percentages and `test_loop`.
State and persistence: temp log file and background workload PID are cleaned.
Dependencies and integration: `timeout`, `perf top`, cpu-clock sampling, `thloop` symbol.
Risks: sample availability can be timing-sensitive; timeout exit `124` is accepted as expected.
Test signals: log includes percentage rows and the `test_loop` symbol.
