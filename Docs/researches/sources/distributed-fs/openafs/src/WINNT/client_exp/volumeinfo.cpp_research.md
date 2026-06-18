## sources/distributed-fs/openafs/src/WINNT/client_exp/volumeinfo.cpp

Purpose: Implements the volume information/quota dialog for selected AFS paths.

Important APIs/functions: `OnInitDialog` allocates `CVolInfo` entries and calls `GetVolumeInfo`; `ShowInfo` renders rows; `OnSelChangeList` loads selected quota into the edit; `OnPartitionInfo` opens partition details; `OnChangeNewQuota` marks changes; `OnOK` persists changed unique volumes with `SetVolInfo`; `OnDeltaPosQuotaSpin` adjusts quota by 1024 blocks.

Control flow/state: The list item data maps display rows to `m_pVolInfo` indexes; duplicate volumes should share quota changes through `m_nDup`.

Dependencies/integration: Uses `gui2fs.cpp`, `partition_info_dlg`, `msgs`, MFC common controls, and localized resources.

Risks/tests: Missing braces in duplicate detection cause `break` to run after the first comparison, so duplicates after index 0 may be missed. `unsigned __int64 nNewQuota < 0` is ineffective, and `%ld` formatting truncates 64-bit IDs/quotas. Test multi-selection duplicates, unlimited quota, spin underflow/overflow, failed `GetVolumeInfo`, and successful/failed quota persistence.
