<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h

## Purpose

`linux/percpu.h` maps kernel per-CPU APIs onto single-process userspace variables for tests.

## Important APIs, Types, and Functions

It defines `DECLARE_PER_CPU`, `DEFINE_PER_CPU`, `__get_cpu_var`, `this_cpu_ptr`, `this_cpu_read`, `this_cpu_xchg`, `this_cpu_cmpxchg`, `per_cpu_ptr`, and `per_cpu`. Atomic exchange and compare-exchange use `uatomic_xchg` and `uatomic_cmpxchg`.

## Control Flow and State

All per-CPU variables collapse to one ordinary variable instance; the CPU argument is ignored in `per_cpu_ptr()`.

## Dependencies and Integration Points

It depends on Userspace RCU atomics and is consumed by imported kernel data-structure code that has per-CPU counters or caches.

## Risks and Test Signals

Risks include hiding real per-CPU concurrency and CPU-indexing bugs. For unit tests focused on algorithms, successful compilation and deterministic single-instance behavior are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h -->
