# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopcode.c

## Purpose
`psopcode.c` defines the master AML opcode information table, `acpi_gbl_aml_op_info`. This table is the parser and interpreter contract for every AML opcode ACPICA recognizes: names, parser argument templates, interpreter argument templates, result object types, opcode classes, execution types, and flags.

## Important APIs, types, and functions
The file exports data rather than functions. `acpi_gbl_aml_op_info[AML_NUM_OPCODES]` is an array of `struct acpi_opcode_info` entries created with `ACPI_OP()`. It includes standard AML opcodes, extended two-byte opcodes, internal parser-only opcodes such as `-NamePath-`, `-MethodCall-`, `-ByteList-`, field helper opcodes, return-value placeholders, unknown/ascii/prefix pseudo-ops, and newer ACPI opcodes such as `External`, `Comment`, `Timer`, and `DataTableRegion`.

## Control flow
There is no runtime control flow in this file. Runtime consumers index this table through lookup tables in `psopinfo.c`. Parser code reads `parse_args`, `class`, `type`, and flags to decide how to parse, whether to create namespace nodes, whether to defer bodies, whether an op has targets or return values, and whether a parse object needs extended storage. Interpreter code reads `runtime_args`, object type, and flags to prepare operands and dispatch execution.

## State and persistence behavior
The table is immutable global parser/interpreter metadata. Its values effectively define persistent ACPICA behavior for all AML parsing and execution. Any edit changes how firmware bytecode is decoded throughout the subsystem.

## Dependencies and integration points
The table depends on constants from `acopcode.h` and `amlcode.h`. It is consumed by `acpi_ps_get_opcode_info()`, `acpi_ps_get_opcode_name()`, `acpi_ps_alloc_op()`, `acpi_ps_get_arguments()`, parse-tree traversal, dispatcher operand resolution, and disassembler/debug output.

## Risks and edge cases
Incorrect flags have wide blast radius. Missing `AML_DEFER` can parse executable bodies too early; missing `AML_NAMED` or namespace flags can prevent namespace object creation; wrong argument templates desynchronize the AML pointer; wrong execution flags can break operand resolution or target handling. Internal pseudo-op entries must align with index lookup tables and `AML_NUM_OPCODES`.

## Test signals
Signals include full ACPICA table-load suites, opcode-by-opcode disassembly round trips, parser pointer synchronization across all opcode templates, namespace creation for all named opcodes, deferred parsing for methods/regions/buffers/packages/create fields, method-call pseudo-op behavior, and lookup-table consistency checks.
