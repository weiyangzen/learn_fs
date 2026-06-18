## sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.h

Purpose: Declares `CSetAfsAcl`, the MFC ACL editor dialog and implementation of the add-entry validation interface.

Important APIs/types: Public `SetDir` chooses the directory under edit, and `IsNameInUse` is exposed to child dialogs. Dialog controls represent ACL lists and permission checkboxes.

Control flow/state: Private helpers render rights, build rights strings, enable/disable permission editing, and respond to selection state.

Dependencies/integration: Includes `add_acl_entry_dlg.h`, resource IDs, and MFC. Implementation depends on `gui2fs.cpp` for actual AFS persistence.

Risks/tests: Header has no include guard and includes another dialog header, increasing coupling. Test compile with repeated includes and child-dialog validation behavior.
