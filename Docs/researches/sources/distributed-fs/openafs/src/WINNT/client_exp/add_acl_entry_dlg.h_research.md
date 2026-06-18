# sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.h

Purpose: declares the ACL add-entry dialog and duplicate-name callback interface.

Important types/APIs: `CSetACLInterface` defines pure virtual `IsNameInUse`; `CAddAclEntryDlg` exposes `SetAclDlg`, `GetName`, `GetRights`, and `IsNormal`, plus MFC controls for name, entry type, and permission checkboxes.

Control flow: dialog users instantiate, set the ACL interface, run `DoModal`, and then read returned entry fields.

State/persistence: holds pending entry name/rights/type only.

Dependencies/integration: uses MFC `CDialog`, `CButton`, `CEdit`, `CString`, resource IDs, and message maps.

Risks: header has no include guard around all MFC dependencies beyond its own guard, and the interface pointer requirement is implicit.

Test signals: compile inclusion from ACL property/dialog modules and duplicate-name callback use.
