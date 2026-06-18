## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.cpp

Purpose: implements the group rename and optional owner-change dialog.

Important APIs/types/functions: `Group_ShowRename`, `Group_Rename_DlgProc`, `Group_Rename_OnInitDialog`, `Group_Rename_OnDestroy`, `Group_Rename_OnNewName`, `Group_Rename_OnChangeOwner`, `Group_Rename_OnOK`, and `Group_Rename_UpdateDialog`.

Control flow: initialization registers object-listen notifications for the target group, fills current group/owner fields, and disables OK until a new name is entered. Owner-change opens a browse dialog restricted to one user or group. OK allocates a group-change/rename task parameter, reads new name and possibly owner, and starts background mutation. Destroy unregisters object listening.

State and persistence behavior: target `ASID` is stored in dialog user data. No persistent settings are changed, but background tasks mutate the OpenAFS protection database and refresh cached object state.

Dependencies and integration points: invoked only for a single selected group by `command.cpp`. Uses `browse`, object listeners, OpenAFS cached properties, and localized help/resources.

Risks: rename is disabled in context menu for multi-select, but direct callers must enforce single group. Owner text may include appended UID and must be stripped before use. Object notifications during the dialog can change displayed current values.

Test signals: rename a group, change owner to user/group, cancel browse, handle group deletion/change while dialog is open, and verify owner UID suffix is not submitted as part of the owner name.
