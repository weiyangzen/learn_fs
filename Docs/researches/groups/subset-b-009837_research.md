# subset-b-009837 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_workgroupdb.c -->
## sources/user-network-fs/samba/source3/nmbd/nmbd_workgroupdb.c

Purpose: maintains nmbd's in-memory NetBIOS workgroup database per subnet. It creates, finds, links, expires, and logs `struct work_record` instances and seeds the local workgroup with Samba's own server records and registered NetBIOS group names.

Important APIs and flow: `create_workgroup_on_subnet()` calls the private `create_workgroup()` initializer and `add_workgroup()` list linker. `find_workgroup_on_subnet()` normalizes names through `name_to_unstring()` before scanning a subnet list. `initiate_myworkgroup_startup()` only acts for `lp_workgroup()`, may request an election when `lp_preferred_master()` and `lp_local_master()` allow it, registers `<00>` and `<1e>` names, and creates local-list-only server records for every `my_netbios_names()` entry. `expire_workgroups_and_servers()` first expires server records, then removes dead non-permanent empty workgroups.

State and persistence: the file owns process-local linked-list state hanging off `struct subnet_record`; no durable database is written here. `workgroup_count` allocates stable-ish tokens, reusing an existing token for the same workgroup name on another subnet. TTL is represented as `death_time = now + ttl * 3`, except `PERMANENT_TTL`.

Dependencies and integration: depends on nmbd subnet/server-list helpers, NetBIOS registration, Samba loadparm settings, name conversion wrappers, and browser election constants. The `work_changed` flag signals later announce/sync work.

Risks: list mutation and raw allocation require careful ordering; a failed server cleanup can prevent freeing a workgroup. Name truncation can alias long workgroup names. Election behavior depends on global loadparm state at creation/startup time.

Test signals: exercise long-name truncation, token reuse across subnets, TTL refresh/removal, preferred-master startup, and dumping at both forced and debug-level paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_workgroupdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/wscript_build -->
## sources/user-network-fs/samba/source3/nmbd/wscript_build

Purpose: declares the Samba3 `nmbd` binary build target and all source files that compose the NetBIOS name service/browser daemon.

Important build API: uses Waf helper `bld.SAMBA3_BINARY('nmbd', ...)`. It conditionally sets `nmbd_cflags` to `-Wno-error=stringop-overflow` when `HAVE_WNO_ERROR_STRINGOP_OVERFLOW` is configured. The source list includes packet handling, browser/election/database modules, WINS proxy/server code, logon processing, async DNS, and `nmbd_workgroupdb.c`.

State and persistence: no runtime state; it affects build graph state by selecting inputs, dependencies, flags, and install path.

Dependencies and integration: links against `talloc`, `tevent`, `smbconf`, `libsmb`, and `CMDLINE_S3`, and installs into `${SBINDIR}`. The broad source list means changes here can include or exclude major nmbd subsystems from the daemon.

Risks: build-file drift can silently omit a daemon module or hide compiler diagnostics globally for the target. The conditional warning downgrade is compiler-feature gated but still broad for all nmbd sources.

Test signals: configure/build should verify `nmbd` is produced, links all named objects, and installs to the expected sbin location. Dependency changes should be validated by a clean build, not just incremental compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm.c -->
## sources/user-network-fs/samba/source3/param/loadparm.c

Purpose: this is the Samba3 configuration engine. It initializes global and share defaults, parses smb.conf/registry configuration, creates and hashes service records, exposes `lp_*` accessors, handles parametric options, loads usershares, tracks config-file changes, and enforces derived security/server-role settings.

Important APIs and types: central state is `Globals`, `sDefault`, `ServicePtrs`, `ServiceHash`, `flags_list`, `file_lists`, and `stored_options`. Public APIs include `loadparm_s3_init_globals()`, `store_lp_set_cmdline()`, `lp_do_parameter()`, `lp_do_section()`, `lp_load_*()` wrappers, `lp_servicenumber()`, `lp_add_home()`, `lp_add_printer()`, `load_usershare_service()`, `load_usershare_shares()`, `parse_usershare_file()`, `lp_parm_*()` parametric readers, canonicalization helpers, dump helpers, and derived getters such as `lp_server_role()`, `lp_security()`, `lp_widelinks()`, and `lp_server_smb_encrypt()`.

Control flow: `lp_load_ex()` resets parse state, initializes globals, parses file or registry backends, processes shares, auto-loads home services, optionally adds IPC/Admin shares, clamps client auth, initializes iconv, enforces AD DC settings, and validates min/max protocol. Section callbacks validate the previous service before adding the next. Registry inclusion is guarded by include depth and only effective from globals.

State and persistence: persistent inputs are smb.conf files, registry smbconf, usershare files, share-security TDB, and system state paths. Runtime state is global and mutable; command-line options are stored and re-applied across reloads. File modification tracking stores original and substituted include paths plus mtimes.

Dependencies and integration: integrates lib/param generated tables, smbconf, dbwrap rbt hash, talloc, printing defaults, idmap parametrics, charset/iconv, auth/credentials, server role logic, usershare ACL/security helpers, and smbd callbacks for in-use service numbers.

Risks: highly stateful global parser with reload paths, recursive include handling, registry/file backend switching, and service deletion while smbd may hold active connections. Usershare loading is security-critical and depends on lstat/open/fstat race checks, directory ownership/sticky-bit policy, path allow/deny lists, ACL parsing, and share count limits. A notable edge in `load_usershare_shares()` counts a successfully loaded usershare only when `process_usershare_file()` returns `0`, although service numbers are generally nonnegative and may not be zero. Parameter flags and synonyms must stay aligned with generated `parm_table`.

Test signals: repeated `lp_load_with_registry_shares()` runs, config reload detection, param canonicalization/value validation, registry include/backend switch, usershare symlink/race/path/ACL cases, AD DC enforced defaults, min/max protocol warnings, and dynamic service cleanup with in-use callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm.h -->
## sources/user-network-fs/samba/source3/param/loadparm.h

Purpose: public Samba3 loadparm header exposing the S3 configuration API to daemons, passdb, smbd, Python helpers, and the shared loadparm bridge.

Important APIs/types: forward declares `loadparm_context`, `loadparm_service`, `files_struct`, `smbd_server_connection`, and security descriptor types. It declares initialization/helpers (`loadparm_s3_init_globals()`, `loadparm_s3_helpers()`), substitution/accessors, parametric readers, service creation/removal/lookup, registry/usershare loaders, config load variants, dump APIs, role/security/protocol derived getters, spoolss/sendfile/mangling controls, widelinks helpers, and `get_globals()`/`get_flags()` style state access through the helper implementation.

State and persistence: the header itself owns no state but exposes functions that operate on process-global configuration, service arrays, usershare state, registry/file backends, and command-line sticky settings.

Dependencies and integration: includes `talloc.h` and `regex.h`; depends on generated enum/type declarations available through wider Samba includes. It is the contract used by `service.c`, `loadparm_ctx.c`, nmbd modules, passdb, and tests.

Risks: because this header publishes many process-global mutators, API additions can lock in global-state assumptions. Callers must respect ownership of returned talloc strings versus const internal pointers. Signature drift must stay synchronized with `loadparm.c` and generated `param_functions.c`.

Test signals: compile coverage across all consumers is the primary signal. ABI/API-sensitive changes should be validated by full source3 builds and by loadparm unit/smoke tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm_ctx.c -->
## sources/user-network-fs/samba/source3/param/loadparm_ctx.c

Purpose: adapts Samba3's global loadparm implementation to the shared/Samba4 `loadparm_context` helper interface.

Important APIs and flow: private wrappers `lp_service_for_s4_ctx()`, `lp_servicebynum_for_s4_ctx()`, and `lp_load_for_s4_ctx()` add short-lived talloc stackframes around S3 calls. Static `s3_fns` fills a `struct loadparm_s3_helpers` with function pointers for parameter pointer lookup, service lookup, loading, command-line storage, dumping, include processing, LDAP debug initialization, section parsing, and global initialization. `loadparm_s3_helpers()` refreshes `helpers->globals` and `helpers->flags` before returning the singleton helper table.

State and persistence: no durable state; it bridges to `loadparm.c` global state. The helper struct is static and mutable only for its state pointers.

Dependencies and integration: includes `lib/param/s3_param.h` and is consumed by `loadparm_init_s3()` callers, including Python module creation and `loadparm.c` setup contexts.

Risks: returns pointers to global services after freeing only the temporary stackframe; correctness relies on those services being globally owned. The singleton helper table is not isolated per context, so concurrent or nested uses share global state.

Test signals: creating S3-backed contexts, loading without reinit, dumping, include callbacks, and Python `get_context()` should exercise this bridge.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/loadparm_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam.c -->
## sources/user-network-fs/samba/source3/param/pyparam.c

Purpose: implements the `samba.samba3.param` Python extension module and exposes a `get_context()` method returning an S3-backed `samba.param.LoadParm` object.

Important APIs and flow: `py_get_context()` obtains `loadparm_s3_helpers()`, calls `loadparm_init_s3()` on a stackframe, then transfers the resulting context to Python with `pytalloc_steal(loadparm_Type, ...)`. `MODULE_INIT_FUNC(param)` creates the module, imports `samba.param`, looks up the `LoadParm` Python type, and stores it in static `loadparm_Type`.

State and persistence: only module-global `loadparm_Type` is stored. The returned context is memory-managed through pytalloc after ownership transfer.

Dependencies and integration: uses Python C API compatibility wrappers, `pytalloc`, `param/loadparm.h`, and shared Samba Python module `samba.param`. Build integration is in `param/wscript_build` as `pys3param`.

Risks: initialization failure paths after `PyImport_ImportModule()` return `NULL` without DECREFing the already created module object, but import-time failure usually aborts module loading. Correctness depends on `samba.param.LoadParm` matching the talloc-wrapped `struct loadparm_context` type.

Test signals: importing `samba.samba3.param`, calling `get_context()`, and using returned LoadParm APIs from Python with Python build enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam.h -->
## sources/user-network-fs/samba/source3/param/pyparam.h

Purpose: small public header for converting Python objects into Samba loadparm contexts.

Important API: declares `_PUBLIC_ struct loadparm_context *lpcfg_from_py_object(TALLOC_CTX *mem_ctx, PyObject *py_obj);`. It includes `param/param.h`, relying on the Python object type being available through surrounding Python includes in consumers.

State and persistence: no state; it declares a conversion/adapter function implemented in `pyparam_util.c`.

Dependencies and integration: used by Python-facing Samba3 utilities that accept an optional `samba.param.LoadParm` object or `None` and need a C `loadparm_context`.

Risks: the header exposes `PyObject` without including Python headers itself, so include order matters. API consumers must honor talloc ownership of returned contexts/references.

Test signals: compile tests for Python extension consumers and runtime conversion of `None`, valid LoadParm, and invalid Python object inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam_util.c -->
## sources/user-network-fs/samba/source3/param/pyparam_util.c

Purpose: converts an optional Python LoadParm object into a C `struct loadparm_context`, creating a default S3-backed context when Python passes `None`.

Important API and flow: `lpcfg_from_py_object()` checks `Py_None`, builds an S3 context with `loadparm_init_s3()`, loads defaults via `lpcfg_load_default()`, and returns it. For non-None objects, it imports `samba.param`, fetches `LoadParm`, verifies `PyObject_TypeCheck()`, and returns a `talloc_reference()` to the embedded context using pytalloc. Invalid types raise `TypeError`.

State and persistence: no persistent state. The returned default context is owned by `mem_ctx`; object-backed contexts are references tied to `mem_ctx`.

Dependencies and integration: uses Python C API, pytalloc, `param/s3_param.h`, `param/loadparm.h`, and `loadparm_s3_helpers()`.

Risks: the local `PyErr_FromString` macro builds a tuple but does not set a Python exception; the default-load failure path may therefore return `NULL` without a conventional exception. Import/type lookup failures are surfaced through Python exceptions. Type compatibility depends on the Python `LoadParm` binding.

Test signals: Python C-extension tests should cover `None`, valid `samba.param.LoadParm`, invalid object, import failure, and default-load failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/pyparam_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/service.c -->
## sources/user-network-fs/samba/source3/param/service.c

Purpose: resolves requested SMB share/service names into loadparm service numbers, including dynamic registry shares, `[homes]`, printers, usershares, default service fallback, and local address filtering.

Important APIs and flow: `find_service()` copies and normalizes the requested name, checks loaded services, tries registry shares before dynamic homes, maps usernames if needed, creates home services through `add_home_service()`, creates printer services when printcap says the name is valid, loads usershares after lowercasing, and finally recurses through `default service` if safe. `load_registry_service()` and `load_registry_shares()` wrap registry-backed loadparm APIs. `lp_allow_local_address()` compares a local socket address against configured `server addresses`.

State and persistence: modifies global loadparm service state by adding homes/printers/usershares and by processing registry shares. It reads passwd/home data, printer lists, usershare files, and registry smbconf through loadparm.

Dependencies and integration: used by smbd connection setup. Depends on loadparm, printer list, username mapping, tsocket normalization, passdb SID lookup includes, and auth utilities.

Risks: order matters: explicit registry shares intentionally beat home-directory autoloading. Default-service recursion must block special services and path traversal. Usershare lookup lowercases the name in place. `lp_allow_local_address()` ignores malformed configured addresses after logging, which can make partial lists permissive only for remaining valid entries.

Test signals: requested share resolution for explicit shares, registry shares, domain-qualified home names, mapped usernames, printers, usershares, default service fallback, invalid snums, and IPv4/IPv6 server address normalization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/test_lp_load.c -->
## sources/user-network-fs/samba/source3/param/test_lp_load.c

Purpose: command-line smoke test that repeatedly calls `lp_load_with_registry_shares()` against a supplied or default config file.

Important APIs and flow: initializes locale and Samba command-line state, suppresses log level through `lpcfg_set_cmdline()`, parses `--count/-c`, chooses a config path, loops `count` times, prints success/error per load, then calls `gfree_loadparm()`.

State and persistence: exercises loadparm global state, registry share loading, config parsing, and cleanup. It does not create persistent output itself, though underlying loadparm may open registry/config databases.

Dependencies and integration: built as non-installed `test_lp_load` binary with `talloc`, `smbconf`, and `CMDLINE_S3` dependencies. Useful for manual or automated regression checks around reload idempotence and cleanup.

Risks: `atoi()` accepts invalid or negative counts silently. The test only checks boolean load success, not service contents, leaks, or exact registry behavior. Some error exits bypass `poptFreeContext()` but process termination makes that low impact.

Test signals: run with real smb.conf, registry-backed config, high `--count`, missing config, and memory checking to catch reload leaks or stale globals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/test_lp_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/util.c -->
## sources/user-network-fs/samba/source3/param/util.c

Purpose: tiny helpers for extracting values from strings shaped like `parameter = value`.

Important APIs: `get_int_param()` returns `atoi()` of the substring after the first `=`, or `0` if absent. `get_string_param()` returns a pointer to the substring after the first `=`, or `NULL` if absent.

State and persistence: stateless; no allocation and no mutation.

Dependencies and integration: declared in `loadparm.h`, built as `PARAM_UTIL`, and likely used by older parameter parsing code that already has raw assignment strings.

Risks: no whitespace trimming, quoting, overflow detection, base handling, or error distinction between missing/invalid and integer zero. Returned string points into caller-owned input.

Test signals: inputs with no equals, empty values, whitespace, negative/large integers, and multiple equals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/wscript_build -->
## sources/user-network-fs/samba/source3/param/wscript_build

Purpose: declares build targets for Samba3 parameter utilities, S3 loadparm bridge, generated prototypes, Python bindings, service resolver, and `test_lp_load`.

Important build API: defines `PARAM_UTIL`, `LOADPARM_CTX`, `s3_param_proto_h` generator from `generate_param.py` and XML parameter metadata, Python module `pys3param`, Python utility subsystem `pyparam3_util`, `param_service`, and non-installed test binary `test_lp_load`.

State and persistence: no runtime state; generates `param_proto.h` during build and controls whether Python extension helpers are built.

Dependencies and integration: ties param code to `talloc`, `smbconf`, `samba-hostconfig`, Python embedding libraries, `USER_UTIL`, and `CMDLINE_S3`. The generated header keeps C prototypes synchronized with XML parameter definitions.

Risks: Python build gating must match consumers; missing generated header inputs can break broad source3 builds. Dependency under-declaration can surface only in clean or differently configured builds.

Test signals: clean Waf configure/build with Python enabled and disabled, generated `param_proto.h` freshness, import of `samba/samba3/param.so`, and execution of `test_lp_load`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/param/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/account_pol.c -->
## sources/user-network-fs/samba/source3/passdb/account_pol.c

Purpose: manages Samba account policy metadata and persistent policy values in `account_policy.tdb`, with short-lived gencache support for LDAP-backed policy reads.

Important APIs and flow: `account_policy_names` maps policy enum values to smb.conf-style names, defaults, descriptions, and LDAP attributes. Lookup helpers expose names, descriptions, defaults, and LDAP attrs. `init_account_policy()` opens or creates the TDB, checks `INFO/version`, runs a transaction to upgrade defaults and seed privilege accounts, and grants all privileges to BUILTIN Administrators when enabled. `account_policy_get()` and `account_policy_set()` fetch/store uint32 values. Cache helpers write/read `ACCT_POL/<name>` values with a 60-second TTL.

State and persistence: static `db` is a process-global dbwrap context. Durable state lives in `state_path("account_policy.tdb")`; cache state lives in gencache and expires after `AP_TTL`.

Dependencies and integration: passdb policy enums, dbwrap, privilege initialization, global SIDs, `lp_enable_privileges()`, gencache, and Samba string-to-integer parsing.

Risks: global db lifetime is lazy and long-lived. Upgrade transaction mixes policy initialization and privilege creation, so failures must cancel cleanly. Default value `(uint32_t)-1` represents never/disabled for some policies and must be interpreted consistently by callers. Cache serialization uses decimal text and must reject parse errors.

Test signals: fresh DB creation, version upgrade/race path, invalid policy enum handling, get/set transaction behavior, cache expiry and parse failure, and privilege seeding with privileges enabled/disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/account_pol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/login_cache.c -->
## sources/user-network-fs/samba/source3/passdb/login_cache.c

Purpose: stores a local TDB cache of selected `struct samu` logon state, mainly bad password counters/timestamps and account-control flags.

Important APIs and flow: `login_cache_init()` lazily opens `cache_path("login_cache.tdb")`; `login_cache_shutdown()` closes it. `login_cache_read()` fetches by `pdb_get_nt_username()`, unpacks `SAM_CACHE_FORMAT` (`dwwd`) into timestamp, 16-bit acct flags, bad count, and bad time. `login_cache_write()` packs current timestamp and entry data and stores it by username. `login_cache_delentry()` deletes by username.

State and persistence: static `TDB_CONTEXT *cache` is process-global. Durable cache is `login_cache.tdb` under Samba cache path, mode 0644. Packed timestamps are 32-bit, then cast to `time_t`.

Dependencies and integration: passdb `struct samu` accessors, util_tdb pack/unpack helpers, TDB logging/opening, Samba allocation wrappers.

Risks: `login_cache_shutdown()` does not set `cache` to NULL after successful close, which can leave a stale pointer if the same process tries to reinitialize. The on-disk format stores account-control as 16-bit and times as 32-bit for compatibility, limiting future range/flag expansion. Usernames are used as raw keys, so rename/case behavior depends on passdb conventions.

Test signals: read missing entry, write/read/delete cycle, shutdown/reinit behavior, 64-bit `time_t` compatibility, malformed TDB record handling, and null/empty username cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/login_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/lookup_sid.c -->
## sources/user-network-fs/samba/source3/passdb/lookup_sid.c

Purpose: canonical Samba3 name/SID/Unix-ID translation layer. It resolves names to SIDs, SIDs to names, SIDs to uid/gid/unixid, uid/gid to SIDs, and primary group SIDs, combining local SAM, BUILTIN/well-known domains, Unix users/groups, passdb, idmap cache, winbind, trusted domains, and fallback Unix SID domains.

Important APIs and flow: `lookup_name_internal()` parses `DOMAIN\name`, UPN, or isolated names, then follows Windows-like lookup order controlled by `LOOKUP_NAME_*` flags. `lookup_name_smbconf_ex()` qualifies smb.conf names against default domain, own SAM, then Unix Users/Groups. `lookup_sids()` groups requested SIDs by domain, handles domain SIDs specially, applies LSA lookup levels, bulk-resolves RIDs with `lookup_rids()`, and returns `lsa_dom_info`/`lsa_name_info`. `lookup_sid()` is a single-SID wrapper. `xid_to_sid()`, `uid_to_sid()`, `gid_to_sid()`, `sids_to_unixids()`, `sid_to_uid()`, and `sid_to_gid()` use direct Unix SID checks, idmap cache, winbind, passdb legacy mapping, and fallback `S-1-22` Unix SIDs. `get_primary_group_sid()` maps a user's primary gid and forces Domain Users if no valid domain group can be proven.

State and persistence: no owned durable state, but it reads secrets for domain SIDs/trusts, passdb mappings, NSS passwd/group, idmap cache, winbind caches, and local/global SID constants. Some paths call `become_root()` for passdb access.

Dependencies and integration: passdb, secrets, idmap cache, winbind client utilities, libwbclient, bitmap tracking, SID utility libraries, loadparm settings (`lp_workgroup()`, separator/default domain), and domain role macros.

Risks: lookup order is compatibility-sensitive and flag-dependent; changing it can alter access-control semantics. Remote winbind status errors sometimes propagate early. Bulk SID mapping uses fixed `LSA_REF_DOMAIN_LIST_MULTIPLIER`, so too many domains fail. `sids_to_unixids()` allocates a bitmap but does not explicitly free it; it is parented under `wbc_sids`, so freeing that parent is relied upon. Primary group fallback deliberately masks mapping failure with Domain Users for operability.

Test signals: RPC-LSALOOKUP level matrix, qualified/unqualified smb.conf names, BUILTIN/well-known/domain SID cases, Unix Users/Groups direct mappings, winbind failure/unknown paths, idmap negative cache fallback, trusted domain lookup, primary group validation, and mixed-domain bulk lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/lookup_sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/lookup_sid.h -->
## sources/user-network-fs/samba/source3/passdb/lookup_sid.h

Purpose: public interface and flag definitions for Samba3 SID/name/Unix-ID lookup operations.

Important APIs/types: defines `LOOKUP_NAME_*` flags controlling isolated, remote, group, no-NSS, builtin, well-known, domain-local, local, and all lookup behavior. `struct lsa_dom_info` and `struct lsa_name_info` model `lookup_sids()` results. Declares `lookup_name()`, `lookup_name_smbconf()`, `lookup_name_smbconf_ex()`, `lookup_sids()`, `lookup_sid()`, uid/gid/xid conversion helpers, `sids_to_unixids()`, and `get_primary_group_sid()`.

State and persistence: no state; functions declared here access passdb, winbind, NSS, idmap cache, and secrets through the implementation.

Dependencies and integration: includes generated LSA NDR types and forward declares passwd/unixid structures. Used by smbd/service/auth/passdb code that needs identity translation.

Risks: flag combinations define security-sensitive lookup scope. `LOOKUP_NAME_GROUP` is explicitly documented as a hack for group-preferring smb.conf contexts. Callers must allocate result arrays on a valid talloc context and handle `SID_NAME_UNKNOWN` separately from transport/status failure.

Test signals: compile coverage and behavioral tests for every flag combination exposed to auth/config/RPC callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/lookup_sid.h -->
