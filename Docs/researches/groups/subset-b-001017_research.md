# Research: subset-b-001017

Grouped research for ACPICA hardware sleep/timer interfaces, I/O validation, public hardware entry points, and namespace access, allocation, evaluation, loading, initialization, pathname, object attachment, predefined return validation, package validation, and repair code. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c

## Purpose
Implements legacy ACPI sleep and wake transitions through the original FADT PM1/PM2 register model for non-reduced-hardware systems. It is the low-level half of the public sleep API: callers prepare global sleep-type values elsewhere, then this file programs `SLP_TYP`/`SLP_EN`, manages wake GPEs, waits for wake status, and restores post-resume ACPI state.

## Important APIs, Types, And Functions
Exports internal hardware routines `acpi_hw_legacy_sleep`, `acpi_hw_legacy_wake_prep`, and `acpi_hw_legacy_wake`. They use `struct acpi_bit_register_info`, fixed bit register IDs such as `ACPI_BITREG_SLEEP_TYPE`, `ACPI_BITREG_SLEEP_ENABLE`, and `ACPI_BITREG_WAKE_STATUS`, and globals including `acpi_gbl_sleep_type_a/b`, `acpi_gbl_sleep_type_a_s0/b_s0`, `acpi_gbl_system_awake_and_running`, and fixed event metadata.

## Control Flow
`acpi_hw_legacy_sleep` clears wake status, disables runtime GPEs, clears ACPI status, marks the system not awake, enables wake GPEs, reads PM1 control, writes sleep type first, flushes CPU caches for S1-S3, lets `acpi_os_enter_sleep` veto or prepare platform sleep, writes sleep enable, retries S4/S5 after a long stall if execution continues, then polls `WAK_STS`. Wake preparation optionally writes S0 sleep type back into PM1 control. Final wake disables all GPEs, enables runtime GPEs, invokes `_WAK`, clears `WAK_STS`, restores power/sleep button fixed events, and reports `_SST` working.

## State And Persistence
The file mutates ACPI global sleep type state, global awake/running state, PM1 control/status registers, fixed event enable/status bits, and GPE enable masks. Nothing is durable beyond hardware register state across suspend/resume.

## Dependencies And Integration Points
Depends on ACPICA hardware register helpers, GPE management, fixed event metadata, OS hooks for entering sleep and stalling, and AML sleep methods `_SST` and `_WAK`. It is selected by `hwxfsleep.c` when `acpi_gbl_reduced_hardware` is false.

## Risks And Edge Cases
This code must run with the documented interrupt state; wrong ordering can miss wake events or leave GPEs disabled. Firmware quirks require split `SLP_TYP`/`SLP_EN` writes and S4/S5 retry behavior. Errors while re-enabling runtime GPEs can affect wake-device behavior after resume. Polling wake status assumes the platform eventually sets `WAK_STS`.

## Test Signals
Suspend/resume tests for S1-S5 on legacy ACPI machines, wake from GPE devices, power/sleep button events after resume, PM1 control tracing, `_WAK` execution logs, and failure injection around GPE disable/enable and PM1 register writes are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c

## Purpose
Provides the exported ACPICA PM timer interface for non-reduced-hardware systems. It reports timer width, reads the current PM timer tick value, and converts two PM timer snapshots into elapsed microseconds while handling one rollover.

## Important APIs, Types, And Functions
Exports `acpi_get_timer_resolution`, `acpi_get_timer`, and `acpi_get_timer_duration`. Key inputs are `acpi_gbl_FADT.flags`, `ACPI_FADT_32BIT_TIMER`, `acpi_gbl_FADT.xpm_timer_block`, `ACPI_PM_TIMER_FREQUENCY`, and `ACPI_USEC_PER_SEC`.

## Control Flow
Resolution returns 24 bits unless the FADT advertises the 32-bit timer flag. Timer reads reject null output pointers, return `AE_SUPPORT` if ACPI 5.0-style optional PM timer address is absent, then read the GAS via `acpi_hw_read` and truncate to 32 bits. Duration validates output and timer presence, handles equal timestamps as zero, extends `end_ticks` by 2^24 or 2^32 when the interval crosses one wrap, subtracts `start_ticks`, and divides ticks times microseconds-per-second by PM timer frequency.

## State And Persistence
This file is stateless except for reads from FADT-derived global table state. It does not latch hardware or store calibration data.

## Dependencies And Integration Points
Depends on generic GAS reads and ACPICA integer division helpers. Consumers include OS/platform code needing stable firmware timer measurements across CPU C-states.

## Risks And Edge Cases
The duration helper only supports a single rollover, so long intervals on 24-bit timers produce incorrect elapsed time. Missing timer blocks must be handled by callers. Firmware with incorrect 24/32-bit FADT flags changes rollover behavior.

## Test Signals
Validate resolution on FADT variants, reads from real or emulated PM timer GAS addresses, zero-duration behavior, rollover cases for 24-bit and 32-bit timers, missing timer block handling, and comparison against known elapsed wall-clock intervals below rollover limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c

## Purpose
Implements ACPICA validation for AML system-I/O port accesses. It enforces protected port ranges for DMA, PIC, PIT, RTC/CMOS, PCI config, and related legacy hardware, while preserving compatibility by allowing byte-granular partial access around illegal bytes.

## Important APIs, Types, And Functions
Core routines are `acpi_hw_validate_io_request`, `acpi_hw_read_port`, `acpi_hw_write_port`, and `acpi_hw_validate_io_block`. The central table is `acpi_protected_ports[]` of `struct acpi_port_info`, keyed by port range and `_OSI` dependency, plus globals `acpi_gbl_osi_data` and `acpi_gbl_truncate_io_addresses`.

## Control Flow
Validation accepts only 8/16/32-bit accesses, computes the byte range, rejects requests above 64 KiB, then scans the ordered protected-port table for overlap. Always-illegal ranges and ranges matching the BIOS-selected `_OSI` compatibility level return `AE_AML_ILLEGAL_ADDRESS`. Read/write wrappers optionally truncate addresses to 16 bits, try a whole access first, and on illegal-address status retry one byte at a time, skipping protected bytes but preserving readable/writable unprotected bytes. Block validation repeats request validation for each register-sized element.

## State And Persistence
No persistent state is stored here, but behavior depends on global `_OSI` data and the truncate-I/O-address compatibility flag set during namespace/device initialization.

## Dependencies And Integration Points
Wraps OSL port I/O (`acpi_os_read_port`, `acpi_os_write_port`) and is used by ACPICA region/register access paths. The rules mirror Microsoft ACPI compatibility restrictions.

## Risks And Edge Cases
Incorrect table ordering would break the early-exit scan. Partial-byte fallback can mask firmware bugs and produce synthetic values with skipped bytes zeroed. `_OSI` compatibility changes whether some ports are blocked. Address truncation can redirect accesses on systems with invalid firmware addresses.

## Test Signals
Exercise protected and unprotected ranges, overlap at start/end/full containment, invalid widths, above-64K requests, `_OSI`-dependent behavior, truncate mode, and partial reads/writes spanning protected and unprotected bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c

## Purpose
Provides public ACPICA hardware interfaces for reset, generic GAS reads/writes, fixed bit register access, and sleep type discovery from namespace `_Sx` objects.

## Important APIs, Types, And Functions
Exports `acpi_reset`, `acpi_read`, `acpi_write`, `acpi_read_bit_register`, `acpi_write_bit_register`, and `acpi_get_sleep_type_data`. Important types are `struct acpi_generic_address`, `struct acpi_bit_register_info`, `struct acpi_evaluate_info`, and operand packages returned by AML evaluation.

## Control Flow
`acpi_reset` verifies the FADT reset flag and address, bypasses port validation for system-I/O reset registers with an 8-bit write, and otherwise uses `acpi_hw_write`. Generic read/write are direct public wrappers over GAS helpers. Bit-register reads locate metadata, read the parent register, mask and shift. Bit-register writes take the raw hardware lock, preserve unrelated bits for enable/control registers, and use write-one-to-clear semantics for PM1 status. Sleep type discovery allocates an evaluation block, evaluates the appropriate `_Sx` object, accepts either one encoded integer or at least two integer elements, fills type A/B, reports malformed returns, and releases references.

## State And Persistence
Mutates reset hardware, ACPI fixed registers, and caller-provided sleep type outputs. It temporarily allocates evaluation info and references returned AML objects.

## Dependencies And Integration Points
Integrates FADT data, GAS access, raw hardware lock, namespace evaluation, predefined-name validation, and sleep-state name globals. It is a public API surface exported to kernel ACPI code.

## Risks And Edge Cases
Reset deliberately bypasses I/O validation for compatibility. Bit-register writes must preserve status semantics or they may clear unrelated events. `_Sx` packages are firmware-controlled and may be absent, empty, wrongly typed, or encoded in vendor-compatible two-integer form.

## Test Signals
Check reset register variants, GAS memory/I/O read-write behavior, PM1 status write-one-to-clear behavior, locking under concurrent bit access, and `_S0`-`_S5` package shapes including missing, one-integer, two-integer, empty, and wrong-type returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c

## Purpose
Implements exported ACPI sleep/wake orchestration APIs above the legacy and extended hardware backends. It sets firmware waking vectors, handles S4BIOS, prepares sleep by evaluating control methods, dispatches sleep entry, and dispatches wake cleanup.

## Important APIs, Types, And Functions
Exports `acpi_set_firmware_waking_vector`, `acpi_enter_sleep_state_s4bios`, `acpi_enter_sleep_state_prep`, `acpi_enter_sleep_state`, `acpi_leave_sleep_state_prep`, and `acpi_leave_sleep_state`. Internal helper `acpi_hw_set_firmware_waking_vector` updates FACS wake vector fields.

## Control Flow
Wake vector setup writes the 32-bit FACS vector and conditionally writes or clears the 64-bit vector based on FACS length/version. S4BIOS clears wake/status state, disables GPEs, enables wake GPEs, writes the FADT SMI command request, and polls wake status. Sleep prep obtains target sleep types and S0 sleep types, runs `_PTS`, maps the target sleep state to `_SST`, and invokes `_SST`. Sleep entry validates cached sleep type bounds, then chooses legacy or extended sleep based on reduced-hardware state. Wake prep and final wake similarly dispatch to legacy or extended backend functions.

## State And Persistence
Mutates FACS wake vector fields, global sleep type caches, global awake/running state via backend calls, and platform firmware-visible PM/GPE state. Sleep prep state persists only until entry or wake clears/invalidates it.

## Dependencies And Integration Points
Connects public ACPICA sleep APIs to FACS, FADT SMI fields, namespace methods `_PTS` and `_SST`, legacy sleep in `hwsleep.c`, and extended sleep in reduced-hardware support.

## Risks And Edge Cases
Firmware wake vector handling is compatibility-sensitive, especially systems that fail with 64-bit vectors. Calling entry without successful prep leaves invalid sleep types and returns operand errors. S4BIOS polling can hang if wake status never appears. Optional `_PTS`/`_SST` behavior must distinguish `AE_NOT_FOUND` from real failures.

## Test Signals
Suspend/resume paths for legacy and reduced-hardware systems, FACS vector inspection, S4BIOS request tests, invalid sleep type cache tests, `_PTS` failure propagation, optional `_SST` absence, and backend dispatch under `acpi_gbl_reduced_hardware`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c

## Purpose
Provides top-level namespace initialization and lookup. It creates the root namespace with predefined objects and resolves AML internal pathnames relative to scopes, optionally creating nodes during table load.

## Important APIs, Types, And Functions
Primary routines are `acpi_ns_root_initialize` and `acpi_ns_lookup`. They operate on `struct acpi_namespace_node`, `union acpi_generic_state` scope records, `struct acpi_walk_state`, predefined-name descriptors, owner IDs, and namespace flags such as `ACPI_NS_SEARCH_PARENT`, `ACPI_NS_PREFIX_MUST_EXIST`, and `ACPI_NS_DONT_OPEN_SCOPE`.

## Control Flow
Root initialization locks the namespace, installs predefined root children from `acpi_gbl_pre_defined_names`, creates initial operand objects for methods, integers, strings, and mutexes, initializes special `_OSI` and `_GL_`, attaches objects, releases local references, unlocks, then caches `\_GPE`. Lookup chooses root or caller prefix, backs up to an opening scope when needed, parses root and parent prefixes, decodes null/dual/multi/simple AML name formats, searches each segment with creation rules tied to interpreter mode, handles aliases that open scopes, warns on terminal type mismatch, and pushes a new scope on the walk stack for scope-opening objects.

## State And Persistence
Creates and mutates persistent global namespace nodes, root-node globals, attached initial objects, global lock mutex/semaphore, `_GPE` cached handle, lookup counters, and walk-state scope stack entries.

## Dependencies And Integration Points
Depends on namespace allocation/search, object attachment, predefined name tables, OSL mutex/semaphore creation, AML name encoding, dispatcher scope-stack management, and optional compiler/disassembler behavior.

## Risks And Edge Cases
Lookup must correctly implement ACPI upward-search rules only for single relative names. Parent-prefix overrun returns `AE_NOT_FOUND`. Namespace creation during load can collide with existing names. Special compiler and ACPI_EXEC paths alter duplicate/external behavior. Root initialization failure can leave partially created predefined nodes.

## Test Signals
Tests should cover absolute, relative, parent-prefixed, dual, multi, and null paths; load-pass creation; execute-mode not-found behavior; alias scope traversal; duplicate names; predefined root object presence; `_OSI` optional creation; and scope stack push behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c

## Purpose
Implements namespace node allocation, installation, removal, subtree deletion, and owner-based deletion. This is the lifecycle layer for `struct acpi_namespace_node` entries created while loading tables or executing methods.

## Important APIs, Types, And Functions
Key functions are `acpi_ns_create_node`, `acpi_ns_delete_node`, `acpi_ns_remove_node`, `acpi_ns_install_node`, `acpi_ns_delete_children`, `acpi_ns_delete_namespace_subtree`, and `acpi_ns_delete_namespace_by_owner`. It uses namespace cache objects, node owner IDs, peer/child/parent links, and method flags such as `ACPI_METHOD_MODIFIED_NAMESPACE`.

## Control Flow
Node creation obtains a zeroed node from the namespace cache, tracks allocation statistics, sets the name and descriptor type. Installation appends the node to its parent's child peer list, assigns owner/type, and marks methods that create non-local namespace entries. Deletion detaches regular objects, invokes attached data handlers, frees data descriptors, and releases non-root nodes to the cache. Subtree deletion walks depth-first under the namespace mutex, detaches objects before descending, then deletes children when bubbling up. Owner deletion walks from root, detaches matching-owner objects, and removes matching leaf/subtree nodes after child cleanup.

## State And Persistence
Mutates the persistent namespace tree, object reference counts through detach/delete, allocation counters, method info flags, and owner-tagged nodes associated with ACPI tables or dynamic method-created objects.

## Dependencies And Integration Points
Depends on namespace cache allocation, object detach/reference handling, attached-data callbacks, mutex protection, and owner IDs allocated by table management.

## Risks And Edge Cases
`acpi_ns_remove_node` assumes the node exists in its parent's child list. Deletion order must avoid using freed peer links. Owner deletion defers removal with `deletion_node` to keep traversal stable. Root node is static and must not be freed.

## Test Signals
Useful tests load/unload tables by owner, create method-local and non-local names, attach data handlers, delete deep subtrees, verify reference counts, and run namespace mutation under lockdep or sanitizer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c

## Purpose
Validates argument declarations and caller-supplied arguments for ACPI predefined methods and ordinary control methods. It emits firmware/caller diagnostics without usually blocking execution.

## Important APIs, Types, And Functions
Provides `acpi_ns_check_argument_types`, `acpi_ns_check_acpi_compliance`, and `acpi_ns_check_argument_count`. It uses `struct acpi_evaluate_info`, `union acpi_predefined_info`, method argument-list bitfields, node flags such as `ANOBJ_EVALUATED`, and method parameter counts from attached method objects.

## Control Flow
Type checking only applies to predefined names that have not already been evaluated; it walks the expected type list and compares actual operand object types. ACPI compliance checks predefined method declarations: non-method objects are flagged when the spec requires a method, and method AML parameter counts are compared with required or minimum counts. Caller argument-count checking handles non-predefined methods by comparing caller count with AML declaration, and predefined names by comparing caller count with the ACPI spec.

## State And Persistence
No objects are modified except `ANOBJ_EVALUATED`, which suppresses repeated warning noise for a node after a mismatch. Diagnostics persist only in logs.

## Dependencies And Integration Points
Called from `acpi_ns_evaluate` before method execution or object resolution. Depends on predefined-name tables and ACPICA warning macros.

## Risks And Edge Cases
The code intentionally warns rather than fails for many mismatches, so invalid firmware may continue until AML actually references missing arguments. `ANOBJ_EVALUATED` suppresses future type warnings, trading log clarity for reduced repetition. Minimum-argument predefined methods require special handling.

## Test Signals
Evaluate predefined and non-predefined methods with too few, exact, and excess arguments; wrong argument object types; non-method predefined objects; `_SCP`-style minimum counts; and repeated evaluation to verify warning suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c

## Purpose
Provides conversion helpers used by predefined-object repair. These routines turn common firmware return mistakes into the ACPI-specified object forms consumed by drivers.

## Important APIs, Types, And Functions
Exports internal converters `acpi_ns_convert_to_integer`, `acpi_ns_convert_to_string`, `acpi_ns_convert_to_buffer`, `acpi_ns_convert_to_unicode`, `acpi_ns_convert_to_resource`, and `acpi_ns_convert_to_reference`. They operate on `union acpi_operand_object`, namespace scopes, AML resource end tags, and reference objects.

## Control Flow
Integer conversion accepts strings parsed as integers and buffers up to 8 bytes interpreted little-endian. String conversion accepts integer zero as an empty string, nonzero integers through implicit hex conversion, and buffers copied until NUL. Buffer conversion accepts integers, strings, and packages of integer DWORDs. Unicode conversion leaves valid buffers alone or expands ASCII strings to UTF-16LE buffers. Resource conversion repairs null, zero, or empty returns into an end-tag resource template. Reference conversion internalizes a returned pathname string, looks it up relative to scope, and builds a named-reference object.

## State And Persistence
Creates new operand objects and may add a reference to a resolved namespace node's attached object for references. It does not install converted objects itself; callers replace or wrap return values.

## Dependencies And Integration Points
Used by `nsrepair.c` and return validation. Depends on interpreter conversion helpers, namespace lookup/internalization, resource descriptor constants, and object allocation/reference management.

## Risks And Edge Cases
Buffer-to-integer refuses buffers larger than 64 bits. Buffer-to-string truncates at first NUL. Package-to-buffer requires every element to be an integer. Reference conversion depends on correct scope search and can fail if firmware returns an invalid path.

## Test Signals
Cover each supported conversion, malformed numeric strings, oversized buffers, packages with null or non-integer elements, Unicode string/buffer returns, resource null/zero/empty repair, and `_DEP`-style string-to-reference resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c

## Purpose
Implements debug and debugger namespace dump utilities. It formats namespace nodes, attached operand objects, object paths, owner filtering, and selected object internals for ACPICA diagnostics.

## Important APIs, Types, And Functions
When debug support is enabled, key functions include `acpi_ns_print_pathname`, `acpi_ns_dump_one_object`, `acpi_ns_dump_objects`, `acpi_ns_dump_object_paths`, `acpi_ns_dump_entry`, and compiler-only `acpi_ns_dump_tables`. It uses `struct acpi_walk_info`, namespace walk callbacks, debug level masks, and many operand object variants.

## Control Flow
Dump entry points acquire the namespace mutex, build walk context, and call `acpi_ns_walk_namespace` with no-unlock/temp-node flags. Per-object dumping validates handles, filters by owner, prints type/name/owner, fetches the attached object with debug output suppressed, and formats summaries for processors, devices, methods, integers, packages, buffers, strings, regions, references, fields, and aliases. Object-path dumping first computes max depth for alignment, then prints normalized paths.

## State And Persistence
This file should not mutate namespace state, except temporary debug-level suppression while fetching objects. It reads live namespace and attached object state under the namespace mutex.

## Dependencies And Integration Points
Depends on debug builds (`ACPI_DEBUG_OUTPUT`, `ACPI_DEBUGGER`, and compiler gates), namespace walking, object formatting helpers, and ACPICA output functions.

## Risks And Edge Cases
Dumping live objects requires namespace locking to avoid temporary node churn. Some formatting reaches secondary object pointers and raw AML/buffer memory, so stale or malformed object descriptors can produce misleading diagnostics. Most code is compile-gated and may not be covered in normal kernels.

## Test Signals
Enable ACPICA debug output/debugger, dump full and filtered namespaces, inspect object paths, exercise owner filters, include method-created temporary nodes, and run with regions, fields, aliases, packages, and buffers present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c

## Purpose
Contains obsolete, compile-gated debug helpers for dumping root devices and selected device identity data from the namespace.

## Important APIs, Types, And Functions
Under `ACPI_OBSOLETE_FUNCTIONS` and debug gates, defines `acpi_ns_dump_one_device` and `acpi_ns_dump_root_devices`. It uses `acpi_ns_dump_one_object`, `acpi_get_object_info`, `struct acpi_device_info`, and namespace walking for `ACPI_TYPE_DEVICE`.

## Control Flow
`acpi_ns_dump_root_devices` checks table-debug level, obtains the `\_SB_` handle, prints a heading, and walks all device objects below it. The per-device callback delegates generic object dumping, asks ACPICA for object info, then prints HID and ADR with indentation.

## State And Persistence
No persistent state is modified. It allocates and frees the temporary object-info buffer returned by `acpi_get_object_info`.

## Dependencies And Integration Points
Only compiled for obsolete debug configurations. Integrates with namespace dump support and object-info evaluation helpers that may evaluate device identification methods.

## Risks And Edge Cases
The module is explicitly marked obsolete. Because object info may depend on firmware methods, debug dumping can have side effects or fail on malformed devices. It silently returns if debug level is disabled or `\_SB_` is absent.

## Test Signals
Build with obsolete/debug options, enable table debug level, verify device listings under `\_SB_`, include devices with and without HID/ADR data, and confirm buffers from `acpi_get_object_info` are freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nseval.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nseval.c

## Purpose
Implements namespace object evaluation, including control method execution and non-method object value resolution. It is the central path behind `acpi_evaluate_object`-style operations.

## Important APIs, Types, And Functions
Primary routine is `acpi_ns_evaluate`. It uses `struct acpi_evaluate_info`, namespace nodes, attached operand objects, predefined method metadata, interpreter lock functions, parser execution, object resolution, and return-value validation.

## Control Flow
Evaluation resolves the target node if needed, follows method aliases, initializes evaluation info, gets predefined metadata and full pathname, counts arguments with a hard cap, runs predefined compliance/count/type checks, and branches by node type. Non-evaluable namespace container types return `AE_TYPE`. Methods require an attached method object and execute under the interpreter lock via `acpi_ps_execute_method`. Other objects are resolved to values under the interpreter lock with `acpi_ex_resolve_node_to_value`. Predefined return validation and repair then runs, ignored returns are deleted, `AE_CTRL_RETURN_VALUE` is normalized to `AE_OK`, and failed returns are dereferenced.

## State And Persistence
Mutates only evaluation info, returned object references, possible predefined warning-suppression flags, and any side effects caused by executing AML methods or resolving operation regions.

## Dependencies And Integration Points
Integrates namespace lookup, argument validation, AML parser/interpreter, object resolution, predefined return checking, and ACPI debug/evaluation logging.

## Risks And Edge Cases
Correct interpreter locking is required because resolution can access operation regions. Methods without attached objects fail. Return-object ownership is subtle: ignored or failed returns must be dereferenced exactly once. Predefined repair can change object identity before callers receive it.

## Test Signals
Evaluate methods, method aliases, fields/regions, constants, invalid container types, missing methods, excess arguments, ignored returns, failing AML methods, and predefined methods with repairable and nonrepairable returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nseval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c

## Purpose
Completes ACPICA namespace initialization after table load. It initializes deferred objects, runs device initialization methods, initializes address-space regions, and invokes global initialization handlers.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_initialize_objects`, `acpi_ns_initialize_devices`, `acpi_ns_init_one_package`, and callbacks `acpi_ns_init_one_object`, `acpi_ns_find_ini_methods`, and `acpi_ns_init_one_device`. It uses `struct acpi_init_walk_info`, `struct acpi_device_walk_info`, `_STA`, `_INI`, `_REG`, and flags such as `ANOBJ_SUBTREE_HAS_INI`.

## Control Flow
Object initialization walks the namespace, counts objects, and initializes deferred package/bank-field data under the interpreter lock. Device initialization optionally scans for `_INI` methods and bubbles `ANOBJ_SUBTREE_HAS_INI` up ancestors, allocates shared evaluation info, runs root `_INI` and `\_SB._INI`, initializes operation regions unless disabled, then walks present device/processor/thermal objects. Each device checks subtree tagging, evaluates `_STA`, prunes absent nonfunctional subtrees, skips `_INI` for absent-but-functional bridge-like nodes, evaluates `_INI` when present, and calls the global init handler.

## State And Persistence
Sets package data-valid flags, subtree-has-INI flags, global truncate-I/O-address compatibility after `_OSI` use, operation-region handler state through event code, and counters used for diagnostics.

## Dependencies And Integration Points
Depends on namespace walking, dispatcher deferred-argument initialization, interpreter locking, event/op-region initialization, `_STA` execution helpers, `acpi_ns_evaluate`, and global init callbacks.

## Risks And Edge Cases
Initialization intentionally ignores many per-object errors to continue booting. `_STA` semantics control subtree pruning and can hide children if firmware reports absent/nonfunctional. `\_SB._INI` ordering before `_REG` is compatibility-sensitive. Shared evaluation info must be cleared between method calls.

## Test Signals
Boot tests with devices containing `_INI`, absent `_STA`, absent/functioning bridge states, failing `_INI`, operation regions requiring `_REG`, deferred packages with forward references, and `_OSI` calls that should enable I/O truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c

## Purpose
Loads ACPI tables into the namespace and initializes table-owned objects. It also contains obsolete/future namespace unload helpers behind compile-time gates.

## Important APIs, Types, And Functions
Primary live API is `acpi_ns_load_table`. Gated routines include `acpi_ns_load_namespace`, `acpi_ns_delete_subtree`, and `acpi_ns_unload_namespace`. It coordinates table indices, owner IDs, namespace parse, loaded flags, and dispatcher object initialization.

## Control Flow
`acpi_ns_load_table` returns `AE_ALREADY_EXISTS` for already-loaded tables, allocates an owner ID, parses the table into the namespace, marks the table loaded on success, or deletes all namespace nodes owned by the table and releases the owner ID on parse failure. It then enters the interpreter and calls `acpi_ds_initialize_objects` to parse/initialize control methods and deferred objects. Gated legacy code loads DSDT/SSDT/PSDT by type; future unload code walks a subtree and deletes children.

## State And Persistence
Mutates table loaded flags, table owner IDs, namespace nodes and objects owned by loaded tables, and initialized method/object state. Failure paths remove partially loaded namespace content.

## Dependencies And Integration Points
Depends on table manager ownership, namespace parsing in `nsparse.c`, namespace owner deletion in `nsalloc.c`, dispatcher initialization, and interpreter locking.

## Risks And Edge Cases
Namespace collisions and missing `Scope` targets during parse are treated as severe load failures and trigger owner cleanup. The function returns `AE_ALREADY_EXISTS` for duplicate loads, which callers must treat appropriately. Partial cleanup correctness depends on accurate owner IDs.

## Test Signals
Load DSDT/SSDT-like tables, duplicate table loads, parse failures after some names are created, namespace collision cases, missing scope target cases, owner cleanup validation, and method-object initialization after successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c

## Purpose
Builds and normalizes namespace names and paths. It converts handles to simple names or full paths, constructs normalized absolute paths, combines scope prefixes with internal AML paths, and strips trailing underscores for display.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_get_external_pathname`, `acpi_ns_get_pathname_length`, `acpi_ns_handle_to_name`, `acpi_ns_handle_to_pathname`, `acpi_ns_build_normalized_path`, `acpi_ns_get_normalized_pathname`, `acpi_ns_build_prefixed_pathname`, and `acpi_ns_normalize_pathname`.

## Control Flow
Handle helpers validate namespace handles, calculate required buffer sizes with `acpi_ns_build_normalized_path`, initialize caller buffers, then write names or full paths. Normalized path building walks from node to root, writes reversed name segments with optional trailing-underscore suppression and root prefix, reverses the assembled buffer, and appends NUL. Prefix building obtains the prefix scope path, externalizes the internal AML path, avoids prepending when the path is already absolute or parent-prefixed, normalizes display underscores, and concatenates. Pathname normalization copies special prefixes then removes trailing underscores from each segment in place via a temporary buffer.

## State And Persistence
No namespace state is mutated. The file allocates returned pathname buffers and initializes caller-provided buffers.

## Dependencies And Integration Points
Used by diagnostics, evaluation warnings, namespace dumping, and error reporting. Depends on handle validation, AML name externalization, ACPICA buffer initialization, and allocation utilities.

## Risks And Edge Cases
Path-size computation and write mode share one routine, so off-by-one errors would affect caller buffer contracts. `no_trailing` must not remove leading underscores. Prefix concatenation must preserve fully qualified and parent-prefixed paths. Invalid handles return bad-parameter statuses.

## Test Signals
Check root paths, deep paths, names with trailing underscores, leading underscore segments, parent/root-prefixed internal paths, too-small caller buffers, invalid handles, and allocated path freeing under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c

## Purpose
Manages objects and caller data attached to namespace nodes. It attaches/detaches operand objects, retrieves primary/secondary objects, and stores opaque handler-keyed data objects.

## Important APIs, Types, And Functions
Provides `acpi_ns_attach_object`, `acpi_ns_detach_object`, `acpi_ns_get_attached_object`, `acpi_ns_get_secondary_object`, `acpi_ns_attach_data`, `acpi_ns_detach_data`, and `acpi_ns_get_attached_data`. It uses operand descriptor lists, node object pointers, node types, region address-range registration, and local data objects.

## Control Flow
Attach validates node/object parameters, resolves namespace-node inputs to their attached object, detaches any existing non-data object, increments the new object's reference count, chains multi-descriptor objects before data objects, updates node type, and stores the object. Detach ignores pure data lists, frees allocated method AML buffers when flagged, removes operation-region address ranges, unlinks primary/secondary descriptors while preserving data attachments, resets node type, and drops the object reference. Data attach scans for duplicate handlers, creates a local-data object, and appends it; detach and get scan the linked list by handler.

## State And Persistence
Mutates namespace node object pointers and types, operand reference counts, local data attachment lists, allocated method AML buffers, and global region address-range tracking.

## Dependencies And Integration Points
Used throughout namespace load, evaluation, deletion, and driver data attachment APIs. Depends on object allocation/reference utilities and region address range helpers.

## Risks And Edge Cases
Reference count ownership is subtle when attaching an object already referenced elsewhere. Multi-descriptor objects and data attachments share the same `next_object` chain, so detach must preserve data nodes. Region detach must unregister address ranges to avoid stale handlers.

## Test Signals
Attach/detach integers, methods with allocated AML, regions, data-only nodes, duplicate data handlers, secondary descriptor objects, namespace-node aliases as attach sources, and reference count/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c

## Purpose
Bridges namespace loading to the AML parser. In this version it executes a table as a module-level pseudo-method so module-level AML runs as the table is parsed.

## Important APIs, Types, And Functions
Key functions are `acpi_ns_execute_table`, `acpi_ns_one_complete_parse`, and `acpi_ns_parse_table`. They use table headers, AML ranges, owner IDs, parse roots, walk states, method operand objects, and parser/dispatcher entry points.

## Control Flow
`acpi_ns_execute_table` fetches the table, validates header length, derives AML start/length, gets owner ID, creates a temporary method object flagged `ACPI_METHOD_MODULE_LEVEL`, builds evaluation info rooted at the load node, logs module-level evaluation, and calls `acpi_ps_execute_table`. `acpi_ns_one_complete_parse` is the traditional pass parser: it creates a scope op and walk state, initializes AML walk for the requested pass, enables namespace override for OSDT pass 1, optionally pushes a non-root start scope, parses AML under interpreter lock, and deletes the parse tree. `acpi_ns_parse_table` currently delegates to table execution.

## State And Persistence
Temporary method/evaluation/parse objects are allocated and freed. Persistent namespace mutations come from parser execution and use the table owner ID.

## Dependencies And Integration Points
Used by `nsload.c`. Depends on table lookup, owner IDs, parser, dispatcher walk-state management, interpreter locking, and namespace root/start nodes.

## Risks And Edge Cases
Malformed table lengths fail early. Module-level execution changes semantics versus pure two-pass loading and can run AML side effects during parse. Cleanup must release temporary method references and full path buffers on all exits.

## Test Signals
Parse valid and short-header tables, module-level AML side effects, OSDT override behavior, non-root load nodes, owner ID propagation, parser failures with cleanup, and comparison with pass parser configurations if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nspredef.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nspredef.c

## Purpose
Validates return values from ACPI predefined names at evaluation time. It checks expected top-level types, package contents, reference classes, and invokes repair paths for common firmware mistakes.

## Important APIs, Types, And Functions
Primary APIs are `acpi_ns_check_return_value` and `acpi_ns_check_object_type`, with helpers `acpi_ns_check_reference` and `acpi_ns_get_bitmapped_type`. It uses predefined info tables, bitmapped return types (`ACPI_RTYPE_*`), `struct acpi_evaluate_info`, node flags, and package/repair helpers.

## Control Flow
Return checking exits for non-predefined names, failed evaluations, disabled auto repair, names expecting no value, or names accepting all types. It validates the top-level object against expected bitmaps, treats optional no-return cases as OK, validates packages through `acpi_ns_check_package`, then performs complex per-name repairs. Object type checking rejects namespace nodes as returns, maps operand types to bitmaps, validates named-reference classes, attempts simple repair, and emits mismatch warnings when repair fails.

## State And Persistence
May replace return objects through repair, set `info->return_flags`, update `info->return_btype`, and mark namespace nodes `ANOBJ_EVALUATED` to suppress repeated warnings after failures or repairs.

## Dependencies And Integration Points
Called by `acpi_ns_evaluate` after method execution/object resolution. Depends on predefined metadata generated by `ACPI_CREATE_PREDEFINED_TABLE`, package validation, simple and complex repair modules, and ACPICA diagnostics.

## Risks And Edge Cases
Overly aggressive repair can hide firmware defects, but failed validation can break drivers expecting sanitized data. Reference returns are valid only for named references. Warning suppression means later different bad returns may be quieter after first evaluation.

## Test Signals
Evaluate predefined methods returning correct types, wrong scalar types, namespace nodes, wrong reference classes, optional null returns, package returns, repair-disabled mode, and repeated bad returns to check `ANOBJ_EVALUATED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nspredef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsprepkg.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsprepkg.c

## Purpose
Validates package-shaped return values for predefined ACPI names. It enforces package counts, subpackage layout, element types, UUID pair rules, and selected custom layouts such as `_BIX`.

## Important APIs, Types, And Functions
Main routine is `acpi_ns_check_package`, supported by `acpi_ns_check_package_list`, `acpi_ns_custom_package`, and `acpi_ns_check_package_elements`. It consumes package descriptors in the predefined info table and calls `acpi_ns_check_object_type` for element validation and repair.

## Control Flow
Top-level validation removes null elements for variable package forms, rejects empty fixed packages, dispatches by package type, and handles fixed, variable, optional, revised-fixed, count-prefixed, package-of-packages, UUID-pair, and custom forms. For package-of-package types, it can wrap a lone package into an outer package before validating subpackages. Subpackage validation checks each subpackage type and length, supports fixed and minimum-length variants, adjusts zero count fields to actual length for count packages, and validates element groups. `_BIX` custom validation checks version-dependent counts and expected integer/string groupings.

## State And Persistence
May mutate returned package objects by removing null elements, changing package counts, wrapping objects, replacing repaired elements, and adjusting zero count fields.

## Dependencies And Integration Points
Called from predefined return validation. Depends on predefined package metadata, null-element removal and wrapping in `nsrepair.c`, simple object repair, and ACPICA warning/debug macros.

## Risks And Edge Cases
Package metadata must exactly match ACPI spec expectations. In-place removal of null elements changes array ordering and count. Count-prefixed packages can be smaller than physical package length by design. UUID buffers must be exactly 16 bytes.

## Test Signals
Use predefined methods with fixed, variable, optional, package-of-package, count-prefixed, UUID-pair, and `_BIX` layouts; include too-small/oversized packages, null elements, lone subpackage needing wrap, bad element types, and zero count repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsprepkg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c

## Purpose
Repairs common invalid objects returned by predefined ACPI methods so ACPICA clients receive spec-compatible values despite firmware defects.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_simple_repair`, `acpi_ns_repair_null_element`, `acpi_ns_remove_null_elements`, and `acpi_ns_wrap_with_package`, plus the repair dispatch table `acpi_object_repair_info`. It uses converter functions from `nsconvert.c`, expected return bitmaps, package indexes, and `ACPI_OBJECT_REPAIRED`/`ACPI_OBJECT_WRAPPED` flags.

## Control Flow
Simple repair first checks name-specific conversions: resource-return names (`_CRS`, `_DMA`, `_PRS`) can become end-tag resource buffers; `_DEP` strings become references; `_MLS` and `_STR` strings become Unicode buffers. If returned type is already expected it succeeds. Missing package elements can be repaired to zero integer, empty string, or empty buffer. Otherwise it tries conversions to expected integer, string, buffer, or wraps a lone object in a package. Successful scalar repair replaces the old object and removes its reference; package-element repair preserves parent package reference count. Null removal compacts variable package element arrays and updates count. Wrapping creates a one-element outer package around the original object.

## State And Persistence
Mutates return object pointers, package elements/counts, object reference counts, and evaluation return flags. It does not alter namespace nodes directly except through caller-visible repaired returns.

## Dependencies And Integration Points
Used by `nspredef.c` and `nsprepkg.c`. Depends on conversion helpers, predefined method names, package metadata, reference-count utilities, and repair debug logging.

## Risks And Edge Cases
Repair is intentionally permissive and can hide BIOS bugs. Reference-count transfer differs for wrapped objects versus converted package elements. Null removal is safe only for selected variable package types. Missing top-level returns are not generally fabricated unless a name-specific repair allows it.

## Test Signals
Exercise resource null/zero/empty repairs, `_DEP` string paths, `_STR`/`_MLS` Unicode conversion, scalar type conversions, NULL package element replacement, variable-package null compaction, object wrapping, repair-disabled mode, and reference-count leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c -->
