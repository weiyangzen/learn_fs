# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.cpp

## Purpose
`set_clone.cpp` implements fileset clone commands: cloning one selected fileset or cloning multiple filesets in a cell/server/aggregate scope with optional prefix filtering.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Clone`. Single-fileset UI is handled by `Filesets_Clone_DlgProc` and `Filesets_Clone_OnInitDialog`. Bulk clone UI is handled by `Filesets_Clonesys_DlgProc`, `Filesets_Clonesys_OnInitDialog`, `Filesets_Clonesys_OnOK`, `Filesets_Clonesys_OnSelect`, `Filesets_Clonesys_OnSelectServer`, and end-task handlers for server/aggregate enumeration.

## Control Flow
`Filesets_Clone` allocates `SET_CLONESYS_PARAMS`, defaults the target identity to the supplied object or current cell, and chooses a simple confirmation dialog for a fileset or a scope-selection dialog otherwise. Single clone confirmation starts `taskSET_CLONE` with the fileset identity. Bulk clone gathers scope controls, optional prefix/exclusion prefix, and starts `taskSET_CLONESYS`, transferring ownership of the parameter block to the task.

## State And Persistence
Dialog state lives in `SET_CLONESYS_PARAMS`: target identity, prefix flags, prefix text, and enumeration-complete flags. No settings are persisted. The property cache tracks clone dialogs while open.

## Dependencies And Integration Points
Dependencies include `PropCache`, task IDs `taskSET_CLONE`, `taskSET_CLONESYS`, `taskSVR_ENUM_TO_COMBOBOX`, and `taskAGG_ENUM_TO_COMBOBOX`, combobox helpers, current cell `g.lpiCell`, and resource controls for clone scope selection.

## Risks And Edge Cases
The same `pcSET_CLONE` cache key is used for both single and bulk clone dialogs with `NULL` payload, so only one clone dialog of either kind can be active. Prefix exclusion is encoded by a leading `!`, which is simple but ambiguous if a literal prefix begins with that character. OK can be disabled while asynchronous enumeration is incomplete; failed enumeration handling is minimal.

## Test Signals
Test single-fileset clone confirmation, bulk clone for cell/server/aggregate, server combobox enumeration, aggregate combobox refresh when server changes, prefix include/exclude parsing, OK enablement during enumeration, cancel cleanup, and task parameter ownership.
