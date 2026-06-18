# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acparser.h

Purpose: declares AML parser interfaces for method/table execution, AML argument parsing, namepath parsing, parse-object creation/completion, opcode lookup, parse-loop control, scope-stack management, parse-tree manipulation, parse-tree walking, parser utilities, and debug display.

Important APIs/functions: defines parse flags for tree deletion, load pass 1, load pass 2, execute, deferred op, disassemble, and module-level parsing. Declares opcode index tables and functions including `acpi_ps_execute_method`, `acpi_ps_execute_table`, `acpi_ps_get_next_arg`, `acpi_ps_get_next_namepath`, `acpi_ps_build_named_op`, `acpi_ps_create_op`, `acpi_ps_complete_op`, `acpi_ps_get_opcode_info`, `acpi_ps_parse_aml`, `acpi_ps_parse_loop`, scope push/pop helpers, tree append/find/walk/delete helpers, op allocation/free/init, and parse-tree display helpers.

Control flow: parser entry points initialize walk/parse state, read AML bytecode using opcode metadata, manage package and scope boundaries, call dispatcher callbacks in load or execute modes, complete/delete parse nodes, and walk parse trees for execution or table processing.

State and persistence: state is in `acpi_parse_state`, `acpi_parse_object`, scope-stack states, walk states, namespace nodes, owner IDs, and caller return descriptors. Parse trees may be deleted or retained depending on flags.

Dependencies and integration: depends on parser structs from `aclocal.h`, opcode metadata, operand objects, and dispatcher callback types. Bridges raw AML to dispatcher, namespace loader, interpreter, disassembler, and debug display code.

Risks: package-end calculation, variable argument counts, method-call ambiguity, deferred ops, scope completion, and parse-tree deletion are common failure areas. Callback status handling must avoid leaks and skipped execution.

Test signals: AML fuzzing, table load passes, method execution with nested scopes, deferred methods/regions, malformed package lengths, method-call namepath ambiguity, disassembly parses, parse-tree deletion on errors, and debug tree output.
