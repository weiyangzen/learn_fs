# Research: subset-b-009929

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging.c -->
# sources/user-network-fs/samba/source4/lib/messaging/messaging.c

`messaging.c` is the main source4 internal messaging and IRPC implementation. It builds an `imessaging_context` around a tevent loop, a datagram socket reference, dispatch tables, temporary message IDs, pending IRPC calls, and a `server_id_db` name registry. Public entry points include `imessaging_init()`, `imessaging_init_discard_incoming()`, `imessaging_client_init()`, `imessaging_register()`, `imessaging_register_tmp()`, `imessaging_deregister()`, `imessaging_reinit_all()`, `imessaging_process_cleanup()`, `irpc_register()`, `irpc_add_name()`, `irpc_remove_name()`, `irpc_all_servers()`, `irpc_binding_handle()`, and `irpc_binding_handle_by_name()`.

Control flow starts in `imessaging_init_internal()`, which creates `msg.sock` and `msg.lock`, opens `messaging_dgm_ref()`, initializes IDR tables, registers built-in handlers, and registers the IRPC uptime call. Incoming datagrams are parsed by `imessaging_dgm_recv()`, optionally rescheduled onto the owning event context, then dispatched to all handlers for the message type. IRPC requests decode `irpc_header`, find registered NDR interface handlers, invoke them, and either reply immediately, defer reply ownership, or suppress replies. IRPC client calls allocate a call ID, send an NDR packet through `imessaging_send()`, and complete a `dcerpc_binding_handle` request when the reply arrives.

State persists in process memory, filesystem socket/lock directories, and the `server_id_db` names database. Fork handling resets outstanding requests, replaces the datagram reference, updates pid, and reinitializes name state. Risks include silent drops for unregistered handlers, dropped remote-cluster sends in source4, listener reference miscounts around pending IRPC calls, and security-sensitive built-in messages such as debug-level changes. Test signals come from `tests/messaging.c`, `tests/irpc.c`, fork/reinit tests, timeout tests, and multi-context broadcast/free-during-callback cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging.h -->
# sources/user-network-fs/samba/source4/lib/messaging/messaging.h

`messaging.h` is the public source4 messaging API. It declares the opaque `imessaging_context`, `msg_callback_t`, `SAMBA_PARENT_TASKID`, send/register/deregister routines, context constructors, datagram cleanup, fork reinit, pointer send, server-id access, and process cleanup. The callback contract receives the context, private data, message type, source `server_id`, optional file descriptors, and payload `DATA_BLOB`.

The header defines the integration boundary for users of the messaging library while hiding the dispatch arrays, IDR state, datagram reference, and name database in `messaging_internal.h`. Callers must provide a loadparm context, tevent context, and server ID, then register callbacks before expecting delivery. Temporary registrations allocate message IDs at or above `MSG_TMP_BASE`.

State behavior is owned by the implementation, but the API exposes lifecycle-sensitive operations: `imessaging_dgm_unref_ev()` must run before an event context disappears, and `imessaging_reinit_all()` must be called after fork. Risks are mostly ownership and callback-lifetime mistakes: private data must outlive registered handlers, fd-bearing messages need explicit handling, and contexts created with discard-incoming drop messages unless an IRPC pending call temporarily increments listeners. Compile coverage plus local messaging tests are the main test signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_handlers.c -->
# sources/user-network-fs/samba/source4/lib/messaging/messaging_handlers.c

`messaging_handlers.c` adds non-core internal message handlers that are compiled only for developer or selftest builds. `imessaging_register_extra_handlers()` registers `MSG_SMB_INJECT_FAULT` and `MSG_SMB_SLEEP`. `do_inject_fault()` validates that no file descriptors arrived, checks the payload is an aligned `int`, then either exits on `-1` or sends the requested signal to the current process. `do_sleep()` similarly validates an aligned `unsigned int` payload and blocks the process with `sleep()`.

These handlers integrate with `imessaging_init_internal()` behind `#if defined(DEVELOPER) || defined(ENABLE_SELFTEST)`, making them deliberate test and fault-injection hooks rather than production protocol surface. They do not persist state, but they mutate process liveness and scheduling. Risks are intentional: a malformed payload is ignored, but a valid sender can terminate, signal, or stall a process. The code relies on same-host messaging access controls and build-time exclusion. Test signals are selftest scenarios that need process crash/sleep injection and compile checks that production builds do not register these handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_handlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_internal.h -->
# sources/user-network-fs/samba/source4/lib/messaging/messaging_internal.h

`messaging_internal.h` defines the private layout of `struct imessaging_context` and declares `imessaging_register_extra_handlers()`. The context links all live messaging contexts, stores the owning `tevent_context`, local `server_id`, socket and lock directories, fixed and temporary dispatch registries, IRPC registration list, pending IRPC request IDR, `server_id_db` name store, start time, datagram reference, and incoming-listener accounting.

This header is the shared contract between `messaging.c`, `messaging_send.c`, `messaging_handlers.c`, and the Python binding. The most important state behavior is the split between normal and discard-incoming contexts: discard contexts start with zero listeners but pending IRPC calls temporarily add listeners so replies can be received. The global context list enables fork reinitialization and event-context datagram unref.

Risks are ABI and encapsulation related. Because the Python module includes this private header to access `msg_ctx->ev`, changes to the structure can break bindings. Listener count, IDR cleanup, and datagram reference ownership must stay consistent with destructors and reinit code. Test coverage should exercise free-during-callback and fork/reinit paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_send.c -->
# sources/user-network-fs/samba/source4/lib/messaging/messaging_send.c

`messaging_send.c` contains the send-side subset of source4 messaging to avoid pulling full DCERPC dependencies into auth logging paths. `irpc_servers_byname()` looks up registered server IDs in `server_id_db`. `imessaging_send()` constructs a fixed message header with `message_hdr_put()`, appends an optional payload iovec, and sends through `messaging_dgm_send()`. `imessaging_send_ptr()` wraps a pointer-sized payload for in-process style messages.

The main control flow rejects non-local cluster nodes with success because source4 has no cluster transport here, normalizes pid zero to the current pid, and retries under `root_privileges()` on `EACCES`. Persistence is indirect: sends depend on the receiver's socket path and name database, but this file itself only transmits datagrams.

Risks include silent success for non-local cluster destinations, pointer payloads being meaningful only inside compatible local process layouts, and privilege retry broadening the effective send capability. Payload ownership remains with the caller until send completes. Tests should cover local sends with and without payloads, name lookups, permission fallback, and failures from stale server IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/messaging_send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/pymessaging.c -->
# sources/user-network-fs/samba/source4/lib/messaging/pymessaging.c

`pymessaging.c` exposes source4 messaging to Python as `samba.messaging.Messaging`. The type owns a talloc context and `imessaging_context`. Constructor arguments are optional `own_id` and `lp_ctx`; IDs can be Python tuples or `samba.dcerpc.server_id` objects. Methods include `send()`, `register()`, `deregister()`, `loop_once()`, `irpc_add_name()`, `irpc_remove_name()`, `irpc_servers_byname()`, `irpc_all_servers()`, and the `server_id` property.

Control flow creates a private event context, then either initializes a listening context for explicit IDs or a discard-incoming client context. Registered Python callbacks are wrapped by `py_msg_callback_wrapper()`, which converts source server IDs to NDR Python objects and calls `(private, msg_type, server_id, bytes)`. Temporary registration returns the allocated message type.

State persists in the Python object's talloc tree and in the shared messaging name database for IRPC names. Risks include callback reference handling: registration `Py_INCREF`s the tuple, but deregistration requires the exact same private-data pointer to release references. The wrapper ignores fd-bearing messages and does not propagate callback exceptions robustly. Test signals include Python send/register round trips, temporary IDs, name registration enumeration, and event-loop timeout behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/pymessaging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/tests/irpc.c -->
# sources/user-network-fs/samba/source4/lib/messaging/tests/irpc.c

`tests/irpc.c` is the local torture suite for IRPC over source4 messaging. It creates two messaging contexts on the same event loop, registers generated echo interface calls on both, and verifies synchronous, deferred, and high-volume asynchronous RPC behavior. Key test handlers are `irpc_AddOne()` and `irpc_EchoData()`, with `deferred_echodata()` proving delayed replies through `irpc_send_reply()`.

`irpc_setup()` configures a temporary pid directory, creates contexts with task IDs 1 and 2, and registers `ECHO_ADDONE` and `ECHO_ECHODATA`. `test_addone()` exercises NDR request/reply and edge input values. `test_echodata()` validates deferred payload echo. `test_speed()` sends asynchronous calls with a bounded backlog and drains replies through the shared tevent loop.

The suite does not persist data outside messaging socket/name state under the test pid directory. Risks covered include nested event loops, call-id routing, deferred reply ownership, async completion, and timeout/backlog pressure. Gaps include cross-process IRPC name lookup and security-token propagation. It is a strong regression signal for `messaging.c` IRPC binding-handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/tests/irpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/tests/messaging.c -->
# sources/user-network-fs/samba/source4/lib/messaging/tests/messaging.c

`tests/messaging.c` is the local torture suite for raw imessaging datagrams. It defines ping/pong/exit callbacks, overflow tests, checksum validation across a forked child, and multi-context delivery tests. `torture_local_messaging()` registers `overflow`, `overflow_check`, `ping_speed`, and `multi_ctx`.

`test_ping_speed()` creates client/server contexts, registers temporary message handlers, sends payload and NULL-payload pings for a configurable timelimit, and drains replies. `test_messaging_overflow()` sends many pings to a forked child to ensure queue pressure does not break initialization or cleanup. `test_messaging_overflow_check()` streams random payloads to a child and compares MD5 digests returned over messaging. `test_multi_ctx()` sends to `cluster_id(0,0)` and frees contexts from inside callbacks, proving dispatch iteration survives callback-side destruction.

State is limited to temporary pid/socket directories and process memory. Dependencies include tevent, cluster IDs, GnuTLS hashing, fork/pipe synchronization, and loadparm. Risks tested include fd rejection, queue overflow, message loss, broadcast semantics, and use-after-free during callback dispatch. Gaps include privilege retry and non-local cluster behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/tests/messaging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/wscript_build -->
# sources/user-network-fs/samba/source4/lib/messaging/wscript_build

This build script defines the source4 messaging build targets. `MESSAGING_SEND` compiles `messaging_send.c` as a private library with dependencies kept small for auth-log users. `MESSAGING` compiles `messaging.c` and `messaging_handlers.c` with full NDR, DCERPC, clustering, server-id DB, and talloc-report dependencies. `python_messaging` builds `pymessaging.c` as `samba/messaging.so` with `MESSAGING`, events, pyparam, and pytalloc utilities.

The dependency split is the important integration decision: send-only helpers can link without the heavier IRPC server implementation, reducing dependency loops. State and persistence behavior are build-time only, but target names define the linking surface consumed elsewhere in Samba. Risks include accidental dependency expansion in `MESSAGING_SEND`, missing generated NDR dependencies for IRPC, and Python module ABI drift if private headers change. Test signals are successful Waf configuration/build, import of `samba.messaging`, and local messaging/IRPC torture suites linked against these targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_filesys.c -->
# sources/user-network-fs/samba/source4/lib/policy/gp_filesys.c

`gp_filesys.c` implements Group Policy Template (GPT) filesystem operations over the domain controller's `sysvol` SMB share. Important helpers include `gp_cli_connect()`, `gp_get_share_path()`, `gp_fetch_gpt()`, `gp_push_gpt()`, `gp_create_gpt()`, and `gp_set_gpt_security_descriptor()`. Internal list/copy helpers walk remote directories, copy files to local temporary policy directories, recursively push local files, and set NT security descriptors on GPT directories.

Control flow for fetch connects to `sysvol`, derives the share-relative path from a UNC `gPCFileSysPath`, lists remote entries recursively up to `GP_MAX_DEPTH`, creates local directories, and copies file contents while checking final size. Push does the reverse using local `opendir()` and SMB create/write calls. Create builds a local GPT skeleton with `User`, `Machine`, and `GPT.INI`, then uploads it.

Persistence spans local temp directories under `tmpdir()/policy` and remote SYSVOL contents. Risks include path parsing based on the fourth backslash, partial cleanup on copy failures, depth truncation, local case-sensitivity around `GPT.INI`, mkdir failures on preexisting directories, and ACL application only to the top GPT directory. Tests need live or fake SMB SYSVOL coverage for fetch, push, create, and security descriptor setting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_filesys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_ini.c -->
# sources/user-network-fs/samba/source4/lib/policy/gp_ini.c

`gp_ini.c` parses and queries GPT INI files. `gp_parse_ini()` calls Samba's `pm_process()` parser with `gp_add_ini_section()` and `gp_add_ini_param()` callbacks to build a `gp_ini_context` containing sections and key/value arrays. `gp_get_ini_string()` and `gp_get_ini_uint()` scan the parsed structure for a section/name pair and return a string pointer or `atol()`-converted integer.

The file has no external persistence beyond reading the supplied INI path; parsed state lives under the caller's talloc context. It depends on `samba_util.h` and `policy.h`. Control flow is simple but strict: parameters before any section fail parsing because `cur_section` remains `-1`.

Risks include linear lookups, duplicate sections or keys returning the first match, unsigned integer conversion through `atol()` without range or error validation, and `gp_parse_ini()` callers needing to pass the actual file path. In `gp_manage.c`, a computed `GPT.INI` path is not used when calling `gp_parse_ini()`, which looks suspicious. Test signals should include normal GPT.INI, missing section/name, malformed files, duplicate keys, and large numeric values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_ini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_ldap.c -->
# sources/user-network-fs/samba/source4/lib/policy/gp_ldap.c

`gp_ldap.c` implements LDAP-side Group Policy Object operations. `gp_init()` discovers a PDC, connects to LDAP, and creates `gp_context`. Query APIs list all GPOs, fetch one GPO, parse `gPLink`, list applicable GPOs for a security token, and map flag bits to strings. Mutation APIs set/delete `gPLink`, get/set inheritance through `gPOptions`, create a GPC object plus `CN=User` and `CN=Machine`, set `nTSecurityDescriptor`, and update basic GPO attributes.

Control flow centers on LDB searches under `CN=Policies,CN=System` and base-object modifications. `parse_gpo()` converts LDAP attributes into `gp_object` and pulls the security descriptor via NDR. `gp_list_gpos()` finds the token's user/computer DN, walks parent containers to the domain root, applies inheritance/enforcement/disable flags, checks GPO read/list property access, and returns applicable GPO DNs.

Persistent state is Active Directory LDAP data: GPC objects, links, inheritance options, security descriptors, flags, display names, and version attributes. Risks include string parsing of `gPLink`, direct mutation of returned LDAP attribute strings in `gp_set_gplink()`/`gp_del_gplink()`, missing transactionality across multi-object GPO creation, possible `version` vs `versionNumber` mismatch in `gp_set_ldap_gpo()`, and limited validation of LDAP result shapes. Tests require LDAP integration with links, inheritance, disabled user/machine policy, ACL filtering, and create/update/delete paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_manage.c -->
# sources/user-network-fs/samba/source4/lib/policy/gp_manage.c

`gp_manage.c` orchestrates higher-level Group Policy management across LDAP and SYSVOL. `gp_ads_to_dir_access_mask()` maps directory-service ACE access bits to filesystem directory rights. `gp_create_gpt_security_descriptor()` converts a DS security descriptor to a GPT filesystem descriptor, copying owner/group/SACL, transforming DACL ACEs, skipping `SID_BUILTIN_PREW2K` allow ACEs, and adding inheritance flags. `gp_create_gpo()`, `gp_set_acl()`, and `gp_push_gpo()` combine LDAP and filesystem helpers.

`gp_create_gpo()` generates an uppercase GUID name, builds a SYSVOL path, creates the GPT, creates the LDAP GPC, refetches the GPO security descriptor, converts it to filesystem form, and applies it to SYSVOL. `gp_set_acl()` writes LDAP ACL first, then mirrors the resulting descriptor to SYSVOL. `gp_push_gpo()` parses GPT.INI, pushes local GPT files, and updates LDAP metadata.

Persistence spans both AD and SYSVOL, but operations are not transactional across those stores. Failures can leave an LDAP GPC without files, files without matching LDAP state, or mismatched ACLs. Additional risks include assuming `ds_sd->dacl` is non-NULL, broad access-mask mapping, and the unused GPT.INI filename in `gp_push_gpo()`. Tests should cover partial failures, descriptor conversion, GUID/path creation, and LDAP/SYSVOL consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/gp_manage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/policy.h -->
# sources/user-network-fs/samba/source4/lib/policy/policy.h

`policy.h` defines the source4 Group Policy C API. It declares link option bits, GPO disable flags, `enum gpo_inheritance`, and the core data structures `gp_context`, `gp_object`, `gp_link`, `gp_ini_param`, `gp_ini_section`, and `gp_ini_context`. It also prototypes LDAP, filesystem, INI, and management functions implemented across `gp_ldap.c`, `gp_filesys.c`, `gp_ini.c`, and `gp_manage.c`.

The central integration type is `gp_context`, which holds LDB, loadparm, credentials, tevent, cached SMB client state, and active DC information. `gp_object` represents both LDAP GPC metadata and the SYSVOL path. The API exposes direct mutation routines for LDAP links/inheritance/ACLs and filesystem GPT creation/push/ACL operations.

State ownership follows talloc conventions and is not encoded in the types, so callers must keep contexts and returned objects alive. Risks include broad header coupling to LDB/SMB/security types, lack of explicit transaction or consistency API, and callers misunderstanding which functions mutate LDAP, SYSVOL, or both. Test signals are compile coverage and integrated policy create/fetch/push/ACL tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/pypolicy.c -->
# sources/user-network-fs/samba/source4/lib/policy/pypolicy.c

`pypolicy.c` exposes a small subset of `samba-policy` to Python as `samba.policy`. It wraps `gp_get_gpo_flags()`, `gp_get_gplink_options()`, and `gp_ads_to_dir_access_mask()`, and exports constants for GPO and link flags. The wrappers allocate a temporary talloc context, call the C helper, convert NULL-terminated string arrays to Python lists, and translate NTSTATUS failures to Python exceptions.

There is no persistent state beyond module constants. Integration is mainly for Python tooling that needs symbolic flag names or access-mask conversion without driving full GPO management. Risks include constant naming mistakes: the module adds `GPO_MACHINE_USER_DISABLE` instead of the expected `GPO_FLAG_MACHINE_DISABLE`, and `GPLINK_OPT_ENFORCE ` has a trailing space in the exported Python name. Input parsing uses signed `int` for flag masks in two wrappers. Test signals should import the module, verify exact constant names, compare flag list outputs, and validate mask conversion for each ADS access bit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/pypolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/samba-policy.pc.in -->
# sources/user-network-fs/samba/source4/lib/policy/samba-policy.pc.in

`samba-policy.pc.in` is the pkg-config template for the `samba-policy` library. It declares install prefix variables, package name and description, public `Requires: talloc`, private `Requires.private: ldb`, package version substitution, linker flags for `-lsamba-policy`, and include flags with `-DHAVE_IMMEDIATE_STRUCTURES=1`.

The file has no runtime control flow or persistence, but it defines the external build integration contract for consumers outside the Samba Waf build. The dependency split exposes talloc publicly while keeping LDB private unless static linking or private resolution is needed.

Risks are packaging-related: missing dependencies can break external builds, the immediate-structures define may leak Samba internals into consumers, and version/library path substitutions must match install layout. Test signals include `pkg-config --cflags --libs samba-policy` after install and compiling a small consumer that includes `policy.h` and links against `libsamba-policy`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/samba-policy.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/wscript_build -->
# sources/user-network-fs/samba/source4/lib/policy/wscript_build

This Waf script builds the Group Policy library and Python module. `bld.SAMBA_LIBRARY('samba-policy')` compiles `gp_ldap.c`, `gp_filesys.c`, `gp_manage.c`, and `gp_ini.c`, installs `samba-policy.pc`, exposes `policy.h`, and declares public dependencies on `ldb` and `samba-net`. `bld.SAMBA_PYTHON('py_policy')` builds `pypolicy.c` as `samba/policy.so` and links against `samba-policy` and pytalloc utility support.

Its main integration role is packaging the LDAP, SYSVOL, management, and INI helpers into one library. There is no runtime state. Risks are dependency drift, especially because `gp_filesys.c` uses SMB client APIs and `gp_manage.c` uses security descriptor helpers that must arrive transitively. Test signals are Waf target build, pkg-config generation, Python import of `samba.policy`, and link tests for external `policy.h` consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/policy/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/hive.c -->
# sources/user-network-fs/samba/source4/lib/registry/hive.c

`hive.c` is the generic registry hive wrapper layer. `reg_open_hive()` peeks at a file header and dispatches to `reg_open_regf_file()` for `regf` hives or `reg_open_ldb_file()` for LDB/TDB-backed hives. The remaining functions forward key operations to `struct hive_operations`: key info, add/delete/open/enumerate subkeys, set/get/enumerate/delete values, get/set security descriptors, and flush.

Control flow is intentionally thin and backend-driven. Optional operations return `WERR_NOT_SUPPORTED`, while `hive_key_flush()` treats a missing flush hook as success. State and persistence are entirely backend-owned; this file only chooses a backend and normalizes API behavior.

Risks include simplistic file-type detection using a short read, returning `WERR_FILE_NOT_FOUND` for several different open/read/unknown-format failures, and trusting backend operation tables. `hive_key_add_name()` asserts that names do not contain backslashes, so path splitting must happen above this layer. Test signals include opening REGF and LDB hives, unsupported optional operations, and operation forwarding against mock or local backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/hive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/interface.c -->
# sources/user-network-fs/samba/source4/lib/registry/interface.c

`interface.c` is the public registry-context wrapper API. It defines the predefined key table and provides functions to look up predefined names/handles, open keys, enumerate subkeys and values, read key info, add/delete keys, set/get/delete values, flush keys, and get/set security descriptors. Each call validates obvious NULL inputs and dispatches to `struct registry_operations` in the active backend.

The control flow is direct delegation; this file is the stable boundary between callers and backends such as `local.c`. Persistence is backend-specific and can be local hive files, LDB hives, or remote registry implementations outside this subset. Integration points include absolute-path helpers declared elsewhere and predefined HKEY constants from generated winreg headers.

Risks include inconsistent fallback behavior: comments mention fallback for open but the implementation requires `open_key`; most missing backend hooks return `WERR_NOT_SUPPORTED`. The predefined lookup is case-insensitive by name. Tests should cover each public wrapper with NULL keys, unsupported backend hooks, predefined key lookup, and propagation of backend WERRORs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/ldb.c -->
# sources/user-network-fs/samba/source4/lib/registry/ldb.c

`ldb.c` implements a registry hive backend stored in LDB. Keys are LDB entries under `hive=NONE` with `key=` RDNs; non-default values are child entries with `value=` RDNs, while default values live as `data`/`type` attributes on the key entry. `struct ldb_key_data` caches the LDB context, DN, subkey/value search results, and classname. The backend implements open/add/delete key, enumerate key/value, set/get/delete value, and key info.

Value packing/unpacking maps registry types to LDB attributes: strings convert UTF-16 to/from UTF-8, DWORD/QWORD values are stored as numeric strings, and binary data is stored raw. `reg_open_ldb_file()` connects through `ldb_wrap_connect()`, adds `@ATTRIBUTES` case-insensitive rules, and returns a root hive key. Key deletion recursively deletes child keys and values inside an LDB transaction. Set value tries modify first and falls back to add.

Persistence is the LDB database file. Risks include cache invalidation correctness, no implemented security descriptor or flush hooks, type conversion failures producing empty data, transaction nesting during recursive delete, and root DN assumptions. Tests should cover all registry value types, default values, recursive delete, case-insensitive key/value names, and reopen persistence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/local.c -->
# sources/user-network-fs/samba/source4/lib/registry/local.c

`local.c` implements a registry context that mounts hive roots under predefined HKEY paths. `reg_open_local()` creates a `registry_local` context with `local_ops`; `reg_mount_hive()` attaches a `hive_key` at a predefined key and optional path; `reg_import_hive_key()` wraps a hive key as a registry key. Operations split registry paths, walk or create hive keys, and forward value, enumeration, info, security, delete, and flush operations to the mounted hive.

State persists through mounted hive backends, while `registry_local` holds only mountpoint metadata and talloc references. `local_open_key()` and `local_create_key()` maintain path element arrays so wrapped keys know their absolute position. Integration is the bridge from high-level `registry_context` APIs in `interface.c` to low-level `hive_operations` in `hive.c`/`ldb.c`/REGF.

Risks include mountpoint lookup only returning exact predefined roots with NULL elements in `local_get_predefined_key()`, path element allocation size needing NULL terminators, no duplicate mountpoint protection, and forwarding backend limitations. Tests should mount hives under multiple HKEY roots, create nested keys, delete values, flush, and check security descriptor propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regdiff.1.xml -->
# sources/user-network-fs/samba/source4/lib/registry/man/regdiff.1.xml

This DocBook man page documents `regdiff`, a command that compares two Windows registry files key by key and emits a patch format that `regpatch` can apply. The synopsis includes common Samba command-line option includes plus `--backend BACKEND` and `--credentials=CREDENTIALS`. It states that `regdiff` and `regpatch` use the same format as Windows `.REG` files.

There is no executable control flow, but the document is an integration contract for command-line behavior and supported workflows: compare registry backends, generate a diff, and later apply it. Persistence is through the input registry files and generated patch file.

Risks are documentation drift from actual tool behavior, especially backend names, authentication behavior, and patch format support. The page references version 4.0 and related tools. Test signals include generated manpage build, `regdiff --help` matching documented options, and end-to-end diff/apply tests with `regpatch`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regdiff.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regpatch.1.xml -->
# sources/user-network-fs/samba/source4/lib/registry/man/regpatch.1.xml

This DocBook man page documents `regpatch`, which applies registry patches to Windows registry files. The synopsis accepts `PATCHFILE`, includes Samba common options, and documents `--backend BACKEND` and `--credentials=CREDENTIALS`. It states that if no patch file is specified, patch data is read from standard input.

The page has no runtime control flow, but it describes the user-facing wrapper around `reg_diff_apply()` and patch loaders such as `.REG` and PReg support. Persistence is mutation of the target registry backend or file. Integration points are `regdiff`, `regtree`, `regshell`, Samba credential parsing, and backend loading.

Risks are user-impacting because applying patches mutates registry data; documentation should be precise about input format, stdin behavior, and backend selection. Test signals include manpage generation, `regpatch --help`, applying a `.REG` file from disk and stdin, and verifying modified output with `regtree` or `regdiff`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regpatch.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regshell.1.xml -->
# sources/user-network-fs/samba/source4/lib/registry/man/regshell.1.xml

This DocBook man page documents `regshell`, a readline-style interactive browser for Windows registry files or remote registries. It lists backend and credential options, then documents shell commands such as `ck|cd`, `ch|predef`, `list|ls`, `mkkey|mkdir`, `rmval|rm`, `rmkey|rmdir`, `pwd|pwk`, `set|update`, `help|?`, and `exit|quit`. Examples show browsing an NT4 registry file and listing a remote `HKEY_CURRENT_USER\AppEvents` path.

The document describes interactive control flow rather than implementing it: open a backend, switch predefined roots, navigate keys, list contents, and mutate keys/values where supported. Persistence depends on the selected backend and commands used. Risks include documentation drift, particularly the note that `set|update` is not implemented, and remote examples requiring credentials and backend support. Test signals are manpage generation, command help parity, scripted regshell sessions, and remote/local examples.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regshell.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regtree.1.xml -->
# sources/user-network-fs/samba/source4/lib/registry/man/regtree.1.xml

This DocBook man page documents `regtree`, a text-mode registry viewer that prints all contents of a Windows registry file. It documents backend and credential options plus `--fullpath` and `--no-values`, which control output path formatting and whether values are printed. It links related tools such as `gregedit`, `regshell`, `regdiff`, and `regpatch`.

There is no executable control flow in the XML; it describes read-only traversal behavior over registry backends. Persistence is not mutated by the tool, but output reflects the selected registry file or backend. Integration points are registry backend loading, Samba credential parsing for remote registries, and the registry enumeration APIs.

Risks are documentation drift around option names and backend support. Since `regtree` is often used to validate `regpatch` or inspect generated hives, output stability matters. Test signals include manpage generation, `regtree --help`, full-path/no-values output comparison, and traversal of hives containing default values and nested keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/man/regtree.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile.c -->
# sources/user-network-fs/samba/source4/lib/registry/patchfile.c

`patchfile.c` implements registry diff generation, patch format dispatch, and patch application callbacks. `reg_generate_diff_key()` recursively compares old and new registry keys, emitting add/delete key and set/delete value callbacks. `reg_generate_diff()` iterates all predefined HKEY roots. `reg_diff_load()` detects PReg files by `PReg` header and otherwise treats input as `.REG`. `reg_diff_apply()` wires callbacks that create/delete absolute keys and set/delete values on a `registry_context`.

Control flow is callback-driven: generation is backend-agnostic, and loading delegates parsing to format-specific modules. Apply creates intermediate keys for additions, ignores missing deleted parent keys, and repeatedly deletes value index 0 for "delete all values".

Persistence is whatever registry backend the context represents; patch application mutates it. Risks include non-transactional patch application, recursive diff order interactions, ignored callback return values in some generation paths, memory ownership around value names/data, and type/data comparisons relying on backend canonicalization. Test signals include round-trip diff/apply between two hives, PReg and `.REG` loaders, deletion of nested keys, default values, and failed mid-patch behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile_dotreg.c -->
# sources/user-network-fs/samba/source4/lib/registry/patchfile_dotreg.c

`patchfile_dotreg.c` saves and loads Windows `REGEDIT4` `.REG`-style registry diffs. Save-side callbacks write key headers, delete-key headers, value assignments, and delete-value lines. `reg_val_dotreg_string()` converts registry data to strings: UTF-16 strings become Unix strings, DWORDs become eight-digit hex, binary data becomes comma-separated bytes, and other types use `hex(type):...`. `reg_dotreg_diff_load()` parses line-oriented `.REG` input and invokes registry diff callbacks.

Parser control flow skips the first header line, tracks the current key, supports key deletion with `[-key]`, value deletion with `=-`, line continuation with trailing backslash and two-space continuation, and uses `reg_string_to_val()` for data conversion.

Persistence occurs through callbacks, usually `reg_diff_apply()`. Risks include documented lack of newer UCS-2 `.REG` support, fragile quoting and default-value handling, clearing `curkey` on blank/comment lines, mode `0755` for created patch files, limited escaping on save, and non-transactional application. Tests should include REG_SZ, DWORD, binary, default `@`, multiline hex, delete value/key, comments, CRLF input, and malformed lines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile_dotreg.c -->
