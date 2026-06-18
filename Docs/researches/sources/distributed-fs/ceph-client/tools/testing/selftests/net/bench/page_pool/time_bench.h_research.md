# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.h

Purpose: Header API for in-kernel benchmark timing records, CPU concurrency records, and low-level timestamp helpers.

Important APIs/types/functions: Defines `struct time_bench_record`, measurement flags (`TIME_BENCH_LOOP`, `TIME_BENCH_TSC`, `TIME_BENCH_WALLCLOCK`, `TIME_BENCH_PMU`), `struct time_bench_sync`, `struct time_bench_cpu`, TSC helpers `tsc_start_clock()` and `tsc_stop_clock()`, PMU helpers (`p_rdpmc()`, `pmc_inst()`, `pmc_clk()`), prototypes for the C implementation, and inline `time_bench_start()` / `time_bench_stop()`.

Control flow: Benchmark callbacks call `time_bench_start()` before their measured loop and `time_bench_stop()` afterward with the invocation count. The inline helpers record wall-clock time, optional PMU counters, and serialized TSC values.

State and persistence behavior: No global state except constants and inline code. Records are caller-owned and later consumed by `time_bench_calc_stats()`.

Dependencies and integration points: Used by `bench_page_pool_simple.c` and implemented by `time_bench.c`. Depends on kernel `BIT`, atomics, completions, task structs, x86 asm instructions (`CPUID`, `RDTSC`, `RDTSCP`, `RDPMC`), and timekeeping APIs.

Risks: The TSC/PMU inline asm is not portable to all architectures and comments acknowledge guest/CPU flag constraints. PMU helpers require counters to be configured externally or by incomplete code. Some comments use outdated timekeeping API references.

Test signals: Correct integration yields populated records with TSC cycles, wall-clock intervals, and optional PMU counters printed by the implementation.
