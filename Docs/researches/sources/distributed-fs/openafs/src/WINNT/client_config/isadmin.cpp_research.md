# sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.cpp

## Purpose
`isadmin.cpp` detects whether the process is running on Windows NT and whether the current user has OpenAFS client administration rights.

## Important APIs, Types, and Functions
The exports are `IsWindowsNT` and `IsAdmin`. `IsAdmin` checks membership in the local `AFS Client Admins` group and also treats LocalSystem as administrative.

## Control Flow
`IsWindowsNT` caches `GetVersionEx` platform detection. `IsAdmin` caches its result after first evaluation, builds `COMPUTERNAME\AFS Client Admins`, resolves the group SID, opens the process token, uses `CheckTokenMembership`, falls back to enumerating `TokenGroups`, and finally compares the token user SID against LocalSystem.

## State and Persistence Behavior
Only static process-local cache state is maintained. If the AFS Client Admins group cannot be found, the function intentionally grants admin privileges to preserve compatibility on systems without the group.

## Dependencies and Integration Points
`main.cpp` uses these functions to set `g.fIsWinNT` and `g.fIsAdmin`. The General tab uses `g.fIsAdmin` to enable/disable service start/stop and configuration controls. The code depends on Win32 security APIs and `TaLocale`-included platform headers.

## Risks and Edge Cases
Returning admin when the local group is absent is permissive. Some early returns before `fTested = TRUE` mean repeated calls can redo work after unexpected computer-name lookup failures. Token handles are not explicitly closed, which can leak handles. Allocation and lookup failures generally bias toward allowing operation after the group has been detected once.

## Test Signals
Tests should cover group missing, user in group, user not in group, LocalSystem token, failed `GetComputerName`, denied token queries, and repeated calls verifying cache behavior and handle cleanup.
