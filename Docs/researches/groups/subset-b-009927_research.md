# subset-b-009927 Research

Grouped research for Samba `source4/kdc` Kerberos password-change, MIT KDB, PAC, and SDB/HDB bridge files. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service-heimdal.c -->
## sources/user-network-fs/samba/source4/kdc/kpasswd-service-heimdal.c

Purpose: Heimdal-flavoured request handler for the authenticated kpasswd payload after `kpasswd-service.c` has accepted and unwrapped the AP-REQ. It implements version 1 password change and RFC3244/Microsoft set-password semantics, then formats an authenticated kpasswd reply.

Important APIs and functions: `kpasswd_handle_request()` obtains `auth_session_info` from GENSEC, rejects TGT misuse with `kpasswd_check_non_tgt()`, then dispatches to `kpasswd_change_password()` for `KRB5_KPASSWD_VERS_CHANGEPW` or `kpasswd_set_password()` for `KRB5_KPASSWD_VERS_SETPW`. `kpasswd_change_password()` requires an initial ticket via `gensec_krb5_initial_ticket()` and delegates the actual SAMDB update to `samdb_kpasswd_change_password()`. `kpasswd_set_password()` decodes `ChangePasswdDataMS`, converts the password from UTF-8 to UTF-16, builds/unparses target principals, classifies service principals by component count, and calls `kpasswd_samdb_set_password()`.

Control flow: malformed set-password ASN.1 yields a kpasswd authenticated error reply rather than a transport failure. Missing target realm/name pairs are rejected as malformed. If no target principal is supplied, set-password falls back to self password change. For target principal changes, the function always builds a normal password-change reply using the NTSTATUS/reject reason from SAMDB.

State and persistence: no durable state is held locally; password changes persist through SAMDB helper calls. Per-request state is talloc-scoped, with Heimdal allocated structures released by `free_ChangePasswdDataMS()` and `krb5_free_principal()`.

Dependencies and integration: depends on Heimdal generated `ChangePasswdDataMS` decode/free helpers, GENSEC Kerberos ticket properties, Samba loadparm iconv handles, `kpasswd-helper`, and `kpasswd_glue`.

Risks: target principal parsing and service-principal classification affect whether SAMDB treats a password set as a user or service account operation. String conversion failure returns hard kpasswd errors. Initial-ticket enforcement is security critical for self-service password changes.

Test signals: exercise change-password with non-initial and initial tickets, RFC3244 set-password with and without target realm/name, malformed ASN.1, service principal targets, and password-policy rejection strings/dominfo mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service-heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service-mit.c -->
## sources/user-network-fs/samba/source4/kdc/kpasswd-service-mit.c

Purpose: MIT Kerberos variant of the decoded kpasswd request handler. It mirrors the Heimdal path but uses MIT decode APIs and a local simple ASN.1 fallback for RFC3244 set-password requests that omit optional target principal and realm.

Important APIs and functions: external `decode_krb5_setpw_req()` parses MIT set-password structures. `decode_krb5_setpw_req_simple()` manually reads `SEQUENCE`/context-0 octet-string password via Samba ASN.1 helpers. `kpasswd_change_password()` enforces initial-ticket use and calls `samdb_kpasswd_change_password()`. `kpasswd_set_password()` converts password bytes to UTF-16, validates target realm/name pairing, unparses MIT principals, calls `kpasswd_samdb_set_password()`, and always serializes `kpasswd_make_pwchange_reply()` on SAMDB outcomes. `kpasswd_handle_request()` performs session extraction, TGT rejection, and version dispatch.

Control flow: MIT parser success gives password and optional target principal. Parser failure falls back only to the simple no-target packet shape; if that also fails, the client receives `KRB5_KPASSWD_MALFORMED` in an authenticated reply. No target principal means self-change, preserving initial-ticket enforcement. Targeted set-password skips initial-ticket check and relies on SAMDB authorization from `session_info`.

State and persistence: local state is transient and talloc/krb5 allocated. Persistent changes are made only by `samdb_kpasswd_change_password()` or `kpasswd_samdb_set_password()`.

Dependencies and integration: uses MIT krb5 principal APIs, Samba ASN.1 utilities, GENSEC, `kpasswd-helper`, `kpasswd_glue`, loadparm iconv configuration, and SAMDB password helpers.

Risks: the fallback decoder intentionally accepts a minimal structure; tests must ensure it cannot accidentally accept malformed targeted requests. `target_principal_string` allocation uses MIT free semantics, while other strings are talloc/SAFE_FREE; ownership errors here would be crash-prone. Version constants differ from Heimdal names but must stay wire-compatible.

Test signals: compare MIT and Heimdal behaviour for the same wire payloads, especially no-target RFC3244, target realm-only/name-only rejects, service principal short-name unparse, password policy rejects, and GENSEC session failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service-mit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service.c -->
## sources/user-network-fs/samba/source4/kdc/kpasswd-service.c

Purpose: common kpasswd packet processor. It parses the outer kpasswd framing, accepts the AP-REQ with Samba GENSEC Kerberos, unwraps the encrypted password payload, calls the backend-specific `kpasswd_handle_request()`, wraps the response, and emits the RFC-style reply frame.

Important APIs and functions: `kpasswd_process()` is the sole exported implementation. It validates RODC forwarding (`kdc->am_rodc` returns `KDC_PROXY_REQUEST`), source/destination socket addresses, request length/version/AP-REQ boundaries, server credentials for `kadmin/changepw`, keytab binding through `kdc->kpasswd_keytab_name`, GENSEC local/remote addresses, `gensec_update()`, `gensec_unwrap()`, `kpasswd_handle_request()`, `gensec_wrap()`, `kpasswd_make_error_reply()`, and `smb_krb5_mk_error()` for unauthenticated Kerberos error bodies.

Control flow: after frame validation, the function constructs explicit `kadmin/changepw` credentials bound to the KDC krb5 context so the loaded KDB/DSDB plugin is used. AP-REQ failure and unwrap/wrap failures move to the reply path with kpasswd hard-error semantics. Handler failures clear the AP-REP and generate a Kerberos error with a kpasswd error blob. Success returns a header with AP-REP length and encrypted response body.

State and persistence: no persistence is performed here. All per-request buffers are under `tmp_ctx`; the caller receives a talloced reply. Credentials deliberately reuse `kdc->smb_krb5_context` to avoid opening a separate database context.

Dependencies and integration: sits between the KDC server network layer, tsocket address handling, Samba credentials, GENSEC Kerberos, `kpasswd-helper`, and MIT/Heimdal-specific `kpasswd_handle_request()` implementations selected at build time.

Risks: frame-length arithmetic is security sensitive; `enc_data_len` includes the header-derived layout and must not underflow. The explicit realm/principal setup prevents match-by-key fallback, so regressions could permit accepting the wrong key. MIT sets the remote address while Heimdal deliberately skips it due to krb5_rd_req behaviour.

Test signals: truncated frames, mismatched total length, unsupported versions, invalid addresses, AP-REQ failures, unwrap/wrap errors, RODC proxying, and successful version 1/RFC3244 round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service.h -->
## sources/user-network-fs/samba/source4/kdc/kpasswd-service.h

Purpose: public interface for Samba's kpasswd service path. It declares the common packet processor and the backend request handler implemented separately for MIT and Heimdal builds.

Important APIs and types: forward-declares `struct gensec_security`. `kpasswd_handle_request()` consumes an already unwrapped password payload plus protocol version and produces a decoded kpasswd reply or error string. `kpasswd_process()` consumes the full wire request, remote/local socket addresses, and datagram flag, then produces the full wire reply.

Control flow and integration: the header defines the contract boundary between network/GENSEC framing (`kpasswd_process`) and password operation semantics (`kpasswd_handle_request`). Only one backend implementation of `kpasswd_handle_request` should be linked.

State and persistence: no state; callers pass `kdc_server`, talloc context, and mutable `DATA_BLOB` output pointers.

Dependencies: relies on KDC server types, `DATA_BLOB`, `TALLOC_CTX`, `tsocket_address`, `krb5_error_code`, and `kdc_code` from included compilation units.

Risks: ABI/prototype drift between MIT and Heimdal C files would break build-time selection. `datagram` is exposed in `kpasswd_process` but currently not used by the implementation, so future UDP/TCP differences need care.

Test signals: compile both MIT and Heimdal configurations and verify callers include this header rather than declaring local prototypes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd_glue.c -->
## sources/user-network-fs/samba/source4/kdc/kpasswd_glue.c

Purpose: SAMDB glue for self-service kpasswd password changes. It converts authenticated Kerberos session information into a user-privileged SAMDB operation and returns Samba password-policy details to the kpasswd layer.

Important APIs and functions: `samdb_kpasswd_change_password()` opens SAMDB with `samdb_connect()` using the caller's `auth_session_info`, logs the account and SID, and invokes `samdb_set_password_sid()` for the primary user SID with `DSDB_PASSWORD_CHECKED_AND_CORRECT`.

Control flow: connection failure returns `NT_STATUS_ACCESS_DENIED` and an error string. `samdb_set_password_sid()` status is copied into `*result`; no-such-user and other failures populate human-readable error strings, but the function itself returns `NT_STATUS_OK` after the SAMDB operation so the caller can encode the policy outcome in the kpasswd reply.

State and persistence: the durable change is the password write through SAMDB. Reject reason and domain password policy info are returned via output pointers for reply formatting. The SAMDB connection is talloc-scoped to `mem_ctx`.

Dependencies and integration: used by MIT/Heimdal kpasswd service handlers and by `mit_samba_kpasswd_change_password()` for MIT KDB password changes. Depends on DSDB/SAMDB, session tokens, primary SID layout, and SAM password policy structures.

Risks: relies on `PRIMARY_USER_SID_INDEX` being valid in the session token. Returning `NT_STATUS_OK` even when the password result failed is intentional but can be misread by callers; they must inspect `*result`.

Test signals: no SAMDB connection, no such user, policy rejects, successful password change, and verification that the write runs as the authenticated user rather than system.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd_glue.h -->
## sources/user-network-fs/samba/source4/kdc/kpasswd_glue.h

Purpose: declaration of the SAMDB password-change helper used by kpasswd and MIT KDB password-change paths.

Important API: `samdb_kpasswd_change_password()` takes loadparm/event contexts, authenticated `session_info`, UTF-16 password blob, output password-policy reject reason/domain info/error string, and an `NTSTATUS *result` for the actual password operation.

Control flow and integration: callers treat a non-OK function return as infrastructure/access failure and a non-OK `result` as an authenticated password-change outcome to encode for the client.

State and persistence: no state in the header; persistence happens in the C implementation via SAMDB.

Dependencies: requires Samba auth, loadparm, tevent, `DATA_BLOB`, SAMR password-policy types, and NTSTATUS definitions from includers.

Risks: the split between return status and result status is subtle and should be documented in callers. Password blob encoding is expected to be UTF-16 before invocation.

Test signals: compile all callers and confirm policy reject paths preserve both `reject_reason` and `dominfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd_glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ktutil.c -->
## sources/user-network-fs/samba/source4/kdc/ktutil.c

Purpose: minimal keytab listing utility used for Samba selftests, not a full ktutil replacement.

Important APIs and functions: `main()` requires a single keytab argument, initializes a Samba krb5 context, opens a relative keytab with `smb_krb5_kt_open_relative()`, iterates entries via `krb5_kt_start_seq_get()`/`krb5_kt_next_entry()`/`krb5_kt_end_seq_get()`, unparses principal names, formats enctypes, and prints `principal (enctype)` lines. `smb_krb5_err()` prints krb5 errors, frees the talloc context, and exits.

Control flow: every krb5 operation is fail-fast. If enctype-to-string fails, the numeric enctype is printed instead. Entries are freed after each iteration.

State and persistence: read-only keytab traversal; no keytab modification. Process state is limited to krb5 context, keytab cursor, and talloc allocations.

Dependencies and integration: depends on Samba krb5 wrapper helpers and is likely consumed by test scripts checking generated keytabs.

Risks: exits immediately on cursor close or keytab close errors, which is appropriate for selftest but unsuitable as a robust administrative tool. Output format is intentionally simple and may be depended on by tests.

Test signals: empty keytab, multiple enctypes, unknown enctype fallback, invalid relative path, and resource cleanup under valgrind/asan.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ktutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.c

Purpose: MIT Kerberos KDB DAL plugin entry point for Samba. It registers the `kdb_function_table` that lets the MIT KDC/kadmind fetch principals, issue PACs, check policy, and change passwords backed by Samba DSDB.

Important APIs and functions: `kdb_samba_init_module()` creates `mit_samba_context` and stores it with `krb5_db_set_context()`. `kdb_samba_fini_module()` retrieves and frees it. Create/destroy return unsupported for kadmin database creation, lock/unlock are no-ops, and `get_age()` returns `time(NULL)`. `kdb_samba_db_free_principal_e_data()` frees the attached `samba_kdc_entry`.

Control flow: MIT calls through `kdb_function_table`, which delegates nearly all real operations to sibling files: principal fetch/iteration, master key shim, key data copy, AS policy/audit, delegation, PAC issue, and password change.

State and persistence: the module context owns Samba loadparm/event/DSDB state via `mit_samba_context`. Persistent data remains in DSDB; the plugin does not implement native MIT database storage.

Dependencies and integration: depends on MIT `<kdb.h>`, Samba `mit_samba`, and `samba_kdc` structures. Installed as `samba.so` under MIT KDB plugin path by `wscript_build`.

Risks: no locking or age tracking means MIT lookaside/cache semantics rely on current-time invalidation rather than real DSDB modification stamps. Unsupported create/destroy/put/delete must remain compatible with kadmin expectations.

Test signals: plugin load/unload, repeated init/fini, principal lookup through MIT KDC, kadmind startup with fake admin principals, and memory ownership of `e_data`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.h -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.h

Purpose: private interface shared by the MIT KDB plugin implementation files.

Important APIs and types: declares context helpers (`ks_get_context`), principal wrappers/free routines, kadmin principal classifiers, DAL methods for get/put/delete/iterate, master-key functions, encrypt/decrypt key-data shims, PAC/policy/delegation hooks, audit hook, and `kdb_samba_change_pwd()`. Defines `PAC_LOGON_INFO` and a portability `discard_const_p` macro.

Control flow and integration: this header mirrors the function table in `kdb_samba.c`, allowing each KDB operation to live in a focused implementation file while satisfying MIT KDB DAL signatures.

State and persistence: no state directly; most declarations accept `krb5_context`, from which `ks_get_context()` recovers the `mit_samba_context` tied to DSDB.

Dependencies: MIT krb5 plugin/KDB headers, Samba `mit_samba_context`, and KDC/PAC abstractions.

Risks: MIT KDB signatures vary across versions; this header is the compatibility choke point. `discard_const_p` can hide const ownership issues and should stay constrained.

Test signals: compile against supported MIT versions with `HAVE_KDB_H`, and verify every function table member has a matching prototype.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_change_pwd.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_change_pwd.c

Purpose: MIT KDB DAL password-change hook that bridges MIT password-change requests into Samba's SAMDB-backed password-change implementation.

Important API: `kdb_samba_change_pwd()` retrieves `mit_samba_context` with `ks_get_context()` and calls `mit_samba_kpasswd_change_password(mit_ctx, passwd, db_entry)`. It ignores MIT master key, key salt tuple, kvno, and keepold inputs because Samba does not use MIT's local key database storage path for password changes.

Control flow: missing plugin context returns `KRB5_KDB_DBNOTINITED`; otherwise the helper result is returned directly.

State and persistence: persistence happens inside `mit_samba_kpasswd_change_password()`, which generates session information and writes to SAMDB. This file holds no durable state.

Dependencies and integration: registered as `.change_pwd` in `kdb_function_table`; depends on `mit_samba.c` and `kpasswd_glue.c` for the real work.

Risks: callers might expect MIT KDB key-generation parameters to be honored. Samba instead relies on DSDB password handling and policy, so divergence from MIT kadmind assumptions should be covered in tests.

Test signals: kadmind password change through the MIT plugin, missing context, policy rejection mapping to KADM5 errors, and verification that kvno/key history are updated by DSDB rather than this hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_change_pwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_common.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_common.c

Purpose: common helpers for the MIT KDB plugin.

Important APIs and functions: `ks_get_context()` retrieves the `mit_samba_context` from MIT's krb5 DB context and resets `errno` for clearer com_err reporting. `ks_data_eq_string()` compares krb5 data components to C strings. `ks_is_kadmin()`, `ks_is_kadmin_history()`, `ks_is_kadmin_changepw()`, and `ks_is_kadmin_admin()` classify special kadmin principals by components.

Control flow: all classifiers are pure checks on principal component count and component bytes. Missing DB context returns NULL.

State and persistence: no persistence. `errno = 0` side effect is deliberate to avoid stale errno in MIT logging.

Dependencies and integration: used by principal lookup, policy checks, and the password-change service restriction logic.

Risks: exact component matching means realm is ignored by these helpers; callers must perform realm checks when needed, as AS policy does for changepw. Resetting global errno is unusual but scoped to the entry point.

Test signals: kadmin/admin, kadmin/history, kadmin/changepw, bare kadmin, different component counts, and empty krb5 data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_masterkey.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_masterkey.c

Purpose: MIT KDB master-key compatibility shim. Samba does not use a MIT master key to encrypt principal keys, so this file supplies dummy success responses where MIT requires master-key APIs.

Important APIs and functions: `kdb_samba_fetch_master_key()` returns success without populating a real key. `kdb_samba_fetch_master_key_list()` allocates a single `krb5_keylist_node` with `ENCTYPE_UNKNOWN` and kvno 1.

Control flow: only allocation failure returns `ENOMEM`; otherwise the dummy list is returned.

State and persistence: no persistent key material. This reinforces that Samba key material is stored and protected by DSDB mechanisms, not MIT KDB master-key wrapping.

Dependencies and integration: used by the MIT KDB function table and key-data decrypt/encrypt shims.

Risks: MIT features expecting real master-key rotation or validation are not supported. The dummy key must be acceptable to the MIT code paths Samba uses.

Test signals: KDC startup, principal key decrypt/encrypt paths, and kadmind operations that ask for master-key lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_masterkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_pac.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_pac.c

Purpose: key-data copy helpers for MIT KDB plugin. Despite the filename, this file handles decrypt/encrypt of KDB key data in Samba's no-master-key model.

Important APIs and functions: `kdb_samba_dbekd_decrypt_key_data()` copies key bytes and optional salt from `krb5_key_data` into `krb5_keyblock`/`krb5_keysalt`. `kdb_samba_dbekd_encrypt_key_data()` copies a keyblock and optional salt into `krb5_key_data`, sets version/kvno/type metadata, and does no cryptographic wrapping.

Control flow: each allocation failure returns `ENOMEM`; partial allocations are freed on immediate failure paths.

State and persistence: the functions copy transient key buffers between MIT representations. Durable storage is still Samba DSDB/SDB.

Dependencies and integration: called by MIT KDB when it needs key material in standard MIT forms. Works in tandem with dummy master-key functions.

Risks: because data is copied unencrypted, memory hygiene and caller free paths matter. Multi-slot key-data assumptions are limited to current key and optional salt at index 1.

Test signals: key data with and without salt, allocation-failure injection, kvno preservation, and freeing decrypted key contents without leaks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_pac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_policies.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_policies.c

Purpose: MIT KDB policy, PAC issue/update, delegation, and AS audit callbacks for Samba.

Important APIs and functions: `kdb_samba_db_check_policy_as()` rejects invalid kadmin clients, detects changepw AS requests, extracts NetBIOS workstation addresses, and calls `mit_samba_check_client_access()`, decoding returned e-data into MIT padata. `kdb_samba_db_issue_pac()` decides whether to generate a fresh PAC (`ks_get_pac`) or update/copy an old PAC (`ks_update_pac`), especially for protocol transition/cross-realm cases. `kdb_samba_db_check_allowed_to_delegate()` and `kdb_samba_db_allowed_to_delegate_from()` bridge constrained delegation checks. `kdb_samba_db_audit_as_req()` updates bad-password counters on success/preauth failure/bad integrity.

Control flow: AS policy prefers canonical client entry principal; `kadmin/*` as a client is denied. Changepw detection requires server principal `kadmin/changepw` in the default realm. PAC issue logs AS versus TGS paths and uses Samba PAC glue. Audit ignores NULL clients to avoid known FAST crash cases.

State and persistence: client access checks may set reject status on `samba_kdc_entry`; audit calls persist bad password count or success accounting through DSDB/SAMDB.

Dependencies and integration: sits between MIT KDC DAL callbacks and `mit_samba.c`, `pac-glue.c`, auth_sam accounting, and generated krb5 padata encoding/decoding.

Risks: padata decode uses an exported but undeclared MIT function. Cross-realm/protocol-transition PAC decisions are subtle and security-sensitive. Bad-password accounting only handles selected errors.

Test signals: AS login policy errors with e-data, NetBIOS address handling, password-change AS requests, S4U2Self/S4U2Proxy PAC issue paths, constrained delegation denial, and bad-password counter transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_policies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_principals.c -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_principals.c

Purpose: principal fetch, fake administrative principal creation, principal freeing, and iteration for the MIT KDB plugin.

Important APIs and functions: `ks_get_principal()` delegates to `mit_samba_get_principal()`. `ks_free_principal()` frees MIT principal entries, tl-data, key data with zeroing, and attached `samba_kdc_entry`. `ks_get_master_key_principal()` returns a disabled dummy K/M entry. `ks_create_principal()` synthesizes temporary principals with random salt/password-derived AES256 keys. `ks_get_admin_principal()` creates fake `kadmin/admin` and `kadmin/history` entries. `kdb_samba_db_get_principal()` handles special principals, marks `kadmin/changepw` with `KRB5_KDB_PWCHANGE_SERVICE` and short lifetime, and otherwise fetches from DSDB. Put returns success without storing; delete returns database-in-use; iterate walks Samba keys.

Control flow: special MIT/kadmin principals are intercepted before DSDB lookup. Iteration calls the supplied callback for each converted DSDB entry until callback error or no-entry.

State and persistence: real entries are transient MIT wrappers around DSDB records. Synthetic admin/master principals are in-memory only. Put/delete do not mutate DSDB.

Dependencies and integration: depends on `mit_samba_get_principal()`, generated random password/salt helpers, MIT krb5 key derivation, and `samba_kdc_entry` lifetime rules.

Risks: a bug in free logic can leak or double-free attached Samba entry contexts. Synthetic admin principals must be sufficient for kadmind startup without granting unintended ticket use. Put returning success may hide unsupported write operations after password changes.

Test signals: lookup of K/M, kadmin/admin/history/changepw, normal user/server/krbtgt principals, key zeroing on free, iterator callback errors, and unsupported put/delete semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_principals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/wscript_build -->
## sources/user-network-fs/samba/source4/kdc/mit-kdb/wscript_build

Purpose: Waf build definition for the MIT Kerberos KDB Samba plugin library.

Important build API: `bld.SAMBA_LIBRARY('mit-kdb-samba', ...)` compiles the MIT KDB implementation files into a private library with real name `samba.so`, installs it to `${LIBDIR}/krb5/plugins/kdb`, links `MIT_SAMBA`, `com_err`, `krb5`, and `kdb5`, and enables it only when `HAVE_KDB_H` is configured.

Control flow: the source list matches the plugin function table decomposition: module entry, common helpers, master-key shim, key-data shim, policies, principals, and password change.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: bridges Samba's build system with MIT Kerberos plugin discovery expectations. The `realname='samba.so'` value is what MIT KDB loads by plugin name.

Risks: missing or reordered source files can create unresolved function table references. Incorrect install path or realname breaks runtime plugin loading. `HAVE_KDB_H` must accurately reflect MIT KDB development headers.

Test signals: configure with/without MIT KDB headers, inspect installed plugin path/name, and run MIT KDC startup using Samba KDB.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit-kdb/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.c -->
## sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.c

Purpose: IRPC service support for MIT KDC PAC validation requests, primarily Netlogon generic Kerberos PAC validation.

Important APIs and functions: `samba_setup_mit_kdc_irpc()` allocates `mit_kdc_irpc_context`, creates a Samba KDC DB context and krb5 context, registers `KDC_CHECK_GENERIC_KERBEROS` with `IRPC_REGISTER()`, and advertises the `kdc_server` messaging name. `netr_samlogon_generic_logon()` parses `PAC_Validate`, fetches local krbtgt keys from Samba DB, and brute-force checks the supplied PAC checksum/signature with `check_pac_checksum()`.

Control flow: unsupported generic message types and malformed checksum/signature lengths return invalid parameter. krbtgt principal lookup failures return logon failure. Checksum verification succeeds if any krbtgt key validates the KDC signature.

State and persistence: no durable writes. It reads krbtgt keys from DSDB and updates the DB current time opaque before fetches for gMSA/time-sensitive logic.

Dependencies and integration: used by Samba process messaging/IRPC, Netlogon PAC validation NDR, `samba_kdc_fetch()`, gMSA current time, and krb5 principal creation.

Risks: signature-length validation is security critical. MIT lacks a checksum-to-enctype helper, so the brute-force key loop must stay correct and efficient. Only PAC validation is implemented; certificate validation is explicitly unsupported.

Test signals: valid and invalid PAC validation IRPC messages, malformed length combinations, multiple krbtgt enctypes, missing krbtgt, unsupported message type, and registration under `kdc_server`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.h -->
## sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.h

Purpose: small public declaration for registering MIT KDC IRPC handlers.

Important API: `samba_setup_mit_kdc_irpc(struct task_server *task)` returns NTSTATUS after setting up DB/krb5 context and IRPC registration.

Control flow and integration: included by MIT KDC server setup code so the IRPC service can be installed when running with MIT Kerberos.

State and persistence: no state; implementation stores registration context under the task.

Dependencies: requires `struct task_server` and NTSTATUS from includers.

Risks: no include guard in this header as shown; repeated inclusion in a single translation unit could redeclare harmlessly but guard consistency would be preferable.

Test signals: compile inclusion from multiple MIT KDC units and verify setup failure propagates NTSTATUS.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_samba.c -->
## sources/user-network-fs/samba/source4/kdc/mit_samba.c

Purpose: core bridge between MIT KDB callbacks and Samba's KDC/DSDB implementation. It creates runtime context, converts Samba SDB entries to MIT DB entries, handles PAC generation/update/delegation, checks client access, changes passwords, and updates bad-password accounting.

Important APIs and functions: `mit_samba_context_init/free()` set up tevent, loadparm, Samba KDC DB context, MIT krb5 context, and MIT log callback. `mit_samba_get_principal()` maps MIT KDB flags to SDB flags, fetches via `samba_kdc_fetch()`, handles wrong-realm referral principals, and converts via `sdb_entry_to_krb5_db_entry()`. `mit_samba_get_firstkey()/get_nextkey()` iterate DSDB. `mit_samba_get_pac()` calls `samba_kdc_get_pac()`. `mit_samba_update_pac()` verifies old PAC trust and calls `samba_kdc_update_pac()`. `mit_samba_check_client_access()`, `mit_samba_check_s4u2proxy()`, and `mit_samba_check_allowed_to_delegate_from()` bridge access and delegation policy. `mit_samba_kpasswd_change_password()` builds session info from DB user info and calls `samdb_kpasswd_change_password()`. `mit_samba_zero_bad_password_count()` and `mit_samba_update_bad_password_count()` persist logon accounting.

Control flow: principal lookup always forces canonicalization and requests admin data so `samba_kdc_entry` metadata is available. Wrong-realm TGS lookups retry as krbtgt referral lookups; wrong-realm AS TGT lookups let MIT return the client-facing error. PAC update checks krbtgt trust/in-DB state, validates the incoming PAC, maps MIT flags to Samba flags, and treats `ENOATTR` as no-PAC success for MIT.

State and persistence: `mit_samba_context` owns Samba DB context and MIT krb5 context. DSDB current time is refreshed before fetches and copied from entries before policy/PAC/accounting operations. Password and bad-password updates persist through SAMDB/auth_sam helpers.

Dependencies and integration: central integration point for MIT KDB DAL, `samba_kdc_fetch`, `sdb_to_kdb`, `pac-glue`, `db-glue`, `kpasswd_glue`, auth session generation, auth_sam accounting, and gMSA time handling.

Risks: context initialization must load the same smb.conf and DB context as the KDC. Referral retry logic can affect cross-realm ticketing. PAC trust handling for RODCs and cross-realm clients is security-sensitive. Password-change path expects UTF-8 MIT input and converts to UTF-16 for SAMDB.

Test signals: MIT KDC startup, client/server/krbtgt lookup flags, wrong-realm referral TGS, first/next iteration, AS/TGS PAC generation/update, protocol transition, constrained delegation, RBCD, kpasswd through kadmind, bad-password counter updates, and no-PAC accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_samba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_samba.h -->
## sources/user-network-fs/samba/source4/kdc/mit_samba.h

Purpose: public interface for the MIT-Samba bridge library consumed by the MIT KDB plugin.

Important types and APIs: `struct mit_samba_context` stores optional session info, an MIT krb5 context, and a `samba_kdc_db_context`. Function declarations cover context lifecycle, salt/password generation, principal fetch/iteration, PAC get/update/reget, client access checks, S4U2Proxy/RBCD checks, kpasswd password change, bad-password accounting, and PAC requirement checks.

Control flow and integration: this header is the stable boundary between `mit-kdb/*` plugin code and the larger Samba KDC implementation in `mit_samba.c`/`pac-glue.c`.

State and persistence: context points to DSDB-backed KDC state; callers must treat returned MIT DB entries as transient wrappers and free them through KDB hooks.

Dependencies: requires krb5 types, `krb5_db_entry`, `krb5_pac`, Samba KDC DB context, and auth session structures.

Risks: ownership contracts are mostly implicit: PAC pointers, `krb5_db_entry->e_data`, and context-owned cached user info must not be freed by callers incorrectly. API drift with MIT KDB flags can require header updates.

Test signals: compile all MIT plugin files, free/finalize context after operations, and validate each declared function is exercised by the KDB function table or policy path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/mit_samba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-blobs.c -->
## sources/user-network-fs/samba/source4/kdc/pac-blobs.c

Purpose: helper for representing PAC buffers as an ordered list plus fast index by supported PAC type. It lets PAC update code replace, add, remove, and validate buffer types while preserving original buffer order where possible.

Important APIs and functions: `pac_blobs_from_krb5_pac()` reads buffer types from a krb5 PAC, initializes type indexes to `SIZE_MAX`, rejects duplicate supported types, and records original order. `_pac_blobs_ensure_exists()` checks required type presence. `_pac_blobs_replace_existing()` attaches a replacement `DATA_BLOB` for an existing type. `pac_blobs_add_blob()` appends or replaces a type when a non-NULL blob is supplied. `pac_blobs_remove_blob()` removes a type, shifts later entries, and updates indexes.

Control flow: unsupported PAC types remain in the ordered array but are not indexed unless within the supported type range. Replacement does not copy blob data; it stores the caller's pointer. Removal leaves blob storage ownership untouched.

State and persistence: in-memory talloc structure only. Used during PAC update before constructing a new krb5 PAC.

Dependencies and integration: used heavily by `pac-glue.c` validation/update paths. Depends on PAC type constants from generated NDR headers and krb5 PAC type enumeration.

Risks: type range assertions assume all manipulated types fall within `PAC_TYPE_BEGIN..PAC_TYPE_END`. Because blob pointers are borrowed, caller memory contexts must outlive PAC reconstruction. Duplicate PAC buffers are rejected for known supported types.

Test signals: PACs with duplicate known types, unknown types, add existing/new type, remove first/middle/last type, and order preservation when copying trusted PAC buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-blobs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-blobs.h -->
## sources/user-network-fs/samba/source4/kdc/pac-blobs.h

Purpose: declarations and structures for PAC buffer list/index manipulation.

Important types and APIs: `struct type_data` stores PAC type plus optional replacement blob. `struct pac_blobs` stores type index array, ordered type blobs, and count. Public helpers create the structure from krb5 PACs, ensure required types exist, replace existing types, add blobs, and remove blobs. Macros capture type names, source location, and function name for diagnostics.

Control flow and integration: consumers use this header to validate required buffers before constructing a new PAC and to preserve or replace trusted input buffers.

State and persistence: no persistence; the structures are talloc-owned working state.

Dependencies: krb5 PAC APIs, Samba `DATA_BLOB`, generated PAC type constants, and talloc context types.

Risks: consumers must respect borrowed `DATA_BLOB` ownership. The fixed index array size must match the PAC type range constants.

Test signals: build with current generated `ndr_krb5pac.h` and unit-test macro error diagnostics for missing required buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-blobs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-glue.c -->
## sources/user-network-fs/samba/source4/kdc/pac-glue.c

Purpose: main PAC authorization-data glue between Samba account/authn-policy state and Heimdal/MIT KDC PAC APIs. It builds new PAC buffers, validates incoming PACs, updates PACs for TGS/S4U/delegation, manages claims/device info, and enforces authentication policy and RBCD.

Important APIs and functions: low-level builders create `PAC_LOGON_INFO`, `PAC_UPN_DNS_INFO`, NTLM credential info, PAC attributes, requester SID, claims, device info, and constrained delegation blobs. `samba_kdc_encrypt_pac_credentials()` encrypts credential data differently for Heimdal and MIT. `samba_make_krb5_pac()` assembles buffers into a krb5 PAC. `samba_princ_needs_pac()`, `samba_client_requested_pac()`, `samba_krbtgt_is_in_db()`, and `samba_kdc_entry_pac*()` define PAC necessity/trust wrappers. `samba_kdc_get_user_info_from_db()/from_pac()` cache authorization info. `samba_kdc_verify_pac()` validates SID consistency, RODC allowance, and required PAC buffer types. `samba_kdc_get_pac()` generates AS/S4U2Self PACs. `samba_kdc_update_pac()` updates TGS PACs, resource groups, claims, delegation, device/compound identity, and requester SID handling. `samba_kdc_check_device()` and `samba_kdc_check_s4u2proxy_rbcd()` enforce device restrictions and resource-based constrained delegation.

Control flow: new PAC generation obtains DB user info, adds asserted identity/Claims Valid/Fresh Public Key SIDs as appropriate, optionally enforces server authentication policy, builds logon/UPN/claims/requester SID/credential buffers, then adds them to the KDC-created PAC. PAC update first derives user info from a trusted PAC or DB fallback, decides whether device/compound auth and access checks are required, updates delegation info, rebuilds logon/UPN/claims/device buffers, edits an ordered `pac_blobs` view, removes attributes/requester SID where not valid, honors no-PAC account/client policy with `ENOATTR`, then copies replacement or trusted original buffers to the new PAC.

State and persistence: PAC buffers are transient, but cached `info_from_db`, `info_from_pac`, `claims_from_db`, and `claims_from_pac` are stored on `samba_kdc_entry` for the lifetime of the entry. Account policy checks read DSDB; RODC allow/deny and RBCD read DSDB security descriptors. No PAC updates write DSDB directly.

Dependencies and integration: integrates auth_sam, authn_policy, claims transformation, generated NDR PAC structures, krb5 PAC APIs, DSDB trust policy attributes, SID/security descriptor helpers, and `pac-blobs`.

Risks: this is a high-risk security file. PAC trust decisions for RODC/trusts, SID mismatch checks, requester SID enforcement, claims transformation defaults, compound identity conditions, and RBCD access masks all affect authorization. Heimdal/MIT conditional paths differ for checksum/logon-name buffers and credential encryption.

Test signals: AS PAC generation, no-PAC accounts, client requested no PAC, trusted and untrusted RODC PACs, SID mismatch revocation, requester SID missing, S4U2Self, constrained delegation, cross-realm trust claims ingress/egress defaults, compound identity with FAST armor, device restriction audit/status, RBCD security descriptor allow/deny, credential PAC encryption with PKINIT reply key, and buffer ordering/unknown PAC preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-glue.h -->
## sources/user-network-fs/samba/source4/kdc/pac-glue.h

Purpose: public PAC glue interface shared by Heimdal and MIT KDC integration layers.

Important types and APIs: defines `enum samba_asserted_identity`, Samba KDC PAC flags, and `struct samba_kdc_entry_pac` wrapper containing PAC pointer, PAC principal, krbtgt entry, optional local entry, and MIT-only trust boolean. Declares PAC wrapper constructors, PAC necessity and krbtgt trust checks, DB user-info fetch, policy error mapping, client-access check, PAC verify/get/update, device check, and S4U2Proxy RBCD check.

Control flow and integration: callers construct `samba_kdc_entry_pac` for client/device/delegated proxy tickets, then call verify/get/update depending on AS/TGS flow. MIT uses `samba_kdc_entry_pac_from_trusted()` because MIT lacks Heimdal's `krb5_pac_is_trusted()` API.

State and persistence: interface exposes entry-backed caches but performs no persistence in the header.

Dependencies: krb5 PAC/principal types, Samba KDC entries, auth session/audit types, NTSTATUS/WERROR mapping, and generated auth/PAC structures.

Risks: the wrapper invariants are critical: non-NULL PAC must have an associated krbtgt, and trust must be explicit on MIT. Flag meanings must remain aligned between MIT bridge and PAC glue.

Test signals: compile both Heimdal and MIT builds, construct PAC wrappers for absent PAC, trusted PAC, RODC PAC, trust PAC, and validate each public PAC operation rejects invalid wrapper combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/pac-glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/samba_kdc.h -->
## sources/user-network-fs/samba/source4/kdc/samba_kdc.h

Purpose: shared Samba KDC data structures used by DB glue, MIT/Heimdal adapters, and PAC logic.

Important types: `samba_kdc_policy` holds ticket lifetime policy. `samba_kdc_base_context` carries event/loadparm/messaging/SAMDB and current-time pointer used when creating DB contexts. `samba_kdc_db_context` stores DB runtime state, RODC identity, krbtgt metadata, policy, sequence context, and current-time pointer. `samba_kdc_entry` binds an SDB/DSDB record to a KDC entry, carrying LDB message, realm DN, cached PAC/DB user info, claims, authn policies, supported enctypes, reject status, trust/RODC/krbtgt flags, and enforced lifetime data. `CHANGEPW_LIFETIME` defines two-minute lifetime for changepw tickets.

Control flow and integration: these structs are the data backbone passed through `samba_kdc_fetch()`, SDB conversion, MIT `e_data`, Heimdal HDB context, and PAC generation.

State and persistence: structures cache DSDB-derived data for an entry lifetime but do not own durable storage except references to LDB messages and contexts. `current_nttime_ull` is used to align DSDB time-sensitive operations with KDC request time.

Dependencies: time, NTSTATUS, LDB, tevent/loadparm/messaging, DSDB, claims, authn policy, and Kerberos DB adapters.

Risks: lifetime comments matter: `sdb_entry.db_entry` is temporarily valid, while `kdc_entry` references Heimdal/MIT wrapper objects. Incorrect ownership causes use-after-free. Current-time pointer must be set before gMSA/authn policy operations.

Test signals: fetch/free KDC entries under MIT and Heimdal, RODC and trust entries, gMSA current time propagation, changepw ticket lifetime, and cache reuse of info/claims fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/samba_kdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb.c -->
## sources/user-network-fs/samba/source4/kdc/sdb.c

Purpose: memory management and encryption-type derivation for Samba's intermediate SDB entry representation.

Important APIs and functions: `sdb_key_free()`, `sdb_keys_free()`, `sdb_pub_key_free()`, `sdb_pub_keys_free()`, `sdb_certificate_mapping_free()`, `sdb_certificate_mappings_free()`, and `sdb_entry_free()` recursively free and zero SDB structures. `sdb_entry_set_etypes()` derives current etype list from key keytypes. `sdb_entry_set_session_etypes()` builds preferred session etype lists in AES256, AES128, RC4 order based on requested booleans.

Control flow: free helpers tolerate NULL, clear sensitive keyblock contents via krb5 APIs, free principal fields with NULL context, and reset structs after release. Etype setters allocate only when corresponding input exists/flags are requested.

State and persistence: SDB entries are transient conversion objects populated from DSDB. Freeing an SDB entry also detaches and frees its `samba_kdc_entry`, clearing back-pointers.

Dependencies and integration: used by DB fetchers and conversion files (`sdb_to_hdb`, `sdb_to_kdb`) before presenting data to Heimdal/MIT.

Risks: key material zeroing depends on correct helper use. Session etype order influences negotiated service ticket session keys. Attached `samba_kdc_entry` lifetime must not outlive the converted KDC entry incorrectly.

Test signals: free fully and partially populated entries, valgrind/asan leak checks, etype derivation from multi-key accounts, session etype ordering, and double-free resistance through zeroing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb.h -->
## sources/user-network-fs/samba/source4/kdc/sdb.h

Purpose: definition of Samba's KDC database-neutral SDB representation and fetch flags.

Important types: `sdb_salt`, `sdb_key`, `sdb_keys`, `sdb_event`, `sdb_etypes`, `SDBFlags`, `sdb_pub_key`, `sdb_pub_keys`, certificate mapping structures, and `sdb_entry`. `sdb_entry` includes principal, kvno, current/old keys, etypes/session etypes, creation/modification events, validity/password lifetimes, KDC flags, PKINIT key trust data, certificate mappings, object SID, and attached `samba_kdc_entry`.

Important constants: SDB error codes (`SDB_ERR_NOENTRY`, `SDB_ERR_NOT_FOUND_HERE`, `SDB_ERR_WRONG_REALM`) and fetch flags for decrypt, replace, client/server/krbtgt, canonicalization, admin data, kvno, AS/TGS, armor/user2user/cross-realm/S4U, force-canon, and RODC number.

Control flow and integration: SDB is the common shape fetched from Samba DSDB before conversion into Heimdal HDB or MIT KDB entries. `SDB_F_HDB_MASK` documents the subset compatible with Heimdal HDB.

State and persistence: declarations only; SDB values are transient snapshots of DSDB state plus derived metadata.

Dependencies: Kerberos types and generated security SID types.

Risks: `SDBFlags` is asserted to match Heimdal `HDBFlags` size in conversion; layout drift is dangerous. Fetch flag combinations control KDC authorization semantics and must be mapped carefully from MIT/Heimdal callers.

Test signals: compile-time flag/layout checks, fetch flag mapping from AS/TGS/S4U paths, and conversion tests for all optional entry fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb_to_hdb.c -->
## sources/user-network-fs/samba/source4/kdc/sdb_to_hdb.c

Purpose: converts Samba SDB entries into Heimdal `hdb_entry` structures, including keys, flags, events, lifetimes, etypes, key trust, certificate mappings, object SID extension, and Samba KDC context attachment.

Important APIs and functions: `sdb_flags_to_hdb_flags()` maps SDB bitfields to Heimdal HDB flags with size assertion. `sdb_salt_to_Salt()`, `sdb_key_to_Key()`, `sdb_keys_to_Keys()`, and `sdb_keys_to_HistKeys()` copy key material and key history. `sdb_event_to_Event()` copies modifier principals/times. `sdb_pub_key_to_hdb_key_trust_val()` wraps RSA public keys in SubjectPublicKeyInfo for key-trust extension. `sdb_certificate_mappings_to_hdb_ext()` converts PKINIT certificate mappings. `sdb_entry_to_hdb_entry()` performs the whole conversion, replaces HDB extensions, and attaches `samba_kdc_entry` as `h->context`.

Control flow: conversion zero-initializes the output and uses `goto error` cleanup via `free_hdb_entry()` on failures. Optional SDB fields allocate corresponding Heimdal pointers only when present. Old and older keys are added as history when kvno permits. Object SID is serialized as a string octet extension.

State and persistence: no durable writes. The output `hdb_entry` owns copied key/extension data; the attached `samba_kdc_entry` back-pointer is set so later PAC/authn code can recover DSDB metadata.

Dependencies and integration: Heimdal HDB ASN.1 types, Samba krb5 wrappers, SID formatting, SDB definitions, and PAC/KDC entry structures.

Risks: conversion handles sensitive key material and complex ASN.1 allocations. Failure cleanup must free all partially built extensions. Public-key bit/byte length conversion and certificate mapping optional fields are easy to regress. The `ske->kdc_entry = h` back-pointer creates lifetime coupling.

Test signals: existing `source4/kdc/tests/sdb_to_hdb_test.c`, entries with key history, no keys, PKINIT key trust, certificate mapping enforcement modes, SID extension, optional lifetimes, etype/session etype lists, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb_to_hdb.c -->
