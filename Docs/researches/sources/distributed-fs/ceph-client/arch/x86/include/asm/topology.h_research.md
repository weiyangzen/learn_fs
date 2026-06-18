# sources/distributed-fs/ceph-client/arch/x86/include/asm/topology.h

Purpose: x86 topology declarations for NUMA, SMT/core/package hierarchy, scheduler capacity, PCI root-bus locality, and hybrid CPU classification. It bridges generic Linux topology helpers with x86 CPU metadata in `cpu_data(cpu).topo`.

Important APIs/types/functions: `enum x86_topology_domains`, `enum x86_topology_cpu_type`, `struct x86_topology_system`, `x86_topo_system`, `topology_get_domain_size()`, `topology_get_domain_shift()`, `cpu_coregroup_mask()`, `cpu_clustergroup_mask()`, topology access macros for package/die/core IDs, `topology_get_logical_id()`, `topology_is_primary_thread()`, `topology_get_primary_thread()`, `topology_is_core_online()`, `x86_pci_root_bus_node()`, ITMT scheduler hooks, and frequency/capacity scaling hooks.

Control flow: the header is mostly inline dispatch and configuration gating. NUMA builds use early per-CPU CPU-to-node maps and node cpumasks; non-NUMA builds collapse everything to node 0. SMP builds expose sibling/core/cluster/die masks, SMT counts, and AMD node data; uniprocessor builds return conservative constants. Local APIC builds can map APIC topology IDs; otherwise logical IDs collapse to zero.

State/persistence: state is boot-discovered and held in extern globals/per-CPU maps: `x86_topo_system`, max package/die/thread counters, node cpumasks, `__cpu_primary_thread_mask`, ITMT priorities, and scheduler capacity/frequency values. The header does not persist data itself, but exposes long-lived topology state consumed by scheduler, NUMA, PCI, and CPU hotplug paths.

Dependencies/integration: depends on `linux/numa.h`, `linux/cpumask.h`, `asm/mpspec.h`, per-CPU support, APIC, scheduler MC priority, static keys, and generic topology. It integrates with sched domains, CPU capacity scaling, PCI resource discovery, and architecture-specific CPU enumeration.

Risks/test signals: wrong domain shifts or cpumasks can misplace scheduler domains, NUMA locality, PCI locality, and hybrid capacity decisions. Test via x86 boot on NUMA/non-NUMA, SMT on/off, CPU hotplug, hybrid Intel systems, AMD multi-node packages, `lscpu` topology checks, scheduler tracepoints, and PCI root-bus NUMA node validation.
