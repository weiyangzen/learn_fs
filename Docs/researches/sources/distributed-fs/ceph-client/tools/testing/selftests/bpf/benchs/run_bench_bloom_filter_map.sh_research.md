# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bloom_filter_map.sh

Purpose: shell benchmark matrix for bloom filter map lookup/update/false-positive performance and hashmap-with-bloom versus hashmap-without-bloom throughput.

Important APIs and functions: sources `run_common.sh`, uses `header`, `subtitle`, `summarize`, `summarize_percentage`, and `summarize_total`. It invokes `$RUN_BENCH` with variable thread counts, hash function counts, entry counts, and value sizes.

Control flow: nested loops sweep value sizes, producer counts, hash function counts, and entry counts. For each point it runs bloom lookup, update, false-positive, and later hashmap comparison benchmarks.

State and persistence: no persistent state beyond shell variables and benchmark output. Kernel maps are created and destroyed by each `./bench` invocation.

Dependencies and integration points: assumes execution from selftests/bpf root with `./benchs/run_common.sh` available and `sudo ./bench -w3 -d10 -a` runnable.

Risks: very large sweep can take a long time; output parsing depends on stable summary text; `set -euo pipefail` makes any benchmark failure abort the whole matrix.

Test signals: formatted sections show per-entry throughput and false-positive percentages; missing parsed values indicate output format drift.
