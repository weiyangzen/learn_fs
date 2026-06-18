# sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.cpp

Purpose: implements the dialog for copying ACLs from one directory to another, optionally clearing target ACLs first.

Important APIs/functions: constructor, `OnInitDialog`, `OnChangeToDir`, `OnBrowse`, `OnOK`, and `OnHelp`.

Control flow: initialization displays the source directory. The target edit box enables OK when non-empty. Browse uses `CFileDialog` to choose an existing file and then strips to its containing directory. OK records the clear flag and target path, validates the target with `PathIsDirectory`, and closes on success.

State/persistence: local `m_strFromDir`, `m_strToDir`, and `m_bClear`; actual ACL copy is performed by the caller.

Dependencies/integration: used by `CPropACL`, depends on MFC, `shlwapi`, `_access`/I/O headers, message helpers, and help IDs.

Risks: `PathIsDirectory` returns BOOL, but the code compares to `-1`, so nonexistent paths may not be rejected as intended. Browse cannot select a directory directly, only a file whose directory is then used.

Test signals: empty target disables OK, invalid target rejection, browse path trimming for root and nested paths, clear checkbox propagation, and help display.
