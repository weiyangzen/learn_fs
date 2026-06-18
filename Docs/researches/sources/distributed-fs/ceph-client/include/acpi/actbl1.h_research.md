<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl1.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl1.h

## Purpose
`actbl1.h` defines many additional ACPI table layouts used primarily by OS drivers, firmware error handling, debug/boot infrastructure, IOMMU/NUMA/memory-topology code, CXL support, and ACPICA disassembly tools. These tables are not all consumed directly by ACPICA core, but they form the shared binary ABI between firmware and Linux ACPI subsystems.

## Important APIs, types, and functions
The header declares signatures for tables including AEST, ASF, ASPT, BERT, BGRT, BOOT, CDAT, CEDT, CPEP, CSRT, DBG2, DBGP, DMAR, DRTM, DTPR, ECDT, EINJ, ERST, FPDT, GTDT, HEST, HMAT, HPET, IBFT, MSCT, NBFT, PCCS, S3PT, and reserved/field-seen signatures. Common structures include `struct acpi_subtable_header`, `struct acpi_subtbl_hdr_16`, and `struct acpi_whea_header`. Major table families include ASF remote-management records, BERT/HEST generic error records, CXL CDAT/CEDT structures, CSRT resources, debug-port tables, Intel DMAR subtables and device scopes, DRTM and DTPR security/protection structures with bit helper macros, ECDT boot EC resources, EINJ/ERST WHEA action entries, FPDT/S3PT performance records, ARM GTDT timers/watchdogs, HMAT heterogeneous memory locality/cache records, HPET timers, and iBFT boot network records.

## Control flow
This header is declarative. Runtime parsers locate a table by signature, validate the common header and length, then walk variable-length subtables using the family-specific header length fields. WHEA-style tables execute action/instruction entries against GAS registers. DMAR, CEDT, HMAT, GTDT, HPET, and iBFT consumers translate table data into kernel subsystems such as IOMMU, CXL, NUMA/memory tiers, timers, watchdogs, and boot networking.

## State and persistence behavior
The structures describe firmware-persistent boot tables and sometimes firmware-owned memory regions. Runtime state is created by consumers after parsing, such as IOMMU units, error-source records, timer devices, EC boot resources, memory-locality data, or CXL windows. The header owns no mutable state.

## Dependencies and integration points
It depends on packed ACPI table layout conventions and `struct acpi_generic_address` from `actbl.h`. Integration points span Linux APEI/WHEA error handling, CXL, VT-d/IOMMU, trusted execution, EC, debug console discovery, HPET/ARM timer drivers, NUMA/HMAT memory topology, iSCSI boot, and platform boot graphics/performance reporting.

## Risks and test signals
Risks include walking malformed variable-length subtables, using stale spec revisions, structure-size drift, flexible-array bounds errors, action-table instruction misuse, security-sensitive table trust in DRTM/DTPR/DMAR, and consumer disagreement on flags or address widths. Test signals include table checksum and length fuzzing, subtable length underflow/overflow tests, DMAR device-scope parsing, EINJ/ERST action execution with preserve masks, HEST/BERT generic error data parsing, CEDT/CDAT/HMAT topology parsing, GTDT timer/watchdog discovery, ECDT EC boot setup, HPET discovery, iBFT parsing, and build coverage for all table consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl1.h -->
