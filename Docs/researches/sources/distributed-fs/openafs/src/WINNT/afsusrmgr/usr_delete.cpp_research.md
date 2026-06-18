# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.cpp

Purpose: implements the user deletion confirmation dialog.

Important APIs and control flow: `User_ShowDelete` opens `IDD_USER_DELETE` with an ASID list. Initialization formats either a single display name or a multi-user name list and defaults both KAS and PTS deletion checkboxes to checked. `User_Delete_OnCheck` prevents OK when neither backing database is selected. `User_Delete_OnOK` copies the ASID list into `USER_DELETE_PARAMS`, records KAS/PTS delete flags, and starts `taskUSER_DELETE`.

State and dependencies: the selected user list is stored in `DWLP_USER` and freed on dialog destroy. Actual deletion and aggregate error reporting live in `task.cpp`. Dependencies include user display-name formatting, ASID-list helpers, resource strings, and task dispatch.

Risks and test signals: ownership of the passed ASID list is important because this dialog frees it. Tests should cover single vs multi-title formatting, checkbox gating, copying lists before task start, and deleting only KAS or only PTS records.
