# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_loop.sh

Purpose: sweeps BPF loop helper throughput over multiple producer counts and loop iteration counts.

Important APIs and functions: sources `run_common.sh`, uses `subtitle` and `summarize_ops`, invokes `$RUN_BENCH -p $t --nr_loops $i bpf-loop`.

Control flow: nested loops over thread counts and `nr_loops` values, printing a subtitle and parsed throughput/latency for each run.

State and persistence: shell-local only; each benchmark child owns its BPF state.

Dependencies and integration points: depends on common summary regexes in `run_common.sh` matching `throughput` and `latency` text.

Risks: large iteration values can make individual runs long; parser fragility if `bpf-loop` report format changes; any run failure stops the script.

Test signals: each matrix point emits throughput and latency, enabling trend comparison by loop count and producer count.
