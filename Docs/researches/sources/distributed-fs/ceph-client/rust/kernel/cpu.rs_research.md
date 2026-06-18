<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpu.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpu.rs

## Purpose
This file provides basic Rust CPU identifier wrappers and access to CPU devices.

## Important APIs, Types, and Functions
`nr_cpu_ids()` returns the configured maximum possible CPU count, using either `bindings::NR_CPUS` or the runtime `bindings::nr_cpu_ids` global depending on config. `CpuId(u32)` enforces IDs in `[0, nr_cpu_ids())` through checked `from_i32`/`from_u32` and unsafe unchecked constructors. It exposes `as_u32`, `current`, and conversions into `u32`/`i32`. Unsafe `from_cpu` returns the `Device` for a CPU.

## Control Flow and State
Checked constructors reject negative or too-large IDs. Unchecked constructors debug-assert validity and rely on caller safety. `CpuId::current` calls `raw_smp_processor_id` and wraps it unchecked. `from_cpu` calls `get_cpu_device`, returns `ENODEV` on null, and casts the C device pointer into a Rust `Device`.

## State and Persistence Behavior
`CpuId` is a copyable validated value. `from_cpu` returns a `'static` device reference because C does not free CPU device memory on hot-unplug, but the docs warn that unregister can make use invalid from a logical lifetime perspective.

## Dependencies and Integration Points
The file depends on CPU bindings, `device::Device`, kernel `Result`, and `ENODEV`. It is used by cpufreq and cpumask abstractions.

## Risks
`CpuId::current` can become stale under preemption or migration. `from_cpu` is unsafe because CPU hotplug can unregister the device while memory remains allocated; callers need hotplug notification or another lifetime discipline. Unchecked constructors must not be used with arbitrary C integers.

## Test Signals
No local tests. Doc examples cover checked and unchecked construction. Runtime validation should include boundary IDs and CPU hotplug-aware device use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpu.rs -->
