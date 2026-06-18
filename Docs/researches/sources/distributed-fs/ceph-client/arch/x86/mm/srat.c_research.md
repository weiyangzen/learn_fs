# sources/distributed-fs/ceph-client/arch/x86/mm/srat.c

## Purpose
`srat.c` handles x86 ACPI SRAT CPU-affinity parsing for NUMA setup. It maps ACPI proximity domains to Linux NUMA nodes and associates LAPIC/x2APIC IDs with those nodes.

## Important APIs, Types, and Functions
The ACPI callbacks are `acpi_numa_x2apic_affinity_init()` and `acpi_numa_processor_affinity_init()`. `x86_acpi_numa_init()` calls generic `acpi_numa_init()` and returns failure if SRAT was disabled.

## Control Flow and State
Each affinity callback first exits if SRAT is disabled, validates record length, ignores disabled CPUs, extracts the proximity domain, maps it to a node through `acpi_map_pxm_to_node()`, validates APIC IDs, and records `set_apicid_to_node()`. The LAPIC path composes larger proximity domains for SRAT revision 2+ and handles UV x2APIC-style APIC IDs by combining APIC ID and SAPIC EID.

## State and Persistence
The file updates global APIC-ID-to-node mappings and marks `numa_nodes_parsed` and `numa_phys_nodes_parsed`. `bad_srat()` can disable or invalidate SRAT-derived NUMA setup.

## Dependencies and Integration Points
It depends on ACPI SRAT structures, generic ACPI NUMA parsing, x86 APIC ID validation, UV system-type detection, topology node masks, and early NUMA initialization.

## Risks and Test Signals
Risks include malformed SRAT lengths, proximity-domain overflow, too-large APIC IDs, UV APIC-ID interpretation mismatches, and assuming memory regions per proximity domain are contiguous enough for higher-level NUMA code. Test signals are boot logs mapping PXM to APIC/node, NUMA node CPU masks, SRAT disabled/fallback behavior, and validation on LAPIC, x2APIC, and UV systems.
