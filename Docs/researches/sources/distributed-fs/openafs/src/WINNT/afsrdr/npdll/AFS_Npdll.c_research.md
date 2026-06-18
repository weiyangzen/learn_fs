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
