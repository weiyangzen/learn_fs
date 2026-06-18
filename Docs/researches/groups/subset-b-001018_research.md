# Research: subset-b-001018

Grouped research for ACPICA namespace and parser files under `sources/distributed-fs/ceph-client/drivers/acpi/acpica`. Each section preserves the source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair2.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair2.c

## Purpose
`nsrepair2.c` implements complex repair logic for selected ACPI predefined method return values after normal predefined-object validation has found a mismatch or suspicious shape. It is a compatibility layer for common firmware defects: malformed `_HID`/`_CID` strings, undersized `_FDE`/`_GTM` buffers, reversed `_PRT` fields, invalid `_CST` entries, and unsorted power/thermal/light-response packages.

## Important APIs, types, and functions
The public entry is `acpi_ns_complex_repairs()`, which receives `struct acpi_evaluate_info`, the target namespace node, the prior validation status, and an in/out operand-object pointer. `struct acpi_repair_info` maps four-character ACPI names to `acpi_repair_function` handlers. Repair handlers cover `_ALR`, `_CID`, `_CST`, `_FDE`/`_GTM`, `_HID`, `_PRT`, `_PSS`, and `_TSS`. Shared helpers include `acpi_ns_match_complex_repair()`, `acpi_ns_check_sorted_list()`, `acpi_ns_sort_list()`, and `acpi_ns_remove_element()`.

## Control flow
`acpi_ns_complex_repairs()` first matches `node->name.ascii` against `acpi_ns_repairable_names`; non-matches return the original validation status. Matched names dispatch to a repair function. String repairs create replacement string objects, remove invalid leading `*`, uppercase characters, replace the object pointer, and drop the old reference. `_CID` applies the `_HID` string repair to either the returned string or every package element while preserving package element reference counts. `_FDE` and `_GTM` accept a valid 5-DWORD buffer or expand the known 5-byte firmware bug into a 20-byte DWORD buffer. Package sorting repairs validate outer package and subpackage shape, compare integer sort keys, and bubble-sort only when a disorder is detected. `_CST` also removes zero-count or type-zero C-state entries and rewrites the top-level count. `_TSS` suppresses sorting when a sibling `_PSS` exists because firmware may leave `_TSS` power fields meaningless in that case.

## State and persistence behavior
The file mutates transient ACPICA operand objects returned by method evaluation, not persistent firmware tables. State changes are reference-counted: replacement objects take over `*return_object_ptr`, original objects are released, removed package entries are dereferenced, and `info->return_flags` is marked with `ACPI_OBJECT_REPAIRED` when a visible repair occurs. The repaired object then flows to predefined validation and caller-facing object conversion.

## Dependencies and integration points
This code depends on namespace identity (`struct acpi_namespace_node`), operand object constructors in `acpi_ut_create_*`, reference management in `acpi_ut_remove_reference`, namespace lookup through `acpi_ns_get_node()`, and predefined warning/debug macros. It is called from ACPICA namespace evaluation validation, so its behavior directly affects public `acpi_evaluate_object*()` results and Linux driver enumeration.

## Risks and edge cases
The repairs intentionally accept firmware that violates the ACPI spec, so overly broad repair can mask real BIOS defects. Package repair assumes earlier validation has removed null elements before sorting. `_CST` indexes subpackage element 1 after only checking package count is nonzero, relying on prior type/length validation. `_PRT` has a warning call with a duplicated format string in the arguments, making that path worth compiler-format scrutiny. Reference-count mistakes here would leak or prematurely free returned operand objects.

## Test signals
Useful signals include ACPICA tests or firmware tables that return lower-case or starred IDs, 5-byte `_FDE`/`_GTM` buffers, reversed `_PRT` source fields, unsorted `_PSS`/`_TSS`/`_ALR`/`_CST` packages, zero-type C-state entries, and valid cases that should remain untouched. Memory-debug builds should show no leaks or double releases when repairs replace or remove objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nssearch.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nssearch.c

## Purpose
`nssearch.c` performs low-level ACPI namespace name lookup and optional insertion for a single name segment. It is the search primitive used by namespace loading, namespace reference resolution, and execution-time lookup.

## Important APIs, types, and functions
`acpi_ns_search_one_scope()` scans the child list of a namespace node for a 4-byte target name. `acpi_ns_search_parent_tree()` implements ACPI upward search rules for non-local object types. `acpi_ns_search_and_enter()` combines validation, one-scope search, parent search, override handling, error-if-found behavior, temporary/external flags, node creation, and installation.

## Control flow
Single-scope search walks `parent_node->child` through peer links and compares `node->name.integer` with `target_name`. When it finds a local method alias, it resolves the alias to the actual method node before returning it. Parent-tree search exits early at root or for object types marked local by `acpi_ns_local()`, otherwise it repeatedly searches enclosing parents with `ACPI_TYPE_ANY`.

`acpi_ns_search_and_enter()` repairs non-printable name bytes, searches the current scope, and if found applies special flags. `ACPI_NS_OVERRIDE_IF_FOUND` deletes children and either clears the attached object for runtime override or removes the node. `ACPI_NS_ERROR_IF_FOUND` converts a found node to `AE_ALREADY_EXISTS`. If not found and not in load pass 1, the parent tree is searched when `ACPI_NS_SEARCH_PARENT` is set. Execute mode never creates nodes. Load modes allocate a new namespace node, mark ASL compiler external or temporary flags as needed, then install it under the parent.

## State and persistence behavior
The file mutates the in-memory namespace tree only through `acpi_ns_search_and_enter()` in load modes or override mode. New nodes are attached to parent child/peer lists and inherit owner information via `acpi_ns_install_node()`. Override mode can delete subtree children, clear attached objects, change owner IDs, or remove the node entirely.

## Dependencies and integration points
Search depends on namespace node layout, `acpi_ns_create_node()`, `acpi_ns_install_node()`, `acpi_ns_remove_node()`, `acpi_ns_delete_children()`, `acpi_ut_repair_name()`, and global runtime namespace override policy. It is invoked by `acpi_ns_lookup()` and parser callbacks in `psobject.c`/dispatcher code when AML names are loaded or resolved.

## Risks and edge cases
Lookups are linear within a scope; this is intentional but can still affect pathological firmware tables with huge sibling lists. Parent search must not run during load pass 1 or it can resolve forward references incorrectly. Override behavior has high blast radius because it deletes children and attached objects. Method aliases require safe casting from `node->object` back to a namespace node.

## Test signals
Tests should cover local-only types, parent upsearch, execute-mode misses that do not create nodes, load-pass insertion, duplicate detection, runtime override with and without `acpi_gbl_runtime_namespace_override`, method aliases, invalid name repair warnings, and temporary/external flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nssearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsutils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsutils.c

## Purpose
`nsutils.c` provides common namespace utilities: path printing, type/scope property lookup, conversion between external ASL names and internal AML namestrings, ACPI handle validation, namespace teardown, and locked/unlocked node lookup.

## Important APIs, types, and functions
Important functions include `acpi_ns_print_node_pathname()`, `acpi_ns_get_type()`, `acpi_ns_local()`, `acpi_ns_get_internal_name_length()`, `acpi_ns_build_internal_name()`, `acpi_ns_internalize_name()`, `acpi_ns_externalize_name()`, `acpi_ns_validate_handle()`, `acpi_ns_terminate()`, `acpi_ns_opens_scope()`, `acpi_ns_get_node_unlocked()`, and `acpi_ns_get_node()`. Core data structures are `struct acpi_namestring_info`, `struct acpi_namespace_node`, `union acpi_generic_state`, and `struct acpi_buffer`.

## Control flow
Internalization first scans an external path for root prefixes, parent prefixes, path separators, and segment count, then allocates a zeroed internal string and writes root/parent/dual/multi-name prefixes plus padded four-byte name segments. Externalization parses internal prefixes, determines segment count, validates the encoded length, allocates the printable name, copies prefixes, repairs name segments for printable output, and inserts dots between segments. `acpi_ns_get_node_unlocked()` handles null path and root-only fast paths, internalizes the path, builds a scope wrapper, calls `acpi_ns_lookup()` in execute mode with `ACPI_NS_DONT_OPEN_SCOPE`, frees the internal path, and returns the node. `acpi_ns_get_node()` wraps the same logic in `ACPI_MTX_NAMESPACE`.

## State and persistence behavior
Most routines are conversion or query helpers. Allocated name buffers are returned to callers, who must free them. `acpi_ns_terminate()` is destructive: it deletes the namespace subtree rooted at `acpi_gbl_root_node`, locks the namespace, deletes the root node's attached object, and releases the lock.

## Dependencies and integration points
This file integrates with name parsing constants from `amlcode.h`, namespace property table `acpi_gbl_ns_properties`, global root node `acpi_gbl_root_node`, namespace lookup, mutex helpers, and pathname conversion helpers such as `acpi_ns_handle_to_pathname()`. Public namespace APIs in `nsxfname.c`, `nsxfobj.c`, and `nsxfeval.c` use these helpers to validate handles and resolve paths.

## Risks and edge cases
Name conversion must handle redundant root prefixes, parent-prefix-only strings, zero segments, dual and multi-name encodings, short segments padded with underscores, and malformed separators. `acpi_ns_validate_handle()` can only check the ACPICA descriptor type, so stale driver handles after table unload remain a broader lifecycle risk. `acpi_ns_externalize_name()` uses length checks that are necessary but must remain aligned with AML namestring encoding.

## Test signals
Strong tests include round-tripping names such as `\\_SB.PCI0`, `^^DEV0`, single segments, multi-segment names, redundant roots, bad separators, root-only lookup, null pathname lookup, locked and unlocked lookup parity, invalid handles, scope property checks for local and opens-scope types, and teardown under memory-debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nswalk.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nswalk.c

## Purpose
`nswalk.c` implements internal namespace iteration and a generic depth-first namespace walker. It supports public walking APIs, device discovery, debugging, and ACPICA subsystems that need callbacks over namespace nodes.

## Important APIs, types, and functions
`acpi_ns_get_next_node()` returns a parent's first child or a child's next peer. `acpi_ns_get_next_node_typed()` skips peers until it finds a requested object type or returns any type. `acpi_ns_walk_namespace()` is the main tree walker with descending and ascending callbacks, maximum depth, temporary-node policy, and optional namespace unlock around callbacks.

## Control flow
The walker normalizes `ACPI_ROOT_OBJECT` to `acpi_gbl_root_node`, rejects null starts, then enters a modified depth-first loop starting at the first child. For each node it optionally filters by type and temporary-node flag. Matching nodes invoke the descending callback on the first visit and ascending callback on the revisit. If `ACPI_NS_WALK_UNLOCK` is set, the namespace mutex is released before calling the callback and reacquired afterward. Callback statuses control traversal: `AE_CTRL_DEPTH` prunes children, `AE_CTRL_TERMINATE` ends successfully, and other failures propagate. The loop descends to children while below `max_depth`, revisits nodes after children, advances to peers, and bubbles to parents until it returns past the start.

## State and persistence behavior
The walker itself does not mutate namespace nodes. It maintains transient traversal state: parent, child, current level, child type, and whether the current node is being revisited. Callback code may mutate system state, which is why the unlock flag and temporary-node filtering matter.

## Dependencies and integration points
The implementation depends on child/peer/parent links in `struct acpi_namespace_node`, namespace mutex helpers, node flags such as `ANOBJ_TEMPORARY`, and callback status conventions. The public `acpi_walk_namespace()` wrapper in `nsxfeval.c` adds read locking and handle validation before calling this internal walker.

## Risks and edge cases
Unlocking around callbacks is necessary for clients that call back into ACPICA but exposes race risks from temporary method-created nodes, so default filtering is important. `max_depth` handling and revisit state are easy to regress because ascending callbacks are tied to the same node after child traversal. Callback errors must not leave the namespace mutex released.

## Test signals
Tests should check depth-limited traversal, type-filtered traversal, callbacks on descent and ascent, pruning with `AE_CTRL_DEPTH`, termination with `AE_CTRL_TERMINATE`, temporary-node exclusion and inclusion, root-object handling, and mutex release/reacquire behavior when callbacks invoke ACPICA APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nswalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfeval.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfeval.c

## Purpose
`nsxfeval.c` contains public namespace evaluation and traversal interfaces. It resolves handles and paths, converts external parameters to internal ACPICA operands, evaluates methods or objects, converts internal returns back to `union acpi_object`, walks the namespace for clients, filters device enumeration, and exposes attach/detach/get data helpers.

## Important APIs, types, and functions
Exports include `acpi_evaluate_object_typed()`, `acpi_evaluate_object()`, `acpi_walk_namespace()`, `acpi_get_devices()`, `acpi_attach_data()`, `acpi_detach_data()`, `acpi_get_data_full()`, and `acpi_get_data()`. Internal helpers include `acpi_ns_resolve_references()` and `acpi_ns_get_device_callback()`. Key data types are `struct acpi_evaluate_info`, `struct acpi_object_list`, `struct acpi_buffer`, `struct acpi_get_devices_info`, ACPICA operand objects, and namespace nodes.

## Control flow
`acpi_evaluate_object_typed()` validates a return buffer, resolves a target handle for diagnostics, calls `acpi_evaluate_object()`, and validates the returned external object type unless the requested type is `ACPI_TYPE_ANY`. On type mismatch it frees an auto-allocated buffer and clears the buffer length. `acpi_evaluate_object()` allocates evaluation info, validates the prefix handle, handles absolute versus relative path rules, converts incoming external parameters into an internal null-terminated operand list, calls `acpi_ns_evaluate()`, and if a return buffer was provided, rejects namespace-node returns, dereferences simple `Index`/`RefOf` references, sizes the object, initializes the caller buffer, and copies the internal object outward. It then removes the internal return reference under interpreter lock and frees converted parameters.

`acpi_walk_namespace()` validates callbacks and depth, acquires the namespace read lock to protect against table unload, locks the namespace mutex, validates the start handle, and delegates to `acpi_ns_walk_namespace()` with callback unlocks enabled. `acpi_get_devices()` walks devices from root and filters through `acpi_ns_get_device_callback()`, which optionally matches `_HID` or `_CID`, runs `_STA`, prunes absent/nonfunctional devices, and invokes the user callback. Data attachment APIs lock the namespace, validate handles, then delegate to namespace attachment helpers.

## State and persistence behavior
Evaluation creates transient internal operand objects for parameters and return values. Return buffers may be caller-supplied or allocated by ACPICA. Attached data persists on namespace nodes until detached or node deletion and is keyed by handler. Namespace walking holds locks to prevent persistent namespace deletion while callbacks see nodes.

## Dependencies and integration points
This file bridges public ACPI exports to `acpi_ns_evaluate()`, namespace lookup/validation, object conversion (`acpi_ut_copy_eobject_to_iobject`, `acpi_ut_copy_iobject_to_eobject`), interpreter locking, `_HID`/`_CID`/`_STA` utility execution, namespace data attachment helpers, and Linux driver enumeration paths.

## Risks and edge cases
Parameter count is capped at `ACPI_METHOD_NUM_ARGS` with a warning, so excess caller arguments are silently ignored after logging. Reference returns inside packages are not recursively dereferenced. Device filtering intentionally avoids `_STA` until HID/CID match when a HID is requested, which changes side effects compared with unconditional `_STA`. Locking is subtle because callbacks may call ACPICA while table unload protection must remain in force. Auto-allocated buffers must be freed on typed-evaluation mismatch.

## Test signals
Evaluation tests should cover null and invalid handles, absolute/relative path rules, methods with zero and many arguments, excess argument warnings, no-return methods, typed return mismatch cleanup, `RefOf` and `Index` top-level returns, too-small return buffers, namespace-node return rejection, device HID/CID matching, `_STA` pruning, attach/detach/get data, and namespace walk callbacks that call back into ACPICA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfeval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfname.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfname.c

## Purpose
`nsxfname.c` provides public namespace name-oriented APIs: path-to-handle lookup, handle-to-name conversion, object/device information collection, and dynamic installation of a single control method from a DSDT/SSDT buffer.

## Important APIs, types, and functions
Exports include `acpi_get_handle()`, `acpi_get_name()`, `acpi_get_object_info()`, and `acpi_install_method()`. `acpi_ns_copy_device_id()` is a local helper that packs variable-length PNP ID strings into an allocated `struct acpi_device_info` buffer. The file uses `struct acpi_pnp_device_id`, `struct acpi_pnp_device_id_list`, `struct acpi_device_info`, `struct acpi_table_header`, parser state, namespace nodes, and method operand objects.

## Control flow
`acpi_get_handle()` validates output and path parameters, converts an optional parent handle to a prefix node, accepts fully qualified names without a parent, rejects relative names without a parent, special-cases the root path, then calls `acpi_ns_get_node()` with no upsearch. `acpi_get_name()` validates buffer and name type, locks the namespace, and calls either full-path or single-name conversion.

`acpi_get_object_info()` locks only long enough to validate the handle and snapshot node type/name/parameter count. For devices and processors it then executes selected simple methods (`_HID`, `_UID`, `_CID`, `_CLS`, `_ADR`, `_SxW`, `_SxD`) and uses success to size and populate one allocated `acpi_device_info` buffer. HID/CID values are also checked for PCI root bridge classification. `acpi_install_method()` validates a DSDT/SSDT buffer containing a MethodOp, parses the method namestring/package length/flags from raw AML, preallocates an AML copy and method object, creates or finds a method node, initializes method metadata, attaches the new object, and marks the node buffer as dynamically allocated.

## State and persistence behavior
Handle/name functions are read-only. `acpi_get_object_info()` allocates a caller-owned information buffer and frees temporary ID buffers before return. `acpi_install_method()` persists a new or replacement method object in the namespace and stores copied AML that must later be freed because `ANOBJ_ALLOCATED_BUFFER` is set.

## Dependencies and integration points
The file depends on namespace lookup and validation helpers, path conversion helpers, parser helpers (`acpi_ps_peek_opcode`, `acpi_ps_get_opcode_size`, `acpi_ps_get_next_package_end`, `acpi_ps_get_next_namestring`), namespace attachment, object construction, simple predefined-method execution, and exported ACPI symbols used by kernel drivers.

## Risks and edge cases
`acpi_get_object_info()` intentionally avoids complex methods such as `_SUB` and `_STA` because discovery-time evaluation can touch operation regions. Size calculation must match the later packed-copy layout for HID/UID/CID/CLS strings. `acpi_install_method()` assumes the input table contains exactly the expected single MethodOp shape and that raw AML package parsing cannot run past the buffer. Replacing an existing method must not leak the old attached method object.

## Test signals
Signals include fully qualified and parent-relative `acpi_get_handle()` lookups, root path lookup, invalid relative lookup, name buffer sizing, device info with each optional ID/method present or absent, PCI root bridge flag detection through HID and CID, method parameter count reporting, invalid table signatures, non-method AML rejection, existing non-method node rejection, and successful replacement of an existing method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfobj.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfobj.c

## Purpose
`nsxfobj.c` implements small public object-oriented namespace APIs for querying an object's type, parent, and next child/peer by type. These are exported ACPICA interfaces used by drivers and enumeration code.

## Important APIs, types, and functions
The exported functions are `acpi_get_type()`, `acpi_get_parent()`, and `acpi_get_next_object()`. They rely on `acpi_ns_validate_handle()`, `acpi_ns_get_next_node_typed()`, `ACPI_MTX_NAMESPACE`, `acpi_handle`, `acpi_object_type`, and `struct acpi_namespace_node`.

## Control flow
`acpi_get_type()` validates the output pointer, special-cases `ACPI_ROOT_OBJECT` as `ACPI_TYPE_ANY`, locks the namespace, validates the handle, copies `node->type`, and unlocks. `acpi_get_parent()` validates output, returns `AE_NULL_ENTRY` for root, locks, validates the handle, returns `node->parent` as a handle, and reports `AE_NULL_ENTRY` if no parent exists. `acpi_get_next_object()` validates the requested external type, locks, either validates the parent when no child is supplied or validates the child and ignores parent, asks `acpi_ns_get_next_node_typed()` for the next matching node, and writes the returned handle when the output pointer is non-null.

## State and persistence behavior
The file is query-only and does not mutate namespace state. It depends on the namespace mutex so the child/parent/peer links and node type fields remain stable while handles are translated.

## Dependencies and integration points
These APIs are thin wrappers over internal namespace traversal and handle validation. They are commonly paired with `acpi_get_name()`, `acpi_get_object_info()`, and `acpi_walk_namespace()` by driver discovery code that enumerates child objects without a callback walker.

## Risks and edge cases
Root handling differs by API: root has type `ANY` but no parent. `acpi_get_next_object()` permits a null `ret_handle`, in which case success still means a node exists but no handle is returned. Passing a child handle from a different parent ignores the parent parameter, matching the documented iteration contract but surprising callers that expect parent validation.

## Test signals
Tests should cover root type and parent behavior, invalid handles, type filtering, `ACPI_TYPE_ANY`, first-child iteration via null child, peer iteration via prior child, end-of-list `AE_NOT_FOUND`, and calls with null output handle to `acpi_get_next_object()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psargs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psargs.c

## Purpose
`psargs.c` decodes AML opcode arguments into parse objects. It handles package lengths, AML namestrings and namespace-assisted namepaths, simple constants, strings, field lists, byte lists, targets, supernames, and variable argument lists.

## Important APIs, types, and functions
Exports and shared parser helpers include `acpi_ps_get_next_package_end()`, `acpi_ps_get_next_namestring()`, `acpi_ps_get_next_namepath()`, `acpi_ps_get_next_simple_arg()`, and `acpi_ps_get_next_arg()`. Local helpers are `acpi_ps_get_next_package_length()`, `acpi_ps_get_next_field()`, and `acpi_ps_free_field_list()`. The file uses `struct acpi_parse_state`, `struct acpi_walk_state`, `union acpi_parse_object`, namespace nodes, method operand objects, and argument type constants such as `ARGP_TERMARG`, `ARGP_FIELDLIST`, and `ARGP_SUPERNAME`.

## Control flow
Package-length decoding reads the low two count bits from byte 0, consumes up to four bytes, and reconstructs the 28-bit length. Namestring decoding skips root/parent prefixes, handles null, dual-name, multi-name, and single-segment forms, and advances the AML pointer. Namepath decoding initializes an internal namepath op, looks up the path in the namespace in execute mode with parent search, detects control-method invocations when allowed, rewinds AML for target/supername ambiguity, creates a method-call op with a child namepath op, and sets `walk_state->arg_count` from the method's parameter count. Not-found statuses are tolerated in load passes, `CondRefOf`, and package construction contexts.

Simple arguments copy fixed-width integer data, strings, or raw namestrings. Field-list parsing repeatedly decodes named fields, reserved fields, access fields, extended access fields, and connection fields until package end. `acpi_ps_get_next_arg()` dispatches by expected argument type: some types immediately allocate and fill parse ops, package length updates `pkg_end`, complex term arguments set `walk_state->arg_count`, and variable lists set `ACPI_VAR_ARGS`.

## State and persistence behavior
The file mutates parser state by advancing `parser_state->aml`, setting `pkg_end`, and appending allocated parse objects. It may set `walk_state->arg_count` and rewrite `walk_state->parser_state.aml` when a namepath is actually a method call. Allocated field-list nodes are freed on partial allocation failure.

## Dependencies and integration points
It integrates parser utilities (`acpi_ps_alloc_op`, `acpi_ps_append_arg`, `acpi_ps_init_op`), namespace lookup (`acpi_ns_lookup`, `acpi_ns_get_attached_object`), dispatcher method error conversion, AML opcode helpers, ASL compiler comment capture hooks, and field/connection AML grammar. `psloop.c` calls it to populate each operation's operands.

## Risks and edge cases
AML pointer arithmetic must stay within package boundaries. Method-call detection is grammar-sensitive because a bare name can be a namepath, target, supername, or method invocation depending on expected argument type. Not-found tolerance in package construction can hide errors until later phases. Connection-field parsing has several nested length and opcode interpretations that must agree with AML resource descriptors. Allocation failures in partially built field lists need complete cleanup.

## Test signals
Useful tests include package length encodings with 1 to 4 bytes, null/root/parent/dual/multi namestrings, method-call arity detection, forward references in load passes, `CondRefOf` missing names, missing names in packages with and without slack behavior, all simple integer sizes, strings, field/access/extended/connection entries, byte lists, targets that are method calls, and malformed field-list allocation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psargs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psloop.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psobject.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopcode.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopcode.c

## Purpose
`psopcode.c` defines the master AML opcode information table, `acpi_gbl_aml_op_info`. This table is the parser and interpreter contract for every AML opcode ACPICA recognizes: names, parser argument templates, interpreter argument templates, result object types, opcode classes, execution types, and flags.

## Important APIs, types, and functions
The file exports data rather than functions. `acpi_gbl_aml_op_info[AML_NUM_OPCODES]` is an array of `struct acpi_opcode_info` entries created with `ACPI_OP()`. It includes standard AML opcodes, extended two-byte opcodes, internal parser-only opcodes such as `-NamePath-`, `-MethodCall-`, `-ByteList-`, field helper opcodes, return-value placeholders, unknown/ascii/prefix pseudo-ops, and newer ACPI opcodes such as `External`, `Comment`, `Timer`, and `DataTableRegion`.

## Control flow
There is no runtime control flow in this file. Runtime consumers index this table through lookup tables in `psopinfo.c`. Parser code reads `parse_args`, `class`, `type`, and flags to decide how to parse, whether to create namespace nodes, whether to defer bodies, whether an op has targets or return values, and whether a parse object needs extended storage. Interpreter code reads `runtime_args`, object type, and flags to prepare operands and dispatch execution.

## State and persistence behavior
The table is immutable global parser/interpreter metadata. Its values effectively define persistent ACPICA behavior for all AML parsing and execution. Any edit changes how firmware bytecode is decoded throughout the subsystem.

## Dependencies and integration points
The table depends on constants from `acopcode.h` and `amlcode.h`. It is consumed by `acpi_ps_get_opcode_info()`, `acpi_ps_get_opcode_name()`, `acpi_ps_alloc_op()`, `acpi_ps_get_arguments()`, parse-tree traversal, dispatcher operand resolution, and disassembler/debug output.

## Risks and edge cases
Incorrect flags have wide blast radius. Missing `AML_DEFER` can parse executable bodies too early; missing `AML_NAMED` or namespace flags can prevent namespace object creation; wrong argument templates desynchronize the AML pointer; wrong execution flags can break operand resolution or target handling. Internal pseudo-op entries must align with index lookup tables and `AML_NUM_OPCODES`.

## Test signals
Signals include full ACPICA table-load suites, opcode-by-opcode disassembly round trips, parser pointer synchronization across all opcode templates, namespace creation for all named opcodes, deferred parsing for methods/regions/buffers/packages/create fields, method-call pseudo-op behavior, and lookup-table consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopinfo.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopinfo.c

## Purpose
`psopinfo.c` implements AML opcode metadata lookup helpers and the direct opcode-to-table-index maps used by the parser. It is the fast path from raw AML opcode bytes to `struct acpi_opcode_info`.

## Important APIs, types, and functions
Key functions are `acpi_ps_get_opcode_info()`, `acpi_ps_get_opcode_name()`, and `acpi_ps_get_argument_count()`. Global tables include `acpi_gbl_argument_count[]`, `acpi_gbl_short_op_index[256]`, and `acpi_gbl_long_op_index[NUM_EXTENDED_OPCODE]`. The helpers return entries from `acpi_gbl_aml_op_info`.

## Control flow
`acpi_ps_get_opcode_info()` first distinguishes one-byte opcodes from extended opcodes by checking the high byte. One-byte opcodes index `acpi_gbl_short_op_index`. Extended opcodes must have the extended prefix and a second byte at or below `MAX_EXTENDED_OPCODE`, then index `acpi_gbl_long_op_index`. Unknowns return the `_UNK` opcode-info entry, and ASL compiler debug builds can name raw-data pseudo opcodes for diagnostics. `acpi_ps_get_opcode_name()` returns the table name only when disassembler or debug output is enabled; otherwise it returns a fixed unavailable string. `acpi_ps_get_argument_count()` maps execution type classes to counts for target/operand marking.

## State and persistence behavior
All state is immutable global lookup data. The functions are pure lookups except for debug output. The tables persist for the lifetime of ACPICA and must stay synchronized with `psopcode.c`.

## Dependencies and integration points
This file integrates with `psopcode.c`, AML constants, parser object allocation, opcode classification in `psobject.c`, debug output, disassembler builds, and target-count logic in `pstree.c`/`psobject.c`.

## Risks and edge cases
The guarantee that `acpi_ps_get_opcode_info()` always returns a valid pointer is essential. A wrong short or long index maps raw AML to the wrong grammar. Extended-opcode bounds must prevent out-of-range table access. Non-debug builds returning `"OpcodeName unavailable"` can limit diagnostics unless debug/disassembler is enabled.

## Test signals
Tests should verify every valid AML opcode maps to the intended `acpi_gbl_aml_op_info` index, unknown bytes map to `_UNK`, ASCII and prefix bytes map to pseudo classes, extended opcodes respect bounds, opcode names are stable in debug builds, and argument counts match execution type constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psopinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psparse.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psparse.c

## Purpose
`psparse.c` provides top-level AML parsing orchestration and parser-state transitions. It peeks opcode size, completes parse ops, interprets callback control statuses, manages nested method execution through walk-state stacks, and performs final method/table parse cleanup.

## Important APIs, types, and functions
Exports include `acpi_ps_get_opcode_size()`, `acpi_ps_peek_opcode()`, `acpi_ps_complete_this_op()`, `acpi_ps_next_parse_state()`, and `acpi_ps_parse_aml()`. Key state types are `struct acpi_walk_state`, `struct acpi_thread_state`, `struct acpi_parse_state`, `union acpi_parse_object`, and `union acpi_operand_object`.

## Control flow
Opcode helpers return one or two-byte AML opcode identity without or with size calculation. `acpi_ps_complete_this_op()` stops opcode tracing, and when parse flags request tree deletion it unlinks the completed op from its parent, optionally inserts a return-value placeholder for contexts that need a value node after subtree deletion, then deletes the subtree. `acpi_ps_next_parse_state()` maps dispatcher statuses to AML pointer movement: terminate jumps to AML end, break/continue/pending jump to the last while, true skips the matching else package, false jumps to current package end, and transfer records method-call metadata.

`acpi_ps_parse_aml()` creates a thread state, pushes the initial walk state, installs it as `acpi_gbl_current_walk_list`, then repeatedly calls `acpi_ps_parse_loop()`. `AE_CTRL_TRANSFER` invokes `acpi_ds_call_control_method()` and continues with the newly pushed walk state. Completed or failed walks are popped, scope stacks are cleared, control methods are terminated when needed, parse scopes are cleaned, return or implicit-return objects are propagated to callers or released, and walk states are deleted. At final exit it releases all mutexes held by the thread, deletes thread state, and restores the previous global walk list.

## State and persistence behavior
Persistent state includes the global current walk list during execution and method objects that may be marked pending serialized after reentrancy-related `AE_ALREADY_EXISTS`. Transient state includes thread/walk stacks, parser scopes, control states, return descriptors, implicit return objects, and parse subtrees. The function owns cleanup of these objects on every exit path.

## Dependencies and integration points
This file is between the parser loop and dispatcher/interpreter: it calls `acpi_ps_parse_loop()`, `acpi_ds_call_control_method()`, `acpi_ds_restart_control_method()`, `acpi_ds_terminate_control_method()`, `acpi_ex_enter_interpreter()`/`exit`, mutex release helpers, trace hooks, parse-tree deletion, and method error reporting.

## Risks and edge cases
Nested method execution is iterative but state-heavy; return object ownership is easy to mishandle. Slack-mode implicit returns add alternate return paths. If `acpi_gbl_current_walk_list` is not restored after errors, debugger and nested execution state become corrupt. Parse-tree deletion with replacement placeholders must not detach needed AML metadata for deferred objects. Reentrancy auto-serialization only triggers for a narrow error pattern.

## Test signals
Tests should cover simple and nested method execution, methods returning values and no values, implicit-return slack mode, parse errors inside methods, method-call transfer and restart, break/continue/if/else pointer transitions, subtree deletion mode, module-level load errors, mutex release on thread exit, and pending-serialized marking for reentrant method namespace creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psscope.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psscope.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/pstree.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/pstree.c

## Purpose
`pstree.c` provides parse-tree argument access, append, and depth-first traversal helpers for ACPICA parser op trees.

## Important APIs, types, and functions
`acpi_ps_get_arg()` returns the nth linked argument op. `acpi_ps_append_arg()` appends one or more linked argument ops to an op and sets parent pointers. `acpi_ps_get_depth_next()` returns the next parse op in depth-first order from an origin. An obsolete `acpi_ps_get_child()` helper remains under `ACPI_OBSOLETE_FUNCTIONS`.

## Control flow
Argument lookup first gets opcode metadata and returns null for unknown opcodes or opcodes without `AML_HAS_ARGS`. It then walks `common.value.arg` and `common.next` until the requested index. Append validates that the parent opcode can have arguments, appends at the tail or initializes the list, then walks every linked argument being appended to set `common.parent` and increment the parent's argument-list length. Depth-first traversal first tries the current op's first argument, then its next sibling, then climbs parent links looking for a parent's sibling; it stops when it reaches the origin boundary.

## State and persistence behavior
`acpi_ps_append_arg()` mutates parse tree topology, parent pointers, sibling links, and the parent argument-list length. The lookup and traversal helpers are read-only except for ASL comment/filename labeling macros in compiler builds.

## Dependencies and integration points
These helpers depend on opcode metadata from `acpi_ps_get_opcode_info()`, parse object layout, AML flags, and ASL compiler comment macros. Parser construction in `psargs.c` and `psobject.c`, parse-tree deletion in `pswalk.c`, and disassembler/debug walkers rely on this file.

## Risks and edge cases
Appending a linked chain increments the parent length for every node in the chain, so callers must not pass an unintended sibling list. Unknown opcodes are ignored rather than asserted. Depth traversal must respect the origin boundary or it can walk outside a requested subtree. Parent pointers must be set before deletion and traversal paths depend on them.

## Test signals
Tests should cover appending first and subsequent args, appending chained args, retrieving existing and missing arg indexes, opcodes without arguments, unknown opcode behavior, depth-first traversal through child and sibling paths, stopping at origin, and tree integrity after parser construction and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/pstree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psutils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psutils.c

## Purpose
`psutils.c` contains parser-only utility functions for parse-op allocation, initialization, freeing, and simple parse-op name helpers.

## Important APIs, types, and functions
Functions include `acpi_ps_create_scope_op()`, `acpi_ps_init_op()`, `acpi_ps_alloc_op()`, `acpi_ps_free_op()`, `acpi_ps_is_leading_char()`, `acpi_ps_get_name()`, and `acpi_ps_set_name()`. The file uses parser object caches `acpi_gbl_ps_node_cache` and `acpi_gbl_ps_node_ext_cache`, opcode metadata, parse-op flags, and ASL comment capture globals.

## Control flow
`acpi_ps_create_scope_op()` allocates a `AML_SCOPE_OP` and names it as the root. `acpi_ps_init_op()` sets descriptor type and AML opcode, and in disassembler builds copies the opcode name into the op. `acpi_ps_alloc_op()` chooses a generic parse op by default, an extended op for deferred or named opcodes, or a bytelist op for `AML_INT_BYTELIST_OP`; it acquires from the corresponding object cache, initializes the op, records the AML pointer and parse-op flags, updates current scope for scope ops, and transfers captured comments when enabled. `acpi_ps_free_op()` clears comment metadata and releases to the same cache family based on flags.

## State and persistence behavior
The file manages transient parse-op cache objects and writes global parser/comment state such as `acpi_gbl_current_scope` in scope-op allocation. It does not create namespace objects or operand objects, but bad allocation/free behavior affects every parse.

## Dependencies and integration points
It depends on opcode metadata from `psopinfo.c`, ACPICA object cache functions, parse object layout, AML constants, and ASL compiler/disassembler comment macros. All parser construction and deletion paths call these helpers either directly or through `psargs.c`, `psobject.c`, and `pswalk.c`.

## Risks and edge cases
The cache selected for allocation must match the flag used for free. Flags are derived from opcode metadata, so metadata bugs can cause size mismatches. Generic ops cannot hold named fields; `acpi_ps_get_name()` and `acpi_ps_set_name()` intentionally no-op for generic ops. Comment capture paths are build-configuration dependent and can leak metadata if not cleared.

## Test signals
Signals include allocation/free for generic, named, deferred, and bytelist ops, cache leak checking, scope-op root name initialization, disassembler opcode-name population, leading-character classification, get/set name behavior for generic versus extended ops, and comment capture/clear behavior in ASL compiler builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/pswalk.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/pswalk.c

## Purpose
`pswalk.c` provides parse-tree deletion. It walks a parser subtree without recursion and frees every parse op through the parser object-cache layer.

## Important APIs, types, and functions
The single exported function is `acpi_ps_delete_parse_tree()`. It uses `acpi_ps_get_arg()` to descend, `acpi_ps_free_op()` to release nodes, optional debug output through `acpi_ps_get_opcode_name()`, and AML opcode constants for namepath/string debug printing.

## Control flow
Deletion starts at `subtree_root` and performs a manual depth-first traversal using `op`, `next`, `parent`, and a debug level counter. On descent it optionally prints the parse-tree node, then tries the first argument. If a child exists, it descends. When no child remains or the traversal is returning from a child, it records the node's sibling and parent, frees the current op, exits if it just freed the root, otherwise moves to the sibling or bubbles to the parent.

## State and persistence behavior
This function destroys parse-tree state and returns parse ops to caches. It does not unlink nodes from any parent before freeing; callers must have already isolated the subtree or be intentionally deleting the complete tree. Debug printing is the only side effect outside memory/cache state.

## Dependencies and integration points
It is called by parser cleanup in `psparse.c`, op completion in `acpi_ps_complete_this_op()`, method/table execution cleanup in `psxface.c`, and error paths in `psobject.c`. It depends on correct parent/next/arg links from `pstree.c` and allocation flags from `psutils.c`.

## Risks and edge cases
Because deletion is non-recursive, it avoids stack depth risk from deeply nested AML, but it depends on valid parent pointers. Corrupt parse-tree links could cause cycles or use-after-free traversal. Callers deleting a subtree still linked into a parent must unlink or replace it first, as `psparse.c` does.

## Test signals
Tests should include deleting single-node trees, trees with deep child chains, wide sibling lists, mixed child/sibling structures, debug parse-tree output, deletion after subtree replacement, and memory-cache accounting that confirms every allocated op is released once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/pswalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psxface.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/psxface.c -->
