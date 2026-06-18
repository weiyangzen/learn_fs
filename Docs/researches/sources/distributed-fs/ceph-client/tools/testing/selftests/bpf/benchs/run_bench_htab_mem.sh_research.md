# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_htab_mem.sh

Purpose: runs hash-table memory-use benchmarks for selected use cases with preallocated and normal allocation modes.

Important APIs and functions: `htab_mem()` parses per-producer operations, average memory, and peak memory from a summary; `summarize_htab_mem()` formats one row; `htab_mem_bench()` runs `htab-mem --use-case` for `overwrite`, `batch_add_batch_del`, and `add_del_on_diff_cpu`.

Control flow: prints `preallocated`, runs all use cases with `--preallocated`, prints `normal bpf ma`, and reruns without the flag.

State and persistence: shell variables only. Memory behavior is measured by the child benchmark.

Dependencies and integration points: sources `run_common.sh`; uses sed regexes tied to `htab-mem` final summary text.

Risks: typo-like header `normal bpf ma` may be intentional but unclear; regexes require exact units and `±` text; fixed `-p8` may be inappropriate on small systems.

Test signals: rows report per-prod-op, average memory, and peak memory for each use case/allocation mode.
