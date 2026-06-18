<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c

Purpose: Implements ACPI SRAT-based NUMA CPU-to-node discovery for RISC-V.

Important APIs/types/functions: Key functions are `acpi_map_cpus_to_nodes()`, `acpi_numa_rintc_affinity_init()`, `acpi_parse_rintc_pxm()`, and internal UID-to-CPU lookup.

Control flow: SRAT RINTC affinity entries map ACPI processor UIDs to logical CPUs using cached MADT RINTC data, translate proximity domains to nodes, record early CPU-node mapping, and mark parsed NUMA nodes.

State and persistence: Persistent boot-time state is `acpi_early_node_map[NR_CPUS]` and generic NUMA parsed-node masks.

Dependencies and integration points: Depends on ACPI SRAT/MADT, `acpi_get_cpu_uid()`, `cpuid_to_hartid_map()`, generic NUMA mapping, memblock, and topology.

Risks: UID mismatches or invalid proximity domains put CPUs on wrong NUMA nodes, hurting locality or causing boot warnings/bad SRAT handling.

Test signals: ACPI NUMA boots, malformed SRAT length tests, disabled SRAT, multiple proximity domains, CPU hotplug/topology sysfs, and memory locality benchmarks.

Source read size: 134 lines, 3322 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c -->
