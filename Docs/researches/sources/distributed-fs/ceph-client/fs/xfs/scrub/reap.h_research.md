# sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.h

## Purpose
`reap.h` declares the block disposal APIs used by online repair after rebuilding metadata and defines the buffer-cache scan context used to find incore buffers over old extents.

## Important APIs, Types, And Functions
It declares reaping functions for AG block bitmaps, fsblock bitmaps, inode forks, metadata-directory fsblocks, and realtime block bitmaps. `struct xrep_bufscan` tracks a disk address, maximum scan length, step size, and internal sector count. `xrep_bufscan_max_sectors` and `xrep_bufscan_advance` drive buffer-cache scanning.

## Control Flow
Callers choose the reaping API matching the coordinate space of their old metadata: AG blocks, fsblocks, realtime blocks, metadir blocks, or file fork mappings. Realtime reaping returns `-EOPNOTSUPP` when realtime support is not compiled.

## State And Persistence Behavior
The header itself has no persistence. The declared functions persistently mutate allocation, rmap, bmap, refcount, and quota metadata through transactions.

## Dependencies And Integration Points
It depends on scrub context, bitmap types, owner info, AG reservation types, inode types, and mount/block address types. It is used throughout repair modules that replace old metadata structures.

## Risks And Edge Cases
Callers must pass the correct owner info and bitmap coordinate type; mixing them could free or unmap the wrong metadata. Realtime callers must handle the stubbed unsupported case.

## Test Signals
Compile both realtime and non-realtime configurations, and test each public reaping API with empty and non-empty bitmaps plus buffer scan progression.
