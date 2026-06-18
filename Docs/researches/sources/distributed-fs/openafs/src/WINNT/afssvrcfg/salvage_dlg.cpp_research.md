<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp

Purpose: Implements the salvage options dialog and starts an asynchronous bos salvage operation for the server, selected partition, or selected volume.

Important APIs/functions: `ShowSalvageDlg` captures the optional partition and creates `g_CfgData.hSalvageThread` after OK. `SalvageDlgProc`, `OnInitDialog`, `OnAdvanced`, `UpdateControls`, `OnSalvage`, and worker `Salvage` manage UI and execution.

Control flow: The dialog defaults to partition salvage when a partition is selected, otherwise only server salvage is allowed. Advanced options are initially collapsed. OK validates volume name and optional parallel process count, prompts for admin login if reusable admin info is unavailable, refreshes handles, and starts a worker thread. The worker opens the bos server, calls `bos_Salvage` with selected partition/volume/temp/log/process options and fixed salvage flags, closes the bos server, and records whether admin info can be reused.

State and persistence: Uses static buffers for selected partition, volume, temp directory, process count, and output pointers consumed by the worker. Writes `g_CfgData.szSalvageLogFileName`, `hSalvageThread`, and `bReuseAdminInfo`. Durable effects are server salvage activity and optional salvage log generation by bosserver.

Dependencies and integration points: Integrates OpenAFS bos admin APIs, `admin_info_dlg` for login, `GetHandles`, app-library help/modal UI, and the salvage-results dialog that waits on `g_CfgData.hSalvageThread`.

Risks: Static option buffers are shared with the worker after the modal dialog closes. UI controls for advanced flags are shown but their checkbox values are not passed; fixed flags are used instead. Worker calls `ShowError` from a background thread. Thread handle ownership is transferred to the results dialog; if results are not shown, it can leak. User-specified log file is saved later from fetched log text, not passed to `bos_Salvage`.

Test signals: Test server/partition/volume modes, no selected partition, invalid/empty volume, process count bounds, admin login failure, handle refresh failure, bos open/salvage failure, advanced collapse/expand, and handoff to results dialog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp -->
