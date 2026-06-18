# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSProcessSupport.cpp

## Purpose
`AFSProcessSupport.cpp` tracks process creation/destruction and assigns OpenAFS authentication-group GUIDs to processes and threads. It bridges Windows process/session/SID information to the redirector's PAG/auth-group model and records whether the current process is the user-mode service.

## Important APIs, Control Flow, And State
`AFSProcessNotify` and `AFSProcessNotifyEx` adapt legacy and Vista+ process callbacks into `AFSProcessCreate` and `AFSProcessDestroy`. Creation locks `ProcessTree`, allocates an `AFSProcessCB` through `AFSInitializeProcessCB`, records creator process/thread IDs, then validates/assigns an auth group. Destruction removes the B-tree entry, frees per-process auth-group and thread lists, deletes the process resource, and frees the process CB.

`AFSValidateProcessEntry` is the core. It locates or creates the process entry, locks the parent and process CBs, records 64-bit state on 64-bit builds, obtains the caller SID and session ID, reuses an existing non-NoPAG auth group when possible, otherwise inherits from the creating parent thread or parent process, and finally hashes `(sessionId, SID hash)` into `AuthGroupTree`. If no SID entry exists it allocates an `AFSSIDEntryCB` and creates a GUID with `ExUuidCreate`. It stores the selected GUID in `ActiveAuthGroup`, marks local-system SIDs, and calls `AFSProcessSetProcessDacl` once per non-impersonating process to install the custom DACL ACE.

Support functions query 64-bit process state, initialize thread CBs, test whether a SID is the current token user or a group member, and set/query the static `AFSServicePid` through `AFSRegisterService`, `AFSDeregisterService`, and `AFSIsService`.

## Dependencies And Integration Points
This file depends on the process and auth-group B-trees in the control device extension, B-tree helpers, `AFSGetCallerSID`, `AFSGetSessionId`, `AFSIsLocalSystemSID`, `AFSIsNoPAGAuthGroup`, `AFSProcessSetProcessDacl`, resource wrappers, token APIs (`SeCaptureSubjectContext`, `SeQueryInformationToken`), and pool wrappers. The auth lookup callback `AFSRetrieveAuthGroup` in other files consumes these structures.

## Risks And Test Signals
Lock ordering across `ProcessTree`, parent process lock, process lock, and `AuthGroupTree` is delicate. The code calls `AFSProcessCreate` while holding or upgrading tree locks in some paths, so recursion/deadlock behavior needs review. Auth-group inheritance depends on creation thread IDs being captured accurately. SID/session hash collisions are possible in the combined key if SID hash collides. Tests should cover legacy and Ex callbacks, process destruction cleanup, impersonation vs non-impersonation paths, parent-thread and parent-process inheritance, local-system marking, DACL install failures, concurrent validation of the same process, 32-bit process detection on 64-bit OS, and service PID registration.
