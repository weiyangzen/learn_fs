## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.h

Purpose: declares the group rename dialog entry point.

Important APIs/types/functions: `Group_ShowRename(HWND hParent, ASID idGroup)`.

Control flow: command handling calls this for single selected group rename.

State and persistence behavior: no persistent state in the API; the implementation listens for object updates and starts mutation tasks.

Dependencies and integration points: uses OpenAFS `ASID` identity and a Win32 parent window.

Risks: the API does not encode object type, so callers must pass a group ASID.

Test signals: compile direct callers and assert only `TYPE_GROUP` selections reach this function.
