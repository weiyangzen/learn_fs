# sources/distributed-fs/ceph-client/arch/arm/include/asm/mcpm.h

## Purpose
Defines ARM multi-cluster power management (MCPM) limits, entry vectors, CPU/cluster power lifecycle APIs, platform callback registration, and the assembly-visible synchronization structure used to coordinate big.LITTLE style cluster shutdown and bring-up.

## Important APIs, Types, And Functions
Key declarations include extern void mcpm_entry_point(void);; void mcpm_set_entry_vector(unsigned cpu, unsigned cluster, void *ptr);; void mcpm_set_early_poke(unsigned cpu, unsigned cluster,; unsigned long poke_phys_addr, unsigned long poke_val);; int mcpm_cpu_power_up(unsigned int cpu, unsigned int cluster);; void mcpm_cpu_power_down(void);. Important macros/constants include MCPM_H, MAX_CPUS_PER_CLUSTER, MAX_NR_CLUSTERS, MAX_NR_CLUSTERS, __CACHE_WRITEBACK_GRANULE, CPU_DOWN, CPU_COMING_UP, CPU_UP, CPU_GOING_DOWN, CLUSTER_DOWN. It depends directly on #include <linux/types.h>, #include <asm/cacheflush.h>, #include <asm/asm-offsets.h>.

## Control Flow
Power control is driven by callers setting entry vectors and early pokes, requesting CPU power-up/down/suspend, and platform callbacks updating CPU, cluster, and inbound states under the MCPM lock. Assembly code consumes the sync structure offsets for cache-safe handoff.

## State And Persistence
State is held in the MCPM synchronization structure with per-CPU, per-cluster, and inbound flags aligned to cache writeback granules; platform code owns the real power-controller state.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>, #include <asm/cacheflush.h>, #include <asm/asm-offsets.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
