# subset-b-001011 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_video.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpi_video.c

### Purpose
`acpi_video.c` implements the Linux ACPI video bus driver. It discovers ACPI video output devices under a graphics controller, interprets video-related AML methods such as `_DOD`, `_DOS`, `_BCL`, `_BCM`, `_BQC`/`_BCQ`, and `_DDC`, exposes firmware backlight devices, emits input key events for video and brightness hotkeys, registers thermal cooling devices for LCD backlight control, and provides exported helper APIs used by GPU/vendor drivers.

### Important APIs, Types, And Functions
Core state is split between `struct acpi_video_bus` and `struct acpi_video_device`. The bus tracks the ACPI companion, `_DOD` attachment array, capabilities, child devices, input device, PM notifier, and global list entry. Each video output tracks device ID, inferred type flags, AML capabilities, delayed brightness work, brightness table, backlight and cooling devices. Exported APIs are `acpi_video_register()`, `acpi_video_unregister()`, `acpi_video_register_backlight()`, `acpi_video_get_levels()`, `acpi_video_get_edid()`, and `acpi_video_handles_brightness_key_presses()`. Key internal functions include `acpi_video_bus_probe()`, `acpi_video_device_enumerate()`, `acpi_video_bus_get_one_device()`, `acpi_video_init_brightness()`, `acpi_video_bqc_quirk()`, `acpi_video_bus_notify()`, and `acpi_video_device_notify()`.

### Control Flow
Module initialization defers registration if ACPI is disabled or an Intel OpRegion is present; otherwise `acpi_video_register()` applies DMI quirks and registers an auxiliary driver named `acpi.video_bus`. Probe rejects duplicate video buses unless allowed, finds bus capabilities, verifies the ACPI object maps to a PCI VGA controller, enumerates `_DOD`, walks child ACPI devices, binds children by `_ADR`, identifies display type, and installs notify handlers. Backlight registration is either deferred to GPU drivers through `acpi_video_register_backlight()` or done immediately when backlight auto-detection is not in play. Brightness setup reads `_BCL`, normalizes missing AC/battery entries, sorts reversed packages, validates `_BQC`, and initializes firmware brightness through `_BCM`. Notify paths translate ACPI events to Linux input events and schedule delayed brightness changes when firmware is expected not to handle them.

### State, Persistence, And Dependencies
Persistent kernel state is in global module parameters, `register_count`, `may_report_brightness_keys`, `video_bus_head`, per-bus lists, per-device brightness tables, and registered kernel class devices. Firmware state is changed through `_DOS` and `_BCM`; suspend/resume restores cached brightness values through a PM notifier. The driver depends on ACPI core evaluation/notification APIs, auxiliary bus registration, PCI device lookup, DMI quirks, input, backlight, thermal cooling, delayed work, sysfs links, and ACPI video definitions in `<acpi/video.h>`.

### Integration Points
GPU drivers call `acpi_video_register()` and later `acpi_video_register_backlight()` once panel detection clarifies whether ACPI video should own the backlight. Vendor hotkey drivers can consult `acpi_video_handles_brightness_key_presses()` to avoid duplicate reporting. EDID consumers can call `acpi_video_get_edid()`. The backlight class exposes `acpi_videoN`, thermal exposes `LCD`, userspace receives input events, and `acpi_notifier_call_chain()` lets other ACPI clients veto or observe events.

### Risks
Firmware variance is the dominant risk: malformed `_BCL`, indexed or broken `_BQC`, devices missing from `_DOD`, duplicate video buses, incorrect device ID scheme bits, and systems that change brightness in hardware all require quirks. Backlight ownership must not conflict with native GPU backlights. Notify removal must cancel delayed work before freeing devices. `video_get_cur_state()` and brightness index conversion depend on normalized brightness tables. `_DDC` handling accepts a one-element package workaround but still trusts firmware-reported buffer length after copying.

### Test Signals
Useful signals include booting ACPI-video and native-backlight systems, DMI quirk coverage, `_BCL` packages with missing special levels, reversed and unordered brightness levels, `_BQC` value versus index behavior, hotkey event reporting/veto behavior, suspend/resume brightness restore, duplicate video-bus detection, EDID reads at multiple lengths, and module load/unload with lockdep/workqueue checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_watchdog.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpi_watchdog.c

### Purpose
`acpi_watchdog.c` parses the ACPI WDAT table and creates a Linux platform device for the generic ACPI watchdog driver when firmware advertises a usable ACPI watchdog. It also lets native watchdog drivers ask whether the ACPI watchdog should be preferred.

### Important APIs, Types, And Functions
The exported `acpi_has_watchdog()` returns whether a usable WDAT table exists. `acpi_watchdog_init()` is the init-time device creation path. `acpi_watchdog_get_wdat()` centralizes ACPI-disabled, boot-parameter, table lookup, and RTC-SRAM exclusion checks. When `CONFIG_RTC_MC146818_LIB` is enabled, `acpi_watchdog_uses_rtc()` scans WDAT entries and detects register GAS entries targeting RTC I/O ports. `disable_acpi_watchdog()` handles the `acpi_no_watchdog` boot option.

### Control Flow
The init path obtains WDAT, exits quietly if absent, rejects BIOS-disabled tables, and skips legacy PCI watchdog descriptors by requiring all PCI location fields to be `0xff`. It walks each WDAT register entry, converts supported system-memory and system-I/O GAS regions into `struct resource` ranges, merges overlapping resources with `resource_union()`, copies the list into an array, and registers a `wdat_wdt` platform device. All paths release the resource list and ACPI table reference.

### State, Persistence, And Dependencies
State is minimal: `acpi_no_watchdog` persists the boot-parameter decision. WDAT table references are temporary and must be released with `acpi_put_table()`. The persistent artifact is a platform device with memory/I/O resources consumed by `wdat_wdt`. Dependencies include ACPI table APIs, resource-list helpers, platform device registration, IORESOURCE flags, and optional RTC port definitions.

### Integration Points
Native watchdog drivers can use `acpi_has_watchdog()` to avoid binding hardware that firmware wants exposed through WDAT. The created `wdat_wdt` device is the handoff to the watchdog subsystem. The `acpi_no_watchdog` kernel command-line parameter provides an administrative override.

### Risks
`acpi_has_watchdog()` obtains a WDAT pointer through `acpi_watchdog_get_wdat()` but does not release it, so behavior depends on ACPICA table reference semantics and is worth auditing. Firmware tables with unsupported address spaces abort device creation. RTC-SRAM detection is compiled out without `CONFIG_RTC_MC146818_LIB`, allowing WDAT on systems that might conflict with the RTC driver. Resource merging must preserve correct ranges across mixed I/O and memory entries.

### Test Signals
Test with no WDAT, disabled WDAT, RTC-backed WDAT, legacy PCI WDAT, valid memory and I/O regions, overlapping resources, unsupported address spaces, platform-device registration failure, and the `acpi_no_watchdog` boot option. Refcount/leak checking around repeated `acpi_has_watchdog()` calls is a useful targeted signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/Makefile -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/Makefile

### Purpose
This Makefile defines how the Linux kernel builds ACPICA core interpreter sources into the ACPI object namespace. It groups dispatcher, event, executor, hardware, namespace, parser, resource, table, utility, debugger, and future-use objects into `acpi.o`.

### Important APIs, Types, And Functions
There are no C APIs here, but the build contract is important: `ccflags-y` defines `_LINUX` and `BUILDING_ACPICA`, `CONFIG_ACPI_DEBUG` adds `ACPI_DEBUG_OUTPUT`, `CFLAGS_tbfind.o` suppresses a string truncation warning, `obj-y += acpi.o` places all objects under the ACPI module parameter namespace, and `acpi-y` lists the object files linked into the composite.

### Control Flow
Kbuild expands unconditional `acpi-y` blocks and conditional additions. Core dispatcher (`ds*`), event (`ev*`), executor (`ex*`), hardware (`hw*`), namespace (`ns*`), parser (`ps*`), resource (`rs*`), table (`tb*`), and utility (`ut*`) objects are always included. `hwpci.o` depends on `CONFIG_PCI`, debugger objects depend on `CONFIG_ACPI_DEBUGGER`, and some unused/upstream ACPICA utilities depend on `ACPI_FUTURE_USAGE`.

### State, Persistence, And Dependencies
The persistent result is build composition, not runtime state. The file depends on Linux Kbuild variables and config symbols. Its object ordering matters because it defines which ACPICA implementation files are available to satisfy declarations in the headers researched in this group.

### Integration Points
This is the build bridge between upstream ACPICA source layout and Linux's ACPI core. It controls whether debugger interfaces, PCI config helpers, and future utility/debug allocation features are linked into the kernel build.

### Risks
Missing an object can surface as link failures or as disabled runtime functionality behind a config path. Adding ACPICA headers without matching objects can compile but fail later. Warning suppression should stay local. Conditional `ACPI_FUTURE_USAGE` objects must not be assumed present by normal code.

### Test Signals
Build matrix signals include ACPI core builds with and without `CONFIG_PCI`, `CONFIG_ACPI_DEBUG`, and `CONFIG_ACPI_DEBUGGER`; clean `W=1` builds; link coverage for newly referenced ACPICA functions; and boot smoke tests for table loading, namespace initialization, GPE handling, and AML execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acapps.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acapps.h

### Purpose
`acapps.h` is a shared ACPICA application/tool header. It declares sign-on strings, usage-printing macros, table/file helper prototypes, getopt state, disassembler namespace helpers, and filename/table-output helpers used by ACPICA utilities rather than normal kernel runtime paths.

### Important APIs, Types, And Functions
Macros include `ACPICA_NAME`, `ACPICA_COPYRIGHT`, `ACPI_WIDTH`, `ACPI_COMMON_SIGNON`, `ACPI_COMMON_HEADER`, `ACPI_COMMON_BUILD_TIME`, `ACPI_USAGE_HEADER`, `ACPI_USAGE_TEXT`, `ACPI_OPTION`, `ACPI_CHECK_STATUS`, and `ACPI_CHECK_OK`. File/table interfaces include `ac_get_all_tables_from_file()`, `ac_delete_table_list()`, `ac_is_file_binary()`, and `ac_validate_table_header()`. Tool parsing uses `acpi_getopt()`, `acpi_getopt_argument()`, and global option variables. Disassembler helpers include `acpi_dm_cross_reference_namespace()`, `acpi_dm_finish_namespace_load()`, and parse-object conversion/dump functions.

### Control Flow
This header does not implement control flow, but it standardizes tool startup, option parsing, ACPI table-file loading, disassembler namespace post-processing, and output filename generation. Callers include the declared helper implementations based on application build mode.

### State, Persistence, And Dependencies
State is external: option globals, file handles, table descriptor lists, parse trees, and namespace roots are owned by applications. The header depends on standard headers under `ACPI_USE_STANDARD_HEADERS`, ACPICA public types, parse objects, namespace nodes, `FILE`, and `ACPI_FILE`.

### Integration Points
It integrates ACPICA command-line utilities with shared ACPICA table parsing and disassembly code. In the Linux tree it remains part of the vendored ACPICA surface even if many functions are not linked into normal kernel builds.

### Risks
Macros print directly and assume `printf()`/`acpi_os_printf()` availability in application contexts. Version/copyright strings must track ACPICA releases. Option parser globals are process-global and not thread-safe. Tool-only declarations can be mistaken for kernel-runtime APIs.

### Test Signals
Signals are ACPICA utility builds, usage output snapshots, getopt edge cases, binary versus text table detection, invalid table-header handling, disassembler namespace cross-reference tests, and file name/path split cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acapps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/accommon.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/accommon.h

### Purpose
`accommon.h` is the umbrella include for ACPICA source files. It centralizes the ordered include set needed by most ACPICA implementation units.

### Important APIs, Types, And Functions
It does not declare functions itself. Its important contract is include ordering: `<acpi/acconfig.h>`, `acmacros.h`, `aclocal.h`, `acobject.h`, `acstruct.h`, `acglobal.h`, `achware.h`, `acutils.h`, and optionally `acclib.h` when `ACPI_USE_SYSTEM_CLIBRARY` is not set.

### Control Flow
There is no runtime control flow. The compile-time flow is that ACPICA `.c` files include this header to receive configuration constants, macros, internal types, operand-object layouts, shared structures, global declarations, hardware prototypes, utility prototypes, and library shims in a consistent sequence.

### State, Persistence, And Dependencies
This header exposes shared declarations but owns no state. It depends on all included headers being self-consistent and order-sensitive, especially because macros and typedefs in earlier headers are used by later ones.

### Integration Points
It is the main integration surface for the ACPICA core objects listed in the Makefile. Changes here affect nearly every ACPICA implementation file.

### Risks
Include-order regressions can break large portions of ACPICA. Adding heavy or platform-specific includes here expands compile impact. The conditional C-library include must match kernel versus application build configuration.

### Test Signals
Full ACPI builds are the primary signal. Header self-sufficiency checks, minimal translation-unit builds, and config matrix builds around `ACPI_USE_SYSTEM_CLIBRARY` help catch dependency regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/accommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acconvert.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acconvert.h

### Purpose
`acconvert.h` declares ASL/ASL+ comment conversion support for the ACPICA compiler/disassembler path. It classifies comment states and comment emission forms and exposes converter routines only under `ACPI_ASL_COMPILER`.

### Important APIs, Types, And Functions
Comment-state constants include `ASL_COMMENT_STANDARD`, `ASLCOMMENT_INLINE`, open/close paren, and close brace states. AML print constants include standard, inline, end-node, name, close-brace, end-block, and include comments. Declared functions cover comment capture (`cv_process_comment*`, `cv_capture_comments*`), comment placement/listing (`cv_add_to_comment_list()`, `cv_place_comment()`), parse-object annotation (`cv_transfer_comments()`, `cv_clear_op_comments()`), file tree handling (`cv_init_file_tree()`, `cv_switch_files()`), and AML comment output (`cg_write_aml_comment()`).

### Control Flow
The intended flow is compiler/disassembler-only: lexical comment capture records comments into lists or parse-object fields; parser/disassembler phases transfer comments to relevant parse nodes; code-generation/disassembly output functions emit comments in the proper location.

### State, Persistence, And Dependencies
State is held in parse objects, `struct asl_comment_state`, comment lists, file nodes, and globals declared elsewhere. The header depends on parse state, walk state, parse object, table header, file, and comment-node types.

### Integration Points
`acmacros.h` uses conditional converter macros that compile to real converter calls only when `ACPI_ASL_COMPILER` is enabled. This keeps normal kernel ACPICA builds free of comment-conversion behavior.

### Risks
These declarations are inactive outside compiler builds, so normal kernel builds will not catch implementation drift. Comment placement is sensitive to parse-tree ownership and include-file switching. Mismanaged comment lists can leak memory in tools.

### Test Signals
iASL compiler/disassembler round trips with inline, block, include, close-brace, and end-block comments are the strongest signals. Builds with and without `ACPI_ASL_COMPILER` verify conditional compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acconvert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdebug.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdebug.h

### Purpose
`acdebug.h` declares the ACPICA AML debugger command, conversion, namespace, method-execution, display, file I/O, history, statistics, and utility interfaces.

### Important APIs, Types, And Functions
It defines debugger buffer sizing, command/help/argument metadata structs, execution walk state, and stepping flags. Declarations span `dbxface` single-step and breakpoint hooks, command handlers such as table display/unload, notify injection, lock/resource/GPE/handler display, object conversion helpers, method breakpoints and data mutation, namespace dumping/searching, method execution threads, debug file/table loading, history retrieval, internal/external object dumps, statistics generation, output redirection, namespace lookup, and interrupt generation.

### Control Flow
The debugger command loop tokenizes input, dispatches commands through `acpi_db_command_dispatch()`, optionally executes AML methods, displays objects or namespace state, and can create background execution threads. Some hooks are wrapped with `ACPI_DBR_DEPENDENT_RETURN_*` or hardware-dependent macros so non-debugger or reduced-hardware builds can compile stubs.

### State, Persistence, And Dependencies
State lives in debugger globals declared in `acglobal.h`, walk states, parse objects, namespace nodes, loaded tables, output files, and history buffers. This header depends on disassembler declarations when `ACPI_DISASSEMBLER` is enabled and on ACPICA object, walk, memory, PLD, and namespace types.

### Integration Points
Debugger objects are linked only when `CONFIG_ACPI_DEBUGGER` enables the Makefile entries. The header connects debugger commands to ACPICA interpreter, namespace, event/GPE, disassembler, and table subsystems.

### Risks
Debugger-only code is broad and privileged: command parsing can mutate AML method data, inject events, load/unload tables, or spawn execution threads. Conditional stubs must match signatures. Display code must avoid dereferencing invalid namespace or operand descriptors during failure debugging.

### Test Signals
Signals include debugger-enabled builds, command parsing tests, single-step method execution, namespace dumps, object conversion from command arguments, table load/unload flows, GPE/SCI generation on hardware-enabled configs, and output redirection/history behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdispat.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdispat.h

### Purpose
`acdispat.h` declares the ACPICA dispatcher layer, which connects parsed AML operations to namespace loading and interpreter execution.

### Important APIs, Types, And Functions
The header covers dynamic argument evaluation for buffers, packages, regions, bank fields, and buffer fields; control-op begin/end handling; operand evaluation for late-bound objects; method execution callbacks; AML field creation; namespace load pass callbacks; method locals/args management; control method call/restart/termination; object initialization; package initialization; operand/result-stack utilities; scope stack manipulation; walk-state lifecycle; and method-stack debug dumps.

### Control Flow
ACPICA table load uses dispatcher callbacks for pass 1 and pass 2 namespace construction. Runtime method execution creates a walk state, parses AML, pushes/pops scope and operand/result stacks, resolves operands, dispatches opcodes to executor routines, handles control flow predicates, calls nested methods, and terminates control methods while releasing method state.

### State, Persistence, And Dependencies
Dispatcher state is held in `struct acpi_walk_state`, thread state, parse objects, namespace nodes, operand objects, result stacks, local/arg entries, and method descriptors. The header depends heavily on `aclocal.h`, `acobject.h`, parser structures, and namespace nodes.

### Integration Points
It is the central contract between parser (`ps*`), namespace (`ns*`), and executor (`ex*`) objects listed in the Makefile. Table loading, method invocation, field creation, and dynamic object initialization all pass through these declarations.

### Risks
Walk-state and stack ownership are subtle. Incorrect result usage decisions can leak or prematurely delete operand objects. Method serialization, restart, and termination must keep mutex and thread state balanced. Namespace load pass behavior must match AML rules or devices/methods may be missing or duplicated.

### Test Signals
AML tests should cover table load passes, nested scopes, control flow, implicit returns, field/bank/index/buffer field creation, package initialization, nested method calls, method errors, operand stack underflow/overflow, and namespace mutations during method execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdispat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acevents.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acevents.h

### Purpose
`acevents.h` declares ACPICA event support: fixed events, SCI dispatch, GPE discovery/enable/dispatch, global lock handling, notify queuing, address-space handler installation, operation-region initialization, and region setup callbacks.

### Important APIs, Types, And Functions
The header defines `ACPI_GPE_IS_POLLING_NEEDED()` when GPE polling is enabled. Declarations include `acpi_ev_initialize_events()`, `acpi_ev_install_xrupt_handlers()`, `acpi_ev_fixed_event_detect()`, notify helpers, global lock acquire/release, low-level GPE detect/enable/mask/reference/finish operations, GPE block creation/deletion/initialization/dispatch, GPE list utilities, region handler lookup/install, address-space dispatch, region attach/detach, `_REG` execution, default region setups, SCI handler installation/removal, and subsystem termination.

### Control Flow
Initialization installs SCI/GPE interrupt handlers and region handlers. On SCI, fixed events and GPEs are detected; GPE dispatch invokes a method, handler, or implicit notify path. Region access uses installed address-space handlers and setup callbacks. GPE reference counts control runtime enablement, and optional polling checks edge-triggered GPEs after enable.

### State, Persistence, And Dependencies
Event state is in GPE blocks, register arrays, interrupt blocks, handler objects, notify queues, global lock globals, fixed-event handler arrays, and region context stored in operand objects. Dependencies include namespace nodes, GPE structs from `aclocal.h`, hardware access prototypes, OS interrupt services, and operand objects.

### Integration Points
ACPICA event declarations integrate AML `Notify`, `_Lxx`/`_Exx` GPE methods, operation regions, fixed power/sleep/timer events, and Linux ACPI interrupt handling. Hardware-dependent macros isolate reduced-hardware builds.

### Risks
GPE enable/mask/reference counts are concurrency-sensitive and protected by ACPI locks. Edge-triggered GPE polling is conditional and can miss events if configured incorrectly. Region handler attachment must avoid use-after-free across namespace/table unload. Global lock handling must preserve firmware handshake semantics.

### Test Signals
Signals include fixed-event detection, SCI storms, GPE method and handler dispatch, wake versus runtime GPE masks, GPE block hot-add/remove, `_REG` execution, region setup failures, reduced-hardware builds, and lockdep/interrupt-context checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acevents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acglobal.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acglobal.h

### Purpose
`acglobal.h` declares ACPICA global variables shared across table management, namespace, interpreter, hardware, event, debugger, disassembler, compiler, and application builds.

### Important APIs, Types, And Functions
This header is data declarations rather than functions. It declares root table and DSDT/FACS/FADT indexes, FADT-derived PM/GPE addresses, integer width globals, mutex/spinlock objects, global lock state, caches, startup/shutdown flags, global notify/exception/table/interface/SCI/GED handlers, owner ID masks, namespace root and predefined names, parser/interpreter globals, hardware sleep state values, GPE/fixed-event globals, debug counters, dynamic tracing levels, debugger buffers/state, disassembler options, ASL converter globals, and application output/print buffers.

### Control Flow
Runtime control flow is implicit: initialization code fills tables, locks, caches, namespace roots, and event globals; interpreter and event code then consume and mutate them; termination paths release them. `ACPI_GLOBAL` and `ACPI_INIT_GLOBAL` determine whether the header declares or defines storage depending on the including compilation unit configuration.

### State, Persistence, And Dependencies
This is the central ACPICA state map. State persists for the life of the ACPI subsystem or for tool process lifetime. Dependencies include table, namespace, operand, mutex, GPE, handler, and debugger types.

### Integration Points
Nearly every ACPICA object built by the Makefile includes this header indirectly through `accommon.h`. It is the shared state bridge among table loader, namespace loader, interpreter, events, hardware access, debugger, and applications.

### Risks
Global state makes initialization order, locking, and teardown order critical. `ACPI_GLOBAL` misuse can create duplicate definitions or missing storage. Debugger/disassembler/compiler sections must remain gated by config macros. Any lock or handler global has concurrency and lifetime risk, especially during dynamic table unload and suspend/resume.

### Test Signals
Full ACPI boot, table load/unload, namespace initialization, method execution, GPE dispatch, sleep/wake, debugger-enabled builds, disassembler/compiler builds, and subsystem shutdown/leak tests exercise these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acglobal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/achware.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/achware.h

### Purpose
`achware.h` declares ACPICA hardware-facing interfaces for ACPI mode switching, register access, sleep/wake flows, port validation, GPE register manipulation, and PCI ID derivation.

### Important APIs, Types, And Functions
It defines `_SST` indicator values and declares `acpi_hw_set_mode()`, `acpi_hw_get_mode()`, generic register validation/read/write, bit-register lookup/read/write, PM1 control writes, status clearing, legacy and extended sleep/wake entry points, sleep-method execution, validated port I/O, GPE register read/write/bit/set/clear/status helpers, runtime GPE enable helpers, and `acpi_hw_derive_pci_id()` under `ACPI_PCI_CONFIGURED`.

### Control Flow
Higher ACPICA layers call these routines when enabling ACPI mode, clearing/reading/writing PM registers, entering or leaving sleep states, manipulating GPE enable/status registers, and accessing PCI config operation regions. The inline fallback for `acpi_hw_derive_pci_id()` returns `AE_SUPPORT` when PCI support is not configured.

### State, Persistence, And Dependencies
The header owns no state but operates on global ACPI hardware state declared elsewhere and on `struct acpi_generic_address`, GPE event/register info, and PCI IDs. Dependencies include OS port/MMIO access and ACPI FADT-derived addresses.

### Integration Points
It bridges event, sleep, region, and interpreter code to platform hardware. `accommon.h` includes it for broad ACPICA availability.

### Risks
Hardware register access has platform safety risk: wrong widths, invalid GAS addresses, preserved/write-only bits, or reduced-hardware configurations can break firmware interaction. Sleep/wake sequencing is particularly sensitive to FADT generation and platform quirks.

### Test Signals
Signals include ACPI mode transition, PM register read/write validation, fixed event clearing, GPE enable/disable/status operations, S-state suspend/resume on legacy and extended sleep platforms, invalid I/O block rejection, reduced-hardware builds, and PCI-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/achware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acinterp.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acinterp.h

### Purpose
`acinterp.h` declares the ACPICA AML interpreter/executor interfaces. It covers operand conversion, debug tracing, field I/O, object creation, dynamic table loading, mutex/event/system operations, opcode execution by operand count, operand resolution, object storage/copying, interpreter locking, default operation-region handlers, and debug dumps.

### Important APIs, Types, And Functions
Important declarations include `acpi_ex_convert_to_*()`, `acpi_ex_do_debug_object()`, field helpers such as `acpi_ex_read_data_from_field()` and `acpi_ex_write_data_to_field()`, region access, concatenate/logical/math helpers, object creation for Mutex/Processor/Power/Region/Event/Alias/Method, `acpi_ex_load_op()` and `acpi_ex_unload_table()`, mutex acquire/release functions, serial bus and GPIO field access, OS service wrappers for Notify/Sleep/Stall/Event/Semaphore/Mutex, opcode groups `acpi_ex_opcode_*`, operand resolution/store/copy helpers, `acpi_ex_enter_interpreter()`, global-lock helpers, EISA/PCI/string conversion, space-ID validation, and default region handlers.

### Control Flow
Dispatcher code resolves operands using these declarations, executes opcode handlers by arity/target/result pattern, converts values to target types, performs field/region access, stores results to namespace nodes or target references, and calls OS services for sleep, stall, events, and synchronization. Region handlers route AML operation-region reads/writes to system memory, system I/O, PCI config, CMOS, PCI BAR, EC, SMBus, or data table backends.

### State, Persistence, And Dependencies
Interpreter state is in walk states, operand objects, namespace nodes, method/thread state, mutex lists, fields, regions, and global interpreter locks. The header depends on operand-object layout, parse objects, namespace nodes, ACPI status/types, and OS synchronization interfaces.

### Integration Points
This is the executor side of the parser/dispatcher/interpreter pipeline. It integrates with events for Notify, hardware for global lock and regions, namespace for stores, table manager for dynamic loads, and OS services for blocking operations.

### Risks
Operand conversion and implicit store rules are compatibility-sensitive. Field I/O must preserve update rules, byte widths, alignment, and region locking. Mutex acquisition must honor sync levels and avoid leaks on method termination. Default region handlers are hardware-facing and need strict address validation.

### Test Signals
AML interpreter suites should exercise conversions, arithmetic/logical opcodes, stores to fields/indexes/buffers/nodes, package/buffer/string handling, dynamic table load/unload, mutex/event methods, Notify, Sleep/Stall, region I/O, GPIO/serial bus fields, and method error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acinterp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/aclocal.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/aclocal.h

### Purpose
`aclocal.h` defines ACPICA internal data types and constants shared across the subsystem. It is the dense state-schema header for mutexes, namespace nodes, table lists, predefined-name validation, events/GPEs, parser state, AML parse objects, hardware register metadata, resource descriptor constants, disassembler/debugger structs, and debug memory tracking.

### Important APIs, Types, And Functions
Important types include `struct acpi_rw_lock`, `struct acpi_mutex_info`, `struct acpi_namespace_node`, `struct acpi_table_list`, `struct acpi_create_field_info`, predefined package info unions, repair callbacks, GPE handler/notify/dispatch/event/register/block/interrupt structs, fixed-event structs, generic state unions for control/scope/package/thread/result/notify, `struct acpi_opcode_info`, parse value/object/state structures, `struct acpi_bit_register_info`, `_OSI` and port validation structs, external/disassembler file lists, debugger method/integrity/object info, and debug allocation headers.

### Control Flow
The header does not execute code, but it models control flow for ACPICA: interpreter modes distinguish load pass 1, load pass 2, and execute; generic states form parser, scope, control, thread, result, and notify stacks; parse objects form AML trees; GPE dispatch unions select method, handler, or notify processing; namespace nodes hold parent/child/peer trees and attached objects.

### State, Persistence, And Dependencies
Most ACPICA persistent state is shaped here. Namespace nodes persist loaded tables and dynamic method-created nodes; table lists persist installed ACPI tables; GPE blocks and registers persist event routing; generic states are transient stack/cache objects; parser states are per-parse invocation. The header depends on public ACPI types, operand objects by forward reference, parse objects, locks, and build feature macros.

### Integration Points
Nearly all ACPICA subsystems include `aclocal.h` through `accommon.h`. Its structs are consumed by namespace, parser, dispatcher, interpreter, events, resources, table manager, debugger, disassembler, and ASL compiler code.

### Risks
Layout is ABI-like within ACPICA: descriptor fields must line up with operand objects, namespace-node size is optimized, packed predefined info depends on table layout, and small GPE structs are memory-sensitive. Flag reuse between runtime and iASL-only meanings can be confusing. Any change can cascade through caches, locks, parser walks, and table unload.

### Test Signals
Signals include full ACPICA builds, namespace load/unload, AML parse/execute, GPE dispatch, predefined-name validation/repair, resource parsing, debugger/disassembler/compiler builds, memory-debug builds, and static assertions or compile-time checks around packed/aligned structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/aclocal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acmacros.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acmacros.h

### Purpose
`acmacros.h` provides low-level C macros used across ACPICA for unaligned/endian data movement, integer formatting, power-of-two math, alignment/rounding, bit search, bit masks, register bit insertion, descriptor inspection, AML opcode table construction, error reporting, hardware optionality, UUID initialization, octal checks, and ASL converter hooks.

### Important APIs, Types, And Functions
Important macro families are `ACPI_GET/SET*`, `ACPI_MOVE_*`, `ACPI_FORMAT_UINT64`, division/multiply/modulo power-of-two helpers, alignment and rounding helpers, `ACPI_FIND_FIRST/LAST_BIT_*`, power-of-two rounding, masks above/below bit positions, register bit insertion/extraction, ACPI pathname character tests, descriptor pointer/type accessors, `ACPI_OP`, `ARGP/ARGI_LIST*` encoders, error/predefined warning macros, `ACPI_HW_OPTIONAL_FUNCTION`, `ACPI_INIT_UUID`, and `ASL_CV_*` converter hooks.

### Control Flow
These macros expand into inline operations used by many ACPICA paths. Compile-time branches select big-endian versus little-endian, unaligned-transfer support versus byte moves, native bit finder versus macro implementation, error-message enabled versus disabled, reduced-hardware versus hardware callback, and compiler-comment conversion versus no-op behavior.

### State, Persistence, And Dependencies
No state is owned, but macros directly read/write caller memory and descriptor fields. Dependencies include ACPICA integer types, cast macros from public headers, endian/alignment feature macros, and converter functions when compiler support is enabled.

### Integration Points
This header underpins parser opcode table definitions, AML argument encoding, register manipulation, resource parsing, table access, and debug/error reporting throughout ACPICA.

### Risks
Macro side effects are a major risk: many arguments may be evaluated in assignments or casts. Unaligned access choices must match architecture capabilities. Mask macros around full integer width avoid undefined shifts only when used correctly. Descriptor macros rely on common field layout shared by namespace and operand objects.

### Test Signals
Signals include big-endian and strict-alignment builds, UBSAN/ASAN where applicable, opcode table generation checks, register bit manipulation tests, error-message-disabled builds, reduced-hardware builds, and ASL compiler builds with comment conversion enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acmacros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acnamesp.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acnamesp.h

### Purpose
`acnamesp.h` declares ACPICA namespace management interfaces. It covers namespace initialization/loading/parsing, walking, lookup, node allocation/deletion, dynamic conversion, dumping, object evaluation, predefined-name argument and return validation/repair, pathname conversion, object attachment/data attachment, searching, and termination.

### Important APIs, Types, And Functions
Key constants include namespace property and lookup flags (`ACPI_NS_SEARCH_PARENT`, `ACPI_NS_DONT_OPEN_SCOPE`, `ACPI_NS_ERROR_IF_FOUND`, etc.), walk flags, package-element sentinels, and warning control. Important functions include `acpi_ns_load_namespace()`, `acpi_ns_load_table()`, `acpi_ns_walk_namespace()`, `acpi_ns_parse_table()`, `acpi_ns_execute_table()`, `acpi_ns_lookup()`, node create/delete/remove helpers, type conversion helpers, namespace dump functions, `acpi_ns_evaluate()`, predefined checking/repair functions, pathname builders/internalizers/externalizers, object attach/get/detach functions, data attachment functions, search/install functions, and `acpi_ns_terminate()`.

### Control Flow
Table loading parses AML into namespace nodes across load passes. Runtime evaluation resolves handles/pathnames, checks predefined argument counts/types, invokes methods or returns objects, validates/repairs predefined returns, and attaches resulting operand objects to namespace nodes. Walk helpers traverse namespace subtrees for initialization, dumps, unload, and GPE/method discovery.

### State, Persistence, And Dependencies
Namespace state is a tree of `struct acpi_namespace_node` objects, attached operand objects, owner IDs, and optional per-node data. The header depends on walk callbacks, evaluate info, predefined info, operand objects, and name/path conversion structures.

### Integration Points
It integrates parser/dispatcher table load, interpreter method execution, predefined-object validation, table unload, event/device initialization, debugger namespace commands, and public handle/path APIs.

### Risks
Lookup flags are subtle: parent search, temporary nodes, external declarations, and scope opening must match AML semantics. Dynamic table unload depends on owner IDs and object lifetime. Predefined repair can hide firmware defects but must not corrupt caller-owned objects. Namespace locking must be correct during walks and dynamic changes.

### Test Signals
Signals include AML namespace load, external declarations, dynamic table load/unload, path internalize/externalize round trips, handle lookup failures, predefined method validation/repair, namespace walks with unlock flags, node deletion by owner, and debugger namespace dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acnamesp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acobject.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acobject.h

### Purpose
`acobject.h` defines `union acpi_operand_object`, ACPICA's internal object descriptor used for AML operands, namespace-attached objects, operation regions, fields, methods, synchronization objects, handlers, references, and cache entries.

### Important APIs, Types, And Functions
It defines common object headers and flags, basic integer/string/buffer/package objects, event and mutex objects, operation regions, methods, common notify-capable objects, device/power/processor/thermal objects, common field information, region/bank/index/buffer fields, notify and address-space handler objects, reference objects and `ACPI_REFERENCE_CLASSES`, extra data objects, attached data objects, cache-list objects, descriptor-type constants, `union acpi_operand_object`, and `union acpi_descriptor`.

### Control Flow
The interpreter creates operand objects while parsing/executing AML, attaches them to namespace nodes, passes them through dispatcher/executor stacks, reads/writes fields and regions, manages references, calls method/handler dispatch pointers, and eventually releases them through reference counting and caches. Descriptor type fields let common code distinguish operand objects, namespace nodes, parser objects, walk states, and generic state entries.

### State, Persistence, And Dependencies
Objects may be transient operands, persistent namespace attachments, active method/region/handler state, synchronization primitives, or cached free-list entries. The common header includes `reference_count`; several object variants link back to namespace nodes or region handlers. Packing is set to 8 bytes on 64-bit and 4 bytes on 32-bit, and comments warn that the object is not byte-packable.

### Integration Points
All interpreter, namespace, event, region, and handler code depends on this layout. `acmacros.h` descriptor macros and `aclocal.h` namespace node layout rely on common field positions matching.

### Risks
Layout changes are high risk. String and buffer common fields must stay identical. Common descriptor/type positions must match namespace nodes. Reference-count and ownership flags (`AOPOBJ_STATIC_POINTER`, `AOPOBJ_DATA_VALID`, region flags) drive deletion and initialization behavior. Handler and region lists are lifetime-sensitive during detach/unload.

### Test Signals
Signals include object allocation/cache tests, reference-count leak detection, namespace attach/detach, method execution, region and field I/O, handler install/remove, package traversal, reference opcodes, table unload, and 32-bit/64-bit build layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acobject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acopcode.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acopcode.h

### Purpose
`acopcode.h` defines AML opcode metadata macros for parser-time arguments (`ARGP_*`) and interpreter-time arguments (`ARGI_*`). These macros feed ACPICA's master opcode table in `psopcode.c`.

### Important APIs, Types, And Functions
It defines extended/internal opcode bounds, sentinel opcode classes for unknown/name/prefix handling, then enumerates parse argument lists for AML opcodes such as `Method`, `Device`, `Field`, `If`, `While`, `Store`, arithmetic/logical operations, buffer/package creation, region declarations, and method calls. It also enumerates runtime operand requirements for executable opcodes, marking declaration-only opcodes as `ARGI_INVALID_OPCODE`.

### Control Flow
During parsing, `ARGP_*` lists tell the parser how to consume AML byte streams and construct parse objects. During execution, `ARGI_*` lists tell operand-preparation code how to resolve and type-check runtime operands before executor functions run. The argument-list packing macros come from `acmacros.h`.

### State, Persistence, And Dependencies
No runtime state is owned. The persistent effect is generated compile-time metadata in the opcode table. Dependencies include argument token constants and list macros defined elsewhere.

### Integration Points
Parser (`psargs`, `psopcode`, `psparse`) and interpreter operand-resolution code depend on these definitions. ASL compiler code may also use runtime argument definitions for validation.

### Risks
One incorrect argument list can desynchronize AML parsing, create malformed parse trees, or cause interpreter type errors. The split between parse-time and runtime argument forms is subtle, especially for declaration opcodes, targets, references, method calls, and package/field bodies. The file contains a bare `#define MAX_INTERNAL_OPCODE`, so consumers must tolerate or complete that upstream pattern.

### Test Signals
AML parser suites covering every opcode, malformed AML fuzzing, runtime operand type validation, ASL compiler opcode validation, and comparisons against known ACPICA opcode tables are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acopcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acparser.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/acparser.h

### Purpose
`acparser.h` declares AML parser interfaces. It covers method/table execution entry points, AML argument parsing, namepath parsing, parse-object creation/completion, opcode metadata lookup, parse-loop control, scope-stack management, parse-tree manipulation, parse-tree walking, parser utilities, and debug display helpers.

### Important APIs, Types, And Functions
Constants define parse modes and flags such as delete/no-delete tree, load pass 1, load pass 2, execute, deferred op, disassemble, and module-level parsing. Extern tables `acpi_gbl_short_op_index` and `acpi_gbl_long_op_index` map opcodes. Key functions include `acpi_ps_execute_method()`, `acpi_ps_execute_table()`, `acpi_ps_get_next_arg()`, `acpi_ps_get_next_namepath()`, `acpi_ps_build_named_op()`, `acpi_ps_create_op()`, `acpi_ps_complete_op()`, `acpi_ps_get_opcode_info()`, `acpi_ps_parse_aml()`, `acpi_ps_parse_loop()`, scope push/pop helpers, parse-tree append/find/get-depth functions, parse-tree walk/delete functions, op allocation/free/init functions, and parse-tree display functions.

### Control Flow
Parser entry points initialize a walk/parse state, parse AML bytecode into parse objects using opcode metadata, manage nested package/scope boundaries, call dispatcher callbacks during load or execute modes, complete or delete parse nodes, and walk parse trees for method execution or table processing.

### State, Persistence, And Dependencies
Parser state is in `struct acpi_parse_state`, `union acpi_parse_object`, scope-stack states, walk states, namespace nodes, owner IDs, and caller return descriptors. The header depends on parser structs from `aclocal.h`, opcode metadata, operand objects, and dispatcher callback types.

### Integration Points
It bridges raw AML tables/method bodies to the dispatcher, namespace loader, interpreter, disassembler, and debug display code. The Makefile links `ps*` objects to implement these declarations.

### Risks
Parser correctness is foundational. Package-end calculation, variable argument counts, method-call ambiguity, deferred ops, scope completion, and parse-tree deletion are common bug areas. Incorrect callback status handling can leak parse objects or skip execution steps.

### Test Signals
Signals include AML fuzzing, table load passes, method execution with nested scopes, deferred methods/regions, malformed package lengths, method-call namepath ambiguity, disassembly parses, parse-tree deletion under errors, and debug parse-tree output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/acparser.h -->
