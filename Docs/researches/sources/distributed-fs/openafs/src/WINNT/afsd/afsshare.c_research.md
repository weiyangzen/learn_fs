# sources/distributed-fs/openafs/src/WINNT/afsd/afsshare.c

## Purpose
`afsshare.c` implements the `afsshare.exe` utility for creating, updating, or deleting OpenAFS Windows submount registry entries. A submount maps a short share-like name to an AFS mount path relative to the configured mount root when possible.

## Important APIs And Control Flow
`main` accepts `afsshare.exe <submount> [<afs mount path>]`. With only a submount argument, it deletes that value from `HKLM\<OpenAFS>\Submounts`. With a path argument, it reads `MountRoot` from the AFSD service parameters, strips that prefix from the requested AFS path if present, and writes the resulting string as a `REG_EXPAND_SZ` value named by the submount. Registry opens use `KEY_WOW64_64KEY` when running under WOW64, via `IsWow64()`.

## State And Persistence
All persistent state is in HKLM OpenAFS registry keys. The tool writes nonvolatile submount values and reads the service `MountRoot`, defaulting to `/afs` when the setting is unavailable. It does not contact the cache manager or validate that the target AFS path exists.

## Dependencies, Risks, And Test Signals
The utility depends on Windows registry APIs, OpenAFS registry path macros, and administrator permissions to modify HKLM. Risks include accepting arbitrary submount/value names, no path validation, and behavior differences under 32-bit processes on 64-bit Windows if WOW64 redirection is wrong. Test signals include argument count errors, deletion success/failure codes, setting a path under and outside `MountRoot`, missing `MountRoot` fallback, access denied handling, and 32-bit/64-bit registry view behavior.
