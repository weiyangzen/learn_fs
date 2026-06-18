# sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.h

## Purpose
Defines Darwin-specific inode metadata macros used by OpenAFS server/salvager-style inode code and cache compatibility paths.

## Important APIs, Types, And Functions
The header defines `BAD_IGET`, Darwin `VICEMAGIC`, `DI_VICEP3`, `I_VICEP3`, mappings from inode/dinode fields to OpenAFS vice fields, and `IS_*`, `CLEAR_*` magic macros.

## Control Flow
There is no executable control flow. Code includes this header to read, test, or clear OpenAFS magic metadata in UFS-like inode structures.

## State And Persistence
State is persisted in host inode or dinode fields such as flags, generation, uid, gid, and spare slots. The macros encode how OpenAFS overlays vice metadata onto those fields.

## Dependencies And Integration Points
Depends on Darwin inode/dinode layouts used by older cache/server code. It is included by `osi_inode.c` and related cache-file code.

## Risks
The field aliases are only valid for the expected filesystem structure layout. Using them with APFS or incompatible Darwin UFS/HFS internals would read or modify unrelated metadata.

## Test Signals
Builds using legacy inode access should compile against the expected kernel headers. Salvager or cache compatibility tests should verify vice magic detection and clearing on known test inodes.
