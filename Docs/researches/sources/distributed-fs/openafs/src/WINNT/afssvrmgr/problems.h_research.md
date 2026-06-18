# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.h

## Purpose
`problems.h` declares the Problems dialog procedure and provides a helper macro for conditionally adding the Problems tab to property sheets.

## Important APIs, Types, And Functions
`PropSheet_AddProblemsTab(_psh,_idd,_lpi,_nAlerts)` returns true without adding a tab when alert count is zero; otherwise it calls `PropSheet_AddTab` with `Problems_DlgProc`. The header declares `BOOL CALLBACK Problems_DlgProc(...)`.

## Control Flow
The macro is used during property sheet construction to avoid showing an empty Problems tab. The dialog procedure handles runtime refresh and remedy behavior.

## State And Persistence
No storage is declared. The macro passes `LPIDENT` as tab lParam so the dialog can access alert state.

## Dependencies And Integration Points
It depends on property-sheet helpers, resource ID `IDS_PROBLEMS`, and Win32 dialog signatures. It integrates property pages with the alert display module.

## Risks And Test Signals
Macro arguments may be evaluated more than once only for `_nAlerts` in the condition and `_lpi` in the add path, so callers should avoid side effects. Test property sheets with zero and nonzero alerts.
