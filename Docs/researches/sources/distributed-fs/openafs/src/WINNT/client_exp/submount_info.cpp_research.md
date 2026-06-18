## sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.cpp

Purpose: Implements constructors/destructor for the simple submount data object.

Important APIs/functions: Default constructor sets status to `SIS_NULL`; value and copy constructors populate status, share name, and path name through setters; destructor does no extra cleanup.

Control flow/state: State is only the three fields declared in `submount_info.h`; ownership is by callers storing pointers in `SUBMT_INFO_ARRAY`.

Dependencies/integration: Uses `stdafx.h`, AFS base headers, and `CSubmountInfo`. Consumed by `submounts_dlg.cpp` and add-submount workflows.

Risks/tests: Copy behavior is shallow only for `CString` value fields, which is acceptable. Test status propagation and pointer ownership in `CSubmountsDlg`.
