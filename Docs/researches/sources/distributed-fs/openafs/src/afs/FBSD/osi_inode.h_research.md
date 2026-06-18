# sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.h

## Purpose
Defines FreeBSD UFS inode/dinode field mappings used to store and inspect OpenAFS vice metadata.

## Important APIs, Types, And Functions
The header defines `BAD_IGET`, FreeBSD `VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, fake inode sizing, mount-list lock macros, aliases for inode and dinode vice fields, inode-number block/cylinder macros (`itoo`, `itog`, `itod`), and magic test/clear macros.

## Control Flow
There is no runtime flow; it is a macro contract.

## State And Persistence
Persistent state is encoded in UFS inode/dinode fields such as spare words, uid/gid, and old id fields. The macros define OpenAFS interpretation of that metadata.

## Dependencies And Integration Points
Depends on FreeBSD UFS `struct inode`, `struct dinode`, filesystem geometry macros, and legacy server/salvager cache code.

## Risks
UFS layout changes or non-UFS cache filesystems invalidate these aliases. Several fields are repurposed from spare or old-id slots, so collisions with filesystem changes are possible.

## Test Signals
Builds against target FreeBSD UFS headers and salvager/cache tests that set, detect, and clear vice magic on controlled inodes.
