# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/page_frag_test.c

## Purpose

`page_frag_test.c` is a loadable kernel test module for the page fragment cache. It stress-tests fragment allocation and freeing between producer and consumer kthreads, optionally validating cacheline alignment from `page_frag_alloc_align()`.

## Important APIs, Types, and Functions

The module uses `struct page_frag_cache`, `page_frag_cache_init()`, `page_frag_alloc()`, `page_frag_alloc_align()`, `page_frag_free()`, `page_frag_cache_drain()`, `struct ptr_ring`, `ptr_ring_init()`, `__ptr_ring_produce()`, `__ptr_ring_consume()`, kthreads, completions, atomics, CPU placement, and module parameters. Thread functions are `page_frag_push_thread()` and `page_frag_pop_thread()`. Entry and exit points are `page_frag_test_init()` and `page_frag_test_exit()`.

## Control Flow

On module load, parameters are validated, the fragment cache and pointer ring are initialized, producer and consumer kthreads are created on selected CPUs, and both are started. The producer allocates fragments until `nr_test` pushes succeed or `force_exit` is set; if `test_align` is enabled it checks returned addresses against `SMP_CACHE_BYTES`. The consumer removes objects from the ring and frees them until `nr_test` pops complete. The init function waits in 10-second intervals, detecting lack of progress and forcing exit. It logs duration on success, cleans the ring and fragment cache, and returns `-EAGAIN` so insertion completes the test but does not leave the module loaded.

## State and Persistence Behavior

Global module state includes the ring, fragment cache, counters, completion, force-exit flag, and module parameters (`nr_test`, `test_align`, `test_alloc_len`, `test_push_cpu`, `test_pop_cpu`). Fragments are allocated from kernel memory and freed by the consumer or immediately on ring-full producer failure. The cache is drained before exit.

## Dependencies and Integration Points

It depends on kernel module loading, active selected CPUs, `page_frag_cache` APIs, ptr_ring, scheduler/kthread support, and kbuild output from the page_frag Makefile. It integrates with mm/network-style page fragment allocation code paths.

## Risks and Edge Cases

Counters are plain `int` shared between kthreads, so this is a stress test rather than a strict data-race-free accounting example. Invalid CPU or allocation length parameters fail load with `-EINVAL`. If producer or consumer stalls, the wait loop sets `force_exit` and emits a warning. Returning `-EAGAIN` is intentional but may look like module insertion failure to generic tooling.

## Test Signals

Kernel log output is the primary signal: progress lines, duration on success, and warnings with `page_frag_test failed:` on alignment or progress failures. Successful completion drains resources and returns `-EAGAIN`.
