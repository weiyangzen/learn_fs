# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utaddress.c

Purpose: `utaddress.c` tracks system-memory and system-I/O operation region address ranges so ACPICA can detect overlaps between AML `OperationRegion` declarations and host accesses.

Important APIs/types/functions: `acpi_ut_add_address_range()` allocates and links an `acpi_address_range` for a namespace region node. `acpi_ut_remove_address_range()` removes the entry for a region node. `acpi_ut_check_address_range()` counts and optionally warns about overlap with tracked ranges. `acpi_ut_delete_address_lists()` frees all global range lists at shutdown.

Control flow: Add/remove/check ignore address spaces other than `ACPI_ADR_SPACE_SYSTEM_MEMORY` and `ACPI_ADR_SPACE_SYSTEM_IO`. Adds compute inclusive end address and push to `acpi_gbl_address_range_list[space_id]`. Checks compute the queried inclusive end and use interval overlap logic across the list, optionally building a normalized pathname for warnings.

State and persistence behavior: The persistent state is the linked list array `acpi_gbl_address_range_list`. Entries live from evaluated op-region creation until region deletion or subsystem shutdown. The file assumes namespace locking per comments rather than taking its own mutex.

Dependencies and integration points: It depends on namespace nodes/pathname helpers, region-name decoding from `utdecode.c`, ACPICA allocation, and region object deletion in `utdelete.c`, which removes ranges for permanent regions.

Risks and test signals: Risks include length-zero underflow, address+length overflow, missing namespace lock coverage, stale region nodes, and warning allocation failure assumptions. Tests should exercise overlapping/non-overlapping ranges, unsupported address spaces returning zero conflicts, removal at list head/middle, shutdown cleanup, and diagnostic pathnames for conflicts.
