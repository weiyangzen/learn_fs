# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresop.c

## Purpose
`exresop.c` resolves and type-checks operand stacks according to opcode runtime argument metadata before AML opcode execution.

## Important APIs, Types, and Functions
The exported function is `acpi_ex_resolve_operands()`. The local checker is `acpi_ex_check_object_type()`. It consumes `struct acpi_opcode_info::runtime_args`, `ARGI_*` operand encodings, opcode flags, `struct acpi_walk_state`, and operand/reference descriptors.

## Control Flow, State, and Persistence
The resolver fetches opcode metadata, walks encoded argument types from the operand stack, validates descriptors, resolves aliases, validates local reference classes, and decides whether each operand should remain a reference or be resolved to a value. For value operands it calls `acpi_ex_resolve_to_value()` and then enforces simple or complex type requirements. It performs implicit source conversions for integer, buffer, string, buffer-or-string, and computed-data arguments. It treats store targets specially so index references are not accidentally dereferenced, allows AML constants as no-op store targets, supports interpreter slack for broad `Store` sources, and permits Debug object stores.

## Dependencies and Integration Points
This is the gate between the parser/dispatcher and executor opcode handlers. It depends on opcode metadata tables, namespace aliasing, conversion helpers, `acpi_ex_resolve_to_value()`, local reference validation, and global `acpi_gbl_enable_interpreter_slack`.

## Risks and Test Signals
Risks include wrong ARGI metadata interpretation, stack direction mistakes, implicit conversion behavior that differs from the ACPI specification, dereferencing store targets too early, accepting invalid reference classes, and Debug/slack mode masking bugs. Tests should execute opcodes from each ARGI category, invalid operand descriptors, alias operands, constant store targets, store of index references, conversion success/failure for integer/string/buffer, `CopyObject`, `SizeOf`, `Load`, DDB handles, and slack-mode differences.
