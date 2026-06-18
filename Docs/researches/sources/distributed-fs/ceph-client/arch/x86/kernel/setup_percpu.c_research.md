# sources/distributed-fs/ceph-client/arch/x86/kernel/setup_percpu.c

## Purpose
`setup_percpu.c` initializes x86 per-CPU storage during early boot. It exports `cpu_number`, `this_cpu_off`, and `__per_cpu_offset`, chooses the first-chunk allocator strategy, wires early CPU-to-node/APIC maps into allocated per-CPU areas, and makes the per-CPU base usable by CPU0 and AP startup code.

## Important APIs, Types, And Functions
`setup_per_cpu_areas()` is the main boot entry. `pcpu_populate_pte()` calls `populate_extra_pte()`. `pcpu_cpu_distance()` and `pcpu_cpu_to_node()` are callbacks for generic percpu allocation. On 32-bit, `pcpu_need_numa()` may force page chunks and `setup_percpu_segment()` installs `GDT_ENTRY_PERCPU`.

## Control Flow
The file logs topology sizes, tries embedded first-chunk allocation with architecture-specific atom size, falls back to page chunks, and panics if both fail. It computes the delta from `__per_cpu_start` to `pcpu_base_addr`, fills each possible CPU's per-CPU offset and identity variables, copies early APIC/ACPI/NUMA maps, switches CPU0 to the real per-CPU base, clears early arrays, builds node/cpu masks, and syncs initial page tables for SMP boot assembly.

## State, Persistence, Dependencies, Integration
Persistent state is the final per-CPU offset table, exported per-CPU variables, CPU-to-APIC/ACPI/node maps, and 32-bit GDT descriptors. Dependencies include memblock-era percpu allocation, early topology data, GDT helpers, NUMA/APIC setup, and page-table synchronization. It feeds `smpboot.c` topology setup through `setup_cpu_local_masks()` and `setup_node_to_cpumask_map()`.

## Risks And Test Signals
Wrong offsets corrupt all per-CPU access. NUMA allocator choice is boot-critical on 32-bit. Early maps must be cleared only after their contents are copied. Test with 32/64-bit, NUMA/non-NUMA, large CPU counts, APIC variants, kdump boots, CPU hotplug, and validation of APIC IDs, NUMA nodes, and per-CPU variables.
