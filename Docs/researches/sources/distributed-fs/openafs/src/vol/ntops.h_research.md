# sources/distributed-fs/openafs/src/vol/ntops.h

## Purpose
Declares the Windows NT volume-layer file-operation API and NT-specific inode formatting helpers used by NAMEI and partition code.

## Important APIs, Types, And Functions
The header defines `VALID_INO` for Windows builds, `AFS_INO_STR_LENGTH`, and `afs_ino_str_t`. It declares `PrintInode`, all `nt_*` file wrappers, and `nt_DevToDrive`/`nt_DriveToDev`. `nt_fdopen` is declared here as part of the file abstraction, although its implementation may be supplied by the handle layer rather than this file.

## Control Flow
There is no direct control flow. Callers use these declarations behind OpenAFS `OS_*`, `FDH_*`, and `IH_*` abstractions to keep volume code mostly platform-neutral.

## State And Persistence
The header owns no state. Its type and prototype definitions determine how persistent NTFS handles and encoded NAMEI files are manipulated.

## Dependencies And Integration Points
It requires Windows `FILETIME`, OpenAFS `FD_t`, `Inode`, `IHandle_t`, and AFS size/offset types to be available from surrounding includes. It is paired with `ntops.c` and used by NAMEI, partition, and volume modules under `AFS_NT40_ENV`.

## Risks And Test Signals
Risks are prototype drift, missing `AFS_NT40_ENV` guards in consumers, and ABI assumptions around `HANDLE`-typed `FD_t`. Windows build coverage and targeted file-operation tests are the relevant signals.
