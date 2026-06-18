# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswstate.c

## Purpose
Manages dispatcher walk-state lifetime and its internal stacks: result frames, operand stack entries, per-thread walk-state lists, parser scope initialization, method argument setup, and final teardown. It is the state container foundation for namespace loading and AML method execution.

## Important APIs, Types, And Functions
- `acpi_ds_result_push`/`acpi_ds_result_pop` manage result objects across linked result frames, extending and shrinking frames via static `acpi_ds_result_stack_push`/`acpi_ds_result_stack_pop`.
- `acpi_ds_obj_stack_push`, `acpi_ds_obj_stack_pop`, and `acpi_ds_obj_stack_pop_and_delete` maintain the fixed operand stack and remove references when requested.
- `acpi_ds_create_walk_state`, `acpi_ds_push_walk_state`, `acpi_ds_pop_walk_state`, and `acpi_ds_get_current_walk_state` manage walk states on an `acpi_thread_state`.
- `acpi_ds_init_aml_walk` initializes parser AML bounds, scope, method context, arguments, starting namespace node, and callbacks.
- `acpi_ds_delete_walk_state` cleans parser scopes, control states, scope frames, result frames, and the walk object.

## Control Flow
A caller allocates a zeroed walk state, optionally pushes it onto a thread, initializes AML pointers and parser scope, then either pushes the method node as current scope and initializes method args or derives the current scope from the nearest parse op with a namespace node. Callback selection is delegated to `acpi_ds_init_callbacks`. During execution, results are pushed into frame slots of `ACPI_RESULTS_FRAME_OBJ_NUM`, new frames are allocated up to `ACPI_RESULTS_OBJ_NUM_MAX`, and popping the first slot in a frame frees that frame. Operand pop/delete paths clear stack slots and dereference operand objects on error or completion.

## State And Persistence
Persistent runtime state spans a method invocation only: AML cursor bounds, parse scopes, scope stack, result stack, operand stack, control-state list, method args/locals, owner ID, current thread linkage, and callback function pointers. Walk-state deletion owns all remaining generic state frames, but operand object references must normally be balanced by execution cleanup before deletion.

## Dependencies And Integration Points
Uses parser scope initialization/cleanup, dispatcher scope-stack and method-data helpers, callback setup from `dswload.c`, namespace attached objects for method descriptors, and utility generic state allocation. It is used by method execution, table load passes, and nested method call scheduling.

## Risks And Edge Cases
Result stack integrity checks catch mismatched `result_count` and result frames. Pointer arithmetic on null AML start is avoided for zero-length AML. Operand pop/delete indexes must correspond to how operands were pushed; otherwise references can leak or be removed from the wrong slot. `acpi_ds_pop_walk_state` intentionally leaves `next` intact as a parent indicator.

## Test Signals
Cover result stack frame growth/shrink, operand stack overflow/underflow, method invocation with all arguments, zero-length AML walks, nested method calls on one thread, cleanup after parser scope leaks, and walk-state deletion with pending control/result/scope frames.
