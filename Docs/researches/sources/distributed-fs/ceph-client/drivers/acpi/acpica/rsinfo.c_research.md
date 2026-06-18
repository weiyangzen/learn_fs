# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsinfo.c

Purpose: centralizes ACPICA resource dispatch and size tables. It maps internal resource types, AML descriptor names, and serial bus subtypes to conversion tables, dump tables, and base structure sizes.

Important APIs, types, and functions: global arrays include `acpi_gbl_set_resource_dispatch`, `acpi_gbl_get_resource_dispatch`, `acpi_gbl_convert_resource_serial_bus_dispatch`, debug-only `acpi_gbl_dump_resource_dispatch`, debug-only `acpi_gbl_dump_serial_bus_dispatch`, `acpi_gbl_aml_resource_sizes`, `acpi_gbl_resource_struct_sizes`, `acpi_gbl_aml_resource_serial_bus_sizes`, and `acpi_gbl_resource_struct_serial_bus_sizes`.

Control flow: there are no functions. Runtime control flow occurs in consumers: `rslist.c` indexes get/set dispatch by AML resource index or internal type, handles serial bus through the subtype table, `rscalc.c` indexes size arrays for allocation planning, and `rsdump.c` indexes dump tables for diagnostics.

State and persistence: process-global read-only metadata. It does not allocate or mutate state.

Dependencies and integration points: integrates all resource descriptor implementation files. Adding a new resource type requires coordinated updates here, the relevant conversion table file, size calculations in `rscalc.c` when variable length is involved, dump tables in `rsdumpinfo.c`, and public type definitions.

Risks and test signals: array index order is the core risk. A misplaced entry can route an AML descriptor to the wrong conversion table or size, producing memory corruption or invalid resources. Serial bus entries start with a null slot and must remain bounded by `AML_RESOURCE_MAX_SERIALBUSTYPE`. Tests should validate dispatch coverage for every resource type and descriptor name, all size-table entries against `sizeof`/`ACPI_RS_SIZE`, and failure behavior for reserved or unsupported descriptors.
