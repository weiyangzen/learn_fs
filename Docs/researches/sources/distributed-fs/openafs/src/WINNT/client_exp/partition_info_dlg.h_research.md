## sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.h

Purpose: Declares `CPartitionInfoDlg`, a simple volume partition information dialog.

Important APIs/types: Public `SetValues(LONG nSize, LONG nFree)` provides data. Dialog ID `IDD_PARTITION_INFO` binds total size, percent used, and free-block edit controls.

Control flow/state: Private `LONG` fields store size/free until `OnInitDialog`.

Dependencies/integration: MFC and resource IDs; launched from `volumeinfo.cpp`.

Risks/tests: Uses `LONG` despite `CVolInfo` storing partition values as `unsigned __int64`. Test large partition sizes and include-order safety, since the header has no include guard.
