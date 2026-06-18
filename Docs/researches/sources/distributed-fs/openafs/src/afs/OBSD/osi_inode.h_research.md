# sources/distributed-fs/openafs/src/afs/OBSD/osi_inode.h

## Purpose
Placeholder OpenBSD inode interface header.

## Important APIs, Types, and Functions
Defines only include guards and no macros, declarations, or types.

## Control Flow
None.

## State and Persistence
None.

## Dependencies and Integration Points
The empty header lets shared OpenAFS code include a platform `osi_inode.h` without conditional include logic, even though OpenBSD does not implement the inode syscall helpers here.

## Risks
Callers expecting inode helper declarations from this header will not get compile-time prototypes. Its emptiness is intentional only if OpenBSD inode syscalls remain unsupported.

## Test Signals
Compile OpenBSD kernel module paths that include `afs/osi_inode.h`; confirm unsupported inode calls are resolved to stubs elsewhere.
