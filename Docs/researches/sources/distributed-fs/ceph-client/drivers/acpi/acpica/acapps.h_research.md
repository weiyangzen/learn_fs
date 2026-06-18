# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acapps.h

Purpose: shared ACPICA application/tool header for utility signons, usage text, table/file helpers, getopt state, disassembler namespace helpers, and output filename/table helpers.

Important APIs/macros: signon/header macros include `ACPICA_NAME`, `ACPICA_COPYRIGHT`, `ACPI_WIDTH`, `ACPI_COMMON_SIGNON`, `ACPI_COMMON_HEADER`, and `ACPI_COMMON_BUILD_TIME`. Usage and status macros include `ACPI_USAGE_HEADER`, `ACPI_USAGE_TEXT`, `ACPI_OPTION`, `ACPI_CHECK_STATUS`, and `ACPI_CHECK_OK`. Declared helpers include `ac_get_all_tables_from_file`, `ac_delete_table_list`, `ac_is_file_binary`, `ac_validate_table_header`, `acpi_getopt`, `acpi_getopt_argument`, disassembler namespace functions, and filename/table-output helpers.

Control flow: tool code uses this header to print startup text, parse options, load ACPI tables from files, post-process disassembler namespace state, and generate output paths. It declares behavior implemented by ACPICA application sources rather than normal kernel runtime paths.

State and persistence: state is external and tool-owned: option globals, files, table descriptor lists, parse trees, and namespace roots. The header itself owns no state.

Dependencies and integration: depends on standard headers when enabled, ACPICA public/internal types, parse objects, namespace nodes, `FILE`, and `ACPI_FILE`. It integrates command-line ACPICA utilities with shared table/disassembler code.

Risks: option parser globals are process-global and not thread-safe. Print macros assume application I/O facilities. Tool-only declarations can be mistaken for kernel-runtime APIs. Version strings must track ACPICA.

Test signals: ACPICA utility builds, usage output snapshots, getopt edge cases, binary/text table detection, invalid table headers, disassembler namespace cross-reference, and filename/path splitting.
