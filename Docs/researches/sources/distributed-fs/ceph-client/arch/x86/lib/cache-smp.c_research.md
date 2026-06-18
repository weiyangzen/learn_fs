# sources/distributed-fs/ceph-client/arch/x86/lib/cache-smp.c

Purpose: provides SMP helpers to execute cache writeback/invalidate operations on one CPU, all CPUs, or a CPU mask.

Important APIs/functions: exports `wbinvd_on_cpu`, `wbinvd_on_all_cpus`, `wbinvd_on_cpus_mask`, `wbnoinvd_on_all_cpus`, and `wbnoinvd_on_cpus_mask`. Internal callbacks `__wbinvd` and `__wbnoinvd` invoke the CPU instructions.

Control flow: wrappers call `smp_call_function_single`, `on_each_cpu`, or `on_each_cpu_mask` with wait enabled. The callback runs synchronously on target CPUs and executes the selected instruction.

State and persistence behavior: no C-level state. Hardware cache state is written back and optionally invalidated globally or on targeted CPUs, which affects memory visibility and device/virtualization correctness.

Dependencies/integration points: built under `CONFIG_SMP`. Includes Linux SMP/export infrastructure and KVM export typing. KVM and memory-management code use these helpers for cache coherency operations that must happen on specific CPUs.

Risks: these operations are expensive and globally disruptive. Incorrect CPU masks or missing synchronization can leave stale cache state. `wbinvd` has stronger side effects than `wbnoinvd`, so call sites must select carefully.

Test signals: SMP build tests, KVM module link tests for exported symbols, CPU hotplug stress around target masks, and platform tests involving cache-flush-sensitive device assignment or memory type changes.
