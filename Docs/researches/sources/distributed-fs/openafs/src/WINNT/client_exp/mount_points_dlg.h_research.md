## sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.h

Purpose: Declares the list-only `CMountPointsDlg` class.

Important APIs/types: Public `SetMountPoints` is the only data ingress. Dialog ID `IDD_MOUNT_POINTS` and `IDC_LIST` are bound to an MFC `CListBox`.

Control flow/state: Private `m_MountPoints` stores rows until initialization populates the control.

Dependencies/integration: MFC and shell extension resources; used by `ListMount`.

Risks/tests: Header lacks an include guard. Validate resource ID consistency and copy semantics with caller-owned arrays.
