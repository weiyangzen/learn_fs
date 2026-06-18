# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psloop.c

## Purpose
`psloop.c` contains the main iterative AML parse loop. It builds parse trees, drives dispatcher callbacks, handles nested method-call transfers without C recursion, skips deferred regions where needed, and unwinds scopes after normal and exceptional control flow.

## Important APIs, types, and functions
The local helper `acpi_ps_get_arguments()` fills arguments for one parse op. The exported parser-loop function is `acpi_ps_parse_loop()`. It uses `struct acpi_walk_state`, `struct acpi_parse_state`, parser scope helpers, object creation/completion helpers, dispatcher callbacks, control-state helpers, and status codes such as `AE_CTRL_TRANSFER`, `AE_CTRL_PENDING`, `AE_CTRL_DEPTH`, and `AE_CTRL_TERMINATE`.

## Control flow
`acpi_ps_parse_loop()` validates that a descending callback exists, handles restart of a preempted method by restoring a previous op or popping completed scope, then loops while AML remains or an op is pending. When no op is active it calls `acpi_ps_create_op()` and handles parse-continue, parse-pending, terminate, module-level toleration, and scope-op skip recovery. For each op it resets argument count, calls `acpi_ps_get_arguments()` when template argument bits remain, pushes scope if complex arguments are pending, or completes the op when all arguments are known. Named region/create/bank-field lengths are finalized after body parsing. Ascending callbacks run at completion, and `acpi_ps_next_parse_state()` interprets dispatcher control statuses before `acpi_ps_complete_op()` unwinds or deletes parse subtrees.

`acpi_ps_get_arguments()` directly decodes literal ops and namepath ops, otherwise loops through fixed template arguments using `acpi_ps_get_next_arg()`. It defers method bodies, and in early load passes can defer `Name(Buffer/Package)` contents by storing AML data and length and skipping to package end. While ops record package end in the control state.

## State and persistence behavior
The parser mutates `walk_state`, `parser_state->aml`, parse scopes, control state, and parse tree nodes. Depending on parse flags, completed subtrees can be retained or deleted. Deferred methods, buffers, packages, operation regions, create fields, and bank fields store AML start and length for later execution or object creation.

## Dependencies and integration points
The loop depends on opcode metadata from `psopinfo.c`/`psopcode.c`, argument decoding from `psargs.c`, object lifecycle from `psobject.c`/`pswalk.c`, dispatcher callbacks from `acdispat`, interpreter trace hooks, and namespace scope rules. It is invoked by `acpi_ps_parse_aml()` in `psparse.c`.

## Risks and edge cases
Recovery paths for malformed AML must advance the AML pointer correctly or the parser can loop forever or skip valid AML. Module-level execution intentionally ignores some load errors to keep loading later objects. If/while parse failure skips bodies and optional else blocks, which is necessary but can hide additional errors. Scope push/pop and `arg_count` bookkeeping are fragile because one missed decrement corrupts later parsing.

## Test signals
Signals include parsing normal methods, nested method calls with restart, deferred method/buffer/package bodies in load pass 1/2, operation region and create-field length capture, malformed opcode recovery, if/while predicate failures and skipped else blocks, module-level error tolerance, scope push/pop balance, and parse tree deletion modes under memory-debug builds.
