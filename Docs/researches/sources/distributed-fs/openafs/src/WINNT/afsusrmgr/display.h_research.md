## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.h

Purpose: declares tab and FastList display services for account manager modules.

Important APIs/types/functions: defines `TABTYPE` (`ttUSERS`, `ttGROUPS`, `ttMACHINES`) and declares population, async completion, view refresh, selection, active-tab, column notification, lazy text, and icon-selection functions.

Control flow: tab dialogs and command handlers use these declarations to populate current lists and retrieve selected ASIDs for commands. FastList callbacks call `Display_GetItemText`, and notification handlers call `Display_HandleColumnNotify`.

State and persistence behavior: API operates on global windows and restored `VIEWINFO`/`ICONVIEW` records rather than caller-owned display state.

Dependencies and integration points: uses `LPTASKPACKET`, `LPVIEWINFO`, `LPASIDLIST`, `LPFLN_GETITEMTEXT_PARAMS`, `ICONVIEW`, and `ASID` from the larger OpenAFS Windows support headers.

Risks: all selection helpers assume the current tab child contains exactly one recognized list control. Adding tabs or changing resource IDs requires updating implementation heuristics.

Test signals: compile all callers after any signature changes and verify user/group/machine tabs all support populate, selection, column notification, and lazy text callbacks.
