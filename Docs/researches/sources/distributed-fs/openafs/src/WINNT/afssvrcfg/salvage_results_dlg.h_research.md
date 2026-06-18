<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h

Purpose: Declares the salvage-results dialog entry point.

Important APIs/functions: `ShowSalvageResults(HWND hParent)` returns true when the results dialog closes with OK.

Control flow: No implementation logic. Callers invoke it after `ShowSalvageDlg` starts the salvage thread.

State and persistence: Implementation observes `g_CfgData.hSalvageThread` and may save the fetched salvage log to `g_CfgData.szSalvageLogFileName`.

Dependencies and integration points: Requires Win32 `HWND`; included by `partitions_page.cpp`.

Risks: The API assumes a salvage thread is already present in global state; there is no parameter enforcing that precondition.

Test signals: Verify caller sequence and behavior when the salvage thread handle is null or already signaled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h -->
