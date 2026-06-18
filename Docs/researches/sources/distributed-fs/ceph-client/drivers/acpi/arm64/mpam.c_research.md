# sources/distributed-fs/ceph-client/drivers/acpi/arm64/mpam.c

## Purpose
Parses the Arm MPAM ACPI table and creates `mpam_msc` platform devices for memory system components.

## Important APIs, Types, And Functions
Exports `acpi_mpam_parse_resources()` and `acpi_mpam_count_msc()`. Internal helpers handle IRQ registration, resource-node parsing, power-management links, interface decoding, MSC platform-device creation, and table parsing.

## Control Flow
`acpi_mpam_parse()` runs at `subsys_initcall_sync`, checks ACPI and MPAM CPU support, obtains the MPAM table, validates revision and MSC bounds, skips reserved or disabled MSCs, then creates platform devices. Each MSC may get MMIO resources or PCC channel properties, overflow/error IRQ resources, not-ready timing property, CPU affinity property derived from linked processor/container devices, software node properties, and a copy of the MSC table entry as platform data. Later, the MPAM driver calls `acpi_mpam_parse_resources()` to create RIS objects from resource nodes.

## State And Persistence
State is represented by created platform devices, software node properties, ACPI companions, device links, and platform data copies. The parser itself has no global mutable state.

## Dependencies And Integration Points
Integrates ACPI MPAM table structures, ARM MPAM core, GSI registration, ACPI processor/cache helpers, NUMA proximity mapping, PCC/MMIO interfaces, software nodes, and platform devices.

## Risks
Reserved MSC fields make MPAM globally unsafe and are skipped while still counted. Partitioned PPIs are unsupported. Resource-node bounds and functional dependency counts are critical. Bad proximity domains fall back to node 0.

## Test Signals
Test unsupported revisions, malformed MSC lengths, reserved field handling, disabled MSCs, MMIO and PCC interfaces, overflow/error IRQs, partitioned IRQ rejection, processor-container affinity, resource-node cache/memory RIS creation, and count-vs-parse behavior.
