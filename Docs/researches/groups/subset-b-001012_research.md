# subset-b-001012 Research

Grouped research for ACPICA predefined-name, resource, AML, table, and debugger files from `sources/distributed-fs/ceph-client/drivers/acpi/acpica`. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acpredef.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acpredef.h

## Purpose
Defines ACPICA's canonical table of ACPI predefined methods/objects and, for compiler/help builds, predefined resource descriptor and scope names. The table describes which reserved ACPI names may be evaluated, required method argument counts/types, allowed return bit types, and package return layouts.

## Important APIs, Types, And Data
`enum acpi_return_package_types` classifies return package shapes such as fixed elements, variable elements, package-count forms, revision-prefixed packages, UUID-pair packages, and custom validators. `METHOD_*ARGS`, `METHOD_RETURNS`, and `PACKAGE_INFO` pack method metadata into `union acpi_predefined_info` entries. When `ACPI_CREATE_PREDEFINED_TABLE` is defined, `acpi_gbl_predefined_methods[]` is emitted with entries for names such as `_ADR`, `_CRS`, `_DSD`, `_DSM`, `_PRT`, `_PRS`, `_Sx_`, `_STA`, `_UID`, and `_WAK`. With `ACPI_CREATE_RESOURCE_TABLE && ACPI_APPLICATION`, `acpi_gbl_resource_names[]` and `acpi_gbl_scope_names[]` expose ASL-only resource/scope names to iASL and acpi_help.

## Control Flow, State, And Persistence
The file is declarative but drives runtime validation elsewhere. Namespace/evaluation code looks up entries, extracts argument counts via `METHOD_GET_ARG_COUNT`, walks packed argument types with `METHOD_GET_NEXT_TYPE`, and validates returned objects/package elements against the following `PACKAGE_INFO` row. The table is static read-only process/kernel state; it persists for the lifetime of ACPICA and is not mutated.

## Dependencies And Integration Points
The table depends on ACPICA object type constants, return bitmaps, and `union acpi_predefined_info` from common ACPICA headers. It integrates with predefined-name validation/repair code, namespace evaluation, the iASL compiler, the ACPICA help utility, and resource descriptor field-name checking. Package formats encode firmware compatibility decisions, including tolerating common `_S0_` through `_S5_` package length deviations and warning about common `_PRT` source/source-index reversal.

## Risks And Test Signals
Risk is spec drift or packed metadata mistakes: one wrong type/count can reject valid firmware, accept invalid firmware, or break compiler diagnostics. Because package descriptors are adjacent table rows, insertion/removal errors can desynchronize method entries and package metadata. Test signals include ACPICA predefined-name tests, iASL diagnostics, kernel boot logs for predefined return warnings, `_DSM`/`_DSD` validation, resource-name help output, and systems with known nonconforming firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acpredef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acresrc.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acresrc.h

## Purpose
Declares ACPICA Resource Manager internals. It defines conversion-table row formats, dump-table row formats, conversion opcodes, dispatch tables, and prototypes that convert between raw AML resource templates and `struct acpi_resource` lists.

## Important APIs, Types, And Functions
`struct acpi_rsconvert_info` is the byte-sized conversion instruction used by resource conversion tables; `enum ACPI_RSCONVERT_OPCODES` includes initialization, flag extraction, bitmask encode/decode, count calculation, source-string handling, fixed-width moves, GPIO/serial variable field moves, and exit predicates. `struct acpi_rsdump_info` plus `enum ACPI_RSDUMP_OPCODES` describe debugger/disassembler resource dumps. Public internal prototypes cover list creation (`acpi_rs_create_resource_list`, `acpi_rs_create_aml_resources`, `acpi_rs_create_pci_routing_table`), method wrappers (`acpi_rs_get_crs_method_data`, `acpi_rs_set_srs_method_data`, `_PRT`, `_PRS`, `_AEI`), length calculation, AML/resource conversion, address common-field helpers, data movement, bitmask helpers, resource-source handling, and descriptor header writes.

## Control Flow, State, And Persistence
The Resource Manager is table-driven. Dispatch arrays map internal resource type or AML descriptor type to a `struct acpi_rsconvert_info` program, and conversion routines execute that program to copy, synthesize, count, or validate fields. Dump dispatch arrays perform the same indirection for debug output. No persistent data is owned here except global static table declarations defined in resource modules.

## Dependencies And Integration Points
Includes `amlresrc.h` for packed AML descriptor overlays and relies on ACPICA namespace, operand object, buffer, resource, and status types. It is used by ACPI external resource APIs, namespace method evaluation for `_CRS`/`_PRS`/`_SRS`/`_AEI`/`_PRT`, debugger resource commands, and disassembler/compiler resource template support. Packing pragmas are important because conversion tables store byte offsets into packed raw descriptors.

## Risks And Test Signals
Offset and packing errors are the primary risk, especially on architectures that cannot tolerate misaligned access. GPIO, pin, serial-bus, and vendor-data descriptors carry variable sections whose lengths and offsets must be consistent. Test signals include AML-to-resource-to-AML round trips, debugger `Resources`/`Template` output, `acpi_walk_resources`, `_SRS` application tests, compiler/disassembler resource template tests, and boots on devices with modern GPIO/I2C/SPI/UART/CSI2 descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acresrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acstruct.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acstruct.h

## Purpose
Defines core ACPICA internal state structures used by parse-tree walking, control method execution, namespace/device initialization, evaluation, debugger walks, and region display.

## Important APIs, Types, And Fields
`struct acpi_walk_state` is the central interpreter/parser execution frame. It stores walk type, current opcode, owner ID, method nesting, parser state, arguments, locals, operand stack, method descriptors/nodes, parse op pointers, result stack, scope/control stacks, current thread, callbacks, breakpoints, implicit return object, and execution flags. `struct acpi_init_walk_info`, `struct acpi_get_devices_info`, `union acpi_aml_operands`, `struct acpi_evaluate_info`, `struct acpi_device_walk_info`, `struct acpi_region_walk_info`, and `struct acpi_walk_info` are compact context objects for subsystem initialization, device enumeration, AML operand grouping, object evaluation, device `_STA`/`_INI` walks, and debugger display.

## Control Flow, State, And Persistence
The structures are mutable runtime state passed between dispatcher, parser, interpreter, namespace, and debugger layers. `acpi_walk_state` instances form linked stacks for nested methods and restarts; result/control/scope stacks are chained through generic-state objects. Evaluation state is usually stack-allocated by callers to reduce CPU stack pressure and carry predefined-name return analysis through namespace evaluation.

## Dependencies And Integration Points
This header depends on ACPICA parse objects, namespace nodes, operand objects, opcode info, generic state, parse callbacks, owner IDs, and thread state. It is integrated by dispatcher (`ds*`), parser (`ps*`), executor (`ex*`), namespace initialization/evaluation (`ns*`), and debugger display commands such as locals, args, result stack, and call tree.

## Risks And Test Signals
Changes have broad ABI-like internal impact because many subsystems assume field meaning and lifetime. Risks include stale operand/result pointers, incorrect method nesting or owner IDs, breakpoint state corruption, and leaks from result/control/scope stacks. Test signals include AML method execution, nested method calls, namespace load/unload, predefined return repair, single-step debugging, locals/args/results display, and stress tests that execute recursive or concurrently invoked methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acstruct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/actables.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/actables.h

## Purpose
Declares internal ACPICA table-management APIs for root table allocation, RSDP discovery/validation, table descriptor lifecycle, FADT handling, table lookup, install/load/unload, owner ID management, and namespace loading.

## Important APIs And Functions
Root and RSDP helpers include `acpi_allocate_root_table`, `acpi_tb_get_rsdp_length`, `acpi_tb_validate_rsdp`, and `acpi_tb_scan_memory_for_rsdp`. Descriptor functions include `acpi_tb_get_next_table_descriptor`, `acpi_tb_init_table_descriptor`, `acpi_tb_acquire_temp_table`, `acpi_tb_validate_temp_table`, `acpi_tb_verify_temp_table`, `acpi_tb_validate_table`, and `acpi_tb_invalidate_table`. Install/load APIs include `acpi_tb_install_standard_table`, `acpi_tb_install_and_load_table`, `acpi_tb_load_table`, `acpi_tb_unload_table`, and `acpi_tb_load_namespace`. Owner and cleanup APIs include `acpi_tb_delete_namespace_by_owner`, `acpi_tb_allocate_owner_id`, `acpi_tb_release_owner_id`, `acpi_tb_get_owner_id`, and `acpi_tb_terminate`.

## Control Flow, State, And Persistence
The declared routines manage entries in `acpi_gbl_root_table_list`, table descriptors, mapped table memory, table loaded flags, owner IDs, and namespace objects created from AML tables. Typical flow is parse RSDP/root tables, acquire/validate descriptors, optionally override tables, install into the root list, load AML into the namespace, mark loaded, and later unload/delete namespace objects by owner.

## Dependencies And Integration Points
Depends on ACPI physical addresses, table headers, descriptors, namespace nodes, and status codes. It is consumed by initialization, table external APIs, debugger table display/unload commands, dynamic table load support, FADT/FACS handling, and namespace teardown.

## Risks And Test Signals
Risks include stale mappings, double loads/unloads, owner ID leaks, bad override handling, namespace objects surviving table unload, and RSDP/checksum validation regressions. Test signals include boot-time table discovery, dynamic SSDT load/unload, debugger `Tables` and `Unload`, table notification callbacks, FADT conversion validation, and namespace cleanup after table removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/actables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acutils.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acutils.h

## Purpose
Collects prototypes, callback types, constants, and small macros for ACPICA subsystem-wide utilities: strings, checksums, object conversion, reference counting, debugging, evaluation helpers, locks, caches, resources, owner IDs, UUIDs, address ranges, and diagnostic output.

## Important APIs, Types, And Functions
The header declares AML/resource size globals, decode string tables for debug/disassembler output, message redirection/prefix macros, `acpi_walk_aml_callback`, `acpi_pkg_callback`, and `struct acpi_pkg_info`. Utility families include ASCII/name validation, checksum verification, non-ANSI string helpers, string-to-integer conversion, global name/type formatting, subsystem init/shutdown, internal/external object copying, object reference management, trace/debug buffer dump, object deletion, `_STA`/power/HID/UID/CID/CLS evaluation, reader/writer locks, object creation, `_OSI` interface management, predefined method lookup/display, generic state allocation, integer math helpers, package tree walking, owner ID allocation, AML resource walking/validation, safe string functions, mutexes, memory caches/buffer initialization, allocation tracking, address range tracking, prefixed/predefined error output, predefined-name/device-ID/UUID matching, and UUID conversion.

## Control Flow, State, And Persistence
Most functions are implemented in `ut*` modules and operate on global ACPICA state: caches, mutexes, supported `_OSI` interfaces, owner ID bitmaps, address range lists, debug settings, and allocation ledgers. Object copy/delete/reference functions control operand-object lifetime and package traversal. Resource walkers iterate AML descriptors with callbacks. Error helpers centralize warning formatting and source-location suffixes.

## Dependencies And Integration Points
This is a high-fanout internal header included by nearly every ACPICA subsystem. It integrates with namespace evaluation, interpreter execution, debugger/disassembler output, resource manager, table manager, compiler/help tools, OS services, and optional allocation tracking. `ACPI_ASL_COMPILER`, `ACPI_APPLICATION`, `ACPI_DEBUG_OUTPUT`, `ACPI_DEBUGGER`, and related build flags expose different subsets.

## Risks And Test Signals
Because this is a prototype hub, signature or macro changes can break many modules. Behavioral risks include reference count imbalance, unsafe object copies, bad string-to-integer conversion, stale `_OSI` interface state, checksum false positives/negatives, and address range warning regressions. Test signals include ACPICA unit tests, kernel boot logs, namespace/device ID evaluation, AML resource validation, debug output formatting, allocation tracking runs, and compiler/disassembler builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlcode.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlcode.h

## Purpose
Defines AML opcode numbers, parser argument encodings, interpreter resolved argument types, opcode metadata flags/types/classes, package-length markers, match operators, field flags, access/update/lock rules, access attributes, and method flag bit masks directly derived from the ACPI specification.

## Important APIs, Types, And Constants
Primary opcodes cover literals, names, method/scope/package/buffer creation, locals/args, arithmetic/logical operations, type conversions, control flow, and return/break operations. Extended opcodes use the `0x5B` prefix and include mutex/event, field, load/stall/sleep, acquire/release, region/device/processor/power/thermal, and data-region definitions. Internal parser opcodes represent synthetic nodes such as name paths, named fields, byte lists, method calls, return values, and connection/ext-access fields. `ARGP_*` values describe parser grammar arguments, `ARGI_*` values describe interpreter operand requirements, `AML_FLAGS_*` and `AML_TYPE_*` drive opcode dispatch, and field/method enums decode AML flag bytes.

## Control Flow, State, And Persistence
This file is declarative, but its numeric constants drive parser decoding and interpreter dispatch. Parser code reads AML bytes, maps opcodes to `acpi_opcode_info`, interprets `ARGP_*` grammar encodings, resolves operands to `ARGI_*` types, and dispatches by `AML_TYPE_*`. Field-creation paths decode access, lock, update, and attribute bits from AML field flags. There is no owned mutable state.

## Dependencies And Integration Points
Used by parser, interpreter, disassembler, compiler, dispatcher, debugger displays, and field handling. Numeric values must stay aligned with the ACPI specification and opcode info tables compiled elsewhere. Internal opcode values deliberately avoid valid ACPI ASCII values to prevent conflicts.

## Risks And Test Signals
Changing an opcode value or dispatch type is catastrophic because it alters AML bytecode semantics. Risks include parser/interpreter table mismatch, invalid operand resolution, incorrect field access/update behavior, and broken disassembly output. Test signals include AML parser/compiler round trips, method execution tests for each opcode class, field access tests, disassembler output comparison, and boots with diverse firmware AML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlresrc.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlresrc.h

## Purpose
Defines raw AML resource descriptor tags and packed wire-format structures used to overlay ACPI resource template byte streams. It also declares mapfile/compiler helper interfaces for GPIO, serial-bus, HID, and connection metadata.

## Important APIs, Types, And Structures
`ACPI_RESTAG_*` constants map ASL descriptor field names such as `_ADR`, `_LEN`, `_INT`, `_SHR`, `_VEN`, `_FQN`, and `_FQD`. Default small-descriptor sizes support ASL resource generation. `struct asl_resource_node` and `struct asl_resource_info` support compiler resource-template construction. Packed structs model small descriptors (`irq`, `dma`, `io`, `fixed_io`, `fixed_dma`, `end_tag`) and large descriptors (`memory24/32`, fixed memory, address16/32/64, extended address64, extended IRQ, generic register, GPIO, CSI2/I2C/SPI/UART serial bus, pin function/config/group/group function/group config, and clock input). `union aml_resource` overlays all descriptor variants and scalar utility views.

## Control Flow, State, And Persistence
The header has no executable control flow, but conversion and validation code casts raw AML bytes to these packed structs and uses embedded lengths/offsets to locate variable trailing data such as pin lists, resource-source strings, labels, and vendor bytes. Compiler/disassembler map helpers persist relationship metadata outside these raw descriptors as needed.

## Dependencies And Integration Points
Used by `acresrc.h` conversion tables, resource manager code, AML resource walkers, iASL resource generation, disassembler mapfile support, and debugger resource dumps. `#pragma pack(1)` is essential because these structs are ABI overlays on AML bytes, not native in-memory layouts.

## Risks And Test Signals
Risks include descriptor layout drift from the ACPI spec, incorrect variable-section offsets, missing revision/minimum-data-length updates, and unaligned-access problems if code performs unsafe native loads on strict architectures. Test signals include resource-template compile/disassemble round trips, AML-to-resource conversion for each descriptor kind, GPIO/pin/serial bus device enumeration, `_CRS`/`_PRS`/`_AEI` debugger dumps, and firmware samples using ACPI 6.2+ pin and ACPI 6.5 clock descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlresrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbcmds.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbcmds.c

## Purpose
Implements miscellaneous ACPICA AML debugger commands for namespace-node conversion, sleep simulation, lock/table display, table unload, notify/GED/GPE/SCI generation, `_OSI` interface display/modification, resource/template display, resource conversion round-trip testing, and method tracing.

## Important APIs And Functions
`acpi_db_convert_to_node` accepts either a hex pointer or namespace path and returns a validated namespace node. `acpi_db_sleep` and `acpi_db_do_one_sleep_state` simulate S-state prep/enter/leave flows. `acpi_db_display_locks`, `acpi_db_display_table_info`, `acpi_db_unload_acpi_table`, `acpi_db_send_notify`, and `acpi_db_display_interfaces` expose global ACPICA state. Resource helpers include `acpi_db_display_template`, `acpi_dm_compare_aml_resources`, `acpi_dm_test_resource_conversion`, `acpi_db_resource_callback`, `acpi_db_device_resources`, and `acpi_db_display_resources`. Hardware simulation functions include `acpi_db_generate_interrupt`, `acpi_db_generate_gpe`, and `acpi_db_generate_sci`. `acpi_db_trace` configures control method tracing and stores the traced method name in `acpi_db_trace_method_name`.

## Control Flow, State, And Persistence
Commands generally parse textual arguments, resolve namespace nodes, call ACPICA public/internal APIs, print diagnostics, and restore debugger output destination. Resource display walks devices or one device, evaluates `_PRT`/`_CRS`/`_PRS`/`_AEI`, converts buffers to internal resources, walks resources, dumps them, round-trips `_CRS` AML, and attempts `_SRS`. The trace command allocates and replaces persistent debugger method-name state.

## Dependencies And Integration Points
Depends on events, namespace, resources, and table internals. It integrates with the debugger command dispatcher in `dbinput.c`, resource manager conversion/dump tables, sleep/wake APIs, GPE/GED event infrastructure, table manager, `_OSI` interface list, and debug output routing.

## Risks And Test Signals
Risk areas include accepting raw pointer strings, modifying `_OSI` state, triggering sleep/wake/event paths from a debugger, executing `_SRS` with current resources, and buffer-size assumptions around `acpi_gbl_db_buffer`. Test signals include debugger `Resources`, `Template`, `Tables`, `Unload`, `Notify`, `Trace`, `Sleep`, `Gpe`, `Sci`, and `Interrupt` commands, plus resource round-trip mismatch diagnostics and systems with GED/GPE devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbcmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbconvert.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbconvert.c

## Purpose
Provides debugger conversion routines that turn command-line tokens into `union acpi_object` arguments and decode/re-encode `_PLD` buffers for formatted display and validation.

## Important APIs And Functions
`acpi_db_hex_char_to_value` validates and converts one hex digit. `acpi_db_hex_byte_to_binary` converts two hex characters to a byte. `acpi_db_convert_to_buffer` parses comma/space-separated hex bytes inside debugger buffer syntax. `acpi_db_convert_to_package` allocates a fixed default package element array and recursively calls `acpi_db_convert_to_object` for nested package elements. `acpi_db_convert_to_object` creates string, buffer, package, or integer external objects from parsed token types. `acpi_db_encode_pld_buffer` bit-packs an `acpi_pld_info` structure into an ACPI `_PLD` buffer using `ACPI_PLD_SET_*` macros. `acpi_db_dump_pld_buffer` decodes the first package buffer element as `_PLD`, verifies re-encoding, and prints fields.

## Control Flow, State, And Persistence
Conversion is request-scoped. Buffers and package element arrays are dynamically allocated and later freed by `acpi_db_delete_objects` in `dbexec.c`. String objects borrow pointers into the parsed command buffer. `_PLD` dump allocates decoded structure and re-encoded buffer, compares byte-for-byte, prints fields, and frees temporary memory.

## Dependencies And Integration Points
Consumes token types produced by `acpi_db_get_next_token` in `dbinput.c` and feeds `acpi_evaluate_object` calls in `dbexec.c`. Uses utility conversion functions, memory allocation macros, `_PLD` macros, `acpi_decode_pld_buffer`, and debugger buffer dump output.

## Risks And Test Signals
Risks include fixed `DB_DEFAULT_PKG_ELEMENTS` truncation, malformed buffer strings with odd/missing hex digits, borrowed string lifetimes tied to parsed command storage, recursive package cleanup on partial failures, and `_PLD` revision/length handling. Test signals include debugger `Evaluate` with integer/string/buffer/package/nested-package arguments, invalid hex input, allocation-failure paths, `_PLD` method evaluation output, and compare warnings from `_PLD` re-encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbconvert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbdisply.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbdisply.c

## Purpose
Implements AML debugger display commands for internal objects, parser descriptors, current method execution state, locals/arguments/results, call tree, object info, GPE state, and installed handlers.

## Important APIs And Functions
`acpi_db_decode_and_display_object` distinguishes hex pointer input from namespace names, validates readability, decodes descriptor types, dumps namespace nodes, operand objects, parser ops, or raw memory, and follows attached objects. `acpi_db_display_method_info`, `acpi_db_display_locals`, `acpi_db_display_arguments`, `acpi_db_display_results`, and `acpi_db_display_calling_tree` inspect the active walk-state list. `acpi_db_display_object_type` calls `acpi_get_object_info` for a handle. `acpi_db_display_result_object` and `acpi_db_display_argument_object` print single-step operands only on the debugger thread. `acpi_db_display_gpes`, `acpi_db_display_handlers`, and `acpi_db_display_non_root_handlers` enumerate event and operation-region handler state.

## Control Flow, State, And Persistence
Display commands are read-only diagnostics over live ACPICA state. Object dumping follows pointer/name resolution, descriptor validation, optional namespace pathname formatting, raw buffer dump, and structured object dump. Method-state commands obtain the current walk state and traverse parse trees/result frames. Handler/GPE display walks global lists and namespace devices.

## Dependencies And Integration Points
Depends on AML opcode definitions, dispatcher current walk state, parser tree traversal, interpreter dump helpers, namespace utilities, event/GPE structures, and debug output routines. It is invoked through `dbinput.c` commands such as `Dump`, `Information`, `Locals`, `Args`, `Results`, `Tree`, `Type`, `Gpes`, and `Handlers`.

## Risks And Test Signals
Raw pointer display is inherently risky and relies on `acpi_os_readable` to avoid faults. Live GPE/handler traversal can race with event reconfiguration if the embedding environment allows concurrent changes. Result-stack indexing must handle empty stacks correctly. Test signals include single-step sessions, object dumps by name and address, handler enumeration after installing address-space handlers, GPE display on reduced and full hardware builds, and malformed pointer inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbdisply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbexec.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbexec.c

## Purpose
Implements debugger control-method/object evaluation, cleanup of converted arguments, execution setup, optional allocation-leak reporting, execution of all matching/predefined methods, and background/threaded method execution.

## Important APIs And Functions
`acpi_db_delete_objects` recursively frees debugger-created buffer and package external objects. `acpi_db_execute_method` converts command arguments, prepares a return buffer, sets `acpi_gbl_method_executing`, invokes `acpi_evaluate_object`, handles aborts/buffer overflow, and deletes arguments. `acpi_db_execute_setup` builds the fully qualified pathname from current debugger scope and configures output/single-step state. `acpi_db_execution_walk` evaluates zero-argument methods during wildcard execution. `acpi_db_execute` handles `*`, `PREDEF`, `ALL`, normal evaluate/debug modes, return-object dumping, `_PLD` special formatting, and allocation tracking. `acpi_db_create_execution_thread`, `acpi_db_single_execution_thread`, `acpi_db_create_execution_threads`, and `acpi_db_method_thread` run evaluations in one or more OS-layer debugger threads.

## Control Flow, State, And Persistence
The global `acpi_gbl_db_method_info` is reused as command context. Normal flow is parse/setup path, get handle, execute, sleep briefly for async handlers, report return object, restore console output. Threaded flow creates semaphores, initializes per-thread argument strings with thread count/id/index, launches OS execution callbacks, waits for completion, then destroys semaphores and thread ID storage. Single-step mode toggles `acpi_gbl_cm_single_step`.

## Dependencies And Integration Points
Integrates with `dbinput.c` command dispatch, `dbconvert.c` argument conversion, namespace handle lookup, ACPI object evaluation, debug output, allocation tracking caches, OS services for sleep/semaphores/thread execution, and `_PLD` display in `dbconvert.c`.

## Risks And Test Signals
Risks include global method-info reuse across background execution, races in threaded mode, semaphore cleanup on partial failures, return-buffer sizing (`ACPI_DEBUG_BUFFER_SIZE`), leaked external return buffers in some execution paths, and deadlock prevention through `acpi_gbl_method_executing`. Test signals include `Evaluate`, `Debug`, `All`, `Execute predefined`, `Background`, and `Threads` debugger commands, aborting a method, methods returning large objects, allocation tracking before/after execution, and AML tests that depend on thread argument conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbfileio.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbfileio.c

## Purpose
Provides application-build debugger file I/O support: opening/closing a debug output file and loading ACPI tables from an already parsed list.

## Important APIs And Functions
Under `ACPI_APPLICATION` and `ACPI_DEBUGGER`, `acpi_db_close_debug_file` closes `acpi_gbl_debug_file`, clears `acpi_gbl_db_output_to_file`, and reports the filename. `acpi_db_open_debug_file` closes any current file, opens the requested path with `w+`, stores the filename with `acpi_ut_safe_strncpy`, and enables output-to-file mode. `acpi_db_load_tables` walks a `struct acpi_new_table_desc` list, calls `acpi_load_table` for each table, reports duplicate or install errors, and prints successful installs.

## Control Flow, State, And Persistence
Debug file state persists in globals until closed or debugger exit. Opening a new file always closes the previous one. Table loading mutates ACPICA table and namespace state through `acpi_load_table`; on the first failure it returns the failing status and leaves previously loaded tables installed.

## Dependencies And Integration Points
Only built for ACPICA application environments, not typical kernel debugger use. It depends on C stdio, `acapps.h` table-file parsing structures, table manager APIs, safe string utilities, and `dbinput.c` commands `Open`, `Close`, and `Load`.

## Risks And Test Signals
Risks include filesystem availability differences, truncating existing output files via `w+`, global output state not restored if callers bypass close, partial table-list load on failure, and duplicate table handling. Test signals include debugger `Open`/`Close` redirection, loading AML/ACPI table files in acpiexec-like tools, duplicate-load diagnostics, and verifying output destination after file errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbfileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbhistry.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbhistry.c

## Purpose
Implements the AML debugger command history ring buffer and history recall commands.

## Important APIs And Functions
The module defines `HISTORY_SIZE` as 40 and stores `HISTORY_INFO` entries containing a heap-allocated command string plus command number. `acpi_db_add_to_history` inserts a non-empty command, reuses or reallocates the target slot as needed, stores `acpi_gbl_next_cmd_num`, advances circular indices, and caps count at 40. `acpi_db_display_history` prints commands from the oldest index. `acpi_db_get_from_history` resolves a supplied command number or defaults to the previous command. `acpi_db_get_history_by_index` searches the circular buffer and returns the stored command pointer.

## Control Flow, State, And Persistence
History state is process-local static memory: `acpi_gbl_history_buffer`, `acpi_gbl_lo_history`, `acpi_gbl_num_history`, and `acpi_gbl_next_history_index`. Command numbers persist monotonically through the debugger session via `acpi_gbl_next_cmd_num`. Recalled commands are not copied; callers dispatch the returned stored pointer.

## Dependencies And Integration Points
Used by `dbinput.c` for `History`, `!`, and `!!`. It uses ACPICA OS allocation/free and output services. `dbinput.c` deliberately avoids adding `!!` itself to history to prevent recursive repeat loops.

## Risks And Test Signals
Risks include unchecked allocation failure before `strcpy`, fixed-size history eviction behavior, returned command pointers being overwritten by later history insertion, and the final invalid-history message printing the circular index rather than requested command number. Test signals include command history wraparound beyond 40 entries, recalling explicit and last commands, repeated `!!`, long commands that force reallocation, and allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbhistry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbinput.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbinput.c

## Purpose
Implements the front end for the AML debugger: command tables, help text, tokenization, command matching, dispatch, command history integration, interactive command loop, and the debugger command execution thread.

## Important APIs And Functions
`enum acpi_ex_debugger_commands`, `acpi_gbl_db_commands[]`, and `acpi_gbl_db_command_help[]` define command names, minimum argument counts, and help output. `acpi_db_get_next_token` tokenizes integers, quoted strings, buffers `(...)`, field units `{...}`, and nested packages `[...]`, returning an ACPI object type for later conversion. `acpi_db_get_line` copies input into the parsed buffer, extracts up to `ACPI_DEBUGGER_MAX_ARGS`, and uppercases the command. `acpi_db_match_command` supports prefix matching against the command table. `acpi_db_command_dispatch` validates argument count, adds history, and routes each command to the corresponding debugger subsystem. `acpi_db_execute_thread` and `acpi_db_user_commands` run the interactive loop using OS command-ready/complete callbacks.

## Control Flow, State, And Persistence
Input dispatch flow is copy line, tokenize in place by inserting NUL terminators, uppercase command, match prefix, optionally record history, validate minimum args, switch on command ID, return an ACPICA control status. Single-step commands return `AE_OK` to resume execution or `AE_CTRL_TERMINATE` to stop. The user loop runs until `acpi_gbl_db_terminate_loop`, resetting method-execution and step-to-call flags before each command and notifying the OS layer when complete.

## Dependencies And Integration Points
This is the hub for debugger modules: namespace displays, object dumps, method execution, resource displays, statistics, tracing, file I/O, table load/unload, hardware simulation, predefined-name tests, and history. Build flags gate application-only commands and disassembler-dependent commands. It depends on global debugger buffers/argument arrays, OS command synchronization hooks, and status codes used by the AML interpreter single-step loop.

## Risks And Test Signals
Prefix matching can make ambiguous abbreviations order-dependent. Tokenization mutates the parsed buffer and does not report unmatched quote/paren/bracket errors explicitly, so later conversion may see malformed tokens. Several commands assume optional args may be NULL, while minimum-argument validation only checks required counts. Test signals include help output, abbreviated command matching, nested package argument parsing, history recall dispatch, single-step commands during method execution, application-only commands, command loop termination, and malformed input fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbinput.c -->
