# sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.cpp

Purpose: implements the modal dialog for adding a normal or negative AFS ACL entry.

Important APIs/functions: constructor initializes localized dialog template and clears the ACL interface pointer; `OnInitDialog` sets normal-entry default and disables OK; `MakePermString` builds rights letters; `OnOK` validates duplicate names through `CSetACLInterface`; radio/name/help handlers update state.

Control flow: user chooses normal/negative entry, types a name, selects permission checkboxes, and presses OK. The dialog collects name/rights, checks for duplicates in the target ACL list, and returns values to the caller.

State/persistence: maintains `m_bNormal`, `m_Rights`, `m_strName`, and `m_pAclSetDlg` in memory. No persistent writes; caller updates ACL arrays and eventually saves.

Dependencies/integration: used by `CPropACL` and `set_afs_acl` style dialogs, uses localized resources, MFC DDX, and help/message helpers.

Risks: `m_pAclSetDlg` must be set before OK; otherwise `OnOK` dereferences null. `OnChangeName` enables OK when name is non-empty but never disables it again if the name is cleared.

Test signals: normal/negative selection, each permission bit, empty-name enable/disable, duplicate-name rejection, missing interface defensive behavior, and help launch.
