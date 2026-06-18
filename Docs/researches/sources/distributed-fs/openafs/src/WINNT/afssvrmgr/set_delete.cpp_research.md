# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.cpp

## Purpose
`set_delete.cpp` implements fileset deletion confirmation. It handles normal read-write volumes, read-only replicas, clones, and ghost state where VLDB and server entries may differ.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Delete`. Internal handlers are `Filesets_Delete_DlgProc`, `Filesets_Delete_OnInitDialog`, `Filesets_Delete_OnEndTask_FindGhost`, `Filesets_Delete_OnCheckBoxes`, and `Filesets_Delete_ShrinkWindow`. Parameters are stored in `SET_DELETE_PARAMS`.

## Control Flow
Before opening a dialog, `Filesets_Delete` checks `PropCache` for an existing delete dialog for that fileset. The modeless dialog starts hidden, formats object text, disables OK, and starts `taskSET_FIND_GHOST`. When status returns, it rejects replicated read-write filesets, sets default VLDB/server deletion checkboxes from ghost bits, specializes the dialog for replicas or clones by hiding checkboxes, enables only valid choices, shows the dialog, and eventually starts `taskSET_DELETE` if the user selected at least one deletion surface.

## State And Persistence
Dialog/task state includes target identity, selected VLDB/server deletion flags, ghost flags, and current help dialog ID. The property cache prevents duplicate modeless delete dialogs. No settings are persisted.

## Dependencies And Integration Points
Dependencies include `PropCache`, AfsAppLib help, `taskSET_FIND_GHOST`, `taskSET_DELETE`, fileset status types, ghost flag constants, error dialogs, and resource strings for normal/replica/clone descriptions.

## Risks And Edge Cases
The dialog is modeless and transfers ownership of `SET_DELETE_PARAMS` to the task on OK, so lifetime bugs are possible if later messages arrive. Destroying the window after starting the task leaves task-layer ownership. Replicated read-write filesets are blocked based on the ghost/status task result. Shrink logic assumes specific control positions.

## Test Signals
Test duplicate dialog focus, ghost combinations, read-write with replicas rejection, replica and clone specialized layouts, VLDB/server checkbox enablement, OK disable when nothing selected, cancel cleanup, task parameter values, and hidden-until-status behavior.
