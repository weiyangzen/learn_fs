## sources/distributed-fs/openafs/src/WINNT/client_exp/volume_info.h

Purpose: Declares `CVolumeInfo`, the dialog for viewing and changing volume quotas.

Important APIs/types: Public `SetFiles` provides selected paths. Private `ShowInfo` renders rows and `GetCurVolInfoIndex` resolves duplicate volume selections. Dialog controls include list, quota edit, quota spin, partition info, and OK button.

Control flow/state: The dialog owns an allocated `CVolInfo` array and tracks current selection in `m_nCurIndex`.

Dependencies/integration: Uses `CVolInfo`, MFC controls, and resource ID `IDD_VOLUME_INFO`; implementation calls `GetVolumeInfo`, `SetVolInfo`, and `CPartitionInfoDlg`.

Risks/tests: Header lacks include guard and uses `unsigned __int64` in DDX. Test allocation/destruction, multiple files in same volume, and quota edit/spin behavior.
