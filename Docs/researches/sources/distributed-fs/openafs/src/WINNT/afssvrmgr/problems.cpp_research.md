# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.cpp

## Purpose
`problems.cpp` implements the Problems tab shown on property sheets when an AFS object has alerts. It summarizes alert count, displays alert descriptions/remedies, provides a remedy button, and updates itself when the underlying object changes.

## Important APIs, Types, And Functions
The dialog entry point is `Problems_DlgProc`. Internal handlers are `Problems_OnInitDialog`, `Problems_OnRefresh`, `Problems_OnRedraw`, `Problems_OnRemedy`, and `ParseFilesetName`. Remedy actions call `StartTask(taskREFRESH)`, `Filesets_ShowProperties`, `Aggregates_ShowProperties`, `Services_ShowServiceLog`, or `NewCredsDialog` depending on alert type.

## Control Flow
On initialization the dialog stores the target `LPIDENT`, subscribes through `NotifyMe`, formats a title based on object type, and refreshes. Refresh reads `Alert_GetCount`; zero alerts hide scrolling/remedy controls and show a no-problems string, one alert redraws without the scrollbar, and multiple alerts configure a scrollbar. Redraw reads the selected alert's description, remedy text, and button label. The remedy button maps selected alert type to the appropriate corrective UI or task.

## State And Persistence
State is dialog-local (`DWLP_USER`, scrollbar position, visible controls) plus the alert subsystem's state. No settings are persisted. Notification subscriptions are removed with `DontNotifyMeEver` on destroy.

## Dependencies And Integration Points
Dependencies include the alert subsystem, AFSClass notification dispatch (`WM_NOTIFY_FROM_DISPATCH`), service log viewing, fileset and aggregate properties, credentials dialogs, and resource strings. The macro in `problems.h` decides whether this tab is added to property sheets.

## Risks And Edge Cases
`WM_CTLCOLORSTATIC` returns a newly created brush without visible cleanup, which can leak GDI objects. `ParseFilesetName` appears to compute `pszBase[pszEnding - szFileset]`, subtracting pointers from different buffers; that is suspicious and could corrupt memory if the function is used. Remedy handling assumes alert target identities remain valid. Alerts with no button intentionally hide remediation.

## Test Signals
Test zero/one/multiple alert display, scrollbar navigation, notification-driven refresh, each remedy action, property-tab addition only when alerts exist, object-title formatting for all identity types, GDI leak checks, and direct tests for `ParseFilesetName` with `.readonly`, `.backup`, and ordinary names.
