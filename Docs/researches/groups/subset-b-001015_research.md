# Research: subset-b-001015

Grouped research for ACPICA event and executor files under `sources/distributed-fs/ceph-client/drivers/acpi/acpica`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evsci.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evsci.c

## Purpose
`evsci.c` owns SCI interrupt installation, dispatch, and removal for non-reduced-hardware ACPICA builds. It bridges the OS interrupt layer to ACPICA fixed-event, GPE, and host-installed SCI handler dispatch.

## Important APIs, Types, And Functions
Key entry points are `acpi_ev_install_sci_handler`, `acpi_ev_remove_all_sci_handlers`, `acpi_ev_sci_dispatch`, and `acpi_ev_gpe_xrupt_handler`. The private interrupt callback `acpi_ev_sci_xrupt_handler` is registered with `acpi_os_install_interrupt_handler`. It works with `struct acpi_gpe_xrupt_info`, `struct acpi_sci_handler_info`, `acpi_gbl_sci_handler_list`, `acpi_gbl_gpe_xrupt_list_head`, and `acpi_gbl_FADT.sci_interrupt`.

## Control Flow
The SCI interrupt path enters `acpi_ev_sci_xrupt_handler`, detects fixed events with `acpi_ev_fixed_event_detect`, detects GPEs with `acpi_ev_gpe_detect`, invokes host SCI callbacks through `acpi_ev_sci_dispatch`, increments `acpi_sci_count`, and returns an interrupt-handled bitmap. GPE block interrupts use `acpi_ev_gpe_xrupt_handler`, which skips fixed events and host SCI callbacks. Installation registers the SCI IRQ using the FADT SCI interrupt number and passes the GPE interrupt list as callback context. Removal unregisters the OS interrupt handler and frees all host SCI callback records.

## State And Persistence
State is process/kernel resident only. `acpi_gbl_sci_handler_list` is protected by `acpi_gbl_gpe_lock` during dispatch and teardown. `acpi_sci_count` is a runtime diagnostic counter. Removal drains the list by freeing each `struct acpi_sci_handler_info`; no persistent table or firmware state is updated here.

## Dependencies And Integration Points
The file depends on OS services for interrupt registration/removal and locks, ACPICA event detection in `acevents.h`, and FADT state. It is compiled out under `ACPI_REDUCED_HARDWARE`, matching platforms where legacy ACPI event hardware is absent.

## Risks
Host SCI handlers run at interrupt level while the GPE lock is held, so callbacks must be short, nonblocking, and careful about lock ordering. Removing handlers while interrupts are active depends on OS interrupt removal semantics. A stale or malformed GPE interrupt context would affect GPE detection for every SCI.

## Test Signals
Useful signals include successful SCI registration/removal, fixed-event dispatch after status bits are set, GPE dispatch from SCI and non-SCI GPE interrupt paths, host SCI callback ordering, no callback after removal, and correct no-op behavior in reduced-hardware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evsci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxface.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxface.c

## Purpose
`evxface.c` exposes high-level ACPI event interfaces: notify handlers, SCI handlers, global and fixed event handlers, GPE handlers, and ACPI global lock acquisition/release. It is the host-facing registration surface that updates ACPICA event dispatch state.

## Important APIs, Types, And Functions
Exports include `acpi_install_notify_handler`, `acpi_remove_notify_handler`, `acpi_install_sci_handler`, `acpi_remove_sci_handler`, `acpi_install_global_event_handler`, `acpi_install_fixed_event_handler`, `acpi_remove_fixed_event_handler`, `acpi_install_gpe_handler`, `acpi_install_gpe_raw_handler`, `acpi_remove_gpe_handler`, `acpi_acquire_global_lock`, and `acpi_release_global_lock`. The internal `acpi_ev_install_gpe_handler` installs normal or raw GPE handlers. Important state includes `acpi_gbl_global_notify`, per-object `notify_list`, `acpi_gbl_sci_handler_list`, `acpi_gbl_fixed_event_handlers`, GPE dispatch flags, and `acpi_gbl_global_lock_mutex`.

## Control Flow
Notify installation validates the handle and handler type, creates an attached namespace object if needed, rejects duplicate handlers, and links a `LOCAL_NOTIFY` object into one or both notify lists. Notify removal unlinks under the namespace mutex, then waits for deferred notify tasks to finish before dropping references. SCI handler installation allocates a callback node, takes the events mutex plus GPE lock, rejects duplicate callbacks, and pushes the node onto the global list. Fixed event installation stores the handler before clearing/enabling the event; removal disables then clears the handler pointer. GPE handler installation allocates a handler object, validates the GPE, preserves original method/notify dispatch state, disables an auto-enabled method GPE if needed, and swaps dispatch to handler or raw-handler mode. Removal restores the original dispatch state, may re-enable a previously enabled method/notify GPE, waits for deferred GPE tasks, then frees the handler. Global lock operations enter the interpreter and delegate to executor mutex logic.

## State And Persistence
All state is in ACPICA globals or namespace-attached objects. Notify objects use ACPICA reference counts, including an extra reference when the same object is linked into both system and device lists. GPE handler install persists original flags and method node so removal can restore firmware dispatch. Global lock state persists in the global lock mutex and firmware global lock handle.

## Dependencies And Integration Points
This file integrates namespace validation, event mutexes, GPE spinlock-protected state, fixed event register helpers from `evxfevnt.c`, GPE runtime reference helpers from the event core, OS deferred-event completion waits, and executor mutex/global-lock code from `exmutex.c`.

## Risks
Lock ordering is central: namespace/events mutexes are combined with the GPE spinlock in several paths. Handler removal must wait for deferred work or freed handler objects could be used asynchronously. GPE handler installation can temporarily suppress firmware methods, so removal must faithfully restore method/notify dispatch and runtime references. Fixed handler installation does not validate a null handler beyond event range, so callers must pass usable callbacks.

## Test Signals
Tests should cover duplicate install rejection, root versus per-device notify behavior, all-notify reference accounting, deferred work drain on removal, fixed event enable/disable rollback, normal versus raw GPE dispatch flags, restoring original GPE method state, and global lock recursive acquisition by one thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfevnt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfevnt.c

## Purpose
`evxfevnt.c` provides external interfaces for switching ACPI mode and controlling fixed ACPI events on non-reduced hardware.

## Important APIs, Types, And Functions
Exports are `acpi_enable`, `acpi_disable`, `acpi_enable_event`, `acpi_disable_event`, `acpi_clear_event`, and `acpi_get_event_status`. It relies on `acpi_gbl_fadt_index`, `acpi_gbl_reduced_hardware`, `acpi_gbl_fixed_event_info`, `acpi_gbl_fixed_event_handlers`, `acpi_hw_get_mode`, `acpi_hw_set_mode`, `acpi_read_bit_register`, and `acpi_write_bit_register`.

## Control Flow
`acpi_enable` validates that ACPI tables exist, no-ops on reduced-hardware or already-ACPI systems, requests ACPI mode through hardware, then polls up to 30,000 times at 100 microseconds per loop for mode confirmation. `acpi_disable` no-ops on reduced hardware or already-legacy systems, otherwise requests legacy mode. Fixed event enable/disable validates the event index, writes the enable bit, reads it back, and returns `AE_NO_HARDWARE_RESPONSE` if the bit did not change. Clearing writes the status bit with `ACPI_CLEAR_STATUS`. Status reads combine installed-handler, enable-bit, and status-bit information into `acpi_event_status`.

## State And Persistence
The ACPI/legacy mode transition changes platform hardware state. Fixed event operations update PM register bits. Handler presence is read from global handler slots but handler registration itself lives in `evxface.c`.

## Dependencies And Integration Points
These APIs are used by subsystem enable/disable code and fixed-event handler registration. They integrate with FADT-derived register metadata, ACPICA hardware access helpers, and event names for diagnostics. The whole module is excluded when reduced hardware support removes fixed event registers.

## Risks
Hardware may ignore mode or enable-bit transitions, and the code explicitly reports that as no response. The long ACPI-mode polling loop can add startup latency on slow firmware. Callers must not assume fixed events exist on reduced-hardware systems because these functions compile out or no-op in that configuration.

## Test Signals
Mock hardware tests should verify ACPI-mode success, timeout, already-enabled mode, missing FADT, fixed event bad-index rejection, enable/disable readback failure, status flag composition, and clear-status writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfevnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfgpe.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfgpe.c

## Purpose
`evxfgpe.c` is the external GPE control API layer. It initializes GPE blocks, manages runtime and wake references, masks/unmasks or directly sets GPE hardware state, installs/removes user GPE blocks, and maps system GPE indices back to GPE devices.

## Important APIs, Types, And Functions
Exports include `acpi_update_all_gpes`, `acpi_enable_gpe`, `acpi_disable_gpe`, `acpi_set_gpe`, `acpi_mask_gpe`, `acpi_mark_gpe_for_wake`, `acpi_setup_gpe_for_wake`, `acpi_set_gpe_wake_mask`, `acpi_clear_gpe`, `acpi_get_gpe_status`, `acpi_dispatch_gpe`, `acpi_finish_gpe`, `acpi_disable_all_gpes`, `acpi_enable_all_runtime_gpes`, `acpi_enable_all_wakeup_gpes`, `acpi_any_gpe_status_set`, `acpi_install_gpe_block`, `acpi_remove_gpe_block`, and `acpi_get_gpe_device`. Key types are `struct acpi_gpe_event_info`, `struct acpi_gpe_register_info`, `struct acpi_gpe_block_info`, and `struct acpi_gpe_notify_info`.

## Control Flow
Initialization walks all GPE blocks once via `acpi_ev_walk_gpe_list`, initializes each block, sets `acpi_gbl_all_gpes_initialized`, and polls pre-triggered edge GPEs if needed. `acpi_enable_gpe` validates dispatchability and adds a runtime reference; first reference enables hardware and may trigger a poll. `acpi_disable_gpe` removes a reference and disables only at zero. Direct set bypasses reference counting and toggles `disable_for_dispatch`. Wake setup validates a wake device, optionally converts an unhandled GPE into implicit notify dispatch, removes auto-enable references for PRW wake GPEs, appends a notify target, and marks `ACPI_GPE_CAN_WAKE`. Wake mask updates `enable_for_wake` bits. GPE block install validates a device node, creates a block, creates/attaches a device object if needed, and stores `device.gpe_block`; removal deletes the block and clears the pointer.

## State And Persistence
Runtime state includes GPE flags, runtime reference counts, wake masks, notification lists, per-device GPE block pointers, and global count/list state. All per-GPE changes are in memory plus hardware enable/status registers.

## Dependencies And Integration Points
The file depends on the GPE core, hardware register helpers, namespace validation, FADT/user GPE block management, and PM sleep/wake code that calls PRW-related APIs.

## Risks
Bypassing reference counts with `acpi_set_gpe` can break shared GPE users. Wake setup allocation must happen before the spinlock to avoid sleeping while locked. `acpi_remove_gpe_block` returns directly on a null attached object without releasing the namespace mutex, which is a control-flow hazard in this version. Implicit notify assumes level-triggered behavior for compatibility.

## Test Signals
Coverage should include first/last reference enablement, no-handler rejection, direct set versus reference-counted enable state, wake mark/setup duplicate detection, wake mask bit changes, GPE block install/remove lifecycle, skipped-GPE status scans, and lock release on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfgpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfregn.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfregn.c

## Purpose
`evxfregn.c` exposes address-space operation-region handler registration and `_REG` execution APIs. It connects host region handlers to namespace devices and disconnects regions when handlers are removed.

## Important APIs, Types, And Functions
Exports are `acpi_install_address_space_handler`, `acpi_install_address_space_handler_no_reg`, `acpi_remove_address_space_handler`, and `acpi_execute_reg_methods`. The shared helper `acpi_install_address_space_handler_internal` controls whether `_REG` methods are run. It uses namespace nodes, attached operand objects, address-space handler objects, and region lists.

## Control Flow
Installation validates a device handle under the namespace mutex, calls `acpi_ev_install_space_handler`, and optionally executes `_REG(..., Connect)` methods beneath the node. The `_no_reg` variant deliberately skips `_REG` so callers can delay method execution until hardware initialization is complete. Removal validates the device/root/processor/thermal handle, locates the matching handler object by `space_id` and callback pointer, detaches every region on the handler's region list with `_REG(..., Disconnect)`, unlinks the handler object from the attached object's handler list, and drops its reference. `acpi_execute_reg_methods` validates the node and runs connect `_REG` methods to a caller-provided depth.

## State And Persistence
Handlers are stored in namespace-attached object handler chains. Regions point back to active handlers and are detached during removal. `_REG` execution informs firmware AML of region availability but does not persist data beyond interpreter and firmware side effects.

## Dependencies And Integration Points
The file integrates namespace locking, `acpi_ev_install_space_handler`, `acpi_ev_execute_reg_methods`, `acpi_ev_detach_region`, and region access dispatch used later by field I/O. Default handler setup and host driver region handlers rely on these APIs.

## Risks
Running `_REG` too early can execute AML before hardware/default handlers are ready; the no-reg variant exists to avoid that. Removal requires exact handler pointer matching and can reject otherwise valid space IDs if the callback differs. Detaching regions can invoke AML and must stay under correct namespace synchronization.

## Test Signals
Tests should validate handler install with and without `_REG`, removal of existing and non-existing handlers, mismatched callback rejection, root/device/processor/thermal validation, region detachment list draining, and deferred `_REG` execution depth limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfregn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconcat.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconcat.c

## Purpose
`exconcat.c` implements AML concatenate operations for normal data objects and resource templates, including ACPICA's extension that converts unsupported object types to readable type strings.

## Important APIs, Types, And Functions
The main APIs are `acpi_ex_do_concatenate` and `acpi_ex_concat_template`; `acpi_ex_convert_to_object_type_string` is private. The code manipulates `union acpi_operand_object` instances of integer, string, buffer, and local converted string types, and uses `struct aml_resource_end_tag` for resource templates.

## Control Flow
`acpi_ex_do_concatenate` preprocesses each operand. Integer, string, and buffer are kept as-is; other object types become strings like `[Device Object]`. Operand 0 determines the target type for operand 1: integer converts operand 1 to integer, buffer converts to buffer, and string converts integer/string/buffer to a string using implicit hex rules. The result is a new buffer for integer+integer or buffer+buffer, or a new string for string concatenation. Temporary converted objects are reference-dropped before return. `acpi_ex_concat_template` locates each template's end tag, copies both bodies without duplicate tags, creates one final end tag, and clears checksum to zero.

## State And Persistence
The file creates new operand objects only; it does not mutate namespace state. It carefully removes references for temporary converted operands but returns the newly allocated result to the caller.

## Dependencies And Integration Points
It depends on executor conversion helpers from `exconvrt.c`, resource template parsing helpers from `amlresrc.h`, object allocation utilities, and AML interpreter walk state conventions.

## Risks
String concatenation uses C string routines and assumes ACPICA string objects are null-terminated. Integer concatenation copies raw little-endian integer bytes into buffers, so behavior depends on `acpi_gbl_integer_byte_width`. Resource template correctness depends on finding valid end tags; malformed buffers must be rejected upstream by `acpi_ut_get_resource_end_tag`.

## Test Signals
Tests should cover all operand type combinations, temporary reference cleanup, unsupported object type string conversion, 32-bit versus 64-bit integer width, zero-length resource templates, malformed templates, and single-end-tag output with checksum ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconfig.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconfig.c

## Purpose
`exconfig.c` implements AML dynamic table load and unload support for `LoadTable`, `Load`, and `Unload`-related execution paths. It turns table indices into DDB handles and integrates newly loaded tables into the namespace.

## Important APIs, Types, And Functions
Important functions are `acpi_ex_load_table_op`, `acpi_ex_load_op`, `acpi_ex_unload_table`, and private helpers `acpi_ex_add_table` and `acpi_ex_region_read`. It uses `struct acpi_table_header`, table manager APIs, namespace nodes, DDB local-reference objects, and executor store/region dispatch.

## Control Flow
`acpi_ex_load_table_op` creates an integer return object initialized to zero, finds a table by signature/OEM fields, resolves optional root and parameter paths, loads the table under the chosen parent, creates a table-reference DDB handle, initializes namespace objects, optionally stores caller parameter data, then returns all-ones success. `acpi_ex_load_op` accepts a system-memory operation region or a buffer/resolved field. For regions, it evaluates region arguments, reads the ACPI header bytewise through the region handler, validates length, allocates a copy, and reads the full table through operation-region dispatch. For buffers, it validates header length and copies the table bytes. It then installs and loads the table from the internal buffer, initializes namespace objects, and sets the target integer to all ones. `acpi_ex_unload_table` validates a DDB handle but currently emits warnings and returns not implemented through table unload support behavior.

## State And Persistence
Dynamic loads update ACPICA table manager state and namespace contents. DDB handles are local-reference operand objects flagged `AOPOBJ_DATA_VALID` with the table index in `reference.value`. The loaded table buffer is copied so later AML buffer/region changes do not affect table manager state.

## Dependencies And Integration Points
The code integrates the interpreter lock with table manager locks by exiting/re-entering the interpreter around table operations and namespace initialization. Region-backed loads depend on address-space handlers and field dispatch.

## Risks
Dynamic table load executes namespace initialization and can run AML side effects. Region reads are bytewise and handler-dependent, so malformed or slow handlers affect load behavior. Load failure after table insertion can leave partially initialized table-manager state if downstream cleanup is incomplete. Unload is intentionally unsupported, so AML relying on it will fail.

## Test Signals
Tests should cover table-not-found returning integer zero, successful `LoadTable` with root/parameter paths, bad path failures, region-backed length validation, buffer limit checks, copied-table lifetime, interpreter lock release around table manager calls, and DDB handle validation for unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconvrt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconvrt.c

## Purpose
`exconvrt.c` implements AML object conversion rules among integer, buffer, and string objects, plus target-type conversion used by Store and target operands.

## Important APIs, Types, And Functions
Public executor APIs are `acpi_ex_convert_to_integer`, `acpi_ex_convert_to_buffer`, `acpi_ex_convert_to_string`, and `acpi_ex_convert_to_target_type`. Private `acpi_ex_convert_to_ascii` formats integers or bytes in decimal or hex. The code depends on `acpi_gbl_integer_byte_width`, `acpi_gbl_integer_bit_width`, conversion flags such as `ACPI_IMPLICIT_CONVERSION`, `ACPI_IMPLICIT_CONVERT_HEX`, and explicit decimal/hex conversion modes.

## Control Flow
Integer conversion returns integer operands unchanged, parses strings with explicit or implicit string-to-integer helpers, and converts buffers little-endian up to the current integer width. Buffer conversion returns buffers unchanged, copies integer bytes little-endian, or copies string bytes plus a null terminator. String conversion returns strings unchanged, formats integers as decimal, explicit hex with `0x`, or fixed-width implicit hex, and formats buffers as comma- or space-separated decimal/hex byte strings with `0x` prefixes for hex byte output. Target conversion first classifies the current AML argument kind: explicit/simple targets mostly reject type changes, store targets convert based on destination object type, and reference targets pass through. A failed explicit type mismatch is normalized to success so Store can overwrite the target with the source object.

## State And Persistence
Conversions allocate new operand objects unless the source already has the requested type. New buffers are marked `AOPOBJ_DATA_VALID`. No namespace state is changed directly, but target conversion controls what object later gets stored.

## Dependencies And Integration Points
This file is used by concatenation, logical comparisons, Store, field writes, and other executor opcode paths. It relies on utility numeric parsing/formatting helpers and object allocation/reference conventions.

## Risks
Buffer-to-integer conversion rejects zero-length buffers and truncates to integer width. String conversion length calculations must match emitted separators and prefixes. Some behavior intentionally preserves compatibility quirks, such as including the string null terminator in string-to-buffer conversion.

## Test Signals
Tests should cover implicit versus explicit string parsing, zero-length buffer rejection, little-endian buffer/integer conversion, 32-bit table truncation, decimal and hex string formatting, buffer byte separators, null-terminator inclusion, Store target conversions, and overwrite-on-type-mismatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconvrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/excreate.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/excreate.c

## Purpose
`excreate.c` creates named AML runtime objects: aliases, events, mutexes, operation regions, processors, power resources, and methods.

## Important APIs, Types, And Functions
Executor APIs are `acpi_ex_create_alias`, `acpi_ex_create_event`, `acpi_ex_create_mutex`, `acpi_ex_create_region`, `acpi_ex_create_processor`, `acpi_ex_create_power_resource`, and `acpi_ex_create_method`. It works with `struct acpi_walk_state`, namespace nodes, operand objects, OS semaphores/mutexes, method flags, and region secondary objects.

## Control Flow
Alias creation dereferences an alias target to avoid alias chains, then marks the alias node as method-alias or general alias pointing at the final namespace node. Event creation allocates an event object, creates an unsignaled OS semaphore, attaches it to the namespace node, and removes the local reference. Mutex creation allocates an object, creates an OS mutex, records sync level and node, attaches it, and drops the local reference. Region creation skips if an object is already attached, validates but does not fail on unknown space IDs, records AML operand location and scope in the secondary object, initializes address/length as unevaluated, clears setup/REG/initialized flags, and attaches the region. Processor, power resource, and method creation copy AML operands into typed objects and attach them to namespace nodes.

## State And Persistence
Created objects persist as namespace-attached operand objects. Region address and length are deliberately deferred until runtime and stored as AML pointers. Methods persist AML start/length, parameter count, serialization flag, and sync level. Local references are dropped after attach because namespace ownership remains.

## Dependencies And Integration Points
The file integrates parser/walk-state operands, namespace attach logic, object allocation, OS synchronization primitives, and later executor paths for region argument evaluation, method invocation, event signaling, and mutex acquisition.

## Risks
Deferred region evaluation means invalid region operands may surface much later at field access time. Invalid space IDs are logged but tolerated during table load. Semaphore/mutex creation failure paths rely on reference cleanup to delete partially created OS resources. Alias correctness depends on avoiding chains and preserving method alias type.

## Test Signals
Tests should cover alias-to-alias flattening, event initial semaphore count, mutex sync-level storage, region redefinition no-op, invalid space-id logging without load abort, scope capture for regions, serialized method flag decoding, and reference cleanup after attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/excreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdebug.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdebug.c

## Purpose
`exdebug.c` implements AML `Store(..., Debug)` output support when error/debug messages are enabled.

## Important APIs, Types, And Functions
The sole exported executor function is `acpi_ex_do_debug_object`. It formats `union acpi_operand_object` values, namespace node descriptors, references, buffers, strings, integers, packages, and table references. It is gated by `ACPI_NO_ERROR_MESSAGES`, `acpi_gbl_enable_aml_debug_object`, `acpi_dbg_level`, and optional timer display state.

## Control Flow
The function first returns unless debug-object output is enabled. A one-character newline string emits a bare newline. Otherwise it prints a header with optional microsecond timer and indentation, displays package element indices, handles null and invalid descriptors, and switches by object type. Integers are printed at current ACPICA integer width, buffers dump up to 256 bytes, strings print quoted text, packages recurse into elements, and local references decode index/table/name/object cases. Namespace nodes print type and node pointer without dereferencing as operand objects.

## State And Persistence
The function does not mutate ACPICA state. Its only effects are diagnostic output through `acpi_os_printf` and debug-print macros. Recursion depth and index are call parameters used for formatting nested packages.

## Dependencies And Integration Points
This code is called from Store-to-Debug execution paths and relies on descriptor validation, reference-name helpers, object type names, buffer dump utilities, and OS timer/print services.

## Risks
Debug output can expose firmware data and pointer values, so it is gated. Recursing packages can produce large logs. Invalid object descriptors are handled defensively, but reference decoding still assumes internal reference fields are coherent once descriptor validation passes.

## Test Signals
Tests should cover disabled-output no-op, newline shortcut, integer width formatting, package recursion, null package elements, local/reference/table reference decoding, invalid descriptor handling, and buffer dump truncation at 256 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdump.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdump.c

## Purpose
`exdump.c` provides debug-only object and namespace dump routines for the ACPICA executor and debugger.

## Important APIs, Types, And Functions
Compiled under `ACPI_DEBUG_OUTPUT` or `ACPI_DEBUGGER`, it exposes `acpi_ex_dump_operand`, `acpi_ex_dump_operands`, `acpi_ex_dump_namespace_node`, and `acpi_ex_dump_object_descriptor`. Private helpers include `acpi_ex_dump_object`, `acpi_ex_dump_reference_obj`, `acpi_ex_dump_package_obj`, `acpi_ex_out_string`, and `acpi_ex_out_pointer`. Large `struct acpi_exdump_info` tables describe fields for each object type.

## Control Flow
Dump descriptor tables map object types to offsets and display opcodes. `acpi_ex_dump_object` walks a table and prints scalar fields, pointers, strings, buffers, package contents, handler lists, region lists, nodes, and reference details. `acpi_ex_dump_operand` is the concise operand dump path gated by execution debug level; it validates descriptor type and switches over common ACPI object types. `acpi_ex_dump_operands` iterates opcode operands. `acpi_ex_dump_object_descriptor` can force display, dumps namespace nodes first when given a node, validates object type, dumps common fields, then object-specific fields and region secondary objects.

## State And Persistence
No runtime state is changed. The routines read live object graphs and print diagnostic information. They include circular-list detection for object, handler, and region chains to avoid infinite dumps.

## Dependencies And Integration Points
The file depends on ACPICA descriptor layout, namespace names, debug level checks, debugger builds, and dump/print helpers. It is an observability tool for executor objects created by files such as `excreate.c`, `evxface.c`, and `evxfregn.c`.

## Risks
Because it reads internal structures by offsets, descriptor layout changes require table updates. Debug output may reveal pointers and firmware contents. Recursive package dumps and large buffers can create substantial logs, although some paths cap buffer display. Debug-only compilation means production issues may not exercise this code.

## Test Signals
Tests should compile debug and non-debug configurations, dump each supported object type, validate circular-list detection, verify namespace node plus attached object output, exercise package recursion and reference path conversion, and confirm debug-level gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfield.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfield.c

## Purpose
`exfield.c` is the high-level read/write layer for AML named fields. It chooses return object types, handles special address spaces, and delegates bit-level field extraction/insertion to `exfldio.c`.

## Important APIs, Types, And Functions
APIs are `acpi_ex_get_protocol_buffer_length`, `acpi_ex_read_data_from_field`, and `acpi_ex_write_data_to_field`. It defines serial bus protocol length mapping and PCC command-offset macros. Important field types include buffer fields, region fields, GPIO, SMBus/GSBus/IPMI/platform runtime/fixed hardware serial regions, Platform Communication Channel regions, and normal operation regions.

## Control Flow
Protocol lookup validates AccessAs protocol IDs and returns fixed, variable, or invalid lengths. Field reads first evaluate lazy buffer-field arguments, route serial bus regions to serial bus helpers, allocate either a buffer or integer depending on field bit length and CreateField semantics, route GPIO reads to GPIO helpers, read PCC fields from the internal PCC buffer, or acquire the global lock and call `acpi_ex_extract_from_field`. Field writes similarly evaluate lazy buffer fields, route GPIO and serial bus writes to helpers, handle PCC by copying to the internal PCC buffer and invoking the region handler only when the command field is written, or convert integer/buffer/string source data into a byte pointer and call `acpi_ex_insert_into_field` under the global lock.

## State And Persistence
Normal fields update backing buffers or operation regions. PCC writes update `internal_pcc_buffer` and may trigger a handler. Lazy buffer field evaluation sets object data-valid state. Global lock acquisition is transient around locked field transactions.

## Dependencies And Integration Points
This layer depends on dispatcher argument evaluation, serial bus/GPIO helpers, PCC region state, global lock helpers, and the lower-level field I/O functions in `exfldio.c`.

## Risks
Special address-space routing means incorrect space IDs can bypass normal locking or validation. PCC command detection uses offsets rather than names for robustness, so region layout must match spec. Field return type compatibility preserves CreateField-as-buffer behavior even for small fields.

## Test Signals
Tests should cover protocol ID validation, integer-versus-buffer read result selection, CreateField buffer preservation, lazy buffer-field evaluation, GPIO/serial/PCC routing, command-field PCC handler invocation, global lock use for locked fields, and source type rejection on writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfldio.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfldio.c

## Purpose
`exfldio.c` performs low-level AML field I/O: region validation, datum reads/writes, bank and index register sequencing, update-rule merging, and bit extraction/insertion across access-width boundaries.

## Important APIs, Types, And Functions
Public executor functions are `acpi_ex_access_region`, `acpi_ex_write_with_update_rule`, `acpi_ex_extract_from_field`, and `acpi_ex_insert_into_field`. Private helpers are `acpi_ex_setup_region`, `acpi_ex_register_overflow`, and `acpi_ex_field_datum_io`. It operates on common field metadata such as access byte width, bit length, base byte offset, start bit offset, update rules, bank objects, index/data objects, and region objects.

## Control Flow
Region setup validates that the backing object is a region, validates address-space ID, lazily evaluates region address/length, skips direct bounds validation for nonlinear SMBus/GSBus/IPMI spaces, and checks that each access datum fits within the region, with optional interpreter slack rounding. `acpi_ex_access_region` computes region byte offset and dispatches to the address-space handler. Datum I/O switches among buffer fields, bank fields, region fields, and index fields. Bank fields write the bank selector first then fall through to region access. Index fields write the computed index register then read or write the data register. Update-rule writes preserve, write-as-ones, or write-as-zeros outside the field mask. Extraction reads one or more access-width datums, shifts/merges around start bit offset, masks tail bits, and copies to the caller buffer. Insertion pads too-short inputs, builds masks, merges source bytes into datums, applies update rules, and writes each datum.

## State And Persistence
The file updates operation regions, backing buffers, bank selector fields, index registers, and data registers. It may set lazy region/buffer-field data-valid state through dispatcher helpers. It also mutates `access_byte_width` down to `sizeof(u64)` when wider access widths are encountered.

## Dependencies And Integration Points
It depends on address-space dispatch from the event subsystem, dispatcher region/buffer argument evaluation, global interpreter slack behavior, AML field flags, and high-level read/write entry points in `exfield.c`.

## Risks
Bitfield algorithms are sensitive to shifts at or beyond integer width, access-width truncation, and partial buffer padding. Region limit checks must remain exact because field accesses can target hardware. Bank/index fields can have side effects before the final data access. Slack mode intentionally tolerates firmware that exceeds strict bounds.

## Test Signals
Tests should cover aligned simple fields, unaligned multi-datum extraction/insertion, tail masking, preserve/write-as-ones/write-as-zeros rules, too-short write padding, region limit errors, slack acceptance, bank/index register overflow, nonlinear-space bypass, and address-space handler error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfldio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmisc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmisc.c

## Purpose
`exmisc.c` contains executor helper operations for object references, integer math, numeric logical operations, and generic logical comparisons.

## Important APIs, Types, And Functions
Functions are `acpi_ex_get_object_reference`, `acpi_ex_do_math_op`, `acpi_ex_do_logical_numeric_op`, and `acpi_ex_do_logical_op`. It uses AML opcode constants, local reference classes, operand objects, namespace node descriptors, and conversion helpers from `exconvrt.c`.

## Control Flow
Reference creation accepts either a local/arg/debug reference operand or an already resolved namespace node. It creates a new `LOCAL_REFERENCE` object of class `REFOF` pointing to the referenced pseudo-node or namespace node. Math operations switch on AML integer opcodes and return raw 64-bit results; shifts explicitly return zero when the shift count is at least the active integer bit width to avoid undefined C behavior. Numeric logical ops implement LAnd/LOr on integer values. General logical comparisons convert operand 1 to operand 0's type, then compare integers numerically or strings/buffers lexicographically by bytes and length. Temporary converted operands are reference-dropped.

## State And Persistence
The file only allocates reference objects and temporary conversion objects. It does not mutate namespace or hardware state. Results are returned through output parameters or function return values.

## Dependencies And Integration Points
These helpers are used by AML opcode execution paths for `RefOf`, `CondRefOf`, arithmetic, logical comparisons, and conversion-sensitive comparisons. They integrate with object conversion rules and ACPICA reference counting.

## Risks
Arithmetic intentionally does not detect overflow, matching AML integer semantics. Logical comparison behavior depends on operand 0 type, so asymmetric conversions are expected. Reference creation rejects unsupported reference classes; callers must resolve operands correctly before reaching this layer.

## Test Signals
Tests should cover reference creation for locals, args, debug objects, and namespace nodes; invalid descriptor/class rejection; all math opcode results; oversize shift counts; numeric LAnd/LOr invalid opcodes; integer/string/buffer comparisons; lexicographic length tie-breakers; and temporary object cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmutex.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmutex.c

## Purpose
`exmutex.c` implements AML mutex acquire/release behavior, including SyncLevel ordering, recursive acquisition by the same thread, global lock special handling, and forced release at interpreter thread exit.

## Important APIs, Types, And Functions
Public/internal functions are `acpi_ex_acquire_mutex_object`, `acpi_ex_acquire_mutex`, `acpi_ex_release_mutex_object`, `acpi_ex_release_mutex`, `acpi_ex_unlink_mutex`, and `acpi_ex_release_all_mutexes`; `acpi_ex_link_mutex` is private. Important state lives in `union acpi_operand_object` mutex fields and `struct acpi_thread_state` acquired-mutex list/current sync level.

## Control Flow
Low-level acquire supports recursive acquisition by the owning thread by incrementing acquisition depth. Otherwise it waits on either the ACPI global lock or OS mutex, then records thread ID and depth. AML acquire first validates thread state and SyncLevel ordering, delegates to low-level acquire, then on first acquisition stores owner thread, original sync level, updates current sync level, and links the mutex into the thread's acquired list. Low-level release decrements depth, unlinks when depth reaches zero, releases global lock or OS mutex, and clears thread ID. AML release validates ownership, thread ID, and SyncLevel equality, restores the prior sync level from the list head's saved value after final release, and handles same-level non-LIFO releases. Forced release walks the acquired list at thread exit and releases every held mutex while clearing ownership fields.

## State And Persistence
Mutex ownership, acquisition depth, owner thread, current/original SyncLevel, and acquired-list links are mutable runtime state. Global lock acquire/release also affects firmware global lock state through event helpers.

## Dependencies And Integration Points
The file integrates OS mutex waits/releases, ACPI global lock event helpers, interpreter lock expectations, and external global lock APIs in `evxface.c`.

## Risks
SyncLevel rules are the main deadlock prevention mechanism; bypassing them or corrupting list links can leave methods deadlocked. Forced release intentionally releases all held mutexes at thread exit, which may mask method bugs but prevents permanent lock leaks. Global lock has special ownership semantics allowing release by other threads in one path.

## Test Signals
Tests should cover recursive acquire/release depth, timeout failures, SyncLevel ordering rejection, non-owner release rejection, same-level non-LIFO release restoration, forced release cleanup, global lock special case, and acquired-list link/unlink integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exnames.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exnames.c

## Purpose
`exnames.c` parses AML name strings from the byte stream into allocated ACPICA namestring buffers, including root prefixes, parent prefixes, dual-name and multi-name prefixes, null names, and field-name restrictions.

## Important APIs, Types, And Functions
The exported parser helper is `acpi_ex_get_name_string`. Private helpers are `acpi_ex_allocate_name_string` and `acpi_ex_name_segment`. It uses AML prefix opcodes, `ACPI_NAMESEG_SIZE`, `ACPI_UINT32_MAX` as the internal root-prefix sentinel, and `acpi_ut_valid_name_char`.

## Control Flow
Allocation computes enough space for root/parent prefixes, optional dual or multi prefix bytes, name segments, and the null terminator, then writes the prefix encoding into the output buffer. Segment parsing rejects a leading digit, consumes exactly four valid name characters, appends them to the output string, returns `AE_CTRL_PENDING` when the first byte is not a name, and returns `AE_AML_BAD_NAME` for partial segments. Full namestring parsing disallows prefixes for field-unit names and parses exactly one segment. Other names first consume root or repeated parent prefixes, then handle dual-name, multi-name, null-name, or single segment forms. If a prefix was consumed but no valid segment followed, pending status is upgraded to malformed-name failure. On success the function returns the allocated namestring and byte length consumed.

## State And Persistence
The parser allocates a namestring owned by the caller. It does not update namespace state; it only advances an AML pointer locally and reports the consumed length. On failure it frees any allocated buffer.

## Dependencies And Integration Points
This helper is used by AML scanner/interpreter code while loading or executing names. Namespace lookup happens later; this file only validates and formats raw AML namepath syntax.

## Risks
The allocated buffer is intentionally somewhat larger than necessary, so callers must rely on returned length/string rather than exact allocation size. Malformed AML can produce pending status, bad-name errors, or leading-digit diagnostics. Field-unit prefix rejection is important because field declarations use restricted names.

## Test Signals
Tests should cover root name, repeated parent prefixes, dual and multi names, null names, single segment names, field-unit names with and without illegal prefixes, leading-digit rejection, partial segment bad-name reporting, consumed length accuracy, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/exnames.c -->
