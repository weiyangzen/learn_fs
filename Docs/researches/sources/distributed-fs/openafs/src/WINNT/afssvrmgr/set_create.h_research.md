# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.h

## Purpose
`set_create.h` declares the Create Fileset dialog entry point and the task parameter structure for fileset creation.

## Important APIs, Types, And Functions
`SET_CREATE_PARAMS` contains the target aggregate identity, new fileset name, quota in KB units, and whether to create a clone. `Filesets_Create(LPIDENT lpiParent = NULL)` opens the dialog.

## Control Flow
The dialog fills the struct and transfers it to `taskSET_CREATE` on success. On cancel or validation failure, the implementation deletes it.

## State And Persistence
The struct is transient dialog/task state. No persistent settings are declared here.

## Dependencies And Integration Points
Consumers need `LPIDENT`, `TCHAR`, quota units, and task-layer agreement on `SET_CREATE_PARAMS`.

## Risks And Test Signals
Risks include ownership transfer and quota unit assumptions. Compile coverage and task tests for create-fileset parameter handling are the main signals.
