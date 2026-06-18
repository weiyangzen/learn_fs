# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psobject.c

## Purpose
`psobject.c` creates and completes parser op objects from AML. It classifies opcodes, builds named ops through namespace callbacks, appends non-named ops to parent scopes, tracks target operands, and handles scope cleanup for normal and exceptional parse statuses.

## Important APIs, types, and functions
The local helper `acpi_ps_get_aml_opcode()` peeks and classifies the next AML opcode. Exported functions are `acpi_ps_build_named_op()`, `acpi_ps_create_op()`, `acpi_ps_complete_op()`, and `acpi_ps_complete_final_op()`. They operate on `struct acpi_walk_state`, `union acpi_parse_object`, opcode metadata, parse scopes, namespace nodes, and dispatcher callback results.

## Control flow
Opcode classification recognizes valid normal opcodes, ASCII/prefix bytes that start a namestring, and unknown opcodes. Unknown opcodes are skipped in normal ACPICA parsing and can abort disassembly builds. Named-op construction first parses arguments before the name operand, calls the descending callback to perform namespace lookup or insertion, handles callback parse-state control, and appends previously parsed unnamed arguments to the returned named op. Non-named creation allocates the op, marks deferred create/bank fields with AML start data, appends it to the parent scope, marks target operands when the parent opcode expects a target, and invokes the descending callback.

Completion decrements the containing scope argument count, calls `acpi_ps_complete_this_op()`, then interprets statuses. Transfers preserve previous op state for method calls. End, break, continue, terminate, and generic failures pop scopes, run ascending callbacks as needed, delete parse subtrees, remove namespace nodes for failed region/data-region creation, and tolerate module-level execution errors. Final completion drains every open scope and gives the first meaningful failure priority.

## State and persistence behavior
The file allocates parse ops, links them into parent argument lists, writes node pointers from namespace callbacks, updates `walk_state->prev_op`, `prev_arg_types`, `method_call_op`, and parser-scope state, and deletes parse subtrees depending on parse flags. Failed region/data-region ops can remove namespace nodes that were already created.

## Dependencies and integration points
It depends on opcode tables, argument parsing, parse tree utilities, namespace callbacks supplied by the dispatcher, `acpi_ps_next_parse_state()`, `acpi_ps_complete_this_op()`, namespace deletion helpers, and ASL compiler/disassembler comment metadata transfer.

## Risks and edge cases
The distinction between namestring-as-opcode and real opcode is central to AML parsing correctness. Named-op construction has to keep an unnamed temporary op only long enough to parse pre-name arguments, then transfer metadata safely. Error paths must not leave namespace nodes for failed region declarations. Break/continue unwinding assumes a while op exists on the parse stack.

## Test signals
Tests should cover normal and extended opcodes, bare namestring conversion, unknown opcode skip behavior, named-object creation, external-op disassembler recovery, target flag assignment for store/create/increment/decrement cases, failed namespace callback cleanup, method-call transfer status, break/continue scope unwinding, terminate cleanup, and final-op completion with multiple nested open scopes.
