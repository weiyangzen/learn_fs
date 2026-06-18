# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/bench_page_pool_simple.c

Purpose: Kernel module benchmark for page-pool allocation and recycling paths, with baseline loop/atomic/spinlock measurements.

Important APIs/types/functions: Uses `page_pool_create()`, `page_pool_alloc_pages()`, `page_pool_recycle_direct()`, `page_pool_put_page()`, `page_pool_destroy()`, `in_serving_softirq()`, module params `run_flags` and `loops`, and timing helpers from `time_bench.h`. Benchmark functions include `time_bench_for_loop()`, `time_bench_atomic_inc()`, `time_bench_lock()`, `pp_fill_ptr_ring()`, `time_bench_page_pool()`, and wrappers for fast path, ptr_ring path, and page allocator slow path.

Control flow: On module init, the module validates `loops <= U32_MAX`, then `run_benchmark_tests()` conditionally runs baseline and page-pool benchmarks. `time_bench_page_pool()` creates a page pool, pre-fills its ptr_ring, times repeated allocation plus one of three return paths, destroys the pool, and logs per-element results.

State and persistence behavior: State is transient kernel module state, module parameters, allocated pages, a page_pool, and kernel log output. The module unload path only logs unload; benchmarks run at load time.

Dependencies and integration points: Requires kernel page_pool internals/helpers, module loading, and `time_bench.*`. The shell runner parses dmesg lines emitted by `time_bench_loop()`.

Risks: `page_pool_destroy(pp)` is called even after `page_pool_create()` returns an error pointer, which is risky if creation fails. Benchmarks are context-sensitive: comments note no-softirq context cannot activate the true fast path. Loop count can make module load slow.

Test signals: Dmesg lines named `for_loop`, `atomic_inc`, `lock`, `no-softirq-page_pool01`, `02`, and `03` with cycles/ns per element indicate benchmark execution.
