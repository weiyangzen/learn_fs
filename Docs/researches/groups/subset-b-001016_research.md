# subset-b-001016 ACPICA executor and hardware research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg1.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg1.c

## Purpose
`exoparg1.c` executes AML opcodes with zero or one input argument, including `Timer`, synchronization/control side effects, `Store`, conversion operators, `RefOf`, `DerefOf`, `SizeOf`, `ObjectType`, increment/decrement, and BCD/bit search helpers. It is part of the ACPICA executor dispatch layer and assumes the dispatcher has already parsed the opcode form and resolved operands to the expected stack slots.

## Important APIs, Types, and Functions
Exported executor entry points are `acpi_ex_opcode_0A_0T_1R()`, `acpi_ex_opcode_1A_0T_0R()`, `acpi_ex_opcode_1A_1T_1R()`, and `acpi_ex_opcode_1A_0T_1R()`. They operate on `struct acpi_walk_state`, `walk_state->opcode`, `walk_state->operands[]`, and `walk_state->result_obj`. Important dependencies include `acpi_ut_create_integer_object()`, `acpi_ex_store()`, `acpi_ex_resolve_operands()`, `acpi_ex_resolve_multiple()`, `acpi_ex_get_object_reference()`, `acpi_ex_read_data_from_field()`, `acpi_ds_method_data_get_value()`, `acpi_ds_get_buffer_arguments()`, and `acpi_ds_get_package_arguments()`.

## Control Flow, State, and Persistence
Each exported function switches on the AML opcode and writes either a new return descriptor or side effects into ACPI objects. `Timer` returns the OS timer. `Release`, `Reset`, `Signal`, `Sleep`, `Stall`, and `Unload` delegate to mutex/event/table/OS wrappers. `Store` calls `acpi_ex_store()` and returns the stored source object unless a field store already produced a result. Conversion and bit/BCD opcodes allocate temporary integer/string/buffer objects, store into the target operand, and retain the result through `walk_state->result_obj`. `DerefOf` has the most branching: it handles locals/args, `RefOf`, strings that name namespace nodes, device/thermal namespace nodes, index references into buffers/packages, and field references that require an actual field read. Persistent effects are reference-count changes, target stores, field reads/writes through downstream helpers, namespace/table load effects from `Load`, and interpreter-visible `result_obj` ownership.

## Dependencies and Integration Points
This file is reached from ACPICA dispatcher opcode execution after operand resolution. It integrates with namespace nodes, method local/arg storage, field access, table loading, conversion helpers, and OS synchronization/time services. It also depends on global integer sizing such as `acpi_gbl_integer_nybble_width` and `acpi_gbl_integer_byte_width`.

## Risks and Test Signals
Risks include reference leaks or premature drops around `Store`, `CondRefOf`, `DerefOf`, and increment/decrement; incorrect handling of uninitialized package elements; BCD overflow and invalid digit detection; 32-bit versus 64-bit integer width behavior; and string namespace lookup failures. Tests should exercise all listed opcodes, stores to locals/args/names/fields/index targets, dereferencing nested references, `DerefOf` on string paths, buffer and package `SizeOf`, missing `CondRefOf` targets, BCD boundary values, and error paths for unsupported obsolete shift-bit opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg2.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg2.c

## Purpose
`exoparg2.c` implements executor entry points for AML opcodes with two input operands, covering `Notify`, `Divide`, arithmetic/logical operators, `Mod`, concatenation, `ToString`, `ConcatenateResTemplate`, `Index`, `Acquire`, and `Wait`.

## Important APIs, Types, and Functions
The exported handlers are `acpi_ex_opcode_2A_0T_0R()`, `acpi_ex_opcode_2A_2T_1R()`, `acpi_ex_opcode_2A_1T_1R()`, and `acpi_ex_opcode_2A_0T_1R()`. Key dependencies include `acpi_ev_is_notify_object()`, `acpi_ev_queue_notify_request()`, `acpi_ut_divide()`, `acpi_ex_do_math_op()`, `acpi_ex_do_concatenate()`, `acpi_ex_concat_template()`, `acpi_ex_store()`, `acpi_ex_do_logical_numeric_op()`, `acpi_ex_do_logical_op()`, `acpi_ex_acquire_mutex()`, and `acpi_ex_system_wait_event()`.

## Control Flow, State, and Persistence
`Notify` validates the target namespace node and queues asynchronous notify delivery after the current method completes. `Divide` allocates quotient and remainder objects, stores remainder and quotient into two targets, and returns the quotient. Math and `Mod` allocate integer results and store them into the target. `ToString` copies bytes from a buffer until the requested length, buffer length, or NUL byte. `Index` builds a `ACPI_TYPE_LOCAL_REFERENCE` object that points to a buffer/string byte or package element, stores that reference into the target, and returns it. `Acquire` and `Wait` convert `AE_TIME` into an AML logical true return while preserving other errors.

## Dependencies and Integration Points
This file bridges AML operators to event dispatch, resource-template concatenation, package/buffer/string indexing, mutex and event waits, and target storage. It relies on opcode metadata flags `AML_MATH`, `AML_LOGICAL_NUMERIC`, and `AML_LOGICAL` from the parser tables.

## Risks and Test Signals
Risks include swapped quotient/remainder semantics, index references outliving the parent buffer/package incorrectly, off-by-one range checks for strings/buffers/packages, asynchronous notify ordering, and timeout truth-value semantics for `Acquire`/`Wait`. Tests should include division by zero, divide target ordering, concatenation of supported types, `ToString` truncation and NUL handling, index into each supported container, out-of-range index errors, notify on invalid object types, and timed wait/acquire behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg3.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg3.c

## Purpose
`exoparg3.c` handles triadic AML opcode execution, specifically `Fatal`, `External`, and `Mid`.

## Important APIs, Types, and Functions
The exported functions are `acpi_ex_opcode_3A_0T_0R()` and `acpi_ex_opcode_3A_1T_1R()`. Important types include `struct acpi_signal_fatal_info`, `struct acpi_walk_state`, and internal string/buffer operand objects. Dependencies include `acpi_os_signal()`, `acpi_ut_create_internal_object()`, `ACPI_ALLOCATE_ZEROED`, `acpi_ex_store()`, and debug/error macros.

## Control Flow, State, and Persistence
`Fatal` constructs a fatal signal payload from three integer operands, reports a BIOS error, calls the OS fatal signal hook, and returns either `AE_ERROR` or `AE_OK` depending on `ACPI_CONTINUE_ON_FATAL`. `External` is ignored at runtime after logging because it should only aid disassembly. `Mid` creates a new string or buffer object with the source type, clamps the requested slice to source length, allocates storage for non-empty output, copies the selected bytes, marks buffers data-valid, stores the result to the target, and exposes it as `walk_state->result_obj`.

## Dependencies and Integration Points
This file integrates AML fatal signaling with the host OS and implements `Mid` in the same store/result convention used by other executor opcode files. It relies on operand resolution to guarantee source type and integer arguments before execution.

## Risks and Test Signals
Risks include host-specific fatal signal behavior, configuration-dependent fatal return status, slice length overflow/truncation around large indices, zero-length buffer ownership, and result cleanup when target storage fails. Tests should cover `Fatal` signal payloads, `External` no-op execution, `Mid` for strings and buffers, index beyond end, zero requested length, truncation at source end, and allocation/store failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg6.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg6.c

## Purpose
`exoparg6.c` implements AML six-argument operators: package `Match` and `LoadTable`.

## Important APIs, Types, and Functions
The main entry point is `acpi_ex_opcode_6A_0T_1R()`. The local helper `acpi_ex_do_match()` evaluates `MTR`, `MEQ`, `MLE`, `MLT`, `MGE`, and `MGT` terms. Dependencies include `acpi_ex_do_logical_op()` for type-aware comparisons, `acpi_ut_create_integer_object()`, and `acpi_ex_load_table_op()`.

## Control Flow, State, and Persistence
`Match` validates both match operator IDs, validates `start_index` against the package count, creates an integer result initialized to all ones, then scans package elements from the start index. NULL package elements are non-matches. Both match terms must pass before the result is changed to the matching index. `LoadTable` delegates table loading and returns the descriptor produced by the loader.

## Dependencies and Integration Points
`Match` relies on the common logical comparison engine so package elements can be implicitly converted to the match object type. `LoadTable` integrates with ACPICA table loading and returns a DDB handle-style object through the normal result path.

## Risks and Test Signals
Risks include reversed comparison semantics in `acpi_ex_do_match()`, invalid operator acceptance, package boundary errors, NULL package element handling, and table loader reference ownership. Tests should include every match operator, mixed integer/string/buffer package elements, no-match all-ones return, start index at and beyond package length, NULL elements, and `LoadTable` success/failure with DDB handle lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exprep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exprep.c

## Purpose
`exprep.c` prepares AML field descriptors for region fields, bank fields, and index fields. It decodes AML field flags, computes access granularity and offsets, attaches constructed field objects to namespace nodes, and preserves enough metadata for later field reads/writes.

## Important APIs, Types, and Functions
Exported functions are `acpi_ex_prep_common_field_object()` and `acpi_ex_prep_field_value()`. Internal helpers include `acpi_ex_decode_field_access()` and, under `ACPI_UNDER_DEVELOPMENT`, `acpi_ex_generate_access()`. Important inputs are `struct acpi_create_field_info`, `union acpi_operand_object`, `ACPI_COMMON_FIELD_INFO`, AML field flags, region/register namespace nodes, and optional connection/resource buffer metadata.

## Control Flow, State, and Persistence
Common preparation stores field flags, attributes, bit length, access byte width, base byte offset, and starting bit offset. Access types map to byte/word/dword/qword or byte-oriented `AnyAcc`, with buffer fields forced to one-byte alignment. `acpi_ex_prep_field_value()` validates region-backed fields, allocates the field object, initializes common state, then fills type-specific references: region fields point at the region object and optional serial/GPIO connection resource; bank fields keep region and bank register objects plus AML source locations; index fields keep index/data register objects and compute the index value from byte offset. The new object is attached to the field namespace node and the local reference is dropped.

## Dependencies and Integration Points
This file depends on namespace object attachment, dispatcher lazy argument evaluation for connection buffers, AML parse object metadata for bank fields, and later field access code that consumes `common_field`, `field`, `bank_field`, or `index_field` members. EC regions receive a special wider access width for multi-byte reads when possible.

## Risks and Test Signals
Risks include incorrect bit/byte offset math, access width mismatches, stale resource buffer pointers, missing reference increments for bank/index backing objects, invalid region-node acceptance, and EC access-width compatibility. Tests should create byte/word/dword/qword/buffer fields at unaligned bit offsets, region/bank/index fields, serial-bus/GPIO connection fields, EC multi-byte fields, invalid region targets, and teardown/reference-count scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exprep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exregion.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exregion.c

## Purpose
`exregion.c` provides ACPICA default address-space handlers for operation regions: system memory, system I/O, PCI configuration, CMOS, PCI BAR, and data table spaces.

## Important APIs, Types, and Functions
Handlers include `acpi_ex_system_memory_space_handler()`, `acpi_ex_system_io_space_handler()`, `acpi_ex_pci_config_space_handler()` under `ACPI_PCI_CONFIGURED`, `acpi_ex_cmos_space_handler()`, `acpi_ex_pci_bar_space_handler()` under `ACPI_PCI_CONFIGURED`, and `acpi_ex_data_table_space_handler()`. Important context types include `struct acpi_mem_space_context`, `struct acpi_mem_mapping`, `struct acpi_pci_id`, and `struct acpi_data_table_mapping`.

## Control Flow, State, and Persistence
The system-memory handler validates 8/16/32/64-bit widths, optionally rejects misaligned accesses, reuses a cached mapping if it covers the requested range, searches prior mappings, or maps a new page-limited range and links it into the region context. It then performs typed reads or writes through `ACPI_GET*`/`ACPI_SET*`. The system-I/O handler delegates reads/writes to port helpers. The PCI config handler casts region context to a PCI ID and calls OS PCI config accessors. CMOS and PCI BAR handlers are stubs that return success. The data-table handler computes an offset into the mapped table and copies bytes to or from the caller value.

## Dependencies and Integration Points
These handlers are installed into ACPICA address-space dispatch and are invoked by field access. They integrate with OS memory mapping, port I/O, PCI config access, and table-mapping state created elsewhere. The memory handler persists mapping entries in `region_context` for reuse.

## Risks and Test Signals
Risks include memory mapping lifetime leaks, page-boundary and end-of-region bugs, invalid bit width acceptance, unaligned access on strict platforms, PCI register truncation to 16 bits, and data-table writes mutating firmware table memory. Tests should cover memory reads/writes across cached and new mappings, rejected widths, optional misalignment builds, I/O read/write status propagation, PCI config reads/writes, data-table byte-copy widths, and cleanup of mapping lists by region teardown code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresnte.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresnte.c

## Purpose
`exresnte.c` resolves namespace nodes to valued ACPICA operand objects for AML execution.

## Important APIs, Types, and Functions
The exported function is `acpi_ex_resolve_node_to_value()`. It operates on `struct acpi_namespace_node`, `union acpi_operand_object`, namespace node flags such as `ANOBJ_METHOD_ARG` and `ANOBJ_METHOD_LOCAL`, and ACPI object types. Dependencies include `acpi_ns_get_attached_object()`, `acpi_ns_get_type()`, `acpi_ds_get_package_arguments()`, `acpi_ds_get_buffer_arguments()`, and `acpi_ex_read_data_from_field()`.

## Control Flow, State, and Persistence
The function accepts a pointer to a namespace-node pointer, follows one level of alias indirection, and returns early for device, thermal, method, local, and argument pseudo-nodes. For package and buffer nodes it forces lazy argument evaluation before returning an extra reference. Strings and integers are returned with an added reference. Field-unit nodes are read immediately into a value object. Mutex, power, processor, event, and region nodes return their attached object with an added reference. Supported local references such as DDB handles, `RefOf`, and `Index` are returned as references; unsupported references and untyped nodes fail.

## Dependencies and Integration Points
This resolver is called by `acpi_ex_resolve_to_value()` and other opcode paths that turn namepaths into executable values. It integrates lazy buffer/package evaluation, namespace aliasing, and field I/O with the operand stack.

## Risks and Test Signals
Risks include alias misresolution, uninitialized-node errors, field reads happening when callers expected references, reference-count imbalance, and unsupported reference classes leaking into value paths. Tests should cover aliases, uninitialized names, package and buffer lazy evaluation, device/thermal nodes, all field kinds, mutex/event/region references, method locals/args, DDB handles, and unsupported local reference classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresnte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresolv.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresolv.c

## Purpose
`exresolv.c` resolves operand-stack entries and nested reference objects into concrete AML values or base object/type information.

## Important APIs, Types, and Functions
Exports are `acpi_ex_resolve_to_value()` and `acpi_ex_resolve_multiple()`. The local resolver is `acpi_ex_resolve_object_to_value()`. Important data includes operand descriptors, namespace nodes, local reference classes (`LOCAL`, `ARG`, `INDEX`, `REFOF`, `NAME`, `DEBUG`, `TABLE`), and walk-state opcode context.

## Control Flow, State, and Persistence
`acpi_ex_resolve_to_value()` validates the stack entry, resolves operand descriptors first, then namespace nodes. The object resolver turns local/arg references into method data values, dereferences package indexes except for method calls and `CopyObject`, leaves buffer-field indexes as references, resolves name references to attached objects or device/thermal nodes, evaluates buffers/packages lazily, and reads fields into value objects. It removes references to replaced stack objects. `acpi_ex_resolve_multiple()` traverses reference chains for `ObjectType` and `SizeOf`, follows namespace nodes and package index references, detects circular references, maps internal field types to external `FieldUnit`, maps scope to `Any`, and can optionally return the final descriptor.

## Dependencies and Integration Points
This file is central to operand resolution before opcode execution and to type introspection opcodes. It integrates method local/arg storage, namespace lookup, lazy buffer/package evaluation, field reads, and ACPI reference classes produced by `RefOf`, `Index`, `Load`, and namepath parsing.

## Risks and Test Signals
Risks include dereferencing when an opcode requires a reference, uninitialized package element errors, circular reference handling, stale pointer/reference ownership after stack replacement, and incorrect external type mapping. Tests should cover every reference class, package index behavior for method call versus normal use, buffer-field index preservation, name references to device/thermal and ordinary objects, nested `RefOf` chains, circular references, lazy buffer/package evaluation, and field reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresolv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresop.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresop.c

## Purpose
`exresop.c` resolves and type-checks operand stacks according to opcode runtime argument metadata before AML opcode execution.

## Important APIs, Types, and Functions
The exported function is `acpi_ex_resolve_operands()`. The local checker is `acpi_ex_check_object_type()`. It consumes `struct acpi_opcode_info::runtime_args`, `ARGI_*` operand encodings, opcode flags, `struct acpi_walk_state`, and operand/reference descriptors.

## Control Flow, State, and Persistence
The resolver fetches opcode metadata, walks encoded argument types from the operand stack, validates descriptors, resolves aliases, validates local reference classes, and decides whether each operand should remain a reference or be resolved to a value. For value operands it calls `acpi_ex_resolve_to_value()` and then enforces simple or complex type requirements. It performs implicit source conversions for integer, buffer, string, buffer-or-string, and computed-data arguments. It treats store targets specially so index references are not accidentally dereferenced, allows AML constants as no-op store targets, supports interpreter slack for broad `Store` sources, and permits Debug object stores.

## Dependencies and Integration Points
This is the gate between the parser/dispatcher and executor opcode handlers. It depends on opcode metadata tables, namespace aliasing, conversion helpers, `acpi_ex_resolve_to_value()`, local reference validation, and global `acpi_gbl_enable_interpreter_slack`.

## Risks and Test Signals
Risks include wrong ARGI metadata interpretation, stack direction mistakes, implicit conversion behavior that differs from the ACPI specification, dereferencing store targets too early, accepting invalid reference classes, and Debug/slack mode masking bugs. Tests should execute opcodes from each ARGI category, invalid operand descriptors, alias operands, constant store targets, store of index references, conversion success/failure for integer/string/buffer, `CopyObject`, `SizeOf`, `Load`, DDB handles, and slack-mode differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exserial.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exserial.c

## Purpose
`exserial.c` implements field-unit read/write support for GPIO, SMBus, IPMI, GenericSerialBus, Platform Runtime Mechanism, and Fixed Function Hardware address spaces.

## Important APIs, Types, and Functions
Exports are `acpi_ex_read_gpio()`, `acpi_ex_write_gpio()`, `acpi_ex_read_serial_bus()`, and `acpi_ex_write_serial_bus()`. They operate on field descriptors, serial address-space IDs, field attributes/protocol IDs, and ACPICA buffer objects. Dependencies include `acpi_ex_access_region()`, `acpi_ex_get_protocol_buffer_length()`, `acpi_ut_create_buffer_object()`, `acpi_ex_acquire_global_lock()`, and `acpi_ex_release_global_lock()`.

## Control Flow, State, and Persistence
GPIO reads and writes bypass normal bitfield packing and pass the pin index and bit length directly to the region handler while holding the ACPI global lock when the field requests it. GPIO writes require an integer source. Serial-bus reads select a transfer buffer length and function code from the region space and accessor type, reject direct reads for bidirectional raw process bytes, allocate a return buffer, and call the region handler. Serial-bus writes require a source buffer, allocate a fixed/protocol-sized bidirectional buffer, copy as much input as fits, call the region handler, and return the same buffer to the caller.

## Dependencies and Integration Points
These helpers are called by field read/write code for special address spaces. They integrate field metadata prepared in `exprep.c`, operation-region handlers, global-lock semantics, and protocol-specific ACPICA constants for SMBus/IPMI/GSBus/PRM/FFH buffers.

## Risks and Test Signals
Risks include incorrect protocol buffer sizing, accepting invalid accessor types, global-lock leaks on error paths, source buffer truncation, GPIO integer-only enforcement, and handler expectations for bidirectional buffers. Tests should cover GPIO read/write pin metadata, SMBus/IPMI/GSBus read/write protocols, raw-process read rejection, invalid space IDs, invalid GSBus protocol IDs, short and long source buffers, PRM/FFH buffer sizes, and lock acquire/release pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exserial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstore.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstore.c

## Purpose
`exstore.c` is the main AML store engine. It stores values into namespace nodes, reference targets, indexed buffers/packages, locals/args, Debug, and fields.

## Important APIs, Types, and Functions
Exports are `acpi_ex_store()` and `acpi_ex_store_object_to_node()`. Local helpers are `acpi_ex_store_object_to_index()` and `acpi_ex_store_direct_to_node()`. Important types include local reference descriptors, namespace nodes, `ACPI_TYPE_LOCAL_REGION_FIELD`, `ACPI_TYPE_LOCAL_BANK_FIELD`, `ACPI_TYPE_LOCAL_INDEX_FIELD`, and `ACPI_TYPE_BUFFER_FIELD`.

## Control Flow, State, and Persistence
`acpi_ex_store()` validates source and destination, routes namespace-node destinations to `acpi_ex_store_object_to_node()`, treats AML constants as no-op store destinations, and dispatches reference classes: `RefOf` stores to the referenced node, `Index` stores to a buffer/string byte or package element, locals/args update method data, and Debug prints the object. Package index stores copy normal objects or retain DDB handles, adjust references according to the parent package reference count, and replace the element. Buffer/string index stores the low byte of an integer or first byte of a buffer/string. Named-object stores reject immutable target types for normal `Store`, resolve references, convert for integer/string/buffer targets when allowed, preserve field object type by writing field data, and use direct copy/attach for `CopyObject` or other allowed targets.

## Dependencies and Integration Points
This file integrates with namespace attachment, method local/arg storage, field write code, object copying, implicit conversion in `exstoren.c`, object printing for Debug, and opcode-specific semantics for `Store` versus `CopyObject`.

## Risks and Test Signals
Risks include reference-count imbalance in package replacement, incorrect package parent reference-count adjustment, accidental type changes for field nodes, wrong implicit conversion on `ArgX` stores, store-to-constant behavior, and buffer/string index source validation. Tests should cover stores to names, locals, args, constants, Debug, fields, package indexes with existing/null elements, DDB handles, buffer/string indexes, immutable targets, `CopyObject` type changes, and conversion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstoren.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstoren.c

## Purpose
`exstoren.c` supports storing into namespace objects by resolving source references and copying or converting object values into existing destination objects.

## Important APIs, Types, and Functions
Exports are `acpi_ex_resolve_object()` and `acpi_ex_store_object_to_object()`. Dependencies include `acpi_ex_resolve_to_value()`, `acpi_ex_convert_to_target_type()`, `acpi_ut_copy_iobject_to_iobject()`, `acpi_ex_truncate_for32bit_table()`, `acpi_ex_store_string_to_string()`, and `acpi_ex_store_buffer_to_buffer()`.

## Control Flow, State, and Persistence
`acpi_ex_resolve_object()` resolves local reference sources when the target is a field or simple integer/string/buffer, skips extra validation for `CopyObject`, and otherwise enforces that field/simple stores receive integer, string, buffer, or DDB handle-like table references. It also rejects unresolved aliases. `acpi_ex_store_object_to_object()` copies directly when the destination is uninitialized, performs implicit conversion to the destination type when source and destination differ, then updates the destination value in place for integers, strings, buffers, or packages. Integer stores are truncated in 32-bit table mode. Temporary converted source objects are released before return.

## Dependencies and Integration Points
This module is used by `exstore.c` for named object stores and by conversion-aware target storage. It depends on separate buffer/string copy helpers and on the global integer execution width.

## Risks and Test Signals
Risks include validating the pre-resolution source instead of the updated source pointer, conversion returning the original object as a new descriptor, package copy semantics, 32-bit truncation, and temporary object cleanup. Tests should cover uninitialized destinations, integer/string/buffer cross-conversions, field-target resolution, `CopyObject` no-conversion paths, alias rejection, DDB handles, package stores, and 32-bit table truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstoren.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstorob.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstorob.c

## Purpose
`exstorob.c` implements low-level value copying for buffer-to-buffer and string-to-string AML stores.

## Important APIs, Types, and Functions
Exports are `acpi_ex_store_buffer_to_buffer()` and `acpi_ex_store_string_to_string()`. They manipulate `union acpi_operand_object` buffer/string fields, `AOPOBJ_STATIC_POINTER`, allocation/free helpers, and buffer flags.

## Control Flow, State, and Persistence
Buffer stores return immediately for self-assignment. If the target buffer has length zero or points at static table storage, a new buffer is allocated at the source length. If the source fits, the target is zeroed then overwritten; if not, the source is truncated to the existing target length. Source buffer flags are copied and the static-pointer flag is cleared. String stores either reuse an existing non-static buffer when the new string is shorter than the old length, or free non-static storage and allocate a new NUL-terminated buffer. The target string length is updated to the source length.

## Dependencies and Integration Points
These helpers are called by `acpi_ex_store_object_to_object()` after any required implicit conversion has produced matching source and destination types. They preserve ACPICA ownership rules for pointers into AML tables.

## Risks and Test Signals
Risks include leaks when replacing static and dynamic buffers, truncation surprises for fixed-size buffers, stale bytes after string reuse, allocation failures leaving partial target state, and buffer flag propagation. Tests should cover self-assignment, zero-length targets, static-pointer targets, source shorter/equal/longer than target, zero-length strings, allocation failures, and post-store flags/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstorob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exsystem.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exsystem.c

## Purpose
`exsystem.c` wraps host OS synchronization and timing services for AML `Acquire`, `Wait`, `Sleep`, `Stall`, `Signal`, and `Reset` behavior.

## Important APIs, Types, and Functions
Exports include `acpi_ex_system_wait_semaphore()`, `acpi_ex_system_wait_mutex()`, `acpi_ex_system_do_stall()`, `acpi_ex_system_do_sleep()`, `acpi_ex_system_signal_event()`, `acpi_ex_system_wait_event()`, and `acpi_ex_system_reset_event()`. Dependencies include `acpi_os_wait_semaphore()`, `acpi_os_acquire_mutex()`, `acpi_os_stall()`, `acpi_os_sleep()`, semaphore creation/deletion, and `acpi_ex_exit_interpreter()`/`acpi_ex_enter_interpreter()`.

## Control Flow, State, and Persistence
Semaphore and mutex waits first try a non-blocking acquire. If they would block, they release the interpreter and namespace mutexes, wait with the requested timeout, then reacquire interpreter state. `Stall` enforces a hard compatibility cap of 255 microseconds and warns once above the ACPI 100-microsecond guidance. `Sleep` releases the interpreter, caps the sleep duration to `ACPI_MAX_SLEEP`, sleeps, and reacquires the interpreter. Event signal/wait wrappers operate on the event object's OS semaphore. Event reset creates a fresh semaphore, deletes the old one, and swaps the object pointer.

## Dependencies and Integration Points
Opcode handlers in `exoparg1.c` and `exoparg2.c` call these wrappers. The file integrates AML synchronization semantics with OS primitives while preventing the AML interpreter lock from blocking unrelated AML progress during waits or sleeps.

## Risks and Test Signals
Risks include interpreter lock imbalance, timeout truncation to `u16` for event waits, reset races while other waiters use the old semaphore, oversized stall/sleep compatibility behavior, and OS error propagation. Tests should cover immediate and blocking semaphore/mutex paths, timeout returns, interpreter lock release/reacquire under contention, `Stall` boundary values, sleep cap behavior, signal/wait/reset event sequences, and error injection from OS primitives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exsystem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/extrace.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/extrace.c

## Purpose
`extrace.c` implements interpreter tracing for AML methods, opcodes, and regions, including filtered and one-shot method tracing.

## Important APIs, Types, and Functions
Exports include `acpi_ex_trace_point()`, `acpi_ex_trace_args()`, `acpi_ex_start_trace_method()`, `acpi_ex_stop_trace_method()`, `acpi_ex_start_trace_opcode()`, and `acpi_ex_stop_trace_opcode()`. Local state is `acpi_gbl_trace_method_object`. Global controls include `acpi_gbl_trace_flags`, `acpi_gbl_trace_method_name`, `acpi_gbl_trace_dbg_level`, `acpi_gbl_trace_dbg_layer`, `acpi_dbg_level`, and `acpi_dbg_layer`.

## Control Flow, State, and Persistence
`acpi_ex_interpreter_trace_enabled()` checks global enable, method-name filters, active traced method object, and one-shot state. Method start obtains the normalized path, decides whether tracing is enabled, records the method object, saves original debug level/layer, installs trace debug settings, and emits a begin trace point. Method stop emits the end trace point, clears one-shot filter state when appropriate, restores original debug settings, and clears the active method object. Opcode start/stop trace only when opcode tracing is enabled. Argument tracing prints integer and string arguments to the trace stream.

## Dependencies and Integration Points
This file is used by dispatcher/executor trace hooks and by ACPICA debug output macros. It integrates namespace pathname formatting, parser opcode names, debug level/layer globals, and method argument object formatting.

## Risks and Test Signals
Risks include global debug settings not being restored after abnormal method exit, one-shot filters being cleared too early or late, NULL/empty string argument handling, nested traced method behavior, and tracing overhead when disabled. Tests should cover unfiltered, filtered, and one-shot tracing; nested methods; opcode trace flags; integer/string/empty-string arguments; method-not-found path handling; and failure paths that still call the stop hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/extrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exutils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exutils.c

## Purpose
`exutils.c` provides executor utility functions and defines AML globals. It manages interpreter/namespace mutex entry, 32-bit integer truncation, global-lock acquisition for field access, numeric formatting helpers, EISA/PCI ID string conversions, and operation-region space ID validation.

## Important APIs, Types, and Functions
Exports are `acpi_ex_enter_interpreter()`, `acpi_ex_exit_interpreter()`, `acpi_ex_truncate_for32bit_table()`, `acpi_ex_acquire_global_lock()`, `acpi_ex_release_global_lock()`, `acpi_ex_eisa_id_to_string()`, `acpi_ex_integer_to_string()`, `acpi_ex_pci_cls_to_string()`, and `acpi_is_valid_space_id()`. The local helper is `acpi_ex_digits_needed()`. It defines `DEFINE_AML_GLOBALS` before including AML headers.

## Control Flow, State, and Persistence
Interpreter entry acquires the interpreter mutex then namespace mutex; exit releases them in reverse order. Integer truncation masks values to 32 bits when executing 32-bit ACPI tables. Global-lock helpers only act when the field flags request `AlwaysLock`, using the global lock mutex and current thread ID. Formatting helpers convert integer IDs to ACPI-required strings using division, byte swapping, and hex conversion. Space validation rejects reserved predefined region IDs while allowing user-defined regions, data-table regions, and fixed hardware.

## Dependencies and Integration Points
These utilities are used throughout the executor, field access, and system wait paths. They integrate ACPICA mutexes, global lock objects, AML global declarations, ACPI table integer width state, and namespace/region validation.

## Risks and Test Signals
Risks include mutex acquisition order regressions, lock release imbalance, silent global-lock acquisition failures, 32-bit truncation in the wrong execution mode, buffer-size assumptions in string conversions, and rejecting valid OEM/user region IDs. Tests should cover nested interpreter entry assumptions, blocking paths that exit/reenter, 32-bit and 64-bit integer truncation, global-lock requested/unrequested field accesses, EISA/PCI/integer string known vectors, and space ID boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwacpi.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwacpi.c

## Purpose
`hwacpi.c` controls ACPI versus legacy system mode transitions and reports the current ACPI hardware mode.

## Important APIs, Types, and Functions
Exports are `acpi_hw_set_mode()` and `acpi_hw_get_mode()`, compiled when `!ACPI_REDUCED_HARDWARE`. They use `acpi_gbl_reduced_hardware`, `acpi_gbl_FADT.smi_command`, `acpi_gbl_FADT.acpi_enable`, `acpi_gbl_FADT.acpi_disable`, `acpi_hw_write_port()`, and `acpi_read_bit_register(ACPI_BITREG_SCI_ENABLE)`.

## Control Flow, State, and Persistence
Reduced-hardware systems always report success/ACPI mode. `acpi_hw_set_mode()` validates that SMI command and enable/disable values exist, then writes the ACPI enable or disable byte to the SMI command port. `acpi_hw_get_mode()` returns ACPI mode if no transition mechanism exists, otherwise reads `SCI_EN`; read failure is treated as legacy mode.

## Dependencies and Integration Points
This file is part of ACPICA hardware initialization and shutdown paths. It depends on normalized FADT contents and port I/O helpers, and it coordinates with fixed-event/GPE setup expectations around mode transitions.

## Risks and Test Signals
Risks include treating absent mode-transition support as success, hardware/firmware not responding to SMI writes, reduced-hardware compile/runtime paths, and SCI_EN read failures causing legacy reports. Tests should cover reduced-hardware mode, missing SMI command, zero enable/disable values, ACPI and legacy transition writes, invalid mode input, SCI_EN true/false, and port I/O error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwacpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwesleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwesleep.c

## Purpose
`hwesleep.c` implements sleep and wake support for ACPI extended FADT v5 sleep control/status registers.

## Important APIs, Types, and Functions
Exports are `acpi_hw_execute_sleep_method()`, `acpi_hw_extended_sleep()`, `acpi_hw_extended_wake_prep()`, and `acpi_hw_extended_wake()`. Dependencies include `acpi_evaluate_object()`, `acpi_read()`, `acpi_write()`, `acpi_os_enter_sleep()`, `ACPI_FLUSH_CPU_CACHE()`, FADT sleep control/status GAS fields, and globals such as `acpi_gbl_sleep_type_a`, `acpi_gbl_sleep_type_a_s0`, and `acpi_gbl_system_awake_and_running`.

## Control Flow, State, and Persistence
Sleep-method execution builds a one-integer argument list and ignores missing methods while logging other failures. Extended sleep validates sleep registers, clears wake status, marks the system not awake, computes sleep control from `_Sx` sleep type A plus sleep enable, flushes CPU cache before S1-S3, calls `acpi_os_enter_sleep()`, writes the sleep control register unless the OS hook terminates the sequence, and polls sleep status until wake status is set. Wake prep optionally writes S0 sleep type plus enable. Wake invalidates sleep type A, runs `_SST(WAKING)` and `_WAK`, clears wake status for BIOS compatibility, marks the system awake, then runs `_SST(WORKING)`.

## Dependencies and Integration Points
This file integrates ACPICA sleep-state preparation, FADT extended registers, OS sleep entry hooks, and AML sleep/wake methods. It must be called in the interrupt state documented by each function.

## Risks and Test Signals
Risks include infinite polling if wake status never appears, incorrect interrupt-state callers, stale sleep type globals, OS hook termination semantics, missing register handling, and firmware methods with side effects. Tests should cover absent sleep registers, read/write failures, each sleep state, OS hook `AE_CTRL_TERMINATE`, wake-status polling, S0 wake prep, missing and failing `_SST`/`_WAK`, and global awake/sleep-type transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwesleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwgpe.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwgpe.c

## Purpose
`hwgpe.c` provides low-level General Purpose Event register access, enable/disable/clear operations, runtime and wake enable programming, and all-GPE status checks.

## Important APIs, Types, and Functions
Exports include `acpi_hw_gpe_read()`, `acpi_hw_gpe_write()`, `acpi_hw_get_gpe_register_bit()`, `acpi_hw_low_set_gpe()`, `acpi_hw_clear_gpe()`, `acpi_hw_get_gpe_status()`, `acpi_hw_disable_gpe_block()`, `acpi_hw_clear_gpe_block()`, `acpi_hw_enable_runtime_gpe_block()`, `acpi_hw_disable_all_gpes()`, `acpi_hw_enable_all_runtime_gpes()`, `acpi_hw_enable_all_wakeup_gpes()`, and `acpi_hw_check_all_gpes()`. Local helpers include `acpi_hw_gpe_enable_write()`, `acpi_hw_enable_wakeup_gpe_block()`, and `acpi_hw_get_gpe_block_status()`.

## Control Flow, State, and Persistence
GPE register reads/writes target system memory or I/O address spaces, with optional logical-address memory access. Bit computation derives a one-bit mask from the GPE number and register base. Single-GPE enable/disable reads the enable register, modifies only the target bit, honors conditional-enable masks, and skips hardware writes when the GPE is runtime-masked. Clear writes one to the status bit. Status combines handler presence, runtime enabled/masked, wake enabled, current enable bit, and current status bit. Block operations iterate register arrays to disable enables, clear statuses, enable runtime masks, or enable wake masks. All-GPE operations walk the global GPE list. `acpi_hw_check_all_gpes()` optionally skips one GPE while checking enabled-and-active bits under the GPE lock for skip lookup.

## Dependencies and Integration Points
This file is compiled out for reduced hardware. It integrates event-layer GPE lists, GPE locks, OS memory/port access, register metadata populated during ACPI event initialization, and wake/runtime policy fields.

## Risks and Test Signals
Risks include stale software enable masks versus hardware state, masking semantics that skip hardware writes, failures ignored while checking all blocks, reduced-hardware build coverage, memory versus I/O register access differences, and skip-GPE race windows. Tests should cover read/write for memory and I/O GPE registers, enable/disable/conditional enable, masked runtime GPEs, clear-on-write-one status, status flag composition, block-wide disable/clear/runtime/wake programming, all-GPE walks, skip behavior in `acpi_hw_check_all_gpes()`, and hardware access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwgpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwpci.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwpci.c

## Purpose
`hwpci.c` derives the full PCI segment/bus/device/function identity for PCI configuration operation regions by walking ACPI namespace ancestry and reading PCI bridge configuration.

## Important APIs, Types, and Functions
The exported function is `acpi_hw_derive_pci_id()`. Local helpers are `acpi_hw_build_pci_list()`, `acpi_hw_process_pci_list()`, `acpi_hw_delete_pci_list()`, and `acpi_hw_get_pci_device_info()`. It uses `struct acpi_pci_id`, a local `struct acpi_pci_device` linked list, `_ADR` evaluation, and PCI config registers for header type, primary bus, and secondary bus.

## Control Flow, State, and Persistence
`acpi_hw_derive_pci_id()` validates input, builds a non-recursive list of devices from the PCI config region up to the root bridge, processes the list from root downward, then frees it. Device processing ignores non-device nodes and devices without `_ADR`, extracts device/function from `_ADR`, applies the previous bridge bus when appropriate, reads the PCI header type, and if the device is a PCI or CardBus bridge, reads primary and secondary bus numbers to update current and downstream bus state.

## Dependencies and Integration Points
This file is used while initializing PCI_Config operation regions. It integrates ACPI namespace traversal, `_ADR` evaluation, OS PCI configuration reads, and root bridge discovery done elsewhere. It deliberately avoids recursion by using a temporary linked list.

## Risks and Test Signals
Risks include namespace ascent not reaching the expected root, memory cleanup on build failures, `_ADR` interpretation mistakes, bridge bus propagation errors, PCI config read failures, and CardBus bridge handling. Tests should cover direct child devices, nested bridges, non-device ancestors, missing `_ADR`, PCI and CardBus bridges, config read errors, root-not-found paths, allocation failure, and final PCI ID values across multi-bridge topologies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwregs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwregs.c

## Purpose
`hwregs.c` implements generic ACPI GAS register validation and read/write access plus fixed ACPI register helpers for PM1/PM2/timer/SMI and ACPI status clearing.

## Important APIs, Types, and Functions
Exports include `acpi_hw_validate_register()`, `acpi_hw_read()`, `acpi_hw_write()`, `acpi_hw_clear_acpi_status()`, `acpi_hw_get_bit_register_info()`, `acpi_hw_write_pm1_control()`, `acpi_hw_register_read()`, and `acpi_hw_register_write()`. Local helpers are `acpi_hw_get_access_bit_width()`, `acpi_hw_read_multiple()`, and `acpi_hw_write_multiple()`. Important inputs are `struct acpi_generic_address`, FADT GAS fields, `acpi_gbl_bit_register_info`, hardware locks, and fixed-register IDs.

## Control Flow, State, and Persistence
Access-width selection distinguishes FADT register-style GAS from region-style GAS, uses `access_width` when needed, rounds bit ranges to supported widths, enforces a 32-bit maximum for system I/O, and clamps to caller maximum. Validation rejects NULL/zero-address/unsupported-space/invalid-access-width registers and ensures requested register width fits the caller maximum. Generic read/write loops over access-width chunks in system memory or I/O and uses bit insertion/extraction to assemble or split a 64-bit value. Status clearing takes the hardware raw lock, clears PM1 fixed status, then clears all GPE blocks. Fixed register read/write dispatch handles PM1 A/B pairs, masks PM1 control write-only bits on read, preserves required PM1/PM2 control bits on write, writes zero to preserved PM1 status bits, and treats SMI command as port I/O. Multiple-register helpers OR PM1 A/B reads and write the same bit pattern to both blocks.

## Dependencies and Integration Points
This file underpins ACPICA public register accessors and sleep/event code. It integrates FADT register normalization, OS memory access, port I/O helpers, fixed-event/GPE event code, and hardware locking.

## Risks and Test Signals
Risks include access-width calculation for unusual GAS bit offsets, partial multi-access reads/writes after an error, reserved/write-only/preserved bit masking, optional PM1B handling, zero-address optional registers, reduced-hardware compile paths, and I/O-space width limits. Tests should cover FADT-style and region-style GAS inputs, memory and I/O reads/writes at 8/16/32/64 widths, invalid spaces/access widths, bit offsets spanning multiple accesses, PM1 status/enable/control read-write semantics, PM2 preservation, PM timer and SMI command access, PM1B absent/present, status clearing under lock, and GPE clear failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwregs.c -->
