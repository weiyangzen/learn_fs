## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxface.c

Purpose: `utxface.c` exposes miscellaneous external ACPICA utility interfaces: subsystem termination, optional status/system info/statistics APIs, cache purging, `_OSI` interface management, operation-region overlap checks, and `_PLD` buffer decoding.

Important APIs and functions: `acpi_terminate` shuts down ACPICA resources, mutexes, and the OS layer. Future-usage blocks include `acpi_subsystem_status`, `acpi_get_system_info`, `acpi_get_statistics`, and `acpi_install_initialization_handler`. Runtime exports include `acpi_purge_cached_objects`, `acpi_install_interface`, `acpi_remove_interface`, `acpi_install_interface_handler`, `acpi_update_interfaces`, `acpi_check_address_range`, and `acpi_decode_pld_buffer`.

Control flow: interface APIs validate names, lock `acpi_gbl_osi_mutex`, then use `utosi.c` list helpers or handler state. Cache purging calls OS cache purge on state, operand, and parser caches. Address-range checking locks the namespace before querying operation-region overlaps. `_PLD` decoding validates buffer length, allocates `struct acpi_pld_info`, reads packed dwords with ACPI macros, and fills revision 1 plus optional revision 2 fields.

State and dependencies: persistent state includes startup flags, global FADT/system counters/debug levels, caches, `_OSI` list/handler, namespace region data, and allocated `_PLD` result buffers owned by callers.

Integration points: ACPI core init/exit, drivers using public ACPICA APIs, firmware interface policy, device physical-location parsing, and operation-region safety checks all route through this file.

Risks: many optional APIs are build-gated. `_PLD` callers must free returned memory. Interface modifications affect firmware execution paths. Termination order matters because mutexes are deleted before OS termination.

Test signals: invalid buffer/name parameters, interface install/remove/reinstall, handler duplicate install/removal, cache purge success, address overlap warnings, `_PLD` rev1/rev2 decoding, short `_PLD` rejection, and termination after partial initialization are relevant.
