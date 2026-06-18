# sources/distributed-fs/ceph-client/tools/testing/radix-tree/benchmark.c

## Purpose
`benchmark.c` measures insertion, tagging, iteration, and deletion costs for radix trees across multiple tree sizes and index steps.

## Important APIs, Types, And Functions
Important functions are `benchmark_iter()`, `benchmark_insert()`, `benchmark_tagging()`, `benchmark_delete()`, `benchmark_size()`, and public `benchmark()`. It uses radix-tree iteration macros, tag APIs, `item_insert()`, `item_delete()`, `item_kill_tree()`, `rcu_barrier()`, and `clock_gettime(CLOCK_MONOTONIC)`.

## Control Flow
`benchmark()` loops over sizes `1 << 10` and `1 << 20` and a range of sparse/dense step values. For each pair, `benchmark_size()` inserts items, tags them, measures tagged and untagged iteration, deletes items, and kills any remaining tree state. When compiled with `BENCHMARK`, `benchmark_iter()` repeats loops enough to get stable timing.

## State And Persistence
State is local to each `RADIX_TREE(tree, GFP_KERNEL)` instance. The volatile `sink` in `benchmark_iter()` prevents the compiler from discarding iteration work. No results are persisted outside printed output.

## Dependencies And Integration Points
This file depends on the local radix-tree user-space harness and is invoked at the end of `main.c` after functional tests. It uses `printv()` so output volume is controlled by verbosity.

## Risks
Timing is environment-sensitive and not a pass/fail signal. Without `BENCHMARK`, single-pass measurements for small trees can be noisy. The benchmark also depends on test item allocation behavior and RCU cleanup.

## Test Signals
The primary signal is performance output at verbosity level 2 and absence of leaks/assertion failures after cleanup. Functional regressions usually surface through allocation or deletion assertions in shared item helpers rather than timing values.
