# sources/distributed-fs/ceph-client/arch/x86/include/asm/numa.h

## Purpose
Declares x86 NUMA CPU/node mapping state and lifecycle helpers.

## Important APIs, Types, And Functions
With `CONFIG_NUMA`, declares `numa_off`, `__apicid_to_node[]`, `numa_nodes_parsed`, `numa_phys_nodes_parsed`, `set_apicid_to_node()`, `numa_cpu_node()`, `numa_set_node()`, `numa_clear_node()`, `init_cpu_to_node()`, `numa_add_cpu()`, `numa_remove_cpu()`, `init_gi_nodes()`, and `num_phys_nodes()`. Non-NUMA builds provide stubs and return `NUMA_NO_NODE` or 1 physical node. Debug builds can call `debug_cpumask_set_cpu()`.

## Control Flow
Early topology code maps APIC IDs to nodes, initializes CPU-to-node maps, and updates mappings during CPU hotplug. Non-NUMA configs compile calls away.

## State And Persistence
State is boot-time and hotplug-updated NUMA topology in node masks and APIC-to-node arrays. It persists for the running kernel.

## Dependencies And Integration Points
Depends on node masks, topology, APIC definitions, and debug per-CPU maps. It integrates with memory policy, scheduler topology, CPU hotplug, ACPI/SRAT parsing, and platform-specific NUMA code.

## Risks And Edge Cases
APIC ID bounds and overrides are important, especially on 32-bit with APIC-specific `numa_cpu_node()` behavior. Wrong mappings hurt locality or break memory allocation assumptions.

## Test Signals
NUMA boot on multi-node systems, CPU hotplug, SRAT parsing tests, scheduler topology checks, and non-NUMA build coverage are useful.
