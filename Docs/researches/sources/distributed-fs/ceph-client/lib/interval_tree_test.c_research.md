# sources/distributed-fs/ceph-client/lib/interval_tree_test.c

## Purpose
`interval_tree_test.c` is a loadable kernel test/benchmark module for the interval tree implementation. It measures insert/remove and search costs, validates intersection iteration against brute-force bitmaps, and validates span iteration against Maple Tree behavior when enabled.

## Important APIs, Types, and Functions
Module parameters control workload size and randomness: `nnodes`, `perf_loops`, `nsearches`, `search_loops`, `search_all`, `max_endpoint`, and `seed`. Static state includes a cached root, allocated node array, query array, and `rnd_state`. Test routines are `init()`, `basic_check()`, `search_check()`, `intersection_range_check()`, `span_iteration_check()`, and module `interval_tree_test_init()`/`interval_tree_test_exit()`. Under span-iterator config, `mas_cur_span()` derives comparable spans from a Maple Tree.

## Control Flow, State, and Persistence
Module init allocates nodes and queries, seeds the PRNG, then runs the benchmark and validation routines. `init()` fills random intervals and query points. `basic_check()` repeatedly inserts and removes all nodes while timing cycles. `search_check()` inserts once, repeatedly counts query intersections, times the work, then removes nodes. `intersection_range_check()` repeatedly rebuilds the tree, computes brute-force intersecting node bitmaps for random ranges, compares them to interval-tree iteration results, and removes nodes. Span testing builds a Maple Tree from the same ranges and compares each interval-tree span's hole/used boundaries to Maple Tree traversal. The module returns `-EAGAIN` intentionally so it unloads after running.

## Dependencies and Integration Points
It depends on module parameters, interval tree APIs, pseudo-random state, slab allocation, cycle counters, bitmaps, and Maple Tree under span testing. It is an in-kernel validation and performance signal for `interval_tree.c`.

## Risks and Test Signals
Risks include random generation using modulo `b` and `% max_endpoint`, which requires nonzero effective endpoints, WARN-only failure reporting, benchmark noise from `get_cycles()`, and limited coverage based on random seeds. Useful signals are absence of WARNs, cycle logs for insert/remove and search, successful brute-force bitmap comparisons, successful Maple Tree span comparisons, and running multiple seeds plus edge parameter values such as small node counts, single-point ranges, and broad `search_all` queries.
