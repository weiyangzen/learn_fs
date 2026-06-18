# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopinfo.c

## Purpose
`psopinfo.c` implements AML opcode metadata lookup helpers and the direct opcode-to-table-index maps used by the parser. It is the fast path from raw AML opcode bytes to `struct acpi_opcode_info`.

## Important APIs, types, and functions
Key functions are `acpi_ps_get_opcode_info()`, `acpi_ps_get_opcode_name()`, and `acpi_ps_get_argument_count()`. Global tables include `acpi_gbl_argument_count[]`, `acpi_gbl_short_op_index[256]`, and `acpi_gbl_long_op_index[NUM_EXTENDED_OPCODE]`. The helpers return entries from `acpi_gbl_aml_op_info`.

## Control flow
`acpi_ps_get_opcode_info()` first distinguishes one-byte opcodes from extended opcodes by checking the high byte. One-byte opcodes index `acpi_gbl_short_op_index`. Extended opcodes must have the extended prefix and a second byte at or below `MAX_EXTENDED_OPCODE`, then index `acpi_gbl_long_op_index`. Unknowns return the `_UNK` opcode-info entry, and ASL compiler debug builds can name raw-data pseudo opcodes for diagnostics. `acpi_ps_get_opcode_name()` returns the table name only when disassembler or debug output is enabled; otherwise it returns a fixed unavailable string. `acpi_ps_get_argument_count()` maps execution type classes to counts for target/operand marking.

## State and persistence behavior
All state is immutable global lookup data. The functions are pure lookups except for debug output. The tables persist for the lifetime of ACPICA and must stay synchronized with `psopcode.c`.

## Dependencies and integration points
This file integrates with `psopcode.c`, AML constants, parser object allocation, opcode classification in `psobject.c`, debug output, disassembler builds, and target-count logic in `pstree.c`/`psobject.c`.

## Risks and edge cases
The guarantee that `acpi_ps_get_opcode_info()` always returns a valid pointer is essential. A wrong short or long index maps raw AML to the wrong grammar. Extended-opcode bounds must prevent out-of-range table access. Non-debug builds returning `"OpcodeName unavailable"` can limit diagnostics unless debug/disassembler is enabled.

## Test signals
Tests should verify every valid AML opcode maps to the intended `acpi_gbl_aml_op_info` index, unknown bytes map to `_UNK`, ASCII and prefix bytes map to pseudo classes, extended opcodes respect bounds, opcode names are stable in debug builds, and argument counts match execution type constants.
