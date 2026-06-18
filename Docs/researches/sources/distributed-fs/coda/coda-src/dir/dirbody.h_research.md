# sources/distributed-fs/coda/coda-src/dir/dirbody.h

## Purpose
Private directory-body layout and function declarations for the Coda directory implementation.

## APIs, Types, and Functions
Defines page/blob constants `LOGPS`, `NHASH`, `EPP`, `LEPP`, `ESZ`, `LESZ`, `DHE`, and `FFIRST`. Defines `DirBlob`, `PageHeader`, and `DirHeader`. Declares `DIR_rvm()`, `DIR_IsEmpty()`, `DIR_Free()`, `DirHash()`, `DirToNetBuf()`, `DIR_MakeDir()`, `DIR_LookupByFid()`, `DIR_Lookup()`, `DIR_EnumerateDir()`, `DIR_Create()`, `DIR_Length()`, `DIR_Delete()`, `DIR_PrintChain()`, `DIR_Hash()`, `DIR_DirOK()`, `DIR_Convert()`, and `DIR_Setpages()`.

## Control Flow, State, and Persistence
No control flow. The structs define the persistent in-memory/RVM representation: a first page containing page header, allocation map, and hash table, followed by additional pages of blob slots.

## Dependencies and Integration
Used by `dirbody.c`, `codadir.c`, and tests. It relies on `DIR_MAXPAGES`, `PDirHeader`, `DirEntry`, `DirFid`, and Coda FID/volume types from `codadir.h`.

## Risks and Test Signals
Risks include layout compatibility sensitivity, magic constants tied to 2 KB pages and 32-byte blobs, and stale legacy declarations. Test signals are binary layout stability and successful `DIR_DirOK()` validation of directories made by current code.
