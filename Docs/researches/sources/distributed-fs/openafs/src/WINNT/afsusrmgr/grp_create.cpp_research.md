## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.cpp

Purpose: implements the new-group dialog, advanced defaults, input parsing, and task parameter creation.

Important APIs/types/functions: `Group_SetDefaultCreateParams`, `Group_ShowCreate`, `Group_Create_DlgProc`, `Group_Create_OnInitDialog`, `Group_Create_OnNames`, `Group_Create_OnID`, `Group_Create_OnAdvanced`, `Group_Create_OnOK`, and `Group_Create_OnEndTask_ObjectGet`.

Control flow: dialog initialization formats title with current cell, creates a negative-ID spinner, selects auto-ID, and starts `taskOBJECT_GET` to fetch cell max group ID. Name changes enable OK and disable manual ID when multiple names are detected. Advanced opens group properties in modal new-group mode. OK builds `GROUP_CREATE_PARAMS`, copies access permissions/members/owned groups, tokenizes names using localized separators plus whitespace, and starts `taskGROUP_CREATE`.

State and persistence behavior: defaults are stored in `gr.CreateGroup` after OK. The temporary `CREATEGROUPDLG` owns advanced member/owner ASID lists and frees them after dialog close.

Dependencies and integration points: depends on group property UI (`grp_prop.cpp`), spinner helpers, `FormatMultiString`, `StartTask`, OpenAFS cell properties, and resource IDs for the dialog.

Risks: name tokenization uses a fixed `cchNAME` buffer after copying the remaining string before truncating, so unusually long input is risky. Multiple-name creation forces auto IDs. Advanced property pointers are nulled before modal editing to avoid sharing stale lists.

Test signals: create one group with auto/manual ID, create multiple groups, use advanced permissions/members, cancel after advanced edits, and verify cell max group ID display updates from `taskOBJECT_GET`.
