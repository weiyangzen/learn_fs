# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-functions.c

Purpose: implements perf bench memory benchmarks for `memcpy`, `memset`, and `mmap` demand/populate behavior.

Important APIs/types/functions: `bench_mem_memcpy()`, `bench_mem_memset()`, and `bench_mem_mmap()` are entry points. `bench_mem_common()` parses common options, validates sizes/page sizes, selects a function, and calls `__bench_mem_function()`. `do_memcpy()`, `do_memset()`, and `do_mmap()` perform timed operations. `bench_mmap()` maps 4KB/2MB/1GB pages with optional huge pages and populate. `init_cycles()`/`get_cycles()` optionally measure CPU cycles.

Control flow: common setup parses buffer size, chunk size, page size, loops, selected implementation, and cycle timing. Copy/set benchmarks allocate prefaulted mmap buffers, run nested loop over loops and chunks, then report bandwidth or cycles/byte. Mmap benchmark starts configurable threads, each repeatedly maps, touches pages either sequentially or random-offset, unmaps, and accumulates timing.

State and persistence: static option globals and a static stats object hold process state. Memory is anonymous mmap and freed after each function. Optional cycle counter fd is opened for the process. No files persist.

Dependencies and integration: depends on perf syscall wrapper for `perf_event_open`, perf size parser, stats, x86 asm implementation tables when enabled, pthreads, mmap/hugetlb flags, and bench output format.

Risks: uses `void *` pointer arithmetic as a compiler extension. Huge-page modes require kernel support and available huge pages. `print_bps()` has a formatting typo for KB (`%lfd`). Cycle measurement requires perf permissions. Multi-thread mmap results use shared global options and aggregate per-thread stats.

Test signals: `mem memcpy`, `mem memset`, and `mem mmap` with default/all/help functions, x86 asm functions, chunked operations, cycle mode, 4KB/2MB/1GB pages, random mmap touch, multiple threads, and allocation failure paths.
