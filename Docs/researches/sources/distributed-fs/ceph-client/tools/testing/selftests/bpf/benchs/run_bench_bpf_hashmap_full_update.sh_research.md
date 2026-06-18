# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_hashmap_full_update.sh

Purpose: runs the `bpf-hashmap-full-update` benchmark using all but one detected CPU as producer threads.

Important APIs and functions: sources `run_common.sh`, computes `nr_threads` from `/proc/cpuinfo`, invokes `$RUN_BENCH -p $nr_threads bpf-hashmap-full-update`, and prints the raw summary.

Control flow: one CPU-count calculation, one benchmark invocation, one print.

State and persistence: shell-only; benchmark state is contained in the child `bench` process.

Dependencies and integration points: relies on Linux `/proc/cpuinfo`, GNU `expr`, `grep`, `wc`, and common runner defaults from `run_common.sh`.

Risks: CPU count parsing is x86/procfs-string dependent; on single-CPU systems `nr_threads` becomes zero; output is not parsed/normalized like other scripts.

Test signals: non-empty benchmark summary from `bpf-hashmap-full-update`.
