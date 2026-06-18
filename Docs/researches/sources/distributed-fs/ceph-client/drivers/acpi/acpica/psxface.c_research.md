# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psxface.c

## Purpose
`psxface.c` is the parser external-interface layer for debug tracing, control-method execution, table execution, and method parameter reference management. It bridges namespace evaluation to the parser, dispatcher, and interpreter.

## Important APIs, types, and functions
Exports include `acpi_debug_trace()`, `acpi_ps_execute_method()`, and `acpi_ps_execute_table()`. The local helper `acpi_ps_update_parameter_list()` increments or decrements references for method parameter objects. Key types are `struct acpi_evaluate_info`, `struct acpi_walk_state`, `union acpi_parse_object`, method operand objects, and namespace nodes.

## Control flow
`acpi_debug_trace()` locks the namespace mutex and updates global trace method name, flags, debug level, and debug layer. `acpi_ps_execute_method()` checks the DSDT header, validates evaluation info, begins method execution through the dispatcher, increments references on caller-owned parameters, creates a root scope op, creates and initializes an execute-mode AML walk state, marks module-level methods, handles internal-only methods by calling their implementation directly, optionally creates a slack-mode implicit zero return, then calls `acpi_ps_parse_aml()`. Cleanup deletes the root parse tree, decrements parameter references, and returns `AE_CTRL_RETURN_VALUE` when a method produced a return object. `acpi_ps_execute_table()` similarly creates a root op and walk state for table AML, optionally pushes the load scope, enters the interpreter, parses AML, exits the interpreter, and cleans up any remaining walk state/op on early failure.

## State and persistence behavior
The file mutates global debug trace settings, method execution state, parameter object reference counts, walk state, parse tree allocations, and method return ownership in `info->return_object`. Table execution can populate or modify the namespace through dispatcher callbacks while parsing. Method execution uses dispatcher begin/terminate logic to enforce concurrency and serialized method semantics.

## Dependencies and integration points
It depends on table validation, dispatcher walk-state creation/init/delete, method execution lifecycle, parser scope creation/deletion, `acpi_ps_parse_aml()`, interpreter enter/exit, namespace scope stack push, object reference management, and global slack/debug settings. It is called from namespace evaluation paths in `nsxfeval.c` through `acpi_ns_evaluate()` and from table loading paths.

## Risks and edge cases
Parameter references must be balanced even when allocation or walk initialization fails. Internal-only method cleanup differs from normal parsed methods and must terminate dispatcher state manually. Slack-mode implicit return allocation can fail after method execution has begun. `acpi_ps_parse_aml()` deletes walk states on normal paths, so callers must not double free them. Trace globals are set under namespace mutex but are global policy, not per-thread.

## Test signals
Tests should cover debug trace configuration, normal method execution with and without return objects, parameter reference balance, method begin failure, scope-op allocation failure, walk-state allocation/init failure, internal-only methods, module-level parse flag propagation, slack implicit zero returns, table execution under a non-root node, interpreter lock pairing, and cleanup after parse errors.
