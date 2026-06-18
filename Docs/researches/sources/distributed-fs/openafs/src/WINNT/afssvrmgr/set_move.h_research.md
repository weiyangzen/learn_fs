# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.h

## Purpose
`set_move.h` declares the Move Fileset dialog and its parameter structure.

## Important APIs, Types, And Functions
`SET_MOVE_PARAMS` contains `lpiSource` and `lpiTarget`. `Filesets_ShowMoveTo(LPIDENT lpiSource, LPIDENT lpiTarget)` opens the dialog.

## Control Flow
The implementation updates `lpiTarget` from UI selection and transfers the struct to `taskSET_MOVE` on OK.

## State And Persistence
The struct is transient dialog/task state and is not persisted.

## Dependencies And Integration Points
The header depends on `LPIDENT` and is used by fileset menu and drag/drop paths.

## Risks And Test Signals
Risks include ownership transfer and stale identities between dialog open and task execution. Compile coverage and move task parameter tests validate the API.
