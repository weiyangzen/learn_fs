## sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.h

Purpose: Declares `CSymlinksDlg`, the list-only dialog for symlink results.

Important APIs/types: Public `SetSymlinks` supplies rows. Dialog ID `IDD_SYMLINKS` binds `IDC_LIST`.

Control flow/state: Private `CStringArray m_Symlinks` stores rows until initialization.

Dependencies/integration: MFC and resource IDs; used by `ListSymlink`.

Risks/tests: Header lacks include guards, and the parameter name still says `mountPoints`. Test repeated include compatibility and display of caller-copied data.
