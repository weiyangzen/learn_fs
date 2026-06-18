## sources/distributed-fs/ceph-client/drivers/acpi/acpica/uttrack.c

Purpose: `uttrack.c` implements ACPICA debug-only allocation tracking when `ACPI_DBG_TRACK_ALLOCATIONS` is enabled. It helps detect leaks, duplicate frees, invalid descriptors, and outstanding cache allocations.

Important APIs and functions: `acpi_ut_create_list` allocates a tracking list descriptor. `acpi_ut_allocate_and_track` and `acpi_ut_allocate_zeroed_and_track` allocate memory with a debug header and insert it into the global list. `acpi_ut_free_and_track` removes a block, updates counters, poisons user memory with `0xEA`, and frees it. Static `acpi_ut_find_allocation`, `acpi_ut_track_allocation`, and `acpi_ut_remove_allocation` manage the address-ordered doubly linked list. `acpi_ut_dump_allocation_info` is mostly stubbed/commented, and `acpi_ut_dump_allocations` prints outstanding matching allocations with descriptor interpretation.

Control flow: allocation normalizes zero-byte requests to one byte with a warning, allocates header plus user payload, tracks under `ACPI_MTX_MEMORY`, and updates totals/max occupancy. Free derives the header from the user pointer, updates totals, unlinks under the memory mutex, poisons, and frees.

State and dependencies: persistent debug state includes `acpi_gbl_global_list`, allocation counters, current/max size, `acpi_gbl_disable_mem_tracking`, `acpi_gbl_verbose_leak_dump`, and the global allocation list. It depends on `ACPI_MTX_MEMORY`, descriptor macros, and diagnostic output.

Integration points: ACPICA allocation macros route here in debug builds. Leak dumps integrate with object, parser, and namespace descriptor layouts.

Risks: this code is intentionally expensive and debug-only. If tracking is disabled midstream, list consistency assumptions differ. Pointer ordering in `acpi_ut_find_allocation` assumes comparable allocation addresses.

Test signals: zero-size allocation, duplicate insertion detection, freeing null, freeing with empty list, component/module-filtered dumps, cached descriptor suppression, verbose hex dump, and descriptor type/size validation are useful.
