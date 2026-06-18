<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl.h

## Purpose
`actbl.h` defines the fundamental ACPI table structures directly consumed by ACPICA: common ACPI table headers, Generic Address Structures, RSDP/RSDT/XSDT, FACS, FADT, table descriptors, table-origin flags, FADT size/version helpers, and signature constants. It also includes the additional table catalogs from `actbl1.h`, `actbl2.h`, and `actbl3.h`.

## Important APIs, types, and functions
Important signatures include `ACPI_SIG_DSDT`, `ACPI_SIG_FADT`, `ACPI_SIG_FACS`, `ACPI_SIG_RSDP`, `ACPI_SIG_RSDT`, `ACPI_SIG_XSDT`, and `ACPI_SIG_SSDT`. Core structures are `struct acpi_table_header`, `struct acpi_generic_address`, `struct acpi_table_rsdp`, `struct acpi_rsdp_common`, `struct acpi_rsdp_extension`, `struct acpi_table_rsdt`, `struct acpi_table_xsdt`, `struct acpi_table_facs`, `struct acpi_table_fadt`, `union acpi_name_union`, and `struct acpi_table_desc`. Flags define FACS global-lock/wake behavior, FADT boot architecture and hardware flags, preferred PM profiles, sleep-control bits, table origins, verification/loading state, validation limits, and FADT version sizes.

## Control flow
There is no local runtime flow, but ACPICA table discovery uses the RSDP and RSDT/XSDT structures to locate other tables; FADT parsing populates `acpi_gbl_FADT` and drives hardware availability, SCI/GPE block setup, reset, sleep, and reduced-hardware decisions; FACS fields support global lock and waking vectors. The table manager tracks mapped/loaded tables through `struct acpi_table_desc`.

## State and persistence behavior
ACPI tables are firmware-provided persistent boot data, typically mapped into kernel memory. `struct acpi_table_desc` is runtime state tracking address, pointer, length, signature, owner ID, flags, and validation count. FADT/FACS fields describe firmware/platform state and may be copied, mapped, or overridden for the boot.

## Dependencies and integration points
`acpixf.h`, OSL table functions, Linux ACPI boot, PM, reset, event, and table override code all use these structures. GAS definitions also integrate with `acpi_io.h`, `acpiosxf.h`, and ACPICA register access APIs.

## Risks and test signals
Risks include byte-packing violations, misaligned 64-bit GAS accesses, trusting revision instead of length, corrupt 64-bit versus 32-bit FADT addresses, table validation leaks due to unmatched get/put, malformed checksums, and reduced-hardware flag handling. Test signals include RSDP discovery, RSDT versus XSDT fallback, FADT length variants V1/V2/V3/V5/V6, FACS global-lock behavior, sleep/reset register access, table override/install/unload, and checksum/length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl.h -->
