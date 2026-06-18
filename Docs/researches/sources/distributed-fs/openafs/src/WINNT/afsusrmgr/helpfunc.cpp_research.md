## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.cpp

Purpose: implements command lookup help, error-code translation, about dialog behavior, and context-help registration.

Important APIs/types/functions: public functions are `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`. Helpers include `lstrstr`, `Help_FindCommand_Search`, `NextSearch`, dialog procedures, error shrink/expand logic, and many static dialog-control-to-help-ID arrays.

Control flow: command help populates a combo from `aCOMMANDS`, skips leading utility words like `pts` or `kas`, does case-insensitive substring matching, and opens WinHelp at the matched context. Error help parses numeric input with `strtoul`, translates via `AfsAppLib_TranslateError`, strips duplicated numeric suffixes, and expands the dialog to show results. About dialog subclasses the OK button and uses timer/system-command messages plus `aSEARCHVALUES` for hidden text behavior. `Main_ConfigureHelp` registers the help file and per-dialog context maps.

State and persistence behavior: static arrays hold command mappings, packed search values, and help maps. No user settings are persisted.

Dependencies and integration points: depends on WinHelp, AfsAppLib help registration, localization resources, dialog resource IDs, and help context IDs from help headers/resources.

Risks: help mappings must stay synchronized with dialogs and `resource.h`; stale control IDs silently break F1/context help. `NextSearch` packed data logic is opaque and uses static command state. Parsing error input accepts C numeric bases but does not validate trailing garbage.

Test signals: search PTS/KAS command aliases, unknown/empty command input, translate decimal and hex error codes, context-help every registered dialog, and exercise about dialog close/subclass cleanup.
