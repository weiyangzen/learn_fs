## sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.cpp

Purpose: Implements the dialog for creating an AFS symbolic link from a base Explorer directory.

Important APIs/functions: `CMakeSymbolicLinkDlg::OnOK` validates the base path is in AFS, switches the process current directory to that base, and calls `MakeSymbolicLink`. `CheckEnableOk` tests cached name/target fields, and `OnInitDialog` initializes controls.

Control flow/state: The base path is set through `Setbase`; name and target are DDX-bound strings with max-character validators. The change handlers are present but commented out in the message map, so OK enablement may not update dynamically.

Dependencies/integration: Calls `IsPathInAfs`, `MakeSymbolicLink`, `GetAfsError`, and `ShowMessageBox`. Used by the shell extension symbolic-link menu.

Risks/tests: Changing process current directory from an Explorer extension can affect later relative operations. `m_sBase` length and AFS membership errors must be handled before creation. Test base directory extraction, relative link names, non-AFS bases, long paths, missing change-handler wiring, and create-failure display.
