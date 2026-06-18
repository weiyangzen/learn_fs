# sources/distributed-fs/ceph-client/drivers/acpi/acpica/actables.h

## Purpose
Declares internal ACPICA table-management APIs for root table allocation, RSDP discovery/validation, table descriptor lifecycle, FADT handling, table lookup, install/load/unload, owner ID management, and namespace loading.

## Important APIs And Functions
Root and RSDP helpers include `acpi_allocate_root_table`, `acpi_tb_get_rsdp_length`, `acpi_tb_validate_rsdp`, and `acpi_tb_scan_memory_for_rsdp`. Descriptor functions include `acpi_tb_get_next_table_descriptor`, `acpi_tb_init_table_descriptor`, `acpi_tb_acquire_temp_table`, `acpi_tb_validate_temp_table`, `acpi_tb_verify_temp_table`, `acpi_tb_validate_table`, and `acpi_tb_invalidate_table`. Install/load APIs include `acpi_tb_install_standard_table`, `acpi_tb_install_and_load_table`, `acpi_tb_load_table`, `acpi_tb_unload_table`, and `acpi_tb_load_namespace`. Owner and cleanup APIs include `acpi_tb_delete_namespace_by_owner`, `acpi_tb_allocate_owner_id`, `acpi_tb_release_owner_id`, `acpi_tb_get_owner_id`, and `acpi_tb_terminate`.

## Control Flow, State, And Persistence
The declared routines manage entries in `acpi_gbl_root_table_list`, table descriptors, mapped table memory, table loaded flags, owner IDs, and namespace objects created from AML tables. Typical flow is parse RSDP/root tables, acquire/validate descriptors, optionally override tables, install into the root list, load AML into the namespace, mark loaded, and later unload/delete namespace objects by owner.

## Dependencies And Integration Points
Depends on ACPI physical addresses, table headers, descriptors, namespace nodes, and status codes. It is consumed by initialization, table external APIs, debugger table display/unload commands, dynamic table load support, FADT/FACS handling, and namespace teardown.

## Risks And Test Signals
Risks include stale mappings, double loads/unloads, owner ID leaks, bad override handling, namespace objects surviving table unload, and RSDP/checksum validation regressions. Test signals include boot-time table discovery, dynamic SSDT load/unload, debugger `Tables` and `Unload`, table notification callbacks, FADT conversion validation, and namespace cleanup after table removal.
