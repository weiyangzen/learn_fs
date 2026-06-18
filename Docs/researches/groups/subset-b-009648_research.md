# subset-b-009648 Research

Grouped source research for ksmbd-tools mount/config/authentication management code and libfuse example programs. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/worker.c -->
# sources/user-network-fs/ksmbd-tools/mountd/worker.c

## Purpose

`worker.c` is the ksmbd mount daemon's asynchronous IPC worker dispatcher. It receives kernel/userspace IPC events, pushes them into a GLib thread pool, routes each event type to the correct management subsystem, and sends IPC responses back to the server side. The source was read as a complete 387-line file.

## Important APIs, Types, and Functions

Public lifecycle/API functions are `wp_init`, `wp_destroy`, and `wp_ipc_msg_push`. Internal handlers include `login_request`, `login_request_ext`, `spnego_authen_request`, `tree_connect_request`, `share_config_request`, `tree_disconnect_request`, `logout_request`, `heartbeat_request`, and `rpc_request`. The `VALID_IPC_MSG` macro enforces exact payload size for fixed-size events. The worker binds kernel IPC structs such as `ksmbd_login_request`, `ksmbd_tree_connect_request`, `ksmbd_share_config_request`, `ksmbd_rpc_command`, and `ksmbd_spnego_authen_request` to userspace manager APIs.

## Control Flow

`wp_init` creates a `GThreadPool` with up to four workers. `wp_ipc_msg_push` queues a received `ksmbd_ipc_msg`. `worker_pool_fn` switches on `msg->type`, calls the matching handler, and frees the inbound message. Login handlers consult user management, tree handlers consult share/session management, RPC messages are delegated to `rpc_*_request`, and SPNEGO first authenticates the token before doing a normal login lookup and returning session key/blob payloads.

## State and Persistence Behavior

The file owns only the process-local thread pool. Persistent or long-lived state lives in the user, share, session, RPC, IPC, and SPNEGO modules. Response messages are heap allocated per request and freed after send.

## Dependencies and Integration Points

It depends on GLib threads, `linux/ksmbd_server.h`, `ipc.h`, `rpc.h`, and management modules for users, shares, tree connections, and SPNEGO. It is the integration boundary between kernel IPC events and ksmbd-tools userspace policy.

## Risks and Edge Cases

Some handlers dereference request payloads before or after size validation for fields such as handles/accounts, so malformed IPC sizes remain sensitive. `spnego_authen_request` reallocates the response after authentication and must free `auth_out` buffers on every path. RPC response sizing is based on command flags and `payload_sz`; incorrect handler sizes can overrun the intended IPC payload contract.

## Test Signals

Useful signals are mountd IPC integration tests for each event type, malformed-size message tests, SPNEGO success/failure paths, RPC open/read/write/ioctl smoke tests, and thread-pool shutdown tests that ensure queued messages are drained or freed cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/worker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/tools/Makefile.am

## Purpose

`tools/Makefile.am` is the Autotools build definition for the `ksmbd.tools` libexec binary. It lists shared management/config source files, conditionally includes Kerberos/SPNEGO support, and links the command-specific static libraries that provide addshare, adduser, control, and mountd entry points.

## Important APIs, Types, and Functions

The important build variables are `AM_CFLAGS`, `LIBS`, `libexec_PROGRAMS`, `ksmbd_tools_SOURCES`, and `ksmbd_tools_LDADD`. The `HAVE_LIBKRB5` conditional adds `management/spnego.c`, `asn1.c`, `management/spnego_krb5.c`, and `management/spnego_mech.h`.

## Control Flow

There is no runtime control flow. At build generation time Automake expands this file, compiles the listed shared sources into `ksmbd.tools`, and links the tool-specific archives. At runtime `tools.c` dispatches based on the executable basename.

## State and Persistence Behavior

No runtime state is stored here. The file persists build policy: include paths, defines for `SYSCONFDIR` and `RUNSTATEDIR`, feature-gated Kerberos sources, and linked libraries.

## Dependencies and Integration Points

The build integrates GLib, libnl, optional libkrb5, pthreads, top-level include headers, and static libraries from sibling directories. It must remain consistent with `tools/meson.build` so both build systems expose the same feature surface.

## Risks and Edge Cases

Source-list drift between Autotools and Meson can produce different binaries. Optional Kerberos compilation depends on `HAVE_LIBKRB5`; missing the ASN.1/SPNEGO files when krb5 is enabled would break authentication symbols.

## Test Signals

Run an Autotools build with and without libkrb5 detected, check that `ksmbd.tools` links, and verify each symlink/basename mode starts correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/asn1.c -->
# sources/user-network-fs/ksmbd-tools/tools/asn1.c

## Purpose

`asn1.c` implements small ASN.1/BER decoding and encoding helpers used by ksmbd SPNEGO/Kerberos negotiation. It parses headers, object identifiers, octet payloads, and raw buffers, and it builds simple definite-length headers/OID encodings for response tokens. The source was read as a complete 391-line file.

## Important APIs, Types, and Functions

Public functions are `asn1_open`, `asn1_header_decode`, `asn1_octets_decode`, `asn1_read`, `asn1_oid_decode`, `asn1_header_len`, `asn1_oid_encode`, and `asn1_header_encode`. Internal helpers decode octets, high-tag-number tags, identifier octets, lengths, EOC markers, and OID subidentifiers. State is held in `struct asn1_ctx` from `asn1.h`.

## Control Flow

Callers initialize a context with `asn1_open`, then repeatedly decode headers and consume payloads until the returned EOC pointer is reached. OID decode reads the compressed first two subidentifiers and then variable-length base-128 subids. Encoding first computes nested header sizes, then writes identifier octets and short or long-form lengths before payload bytes are copied by the caller.

## State and Persistence Behavior

All parser state is cursor state inside `asn1_ctx`: `begin`, `end`, `pointer`, and `error`. The module allocates output buffers with GLib allocators and leaves ownership to callers. There is no file or process-global persistence.

## Dependencies and Integration Points

It depends on GLib allocation and is integrated by `management/spnego.c` for SPNEGO OID/token parsing and response construction.

## Risks and Edge Cases

Length decoding rejects lengths beyond the remaining buffer, which is essential for untrusted network tokens. However, some integer math mixes pointer differences and unsigned sizes; very large inputs should be fuzzed. `asn1_octets_decode` assumes a definite EOC pointer. Encoding supports up to four length octets and simple single-octet tags, matching current SPNEGO needs rather than a full ASN.1 implementation.

## Test Signals

ASN.1 fuzzing with truncated, indefinite, overlong, and malformed OIDs is the main signal. SPNEGO token interoperability tests and round-trip OID/header encode/decode tests should cover the expected Kerberos OIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/asn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/config_parser.c -->
# sources/user-network-fs/ksmbd-tools/tools/config_parser.c

## Purpose

`config_parser.c` parses ksmbd configuration files and turns text configuration into process-local global config, users, shares, generated SID subauthority values, and daemon lock state. It handles Samba-like `smb.conf` groups/key-values, the ksmbd password database, subauth and lock files, and externally supplied addshare options. The source was read as a complete 1011-line file.

## Important APIs, Types, and Functions

Public parser helpers include `cp_parse_smbconf`, `cp_parse_pwddb`, `cp_parse_subauth`, `cp_parse_lock`, `cp_parse_external_smbconf_group`, `cp_smbconf_parser_init`, `cp_smbconf_parser_destroy`, `cp_memparse`, `cp_get_group_kv_*`, `cp_group_kv_steal`, `cp_ltrim`, `cp_rtrim`, and `cp_key_cmp`. Global variables are `global_conf` and `parser`. Major internals validate groups and key-values, mmap files line by line, apply global defaults, propagate global share defaults, and process user/password/subauth/lock records.

## Control Flow

`__mmap_parse_file` opens a file, maps it, splits it into lines, and calls a file-specific `process_entry` function. `cp_parse_smbconf` accumulates groups, recursively validates nested parser ownership when needed, then `finalize_smbconf_parser` injects `[global]` and `[ipc$]` defaults, processes global options, copies global share options into all shares, creates shares through `shm_add_new_share`, logs ignored keys, and destroys parser state. Password parsing validates `name:base64hash`, updating or creating users. Subauth and lock parsing either read existing state or create mountd-owned defaults.

## State and Persistence Behavior

Parsed state persists in `global_conf`, the user manager, and the share manager. `set_conf_contents` can create missing config, password database, subauth, and lock files with restricted permissions. On reload, `KSMBD_SHOULD_RELOAD_CONFIG` changes stealing behavior so existing config values can be refreshed without resetting defaults in the same way as startup.

## Dependencies and Integration Points

It depends on GLib mapped files/hash tables, POSIX file APIs, `linux/ksmbd_server.h`, `management/user.h`, and `management/share.h`. It is called by `tools.c` during `load_config` for all ksmbd tool modes.

## Risks and Edge Cases

`cp_key_cmp` compares only the length of the right-hand key, so callers rely on canonical lookup strings to avoid prefix ambiguity. `cp_memparse` shifts without overflow checks. Lock handling trusts `kill(pid, 0)` and can be affected by permissions. File parsing stops after the first valid subauth/lock entry. Defaults and reload behavior are subtle because key stealing mutates group hash tables.

## Test Signals

High-value tests parse representative smb.conf files, duplicate keys, invalid UTF-8 names/comments, missing files in each tool mode, reload behavior, global-to-share default propagation, lock/subauth creation, base64 password validation, and boundary values for `max connections`, `sessions_cap`, and size suffix parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/config_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/session.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/session.c

## Purpose

`session.c` manages ksmbd userspace session objects and their tree connections. It keeps a hash table keyed by session ID, reference-counts sessions, binds tree connections to sessions, and enforces the configured maximum active session capacity. The source was read as a complete 217-line file.

## Important APIs, Types, and Functions

Public functions are `sm_init`, `sm_destroy`, `sm_handle_tree_connect`, `sm_handle_tree_disconnect`, and `sm_check_sessions_capacity`. Important internals include `new_ksmbd_session`, `kill_ksmbd_session`, `sm_lookup_session`, `__get_session`, `__put_session`, and `__sm_remove_session`. State is `sessions_table`, `sessions_table_lock`, each session's `update_lock`, `ref_counter`, `id`, `user`, and `tree_conns`.

## Control Flow

Tree connect first checks capacity; if no session exists, it allocates one, takes the table writer lock, handles a concurrent insertion race, and inserts the session. The tree connection is appended under the session update lock. Tree disconnect looks up the session, increments global capacity, finds the matching connection, removes it, decrements the session refcount, frees the tree connection, and puts the session reference.

## State and Persistence Behavior

State is in-memory only and is reset by `sm_destroy`. Session capacity is stored in `global_conf.sessions_cap` and mutated atomically as sessions are admitted and disconnected.

## Dependencies and Integration Points

It depends on GLib hash/list/locks, `management/tree_conn.h`, `management/user.h`, and `global_conf` from the config parser. Tree connection management calls it after access checks.

## Risks and Edge Cases

Capacity accounting is easy to regress: `sm_check_sessions_capacity` decrements only when a new session is needed, but `sm_handle_tree_disconnect` increments on every disconnect path in this file. Refcount and table removal are tightly coupled; races around lookup, put, and remove require lock coverage. Session objects store a user pointer without visibly taking a user reference here, so lifetime assumptions depend on the caller and shutdown ordering.

## Test Signals

Concurrent tree-connect/disconnect stress tests, capacity limit tests, duplicate session-ID races, missing-session disconnects, and shutdown with live tree connections are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/share.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/share.c

## Purpose

`share.c` implements ksmbd share management. It validates and stores share definitions parsed from smb.conf, maintains a ref-counted global share table, expands user/group and host access maps, applies share flags and masks, tracks connection counts, and serializes share configuration into kernel IPC responses. The source was read as a complete 961-line file.

## Important APIs, Types, and Functions

Public APIs include `shm_init`, `shm_destroy`, `shm_add_new_share`, `shm_lookup_share`, `get_ksmbd_share`, `put_ksmbd_share`, `shm_remove_all_shares`, `shm_lookup_users_map`, `shm_lookup_hosts_map`, `shm_open_connection`, `shm_close_connection`, `shm_iter_shares`, `shm_share_config_payload_size`, `shm_handle_share_config_request`, `shm_share_name`, `shm_share_name_hash`, `shm_share_name_equal`, and `shm_share_config`. Key static routines parse individual share options through `process_share_conf_kv`.

## Control Flow

Config finalization creates a `ksmbd_share`, initializes defaults, marks reload updates when needed, and processes group key-values into fields and flags. Share table insertion rejects casefolded duplicate names. Tree connect looks up a share, increments connection count through `shm_open_connection`, checks host/user maps, and later uses `shm_handle_share_config_request` to build the kernel-facing response payload.

## State and Persistence Behavior

Share state is process-local in `shares_table`, protected by `shares_table_lock`, and each share has update/maps locks and a refcount. Maps hold borrowed or referenced `ksmbd_user` objects. Persistence originates from smb.conf, but this file itself does not write disk state.

## Dependencies and Integration Points

It depends on GLib hash/UTF-8/casefold helpers, POSIX passwd/group APIs, `config_parser.h`, `management/user.h`, and `linux/ksmbd_server.h`. It feeds tree connection authorization and share config IPC responses.

## Risks and Edge Cases

`shm_open_connection` increments before checking `>= max_connections`, and error paths in tree connection also close the share, so off-by-one and double-close behavior need coverage. Host allow/deny maps are exact strings with a FIXME for real IP/mask matching. Group expansion scans system passwd/group databases at parse time. Veto-list parsing assumes a leading delimiter and rewrites slashes to NULs.

## Test Signals

Tests should cover UTF-8/casefold share names, duplicate shares, every share option, group expansion, guest account creation, host allow/deny semantics, max-connection boundaries, IPC payload sizing with root dir and veto lists, and reload update flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/spnego.c

## Purpose

`spnego.c` implements SPNEGO token negotiation glue for ksmbd Kerberos authentication. It initializes supported mechanisms, decodes incoming `negTokenInit` ASN.1 blobs, extracts the Kerberos AP_REQ, selects MS-KRB5 or standard KRB5 by OID, and wraps mechanism AP_REP output into a `negTokenTarg` response. The source was read as a complete 339-line file.

## Important APIs, Types, and Functions

Public functions are `spnego_init`, `spnego_destroy`, and `spnego_handle_authen_request`. Important internals are `get_mech`, `compare_oid`, `is_supported_mech`, `decode_asn1_header`, `decode_negTokenInit`, and `encode_negTokenTarg`. State is the static `mech_ctxs[SPNEGO_MAX_MECHS]` array of `spnego_mech_ctx`.

## Control Flow

Initialization assigns operations and global Kerberos service/keytab parameters to MSKRB5 and KRB5 contexts, then calls each mechanism setup. Authentication decodes the outer GSS/SPNEGO layers, validates SPNEGO and Kerberos OIDs, extracts the AP_REQ bytes, finds the selected mechanism context, and invokes its `handle_authen` callback with `encode_negTokenTarg` as a response encoder.

## State and Persistence Behavior

Mechanism contexts persist for the mountd process lifetime and are cleaned up by `spnego_destroy`. Per-request output buffers are allocated by the mechanism/encoder and freed by the worker after IPC response construction.

## Dependencies and Integration Points

It depends on `asn1.c`, `spnego_mech.h`, `management/spnego.h`, global config, and `spnego_krb5.c` operations. It is called from `mountd/worker.c` for `KSMBD_EVENT_SPNEGO_AUTHEN_REQUEST`.

## Risks and Edge Cases

The decoder accepts only the expected token shape and first mechanism OID; clients offering multiple mechanisms or unusual optional SPNEGO fields may fail. `spnego_init` assumes non-null operations before testing `mech_ctxs[i].ops->setup`, so all mechanism slots must be initialized. ASN.1 length and pointer handling is security-sensitive because blobs originate from clients.

## Test Signals

Valid Windows Kerberos negotiation, unsupported OID rejection, malformed/truncated SPNEGO fuzz cases, krb5-disabled builds, and cleanup/reinit tests are the core signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego_krb5.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/spnego_krb5.c

## Purpose

`spnego_krb5.c` provides the Kerberos mechanism implementation behind SPNEGO. It initializes a Kerberos context/keytab/credentials, validates AP_REQ tokens, extracts the client principal and session key, creates an AP_REP, and exposes separate operations for standard KRB5 and Microsoft KRB5 OIDs. The source was read as a complete 406-line file.

## Important APIs, Types, and Functions

Exported objects are `spnego_krb5_operations` and `spnego_mskrb5_operations`. Key internals are `setup_krb5`, `setup_mskrb5`, `setup_krb5_ctx`, `cleanup_krb5`, `handle_krb5_authen`, `acquire_creds_from_keytab`, `parse_service_full_name`, `get_host_name`, and compatibility shims/macros for different krb5 APIs.

## Control Flow

Setup optionally returns early when Kerberos support is disabled, otherwise initializes krb5, resolves the configured or default keytab, parses/generates the service principal, and obtains initial credentials from the keytab. Authentication creates an auth context, calls `krb5_rd_req`, retrieves the receive subkey, builds AP_REP, extracts the authenticator client without realm, copies username/session key to `auth_out`, and wraps AP_REP through the SPNEGO encoder callback.

## State and Persistence Behavior

`struct spnego_krb5_ctx` persists in `mech_ctx->private` and owns `krb5_context`, `krb5_keytab`, and `krb5_creds`. Request outputs are allocated for `user_name`, `sess_key`, and `spnego_blob`. Keytab contents are external persistent state.

## Dependencies and Integration Points

It depends on libkrb5, DNS/hostname resolution, sockets/netdb, GLib allocation, `asn1.h`, and `spnego_mech.h`. It is built only when Kerberos dependencies are present.

## Risks and Edge Cases

`parse_service_full_name` rejects host names without a dot, which can make default host resolution fragile. The setup path aborts SPNEGO initialization if credentials cannot be acquired when Kerberos support is enabled. Principal handling has compile-time branches for krb5 library variants. Session-key copying and AP_REP cleanup require exact ownership handling.

## Test Signals

Use a test realm/keytab to validate default service name, explicit `service/host@REALM`, bad keytab, disabled Kerberos, MSKRB5 and KRB5 OIDs, AP_REQ failures, and memory cleanup under repeated authentications.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego_krb5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego_mech.h -->
# sources/user-network-fs/ksmbd-tools/tools/management/spnego_mech.h

## Purpose

`spnego_mech.h` defines the private mechanism interface shared by SPNEGO negotiation and Kerberos mechanism implementations. It declares mechanism identifiers, the response encoder callback type, operation vtable, mechanism context layout, and exported krb5 operation tables. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions

Important declarations are `SPNEGO_MECH_MSKRB5`, `SPNEGO_MECH_KRB5`, `SPNEGO_MAX_MECHS`, `spnego_encode_t`, `struct spnego_mech_operations`, `struct spnego_mech_ctx`, `spnego_krb5_operations`, and `spnego_mskrb5_operations`.

## Control Flow

There is no executable flow. `spnego.c` fills `spnego_mech_ctx` entries with operation pointers and parameters, calls `setup`, and later calls `handle_authen`. Mechanism implementations call the `spnego_encode_t` callback to package their output token.

## State and Persistence Behavior

The header defines context fields for OID metadata, private mechanism state, and Kerberos keytab/service parameters. Actual storage is the static context array in `spnego.c`.

## Dependencies and Integration Points

It is included by `spnego.c` and `spnego_krb5.c` and depends on `ksmbd_spnego_auth_out` being visible through surrounding includes.

## Risks and Edge Cases

The Kerberos parameter fields are typed as `void *` despite holding string pointers, weakening compile-time checks. Adding mechanisms requires increasing the enum and ensuring every slot has valid operations before `spnego_init` iterates it.

## Test Signals

Build coverage with and without Kerberos, plus compiler warnings under stricter pointer diagnostics, are the key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/spnego_mech.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/tree_conn.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/tree_conn.c

## Purpose

`tree_conn.c` authorizes and creates SMB tree connections between authenticated accounts and configured shares. It checks session capacity, bad-password policy, share existence, connection limits, host allow/deny maps, guest restrictions, and user access maps before binding a tree connection into session state. The source was read as a complete 227-line file.

## Important APIs, Types, and Functions

Public functions are `tcm_handle_tree_connect`, `tcm_handle_tree_disconnect`, and `tcm_tree_conn_free`. Internal helper `new_ksmbd_tree_conn` allocates a connection object. The file manipulates `ksmbd_tree_connect_request`, `ksmbd_tree_connect_response`, `ksmbd_tree_conn`, share flags, user flags, and global config fields.

## Control Flow

Connect allocates a connection, checks session capacity, resolves the share, mirrors share access flags into connection flags, opens the share connection, evaluates host maps, enforces anonymous/guest restrictions, resolves guest or named users, applies admin/invalid/read/write/valid user maps in precedence order, then binds the connection via `sm_handle_tree_connect`. Error paths free the connection and release share/user references. Disconnect delegates to session management.

## State and Persistence Behavior

The file creates in-memory tree connection objects. Long-lived state is retained in session lists and share connection counters until disconnect/free. It clears a share's update flag after a successful bind.

## Dependencies and Integration Points

It depends on session, share, user, tools, and kernel IPC structs. It is invoked by the mountd worker's tree-connect and tree-disconnect IPC handlers.

## Risks and Edge Cases

Error cleanup calls both `tcm_tree_conn_free(conn)` and separate `shm_close_connection(share)` / `put_ksmbd_share(share)`; because `conn->share` is only assigned on success this is intentional but fragile. Access-map return conventions distinguish absent maps from explicit misses. Guest fallback depends on configured guest users existing in the user manager.

## Test Signals

Exercise each response status: no share, no user, invalid user, host denied, too many sessions, too many share connections, guest denied, admin/read/write-list overrides, reload update flag clearing, and disconnect idempotency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/tree_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/user.c -->
# sources/user-network-fs/ksmbd-tools/tools/management/user.c

## Purpose

`user.c` manages ksmbd user records loaded from the password database and synthesized guest accounts. It stores decoded password hashes, uid/gid/supplementary groups, login flags, failed-login state, and ref-counted lifetime. The source was read as a complete 471-line file.

## Important APIs, Types, and Functions

Public APIs include `usm_init`, `usm_destroy`, `usm_add_new_user`, `usm_add_guest_account`, `usm_lookup_user`, `get_ksmbd_user`, `put_ksmbd_user`, `usm_remove_user`, `usm_remove_all_users`, `usm_update_user_password`, `usm_user_name`, `usm_iter_users`, `usm_handle_login_request`, `usm_handle_login_request_ext`, and `usm_handle_logout_request`.

## Control Flow

Password parsing calls `usm_add_new_user` or `usm_update_user_password`. New user creation resolves uid/gid with `getpwnam`, decodes the base64 password hash, and collects supplementary groups with `getgrouplist`. Login lookup returns the hash, account, uid/gid, flags, and extension marker when groups exist; null or bad-user login may map to the configured guest account. Extended login responses copy supplementary group IDs into the variable payload.

## State and Persistence Behavior

User state is in-memory in `users_table`, protected by `users_table_lock`; each user has an update lock and refcount. Persistent source state is the password database and system passwd/group databases. Failed login count and delayed-session flag persist only for the process lifetime.

## Dependencies and Integration Points

It depends on GLib, POSIX group/passwd APIs, `config_parser.h`, share constants, and kernel IPC structs. The worker login path and tree connection authorization depend on this module.

## Risks and Edge Cases

`base64_decode` appends a NUL byte after GLib allocation assumptions; malformed password text should be tested. Users missing from `/etc/passwd` are accepted with invalid uid/gid, which may be intentional but affects authorization. `usm_handle_login_request_ext` copies group payload based on prior sizing assumptions. Failed-login counters are modified without the user's update lock.

## Test Signals

Cover valid users, duplicate users, password updates, missing system accounts, supplementary group payloads, guest mapping, null sessions, failed-password delay thresholds, UTF-8/colon username validation, and concurrent lookup/remove.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/management/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/meson.build -->
# sources/user-network-fs/ksmbd-tools/tools/meson.build

## Purpose

`tools/meson.build` is the Meson build definition for `ksmbd.tools`. It declares the common source list, conditionally adds SPNEGO/Kerberos implementation files when `krb5_dep` is found, sets path defines, links command-specific internal libraries, and installs the resulting libexec executable.

## Important APIs, Types, and Functions

Important Meson objects are `ksmbd_tools_files`, `executable('ksmbd.tools', ...)`, `include_dirs`, `glib_dep`, `krb5_dep`, `asn1_lib`, `pthread_lib`, and link targets `addshare_lib`, `adduser_lib`, `control_lib`, and `mountd_lib`.

## Control Flow

At configuration time Meson checks `krb5_dep.found()`. At build time it compiles the selected files and links the executable. Runtime control remains in `tools.c`.

## State and Persistence Behavior

No runtime state. Build-time persistence is the source list, `SYSCONFDIR`, `RUNSTATEDIR`, dependency graph, and installation directory.

## Dependencies and Integration Points

It must match the Autotools source selection in `Makefile.am`. It also integrates the project-level `asn1_lib` dependency while the local ASN.1 source is included only for krb5-enabled builds.

## Risks and Edge Cases

Differences from `Makefile.am` can alter behavior across build systems. Passing `krb5_dep` in dependencies even when not found depends on Meson's dependency object semantics. Optional Kerberos source selection must keep headers and symbols consistent.

## Test Signals

Run Meson configure/build on Linux with krb5 present and absent, inspect `ksmbd.tools` link dependencies, and verify installed libexec path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/tools.c -->
# sources/user-network-fs/ksmbd-tools/tools/tools.c

## Purpose

`tools.c` is the shared entry point and utility layer for ksmbd-tools. It dispatches `ksmbd.tools` behavior by executable basename, owns logging selection, exposes charset/base64/string helpers, loads and removes global configuration state, initializes mountd subsystems, and prints version information. The source was read as a complete 381-line file.

## Important APIs, Types, and Functions

Public/shared functions include `__pr_log`, `pr_logger_init`, `set_log_level`, `pr_hex_dump`, `base64_encode`, `base64_decode`, `ksmbd_gconvert`, `gptrarray_to_strv`, `gptrarray_to_str`, `gptrarray_printf`, `set_conf_contents`, `load_config`, `remove_config`, `set_tool_main`, `get_tool_name`, `show_version`, and `main`. Global variables are `log_level`, `ksmbd_health_status`, and `tool_main`.

## Control Flow

`main` derives the basename and calls `set_tool_main`, which selects addshare, adduser, control, or mountd. `load_config` initializes user/share state, parses password and SMB config, and, for mountd, initializes sessions, RPC, IPC, SPNEGO, and worker pool. `remove_config` tears these down in reverse. Logging defaults to stdio and can switch to syslog.

## State and Persistence Behavior

Process state includes logger mode, health status, selected tool function, user/share/session/RPC/IPC/SPNEGO/worker subsystems, and config-derived globals. `set_conf_contents` writes configuration files with owner/group-limited mode.

## Dependencies and Integration Points

It links every major ksmbd-tools subsystem and the command-specific `*_main` functions. It depends heavily on GLib helpers through `tools.h` and config/management modules.

## Risks and Edge Cases

`base64_decode` writes a trailing NUL at `ret[*dstlen]`, assuming GLib provides enough room. `ksmbd_gconvert` retries UTF-16/UCS-2 aliases but returns NULL after logging conversion errors. Startup ordering is significant: SPNEGO sees parsed global Kerberos config, and worker pool starts after IPC/RPC initialization.

## Test Signals

Test basename dispatch, each tool mode's config lifecycle, syslog/stdout logging, charset conversion fallback, config file creation permissions, mountd init/teardown order, and version output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/tools/tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cuse.c -->
# sources/user-network-fs/libfuse/example/cuse.c

## Purpose

`cuse.c` is a libfuse CUSE example that implements a character device backed by a process-local resizable memory buffer. It demonstrates low-level CUSE callbacks, unrestricted ioctl retry flows, and command-line parsing for major/minor/device name. The source was read as a complete 335-line file.

## Important APIs, Types, and Functions

Important callbacks are `cusexmp_init`, `cusexmp_open`, `cusexmp_read`, `cusexmp_write`, and `cusexmp_ioctl`, registered in `cusexmp_clop`. Helpers include `cusexmp_resize`, `cusexmp_expand`, `fioc_do_rw`, `cusexmp_process_arg`, and `main`. State is `cusexmp_buf` and `cusexmp_size`.

## Control Flow

`main` parses options, requires `--name` unless showing help, builds `DEVNAME=...`, sets `CUSE_UNRESTRICTED_IOCTL`, and calls `cuse_lowlevel_main`. Reads and writes clamp/expand the global buffer. Ioctl dispatch handles restricted `FIOC_GET_SIZE`/`FIOC_SET_SIZE` and unrestricted `FIOC_READ`/`FIOC_WRITE` by using `fuse_reply_ioctl_retry` to request user buffers before replying with iovecs.

## State and Persistence Behavior

All device contents are volatile memory in a single global buffer. There is no synchronization, so multi-threaded access can race in this demonstration program.

## Dependencies and Integration Points

It depends on `cuse_lowlevel.h`, `fuse_opt.h`, and the shared `ioctl.h` contract used by client examples.

## Risks and Edge Cases

Pointer arithmetic on `void *` relies on compiler extensions. Concurrent read/write/ioctl resizing can race. `strncat` may truncate long names. Offset plus size arithmetic can overflow for extreme requests.

## Test Signals

Run as root with `cuse_client`, exercise size get/set, normal read/write, unrestricted ioctl read/write, missing `--name`, help mode, and large sparse offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cuse_client.c -->
# sources/user-network-fs/libfuse/example/cuse_client.c

## Purpose

`cuse_client.c` is the command-line test client for the `cuse.c` character device example. It opens a device path and exercises size, read, and write ioctls defined in `ioctl.h`. The source was read as a complete 157-line file.

## Important APIs, Types, and Functions

The main helper is `do_rw`, which builds `struct fioc_rw_arg`, allocates a user buffer, calls `ioctl` with `FIOC_READ` or `FIOC_WRITE`, and reports previous/new sizes. `main` parses commands `s`, `r`, and `w`.

## Control Flow

The program opens the device read/write, lowercases the command, parses up to two numeric arguments, and dispatches: `s` gets or sets size, `r` reads size/offset through ioctl and writes data to stdout, and `w` reads stdin then writes through ioctl.

## State and Persistence Behavior

The client stores only transient buffers. Persistent effects are changes to the CUSE server's in-memory buffer for the life of that server.

## Dependencies and Integration Points

It depends on POSIX `open`, `ioctl`, `read` through `fread`, `write` through `fwrite`, and the shared `ioctl.h` ABI.

## Risks and Edge Cases

Argument parsing does not limit the number of trailing numeric parameters even though `param` has two entries, so extra arguments can overrun. It does not validate negative offsets represented through unsigned parsing. Large requested buffers may fail allocation.

## Test Signals

Use it against a running `cuse` device for size get/set, stdin writes, short reads past EOF, invalid commands, invalid numeric arguments, and oversized argument counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cuse_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cxxopts.hpp -->
# sources/user-network-fs/libfuse/example/cxxopts.hpp

## Purpose

`cxxopts.hpp` is a vendored single-header C++ command-line option parser, version 2.2.1. It provides value conversion, option specification, parse results, positional argument mapping, and help text formatting for C++ examples. The source was read as a complete 2114-line file.

## Important APIs, Types, and Functions

Core public types are `cxxopts::Options`, `OptionAdder`, `ParseResult`, `OptionValue`, `KeyValue`, `Value`, and exception classes such as `option_exists_error`, `option_not_exists_exception`, `missing_argument_exception`, and `argument_incorrect_type`. The `value<T>()` helpers create typed storage. The `values` namespace implements integer, boolean, string, vector, optional, and stream-based parsing. Help-related structs include `HelpOptionDetails` and `HelpGroupDetails`.

## Control Flow

Users create `Options`, add options through `add_options()`, optionally configure positional parsing, and call `parse(argc, argv)`. `ParseResult::parse` walks argv, handles `--`, long options with optional `=`, clustered short options, implicit/default values, positional consumption, and unrecognized-option retention when enabled. After parsing explicit arguments it applies defaults. Help generation formats option names and wrapped descriptions by group.

## State and Persistence Behavior

All state is in-memory: maps from short/long names to shared `OptionDetails`, parse results keyed by option details, positional vectors, help groups, and optional externally referenced value storage. The parser mutates `argc/argv` to retain unconsumed arguments.

## Dependencies and Integration Points

It depends only on the C++ standard library unless `CXXOPTS_USE_UNICODE` enables ICU-backed string width handling. It is a library-style header; examples can include it directly without a separate build target.

## Risks and Edge Cases

Regex-based parsing defines the accepted option grammar and can reject unusual but valid-looking CLI forms. `OptionValue::as<T>` uses `dynamic_cast` unless RTTI is disabled, so requested types must match the declared value type. Integer parsing has explicit overflow checks, but command-line mutation and external storage lifetimes are caller responsibilities. Vendored code may diverge from upstream fixes.

## Test Signals

Parser tests should cover short clusters, long `--name=value`, implicit bools, missing required arguments, defaults, vector delimiters, positional parsing, `--` passthrough, unrecognized options, help formatting, and integer overflow/hex parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/cxxopts.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello.c -->
# sources/user-network-fs/libfuse/example/hello.c

## Purpose

`hello.c` is the minimal high-level libfuse filesystem example. It exposes a root directory and one read-only file whose name and contents are configurable through command-line options. The source was read as a complete 184-line file.

## Important APIs, Types, and Functions

Callbacks in `hello_oper` are `hello_init`, `hello_getattr`, `hello_readdir`, `hello_open`, and `hello_read`. Option parsing uses `struct options`, `option_spec`, `fuse_opt_parse`, and `show_help`.

## Control Flow

`main` sets default duplicated strings, parses options, optionally appends `--help`, and calls `fuse_main`. FUSE invokes path-based callbacks: `getattr` returns directory or file metadata, `readdir` emits `.`, `..`, and the configured file, `open` enforces read-only access, and `read` slices the configured content by offset/size.

## State and Persistence Behavior

State is the static `options` struct and kernel cache settings. `hello_init` enables `kernel_cache` and toggles an async-read feature flag as an API demonstration. No data is persisted.

## Dependencies and Integration Points

It depends on the high-level `fuse.h` API and demonstrates option parsing via `fuse_opt`.

## Risks and Edge Cases

Callbacks compare `path + 1` without checking that the path is at least `/x`, which is normal for FUSE paths but still assumption-based. The filesystem is read-only and cannot reflect runtime option changes. Defaults are heap allocated so `fuse_opt_parse` can replace/free them.

## Test Signals

Mount, list root, stat/read the configured file, verify non-existent paths return ENOENT, write opens return EACCES, custom `--name` and `--contents` work, and help output preserves FUSE help behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello_ll.c -->
# sources/user-network-fs/libfuse/example/hello_ll.c

## Purpose

`hello_ll.c` is the minimal low-level libfuse filesystem example. It exposes inode 1 as root and inode 2 as a read-only `hello` file, plus simple xattr callback demonstrations. The source was read as a complete 297-line file.

## Important APIs, Types, and Functions

Low-level callbacks are `hello_ll_init`, `hello_ll_lookup`, `hello_ll_getattr`, `hello_ll_readdir`, `hello_ll_open`, `hello_ll_read`, `hello_ll_getxattr`, `hello_ll_setxattr`, and `hello_ll_removexattr`. Helpers include `hello_stat`, `dirbuf_add`, `reply_buf_limited`, and the manual session setup in `main`.

## Control Flow

`main` parses FUSE cmdline options, handles help/version, creates a session, installs signal handlers, mounts, daemonizes, and enters single-threaded or multi-threaded loops. Lookup maps root/name to inode 2, getattr emits fixed stat data, readdir builds a packed directory buffer, open enforces read-only access, read replies from `hello_str`, and xattr callbacks accept only hard-coded names/values.

## State and Persistence Behavior

The filesystem has no mutable storage besides process-global constants. Kernel attr and entry caches are set to one second in lookup/getattr replies.

## Dependencies and Integration Points

It depends on `fuse_lowlevel.h` and demonstrates the lower-level session API rather than `fuse_main`.

## Risks and Edge Cases

The file asserts expected inode values in read/xattr paths, so malformed internal calls abort instead of returning errors. Directory buffers are rebuilt per request and allocated with `realloc` without failure checks, acceptable for an example but not production.

## Test Signals

Mount and verify lookup/stat/readdir/read, xattr get/set/remove with accepted and rejected names, help/version paths, single-thread and multi-thread loops, and non-read-only open denial.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello_ll_uds.c -->
# sources/user-network-fs/libfuse/example/hello_ll_uds.c

## Purpose

`hello_ll_uds.c` adapts the low-level hello filesystem to custom FUSE I/O over a Unix domain stream socket. It demonstrates `fuse_session_custom_io` callbacks for reading, writing, and splice sending FUSE packets outside the normal `/dev/fuse` file descriptor path. The source was read as a complete 367-line file.

## Important APIs, Types, and Functions

Filesystem callbacks mirror `hello_ll.c`: lookup/getattr/readdir/open/read. Custom I/O helpers are `create_socket`, `stream_writev`, `readall`, `stream_read`, and `stream_splice_send`, supplied through `struct fuse_custom_io`. `main` creates a session and binds it to a connected socket.

## Control Flow

The program parses help/version, creates a low-level session, installs signal handlers, waits for a client connection on `/tmp/libfuse-hello-ll.sock`, registers custom I/O, and runs `fuse_session_loop`. `stream_read` first reads a `fuse_in_header`, uses its `len` to read the rest of the packet, and `stream_writev` drains an iovec sequence with repeated `writev` calls.

## State and Persistence Behavior

Filesystem data is static. Runtime socket filesystem state is the socket path under `/tmp`; the program removes an old socket entry before binding but does not explicitly close all descriptors on every failure path.

## Dependencies and Integration Points

It depends on low-level libfuse, `fuse_kernel.h`, Unix sockets, `readv/writev` style I/O, and `splice`. It is built on non-BSD platforms in the example Meson file.

## Risks and Edge Cases

Custom stream framing is sensitive to partial reads/writes and malformed packet lengths. `create_socket` can leak the listening socket on later errors. The socket path is fixed and global. `stream_writev` mutates the caller-provided iovec entries while draining them.

## Test Signals

Run with a custom client that speaks FUSE packets over the socket, test partial packet reads, disconnects, overly large packet lengths, stale socket removal, and normal hello lookup/read behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/hello_ll_uds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/invalidate_path.c -->
# sources/user-network-fs/libfuse/example/invalidate_path.c

## Purpose

`invalidate_path.c` is a high-level libfuse example for path-based cache invalidation. It exposes dynamic files `current_time` and `growing`, gives the kernel very long entry/attr timeouts, then uses `fuse_invalidate_path` from a background thread so changes become visible. The source was read as a complete 292-line file.

## Important APIs, Types, and Functions

Callbacks in `xmp_oper` are `xmp_init`, `xmp_getattr`, `xmp_readdir`, `xmp_open`, and `xmp_read`. Other key functions are `update_fs`, `invalidate`, `update_fs_loop`, `show_help`, and `main`. Options are `--no-notify` and `--update-interval`.

## Control Flow

`main` initializes contents, parses options/cmdline, mounts, daemonizes, starts an updater thread, installs signal handlers, and enters a FUSE loop. The updater refreshes the time string and growing size, then invalidates both paths unless notifications are disabled. Reads serve the current memory state.

## State and Persistence Behavior

State is volatile globals: `time_file_contents`, `grow_file_size`, and options. Kernel cache persistence is intentionally long (`NO_TIMEOUT`) so invalidation behavior is observable.

## Dependencies and Integration Points

It depends on high-level libfuse, low-level cmdline helpers, pthreads, and time APIs.

## Risks and Edge Cases

The updater thread is not joined or explicitly stopped. Dynamic globals are read by callbacks and written by the updater without locking, making races possible. Read calculations can underflow when offsets exceed dynamic file sizes.

## Test Signals

Mount with and without `--no-notify`, repeatedly read/stat both files, vary update interval, exercise single-thread/multi-thread loops, and verify invalidation treats `-ENOENT` as benign.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/invalidate_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl.c -->
# sources/user-network-fs/libfuse/example/ioctl.c

## Purpose

`ioctl.c` is a high-level FUSE ioctl example. It exposes a single regular file `fioc` backed by a resizable memory buffer and supports ordinary read/write/truncate plus restricted size get/set ioctls. The source was read as a complete 230-line file.

## Important APIs, Types, and Functions

Callbacks in `fioc_oper` are `fioc_getattr`, `fioc_readdir`, `fioc_truncate`, `fioc_open`, `fioc_read`, `fioc_write`, and `fioc_ioctl`. Helpers include `fioc_resize`, `fioc_expand`, `fioc_file_type`, `fioc_do_read`, and `fioc_do_write`. Global state is `fioc_buf` and `fioc_size`.

## Control Flow

`fuse_main` dispatches path-based operations. Metadata identifies root or `/fioc`; read/write clamp or expand the buffer; truncate resizes it. `fioc_ioctl` rejects non-file paths and compat mode, then handles `FIOC_GET_SIZE` and `FIOC_SET_SIZE` using kernel-provided data transfer for `_IOR/_IOW` ioctls.

## State and Persistence Behavior

File contents are volatile process memory. No synchronization protects the buffer, so concurrent operations may race.

## Dependencies and Integration Points

It depends on high-level `fuse.h` and `ioctl.h`, and is tested by `ioctl_client.c`.

## Risks and Edge Cases

`void *` arithmetic is compiler-extension dependent. `fioc_resize` return value is ignored by `FIOC_SET_SIZE`, so allocation failure can still return success. Offset plus size can overflow. Lack of locking is acceptable for an example but not production.

## Test Signals

Use `ioctl_client` and normal shell I/O to test size get/set, truncate, read/write, invalid paths, compat ioctl rejection, and allocation-failure behavior if injectable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl.h -->
# sources/user-network-fs/libfuse/example/ioctl.h

## Purpose

`ioctl.h` defines the shared ioctl ABI for libfuse ioctl examples and their clients. It declares restricted size ioctls and unrestricted variable-buffer read/write ioctls, plus the struct used for the latter. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

Definitions are `FIOC_GET_SIZE`, `FIOC_SET_SIZE`, `FIOC_READ`, `FIOC_WRITE`, and `struct fioc_rw_arg` with `offset`, `buf`, `size`, `prev_size`, and `new_size`.

## Control Flow

No executable flow. Kernel and FUSE ioctl handlers interpret the encoded command numbers and shared argument layout.

## State and Persistence Behavior

No state is stored. The header defines the in-memory ABI shared between server and client examples.

## Dependencies and Integration Points

It depends on `sys/types.h`, `sys/uio.h`, and `sys/ioctl.h`. It is included by `ioctl.c`, `ioctl_ll.c`, `cuse.c`, and their clients.

## Risks and Edge Cases

The unrestricted `_IO` commands intentionally do not encode size, so handlers must use retry/iovec mechanisms and are only suitable for CUSE or privileged/low-level demonstrations. ABI layout depends on native pointer and `size_t` widths, so clients and servers must be same-ABI processes.

## Test Signals

Compile all ioctl examples and clients together, verify command numbers, and run cross-command read/write/size tests on the same architecture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_client.c -->
# sources/user-network-fs/libfuse/example/ioctl_client.c

## Purpose

`ioctl_client.c` is the minimal test client for the high-level `ioctl.c` filesystem. It opens the `fioc` file and either reads its current size or sets a new size using restricted ioctls. The source was read as a complete 74-line file.

## Important APIs, Types, and Functions

The single `main` function parses arguments, opens the target file, calls `ioctl(fd, FIOC_GET_SIZE, &size)` or `ioctl(fd, FIOC_SET_SIZE, &size)`, prints results, and closes the file.

## Control Flow

With one file argument it gets size and prints it. With a second argument it parses that argument with `strtoul` and sets size. Errors print via `perror` and return nonzero.

## State and Persistence Behavior

The client has no persistent state. Effects are changes to the mounted example filesystem's in-memory buffer.

## Dependencies and Integration Points

It depends on POSIX open/close/ioctl and `ioctl.h`. It targets the high-level `ioctl.c` example but also exercises compatible restricted ioctls in other examples.

## Risks and Edge Cases

`strtoul` errors and trailing characters are not checked, so invalid sizes can silently parse as zero or partial values. The client does not support unrestricted read/write ioctls.

## Test Signals

Run against a mounted `ioctl` filesystem for get, set, invalid path, invalid size text, permission failures, and repeated size changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_ll.c -->
# sources/user-network-fs/libfuse/example/ioctl_ll.c

## Purpose

`ioctl_ll.c` is a low-level FUSE ioctl example for a single in-memory `fioc` file. It demonstrates both restricted `_IOR/_IOW` size ioctls and unrestricted `_IO` read/write ioctls that require `fuse_reply_ioctl_retry`. The source was read as a complete 472-line file.

## Important APIs, Types, and Functions

Callbacks in `fioc_ll_oper` include `fioc_ll_lookup`, `fioc_ll_getattr`, `fioc_ll_readdir`, `fioc_ll_open`, `fioc_ll_read`, `fioc_ll_write`, and `fioc_ll_ioctl`. Helpers are `fioc_resize`, `fioc_expand`, `fioc_stat`, `dirbuf_add`, `reply_buf_limited`, and `fioc_do_rw`. State is `fioc_buf` and `fioc_size`.

## Control Flow

`main` manually creates a low-level session, mounts, daemonizes, and runs a single-threaded or multi-threaded loop. Lookup maps root/name to inode 2. Read/write operate on the global buffer. Ioctl rejects non-file and compat calls; restricted commands reply directly when buffers are supplied or request retry buffers otherwise; unrestricted read/write first request `fioc_rw_arg`, then user data/output buffers, then reply with iovecs.

## State and Persistence Behavior

Data is volatile memory. The program has no locking around global buffer and size, so multi-threaded runs can race.

## Dependencies and Integration Points

It depends on `fuse_lowlevel.h` and `ioctl.h`, and is paired with `ioctl_ll_client.c`.

## Risks and Edge Cases

Comments note unrestricted ioctls are blocked for regular FUSE mounts by kernel policy in many cases, so behavior differs from CUSE. Allocation failures in `FIOC_SET_SIZE` are ignored. Offset/size overflow and concurrent resizing remain example-level risks.

## Test Signals

Run restricted get/set via both clients, attempt unrestricted read/write and observe expected kernel behavior, test help/version, invalid inode paths, compat ioctl rejection, and multi-thread read/write stress.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_ll_client.c -->
# sources/user-network-fs/libfuse/example/ioctl_ll_client.c

## Purpose

`ioctl_ll_client.c` is the richer client for `ioctl_ll.c`. It can issue restricted size get/set commands and unrestricted read/write commands using `struct fioc_rw_arg`. The source was read as a complete 176-line file.

## Important APIs, Types, and Functions

Helpers are `do_get_size`, `do_set_size`, `do_read`, and `do_write`, all called from `main`. They invoke `FIOC_GET_SIZE`, `FIOC_SET_SIZE`, `FIOC_READ`, and `FIOC_WRITE`.

## Control Flow

`main` expects `<command> <fioc_file> [args]`, opens the file, validates command-specific arity, calls the helper, prints results including previous/new sizes for unrestricted commands, and closes the descriptor.

## State and Persistence Behavior

The client owns temporary buffers only. Writes affect the mounted example's volatile memory.

## Dependencies and Integration Points

It depends on POSIX file/ioctl APIs and the shared `ioctl.h` ABI. It tests the low-level and, for restricted commands, compatible CUSE/high-level examples.

## Risks and Edge Cases

Numeric parsing uses `strtoul`/`strtol` without end-pointer validation. Unrestricted ioctls may fail with `EIO` on normal FUSE mounts due to kernel policy, which is expected by the example comments. Read output treats data as a string by appending NUL.

## Test Signals

Run every command, invalid arity, invalid command, invalid numeric input, unrestricted ioctl failure modes on regular FUSE, and successful unrestricted operations where supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/ioctl_ll_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/memfs_ll.cc -->
# sources/user-network-fs/libfuse/example/memfs_ll.cc

## Purpose

`memfs_ll.cc` is a C++20 low-level libfuse in-memory filesystem example. It implements mutable files and directories with inode/dentry classes, lookup counts, hard links, rename, mkdir/rmdir/unlink, setattr, statfs, directory handles, and multi-threaded session looping. The source was read as a complete 1139-line file.

## Important APIs, Types, and Functions

Core types are `Inode`, `Dentry`, `Inodes`, and `DirHandle`. Low-level callbacks in `memfs_oper` include `memfs_lookup`, `memfs_forget`, `memfs_forget_multi`, `memfs_getattr`, `memfs_setattr`, `memfs_mkdir`, `memfs_unlink`, `memfs_rmdir`, `memfs_rename`, `memfs_link`, `memfs_open`, `memfs_read`, `memfs_write`, `memfs_release`, `memfs_opendir`, `memfs_readdir`, `memfs_releasedir`, `memfs_statfs`, and `memfs_create`.

## Control Flow

The global `Inodes` table starts with root. Create/mkdir allocate an inode, create a dentry, attach it to the parent, and reply with entry data. Lookup finds a child dentry and increments lookup count. Read/write operate on `Inode::content`. Opendir snapshots children into a `DirHandle`; readdir serializes that snapshot. Forget decrements lookup count and erases inodes when it reaches zero. Rename locks global and parent directories, removes existing targets as needed, and moves by creating a new dentry for the same inode.

## State and Persistence Behavior

All filesystem data is memory resident in the global inode table, inode content vectors, dentry vectors, attributes, link counts, and lookup counts. There is no disk persistence. Attribute and entry timeouts are zero, forcing fresh kernel queries.

## Dependencies and Integration Points

It depends on C++ STL containers/locks/atomics and `fuse_lowlevel.h`. Meson builds it when C++ is available on non-DragonFly platforms.

## Risks and Edge Cases

Locking is complex and not fully consistent: some methods use inode mutexes, some attr mutexes, and some call `Inodes.find` while holding `Inodes.lock`. `memfs_link` stores a raw dentry pointer from a `unique_ptr` that is destroyed at function exit, causing a dangling directory entry. `memfs_mkdir` cleanup calls `erase_locked` without visibly holding the global lock on that path. `memfs_forget_multi` decrements lookup counts but does not erase zero-count inodes. Removal decrements nlink but does not erase unreferenced content by link count.

## Test Signals

High-value tests are fsx-style create/write/read/truncate/unlink, mkdir/rmdir non-empty, hard link lifetime, rename overwrite and cross-directory rename, lookup/forget accounting, readdir snapshot behavior, chmod/chown/utimens/truncate through setattr, multi-thread stress, and sanitizer runs for dangling dentry/use-after-free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/memfs_ll.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/meson.build -->
# sources/user-network-fs/libfuse/example/meson.build

## Purpose

`example/meson.build` declares libfuse example executables and their platform-specific inclusion rules. It builds simple C examples, threaded notification examples, Linux service examples, and optional C++ examples without installing them. The source was read as a complete 71-line file.

## Important APIs, Types, and Functions

Important variables are `examples`, `single_file_examples`, and `threaded_examples`. Meson constructs include `configure_file`, `foreach ex : examples`, `foreach ex : single_file_examples`, `foreach ex : threaded_examples`, `add_languages('cpp', ...)`, and `executable(...)`.

## Control Flow

At configure time Meson selects examples based on `platform`: non-BSD adds `passthrough_ll`, `hello_ll_uds`, and `null`; Linux adds socket units and service examples; threaded examples always link `thread_dep`; C++ examples build when the compiler is available and platform is not DragonFly.

## State and Persistence Behavior

No runtime state. It generates socket unit files from templates for Linux-only examples and records build graph policy.

## Dependencies and Integration Points

It integrates `libfuse_dep`, `thread_dep`, and generated `private_cfg` files. It is the build entry for many files researched in this subset.

## Risks and Edge Cases

Platform filters are coarse and can accidentally include examples unsupported by a specific Unix variant. C++ language enablement is optional, so `memfs_ll` coverage depends on toolchain availability. Build lists must be updated when example source files are added or renamed.

## Test Signals

Run Meson configure/build on Linux, BSD-like platforms, and without a C++ compiler; verify expected targets are present/absent and generated socket files exist only where intended.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_inval_entry.c -->
# sources/user-network-fs/libfuse/example/notify_inval_entry.c

## Purpose

`notify_inval_entry.c` is a low-level libfuse example for dentry invalidation. It exposes one file whose name changes to the current time and demonstrates `fuse_lowlevel_notify_inval_entry`, `fuse_lowlevel_notify_expire_entry`, and `fuse_lowlevel_notify_increment_epoch`. The source was read as a complete 427-line file.

## Important APIs, Types, and Functions

Callbacks are `tfs_init`, `tfs_lookup`, `tfs_forget`, `tfs_getattr`, and `tfs_readdir`. Other important functions are `update_fs`, `update_fs_loop`, `show_help`, and `main`. Options are `--no-notify`, `--update-interval`, `--timeout`, `--only-expire`, and `--inc-epoch`.

## Control Flow

`main` parses options, rejects mutually exclusive expire/epoch modes, initializes the file name, creates and mounts a low-level session, daemonizes, records the main thread, starts an updater thread, and runs the FUSE loop. Lookup increments `lookup_cnt`; forget decrements it. The updater saves the old name, updates to the new name, and if the kernel has a lookup, invalidates/expires/increments epoch for cached dentries.

## State and Persistence Behavior

State is volatile globals: `file_name`, `file_ino`, `lookup_cnt`, options, and `main_thread`. Kernel cache entries persist for `options.timeout` unless notifications invalidate or expire them.

## Dependencies and Integration Points

It depends on low-level libfuse, pthreads, signal handling, and time APIs. It is built as a threaded example.

## Risks and Edge Cases

`lookup_cnt` and `file_name` are shared across FUSE and updater threads without locks. The updater handles `-ENOSYS` by exiting the session and signalling the main thread, but other notification failures are asserted. There is no updater join at shutdown.

## Test Signals

Compare behavior with `--no-notify`, default invalidation, `--only-expire`, and `--inc-epoch`; test old-name stat behavior across timeout intervals, ENOSYS handling on older kernels, and lookup/forget count changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_inval_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_inval_inode.c -->
# sources/user-network-fs/libfuse/example/notify_inval_inode.c

## Purpose

`notify_inval_inode.c` is a low-level libfuse example for inode data/attribute cache invalidation. It exposes `current_time`, keeps file data cached, updates the backing content in a background thread, and calls `fuse_lowlevel_notify_inval_inode` so later reads fetch updated contents. The source was read as a complete 402-line file.

## Important APIs, Types, and Functions

Callbacks are `tfs_init`, `tfs_destroy`, `tfs_lookup`, `tfs_forget`, `tfs_getattr`, `tfs_readdir`, `tfs_open`, and `tfs_read`. Other key functions are `update_fs`, `update_fs_loop`, `show_help`, and `main`. Globals include `file_contents`, `lookup_cnt`, `file_size`, and atomic `is_stop`.

## Control Flow

`main` parses options, initializes contents, creates/mounts a low-level session, daemonizes, starts the updater thread, and enters the FUSE loop. Lookup increments lookup count and gives very long attr/entry timeouts. Open sets `keep_cache`. The updater refreshes the time string and, if notification is enabled and the kernel knows the inode, invalidates the inode's whole cached range.

## State and Persistence Behavior

All file data is volatile globals. Kernel cache persistence is intentionally long (`NO_TIMEOUT`) unless invalidated. `tfs_destroy` flips `is_stop` so the updater can exit after session teardown.

## Dependencies and Integration Points

It depends on low-level libfuse, pthreads, C11 atomics, and time APIs. It is built as a threaded example.

## Risks and Edge Cases

`lookup_cnt`, `file_contents`, and `file_size` are not protected by locks. The updater accepts ENOENT/EBADF/ENODEV during unmount but aborts on other notification errors. The error message mentions `notify_store` despite calling `notify_inval_inode`, a minor diagnostic mismatch.

## Test Signals

Run with and without `--no-notify`, repeatedly read cached contents, vary update interval, unmount during updates, check acceptable notification errors, and run under thread sanitizer to observe demonstration-level data races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_inval_inode.c -->
