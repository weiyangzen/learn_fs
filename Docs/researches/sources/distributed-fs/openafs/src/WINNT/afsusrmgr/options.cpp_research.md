## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.cpp

Purpose: implements the Options property sheet for regexp style, bad-credential warnings, and automatic refresh interval.

Important APIs/types/functions: `ShowOptionsDialog`, `Options_DlgProc`, `Options_OnInitDialog`, and `Options_OnApply`. Constants define refresh spinner bounds: min 1, default 60, max 10080 minutes, despite a stale comment saying min is 15 minutes.

Control flow: showing options creates a modal PropSheet with one `IDD_OPTIONS` tab. Init checks radio/checkboxes from `gr`, creates the refresh-rate spinner, and enables it only if refresh is checked. Apply copies selections back to `gr`; if refresh rate changed while a cell is open, it starts `taskSET_REFRESH`.

State and persistence behavior: updates restored settings `gr.fWindowsRegexp`, `gr.fWarnBadCreds`, and `gr.cminRefreshRate`. Persistence to registry occurs on `Quit`.

Dependencies and integration points: command menu calls `ShowOptionsDialog`; credential warning code reads `gr.fWarnBadCreds`; search code likely reads regexp mode; refresh scheduling uses `taskSET_REFRESH`.

Risks: apply does not immediately persist settings unless the app quits cleanly. Refresh-rate comment disagrees with the actual minimum. Toggling refresh only enables/disables the spinner; task scheduling changes happen on Apply.

Test signals: switch regexp modes, warning checkbox, disable refresh, set min/default/max refresh, apply with and without open cell, and verify `taskSET_REFRESH` only starts on actual interval changes.
