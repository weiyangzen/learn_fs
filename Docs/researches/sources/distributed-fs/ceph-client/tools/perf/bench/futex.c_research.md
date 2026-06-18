# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex.c

Purpose: shared futex benchmark helper for configuring and reporting the kernel futex hash bucket count.

Important APIs/types/functions: `futex_set_nbuckets_param()` writes requested bucket count to `/proc/sys/kernel/futex_hash_buckets` when `params->nbuckets > 0`. `futex_print_nbuckets()` reads and prints the current bucket count.

Control flow: both helpers early-return when no bucket override/reporting is requested. They use `sysctl__write_int()` and `sysctl__read_int()` and print warnings on failure.

State and persistence: unlike most bench files, this can persistently change the kernel sysctl futex hash bucket setting for the running system. It stores no internal state.

Dependencies and integration: depends on `bench_futex_parameters` from `futex.h`, sysctl helpers, and warning output. Used by futex hash/wake/requeue/PI benchmarks.

Risks: changing a global kernel sysctl affects the whole system and may require privileges. The helper does not restore the old value. Tests should isolate or avoid bucket writes unless intentional.

Test signals: run futex benchmarks with default `-1`, explicit valid bucket count, permission-denied sysctl, and readback reporting.
