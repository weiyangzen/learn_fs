## sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.h

Purpose: Declares `CMakeMountPointDlg`, the MFC form for mount point creation.

Important APIs/types: Public setters provide directory, cell, and volume defaults; `MountWasMade` reports operation success. Dialog data binds OK, volume, RW radio, directory, cell, and mount type.

Control flow/state: Private cached strings are updated by edit-change handlers; `CheckEnableOk` controls command availability.

Dependencies/integration: Uses MFC and resource IDs from the shell extension resources. The implementation calls `MakeMount`.

Risks/tests: Header has no include guard. Test dialog resource IDs and that caller logic observes `MountWasMade`.
