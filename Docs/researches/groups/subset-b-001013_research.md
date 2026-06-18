# subset-b-001013 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c

### Purpose
`dbnames.c` implements AML debugger commands for inspecting and validating the ACPI namespace. It changes the debugger current scope, dumps namespace subtrees and full paths, searches names with wildcard support, reports object counts and field values, checks predefined-name compliance, performs namespace integrity checks, finds direct references, and reports bus/device information around `_PRT` providers.

### Important APIs, Types, And Functions
Entry points include `acpi_db_set_scope`, `acpi_db_dump_namespace`, `acpi_db_dump_namespace_paths`, `acpi_db_dump_namespace_by_owner`, `acpi_db_find_name_in_namespace`, `acpi_db_check_predefined_names`, `acpi_db_display_objects`, `acpi_db_display_fields`, `acpi_db_check_integrity`, `acpi_db_find_references`, and `acpi_db_get_bus_info`. Static walk callbacks implement matching, predefined-name validation, object counting, field display, integrity validation, reference finding, and bus reporting.

### Control Flow
Most commands normalize or resolve an input path, then call `acpi_walk_namespace`/`acpi_ns_dump_*` with a focused callback. Scope setting validates either root-relative or current-scope-relative paths before appending to `acpi_gbl_db_scope_buf`. Name search uppercases and pads to a four-character nameseg, supports `?` wildcards, then prints full path plus summary object data. Object display either counts all types or walks only the requested type. Field display filters region fields by address-space ID and evaluates each matching field for readable output.

### State, Persistence, And Dependencies
Persistent debugger state is limited to `acpi_gbl_db_scope_buf`, `acpi_gbl_db_scope_node`, and output redirection flags. The code reads live namespace nodes, attached objects, object info, predefined method metadata, region field descriptors, and device info returned by `acpi_get_object_info`. It depends on namespace locks handled by the walker/evaluator APIs.

### Integration Points
The file integrates with `dbutils.c` for argument matching, namestring preparation, and output routing. It uses predefined-name validation from `acpredef`, interpreter field evaluation via `acpi_evaluate_object`, and namespace dumping/integrity helpers from `acnamesp`.

### Risks
Field display and bus reporting can execute firmware objects, so debugger inspection may have side effects. Integrity and reference searches only check direct node/object relationships, not every nested subobject. Scope buffer concatenation is guarded, but a failed relative scope update leaves the prior scope intact. Field walks assume valid field object chains, so corrupt namespace state can still produce null dereference risk if invariants are already broken.

### Test Signals
Signals include correct namespace dumps from root and subtrees, wildcard name matches, predefined-name counts matching firmware contents, object-type summaries matching raw namespace walks, field display only for the requested address space, integrity checks reporting invalid descriptors/names, and bus info listing devices/processors with `_PRT` plus `_ADR`, `_HID`, `_UID`, and `_CID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbobject.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbobject.c

### Purpose
`dbobject.c` provides compact debugger decoding for internal ACPICA operand objects, namespace nodes, method locals, and method arguments. It is primarily diagnostic support used after method errors and during interactive debugging.

### Important APIs, Types, And Functions
Public functions are `acpi_db_dump_method_info`, `acpi_db_decode_internal_object`, `acpi_db_display_internal_object`, `acpi_db_decode_locals`, and `acpi_db_decode_arguments`. `acpi_db_decode_node` is the local namespace-node formatter. The implementation understands `union acpi_operand_object`, `struct acpi_namespace_node`, `struct acpi_walk_state`, method pseudo-nodes, reference classes, and descriptor types.

### Control Flow
`acpi_db_dump_method_info` ignores module-level code, control exceptions, deferred opcode execution, and non-method compiler folding contexts; otherwise it prints locals and arguments. Object display first validates descriptor type, then dispatches between parser, named, operand, and invalid descriptors. Local-reference operands are resolved against the active walk state's local or argument arrays when possible. Index references display buffer-field or package target data, and `RefOf` references handle both namespace-node and operand-object targets.

### State, Persistence, And Dependencies
The file is read-only with respect to interpreter state; it prints values without changing reference counts or object storage. It depends on live method walk frames, pseudo-namespace nodes created by `dsmthdat.c`, namespace attached-object lookups, and ACPICA descriptor/type-name helpers.

### Integration Points
`dsmethod.c` calls the method-info dump on failed method execution when the debugger is enabled. `dbmethod.c` uses `acpi_db_display_internal_object` after setting locals or args. `dbutils.c` uses the same display path for object references in external object dumps.

### Risks
This code is diagnostic but walks potentially corrupt structures after failures, so descriptor validation is critical. It intentionally truncates strings and buffers for display, which is useful but can hide data differences. Reference display depends on a valid `walk_state`; without one, local/arg references cannot be dereferenced.

### Test Signals
Good signals are clear output for initialized and uninitialized locals/args, correct formatting of integers/strings/buffers, robust handling of invalid descriptors, correct display of `RefOf`, `Index`, `Arg`, and `Local` references, and no output for module-level code where locals/args do not exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c

### Purpose
`dbstats.c` implements debugger statistics commands for ACPICA allocation/cache state, namespace object counts, miscellaneous parser/namespace/mutex counters, internal structure sizes, and optional stack-use data.

### Important APIs, Types, And Functions
The main entry point is `acpi_db_display_statistics`. Internal helpers are `acpi_db_count_namespace_objects`, `acpi_db_classify_one_object`, `acpi_db_enumerate_object`, and conditionally `acpi_db_list_info`. It uses `struct acpi_memory_list`, global node/object counters, namespace nodes, operand objects, and compile-time feature gates such as `ACPI_DBG_TRACK_ALLOCATIONS`, `ACPI_USE_LOCAL_CACHE`, and `ACPI_DEBUG_OUTPUT`.

### Control Flow
The command uppercases the subcommand, maps it through `acpi_db_match_argument`, and selects a display branch. Object statistics reset global count arrays, walk the namespace, count each node type, and recursively enumerate attached objects plus package elements and notify/handler subobjects. Memory statistics print cache/allocation list data when enabled. Size statistics print `sizeof` values for all major ACPICA internal structures.

### State, Persistence, And Dependencies
The command mutates only transient global statistic arrays before printing. It reads ACPICA allocation trackers, local caches, mutex use counters, parser/namespace lookup counters, and stack watermark globals. It depends on namespace walking without modifying namespace contents.

### Integration Points
The debugger command parser calls `acpi_db_display_statistics`; the implementation relies on `dbutils.c` for subcommand matching and on namespace/object APIs for classification. It reflects state maintained by parser, namespace, mutex, and memory-management subsystems.

### Risks
Recursive enumeration of packages is bounded only by object graph shape and assumes sane package contents. Compile-time feature gates mean some subcommands silently produce little or no data depending on build configuration. The count reset loop uses the local ACPICA type bounds, so changes to type constants must stay aligned with array sizes.

### Test Signals
Signals include `OBJECTS` totals matching namespace walk size, package and handler subobjects included in object counts, `MEMORY` output appearing only when allocation/cache tracking is configured, `MISC` showing nonzero parser/namespace/mutex counters after activity, and `SIZES` matching the target ABI/build configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c

### Purpose
`dbtest.c` implements invasive debugger self-tests for namespace data objects and predefined-name evaluation. It installs helper AML methods that read and write arbitrary namespace objects through the interpreter so the tests exercise normal AML semantics instead of directly poking C structures.

### Important APIs, Types, And Functions
The command entry is `acpi_db_execute_test`, with subcommands `OBJECTS` and `PREDEFINED`. Key helpers include `acpi_db_test_all_objects`, `acpi_db_test_one_object`, typed tests for integer/buffer/string/package/field objects, `acpi_db_read_from_object`, `acpi_db_write_to_object`, `acpi_db_evaluate_all_predefined_names`, and `acpi_db_evaluate_one_predefined_name`. Static AML byte arrays define `\_T98` read and `\_T99` write helper methods.

### Control Flow
`OBJECTS` installs the read/write methods once, caches their handles, walks the namespace, maps supported object kinds to integer/string/buffer/package/field test families, reads original values, writes a synthetic value, reads back for comparison, restores the original, and verifies restoration. Field-unit tests directly acquire interpreter and namespace mutexes, read the field, write the same value back, then release locks. `PREDEFINED` walks predefined names, constructs default arguments based on predefined metadata, evaluates each object, and optionally stops at a count limit.

### State, Persistence, And Dependencies
The file persists `read_handle` and `write_handle` and installs debugger SSDT methods into the namespace. It temporarily mutates namespace data objects, field units, and operation-region-backed state. It depends on public method installation/evaluation APIs, namespace walking, predefined metadata, field I/O helpers, and interpreter/namespace mutexes.

### Integration Points
The tests validate object behavior implemented across namespace, interpreter, region, and field subsystems. They also overlap with `dbmethod.c` batch predefined evaluation but use spec-derived argument types instead of only integer defaults.

### Risks
This is intentionally destructive if restoration fails or firmware has side-effectful fields. Writing `0xFF` buffers, replacement strings, or max-width integers to fields can affect hardware-backed system memory, I/O, or PCI config regions. Unsupported spaces are skipped, but supported spaces still need care. Helper AML methods remain installed for the debugger session.

### Test Signals
Expected output is per-object type/name, length/value summaries, no mismatch messages after write/read/restore, field-unit tests limited to supported address spaces, successful helper method installation, predefined-name evaluations returning statuses rather than crashing, and no unreleased returned external-object buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbutils.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbutils.c

### Purpose
`dbutils.c` contains small AML debugger utilities shared by command modules: command argument matching, output-destination selection, external object dumping, debugger path normalization and lookup, hex string formatting, and obsolete second-pass parse/buffer-dump helpers when enabled.

### Important APIs, Types, And Functions
Important functions are `acpi_db_match_argument`, `acpi_db_set_output_destination`, `acpi_db_dump_external_object`, `acpi_db_prep_namestring`, `acpi_db_local_ns_lookup`, and `acpi_db_uint32_to_hex_string`. Conditional obsolete functions include `acpi_db_second_pass_parse` and `acpi_db_dump_buffer`.

### Control Flow
Argument matching treats a user token as a prefix of a known argument name and returns the table index. Output destination updates `acpi_gbl_db_output_flags` and switches `acpi_dbg_level` between file and console debug levels. External object dumping recursively prints packages and formats integers, strings, buffers, references, processor, and power-resource objects. Namestring preparation uppercases input, converts a leading slash to root prefix, then converts path separators after the root to dots for namespace internalization.

### State, Persistence, And Dependencies
The file mutates debugger output globals and may modify caller-provided path strings in place. Namespace lookup allocates and frees internalized path buffers. External object dumping is read-only but recurses through returned package buffers owned by the caller. Obsolete parse helpers create walk states and adjust parse offsets.

### Integration Points
Almost every `db*` file uses command matching, output routing, object dumping, or namespace lookup from this file. It depends on namespace internalization/lookup, ACPICA debug levels, string printing, buffer dump helpers, parser and dispatcher functions for obsolete support.

### Risks
Prefix matching can make abbreviated commands ambiguous if command tables are reordered or extended. `acpi_db_prep_namestring` edits input strings, so callers must not pass string literals unless mutable storage is guaranteed. External package dumping can be deep if firmware returns nested packages. `acpi_db_uint32_to_hex_string` requires a sufficiently large caller buffer.

### Test Signals
Signals include correct abbreviated command resolution, output redirection changing debug verbosity as expected, recursive object dumps for mixed packages, path lookups accepting `/`, `\`, and dotted forms, hex formatting of zero and nonzero values, and no leaks from allocated namespace path buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c

### Purpose
`dbxface.c` is the external interface between the AML interpreter and the AML debugger. It initializes/terminates debugger state, manages single-step and breakpoint entry into the command loop, filters debugger handling to the configured thread, and exports debugger setup symbols.

### Important APIs, Types, And Functions
Public functions include `acpi_db_signal_break_point`, `acpi_db_single_step`, `acpi_initialize_debugger`, `acpi_terminate_debugger`, and `acpi_set_debugger_thread_id`. Static helpers are `acpi_db_start_command` and, with the disassembler, `acpi_db_get_display_op`. The code uses parse ops, walk states, debugger globals, OSL debugger hooks, and interpreter enter/exit wrappers.

### Control Flow
Breakpoint opcode handling sets `acpi_gbl_cm_single_step` for the debugger thread. `acpi_db_single_step` first handles abort requests, method/user breakpoints, opcode filtering, optional disassembly/logging, step-to-call semantics, and step-over behavior for method calls. When it must stop, it exits the interpreter, runs the command loop until dispatch no longer returns `AE_CTRL_TRUE`, then re-enters the interpreter. Initialization allocates the debugger buffer, resets scope/output options, and optionally starts a separate debugger execution thread.

### State, Persistence, And Dependencies
Persistent state includes `acpi_gbl_db_buffer`, output flags, debug levels, scope state, terminate flags, debugger thread id, single-step flags, and debugger-thread termination flags. The file depends on OSL debugger synchronization (`acpi_os_notify_command_complete`, `acpi_os_wait_command_ready`, `acpi_os_initialize_debugger`), command dispatch, disassembler support, and interpreter lock transitions.

### Integration Points
`dscontrol.c` calls `acpi_db_signal_break_point` for AML breakpoint opcodes. `dbmethod.c` writes breakpoint/step globals that `acpi_db_single_step` consumes. `acdebug` command dispatch implements the interactive commands.

### Risks
Entering the command loop while interpreter state is paused is sensitive to locking; comments note namespace locking concerns. Thread filtering is required in kernel-style builds. Step-over uses a synthetic nonzero method breakpoint and must not collide with user breakpoints. Multi-threaded debugger shutdown spins until worker threads terminate.

### Test Signals
Signals include clean initialization/termination, debugger buffer allocation/free, single-step stopping only on the configured thread, AML breakpoint opcodes producing `ACPI_SIGNAL_BREAKPOINT`, step-to-call stopping at method calls, step-over resuming after nested methods, and no interpreter lock imbalance around command dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsargs.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsargs.c

### Purpose
`dsargs.c` performs late evaluation of dynamic AML arguments for static namespace objects such as operation regions, buffers, packages, buffer fields, and bank fields. These objects can be installed during load with AML operands deferred until first use or initialization.

### Important APIs, Types, And Functions
Public functions are `acpi_ds_get_buffer_field_arguments`, `acpi_ds_get_bank_field_arguments`, `acpi_ds_get_buffer_arguments`, `acpi_ds_get_package_arguments`, and `acpi_ds_get_region_arguments`. The central helper `acpi_ds_execute_arguments` creates temporary parse roots and walk states for both load-pass parsing and execute-mode evaluation.

### Control Flow
Each public function first checks `AOPOBJ_DATA_VALID`; if set, no work is needed. Otherwise it retrieves the namespace node and saved AML pointer/length from the object or secondary extra descriptor, logs the initialization path, and calls `acpi_ds_execute_arguments`. That helper parses the deferred AML once in load mode with `ACPI_PARSE_DEFERRED_OP`, deletes that tree, then allocates a second eval subtree op and executes the same AML in execute mode. Region and bank-field paths add initialized address ranges after successful evaluation.

### State, Persistence, And Dependencies
The code consumes saved AML spans and secondary descriptors created by field/object builders. It updates underlying objects indirectly during deferred execution and persists address-range tracking through `acpi_ut_add_address_range`. It depends on parser allocation/deletion, walk-state creation/initialization, namespace nodes, dispatcher callbacks, and object flags.

### Integration Points
`dsfield.c` and `dsobject.c` create deferred objects with AML locations. `dsopcode.c` evaluates the concrete operands and sets data-valid flags. Event/address-range code uses the ranges added for initialized regions and bank fields.

### Risks
Incorrect AML start/length or scope node values cause deferred evaluation in the wrong namespace. Re-running initialization must be prevented by `AOPOBJ_DATA_VALID`. Cleanup paths must delete parse trees even after partial walk-state setup. Address-range registration after bank-field initialization uses region fields from the initialized object and must stay aligned with object layout.

### Test Signals
Signals include first-use initialization of buffers/packages/regions/fields, repeated calls returning immediately after data-valid, correct address/length registration for operation regions, successful bank-value evaluation, and no leaked parse trees or walk states on parse/evaluation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsargs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dscontrol.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dscontrol.c

### Purpose
`dscontrol.c` implements dispatcher handling for AML control opcodes: `If`, `Else`, `While`, `Return`, `Noop`, `BreakPoint`, `Break`, and `Continue`. It manages control-state stack entries and communicates loop/return control back to the parser/interpreter through ACPICA control status codes.

### Important APIs, Types, And Functions
The two entry points are `acpi_ds_exec_begin_control_op` and `acpi_ds_exec_end_control_op`. They operate on `struct acpi_walk_state`, `union acpi_parse_object`, and `union acpi_generic_state` control states. They call operand creation/resolution helpers, implicit-return cleanup, debugger breakpoint signaling, and OSL signal hooks.

### Control Flow
Begin handling pushes a control state for new `If`/`While` predicates, reuses the existing `While` state for another iteration, records predicate AML start/package end, and sets a loop timeout. `Else` begin returns `AE_CTRL_TRUE` when the prior predicate was true so the parser skips the else body. End handling records `If` predicate result, pops completed states, loops back on true `While` predicates via `AE_CTRL_PENDING`, times out long loops, resolves explicit return values, stores them in `walk_state->return_desc`, and terminates methods with `AE_CTRL_TERMINATE`.

### State, Persistence, And Dependencies
State lives in the walk state's control stack, `last_predicate`, `aml_last_while`, result stack, return descriptor, and operand stack. Loop timeout uses `acpi_gbl_max_loop_iterations` converted to timer ticks. It depends on interpreter operand resolution and reference ownership rules.

### Integration Points
Parser walk code consumes `AE_CTRL_PENDING`, `AE_CTRL_BREAK`, `AE_CTRL_CONTINUE`, and `AE_CTRL_TERMINATE`. `dsmethod.c` later returns `walk_state->return_desc` to callers. `dbxface.c` handles breakpoint signaling triggered here.

### Risks
Control-state stack corruption breaks nested conditionals/loops. Return must resolve local/arg references before frame teardown except allowed `Index` references. Loop timeout is a safety valve for firmware loops that wait forever. Break/continue must pop intermediate control states until the nearest while or report `AE_AML_NO_WHILE`.

### Test Signals
Signals include correct if/else predicate skipping, nested while control-stack behavior, loop timeout on nonterminating AML, explicit return overriding implicit return, break/continue targeting the nearest loop, and breakpoint opcodes entering debugger/OSL signal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dscontrol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c

### Purpose
`dsdebug.c` provides dispatcher-side debug printing for failed method execution. It reports the exception, current method path, active method-call stack, and optionally the failed ASL statement when disassembler support is compiled in.

### Important APIs, Types, And Functions
The exported function is `acpi_ds_dump_method_stack`; under debug/debugger builds it uses static `acpi_ds_print_node_pathname`. A no-op implementation is compiled when neither debug output nor debugger support is enabled.

### Control Flow
The dump routine ignores ACPICA control exceptions and deferred opcode subtrees. It also returns when no thread state exists, such as compiler constant folding. Otherwise it prints the exception and current method path, walks `thread->walk_state_list`, stops method tracing for each method descriptor, displays the current failed opcode by temporarily severing `op->common.next`, and labels older stack entries as callers of the previous method.

### State, Persistence, And Dependencies
The function is diagnostic and only transiently modifies `op->common.next`, restoring it before returning. It depends on walk-state linkage, method descriptors, namespace pathname allocation, optional disassembler support, and tracing hooks.

### Integration Points
`dsmethod.c` calls this after method errors and before optional debugger local/argument dumps. It complements `dbobject.c` by showing call stack and failed statement rather than frame variables.

### Risks
Because it runs after errors, it must tolerate partial method state and null nodes. The temporary parse-op link modification must always be restored to avoid corrupting parse traversal. Without disassembler support, diagnostics are less specific.

### Test Signals
Useful checks are no output for control exceptions, clear stack output for nested method failures, correct path allocation/free behavior, failed opcode display when disassembler is enabled, and a no-op build result when debug output is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsfield.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsfield.c

### Purpose
`dsfield.c` creates namespace nodes and operand objects for AML field declarations: buffer fields, operation-region fields, bank fields, and index fields. It also processes field-list terms such as reserved fields, `AccessAs`, extended access attributes, and `Connection`.

### Important APIs, Types, And Functions
Entry points include `acpi_ds_create_buffer_field`, `acpi_ds_create_field`, `acpi_ds_init_field_objects`, `acpi_ds_create_bank_field`, and `acpi_ds_create_index_field`. Static `acpi_ds_get_field_names` walks field elements and calls `acpi_ex_prep_field_value`. Under ASL compiler builds, `acpi_ds_create_external_region` creates externals for disassembly.

### Control Flow
Buffer field creation finds the result name operand, creates or reuses a namespace node, creates a buffer-field object, saves AML start/length in the secondary descriptor for later operand evaluation, attaches the object, and drops the local reference. Field initialization first enters all named fields into the namespace during load pass. Creation of actual field objects resolves region/register nodes, initializes `struct acpi_create_field_info`, walks remaining field-list entries, updates bit positions, applies access/connection state to following fields, and creates attached field objects when absent.

### State, Persistence, And Dependencies
The file persists namespace nodes, attached field objects, AML spans for deferred buffer/bank evaluation, field bit offsets, access flags, connection resource pointers, and for PCC regions an internal buffer allocated to region length. It depends on namespace lookup flags, parser arg layout, interpreter field preparation, and optional ACPI execution app initialization data.

### Integration Points
`dsopcode.c` later evaluates buffer-field and bank-field operands. `dsargs.c` performs late execution for deferred fields. `acpiexec` may initialize field values from init files. Namespace deletion in `dsmethod.c` cleans temporary method-created fields.

### Risks
Bit-position arithmetic is guarded against 32-bit overflow; regressions here can create malformed fields. Lookup flags differ between load/execution/disassembly and method/module-level contexts. Connection state applies to subsequent fields, so failure to reset resource fields changes later field semantics. PCC buffer allocation depends on a valid initialized region length.

### Test Signals
Signals include correct namespace entries for all named fields, reserved fields advancing bit position, access/connection changes applying to following fields, duplicate field handling in disassembly/acpiexec modes, bank/index/register lookup failures reported with namespace paths, and buffer-field deferred AML later becoming data-valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsfield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsinit.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsinit.c

### Purpose
`dsinit.c` performs post-load initialization over namespace objects owned by a specific ACPI table. It initializes operation regions and gathers method/device/region counts, including optional auto-serialization of unsafe-looking methods.

### Important APIs, Types, And Functions
The public function is `acpi_ds_initialize_objects`; the namespace-walk callback is `acpi_ds_init_one_object`. It uses `struct acpi_init_walk_info`, table owner IDs, namespace nodes, operand objects, and table headers.

### Control Flow
Initialization obtains the table owner ID, zeroes the walk info, walks from the supplied start node with `acpi_ns_walk_namespace`, and skips nodes not owned by the target table. Region nodes call `acpi_ds_initialize_region`. Method nodes increment counters, inspect attached objects, skip already serialized methods, and optionally call `acpi_ds_auto_serialize_method`; device nodes only update counts. After the walk, it fetches table metadata and emits a summary.

### State, Persistence, And Dependencies
The function mutates operation-region initialization state through the event subsystem and may set method serialization flags through `dsmethod.c`. It reads table owner IDs and table headers from `actables`. Count state is local to the walk.

### Integration Points
Called after AML table load to transition namespace declarations from parsed to initialized. It bridges namespace loading with region event initialization and method auto-serialization policy.

### Risks
Errors during one object's initialization are logged but do not abort the walk, so later consumers may encounter partially initialized regions. Owner-ID filtering must be correct or it can initialize objects from the wrong table. Auto-serialization scans method AML and changes concurrency behavior, intentionally trading parallelism for safety.

### Test Signals
Signals include accurate summary counts for table-owned objects, region initialization errors logged with node names, serialized/nonserialized/converted method counts matching method flags, DSDT-specific initialization banner output, and no namespace reader-lock deadlock because the internal namespace walker is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c

### Purpose
`dsmethod.c` manages control-method lifecycle: auto-serialization scanning, method error handling, serialized method mutex acquisition, nested method invocation, restart after callee return, and teardown of method-created namespace state.

### Important APIs, Types, And Functions
Entry points include `acpi_ds_auto_serialize_method`, `acpi_ds_method_error`, `acpi_ds_begin_method_execution`, `acpi_ds_call_control_method`, `acpi_ds_restart_control_method`, and `acpi_ds_terminate_control_method`. Static helpers are `acpi_ds_detect_named_opcodes` and `acpi_ds_create_method_mutex`.

### Control Flow
Auto-serialization creates a temporary parse root/walk state, scans method AML, and marks methods serialized when named/create/field opcodes appear. Begin execution starts trace, enforces reentrancy limit, lazily creates/acquires method mutexes, checks sync level unless ignored, allocates owner IDs, and increments thread counts. Method calls validate argument counts, begin callee execution, create a nested walk state, initialize it with copied arguments, clear caller operands, and dispatch internal methods if needed. Termination deletes locals/args, removes temporary namespace objects when the last thread exits, releases method mutex depth, decrements thread count, applies pending serialization, and releases owner IDs.

### State, Persistence, And Dependencies
Persistent method state includes flags, mutex object, sync level, owner ID, thread count, AML pointers, and modified-namespace flags. Walk state carries nesting depth, method pathname, return descriptors, and thread sync level. The file depends on parser, namespace cleanup, mutex/OS wait APIs, trace hooks, and exception handler callbacks.

### Integration Points
`dsinit.c` calls auto-serialization. `dscontrol.c` creates method return descriptors. `dsmthdat.c` initializes/deletes arguments and locals. Namespace and interpreter subsystems use method owner IDs for temporary object cleanup.

### Risks
Reference, mutex, and owner-ID balancing are critical. Recursive serialized calls rely on acquisition depth. Failure paths must terminate partially started methods. Dynamic serialization after `AE_ALREADY_EXISTS` intentionally changes future behavior. Exception handlers run outside the interpreter and can remap failures.

### Test Signals
Signals include serialized methods acquiring/releasing mutexes correctly, sync-level order errors detected, nested method calls returning values to caller result stacks, temporary namespace objects deleted after method exit, owner IDs released when no threads remain, pending serialization applied only after the last active thread, and method errors invoking stack/local diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c

### Purpose
`dsmthdat.c` implements storage for AML control-method arguments and local variables. It models Args and Locals as pseudo namespace nodes so `RefOf`, `DerefOf`, and indirect stores can use normal namespace/object semantics.

### Important APIs, Types, And Functions
Public functions are `acpi_ds_method_data_init`, `acpi_ds_method_data_delete_all`, `acpi_ds_method_data_init_args`, `acpi_ds_method_data_get_node`, `acpi_ds_method_data_get_value`, and `acpi_ds_store_object_to_local`. Static helpers set and delete slot values. An obsolete type getter is conditionally compiled.

### Control Flow
Initialization fills fixed Arg and Local pseudo-nodes with names, descriptor type, flags, and type `ANY`. Argument initialization stores incoming operand pointers directly for call-by-reference semantics. Get-node validates class/index and returns a pseudo-node. Get-value reports uninitialized args/locals unless interpreter slack is enabled, in which case it installs an integer zero. Store-to-local copies shared objects when needed, handles indirect stores through Arg references created by `RefOf`, deletes existing values, and installs the new object with reference-count incrementing.

### State, Persistence, And Dependencies
All state lives in the current `struct acpi_walk_state`: `arguments[]` and `local_variables[]` pseudo-nodes plus attached objects. Reference counts are incremented on install and decremented on delete/detach. The module depends on namespace attach/detach helpers, object copying, interpreter store-to-node, and global interpreter-slack policy.

### Integration Points
`dsmethod.c` initializes and deletes method frames. `dsobject.c` creates local/arg reference objects using `acpi_ds_method_data_get_node`. `dbmethod.c` mutates live locals/args through `acpi_ds_store_object_to_local`.

### Risks
Call-by-reference means argument storage can alias caller-owned objects. Indirect Arg stores are subtle and intentionally differ from Local stores. Shared objects must be copied before overwrite, or unrelated references observe unintended mutation. Slack-mode zero initialization can hide firmware bugs.

### Test Signals
Signals include valid pseudo-node names/flags for all Args/Locals, correct uninitialized Arg/Local errors without slack, zero-object creation with slack, reference counts balanced across set/delete/all-delete, indirect `Store(..., ArgX)` through `RefOf` updating the target node, and Local overwrite not performing automatic dereference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c

### Purpose
`dsobject.c` translates parser ops into compact ACPICA operand objects and attaches them to namespace nodes. It handles constants, literals, strings, deferred buffers/packages, namespace references, method arguments/locals, and named object creation.

### Important APIs, Types, And Functions
Entry points are `acpi_ds_build_internal_object`, `acpi_ds_build_internal_buffer_obj`, `acpi_ds_create_node`, and `acpi_ds_init_object_from_op`. Key types include `union acpi_parse_object`, `union acpi_operand_object`, `struct acpi_walk_state`, opcode metadata, namespace nodes, and method pseudo-nodes.

### Control Flow
For namepath ops, object building reuses a resolved node, resolves it immediately unless it is a package element, or records unresolved package references for later resolution. It creates an object based on opcode object type and initializes it from opcode-specific data. Buffer creation chooses the larger of declared length and byte-list initializer length, allocates zeroed storage, copies byte-list data, and marks the buffer data-valid. Named node creation builds the first argument object, retypes the namespace node, attaches the object, and drops the local reference.

### State, Persistence, And Dependencies
The file persists object payloads and node attachments. Buffers/packages store node backpointers and deferred AML ranges. Strings point into the ACPI table and are marked static. Integer constants are marked `AOPOBJ_AML_CONSTANT`, with table-width truncation for 32-bit AML. Local/Arg references store pseudo-node pointers.

### Integration Points
`dsopcode.c` completes deferred data objects. `dsargs.c` evaluates deferred AML ranges. `dsmthdat.c` provides Local/Arg pseudo-nodes. Namespace attach/detach code owns lifetime once objects are attached.

### Risks
Package namepaths intentionally defer resolution to support forward/external references; resolving too early breaks compatibility. Static string pointers must never be freed. Buffer allocation failure must delete the object descriptor correctly. Reference objects must distinguish namespace names, debug object, Args, and Locals.

### Test Signals
Signals include correct integer values for Zero/One/Ones/Revision, 64-bit literal truncation warnings for 32-bit tables, buffer length selection from declared versus initializer lengths, package forward references marked unresolved, node type retyping on attach, and no freeing of table-backed string storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c

### Purpose
`dsopcode.c` evaluates operands for region, table-region, buffer-field, data-object, and bank-field opcodes after parse nodes and namespace objects already exist. It turns deferred operand expressions into concrete addresses, lengths, buffers, packages, and field parameters.

### Important APIs, Types, And Functions
Entry points include `acpi_ds_initialize_region`, `acpi_ds_eval_buffer_field_operands`, `acpi_ds_eval_region_operands`, `acpi_ds_eval_table_region_operands`, `acpi_ds_eval_data_object_operands`, and `acpi_ds_eval_bank_field_operands`. Static `acpi_ds_init_buffer_field` performs common buffer-field setup.

### Control Flow
Buffer-field evaluation creates operands from the create-field parse args, resolves them, retrieves the attached buffer-field object, computes bit offset/count based on create opcode, validates target buffer size, prepares common field metadata, links the host buffer, adjusts reference count inheritance, and marks the field data-valid. Region evaluation resolves address/length operands, stores them on the region object, warns for zero-length predefined spaces, registers the address range, and marks data-valid. Table-region evaluation resolves signature/OEM strings, finds the matching ACPI table, stores its physical address/length/pointer, and marks valid. Data-object evaluation resolves length then builds buffer or package objects. Bank-field evaluation resolves the bank value and stores it into every named bank-field object in the field list.

### State, Persistence, And Dependencies
The file persists object fields: buffer-field common metadata and buffer link, operation-region address/length/pointer, data-valid flags, package/buffer payloads, and bank-field selector values. It removes operand references after use. Dependencies include operand creation/resolution, field preparation, table lookup, event region initialization, namespace attachment, and address-range tracking.

### Integration Points
`dsargs.c` triggers deferred evaluation using saved AML spans. `dsfield.c` creates field objects and parse-node node pointers consumed here. `dsobject.c` builds data object descriptors. Event code initializes operation regions.

### Risks
Bounds checking is essential for buffer fields; overflow or wrong unit conversion can expose memory outside the buffer. Region address/length evaluation can register invalid firmware ranges. Table-region lookup depends on exact string operands. Reference cleanup must match operand stack ownership, especially on failure paths.

### Test Signals
Signals include buffer-field creation failing on non-buffer targets and out-of-bounds bit ranges, all create-field opcode widths producing correct bit counts, operation regions receiving correct address/length and data-valid flag, table regions pointing at the selected ACPI table, buffer/package objects materialized from deferred AML, and bank fields receiving evaluated bank values across all named fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c -->
