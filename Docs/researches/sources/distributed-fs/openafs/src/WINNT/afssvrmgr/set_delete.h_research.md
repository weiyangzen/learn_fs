# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.h

## Purpose
`set_delete.h` declares fileset deletion UI and the task parameter structure.

## Important APIs, Types, And Functions
`SET_DELETE_PARAMS` stores target fileset identity, booleans for VLDB and server deletion, ghost flags, and the help dialog ID. `Filesets_Delete(LPIDENT lpiFileset)` opens or focuses the delete dialog.

## Control Flow
The implementation fills the struct after a ghost-status task and passes it to `taskSET_DELETE` on confirmation.

## State And Persistence
The struct is runtime dialog/task state. No persistence is declared.

## Dependencies And Integration Points
It depends on `LPIDENT`, Win32 booleans, and ghost/task semantics defined elsewhere.

## Risks And Test Signals
Risks include task ownership and consistency between `wGhost`, `fVLDB`, and `fServer`. Compile and delete-task parameter tests cover the contract.
