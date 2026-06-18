# subset-b-007727 Research

Grouped source research for the OpenAFS Windows redirector network-provider DLL, its enumeration smoke test, and user-mode control tools for authentication groups, crash injection, trace handling, and object status inspection. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.c -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.c

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.c` implements the OpenAFS Windows Network Provider DLL entry points used by the Multiple Provider Router/WNet layer. It translates Windows network-provider operations into OpenAFS redirector device IOCTLs, manages DOS device mappings for drive-letter connections, formats and enumerates `NETRESOURCE` records, resolves local paths to UNC names, and provides debug logging controlled by the provider registry key. The complete 4052-line file was read for this research.

## Important APIs, Types, and Functions

The exported provider surface includes `NPGetCaps`, `NPAddConnection`, `NPAddConnection3`, `NPCancelConnection`, `NPGetConnection`, `NPGetConnection3`, `NPGetConnectionPerformance`, `NPOpenEnum`, `NPEnumResource`, `NPCloseEnum`, `NPGetResourceParent`, `NPGetResourceInformation`, `NPGetUniversalName`, `NPFormatNetworkName`, `NPLogonNotify`, `NPPasswordChangeNotify`, `NPGetUser`, `NPGetReconnectFlags`, and `I_SystemFocusDialog`. Internal helpers include `ReadProviderNameString`, `ReadServerNameString`, `NPIsFSDisabled`, `DriveSubstitution`, `OpenRedirector`, `SeparateRemainingPath`, `Debug`, `cm_Utf16ToUtf8Alloc`, `AppendDebugStringToLogFile`, and `AFSDbgPrint`.

The central protocol type is `AFSNetworkProviderConnectionCB` from `AFSProvider.h`, passed to `IOCTL_AFS_ADD_CONNECTION`, `IOCTL_AFS_CANCEL_CONNECTION`, `IOCTL_AFS_GET_CONNECTION`, `IOCTL_AFS_LIST_CONNECTIONS`, and `IOCTL_AFS_GET_CONNECTION_INFORMATION`. `AFSEnumerationCB` is this DLL's heap-owned enumeration cursor containing the current index, requested scope/type, and optional remote-name seed. A local `UNICODE_STRING` definition is used to build redirector target paths for `DefineDosDevice`.

## Control Flow

Initialization is lazy and registry driven. `ReadProviderNameString` reads `HKLM\SYSTEM\CurrentControlSet\Services\AFSRedirector\NetworkProvider\Name`; `ReadServerNameString` reads `HKLM\SYSTEM\CurrentControlSet\Services\TransarcAFSDaemon\Parameters\NetbiosName`; `NPIsFSDisabled` treats a missing or disabled `AFSRedirector` service as unavailable.

Connection creation starts in `NPAddConnection`, which forwards to `NPAddConnection3`. `NPAddConnection3` validates a disk or any-resource UNC remote name, copies it into an `AFSNetworkProviderConnectionCB`, opens `AFS_SYMLINK_W` with `CreateFile`, sends `IOCTL_AFS_ADD_CONNECTION`, then, for drive-letter mappings, creates a DOS device target of the form `\Device\AFSRedirector\;<drive>:\\...` with `DefineDosDeviceW`. On collision it cancels the provider connection and returns assignment errors.

Connection cancellation accepts either a UNC name or a local drive. For a drive, `NPCancelConnection` first calls `NPGetConnectionCommon` to obtain the remote name, sends `IOCTL_AFS_CANCEL_CONNECTION`, and removes the DOS device mapping when the redirector reports success. Remote-name cancellation can use the local letter returned by `AFSCancelConnectionResultCB`.

Connection lookup and universal-name resolution have two paths. The primary path asks the redirector with `IOCTL_AFS_GET_CONNECTION`; if no mapping is found, `NPGetConnection`, `NPGetConnection3`, and `NPGetUniversalName` retry through `DriveSubstitution`, which recursively follows `QueryDosDevice` substitutions and recognizes both `\??\UNC\...` and `\Device\AFSRedirector...` targets. `NPGetUniversalNameCommon` supports both `UNIVERSAL_NAME_INFO_LEVEL` and `REMOTE_NAME_INFO_LEVEL`, appending the local path suffix after the drive letter to the connection root.

Enumeration starts with `NPOpenEnum`, which allocates `AFSEnumerationCB` for connected, context, or global network scopes and optionally stores the parent remote name for nested global enumeration. `NPEnumResource` asks the redirector for a packed list with `IOCTL_AFS_LIST_CONNECTIONS`, then builds a caller-provided array of `NETRESOURCE` entries at the front of the buffer while placing strings from the end backward. `NPCloseEnum` frees the optional remote name and cursor.

Resource metadata calls use `IOCTL_AFS_GET_CONNECTION_INFORMATION`. `NPGetResourceInformation` fills `NETRESOURCE`, comment, provider name, and optional remaining path. `NPGetResourceParent` truncates the input remote name at the final backslash, delegates to `NPGetResourceInformation`, or returns an empty resource when the root has no parent. `NPFormatNetworkName` returns the final path component.

Unsupported logon, password-change, user, reconnect, and focus-dialog entry points return `WN_NOT_SUPPORTED`; the file notes AuthGroup logon processing is implemented elsewhere in `src/WINNT/afsd/afslogon.c`.

## State and Persistence Behavior

Persistent state is external. Provider name, server name, disabled state, and debug flags are read from the registry and cached in process-wide static variables with no explicit synchronization. Drive mappings are persisted as DOS device symbolic links through `DefineDosDevice`; actual connection state is maintained by the redirector kernel component behind the IOCTLs. Enumeration state is per-handle heap memory. Debug output is controlled by the registry `Debug` DWORD and can write to the debugger and/or append UTF-8 log lines to `C:\TEMP\AFSRDFSProvider.log`.

## Dependencies and Integration Points

The file integrates Windows `npapi.h`, `winnetwk.h`, registry APIs, `QueryDosDevice`, `DefineDosDevice`, `CreateFile`, `DeviceIoControl`, heap/local allocation, and `strsafe.h`. OpenAFS integration comes from `AFSUserDefines.h`, `AFSUserIoctl.h`, `AFSUserStructs.h`, `AFSProvider.h`, and `AFS_Npdll.h`. Kernel-side receivers are visible in `kernel/lib/AFSDevControl.cpp` and `kernel/fs/AFSCommSupport.cpp` for connection and debug/auth/object IOCTL routing.

## Risks and Edge Cases

`ReadServerNameString` initializes `dwLen` with `sizeof(wszProviderName)` while writing into the smaller `wszServerName` buffer, so a long registry `NetbiosName` could overflow unless the registry value is constrained elsewhere. `NPGetResourceParent` mutates `lpNetResource->lpRemoteName` in place while searching for a parent, which is surprising for caller-owned input and can corrupt reusable `NETRESOURCE` strings. `NPGetUniversalNameCommon` reads `*lpBufferSize` into locals before checking `lpBufferSize` for null, and computes `dwLocalPathLength - 2` before validating path length, so malformed inputs can underflow or fault. `Add3FlagsToString` checks `CONNECT_INTERACTIVE` twice and labels the second occurrence `DEFERRED`, likely intending `CONNECT_DEFERRED`. `AppendDebugStringToLogFile` leaks the allocated UTF-8 buffer if `CreateFileW` fails. Several fixed 0x1000 buffers assume redirector responses fit; callers receive `WN_MORE_DATA` in many places, but not every copy checks all `StringCbCopy` results.

## Test Signals

Useful tests include WNet add/cancel/get cycles for drive-letter and deviceless UNC connections, retry coverage for substituted drives and `\??\UNC` targets, enumeration over connected/context/global scopes with small buffers forcing `WN_MORE_DATA`, universal-name tests for both info levels and too-small buffers, provider disabled and missing-redirector scenarios, registry override tests for provider/server names, and negative tests for long UNC paths and malformed local names. The supplied `npdll/tests/enumresources.c` is a smoke test for enumeration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h` is the small public-local header for the OpenAFS network-provider DLL. The complete 35-line file was read; it contains license text and the declaration needed by other translation units to force or share provider-name initialization.

## Important APIs, Types, and Functions

The only declaration is `void ReadProviderNameString(void);`. There are no local types, macros, or constants beyond the license/comment block.

## Control Flow

The header has no executable flow. Consumers include it to call the provider-name registry loader implemented in `AFS_Npdll.c`.

## State and Persistence Behavior

No state is defined in this header. The declared function affects `AFS_Npdll.c` static cached state by reading the provider name from the Windows registry.

## Dependencies and Integration Points

The integration point is `AFS_Npdll.c`, where `ReadProviderNameString` populates `wszProviderName` and `cbProviderNameLength` for `NETRESOURCE.lpProvider` values returned by enumeration and resource information calls.

## Risks and Edge Cases

The header intentionally exposes only one function, so the main risk is declaration drift if the implementation signature changes. Because it has no include guard, duplicate inclusion is harmless for the single function prototype but would become risky if definitions were later added.

## Test Signals

Compile coverage of the network-provider DLL is the primary signal. Runtime provider-name tests belong to `AFS_Npdll.c` because that file owns the registry read and cached data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c` is a standalone WNet enumeration smoke test adapted from MSDN sample code. It exercises all installed Windows network providers, including OpenAFS when registered, by calling `WNetOpenEnum`, `WNetEnumResource`, and `WNetCloseEnum` for several scopes. The complete 322-line file was read.

## Important APIs, Types, and Functions

`main` enumerates `RESOURCE_CONNECTED`, `RESOURCE_CONTEXT`, `RESOURCE_GLOBALNET`, and `RESOURCE_REMEMBERED` for `RESOURCETYPE_DISK`. `EnumerateFunc` performs recursive enumeration with a 16 KiB `GlobalAlloc` buffer and `cEntries = -1`. `DisplayStruct` decodes `NETRESOURCE` scope, type, display type, usage flags, local name, remote name, comment, and provider. A commented `NetErrorHandler` shows extended-error handling but is not compiled.

## Control Flow

The program prints a heading for each scope, calls `EnumerateFunc`, and exits with `1` on the first failed scope. `EnumerateFunc` opens an enumeration handle, repeatedly zeroes the buffer and calls `WNetEnumResource` until `ERROR_NO_MORE_ITEMS`, displays each returned entry, and recursively descends into container entries only for `RESOURCE_GLOBALNET`.

## State and Persistence Behavior

The tool keeps only process-local heap state and does not persist data. Its observable behavior depends on system network-provider registration, current user connections, remembered mappings, and provider-specific enumeration implementations.

## Dependencies and Integration Points

The file links against `mpr.lib` and includes `windows.h`, `stdio.h`, and `winnetwk.h`. For OpenAFS, it indirectly drives `NPOpenEnum`, `NPEnumResource`, and `NPCloseEnum` in `AFS_Npdll.c` through the Windows Multiple Provider Router.

## Risks and Edge Cases

The code assumes a 16 KiB buffer remains adequate; providers can return `ERROR_MORE_DATA`, but this sample prints an error and breaks instead of resizing. Recursive global enumeration can be expensive or noisy on systems with many network providers. It uses `%S` for nullable string fields without null checks; OpenAFS sometimes returns null local/comment fields, so output behavior depends on the C runtime's handling of null wide-string pointers.

## Test Signals

Successful output over connected, context, and global scopes is a useful manual signal that OpenAFS provider enumeration works and returns well-formed `NETRESOURCE` strings. Useful variations include running with no AFS redirector, with one drive-letter connection, with a deviceless UNC connection, and with a deliberately small modified buffer to verify provider `WN_MORE_DATA` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/authgroup/AuthGroup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/authgroup/AuthGroup.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/authgroup/AuthGroup.cpp` implements the `AFSAuthGroup` command-line tool for querying, creating, selecting, and resetting OpenAFS authentication groups. AuthGroups are the Windows redirector's PAG-like identity containers, represented as GUIDs and controlled through redirector IOCTLs. The complete 518-line file was read.

## Important APIs, Types, and Functions

`Usage` prints the accepted switches. `main` parses `/q`, `/l`, `/c`, `/s`, `/r`, `/n`, `/sid`, `/ag`, `/session`, `/thread`, and `/active`. It opens `AFS_SYMLINK` with read/write sharing and uses `DeviceIoControl` with `IOCTL_AFS_AUTHGROUP_SID_QUERY`, `IOCTL_AFS_AUTHGROUP_QUERY`, `IOCTL_AFS_AUTHGROUP_CREATE_AND_SET`, `IOCTL_AFS_AUTHGROUP_SET`, `IOCTL_AFS_AUTHGROUP_RESET`, and `IOCTL_AFS_AUTHGROUP_SID_CREATE`. It uses `AFSAuthGroupRequestCB`, `AFS_PAG_FLAGS_THREAD_AUTH_GROUP`, `AFS_PAG_FLAGS_SET_AS_ACTIVE`, `UuidToString`, `UuidFromString`, and `RpcStringFree`.

## Control Flow

Argument parsing sets one or more booleans, converts optional SID text from ANSI to UTF-16, copies the optional GUID string, and parses optional session IDs with `StrToIntExA`. The first matching operation branch runs after the control device opens: query active group, list process groups, create-and-set, set existing group, reset, create group for SID/session, or report invalid parameters. Create branches allocate an `AFSAuthGroupRequestCB` sized to include the SID string, set optional session and flags, then send the corresponding IOCTL.

## State and Persistence Behavior

The tool owns no persistent state. It mutates redirector-maintained AuthGroup membership and active process/thread AuthGroup state. The underlying model, documented in `AFSUserStructs.h`, lets processes maintain one or more AuthGroup GUIDs, switch active process/thread groups only among groups already associated with the process, reset to the SID AuthGroup, and create SID or logon-session groups with privilege checks in the driver.

## Dependencies and Integration Points

The file depends on Windows base APIs, `shlwapi.h` for integer parsing, `rpc.h` for GUID conversion, and OpenAFS `AFSUserDefines.h`, `AFSUserIoctl.h`, and `AFSUserStructs.h`. Kernel-side receivers are in `kernel/fs/AFSAuthGroupSupport.cpp` and dispatch paths in `kernel/fs/AFSCommSupport.cpp`; logon integration also uses AuthGroup IOCTLs in `src/WINNT/afsd/logon_ad.cpp`.

## Risks and Edge Cases

Several options increment `dwIndex` without checking that a value follows, so truncated command lines can read past `argv`. `/thread` and `/active` also increment `dwIndex` even though they are flag options, which can skip the following argument. `strcpy(chGUID, argv[dwIndex])` has no length bound for the 256-byte local buffer. `MultiByteToWideChar` sizes the output using the source byte length and a 256-wide-character destination, so very long SID strings can fail but are not prevalidated. The branch order allows multiple action switches but executes only the first true branch, which can surprise callers.

## Test Signals

Manual tests should cover querying with no custom group, creating a SID group, create-and-set with process and thread flags, setting an existing GUID, resetting process and thread state, invalid GUID strings, missing required option values, and non-admin or wrong-SID attempts for privileged SID/session operations. Driver-level tests should confirm that process inheritance and active-thread precedence match the comments in `AFSUserStructs.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/authgroup/AuthGroup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp` is a diagnostic utility that asks the OpenAFS redirector to intentionally crash through `IOCTL_AFS_FORCE_CRASH`. The complete 84-line file was read.

## Important APIs, Types, and Functions

The only executable function is `main`. It opens `AFS_SYMLINK` with `CreateFile`, sends `DeviceIoControl(IOCTL_AFS_FORCE_CRASH)`, closes the handle, and exits. It includes `AFSUserDefines.h` and `AFSUserIoctl.h` for the control device path and IOCTL code.

## Control Flow

There is no argument parsing. Failure to open the control device prints `GetLastError()` and returns `0`; otherwise the crash IOCTL is issued once and the device handle is closed.

## State and Persistence Behavior

The tool has no local persistence. Its intended effect is a system-level driver crash or bugcheck path controlled by the redirector implementation, so any persistence is crash dump and system log output produced outside this program.

## Dependencies and Integration Points

The integration point is the redirector control device behind `AFS_SYMLINK`. Dispatch for the crash IOCTL is visible in `kernel/fs/AFSCommSupport.cpp`.

## Risks and Edge Cases

This utility is intentionally destructive and should not be installed or run casually. It ignores the `DeviceIoControl` return value, so a failed crash request is silent. Returning `0` even on open failure makes automation treat failure as success unless it parses stdout.

## Test Signals

Validation should be limited to controlled debug or test systems. Expected signals are successful control-device open, crash dump generation or driver verifier output, and correct access control preventing unprivileged accidental use if the driver enforces it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/gettrace/gettrace.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/gettrace/gettrace.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/gettrace/gettrace.cpp` implements `GetTrace`, a command-line utility that retrieves the OpenAFS redirector trace buffer and writes it to stdout. The complete 135-line file was read.

## Important APIs, Types, and Functions

`main` parses an optional buffer size in kilobytes, opens `AFS_SYMLINK`, allocates a byte buffer, and sends `IOCTL_AFS_GET_TRACE_BUFFER`. It uses `StrToIntExA` for decimal/hex parsing and `AFSUserIoctl.h` for the IOCTL.

## Control Flow

With no argument, the nominal default is `2001` before scaling. With `?`, it prints usage and exits. Otherwise it parses `argv[1]`, rejects zero, opens the control device, multiplies the requested value by `1024 + 1`, allocates, retrieves the trace buffer, null terminates at `bytesReturned`, prints the result, frees memory, and closes the handle.

## State and Persistence Behavior

The program only reads driver-maintained trace state. It does not clear the trace buffer or write files. Output is transient unless redirected by the caller.

## Dependencies and Integration Points

The control IOCTL is handled by the redirector debug/trace path in `kernel/fs/AFSCommSupport.cpp`, with trace configuration state managed near `kernel/fs/AFSLogSupport.cpp`. It pairs operationally with `settrace.cpp`, which configures trace level, subsystem, buffer length, and debug flags.

## Risks and Edge Cases

`dwBufferSize *= 1024 + 1` multiplies by 1025, not by 1024 and then plus terminator space; this makes buffer sizing slightly surprising. The code writes `pBuffer[bytesReturned] = '\0'` without proving `bytesReturned < dwBufferSize`, relying on the IOCTL not to fill the entire output buffer. Open failures return `0`, which weakens automation. The trace buffer is treated as a C string, so embedded nulls truncate output.

## Test Signals

Tests should configure a small trace buffer with `SetTrace`, generate known redirector activity, run `GetTrace`, and confirm expected text appears. Boundary tests should request tiny, default, and large sizes and verify the driver's `bytesReturned` never causes the terminator write to exceed the allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/gettrace/gettrace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp` implements `AFSObjectStatus`, a diagnostic tool for retrieving redirector object metadata by FID or path and for invalidating a cached object by FID. The complete 523-line file was read.

## Important APIs, Types, and Functions

`main` parses `/f`, `/n`, and `/i`. `ParseFID` splits a `Cell.Volume.VNode.Unique` string into an `AFSFileID` using hex parsing. `GetAFSFileType` maps `AFS_FILE_TYPE_FILE`, `AFS_FILE_TYPE_DIRECTORY`, `AFS_FILE_TYPE_SYMLINK`, `AFS_FILE_TYPE_MOUNTPOINT`, and `AFS_FILE_TYPE_DFSLINK` to display strings. The tool uses `AFSGetStatusInfoCB`, `AFSStatusInfoCB`, `AFSInvalidateCacheCB`, `IOCTL_AFS_GET_OBJECT_INFORMATION`, and `IOCTL_AFS_INVALIDATE_CACHE`.

## Control Flow

The program requires either a FID or a filename. If `/i` is present, it requires `/f`, builds an `AFSInvalidateCacheCB` with reason `AFS_INVALIDATE_FLUSHED`, and sends `IOCTL_AFS_INVALIDATE_CACHE`. Otherwise it builds an `AFSGetStatusInfoCB` using either the parsed FID or a wide filename. For UNC-like names it skips the first leading backslash before copying. It sends `IOCTL_AFS_GET_OBJECT_INFORMATION` with a 1024-byte in/out buffer and prints the returned FID, target FID, expiration, data version, file type, object flags, timestamps, attributes, EOF, allocation size, EA size, and link count.

## State and Persistence Behavior

Status lookup is read-only from the tool perspective. Invalidation mutates redirector cache state for the specified FID, potentially forcing subsequent metadata or data refresh from AFS. No local files or registry values are written.

## Dependencies and Integration Points

The utility opens `AFS_SYMLINK` and depends on OpenAFS user structures from `AFSUserStructs.h`. Kernel-side object status retrieval is visible in `kernel/lib/AFSGeneric.cpp` through `AFSGetObjectStatus`, with IOCTL validation in `kernel/lib/AFSDevControl.cpp` and dispatch from `kernel/fs/AFSCommSupport.cpp`.

## Risks and Edge Cases

`ParseFID` mutates the input `argv` string by replacing dots with nulls. It appends user-provided segments into a 50-byte buffer with `strcat_s`; overly long segments fail safely but are only detected during parsing. Path mode uses a fixed 256-wide-character filename buffer and a fixed 1024-byte IOCTL buffer, so long names or larger future `AFSStatusInfoCB` payloads are not handled dynamically. The `/n` path path can be omitted without validation, leaving `wchFileName` uninitialized if no FID is used. The unused `dwIOControl` local suggests an older refactor left dead state.

## Test Signals

Useful tests include FID parsing with valid and malformed four-part values, path lookup for local AFS and UNC-style names, object status of file, directory, symlink, mount point, and DFS link objects, invalidation by FID followed by a lookup that confirms cache refresh behavior, and access/error tests against nonexistent FIDs or disconnected redirector state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp` implements `SetTrace`, a command-line utility for configuring OpenAFS redirector debug tracing. The complete 202-line file was read.

## Important APIs, Types, and Functions

`usage` prints accepted switches. `main` parses `/l` for trace level, `/s` for subsystem, `/b` for trace buffer size in KB, and `/d` or `/f` for debug flags. It fills `AFSTraceConfigCB` and sends `IOCTL_AFS_CONFIGURE_DEBUG_TRACE`.

## Control Flow

The tool requires at least one option/value pair, opens `AFS_SYMLINK`, scans arguments, parses numeric values with `StrToIntExA`, and aborts on the first parse or option error. On success it copies parsed values into `AFSTraceConfigCB`, sends the configure IOCTL, prints success or `GetLastError()`, closes the device handle, and returns a small status code.

## State and Persistence Behavior

The program mutates driver trace configuration: subsystem, level, buffer length, and debug flags. Whether that state persists across driver restart is controlled by the redirector, not this tool.

## Dependencies and Integration Points

The file depends on `AFSUserDefines.h`, `AFSUserIoctl.h`, and `AFSUserStructs.h`. The kernel-side trace configuration handler is in `kernel/fs/AFSCommSupport.cpp`, with implementation in `kernel/fs/AFSLogSupport.cpp`. It pairs with `gettrace.cpp` for retrieval.

## Risks and Edge Cases

Each option increments `dwIndex` before reading the option value without checking bounds, so truncated command lines can read past `argv`. Unspecified fields remain at `-1` and are sent as unsigned `ULONG` values in `AFSTraceConfigCB`; this may be intentional as an unchanged sentinel, but it depends on driver semantics. The usage string advertises `/f`, while parsing also accepts `/d`. Open failure returns code `2`; parse failure returns code `4`; IOCTL failure returns code `3`, which is useful for scripts.

## Test Signals

Tests should set individual fields and all fields together, verify invalid and missing option values fail without changing driver state, confirm `GetTrace` observes the configured buffer behavior, and check that `-1` sentinel values are either ignored or deliberately applied by the driver as documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp -->
