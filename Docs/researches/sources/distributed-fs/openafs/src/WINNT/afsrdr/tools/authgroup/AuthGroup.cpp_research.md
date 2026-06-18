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
