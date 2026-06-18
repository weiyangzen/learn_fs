<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi.h -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/netapi.h

Purpose: public C compatibility header for Samba's `libnetapi` implementation. It exposes the Windows-style NetAPI contract used by callers for domain join/offline join, server/workstation/DC discovery, users, global groups, local groups, display enumeration, shares, open files, shutdown, Netlogon control, SID conversion, credentials, and NetApi buffer ownership.

Important APIs/types: defines `NET_API_STATUS`, `ERROR_MORE_DATA`, `GUID`, `domsid`, `DOMAIN_CONTROLLER_INFO`, large families of `SERVER_INFO_*`, `USER_INFO_*`, `USER_MODALS_INFO_*`, `GROUP_INFO_*`, `LOCALGROUP_INFO_*`, `SHARE_INFO_*`, `FILE_INFO_*`, `NETLOGON_INFO_*`, and display structs. It declares context functions such as `libnetapi_init`, `libnetapi_free`, credential setters/getters, Kerberos/ccache toggles, error-string helpers, and `NetApiBufferAllocate`/`NetApiBufferFree`. Functional exports include `NetJoinDomain`, `NetUnjoinDomain`, offline join composition/request/provisioning, `NetServerGetInfo`, `NetUser*`, `NetGroup*`, `NetLocalGroup*`, `NetShare*`, `NetFile*`, `NetShutdown*`, and `I_NetLogonControl*`.

Control flow: this header has no executable control flow, but its declarations define the call surface implemented by generated `libnetapi` wrappers and the source files in this directory. Most APIs take `server_name`, level numbers, caller-owned input buffers, and output buffers that must be released through `NetApiBufferFree`. Resume-handle and `ERROR_MORE_DATA` patterns are used for enumeration APIs.

State and persistence: no storage is defined here. Runtime state lives behind `struct libnetapi_ctx`, RPC/session caches, Samba configuration, remote SAM/SRV/NETLOGON services, or caller-allocated buffers. Some operations are persistent on the target host, such as joining domains, creating accounts/groups/shares, changing password policy, changing server comments, and initiating shutdown.

Dependencies/integration: included by both Samba implementation files and external tests/examples through `<netapi.h>`. The concrete behavior depends on generated NDR/RPC bindings, SAMR, SRVSVC, WKSSVC, NETLOGON, INITSHUTDOWN, and Samba credential/loadparm subsystems. Struct layouts intentionally mirror LANMAN/Windows NetAPI levels, so ABI compatibility is more important than local style.

Risks: the header is broad and level-driven, so unsupported level handling is scattered across implementation files. Several old Windows level structs and fields have typo-like names, including `SERVER_INFO_1599`, `1600`, `1601`, and `1602` fields using `sv1598` prefixes, which may be preserved ABI quirks but are easy to misuse. Output string pointers are generally allocated inside NetApi buffers or talloc-backed conversion buffers; callers must obey the documented free discipline. Many mutating APIs are privileged and destructive on a real server.

Test signals: compile tests should verify C/C++ inclusion, struct names, and prototypes. Integration tests should exercise supported levels, unsupported-level error mapping, `ERROR_MORE_DATA` resume behavior, buffer freeing, and destructive operations against isolated Samba instances.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi_net.h -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/netapi_net.h

Purpose: small private header shared between the Samba `net` binary and `libnetapi`. It exposes a context initialization path that reuses already-loaded configuration and credentials instead of doing the full public library initialization sequence.

Important APIs/types: declares `libnetapi_net_init(struct libnetapi_ctx **ctx, struct loadparm_context *lp_ctx, struct cli_credentials *creds)`. The API returns `NET_API_STATUS` and installs the supplied `loadparm_context` and `cli_credentials` into a new `libnetapi_ctx`.

Control flow: no runtime control flow is present in the header. Callers include it when they need the specialized initialization mode, typically after Samba command-line/config parsing has already populated loadparm and credential state.

State and persistence: no storage is defined here. The function it declares affects process-local `libnetapi_ctx` state by wiring existing configuration and credentials into the NetAPI layer. It does not by itself persist anything.

Dependencies/integration: included by `netapi_private.h`, which lets private implementation code know about this initialization contract. It bridges command-line Samba tooling and the library API without forcing a second config read or debug/log setup.

Risks: because the header says it is private between `net` and `libnet`, external consumers should not rely on this ABI. Passing credentials/loadparm with lifetimes shorter than the resulting context would be hazardous unless the implementation takes references. The comment contains a duplicated "and", indicating the file is intentionally minimal rather than heavily maintained.

Test signals: tests should initialize libnetapi through both public `libnetapi_init` and private `libnetapi_net_init` paths and verify credentials, workgroup, Kerberos mode, and loadparm-derived behavior match expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi_private.h -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/netapi_private.h

Purpose: private implementation header for Samba's NetAPI support. It defines the concrete `libnetapi_ctx`, internal private state, localhost-redirection macro for local wrappers, and helper prototypes used by SAMR, SRVSVC, NETLOGON, shutdown, and group/user code.

Important APIs/types: `struct libnetapi_private_ctx` caches SAMR domain metadata, `rpc_pipe_client`, connect/domain/builtin access masks, and policy handles, plus IPC connections and a messaging context. `struct libnetapi_ctx` stores debug/log/error strings, policy handle cache toggle, credentials, private data, and loadparm context. Helper prototypes include error/log setters, RPC pipe/binding acquisition, SAMR domain open/close/free routines, and `add_GROUP_USERS_INFO_X_buffer`.

Control flow: `LIBNETAPI_REDIRECT_TO_LOCALHOST(ctx, r, fn)` logs the redirection, defaults a missing `r->in.server_name` to `"localhost"`, and tail-calls the remote `_r` version. SAMR helpers centralize connection/domain handle acquisition and cache management so higher-level user/group/localgroup operations do not duplicate RPC setup.

State and persistence: state is process-local in `libnetapi_ctx` and its `private_data`. Cached policy handles persist for the lifetime of the context unless masks are insufficient or explicit close/free functions run. Persistent effects occur only through downstream RPC calls, not from this header itself.

Dependencies/integration: includes `netapi_net.h` and Samba credential declarations. It references generated NDR interface tables, DCE/RPC binding handles, RPC pipe clients, policy handles, domain SIDs, client IPC connections, messaging contexts, and loadparm state. Implementation files include it to access the concrete context hidden from public `netapi.h`.

Risks: policy-handle caching requires access-mask checks to be exact; using a cached handle with insufficient rights would break later operations, while failing to close stale handles leaks server-side resources. The redirect macro mutates request input by assigning `server_name`, which can surprise callers inspecting request structs after local calls. `talloc_get_type_abort` in implementations means corrupted or missing private data aborts rather than returning a NetAPI error.

Test signals: targeted tests should cover handle cache reuse, cache invalidation when requested masks grow, cleanup via `libnetapi_samr_free`, localhost redirection when `server_name` is NULL, and error-string propagation from helper failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netapi_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netlogon.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/netlogon.c

Purpose: implements `I_NetLogonControl` and `I_NetLogonControl2` over the NETLOGON DCE/RPC interface. It converts LANMAN-style control inputs and NETLOGON query outputs into the public `NETLOGON_INFO_*` buffers declared in `netapi.h`.

Important APIs/functions: `construct_data` maps a `NETLOGON_CONTROL_*` function code plus caller `data` bytes into `union netr_CONTROL_DATA_INFORMATION`. `construct_buffer` maps `union netr_CONTROL_QUERY_INFORMATION` levels 1 through 4 into `NETLOGON_INFO_1` through `NETLOGON_INFO_4`. `I_NetLogonControl_r` calls `dcerpc_netr_LogonControl`; `I_NetLogonControl2_r` calls `dcerpc_netr_LogonControl2` or `dcerpc_netr_LogonControl2Ex`; `_l` forms redirect to localhost.

Control flow: `I_NetLogonControl_r` obtains a NETLOGON binding, performs the RPC with the requested function/query level, converts NTSTATUS to WERROR on transport failure, honors returned WERROR, then builds the output buffer. `I_NetLogonControl2_r` first validates/builds control data, obtains the binding, selects the Ex RPC for `TC_VERIFY`, `SET_DBFLAG`, and `FORCE_DNS_REG`, then converts the query union into a caller-visible buffer.

State and persistence: no local persistent state is kept. Remote Netlogon controls can affect remote service behavior, trust rediscovery, debug flags, DNS registration, or trust validation depending on function code. Output buffers are talloc allocations under `ctx`.

Dependencies/integration: depends on generated NETLOGON client stubs, generated libnetapi request structs, public/private NetAPI headers, and binding acquisition through `libnetapi_get_binding_handle`. It is invoked by public wrappers generated around `I_NetLogonControl` and `I_NetLogonControl2`.

Risks: `construct_data` casts raw `uint8_t *` data directly to strings or uses `atoi`, so callers must supply NUL-terminated data for string/debug-level controls. Unsupported function codes return `WERR_INVALID_PARAMETER`; unsupported levels return `WERR_INVALID_LEVEL`. `construct_buffer` assumes the RPC returned the expected union arm for the requested level; malformed or unexpected server responses could expose null dereferences if generated stubs do not enforce that invariant.

Test signals: tests should cover levels 1-4, invalid levels, unsupported function codes, `LogonControl2Ex`-selected function codes, NULL data where domain/user data is required, and local redirect behavior. Integration tests require a domain controller or Samba Netlogon service.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/samr.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/samr.c

Purpose: shared SAMR helper implementation for opening and closing domain, builtin-domain, and connect policy handles used by NetAPI user/group/localgroup operations. It centralizes SAMR connection setup and context-level handle caching.

Important APIs/functions: `libnetapi_samr_open_domain` opens or reuses a SAMR connect handle, enumerates domains, skips the builtin domain, looks up the selected domain SID, opens that domain, and caches handles/masks/SID. `libnetapi_samr_open_builtin_domain` opens or reuses the builtin domain using `global_sid_Builtin`. `libnetapi_samr_close_domain_handle`, `libnetapi_samr_close_builtin_handle`, `libnetapi_samr_close_connect_handle`, and `libnetapi_samr_free` close cached handles through `dcerpc_samr_Close`.

Control flow: each open function first checks cached handles in `libnetapi_private_ctx` and reuses them only when the cached access mask covers the requested mask. If a cached handle is insufficient it is closed and reopened. Domain open performs `dcerpc_try_samr_connects`, `samr_EnumDomains`, first non-builtin-domain selection, `samr_LookupDomain`, and `samr_OpenDomain`. Builtin open performs connect and `samr_OpenDomain` with the builtin SID.

State and persistence: policy handles, masks, SAMR pipe client, domain name, and domain SID are cached in the context. The cache is process-local but represents server-side RPC handles that must be closed. No SAM database changes are made here; higher-level callers use the opened handles for persistent account/group changes.

Dependencies/integration: depends on `rpc_pipe_client`, generated SAMR client stubs, `dcerpc_try_samr_connects`, LSA string initialization, Samba security SID constants, and private context shape from `netapi_private.h`. It supports user, group, localgroup, display, and modals code outside this work item.

Risks: domain selection uses the first enumerated non-builtin domain, which may be ambiguous on unusual servers. Cached `domain_name` points into data allocated under the context/RPC call memory and must not outlive the context. Close helpers only close handles equal to the cached handles; closing copies or unrelated handles is ignored, which protects the cache but can leak if callers expected arbitrary close behavior. `priv->samr.cli` must remain valid when close helpers run.

Test signals: tests should open the same domain with identical and wider masks, verify reuse/reopen behavior, simulate no non-builtin domain, verify builtin handle open, and run `libnetapi_samr_free` under leak/handle-close instrumentation. Integration tests should cover Samba standalone/domain-member/AD modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/serverinfo.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/serverinfo.c

Purpose: implements server information and remote time-of-day NetAPI functions over local Samba configuration and remote SRVSVC RPC. It translates `srvsvc_NetSrvInfo` levels into public `SERVER_INFO_*` buffers.

Important APIs/functions: local helpers `NetServerGetInfo_l_101` and `_1005` build server name/version/type/comment buffers from loadparm. `map_server_info_to_SERVER_INFO_buffer` maps SRVSVC levels 100, 101, 102, 402, 403, 502, 503, 599, and 1005, although the remote entry point only accepts a subset. `NetServerGetInfo_r`, `NetServerSetInfo_l`, `NetServerSetInfo_r`, `NetRemoteTOD_r`, and `NetRemoteTOD_l` are the exported request handlers.

Control flow: local get-info supports levels 101 and 1005 directly. Remote get-info validates level 100, 101, 102, 402, 502, 503, or 1005, obtains a SRVSVC binding, calls `dcerpc_srvsvc_NetSrvGetInfo`, and maps the returned union into a talloc-backed buffer. Local set-info only supports level 1005, validates the comment, requires the registry smb.conf backend, initializes an smbconf registry context, and writes global `server string`. Remote set-info supports level 1005 by passing a `srvsvc_NetSrvInfo1005` to `NetSrvSetInfo`. `NetRemoteTOD_r` calls `srvsvc_NetRemoteTOD` and duplicates the returned time structure.

State and persistence: remote get/time calls are read-only. `NetServerSetInfo_l_1005` persists the server comment in Samba's registry configuration backend. Remote set-info persists on the target server according to SRVSVC behavior. Output buffers are allocated under the NetAPI context.

Dependencies/integration: uses generated SRVSVC client stubs, Samba loadparm functions, SMB configuration registry APIs, and `libsmb/dsgetdcname.h`. It integrates with public `NetServerGetInfo`, `NetServerSetInfo`, and `NetRemoteTOD` wrappers and with the tests in `netserver.c`.

Risks: the map function includes code for levels not accepted by `NetServerGetInfo_r`, so future level enablement needs both validation and mapping reviewed. Several level 599 assignments contain comments such as `/* ?? */` and `/* typo ? */`, documenting uncertain field correspondence. Local set-info returns service-style errors for smbconf failures and calls `smbconf_shutdown(conf_ctx)` even after initialization failure paths, so `conf_ctx` lifetime assumptions matter. Tests include level 403 and tolerate status 124, reflecting partial implementation.

Test signals: integration tests should query levels 100, 101, 102, 402, 502, 503, and 1005, verify unsupported level behavior for 403/599 unless enabled, exercise remote TOD, and test local level 1005 with both registry and non-registry config backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/serverinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/share.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/share.c

Purpose: implements NetAPI share add/delete/enumerate/get/set operations over the SRVSVC RPC interface. It maps between public `SHARE_INFO_*` buffers and generated `srvsvc_NetShareInfo*` unions.

Important APIs/functions: `map_srvsvc_share_info_to_SHARE_INFO_buffer` converts SRVSVC levels 0, 1, 2, 501, and 1005 to public buffers. `map_SHARE_INFO_buffer_to_srvsvc_share_info` converts public levels 2, 502, and 1004 into SRVSVC input unions. Request handlers include `NetShareAdd_r/l`, `NetShareDel_r/l`, `NetShareEnum_r/l`, `NetShareGetInfo_r/l`, and `NetShareSetInfo_r/l`.

Control flow: add validates the input buffer and permits levels 2 and 502, rejects 503 as unsupported, obtains a SRVSVC binding, maps the buffer, and calls `NetShareAdd`. Delete validates `net_name` and calls `NetShareDel`. Enum validates levels 0-2, creates the matching SRVSVC share counter union, calls `NetShareEnumAll`, accepts success or `WERR_MORE_DATA`, and appends each returned item to the caller buffer. Get-info validates name/output/level and calls `NetShareGetInfo`. Set-info allows levels 2 and 1004, maps the buffer, and calls `NetShareSetInfo`.

State and persistence: add, delete, and set-info persist share configuration on the target server. Enumeration and get-info are read-only. The implementation itself keeps no durable state; output buffers are talloc arrays under `ctx`.

Dependencies/integration: depends on generated SRVSVC stubs, `ndr_security.h` for security descriptor sizing at level 502, and private NetAPI binding helpers. It is used by public `NetShare*` wrappers and by `tests/netshare.c`.

Risks: `NetShareEnum_r` loops with `info_ctr.ctr.ctr1->count` even when level 0 or 2 selected `ctr0` or `ctr2`; if the generated union does not alias counts compatibly this can crash or miscount. Level 502 can be sent for add but get/set level 502 are declared unsupported, so security descriptor round-tripping is incomplete. The level 502 mapping uses caller-provided security descriptor pointers and NDR size calculation; invalid descriptors may fail later in RPC marshalling. Local `_l` handlers just redirect to localhost, so there is no separate local smb.conf manipulation path in this file.

Test signals: tests should add/delete level 2 and level 502 shares, enumerate levels 0-2 with more-data resume, get levels 0/1/2/501/1005, set level 1004 comments, validate unsupported 502/503 cases, and specifically run level 0 and level 2 enumeration under sanitizers to catch the `ctr1->count` risk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/shutdown.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/shutdown.c

Purpose: implements NetAPI shutdown initiation and abort operations over the INITSHUTDOWN RPC interface. It provides remote handlers plus local wrappers that redirect to localhost.

Important APIs/functions: `NetShutdownInit_r` creates an `lsa_StringLarge` message and calls `dcerpc_initshutdown_Init` with timeout, force-applications, and reboot flags. `NetShutdownAbort_r` calls `dcerpc_initshutdown_Abort`. `NetShutdownInit_l` and `NetShutdownAbort_l` use `LIBNETAPI_REDIRECT_TO_LOCALHOST`.

Control flow: each remote handler obtains an INITSHUTDOWN binding through `libnetapi_get_binding_handle`, performs the RPC with `talloc_tos()` scratch memory, converts NTSTATUS transport failures to WERROR, and returns the server's WERROR. The server-name parameter passed inside the RPC is `NULL`; the binding target carries the actual server choice.

State and persistence: no local state is stored. Successful init changes remote machine state by scheduling shutdown/reboot; successful abort cancels a pending shutdown. These are privileged, user-visible, and potentially disruptive operations.

Dependencies/integration: uses generated INITSHUTDOWN client stubs, LSA string initialization helpers, public/private NetAPI headers, and libnetapi binding acquisition. Public `NetShutdownInit` and `NetShutdownAbort` wrappers dispatch into these handlers.

Risks: operations are destructive against real systems and require suitable privileges. There is no local validation of timeout, force, reboot, or message content beyond RPC marshalling. Passing `NULL` as the RPC server argument matches this interface but can surprise maintainers expecting `r->in.server_name` to be forwarded.

Test signals: tests should use a controlled Samba/Windows test target or mocked RPC binding to verify parameter marshalling, access-denied mapping, abort-without-pending behavior, local redirect, and NTSTATUS-to-WERROR conversion without actually shutting down developer hosts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/shutdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/sid.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/sid.c

Purpose: implements public SID string conversion helpers compatible with Windows `ConvertSidToStringSid` and `ConvertStringSidToSid` semantics for the `struct domsid` type exposed in `netapi.h`.

Important APIs/functions: `ConvertSidToStringSid` validates inputs, formats a `domsid` through Samba `dom_sid_str_buf`, duplicates the string with `SMB_STRDUP`, and returns boolean success. `ConvertStringSidToSid` parses a SID string with `string_to_sid`, allocates a `struct domsid` with `SMB_MALLOC`, copies the parsed SID, and returns boolean success.

Control flow: both functions return `false` for NULL parameters or allocation/parsing failure. The conversion path casts between public `struct domsid` and Samba internal `struct dom_sid`, relying on compatible layout.

State and persistence: stateless except for heap allocation returned to the caller. The string result is documented in the header as freed with `free(3)`, while parsed SID memory is allocated with Samba allocation macros; callers must use the expected deallocator for their build.

Dependencies/integration: includes public `netapi.h` and Samba security SID helpers. These functions support callers that need to inspect SIDs returned in user/group/localgroup structures or supply SIDs for local group member operations.

Risks: ABI correctness depends on `struct domsid` matching `struct dom_sid`. Allocation ownership is easy to get wrong because these helpers do not use `NetApiBufferFree`. Invalid SID strings fail cleanly, but there is no detailed error code beyond boolean false.

Test signals: tests should round-trip well-known and domain SIDs, reject malformed strings, handle NULL arguments, verify allocation/free behavior under leak tools, and confirm maximum subauthority handling matches `MAXSUBAUTHS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/common.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/common.c

Purpose: shared command-line option implementation for the libnetapi example/test programs. It maps common popt options into the process-global/current libnetapi context.

Important APIs/functions: `popt_common_callback` handles `--user/-U`, `--password/-p`, `--debuglevel/-d`, and `--kerberos/-k`. `popt_common_netapi_examples` defines the shared popt table included by test binaries through `POPT_COMMON_LIBNETAPI_EXAMPLES`.

Control flow: the callback calls `libnetapi_getctx`, ignores pre/post callback phases, and switches on option value. For `-U user%password`, it splits a temporary copy, sets username/password, then overwrites the password portion of the original argument with `X` characters. For `-U user`, it only sets username; password and Kerberos options use dedicated setters.

State and persistence: mutates the current `libnetapi_ctx` credentials, debug level, and Kerberos mode. It also mutates the command-line argument buffer to mask an inline password. No persistent files are written.

Dependencies/integration: depends on popt, public `netapi.h`, and `common.h`. Every test binary can include the common option table so tests share credential/debug behavior.

Risks: overwriting `arg` requires casting away constness through pointer gymnastics; this assumes popt's argument storage is writable. Inline passwords still exist briefly in process memory and shell history before masking. The callback assumes a libnetapi context already exists; test programs must call `libnetapi_init` before option parsing.

Test signals: tests should parse `-U user`, `-U user%pass`, `-p pass`, `-d level`, and `-k`, then verify the context reflects them. A robustness test should run against readonly argv storage if the platform permits, because the masking behavior is nonportable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/common.h -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/common.h

Purpose: shared declarations and small macros for libnetapi tests. It lets separate test modules share the common popt option table, test-suite entry point declarations, status-print helpers, and portable array/zeroing macros.

Important APIs/types: declares `popt_common_callback`, `popt_common_netapi_examples`, `test_netuseradd`, and module functions `netapitest_localgroup`, `netapitest_user`, `netapitest_group`, `netapitest_display`, `netapitest_share`, `netapitest_file`, `netapitest_server`, and `netapitest_wksta`. Defines `POPT_COMMON_LIBNETAPI_EXAMPLES`, fallback `POPT_TABLEEND`, fallback `ARRAY_SIZE`, `NETAPI_STATUS`, `NETAPI_STATUS_MSG`, and `ZERO_STRUCT`.

Control flow: no executable code is present. Macro expansion controls how test programs include common popt options and how failures are reported with source line numbers and `libnetapi_get_error_string`.

State and persistence: no state is stored. Macros operate on caller variables and print diagnostics to stdout/stderr through the call sites.

Dependencies/integration: includes popt declarations and assumes `NET_API_STATUS`, `struct libnetapi_ctx`, and `libnetapi_get_error_string` are visible from the including translation unit's `<netapi.h>`. It ties the individual test modules into `netapitest.c`.

Risks: `ZERO_STRUCT` uses `memset`, so including files must include `<string.h>`. The status macros evaluate status and context expressions directly and print numeric status as signed `%d`, which can be misleading for large unsigned `NET_API_STATUS` values. The shared fixed test function names mean adding modules requires header and build updates.

Test signals: build coverage is the main signal. Compile all test translation units with this header and verify failure messages include line numbers and readable libnetapi error strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netapitest.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netapitest.c

Purpose: main executable entry point for the libnetapi integration test suite. It initializes libnetapi, parses common options plus a required hostname, and runs the module tests in a fixed sequence.

Important APIs/functions: `main` calls `libnetapi_init`, configures popt with `POPT_COMMON_LIBNETAPI_EXAMPLES`, retrieves `hostname`, then invokes `netapitest_localgroup`, `netapitest_user`, `netapitest_group`, `netapitest_display`, `netapitest_share`, `netapitest_file`, `netapitest_server`, and `netapitest_wksta`.

Control flow: test execution is fail-fast. If a module returns nonzero, the remaining modules are skipped, a suite failure message is printed, and cleanup runs. Missing hostname prints popt help and exits through the common cleanup path.

State and persistence: creates a process-local `libnetapi_ctx` and frees it before exit. The modules it calls may persistently create/delete users, groups, local groups, and shares on the target host. This driver itself persists nothing.

Dependencies/integration: depends on popt, public `netapi.h`, and the declarations in `common.h`. The build file links this driver with all module sources into the `netapitest` binary.

Risks: because modules are destructive and fail-fast, a failure can leave target-side objects until each module's own cleanup runs. The ordering puts localgroup before user/group/share tests; later modules may depend on privileges established through the parsed credentials. If `libnetapi_init` fails, popt is never initialized and the status is returned directly.

Test signals: run against an isolated Samba test instance with admin credentials. Verify missing-hostname behavior, credential option parsing, fail-fast semantics, cleanup after failures, and final process exit code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netapitest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netdisplay.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netdisplay.c

Purpose: integration tests for `NetQueryDisplayInformation` display enumeration. It checks user, machine, and group display levels.

Important APIs/functions: `test_netquerydisplayinformation` loops over `NetQueryDisplayInformation` for a level, casts returned buffers to `NET_DISPLAY_USER`, `NET_DISPLAY_MACHINE`, or `NET_DISPLAY_GROUP`, optionally searches for a supplied name, and frees each buffer. `netapitest_display` runs levels 1, 2, and 3.

Control flow: enumeration starts at index 0, requests up to 1000 entries and unlimited preferred length, increments `idx` by `entries_read`, and repeats while status is `ERROR_MORE_DATA`. It treats both success and more-data as readable buffers.

State and persistence: read-only against the target account database. Process-local state is limited to temporary buffers and counters. Buffers are released with `NetApiBufferFree`.

Dependencies/integration: depends on public display structs in `netapi.h` and shared status helpers in `common.h`. `netapitest.c` runs this after user/group modules, but this file does not require a specific test account unless `name` is supplied.

Risks: advancing by `entries_read` assumes the API's index contract matches this simple pattern; some display APIs expose `next_index` fields that may be more precise. If `entries_read` is zero with `ERROR_MORE_DATA`, the loop could spin. Name matching is case-insensitive through `strcasecmp`, which matches Windows-ish expectations but is locale-sensitive.

Test signals: run levels 1-3 against a populated domain, verify multi-page enumeration, validate optional name search, and include a guard test for zero-entry more-data behavior if the server can produce it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netdisplay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netfile.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netfile.c

Purpose: integration tests for `NetFileEnum` and placeholder coverage for `NetFileGetInfo`. It verifies that file enumeration levels 2 and 3 can be called successfully on the target host.

Important APIs/functions: `test_netfileenum` calls `NetFileEnum` with NULL base path and user name, a requested level, unlimited preferred length, and a resume handle. `netapitest_file` invokes it for levels 2 and 3.

Control flow: the helper loops while status is `ERROR_MORE_DATA`, accepts success/more-data buffers, validates that the level is one of 2 or 3, iterates over `entries_read` without inspecting fields, frees the buffer, and returns final status. A disabled `#if 0` block sketches future `NetFileGetInfo` tests.

State and persistence: read-only enumeration of open remote files. No target-side state is changed. The test's usefulness depends on whether the server has open files at runtime.

Dependencies/integration: depends on public `NetFileEnum`, `FILE_INFO_2`, `FILE_INFO_3` declarations from `netapi.h` and shared helpers from `common.h`. It is run by `netapitest.c` after share tests.

Risks: because the loop does not inspect returned fields, it mostly catches transport/level regressions rather than data-mapping regressions. If `NetFileEnum` returns `ERROR_MORE_DATA` with zero entries, resume behavior may loop. The disabled get-info block references an unavailable `fid`, so meaningful file-detail testing still needs a setup phase that opens a file.

Test signals: stronger tests should open a known file over SMB, verify it appears in level 2/3 enumeration, close it with `NetFileClose` where appropriate, and then query `NetFileGetInfo` for its id.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netgroup.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netgroup.c

Purpose: destructive integration tests for global/domain group NetAPI operations. It creates test groups and users, exercises enumeration, get/set info, membership add/delete/set, and cleanup.

Important APIs/functions: helpers `test_netgroupenum`, `test_netgroupgetusers`, and `test_netgroupsetusers` cover `NetGroupEnum`, `NetGroupGetUsers`, and `NetGroupSetUsers` levels 0/1 as applicable. `netapitest_group` drives `NetGroupAdd`, duplicate-add failure, `NetGroupGetInfo`, optional rename through `NetGroupSetInfo`, `NetGroupAddUser`, `NetGroupDelUser`, `NetGroupSetUsers`, `NetUserDel`, and `NetGroupDel`.

Control flow: the test first deletes fixed names `torture_test_group`, `torture_test_group2`, and `torture_test_user`, creates a group, verifies duplicate add fails, enumerates levels 0-3 looking for the group, queries levels 0-3 while tolerating status 124 for not-implemented, attempts rename and tolerates not-supported/not-implemented, creates a user via shared `test_netuseradd`, checks membership absence/presence across operations, and finally deletes user and group.

State and persistence: mutates the target SAM database by creating/deleting global groups and a user, renaming a group when supported, and changing group membership. Test buffers are allocated with `NetApiBufferAllocate` and freed with `NetApiBufferFree`.

Dependencies/integration: depends on user creation helper from `netuser.c`, group structs from `netapi.h`, and shared macros from `common.h`. It requires credentials with account-management rights on the target.

Risks: fixed object names can collide with concurrent test runs or preexisting accounts. Failure paths before cleanup can leave accounts/groups behind, though the start cleanup makes later runs recover. The disabled zero-member `NetGroupSetUsers` block leaves one membership edge untested. Some status handling uses raw numeric codes 50 and 124, which can obscure platform-specific error mapping.

Test signals: run in isolated domains, verify all levels return expected structures, add concurrency isolation with unique names, enable membership wipe tests once supported, and inspect SAM state after failure injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netlocalgroup.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netlocalgroup.c

Purpose: destructive integration tests for local group NetAPI operations. It covers local group creation, enumeration, get-info levels, rename through set-info, delete, and negative lookup after delete.

Important APIs/functions: `test_netlocalgroupenum` loops over `NetLocalGroupEnum` levels 0 and 1 and searches returned `LOCALGROUP_INFO_*` entries for a group name. `netapitest_localgroup` drives `NetLocalGroupAdd`, `NetLocalGroupGetInfo`, `NetLocalGroupSetInfo`, `NetLocalGroupDel`, and post-delete `NetLocalGroupGetInfo`.

Control flow: fixed names `torture_test_localgroup` and `torture_test_localgroup2` are deleted first. The test adds level 0 group data, enumerates levels 0/1, queries levels 0/1/1002 while tolerating status 124, renames the group with level 0 set-info, verifies the old name cannot be deleted, queries the new name, deletes it, and verifies get-info no longer succeeds.

State and persistence: mutates the target's local alias database by creating, renaming, and deleting local groups. Temporary buffers are released through `NetApiBufferFree`.

Dependencies/integration: depends on public local group structs/prototypes and shared macros. It requires administrative rights on the target server.

Risks: no local group membership APIs are exercised despite being declared in `netapi.h`. Fixed names are unsafe for parallel test runs. If rename succeeds but later assertions fail, cleanup only deletes the new name along the main path; failure in the middle can leave objects until the next run's initial cleanup.

Test signals: add tests for `NetLocalGroupAddMembers`, `DelMembers`, `GetMembers`, and `SetMembers`, use unique names per run, verify level 1002 comment behavior, and run post-failure cleanup checks against the target SAM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netlocalgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netserver.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netserver.c

Purpose: integration tests for `NetServerGetInfo` levels. It verifies that the server info query path can be called for common LANMAN/SRVSVC levels.

Important APIs/functions: `netapitest_server` iterates levels 100, 101, 102, 402, 403, 502, 503, and 1005, calls `NetServerGetInfo`, and treats status 124 as tolerated not-implemented behavior.

Control flow: the test is a simple fail-fast loop. Each level allocates a local `buffer` pointer, calls the API, and aborts on errors other than 124. It does not inspect or free returned buffers in the visible code, so it primarily checks call success.

State and persistence: read-only target interaction. No server configuration is changed. Any allocated output should be freed for leak cleanliness, but this test does not call `NetApiBufferFree`.

Dependencies/integration: uses public `NetServerGetInfo` declarations and shared `ARRAY_SIZE`/status macros. It is run near the end of `netapitest.c`.

Risks: the test includes level 403 even though `serverinfo.c` remote validation rejects it, relying on tolerated status 124. Lack of field validation can miss mapping regressions. Missing buffer free may show up under leak detectors if the process lifetime is extended or many runs happen in-process.

Test signals: strengthen by checking expected server name/comment/version fields for levels 100/101/102/1005, freeing buffers, explicitly asserting unsupported levels, and adding `NetServerSetInfo` tests in a disposable registry-backed configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netshare.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netshare.c

Purpose: destructive integration tests for share NetAPI operations. It creates a test share, enumerates it, queries multiple levels, changes its comment, verifies the change, and deletes it.

Important APIs/functions: `test_netshareenum` loops over `NetShareEnum` levels 0, 1, and 2 and searches for a share name. `netapitest_share` exercises `NetShareAdd` levels 502 and 2, `NetShareDel`, `NetShareGetInfo` levels 0/1/2/501/1005, and `NetShareSetInfo` level 1004.

Control flow: the test deletes `torture_test_share`, tries adding level 502 with path `c:\`, deletes it, adds level 2, enumerates levels 0-2, queries supported get levels while tolerating 124, sets a comment through level 1004, fetches level 501, compares the returned remark, deletes the share, and verifies get-info fails.

State and persistence: mutates target share configuration. The path is Windows-style `c:\`, so the target environment must accept or map it. Output buffers are mostly freed in enum helper, but some get-info buffers are not freed in the main routine.

Dependencies/integration: depends on public share structs and prototypes plus shared test macros. It requires privileges to add/delete shares on the target and a server implementation that accepts the chosen path.

Risks: fixed share name and path make parallel or non-Windows-like test environments fragile. The test uses level 501 after setting level 1004 to verify remarks, matching implementation mapping, but does not validate DFS flags or security descriptors. Failure before deletion can leave a share behind. The implementation risk in `NetShareEnum_r` for counter selection should be caught by this test under sanitizers.

Test signals: run against isolated targets with unique names, validate level 2 fields, add security descriptor round-trip coverage for 502 where supported, free all buffers, and inject add/set/delete failures to confirm cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netuser.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netuser.c

Purpose: destructive integration tests for user account NetAPI operations and user modals policy calls. It creates a user, enumerates/query levels, changes a comment, verifies group listing, deletes the user, and round-trips modals level 0.

Important APIs/functions: `test_netuserenum` covers `NetUserEnum` levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. `test_netuseradd` creates a level 1 user with a fixed password and comment. `test_netusermodals` calls `NetUserModalsGet` levels 0-3, writes level 0 back through `NetUserModalsSet`, and compares the result. `test_netusergetgroups` enumerates a user's global groups at levels 0 and 1. `netapitest_user` orchestrates add, enum, get-info, set-info level 1007, delete, and modals tests.

Control flow: fixed users `torture_test_user` and `torture_test_user2` are deleted first. A user is created, enumerated across supported levels, queried across the same levels with status 124 tolerated, group membership is enumerated, the comment is changed with `USER_INFO_1007`, queries are repeated, the user is deleted, deletion is verified by expecting get-info failure, and modals are tested. Cleanup deletes both fixed users again on exit.

State and persistence: mutates the target SAM by creating/deleting users, changing a user comment, and writing user modals policy level 0 back to its existing value. The fixed password is embedded in source. Buffers are freed in enumeration helpers but not consistently after get-info/modals calls.

Dependencies/integration: depends on public user, group-users, and modals structs, shared status helpers, and administrative credentials. Other test modules call `test_netuseradd`.

Risks: fixed names/passwords and policy writes require isolated test targets. Writing modals level 0 back should be idempotent but still exercises a persistent policy path and could alter state if structures include server-normalized fields. `memcmp` on `USER_MODALS_INFO_0` assumes no padding differences; the struct currently contains only `uint32_t` fields, making that acceptable. Leak detectors may flag unfreed get-info/modals buffers.

Test signals: use unique account names, assert actual field values after set-info, verify password policy remains unchanged, add negative tests for duplicate user add/delete missing user, and run under leak/sanitizer tooling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netwksta.c -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netwksta.c

Purpose: integration tests for `NetWkstaGetInfo` workstation information queries. It checks basic WKSSVC/NetAPI support levels.

Important APIs/functions: `netapitest_wksta` iterates levels 100, 101, and 102, calls `NetWkstaGetInfo`, and tolerates status 124 for not-implemented behavior.

Control flow: simple fail-fast loop with a fresh output buffer pointer per level. It prints the level under test, treats nonzero/non-124 status as failure, and reports suite-level success/failure.

State and persistence: read-only target interaction. No workstation configuration is changed. Returned buffers are not explicitly freed in this test.

Dependencies/integration: depends on public `NetWkstaGetInfo` and shared test macros. The file is compiled into `netapitest` by `wscript_build`.

Risks: field contents are not validated, so mapping bugs can pass. Missing buffer free is a leak signal. The test assumes levels 100-102 are the relevant coverage set and does not exercise workstation set-info or domain/workgroup transitions.

Test signals: validate returned workstation name/domain/user fields where stable, free buffers, explicitly assert unsupported levels, and run against both standalone and domain-joined Samba configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/netwksta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/wscript_build -->
# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/wscript_build

Purpose: Waf build snippet for the libnetapi integration test binary. It defines how the `netapitest` executable is built from the test modules.

Important APIs/functions: calls `bld.SAMBA_BINARY('netapitest', source='netapitest.c netlocalgroup.c netuser.c netgroup.c netdisplay.c netshare.c netfile.c netserver.c netwksta.c common.c', deps='netapi popt', install=False)`.

Control flow: build-time only. When included by Samba's Waf build, it registers one non-installed binary target named `netapitest`.

State and persistence: no runtime state. Build artifacts are generated by Waf according to the target definition, but the binary is not installed.

Dependencies/integration: links against the `netapi` library under test and `popt` for option parsing. The source list must stay in sync with declarations in `common.h` and the sequence in `netapitest.c`.

Risks: adding a new test module requires editing this source list manually. `install=False` means package/install tests will not automatically include the binary. The shebang is harmless for Waf inclusion but this file is not a standalone script in practice.

Test signals: build Samba with this target enabled, verify `netapitest` links with all module symbols resolved, and run the binary against an isolated test server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/tests/wscript_build -->
