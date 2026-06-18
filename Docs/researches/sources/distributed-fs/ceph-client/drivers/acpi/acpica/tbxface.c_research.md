# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxface.c

Purpose: `tbxface.c` exposes table-manager APIs used by the host OS and ACPICA clients to initialize the root table list, reallocate early static tables, retrieve tables/headers, release tables, and install/remove global table event handlers.

Important APIs/types/functions: `acpi_allocate_root_table()` allocates a resizable root array. `acpi_initialize_tables()` seeds the root list, locates the RSDP through `acpi_os_get_root_pointer()`, and parses the root table. `acpi_reallocate_root_table()` moves early table descriptors into dynamic memory and enables deferred validation. Retrieval APIs are `acpi_get_table_header()`, `acpi_get_table()`, `acpi_put_table()`, and `acpi_get_table_by_index()`. Event handler APIs are `acpi_install_table_handler()` and `acpi_remove_table_handler()`.

Control flow: Initialization either allocates a root table array or installs a caller-provided static array, then parses RSDT/XSDT. Reallocation checks for wrong early-stage validated state, turns on full validation when previously deferred, verifies existing descriptors, removes invalid ones, and resizes the list under `ACPI_MTX_TABLES`. `acpi_get_table_header()` can map only the header for physical unmapped tables, while `acpi_get_table()` uses descriptor validation and requires caller pairing with `acpi_put_table()`. Handler install/remove is serialized under `ACPI_MTX_EVENTS` and allows only one handler.

State and persistence behavior: Persistent state includes `acpi_gbl_root_table_list`, `acpi_gbl_enable_table_validation`, descriptor validation state, and global table handler/context. Table pointers returned by `acpi_get_table()` hold descriptor validation references until released.

Dependencies and integration points: This file is the external boundary for the table subsystem, integrating OSL RSDP discovery, root parsing in `tbutils.c`, descriptor resizing/verification, table mutexes, event mutexes, and exported ACPICA symbols used by the Linux ACPI core.

Risks and test signals: Risks include unbalanced get/put table lifetimes across boot stages, reallocation while descriptors are still validated, invalid instance numbering, single-handler conflicts, and header-only mapping failures. Tests should cover static and dynamic root arrays, reallocation after deferred validation, table retrieval by signature and index, null-output semantics, handler duplicate install/remove errors, and lockdep-style checks around table/event mutexes.
