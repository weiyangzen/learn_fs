# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.cpp

## Purpose
`set_dump.cpp` implements the Dump Fileset dialog, collecting a local dump filename and optional incremental timestamp before starting the dump task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Dump`. Internal handlers are `Filesets_Dump_DlgProc`, `Filesets_Dump_OnInitDialog`, `Filesets_Dump_OnSelect`, `Filesets_Dump_EnableOK`, `Filesets_Dump_OnOK`, and `Filesets_Dump_OnBrowse`.

## Control Flow
`Filesets_Dump` allocates `SET_DUMP_PARAMS`, shows `IDD_SET_DUMP`, and starts `taskSET_DUMP` on OK. Initialization formats source identity text, creates a default dump filename from the fileset name, initializes date/time controls to local time, selects full dump by default, and enables OK only when a filename exists. Radio changes toggle date/time controls. Browse builds a filter from localized strings and uses `GetSaveFileName` with overwrite and path checks.

## State And Persistence
Runtime state includes target identity, filename, `fDumpByDate`, and `stDump`. No settings are persisted. The selected filename is copied into the task parameter block on OK.

## Dependencies And Integration Points
Dependencies include Win32 common dialogs, date/time helper controls (`DA_*`, `TI_*`), resource strings, and task ID `taskSET_DUMP`. It integrates with fileset menus and action-progress handling through the task subsystem.

## Risks And Edge Cases
The dialog validates only that the filename field is nonempty; path validity is mostly delegated to `GetSaveFileName` when browse is used and to the dump task otherwise. The filter parsing depends on the final character of the localized string being the separator. Date/time is local time, while backend interpretation must agree on timezone semantics.

## Test Signals
Test default filename generation, browse filter and default extension, manual filename validation, full versus time-limited dump selection, date/time round-trip, cancel cleanup, and task parameter values for full and incremental dumps.
