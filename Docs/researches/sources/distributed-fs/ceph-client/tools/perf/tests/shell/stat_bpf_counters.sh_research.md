## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters.sh

Purpose: verifies `perf stat --bpf-counters` and `/b` event modifier produce counts comparable to regular counting.
Important functions: `compare_number`, `check_counts`, `test_bpf_counters`, and `test_bpf_modifier`.
Control flow: skips if `--bpf-counters` cannot count instructions, then counts `instructions` for `perf test -w sqrtloop` normally and with BPF, requiring the BPF count to be within +/-20%. It repeats the comparison using named base and bpf events in one stat command.
State and persistence: no files.
Dependencies and integration: requires BPF counters support, instructions event, and `sqrtloop`.
Risks: workload noise beyond 20% fails; not-counted base events skip, but not-counted BPF events fail.
Test signals: comparable instruction totals and successful named modifier output.
