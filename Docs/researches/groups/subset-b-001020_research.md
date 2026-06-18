# subset-b-001020 ACPICA Table and Utility Research

Grouped research for subset `subset-b-001020`. Each section is bounded by the reconciliation markers required for source-tree-aligned per-file output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfadt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfadt.c

Purpose: `tbfadt.c` normalizes the BIOS-provided Fixed ACPI Description Table into ACPICA's internal `acpi_gbl_FADT` representation, validates important FADT register/address fields, and installs the dependent DSDT/FACS tables. It bridges firmware table layout differences across ACPI revisions into a single internal format used by later hardware, event, and namespace code.

Important APIs/types/functions: `struct acpi_fadt_info` describes legacy 32-bit register fields, extended GAS fields, length fields, default widths, and validation flags. `struct acpi_fadt_pm_info` maps PM1 event block GAS entries into separate status/enable GAS globals. `acpi_tb_parse_fadt()` maps the installed FADT descriptor, verifies checksum, creates the local FADT, unmaps the original table, and installs DSDT/FACS/XFACS descriptors. `acpi_tb_create_local_fadt()` copies/truncates the firmware FADT, sets `acpi_gbl_reduced_hardware`, converts fields, and initializes PM register globals. Static helpers `acpi_tb_select_address()`, `acpi_tb_convert_fadt()`, `acpi_tb_init_generic_address()`, and `acpi_tb_setup_fadt_registers()` perform 32/64-bit address resolution, GAS construction, field validation, and PM1 split-register setup.

Control flow: FADT parse starts from `acpi_gbl_fadt_index` in `acpi_gbl_root_table_list`. The table is obtained with `acpi_tb_get_table()`, checksum-checked via `acpi_ut_verify_checksum()`, copied into `acpi_gbl_FADT`, converted, and released with `acpi_tb_put_table()`. Address selection favors nonzero 64-bit fields unless `acpi_gbl_use32_bit_fadt_addresses` forces legacy addresses. Non-reduced hardware conversion iterates `fadt_info_table`, expands legacy I/O addresses into GAS structs where needed, warns on 32/64 address or width mismatch, and validates required/optional length-address pairs. Register setup optionally enforces defaults under `acpi_gbl_use_default_register_widths`, then derives `acpi_gbl_xpm1a_status`, `acpi_gbl_xpm1a_enable`, `acpi_gbl_xpm1b_status`, and `acpi_gbl_xpm1b_enable`.

State and persistence behavior: The file mutates persistent ACPICA globals: `acpi_gbl_FADT`, `acpi_gbl_reduced_hardware`, `acpi_gbl_dsdt_index`, `acpi_gbl_facs_index`, `acpi_gbl_xfacs_index`, and PM1 GAS globals. It does not own durable storage, but it permanently shapes runtime table state for the lifetime of the ACPI subsystem. The original firmware FADT remains mapped only transiently; the internal copy is the authoritative later view.

Dependencies and integration points: It depends on table descriptor management in `tbutils.c`/`tbinstal.c`, checksum logic in `utcksum.c`, global knobs from ACPICA configuration, and ACPI GAS/table structures from `acpi.h`. Hardware register code, fixed-event code, namespace loading, FACS/global-lock handling, and DSDT parsing all consume the globals prepared here.

Risks and test signals: High-risk paths are mismatched 32/64 addresses, GAS bit-width overflow, optional register address/length mismatches, reduced-hardware early return, and DSDT/FACS install failures that are intentionally non-fatal in some cases. Test signals include boot logs for FADT BIOS warnings/errors, successful DSDT and FACS index population, PM1 status/enable GAS addresses derived from event blocks, behavior with `acpi_gbl_use32_bit_fadt_addresses`, and regression coverage for ACPI 1.0-sized FADTs, oversized FADTs, hardware-reduced FADTs, and large GPE blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfadt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfind.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfind.c

Purpose: `tbfind.c` locates an installed ACPI table by signature, OEM ID, and OEM Table ID inside `acpi_gbl_root_table_list`, returning the descriptor index used by later table APIs.

Important APIs/types/functions: `acpi_tb_find_table()` is the sole exported function in this file. It validates the four-character signature with `acpi_ut_valid_nameseg()`, checks OEM string length bounds, normalizes the search fields into a local `struct acpi_table_header`, and scans `struct acpi_table_desc` entries.

Control flow: The function rejects invalid signatures or oversized OEM filters before locking `ACPI_MTX_TABLES`. It walks current root table descriptors, first comparing cached descriptor signatures, validating/mapping a table with `acpi_tb_validate_table()` if its pointer is absent, then comparing full header signature/OEM fields. Empty OEM filters act as wildcards. On match it writes `*table_index`; otherwise it returns `AE_NOT_FOUND`.

State and persistence behavior: It does not allocate lasting state, but may cause a descriptor to become validated/mapped as a side effect of `acpi_tb_validate_table()`. Table list access is serialized by the table mutex.

Dependencies and integration points: It integrates with table validation/mapping logic, ACPICA mutex helpers, name validation from `utascii.c`, and public table lookup paths that need a stable table index rather than a pointer.

Risks and test signals: Risks include pointer validation failures during lookup, caller-provided non-NUL or too-long OEM strings, and races if callers bypass the table mutex elsewhere. Tests should cover wildcard OEM IDs, duplicate signatures/instances, invalid signatures, absent table pointers that must be mapped, and failure propagation from validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbfind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbinstal.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbinstal.c

Purpose: `tbinstal.c` verifies, installs, overrides, and removes ACPI table descriptors in the global root table list. It is the central point where firmware or caller-provided table memory becomes an installed ACPICA table entry.

Important APIs/types/functions: `acpi_tb_install_standard_table()` acquires a temporary descriptor, handles SSDT install suppression, verifies duplicates/unloads, installs the descriptor, notifies table handlers, and releases the temp descriptor. `acpi_tb_install_table_with_override()` allocates the next descriptor slot, applies logical/physical overrides when requested, initializes the descriptor, prints the header, and updates `acpi_gbl_dsdt_index`-related integer width. `acpi_tb_override_table()` uses OSL override hooks and replaces the original descriptor if the override validates. `acpi_tb_uninstall_table()` invalidates and clears a descriptor, freeing internal virtual table memory when owned.

Control flow: Install starts by acquiring table metadata via `acpi_tb_acquire_temp_table()`. Non-reload SSDTs can be skipped by global policy. Under `ACPI_MTX_TABLES`, `acpi_tb_verify_temp_table()` validates checksum/signature/duplicates. `AE_CTRL_TERMINATE` is treated as an unloaded table that may be reloaded, returning `AE_OK` after cleanup and index return. Successful installs release the table mutex around `acpi_tb_notify_table()` to avoid callback deadlock, then reacquire for cleanup. Override first tries `acpi_os_table_override()` for a logical replacement, then `acpi_os_physical_table_override()` for a physical one.

State and persistence behavior: The file mutates `acpi_gbl_root_table_list.tables`, table descriptor address/flags/pointer/signature/validation state, table indexes returned to callers, and DSDT integer-width state. Installed descriptors persist until explicit uninstall or subsystem termination. Temporary descriptors are always released after install/override flow.

Dependencies and integration points: It depends on OSL override hooks, descriptor allocation/resizing, verification, validation/invalidation, table-printing, table event notification, ACPICA memory ownership flags, and mutex helpers. It is called from root-table parsing, FADT DSDT/FACS installation, dynamic load APIs, and host-directed table install APIs.

Risks and test signals: Key risks are leaks or stale pointers on override failure, duplicate/reload semantics, callback ordering after install, incorrect origin flags causing invalid free/unmap behavior, and DSDT index/integer width drift. Test signals include table install/uninstall event notifications, override success/failure logs, root-list count and descriptor state after failed verification, reload of previously unloaded tables, and memory ownership checks for external virtual versus internal virtual tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbinstal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbprint.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbprint.c

Purpose: `tbprint.c` emits sanitized, human-readable ACPI table headers for diagnostics, with special handling for FACS, RSDP, and CDAT tables that do not fully match the common ACPI table header layout.

Important APIs/types/functions: `acpi_tb_print_table_header()` is the public utility. Static `acpi_tb_fix_string()` replaces non-printable bytes with `?`; `acpi_tb_cleanup_table_header()` copies a header and sanitizes signature/OEM/compiler string fields.

Control flow: The print function first identifies FACS by signature and prints only signature/physical address/length. It identifies RSDP by RSDP signature, sanitizes OEM ID, and prints revision and length using the ACPI 2.0 length only when present. If CDAT support is active and the signature is not a valid nameseg, it prints CDAT-style length. Otherwise it prints the sanitized common header fields.

State and persistence behavior: It does not mutate global ACPI state except diagnostic output. It uses a local header copy so firmware table contents are not repaired in place.

Dependencies and integration points: It depends on ACPICA logging macros, table signatures, name validation from `utascii.c`, and is used by root parsing, install, DSDT corruption diagnostics, and FADT/root table discovery paths.

Risks and test signals: Risks are accidental overread of special table layouts, misleading output from corrupt strings, and compiler diagnostics around packed headers. Test signals include clean boot table logs with malformed OEM strings, FACS/RSDP/CDAT formatting, and no mutation of the original table header after printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbprint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbutils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbutils.c

Purpose: `tbutils.c` supplies core table utilities for FACS initialization, DSDT corruption detection/copying, RSDT/XSDT parsing, root entry address decoding, and descriptor validation reference counting.

Important APIs/types/functions: `acpi_tb_initialize_facs()` maps the preferred FACS/XFACS table into `acpi_gbl_FACS`. `acpi_tb_check_dsdt_header()` detects DSDT replacement/corruption by comparing saved length/checksum. `acpi_tb_copy_dsdt()` copies the DSDT into owned memory and replaces the descriptor. `acpi_tb_parse_root_table()` maps the RSDP and RSDT/XSDT, validates checksum/length, installs child tables, and triggers FADT parsing. `acpi_tb_get_table()` and `acpi_tb_put_table()` maintain descriptor validation counts and map/unmap lifetime. Static `acpi_tb_get_root_table_entry()` handles unaligned 32/64-bit root entries.

Control flow: Root parsing maps a small RSDP, selects XSDT unless disabled or unavailable, unmaps RSDP before mapping the root table, validates root length and checksum, then iterates entries. Each nonzero entry is installed through `acpi_tb_install_standard_table()`. When a newly installed table is FADT, it records `acpi_gbl_fadt_index` and parses the FADT immediately to discover DSDT/FACS. Table get/put validates on first use, increments validation count up to `ACPI_MAX_TABLE_VALIDATIONS`, and invalidates when the count drops to zero.

State and persistence behavior: This file mutates `acpi_gbl_FACS`, `acpi_gbl_DSDT`, `acpi_gbl_original_dsdt_header`, descriptor pointers/validation counts, `acpi_gbl_fadt_index`, and DSDT descriptor ownership when copying. Root and table mappings are transient unless validation counts or permanent FACS handling keep them live.

Dependencies and integration points: It integrates OSL memory mapping, checksum utilities, table install/print/validation routines, FADT parsing, DSDT copy policy (`acpi_gbl_copy_dsdt_locally`), 32-bit/XSDT policy (`acpi_gbl_do_not_use_xsdt`), and public table APIs in `tbxface.c`.

Risks and test signals: Risks include mapping failures in early boot, invalid root lengths, 64-bit XSDT truncation on 32-bit builds, table validation count overflow/underflow, DSDT copy ownership mistakes, and FACS preference flag behavior. Tests should watch root table checksum errors, FADT-triggered DSDT/FACS installation, balanced `acpi_get_table()`/`acpi_put_table()` calls, `acpi=copy_dsdt`-style local copy behavior, and warnings from DSDT corruption detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxface.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxface.c

Purpose: `tbxface.c` exposes table-manager APIs used by the host OS and ACPICA clients to initialize the root table list, reallocate early static tables, retrieve tables/headers, release tables, and install/remove global table event handlers.

Important APIs/types/functions: `acpi_allocate_root_table()` allocates a resizable root array. `acpi_initialize_tables()` seeds the root list, locates the RSDP through `acpi_os_get_root_pointer()`, and parses the root table. `acpi_reallocate_root_table()` moves early table descriptors into dynamic memory and enables deferred validation. Retrieval APIs are `acpi_get_table_header()`, `acpi_get_table()`, `acpi_put_table()`, and `acpi_get_table_by_index()`. Event handler APIs are `acpi_install_table_handler()` and `acpi_remove_table_handler()`.

Control flow: Initialization either allocates a root table array or installs a caller-provided static array, then parses RSDT/XSDT. Reallocation checks for wrong early-stage validated state, turns on full validation when previously deferred, verifies existing descriptors, removes invalid ones, and resizes the list under `ACPI_MTX_TABLES`. `acpi_get_table_header()` can map only the header for physical unmapped tables, while `acpi_get_table()` uses descriptor validation and requires caller pairing with `acpi_put_table()`. Handler install/remove is serialized under `ACPI_MTX_EVENTS` and allows only one handler.

State and persistence behavior: Persistent state includes `acpi_gbl_root_table_list`, `acpi_gbl_enable_table_validation`, descriptor validation state, and global table handler/context. Table pointers returned by `acpi_get_table()` hold descriptor validation references until released.

Dependencies and integration points: This file is the external boundary for the table subsystem, integrating OSL RSDP discovery, root parsing in `tbutils.c`, descriptor resizing/verification, table mutexes, event mutexes, and exported ACPICA symbols used by the Linux ACPI core.

Risks and test signals: Risks include unbalanced get/put table lifetimes across boot stages, reallocation while descriptors are still validated, invalid instance numbering, single-handler conflicts, and header-only mapping failures. Tests should cover static and dynamic root arrays, reallocation after deferred validation, table retrieval by signature and index, null-output semantics, handler duplicate install/remove errors, and lockdep-style checks around table/event mutexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfload.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfload.c

Purpose: `tbxfload.c` exposes table load and unload APIs that populate the ACPI namespace from DSDT/SSDT/PSDT/OSDT tables, support host-directed dynamic table loads, and unload namespace objects owned by dynamically loaded tables.

Important APIs/types/functions: `acpi_load_tables()` installs default region handlers, calls `acpi_tb_load_namespace()`, then initializes namespace objects. `acpi_tb_load_namespace()` validates/loads DSDT first, optionally copies DSDT locally, records the original DSDT header, then loads SSDT/PSDT/OSDT tables. `acpi_install_table()` and `acpi_install_physical_table()` install tables before namespace load. `acpi_load_table()` dynamically installs and loads a table, returning an optional table index. `acpi_unload_parent_table()` and `acpi_unload_table()` unload SSDT/OEMx-style tables but reject the DSDT.

Control flow: Namespace load holds `ACPI_MTX_TABLES` while selecting/validating descriptors but releases it during `acpi_ns_load_table()` calls. DSDT failure is tracked separately, while optional table failures increment counters and eventually return `AE_CTRL_TERMINATE`; `acpi_load_tables()` converts that aggregate partial-failure code to `AE_OK` before object initialization. Dynamic load installs and loads in one path via `acpi_tb_install_and_load_table()`, then initializes newly created objects.

State and persistence behavior: It sets `acpi_gbl_DSDT`, `acpi_gbl_original_dsdt_header`, `acpi_gbl_namespace_initialized`, table owner IDs, and namespace objects created by AML load. Unload uses owner IDs to remove namespace objects and descriptors; DSDT owner/table index is protected from unload.

Dependencies and integration points: It depends on event region handler installation, namespace loading/initialization/termination support, table install/load/unload helpers, table mutexes, DSDT copy policy, and exported API symbols used by hotplug and early ACPI initialization.

Risks and test signals: Risks include lock release/reacquire around namespace loading, DSDT validation/copying races, partial optional table failure semantics, returning table indexes after dynamic load failure, and owner ID mismatches during unload. Tests should inspect namespace object counts after load, logs for failed optional AML tables, successful initialization of operation regions/buffers/packages, dynamic SSDT hot-add/hot-remove, and rejection of DSDT unload by handle or table index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfroot.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfroot.c

Purpose: `tbxfroot.c` finds and validates the Root System Description Pointer in low memory, supporting the early boot path that discovers the ACPI root table before the main table manager is initialized.

Important APIs/types/functions: `acpi_tb_get_rsdp_length()` returns either the ACPI 2.0+ RSDP length or the legacy checksum length after signature validation. `acpi_tb_validate_rsdp()` checks signature, legacy checksum, and extended checksum for revision 2+. `acpi_find_root_pointer()` searches EBDA and high BIOS memory windows for a valid RSDP. `acpi_tb_scan_memory_for_rsdp()` scans a mapped memory range in `ACPI_RSDP_SCAN_STEP` increments.

Control flow: Root search maps the EBDA pointer location, converts the segment to a physical address, checks that it is sane, maps up to the EBDA window bounded below VGA memory, scans for a valid RSDP, and returns the physical address if found. If EBDA search fails, it maps and scans the E0000h-FFFFFh window. Scanning validates each candidate by signature and checksum before returning.

State and persistence behavior: It has no persistent internal state; it returns the physical RSDP address through the caller's pointer. Mappings are always temporary and explicitly unmapped.

Dependencies and integration points: It depends on OSL low-memory mapping, checksum utility `acpi_ut_checksum()`, RSDP constants, and is called by OSL/root pointer discovery paths consumed by `acpi_initialize_tables()`.

Risks and test signals: Risks include mapping failures before memory services are mature, bogus EBDA pointers, scanning beyond the EBDA window, accepting duplicate invalid signatures, and revision/length inconsistencies. Tests should cover valid RSDP in EBDA and high BIOS windows, bad legacy or extended checksums, invalid signatures, absent ACPI, and EBDA pointer bounds at 0x400 and 0xA0000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbxfroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utaddress.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utaddress.c

Purpose: `utaddress.c` tracks system-memory and system-I/O operation region address ranges so ACPICA can detect overlaps between AML `OperationRegion` declarations and host accesses.

Important APIs/types/functions: `acpi_ut_add_address_range()` allocates and links an `acpi_address_range` for a namespace region node. `acpi_ut_remove_address_range()` removes the entry for a region node. `acpi_ut_check_address_range()` counts and optionally warns about overlap with tracked ranges. `acpi_ut_delete_address_lists()` frees all global range lists at shutdown.

Control flow: Add/remove/check ignore address spaces other than `ACPI_ADR_SPACE_SYSTEM_MEMORY` and `ACPI_ADR_SPACE_SYSTEM_IO`. Adds compute inclusive end address and push to `acpi_gbl_address_range_list[space_id]`. Checks compute the queried inclusive end and use interval overlap logic across the list, optionally building a normalized pathname for warnings.

State and persistence behavior: The persistent state is the linked list array `acpi_gbl_address_range_list`. Entries live from evaluated op-region creation until region deletion or subsystem shutdown. The file assumes namespace locking per comments rather than taking its own mutex.

Dependencies and integration points: It depends on namespace nodes/pathname helpers, region-name decoding from `utdecode.c`, ACPICA allocation, and region object deletion in `utdelete.c`, which removes ranges for permanent regions.

Risks and test signals: Risks include length-zero underflow, address+length overflow, missing namespace lock coverage, stale region nodes, and warning allocation failure assumptions. Tests should exercise overlapping/non-overlapping ranges, unsupported address spaces returning zero conflicts, removal at list head/middle, shutdown cleanup, and diagnostic pathnames for conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utaddress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utalloc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utalloc.c

Purpose: `utalloc.c` provides ACPICA allocation helpers, creates/deletes common object caches, and validates/initializes public `struct acpi_buffer` outputs.

Important APIs/types/functions: `acpi_os_allocate_zeroed()` is the default calloc-like OSL helper when not overridden. `acpi_ut_create_caches()` creates namespace, state, parse, extended parse, operand, and optional compiler/debug allocation caches. `acpi_ut_delete_caches()` purges/deletes those caches and optional debug allocation lists. `acpi_ut_validate_buffer()` checks public buffer parameters. `acpi_ut_initialize_buffer()` implements `ACPI_NO_BUFFER`, `ACPI_ALLOCATE_BUFFER`, `ACPI_ALLOCATE_LOCAL_BUFFER`, existing-buffer sizing, and zeroing.

Control flow: Cache creation is fail-fast in fixed order. Cache deletion nulls each global after delete and optionally dumps memory statistics. Buffer initialization snapshots the caller-provided length, writes back required length immediately, then either returns overflow, allocates through OSL or ACPICA allocation, validates an existing buffer size, and clears the returned buffer.

State and persistence behavior: Persistent globals include all cache handles (`acpi_gbl_namespace_cache`, `acpi_gbl_state_cache`, `acpi_gbl_operand_cache`, parse caches, optional compiler caches) and debug allocation lists. `acpi_ut_initialize_buffer()` mutates caller-owned buffer length and pointer.

Dependencies and integration points: It integrates with local cache implementations in `utcache.c`, OSL allocation/free functions, debugger statistics, namespace/parser/object allocation sites, and public ACPICA APIs that return variable-sized buffers.

Risks and test signals: Risks include partial cache creation without rollback, mismatched free expectations for OSL versus local allocated buffers, required length zero rejection, and callers ignoring updated lengths on overflow. Tests should cover every buffer length sentinel, existing buffer too small/large, allocation failures, cache create/delete idempotency at subsystem startup/shutdown, and debug allocation reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utascii.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utascii.c

Purpose: `utascii.c` validates ACPI nameseg/table-signature characters and repairs printable ASCII strings for diagnostics.

Important APIs/types/functions: `acpi_ut_valid_nameseg()` validates four characters. `acpi_ut_valid_name_char()` accepts uppercase letters, digits, underscore, and `!` only in position 3 for tables such as `ASF!`. `acpi_ut_check_and_repair_ascii()` copies bytes into a repaired string until NUL or `count`, replacing non-printable bytes with spaces.

Control flow: Nameseg validation is a fixed four-byte loop and does not require a NUL-terminated string. ASCII repair stops early on NUL after copying it, otherwise transforms only non-printable bytes.

State and persistence behavior: No global state is modified. The only mutation is writing to caller-provided `repaired_name`.

Dependencies and integration points: It is used by table lookup/printing, namespace name repair/validation, and any ACPICA component that needs fixed-size ACPI identifier validation.

Risks and test signals: Risks include signed-char `isprint` behavior if callers pass non-ASCII values, accidentally permitting lowercase names, and callers expecting full padding after early NUL. Tests should cover exactly four-byte non-NUL signatures, `ASF!`, lowercase rejection, underscore/digits, embedded NUL repair, and non-printable bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utascii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utbuffer.c

Purpose: `utbuffer.c` formats binary buffers as hex plus printable ASCII for debug output and, in application builds, file output.

Important APIs/types/functions: `acpi_ut_dump_buffer()` prints to ACPICA OS output. `acpi_ut_debug_dump_buffer()` gates dumping on debug layer/level. `acpi_ut_dump_buffer_to_file()` is compiled for `ACPI_APPLICATION` and writes to an `ACPI_FILE`.

Control flow: Dumping rejects null buffers, coerces odd or very small counts to byte display, prints 16 bytes per row using the requested display width, pads incomplete rows, and appends printable ASCII or dots unless `DB_DISPLAY_DATA_ONLY` is set. QWORD display prints as two 32-bit chunks to tolerate alignment.

State and persistence behavior: It holds no persistent state. Output is side-effect only.

Dependencies and integration points: It depends on ACPICA debug globals/macros, OSL printf/file APIs, unaligned move macros, and is used by table/resource/debugging paths where byte-level inspection is needed.

Risks and test signals: Risks include large debug dumps flooding logs, display-width assumptions when count is not aligned, and application/kernel output divergence. Tests should inspect byte/word/dword/qword rendering, data-only mode, null-buffer diagnostics, odd-length fallback, and debug gating by `acpi_dbg_level`/`acpi_dbg_layer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcache.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcache.c

Purpose: `utcache.c` implements ACPICA's optional local fixed-size object cache when `ACPI_USE_LOCAL_CACHE` is enabled.

Important APIs/types/functions: `acpi_os_create_cache()` allocates an `acpi_memory_list` cache descriptor. `acpi_os_purge_cache()` frees all cached objects. `acpi_os_delete_cache()` purges then frees the cache descriptor. `acpi_os_release_object()` returns an object to the cache or frees it if full. `acpi_os_acquire_object()` obtains a cached object or allocates a zeroed one.

Control flow: Cache operations validate inputs, serialize list mutation with `ACPI_MTX_CACHES`, use descriptor pointer fields to link freed objects, poison cached objects with `0xCA`, mark them `ACPI_DESC_TYPE_CACHED`, and zero objects when reacquired. Allocation is performed after releasing the cache mutex to avoid deadlock with tracked allocation.

State and persistence behavior: Persistent cache state lives in `struct acpi_memory_list`: list head, object size, current/max depth, and optional allocation statistics. Cached objects persist in memory for reuse until purged or deleted.

Dependencies and integration points: It integrates with `utalloc.c` cache creation/deletion, ACPICA mutexes, allocation macros, descriptor metadata, and optional memory tracking.

Risks and test signals: Risks include list corruption through descriptor-pointer reuse, depth underflow on purge, starvation or deadlock if mutex handling changes, and stale object contents if zeroing is skipped. Tests should cover cache hit/miss, max-depth freeing, purge/delete with populated cache, concurrent acquire/release under stress, and descriptor type transitions cached-to-operand/state after callers initialize objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcksum.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcksum.c

Purpose: `utcksum.c` verifies and generates ACPI 8-bit circular checksums for standard tables and CDAT-like tables.

Important APIs/types/functions: `acpi_ut_verify_checksum()` skips FACS/S3PT, computes the correct standard-table checksum, warns on mismatch, and optionally aborts under `ACPI_CHECKSUM_ABORT`. `acpi_ut_verify_cdat_checksum()` handles CDAT length/checksum fields. `acpi_ut_generate_checksum()` computes the byte needed to make the table sum zero after excluding the original checksum byte. `acpi_ut_checksum()` returns the raw circular sum over a buffer.

Control flow: Verification uses the table's own length field rather than the incoming length parameter for standard ACPI tables. A mismatch emits BIOS warnings and may return `AE_BAD_CHECKSUM` depending on build policy. CDAT verification writes the computed checksum back into `cdat_table->checksum`.

State and persistence behavior: Standard verification does not mutate the table. CDAT verification mutates the checksum field. No global state is stored.

Dependencies and integration points: It is used by root table parsing, FADT parsing, table validation, RSDP validation, and disassembler/application paths. It depends on table signatures and ACPICA warning macros.

Risks and test signals: Risks include trusting corrupted length fields, optional abort policy differences, CDAT checksum assignment semantics, and skipping checksum for nonstandard tables. Tests should include valid/invalid checksums, FACS/S3PT skip, checksum byte regeneration, zero-length or truncated buffers at callers, and `ACPI_CHECKSUM_ABORT` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcopy.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcopy.c

Purpose: `utcopy.c` translates ACPI objects between internal operand-object form, external `union acpi_object` API form, and deep internal copies. It is central to method return values, user-supplied arguments, packages, references, buffers, strings, and object duplication.

Important APIs/types/functions: External-facing helpers are `acpi_ut_copy_iobject_to_eobject()`, `acpi_ut_copy_eobject_to_iobject()`, and `acpi_ut_copy_iobject_to_iobject()`. Static helpers handle simple object conversion, package-to-package conversion, package tree callbacks, and deep-copy details. Supported simple types include integer, string, buffer, package, local name/reference subsets, processor, and power-resource objects depending on direction.

Control flow: Internal-to-external conversion lays out the top-level `union acpi_object`, package element arrays, and variable data in one caller-provided buffer; package traversal uses `acpi_ut_walk_package_tree()` with callbacks that advance `free_space` and `length`. External-to-internal conversion recursively builds package objects and copies string/buffer contents into new allocations. Internal-to-internal copy creates a destination operand object, copies fixed fields while preserving destination refcount/next-object, then deep-copies strings/buffers, creates new OS mutex/semaphore objects for mutex/event copies, and increments references for reference targets/region handlers.

State and persistence behavior: The file allocates new operand objects, package element arrays, string/buffer data, OS synchronization primitives, and external result buffers. It updates reference counts of referenced internal objects and expects callers to release returned objects with `acpi_ut_remove_reference()`.

Dependencies and integration points: It depends on namespace type lookup, package tree walking, object creation/deletion, interpreter EISA/string utilities, OS mutex/semaphore allocation, allocation macros, and public ACPICA buffer-size logic. It feeds method evaluation, argument conversion, namespace object copying, and public result APIs.

Risks and test signals: High-risk paths include package size/layout accounting, recursive external package conversion depth, null package elements, unsupported reference classes, partially failed deep copies, refcount leaks for references/region handlers, and copying mutex/event OS resources. Tests should round-trip strings/buffers/integers/packages, nested packages, null elements, name references, allocation failure cleanup, internal mutex/event copies, unsupported object type errors, and buffer length matching with `acpi_ut_get_object_size()` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdebug.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdebug.c

Purpose: `utdebug.c` implements ACPICA debug printing, function trace entry/exit helpers, stack-depth tracking, and interpreter trace point forwarding when `ACPI_DEBUG_OUTPUT` is enabled.

Important APIs/types/functions: `acpi_debug_print()` and `acpi_debug_print_raw()` are exported variadic debug sinks. `acpi_ut_trace*()` helpers log function entry with optional pointer/string/u32 payloads. `acpi_ut_exit*()` helpers log function exits with status/value/pointer/string payloads. `acpi_ut_init_stack_ptr_trace()` and `acpi_ut_track_stack_ptr()` maintain stack tracking globals. `acpi_trace_point()` forwards interpreter trace points to `acpi_ex_trace_point()` and optionally `acpi_os_trace_point()`.

Control flow: Debug output first checks `ACPI_IS_DEBUG_ENABLED()` against requested level and component. `acpi_debug_print()` tracks thread ID changes, optionally prints thread/nesting metadata in application builds, trims `Acpi`/`acpi_` prefixes from function names, and formats via `acpi_os_vprintf()`. Trace entry increments nesting and tracks stack before optional logging; exit logs and decrements nesting.

State and persistence behavior: Debug-only globals include previous thread ID, nesting/deepest nesting, entry/lowest stack pointers, and debug level/layer globals. It emits logs but does not affect core ACPI behavior when debug is disabled.

Dependencies and integration points: It depends on ACPICA debug macros, OSL thread/printf/tracing hooks, interpreter trace support, and exception formatting. Many ACPICA files call these helpers through trace macros, so correctness affects observability across the subsystem.

Risks and test signals: Risks include non-thread-safe nesting display across multiple threads, compiler warnings around storing stack addresses intentionally for diagnostics, log flooding, and format-string misuse by callers. Tests should verify debug gating, thread switch messages, function-name trimming for original and linuxized symbols, nesting under balanced trace/exit macros, stack-depth updates, and system tracer forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdecode.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdecode.c

Purpose: `utdecode.c` maps ACPICA numeric IDs, descriptor types, object types, region spaces, event IDs, mutex IDs, reference classes, notify values, and parser argument types to readable strings, and publishes namespace type property metadata.

Important APIs/types/functions: Key data includes `acpi_gbl_ns_properties`, `acpi_gbl_region_types`, type-name arrays, descriptor-name arrays, mutex names, notify-name arrays, and argument-type arrays. Functions include `acpi_ut_get_region_name()`, `acpi_ut_get_event_name()`, `acpi_ut_get_type_name()`, `acpi_ut_get_object_type_name()`, `acpi_ut_get_node_name()`, `acpi_ut_get_descriptor_name()`, `acpi_ut_get_reference_name()`, `acpi_ut_get_mutex_name()`, `acpi_ut_get_notify_name()`, `acpi_ut_get_argument_type_name()`, and `acpi_ut_valid_object_type()`.

Control flow: Most functions bounds-check indexes and return stable fallback strings for invalid IDs. `acpi_ut_get_object_type_name()` validates descriptor type before dereferencing object type. `acpi_ut_get_node_name()` recognizes NULL/root, verifies namespace-node descriptor type, repairs corrupted names, and returns a four-character nameseg. Notify decoding follows ACPI ranges: generic, reserved, per-object-specific, device-specific, and hardware-specific.

State and persistence behavior: The file mostly exposes read-only static/global lookup tables. `acpi_ut_get_node_name()` can repair a namespace node name in place if corruption is detected.

Dependencies and integration points: It is used throughout diagnostics, namespace handling, address-range warnings, mutex debug, notify dispatch logging, parser debugging, and object validation. It depends on namespace node structures and name repair helpers.

Risks and test signals: Risks include table/enum drift when ACPI adds values, in-place node name repair hiding corruption, invalid descriptor dereferences if callers pass arbitrary memory, and debug-only functions missing in non-debug builds. Tests should validate boundary values for every decoder, corrupted namespace names, user-defined region IDs, notify decoding by object type, and `acpi_ut_valid_object_type()` for local max.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdecode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdelete.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdelete.c

Purpose: `utdelete.c` owns internal ACPI operand-object reference counting and destruction. It releases type-specific resources, walks subobject graphs, prevents recursive package deletion stack growth, and deletes objects when reference counts reach zero.

Important APIs/types/functions: Public helpers are `acpi_ut_delete_internal_object_list()`, `acpi_ut_update_object_reference()`, `acpi_ut_add_reference()`, and `acpi_ut_remove_reference()`. Static `acpi_ut_update_ref_count()` updates one object's count under `acpi_gbl_reference_count_lock`; static `acpi_ut_delete_internal_obj()` frees type-specific resources and object descriptors.

Control flow: Refcount updates validate objects, skip namespace nodes where appropriate, update subobjects before the parent, and use a generic-state stack to avoid recursion through complex packages. Type-specific deletion frees strings/buffers/packages, GPE blocks, notify/address handlers, global-lock resources, OS mutexes/semaphores, method mutexes, region address ranges and handler contexts, secondary objects, PCC buffers, and address-handler mutexes. `REF_DECREMENT` deletes the object only when the new count is zero.

State and persistence behavior: The file mutates `common.reference_count`, global lock globals, address-range lists, handler region lists, GPE blocks, notify handler references, and object cache/descriptors. Deletion is permanent and releases memory/OS resources.

Dependencies and integration points: It depends on interpreter mutex unlinking, namespace secondary-object helpers, event/GPE deletion, address range removal, allocation/cache deletion, OS synchronization primitives, and object validation. It is used throughout namespace detach, method return cleanup, argument cleanup, table unload, and subsystem shutdown.

Risks and test signals: This is a high-risk lifecycle file. Risks include refcount underflow/overflow, circular region handler lists, deleting static table-backed buffers/strings, missed subobject references in packages/fields/references, global-lock special-case errors, and lock ordering around reference count updates. Tests should stress nested packages, bank/index/buffer fields, region handler detach, notify lists, global lock deletion, object list cleanup, invalid object guards, and leak/refcount accounting under repeated table load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdelete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uterror.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uterror.c

Purpose: `uterror.c` centralizes ACPICA internal warning/error output for predefined method validation, namespace lookup failures, and method execution failures when error messages are enabled.

Important APIs/types/functions: `acpi_ut_predefined_warning()`, `acpi_ut_predefined_info()`, and `acpi_ut_predefined_bios_error()` emit one-time messages based on namespace node flags. `acpi_ut_prefixed_namespace_error()` builds a prefix+internal path and classifies lookup failures. `acpi_ut_method_error()` reports method-path failures with formatted exception names. An obsolete `acpi_ut_namespace_error()` remains behind `__OBSOLETE_FUNCTION`.

Control flow: Predefined messages suppress repeated output once `ANOBJ_EVALUATED` is set. Namespace error classification treats `AE_ALREADY_EXISTS` and `AE_NOT_FOUND` as BIOS errors, other lookup failures as ACPICA errors, then builds and frees a full path. Method error optionally resolves a relative path from a prefix node before printing the node pathname.

State and persistence behavior: It does not store persistent state, but behavior is gated by node flags set elsewhere. It allocates/frees temporary path strings for diagnostics.

Dependencies and integration points: It depends on namespace path builders/printers, exception formatting, ACPICA output redirection macros, and is called by namespace lookup, predefined validation, and method execution paths.

Risks and test signals: Risks include log suppression hiding repeated firmware issues, allocation failure while building paths, confusing BIOS-vs-ACPICA error classification, and disabled output under `ACPI_NO_ERROR_MESSAGES`. Tests should cover predefined message suppression, prefixed path construction, method errors with and without path resolution, exception name formatting, and builds with error messages compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uterror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uteval.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uteval.c

Purpose: `uteval.c` provides common helpers for evaluating namespace objects/methods and validating their return types, especially standard device status and power methods.

Important APIs/types/functions: `acpi_ut_evaluate_object()` allocates `struct acpi_evaluate_info`, calls `acpi_ns_evaluate()`, checks expected return bitmaps, and returns an internal operand object. `acpi_ut_evaluate_numeric_object()` extracts an integer. `acpi_ut_execute_STA()` evaluates `_STA` with spec-defined defaults when missing. `acpi_ut_execute_power_methods()` evaluates arrays of `_SxD`/`_SxW`-style methods and returns byte values.

Control flow: Generic evaluation handles not-found as debug, other failures as method errors, rejects missing returns when expected, maps returned object types to `ACPI_BTYPE_*`, deletes unexpected implicit returns when interpreter slack is enabled and no return was expected, and removes references on type errors. Numeric/status/power wrappers call the generic helper and release returned objects after extracting values.

State and persistence behavior: It allocates temporary evaluation info and returns reference-counted operand objects to callers. `_STA` writes caller-provided flags; power methods fill an output byte array with values or `ACPI_UINT8_MAX` for missing/failed entries.

Dependencies and integration points: It depends on namespace evaluation, object reference deletion, method error reporting, type-name decoding, interpreter slack policy, standard method names, and is used by device enumeration/power management/ID helpers.

Risks and test signals: Risks include wrong expected-type bitmap, leaked return objects on wrapper errors, slack mode masking unexpected returns, default `_STA` behavior affecting device presence, and truncating power method integers to bytes. Tests should cover missing `_STA`, methods returning wrong types, no-return methods, implicit returns with slack on/off, mixed present/missing power methods, and allocation failure for evaluation info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uteval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utexcep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utexcep.c

Purpose: `utexcep.c` validates and formats `acpi_status` exception codes into stable symbolic strings.

Important APIs/types/functions: `acpi_format_exception()` is the exported formatter. `acpi_ut_validate_exception()` selects an entry from exception tables defined by `ACPI_DEFINE_EXCEPTION_TABLE` for environmental, programmer, table, AML, and control status classes.

Control flow: Formatting delegates to validation; unknown codes emit an ACPICA error and return `"UNKNOWN_STATUS_CODE"`. Validation masks the status class with `AE_CODE_MASK`, checks the sub-status against the class maximum, and returns NULL if no named entry exists.

State and persistence behavior: It uses compile-time exception tables and stores no mutable state.

Dependencies and integration points: It is used by debug, error, method evaluation, table loading, and nearly every path that logs `acpi_status`. It depends on status-code layout and generated exception-name globals.

Risks and test signals: Risks include enum/table drift, incorrect masking of new status classes, and logging recursion if unknown exceptions happen inside error paths. Tests should cover representative statuses from every class, boundary max values, invalid high-bit patterns, and exported symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utexcep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utglobal.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utglobal.c

Purpose: `utglobal.c` defines ACPICA global data tables and exported globals that are shared across the subsystem, including sleep/power method names, predefined namespace names, fixed hardware register metadata, fixed event metadata, PLD decode strings, and public debug/table counters.

Important APIs/types/functions: Data includes `acpi_gbl_sleep_state_names`, lowest/highest D-state method names, lower/upper hex digit strings, `acpi_gbl_pre_defined_names`, `acpi_gbl_bit_register_info`, `acpi_gbl_fixed_event_info`, and optional PLD string lists. It exports `acpi_gbl_FADT`, `acpi_dbg_level`, `acpi_dbg_layer`, `acpi_gpe_count`, and `acpi_current_gpe_count`.

Control flow: This file has no active control flow beyond compile-time conditional inclusion for reduced hardware, disassembler, and compiler builds. Consumers index these arrays by ACPI enum values.

State and persistence behavior: The arrays are persistent global constants or global metadata. Exported counters/debug globals are mutable elsewhere but defined here under `DEFINE_ACPI_GLOBALS`.

Dependencies and integration points: It is included by initialization, namespace setup, hardware/event code, debug code, table code, compiler/disassembler paths, and Linux-exported ACPICA interfaces. The predefined name table seeds namespace root children such as `_SB_`, `_TZ_`, `_REV`, `_OS_`, `_GL_`, and `_OSI`.

Risks and test signals: Risks include enum/table ordering mismatch, reduced-hardware build differences, incorrect predefined namespace type/value, and fixed-event/register metadata drift with ACPI specs. Tests should assert array sizes against enum counts, predefined namespace creation, `_REV` compatibility value, fixed event enable/status bit mapping, and exported debug globals in module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utglobal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uthex.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uthex.c

Purpose: `uthex.c` supplies small hex/ASCII conversion helpers used by compiler, disassembler, parser, and utility code.

Important APIs/types/functions: `acpi_ut_hex_to_ascii_char()` extracts a 4-bit nibble at a bit position from a `u64` and returns uppercase ASCII. `acpi_ut_ascii_to_hex_byte()` converts exactly two hex characters into one byte, validating both with `isxdigit()`. `acpi_ut_ascii_char_to_hex()` converts one valid hex character to a nibble.

Control flow: ASCII-to-byte rejects either invalid digit with `AE_BAD_HEX_CONSTANT`; otherwise it combines low and high nibbles. Single-char conversion assumes the caller already validated the character and branches by ASCII range.

State and persistence behavior: It holds only a static hex lookup table and mutates only caller-provided return bytes.

Dependencies and integration points: It depends on shift helper `acpi_ut_short_shift_right()`, C character classification, and ACPICA status codes. It is used where AML/compiler text or binary encodings need deterministic hex conversion.

Risks and test signals: Risks include caller misuse of `acpi_ut_ascii_char_to_hex()` with invalid characters, locale/signedness issues around `isxdigit`, and bit-position assumptions. Tests should cover uppercase/lowercase digits, invalid pairs, all nibble positions in a `u64`, and byte conversion order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/uthex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utids.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utids.c

Purpose: `utids.c` evaluates standard ACPI device identification methods and converts their AML return objects into allocated PNP device ID strings/lists.

Important APIs/types/functions: `acpi_ut_execute_HID()` evaluates `_HID` and returns a `struct acpi_pnp_device_id`. `acpi_ut_execute_UID()` evaluates `_UID`. `acpi_ut_execute_CID()` evaluates `_CID` and returns a `struct acpi_pnp_device_id_list`. `acpi_ut_execute_CLS()` evaluates `_CLS` and returns a PCI class string. Converters include `acpi_ex_eisa_id_to_string()`, `acpi_ex_integer_to_string()`, and `acpi_ex_pci_cls_to_string()`.

Control flow: HID/UID evaluate integer-or-string methods, compute output string length, allocate one struct plus string area, convert or copy, and release the AML return object. CID accepts integer/string/package, validates every package element, computes combined list and string storage, then writes each ID entry and advances a string pointer. CLS expects a package, reads up to three integer elements into base/sub/prog class bytes, and formats `BBSSPP`.

State and persistence behavior: Each successful function returns newly allocated caller-owned memory. It consumes temporary method return objects and releases them before exit. No global state is changed directly, though method execution can have AML side effects.

Dependencies and integration points: It depends on `uteval.c` for method evaluation/type checking, interpreter conversion utilities, ACPICA allocation/reference deletion, and is used by device enumeration and driver matching.

Risks and test signals: Risks include package elements being NULL or wrong type, unbounded firmware string lengths, allocation-size arithmetic for CID lists, integer UID decimal length, and accepting partial `_CLS` packages. Tests should cover integer and string HID/UID/CID, package CID with mixed entries, wrong CID element types, empty CID package, CLS packages of length 0-3+, allocation failure cleanup, and returned length/list_size correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utinit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utinit.c

Purpose: `utinit.c` initializes and shuts down ACPICA global state, including caches, mutex tracking, owner IDs, events/GPEs, handlers, global lock fields, namespace root, and subsystem termination.

Important APIs/types/functions: `acpi_ut_init_globals()` creates caches and resets global subsystem state for cold or warm restart. Static `acpi_ut_free_gpe_lists()` frees GPE interrupt/block lists when hardware support is enabled. Static `acpi_ut_terminate()` frees GPE lists and address ranges. `acpi_ut_subsystem_shutdown()` performs high-level shutdown of events, dynamic interfaces, namespace, tables, globals, and caches.

Control flow: Initialization first creates caches, then clears address range lists, mutex info, owner ID masks, event counters, GPE/event handler state, global notify/exception/init/table/interface handlers, global lock fields, DSDT/debug/shutdown flags, hardware state, and root namespace node fields. Shutdown checks `acpi_gbl_shutdown`, marks shutdown and clears startup flags, then calls event termination, interface termination, namespace termination, table termination, utility termination, and cache deletion.

State and persistence behavior: This file resets most ACPICA globals that define runtime subsystem state. Shutdown frees memory and marks the subsystem terminated; repeated shutdown logs an error and returns.

Dependencies and integration points: It depends on allocation/cache code, event/GPE code, namespace termination, table termination, interface management, address list cleanup, debug memory tracking, and compile-time reduced-hardware/compiler/disassembler options. It is called by subsystem initialization and termination entry points.

Risks and test signals: Risks include partial initialization failure after cache creation, forgotten globals across warm restart, double shutdown, freeing GPE lists while live handlers remain, and debugger mutex lifetime constraints. Tests should cover init-shutdown-init cycles, reduced hardware builds, GPE list cleanup, address range cleanup, root node initialization, double shutdown behavior, and cache deletion after namespace/table teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utlock.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utlock.c

Purpose: `utlock.c` implements ACPICA's simple reader/writer lock abstraction using two OS mutexes and a reader count.

Important APIs/types/functions: `acpi_ut_create_rw_lock()` initializes `struct acpi_rw_lock` and creates reader and writer mutexes. `acpi_ut_delete_rw_lock()` deletes both mutexes and clears fields. `acpi_ut_acquire_read_lock()`/`acpi_ut_release_read_lock()` manage shared readers. `acpi_ut_acquire_write_lock()`/`acpi_ut_release_write_lock()` manage exclusive writers.

Control flow: The first reader acquires `writer_mutex`, blocking writers; subsequent readers only increment `num_readers` under `reader_mutex`. The last reader releases `writer_mutex`. Writers simply acquire and release `writer_mutex`. The comments acknowledge potential writer starvation but treat it as acceptable for ACPICA usage patterns.

State and persistence behavior: The persistent lock state is `num_readers`, `reader_mutex`, and `writer_mutex` in the caller-owned lock object. No global state is modified.

Dependencies and integration points: It depends on OSL mutex create/delete/acquire/release routines and ACPICA status codes. It is a utility for shared data structures that need many readers and infrequent writers.

Risks and test signals: Risks include writer starvation, failed creation of the second mutex leaking the first, reader count underflow on unmatched release, and deleting a lock with active readers/writers. Tests should cover multiple concurrent readers, writer exclusion, first-reader/last-reader transitions, second-mutex creation failure handling, and misuse assertions under debug/lock checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/utlock.c -->
