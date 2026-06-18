## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.h

Purpose: exposes the group delete dialog entry point.

Important APIs/types/functions: declares `Group_ShowDelete(LPASIDLIST pGroupList)`.

Control flow: command handling passes ownership of selected group ASIDs to the delete dialog, which confirms and starts the delete task.

State and persistence behavior: no persistent state; passed ASID list is transient and freed by the dialog.

Dependencies and integration points: integrates with `command.cpp` selection dispatch and `taskGROUP_DELETE`.

Risks: callers must pass only groups; mixed-selection validation is performed before this API.

Test signals: ensure direct callers do not pass users or machines and that cancellation frees the list.
