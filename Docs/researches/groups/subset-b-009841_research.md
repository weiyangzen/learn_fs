# subset-b-009841 research

Grouped research for Samba passdb secrets/Python bindings and source3 printing load, queue parsing, notification, and NT printer driver support. Each section preserves the source path and uses reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/py_passdb.c -->
# sources/user-network-fs/samba/source3/passdb/py_passdb.c

## Purpose
`py_passdb.c` is the C Python extension for Samba's source3 password database APIs. It exposes `passdb.Samu`, `passdb.Groupmap`, and `passdb.PDB` Python types, plus module helpers for loading Samba configuration, selecting an alternate secrets directory, retrieving domain SIDs, and reinitializing the static passdb backend. The module is a thin but broad bridge from Python into `struct samu`, `GROUP_MAP`, `struct pdb_methods`, secrets, SID/GUID, idmap, account policy, alias, trust-domain, and LSA secret operations.

## Important APIs, types, and functions
- `PySamu` wraps `struct samu` and provides generated get/set properties for account timestamps, strings, SIDs, password hashes/history/plaintext password, account control flags, logon hours, counters, country code, and code page. Setters use the corresponding `pdb_set_*` functions with `PDB_CHANGED`.
- `PyGroupmap` wraps `GROUP_MAP` with properties for `gid`, `sid`, `sid_name_use`, `nt_name`, and `comment`.
- `PyPDB` wraps a `struct pdb_methods` backend instance created by `make_pdb_method_name(url)`.
- `py_pdb_methods` exposes account CRUD (`getsampwnam`, `getsampwsid`, `create_user`, `delete_user`, `add_sam_account`, `update_sam_account`, `rename_sam_account`), group mapping and membership APIs, alias APIs, account policy get/set, id/SID mapping, RID allocation, trusted-domain password APIs, full trusted-domain object APIs, and generic LSA secret get/set/delete.
- Module-level functions include `get_backends`, `set_smb_config`, `set_secrets_dir`, `reload_static_pdb`, `get_global_sam_sid`, and `get_domain_sid`.
- `MODULE_INIT_FUNC(passdb)` readies pytalloc-backed types, creates the module and `passdb.error`, registers the types, and imports `dom_sid`, `security.descriptor`, and `misc.GUID` Python type objects used for type checking and object construction.

## Control flow
Object creation is simple: `Samu()` allocates a new `struct samu`, `Groupmap()` allocates a zeroed `GROUP_MAP`, and `PDB(url)` loads a passdb backend by name. Most `PDB` methods parse Python arguments, obtain the wrapped `pdb_methods` pointer, call one backend method, and either return converted Python data or raise `passdb.error` with the NTSTATUS value and friendly message. Search/enumeration APIs use backend search iterators and convert entries into Python dictionaries/lists. SID and security descriptor arguments are accepted as pytalloc objects of imported Samba Python types. Trust and LSA secret methods marshal between Python dictionaries and Samba's `secrets.c`/`secrets_lsa.c` data structures.

For `Samu` and `Groupmap`, property accessors translate between Python scalar/string/bytes/SID objects and the underlying C structures. Password fields and logon hours are binary-sensitive paths; they copy bytes into passdb setters rather than treating all values as null-terminated text. Module-level setup functions mutate global Samba process state: `set_smb_config` loads global loadparm state, `set_secrets_dir` initializes `secrets.tdb` at an explicit private directory, and `reload_static_pdb` calls `initialize_password_db(true, NULL)`.

## State and persistence behavior
The Python objects are pytalloc wrappers around Samba C allocations, so lifetime depends on talloc ownership transferred to Python. Mutating a `Samu` property only changes the in-memory `struct samu`; persistence happens when callers pass it to `add_sam_account`, `update_sam_account`, or other backend methods. `PDB` operations persist through the selected passdb backend, which may be TDB, LDAP, DSDB, or another compiled backend. Trust-domain passwords and LSA secrets persist through `secrets.tdb`. Configuration and static passdb reload calls affect process-global Samba state and can change how later `PDB` objects and module helpers behave.

## Dependencies and integration points
This file depends on Python C API compatibility wrappers, pytalloc, source3 passdb APIs, `secrets.h`, idmap, Samba SID/security/GUID Python modules, loadparm, and generated NDR/RPC structures. It is built as `samba/samba3/passdb.so` by `wscript_build`. Python Samba tooling that needs legacy source3 account database operations imports this extension instead of reimplementing passdb logic.

## Risks and edge cases
- It exposes high-privilege account, password hash, trust password, and secret operations to Python; caller authorization and filesystem permissions around the selected backend and `secrets.tdb` are critical.
- Many methods pass through raw backend status. Python callers must handle `passdb.error`; otherwise partial account or group mutations can be left in place.
- The module mutates global loadparm/passdb/secrets state, so test suites or long-lived Python processes can affect subsequent operations by calling `set_smb_config`, `set_secrets_dir`, or `reload_static_pdb`.
- Type conversions rely on imported Samba Python type objects and pytalloc pointers. Incorrect type checks or lifetime mistakes can become C-level crashes rather than Python exceptions.
- Binary fields such as hashes, password history, logon hours, trust auth blobs, and LSA secret blobs must not be treated as UTF-8 text by callers.

## Test signals
Useful tests import `samba.samba3.passdb`, instantiate each exported type, verify all `Samu` and `Groupmap` properties round-trip, exercise `PDB("tdbsam")` or a test backend for account/group/alias CRUD, and use a temporary private directory to validate `set_secrets_dir`, trusted-domain password methods, and LSA secret get/set/delete. Build-time signals include successful compilation of the Python extension and import-time resolution of `samba.dcerpc.security.dom_sid`, `descriptor`, and `samba.dcerpc.misc.GUID`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/py_passdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/secrets.c -->
# sources/user-network-fs/samba/source3/passdb/secrets.c

## Purpose
`secrets.c` implements source3 accessors for Samba's private `secrets.tdb` database. This database stores generated/private local state such as machine and domain trust material, LDAP bind passwords, AFS keys, fallback IPC credentials, generic owner/key secrets, and other sensitive blobs used by passdb and authentication code.

## Important APIs, types, and functions
- `secrets_init_path(private_dir)`, `secrets_init()`, `secrets_db_ctx()`, and `secrets_shutdown()` manage the singleton `struct db_context *db_ctx` for `secrets.tdb`.
- `secrets_fetch`, `secrets_store`, `secrets_delete_entry`, and `secrets_delete` are generic key/value helpers over dbwrap/TDB.
- `secrets_store_creds` stores module-level IPC auth username/domain/password records from `cli_credentials`.
- `secrets_fetch_trusted_domain_password`, `secrets_store_trusted_domain_password`, and `trusted_domain_password_delete` marshal `TRUSTED_DOM_PASS` NDR blobs under uppercased domain-trust keys.
- `secrets_store_ldap_pw` and `fetch_ldap_pw` manage LDAP admin bind passwords.
- `secrets_store_afs_keyfile` and `secrets_fetch_afs_key` store and retrieve AFS keyfile data.
- `secrets_fetch_ipc_userpass`, `secrets_store_generic`, and `secrets_fetch_generic` handle fallback IPC credentials and namespaced generic secrets.

## Control flow
All public operations first ensure the database is opened, normally at `lp_private_dir()/secrets.tdb` or an explicit path supplied by `secrets_init_path`. Fetching reads a TDB record into a temporary dbwrap buffer, duplicates it with `smb_memdup`, burns and frees the dbwrap buffer, and returns a malloc-style pointer for the caller to free. Storing uses `dbwrap_trans_store` with `TDB_REPLACE`; deletion uses transactional delete after an existence check for the idempotent `secrets_delete`.

Typed helpers build stable key strings and serialize/deserialize domain-specific records. Trusted-domain passwords are encoded with generated NDR push/pull functions and include domain name, modification time, plaintext trust password, and domain SID. LDAP and generic secrets use string keys and null-terminated string values. AFS retrieval validates exact structure size and key count before returning the highest-index key after network-to-host conversion.

## State and persistence behavior
Persistent state is the on-disk `secrets.tdb`, opened mode `0600` with `O_RDWR|O_CREAT`. The `db_ctx` singleton remains live until `secrets_shutdown`; once initialized, later `secrets_init_path` calls return true without reopening to a new path. Sensitive fetched buffers are explicitly burned where this file knows their size, and some returned talloc data is marked with `talloc_keep_secret` after NDR unmarshalling.

## Dependencies and integration points
The file depends on dbwrap/tdb, loadparm private-dir configuration, generated `ndr_secrets`, `libcli_auth`, credentials APIs, SID/security helpers, and Samba memory-scrubbing utilities. It underpins `secrets_lsa.c`, `py_passdb.c`, machine trust and domain trust management, LDAP passdb support, and code needing fallback IPC credentials.

## Risks and edge cases
- The singleton database path is sticky after first initialization; tests that switch private directories must control process state or call shutdown before reopening.
- Callers own returned buffers and must free/burn them correctly. Missing scrubbing outside this file can leak secret material.
- `secrets_fetch_trusted_domain_password` returns duplicated plaintext password and optional SID/time; partial allocation failure can leave callers without all requested fields.
- AFS key retrieval assumes at least one key after validating only max count; malformed zero-key keyfiles would index `entry[i-1]`.
- Key construction for generic and LDAP secrets uses raw owner/key/DN strings, so callers must avoid collisions or unexpected separators.

## Test signals
Tests should use a temporary private directory with a fresh `secrets.tdb`, verify generic store/fetch/delete and idempotent delete, round-trip trusted-domain password NDR data including SID and modification time, reject malformed LDAP password records without null termination, and validate secrets are not reopened to a different path after the singleton is initialized.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/secrets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/secrets_lsa.c -->
# sources/user-network-fs/samba/source3/passdb/secrets_lsa.c

## Purpose
`secrets_lsa.c` layers Windows LSA secret semantics on top of `secrets.tdb`. It stores current and old secret blobs, last-change timestamps, and optional security descriptors under `SECRETS/LSA/<NAME>` keys encoded as generated `lsa_secret` NDR records.

## Important APIs, types, and functions
- `lsa_secret_key(mem_ctx, secret_name)` uppercases and formats the storage key.
- `lsa_secret_get_common` fetches, NDR-decodes, scrubs the raw blob, and marks current/old secret data as sensitive in talloc.
- `lsa_secret_get` returns optional current secret, current timestamp, old secret, old timestamp, and security descriptor to callers.
- `lsa_secret_set_common` updates the old/current secret slots and timestamps, encodes the full `lsa_secret`, and stores it with `secrets_store`.
- `lsa_secret_set` loads an existing secret when present, then writes the requested current/old/security descriptor state.
- `lsa_secret_delete` verifies the secret exists before deleting the backing key.

## Control flow
Reads build the uppercased key, use `secrets_fetch`, map missing records to `NT_STATUS_OBJECT_NAME_NOT_FOUND`, decode with `ndr_pull_lsa_secret`, and expose requested fields by shallow-copying DATA_BLOB structs owned by the caller's talloc context. Writes attempt to load the previous record. If no explicit old secret is supplied, the previous current secret becomes old and keeps its prior last-change timestamp; otherwise the supplied old secret gets the current timestamp. The supplied current secret, or null current value, also receives a fresh timestamp. The resulting structure is NDR-pushed and stored back in `secrets.tdb`.

## State and persistence behavior
Persistent state is a single NDR blob per LSA secret name in `secrets.tdb`. Names are normalized to uppercase in the key. The set path preserves old-secret history automatically unless the caller overrides it. Secret data blobs are talloc-owned after decoding and marked secret for safer diagnostics/memory handling; the raw fetched blob is burned and freed.

## Dependencies and integration points
This file depends directly on `secrets.c` generic store/fetch/delete and generated NDR definitions in `ndr_secrets.h`. It is used by the Python passdb extension and any source3 code that needs LSA-style secrets rather than simple string/blob keys.

## Risks and edge cases
- Returned `DATA_BLOB`s are shallow views into the decoded `struct lsa_secret`; callers must keep the talloc context alive.
- `lsa_secret_set` treats missing existing records as creation, but propagates other decode/fetch errors; corrupt records block updates until repaired or deleted.
- Security descriptors are stored when supplied but this layer does not itself enforce access checks.
- `lsa_secret_delete` requires the record to be readable first; a corrupt but present blob may fail deletion through this API.

## Test signals
Tests should create, update, read, and delete a secret in a temporary secrets directory, verifying current/old transitions and timestamp changes. Corrupt-record tests should confirm get/set/delete status mapping. Python binding tests through `passdb.PDB.get_secret`, `set_secret`, and `delete_secret` are useful integration signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/secrets_lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/wscript_build -->
# sources/user-network-fs/samba/source3/passdb/wscript_build

## Purpose
`wscript_build` declares the source3 passdb build targets for Samba's waf build system. It wires passdb backend modules and the Python passdb extension into the correct subsystems with static/dynamic and feature gating.

## Important APIs, types, and functions
- `bld.SAMBA3_MODULE('pdb_tdbsam', ...)` builds the TDB passdb backend from `pdb_tdb.c`.
- `bld.SAMBA3_MODULE('pdb_ldapsam', ...)` builds LDAP/NDS passdb support from `pdb_ldap.c pdb_nds.c`, gated by module enablement and `HAVE_LDAP`.
- `bld.SAMBA3_MODULE('pdb_smbpasswd', ...)` builds the smbpasswd backend.
- `bld.SAMBA3_MODULE('pdb_samba_dsdb', ...)` builds the AD DC DSDB-backed passdb module only when AD DC build support is enabled.
- `bld.SAMBA3_PYTHON('pypassdb', ...)` builds `py_passdb.c` as `samba/samba3/passdb.so`, depending on `pdb` and public Python embedding/talloc/util dependencies.

## Control flow
The file is evaluated by waf during configuration/build. Each module declaration sets source files, subsystem, dependencies, init function policy, static-module behavior, and enablement conditions. The Python target queries embedded Python library names for `pyrpc_util` and `pytalloc-util`, then declares the extension real name.

## State and persistence behavior
This file does not store runtime state. It controls compiled artifacts and therefore determines which passdb backends and Python bindings are available in the installed Samba tree. Build-time feature flags such as LDAP and AD DC support affect the presence of modules.

## Dependencies and integration points
The declarations tie source3 passdb code to `samba-util`, dbwrap/TDB, LDAP helper libraries, `LIBCLI_AUTH`, `IDMAP`, `samdb`, `pdb`, Python embedding utilities, and pytalloc. `py_passdb.c` depends on this file for being packaged at the Python import path expected by Samba tooling.

## Risks and edge cases
- Feature gating must stay aligned with source dependencies; enabling LDAP or DSDB modules without required libraries would break builds.
- Static module decisions affect runtime backend discovery through passdb initialization and `passdb.get_backends()`.
- Python extension dependency names come from `pyembed_libname`; mismatches can cause link or import failures even when C passdb modules build.

## Test signals
Build tests should cover configurations with and without LDAP and AD DC support, static and shared passdb modules, and importing `samba.samba3.passdb` from the built tree. Runtime `passdb.get_backends()` should reflect enabled modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/load.c -->
# sources/user-network-fs/samba/source3/printing/load.c

## Purpose
`load.c` loads printer services from Samba's pre-populated printer capability/cache data into loadparm service entries. It bridges the printer list cache and `[printers]` share configuration so automatic printer shares become available.

## Important APIs, types, and functions
- `load_printers()` is the public entry point. It checks the pcap/printer cache, loads configured printer services, and adds cached printers.
- `pcap_cache_loaded(time_t *_last_change)` reports whether the printer cache has a last-refresh timestamp and optionally returns it.
- `add_auto_printers()` handles the `auto services` list by adding named printers that exist in the printer list and are not already configured as services.

## Control flow
`load_printers` first refuses work if `pcap_cache_loaded(NULL)` fails. It then calls `add_auto_printers`, calls `lp_load_printers`, checks that a `[printers]` service exists, and finally iterates cached printer names with `printer_list_read_run_fn(lp_add_one_printer, NULL)`. `add_auto_printers` ensures `[printers]` exists, including a registry-service fallback, copies the configured auto-service string, tokenizes it by Samba list separators, skips already configured services, and adds entries only for names present in the printer list.

## State and persistence behavior
The file does not persist printer data directly. It mutates in-memory loadparm service state by calling `lp_add_printer` and `lp_add_one_printer`. The cache freshness signal comes from `printer_list_get_last_refresh`, which is maintained by the printer list subsystem.

## Dependencies and integration points
It depends on `printing/pcap.h`, `printing/printer_list.h`, `printing/load.h`, and loadparm. It integrates with registry service processing, `lp_load_printers`, and consumers that need print shares loaded before serving SMB/RPC printer operations.

## Risks and edge cases
- If the pcap/printer cache has not been refreshed, no printers are loaded.
- Without `[printers]`, automatic pcap additions are intentionally skipped.
- Auto-services are tokenized with `strtok_r` on a duplicated string; unusual separator or printer-name characters can affect parsing.
- Failures in `printer_list_read_run_fn` are logged but do not abort the process.

## Test signals
Tests should seed a printer list cache, configure `[printers]` and `auto services`, call `load_printers`, and assert expected loadparm services appear. Negative tests should cover missing pcap refresh, missing `[printers]`, and pre-existing service names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/load.h -->
# sources/user-network-fs/samba/source3/printing/load.h

## Purpose
`load.h` is the public header for printer-loading helpers implemented in `load.c`.

## Important APIs, types, and functions
- `bool pcap_cache_loaded(time_t *_last_change);` checks whether the printer cache is available and can return its last refresh time.
- `void load_printers(void);` loads automatic and cached printer services into Samba's loadparm state.

## Control flow
The header only declares functions. Callers include it when they need to trigger printer service loading or inspect pcap cache state.

## State and persistence behavior
No state is stored in the header. The declared functions interact with loadparm and printer-list state in `load.c`.

## Dependencies and integration points
The prototypes expose the printing load component to source3 code. Including files must already have Samba's common types available for `bool` and `time_t`.

## Risks and edge cases
The header is minimal; main risk is ABI/API drift if `load.c` signatures change without updating this declaration or generated include users.

## Test signals
Compile coverage is the primary signal: any caller using stale declarations will fail to build. Runtime behavior is covered by `load.c` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/lpq_parse.c -->
# sources/user-network-fs/samba/source3/printing/lpq_parse.c

## Purpose
`lpq_parse.c` parses textual queue output from multiple Unix and network printing systems into Samba `print_queue_struct` and `print_status_struct` values. It normalizes vendor-specific `lpq`/`lpstat` formats so the rest of Samba can reason about job id, owner, file/document name, size, priority, time, and status consistently.

## Important APIs, types, and functions
- `parse_lpq_entry(printing_type, line, buf, status, first)` is the exported dispatcher.
- Format-specific parsers include `parse_lpq_bsd`, `parse_lpq_lprng`, `parse_lpq_aix`, `parse_lpq_hpux`, `parse_lpq_sysv`, `parse_lpq_qnx`, `parse_lpq_plp`, `parse_lpq_nt`, and `parse_lpq_os2`.
- Developer builds add `parse_lpq_vlp` for virtual/test printer output.
- `EntryTime` parses month/day/time fields and adjusts previous-year jobs; `LPRng_time` parses LPRng time strings in short and full-date forms.
- Status keyword arrays classify non-job lines as OK, stopped, or error messages.

## Control flow
`parse_lpq_entry` switches on `enum printing_types`, invokes one parser, strips the newline from the input line, and if no job was parsed, optionally treats the line as a printer status line by lowercasing it and matching severity keyword sets. Most parsers tokenize with `next_token_talloc` or `strtok_r`, validate minimum token counts and numeric columns, then fill `print_queue_struct`. Some formats need special handling: HPUX stores static header-line state and returns a job only after a following indented file line; NT and OS/2 parse fixed-width output; SYSV rewrites only the last dash before the job id; LPRng removes `@host` from owner names.

## State and persistence behavior
The parser has little persistent state, but `parse_lpq_hpux` uses static variables to carry the current header line, user, job id, priority, time, status, and base priority across calls. Other parsers are stateless aside from mutating the input line in place for tokenization and normalization. Output state is written into caller-provided `print_queue_struct` and `print_status_struct`.

## Dependencies and integration points
The file depends on `printing.h` for queue/status structures, print status constants, and `enum printing_types`, plus Samba string wrappers and talloc tokenization helpers. It is used by printing backends that execute platform-specific queue commands and need to populate Samba's print queue cache.

## Risks and edge cases
- Parsers mutate the input line, so callers must pass writable buffers.
- Fixed-width NT/OS2 parsers reject lines with unexpected lengths, making them sensitive to localization or server version changes.
- The HPUX parser's static state can be wrong if multiple queues are parsed interleaved in one process.
- Many sizes are parsed with `atoi` into integer fields and may truncate or overflow on very large jobs.
- Status-line matching uses substring checks after lowercasing and may misclassify localized messages or lines containing coincidental keywords.
- Filename handling often collapses paths to basenames or substitutes `STDIN`, which can lose document detail.

## Test signals
Good tests feed representative queue outputs for each `PRINT_*` type, including header lines, malformed numeric fields, filenames with spaces, standard-input markers, LPRng host-qualified users, HPUX two-line jobs, status-only lines, and developer VLP records. Regression tests should verify `print_status_struct` severity does not downgrade once an error has been observed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/lpq_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/notify.c -->
# sources/user-network-fs/samba/source3/printing/notify.c

## Purpose
`notify.c` batches and sends spoolss printer/job change notifications to interested Samba processes. It queues `spoolss_notify_msg` records, coalesces noisy job progress updates, serializes messages, finds subscribed PIDs from per-printer print databases, and sends low-priority messaging events.

## Important APIs, types, and functions
- `print_queue_snum(qname)` maps a printable share name to a loadparm service number.
- `print_notify_send_messages(msg_ctx, timeout)` flushes the pending global queue by printer.
- `notify_printer_status*`, `notify_job_status*`, `notify_job_total_bytes`, `notify_job_total_pages`, `notify_job_username`, `notify_job_name`, `notify_job_submitted`, and printer metadata helpers enqueue typed field notifications.
- `send_spoolss_notify2_msg` appends to the pending queue and schedules a one-second tevent timer.
- `flatten_message` serializes a queued message with tdb packing.
- `print_notify_pid_list` reads subscribed PIDs from the printer TDB under `NOTIFY_PID_LIST_KEY`.

## Control flow
Public notification helpers first respect `lp_disable_spoolss`, create the global send talloc context, allocate/fill a `spoolss_notify_msg`, and pass it to `send_spoolss_notify2_msg`. That function replaces existing queued `TOTAL_BYTES`/`TOTAL_PAGES` messages for the same printer/job/field when the queue is still below 100 messages, reducing client flicker, otherwise appends a deep-copied message to `notify_queue_head`. If an event context is supplied, it schedules a one-second timer. The timer switches to root and calls `print_notify_send_messages`, which repeatedly groups messages by printer, serializes a count-prefixed buffer, removes sent messages from the queue, reads interested PIDs, and sends `MSG_PRINTER_NOTIFY2 | MSG_FLAG_LOWPRIORITY` to each PID until an optional timeout expires.

## State and persistence behavior
Runtime state is held in global `send_ctx`, `num_messages`, `notify_queue_head`, and `notify_event`. The subscription list is persisted outside this file in per-printer print TDB records. After a flush, child allocations under `send_ctx` are freed and `num_messages` resets to zero.

## Dependencies and integration points
The file depends on source3 printing structures, generated spoolss constants, messaging, tevent, loadparm, tdb packing/unpacking helpers, and print database helpers such as `get_print_db_byname` and `get_printer_notify_pid_list`. It is called by print queue/job update paths and feeds clients waiting on spoolss change notifications.

## Risks and edge cases
- Global queue state is process-local and not protected by explicit locks; it assumes normal smbd event-loop serialization.
- If allocation fails during flattening or batching, queued children can be freed and notifications dropped.
- `print_notify_pid_list` assumes PID records are 8-byte entries and reads only the low 32-bit value with `IVAL`, which is sensitive to platform PID size/record format.
- Message send results are not checked, so dead subscribers are tolerated but not pruned here.
- A zero or missing event context means queued messages require an explicit flush call.

## Test signals
Tests should enqueue value and buffer notifications, verify coalescing for job byte/page updates, serialize multiple messages for one printer, simulate PID-list records in a print TDB, and confirm `lp_disable_spoolss` suppresses enqueueing. Event-loop tests can assert the one-second timer flushes and clears queue state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/notify.h -->
# sources/user-network-fs/samba/source3/printing/notify.h

## Purpose
`notify.h` declares the source3 printing notification API implemented by `notify.c`.

## Important APIs, types, and functions
- `print_queue_snum` resolves printable queue names to service numbers.
- `print_notify_send_messages` flushes pending queued notifications.
- Printer notification helpers cover status, driver, comment, share name, printer name, port, location, separator file, and generic by-name field updates.
- Job notification helpers cover status, total bytes, total pages, username, document name, and submitted time.

## Control flow
The header is declarative. Callers include it to enqueue spoolss notifications while supplying a `tevent_context`, `messaging_context`, printer/share identifier, job id, and field-specific value.

## State and persistence behavior
No state lives in the header. The declared functions mutate process-local notification queue state and interact with printer TDB subscriber state in `notify.c`.

## Dependencies and integration points
The API exposes notification functions to printing, spoolss, and queue-processing code. Including code needs declarations for `struct tevent_context`, `struct messaging_context`, `time_t`, and fixed-width integer types from Samba common headers.

## Risks and edge cases
The API mixes service-number and printer-name entry points. Callers must choose the correct helper and pass valid share names/job ids so clients receive notifications on the expected printer.

## Test signals
Compile coverage catches signature drift. Behavioral tests belong with `notify.c` and should exercise every declared helper at least enough to verify field type, id, and payload length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing.c -->
# sources/user-network-fs/samba/source3/printing/nt_printing.c

## Purpose
`nt_printing.c` implements major source3 NT spoolss printer support: initialization of print driver directories/databases, driver architecture/version cleanup, PE/NE version parsing, driver file promotion into `print$` download directories, driver/file in-use checks, driver file deletion, printer access checks, print time checks, and winreg-backed printer add/remove helpers.

## Important APIs, types, and functions
- `nt_printing_init` creates required print driver directories, upgrades printing TDBs, registers driver-upgrade forwarding, and checks published printers in ADS mode.
- `get_short_archi` maps Windows architecture strings to Samba short architecture directory names via `archi_table`.
- `get_file_version`, `handle_pe_file`, and `handle_ne_file` parse DOS/PE/NE executable version resources from uploaded driver files.
- `file_version_is_newer` compares old/new driver files by version resource when available, otherwise by modification time.
- `clean_up_driver_struct` and `clean_up_driver_struct_level` normalize spoolss add-driver structures, strip client paths, handle `APD_COPY_FROM_DIRECTORY`, validate architecture, and determine `cversion`.
- `move_driver_to_download_area` and `move_driver_file_to_download_area` copy uploaded driver files into `print$/<arch>/<version>/`.
- `printer_driver_in_use` and `printer_driver_files_in_use` query winreg driver/printer data to decide whether a driver or its files can be removed.
- `delete_driver_files` unlinks unused files from the print driver download directory.
- `print_access_check`, `print_time_access_check`, `nt_printer_remove`, and `nt_printer_add` enforce printer/job permissions, schedule windows, and maintain winreg printer records.

## Control flow
Initialization starts by ensuring `print$` architecture directories, package-aware subdirectories, color directory, and state `DriverStore` directories exist. It then upgrades printing TDB state, registers `MSG_PRINTER_DRVUPGRADE` forwarding to the background queue daemon, and checks AD-published printers when in ADS security mode.

Driver installation first cleans the submitted spoolss structure. Paths such as `c:\...`, `.\...`, or UNC upload paths are reduced to basenames; a temporary driver directory is extracted for copy-from-directory installs; architecture strings are mapped; and `get_correct_cversion` opens the uploaded driver file as the requesting session to infer kernel/user-mode driver version. `move_driver_to_download_area` then opens a connection to `print$`, becomes the session user, creates the target `<short_arch>/<version>` directory, and copies the driver, data, config, help, and unique dependent files when `file_version_is_newer` says the uploaded copy should replace the current one.

Version detection reads DOS headers, seeks to PE/NE headers, scans PE section tables for `.rsrc`, scans version-resource signatures, and extracts major/minor fields. If version data is unavailable, file replacement falls back to mtime comparison. Driver deletion first requires external checks that the driver and files are not in use, then opens `print$` as the session user and unlinks each referenced file. Access checks short-circuit root and `SE_PRINT_OPERATOR`, otherwise fetch printer security descriptors from winreg, map generic rights, derive child job descriptors when needed, and call `se_access_check`.

## State and persistence behavior
Persistent state is spread across filesystem directories under `print$`, Samba state `DriverStore`, printing TDB upgrade state, winreg printer/driver records, and AD-published printer metadata. This file mutates filesystem contents by creating directories, copying driver files, and deleting files. It mutates messaging registrations at runtime and reads printer security/time windows from winreg-backed printer info.

## Dependencies and integration points
The file depends on printing TDB helpers, queue process messaging, generated spoolss/netlogon structures, spoolss server utilities, secrets/machine SID/security helpers, smbd connection/VFS APIs, auth/session code, winreg spoolss client helpers, global messaging contexts, and time utilities. It is central to RPC spoolss add/delete printer driver flows and to SMB access to the `print$` share.

## Risks and edge cases
- PE/NE parsing handles untrusted uploaded driver files and uses many offset/size calculations; integer wrap checks are present but this remains a sensitive parser.
- Driver installation can leave partial updates if one file is copied and a later file fails, as noted by an in-code comment.
- `move_driver_file_to_download_area` takes a `uint32_t version` parameter but checks `version == -1`; this sentinel is awkward and easy to misuse.
- Version fallback to mtime can install older binary content if timestamps are misleading.
- Deletion ignores individual unlink errors and returns true once attempted, so callers may need independent cleanup verification.
- Access checks depend on winreg security descriptor retrieval; failure maps to memory/error outcomes rather than nuanced authorization status.
- Operations that become the user and operate through VFS must preserve correct impersonation cleanup on every error path.

## Test signals
Important tests include initialization with and without a `print$` share, architecture mapping for all entries, PE/NE version extraction on fixtures with and without version info, replacement decisions by version and mtime, add-driver cleanup for level 3/6/8 and `APD_COPY_FROM_DIRECTORY`, partial-copy error injection, driver/file in-use checks against mocked winreg data, delete attempts on shared dependent files, root/print-operator/DACL access checks, and time-window allow/deny behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/nt_printing.c -->
