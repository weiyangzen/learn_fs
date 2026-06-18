# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psparse.c

## Purpose
`psparse.c` provides top-level AML parsing orchestration and parser-state transitions. It peeks opcode size, completes parse ops, interprets callback control statuses, manages nested method execution through walk-state stacks, and performs final method/table parse cleanup.

## Important APIs, types, and functions
Exports include `acpi_ps_get_opcode_size()`, `acpi_ps_peek_opcode()`, `acpi_ps_complete_this_op()`, `acpi_ps_next_parse_state()`, and `acpi_ps_parse_aml()`. Key state types are `struct acpi_walk_state`, `struct acpi_thread_state`, `struct acpi_parse_state`, `union acpi_parse_object`, and `union acpi_operand_object`.

## Control flow
Opcode helpers return one or two-byte AML opcode identity without or with size calculation. `acpi_ps_complete_this_op()` stops opcode tracing, and when parse flags request tree deletion it unlinks the completed op from its parent, optionally inserts a return-value placeholder for contexts that need a value node after subtree deletion, then deletes the subtree. `acpi_ps_next_parse_state()` maps dispatcher statuses to AML pointer movement: terminate jumps to AML end, break/continue/pending jump to the last while, true skips the matching else package, false jumps to current package end, and transfer records method-call metadata.

`acpi_ps_parse_aml()` creates a thread state, pushes the initial walk state, installs it as `acpi_gbl_current_walk_list`, then repeatedly calls `acpi_ps_parse_loop()`. `AE_CTRL_TRANSFER` invokes `acpi_ds_call_control_method()` and continues with the newly pushed walk state. Completed or failed walks are popped, scope stacks are cleared, control methods are terminated when needed, parse scopes are cleaned, return or implicit-return objects are propagated to callers or released, and walk states are deleted. At final exit it releases all mutexes held by the thread, deletes thread state, and restores the previous global walk list.

## State and persistence behavior
Persistent state includes the global current walk list during execution and method objects that may be marked pending serialized after reentrancy-related `AE_ALREADY_EXISTS`. Transient state includes thread/walk stacks, parser scopes, control states, return descriptors, implicit return objects, and parse subtrees. The function owns cleanup of these objects on every exit path.

## Dependencies and integration points
This file is between the parser loop and dispatcher/interpreter: it calls `acpi_ps_parse_loop()`, `acpi_ds_call_control_method()`, `acpi_ds_restart_control_method()`, `acpi_ds_terminate_control_method()`, `acpi_ex_enter_interpreter()`/`exit`, mutex release helpers, trace hooks, parse-tree deletion, and method error reporting.

## Risks and edge cases
Nested method execution is iterative but state-heavy; return object ownership is easy to mishandle. Slack-mode implicit returns add alternate return paths. If `acpi_gbl_current_walk_list` is not restored after errors, debugger and nested execution state become corrupt. Parse-tree deletion with replacement placeholders must not detach needed AML metadata for deferred objects. Reentrancy auto-serialization only triggers for a narrow error pattern.

## Test signals
Tests should cover simple and nested method execution, methods returning values and no values, implicit-return slack mode, parse errors inside methods, method-call transfer and restart, break/continue/if/else pointer transitions, subtree deletion mode, module-level load errors, mutex release on thread exit, and pending-serialized marking for reentrant method namespace creation.
