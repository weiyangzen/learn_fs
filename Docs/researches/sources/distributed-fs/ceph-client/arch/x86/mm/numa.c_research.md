# sources/distributed-fs/ceph-client/arch/x86/mm/numa.c

## Purpose
This file contains common 32/64-bit x86 NUMA initialization and CPU-to-node mapping. It parses NUMA command-line options, initializes node memory blocks from ACPI/AMD/OF or a dummy fallback, registers nodes, and maintains CPU masks.

## Important APIs, Types, and Functions
- `numa_setup()` handles `numa=off`, `numa=fake=`, `numa=noacpi`, and `numa=nohmat`.
- `x86_numa_init()` tries ACPI, AMD, OF, then dummy NUMA initialization.
- `numa_set_node()`, `numa_clear_node()`, `early_cpu_to_node()`, and `__cpu_to_node()` maintain CPU-node mappings.
- `setup_node_to_cpumask_map()`, `numa_add_cpu()`, `numa_remove_cpu()`, and `cpumask_of_node()` maintain node CPU masks.
- `init_gi_nodes()` onlines Generic Initiator-only nodes; `init_cpu_to_node()` seeds early CPU mappings.
- NUMA emulation helpers update APIC-to-node mapping and DMA boundary behavior.

## Control Flow and State
Early parameter parsing can disable NUMA, request emulation, or disable ACPI/HMAT paths. Initialization clears APIC mappings, lets `numa_memblks_init()` parse memory blocks, registers nodes with valid PFN ranges, clears CPU mappings to offline nodes, and round-robins unknown CPUs across online nodes. Dummy mode creates node 0 covering all memory and cannot fail. CPU-node state starts in early percpu storage and later moves to normal percpu data; node masks are bootmem-allocated after possible node IDs are known.

## Dependencies and Integration Points
The file depends on ACPI SRAT/HMAT, AMD northbridge NUMA, OF NUMA, memblock NUMA metadata, topology/percpu APIs, APIC ID mapping, node registration, and NUMA emulation. `init_64.c` calls `x86_numa_init()` through `initmem_init()` when NUMA is configured.

## Risks
Missing or inconsistent firmware tables can leave CPUs mapped to offline nodes; the code clears or fakes mappings to avoid that. `cpumask_of_node()` is invalid before `setup_node_to_cpumask_map()`. Generic Initiator-only nodes need special early online handling before node subsystem registration. NUMA emulation must remap physical node IDs consistently.

## Test Signals
Boot logs show NUMA disabled/fallback/faked nodes and memblock dumps. Tests should cover ACPI NUMA, AMD NUMA, OF fallback, `numa=off`, `numa=fake=`, memoryless CPU nodes, Generic Initiators, CPU hotplug mask updates, and `CONFIG_DEBUG_PER_CPU_MAPS` warnings.
