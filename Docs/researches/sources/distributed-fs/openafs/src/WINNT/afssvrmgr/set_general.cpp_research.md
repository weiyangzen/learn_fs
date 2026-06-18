# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.cpp

## Purpose
`set_general.cpp` contains common fileset helpers for preferences, selection, focus lookup, and lock-state checks.

## Important APIs, Types, And Functions
Public functions are `Filesets_LoadPreferences`, `Filesets_SavePreferences`, `Filesets_GetSelected`, `Filesets_GetFocused`, and `Filesets_fIsLocked`.

## Control Flow
Preference loading allocates `FILESET_PREF`, attempts registry restore, and falls back to default warning and alert settings. It always calls `Alert_Initialize`. Saving retrieves the preference pointer from the identity user param and stores it if present. Selection/focus helpers read `IDC_SET_LIST` FastList state, optionally hit-testing a point. Lock checks test `fsLOCKED` in a `FILESETSTATUS`.

## State And Persistence
Fileset preferences are registry-backed through `RestorePreferences` and `StorePreferences`. Runtime user-param state stores warning settings, alert options, last status, and read-write identity as populated by other modules.

## Dependencies And Integration Points
Dependencies include preference helpers, alert initialization/defaults, FastList wrappers, resource control `IDC_SET_LIST`, and fileset status flags. Display and property modules use these helpers.

## Risks And Edge Cases
`Filesets_LoadPreferences` assumes allocation succeeds. `Filesets_SavePreferences` silently returns false if no user param exists. `Filesets_GetFocusedItem` is declared in the header but not implemented in this file, suggesting either dead API or implementation elsewhere; this should be checked by link coverage.

## Test Signals
Test preference fallback, registry round-trip, alert initialization after restore, selected/focused identity retrieval, point hit testing, lock-state detection, and link coverage for all header declarations.
