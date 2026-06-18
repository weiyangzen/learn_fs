## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.cpp

Purpose: implements machine-account delete confirmation and task dispatch.

Important APIs/types/functions: `Machine_ShowDelete`, `Machine_Delete_DlgProc`, `Machine_Delete_OnInitDialog`, `Machine_Delete_OnDestroy`, and `Machine_Delete_OnOK`.

Control flow: selected machine ASIDs are stored in dialog user data. Initialization builds a single or multi-delete title. OK creates `USER_DELETE_PARAMS`, sets `fDeleteKAS = FALSE` and `fDeletePTS = TRUE`, copies selected machines into `pUserList`, and starts `taskUSER_DELETE`. Destroy frees the original ASID list.

State and persistence behavior: transient dialog state only; actual persisted data changes occur in the OpenAFS protection database via background task.

Dependencies and integration points: called by `Command_OnDelete` when selected user objects satisfy `fIsMachineAccount`. Uses user delete infrastructure rather than a separate machine task.

Risks: machine deletion deliberately does not touch KAS, so any machine credentials outside PTS are left intact. Like group delete, title formatting relies on object-name cache.

Test signals: delete one and multiple machines, ensure normal users do not reach this path, verify KAS deletion flag remains false, and validate cancel frees selected ASID list.
