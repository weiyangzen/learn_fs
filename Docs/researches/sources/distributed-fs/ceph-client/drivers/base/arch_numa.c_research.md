# sources/distributed-fs/ceph-client/drivers/base/arch_numa.c

## Purpose
Provides generic architecture NUMA initialization support used by architectures such as arm64 and RISC-V. It parses early NUMA controls, builds CPU-to-node and node-to-cpumask mappings, initializes node data from firmware or fallback memory ranges, and optionally supports NUMA emulation.

## Important APIs, Types, And Functions
- Global/exported state: `numa_off`, `node_to_cpumask_map`, and optionally `__per_cpu_offset`.
- CPU/node helpers: `early_map_cpu_to_node()`, `numa_store_cpu_info()`, `numa_add_cpu()`, `numa_remove_cpu()`, and `numa_clear_node()`.
- Initialization: `arch_numa_init()`, `numa_init()`, `numa_register_nodes()`, `dummy_numa_init()`, and ACPI/OF init hooks.
- Per-CPU setup under `CONFIG_HAVE_SETUP_PER_CPU_AREA`: `setup_per_cpu_areas()`.

## Control Flow
The early `numa=` parameter can disable NUMA or request fake NUMA. `arch_numa_init()` tries ACPI NUMA when ACPI is enabled, OF NUMA when ACPI is disabled, and finally a dummy single-node setup. Successful initialization validates memblock coverage, registers parsed nodes, sets possible/online maps, and allocates node cpumasks.

## State And Persistence
Persistent boot state includes `cpu_to_node_map`, node masks, node data (`NODE_DATA`), node online/possible maps, node distance data, and per-CPU offsets if this file owns percpu setup. CPU hotplug updates node cpumasks through add/remove helpers.

## Dependencies And Integration Points
Depends on ACPI NUMA, OF NUMA, memblock, `numa_memblks`, node data allocation, CPU masks, early params, and architecture sections/percpu support. Scheduler and topology code consume CPU-node mappings.

## Risks And Edge Cases
Invalid CPU/node IDs or `numa_off` force node 0. Firmware parse failures fall back to dummy NUMA. `cpumask_of_node()` has debug-only validation but non-debug callers must rely on setup order. Memory-less nodes are allowed but must still receive `NODE_DATA`.

## Test Signals
Boot with `numa=off`, fake NUMA, ACPI SRAT, OF NUMA, no firmware NUMA, memory-less nodes, CPU hotplug add/remove, percpu allocator fallback, and memblock coverage validation failures.
