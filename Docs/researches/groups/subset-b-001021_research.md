# Research: subset-b-001021

Grouped research report for ACPI ACPICA utility and APEI support files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmath.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmath.c

Purpose: `utmath.c` supplies ACPICA's portable 64-bit integer math helpers for multiplication, shifts, division, and modulo. It exists so ACPICA can run in 32-bit or freestanding environments that may not provide native 64-bit divide or double-width arithmetic.

Important APIs and functions: `acpi_ut_short_multiply`, `acpi_ut_short_shift_left`, `acpi_ut_short_shift_right`, `acpi_ut_short_divide`, and `acpi_ut_divide` return `acpi_status` and write optional output pointers. The file uses `uint64_overlay` to access high and low 32-bit halves when `ACPI_USE_NATIVE_MATH64` or `ACPI_USE_NATIVE_DIVIDE` are not enabled. The native branches directly use C operators.

Control flow: each helper validates only what matters to that operation, notably zero divisors in divide paths, then computes and conditionally stores requested quotient, remainder, product, or shift result. The non-native full divide has a fast 64-by-32 path and a normalized 64-by-64 path that estimates and corrects a 32-bit quotient.

State and dependencies: there is no persistent state. The code depends on ACPICA arithmetic macros such as `ACPI_DIV_64_BY_32`, `ACPI_SHIFT_RIGHT_64`, trace/error macros, and status values including `AE_AML_DIVIDE_BY_ZERO`.

Integration points: string parsing, printf formatting, AML arithmetic execution, and resource conversion code call these helpers where native arithmetic may not be available.

Risks: correctness is most sensitive in the non-native divide correction logic, shift count handling, and overflow truncation expectations. Native shifts do not mask count, so callers must avoid invalid C shift counts in native builds.

Test signals: divide-by-zero should return `AE_AML_DIVIDE_BY_ZERO`; native and non-native builds should agree for boundary values such as 0, 1, `UINT32_MAX`, `UINT64_MAX`, high-bit divisors, and shift counts around 0, 31, 32, 63, and 64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmisc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmisc.c

Purpose: `utmisc.c` contains common ACPICA utility routines that do not fit a narrower module: PCI root bridge ID checks, executable AML table recognition for tools, byte swapping, global integer width setup, package tree walking, update-state creation, and debug pathname display.

Important APIs and functions: `acpi_ut_is_pci_root_bridge` checks HID/CID strings against PCI and PCI Express root bridge IDs. `acpi_ut_is_aml_table` identifies DSDT, SSDT, PSDT, OSDT, and OEM AML-bearing tables in tool builds. `acpi_ut_dword_byte_swap` performs 32-bit endian swap. `acpi_ut_set_integer_width` updates `acpi_gbl_integer_bit_width`, nybble width, and byte width from DSDT revision. `acpi_ut_create_update_state_and_push` builds reference-count update states. `acpi_ut_walk_package_tree` performs iterative recursive package traversal using generic state objects.

Control flow: the package walker starts with a top-level package state, walks elements by index, invokes the callback for simple elements or packages, pushes parent state for nested packages, and pops states when a package level is exhausted. Allocation failures clean any pending state stack.

State and dependencies: integer width globals persist after `acpi_ut_set_integer_width`. Package walking depends on `utstate.c` state allocation and callback contracts, and on operand descriptor type checks.

Integration points: namespace initialization, object copying/sizing, reference update handling, and debugging all use these helpers. The AML table check is used by compiler/debugger/name tools rather than normal kernel runtime.

Risks: package traversal must handle null elements and namespace nodes without dereferencing them. Callback failures leave the current state allocated in some early return paths, so callers should treat errors as abort conditions in controlled contexts.

Test signals: nested packages with null/uninitialized slots, mixed simple/package elements, and callback-injected failures are useful. DSDT revision 1 versus 2+ should change integer width globals as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmutex.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmutex.c

Purpose: `utmutex.c` owns ACPICA internal synchronization object lifecycle and acquire/release wrappers for the predefined global mutex set, spinlocks, raw locks, the `_OSI` mutex, and the namespace reader/writer lock.

Important APIs and functions: `acpi_ut_mutex_initialize` creates every `acpi_gbl_mutex_info[]` mutex, `acpi_gbl_gpe_lock`, `acpi_gbl_hardware_lock`, `acpi_gbl_reference_count_lock`, `acpi_gbl_osi_mutex`, and `acpi_gbl_namespace_rw_lock`. `acpi_ut_mutex_terminate` deletes them. `acpi_ut_acquire_mutex` and `acpi_ut_release_mutex` validate mutex IDs, delegate to the OS mutex layer, and update owner thread/use-count bookkeeping. Static helpers `acpi_ut_create_mutex` and `acpi_ut_delete_mutex` perform per-entry lifecycle work.

Control flow: initialization loops through the fixed mutex IDs, then creates lock classes in dependency order. Acquire obtains the current thread ID, optionally checks strict mutex ordering under `ACPI_MUTEX_DEBUG`, waits forever on the OS mutex, and records ownership. Release checks validity and acquired state, optionally validates release order, clears owner state first, then releases the OS mutex.

State and dependencies: persistent global state includes OS mutex pointers, owning thread IDs, use counts, spinlock handles, and the namespace rwlock. The file depends on ACPICA OS services for mutex/lock creation and thread IDs.

Integration points: owner ID allocation, memory tracking, namespace access, event/GPE paths, `_OSI`, and subsystem initialization all depend on these locks being initialized first and terminated after subsystem shutdown.

Risks: partial initialization failure does not unwind previously created locks in this file, so callers must handle failed subsystem initialization carefully. Deadlock prevention is debug-only; production relies on correct lock ordering.

Test signals: init/terminate cycles, invalid mutex IDs, double release, same-thread reacquire under debug, and ordered nested acquire/release sequences are the main behavioral checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utnonansi.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utnonansi.c

Purpose: `utnonansi.c` supplies small non-ANSI or portability string helpers used by ACPICA tools and debug paths, including case conversion, case-insensitive compare, and bounded string copy/append wrappers.

Important APIs and functions: `acpi_ut_strlwr` and `acpi_ut_strupr` mutate an input string in place after a null check. `acpi_ut_stricmp` compares two strings case-insensitively and returns the usual signed difference. Under debugger/application/debug-output builds, `acpi_ut_safe_strcpy`, `acpi_ut_safe_strcat`, `acpi_ut_safe_strncat`, and `acpi_ut_safe_strncpy` provide size-aware wrappers; `acpi_ut_safe_strncpy` delegates to Linux `strscpy_pad`.

Control flow: conversion helpers walk until the terminating null byte and call `tolower`/`toupper` for each byte. The safe helpers precompute source/destination lengths and return `TRUE` if the requested operation would not fit; otherwise they call the normal C library operation.

State and dependencies: no persistent state. The file depends on C character/string routines and ACPICA build-condition macros.

Integration points: memory tracking copies module names with the safe copy helper; debugger and application command paths use the bounded routines to protect fixed command buffers. The case helpers support ACPICA parser and utility paths that need platform-independent behavior.

Risks: `acpi_ut_stricmp` does not accept null pointers. The safe append functions use the classic `>= dest_size` fit test and assume `dest` is already null-terminated. `strncat` may scan beyond the intended transfer length if callers provide inconsistent strings, so callers must pass valid C strings.

Test signals: empty strings, mixed-case equality, prefix ordering, exact destination-size boundaries, `max_transfer_length` shorter than source, and null inputs for only the helpers that explicitly allow null are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utnonansi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utobject.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utobject.c

Purpose: `utobject.c` creates, validates, deletes, and sizes ACPICA internal operand objects. It is central to converting AML/interpreter objects into external `union acpi_object` buffers for public APIs.

Important APIs and functions: `acpi_ut_create_internal_object_dbg` allocates a cached operand descriptor, creates secondary `LOCAL_EXTRA` descriptors for region/buffer-field/bank-field objects, sets the object type, and initializes the reference count. `acpi_ut_create_package_object`, `acpi_ut_create_integer_object`, `acpi_ut_create_buffer_object`, and `acpi_ut_create_string_object` allocate typed objects and backing storage. `acpi_ut_valid_internal_object`, `acpi_ut_allocate_object_desc_dbg`, and `acpi_ut_delete_object_desc` validate and manage descriptors through `acpi_gbl_operand_cache`. `acpi_ut_get_object_size` dispatches to simple or package sizing.

Control flow: object creation consistently allocates the descriptor first, then type-specific backing memory, and removes/releases the descriptor on allocation failure. Package sizing walks nested package elements with `acpi_ut_walk_package_tree`, sums rounded simple element sizes, counts package headers, and returns the external buffer length.

State and dependencies: persistent state lives in object descriptors, reference counts, `next_object` chains, package element arrays, and backing buffers. The module depends on operand descriptor caches, namespace pathname helpers for name references, and Linux kmemleak annotation.

Integration points: AML execution, namespace object attachment, public evaluation APIs, package copying, and reference-count deletion paths all rely on these constructors and size calculators.

Risks: sizing supports only specific reference classes and object types; unsupported reference classes return `AE_TYPE`. Alignment and packed string/buffer layout are deliberate, so external-object conversion code must use bytewise access where required.

Test signals: zero-length strings/buffers, package arrays with null elements, nested packages, name references requiring pathname sizing, unsupported local references, and allocation-failure cleanup paths should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utosi.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utosi.c

Purpose: `utosi.c` implements ACPICA support for the predefined `_OSI` method and manages the global list of interface strings reported as supported or unsupported to firmware.

Important APIs and functions: the static `acpi_default_supported_interfaces[]` lists Windows vendor strings through `"Windows 2022"` plus feature-group strings, marking optional features invalid by default. `acpi_ut_initialize_interfaces` links this static array and publishes it as `acpi_gbl_supported_interfaces`. `acpi_ut_interface_terminate` frees dynamic entries and resets static flags. `acpi_ut_install_interface`, `acpi_ut_remove_interface`, `acpi_ut_update_interfaces`, and `acpi_ut_get_interface` manipulate the list while the caller holds `acpi_gbl_osi_mutex`. `acpi_ut_osi_implementation` is the AML-visible `_OSI` implementation.

Control flow: `_OSI` validates its single string argument, creates an integer return object, searches the interface list under the `_OSI` mutex, returns all-ones for supported non-invalid strings, updates `acpi_gbl_osi_data` to the newest requested Windows value, releases the mutex, then invokes an optional host interface handler that can override support.

State and dependencies: persistent state includes the linked interface list, dynamic allocation for runtime interfaces, invalid/default-invalid flags, `acpi_gbl_osi_data`, `acpi_gbl_interface_handler`, and `acpi_gbl_osi_mutex`.

Integration points: public APIs in `utxface.c` wrap these functions. AML method execution routes `_OSI` calls here, and OS policy code can install handlers or modify interface strings before namespace initialization paths execute firmware methods.

Risks: firmware behavior depends heavily on exact string support policy. Dynamic list operations require external locking. Updating the default Windows strings is compatibility-sensitive because it can select different firmware code paths.

Test signals: lookup of valid, invalid, removed, and dynamically re-added strings; optional feature toggling; interface handler override behavior; `_OSI` non-string argument rejection; and Windows version tracking should be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utosi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utownerid.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utownerid.c

Purpose: `utownerid.c` allocates and releases ACPICA owner IDs, which tag namespace objects created by a table or method so they can be cleaned up when the table unloads or the method exits.

Important APIs and functions: `acpi_ut_allocate_owner_id` takes a pointer to an `acpi_owner_id`, rejects double allocation to a nonzero slot, scans global owner-ID bit masks for a free bit, marks it allocated, and returns an encoded one-based ID. `acpi_ut_release_owner_id` clears the caller's slot first, validates nonzero input, decodes ID to mask index/bit, and clears the allocation bit if set.

Control flow: allocation is serialized by `ACPI_MTX_CACHES`, begins at `acpi_gbl_last_owner_id_index` and `acpi_gbl_next_owner_id_offset`, wraps around the mask array, and may scan the starting mask twice. The final possible bit is reserved to prevent one-based overflow. Release also uses `ACPI_MTX_CACHES`, normalizes the ID to zero-based form, and reports attempts to release unallocated IDs.

State and dependencies: persistent global state includes `acpi_gbl_owner_id_mask[]`, the last index, and next offset. It depends on internal mutex services and ACPI division/modulo macros for bit-index decoding.

Integration points: table load/unload, namespace deletion, and control method execution use owner IDs to identify which objects are owned by the current table or method invocation.

Risks: leaked owner IDs eventually hit `AE_OWNER_ID_LIMIT`. Clearing the caller's ID before validation prevents repeated release attempts but can hide the original value from later callers. Correct lock initialization is required before use.

Test signals: allocation from a zero slot, double allocation detection, full-mask exhaustion, wraparound reuse after release, invalid zero release, and release of an unallocated nonzero ID are key cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utownerid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utpredef.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utpredef.c

Purpose: `utpredef.c` provides support routines for ACPICA predefined method/name metadata. Runtime code uses it to match names and format expected return types; compiler/help builds also expose display helpers for argument and resource metadata.

Important APIs and functions: `acpi_ut_get_next_predefined_method` advances through `acpi_gbl_predefined_methods`, skipping package-info entries that follow package-returning names. `acpi_ut_match_predefined_method` quickly rejects non-underscore names and searches predefined metadata. `acpi_ut_get_expected_return_types` formats the expected return bitmask into names such as `Integer/String/Buffer`. Tool-only functions include `acpi_ut_match_resource_name`, `acpi_ut_display_predefined_method`, static `acpi_ut_get_argument_types`, and `acpi_ut_get_resource_bit_width`.

Control flow: table matching is linear and uses ACPICA name-segment comparisons. Formatting iterates bitfields in stable table order and uses separators embedded in static string tables. Tool display logic decodes packed argument counts/types and validates maximum counts/types before printing.

State and dependencies: no mutable persistent state. The file depends on predefined metadata tables from `acpredef.h`, global tables such as `acpi_gbl_predefined_methods` and `acpi_gbl_resource_names`, and compiler/help build flags.

Integration points: namespace validation, predefined return-object repair, diagnostics, iASL, and `acpi_help` use these helpers to turn compact metadata into decisions or user-facing messages.

Risks: static string arrays must stay aligned with `ACPI_RTYPE_*`, `ACPI_TYPE_*`, and resource-width bit definitions. Metadata corruption can lead to invalid display or matching results, so tool-only validation messages are important.

Test signals: names with and without underscore, package-returning predefined entries, `ACPI_RTYPE_ALL`, empty expected bitmasks, invalid packed argument counts/types in tool builds, and resource-width bit combinations are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utpredef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utprint.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utprint.c

Purpose: `utprint.c` implements ACPICA's bounded formatted-printing routines for environments where host libc behavior is unavailable or must be controlled. It supports `vsnprintf`, `snprintf`, `sprintf`, and application-only stdout/file wrappers.

Important APIs and functions: static helpers `acpi_ut_bound_string_length`, `acpi_ut_bound_string_output`, `acpi_ut_put_number`, and `acpi_ut_format_number` implement bounded string handling and integer formatting. `acpi_ut_scan_number` parses decimal width/precision fields. `acpi_ut_print_number` writes a decimal integer string. `vsnprintf` parses flags, width, precision, qualifiers, and specifiers. Application builds add `vprintf`, `printf`, `vfprintf`, and `fprintf`.

Control flow: `vsnprintf` walks the format string, emits ordinary characters through the bounded output helper, parses `%` flags, width, precision, and `h/l/ll` qualifiers, handles `%`, `%c`, `%s`, `%o`, `%x`, `%X`, `%d`, `%i`, `%u`, `%p`, and prints unknown formats literally. It always advances the logical output pointer even when the buffer boundary is reached, then null terminates if size is nonzero.

State and dependencies: no normal persistent state. Application output wrappers serialize use of `acpi_gbl_print_buffer` with `acpi_gbl_print_lock`. Number conversion depends on `acpi_ut_divide` and `acpi_ut_short_multiply`.

Integration points: ACPICA diagnostics, tools, debug paths, and string formatting in freestanding builds depend on this implementation.

Risks: return value semantics are the attempted length, not necessarily bytes stored. Supported specifiers are intentionally limited. Signed conversion casts through fixed widths, and pointer formatting defaults to zero-padded native pointer width.

Test signals: zero-size buffers, exact-fit truncation, width/precision combinations, left/zero padding, signed negatives, 64-bit `%ll` values, null `%s`, pointer formatting, literal `%%`, and application wrapper locking are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utprint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresdecode.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresdecode.c

Purpose: `utresdecode.c` contains global constant string tables used to decode AML resource descriptor bitfields into readable names for ACPICA debug output, debugger resource dumps, and disassembly.

Important APIs and data: when `ACPI_DEBUG_OUTPUT`, `ACPI_DISASSEMBLER`, or `ACPI_DEBUGGER` is enabled, it exports arrays such as `acpi_gbl_bm_decode`, `acpi_gbl_config_decode`, `acpi_gbl_consume_decode`, `acpi_gbl_he_decode`, `acpi_gbl_ll_decode`, `acpi_gbl_mem_decode`, `acpi_gbl_shr_decode`, serial-bus arrays including `acpi_gbl_sbt_decode`, `acpi_gbl_am_decode`, `acpi_gbl_wm_decode`, `acpi_gbl_cph_decode`, `acpi_gbl_cpo_decode`, UART arrays, pin configuration names, and clock input names.

Control flow: there is no executable control flow beyond static initialization. Callers index these arrays with already-decoded descriptor field values.

State and dependencies: the arrays are immutable string-table state compiled only for diagnostic/tool configurations. The file depends on ACPI resource definitions from `acresrc.h` and the expectation that table order matches AML field encodings.

Integration points: resource descriptor dumping, ASL disassembly, and interactive debugger output use these names to convert compact numeric fields to ASL-like keywords.

Risks: the primary risk is table/index drift when ACPI adds resource encodings. Callers must bound-check indexes or choose arrays that include placeholder strings for reserved values, because this file does not validate indexes.

Test signals: descriptor dump tests should verify every legal bitfield value maps to the expected keyword, reserved values produce placeholder text where provided, and new descriptor fields added to `acresrc.h` have corresponding decode strings in diagnostic builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresdecode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresrc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresrc.c

Purpose: `utresrc.c` validates and walks raw AML resource templates. It provides descriptor-size tables, resource type classification, and helpers for extracting descriptor type, payload length, header length, full descriptor length, and end tags.

Important APIs and data: `acpi_gbl_resource_aml_sizes[]` gives minimum/fixed AML payload sizes by resource index, including small and large descriptor forms. `acpi_gbl_resource_aml_serial_bus_sizes[]` covers serial bus subtypes. Static `acpi_gbl_resource_types[]` classifies descriptor lengths as fixed, variable, or small-variable. `acpi_ut_walk_aml_resources`, `acpi_ut_validate_resource`, `acpi_ut_get_resource_type`, `acpi_ut_get_resource_length`, `acpi_ut_get_resource_header_length`, `acpi_ut_get_descriptor_length`, and `acpi_ut_get_resource_end_tag` form the public utility surface.

Control flow: the walker first requires room for an end tag, then repeatedly validates the current descriptor, computes total length, invokes an optional callback, and stops when it finds an end tag. If no end tag is found and a callback exists, it injects a synthetic end tag callback before returning `AE_AML_NO_RESOURCE_END_TAG`.

State and dependencies: there is no mutable state. The code depends on AML resource structure definitions, ACPI move/get macros, and optional `walk_state` for error reporting.

Integration points: resource conversion, `_CRS`/`_PRS` parsing, ASL compiler checks, namespace repair paths, and resource dump/disassembly code rely on these helpers to avoid walking malformed buffers.

Risks: validation must reject invalid type/length combinations before using descriptor lengths for pointer advancement. SerialBus descriptors need subtype validation. The end-tag checksum byte is intentionally not validated for field compatibility.

Test signals: fixed-length mismatch, variable-length minimums, small IRQ min/min-minus-one forms, invalid large/small type values, invalid SerialBus type zero/out of range, missing/truncated end tags, zero-length resource buffer, and callback failure propagation should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstate.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstate.c

Purpose: `utstate.c` manages ACPICA generic state objects, which act as stack frames for package traversal, reference-count updates, control-flow execution, and per-thread method execution state.

Important APIs and functions: `acpi_ut_push_generic_state` and `acpi_ut_pop_generic_state` implement singly linked stack operations. `acpi_ut_create_generic_state` obtains a state object from `acpi_gbl_state_cache`. Specialized constructors include `acpi_ut_create_thread_state`, `acpi_ut_create_update_state`, `acpi_ut_create_pkg_state`, and `acpi_ut_create_control_state`. `acpi_ut_delete_generic_state` returns state objects to the cache.

Control flow: each specialized constructor allocates a generic state, changes its descriptor type to the specific flavor, and initializes the fields used by that flavor. Thread state records the current OS thread ID and replaces an invalid zero ID with one after logging an error. Package state records source object, destination/external object, current index, and package count. Control state initializes conditional execution state.

State and dependencies: persistent state objects are short-lived and cached in `acpi_gbl_state_cache`. The file depends on ACPICA OS object caches and thread ID services.

Integration points: package walking in `utmisc.c`, object sizing/copying in `utobject.c`, interpreter control-flow execution, and reference-count update/deletion logic all use these state objects.

Risks: stack operations do not validate inputs; callers must not push null or corrupted states. State memory is reused from caches, so constructors must initialize all fields they rely on. Zero thread IDs would break ownership matching, hence the defensive repair.

Test signals: push/pop LIFO behavior, empty pop, constructor descriptor types and initialized fields, zero-thread-ID fallback, and delete-null behavior should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstring.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstring.c

Purpose: `utstring.c` contains ACPICA string and character display/repair helpers, mainly for debug output, namespace robustness, and tool pathname normalization.

Important APIs and functions: `acpi_ut_print_string` prints a quoted string with ACPI/C-style escapes and truncation indication after `max_length`. `acpi_ut_repair_name` validates a four-character ACPI name segment and replaces invalid characters with `_`, logging a warning unless interpreter slack mode is enabled. Tool builds also provide `ut_convert_backslashes`, which normalizes path separators to forward slashes.

Control flow: string printing handles null pointers specially, iterates up to `max_length` or null terminator, emits named escapes for control characters, backslash-escapes quotes/backslashes, emits printable characters directly, and emits hex escapes for other bytes. Name repair skips the root pathname special case, copies the original name for diagnostics, validates each segment character with position-aware rules, and reports only if a repair occurred.

State and dependencies: no local persistent state. The warning/debug behavior depends on `acpi_gbl_enable_interpreter_slack`. The file depends on namespace/name validation helpers and `acpi_os_printf`.

Integration points: namespace loading, malformed firmware tolerance, debug dumps, and ACPICA tools use these routines to keep output printable and to avoid rejecting some firmware with bad but repairable names.

Risks: repairing names changes namespace identifiers and could theoretically collide, though `_` is chosen to remain printable and unusual in invalid positions. `acpi_ut_print_string` casts bytes through `int`; callers should provide valid byte strings.

Test signals: null strings, strings with each escape character, nonprintable bytes, max-length truncation, valid/invalid name characters by position, root pathname bypass, slack-mode diagnostic difference, and Windows-style path conversion in tool builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrsuppt.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrsuppt.c

Purpose: `utstrsuppt.c` provides low-level support for ACPICA string-to-integer conversion, including base-specific conversion loops, prefix/whitespace handling, and overflow-checked multiply/add helpers.

Important APIs and functions: `acpi_ut_convert_octal_string`, `acpi_ut_convert_decimal_string`, and `acpi_ut_convert_hex_string` accumulate base 8/10/16 values and return base-specific overflow or bad-constant statuses in compiler builds. `acpi_ut_remove_leading_zeros`, `acpi_ut_remove_whitespace`, `acpi_ut_detect_hex_prefix`, `acpi_ut_remove_hex_prefix`, and `acpi_ut_detect_octal_prefix` mutate caller string pointers. Static `acpi_ut_insert_digit`, `acpi_ut_strtoul_multiply64`, and `acpi_ut_strtoul_add64` implement checked accumulation.

Control flow: each conversion walks until null or invalid character, validates the digit class, multiplies the current accumulator by base, adds the new digit, and stops on invalid input or overflow while returning the value accumulated so far.

State and dependencies: there is no local persistent state, but overflow checks consult `acpi_gbl_integer_bit_width` to enforce 32-bit limits when needed. The helpers depend on `acpi_ut_short_divide`, ASCII hex conversion, and C character classification.

Integration points: `utstrtoul64.c` builds ACPI runtime, compiler, debugger, and tool conversion semantics on top of these helpers. Predefined-name repair and table parsers also depend on consistent conversion behavior.

Risks: runtime and compiler builds intentionally differ on invalid digits. Functions mutate string pointers, so callers must pass writable pointer variables. Global integer width must be set correctly before conversions that should enforce 32-bit limits.

Test signals: whitespace-only strings, leading zeros, hex/octal prefixes, invalid digits by base, maximum 32-bit and 64-bit values, overflow by one digit, compiler versus runtime invalid-input behavior, and pointer advancement after prefix removal should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrsuppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrtoul64.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrtoul64.c

Purpose: `utstrtoul64.c` implements ACPICA's top-level string-to-integer conversion policies for full 64-bit parser/tool conversion, runtime implicit conversion, and runtime explicit `to_integer` conversion.

Important APIs and functions: `acpi_ut_strtoul64` supports decimal, hex with `0x`, and octal with leading `0`, forces a 64-bit conversion regardless of current DSDT integer width, and returns overflow status. `acpi_ut_implicit_strtoul64` implements ACPI implicit conversion rules: hex only, optional ACPICA-accepted `0x`, no errors, overflow truncation. `acpi_ut_explicit_strtoul64` implements explicit conversion rules: decimal by default, hex with `0x`, no octal, no errors, overflow truncation.

Control flow: all three paths trim leading whitespace and leading zeros. `acpi_ut_strtoul64` detects base, temporarily saves and changes `acpi_gbl_integer_bit_width` to 64, calls the base converter, then restores the original width. Runtime conversions ignore status from lower-level converters by design.

State and dependencies: the only mutable state interaction is temporary global integer-width override in `acpi_ut_strtoul64`. The file depends on prefix/removal and base conversion helpers from `utstrsuppt.c`.

Integration points: iASL parsers/preprocessor, data table compiler, AML interpreter conversions, debugger command parsing, `acpi_dump`, return-value repair, and acpi_exec namespace overrides use these conversion policies.

Risks: caller expectations must match the selected conversion policy; implicit hex-only behavior and explicit no-octal behavior are intentionally different from parser conversion. Temporary mutation of global integer width must always be restored.

Test signals: empty and whitespace strings, `0`, decimal, octal, hex, implicit `"BA98"` and `"0x1234"`, explicit `"012"` as decimal not octal, overflow truncation in runtime paths, and status-returning overflow in `acpi_ut_strtoul64` are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrtoul64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uttrack.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/uttrack.c

Purpose: `uttrack.c` implements ACPICA debug-only allocation tracking when `ACPI_DBG_TRACK_ALLOCATIONS` is enabled. It helps detect leaks, duplicate frees, invalid descriptors, and outstanding cache allocations.

Important APIs and functions: `acpi_ut_create_list` allocates a tracking list descriptor. `acpi_ut_allocate_and_track` and `acpi_ut_allocate_zeroed_and_track` allocate memory with a debug header and insert it into the global list. `acpi_ut_free_and_track` removes a block, updates counters, poisons user memory with `0xEA`, and frees it. Static `acpi_ut_find_allocation`, `acpi_ut_track_allocation`, and `acpi_ut_remove_allocation` manage the address-ordered doubly linked list. `acpi_ut_dump_allocation_info` is mostly stubbed/commented, and `acpi_ut_dump_allocations` prints outstanding matching allocations with descriptor interpretation.

Control flow: allocation normalizes zero-byte requests to one byte with a warning, allocates header plus user payload, tracks under `ACPI_MTX_MEMORY`, and updates totals/max occupancy. Free derives the header from the user pointer, updates totals, unlinks under the memory mutex, poisons, and frees.

State and dependencies: persistent debug state includes `acpi_gbl_global_list`, allocation counters, current/max size, `acpi_gbl_disable_mem_tracking`, `acpi_gbl_verbose_leak_dump`, and the global allocation list. It depends on `ACPI_MTX_MEMORY`, descriptor macros, and diagnostic output.

Integration points: ACPICA allocation macros route here in debug builds. Leak dumps integrate with object, parser, and namespace descriptor layouts.

Risks: this code is intentionally expensive and debug-only. If tracking is disabled midstream, list consistency assumptions differ. Pointer ordering in `acpi_ut_find_allocation` assumes comparable allocation addresses.

Test signals: zero-size allocation, duplicate insertion detection, freeing null, freeing with empty list, component/module-filtered dumps, cached descriptor suppression, verbose hex dump, and descriptor type/size validation are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uttrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utuuid.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utuuid.c

Purpose: `utuuid.c` provides UUID conversion helpers for ACPICA compiler, acpi_exec, and help application builds. It converts between ACPI/ASL UUID strings and the 16-byte buffer layout used by `ToUUID`.

Important APIs and data: `acpi_gbl_map_to_uuid_offset[16]` maps each output buffer byte to the two hex characters in a canonical 36-byte UUID string. `acpi_ut_convert_string_to_uuid` converts a formatted UUID string into 16 bytes. `acpi_ut_convert_uuid_to_string` converts a 16-byte buffer back to canonical text with hyphens and null terminator.

Control flow: string-to-buffer conversion loops over all 16 bytes, reads two mapped hex characters, converts high and low nibbles with `acpi_ut_ascii_char_to_hex`, and stores the byte. Buffer-to-string loops over all bytes, writes high/low hex characters at mapped offsets with `acpi_ut_hex_to_ascii_char`, inserts four hyphens, and terminates.

State and dependencies: no mutable state. Compilation is limited to tool-like builds. The code depends on UUID length/offset constants and ACPICA hex conversion helpers.

Integration points: iASL `ToUUID` handling, acpi_exec, and help output use these conversions to match ACPI's specified byte ordering, which differs from simple left-to-right text order for the first UUID fields.

Risks: `acpi_ut_convert_string_to_uuid` assumes callers validated input length, hyphen positions, and hex characters. Buffer-to-string validates null pointers but assumes the output buffer is at least 37 bytes.

Test signals: canonical UUID round trips, mixed-case hex input, invalid/null pointer handling for buffer-to-string, mapped byte order for the first fields, and output hyphen/null placement should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utuuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxface.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxface.c

Purpose: `utxface.c` exposes miscellaneous external ACPICA utility interfaces: subsystem termination, optional status/system info/statistics APIs, cache purging, `_OSI` interface management, operation-region overlap checks, and `_PLD` buffer decoding.

Important APIs and functions: `acpi_terminate` shuts down ACPICA resources, mutexes, and the OS layer. Future-usage blocks include `acpi_subsystem_status`, `acpi_get_system_info`, `acpi_get_statistics`, and `acpi_install_initialization_handler`. Runtime exports include `acpi_purge_cached_objects`, `acpi_install_interface`, `acpi_remove_interface`, `acpi_install_interface_handler`, `acpi_update_interfaces`, `acpi_check_address_range`, and `acpi_decode_pld_buffer`.

Control flow: interface APIs validate names, lock `acpi_gbl_osi_mutex`, then use `utosi.c` list helpers or handler state. Cache purging calls OS cache purge on state, operand, and parser caches. Address-range checking locks the namespace before querying operation-region overlaps. `_PLD` decoding validates buffer length, allocates `struct acpi_pld_info`, reads packed dwords with ACPI macros, and fills revision 1 plus optional revision 2 fields.

State and dependencies: persistent state includes startup flags, global FADT/system counters/debug levels, caches, `_OSI` list/handler, namespace region data, and allocated `_PLD` result buffers owned by callers.

Integration points: ACPI core init/exit, drivers using public ACPICA APIs, firmware interface policy, device physical-location parsing, and operation-region safety checks all route through this file.

Risks: many optional APIs are build-gated. `_PLD` callers must free returned memory. Interface modifications affect firmware execution paths. Termination order matters because mutexes are deleted before OS termination.

Test signals: invalid buffer/name parameters, interface install/remove/reinstall, handler duplicate install/removal, cache purge success, address overlap warnings, `_PLD` rev1/rev2 decoding, short `_PLD` rejection, and termination after partial initialization are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxferror.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxferror.c

Purpose: `utxferror.c` provides ACPICA external-facing diagnostic output functions for errors, exceptions, warnings, informational messages, and firmware/BIOS-specific diagnostics.

Important APIs and functions: when `ACPI_NO_ERROR_MESSAGES` is not defined, the file exports `acpi_error`, `acpi_exception`, `acpi_warning`, `acpi_info`, `acpi_bios_error`, `acpi_bios_exception`, and `acpi_bios_warning`. Exception variants include decoded `acpi_status` text for failures; plain variants print formatted caller messages. `acpi_info` emits a simpler `ACPI:` prefix without module/line/version suffix.

Control flow: every function starts a message redirect block, emits the appropriate ACPICA prefix, formats varargs through `acpi_os_vprintf`, appends the common suffix where appropriate, ends the varargs list, and closes redirect handling. For `AE_OK`, exception functions omit decoded error text and print the message under the error/firmware-error prefix.

State and dependencies: no local persistent state. The module depends on ACPICA message prefix/suffix macros, redirection macros, `acpi_os_printf`, `acpi_os_vprintf`, and `acpi_format_exception`.

Integration points: the rest of ACPICA uses these functions through `ACPI_ERROR`, `ACPI_EXCEPTION`, warning, firmware warning, and info macros. Kernel and ACPICA application builds share this implementation, subject to compile-time message suppression.

Risks: formatting is only as safe as caller format strings and arguments. Redirect macros must be correct for the host build. Suppressing `ACPI_NO_ERROR_MESSAGES` removes these diagnostics, affecting debuggability.

Test signals: each severity prefix, suffix inclusion, `AE_OK` versus failure exception output, firmware-specific prefixes, varargs formatting, message redirection behavior, and builds with `ACPI_NO_ERROR_MESSAGES` should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxferror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfinit.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfinit.c

Purpose: `utxfinit.c` exposes the main ACPICA initialization sequence: early subsystem initialization, hardware/event enablement, and namespace/device object initialization.

Important APIs and functions: `acpi_initialize_subsystem` initializes the OS layer, global variables, internal mutexes, namespace root, and default `_OSI` interfaces. `acpi_enable_subsystem` completes ACPI hardware enablement: clears early initialization, maps FACS unless disabled, enables ACPI mode unless disabled, initializes events unless disabled, and installs SCI/global-lock handlers unless disabled. `acpi_initialize_objects` initializes namespace devices/regions unless disabled, purges caches, and sets `ACPI_INITIALIZED_OK`.

Control flow: each phase is ordered and returns immediately on failure with contextual diagnostics. Compile-time reduced-hardware and obsolete-behavior blocks remove hardware or old object initialization as appropriate. Flags such as `ACPI_NO_FACS_INIT`, `ACPI_NO_ACPI_ENABLE`, `ACPI_NO_EVENT_INIT`, `ACPI_NO_HANDLER_INIT`, `ACPI_NO_DEVICE_INIT`, and `ACPI_NO_ADDRESS_SPACE_INIT` gate work.

State and dependencies: persistent state includes `acpi_gbl_startup_flags`, `acpi_gbl_early_initialization`, FACS mapping, original ACPI mode, initialized locks, namespace root, event handlers, and caches. Dependencies span OS services, tables, hardware, events, namespace, debugger, and `_OSI` utilities.

Integration points: platform ACPI boot code calls these phases in order after table discovery/loading. Later public APIs assume successful completion and startup flags.

Risks: phase ordering is critical: methods may require hardware/events, and `_REG`/`_STA`/`_INI` run after handler setup. Partial failures can leave initialized components for termination paths to clean.

Test signals: each no-init flag combination, reduced-hardware builds, OS-layer failure, mutex failure, namespace root failure, FACS mapping failure, ACPI enable failure, event/handler failure, device init failure, cache purge, and final startup flag are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfmutex.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfmutex.c

Purpose: `utxfmutex.c` implements public driver-facing APIs for acquiring and releasing AML mutex objects, allowing OS drivers and AML code to coordinate access to shared hardware transactions.

Important APIs and functions: static `acpi_ut_get_mutex_object` resolves a mutex by optional namespace handle and/or pathname, verifies the node type is `ACPI_TYPE_MUTEX`, retrieves the attached operand object, and returns it. `acpi_acquire_mutex` resolves the object and calls `acpi_os_acquire_mutex` with a caller-supplied timeout. `acpi_release_mutex` resolves the object and releases the underlying OS mutex.

Control flow: the resolver rejects missing output pointer or both handle and pathname absent. If a pathname is supplied, it calls `acpi_get_handle` relative to the handle. It then enforces mutex node type and non-null attached object. Acquire and release are thin wrappers after resolution.

State and dependencies: no local state. Persistent state is the namespace node and attached mutex operand object with `mutex.os_mutex`. Dependencies include namespace handle lookup, object attachment, and OS mutex services.

Integration points: external kernel drivers can use these APIs to synchronize with AML-defined mutexes around hardware access paths. They complement internal ACPICA mutexes in `utmutex.c` but operate on AML namespace mutex objects.

Risks: release does not verify ownership at this layer; behavior depends on OS mutex semantics. Namespace path resolution can fail if called before namespace load or after object removal. Callers must choose appropriate timeouts to avoid deadlock or unexpected failure.

Test signals: handle-only, pathname-only, and handle-plus-relative-path resolution; null parameter rejection; non-mutex node rejection; mutex with missing attached object; acquire timeout behavior; and release of a valid mutex should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfmutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/acpi/apei/Kconfig

Purpose: this `Kconfig` defines Linux kernel configuration symbols for ACPI Platform Error Interface support and its subfeatures: GHES, PCIe AER integration, ARM64 SEA, memory failure recovery, EINJ, CXL EINJ, NVIDIA GHES vendor records, and ERST debug support.

Important symbols: `HAVE_ACPI_APEI` and `HAVE_ACPI_APEI_NMI` are architecture capability booleans. `ACPI_APEI` enables the base framework and selects `MISC_FILESYSTEMS`, `PSTORE`, and `UEFI_CPER`. `ACPI_APEI_GHES` enables Generic Hardware Error Source and selects ACPI HED, IRQ work, generic allocator, and ARM SDE on ARM64. `ACPI_APEI_PCIEAER`, `ACPI_APEI_SEA`, `ACPI_APEI_MEMORY_FAILURE`, `ACPI_APEI_EINJ`, `ACPI_APEI_EINJ_CXL`, `ACPI_APEI_GHES_NVIDIA`, and `ACPI_APEI_ERST_DEBUG` gate focused integrations.

Control flow: Kconfig dependencies express build eligibility. Selecting `ACPI_APEI` unlocks subordinate options; `ACPI_APEI_EINJ_CXL` additionally requires CXL bus compatibility with the EINJ tristate.

State and dependencies: this file does not define runtime state. It controls which object files and feature code are compiled and which framework dependencies are pulled into the kernel configuration.

Integration points: the `apei/Makefile` consumes these symbols to build `apei.o`, `ghes.o`, `einj.o`, vendor handlers, and debug modules. Architecture Kconfig must provide `HAVE_ACPI_APEI`.

Risks: incorrect dependencies can expose unsupported firmware-first paths on architectures without required interrupt/NMI handling. Tristate compatibility for CXL EINJ must prevent linking built-in code against unavailable module code.

Test signals: configuration matrix builds for disabled base, base-only, GHES, EINJ as built-in/module, CXL EINJ with CXL bus tristate variations, NVIDIA handler, ERST debug, ARM64 SEA defaulting, and missing `HAVE_ACPI_APEI` should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/Makefile -->
## sources/distributed-fs/ceph-client/drivers/acpi/apei/Makefile

Purpose: this `Makefile` maps APEI kernel configuration symbols to object files and composes multi-object built-ins/modules for ACPI Platform Error Interface support.

Important build rules: `obj-$(CONFIG_ACPI_APEI) += apei.o` builds the base aggregate. `obj-$(CONFIG_ACPI_APEI_GHES) += ghes.o` builds GHES. A conditional disables KASAN instrumentation for `ghes.o` when compile-testing with older Clang versions below 18. `obj-$(CONFIG_ACPI_APEI_PCIEAER) += ghes_helpers.o`, `obj-$(CONFIG_ACPI_APEI_EINJ) += einj.o`, `obj-$(CONFIG_ACPI_APEI_ERST_DEBUG) += erst-dbg.o`, and `obj-$(CONFIG_ACPI_APEI_GHES_NVIDIA) += ghes-nvidia.o` add optional pieces. `einj-y` is `einj-core.o` plus optional `einj-cxl.o`; `apei-y` is `apei-base.o hest.o erst.o bert.o`.

Control flow: there is no runtime control flow, but the build composition controls which translation units are linked into each feature object.

State and dependencies: build-time state comes from Kconfig symbols and the `clang-min-version` helper. Runtime state is defined in compiled C files, not here.

Integration points: Kconfig selects symbols; this file turns them into the actual APEI base, GHES, EINJ, ERST debug, and vendor handler objects linked into the kernel.

Risks: object composition affects symbol availability. The Clang/KASAN workaround indicates `ghes.o` stack use or instrumentation sensitivity under older compilers. Missing optional object inclusion would silently drop feature support despite config prompts.

Test signals: build `CONFIG_ACPI_APEI` base, GHES with old/new Clang compile-test KASAN conditions, EINJ with and without CXL, ERST debug as module, NVIDIA handler as module, and all features disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-base.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-base.c

Purpose: `apei-base.c` implements shared APEI infrastructure for ERST/EINJ action-table interpretation, Generic Address Register access, APEI resource reservation, debugfs setup, architecture hooks, and WHEA `_OSC` negotiation.

Important APIs and functions: `apei_exec_ctx_init`, `__apei_exec_run`, `apei_exec_read_register`, `apei_exec_read_register_value`, `apei_exec_write_register`, `apei_exec_write_register_value`, `apei_exec_noop`, `apei_exec_pre_map_gars`, `apei_exec_post_unmap_gars`, and `apei_exec_collect_resources` operate on `struct apei_exec_context`. Resource APIs include `apei_resources_add`, `apei_resources_sub`, `apei_resources_request`, `apei_resources_release`, and `apei_resources_fini`. GAR APIs include `apei_map_generic_address`, `apei_read`, and `apei_write`. `apei_get_debugfs_dir` lazily creates `/sys/kernel/debug/apei`; `apei_osc_setup` runs WHEA `_OSC`.

Control flow: the interpreter scans action-table entries matching an action, validates instruction indexes, invokes instruction handlers, supports handler-directed jumps through `ctx->ip`, and treats missing optional actions as success. Pre-map and resource collection iterate every entry and act only on instruction types flagged `APEI_EXEC_INS_ACCESS_REGISTER`.

State and persistence: global `apei_resources_all` tracks all requested APEI I/O memory and I/O port ranges. Resource lists merge overlapping intervals, subtract already requested, NVS, and arch-filtered regions, then request/release kernel resources. A static debugfs dentry persists after first creation.

Dependencies and integration: the file depends on ACPI GAS accessors, ACPI NVS iteration, resource reservation APIs, debugfs, CPER/WHEA concepts, and weak architecture hooks. ERST, EINJ, GHES, and BERT use this common layer.

Risks: resource interval math must handle overlaps/splits correctly. GAR validation rejects zero addresses, invalid access widths, bad bit ranges, and unsupported address spaces; firmware bugs are common. Action-table loops with jumps must avoid unintended rewinds.

Test signals: invalid instruction indexes, optional missing actions, jump handlers, pre-map rollback on failure, overlapping resource merge/subtract/split, NVS/arch exclusion, GAR read/write for memory and I/O, invalid GAS fields, and `_OSC` failure/success are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-internal.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-internal.h

Purpose: `apei-internal.h` declares internal APEI execution, resource, debugfs, CPER, `_OSC`, and EINJ helper interfaces shared by APEI translation units.

Important APIs and types: `struct apei_exec_context` holds interpreter instruction pointer, value registers, base registers, instruction table, action table pointer, and entry counts. `struct apei_exec_ins_type` pairs flags with instruction handlers, and `APEI_EXEC_INS_ACCESS_REGISTER` marks register-accessing instructions. Inline helpers set/get interpreter input/output and wrap `__apei_exec_run` for required or optional actions. Resource helpers define `struct apei_resources` with `iomem` and `ioport` lists plus init/fini/add/sub/request/release prototypes. `cper_estatus_len` computes CPER generic status length using raw data offset/length if present. EINJ declarations cover base and CXL injection paths and validation.

Control flow: the header itself has only inlines. They map the public internal pattern: initialize context, set input, run an action, read output, and manage resources around tables.

State and dependencies: no storage is defined here except inline behavior. It depends on Linux ACPI types, list heads, debugfs forward declarations, CPER structures, and conditional fallback definitions for newer CXL EINJ bits.

Integration points: `apei-base.c`, `bert.c`, HEST/GHES/ERST/EINJ modules, and CXL EINJ support include this header to share contracts without exporting them outside the APEI implementation boundary.

Risks: structure field layout and helper semantics must stay synchronized with action-table interpreter code. `cper_estatus_len` trusts firmware-provided lengths and must be paired with validation before walking records.

Test signals: compile coverage for every APEI object, optional-action wrapper behavior, resource init producing empty lists, CPER status length with and without raw data, and availability of fallback CXL EINJ bit definitions are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/bert.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/apei/bert.c

Purpose: `bert.c` implements APEI Boot Error Record Table support. It maps the BERT boot error region during late init, prints bounded CPER records from the previous boot, clears one-time-polled block status, and releases resources.

Important APIs and functions: `bert_print_all` walks `struct acpi_hest_generic_status` records in the BERT region, validates length and CPER status, prints at most five records shorter than 1024 bytes, counts skipped records, and clears `block_status`. `setup_bert_disable` handles the `bert_disable` boot parameter. `bert_check_table` validates table and region minimum sizes. `bert_init` is registered with `late_initcall`.

Control flow: initialization exits early if ACPI is disabled or `bert_disable` is set, obtains the BERT table with `acpi_get_table`, validates it, reserves the region through APEI resources, maps it with `ioremap_cache`, prints records, unmaps, releases resources, finalizes lists, and drops the ACPI table reference. `AE_NOT_FOUND` is a quiet no-op.

State and dependencies: `bert_disable` is `__initdata`. Firmware-provided BERT memory is persistent across boot until read; this code clears each printed/skipped record's `block_status` in the mapped region. Dependencies include CPER validation/printing, ACPI table services, I/O mapping, and APEI resource reservation.

Integration points: built into the base `apei.o` aggregate, BERT complements GHES/ERST by surfacing unhandled previous-boot hardware errors through kernel logs while leaving full table data available under ACPI table sysfs.

Risks: firmware may provide truncated, invalid, oversized, or excessive records. Region reservation and mapping can fail. Clearing block status mutates firmware error memory and should only happen after validation/walk decisions.

Test signals: no ACPI, disabled parameter, missing table, invalid table length, short region, resource request failure, map failure, valid multiple records, oversized/skipped records, truncated status block, invalid CPER status, zero block status terminator, and cleanup on every error path are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/bert.c -->
