# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.cpp

Purpose: Implements fileset quota editing and quota display. It can either apply a supplied quota immediately or ask the user via a modal quota dialog.

Important APIs/functions: `Filesets_SetQuota` dispatches `taskSET_SETQUOTA_APPLY`; `Filesets_PickQuota` returns a chosen quota or zero on cancel; `Filesets_SetQuota_DlgProc` handles quota dialog messages; `Filesets_SetQuota_OnEndTask_InitDialog` initializes/updates the spinner based on `ckMin`, `ckMax`, and current quota; `Filesets_DisplayQuota` formats usage text and progress bar percentage.

Control flow: If caller passes `ckQuota == 0`, the modal dialog loads current fileset state through `taskSET_SETQUOTA_INIT`. Unit changes update `gr.cbQuotaUnits`, preserve current value, and restart init to rebuild spinner ranges. Applying closes the dialog and returns quota in KB to `Filesets_SetQuota`, which starts the async apply task.

State and persistence: Uses global `gr.cbQuotaUnits` as a UI preference for KB vs MB. The quota value in the packet is always normalized to KB before applying. No direct persistence beyond the task layer changing the fileset quota.

Dependencies/integration: Depends on `agg_prop.h` to open aggregate properties, `Alert_GetCount`, spinner helpers, combobox helpers, and `LPFILESETSTATUS` from AFS class/task data.

Risks: The dialog procedure stores packet state in a static variable, so concurrent quota dialogs would interfere; the UI likely assumes modal single-instance use. Integer conversion to `int` for spinner min/current/max may truncate very large quotas. MB unit conversion uses integer division, which can round displayed values down.

Test signals: Test cancel path, supplied quota bypass, failed init task, KB/MB switching, very high quota ranges, zero/overfull quota display, and aggregate-properties button routing.
