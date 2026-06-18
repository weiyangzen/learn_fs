<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c` maps arm64 ACPI SRAT/GICC proximity data into NUMA node assignments for CPUs. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`; types: `acpi_srat_gicc_affinity`, `acpi_table_srat`; functions/prototypes/exports: `acpi_numa_get_nid`, `acpi_parse_gicc_pxm`, `acpi_map_cpus_to_nodes`, `acpi_numa_gicc_affinity_init`. The file is 109 lines / 2656 bytes. Direct includes are `linux/acpi.h`, `linux/bitmap.h`, `linux/kernel.h`, `linux/mm.h`, `linux/memblock.h`, `linux/mmzone.h`, `linux/module.h`, `linux/topology.h`, `asm/numa.h`.

### Control Flow
SRAT parsing records early CPU-to-node IDs, then `acpi_map_cpus_to_nodes` applies those IDs during NUMA setup; invalid proximity domains fall back to `NUMA_NO_NODE`.

### State, Persistence, And Dependencies
Notable global/static state symbols are `acpi_early_node_map`, `__init`, `cpu`, `pxm`. `acpi_early_node_map` is early boot state that seeds per-CPU NUMA topology. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Bad ACPI table validation or missing UID matches can place CPUs on wrong nodes, degrading scheduling and memory locality.

### Test Signals
Boot ACPI NUMA systems, inspect CPU node maps, run NUMA balancing tests, and validate SRAT parser error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c -->
