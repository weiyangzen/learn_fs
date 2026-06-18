# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.cpp

Purpose: implements the AFS Server Manager "Salvage Volumes" workflow. It owns the salvage selection dialog, an advanced-options expander, async population of server/aggregate/fileset combo boxes, dispatch of the salvage task, and a separate results dialog for displaying salvager output.

Important APIs/functions: `Server_Salvage` is the public entry point and uses `PropCache_Search/Add/Delete` to keep one dialog per target identity. `Server_Salvage_DlgProc` handles help, `WM_INITDIALOG`, `WM_ENDTASK`, and commands. `Server_Salvage_OnOK` builds `SVR_SALVAGE_PARAMS` and starts `taskSVR_SALVAGE`. `Server_Salvage_Results_DlgProc`, `Server_Salvage_Results_OnInitDialog`, and `Server_Salvage_OnEndTask_Salvage` render the result title and log text.

Control flow: initialization disables selection controls, starts `taskSVR_ENUM_TO_COMBOBOX`, then chains aggregate enumeration and fileset enumeration through `WM_ENDTASK`. The all-aggregates/all-filesets checkboxes gate which combo boxes are enabled. On OK, the chosen target is resolved from fileset to aggregate to server, and the task scheduler posts completion to the hidden results dialog.

State and persistence: dialog state lives in controls and `DWLP_USER`; no registry writes occur here. The result dialog is shown only after successful completion. The code registers the original dialog with `AfsAppLib_RegisterModelessDialog`, but the result dialog is the actual task reply window.

Dependencies/integration: depends on `svrmgr.h`, `svr_salvage.h`, `propcache.h`, AfsAppLib dialog helpers, `StartTask`, Fast/Combo helper APIs, and the task implementation in `task.cpp` that calls `AfsClass_Salvage`.

Risks: `Server_Salvage_OnEndTask_EnumAggregates` assumes `lpi` is non-null when comparing `lpi->GetServer()`, though the public entry point expects a valid identity. `WM_COMMAND` intentionally or accidentally falls through from `IDOK` to `IDCANCEL`, destroying the dialog after dispatch. The `WM_CTLCOLOREDIT` handler creates a brush per message without caching or deleting it. Tests should exercise chained enumeration, all-scope checkbox behavior, parameter mapping for advanced options, failures from `taskSVR_SALVAGE`, and missing/unreadable salvage logs.
