# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg1.c

## Purpose
`exoparg1.c` executes AML opcodes with zero or one input argument, including `Timer`, synchronization/control side effects, `Store`, conversion operators, `RefOf`, `DerefOf`, `SizeOf`, `ObjectType`, increment/decrement, and BCD/bit search helpers. It is part of the ACPICA executor dispatch layer and assumes the dispatcher has already parsed the opcode form and resolved operands to the expected stack slots.

## Important APIs, Types, and Functions
Exported executor entry points are `acpi_ex_opcode_0A_0T_1R()`, `acpi_ex_opcode_1A_0T_0R()`, `acpi_ex_opcode_1A_1T_1R()`, and `acpi_ex_opcode_1A_0T_1R()`. They operate on `struct acpi_walk_state`, `walk_state->opcode`, `walk_state->operands[]`, and `walk_state->result_obj`. Important dependencies include `acpi_ut_create_integer_object()`, `acpi_ex_store()`, `acpi_ex_resolve_operands()`, `acpi_ex_resolve_multiple()`, `acpi_ex_get_object_reference()`, `acpi_ex_read_data_from_field()`, `acpi_ds_method_data_get_value()`, `acpi_ds_get_buffer_arguments()`, and `acpi_ds_get_package_arguments()`.

## Control Flow, State, and Persistence
Each exported function switches on the AML opcode and writes either a new return descriptor or side effects into ACPI objects. `Timer` returns the OS timer. `Release`, `Reset`, `Signal`, `Sleep`, `Stall`, and `Unload` delegate to mutex/event/table/OS wrappers. `Store` calls `acpi_ex_store()` and returns the stored source object unless a field store already produced a result. Conversion and bit/BCD opcodes allocate temporary integer/string/buffer objects, store into the target operand, and retain the result through `walk_state->result_obj`. `DerefOf` has the most branching: it handles locals/args, `RefOf`, strings that name namespace nodes, device/thermal namespace nodes, index references into buffers/packages, and field references that require an actual field read. Persistent effects are reference-count changes, target stores, field reads/writes through downstream helpers, namespace/table load effects from `Load`, and interpreter-visible `result_obj` ownership.

## Dependencies and Integration Points
This file is reached from ACPICA dispatcher opcode execution after operand resolution. It integrates with namespace nodes, method local/arg storage, field access, table loading, conversion helpers, and OS synchronization/time services. It also depends on global integer sizing such as `acpi_gbl_integer_nybble_width` and `acpi_gbl_integer_byte_width`.

## Risks and Test Signals
Risks include reference leaks or premature drops around `Store`, `CondRefOf`, `DerefOf`, and increment/decrement; incorrect handling of uninitialized package elements; BCD overflow and invalid digit detection; 32-bit versus 64-bit integer width behavior; and string namespace lookup failures. Tests should exercise all listed opcodes, stores to locals/args/names/fields/index targets, dereferencing nested references, `DerefOf` on string paths, buffer and package `SizeOf`, missing `CondRefOf` targets, BCD boundary values, and error paths for unsupported obsolete shift-bit opcodes.
