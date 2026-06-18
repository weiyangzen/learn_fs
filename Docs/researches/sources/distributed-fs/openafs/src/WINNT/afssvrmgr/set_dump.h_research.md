# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.h

## Purpose
`set_dump.h` declares the Dump Fileset dialog and its task parameters.

## Important APIs, Types, And Functions
`SET_DUMP_PARAMS` stores target fileset identity, dump filename, whether the dump is limited by date, and the selected `SYSTEMTIME`. `Filesets_Dump(LPIDENT lpi)` opens the dialog.

## Control Flow
The implementation fills the struct and transfers it to `taskSET_DUMP` on OK.

## State And Persistence
The struct is transient runtime state and has no persistence.

## Dependencies And Integration Points
It depends on `LPIDENT`, `TCHAR`, `MAX_PATH`, and Win32 `SYSTEMTIME`. The task layer consumes this struct.

## Risks And Test Signals
Risks include filename truncation and local-time interpretation. Compile coverage and dump task parameter tests validate it.
