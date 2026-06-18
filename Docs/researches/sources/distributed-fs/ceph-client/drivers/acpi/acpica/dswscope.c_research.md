# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswscope.c

## Purpose
Provides the dispatcher scope stack primitives used by namespace load and method execution walks. The scope stack tracks the current namespace node and object type as AML parsing descends into and ascends out of scope-opening objects.

## Important APIs, Types, And Functions
- `acpi_ds_scope_stack_clear` drains all scope frames from a walk state and frees their generic state objects.
- `acpi_ds_scope_stack_push` validates a node, allocates an `ACPI_DESC_TYPE_STATE_WSCOPE` generic state, records node/type, increments `scope_depth`, and pushes it onto `walk_state->scope_info`.
- `acpi_ds_scope_stack_pop` pops the top generic state, decrements `scope_depth`, logs the new scope, and frees the frame.

## Control Flow
Load and execute callbacks push a scope when encountering Scope, Device, Method, Processor, PowerResource, ThermalZone, or other scope-opening object types. Their ascending callbacks pop when the object is complete. Clearing is used during teardown to release any remaining scope states. Push/pop functions do not alter namespace nodes; they maintain walker-local context for subsequent namespace lookup.

## State And Persistence
All state is transient per `acpi_walk_state`: `scope_info` is a linked stack of `union acpi_generic_state` objects and `scope_depth` is a diagnostic/depth counter. Frames contain the namespace node and type only; no namespace references are acquired.

## Dependencies And Integration Points
Used by `dswload.c`, `dswload2.c`, `dswexec.c`, and `dswstate.c`. It depends on ACPI generic state allocation/free utilities and namespace node naming/type helpers for diagnostics.

## Risks And Edge Cases
Pop underflow indicates an unbalanced parser callback path. Push accepts invalid object types after warning, so callers must decide whether a target type is semantically valid. Because clear pops all frames, callers must avoid using it while later code expects a root/current scope frame.

## Test Signals
Nested scopes should produce balanced depth transitions, invalid Scope targets should fail before push in caller logic, early errors should not leak scope frames after walk-state deletion, and namespace lookups inside nested devices/methods should resolve relative to the pushed scope.
