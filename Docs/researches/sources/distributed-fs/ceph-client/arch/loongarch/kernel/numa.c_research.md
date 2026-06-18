## sources/distributed-fs/ceph-client/arch/loongarch/kernel/numa.c

### Purpose
`numa.c` manages early LoongArch CPU-to-node mapping, per-node CPU masks, per-CPU allocator placement, and ACPI/fake NUMA memory initialization. It bridges firmware topology and memblock memory ranges into Linux NUMA node state.

### Important APIs, Types, And Functions
Global state includes `numa_off`, `cpus_on_node`, `phys_cpus_on_node`, `__cpuid_to_node`, and optionally `__per_cpu_offset`. Important functions are `setup_per_cpu_areas`, `early_cpu_to_node`, `early_numa_add_cpu`, `numa_add_cpu`, `numa_remove_cpu`, `init_numa_memory`, and `pcibus_to_node`. ACPI NUMA support uses `numa_memblks_init`, `acpi_numa_init`, `memblock_validate_numa_coverage`, and `numa_add_memblk`.

### Control Flow
Early CPU discovery records physical CPU IDs into node masks. Per-CPU setup chooses embedded allocation for smaller node counts and page allocation otherwise, then computes each CPU's `__per_cpu_offset`. NUMA memory init clears CPU-node maps, parses SRAT/SLIT or fakes node 0, logs EFI memory by node, validates coverage, allocates node data, marks nodes online, updates PFN limits, and stores node/core counts in `loongson_sysconf`.

### State, Persistence, And Dependencies
CPU and memory node maps persist for scheduler, allocator, PCI locality, and hotplug. The code depends on EFI memory descriptors, ACPI NUMA parsing, memblock, Loongson CPU maps from SMP setup, and `nid_to_addrbase`/`pa_to_nid` platform address decoding.

### Integration Points
`setup_arch` calls `init_numa_memory` under `CONFIG_NUMA`; `smp_prepare_boot_cpu` and secondary CPU init call add/remove CPU helpers. The per-CPU allocator calls `pcpu_cpu_to_node` and `pcpu_populate_pte`. PCI code calls `pcibus_to_node`.

### Risks
Physical/logical CPU ID confusion is a main risk: `__cpuid_to_node` is indexed by physical ID, while `cpu_to_node` uses logical IDs later. Incomplete SRAT coverage returns `-EINVAL`. Fake NUMA assumes all memory is one node, which is safe only for non-ACPI systems. `cores_per_node` is derived from node 0 physical mask and may misrepresent asymmetric systems.

### Test Signals
Boot ACPI NUMA and non-ACPI systems, inspect `/sys/devices/system/node`, `/proc/zoneinfo`, CPU node masks, per-CPU allocation logs, and PCI locality. Test CPU hotplug and memory maps with holes or multiple address bases.
