# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.h

## Purpose
Solaris inode metadata macros for OpenAFS inode-based server/cache support.

## Important APIs, Types, and Functions
Defines `BAD_IGET`, `VICEMAGIC`, vice field accessors for disk and in-core inodes, `IS_VICEMAGIC`, `IS_DVICEMAGIC`, `CLEAR_VICEMAGIC`, `CLEAR_DVICEMAGIC`, and cache FS type constants `AFS_SUN_UFS_CACHE` and optional `AFS_SUN_VXFS_CACHE`.

## Control Flow
No runtime control flow; all behavior is macro expansion.

## State and Persistence
Macros read and write persistent inode fields repurposed for OpenAFS vice metadata and magic markers.

## Dependencies and Integration Points
Used by `SOLARIS/osi_inode.c` and `SOLARIS/osi_file.c`. Depends on Solaris UFS inode member names and compile-time VXFS availability.

## Risks
Repurposing inode uid/gid/gen/flags fields is tightly coupled to UFS layouts. A structure change can corrupt metadata or make `IS_VICEMAGIC` unreliable.

## Test Signals
Compile against target Solaris UFS headers, create and inspect VICEMAGIC inodes, clear magic on link-count zero, and validate salvager/server interpretation of vice fields.
