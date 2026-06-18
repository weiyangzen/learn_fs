# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.h

Purpose: exposes the user password/key-change dialog entry point.

Important APIs/types: declares `User_ShowChangePassword(HWND hParent, ASID idUser)`, which opens a modal UI for changing a selected user's password/server key. The implementation uses `USER_CPW_PARAMS` from `task.h` for the actual admin operation.

State and dependencies: no local state or persistence. It depends on Windows `HWND` and AFS `ASID` types through the application include graph.

Risks and test signals: API misuse risk is limited to passing a non-user ASID or invalid parent window. Tests should confirm callers only enable it for single selected users and that the dialog delegates to `taskUSER_CPW`.
