## sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.cpp

Purpose: Shows partition size/free/percent-used values for the selected volume.

Important APIs/functions: `SetValues` in the header seeds `m_nSize` and `m_nFree`; `OnInitDialog` formats them into controls and computes percent used. `OnHelp` opens partition help.

Control flow/state: The dialog is pure presentation; values come from `CVolumeInfo::OnPartitionInfo` after `GetVolumeInfo` populated `CVolInfo`.

Dependencies/integration: Uses MFC edit controls, `TaLocale`, and help ID `PARTITION_INFO_HELP_ID`.

Risks/tests: It computes `strPerUsed` twice and never calls `m_PercentUsed.SetWindowText`, so the percent field may remain blank. `ASSERT(m_nSize != 0)` is not runtime protection in release builds. Test zero-size values, large 64-bit values truncated to `LONG`, and percent display.
