# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswexec.c

## Purpose
Implements dispatcher callbacks for executing AML control methods. It drives the parse-tree walk, handles control predicates and control-flow state, builds operands, dispatches executable opcodes to interpreter handlers, creates method-time namespace objects, and transfers execution into called methods.

## Important APIs, Types, And Functions
- `acpi_gbl_op_type_dispatch` maps opcode type slots to interpreter execution helpers such as `acpi_ex_opcode_2A_1T_1R`.
- `acpi_ds_get_predicate_value` pops or creates a predicate operand, converts it to integer, updates control state, handles implicit return, and maps false predicates to `AE_CTRL_FALSE`.
- `acpi_ds_exec_begin_op` is the descending callback for method execution and method-time namespace loading.
- `acpi_ds_exec_end_op` is the ascending callback that performs most operand creation, operand resolution, interpreter dispatch, method-call transfer, create-field evaluation, named object completion, result-stack handling, and error mapping.

## Control Flow
On descent, a missing parse op is created through load-pass-2 logic, scopes opened during parsing are balanced, conditional control states move into predicate execution, and method-local named objects are entered into the namespace. On ascent, execution resets operand/result scratch fields, gives the debugger a single-step hook, then switches on opcode class and type. Executable opcodes build operands, resolve them unless flagged otherwise, dispatch via the type table, clear operands, and push returned results. Method calls build and resolve callee arguments, then return `AE_CTRL_TRANSFER` so the walk loop preempts the current method. Create and named op types delegate to load-pass-2 and operand-evaluation helpers for fields, buffers, packages, regions, bank fields, and data table regions.

## State And Persistence
State is concentrated in `acpi_walk_state`: `control_state`, `op`, `opcode`, `op_info`, `operands`, `result_obj`, result stack, method node, and scope stack. Named objects created during method execution are temporary unless module-level execution rules apply. Predicate results are removed after evaluation, and normal opcode results are deleted if the parent will not consume them.

## Dependencies And Integration Points
Integrates the dispatcher with the parser walk engine, interpreter opcode handlers, namespace load pass 2, control-op helpers, debugger hooks, region/field operand evaluators, method invocation machinery, and exception handling through `acpi_ds_method_error`. ACPI_EXEC_APP builds also integrate namespace initialization-file support.

## Risks And Edge Cases
The method call transfer path must not clear operand counts because callee setup consumes them. Predicate conversion must handle implicit integer conversion and 32-bit table truncation. Method references inside package declarations must not be invoked. Named object creation inside methods must distinguish Scope from true definitions. Error cleanup must avoid leaving operands or results with extra references.

## Test Signals
Signals include correct `If`/`While` predicate false handling, nested method calls receiving resolved arguments, package method references not executing, create-field and region operands evaluated at execution time, store-to-self uninitialized local treated as a no-op, and result stack cleanup for unused top-level expression results.
