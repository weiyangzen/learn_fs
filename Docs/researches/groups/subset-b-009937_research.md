# Research: subset-b-009937

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_passwd.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_passwd.c

## Purpose

`libnet_passwd.c` implements Samba4 libnet password change and administrator password-set operations over remote SAMR RPC. It supports end-user change-password flows that prove knowledge of the old password and privileged set-password flows that open a SAMR user handle and write one of several SAMR user-info password levels. The file is security-sensitive because it handles plaintext passwords, NT/LM hashes, RPC session keys, weak-crypto fallback, and FIPS-mode exceptions around legacy RC4 paths.

## Important APIs, Types, and Functions

Public entry points are `libnet_ChangePassword()` and `libnet_SetPassword()`, both dispatching on level enums declared in `libnet_passwd.h`.

Password change helpers:
- `libnet_ChangePassword_samr_aes()` builds `samr_EncryptedPasswordAES` for `samr_ChangePasswordUser4`, deriving a content-encryption key from the old NT hash with PBKDF2-SHA512 and a random salt.
- `libnet_ChangePassword_samr_rc4()` implements fallback calls in order: `samr_ChangePasswordUser3`, `samr_ChangePasswordUser2`, and `samr_OemChangePasswordUser2`, using RC4-encrypted password buffers plus NT/LM verifiers.
- `libnet_ChangePassword_samr()` connects to a domain PDC SAMR pipe and tries AES first; it falls back to RC4 only for unsupported-proc statuses and only if weak crypto is not disallowed.
- `libnet_ChangePassword_generic()` maps generic input to the SAMR path.

Password set helpers:
- `libnet_SetPassword_samr_handle_26()`, `_25()`, `_24()`, `_23()`, and `_18()` implement SAMR `SetUserInfo2` levels. Levels 26/25 use `encode_rc4_passwd_buffer()` with the transport session key. Levels 24/23 encode a 516-byte Unicode password buffer and encrypt it with ARCFOUR. Level 18 encrypts an NT hash with `sess_crypt_blob()`.
- `libnet_SetPassword_samr_handle()` tries levels 26, 25, 24, and 23 unless a specific `samr_level` is requested.
- `libnet_SetPassword_samr()` connects to SAMR, opens the connect/domain/user handles, then delegates to the handle-level setter.
- `libnet_SetPassword_generic()` maps generic input to the SAMR path.

## Control Flow

Change-password flow: connect to the PDC SAMR pipe with `LIBNET_RPC_CONNECT_PDC`, format the server as `\\<rpc-server>`, try the AES `ChangePasswordUser4` request, and return immediately on success or implemented failure. Only unsupported-procedure style errors enter the RC4 fallback path, and the fallback is blocked when `lpcfg_weak_crypto()` reports weak crypto disallowed.

Set-password flow: generic requests become SAMR requests; SAMR requests connect to the PDC SAMR pipe, call `samr_Connect`, `samr_LookupDomain`, `samr_OpenDomain`, `samr_LookupNames`, validate exactly one RID/type, call `samr_OpenUser`, then pass the open user handle to the level-dispatcher. Handle-level auto-dispatch attempts modern password-info levels first and continues only for info-class/parameter/enum-level incompatibility.

## State and Persistence Behavior

The file does not maintain persistent local state. Remote persistent state is the user's password and, for most set levels, the password-expired flag or copied `samr_UserInfo21` fields. It uses talloc contexts for RPC request buffers and explicitly unlinks/frees RPC pipes after use. Sensitive temporary data is partially scrubbed with `BURN_DATA()` and `data_blob_clear[_free]()` for AES keys, session keys, and password buffers, but the caller-provided plaintext password strings remain owned by the caller.

## Dependencies and Integration Points

This file depends on libnet RPC connection helpers, generated SAMR RPC stubs, `source3/rpc_client/init_samr.h` password-buffer helpers, GnuTLS PBKDF2/ARCFOUR/session crypto wrappers, Samba credential/config APIs, SAMR/LSA generated structures, and `auth/libcli_auth` hash helpers. Python bindings in `py_net.c` expose the generic change/set functions, and domain-join code reuses the SAMR-handle set-password path for machine-account provisioning.

## Risks and Edge Cases

The weak-crypto fallback boundary is critical: RC4/LM flows must not run when policy forbids them. Several branches convert GnuTLS failures to NTSTATUS and must avoid returning success after crypto setup failure. The set-password levels require the right `info21` presence or absence; wrong combinations intentionally return `NT_STATUS_INVALID_PARAMETER_MIX`. The code sometimes uses maximum SAMR access and broad network error propagation, so tests need real DC/SAMR behavior. Failure handling should also preserve useful `error_string` messages while not leaking secrets.

## Test Signals

Relevant signals include Python `net.change_password()` and `net.set_password()` behavior, domain-join machine-password paths, and integration tests against DCs with and without `ChangePasswordUser4` support. Strong regression tests should cover AES success, unsupported-AES fallback, weak-crypto-disallowed fallback refusal, forced SAMR level 18 from Python, invalid `info21` mixes, exact SAMR result propagation, and FIPS mode restoration after legacy crypto calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_passwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_passwd.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_passwd.h

## Purpose

`libnet_passwd.h` declares the libnet password operation contracts consumed by `libnet_passwd.c` and callers such as Python bindings and domain-join code. It models two families of operation: changing a password with old-password proof and setting a password with administrative authority.

## Important APIs, Types, and Functions

`enum libnet_ChangePassword_level` selects generic, SAMR, KRB5, LDAP, or RAP change-password backends. `union libnet_ChangePassword` defines shared `in` fields (`account_name`, `domain_name`, `oldpassword`, `newpassword`) and `out.error_string` for each backend view.

`enum libnet_SetPassword_level` selects generic, SAMR, SAMR-handle, concrete SAMR info levels 26/25/24/23/18, and placeholder KRB5/LDAP/RAP backends. `union libnet_SetPassword` defines generic and SAMR input (`account_name`, `domain_name`, `newpassword`) plus the SAMR-handle input containing `account_name`, `policy_handle *user_handle`, `dcerpc_pipe *dcerpc_pipe`, `newpassword`, and optional `samr_UserInfo21 *info21`.

## Control Flow

The header does not execute code, but its union layout allows dispatchers to treat `generic`, `samr`, and backend-specific arms as level-tagged views over common input/output structures. `samr_level` lets a generic or SAMR request force a concrete SAMR set-password level instead of trying the default sequence.

## State and Persistence Behavior

The structures are caller-owned request/response containers. They hold pointers to plaintext password strings and RPC handles but do not own external resources by themselves. Output persistence is limited to `error_string` allocations on the supplied talloc context in the implementation.

## Dependencies and Integration Points

The SAMR-handle arm depends on `struct policy_handle`, `struct dcerpc_pipe`, and `struct samr_UserInfo21` from Samba RPC headers included through libnet umbrella headers. `py_net.c`, `libnet_join.c`, and other management flows construct these unions before calling `libnet_SetPassword()` or `libnet_ChangePassword()`.

## Risks and Edge Cases

The union relies on the first fields matching across arms. Mis-setting `level` or `samr_level` can dispatch to the wrong backend or a not-implemented placeholder. The `rap` set-password arm declares `enum libnet_ChangePassword_level level`, which is unusual beside the other set-password arms and is worth caution if RAP support is ever implemented.

## Test Signals

Compile-time coverage catches structure drift. Runtime signals come from password-change/set tests using generic and SAMR-specific levels, especially forced concrete SAMR levels and SAMR-handle callers that pass or omit `info21`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_passwd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_rpc.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_rpc.c

## Purpose

`libnet_rpc.c` provides libnet's asynchronous and synchronous DCERPC connection factory. It turns a `libnet_RpcConnect` request into an authenticated `dcerpc_pipe`, optionally resolving a DC/PDC, querying domain metadata through LSA, and deriving a secondary connection to the requested interface through endpoint mapping.

## Important APIs, Types, and Functions

Public APIs are `libnet_RpcConnect_send()`, `libnet_RpcConnect_recv()`, and synchronous `libnet_RpcConnect()`.

Internal state machines:
- Server path: `libnet_RpcConnectSrv_send()`, `continue_pipe_connect()`, `libnet_RpcConnectSrv_recv()`.
- DC/PDC path: `libnet_RpcConnectDC_send()`, `continue_lookup_dc()`, `continue_rpc_connect()`, `libnet_RpcConnectDC_recv()`.
- DC-info path: `libnet_RpcConnectDCInfo_send()`, `continue_dci_rpc_connect()`, `continue_lsa_policy()`, `continue_lsa_query_info2()`, `continue_lsa_query_info()`, `continue_epm_map_binding_send()`, `continue_epm_map_binding()`, `continue_secondary_conn()`, `libnet_RpcConnectDCInfo_recv()`.

The code also emits monitor messages for lookup, RPC connect, LSA policy open, and LSA policy query progress.

## Control Flow

Direct server/binding flow builds or parses a binding string, applies caller flags and debug flags, calls `dcerpc_pipe_connect_b_send()`, and returns the resulting pipe. Server-address requests use `ncacn_np:<address>[target_hostname=<name>]` to preserve the target host identity while connecting to an address.

DC/PDC flow first calls `libnet_LookupDCs_send()` with `NBT_NAME_LOGON` or `NBT_NAME_PDC`, then connects to the first returned DC via the server-address path.

DC-info flow connects to LSARPC first, opens policy over named pipe transports, queries DNS-domain/GUID and NetBIOS-domain/SID policy info when available, maps the requested RPC interface with EPM using anonymous credentials, then creates a secondary authenticated connection from the LSA pipe. TCP transports skip LSA policy open and go directly to endpoint mapping because policy open is not supported there.

## State and Persistence Behavior

Connection results are talloc-moved or reparented into the caller's memory context. For SAMR and LSARPC interfaces, the returned pipe and binding handle are also referenced into the long-lived `libnet_context` caches (`ctx->samr` or `ctx->lsa`) so later libnet operations can reuse handles after the short-lived call context is freed. DC-info output may include domain name, domain SID, realm, and GUID.

## Dependencies and Integration Points

The file integrates with Samba composite async primitives, tevent requests, `dcerpc_pipe_connect_b`, endpoint mapper helpers, secondary-auth connection helpers, generated LSA/SAMR interface tables, `libnet_LookupDCs`, credentials, and monitor-message infrastructure. It is foundational for password, share, time, domain-open, join, and user management code.

## Risks and Edge Cases

The DC-info monitor block in `continue_dci_rpc_connect()` dereferences `s->r.out.dcerpc_pipe` even though the just-opened pipe is stored in `s->rpc_conn`/context LSA state; this path deserves scrutiny if monitor callbacks are enabled. Memory ownership is delicate: one path uses `talloc_reparent()` with comments noting poor historical talloc usage. `libnet_RpcConnect_recv()` handles `LIBNET_RPC_CONNECT_SERVER_ADDRESS` in send but not explicitly in recv, which is a potential mismatch to test. LSA policy info may legitimately be unavailable on non-AD or unsupported transports, so callers must tolerate NULL realm/GUID/domain outputs.

## Test Signals

`source4/torture/libnet/libnet_rpc.c` is the primary signal, covering server, PDC, DC, DC-info, and binding levels. Additional signals come indirectly from all SAMR/SRVSVC/LSA users. Tests should assert returned pipe ownership, cached context handles, DC-info metadata, monitor callbacks, binding flags, debug flag behavior, endpoint mapper failures, and server-address recv behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_rpc.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_rpc.h

## Purpose

`libnet_rpc.h` declares the libnet RPC connection request/response ABI. It gives callers a single level-tagged structure for connecting to standalone servers, specific addresses, DCs, PDCs, explicit binding strings, or DCs with discovered domain metadata.

## Important APIs, Types, and Functions

`enum libnet_RpcConnect_level` defines `LIBNET_RPC_CONNECT_SERVER`, `SERVER_ADDRESS`, `PDC`, `DC`, `BINDING`, and `DC_INFO`. `struct libnet_RpcConnect` holds input `name`, `address`, `binding`, `dcerpc_iface`, and `dcerpc_flags`; output `dcerpc_pipe`, optional `domain_name`, `domain_sid`, `realm`, `guid`, and `error_string`.

`struct msg_net_rpc_connect` is the monitor payload with host, target domain name, endpoint, and DCERPC transport.

## Control Flow

The header is declarative. Its level enum drives the dispatcher in `libnet_rpc.c`, while its output fields let DC-info callers receive both the pipe and LSA-discovered metadata in one operation.

## State and Persistence Behavior

Callers supply the structure and memory context. On success, implementation stores a talloc-owned `dcerpc_pipe` and optional metadata under the requested output context and may also cache references in `libnet_context`.

## Dependencies and Integration Points

The header includes `librpc/rpc/dcerpc.h` and is included by `libnet/libnet.h` consumers throughout source4 libnet. It couples callers to NDR interface-table pointers and DCERPC transport enums.

## Risks and Edge Cases

Callers must set a compatible combination of level and input fields: server-address needs both `address` and `name`, binding needs `binding`, and DC/PDC needs a domain `name`. `dcerpc_flags` are meaningful only on paths that apply them. Output metadata is only valid for `DC_INFO`.

## Test Signals

Compile-time coverage plus the libnet RPC torture tests are the main signal. Any change to enum order or structure fields can break ABI expectations in C and Python-adjacent callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_samsync.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_samsync.h

## Purpose

`libnet_samsync.h` declares a small request/response structure for dumping SAM data into a keytab-like output path. In this subset it is only a contract header; the implementation is elsewhere.

## Important APIs, Types, and Functions

`struct libnet_SamDump_keytab` contains input `binding_string`, `keytab_name`, and `machine_account` credentials, plus output `error_string`.

## Control Flow

No code executes here. Callers populate the structure and pass it to the SAM dump/keytab implementation.

## State and Persistence Behavior

The intended persistent output is the named keytab file. The structure itself only stores pointers and an error string.

## Dependencies and Integration Points

The header includes generated NETLOGON types and references `struct cli_credentials`. It conceptually fits the libnet replication/secrets export area, alongside vampire and keytab export code.

## Risks and Edge Cases

The binding string and machine account must represent a secure, authorized channel; misuse risks exporting sensitive key material. The header does not express ownership or validation rules.

## Test Signals

Useful signals are integration tests that attempt a SAM dump to a temporary keytab and verify both success and authorization failure paths without leaving stale key material.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_samsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_share.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_share.c

## Purpose

`libnet_share.c` implements libnet share listing, creation, and deletion over the SRVSVC RPC interface. It is a thin wrapper around generated `srvsvc_NetShareEnumAll`, `NetShareAdd`, and `NetShareDel` calls with libnet-style error strings.

## Important APIs, Types, and Functions

Public functions:
- `libnet_ListShares()` connects to `ndr_table_srvsvc`, validates requested info levels 0, 1, 2, 501, or 502, calls `srvsvc_NetShareEnumAll`, and returns the selected union share counter.
- `libnet_AddShare()` sends a level-2 `srvsvc_NetShareAdd` using `srvsvc_NetShareInfo2`.
- `libnet_DelShare()` sends `srvsvc_NetShareDel` for a named share.

## Control Flow

Each function builds a `LIBNET_RPC_CONNECT_SERVER` request for the target server and SRVSVC interface, calls `libnet_RpcConnect()`, formats `server_unc`, performs one generated RPC call, translates transport or WERROR failures into `error_string` and NTSTATUS, then frees the RPC pipe.

## State and Persistence Behavior

`ListShares` reads remote share configuration and returns counters owned by the caller's talloc context. `AddShare` and `DelShare` mutate persistent share definitions on the remote server. The implementation does not page through multiple `WERR_MORE_DATA` responses; it issues one enumeration with `max_buffer = ~0` and returns the current counter.

## Dependencies and Integration Points

The file depends on `libnet_RpcConnect`, generated SRVSVC client stubs, `srvsvc_NetShareInfo` unions, WERROR-to-NTSTATUS conversion, and Samba talloc allocation. The share API is exercised by `source4/torture/libnet/libnet_share.c`.

## Risks and Edge Cases

Enumeration accepts `WERR_MORE_DATA` as non-fatal but does not expose a useful resume handle in the implementation, even though the header has resume fields. Invalid info levels return before disconnect only if no pipe has been opened; that path is safe because validation occurs after connect but before freeing the pipe, so the current code returns early and leaks `c.out.dcerpc_pipe` for invalid levels. Add/delete require appropriate remote privileges and may produce WERROR results even when transport status is OK.

## Test Signals

Torture share tests should cover list levels, add/delete round trips, invalid info levels, duplicate adds, deleting missing shares, access-denied errors, and large enumerations that return `WERR_MORE_DATA`. Leak tests around invalid levels would be valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_share.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_share.h

## Purpose

`libnet_share.h` declares request/response structures for libnet share operations over SRVSVC.

## Important APIs, Types, and Functions

`enum libnet_ListShares_level`, `enum libnet_AddShare_level`, and `enum libnet_DelShare_level` distinguish generic and SRVSVC backends. `struct libnet_ListShares` carries `server_name`, requested info `level`, optional resume pointers, and a returned `union srvsvc_NetShareCtr`. `struct libnet_AddShare` carries server name and a level-2 share definition. `struct libnet_DelShare` carries server and share names.

## Control Flow

The header has no code. Implementation dispatch is simple and currently SRVSVC-only in `libnet_share.c`.

## State and Persistence Behavior

The structures describe remote server share state. Add/delete mutate persistent remote configuration; list returns in-memory counters. Pointer ownership is delegated to implementation memory contexts.

## Dependencies and Integration Points

It includes generated `srvsvc.h` for share types. Callers include Samba management utilities and torture tests.

## Risks and Edge Cases

The header exposes resume-handle fields, but the current implementation does not fully honor them. Callers should not assume paging works unless implementation support is added.

## Test Signals

Compile-time consumers and SRVSVC torture tests validate the contract. Tests should compare header-exposed resume behavior to implementation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_share.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_site.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_site.c

## Purpose

`libnet_site.c` supports domain-join site placement. It discovers the client's AD site using CLDAP netlogon pings, constructs configuration/server DNs, and creates or updates the `server` object under `CN=Sites,CN=Configuration,...` for the joining machine.

## Important APIs, Types, and Functions

`libnet_FindSite()` takes a destination DC address, local NetBIOS name, and domain DN. It sends a CLDAP/netlogon ping to port 389, defaults to `Default-First-Site-Name`, replaces it with `client_site` from a NETLOGON NT5EX response when present, and returns `site_name_str`, `config_dn_str`, and `server_dn_str`.

`libnet_JoinSite()` resolves the SAMR binding host to an address, calls `libnet_FindSite()`, builds an LDB `server` object with `objectClass=server`, `systemFlags=50000000`, and `serverReference=<machine account DN>`, then `ldb_add()`s it or replaces `serverReference` if it already exists.

## Control Flow

Join-site flow derives the host from `libnet_JoinDomain` output SAMR binding, resolves it as an NBT client name, discovers site/DNs, constructs an LDB message, validates the target DN, adds the server object, and on existing entry performs a replace-only modify of `serverReference`. On success it stores `server_dn_str` into the broader join result.

## State and Persistence Behavior

`FindSite` only returns derived strings. `JoinSite` mutates the remote AD configuration partition by adding or modifying a server object. It does not create `CN=NTDS Settings`; a debug message explicitly notes that a future `DsAddEntry()` is still needed. Temporary allocations are freed through `tmp_ctx`; successful server DN is stolen into the join result.

## Dependencies and Integration Points

Dependencies include CLDAP/netlogon ping helpers, resolve APIs, tsocket address construction, LDB add/modify, Samba loadparm for netlogon ping protocol and resolver context, and join-result structures from `libnet_JoinDomain`. It sits in the domain-join flow with machine account creation and SAMR binding discovery.

## Risks and Edge Cases

The configuration DN is generated as `CN=Configuration,<domain DN>` rather than discovered. CLDAP failure does not abort site selection; it silently uses the default site. `resolve_name_ex()` and LDB errors are surfaced inconsistently, with some paths setting `error_string` to NULL. Existing server entries only update `serverReference`, which may leave stale attributes. Missing NTDS Settings creation means this file alone is not a complete DC site-registration implementation.

## Test Signals

Integration tests should verify CLDAP site discovery, default-site fallback, correct DN construction, add-vs-modify behavior on existing server objects, invalid DN handling, and join flows that later consume `server_dn_str`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_site.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_site.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_site.h

## Purpose

`libnet_site.h` declares the small request/response contract for site discovery during join.

## Important APIs, Types, and Functions

`struct libnet_JoinSite` has input `dest_address`, `netbios_name`, and `domain_dn_str`; output `error_string`, `site_name_str`, `config_dn_str`, and `server_dn_str`.

## Control Flow

The implementation fills these output strings in `libnet_FindSite()` and consumes them in `libnet_JoinSite()`.

## State and Persistence Behavior

The structure itself is transient. Output strings become persistent only when higher-level join state steals them; `libnet_JoinSite()` uses `server_dn_str` to write AD configuration state.

## Dependencies and Integration Points

It is included through libnet join-related code and ties CLDAP site discovery to LDB join updates.

## Risks and Edge Cases

The header does not document ownership or whether CLDAP failures are fatal. Callers need to inspect status and not just output pointers.

## Test Signals

Tests around `libnet_FindSite()` should assert all three output strings are populated for both CLDAP-discovered and default-site paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_site.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_time.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_time.c

## Purpose

`libnet_time.c` retrieves a remote server's time-of-day through SRVSVC `NetRemoteTOD` and exposes it through the libnet `RemoteTOD` dispatcher.

## Important APIs, Types, and Functions

`libnet_RemoteTOD()` dispatches generic and SRVSVC levels. `libnet_RemoteTOD_generic()` maps generic input to the SRVSVC backend. `libnet_RemoteTOD_srvsvc()` connects to the server's SRVSVC pipe, calls `srvsvc_NetRemoteTOD`, converts `srvsvc_NetRemoteTODInfo` fields into `time_t` with `timegm()`, and returns timezone offset in seconds.

## Control Flow

The SRVSVC flow connects to `LIBNET_RPC_CONNECT_SERVER`, formats `server_unc`, calls the generated RPC stub, checks both NTSTATUS and WERROR, converts the returned broken-down remote time into UTC `time_t`, stores timezone minutes multiplied by 60, and frees the RPC pipe.

## State and Persistence Behavior

This is read-only. It allocates temporary RPC structures and returns scalar time values plus an error string. No local or remote persistent state is changed.

## Dependencies and Integration Points

The file depends on `libnet_RpcConnect`, generated SRVSVC client stubs, `timegm`, WERROR conversion, and the Python `net.time()` binding in `py_net.c`.

## Risks and Edge Cases

The UNC string uses `"\\%s"` rather than the double-backslash pattern used elsewhere, which may be intentional for the generated API or may deserve compatibility testing. The code trusts returned date fields enough to feed `timegm()`. Timezone sign semantics depend on SRVSVC's `timezone` convention and should be checked against Windows/Samba behavior.

## Test Signals

Useful tests compare returned time against the remote host clock within tolerance, validate timezone sign/units, cover transport and WERROR failures, and exercise Python `Net.time()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_time.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_time.h

## Purpose

`libnet_time.h` declares the request/response union for retrieving remote time of day.

## Important APIs, Types, and Functions

`enum libnet_RemoteTOD_level` defines generic and SRVSVC backends. `union libnet_RemoteTOD` contains input `server_name` and output `time`, `time_zone`, and `error_string`.

## Control Flow

The level tag drives dispatch in `libnet_RemoteTOD()`. Generic requests are translated to SRVSVC requests by the implementation.

## State and Persistence Behavior

The union is transient and returns scalar values. It does not own network resources.

## Dependencies and Integration Points

It relies on C `time_t` and libnet callers. Python binding `Net.time()` consumes it and formats the returned `time_t` with local timezone formatting.

## Risks and Edge Cases

Callers must set the level and server name. Timezone interpretation needs implementation-level validation.

## Test Signals

Compile-time structure use plus runtime `libnet_RemoteTOD()` and Python `Net.time()` calls are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.c

## Purpose

`libnet_unbecome_dc.c` implements an asynchronous libnet workflow that demotes a Samba/AD domain controller back to a member-style computer account, modeled after Windows Server 2003 behavior. It discovers a source DC, modifies the destination computer account over LDAP, moves it to the Computers container, then removes the DS server/NTDS Settings objects through DRSUAPI.

## Important APIs, Types, and Functions

Public APIs are `libnet_UnbecomeDC_send()`, `libnet_UnbecomeDC_recv()`, and synchronous `libnet_UnbecomeDC()`.

Major stages:
- `unbecomeDC_send_cldap()` and `unbecomeDC_recv_cldap()` send netlogon pings to the source address and populate domain, source DSA, and destination site data.
- `unbecomeDC_ldap_connect()`, `_rootdse()`, `_computer_object()`, `_modify_computer()`, and `_move_computer()` bind LDAP, discover naming contexts, locate the DC computer account, replace `userAccountControl` with `UF_WORKSTATION_TRUST_ACCOUNT`, and rename/move it under the well-known Computers container GUID.
- `unbecomeDC_drsuapi_connect_send/recv()`, `_bind_send/recv()`, and `_remove_ds_server_send/recv()` connect sealed DRSUAPI over TCP, bind with `DRSUAPI_DS_BIND_GUID`, parse remote bind-info variants, and call `DsRemoveDSServer` with commit enabled.

## Control Flow

The send function copies inputs into a composite state, constructs destination DNS name as lowercase NetBIOS plus domain DNS name, then starts CLDAP. CLDAP success drives a synchronous LDAP block; LDAP success starts DRSUAPI connect, bind, and server-removal tevent requests. Any failed stage sets composite status and stops; final DRSUAPI success calls `composite_done()`.

## State and Persistence Behavior

Remote persistent changes are significant: the destination account's `userAccountControl` becomes workstation trust, the computer object may be moved/renamed into `CN=Computers`, and `DsRemoveDSServer` removes DS server/NTDS Settings objects from the configuration partition. Local state is held entirely in the composite talloc tree. `recv()` currently zeroes `r->out` and returns status without carrying detailed error strings.

## Dependencies and Integration Points

Dependencies include CLDAP/netlogon ping, LDB/LDAP wrapper connections, DSDB utilities, well-known GUID DN syntax, DRSUAPI generated client stubs, DCERPC pipe connect, loadparm ping protocol, credentials, tsocket address parsing, and libnet composite infrastructure. `source4/torture/libnet/libnet_BecomeDC.c` uses this to clean up after a BecomeDC/vampire promotion test.

## Risks and Edge Cases

The workflow is destructive and must target the intended DC account. Search filters interpolate `dest_dsa.netbios_name` and rely on LDB formatting to avoid malformed filters. CLDAP timeout is short. LDAP steps are synchronous inside an async state machine, so they can block the event loop. `recv()` discards error detail. The code does not explicitly unbind DRS/LDAP; talloc cleanup owns resources. DRS bind-info parsing accepts several lengths but only stores a normalized `DsBindInfo28`.

## Test Signals

The BecomeDC torture test is the main integration signal. Additional tests should validate CLDAP-discovered fields, LDAP move idempotency when already in Computers, no-op account-control updates, DRS remove failure handling, wrong source/destination inputs, and preservation of useful error strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.h

## Purpose

`libnet_unbecome_dc.h` declares the libnet request/response structure for demoting a DC from the directory's perspective.

## Important APIs, Types, and Functions

`struct libnet_UnbecomeDC` takes input `domain_dns_name`, `domain_netbios_name`, `source_dsa_address`, and `dest_dsa_netbios_name`; output is `error_string`.

## Control Flow

The implementation uses these four identifiers to locate a source DC, identify the destination DSA account, and remove DS server metadata.

## State and Persistence Behavior

The structure is transient, but the operation it describes mutates remote LDAP/DRSUAPI directory state.

## Dependencies and Integration Points

It is consumed by `libnet_unbecome_dc.c` and test code that pairs BecomeDC and UnbecomeDC workflows.

## Risks and Edge Cases

Inputs must be exact. A wrong destination NetBIOS name or source address could demote or attempt to remove the wrong directory objects. The output error string contract exists but current implementation does not populate it richly.

## Test Signals

Tests should assert failure on missing/wrong identifiers and successful cleanup after a controlled BecomeDC operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_user.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_user.c

## Purpose

`libnet_user.c` implements higher-level libnet user management operations: create user, delete user, modify user, fetch user info, and enumerate users. It composes domain-open prerequisites, SAMR RPC helpers, LSA domain queries, and asynchronous composite control flow into public libnet APIs.

## Important APIs, Types, and Functions

Public sync/async pairs include `libnet_CreateUser_send/recv()` plus `libnet_CreateUser()`, `libnet_DeleteUser_send/recv()` plus `libnet_DeleteUser()`, `libnet_ModifyUser_send/recv()` plus `libnet_ModifyUser()`, `libnet_UserInfo_send/recv()` plus `libnet_UserInfo()`, and `libnet_UserList_send/recv()` plus `libnet_UserList()`.

Supporting functions and state:
- `samr_domain_opened()` and `lsa_domain_opened()` from `prereq_domain.c` gate cached domain-handle use.
- `libnet_rpc_useradd`, `libnet_rpc_userdel`, `libnet_rpc_userinfo`, and `libnet_rpc_usermod` are lower-level SAMR helpers.
- `set_user_changes()` compares current `samr_UserInfo21` values with requested `libnet_ModifyUser` fields and sets `usermod_change` fields/flags using macros from `libnet_user.h`.

## Control Flow

Create/delete operations ensure a SAMR domain handle is open, then call the low-level add/delete RPC helper. Modify opens SAMR, queries level-21 user info, computes only changed fields, and sends a usermod request. UserInfo opens SAMR, either resolves name with `libnet_LookupName()` then queries by SID/RID or queries directly by SID, and maps level-21 SAMR output into friendly fields and `timeval`s. UserList opens LSA first to query the domain SID, opens SAMR, calls `samr_EnumDomainUsers`, and builds username/SID strings from returned RIDs.

## State and Persistence Behavior

Create, delete, and modify mutate remote SAM database state. UserInfo and UserList are read-only. The file relies on `libnet_context` cached SAMR/LSA domain handles and names, so state can persist across calls in one context. Results are talloc-stolen into caller memory contexts. UserList supports SAMR resume handles and treats `STATUS_MORE_ENTRIES` and `NT_STATUS_NO_MORE_ENTRIES` as successful enumeration statuses.

## Dependencies and Integration Points

Dependencies include composite/tevent, SAMR and LSA generated stubs, libnet domain-open and lookup helpers, lower-level user add/delete/info/modify modules, security/SID utilities, and credentials. Python `Net.create_user()` and `Net.delete_user()` expose part of this file. Torture tests in `source4/torture/libnet/libnet_user.c`, `userinfo.c`, `groupinfo.c`, and `userman.c` exercise related paths.

## Risks and Edge Cases

Several optional monitor paths allocate or send uninitialized `monitor_msg msg` values in create/delete/modify domain-open continuations. `continue_rpc_userinfo()` computes status from `set_user_changes()` but does not check it before sending usermod. `ModifyUser_recv()` does not populate output error strings. `SET_FIELD_ACCT_FLAGS` cannot set account flags to zero because it treats zero as not requested. UserList allocates based on returned SAM array count and assumes `sam` is non-NULL when status allows. Cached-domain logic can reject NULL domain inputs if a handle is already open.

## Test Signals

Torture user-management tests are the key signal. Good coverage includes create/delete idempotence, modify no-op and changed-field behavior, name-vs-SID user info, exact SID construction, time conversion, account flag edge cases, paged enumeration with resume handles, monitor callbacks, and error strings on lookup/open/query failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_user.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_user.h

## Purpose

`libnet_user.h` declares public libnet user-management request/response structures and helper macros for comparing requested user modifications to current SAMR level-21 state.

## Important APIs, Types, and Functions

Structures include `libnet_CreateUser`, `libnet_DeleteUser`, `libnet_ModifyUser`, `libnet_UserInfo`, and `libnet_UserList`. `enum libnet_UserInfo_level` selects lookup by name or SID.

Macros:
- `SET_FIELD_LSA_STRING()` copies a changed string and sets a `USERMOD_FIELD_*` flag.
- `SET_FIELD_NTTIME()` converts a requested `timeval` to NTTIME and flags changed time fields.
- `SET_FIELD_UINT32()` compares scalar fields.
- `SET_FIELD_ACCT_FLAGS()` flags nonzero account flags only when changed.

## Control Flow

The macros are invoked by `set_user_changes()` in `libnet_user.c` after the current user info is fetched. The structs drive async and sync public APIs.

## State and Persistence Behavior

The header models remote user/account state. Create/delete/modify requests mutate SAMR state; info/list outputs return allocated field values, SIDs, times, and arrays.

## Dependencies and Integration Points

It relies on `struct timeval`, `struct dom_sid`, and lower-level usermod field flags from libnet headers. Python bindings and C torture tests construct these structures.

## Risks and Edge Cases

The account-flags macro cannot request zero. Time macros treat NULL as not requested. String macros distinguish NULL from empty string, so callers can set empty strings only if they pass a non-NULL empty value.

## Test Signals

Tests should cover all modify field flags, especially clearing fields, zero account flags, and time conversion boundaries. Compile-time coverage protects structure layout expected by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_vampire.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_vampire.c

## Purpose

`libnet_vampire.c` contains default callbacks for the Samba4 "vampire"/BecomeDC replication path: provision a bare local AD database, receive DRS replication chunks from a source DC, resolve/apply the remote schema, convert replicated objects, and commit them into local LDB/DSDB with replication metadata.

## Important APIs, Types, and Functions

State is held in private `struct libnet_vampire_cb_state`, which tracks names, credentials, schemas, prefix map, LDB, schema chunk accumulation, target directory, loadparm/event contexts, debug counters, and server DN.

Exported callback helpers:
- `libnet_vampire_replicate_init()` initializes replication chunk state around an existing `samdb`.
- `libnet_vampire_cb_state_init()` builds callback state for BecomeDC tests/flows.
- `libnet_vampire_cb_ldb()` and `libnet_vampire_cb_lp_ctx()` expose the resulting LDB/loadparm.
- `libnet_vampire_cb_prepare_db()` provisions a bare database with `provision_bare()` and starts an LDB transaction.
- `libnet_vampire_cb_check_options()` logs BecomeDC source/destination options.
- `libnet_vampire_cb_schema_chunk()` accumulates schema DRS objects and calls `libnet_vampire_cb_apply_schema()` at end of partition.
- `libnet_vampire_cb_store_chunk()` converts and commits normal config/domain/application chunks.

## Control Flow

Preparation creates a bare database using naming information from BecomeDC, a random machine password, and NTVFS-enabled provision settings, then starts one transaction around the full vampire operation so linked-attribute backlinks can be resolved at commit.

Schema flow strips schema-info from the remote prefix map for local provision reload, initializes a self-made schema, appends incoming schema chunk linked lists until `more_data` is false, resolves a working schema through `dsdb_repl_resolve_working_schema()`, attaches it to LDB, converts objects with `dsdb_replicated_objects_convert()`, commits them, writes `prefixMap`, and reloads the schema.

Normal chunk flow decodes level-1 or level-6 DRS replies and request levels 0/5/8/10, derives replication flags for exops, critical-only, GET_TGT, full sync, and special-secret processing, converts replicated objects against the current schema, optionally dumps LDIF/debug metadata, commits objects, and validates linked-attribute identifiers for debug output.

## State and Persistence Behavior

This file writes an entire local AD database under the provision target. It persists schema, configuration/domain objects, replication metadata, prefixMap, repsFromTo metadata, high-watermarks when appropriate, and linked attributes via DSDB commit hooks. The long transaction is essential state behavior. It also tracks per-partition object/link counts and clears counters when a partition finishes.

## Dependencies and Integration Points

It integrates with BecomeDC callbacks, DRSUAPI generated structures, DSDB schema/prefix-map/replication conversion APIs, LDB transactions and LDIF writing, provisioning, loadparm configuration knobs (`become dc:dump objects`, `schema convert retrial`), security/session key handling, and Python replication bindings in `py_net.c`. `source4/torture/libnet/libnet_BecomeDC.c` wires these callbacks into a promotion test.

## Risks and Edge Cases

Schema handling is delicate: remote prefix maps, schemaInfo stripping, two-phase conversion, and schema attachment must remain consistent. Chunk-level request/response version handling must preserve high-watermark correctness while avoiding recording incomplete critical-only or exop subsets. Incorrect DSDB replication flags can mishandle secrets or linked attributes. The transaction must be committed by higher-level code; failure or abort can leave provisioned files needing cleanup. Debug dumping may expose sensitive replicated data.

## Test Signals

BecomeDC/vampire integration tests are the strongest signal: schema partition import, config/domain chunk import, linked-attribute backlink correctness after transaction commit, prefixMap presence, secret-processing behavior, exop/critical-only behavior, and Python `replicate_chunk()` paths. Negative tests should inject bad prefix maps, unsupported ctr/request levels, missing schema, conversion failures, and commit failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_vampire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_vampire.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_vampire.h

## Purpose

`libnet_vampire.h` declares public request structures and an opaque callback-state type for Samba's vampire/replication workflows.

## Important APIs, Types, and Functions

`struct libnet_Vampire` describes a higher-level domain import request with input domain name, NetBIOS name, target directory, and output domain SID/name/error. `struct libnet_Replicate` describes lower-level replication input including domain, NetBIOS, targetdir, domain SID, realm, server, join password, and kvno. `struct libnet_vampire_cb_state` is forward-declared as private callback state.

## Control Flow

The header does not execute code. It lets callers pass structured inputs into vampire/replication implementations and carry opaque callback state without exposing internals.

## State and Persistence Behavior

The described operations persist local provisioned AD database and secrets/key material. The structures themselves are transient request containers.

## Dependencies and Integration Points

It depends on `struct dom_sid` and is included by BecomeDC/vampire C code, tests, and Python-facing replication support.

## Risks and Edge Cases

The request structures carry sensitive `join_password` and target directory paths; callers must manage lifetime and cleanup. Optional `targetdir` in `libnet_Replicate` needs clear implementation behavior.

## Test Signals

Compile-time integration plus BecomeDC/vampire tests validate this header. ABI drift affects both C callbacks and Python replication wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_vampire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/prereq_domain.c -->
# sources/user-network-fs/samba/source4/libnet/prereq_domain.c

## Purpose

`prereq_domain.c` provides prerequisite helpers that ensure a SAMR or LSA domain handle is open before higher-level libnet composite operations continue. It centralizes cached-handle reuse and async `libnet_DomainOpen` scheduling.

## Important APIs, Types, and Functions

`samr_domain_opened()` checks `ctx->samr.handle` and `ctx->samr.name`; if the requested domain is not already open, it fills `libnet_DomainOpen` for `DOMAIN_SAMR` and starts `libnet_DomainOpen_send()`.

`lsa_domain_opened()` mirrors the logic for `ctx->lsa.handle`, `ctx->lsa.name`, and `DOMAIN_LSA`.

Both accept a parent composite context pointer, a continuation callback, and a monitor callback. They return `true` when the prerequisite is already satisfied or a terminal error has been placed on the parent, and `false` when an async open request has been queued.

## Control Flow

If `domain_name` is NULL and no handle is cached, the helpers use `cli_credentials_get_domain(ctx->cred)`. If `domain_name` is non-NULL and the cached handle is empty or for a different domain, they schedule domain open. If the matching handle already exists, they return true so callers can continue immediately. If NULL domain is supplied while a handle already exists, they signal invalid parameter.

## State and Persistence Behavior

The functions mutate no persistent directory state directly. They may initiate `libnet_DomainOpen`, whose receive path updates `libnet_context` cached SAMR/LSA handles and names. The helpers affect control state in parent composite contexts.

## Dependencies and Integration Points

Dependencies include composite async helpers, credentials, NDR policy-handle emptiness checks, generated SAMR/LSA headers, and `libnet_DomainOpen`. `libnet_user.c` and other libnet domain operations depend on this for precondition handling.

## Risks and Edge Cases

The boolean return convention is subtle: true can mean "ready" or "error already set"; false can mean "async request queued". Callers must follow the pattern exactly. `lsa_domain_opened()` returns true on `composite_nomem()` while SAMR returns false, which is an inconsistency. NULL-domain behavior rejects calls when a handle is already open instead of assuming reuse, which may surprise callers.

## Test Signals

Tests should cover already-open same domain, open different domain, NULL domain with and without cached handles, allocation failure simulation, continuation invocation, and both SAMR and LSA branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/prereq_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net.c -->
# sources/user-network-fs/samba/source4/libnet/py_net.c

## Purpose

`py_net.c` implements the `samba.net` Python extension type `net.Net`, exposing selected libnet management, password, time, user, DC discovery, and DRS replication helper operations to Python.

## Important APIs, Types, and Functions

Python methods include:
- `join_member()` -> `libnet_Join_member()`.
- `change_password()` -> `libnet_ChangePassword()`.
- `set_password()` -> `libnet_SetPassword()`, with optional `force_samr_18`.
- `time()` -> `libnet_RemoteTOD()`.
- `create_user()` and `delete_user()` -> `libnet_CreateUser()`/`libnet_DeleteUser()`.
- `replicate_init()` creates `replicate_state`, initializes vampire callback state, extracts DRS auth session key, and populates forest/chunk context.
- `replicate_chunk()` validates DRS ctr/request Python types, selects schema vs normal chunk callback, maps ctr/request fields into `libnet_BecomeDC_StoreChunk`, checks extended-op return codes, and calls vampire chunk handlers.
- `replicate_decrypt()` decrypts a DRS replicated attribute in place using the DRS binding auth session key and RID.
- `finddc()` calls CLDAP DC discovery and returns a Python NDR NETLOGON response object.

The file defines `py_net_Type`, constructor `net_obj_new()`, destructor `py_net_dealloc()`, and module init that exposes join-level constants.

## Control Flow

The constructor requires credentials, accepts optional loadparm and server address, creates a talloc context and event context, initializes `libnet_context`, and stores credentials. Each method parses Python arguments, builds the corresponding C request, allocates a talloc frame/context, calls C libnet or DSDB/DRSUAPI helpers, translates NTSTATUS/WERROR/DRS extended errors into Python exceptions, and returns Python scalars/NDR objects or `None`.

Replication flow is two-step: Python calls `replicate_init()` once to obtain opaque talloc state, then feeds each `DsGetNCChanges` reply to `replicate_chunk()`. The chunk method reuses stored forest, partition, destination DSA, and session-key pointers across calls.

## State and Persistence Behavior

`net.Net` owns a persistent `libnet_context`, event context, and talloc tree for the Python object lifetime. Methods can mutate remote domain state (join, password set/change, user create/delete), read remote state (time/finddc), or mutate local DSDB state via replication chunk import. `replicate_decrypt()` mutates the provided Python DRS attribute object in place.

## Dependencies and Integration Points

The extension integrates Python C API, pytalloc, pyldb, pyparam, pycredentials, generated Python DCERPC type checks, libnet C APIs, DRSUAPI helpers, vampire callbacks, Samba finddc/CLDAP, GENSEC session keys, and Samba Python module initialization. `py_net_dckeytab.c` later injects an additional method into this same `Net` type.

## Risks and Edge Cases

Several methods create a new event context rather than accepting one from Python, noted by FIXME comments. `change_password()` frees parsed Unicode strings after the libnet call; error paths must avoid leaks. `replicate_decrypt()` has early returns after talloc stackframe allocation that can leak the frame if type checks fail. `replicate_chunk()` treats any non-`Py_None` `schema` argument as requiring a bool, so default truthiness is not accepted. Type validation is essential because it casts Python objects to generated C structs.

## Test Signals

Python-level tests should cover constructor credential validation, password operations, user create/delete, time formatting, finddc returns, DRS replicate init/chunk/decrypt paths, extended-error exception mapping, forced SAMR level 18, and bad Python type errors. Integration with Samba replication tooling is a strong end-to-end signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net.h -->
# sources/user-network-fs/samba/source4/libnet/py_net.h

## Purpose

`py_net.h` declares the C struct backing the Python `samba.net.Net` object.

## Important APIs, Types, and Functions

`py_net_Object` embeds `PyObject_HEAD` plus `TALLOC_CTX *mem_ctx`, `struct libnet_context *libnet_ctx`, and `struct tevent_context *ev`.

## Control Flow

The constructor in `py_net.c` initializes these fields; the destructor frees `libnet_ctx` before `mem_ctx`.

## State and Persistence Behavior

This object owns the Python-visible libnet session state. Its `libnet_context` may cache RPC pipes and domain handles, and its talloc context owns allocations that should live for the Python object.

## Dependencies and Integration Points

The header is included by `py_net.c` and `py_net_dckeytab.c`, allowing the latter to add a method that can access the underlying `libnet_context`.

## Risks and Edge Cases

Any change to this struct affects binary compatibility between compiled extension modules that include it. Destruction order matters because `libnet_ctx` may reference objects under `mem_ctx`.

## Test Signals

Python extension import, object construction/destruction under leak checkers, and dckeytab method injection validate this contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net_dckeytab.c -->
# sources/user-network-fs/samba/source4/libnet/py_net_dckeytab.c

## Purpose

`py_net_dckeytab.c` implements a Python extension initializer that injects `export_keytab()` into the existing `samba.net.Net` type. The method exports DC or principal Kerberos keys to a keytab through `libnet_export_keytab()`.

## Important APIs, Types, and Functions

`py_net_export_keytab()` parses `keytab`, optional `samdb`, optional `principal`, and boolean flags `keep_stale_entries`, `only_current_keys`, and `as_for_AS_REQ`; validates optional `samdb` as an LDB object; calls `libnet_export_keytab()` with the current `Net` object's `libnet_context`; and maps NTSTATUS failures to Python exceptions.

`MODULE_INIT_FUNC(dckeytab)` creates a dummy module, imports `samba.net`, obtains the `Net` type, creates a method descriptor, and inserts it into `Net.tp_dict`.

## Control Flow

Importing the `dckeytab` extension mutates the method dictionary of `samba.net.Net`. Calling `export_keytab()` creates a talloc context under the Python object, fills `struct libnet_export_keytab`, invokes the C exporter, frees the context, and returns `None` on success.

## State and Persistence Behavior

The method writes or updates the named keytab file. Options can retain stale entries, restrict to current keys, or simulate AS-REQ key selection behavior used by tests. It may read from a supplied `samdb` or use libnet context defaults depending on exporter behavior.

## Dependencies and Integration Points

Dependencies include Python C API, `py_net.h`, `libnet_export_keytab.h`, pyldb validation, and Samba Python NTSTATUS error helpers. It relies on `samba.net` being importable and on the `Net` type layout declared in `py_net.h`.

## Risks and Edge Cases

The module returns the imported `samba.net` module object rather than the initially created dummy module after successful import, which is intentional-looking but unusual. Method injection mutates an existing type at import time and can fail silently by returning a module with no method if intermediate descriptor creation fails. Exporting keytabs handles sensitive key material; tests must use temporary files and strict permissions.

## Test Signals

Python tests should import `samba.dckeytab`, assert `Net.export_keytab` exists, export to a temporary keytab with different flag combinations, cover invalid `samdb` type handling, and verify failure paths do not leave partial sensitive files where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/py_net_dckeytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userinfo.c -->
# sources/user-network-fs/samba/source4/libnet/userinfo.c

## Purpose

`userinfo.c` implements a lower-level composite SAMR helper for querying user information by username or SID/RID using an already-open SAMR domain handle and binding handle.

## Important APIs, Types, and Functions

Public functions are `libnet_rpc_userinfo_send()`, `libnet_rpc_userinfo_recv()`, and synchronous `libnet_rpc_userinfo()`.

Internal continuation stages:
- `continue_userinfo_lookup()` receives `samr_LookupNames`, validates one RID/type, emits lookup monitor data, and sends `samr_OpenUser`.
- `continue_userinfo_openuser()` receives `samr_OpenUser`, emits open monitor data, and sends `samr_QueryUserInfo` at the requested level.
- `continue_userinfo_getuser()` receives `samr_QueryUserInfo`, steals the returned union, emits query monitor data, and sends `samr_Close`.
- `continue_userinfo_closeuser()` receives `samr_Close`, emits close monitor data, and completes the composite request.

## Control Flow

`send()` creates a composite context and state. If `io->in.sid` is present, it parses the SID string and extracts the last subauthority as the RID, skipping name lookup. Otherwise it sends `samr_LookupNames` for `io->in.username`. Both paths converge on open-user, query-user-info, close-user. `recv()` waits, steals the resulting `union samr_UserInfo` into the caller context, frees the composite context, and returns status.

## State and Persistence Behavior

The helper is read-only except for opening and closing a remote SAMR user policy handle. It depends on caller-provided domain and binding handles but does not cache them. Result data is talloc-transferred to the caller.

## Dependencies and Integration Points

Dependencies include composite/tevent, generated SAMR client stubs, SID parsing, security constants, and libnet monitor message types. `libnet_user.c` uses it for high-level `UserInfo` and `ModifyUser`, and torture tests call it directly in sync and async modes.

## Risks and Edge Cases

SID parsing uses the last subauthority as RID without verifying that the SID belongs to the opened domain. If `io->in.sid` and `io->in.username` are both absent, the username path can dereference NULL through `talloc_strdup`. Monitor payloads allocate under state but no allocation failures are checked before invoking callbacks. If close fails after query success, the whole operation fails even though info was fetched.

## Test Signals

`source4/torture/libnet/userinfo.c`, `groupinfo.c`, and `userman.c` provide direct signals. Tests should cover SID and username paths, bad SID strings, non-user RIDs, missing username, query levels, monitor messages, close failure behavior, and memory ownership of returned info.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userinfo.h -->
# sources/user-network-fs/samba/source4/libnet/userinfo.h

## Purpose

`userinfo.h` declares the lower-level SAMR userinfo request/response structure and monitor payloads used by `userinfo.c`.

## Important APIs, Types, and Functions

`struct libnet_rpc_userinfo` contains input `policy_handle domain_handle`, optional `username`, optional string `sid`, and query `level`; output is `union samr_UserInfo info`.

Monitor structures are `msg_rpc_open_user` with RID/access mask, `msg_rpc_query_user` with query level, and `msg_rpc_close_user` with RID.

## Control Flow

The presence of `sid` selects the direct open-user path; otherwise implementation uses `username` lookup first. Monitor structs are sent at open, query, and close stages.

## State and Persistence Behavior

The structure is transient and read-only with respect to directory data. The remote operation opens/closes a user handle and returns copied SAMR info.

## Dependencies and Integration Points

It includes generated SAMR types and is consumed by `userinfo.c`, `libnet_user.c`, and torture tests. It also shares monitor-message conventions with other libnet RPC helpers.

## Risks and Edge Cases

The contract does not state whether `sid` and `username` are mutually exclusive or what happens if neither is set. The SID is a string rather than a typed `dom_sid`, so callers rely on implementation parsing.

## Test Signals

Direct sync/async userinfo torture tests validate both lookup modes and returned `samr_UserInfo` content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userinfo.h -->
