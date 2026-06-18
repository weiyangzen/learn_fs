## sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.cpp

Purpose: Implements the modal dialog for creating an AFS mount point.

Important APIs/functions: `CMakeMountPointDlg::OnOK` gathers directory, volume, cell, and read/write selection, then calls `MakeMount`. `OnChangeVolume`, `OnChangeDir`, and `OnChangeCell` update cached input and enable OK. `OnInitDialog` seeds fields from setters and defaults the type to regular.

Control flow/state: `m_bMade` records whether `MakeMount` succeeded. The volume edit is limited manually to 63 characters; OK requires non-empty directory and volume.

Dependencies/integration: Uses MFC controls, localized resources, `gui2fs.cpp` mount creation, and help ID `MAKE_MOUNT_POINT_HELP_ID`.

Risks/tests: `OnOK` closes the dialog even when `MakeMount` fails, leaving callers to inspect `MountWasMade`. Cell input is optional but not validated. Test regular/RW mount strings, long volume names, non-AFS parent, freelance admin checks, empty cell, and failed create result handling.
