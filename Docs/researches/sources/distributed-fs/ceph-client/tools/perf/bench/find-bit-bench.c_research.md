# Research: sources/distributed-fs/ceph-client/tools/perf/bench/find-bit-bench.c

Purpose: benchmarks bitmap set-bit iteration against direct `test_bit` probing for several bitmap sizes.

Important APIs/types/functions: `bench_mem_find_bit()` is the entry point. `do_for_each_set_bit()` allocates a bitmap, sets bits with varying sparsity, times `for_each_set_bit` and direct test-bit loops, and reports stats. `asm_test_bit()` uses x86 `bt` when available, otherwise falls back to `test_bit`. `workload()` prevents optimization of found values.

Control flow: parses outer/inner iteration counts, then for each bitmap size and sparsity pattern repeatedly times both approaches with `gettimeofday()`, updating stats and printing averages/stddevs.

State and persistence: static counters `accumulator` and `use_of_val` create observable side effects. Bitmaps are heap-allocated per test and freed. No persistence.

Dependencies and integration: depends on Linux bitmap/bitops helpers, perf stats, parse-options, bench format, and optional x86 inline asm.

Risks: microbenchmark results depend heavily on compiler optimization, CPU branch prediction, bit density, and timer granularity. The x86 asm path differs from generic `test_bit`, so cross-arch comparisons are not apples-to-apples.

Test signals: run with varied `-i/-j`, check bitmap sizes and sparse/dense cases, compare x86 and non-x86 builds, and ensure no optimizer removes workload side effects.
