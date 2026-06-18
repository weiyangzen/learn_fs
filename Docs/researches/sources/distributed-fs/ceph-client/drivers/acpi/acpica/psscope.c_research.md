# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psscope.c

## Purpose
`psscope.c` manages the parser's scope stack. It tracks the current parse op, remaining argument template, remaining argument count, argument end pointer, and package end pointer while AML parsing descends into nested operations.

## Important APIs, types, and functions
Functions include `acpi_ps_get_parent_scope()`, `acpi_ps_has_completed_scope()`, `acpi_ps_init_scope()`, `acpi_ps_push_scope()`, `acpi_ps_pop_scope()`, and `acpi_ps_cleanup_scope()`. They use `struct acpi_parse_state` and `union acpi_generic_state` entries with descriptor types `ACPI_DESC_TYPE_STATE_RPSCOPE` and `ACPI_DESC_TYPE_STATE_PSCOPE`.

## Control flow
`acpi_ps_init_scope()` allocates the root parse-scope state, stores the root op, marks argument count as variable, and sets argument/package ends to the AML end. `acpi_ps_push_scope()` allocates a new scope for a current op, stores remaining args and count, captures the current package end, pushes it on `parser_state->scope`, and sets `arg_end` to package end for variable argument lists or max pointer for single fixed arguments. `acpi_ps_has_completed_scope()` reports completion when the AML pointer has reached the current argument end or the argument count has reached zero. `acpi_ps_pop_scope()` pops only if another scope is present, restores op/arg list/count/package end, and frees the scope state; at root it returns null op and zero counts. Cleanup pops and deletes all remaining scope entries.

## State and persistence behavior
The file owns transient parser scope stack state only. It allocates generic state objects from ACPICA utilities and must release every pushed state during pop or cleanup. No namespace or operand-object state is persisted here.

## Dependencies and integration points
`psloop.c`, `psobject.c`, and `psparse.c` use these helpers to descend into complex arguments, determine when an op is complete, and unwind after errors or method-call transfers. Allocation and stack operations come from `acpi_ut_create_generic_state()`, `acpi_ut_push_generic_state()`, `acpi_ut_pop_generic_state()`, and `acpi_ut_delete_generic_state()`.

## Risks and edge cases
The root scope is deliberately not popped by `acpi_ps_pop_scope()`; callers must understand the null-op root return. Variable argument scopes rely on correct `pkg_end`; corrupt AML lengths can make completion checks wrong. Allocation failure on scope push must be propagated or parsing loses its parent context. Cleanup must handle partially initialized parser states.

## Test signals
Signals include root scope initialization, nested fixed and variable argument scopes, completion by argument count and by AML pointer, package-end restoration after pop, cleanup after parse errors with multiple open scopes, allocation failure injection, and no leaks in repeated parse invocations.
