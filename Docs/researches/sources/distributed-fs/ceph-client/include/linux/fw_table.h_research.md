<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fw_table.h -->
# sources/distributed-fs/ceph-client/include/linux/fw_table.h

Purpose: Provides shared parsing declarations for ACPI and ACPI-like firmware tables, including CXL CDAT consumers.

Important APIs/types/functions: Handler typedefs are `acpi_tbl_entry_handler` and `acpi_tbl_entry_handler_arg`. `acpi_subtable_proc` binds IDs, handlers, arguments, and count. `fw_table_header` overlays ACPI and CDAT table headers. `acpi_subtable_headers` overlays known subtable header variants. Main functions are `acpi_parse_entries_array()` and `cdat_table_parse()`. `EXPORT_SYMBOL_FWTBL_LIB()` and `__init_or_fwtbl_lib` select export/init attributes depending on ACPI and CXL.

Control flow: Callers supply a firmware table header, max length, and handler array. The parser walks subtables, dispatches matching IDs to handlers, and records counts. CDAT parsing filters by `enum acpi_cdat_type`.

State and persistence behavior: This header defines no stored state; parser state is caller-owned and counts are held in `acpi_subtable_proc`.

Dependencies and integration points: Depends on ACPI table structures and CXL when non-ACPI CDAT parsing is enabled. Used by firmware discovery code that needs consistent subtable iteration.

Risks: Parser correctness depends on length bounds and table header compatibility. Incorrect export namespace selection can break modular CXL consumers.

Test signals: ACPI table parser unit tests, malformed length/table boundary inputs, CDAT parser tests, and build combinations for ACPI-only, CXL-only, and both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fw_table.h -->
