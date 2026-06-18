# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.h

## Purpose
`posix-gfid-path.h` declares the gfid2path virtual xattr interface for the POSIX translator and defines the supported link-record limit.

## Important APIs, Types, And Functions
- `MAX_GFID2PATH_LINK_SUP` is `500`.
- `posix_is_gfid2path_xattr()` identifies internal gfid2path xattr names.
- `posix_get_gfid2path()` resolves gfid2path metadata into a dict response.

## Control Flow
There is no executable control flow in the header; it exposes detection and retrieval APIs to other POSIX translator code.

## State And Persistence Behavior
The header does not mutate state. Its limit constant defines a cross-file contract for how many gfid2path records should be supported.

## Dependencies And Integration Points
It includes Gluster dict, inode, boolean, and errno compatibility types, and is included by entry operations, gfid-path implementation, and xattr response code.

## Risks And Edge Cases
Producers and consumers must enforce `MAX_GFID2PATH_LINK_SUP` consistently. Callers must pass valid dict and `op_errno` pointers and honor dict ownership rules.

## Test Signals
Compile coverage plus behavior tests around the 500-link limit, gfid2path xattr creation, and virtual xattr retrieval.
