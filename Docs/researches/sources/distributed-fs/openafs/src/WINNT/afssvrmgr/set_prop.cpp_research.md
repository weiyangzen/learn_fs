# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.cpp

Purpose: Implements the fileset properties sheet, primarily the General tab for a selected fileset. It shows identity, timestamps, state, quota usage, lock/unlock controls, and fileset-full warning settings.

Important APIs/functions: `Filesets_ShowProperties` opens or focuses a cached modeless property sheet and can jump directly to the threshold/problems tab. `Filesets_General_DlgProc` is the Win32 dialog procedure. `Filesets_General_OnInitDialog` fills static identity fields and disables controls while data loads. `Filesets_General_OnEndTask_InitDialog` consumes `taskSET_PROP_INIT` results and refreshes all status controls. `Filesets_General_OnApply` packages warning settings in `SET_PROP_APPLY_PARAMS` for `taskSET_PROP_APPLY`. `Filesets_General_OnWarnings` enables/disables threshold controls based on radio/checkbox state.

Control flow: The property sheet is cached via `PropCache` under `pcSET_PROP`. On `WM_INITDIALOG`, it starts `taskSET_PROP_INIT` and registers `NotifyMe(WHEN_OBJECT_CHANGES, lpi, ...)`. On `WM_ENDTASK`, failed status refresh displays unknown values and an error dialog; successful refresh enables controls, formats timestamps, calculates alert/status text, shows quota via `Filesets_DisplayQuota` for read-write filesets, and replaces quota UI with a static explanation for replicas/clones. Command handling applies warning changes, opens the quota dialog, or starts lock/unlock tasks.

State and persistence: This file does not persist settings directly; it collects UI state and dispatches task packets. It reads server/fileset preferences from the task data (`lpsp`, `lpfp`) and relies on the task layer to save changes. It stores only dialog-local `LPIDENT` in `DWLP_USER` and uses `PropCache` for open-window identity.

Dependencies/integration: Depends on `svrmgr.h` task infrastructure, `set_quota.h` for quota display/editing, `svr_general.h` for default warning values, `propcache.h`, and `problems.h`. It integrates with alerts (`Alert_GetCount`), property sheets, AFS identity helpers, and notification dispatch.

Risks: UI depends on valid `TASKDATA(ptp)` members for both fileset status and preference pointers. The code replaces `IDC_SET_USAGEBAR` with a static child for non-RW filesets, so repeated init paths need the control lifetime to match dialog assumptions. Warning percentages use spinner values and `WORD`; bounds are enforced by spinner creation, not by apply-time validation.

Test signals: Exercise property sheet reuse, jump-to-threshold behavior, failed `taskSET_PROP_INIT`, read-write vs replica/clone filesets, lock/unlock/start quota commands, warning off/default/custom states, and object-change notifications while the dialog is open.
