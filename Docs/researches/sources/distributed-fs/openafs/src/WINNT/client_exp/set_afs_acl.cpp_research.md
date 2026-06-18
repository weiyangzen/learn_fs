## sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.cpp

Purpose: Implements the ACL editing dialog for one AFS directory.

Important APIs/functions: `OnInitDialog` loads ACL entries with `GetRights`; `OnAdd`, `OnClear`, `OnCopy`, `OnRemove`, and `OnClean` perform user actions; `OnPermChange` rewrites selected rights; `OnOK` persists changes with `SaveACL`; `IsNameInUse` implements `CSetACLInterface` validation for the add-entry dialog.

Control flow/state: ACL data is held as paired `CStringArray` entries for normal and negative ACLs, mirrored into two list boxes. `m_bChanges`, `m_bShowingNormal`, and `m_nCurSel` track dirty state and current selection.

Dependencies/integration: Uses add/clear/copy ACL dialogs, `gui2fs.cpp` ACL operations, `msgs`, MFC controls, and help ID `SET_AFS_ACL_HELP_ID`.

Risks/tests: `m_strCellName` is never populated before `SaveACL`, so saved ACLs may use an empty cell name. Multi-select removal and paired-array indexing are fragile. Test normal and negative ACL edits, duplicate-name rejection, clearing one or both lists, copy-with-clear, clean behavior, save failures, and selection edge cases.
