# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.h

Purpose: exposes the user deletion confirmation entry point.

Important APIs/types: declares `User_ShowDelete(LPASIDLIST pUserList)`, which assumes ownership of the selected ASID list through the dialog lifecycle and delegates real deletion to `taskUSER_DELETE`.

State and dependencies: no persistent state. Depends on ASID-list types and Windows UI infrastructure through the application headers.

Risks and test signals: callers must pass a valid, heap-managed ASID list and should not reuse it after invoking the dialog. Tests should verify selected-list ownership and task payload creation.
