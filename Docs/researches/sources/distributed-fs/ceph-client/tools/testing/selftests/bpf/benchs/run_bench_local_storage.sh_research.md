# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage.sh

Purpose: drives local-storage cache benchmarks and hashmap control across key/map-count sweeps.

Important APIs and functions: sources `run_common.sh`; calls `summarize_local_storage` around `./bench --nr_maps ...` local-storage benchmark names.

Control flow: first runs hashmap control with key counts from 10 to full `HASHMAP_SZ`; then runs local-storage sequential and interleaved get tests for map counts from 1 to 1000.

State and persistence: shell-only; each `./bench` invocation creates its own maps and BPF links.

Dependencies and integration points: assumes current directory contains `./bench`; unlike many scripts it bypasses `$RUN_BENCH`, so warmup/duration/affinity defaults differ.

Risks: full hashmap prepopulation with 4,194,304 keys is expensive; direct `./bench` calls may need root/capabilities depending on environment; parser depends on local-storage report text.

Test signals: output shows hits throughput, hits latency, and important-hit throughput for each configuration.
