# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfload.c

Purpose: `tbxfload.c` exposes table load and unload APIs that populate the ACPI namespace from DSDT/SSDT/PSDT/OSDT tables, support host-directed dynamic table loads, and unload namespace objects owned by dynamically loaded tables.

Important APIs/types/functions: `acpi_load_tables()` installs default region handlers, calls `acpi_tb_load_namespace()`, then initializes namespace objects. `acpi_tb_load_namespace()` validates/loads DSDT first, optionally copies DSDT locally, records the original DSDT header, then loads SSDT/PSDT/OSDT tables. `acpi_install_table()` and `acpi_install_physical_table()` install tables before namespace load. `acpi_load_table()` dynamically installs and loads a table, returning an optional table index. `acpi_unload_parent_table()` and `acpi_unload_table()` unload SSDT/OEMx-style tables but reject the DSDT.

Control flow: Namespace load holds `ACPI_MTX_TABLES` while selecting/validating descriptors but releases it during `acpi_ns_load_table()` calls. DSDT failure is tracked separately, while optional table failures increment counters and eventually return `AE_CTRL_TERMINATE`; `acpi_load_tables()` converts that aggregate partial-failure code to `AE_OK` before object initialization. Dynamic load installs and loads in one path via `acpi_tb_install_and_load_table()`, then initializes newly created objects.

State and persistence behavior: It sets `acpi_gbl_DSDT`, `acpi_gbl_original_dsdt_header`, `acpi_gbl_namespace_initialized`, table owner IDs, and namespace objects created by AML load. Unload uses owner IDs to remove namespace objects and descriptors; DSDT owner/table index is protected from unload.

Dependencies and integration points: It depends on event region handler installation, namespace loading/initialization/termination support, table install/load/unload helpers, table mutexes, DSDT copy policy, and exported API symbols used by hotplug and early ACPI initialization.

Risks and test signals: Risks include lock release/reacquire around namespace loading, DSDT validation/copying races, partial optional table failure semantics, returning table indexes after dynamic load failure, and owner ID mismatches during unload. Tests should inspect namespace object counts after load, logs for failed optional AML tables, successful initialization of operation regions/buffers/packages, dynamic SSDT hot-add/hot-remove, and rejection of DSDT unload by handle or table index.
