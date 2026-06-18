# sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h` Connects arm64 CPU topology, NUMA PCI locality, scheduler frequency invariance, CPU capacity, and hardware pressure hooks to generic topology code. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
pcibus_to_node(), cpumask_of_pcibus(), update_freq_counters_refs(), arch_scale_freq_tick, arch_set_freq_scale, arch_scale_freq_capacity, arch_scale_freq_invariant, arch_scale_freq_ref, arch_scale_cpu_capacity, arch_update_cpu_topology, arch_scale/update_hw_pressure, arch_cpu_is_threaded(). The file is 44 lines / 1354 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Scheduler calls the mapped topology_* functions for frequency/capacity/hardware pressure accounting; NUMA builds map PCI buses to node cpumasks; arch_cpu_is_threaded checks MPIDR_MT_BITMASK.

### State, Persistence, And Dependencies
Persistent state is generic arch_topology data and NUMA node maps, not this header. Depends on cpumask, numa, arch_topology, read_cpuid_mpidr; integrates scheduler load balancing, EAS, cpufreq/AMU counters, NUMA, PCI locality, and generic topology.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect capacity/frequency hooks skew scheduling and performance; wrong threaded detection affects SMT/core scheduling policy.

### Test Signals
Run scheduler topology tests, cpufreq/AMU frequency invariance validation, NUMA PCI locality tests, and topology sysfs inspection.
