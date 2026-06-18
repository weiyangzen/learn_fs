# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbmethod.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbmethod.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbmethod.c

### Purpose
`dbmethod.c` implements AML debugger commands that operate on control methods: setting breakpoints, modifying live method arguments/locals or integer namespace nodes, disassembling method AML when the disassembler is enabled, and batch-evaluating ACPI objects from namespace walks. It is debugger-facing code, but it drives real ACPICA interpreter evaluation paths.

### Important APIs, Types, And Functions
Public entry points include `acpi_db_set_method_breakpoint`, `acpi_db_set_method_call_breakpoint`, `acpi_db_set_method_data`, `acpi_db_disassemble_aml`, `acpi_db_disassemble_method`, `acpi_db_evaluate_predefined_names`, and `acpi_db_evaluate_all`. Internal callbacks `acpi_db_walk_for_execute` and `acpi_db_walk_for_execute_all` feed namespace walk results to `acpi_db_evaluate_object`. The code uses `struct acpi_walk_state`, `union acpi_parse_object`, `struct acpi_namespace_node`, `struct acpi_object_list`, and `union acpi_object`.

### Control Flow
Breakpoint commands validate that a method/op is currently executing, convert user input with `strtoul`, and update `walk_state->user_breakpoint` or the global `acpi_gbl_step_to_next_call`. `acpi_db_set_method_data` selects Arg, Local, or namespace-node mode, creates an integer operand object, and stores it through `acpi_ds_store_object_to_local` for live stack slots. Disassembly builds a temporary parse tree and walk state, parses method AML, optionally parses deferred ops, prints ASL, then deletes temporary namespace objects by subtree and owner id. Batch evaluation walks the namespace, filters by predefined-name metadata or nameseg match, then calls `acpi_evaluate_object`.

### State, Persistence, And Dependencies
The file mutates debugger/interpreter state: `walk_state->user_breakpoint`, `acpi_gbl_step_to_next_call`, `acpi_gbl_method_executing`, temporary method owner IDs, and live Arg/Local objects. It depends on namespace lookup, parser/disassembler, predefined-name tables, object info, evaluator APIs, and debugger output helpers. Temporary disassembly state is explicitly deleted after use.

### Integration Points
`dbxface.c` consumes the breakpoint globals during single-step execution. `dsmthdat.c` provides Arg/Local storage semantics. `dbutils.c` prints returned external objects, while namespace and predefined helpers from `acnamesp`/`acpredef` drive the batch commands.

### Risks
Debugger writes can change live method execution and namespace integer values. `acpi_db_set_method_data` uses hex parsing and only supports integer replacement, so malformed input or wrong type selection can produce misleading state. Batch evaluation executes firmware methods with default integer argument `1`, which can trigger side effects. Disassembly must release owner IDs and temporary namespace entries or later lookups can observe stale definitions.

### Test Signals
Useful checks are breakpoint hits at expected AML offsets, step-to-call stopping on method-call opcodes, successful Local/Arg mutation visible in `dbobject` dumps, disassembly cleanup leaving no owner-owned namespace residue, and `Evaluate`/`All` command output showing status plus correctly dumped return objects without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbmethod.c -->
