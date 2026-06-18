<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c

## Purpose

This workload spawns multiple threads that repeatedly copy memory, creating sustained user-space instruction and memory activity for CoreSight tracing.

## Research

`struct args` holds loop count, copy size in KiB, thread id, and return pointer. `thrfn` allocates source and destination buffers of `size * 1024`, exits on allocation failure, and calls `memcpy` for `loops` iterations. `new_thr` initializes pthread attributes and starts a thread. `main` validates three arguments: copy size 1 KiB to 1 GiB, threads 1 to 256, and loop count in hundreds up to 40,000,000,000; it multiplies loop count by 100, starts all threads, and joins them. State is per-thread heap buffers that are not freed before process exit and thread metadata in a fixed 256-entry array. Dependencies are pthreads, libc allocation, and memory bandwidth. Risks include very large memory allocation, uninitialized source contents being acceptable because data value is irrelevant, and long runtimes for high loop counts. Test signal is process completion with enough trace packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c -->
