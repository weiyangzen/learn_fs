# sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_plat.h

## Purpose
Supplies ARM platform SMP helpers for MPIDR affinity decoding and logical/physical CPU mapping.

## Important APIs, Types, And Functions
Key declarations include static inline bool is_smp(void); extern unsigned int smp_on_up;; static inline unsigned int smp_cpuid_part(int cpu); struct cpuinfo_arm *cpu_info = &per_cpu(cpu_data, cpu);; static inline int tlb_ops_need_broadcast(void); static inline int cache_ops_need_broadcast(void). Important macros/constants include __ASMARM_SMP_PLAT_H, tlb_ops_need_broadcast(), cache_ops_need_broadcast(), cpu_logical_map(cpu). It depends directly on #include <linux/cpumask.h>, #include <linux/err.h>, #include <asm/cpu.h>, #include <asm/cputype.h>.

## Control Flow
SMP setup reads MPIDR values, converts cluster/CPU affinity into linear indexes, and stores mappings used by hotplug and power-management code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/cpumask.h>, #include <linux/err.h>, #include <asm/cpu.h>, #include <asm/cputype.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
