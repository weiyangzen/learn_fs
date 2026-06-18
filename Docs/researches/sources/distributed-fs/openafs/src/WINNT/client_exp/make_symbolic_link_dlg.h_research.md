## sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.h

Purpose: Declares `CMakeSymbolicLinkDlg`, the MFC dialog for AFS symlink creation.

Important APIs/types: Public `Setbase` stores the base directory; dialog data binds OK, name, target directory, and string fields. Handlers cover name/target changes, OK, and initialization.

Control flow/state: `m_sBase` is protected state used during `OnOK`; input fields are cached through DDX.

Dependencies/integration: Depends on MFC and resource ID `IDD_SYMBOLICLINK_ADD`; implementation integrates with `gui2fs.cpp`.

Risks/tests: Header has no include guard. `Setbase` takes `const char *`, which is narrow even when the rest of the UI may be Unicode. Test Unicode base paths and message-map consistency with declared handlers.
