# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_ringbufs.sh

Purpose: benchmark matrix for ringbuf/perfbuf libbpf and custom consumers under multiple producer/consumer patterns.

Important APIs and functions: sources `run_common.sh`, sets `RUN_RB_BENCH="$RUN_BENCH -c1"`, and uses `summarize` for `rb-libbpf`, `rb-custom`, `pb-libbpf`, and `pb-custom` across sampling, back-to-back, sample-rate sweeps, output API, CPU affinity, multi-producer, and overwrite producer-only cases.

Control flow: prints themed headers, loops benchmark names and counts, and runs a child benchmark per point.

State and persistence: shell-only. Each run creates its own BPF maps/buffers.

Dependencies and integration points: depends on common runner defaults, ringbuf benchmark argp options, CPU affinity flags, and summary text containing hits/drops.

Risks: high producer counts up to 52 may exceed available CPUs or distort comparisons; long matrix runtime; parser fragility; consumer count is fixed to one except overwrite producer-only section.

Test signals: hit/drop summaries across modes reveal notification overhead, contention, and overwrite behavior.
