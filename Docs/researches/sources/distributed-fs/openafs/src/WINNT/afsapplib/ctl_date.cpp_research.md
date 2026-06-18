## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.cpp

Purpose: Implements a locale-aware composite Date control that expands into year/month/day edit fields, separators, and a spinner.

Important APIs and functions: `RegisterDateClass` registers class `Date`. `DateProc` handles lifecycle, focus, enable, key forwarding, and `DM_GETDATE`/`DM_SETDATE`. `Date_OnCreate` builds child edits in locale order from `LOCALE_IDATE`/`LOCALE_SDATE`. `DateDlgProc` handles edit colors and spinner updates. `DateEditProc`, `Date_Edit_OnSetFocus`, `Date_Edit_OnUpdate`, and `Date_Edit_SetText` synchronize fields with `SYSTEMTIME`.

Control flow: The placeholder Date window creates child edit/static controls in the parent dialog, subclasses edits, creates/reuses a spinner attached to the focused field, and forwards focus/clicks/arrow keys to the relevant child. Updates parse the edit text, mutate `dateNow`, and send `DN_UPDATE` to the parent through `WM_COMMAND`.

State and persistence: Global dynamic `aDate` table, guarded by `csDate`, maps Date HWNDs to child controls and current `SYSTEMTIME`. No durable persistence.

Dependencies and integration points: Uses `ctl_spinner`, `dialog.h` for `NextControlID`, `resize.h`, `subclass.h`, locale APIs, and public messages/macros in `ctl_date.h`.

Risks: `dateNow` is zero-initialized until caller sets a date, so initial spinner positions can be invalid. Day range is always 1-31 and does not validate month/year combinations. Parent color handler creates brushes without stable cleanup. `atoi/atol` use ANSI-oriented parsing under TCHAR builds.

Test signals: Locale formats M/D/Y, D/M/Y, Y/M/D; get/set date; focus changes update spinner range; arrow/page/home/end keys; disabled visual state; invalid dates such as February 31; parent receives `DN_UPDATE`.
