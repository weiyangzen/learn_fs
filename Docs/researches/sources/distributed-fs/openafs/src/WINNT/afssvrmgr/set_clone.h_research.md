# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.h

## Purpose
`set_clone.h` declares the fileset clone UI entry point and the parameter block used by single and bulk clone workflows.

## Important APIs, Types, And Functions
`SET_CLONESYS_PARAMS` stores `LPIDENT lpi`, prefix include/exclude flags, a `MAX_PATH` prefix buffer, and server/aggregate enumeration flags. The public function is `Filesets_Clone(LPIDENT lpi)`.

## Control Flow
Callers pass a fileset, aggregate, server, or cell identity. The implementation decides whether to show single or bulk clone UI and then starts the relevant task.

## State And Persistence
The struct is runtime task/dialog state. It is not persisted.

## Dependencies And Integration Points
The header depends on `LPIDENT`, `BOOL`, and `TCHAR`. Task handlers consume this struct for `taskSET_CLONESYS`.

## Risks And Test Signals
Risks include ownership transfer of the struct to asynchronous tasks and prefix buffer truncation. Compile coverage and clone task tests validate the contract.
