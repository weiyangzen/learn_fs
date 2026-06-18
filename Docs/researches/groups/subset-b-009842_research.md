# Research: subset-b-009842

Grouped research for Samba source3 printing files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_ads.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing_ads.c

Purpose: implements Active Directory publication support for Samba printers when `HAVE_ADS` is enabled. It maps local spoolss printer metadata into AD `printQueue` attributes, stores/retrieves the AD object GUID in the printer registry data, publishes/unpublishes LDAP entries, and checks configured printers that are marked published. Without ADS support it provides compatibility stubs returning `WERR_NOT_SUPPORTED`, `WERR_OK`, or `false`.

Important APIs and functions: `nt_printer_guid_store()` writes `SPOOL_DSSPOOLER_KEY/objectGUID` through internal winreg as `REG_SZ`, while `nt_printer_guid_get()` reads either the current string form or legacy `REG_BINARY`. `nt_printer_dn_lookup()` constructs a printer DN under the local machine account using escaped server CN and share name. `nt_printer_publish()` updates the local `PRINTER_ATTRIBUTE_PUBLISHED` bit via `winreg_update_printer_internal()` before calling `nt_printer_publish_ads()` or `nt_printer_unpublish_ads()`. `check_published_printers()` iterates printable services and republishes those already flagged. `is_printer_published()` is a registry-backed query helper.

Control flow: publish/update actions set the local attribute, connect as the machine account to ADS, build LDAP modifications from `spoolss_PrinterInfo2`, and modify or add the printer entry. Successful ADS publication attempts to retrieve the AD GUID and persist it locally. Unpublish looks up the printer on the server and deletes the LDAP DN. Republish scanning uses loadparm services plus winreg printer fetches.

State and persistence: AD state lives in LDAP printQueue objects; local state lives in Samba winreg printer metadata under `DsSpooler`. The GUID storage path intentionally uses `REG_SZ` for Vista compatibility but retains binary read compatibility.

Dependencies and integration: depends on ADS/LDAP helpers, secrets/machine credentials, loadparm, generated spoolss types, winreg spoolss helpers, NDR GUID conversion, and Samba messaging/session context. It integrates with spoolss server operations that publish printers and with startup or maintenance checks that re-publish configured shares.

Risks: DN construction and LDAP escaping are security-sensitive. ADS failures can leave the local published bit set without an AD object. `nt_printer_info_to_mods()` does not check every `ads_mod_str()` return, so allocation or LDAP-mod construction failures may be partially masked. Empty-string attributes are deliberately skipped to avoid LDAP errors. Tests should cover ADS-disabled stubs, GUID read/write in both formats, publish-add versus publish-modify, unpublish missing entries, and failure behavior when winreg succeeds but ADS fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing_migrate.c

Purpose: converts records from legacy NT printing TDB blobs into current winreg-backed spoolss data by unmarshalling historical NDR structures and invoking winreg spoolss RPC helpers.

Important APIs and functions: `printing_tdb_migrate_form()` unmarshals `ntprinting_form` and calls `winreg_printer_addform1()`, skipping built-in forms and treating existing forms as success. `printing_tdb_migrate_driver()` unmarshals `ntprinting_driver`, strips path components from driver files, populates `spoolss_AddDriverInfo3`, and calls `winreg_add_driver()`. `printing_tdb_migrate_printer()` unmarshals `ntprinting_printer`, maps `ntprinting_printer_info` and devmode fields into `spoolss_SetPrinterInfo2` plus `spoolss_DeviceMode`, then updates printer data values with `winreg_set_printer_dataex()`. `printing_tdb_migrate_secdesc()` unmarshals `sec_desc_buf` and applies it with `winreg_set_printer_secdesc()`.

Control flow: callers provide one key/value pair from old TDB storage. The function selects the expected NDR structure, optionally enables ASCII string conversion for old data, translates fields into spoolss structures, and returns `NTSTATUS` derived from NDR or WERROR failures. Printer data migration splits stored names at the first backslash into key and value names.

State and persistence: this file does not open databases itself. It writes migrated state to the registry-style printing store through the winreg pipe and does not delete source TDB records. It preserves driver private data and devmode extra data when present.

Dependencies and integration: uses generated NDR parsers for `ntprinting`, `spoolss`, and security descriptors, plus `rpc_pipe_client` binding handles and `cli_winreg_spoolss` helpers. It is called by `nt_printing_migrate_internal.c` while walking old `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`.

Risks: malformed blobs currently map to `NT_STATUS_NO_MEMORY`, which can obscure parse corruption. `printing_tdb_migrate_printer()` mutates `printer_data[j].name` in place while splitting on `\\`. Field-by-field devmode translation is easy to regress if generated structs change. Tests should feed representative legacy blobs, built-in forms, existing forms, missing devmode, driver paths with backslashes, invalid NDR, and printer data with and without backslash separators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate.h -->
# sources/user-network-fs/samba/source3/printing/nt_printing_migrate.h

Purpose: public migration interface for translating individual legacy NT printing TDB records into the winreg-backed printing store.

Important APIs and types: declares four `NTSTATUS` functions: `printing_tdb_migrate_form()`, `printing_tdb_migrate_driver()`, `printing_tdb_migrate_printer()`, and `printing_tdb_migrate_secdesc()`. Each takes a `TALLOC_CTX`, an open `rpc_pipe_client *` for winreg, a legacy key name, raw record bytes, and record length. Driver and printer migration also accept `do_string_conversion` for ASCII legacy data.

Control flow and integration: callers choose the function based on the TDB key prefix and pass the unmodified record payload. The implementation handles NDR unmarshalling, spoolss structure mapping, and winreg calls. This header is included by both the implementation file and the internal migration walker.

State and persistence: the header itself owns no state. Its contract implies state changes through the supplied winreg pipe, so callers must already have system-level session credentials and a valid binding.

Dependencies: relies on Samba core declarations for `NTSTATUS`, `TALLOC_CTX`, `bool`, and `struct rpc_pipe_client`, normally available through `includes.h` before inclusion.

Risks and test signals: because this is a narrow ABI between TDB walking and record conversion, prototype drift would break migration at build time. Tests should compile consumers with this header and exercise all four implementation paths through the internal migrator.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.c

Purpose: orchestrates one-time migration from legacy print TDB files into the current registry-backed print store, then renames successfully processed TDB files to `.bak`.

Important APIs and functions: `nt_printing_tdb_migrate()` is the exported entry point. It locates `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`, opens an internal winreg pipe as the system session, and calls `migrate_internal()` for each existing file. `migrate_internal()` opens a TDB read-only, walks records by prefix (`FORMS/`, `DRIVERS/`, `PRINTERS/`, `SECDESC/`), calls the conversion functions in `nt_printing_migrate.c`, and handles security descriptors in a second pass. `rename_file_with_suffix()` moves migrated databases to `*.bak`, treating `ENOENT` as non-fatal.

Control flow: migration first handles forms, drivers, and printers so target printer objects exist before security descriptors are applied. Secdesc failures for missing printers are skipped; other failures abort the file migration. If no legacy databases exist, migration succeeds without opening winreg.

State and persistence: reads legacy state from `state_path()` TDB files, writes current state through internal winreg RPC, and renames source TDBs as a completion marker. It does not wrap multi-file migration in a transaction, so partial migration is possible if a later file fails.

Dependencies and integration: depends on TDB iteration helpers, filesystem paths, `make_session_info_system()`, `rpc_pipe_open_interface()` for `ndr_table_winreg`, Samba messaging, and the per-record migration API. It is a startup/upgrade helper used before old printing databases are retired.

Risks: failures after some records have been written may leave a partly migrated registry with the original TDB still present. Rename failure is logged but does not change the success return from `migrate_internal()`. Iteration must free TDB keys and fetched data correctly. Tests should cover no-file success, malformed TDB records, order-dependent secdesc migration, missing printer secdesc skip, winreg pipe failures, and `.bak` rename behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.h -->
# sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.h

Purpose: internal header exposing the high-level legacy NT printing TDB migration entry point.

Important API: declares `bool nt_printing_tdb_migrate(struct messaging_context *msg_ctx);`. The function uses Samba messaging while opening an internal winreg RPC pipe and migrating old print databases.

Control flow and integration: consumers call this once during initialization or upgrade handling. The implementation performs file discovery, winreg setup, per-file migration, and backup renames.

State and persistence: the declared API can mutate persistent registry-backed printer data and rename legacy TDB files to `.bak`, although the header owns no state itself.

Dependencies: requires prior declarations for `bool` and `struct messaging_context`, provided by normal Samba include ordering.

Risks and test signals: this small header is a coupling point between initialization code and the migration implementation. Build tests should ensure it remains included where the migrator is invoked; integration tests should verify the function is called with a valid messaging context and is idempotent after files are renamed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_os2.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing_os2.c

Purpose: maps Windows printer driver names to OS/2 driver names using the configured `os2 driver map` file, with a single-entry process-local cache for the last successful mapping.

Important APIs and functions: `spoolss_map_to_os2_driver()` validates the input driver pointer, checks whether a map file is configured, returns the cached mapping when possible, loads the map file with `file_lines_load()`, parses `windows=OS/2` lines, trims whitespace, skips comments, and replaces `*pdrivername` with a talloc-owned OS/2 name on match. `set_driver_mapping()`, `get_win_driver()`, and `get_os2_driver()` maintain the static cache.

Control flow: if no map file is configured, the function returns `WERR_FILE_NOT_FOUND`. Empty or unreadable maps return `WERR_EMPTY`. A non-matching map is not an error; it leaves the original driver name in place and returns `WERR_OK`.

State and persistence: map data is read from a configured file. The only in-process state is `win_driver` and `os2_driver`, both replaced with heap-allocated copies after a successful match.

Dependencies and integration: integrates with spoolss code that needs OS/2-compatible driver names. It depends on loadparm substitution, Samba file-line utilities, string helpers, and WERROR conventions.

Risks: the static cache is global and not keyed by mapfile path, so a configuration reload changing the map file could keep serving one stale mapping until another mapping is found. `set_driver_mapping()` failure is ignored before duplicating `os2_name`, losing cache but not the returned mapping. Tests should cover whitespace, comments, missing `=`, repeated lookups, no configured map, empty map, non-match success, and allocation failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_os2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_os2.h -->
# sources/user-network-fs/samba/source3/printing/nt_printing_os2.h

Purpose: declares the OS/2 driver-name mapping helper used by spoolss printing code.

Important API: `WERROR spoolss_map_to_os2_driver(TALLOC_CTX *mem_ctx, const char **pdrivername);` accepts an in/out driver-name pointer and may replace it with a talloc-owned mapped OS/2 name.

Control flow and integration: callers pass the current Windows driver name before returning printer information to OS/2-oriented clients. The implementation decides whether a configured mapping file exists and whether the name should change.

State and persistence: no state in the header. The implementation reads a configured map file and caches the last mapping.

Dependencies: requires `WERROR`, `TALLOC_CTX`, and pointer type declarations from Samba headers.

Risks and test signals: caller ownership expectations matter because the returned pointer may become talloc-managed under `mem_ctx` or remain the original string. Tests should verify no caller frees or mutates the replacement incorrectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_os2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_tdb.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing_tdb.c

Purpose: upgrades old NT printing TDB databases through schema versions before full migration to the registry-backed model. It moves records into separate databases, fixes security descriptors, normalizes printer keys, and records the current database version.

Important APIs and functions: `nt_printing_tdb_upgrade()` is the exported entry point. It opens `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`, reads `INFO/version`, and upgrades to version 5. `upgrade_to_version_3()` moves `FORMS/` records to `ntforms.tdb` and `PRINTERS/` plus `SECDESC/` records to `ntprinters.tdb`. `upgrade_to_version_4()` traverses printer security descriptors with `sec_desc_upg_fn()`, remapping generic access masks to printer-specific rights and adding Builtin Administrators owner/group. `upgrade_to_version_5()` lowercases printer and secdesc keys through `normalize_printers_fn()`.

Control flow: missing all three databases is success. Fresh driver database receives version 5. Version 1 or endian-reversed version 1 moves records to split databases and stores version 3. Version 2 or endian-reversed version 2 is normalized to version 3. Version 3 applies security descriptor fixes, version 4 normalizes keys, and unknown versions fail.

State and persistence: mutates TDB files in place using `tdb_store`, `tdb_delete`, and `tdb_store_int32`. Static TDB handles are closed and nulled on all exit paths.

Dependencies and integration: uses `state_path()`, TDB utilities, generated spoolss/security constants, security descriptor marshalling helpers, and global Builtin Administrators SID. It runs before the later TDB-to-winreg migration path.

Risks: upgrades are not transactional across the three TDBs, so interruption can leave mixed versions. `upgrade_to_version_3()` stores moved records before deleting originals. Bad secdesc records are deleted. `normalize_printers_fn()` deletes before storing under the new key, risking data loss on store failure. Tests should use fixture TDBs for versions 1-5, endian-reversed versions, malformed security descriptors, mixed-case keys, and interruption/retry idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_tdb.h -->
# sources/user-network-fs/samba/source3/printing/nt_printing_tdb.h

Purpose: declares the legacy NT printing TDB schema upgrade entry point.

Important API: `bool nt_printing_tdb_upgrade(void);` upgrades old `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb` files to the expected version/layout.

Control flow and integration: initialization or upgrade code calls this before attempting deeper migration to winreg-backed storage. The implementation handles path discovery, TDB opening, version detection, and in-place upgrades.

State and persistence: no header-owned state. The declared function mutates persistent TDB files and version markers.

Dependencies: requires `bool` from Samba includes.

Risks and test signals: callers only receive a boolean, so logs are needed to diagnose exact upgrade failures. Build tests should verify the declaration matches implementation; integration tests should call it before `nt_printing_tdb_migrate()` on legacy fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/pcap.c -->
# sources/user-network-fs/samba/source3/printing/pcap.c

Purpose: central printcap cache coordinator. It builds transient printer lists from backend-specific discovery code and persists the resulting printer inventory into `printer_list.tdb`.

Important APIs and functions: `pcap_cache_add_specific()` appends a printer entry with optional comment/location to a linked list. `pcap_cache_destroy_specific()` frees that list. `pcap_cache_replace()` marks a new reload timestamp, stores each printer into `printer_list`, and removes stale entries. `pcap_cache_reload()` selects the discovery backend based on `lp_printcapname()` and build flags: CUPS, iPrint, SysV/HPUX `lpstat`, AIX qconfig, or standard printcap parsing. `pcap_printer_fn_specific()` iterates a supplied transient list.

Control flow: reload is skipped if `load printers` is disabled or no printcap name is configured. CUPS is special: it performs asynchronous discovery and invokes the post-fill callback itself. Synchronous backends return a `pcap_cache` list; on success, this file replaces the persistent printer list and optionally calls the post-fill callback.

State and persistence: transient cache entries are heap linked-list nodes. Durable state is delegated to `printer_list_mark_reload()`, `printer_list_set_printer()`, and `printer_list_clean_old()`.

Dependencies and integration: integrates with all backend loaders declared in `pcap.h`, loadparm, tevent/messaging for CUPS, and the printer list database. It is the bridge between system printer discovery and Samba share/printer enumeration.

Risks: failed reloads intentionally preserve old persistent entries, which is desirable but can hide stale printers. CUPS asynchronous handling means callers must not assume a successful return means the list is already replaced. `pcap_cache_add_specific()` does not clean up partially allocated fields if later field allocations fail. Tests should cover backend selection, disabled loading, failed reload preserving old entries, successful cleanup of stale entries, and CUPS callback ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/pcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/pcap.h -->
# sources/user-network-fs/samba/source3/printing/pcap.h

Purpose: shared interface for printcap cache management and platform-specific printer discovery backends.

Important APIs and types: forward declares `struct pcap_cache` and exposes cache list operations, `pcap_cache_reload()`, `pcap_printername_ok()`, and backend reload functions for AIX, CUPS, iPrint, SysV/HPUX, and standard printcap files.

Control flow and integration: `pcap.c` uses the backend declarations to select discovery at runtime and build a cache list, while backend files call `pcap_cache_add_specific()` to populate that list. Other printing code can iterate a specific cache with `pcap_printer_fn_specific()`.

State and persistence: the header abstracts `pcap_cache` internals so backends can append/destroy but not inspect representation. Persistent storage is handled indirectly through `pcap_cache_replace()` and `printer_list`.

Dependencies: uses `tevent_context`, `messaging_context`, and `bool` from Samba includes; conditional backend availability is controlled at compile time in implementation files.

Risks and test signals: `pcap_printername_ok()` is declared here but not implemented in `pcap.c`, so consumers depend on another translation unit. Build coverage across feature flag combinations (`HAVE_CUPS`, `HAVE_IPRINT`, `AIX`, `SYSV`, `HPUX`) is important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/pcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_aix.c -->
# sources/user-network-fs/samba/source3/printing/print_aix.c

Purpose: AIX-specific printcap loader that parses qconfig-style files and returns discovered virtual printers through the shared `pcap_cache` interface.

Important API: under `AIX`, `aix_cache_reload(struct pcap_cache **_pcache)` opens `lp_printcapname()`, scans stanzas, skips comments and the `bsh` entry, and adds printer names when a stanza appears to represent a virtual printer. Without `AIX`, the file only defines a dummy symbol.

Control flow: the parser tracks a small state machine. State 0 looks for a top-level `name:` stanza. State 1 scans indented stanza lines; a `backend` line indicates a device, while a `device` line or a new top-level line causes the saved name to be added.

State and persistence: creates a transient `pcap_cache` list. Durable replacement is performed later by `pcap_cache_replace()` in `pcap.c`.

Dependencies and integration: depends on `fgets_slash()`, AIX qconfig formatting, loadparm printcap name, talloc, and shared pcap cache helpers. It is selected by `pcap_cache_reload()` when the configured printcap name contains `/qconfig`.

Risks: parser heuristics are qconfig-specific and may misclassify unusual stanzas. Some paths use `SAFE_FREE(line)` for talloc memory, which is notable beside `TALLOC_FREE(line)` in nearby code. Tests should cover comments, `bsh` skip, backend-only devices, virtual devices, stanza transitions, and open/read failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_aix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_cups.c -->
# sources/user-network-fs/samba/source3/printing/print_cups.c

Purpose: implements the CUPS printing backend and CUPS printer discovery for Samba. It uses IPP over libcups for printer lists, job submission, queue enumeration, job control, and queue pause/resume.

Important APIs and functions: `cups_cache_reload()` starts asynchronous printer discovery. `cups_pcap_load_async()` forks a child, `cups_cache_reload_async()` queries `CUPS_GET_PRINTERS` and `CUPS_GET_CLASSES`, serializes `pcap_data`, and `cups_async_callback()` receives the blob, builds a `pcap_cache`, and persists it through `pcap_cache_replace()`. `cups_job_submit()` sends `IPP_PRINT_JOB` via `cupsDoFileRequest()` and records returned `job-id`. `cups_queue_get()` requests `IPP_GET_JOBS` and `IPP_GET_PRINTER_ATTRIBUTES` and maps IPP states into Samba `print_queue_struct` and `print_status_struct`. Job delete/pause/resume and queue pause/resume issue the corresponding IPP operations.

Control flow: most operations connect using `cups_connect()`, which honors `cups server`, encryption, and connection timeout settings. Requests add charset/language, URIs assembled with libcups, user/job attributes converted to UTF-8, then inspect response status. Discovery is asynchronous to avoid blocking the parent process; CUPS owns the post-cache-fill callback path.

State and persistence: no long-lived printer list is kept here. Discovery results flow through a pipe and are persisted in `printer_list.tdb` by `pcap_cache_replace()`. Job submission may unlink the spool file on success and updates `pjob->sysjob`.

Dependencies and integration: depends on libcups/IPP, tevent, Samba messaging/fork reinit, generated `ndr_printcap`, UTF-8 conversion, loadparm, and the `struct printif cups_printif` vtable.

Risks: async child/pipe handling is failure-prone; `cache_fd_event` prevents overlapping refreshes. URI assembly, encoding conversion, and response parsing must handle malformed CUPS data. Queue get returns partially allocated queues on some error paths. Tests should cover CUPS version compatibility macros, timeout behavior, async success/failure, class and printer discovery, IPP conflict statuses, file unlink on submit success only, queue state mapping, and no-password callback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_cups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_generic.c -->
# sources/user-network-fs/samba/source3/printing/print_generic.c

Purpose: implements command-based printing for generic/non-CUPS backends using configured shell commands for submit, queue listing, job control, and queue control.

Important APIs and functions: `print_run_command()` substitutes local tokens and loadparm variables, optionally applies advanced service/user substitution, then runs the command through `smbrun_no_sanitize()`. `generic_queue_get()` executes an `lpq` command and parses output with `parse_lpq_entry()`. `generic_job_submit()` changes into the spool directory, sanitizes `%J` job-name substitution with `replace_print_cmd_J()`, runs the print command, then re-queries the queue to map Samba job IDs to backend `sysjob` IDs. `generic_job_delete()`, `generic_job_pause()`, `generic_job_resume()`, `generic_queue_pause()`, and `generic_queue_resume()` call configured commands. `generic_printif` exports the backend vtable.

Control flow: submit extracts the spool directory and filename, picks a default job name if absent, detects mixed quoting for `%J`, substitutes `%s/%f/%z/%c`, runs the backend, and restores the original working directory even on failure. Queue parsing allocates one entry per output line and keeps entries accepted by the parser.

State and persistence: relies on external spooler commands for real state. It mutates `pjob->sysjob` and may track jobs as Unix jobs if backend ID lookup fails. No durable state is stored directly here.

Dependencies and integration: depends on smb.conf print commands, substitution helpers, current user info, `smbrun_no_sanitize()`, `fd_lines_load()`, and printing parser/type definitions.

Risks: command execution is inherently sensitive. The `%J` sanitization and CVE-2026-4480 mixed-quoting fallback are key security controls. `chdir()` process-wide state is dangerous if used in a multithreaded context. Tests should cover missing commands, substitution tokens, `%J` unsafe characters, mixed quoting warning/fallback, queue parse matching, directory restoration, and configured command failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_iprint.c -->
# sources/user-network-fs/samba/source3/printing/print_iprint.c

Purpose: implements the Novell iPrint backend using libcups IPP primitives and Novell-specific operations/URIs. It supports printer discovery, job submit/delete/pause/resume, and queue enumeration; queue pause/resume are unsupported without credentials.

Important APIs and functions: `iprint_cache_reload()` sends `OPERATION_NOVELL_LIST_PRINTERS`, then `iprint_cache_add_printer()` queries each returned printer URI and filters out secure or SMB-disabled printers. `iprint_get_server_version()` detects NetWare/Linux server version and affects job time interpretation. `iprint_job_submit()` sends `IPP_PRINT_JOB`, unlinks the spool file on success, and records `job-id`. `iprint_queue_get()` fetches printer status, detects OES SP1 Unix-time behavior, gets jobs, and maps IPP job state into Samba queue entries. Job delete/pause/resume issue IPP operations against `/ipp/<printer>`.

Control flow: all operations connect to `lp_iprint_server()` or `cupsServer()` without encryption and with no password callback. Discovery is synchronous: a successful reload returns a transient `pcap_cache` for `pcap.c` to persist. Queue enumeration first fetches printer attributes, then job attributes.

State and persistence: stores no printer list itself; discovery results become `printer_list.tdb` through the pcap layer. Job operations mutate backend iPrint state and may set `pjob->sysjob`.

Dependencies and integration: depends on libcups, Samba loadparm, shared pcap helpers, printing structs, and the `iprint_printif` vtable. It is compiled only with `HAVE_IPRINT`.

Risks: uses fixed-size URI buffers and older string-copy patterns. Several fields are not UTF-8 converted unlike the CUPS backend. Authentication-required printers are silently ignored during discovery. Server-version time heuristics can misdate jobs if server clocks or version parsing are wrong. Tests should cover secure/SMB-disabled filtering, auth failures, NetWare versus OES SP1 time handling, job-id extraction, unsupported queue pause/resume, and malformed printer URIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_iprint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_standard.c -->
# sources/user-network-fs/samba/source3/printing/print_standard.c

Purpose: parses traditional BSD-style printcap files into the shared `pcap_cache` format.

Important API: `std_pcap_cache_reload(const char *pcap_name, struct pcap_cache **_pcache)` opens the configured file, reads continuation-aware lines with `fgets_slash()`, ignores comments and empty records, splits at the first colon, and selects a printer name/comment from `|`-separated aliases.

Control flow: for each record, the first alias without punctuation becomes the printer name. Aliases containing punctuation are treated as human-readable comments. Each discovered name is added to a transient pcap cache. A warning is emitted once if any name exceeds `MAXPRINTERLEN`.

State and persistence: produces only a transient list. `pcap.c` later persists successful reloads to `printer_list.tdb`.

Dependencies and integration: used as the default fallback by `pcap_cache_reload()` when the printcap name is not one of the special backend selectors. Depends on Samba file utilities and pcap cache helpers.

Risks: parsing is intentionally heuristic and local-file-only; it ignores NIS and more complex printcap semantics. Repeated `TALLOC_FREE(pcap_line)` inside alias parsing is unusual but guarded by talloc behavior. Tests should cover continuations, comments, multiple aliases, comments with punctuation, overlong names, missing colon, unreadable files, and allocation failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_standard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_svid.c -->
# sources/user-network-fs/samba/source3/printing/print_svid.c

Purpose: discovers printers on SysV/XPG4 or HPUX systems by parsing `lpstat` output into the shared pcap cache.

Important API: under `SYSV` or `HPUX`, `sysv_cache_reload(struct pcap_cache **_pcache)` runs `/usr/bin/lpstat -v`, parses lines like `device for name: ...` or `system for name: ...`, and adds each printer name. Without those platform macros, the file defines only a dummy symbol.

Control flow: command arguments are built as a list and executed with `file_lines_ploadv()`. On HPUX, if `lpstat -v` returns no lines, it checks `lpstat -r`; a running scheduler with no printers is treated as success with an empty list. Each output line skips leading words, handles an extra `for`, ignores `remote to`, truncates at `:`, and adds the result.

State and persistence: creates only a transient `pcap_cache` list. Persistent replacement is handled by `pcap.c`.

Dependencies and integration: selected when `lp_printcapname()` is `lpstat` and build flags match. Depends on external `lpstat`, Samba command-output helpers, talloc string lists, and pcap cache functions.

Risks: output parsing is format-dependent and may mis-handle localized `lpstat` output. The HPUX scheduler path assumes `scheduler` is non-null before dereferencing. Tests should cover normal SysV output, HPUX empty-printer scheduler states, malformed lines, `remote to` filtering, command failure, and zero-printer success semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/print_svid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printer_list.c -->
# sources/user-network-fs/samba/source3/printing/printer_list.c

Purpose: persistent database of currently known system printers. It stores printer name, comment, location, and refresh timestamp in `printer_list.tdb` under the lock path.

Important APIs and functions: `printer_list_get_printer()` fetches one printer by case-insensitive key and returns comment/location/refresh time. `printer_list_printername_exists()` checks for a printer key. `printer_list_set_printer()` packs and stores printer data with uppercase key semantics. `printer_list_mark_reload()` stores the global last-refresh timestamp. `printer_list_get_last_refresh()` reads that timestamp. `printer_list_clean_old()` traverses writable records and deletes printer entries older than the last refresh. `printer_list_read_run_fn()` traverses read-only records and invokes a callback for each printer.

Control flow: `get_printer_list_db()` lazily opens `printer_list.tdb` with `db_open()` and caches the `db_context`. Data is packed as high/low 32-bit monotonic time plus three strings. Cleanup compares each entry timestamp with the global timestamp written at reload start.

State and persistence: global static `printerlist_db` is the process cache for the DB handle. Durable records use `PRINTERLIST/PRN/<name>` and `PRINTERLIST/GLOBAL/LAST_REFRESH`.

Dependencies and integration: used by `pcap_cache_replace()` to publish discovery results and by printer enumeration/name checks elsewhere. Depends on dbwrap/TDB, lock paths, monotonic time, and Samba NTSTATUS conventions.

Risks: if reload marks the timestamp and then fails before storing printers, cleanup is only called on successful reload, preserving old entries. Case-insensitive key storage/fetch is important for share-name behavior. Traversal callbacks treat unpack failures as DB corruption. Tests should cover first open failure, case-insensitive lookup, empty comment/location normalization, stale cleanup, timestamp packing on 32/64-bit time, read traversal skipping the global key, and corruption handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printer_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printer_list.h -->
# sources/user-network-fs/samba/source3/printing/printer_list.h

Purpose: public interface for the persistent printer-list database used by pcap reload and printer enumeration code.

Important APIs: declares lookup (`printer_list_get_printer()`), existence (`printer_list_printername_exists()`), store (`printer_list_set_printer()`), refresh timestamp (`printer_list_get_last_refresh()`, `printer_list_mark_reload()`), cleanup (`printer_list_clean_old()`), and traversal (`printer_list_read_run_fn()`) functions.

Control flow and integration: discovery code marks reload, stores all current printers, then cleans old entries. Enumeration code can fetch one printer or run a callback over all entries. The callback receives name, comment, location, and caller-private data.

State and persistence: the implementation persists records in `printer_list.tdb`; this header defines the API boundary without exposing record formats or dbwrap details.

Dependencies: requires `NTSTATUS`, `TALLOC_CTX`, `time_t`, and `bool` from Samba/core headers.

Risks and test signals: typo-only comments aside, the important contract is ownership: returned comment/location strings are allocated on `mem_ctx`, while traversal callback strings are temporary for the callback duration. Tests should verify callers do not retain traversal pointers beyond callback scope and handle non-OK NTSTATUS values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printer_list.h -->
