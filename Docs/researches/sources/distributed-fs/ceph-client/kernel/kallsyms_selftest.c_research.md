# sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.c

## Purpose
Implements boot-time functional and performance tests for kallsyms lookup and traversal. It validates exact lookup of known function/data symbols, duplicate-name traversal, address-to-name consistency, compression ratio, and relative performance of lookup APIs.

## Important APIs, Types, and Functions
Defines test symbols and variables (`kallsyms_test_func*`, `kallsyms_test_var*`) and uses `struct test_stat` plus `struct test_item`. Main routines are `test_kallsyms_basic_function`, `test_kallsyms_compression_ratio`, `test_perf_kallsyms_lookup_name`, `test_perf_kallsyms_on_each_symbol`, `test_perf_kallsyms_on_each_match_symbol`, and `kallsyms_test_init`.

## Control Flow
`late_initcall(kallsyms_test_init)` starts a CPU-pinned kthread. The thread waits until `SYSTEM_RUNNING`, runs correctness tests first, aborts on failure, then prints compression/performance statistics. Correctness tests compare direct lookup results for fixed symbols, scan all symbols, randomly sample full traversal, and verify `kallsyms_on_each_match_symbol` matches `kallsyms_on_each_symbol`.

## State and Persistence
Temporary state is allocated with `kmalloc_objs`, and fixed test symbols are linked into the kernel image. Results are emitted to the kernel log; no persistent state is stored.

## Dependencies and Integration Points
Depends on `kallsyms.c` public APIs, generated kallsyms internals, random bytes, scheduler clock, kthreads, and exported test declarations in `kallsyms_selftest.h`.

## Risks
Tests are timing-sensitive for performance output but correctness failures should be deterministic. Random sampling reduces cost but may not cover every full traversal path every boot. Data-symbol checks only run with `CONFIG_KALLSYMS_ALL`.

## Test Signals
Kernel log lines include `start`, `abort`, compression table output, per-symbol timing, traversal timing, and `finish`. Failures log symbol name, expected address, observed address/count, or traversal mismatch.
