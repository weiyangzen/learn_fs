# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.cpp

Purpose: Implements confirmation dialog for deleting a service.

Important APIs/functions: `Services_Delete` opens a modal delete confirmation and starts `taskSVC_DELETE` on OK. `Services_Delete_DlgProc` stores the target identity in a static pointer and handles OK/cancel. `Services_Delete_OnInitDialog` formats the target server/service into explanatory text.

Control flow: The dialog is purely synchronous. The selected service identity is passed directly to the delete task after confirmation.

State and persistence: No local persisted state; deletion is remote service state handled by the task layer.

Dependencies/integration: Depends on `svrmgr.h`, `svc_delete.h`, resource strings, and task dispatch. Higher-level menus disable deletion for BOS.

Risks: Uses a static dialog pointer, safe only under modal single-instance assumptions. No local validation prevents deleting BOS or invalid identities; callers must gate.

Test signals: Confirm/cancel paths, delete for normal service, attempted BOS delete via direct call, and error handling in task completion elsewhere.
