# Research: subset-b-009948 Samba source4 RPC server files

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.c -->
# sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.c

## Purpose

This file implements the Samba AD DC server side of the SAMR DCE/RPC interface. It maps SAMR policy handles to Samba `samdb`/LDB state, exposes domain, user, group, alias, display, password-policy, SID/RID lookup, and membership operations, and includes the generated NDR server dispatch table at the end. It is the central bridge between MS-SAMR wire operations and DSDB objects such as users, groups, builtin aliases, foreign security principals, password policy attributes, and account metadata.

## Important APIs, Types, And Functions

The file uses handle states declared in `dcesrv_samr.h`: `samr_connect_state`, `samr_domain_state`, `samr_account_state`, `samr_guid_cache`, and `enum samr_handle`. `dcesrv_samr_Connect*()` opens a SAM database context with caller credentials and returns a connect handle. `dcesrv_samr_OpenDomain()` converts a domain SID into a domain handle with domain DN, role, builtin flag, access mask, loadparm context, GUID caches, and the cached user enumeration array. `dcesrv_samr_OpenUser()`, `OpenGroup()`, and `OpenAlias()` resolve RID-derived SIDs to LDB records and create account handles.

Query and set helpers are macro-heavy. `QUERY_STRING`, `QUERY_UINT`, `QUERY_RID`, `QUERY_APASSC`, `QUERY_BPWDCT`, `QUERY_LHOURS`, and `QUERY_AFLAGS` translate LDB attributes into SAMR info unions. `SET_STRING`, `SET_UINT`, `SET_INT64`, `SET_UINT64`, `SET_AFLAGS`, `SET_LHOURS`, and `SET_PARAMETERS` build replace/delete modifications. Domain info helpers cover levels 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, and 13. User info support is broad: `QueryUserInfo` covers levels 1-17, 20, and 21, while `SetUserInfo` handles account fields and password reset levels 18, 21, 23-26, 31, and 32.

Important database helpers include `dcesrv_samdb_connect_as_user()`, `gendb_search()`, `gendb_search_dn()`, `samdb_search_domain()`, `dsdb_search()`, `dsdb_search_by_dn_guid()`, `dsdb_add_user()`, `dsdb_add_domain_group()`, `dsdb_add_domain_alias()`, `dsdb_lookup_rids()`, `dsdb_enum_group_mem()`, and `samdb_create_foreign_security_principal()`. Password updates are delegated to `samr_set_password()`, `samr_set_password_ex()`, `samr_set_password_buffers()`, and `samr_set_password_aes()` in `samr_password.c`.

## Control Flow

Most RPC operations start with `DCESRV_PULL_HANDLE()` to validate the incoming policy handle type and recover its state. Connect creates a `SAMR_HANDLE_CONNECT`; domain lookup and enumeration then operate on the connect state. `OpenDomain` searches by `objectSid`, determines primary vs BUILTIN domain behavior, initializes caches, and creates a `SAMR_HANDLE_DOMAIN`. Account open/create calls create `SAMR_HANDLE_USER`, `SAMR_HANDLE_GROUP`, or `SAMR_HANDLE_ALIAS` with a domain reference and account DN.

Domain query flow is a level switch selecting the minimal attribute list, an optional DN search, allocation of `union samr_DomainInfo`, and a second level switch that calls the level-specific filler. Domain set flow builds an LDB modify message for supported levels and calls `ldb_modify()`, with a local constraint check for lockout duration/window. Group and alias query/set flows are analogous but smaller, operating on `sAMAccountName`, `description`, and `numMembers`.

Enumeration has distinct paging strategies. `EnumDomainGroups` and `QueryDisplayInfo` cache sorted `objectGUID` values in `samr_guid_cache`, then page by resume/start index and re-read each object by GUID so deleted objects can be skipped without retaining full records. `EnumDomainUsers` instead builds and caches a sorted `samr_SamEntry` array of RID/name pairs on the domain handle; the comment notes this trades memory for faster winbind `getpwent` behavior. Alias enumeration does a direct search, sorts by RID, and resumes by last RID.

Membership calls convert between RIDs, SIDs, DNs, and group `member` values. Group member add/delete resolves the RID inside the domain before modifying `member`. Alias member add can create a foreign security principal when the SID is unknown. User group enumeration reads `primaryGroupID` and `memberOf` extended-DN SIDs, then returns primary plus domain global/universal groups. Display and lookup calls translate between names, RIDs, SIDs, and LSA SID types.

`SetUserInfo` starts an LDB transaction, builds attribute modifications according to the requested level and field mask, calls the password helper when a password field is present, applies `pwdLastSet` changes for expiration flags, then commits or cancels. AES password levels obtain the DCE/RPC transport session key before decrypting. `ValidatePassword` is restricted to TCP or local RPC with privacy auth level and checks complexity/minimum length through `samdb_check_password()`.

## State And Persistence

Persistent state is stored in Samba's SAM database through LDB modifications and DSDB helper calls. The code persists domain policy attributes, account attributes, user/group/alias objects, group memberships, foreign security principals, password hashes, and `pwdLastSet`. In-memory state is talloc-owned by DCE/RPC policy handles: connect handles own caller SAM contexts; domain handles own domain identity, caches, and references to the connect state; account handles own account DN/name/SID and a domain reference. Caches are per-domain-handle and are cleared when a new enumeration starts, when resume input is out of range, on some errors, or when enumeration completes. There is no standalone on-disk persistence outside LDB.

## Dependencies And Integration Points

The file integrates with generated `ndr_samr` RPC definitions, Samba DCE/RPC handle management, DSDB/SAMDB, LDB, LDAP NDR encoding, SID helpers, security descriptors, loadparm role/name settings, password policy helpers, and generated `ndr_samr_s.c` boilerplate. It also integrates behaviorally with winbind clients that depend on SAMR enumeration ordering, with LSA/SAM account type mappings, and with password helper code for encrypted reset buffers.

## Risks And Edge Cases

Access masks are mostly stored but not consistently enforced in this file; many security decisions are delegated to SAMDB/LDB ACLs or explicitly unimplemented with DCE/RPC faults. Enumeration caches can become stale while objects are deleted or modified; the code skips missing/invalid objects, but clients may see gaps or fewer returned entries than requested. `EnumDomainUsers` has a hazard if a nonzero resume handle is supplied without a populated cache; the intended call pattern starts at zero. Several paths assume unique SIDs and treat duplicates as internal corruption. `SetUserInfo` is high risk because field-mask handling, password update side effects, transaction cancellation, and `pwdLastSet` semantics must match Windows-compatible behavior. Some operations intentionally fault or return not supported, which is correct only if generated dispatch and client compatibility expectations align.

## Test Signals

Strong signals include Samba RPC tests for `samr_Connect*`, `LookupDomain`, `OpenDomain`, domain info levels, user/group/alias create/open/query/set/delete, RID/name lookup, paged user/group/display enumeration, membership add/remove including foreign SIDs, and password reset levels 18, 21, 23-26, 31, and 32. Regression tests should cover empty domains, deleted objects during paged enumeration, BUILTIN restrictions, duplicate/invalid SID handling, access-denied mapping from LDB, transaction rollback on password failures, privacy enforcement for `ValidatePassword`, and Windows-compatible sorting by RID.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.h -->
# sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.h

## Purpose

This header defines the private server-side state objects used by the SAMR RPC implementation. It gives `dcesrv_samr.c` and the SAMR password helpers a common model for distinguishing handle types and attaching SAM database, domain, account, access-mask, SID, DN, loadparm, role, and enumeration-cache state to DCE/RPC policy handles.

## Important APIs, Types, And Functions

`enum samr_handle` defines the handle discriminator values consumed by `dcesrv_handle_create()` and `DCESRV_PULL_HANDLE()`: connect, domain, user, group, and alias. `struct samr_connect_state` stores the caller-visible `ldb_context *sam_ctx` and requested access mask for `samr_Connect*`.

`struct samr_guid_cache` stores a paged enumeration cursor: a `handle` field used as caller-specific cache metadata, an entry count, and a talloc-owned array of `struct GUID`. `enum samr_guid_cache_id` allocates cache slots for display info, domain group enumeration, and domain user/group operations. `struct samr_domain_state` ties a domain handle back to its connect state and SAM context, records the domain SID/name/DN, server role, BUILTIN flag, loadparm context, GUID caches, and the cached `samr_SamEntry` array used by user enumeration. `struct samr_account_state` attaches a user/group/alias account handle to its parent domain, SAM context, requested access mask, account SID/name, and account DN.

## Control Flow

The header itself has no executable control flow. Its structures define the lifecycle used by the implementation: connect handles are created first, domain handles reference connect handles, and account handles reference domain handles. Cache structs are initialized when a domain handle is opened and are cleared/reloaded by enumeration calls.

## State And Persistence

All structures are per-RPC-handle runtime state allocated with talloc and released when the handle is closed or the connection ends. They do not persist data themselves. Persistence happens through the `sam_ctx` LDB context that points at Samba's SAM database. The cache arrays are transient snapshots of enumeration identity, not authoritative object state.

## Dependencies And Integration Points

The header depends on `param/param.h` for loadparm types and `libds/common/roles.h` for `enum server_role`. The declarations also assume LDB, SID, GUID, and generated SAMR NDR types are visible from including source files. It is included by the SAMR endpoint implementation and password code through the local RPC server build.

## Risks And Edge Cases

The state model makes handle-type correctness critical; using the wrong `SAMR_HANDLE_*` value would expose incompatible state through a policy handle. The header stores access masks but does not enforce them by itself, so callers must avoid treating the field as sufficient authorization. Cache memory is tied to domain handles, so long-lived handles doing large enumerations can hold significant transient memory. The `void *sam_ctx` fields in domain/account state are less type-safe than the connect state's `struct ldb_context *`.

## Test Signals

Useful signals are compile-time coverage of all SAMR implementation files, RPC tests that open/close each handle type, invalid-handle-type tests that must fail cleanly, leak checks around repeated connect/open/close/enumerate flows, and enumeration tests proving cache reset and talloc ownership behave correctly across resume handles and handle closure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/samr_password.c -->
# sources/user-network-fs/samba/source4/rpc_server/samr/samr_password.c

## Purpose

This file implements SAMR password change and password reset handling for the Samba AD DC RPC server. It supports legacy NTLM-hash based change paths, RC4/confounded password reset buffers, encrypted hash buffers, and AES-based password buffers, while routing the final update through `samdb_set_password()` so domain policy, password history, account state, and DSDB modules remain authoritative.

## Important APIs, Types, And Functions

`log_password_change_event()` builds an `auth_usersupplied_info` record and calls `log_authentication_event()` so SAMR password changes produce consistent audit records. `dcesrv_samr_ChangePasswordUser()` and `dcesrv_samr_OemChangePasswordUser2()` are intentionally not implemented. `dcesrv_samr_ChangePasswordUser4()` handles AES change using PBKDF2 over the old NT hash and caller-provided salt to produce a content decryption key. `dcesrv_samr_ChangePasswordUser_impl()` implements the shared `ChangePasswordUser2`/`3` logic: fetch old NT hash, decrypt the new password with RC4 under that hash, verify the old-password verifier, and call `samdb_set_password()` as the caller.

Reset helpers are used by `dcesrv_samr.c`: `samr_set_password()` decrypts `samr_CryptPassword` with the transport session key and RC4; `samr_set_password_ex()` decrypts a confounded MD5/ARCFOUR buffer; `samr_set_password_buffers()` decrypts encrypted NT/LM hash buffers with `sess_crypt_blob()` and sets hashes directly; `samr_set_password_aes()` decrypts `samr_EncryptedPasswordAES` with Samba's AES-256-CBC-HMAC-SHA512 helper and extracts the password blob.

## Control Flow

Password change calls first connect to SAMDB with system privileges because old password hashes are required for verification. The user is found through `authsam_search_account()` to stay aligned with authentication and bad-password accounting. Once the supplied old credential is verified, the code temporarily swaps the LDB `DSDB_SESSION_INFO` opaque to the caller's session, performs `samdb_set_password()`, restores the previous session info, and commits the transaction. Failures cancel the transaction and are logged.

`ChangePasswordUser4` validates the AES password buffer and PBKDF2 iteration range, derives the content decryption key from the old NT hash and salt, drops to caller privileges for `samr_set_password_aes(..., DSDB_PASSWORD_CHECKED_AND_CORRECT)`, burns the derived key buffer, and commits. The `ChangePasswordUser2` wrapper fills a `ChangePasswordUser3` request and reuses the shared implementation.

Reset helpers follow a simpler decrypt-then-set flow. They obtain or derive the correct session key, enforce weak-crypto policy for RC4 paths when transport encryption is absent, decrypt the supplied buffer in place or into temporary blobs, extract the cleartext password buffer, and call `samdb_set_password()` with either `DSDB_PASSWORD_RESET` or the supplied old-password-checked mode. AES and cleartext blobs are freed or zeroed after use where the code explicitly owns them.

## State And Persistence

Persistent state changes are made only by `samdb_set_password()` and related DSDB modules. This may update password hashes, supplemental credentials, password history, `pwdLastSet`, lockout/bad-password state, and policy-enforced metadata. The file also updates bad password counts through `authsam_update_bad_pwd_count()` on wrong-password outcomes. Runtime sensitive state includes old hashes, session keys, derived AES keys, decrypted password buffers, and temporary LDB session-info overrides inside transactions.

## Dependencies And Integration Points

The file integrates with SAMR generated types, DCE/RPC call/session helpers, SAMDB/DSDB password policy code, auth SAM lookup and bad password accounting, loadparm weak-crypto settings, GnuTLS cipher/PBKDF2/AEAD helpers, NTLM crypto helpers, messaging/audit logging, and password extraction helpers from Samba RPC libraries. It is called directly by SAMR `SetUserInfo` password levels and by generated SAMR password-change opnums.

## Risks And Edge Cases

This file is security-sensitive. Any mismatch in privilege restoration, transaction cancellation, constant-time verifier checks, weak-crypto enforcement, session key selection, or buffer wiping can create authentication bypass, password disclosure, or policy bypass risk. The RC4 paths intentionally enter FIPS lax mode and must always return to strict mode. `samr_set_password_buffers()` tolerates missing user session keys by using a random key to match Windows behavior, but that compatibility path can hide caller/session mistakes. Wrong user results are mapped to wrong password to avoid username disclosure. PBKDF2 iteration bounds and AES buffer parsing must stay aligned with the protocol.

## Test Signals

Important tests include SAMR password change 2/3/4 with correct and incorrect old passwords, nonexistent users, account lockout updates, policy rejection with reject info, weak-crypto disabled behavior with encrypted and unencrypted transports, password reset levels from `SetUserInfo`, AES reset/change buffer round trips, transaction rollback on decrypt or policy failure, audit log event presence, bad password count changes, and memory-sanitizer/leak checks for decrypted buffers and temporary session-info restoration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/samr/samr_password.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/service_rpc.c -->
# sources/user-network-fs/samba/source4/rpc_server/service_rpc.c

## Purpose

This file registers and initializes Samba's `rpc` task service for the source4 DCE/RPC server. It creates the DCE/RPC server context, loads configured endpoint servers, creates the local NCALRPC directory, adds endpoint listeners, and handles the split between endpoints that can run in the normal process model and endpoints that require a single shared process.

## Important APIs, Types, And Functions

`srv_callbacks` supplies DCE/RPC context callbacks for successful authorization logging, GENSEC preparation, root privilege hooks, and association group lookup. The local root hooks are no-ops because this service is already running in the expected server context. `dcesrv_init_endpoints()` iterates `dce_ctx->endpoint_list`, skips unsupported `NCACN_HTTP`, selects either the task's model ops or the `single` process model, and calls `dcesrv_add_ep()` for endpoints whose `use_single_process` flag matches the requested pass.

`dcesrv_task_init()` initializes the RPC server library, sets the task title, creates the DCE/RPC context with callbacks, loads endpoint servers from `dcerpc endpoint servers`, ensures the NCALRPC directory exists, registers multi-process-capable endpoints, and stores the context in `task->private_data`. `dcesrv_post_fork()` runs after worker creation and registers single-process endpoints only for the first instance. `server_service_rpc_init()` registers the service with Samba's task framework.

## Control Flow

Startup enters through `server_service_rpc_init()`, which registers service callbacks. During task initialization, `dcesrv_task_init()` builds the common DCE/RPC context and endpoint list, then calls `dcesrv_init_endpoints(..., false)` to add endpoints that can follow the configured process model. After fork/pre-fork processing, `dcesrv_post_fork()` validates `private_data`, and if `pd->instances == 0`, calls `dcesrv_init_endpoints(..., true)` so shared-context endpoints are added only once. Every post-fork process registers the IRPC name `rpc_server`.

## State And Persistence

The only persistent runtime state owned here is the DCE/RPC context stored in `task->private_data` and registered endpoint listeners. The file may create the NCALRPC directory on disk with mode `0755` if it is missing. It does not persist configuration or endpoint metadata itself; endpoint definitions come from loadparm and endpoint server initialization.

## Dependencies And Integration Points

This service integrates with Samba task services, process models, DCE/RPC server context/endpoint APIs, GENSEC auth setup, DCE/RPC association groups, generated endpoint servers, IRPC messaging, loadparm configuration, NCALRPC filesystem paths, and the process context/event loop supplied by the parent server.

## Risks And Edge Cases

The single-process endpoint split is important for shared policy handles and shared LDB contexts. Registering those endpoints in multiple processes could break handle sharing, while failing to register them in the first instance makes key RPC pipes unavailable. Startup aborts on endpoint initialization errors and NCALRPC directory creation failures. `NCACN_HTTP` endpoints are skipped entirely. The no-op root callbacks assume callers and endpoint implementations do not require privilege transitions from this layer.

## Test Signals

Test signals include successful Samba startup with the `rpc` service enabled, endpoint availability over expected transports except HTTP, creation and permissions of the NCALRPC directory, logs showing no endpoint registration failures, single-process-only endpoints appearing once, multi-process-safe endpoints appearing in normal workers, and successful RPC smoke tests against SAMR, SRVSVC, NETLOGON, and other configured endpoint servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/service_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/srvsvc/dcesrv_srvsvc.c -->
# sources/user-network-fs/samba/source4/rpc_server/srvsvc/dcesrv_srvsvc.c

## Purpose

This file implements the server side of Samba's SRVSVC DCE/RPC interface. It exposes Windows-compatible server service operations for share enumeration, share get/set/add/delete, share name validation, server metadata, remote time, disk enumeration, and file security operations, while returning explicit faults or not-supported errors for many legacy character-device, session, file, transport, path, and DFS opnums.

## Important APIs, Types, And Functions

`SRVSVC_CHECK_ADMIN_ACCESS` enforces that sensitive share info levels are visible only to builtin administrators or server operators. `dcesrv_srvsvc_NetShareAdd()` converts level 2 and 502 share info into Samba `share_info` arrays and calls `share_create()`. `dcesrv_srvsvc_fiel_ShareInfo()` fills SRVSVC share info unions for levels 0, 1, 2, 501, 502, and 1005 from `share_config`. `dcesrv_srvsvc_NetShareEnumAll()` and `dcesrv_srvsvc_NetShareEnum()` enumerate configured shares; the latter hides shares marked with `STYPE_HIDDEN`. `dcesrv_srvsvc_NetShareGetInfo()` fetches one share, and `dcesrv_srvsvc_NetShareSetInfo()` uses `dcesrv_srvsvc_fill_share_info()` plus `share_set()` to update configurable fields.

Other implemented operations include `NetShareCheck`, `NetSrvGetInfo`, `NetDiskEnum`, `NetTransportEnum` stubs with allocated empty arrays, `NetRemoteTOD`, `NetNameValidate`, `NetGetFileSecurity`, `NetSetFileSecurity`, and `NetShareDel`. Many other opnums call `DCESRV_FAULT(DCERPC_FAULT_OP_RNG_ERROR)` or return `WERR_NOT_SUPPORTED` after constructing empty containers for compatibility.

## Control Flow

Most operations switch on the incoming info level, allocate the matching generated NDR container, fill it, and return `WERR_INVALID_LEVEL` for unknown levels. Share creation and setting build arrays of generic `share_info` name/type/value records, normalize Windows `C:\path` style paths by dropping the drive prefix and converting backslashes to slashes, then call the share backend. Share enumeration obtains a `share_context`, lists share names, fetches each config, fills the requested info structure, and updates `totalentries`.

Server metadata flow reads `lpcfg_dcerpc_server_info()` and common helpers for platform, server name, server type, and server string. `NetRemoteTOD` snapshots system time and fills Windows remote time fields. `NetNameValidate` validates share names only for name type 9 and enforces the normal vs 8.3-style length limits. File security calls create an NTVFS context for the named share, construct raw path-info or setpath-info requests, and delegate ACL get/set to `ntvfs_qpathinfo()` or `ntvfs_setpathinfo()`.

## State And Persistence

Share add/set/delete persist through Samba's share backend reached by `share_create()`, `share_set()`, and `share_remove()`. Server info, disk info, transport arrays, and time responses are computed from configuration or current process state and are not persisted by this file. File security operations persist ACL changes through the underlying NTVFS backend and filesystem. The code owns only per-call talloc allocations for NDR response structures.

## Dependencies And Integration Points

The file integrates with generated `ndr_srvsvc` server dispatch, Samba DCE/RPC call/session state, share backend APIs, `rpc_server/common/share.h` helpers, loadparm server metadata, security token helpers, NTVFS raw file info/setfileinfo operations, time helpers, and generated `ndr_srvsvc_s.c`. It relies on `srvsvc_create_ntvfs_context()` from `srvsvc_ntvfs.c` for file security access.

## Risks And Edge Cases

Administrative access checks are present for some sensitive info levels but TODO comments remain for several share get/set/add paths, so authorization relies partly on backend enforcement. Path normalization assumes Windows drive-prefixed paths and does not fully validate filesystem reachability. Share security descriptors are marked TODO for add/set levels 502, so descriptor persistence may be incomplete. Enumeration has TODO paging support and can fail if a share disappears after name enumeration. A likely share-type bug exists in `srvsvc_ntvfs.c` rather than here, but it affects file security calls from this file. Many opnums intentionally fault, which can surprise clients expecting partial legacy support.

## Test Signals

Useful tests include SRVSVC RPC enumeration at levels 0, 1, 2, 501, and 502; admin vs non-admin access to protected levels; add/get/set/delete share round trips including path normalization; hidden share behavior difference between `NetShareEnum` and `NetShareEnumAll`; share name validation edge cases; server info levels 100-102; remote time and disk enum smoke tests; file security get/set over disk shares; and client compatibility tests for unsupported/faulting legacy calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/srvsvc/dcesrv_srvsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/srvsvc/srvsvc_ntvfs.c -->
# sources/user-network-fs/samba/source4/rpc_server/srvsvc/srvsvc_ntvfs.c

## Purpose

This file provides the SRVSVC helper that creates a temporary NTVFS connection to a named share so SRVSVC file security operations can query or set path security descriptors through the same backend mechanisms used by SMB file access.

## Important APIs, Types, And Functions

`struct srvsvc_ntvfs_ctx` wraps an `ntvfs_context *` so talloc cleanup can disconnect it. `srvsvc_ntvfs_ctx_destructor()` calls `ntvfs_disconnect()`. `srvsvc_create_ntvfs_context()` is the exported helper: it obtains the caller session, messaging context, server ID, share context/config, derives the NTVFS type from the share type, initializes an NTVFS connection with `ntvfs_init_connection()`, sets local/remote addresses, creates a request, performs `ntvfs_connect()`, and returns the connected NTVFS context.

## Control Flow

The helper looks up the share through `share_get_context()` and `share_get_config()`. It maps `SHARE_TYPE` to `NTVFS_IPC`, `NTVFS_PRINT`, or `NTVFS_DISK`, allocates the wrapper, initializes the NTVFS connection with protocol `PROTOCOL_NT1`, registers the destructor, sets addresses from the DCE/RPC connection, creates an `ntvfs_request` with the caller's auth session and call timestamp, then invokes the NTVFS tree-connect hook with the share name. On success, callers receive `c->ntvfs`.

## State And Persistence

The NTVFS context is per-call/per-allocation runtime state. It is talloc-owned by the supplied memory context and disconnects through the destructor. This file does not persist configuration or file data; persistence occurs only when callers use the returned context for NTVFS operations such as ACL updates.

## Dependencies And Integration Points

The file integrates SRVSVC with Samba share configuration, DCE/RPC session/address helpers, imessaging, server IDs, NTVFS connection/request APIs, raw tree-connect structures, loadparm context, and the helper prototype consumed by `dcesrv_srvsvc.c`.

## Risks And Edge Cases

The share-type mapping is fragile: the `else if (sharetype && strcmp(sharetype, "PRINTER"))` condition treats any non-`PRINTER` non-`IPC` value as print because `strcmp()` is nonzero, leaving actual `PRINTER` shares to fall through as disk. That appears inverted from the intended check and can misclassify disk shares. Host allow/deny checks are disabled behind `#if 0`. The context uses a hardcoded `PROTOCOL_NT1` and PID 0. Errors during init leave partial allocations to talloc cleanup, but callers must not retain the returned pointer beyond its memory context.

## Test Signals

Test signals include SRVSVC file security get/set on disk, IPC, and printer shares, verification that NTVFS disconnect runs on talloc free, share-not-found errors, address propagation checks in backends that inspect client/server addresses, and a targeted regression test for the share-type branch so `DISK`, `PRINTER`, and `IPC` map to the intended `NTVFS_*` enum values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/srvsvc/srvsvc_ntvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/tests/rpc_dns_server_dnsutils_test.c -->
# sources/user-network-fs/samba/source4/rpc_server/tests/rpc_dns_server_dnsutils_test.c

## Purpose

This is a cmocka unit test file for `source4/rpc_server/dnsserver/dnsutils.c`. It verifies that `dnsserver_init_zoneinfo()` correctly initializes DNS zone info server-address arrays from zone properties for master servers and scavenging servers, including empty-property handling and deep-copy behavior.

## Important APIs, Types, And Functions

The file directly includes `../dnsserver/dnsutils.c`, so the tests exercise the implementation without a separate library boundary. Test cases are `test_dnsserver_init_zoneinfo_master_servers_empty()`, `test_dnsserver_init_zoneinfo_master_servers()`, `test_dnsserver_init_zoneinfo_scavenging_servers_empty()`, and `test_dnsserver_init_zoneinfo_scavenging_servers()`. `main()` registers those four cmocka tests and emits subunit output with `cmocka_set_message_output(CM_OUTPUT_SUBUNIT)`.

The tests construct `dnsserver_zone`, `dnsserver_serverinfo`, `dnsserver_zoneinfo`, and `dnsp_DnsProperty` objects with talloc. Property IDs under test are `DSPROPERTY_ZONE_MASTER_SERVERS` and `DSPROPERTY_ZONE_SCAVENGING_SERVERS`; populated properties use four integer IPv4 address values.

## Control Flow

Each test allocates a talloc context, creates a minimal zone named `test`, attaches one DNS property, creates an empty server-info object, calls `dnsserver_init_zoneinfo(zone, serverinfo)`, and asserts the resulting zoneinfo fields. Empty tests require the corresponding address-list wrapper to exist with count zero and NULL address array. Non-empty tests require count four, copied values, and a distinct destination array pointer; after mutating the original property array, the zoneinfo copy must retain the original values.

## State And Persistence

The tests use only transient talloc-managed memory and free it at the end of each test. There is no filesystem, network, database, or persistent server state. The important state assertion is ownership separation between input property arrays and output zoneinfo arrays.

## Dependencies And Integration Points

The file depends on cmocka, talloc, generated DNS property structures, and the internal DNS server utility implementation. In the broader build, it is an RPC server test target validating DNS server utility behavior used by the DNS RPC endpoint when reporting zone metadata.

## Risks And Edge Cases

Directly including a `.c` file couples the test to implementation-level dependencies and can miss integration issues that appear only through normal object linkage. The tests cover only one property at a time and fixed four-entry arrays; they do not cover multiple properties, allocation failure, malformed counts, NULL zone/serverinfo inputs, IPv6-like data, or other `dnsserver_init_zoneinfo()` fields. Still, the deep-copy assertions protect against dangling pointer or aliasing bugs in zoneinfo construction.

## Test Signals

The primary signal is a passing cmocka/subunit run for all four tests. Useful extensions would add multiple-property zones, larger address arrays, zero count with non-NULL source array, nonzero count with NULL source array if representable, and memory-checker runs to ensure `dnsserver_init_zoneinfo()` owns copied arrays under the expected talloc parent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/tests/rpc_dns_server_dnsutils_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/unixinfo/dcesrv_unixinfo.c -->
# sources/user-network-fs/samba/source4/rpc_server/unixinfo/dcesrv_unixinfo.c

## Purpose

This file implements the Samba `unixinfo` DCE/RPC endpoint. It translates between Windows SIDs and Unix UID/GID values using winbind ID mapping, and exposes a small passwd lookup call that returns home directory and shell data for requested UIDs.

## Important APIs, Types, And Functions

`dcesrv_unixinfo_SidToUid()` maps one SID to an `id_map` with `wbc_sids_to_xids()` and accepts `ID_TYPE_UID` or `ID_TYPE_BOTH`. `dcesrv_unixinfo_UidToSid()` validates that the incoming 64-bit UID fits in 32 bits, prepares an `ID_TYPE_UID` mapping, and calls `wbc_xids_to_sids()`. `dcesrv_unixinfo_SidToGid()` mirrors SID-to-UID but accepts `ID_TYPE_GID` or `ID_TYPE_BOTH`. `dcesrv_unixinfo_GidToSid()` mirrors UID-to-SID for groups. `dcesrv_unixinfo_GetPWUid()` loops over input UIDs, calls `getpwuid()`, and returns per-entry homedir, shell, and NTSTATUS.

## Control Flow

Each mapping call allocates one `struct id_map`, initializes the SID or xid side, calls the relevant winbind client helper, propagates helper failures, and then validates the returned ID type. UID/GID-to-SID calls explicitly reject values that do not round-trip through `uint32_t`. `GetPWUid` preallocates an output array sized to the input count, sets output count to match, then fills each entry independently so missing users or allocation failures are reported per UID rather than failing the whole call.

## State And Persistence

The endpoint does not persist state. It queries winbind/idmap state and the system passwd database at call time. Output arrays and copied strings are per-call talloc allocations. `getpwuid()` may use process-global libc/NSS state, but this file stores none of it.

## Dependencies And Integration Points

The file integrates generated `ndr_unixinfo` dispatch, Samba DCE/RPC call handling, winbind client ID mapping (`wbc_sids_to_xids()` and `wbc_xids_to_sids()`), SID/idmap structures, libc/NSS passwd lookup through `getpwuid()`, and generated `ndr_unixinfo_s.c`.

## Risks And Edge Cases

ID type validation is important because SID mappings can be UID-only, GID-only, both, or unknown. UID/GID truncation checks prevent silently mapping IDs outside the 32-bit Unix ID range accepted by the RPC structures. `getpwuid()` is not reentrant and can be affected by NSS configuration or blocking directory backends. Large input counts allocate proportional memory. Missing passwd entries are not fatal, which clients must handle from per-entry status.

## Test Signals

Useful tests include SID-to-UID/GID mappings for UID-only, GID-only, BOTH, unknown, and unmapped SIDs; UID/GID-to-SID for valid and out-of-range IDs; winbind failure propagation; `GetPWUid` with existing, missing, and mixed UID lists; and NSS-backed integration tests confirming home directory and shell strings are copied under the response memory context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/unixinfo/dcesrv_unixinfo.c -->
