# sources/distributed-fs/ceph-client/include/acpi/actbl3.h

Purpose: Provides packed ACPI table definitions for another group of platform tables, especially NUMA locality, serial console redirection, IPMI, TPM/TCG logs, virtual I/O translation, watchdogs, Windows platform/security tables, and Xen environment data.

Important APIs, types, and functions: Exports signature macros including `ACPI_SIG_SLIT`, `ACPI_SIG_SPCR`, `ACPI_SIG_SPMI`, `ACPI_SIG_SRAT`, `ACPI_SIG_TCPA`, `ACPI_SIG_TPM2`, `ACPI_SIG_VIOT`, `ACPI_SIG_WDAT`, `ACPI_SIG_WDDT`, `ACPI_SIG_WDRT`, `ACPI_SIG_WPBT`, `ACPI_SIG_WSMT`, and `ACPI_SIG_XENV`. Major structs include `acpi_table_slit`, `acpi_table_spcr`, `acpi_table_spmi`, `acpi_table_srat` and SRAT affinity subtables, TCPA client/server trailers, TPM2 revision-3/revision-4 layouts and ARM SMC trailer, VIOT node descriptors, watchdog action/resource descriptors, WPBT handoff metadata, WSMT mitigation flags, and Xen grant/event fields.

Control flow: No runtime logic is implemented. Consumers use table signatures, revisions, subtable type enums, count/offset fields, and table-specific flags to discover devices or firmware behavior. SRAT walkers derive CPU/memory/I/O proximity domains; SPCR initializes early console; TPM and TCPA consumers locate control blocks and event logs; watchdog drivers interpret action instruction entries.

State and persistence: The file models firmware-persistent table bytes and no mutable kernel state. Tables expose persistent configuration such as NUMA affinities, TPM log physical addresses, watchdog register programming sequences, and hypervisor grant/event resources.

Dependencies and integration points: Uses ACPICA common headers and `acpi_generic_address`. Integrates with NUMA initialization, console/serial early boot, IPMI/SPMI, TPM CRB/TIS/SMC paths, virtio-IOMMU discovery through VIOT, watchdog frameworks, Windows compatibility/security reporting, and Xen ACPI plumbing.

Risks and test signals: Risks include incorrect packed layout, misinterpreting SRAT flags or proximity domains, unsafe physical log/control addresses, invalid watchdog instruction masks, and start-method-specific TPM parsing mistakes. Test by dumping and parsing firmware tables, booting with known SRAT/SLIT/TPM2/SPCR/VIOT fixtures, malformed count/offset fuzzing, watchdog action validation, and cross-platform build checks.
