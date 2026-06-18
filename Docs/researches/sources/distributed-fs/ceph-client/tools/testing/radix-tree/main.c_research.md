# sources/distributed-fs/ceph-client/tools/testing/radix-tree/main.c

## Purpose
`main.c` is the primary orchestrator for the user-space radix-tree/XArray test binary. It combines deterministic checks, randomized stress, regression tests, IDR/IDA tests, iteration race tests, and benchmarks.

## Important APIs, Types, And Functions
Important functions include `__gang_check()`, `gang_check()`, `__big_gang_check()`, `big_gang_check()`, `add_and_check()`, `dynamic_height_check()`, `check_copied_tags()`, `copy_tag_check()`, `single_thread_tests()`, and `main()`. It calls external suites: `xarray_tests()`, `regression*_test()`, `multiorder_checks()`, `tag_check()`, `idr_checks()`, `ida_tests()`, `iteration_test()`, `iteration_test2()`, and `benchmark()`.

## Control Flow
`main()` parses `-l` for long runs, `-s` for random seed, and `-v` for verbosity; initializes random state, RCU, and radix-tree infrastructure; runs external regression/iteration suites; then runs single-thread tests and benchmarks. Gang checks insert contiguous ranges around large indexes and verify lookup/gang scan behavior. `dynamic_height_check()` verifies radix-tree height grows and shrinks as expected. `copy_tag_check()` creates randomized tagged entries near range boundaries and verifies `tag_tagged_items()` copies tags only inside the requested range.

## State And Persistence
State is mostly local radix-tree roots and stack arrays. Global harness state includes `test_verbose`, allocation counters, preempt count, and RCU registration. The random seed can be fixed for reproducibility. No durable state is written.

## Dependencies And Integration Points
The file depends on the local test harness, Linux radix-tree APIs, regression headers, XArray/radix-tree/IDR/IDA test functions, pthread-backed RCU shims, and benchmark support. It is the `main` target in the radix-tree Makefile.

## Risks
Randomized tests can expose rare failures but require preserving seeds for reproduction. Long-run mode expands stress durations and loop counts substantially. The code relies on `assert()` and abort-style failure, so partial results are not summarized after a failure.

## Test Signals
Positive signals are the printed seed, "running tests", no assertion failures, `tests completed`, and clean RCU/allocation accounting after `rcu_barrier()`. Failures are typically assertion aborts, explicit `abort()`, allocation leaks, or hangs in threaded tests.
