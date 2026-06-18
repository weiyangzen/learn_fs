## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.cpp

Purpose: implements group property sheets for existing groups and for advanced new-group settings, including general permissions, owner, members, and owned groups.

Important APIs/types/functions: public APIs are `Group_ShowProperties` overloads and `Group_FreeProperties`. Internal dialogs include `GroupProp_General_DlgProc` and `GroupProp_Member_DlgProc`; key handlers update dialogs, browse for owners/members, apply changes, fetch members/owned groups, and populate FastLists.

Control flow: `Group_ShowProperties` prevents duplicate property windows using `WindowList_Search`, creates a property sheet, and adds General and Member tabs. General init starts `taskOBJECT_LISTEN`; updates aggregate selected group properties, marking mixed values. Apply stores selected access controls and normalized owner name in `GROUPPROPINFO`. Freeing properties after sheet close launches `taskGROUP_CHANGE` for each group with mixed fields preserved from current properties. Member tab copies original ASID lists as cancel backups, fetches member/owned lists asynchronously when needed, uses browse dialogs to add objects, removes selected objects, and on apply starts `taskGROUP_MEMBERS_SET` and/or `taskGROUP_OWNED_SET`.

State and persistence behavior: `GROUPPROPINFO` carries selected group list, apply flags, mixed-value flags, owner/creator text, and cached member/owned lists. Dialog window data stores backup ASID lists so cancel can restore prior values. WindowList tracks modeless sheets by group ID or multi-group key.

Dependencies and integration points: depends on `winlist`, `browse`, `usr_col` display-name helpers, `StartTask`, PropSheet helpers, AfsAppLib context help, OpenAFS object properties, and resource IDs. Creation dialogs reuse this code for advanced defaults by passing `pGroupList == NULL`.

Risks: apply-on-destroy in `Group_FreeProperties` means property changes are launched when the sheet closes, so ownership and flags must be exact. Multi-group membership semantics use `lParam` to mean present in all groups vs mixed, and mistakes can add/remove membership too broadly. Async member fetch completion ignores later user edits if list pointers are already populated.

Test signals: single-group properties, multi-group mixed permissions, owner browse, duplicate-window prevention, member add/remove, owned-group add/remove, apply/cancel behavior, object-change notifications, and new-group advanced settings with no backing group.
