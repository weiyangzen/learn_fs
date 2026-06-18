# sources/distributed-fs/ceph-client/lib/fw_table.c

## Purpose
`fw_table.c` provides firmware-table subtable parsing for ACPI and ACPI-like tables, including CDAT. It abstracts differences in subtable header layout and length encoding, then dispatches matching entries to caller-provided handlers.

## Important APIs, Types, and Functions
`enum acpi_subtable_type` distinguishes common ACPI, HMAT, PRMT, CEDT, and CDAT subtables. `struct acpi_subtable_entry` pairs a `union acpi_subtable_headers *` with that type. Helper functions derive entry type, entry length, subtable header length, root table length, and subtable kind from the table signature. `acpi_parse_entries_array()` is the central parser. `cdat_table_parse()` wraps it for CDAT and exports `EXPORT_SYMBOL_FWTBL_LIB`.

## Control Flow, State, and Persistence
Parsing begins by selecting the table type from the four-character signature, reading the root table length, honoring an optional `max_length`, and starting at `table_header + table_size`. It walks subtables until the next minimum header would exceed `table_end`, compares each entry type against each `acpi_subtable_proc`, invokes the matching handler until `max_entries` is reached, increments per-proc and total counts even for ignored overflow entries, and advances by the entry's encoded length. Zero-length entries are rejected to avoid infinite loops.

## Dependencies and Integration Points
The file depends on ACPI/CDAT structure definitions from `<linux/acpi.h>` and `<linux/fw_table.h>`, endian conversion for CDAT lengths, and kernel diagnostics. It integrates with ACPI table consumers that provide `struct acpi_subtable_proc` arrays and with CXL/CDAT users through `cdat_table_parse()`.

## Risks and Test Signals
Risks include malformed firmware lengths, signatures that choose the wrong header interpretation, truncation by `max_length`, handlers receiving entries whose semantic payload length is not otherwise validated here, and warning messages using `proc->id` for aggregate diagnostics. Tests should include common ACPI, HMAT, CEDT, PRMT, and CDAT tables; little-endian CDAT length handling; zero-length subtable rejection; `max_entries` warning behavior; handler and handler_arg dispatch; and truncated table bounds.
