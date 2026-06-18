# subset-b-007707 research

This grouped report covers the requested OpenAFS Windows AFSD utility, Kerberos compatibility, NetBIOS/LANA, Active Directory logon, MSRPC, server-service, chmod parser, and raw cache I/O source files. Each file section is wrapped with reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.c

Purpose: implements shared Windows-side helpers used by the OpenAFS `fs` command family and related AFSD user-mode tooling. It handles drive-letter/path normalization, mount-root registry discovery, AFS path detection via pioctl, NetBIOS name lookup, local AFS client admin checks, UTF-16-to-UTF-8 command-line conversion, command error reporting, and cache-manager file-type labels.

Important APIs/types/functions: `fs_ExtractDriveLetter`, `fs_StripDriveLetter`, and `fs_GetFullPath` normalize DOS drive paths into drive-less absolute paths expected by pioctl callers. `fs_utils_InitMountRoot` reads `Mountroot` from `AFSREG_CLT_SVC_PARAM_SUBKEY` and initializes global `cm_mount_root`, `cm_slash_mount_root`, and `cm_back_slash_mount_root`. `fs_GetParent` returns a static parent-path buffer. `GetFileSystemNameInfo` dynamically uses `GetFileInformationByHandleEx(FileNameInfo)` to resolve junctions and mappings before pioctl. `fs_InAFS` sends `VIOCGETFID` with literal query options to test whether a path belongs to AFS. `fs_IsFreelanceRoot` probes `VIOC_FILE_CELL_NAME` and treats failures as restrictive freelance-root positives. `fs_NetbiosName` reads the configured SMB NetBIOS server name. `fs_IsAdmin` checks membership in the local `AFS Client Admins` group or LocalSystem. `fs_MakeUtf8Cmdline` and `fs_FreeUtf8CmdLine` manage converted argv storage. `fs_Die`, `fs_SetProcessName`, and `fs_filetypestr` provide command diagnostics and type display strings.

Control flow: command code typically initializes the mount-root globals, normalizes incoming paths, tests membership with `fs_InAFS`, then performs pioctl operations. `fs_GetFullPath` may temporarily switch the process current directory to another drive to resolve drive-relative paths, then restores the original directory. AFS membership first attempts OS path resolution through a file handle, then sends a cache-manager ioctl with literal path semantics. Admin detection is lazy and cached: the first call resolves the local group SID, opens the process token, checks membership, falls back to explicit group enumeration if `CheckTokenMembership` fails, and finally allows LocalSystem.

State/persistence: mount-root strings and cached admin result are process globals. Registry values under the OpenAFS client service parameters affect mount-root, NetBIOS name, and admin assumptions. `fs_GetParent` returns a single static buffer and is not reentrant. `fs_utils_InitMountRoot` allocates new strings without freeing previous defaults or earlier allocations.

Dependencies/integration: depends on Windows registry, Win32 file/query APIs, NetBIOS headers, OpenAFS pioctl opcodes, `cm_ioctlQueryOptions_t`, `cm_fid_t`, `pioctl_utf8`, string-safe APIs, and OpenAFS error mappings. It is included by command-line tools and code paths that need to bridge Windows path syntax to AFSD pioctl syntax.

Risks: `fs_utils_InitMountRoot` contains `if ((*pmount=='/') || (*pmount='\\'))`, assigning a backslash in the second condition; that makes the condition true and mutates the first byte when the first test is false. Several buffer failures call `exit(1)`, which is acceptable for command tools but risky if reused in library-like contexts. `GetFileSystemNameInfo` indexes by `FileNameLength/2` while `WideCharToMultiByte` returns bytes, so truncation and termination deserve scrutiny. Static buffers and cached globals are not thread-safe. `fs_GetFullPath` changes process current directory and could race in multithreaded callers.

Test signals: exercise drive-relative, UNC, junction, mount-root, freelance-root, and non-AFS paths; registry-present and registry-missing paths; group-present/group-absent admin checks; LocalSystem detection; UTF-8 conversion failure cleanup; and `fs_Die` mappings for common pioctl/cache-manager errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.h

Purpose: declares the Windows AFSD utility surface exported by `fs_utils.c` and related host utility functions. It gives command modules access to pioctl constants, PRSFS rights, NT error mappings, path helpers, AFS membership checks, command-line conversion, diagnostics, and mount-root globals.

Important APIs/types/functions: prototypes include `fs_utils_InitMountRoot`, `fs_StripDriveLetter`, `fs_ExtractDriveLetter`, `fs_GetFullPath`, `fs_GetParent`, `fs_InAFS`, `fs_IsFreelanceRoot`, `fs_NetbiosName`, `fs_IsAdmin`, `fs_MakeUtf8Cmdline`, `fs_FreeUtf8CmdLine`, `fs_Die`, `fs_filetypestr`, and `fs_SetProcessName`. It also declares `hostutil_GetNameByINet`, `hostutil_GetHostByName`, `util_GetInt32`, `NETBIOSNAMESZ`, and the global mount-root string pointers.

Control flow: consumers include this header to normalize user input before issuing pioctls and to present consistent diagnostics after failures. The duplicated `fs_utils_InitMountRoot` prototype is harmless but signals historical accretion.

State/persistence: exposes mutable process-global `cm_mount_root`, `cm_slash_mount_root`, and `cm_back_slash_mount_root`; callers must treat them as initialized by `fs_utils_InitMountRoot` and not as immutable compile-time constants.

Dependencies/integration: includes SMB ioctl constants, PRSFS rights, NT pioctl definitions, Winsock host types outside MFC, and OpenAFS NT errmap definitions. The header is a bridge between Windows command code and OpenAFS cache-manager APIs.

Risks: exported globals make initialization ordering important. Callers may assume returned strings are thread-safe or owned by the caller when some are static/global. The header lacks SAL or ownership annotations for buffers and returned argv storage.

Test signals: compile consumers with and without `_MFC_VER`, verify all command modules see pioctl/right constants, and test initialization before use of mount-root globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/krb.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/krb.h

Purpose: provides a Kerberos v4 compatibility header excerpted from MIT Kerberos material for OpenAFS Windows code that still references legacy ticket, principal, and protocol constants.

Important APIs/types/functions: defines success/failure constants, Kerberos name component sizes, ticket text size (`MAX_KTXT_LEN`), `struct ktext`/`KTEXT`/`KTEXT_ST`, retry and timeout constants for KDC communication, default ticket lifetime, clock-skew tolerance, and many KDC/library error codes. It includes `krb_prot.h` and declares a legacy `static send_to_kdc(KTEXT pkt, KTEXT rpkt)` prototype without an explicit return type.

Control flow: there is no executable control flow. Including code uses these constants and packet text types when building or parsing legacy Kerberos v4 protocol data.

State/persistence: no runtime state. The constants define fixed wire-buffer sizes and error-code contracts. `struct ktext` contains an `mbz` field intended to remain zero as a guard against runaway strings.

Dependencies/integration: depends on `<hcrypto/des.h>` for DES-era Kerberos support and on `krb_prot.h` for wire message macros and message types. It integrates with older AFS authentication paths that predate Kerberos v5-only APIs.

Risks: Kerberos v4 and DES are obsolete security mechanisms; any live authentication use should be treated as legacy compatibility. Fixed-size principal fields can truncate longer modern names. The K&R-style implicit-int `static send_to_kdc` declaration is incompatible with modern strict C modes and can hide ABI mistakes.

Test signals: compile with modern MSVC/C warning levels, verify no new code depends on v4-only authentication, and regression-test any legacy token path that still maps these error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/krb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/krb_prot.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/krb_prot.h

Purpose: defines Kerberos v4 wire-protocol constants and packet-field access macros used by the legacy Kerberos compatibility header.

Important APIs/types/functions: constants include `KRB_PORT`, `KRB_PROT_VERSION`, `MAX_PKT_LEN`, `MAX_TXT_LEN`, and `TICKET_GRANTING_TICKET`. Macros such as `pkt_version`, `pkt_msg_type`, `pkt_a_name`, `pkt_a_inst`, `pkt_a_realm`, `pkt_time_ws`, `pkt_no_req`, `pkt_x_date`, `pkt_err_code`, and `pkt_err_text` compute offsets inside a `KTEXT` packet. It declares legacy packet constructors/readers `create_auth_reply`, `create_death_packet`, and `pkt_cipher`, and defines Kerberos v4 message and error constants.

Control flow: no direct control flow. Consumers use pointer arithmetic macros to walk variable-length NUL-terminated fields inside a Kerberos v4 packet.

State/persistence: no state. It defines fixed packet layouts and message type values that must match the v4 wire protocol.

Dependencies/integration: expects `KTEXT` from `krb.h` and standard C string semantics. It is part of OpenAFS's Windows compatibility layer for old Kerberos/AFS token handling.

Risks: macros perform unchecked pointer arithmetic and `strlen` over packet data, so malformed or unterminated packets can read outside packet bounds if callers do not validate first. Function declarations omit prototypes/return types in old C style. The protocol itself is obsolete and should not be expanded.

Test signals: fuzz or negative-test packet parsing callers with truncated and unterminated packets, and compile under strict prototype warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/krb_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.cpp

Purpose: discovers Windows NetBIOS LANA adapters and builds the NetBIOS/UNC server name used by the OpenAFS SMB gateway. It maps network-adapter GUIDs to friendly names, identifies loopback adapters, honors OpenAFS registry configuration, and formats names such as `AFS` or `<hostname>-AFS`.

Important APIs/types/functions: `lana_ShellGetNameFromGuidW` can use the Network Connections shell folder, though `lana_GetNameFromGuid` currently forces the undocumented `netman.dll` `HrLanConnectionNameFromGuidOrPath` path. `lana_FindLanaByName` reads `Services\NetBios\Linkage` `LanaMap` and `Bind`, filters IPv4 `_Tcpip_` bindings, extracts GUIDs, and returns `LANAINFO` entries. `lana_FindLoopback`, `lana_OnlyLoopback`, and `lana_IsLoopback` enumerate/reset NetBIOS adapters and compare known loopback MAC patterns or the `ForceLanaLoopback` registry override. `lana_GetUncServerNameEx` is the main policy routine for selecting LANA/gateway settings and building the name. `lana_GetUncServerNameDynamic`, `lana_GetUncServerName`, `lana_GetAfsNameString`, and `lana_GetNetbiosName` are formatting wrappers.

Control flow: name generation starts by reading `LanAdapter`, `IsGateway`, optional `NoFindLanaByName`, and `NetbiosName` from the OpenAFS service-parameter registry. If no LANA is configured, it optionally looks for an adapter named `AFS`, then a loopback adapter when not configured as a gateway. If the chosen adapter is loopback and not a gateway, the configured suffix becomes the whole NetBIOS name; otherwise the helper prefixes the local computer name and appends the suffix. Wrapper functions convert this char buffer to `TCHAR`.

State/persistence: registry values are persistent configuration inputs. No durable state is written. Returned `LANAINFO` and GUID-name strings are heap-allocated for callers to free. NetBIOS reset has process-local adapter initialization effects.

Dependencies/integration: depends on Windows registry, NetBIOS `Netbios` NCB calls, shell/COM APIs, `netman.dll`, network adapter binding registry layout, `AFSREG_CLT_SVC_PARAM_SUBKEY`, and `lanahelper.h`. AFSD SMB startup and UI/display code use these helpers to decide the UNC name.

Risks: the primary friendly-name path uses an undocumented `netman.dll` export and may fail on modern Windows. COM initialization/uninitialization is unconditional inside the shell helper and may interact poorly with callers that already initialized COM with a different apartment. Several string copies use fixed `MAX_NB_NAME_LENGTH` buffers and older `_tcscpy`/`strncat` patterns. Loopback detection by MAC prefix is fragile. `lana_FindLanaByName` can return without closing the registry key on zero `LanaMap` data. The code assumes ANSI conversion for GUID/friendly names.

Test signals: cover registry-configured LANA and gateway values, missing registry defaults, loopback-only machines, machines with no NetBIOS adapters, long host/suffix names, failure to load `netman.dll`, Unicode builds, and `LANA_NETBIOS_NAME_SUFFIX/FULL/IN/NO_RESET` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.h

Purpose: declares the C-callable LANA/NetBIOS helper interface implemented by `lanahelper.cpp`.

Important APIs/types/functions: defines `lana_number_t`, `struct LANAINFO`, invalid value `LANA_INVALID`, maximum NetBIOS name length, and flags `LANA_NETBIOS_NAME_SUFFIX`, `LANA_NETBIOS_NAME_FULL`, `LANA_NETBIOS_NAME_IN`, and `LANA_NETBIOS_NO_RESET`. Exports GUID-name lookup, LANA discovery, loopback checks, UNC server-name generation, and display-string helpers.

Control flow: callers can either use high-level `lana_GetUncServerName`/`lana_GetNetbiosName` or perform explicit discovery with `lana_FindLanaByName`, `lana_FindLoopback`, and `lana_IsLoopback` before passing selected values to `lana_GetUncServerNameEx`.

State/persistence: no state in the header. Ownership is implicit: `lana_GetNameFromGuid` may allocate `*Name`, and `lana_FindLanaByName` returns an allocated array terminated by `LANA_INVALID`.

Dependencies/integration: includes Windows and TCHAR headers and uses `extern "C"` for C/C++ ABI compatibility. Used by AFSD SMB setup and Windows configuration/display components.

Risks: ownership and buffer-size requirements are not encoded in the function signatures. `lana_GetUncServerNameEx` assumes the output buffer can hold at least `MAX_NB_NAME_LENGTH` bytes/chars depending on caller context.

Test signals: compile from both C and C++ consumers, verify Unicode and ANSI builds, and test allocation/free conventions for discovery functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/largeintdotnet.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/largeintdotnet.c

Purpose: supplies compatibility implementations of old Windows `LARGE_INTEGER` helper routines for MSVC 7.0 and newer builds where those functions are not available as expected.

Important APIs/types/functions: under `_MSC_VER >= 1300`, implements `LargeIntegerAdd`, `LargeIntegerSubtract`, `ExtendedLargeIntegerDivide`, `LargeIntegerDivide`, and `ConvertLongToLargeInteger`. The add/subtract routines manually handle low-part carry/borrow; divide routines combine high/low parts into `ULONGLONG`, divide, and split quotient/remainder back into `LARGE_INTEGER`.

Control flow: simple arithmetic helpers return zeroed results for divide-by-zero, return the original dividend for divide-by-one, and otherwise use unsigned 64-bit division.

State/persistence: no mutable state or persistence.

Dependencies/integration: depends on Windows `LARGE_INTEGER` layout and is used by older AFSD cache and raw I/O code that calls Windows-style large integer helpers.

Risks: signedness is subtle because `HighPart` is assigned into `ULONGLONG`; negative `LARGE_INTEGER` values are not clearly handled as signed arithmetic. `ExtendedLargeIntegerDivide` dereferences `remainder` without null checks in nontrivial cases. Divide-by-zero silently returns zero instead of surfacing an error. The `if (r1 > ULONG_MAX) /*XXX */;` branch is a no-op.

Test signals: verify carry/borrow boundaries, high-part propagation, division by zero/one, 64-bit values above 4 GiB, and behavior for negative high parts if any caller can pass signed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/largeintdotnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/logon_ad.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsd/logon_ad.cpp

Purpose: implements Active Directory and SSPI helpers used during Windows logon integration. It obtains delegated security contexts for a logon LUID, impersonates the user, queries AD profile/home information, determines the local AD short domain, and creates AFS authentication groups/PAGs through the redirector control device.

Important APIs/types/functions: `_get_sec_err_text` maps common SSPI statuses for diagnostics. `LogonSSP` acquires `Negotiate` credentials for a logon ID and loops `InitializeSecurityContext`/`AcceptSecurityContext` until it obtains a delegated server context. `QueryAdHomePathFromSid` converts a SID to a string, uses `IADsNameTranslate` to map SID to an LDAP path, opens `IADsUser`, and reads the profile path. `GetAdHomePath` combines `LogonSSP`, impersonation, `LsaGetLogonSessionData`, and `QueryAdHomePathFromSid`, setting `LOGON_FLAG_AD_REALM` on success. `GetLocalShortDomain` uses `IADsADSystemInfo::get_DomainShortName`. `OpenRedirector` opens `AFS_SYMLINK_W`. `AFSCreatePAG` builds an `AFSAuthGroupRequestCB` from the user SID/session and sends redirector IOCTLs to query and create an auth group.

Control flow: logon paths first create a delegated SSPI context, impersonate it, and then use LSA/ADSI under the user's security context. PAG creation intentionally toggles impersonation: it queries auth-group state outside and inside impersonation, reverts before issuing the create IOCTL, then queries again to log before/after GUIDs.

State/persistence: no local persistent state is written by the file. External state changes occur through `IOCTL_AFS_AUTHGROUP_LOGON_CREATE` to the redirector, which creates/updates auth-group association for the logon session. COM is initialized and uninitialized per query. ADSI and LSA buffers are allocated/freed per call.

Dependencies/integration: depends on SSPI/Secur32, LSA logon session APIs, ADSI COM interfaces, SDDL SID conversion, RPC UUID formatting, AFS logon option structures, and AFS redirector user IOCTL definitions under `afsrdr/common`. It integrates Windows logon authentication with AFS PAG/auth-group semantics.

Risks: `LogonSSP` has complex token-buffer ownership; error paths can leak or double-manage SSPI buffers if statuses differ from expected sequences. Domain copying in `GetAdHomePath` treats `UNICODE_STRING.Length` as a WCHAR count even though it is bytes, which can over-allocate and terminate at the wrong index. `wcstombs` in `QueryAdHomePathFromSid` does not guarantee null termination on truncation. `AFSCreatePAG` allocates `pAuthGroup` but does not free it in cleanup. COM apartment assumptions are implicit. The code logs sensitive path/SID/auth-group information through `DebugEvent`.

Test signals: exercise domain and non-domain logons, missing delegation, AD GC unavailable with domain fallback, long profile paths, SID conversion failures, redirector unavailable, IOCTL failures, and leak checks around `AFSCreatePAG` and SSPI loop exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/logon_ad.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ms-srvsvc.idl -->
# sources/distributed-fs/openafs/src/WINNT/afsd/ms-srvsvc.idl

Purpose: defines the MIDL server-service (`srvsvc`) RPC contract used by the custom AFSD MSRPC transport. It mirrors Microsoft SRVSVC structures and opnums enough for Windows clients to ask the AFS SMB endpoint about shares and server metadata.

Important APIs/types/functions: declares UUID `4B324FC8-1670-01D3-1278-5A47BF6EE188`, version 3.0, `ms_union`, `SRVSVC_HANDLE`, `NET_API_STATUS`, connection/file/session/share/server/transport/security/time/DFS/alias structures, discriminated unions for enum/get-info levels, `SHARE_DEL_HANDLE`, and all SRVSVC operations. Important operations for the current implementation are `NetrShareEnum`, `NetrShareGetInfo`, and `NetrServerGetInfo`; most other declared operations are stubbed in `rpc_srvsvc.c`.

Control flow: this file is compiled by MIDL into server stubs and an interface spec consumed by `msrpc.c`. The custom MSRPC dispatcher uses the generated dispatch table after a DCE/RPC bind to this abstract syntax.

State/persistence: no runtime state in the IDL. It defines wire-level memory ownership, `[size_is]`, `[string]`, `[switch_is]`, and context-handle contracts used during marshaling.

Dependencies/integration: imports `wtypes.idl`; generated files expose `srvsvc_v3_0_s_ifspec` and server entry-point signatures. It must stay in sync with `rpc_srvsvc.c` implementations and the custom `MIDL_user_allocate`/RPC allocation shims.

Risks: the contract is large while implementation coverage is narrow; Windows clients may bind and call unsupported opnums. Any mismatch between union cases, level structs, and `rpc_srvsvc.c` allocation/population can cause marshaling faults. The file includes Microsoft-derived protocol definitions, so changes should track protocol documentation carefully.

Test signals: MIDL compile, bind negotiation via `msrpc.c`, `net view`/share enumeration client behavior, unsupported-opnum error mapping, and marshaling tests for levels 0/1/2/100/101/102/103.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ms-srvsvc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ms-wkssvc.idl -->
# sources/distributed-fs/openafs/src/WINNT/afsd/ms-wkssvc.idl

Purpose: defines the MIDL workstation-service (`wkssvc`) RPC contract so the custom AFSD MSRPC transport can negotiate the well-known WKSSVC interface even if AFSD implements little or none of the workstation-management behavior.

Important APIs/types/functions: declares UUID `6BFFD098-A112-3610-9833-46C3F87E345A`, version 1.0, workstation info structures (`WKSTA_INFO_100/101/102/502` and specific setting levels), user and transport enum containers, workstation statistics, domain join status/name enums, encrypted join-password structures, `UNICODE_STRING`, computer-name arrays, and opnums such as `NetrWkstaGetInfo`, `NetrWkstaUserEnum`, `NetrGetJoinInformation`, join/unjoin/rename/validate-name, and alternate computer-name operations.

Control flow: like `ms-srvsvc.idl`, this is a compile-time wire contract. Generated server tables are included in the MSRPC interface list and selected during bind negotiation.

State/persistence: no local state. The IDL defines NDR memory and string layout for callers and generated stubs.

Dependencies/integration: imports `wtypes.idl`; generated `wkssvc_v1_0_s_ifspec` is referenced by `msrpc.c`. It shares the same custom allocation and NDR initialization shims as SRVSVC.

Risks: if clients call WKSSVC opnums without concrete server implementations, dispatch may return faults or link to missing/stub functions depending on generated code coverage elsewhere in the tree. Domain join operations are sensitive; AFSD should avoid accidentally claiming support without enforcing semantics.

Test signals: MIDL generation, bind/alter-context negotiation for WKSSVC, unsupported operation behavior, and Windows IPC clients that probe `\wkssvc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ms-wkssvc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.c

Purpose: implements a custom DCE/RPC connection-oriented PDU engine for AFSD named-pipe style services. It accepts raw RPC messages from SMB transport code, negotiates binds for generated WKSSVC/SRVSVC interfaces, dispatches request stubs through MIDL dispatch tables, fragments responses, tracks per-call `cm_user_t`, and provides minimal RPC runtime shims required by generated stubs.

Important APIs/types/functions: `_Interfaces` lists `wkssvc_v1_0_s_ifspec` and `srvsvc_v3_0_s_ifspec`. Serialization helpers read/write `E_CommonHeader`, `UUID`, `RPC_VERSION`, and `RPC_SYNTAX_IDENTIFIER`. `write_fault_PDU` and `write_bind_nak_PDU` generate errors. `handle_ConnBind` negotiates presentation contexts and stores the selected interface. `handle_ConnRequest` validates opnum, allocates an RPC message buffer, copies stub data, sets TLS user, and invokes the generated dispatch function. Fragment helpers merge incoming fragmented bind/request PDUs. `dispatch_call`, `MSRPC_WriteMessage`, `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, and `MSRPC_ReadMessage` are the transport-facing queue/dispatch/read API. `I_RpcGetBuffer`, `I_RpcFreeBuffer`, and `NdrServerInitializeNew` emulate RPC runtime functions for generated NDR code. `MSRPC_Init`, `MSRPC_Shutdown`, and `MSRPC_IsWellKnownService` connect service setup and named-pipe filtering.

Control flow: SMB transport submits a complete incoming PDU with `MSRPC_WriteMessage`. Reads trigger lazy dispatch: `MSRPC_PrepareRead` skips completed fragments, assembles multipart messages if needed, handles bind or request PDUs, and leaves a response buffer queued. `MSRPC_ReadMessageLength` predicts the next transport read size. `MSRPC_ReadMessage` either copies prebuilt bind/fault PDUs or wraps a stub response in one or more response PDUs with first/last fragment flags according to `max_recv_frag`.

State/persistence: each `msrpc_conn` stores negotiated fragment sizes, association group, protocol version, selected interface, optional secondary address, and queued calls. Each `msrpc_call` owns aligned input/output buffers, RPC message buffers, status, context ID, and held `cm_user_t` reference. TLS stores the current cache-manager user for service implementations such as `rpc_srvsvc.c`. No durable state is written.

Dependencies/integration: depends on generated MIDL headers for WKSSVC/SRVSVC, OpenAFS cache-manager user references, btree/NLS helpers, Windows RPC/NDR types, pthread-once, and AFSD error codes. It is the glue between SMB IPC named pipes and OpenAFS's in-process RPC service implementations.

Risks: `is_equal_RPC_SYNTAX_IDENTIFIER` compares `s2->MinorVersion` to itself, so minor-version mismatch in the first syntax can be ignored. Cursor read/write macros rely on callers checking space; not every later use rechecks all variable-length inputs. `MSRPC_AllocBuffer` does not handle `_aligned_malloc` failure beyond leaving `buf_data` null after raising `buf_alloc`. Fragment merging has subtle offset/memmove logic and should be fuzzed. Authentication is rejected (`auth_length != 0`), so only unauthenticated local/SMB transport assumptions protect calls. Response fragmentation uses caller-supplied buffers by temporarily swapping `call->out.buf_data`, which is delicate on early returns.

Test signals: DCE/RPC bind acceptance/rejection for supported and unsupported syntax, malformed header/data-representation/auth lengths, fragmented bind/request assembly, oversized message rejection, opnum out-of-range faults, generated stub exceptions, response fragmentation at exact `max_recv_frag` boundaries, TLS user propagation, and leak checks on call queue shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.h

Purpose: declares the custom MSRPC transport API, common DCE/RPC PDU structures, connection/call state, allocation shims, and well-known service helpers used by AFSD SMB IPC handling and generated MIDL stubs.

Important APIs/types/functions: maps RPC runtime names `I_RpcGetBuffer`, `I_RpcFreeBuffer`, and `NdrServerInitializeNew` to local implementations. Defines `MAX_RPC_MSG_SIZE`, `DEF_RPC_MSG_SIZE`, call statuses, PDU types, bind reject reasons, DCE/RPC scalar typedefs, `E_CommonHeader`, `msrpc_buffer`, `msrpc_call`, and `msrpc_conn`. Exports connection lifecycle (`MSRPC_InitConn`, `MSRPC_FreeConn`), transport I/O (`MSRPC_WriteMessage`, `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`), RPC allocation/NDR initialization shims, `MSRPC_GetCmUser`, service init/shutdown, and `MSRPC_IsWellKnownService`.

Control flow: transport callers initialize a connection, write inbound messages, then prepare/read outbound messages until the queued call is consumed. Service implementations can call `MSRPC_GetCmUser` during dispatch to recover the authenticated/cache-manager user attached by the transport.

State/persistence: structures define in-memory queues and buffers. Ownership is explicit at connection/call level but not enforced by type system; `MSRPC_FreeConn` must drain queued calls and release held users.

Dependencies/integration: includes Windows RPC headers and `cm_nls.h`; forward-declares `cm_user_t`; generated MIDL headers depend on the local RPC shim name remapping.

Risks: public structures expose internal queue and buffer fields, so callers can corrupt invariants. Buffer length/allocation positions use unsigned int and must stay within `MAX_RPC_MSG_SIZE`. The API assumes one thread manages a connection at a time; no locks are embedded.

Test signals: compile generated stubs against remapped RPC functions, initialize/free empty and populated connections, round-trip queue status transitions, and validate `MSRPC_IsWellKnownService` matching for case-insensitive named-pipe names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.c

Purpose: parses symbolic Unix chmod-style mode expressions into an updated mode bitmask for OpenAFS Windows command tooling.

Important APIs/types/functions: `parsemode(char *symbolic, afs_uint32 oldmode)` supports `u`, `g`, `o`, `a` selectors; `+`, `-`, and `=` actions; permission symbols `r`, `w`, `x`, `X`, `s`, and `t`; and comma-separated clauses. It uses mode groups from `parsemode.h` and `S_ISDIR` from stat macros. Invalid syntax reports through `fs_Die(EINVAL, "invalid mode")` and exits.

Control flow: starts from `oldmode & ALL_MODES`, parses a `who` mask, requires an action, accumulates a permission mask, then applies the action. If `who` is omitted, additions respect a hard-coded umask `022`; `=` with no `who` clears all tracked bits before adding masked bits. `X` only adds execute bits when the old mode is a directory or already has execute bits.

State/persistence: no state or persistence. It returns a computed mode value and terminates the process on invalid input.

Dependencies/integration: includes `parsemode.h` and `fs.h` for constants and `fs_Die`. Used by chmod-like AFS command code.

Risks: invalid input exits the whole process instead of returning an error. The hard-coded umask `022` ignores process/user umask. Fallthrough from `=` to `+` is intentional but not annotated. The parser handles symbolic modes only; numeric parsing must occur elsewhere.

Test signals: cover each selector/action/symbol, comma-separated operations, `X` for directories and executable files, setuid/setgid/sticky bits, omitted `who` with umask behavior, and invalid syntax exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.h

Purpose: declares the symbolic mode parser and the permission-bit masks it uses.

Important APIs/types/functions: exports `parsemode(char *symbolic, afs_uint32 oldmode)` and defines `USR_MODES`, `GRP_MODES`, `EXE_MODES`, and `ALL_MODES`, conditionally including `S_ISVTX` when available.

Control flow: no direct control flow. The macros determine what `parsemode.c` may preserve, clear, or set.

State/persistence: no runtime state.

Dependencies/integration: requires stat permission macros and OpenAFS integer types to be available in includers. Used by chmod-style command implementation.

Risks: macro definitions depend on platform availability of POSIX mode bits in the Windows build. If stat macros differ, parser behavior shifts.

Test signals: compile under all supported Windows toolchains and verify `ALL_MODES` includes/excludes sticky bit as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rawops.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/rawops.c

Purpose: implements raw cache-manager read and write operations over `cm_scache_t` objects, copying data between caller buffers and OpenAFS cache buffers while coordinating callbacks, buffer fetches, dirty marking, and asynchronous store-back.

Important APIs/types/functions: `raw_ReadData` reads from an scache at an `osi_hyper_t` offset into a caller buffer and returns the number of bytes read. `raw_WriteData` writes caller data into cache buffers, extends file length when necessary, marks dirty ranges, and queues `cm_BkgStore` work. Both are documented as requiring the scache write lock on entry.

Control flow: read first synchronizes callback/status, clamps requested length to EOF, then loops block-by-block. For each cache block, it releases the scache write lock around `buf_Get`, reacquires it, synchronizes for read, fetches missing cache data with `cm_GetBuffer`, copies bytes, advances the offset, and releases the final buffer. Write synchronizes for callback/status/setstatus, updates `scp->length` and mask if extending EOF, loops over buffers, obtains and locks each buffer, skips server fetch when overwriting full or past-EOF data, writes bytes into `bufp->datap`, marks dirty ranges, and on success queues an async background store for the written range.

State/persistence: modifies in-memory scache length/mask and cache buffer data/dirty metadata. Actual persistence to AFS servers is delegated to background store. It holds/releases scache and buffer locks according to cache-manager conventions.

Dependencies/integration: depends on `cm_SyncOp`, `cm_SyncOpDone`, `buf_Get`, `buf_Release`, `cm_HaveBuffer`, `cm_GetBuffer`, `buf_SetDirty`, `cm_QueueBKGRequest`, `cm_BkgStore`, `rock_BkgStore_t`, `cm_data.blockSize`, and large-integer helpers. Integrated into raw SMB/redirector file I/O paths.

Risks: callers must hold the scache write lock exactly as expected; misuse can deadlock or corrupt buffers. `raw_ReadData` defines `sequential` but never sets it, so prefetch is never considered. Write returns without calling `cm_SyncOpDone` for `CM_SCACHESYNC_ASYNCSTORE`; the comment relies on `cm_BkgStore` completion, so failed queueing/sync paths need careful audit. Background-store allocation failure silently leaves dirty data for later normal flushing but does not surface pressure. Partial writes before an error leave `writtenp` updated and dirty buffers present.

Test signals: read at EOF/past EOF, multi-block reads/writes, writes extending file length, full-block overwrite avoiding fetch, partial past-EOF zeroing, simulated `buf_Get`/`cm_GetBuffer` failures, async store queue failure, lock-order stress, and dirty range correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rawops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rawops.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/rawops.h

Purpose: declares the raw scache read/write entry points implemented by `rawops.c`.

Important APIs/types/functions: `raw_ReadData(cm_scache_t *scp, osi_hyper_t *offsetp, afs_uint32 length, char *bufferp, afs_uint32 *readp, cm_user_t *userp, cm_req_t *reqp)` and `raw_WriteData(cm_scache_t *scp, osi_hyper_t *offsetp, afs_uint32 length, char *bufferp, cm_user_t *userp, cm_req_t *reqp, afs_uint32 *writtenp)`.

Control flow: callers pass an scache, mutable offset, byte count, caller buffer, user, and request context. The implementation advances the offset and reports bytes transferred.

State/persistence: no state in the header. The contract implies the implementation mutates scache/cache state and requires lock discipline, but the header does not document that requirement.

Dependencies/integration: relies on OpenAFS cache-manager types being declared before inclusion. Used by low-level raw file I/O code.

Risks: missing include guards and missing lock/ownership comments can lead to duplicate declarations or misuse. Return type differs between read (`afs_int32`) and write (`afs_uint32`) despite both returning error codes.

Test signals: compile all includers, verify prototypes match implementation, and add caller-side tests that enforce write-lock preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rawops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rpc_srvsvc.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/rpc_srvsvc.c

Purpose: implements the subset of Microsoft SRVSVC RPC operations that AFSD exposes over its custom MSRPC layer, primarily share enumeration, share lookup, and server information for the AFS SMB namespace. Unsupported SRVSVC, DFS, transport, session, file, path, security, and alias operations return `ERROR_NOT_SUPPORTED`.

Important APIs/types/functions: `NetrConnectionEnum`, `NetrFileEnum`, `NetrSessionEnum`, and many others are explicit unsupported stubs. `NetrIntGenerateShareRemark` builds user-visible remarks from `cm_scache_t`/FID type, cell, and mountpoint strings. `NetrIntGenerateSharePath` builds `\\server\cell\volume.vnode.unique` style share paths. `RPC_SRVSVC_Init` initializes share-enumeration state and randomizes the resume-handle seed; `RPC_SRVSVC_Shutdown` frees saved enumerations. `RPC_SRVSVC_ShareEnumAgeCheck`, `Find`, `Save`, and `Remove` manage five-minute resume handles. `NetrShareEnum` enumerates the AFS root directory into SRVSVC share levels 0/1/2 while honoring preferred maximum response length. `NetrShareGetInfo` resolves volume references, the special `ALL` share, root entries, freelance/cell names, and registry submounts before returning share info levels 0/1/2. `NetrServerGetInfo` returns AFS platform/name/version/type/comment for levels 100-103.

Control flow: service initialization creates the resume-handle mutex and seed. Share enumeration gets the root scache for `MSRPC_GetCmUser`, validates the requested level, performs or resumes a B+ directory enumeration, allocates a result buffer, skips `.`/`..`, optionally peeks entries to enforce `PreferedMaximumLength`, fills level-specific structs, and either saves the enumeration with a resume handle or frees it when complete. Share lookup tries volume-reference syntax first, then `ALL` registry policy, then root lookup with casefold fallback, then submount registry lookup and `cm_NameI`. Server info strips leading slashes from the server name and fills fallthrough-compatible info structs from highest requested level down.

State/persistence: maintains a process-global queue of saved `cm_direnum_t` enumerations guarded by `shareEnum_mx`, with cleanup deadlines and resume handles. Reads persistent registry values for `AllSubmount` and submount mappings. Does not modify AFS namespace or server state because mutating operations are unsupported.

Dependencies/integration: depends on generated `ms-srvsvc.h`, `msrpc.h`, AFSD cache-manager APIs (`cm_RootSCachep`, `cm_SyncOp`, `cm_BPlusDirEnumerate`, `cm_Lookup`, `cm_NameI`, scache refs), SMB error mapping, OpenAFS registry paths, version macros, MIDL allocation, wide/client string conversion helpers, and AFSD logging.

Risks: `RPC_SRVSVC_ShareEnumAgeCheck` removes expired enumeration records from the queue but does not free their `cm_direnum_t` or wrapper, leaking memory. `NetrShareEnum` may dereference `ResumeHandle` or `TotalEntries` assumptions on malformed clients; level-specific unions are accessed through `Level0` fields after allocating other levels because of union layout assumptions. Space accounting subtracts sizes from `size_t` without guarding underflow when `PreferedMaximumLength` is tiny. `NetrShareGetInfo` relies on registry strings and path buffers sized for cell/volume names. Many functions return plain Win32 errors while some invalid-level paths use `HRESULT_FROM_WIN32`, so client-visible status consistency should be checked.

Test signals: `net view` and `NetShareEnum` levels 0/1/2 over `\\AFS`, pagination with small preferred maximum lengths, resume-handle expiry and cleanup, root entries for files/directories/symlinks/mountpoints/DFS links, `ALL` with `AllSubmount` enabled/disabled, submount registry lookup, volume-reference lookup, server-info levels 100-103, unsupported opnums, memory leak checks around enumeration aging/removal, and concurrent enumerations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/rpc_srvsvc.c -->
