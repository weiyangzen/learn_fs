# subset-b-001014 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dspkginit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dspkginit.c

## Purpose
Completes deferred ACPICA package initialization by translating parser package ops into internal package objects and resolving package elements that name namespace objects. It preserves ACPICA compatibility behavior for malformed firmware packages: too-short package lists are padded with null/uninitialized elements, too-long package lists are truncated, and module-level package element resolution can be deferred to support forward references after all tables are loaded.

## Important APIs, Types, And Functions
- `acpi_ds_build_internal_package_obj` creates or reuses an `ACPI_TYPE_PACKAGE` operand object, allocates the element pointer array, builds each parser initializer with `acpi_ds_build_internal_object`, handles nested package parents, and sets `AOPOBJ_DATA_VALID` when resolution is complete.
- `acpi_ds_init_package_element` is the package-tree callback used by direct calls and `acpi_ut_walk_package_tree`; it resolves `ACPI_TYPE_LOCAL_REFERENCE` entries and marks nested packages valid.
- `acpi_ds_resolve_package_element` performs namespace lookup for a named reference, handles optional ignored not-found errors, aliases, node-to-value conversion, and replacement of reference elements with resolved data objects when appropriate.

## Control Flow
Package build starts from the package parse op, finds the nearest non-package parent for the namespace node, reuses an existing package for named objects when available, then walks initializer args up to `element_count`. Elements that are return-value parser ops are either rejected if expression results have no node, converted to namepaths for method references, or lifted from the node pointer. Non-module-level packages resolve elements immediately; module-level packages record AML start and leave element resolution for a later package walk. The resolver uses the saved reference prefix node plus AML namestring, externalizes names only for diagnostics, replaces unresolvable elements with null, and keeps device/thermal/method references as references while resolving data-like objects to concrete values.

## State And Persistence
Persistent state lives in operand object fields: `package.elements`, `package.count`, `package.node`, `package.flags`, `package.aml_start`, and element reference fields such as `reference.node` and `reference.resolved`. Reference counts are adjusted to match an already shared package object, and failed/truncated elements have references removed to avoid leaks.

## Dependencies And Integration Points
Depends on dispatcher builders, namespace lookup/externalization, interpreter node-to-value resolution, parser op layout, and utility reference management. It integrates with table load, module-level execution, package tree walking, AML compatibility slack, and later consumers that expect package data to be valid or safely null-padded.

## Risks And Edge Cases
Key risks are reference-count imbalance when replacing elements, unresolved firmware references hidden by `acpi_gbl_ignore_package_resolution_errors`, unsupported expressions inside package elements, and compatibility-driven truncation that silently drops extra initializers. Alias and non-data object handling must remain precise because devices, methods, mutexes, events, regions, and power resources do not all have package data-object values.

## Test Signals
Useful signals include packages with declared counts smaller/larger than initializer lists, module-level forward references resolving after load, unresolved package names becoming null when ignore mode is enabled, aliases resolving to targets, method references remaining reference-like, and no leaks or double-frees when shared named packages are rebuilt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dspkginit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsutils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsutils.c

## Purpose
Provides dispatcher utility routines for method execution: implicit return tracking, result liveness decisions, operand creation and cleanup, operand resolution for method calls, and namepath evaluation. This file is the glue between parse objects, namespace nodes, operand stacks, result stacks, and interpreter value conversion.

## Important APIs, Types, And Functions
- `acpi_ds_clear_implicit_return` and `acpi_ds_do_implicit_return` maintain optional slack-mode implicit method return values.
- `acpi_ds_is_result_used` and `acpi_ds_delete_result_if_not_used` decide whether an opcode result should remain on the result stack or be popped and dereferenced.
- `acpi_ds_create_operand` translates a parse argument into a namespace node or operand object, including name lookup, create-vs-execute interpreter mode, deferred buffer-field handling, null target placeholders, and previously stacked return values.
- `acpi_ds_create_operands`, `acpi_ds_resolve_operands`, and `acpi_ds_clear_operands` manage the walk state's operand array.
- `acpi_ds_evaluate_name_path` resolves a namepath to a value or target object and pushes the result.

## Control Flow
Opcode execution calls `acpi_ds_create_operands`, which gathers argument parse ops, then creates operands in reverse order into the fixed operand array. Namepath operands are decoded with `acpi_ex_get_name_string`, looked up in the namespace, and pushed directly; non-namepath operands are either popped from the result stack if the parse op already produced a value or initialized from opcode metadata. After interpreter dispatch, `acpi_ds_is_result_used` inspects the parent opcode class to decide whether the result feeds a parent expression, predicate, return, create op, package/buffer/region operand, or should be discarded.

## State And Persistence
State is per `acpi_walk_state`: `implicit_return_obj`, `result_obj`, `operands[]`, `num_operands`, `operand_index`, and parse op flags such as `ACPI_PARSEOP_IN_STACK` and `ACPI_PARSEOP_TARGET`. The functions deliberately add and remove object references as values move between result stack, operand stack, namespace, and implicit return storage.

## Dependencies And Integration Points
Uses parser opcode metadata, namespace lookup, root node fallback for `CondRefOf`, interpreter conversions/resolution, debugger display hooks, dispatcher object stack functions, and utility object copy/delete helpers. It is called from execution callbacks, load pass 2, method invocation setup, buffer/field evaluation, and data-object evaluation paths.

## Risks And Edge Cases
Operand stack overflow/underflow and stale `num_operands` values can corrupt later interpreter calls. Name lookup mode is subtle: create contexts must enter names, execute contexts must reject missing names, and deferred buffer-field names must not be looked up in the wrong scope. Implicit return is optional slack behavior and can accidentally keep stale references if not cleared. Integer namepath values are copied after resolution so later stores do not mutate namespace-backed values unexpectedly.

## Test Signals
Exercise `CondRefOf` missing names, method calls with unresolved locals, store-to-self uninitialized local behavior, null optional target operands, namepath values inside packages and `RefOf`, implicit-return enabled/disabled runs, and cleanup after operand creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswexec.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload.c

## Purpose
Implements first-pass ACPICA namespace loading callbacks. Pass 1 discovers named AML objects, creates or validates namespace nodes, opens and closes scopes, creates early method objects, and handles disassembler-only external/create-field cases before full object attachment in pass 2.

## Important APIs, Types, And Functions
- `acpi_ds_init_callbacks` configures walk-state parse flags and callbacks for parse-only, load pass 1, load pass 2, and execution pass.
- `acpi_ds_load1_begin_op` is the descending pass-1 callback that handles named op lookup/creation, Scope target validation, external declarations, namespace override behavior, and new parse op allocation for stream parsing.
- `acpi_ds_load1_end_op` is the ascending pass-1 callback that initializes field declarations, creates early operation regions/data regions, sets `Name` node types from their initializer object type, creates method objects, and pops scope frames.

## Control Flow
Pass 1 ignores opcodes without associated names. For `Scope`, it looks up the target in execute mode and verifies that the target can open a scope, allowing compatibility type override for integer/string/buffer targets and a module-level root-method exception. Other named opcodes create namespace nodes with no upsearch and optional error/override-if-found semantics, unless a deferred node or method execution context says the node already exists or must wait until execution. On ascent, field objects are initialized outside method execution, region shells are created from saved AML address/length data, method nodes get attached method objects as soon as possible so later method invocations know argument counts, and scope-opening opcodes pop the scope stack.

## State And Persistence
Persistent state is the namespace tree and parse op `common.node`/`named.name` fields. Walk-state flags capture pass semantics, `deferred_node`, `namespace_override`, `method_node`, and scope stack state. Method creation attaches runtime objects to namespace nodes during pass 1; field and region creation may attach partial objects used later by pass 2 or execution.

## Dependencies And Integration Points
Uses parser namestring extraction/allocation, namespace lookup, scope-stack helpers, region and field creation helpers, method creation, ASL compiler/disassembler external handling, and opcode metadata. It is initialized by walk-state setup and feeds load pass 2 and method execution.

## Risks And Edge Cases
Scope target type compatibility is intentionally permissive for firmware quirks, but method targets remain invalid except module-level root handling. Deferred op parsing must not duplicate namespace nodes. External declarations in disassembler mode must be retyped and tracked without opening scopes incorrectly. Method execution must avoid pass-1 namespace creation because execution-time temporary nodes are owned by pass 2/execution.

## Test Signals
Tests should cover Scope on existing devices and invalid targets, duplicate names with and without override, deferred region/buffer/package loading, method objects callable after pass 1, disassembler external op handling, and correct scope-depth balancing after nested devices/power resources/processors/thermal zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload2.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload2.c

## Purpose
Implements second-pass namespace loading callbacks. Pass 2 resolves namespace references and method calls, completes named object creation, initializes fields and operation regions, attaches data objects to name nodes, and supports execution-time creation of temporary method-local namespace objects.

## Important APIs, Types, And Functions
- `acpi_ds_load2_begin_op` performs namespace lookup or creation for pass 2, including namepaths, Scope targets, field op placeholders, existing pass-1 nodes, temporary execute-mode nodes, and external-op compiler handling.
- `acpi_ds_load2_end_op` finalizes namespace objects by opcode type: create fields, field/index/bank fields, processor/power/mutex/event/alias objects, regions/data regions, names, methods, and method-call resolution.

## Control Flow
On descent, conditional module-level loops can be delegated to execution begin logic. Namepath ops are looked up but not created. Scope ops push scope frames for valid scope targets and warn on compatibility type overrides. Other namespace opcodes either reuse `op->common.node`, use `deferred_node`, or call `acpi_ns_lookup` in load-pass-2 mode with prefix-must-exist and temporary-node flags as needed. On ascent, the node saved in the op is pushed as operand zero, scope frames are popped, and a switch on opcode type creates the concrete runtime object or resolves a method call. Region creation may be deferred until method execution, but `acpi_ev_initialize_region` is invoked to attach available handlers. Name ops use `acpi_ds_create_node`, and method ops attach method objects if not already present.

## State And Persistence
Pass 2 persists namespace node attachments, region handler associations, field objects, method dispatch metadata, alias relationships, and temporary nodes for control-method execution. It uses `walk_state->operands[0]` as the current node carrier and resets operand counts during cleanup.

## Dependencies And Integration Points
Depends on namespace lookup/search, scope stack management, field creation helpers, executor object constructors, operation-region initialization, method creation, data-object creation, parser opcode metadata, and ACPI_EXEC_APP initialization-file hooks. It is called both by table loading and from method execution paths for runtime named declarations.

## Risks And Edge Cases
Temporary node flags must be applied only for control-method execution outside module-level code. Scope pop must match prior open-scope decisions. Region initialization can run `_REG` methods and must be invoked with interpreter locking assumptions satisfied by callers. Method-call resolution intentionally looks up `ACPI_TYPE_ANY` first to detect non-method names cleanly. Some cleanup paths return early and must leave operand zero cleared.

## Test Signals
Use AML with runtime-created named objects, field/index/bank field declarations, `Name` objects holding buffers/packages, regions whose handlers are installed before and after creation, method calls to non-method names, and module-level conditional loops that require pass-2 plus execution interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswscope.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswscope.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswstate.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evevent.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evevent.c

## Purpose
Initializes and dispatches fixed ACPI events and coordinates top-level event interrupt handler installation. It disables fixed events during setup, initializes GPEs before SCI delivery, installs SCI and global lock handlers, detects active fixed-event bits, dispatches registered handlers, and exposes a status-set query helper.

## Important APIs, Types, And Functions
- `acpi_ev_initialize_events` initializes fixed events and GPE data structures unless reduced hardware mode is active.
- `acpi_ev_install_xrupt_handlers` installs the SCI handler and global-lock fixed event handler, then marks events initialized.
- `acpi_ev_fixed_event_initialize` clears fixed-event handler slots and disables all fixed events with valid enable registers.
- `acpi_ev_fixed_event_detect` reads PM1 status/enable registers, counts and globally reports active fixed events, and dispatches each enabled status bit.
- `acpi_ev_fixed_event_dispatch` clears status, disables unhandled events, and invokes the installed fixed-event handler.
- `acpi_any_fixed_event_status_set` checks whether any enabled fixed event currently has status set.

## Control Flow
Initialization returns early for reduced hardware. Otherwise, fixed events are disabled before GPE setup to avoid interrupts before handler registration. Interrupt installation starts with SCI, then global lock. During SCI processing, fixed-event detection reads status and enable registers once, iterates all fixed event descriptors, and dispatches only bits with both status and enable set. Dispatch clears the event status before calling the handler, or disables the event permanently if no handler exists.

## State And Persistence
Global state includes `acpi_gbl_fixed_event_handlers`, `acpi_gbl_fixed_event_info`, `acpi_fixed_event_count`, global event handler pointers, and `acpi_gbl_events_initialized`. Hardware PM1 enable/status registers persist event enablement and pending status.

## Dependencies And Integration Points
Depends on hardware register access helpers, fixed-event bit metadata, SCI installation, global-lock initialization, GPE initialization, and global event notification callbacks. The module is compiled out for reduced-hardware builds.

## Risks And Edge Cases
Register read failures silently produce "not handled" for detection. Missing handlers are treated defensively by disabling the event to stop interrupt storms. Events with enable register ID `0xFF` are not disabled during initialization. Ordering matters: enabling SCIs before fixed/GPE setup could deliver events into uninitialized handler tables.

## Test Signals
Signals include fixed events disabled after initialization, no-op behavior in reduced hardware mode, handler dispatch only when both status and enable bits are set, global handler invocation and per-event count increments, unhandled fixed events being disabled, and `acpi_any_fixed_event_status_set` reflecting PM1 register contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evglock.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evglock.c

## Purpose
Implements ACPICA global lock support for non-reduced hardware. It installs the global-lock fixed event handler, maps absent hardware to mutex-only behavior, serializes host-side acquisition, performs the FACS global-lock hardware handshake, and releases the BIOS when pending.

## Important APIs, Types, And Functions
- `acpi_ev_init_global_lock_handler` installs the fixed event handler, creates the pending spin lock, and records whether global lock hardware is present.
- `acpi_ev_remove_global_lock_handler` removes the fixed event handler and deletes the pending lock.
- `acpi_ev_global_lock_handler` handles release interrupts and signals the global-lock semaphore when a request is pending.
- `acpi_ev_acquire_global_lock` acquires the OS mutex, updates the external handle, then loops on `ACPI_ACQUIRE_GLOBAL_LOCK` and waits for the semaphore if hardware ownership is not granted.
- `acpi_ev_release_global_lock` releases hardware ownership with `ACPI_RELEASE_GLOBAL_LOCK`, writes the global-lock release bit if BIOS is pending, clears acquired state, and releases the OS mutex.

## Control Flow
Initialization exits for reduced hardware or disabled global-lock use. Handler installation failure with `AE_NO_HARDWARE_RESPONSE` disables hardware global-lock use but is not fatal. Acquire first obtains a local mutex so only one ACPICA thread can contend for hardware, then either succeeds immediately in mutex-only mode or loops under the pending spin lock until FACS ownership is acquired. If the BIOS owns the lock, ACPICA marks `acpi_gbl_global_lock_pending`, releases the spin lock, waits on the semaphore signaled by the fixed event handler, and retries. Release writes the hardware release notification only when the pending bit is returned.

## State And Persistence
Global state includes `acpi_gbl_global_lock_present`, `acpi_gbl_global_lock_pending`, `acpi_gbl_global_lock_acquired`, `acpi_gbl_global_lock_handle`, global lock mutex/semaphore, pending spin lock, and FACS global-lock bits. The local OS mutex persists ownership across AML/external callers until release.

## Dependencies And Integration Points
Uses fixed event registration, ACPI bit-register writes, OS spin locks/mutexes/semaphores, interpreter wait helpers that can release the interpreter while blocking, and FACS global-lock macros.

## Risks And Edge Cases
Spurious release interrupts are ignored if no pending request exists. Absent hardware falls back to a standard mutex but later code can still identify that hardware is missing. Release without acquire returns `AE_NOT_ACQUIRED`. Timeout applies to local mutex acquisition, while hardware wait uses `ACPI_WAIT_FOREVER`, so firmware that never signals can hang the wait path.

## Test Signals
Validate no-op behavior in reduced/disabled modes, graceful handling of no hardware response, semaphore signaling only when pending, handle wraparound skipping zero, mutex-only acquire/release when hardware is absent, pending-bit release register writes, and warnings on unmatched release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evglock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpe.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpe.c

## Purpose
Implements General Purpose Event runtime control, detection, and dispatch. It tracks runtime enable references and masks, maps raw GPE numbers to event descriptors, scans interrupt blocks, atomically detects enabled status bits, dispatches raw/normal handlers, queues methods or implicit notifies, and finishes GPEs with correct edge/level clear timing.

## Important APIs, Types, And Functions
- `acpi_ev_update_gpe_enable_mask`, `acpi_ev_enable_gpe`, `acpi_ev_mask_gpe`, `acpi_ev_add_gpe_reference`, and `acpi_ev_remove_gpe_reference` maintain runtime enable state and hardware enable bits.
- `acpi_ev_low_get_gpe_info` and `acpi_ev_get_gpe_event_info` resolve raw GPE numbers within FADT or device GPE blocks.
- `acpi_ev_gpe_detect` scans all blocks on an interrupt descriptor and delegates each bit to `acpi_ev_detect_gpe`.
- `acpi_ev_detect_gpe` reads enable/status registers, invokes the global event handler, and dispatches active GPEs.
- `acpi_ev_gpe_dispatch`, `acpi_ev_asynch_execute_gpe_method`, `acpi_ev_asynch_enable_gpe`, and `acpi_ev_finish_gpe` handle disable/clear/execute/re-enable sequencing.

## Control Flow
Runtime references set `enable_for_run` and enable hardware on the first reference; the last reference clears the mask and disables hardware. Interrupt scanning skips registers with no run or wake enables. Each candidate GPE is detected under `acpi_gbl_gpe_lock`, but the block scan releases the lock around per-GPE detection to reduce critical sections. Active raw handlers run with the GPE lock released. Standard dispatch first disables the GPE, clears edge-triggered status before service, then invokes an interrupt-level handler, queues a method/notify worker, or leaves unhandled GPEs disabled. Method/notify completion defers re-enable until notify handlers can complete, and level-triggered status is cleared in `acpi_ev_finish_gpe`.

## State And Persistence
Per-GPE state includes `runtime_count`, `flags`, `disable_for_dispatch`, `dispatch.handler`, `dispatch.method_node`, `dispatch.notify_list`, and register masks `enable_for_run`, `enable_for_wake`, `mask_for_run`, and `enable_mask`. Global counters include `acpi_gpe_count`; global event handlers receive each active GPE.

## Dependencies And Integration Points
Depends on GPE block metadata, hardware GPE read/write helpers, OS lock and work-queue execution, namespace method evaluation, notify queuing, and global event handler callbacks. It integrates with public GPE enable/mask APIs and with `_Lxx`/`_Exx` discovery from `evgpeinit.c`.

## Risks And Edge Cases
Reference count overflow/underflow returns `AE_LIMIT`. Mask/unmask validates current mask state and can reject duplicate operations. Raw handler safety depends on caller-installed handler lifetime and flushing before destruction. Failed queueing leaves the event disabled after logging. Edge and level clear timing must not be swapped or GPEs can be lost or storm.

## Test Signals
Signals include first/last reference hardware enable transitions, duplicate mask/unmask errors, lookup across GPE0/GPE1 and device GPE blocks, skipped disabled registers, global handler calls, raw handler execution with lock released, edge GPE status cleared before handler, level GPE status cleared after completion, and method/notify dispatch re-enabling only after finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeblk.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeblk.c

## Purpose
Creates, installs, initializes, and deletes GPE register blocks. It allocates per-register and per-GPE metadata, disables and clears hardware on creation, links blocks to interrupt descriptors, discovers matching `_Lxx`/`_Exx` methods, auto-enables eligible runtime GPEs, and frees block resources on deletion.

## Important APIs, Types, And Functions
- `acpi_ev_create_gpe_block` validates address space, allocates a `struct acpi_gpe_block_info`, creates substructures, installs the block, walks methods, and returns the block.
- `acpi_ev_create_gpe_info_blocks` allocates and initializes `acpi_gpe_register_info` and `acpi_gpe_event_info` arrays, computes status/enable register addresses, disables enable registers, and clears status registers.
- `acpi_ev_install_gpe_block` links a block into the proper `acpi_gpe_xrupt_info` list under the events mutex and GPE spin lock.
- `acpi_ev_initialize_gpe_block` marks all GPEs initialized and auto-enables non-wake GPEs with method dispatch.
- `acpi_ev_delete_gpe_block` disables a block, unlinks it, deletes the xrupt if needed, updates global count, and frees arrays.

## Control Flow
Creation validates nonzero register count and memory/IO address space, validates IO blocks, allocates the top-level block, builds metadata arrays, then installs into the interrupt list. Method discovery walks under the GPE device and calls `acpi_ev_match_gpe_method`. Initialization later iterates every event descriptor, ignores wake-only or methodless GPEs, adds a runtime reference to method-backed GPEs, marks them auto-enabled, and records whether polling is needed.

## State And Persistence
Persistent global GPE state includes xrupt block lists, GPE block linked lists, `acpi_current_gpe_count`, per-register addresses/masks, and per-event dispatch flags. Hardware enable/status registers are reset during block creation.

## Dependencies And Integration Points
Uses events mutex, GPE spin lock, xrupt allocation, hardware GPE writes, IO range validation, namespace method walking, GPE method matching, and reference-count enable helpers. It supplies data consumed by interrupt dispatch in `evgpe.c`.

## Risks And Edge Cases
Partial allocation or install failures must free both register and event arrays. Deleting a block must not remove the SCI interrupt descriptor itself, and the code delegates that distinction to xrupt deletion. Auto-enable failures are logged per GPE but do not abort the whole block. Unsupported address spaces and invalid IO ranges reject block creation.

## Test Signals
Exercise zero-register no-op blocks, memory and IO FADT blocks, unsupported space IDs, register address calculations for status versus enable halves, hardware disable/clear writes during creation, method discovery immediately after install, auto-enable counts, polling-needed propagation, and deletion of last versus non-last block on an interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeblk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeinit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeinit.c

## Purpose
Initializes system GPE blocks from the FADT and updates GPE dispatch metadata when new tables introduce `_Lxx` or `_Exx` methods. It also decodes method names into GPE numbers, trigger types, and dispatch method associations.

## Important APIs, Types, And Functions
- `acpi_ev_gpe_initialize` creates optional FADT GPE0 and GPE1 blocks from FADT lengths/addresses and SCI interrupt routing.
- `acpi_ev_update_gpes` walks all GPE block devices after dynamic table load and enables newly discovered methods for a specific owner ID.
- `acpi_ev_match_gpe_method` is the namespace walk callback that recognizes `_Lxx`/`_Exx`, parses hex GPE numbers, validates block membership, detects handler conflicts, and records method dispatch data.

## Control Flow
Initialization locks the namespace, computes register counts as half of FADT GPE block lengths, creates GPE0 if present, then creates GPE1 if present and non-overlapping with GPE0. Missing blocks are valid. Dynamic update locks events, walks every xrupt and block, and searches each block's GPE device for methods owned by the newly loaded table. Method matching filters by owner when requested, requires names beginning with `_L` or `_E` plus two hex digits, ignores methods outside the block's GPE range, refuses to override installed handlers, reports `_Lxx`/`_Exx` trigger conflicts, disables the GPE, and sets dispatch flags plus method node.

## State And Persistence
State includes `acpi_gbl_gpe_fadt_blocks[0..1]`, FADT-derived register counts/base numbers, xrupt/block lists, per-event flags and method nodes, and update walk counters. This file no longer executes `_PRW`; wake GPE ownership is expected to be configured by the host OS.

## Dependencies And Integration Points
Depends on FADT global data, optional logical GPE block addresses, namespace and events mutexes, GPE block creation, method walking, GPE low-level lookup, hardware low-level GPE disable, and owner IDs assigned to loaded ACPI tables.

## Risks And Edge Cases
GPE0 and GPE1 overlap is detected and causes GPE1 to be ignored. Methods with malformed names are silently ignored with debug output. Existing handlers take precedence over methods. If both `_Lxx` and `_Exx` exist, the first wins and a mismatch error is logged. Dynamic updates must filter by table owner to avoid reprocessing unrelated methods.

## Test Signals
Test no-GPE FADT, GPE0-only, GPE1-only, overlapping GPE0/GPE1, logical versus physical addresses, valid `_Lxx` and `_Exx` registration, malformed method names, duplicate level/edge method conflicts, handler-over-method precedence, and dynamic `Load()` enabling newly introduced GPE methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeutil.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeutil.c

## Purpose
Supplies utility routines for walking GPE block lists, mapping a global GPE index to its device, creating/deleting GPE interrupt descriptors, and freeing installed GPE handlers/notify lists during termination.

## Important APIs, Types, And Functions
- `acpi_ev_walk_gpe_list` iterates every xrupt descriptor and block under `acpi_gbl_gpe_lock`, invoking a callback with shared context.
- `acpi_ev_get_gpe_device` maps an index in the global GPE sequence to the block's device node or null for FADT-defined GPEs.
- `acpi_ev_get_gpe_xrupt_block` finds or allocates an interrupt descriptor and installs an OS interrupt handler for non-SCI GPE interrupts.
- `acpi_ev_delete_gpe_xrupt` removes a non-SCI interrupt handler, unlinks and frees the xrupt descriptor, or preserves the SCI descriptor while clearing its block list.
- `acpi_ev_delete_gpe_handlers` frees per-GPE handler objects and implicit notify node lists.

## Control Flow
List walking holds the GPE spin lock for stable traversal and lets callbacks abort with `AE_CTRL_END`. Xrupt lookup scans the global list without changing it; if absent, it allocates, appends under the spin lock, then installs an OS interrupt handler when the interrupt is not the SCI. Deletion skips handler removal for SCI, but removes non-SCI OS handlers before unlinking. Handler cleanup scans every register and every bit in a block and clears dispatch masks after freeing associated storage.

## State And Persistence
State includes `acpi_gbl_gpe_xrupt_list_head`, doubly linked xrupt descriptors, block list heads, block/device pointers, per-GPE dispatch handler pointers, and implicit notify linked lists. The device-index helper mutates a caller-provided `acpi_gpe_device_info`.

## Dependencies And Integration Points
Uses OS interrupt install/remove callbacks, GPE xrupt handler entry point, spin locks, GPE block structures, event termination, and public GPE device enumeration helpers. It supports block creation/deletion in `evgpeblk.c` and cleanup in `evmisc.c`.

## Risks And Edge Cases
Installing a new xrupt appends it before OS interrupt handler installation; failure returns an error but leaves list state that callers must account for. Walking while holding the spin lock means callbacks must be lightweight and lock-safe. SCI descriptors are never freed by `acpi_ev_delete_gpe_xrupt`, so later cleanup must not expect the same behavior as non-SCI descriptors. Handler lifetime relies on event flushing before free.

## Test Signals
Signals include callback traversal order across multiple interrupt descriptors, `AE_CTRL_END` early exit mapping to success, device mapping for FADT versus device GPE blocks, non-SCI interrupt handler installation/removal, SCI preservation, and handler/notify dispatch masks cleared after termination cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evhandler.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evhandler.c

## Purpose
Installs and finds address-space handlers for operation regions. It registers ACPICA default handlers at the root, creates handler objects on devices/root, prevents duplicate/conflicting handlers, and walks namespace branches to attach matching regions while respecting handler scoping rules.

## Important APIs, Types, And Functions
- `acpi_gbl_default_address_spaces` lists default spaces: system memory, system IO, PCI config, and data table.
- `acpi_ev_install_region_handlers` installs default handlers on the root node and treats already-installed/same-handler cases as success.
- `acpi_ev_has_default_handler` checks whether a node has a default handler for a space ID.
- `acpi_ev_find_region_handler` searches a handler linked list by space ID.
- `acpi_ev_install_space_handler` validates target node type, expands `ACPI_DEFAULT_HANDLER` to concrete handler/setup routines, creates device objects when needed, allocates handler objects with context mutexes, links handlers, and walks regions.
- `acpi_ev_install_handler` is the namespace walk callback that attaches matching regions or prunes branches where a nearer device handler already exists.

## Control Flow
Default handler installation holds the namespace mutex and iterates default spaces. Installing a specific handler first resolves default handler functions/setup routines, checks for an existing attached object and duplicate handler, creates an internal object if needed, allocates a local address-handler object, creates its context mutex, links it at the head of the device/root handler list, then walks downward from the target node. During the walk, device nodes with an existing handler for the same space stop traversal below that device; matching region nodes are detached from previous handlers and attached to the new handler.

## State And Persistence
Persistent state is stored in namespace-attached device/root objects and `ACPI_TYPE_LOCAL_ADDRESS_HANDLER` objects: space ID, handler flags, region list, context, setup callback, context mutex, owning node, and next-handler links. Region objects receive handler pointers and linked-list membership through `evregion.c`.

## Dependencies And Integration Points
Depends on namespace locking/walking, namespace object attach/get helpers, operation-region attach/detach routines, executor default address-space handlers, region setup callbacks from `evrgnini.c`, and utility object allocation/reference management.

## Risks And Edge Cases
Handlers may be installed on the root for default spaces before platform enumeration, but later PCI root handler installation can move PCI config regions closer to the correct root bridge. Duplicate same handler returns `AE_SAME_HANDLER`; different handler returns `AE_ALREADY_EXISTS`. The walk unlocks namespace around callbacks, so attach/detach paths must tolerate region state changes. Context mutex creation failure must release the handler object.

## Test Signals
Cover default handler installation idempotence, invalid target node rejection, duplicate same and conflicting handlers, branch pruning below nearer device handlers, root-installed PCI config fallback, handler context mutex creation/cleanup, and region reattachment from previous to new handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evhandler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evmisc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evmisc.c

## Purpose
Provides miscellaneous event-manager support: validation and asynchronous dispatch of Notify requests, and event subsystem termination for fixed events, GPEs, SCI handlers, global lock, handler storage, and legacy-mode restoration.

## Important APIs, Types, And Functions
- `acpi_ev_is_notify_object` restricts Notify targets to Device, Processor, and Thermal objects.
- `acpi_ev_queue_notify_request` selects system versus device notify lists, builds a notify generic state, and queues asynchronous dispatch if any global or local handler exists.
- `acpi_ev_notify_dispatch` invokes the global notify handler and local notify handler chain, then frees the notify state.
- `acpi_ev_terminate` disables fixed events and all GPEs, removes global lock and SCI handlers, deletes GPE handler storage, clears initialized state, and returns to legacy ACPI mode if necessary.

## Control Flow
Notify queueing rejects unsupported target node types, determines handler-list ID based on `notify_value <= ACPI_MAX_SYS_NOTIFY`, loads local handlers from the node's attached object, and returns success without work if no handler is present. If work is needed, it creates `ACPI_DESC_TYPE_STATE_NOTIFY`, records node/value/local/global handler state, and submits `acpi_ev_notify_dispatch` to the notify worker queue. Termination runs only initialized event disablement first, then always removes SCI handlers, walks GPE lists to free handler structures, and finally disables ACPI if original mode was legacy.

## State And Persistence
Notify state is transient generic-state storage passed to the worker. Persistent event state includes global notify handler arrays, per-object notify lists, fixed-event enable state, GPE block/handler state, global lock state, SCI handler lists, `acpi_gbl_events_initialized`, and original ACPI mode.

## Dependencies And Integration Points
Uses namespace attached objects, OS work queues, generic-state allocation, fixed-event APIs, GPE list walking, hardware GPE disable callbacks, global-lock removal, SCI removal, and ACPI mode switching. GPE implicit notify dispatch from `evgpe.c` queues through this file.

## Risks And Edge Cases
No-handler Notify is intentionally ignored rather than treated as an error. Asynchronous dispatch means handler lists must remain valid until queued work drains. Termination logs errors but continues because teardown must be best-effort. Notify type validation must match ACPI object semantics or firmware notifications may be dropped incorrectly.

## Test Signals
Signals include Device/Processor/Thermal Notify acceptance, other types returning `AE_TYPE`, correct system/device notify list selection, global and local handler invocation order, cleanup when `acpi_os_execute` fails, fixed/GPE disable attempts during termination, GPE handler memory free, and legacy-mode disable on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evregion.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evregion.c

## Purpose
Implements operation-region handler dispatch, region attach/detach, `_REG` execution, and bulk `_REG` walks. It lazily activates regions on first access, routes field accesses to installed address-space handlers, manages handler-region bidirectional links, and notifies firmware when region availability changes.

## Important APIs, Types, And Functions
- `acpi_ev_initialize_op_regions` runs `_REG(CONNECT)` for default-handler spaces that need it.
- `acpi_ev_address_space_dispatch` initializes a region if needed, prepares special context for PCC/FFH/GSBus/GPIO, exits the interpreter for non-default handlers, and invokes the address-space handler.
- `acpi_ev_attach_region` and `acpi_ev_detach_region` maintain the handler's region list and the region's handler pointer/reference.
- `acpi_ev_execute_reg_method` finds/caches a region's `_REG` method, builds `(space_id, connect_state)` arguments, evaluates it, and tracks `AOPOBJ_REG_CONNECTED`.
- `acpi_ev_execute_reg_methods`, `acpi_ev_reg_run`, and `acpi_ev_execute_orphan_reg_method` walk regions for a space and handle EC/GPIO orphan `_REG` compatibility.

## Control Flow
Dispatch first requires a secondary object and installed handler. If setup is incomplete, it prepares space-specific handler context, exits the interpreter, calls the setup routine with `ACPI_REGION_ACTIVATE`, records the returned region context, then continues. Non-default handlers run outside the interpreter lock. GSBus/GPIO use the handler context mutex to pass connection buffer, resource length, and access length; GPIO also remaps address/bit width to pin index and field bit length. Detach unlinks the region, optionally drops the namespace mutex to run `_REG(DISCONNECT)`, deactivates the region through setup, clears context, removes the handler reference, and protects against circular handler lists.

## State And Persistence
State is stored in region objects and secondary objects: handler pointer, next-region link, setup flags, `_REG` cached method node, region context, address/length/space ID, `AOPOBJ_SETUP_COMPLETE`, and `AOPOBJ_REG_CONNECTED`. Handler objects store region lists, setup callbacks, contexts, and context mutexes.

## Dependencies And Integration Points
Depends on namespace object lookup/walking/search, address-space handler registration, interpreter lock enter/exit, OS mutexes, region setup callbacks, utility integer object creation, method evaluation, and public `acpi_get_handle`/`acpi_evaluate_object` for orphan `_REG`.

## Risks And Edge Cases
Missing handlers return `AE_NOT_EXIST` but many regions are created before handlers exist. Setup callbacks may run control methods, so interpreter locking must be correct. Non-default handlers may block, requiring interpreter release. GSBus/GPIO shared context must be mutex-protected. `_REG` connect/disconnect calls are paired and skipped if already in the requested state. Orphan `_REG` execution intentionally ignores errors for EC/GPIO firmware compatibility.

## Test Signals
Test lazy setup on first field access, no-handler region access failure, default versus non-default interpreter lock behavior, GSBus/GPIO context population, handler errors including EC timeout diagnostics, attach/detach reference counts, `_REG` connect/disconnect pairing, skipped `_REG` for system memory/IO/data table, and orphan EC/GPIO `_REG` execution only when no matching region exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evrgnini.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evrgnini.c

## Purpose
Provides address-space-specific setup routines for operation regions and the region initialization search that binds newly created regions to the nearest installed handler. It creates and destroys per-region contexts for memory, IO, PCI config, data table, and default spaces, detects PCI root bridges, and runs `_REG(CONNECT)` after successful handler attachment.

## Important APIs, Types, And Functions
- `acpi_ev_system_memory_region_setup` creates `acpi_mem_space_context` and frees all cached memory mappings on deactivate.
- `acpi_ev_io_space_region_setup`, `acpi_ev_default_region_setup`, `acpi_ev_pci_bar_region_setup`, and `acpi_ev_cmos_region_setup` provide simple or placeholder setup behavior.
- `acpi_ev_pci_config_region_setup` discovers PCI segment/bus/device/function, installs a handler on a PCI root bridge when only the root default handler is present, and returns an `acpi_pci_id` context.
- `acpi_ev_is_pci_root_bridge` detects PCI/PCIe root bridges via `_HID` and `_CID`.
- `acpi_ev_data_table_region_setup` creates/frees an `acpi_data_table_mapping`.
- `acpi_ev_initialize_region` searches upward from the region's parent for a matching handler, attaches the region, exits the interpreter, and runs `_REG(CONNECT)`.

## Control Flow
Setup callbacks receive activate/deactivate function codes. Memory deactivate unmaps every cached mapping and frees context; activate records region address/length. IO and default setup reuse handler context. PCI config setup handles deactivation by freeing existing PCI ID, then on activation identifies the PCI root bridge, possibly installs a more specific default handler, evaluates `_ADR`, `_SEG`, and `_BBN`, derives the full PCI ID, and returns it. Region initialization marks the object initialized once, walks parent scopes toward root, inspects handlers on devices/processors/thermal/root, attaches the first matching handler, and notifies firmware with `_REG(CONNECT)`.

## State And Persistence
Per-region contexts persist in the region secondary object's `extra.region_context`. Memory contexts own a mapping list; PCI contexts own derived bus identity; data-table contexts hold a table pointer. Region objects persist initialization flags, handler attachment, node pointers, space ID, address, and length.

## Dependencies And Integration Points
Depends on operation-region dispatch and handler registration, namespace attached objects, PCI helper evaluation and derivation, ACPI `_HID`/`_CID`/`_ADR`/`_SEG`/`_BBN` execution helpers, OS memory unmapping, and interpreter lock management around `_REG`.

## Risks And Edge Cases
PCI config setup may be called while a root default handler is still attached and must re-associate to the nearest PCI root bridge without losing context creation. Missing `_ADR`, `_SEG`, or `_BBN` default to zero where permitted, but no enclosing device is an operand error. Memory deactivate must clear all mappings to avoid stale virtual addresses. `AOPOBJ_OBJECT_INITIALIZED` is set before handler discovery, so later handler installation paths must attach regions independently.

## Test Signals
Signals include memory mapping cleanup on deactivate, IO/default context passthrough, PCI root bridge detection by HID and CID, PCI ID derivation from `_ADR`/`_SEG`/`_BBN`, handler search from region parent to root, `_REG(CONNECT)` after attach, no-handler initialization succeeding without attachment, and data table mapping allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evrgnini.c -->
