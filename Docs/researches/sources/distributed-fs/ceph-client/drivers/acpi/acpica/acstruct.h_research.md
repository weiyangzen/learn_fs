# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acstruct.h

## Purpose
Defines core ACPICA internal state structures used by parse-tree walking, control method execution, namespace/device initialization, evaluation, debugger walks, and region display.

## Important APIs, Types, And Fields
`struct acpi_walk_state` is the central interpreter/parser execution frame. It stores walk type, current opcode, owner ID, method nesting, parser state, arguments, locals, operand stack, method descriptors/nodes, parse op pointers, result stack, scope/control stacks, current thread, callbacks, breakpoints, implicit return object, and execution flags. `struct acpi_init_walk_info`, `struct acpi_get_devices_info`, `union acpi_aml_operands`, `struct acpi_evaluate_info`, `struct acpi_device_walk_info`, `struct acpi_region_walk_info`, and `struct acpi_walk_info` are compact context objects for subsystem initialization, device enumeration, AML operand grouping, object evaluation, device `_STA`/`_INI` walks, and debugger display.

## Control Flow, State, And Persistence
The structures are mutable runtime state passed between dispatcher, parser, interpreter, namespace, and debugger layers. `acpi_walk_state` instances form linked stacks for nested methods and restarts; result/control/scope stacks are chained through generic-state objects. Evaluation state is usually stack-allocated by callers to reduce CPU stack pressure and carry predefined-name return analysis through namespace evaluation.

## Dependencies And Integration Points
This header depends on ACPICA parse objects, namespace nodes, operand objects, opcode info, generic state, parse callbacks, owner IDs, and thread state. It is integrated by dispatcher (`ds*`), parser (`ps*`), executor (`ex*`), namespace initialization/evaluation (`ns*`), and debugger display commands such as locals, args, result stack, and call tree.

## Risks And Test Signals
Changes have broad ABI-like internal impact because many subsystems assume field meaning and lifetime. Risks include stale operand/result pointers, incorrect method nesting or owner IDs, breakpoint state corruption, and leaks from result/control/scope stacks. Test signals include AML method execution, nested method calls, namespace load/unload, predefined return repair, single-step debugging, locals/args/results display, and stress tests that execute recursive or concurrently invoked methods.
