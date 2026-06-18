<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp

Purpose: Displays live and final salvage log output while waiting for the salvage worker thread to finish, and optionally saves the final log to disk.

Important APIs/functions: `ShowSalvageResults` opens the modal dialog. `OnInitDialog` opens a bos server handle, disables system close, starts animation, and spawns `ShowResults`. `ShowResults` waits on `g_CfgData.hSalvageThread`, periodically calls `bos_LogGet`, expands buffers on `ADMMOREDATA`, converts LF to CRLF, trims to edit-control capacity, updates the edit control, saves the final log, closes the salvage thread handle, and enables Close. Helpers include `AddCarriageReturnsToLog`, `GetMaxPartOfLogWeCanShow`, `AllocMemory`, and `SaveLogToDisk`.

Control flow: The dialog cannot be closed until `bSalvageComplete` is true. The polling thread updates the log every five seconds or immediately when the salvage thread exits, then marks complete/failure and enables the Close button. `OnClose` closes the bos server and ends the dialog.

State and persistence: Static dialog globals hold bos handle/status/result, logo handle, and completion flag. It reads `g_CfgData.hSalvageThread` and `szSalvageLogFileName`. Durable persistence occurs only if the user supplied a log path, in which case fetched log text is written to that file.

Dependencies and integration points: Uses OpenAFS bos admin APIs, Win32 threads/waits, app-library animation, resize helpers, conversion wrappers, global config/log state, and the salvage dialog's thread handle.

Risks: Worker thread updates dialog controls directly. `AllocMemory` uses `delete` instead of `delete[]` for arrays, and cleanup also uses `delete` for arrays. `pszLogBuf[nLogSize] = 0` assumes the allocated buffer is larger than the returned size. `bos_ServerClose` only runs on user close; init failure can leave partial UI state. Close handle ownership depends on this dialog always running after salvage starts.

Test signals: Test short and large salvage logs, `ADMMOREDATA` resizing, log over edit-control limit, save-to-disk success/failure, bos open/log get failure, user pressing Cancel before/after completion, and memory diagnostics for array deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp -->
