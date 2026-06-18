## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.cpp

Purpose: implements group delete confirmation and task dispatch.

Important APIs/types/functions: `Group_ShowDelete`, `Group_Delete_DlgProc`, `Group_Delete_OnInitDialog`, `Group_Delete_OnDestroy`, and `Group_Delete_OnOK`.

Control flow: selected group `ASIDLIST` is passed as dialog user data. Initialization formats a single-group title from the object name or a multi-group title from `CreateNameList`. OK copies the ASID list and starts `taskGROUP_DELETE`; destroy frees the original list.

State and persistence behavior: transient dialog state only. Actual deletion and subsequent cache/list updates occur in background task/action layers.

Dependencies and integration points: called by `Command_OnDelete` for homogeneous group selections. Uses OpenAFS object-name cache, localized strings, and `StartTask`.

Risks: if `asc_ObjectNameGet_Fast` fails for a single group, title formatting may use uninitialized/empty text. Ownership is split between the original list freed on destroy and the copied list owned by the task.

Test signals: delete one group, multiple groups, groups with missing cache names, OK/cancel, and verify no list double-free after task dispatch.
