# sources/distributed-fs/ceph-client/arch/arm/include/asm/topology.h

## Purpose
Provides ARM CPU topology hooks and default scheduling topology integration.

## Important APIs, Types, And Functions
Key declarations include static inline void init_cpu_topology(void) { }; static inline void store_cpu_topology(unsigned int cpuid) { }. Important macros/constants include _ASM_ARM_TOPOLOGY_H, arch_set_freq_scale, arch_scale_freq_capacity, arch_scale_freq_invariant, arch_scale_freq_ref, arch_scale_cpu_capacity, arch_update_cpu_topology, arch_scale_hw_pressure, arch_update_hw_pressure. It depends directly on #include <linux/cpumask.h>, #include <linux/arch_topology.h>, #include <asm-generic/topology.h>.

## Control Flow
SMP setup can populate topology from MPIDR or device tree so scheduler domains understand clusters/cores.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/cpumask.h>, #include <linux/arch_topology.h>, #include <asm-generic/topology.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
