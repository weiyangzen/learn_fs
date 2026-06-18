# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.cpp

## Purpose
`helpfunc.cpp` implements Server Manager help features: command help lookup, numeric error translation, About dialog behavior, and registration of context-sensitive help maps for dialogs across the application.

## Important APIs, Types, And Functions
Public functions are `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`. Internal structures map Unix command families (`vos`, `bos`, `kas`, `fs`) to string and help IDs. `lstrstr` performs case-insensitive substring search, `Help_FindCommand_Search` strips leading command-family tokens, `Help_FindError_OnTranslate` formats system/OpenAFS error text, and `Main_ConfigureHelp` registers dozens of dialog/control help maps through AfsAppLib.

## Control Flow
The Find Command dialog fills a combobox from `aCOMMANDS`, accepts free text, narrows by utility family if the user typed one, searches localized command strings, and opens WinHelp at the selected context ID. The Find Error dialog starts in a compact state, parses decimal or hex input with `strtoul`, formats an error description, strips the trailing numeric code, and expands the window with the translated text. The About dialog subclasses its OK button and uses timer/syscommand hooks plus `NextSearch()` to reveal hidden animated text.

## State And Persistence
The module has static command/help tables, compressed search values for the About animation, and static layout state for the error dialog shrink/expand path. No persistent settings are written. Help registration mutates AfsAppLib's process-global help table.

## Dependencies And Integration Points
Dependencies include Win32 dialogs, WinHelp, AfsAppLib help registration, localization resource IDs, control IDs from `resource.h`, and string/error formatting helpers. The help maps cover fileset create/delete/move/dump/restore, server operations, service operations, subsets, credentials, options, and problem tabs.

## Risks And Edge Cases
The command search relies on localized command strings and a first-match substring search, so ambiguous keywords may open an unexpected topic. `Help_FindCommand_Search` edits the input buffer by inserting NULs. The About dialog uses hard-coded child IDs (`0x051E`, `0x051F`) and nonstandard messages. The error dialog creates a brush in `WM_CTLCOLORSTATIC` without visible ownership management elsewhere.

## Test Signals
Test command lookup by full command, partial command, and family-qualified search; unknown and empty input paths; decimal and hex error translation; shrink/expand layout; WinHelp context opening; About dialog lifecycle; and context help coverage for every dialog ID registered in `Main_ConfigureHelp`.
