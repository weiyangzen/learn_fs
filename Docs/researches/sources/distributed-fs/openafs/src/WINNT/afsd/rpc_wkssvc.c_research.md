# sources/distributed-fs/openafs/src/WINNT/afsd/rpc_wkssvc.c

## Purpose

`rpc_wkssvc.c` implements the server-side bodies for the Windows Workstation Service (`wkssvc`) MSRPC interface used by the OpenAFS Windows client daemon. It is paired with the generated MIDL server stub from `ms-wkssvc.idl`; the generated stub handles RPC unmarshalling and dispatches into the exported `Netr*` routines in this file.

The implementation is intentionally minimal. The only substantive call is `NetrWkstaGetInfo`, which returns workstation identity/version data for levels 100, 101, and 102. All mutating, enumeration, statistics, domain-join, name-validation, and computer-name management entry points are present to satisfy the wire interface but log and return `ERROR_NOT_SUPPORTED`. The file also defines empty `Opnum*NotUsedOnWire` placeholders for IDL opnums that exist in the protocol layout but have no callable operation.

## Important APIs, Types, and Functions

- `NetrWkstaGetInfo(ServerName, Level, WkstaInfo)`: supports levels 100, 101, and 102. It allocates the requested `WKSTA_INFO_*` structure, strips leading slash characters from `ServerName`, uppercases the returned computer name, sets the workgroup/domain string to `AFS`, sets `PLATFORM_ID_AFS` to `800`, and reports `AFSPRODUCT_VERSION_MAJOR` / `AFSPRODUCT_VERSION_MINOR`.
- `NetrWkstaSetInfo`, `NetrWkstaUserEnum`, `NetrWkstaTransportEnum`, `NetrWkstaTransportAdd`, `NetrWkstaTransportDel`, `NetrWorkstationStatisticsGet`, `NetrGetJoinInformation`, `NetrJoinDomain2`, `NetrUnjoinDomain2`, `NetrRenameMachineInDomain2`, `NetrValidateName2`, `NetrGetJoinableOUs2`, `NetrAddAlternateComputerName`, `NetrRemoveAlternateComputerName`, `NetrSetPrimaryComputerName`, and `NetrEnumerateComputerNames`: protocol entry points that currently only write an `afsd_logp` trace message and return `ERROR_NOT_SUPPORTED`.
- `WKSSVC_IDENTIFY_HANDLE`, `WKSSVC_IMPERSONATE_HANDLE`, `WKSTA_INFO`, `WKSTA_INFO_100`, `WKSTA_INFO_101`, `WKSTA_INFO_102`, `WKSTA_USER_ENUM_STRUCT`, `WKSTA_TRANSPORT_ENUM_STRUCT`, `STAT_WORKSTATION_0`, join-related types, and computer-name types: generated from `ms-wkssvc.idl` into `ms-wkssvc.h` during the Windows build.
- `MIDL_user_allocate`: used to allocate RPC output structures. In this tree the allocator is implemented in `src/WINNT/client_osi/osiutils.c` as `malloc`; the paired `MIDL_user_free` calls `free`.
- `wcsdup` and `_wcsupr`: used for output strings in RPC structures. These allocations are expected to be released by RPC/MIDL ownership handling after marshalling.
- `osi_Log0` and `osi_Log1`: write diagnostic records through the global AFSD log pointer declared in `afsd.h`.
- `AFSPRODUCT_VERSION_MAJOR` and `AFSPRODUCT_VERSION_MINOR`: product version constants from `AFS_component_version_number.h`.

## Control Flow

For `NetrWkstaGetInfo`, the first switch allocates a structure matching the requested level:

- level 102 allocates `WKSTA_INFO_102`
- level 101 allocates `WKSTA_INFO_101`
- level 100 allocates `WKSTA_INFO_100`
- unsupported levels fall through with no allocation

The code then checks the level-100 union member, relying on the union layout so the pointer value is valid regardless of which of the supported cases was assigned. If the pointer is `NULL`, it returns `ERROR_INVALID_LEVEL`. For a supported level, it skips any leading `\` or `/` characters in `ServerName`, then uses intentional switch fallthrough to populate the prefix of the larger workstation structures:

- level 102 sets `wki102_logged_on_users = 0`, then falls through
- level 101 sets `wki101_lanroot = NULL`, then falls through
- level 100 sets the common workstation fields and returns success

The common fields are the uppercase server/computer name, `AFS` as the language group/workgroup string, AFS platform id, and OpenAFS product version. Levels 502, 1013, 1018, 1046, and all other cases return `ERROR_INVALID_LEVEL`.

Every other `Netr*` function follows the same simple path: log a fixed "not supported" message and return `ERROR_NOT_SUPPORTED`. The `Opnum*NotUsedOnWire` functions have empty bodies and exist only so the implementation matches generated interface symbols for unused opnums.

## State and Persistence Behavior

This file has no persistent state of its own and does not modify registry keys, cache objects, server lists, tokens, or on-disk data. Its only externally visible state effects are:

- transient RPC response allocations for supported `NetrWkstaGetInfo` calls
- duplicated wide strings placed in those response structures
- diagnostic log entries through `afsd_logp`

The returned workstation data is synthesized from call parameters and compile-time/version constants. `NetrWkstaGetInfo` does not consult live workstation configuration, authenticated user state, join state, transport state, or OpenAFS cache state.

## Dependencies

- Windows and LAN Manager headers: `windows.h` and `lmcons.h` provide Win32 types and status constants used by the RPC signatures.
- OpenAFS platform headers: `afsconfig.h`, `afs/param.h`, `roken.h`, and `afsd.h` provide build configuration, portability helpers, and AFSD logging declarations.
- Generated wkssvc header: `ms-wkssvc.h` is generated from `ms-wkssvc.idl` by the `NTMakefile` MIDL rule. The source checkout contains the IDL, not the generated header.
- Product version header: `AFS_component_version_number.h` supplies the version fields returned to clients.
- MIDL runtime allocation hooks: `MIDL_user_allocate` / `MIDL_user_free` come from `client_osi/osiutils.c`.

## Integration Points

The Windows AFSD build generates `ms-wkssvc_$(CPU)_s.c` and `ms-wkssvc.h` from `ms-wkssvc.idl`, compiles the generated server stub with `msrpc.h` forced in, and links it with `rpc_wkssvc.obj`. `msrpc.c` registers `wkssvc_v1_0_s_ifspec` in its `_Interfaces` array alongside the `srvsvc` interface, so incoming MSRPC binds can select the Workstation Service interface.

The endpoint is reachable through the SMB/MSRPC named-pipe path for `wkssvc`. `smb_rpc.c` maps an endpoint name of `wkssvc` to `.\\PIPE\\wkssvc`, and `msrpc.c` treats `\\wkssvc` as a well-known service. `cm_vnodeops.c` also excludes `wkssvc` from freelance-root auto-mount creation, preventing this service pipe name from being mistaken for an AFS cell or root directory entry.

The file is the Workstation Service counterpart to `rpc_srvsvc.c`. Both files expose Microsoft-compatible LAN Manager RPC surfaces, use generated IDL types, allocate response structures with `MIDL_user_allocate`, and synthesize enough information for Windows network clients to interact with the OpenAFS redirector/service namespace.

## Risks and Edge Cases

- `NetrWkstaGetInfo` dereferences `ServerName` while stripping leading slashes. The IDL marks the handle as unique, so a malformed or unexpected `NULL` `ServerName` would be unsafe unless the generated stub or caller guarantees a non-null string.
- Allocation failure in `NetrWkstaGetInfo` is indistinguishable from unsupported level because the post-allocation check returns `ERROR_INVALID_LEVEL`. The sibling `NetrServerGetInfo` path in `rpc_srvsvc.c` returns `ERROR_NOT_ENOUGH_MEMORY` for the same condition, so clients may receive misleading errors under memory pressure.
- The string allocations from `wcsdup` are not checked. If either string allocation fails after the structure allocation succeeds, the function can return success with a `NULL` string field in an RPC response that declares those fields as strings.
- The level population relies on intentional fallthrough without explicit `AFS_FALLTHROUGH` annotations. That is consistent with older C style in this file, but modern compiler warning settings could flag it.
- Nearly all wkssvc operations are stubbed. Any Windows client expecting user enumeration, transport enumeration, workstation statistics, join-state discovery, or domain-join semantics will receive `ERROR_NOT_SUPPORTED`.
- The returned `wki100_langroup` value is hard-coded to `AFS` and the logged-on user count is always zero. This is simple and stable, but it is not a live reflection of Windows domain/workgroup or session state.
- No access control or impersonation-specific behavior is implemented in this file. For the supported read-only call this is low risk, but it means the `WKSSVC_IDENTIFY_HANDLE` and `WKSSVC_IMPERSONATE_HANDLE` distinction only exists in the generated interface contract here.

## Test Signals

Useful validation signals are mostly integration-level because this file is dispatched through generated RPC stubs:

- Build the Windows AFSD target and confirm `ms-wkssvc.h`, `ms-wkssvc_$(CPU)_s.c`, `ms-wkssvc_$(CPU)_s.obj`, and `rpc_wkssvc.obj` are generated/linked successfully.
- Exercise `NetrWkstaGetInfo` over the `.\\PIPE\\wkssvc` MSRPC endpoint for levels 100, 101, and 102. Expected success fields include uppercase server name with leading slashes removed, `AFS` as `wki*_langroup`, platform id `800`, OpenAFS product major/minor versions, `NULL` `wki101_lanroot`, and zero `wki102_logged_on_users`.
- Exercise invalid levels such as 502, 1013, 1018, and 1046 and confirm `ERROR_INVALID_LEVEL`.
- Exercise each stubbed operation and confirm the return code is `ERROR_NOT_SUPPORTED` and AFSD logging records the corresponding "not supported" message.
- Run an MSRPC named-pipe smoke test that binds to `wkssvc`, verifying `smb_RPC_SetupEndpointByname` maps the endpoint and `MSRPC_IsWellKnownService` recognizes the pipe name.
- Add fault-injection or allocator tests around `MIDL_user_allocate` and `wcsdup` to document current error behavior, especially the allocation-failure path returning `ERROR_INVALID_LEVEL`.
