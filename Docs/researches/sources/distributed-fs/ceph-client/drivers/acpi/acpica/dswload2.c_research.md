# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload2.c

## Purpose
Implements second-pass namespace loading callbacks. Pass 2 resolves namespace references and method calls, completes named object creation, initializes fields and operation regions, attaches data objects to name nodes, and supports execution-time creation of temporary method-local namespace objects.

## Important APIs, Types, And Functions
- `acpi_ds_load2_begin_op` performs namespace lookup or creation for pass 2, including namepaths, Scope targets, field op placeholders, existing pass-1 nodes, temporary execute-mode nodes, and external-op compiler handling.
- `acpi_ds_load2_end_op` finalizes namespace objects by opcode type: create fields, field/index/bank fields, processor/power/mutex/event/alias objects, regions/data regions, names, methods, and method-call resolution.

## Control Flow
On descent, conditional module-level loops can be delegated to execution begin logic. Namepath ops are looked up but not created. Scope ops push scope frames for valid scope targets and warn on compatibility type overrides. Other namespace opcodes either reuse `op->common.node`, use `deferred_node`, or call `acpi_ns_lookup` in load-pass-2 mode with prefix-must-exist and temporary-node flags as needed. On ascent, the node saved in the op is pushed as operand zero, scope frames are popped, and a switch on opcode type creates the concrete runtime object or resolves a method call. Region creation may be deferred until method execution, but `acpi_ev_initialize_region` is invoked to attach available handlers. Name ops use `acpi_ds_create_node`, and method ops attach method objects if not already present.

## State And Persistence
Pass 2 persists namespace node attachments, region handler associations, field objects, method dispatch metadata, alias relationships, and temporary nodes for control-method execution. It uses `walk_state->operands[0]` as the current node carrier and resets operand counts during cleanup.

## Dependencies And Integration Points
Depends on namespace lookup/search, scope stack management, field creation helpers, executor object constructors, operation-region initialization, method creation, data-object creation, parser opcode metadata, and ACPI_EXEC_APP initialization-file hooks. It is called both by table loading and from method execution paths for runtime named declarations.

## Risks And Edge Cases
Temporary node flags must be applied only for control-method execution outside module-level code. Scope pop must match prior open-scope decisions. Region initialization can run `_REG` methods and must be invoked with interpreter locking assumptions satisfied by callers. Method-call resolution intentionally looks up `ACPI_TYPE_ANY` first to detect non-method names cleanly. Some cleanup paths return early and must leave operand zero cleared.

## Test Signals
Use AML with runtime-created named objects, field/index/bank field declarations, `Name` objects holding buffers/packages, regions whose handlers are installed before and after creation, method calls to non-method names, and module-level conditional loops that require pass-2 plus execution interaction.
