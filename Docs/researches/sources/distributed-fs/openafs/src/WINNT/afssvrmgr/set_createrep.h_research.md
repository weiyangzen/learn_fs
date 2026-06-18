# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.h

## Purpose
`set_createrep.h` declares Create Replica UI and its parameter block.

## Important APIs, Types, And Functions
`SET_CREATEREP_PARAMS` contains `lpiSource` and `lpiTarget`. `Filesets_CreateReplica(LPIDENT lpiSource, LPIDENT lpiTarget = NULL)` opens the confirmation/selection dialog.

## Control Flow
The implementation fills or updates `lpiTarget`, then transfers the struct to `taskSET_CREATEREP` on OK.

## State And Persistence
The struct is transient dialog/task state and has no persistence.

## Dependencies And Integration Points
The API depends on `LPIDENT` and is called by fileset menu/drag/drop workflows.

## Risks And Test Signals
Risks include ownership transfer and validating that source/target identities remain live. Compile coverage and create-replica task tests validate the contract.
