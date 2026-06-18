# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_link.c

## Purpose

`afs_vnop_link.c` implements hard-link creation for OpenAFS vnode operations. It validates source and destination compatibility, calls the fileserver `Link` RPC, updates the parent directory dcache when safe, and marks the linked file vcache stale.

## Important APIs, Types, and Functions

The single exported operation is `afs_link`, with argument order varying by platform. It uses `struct vrequest`, parent dcache `tdc`, `OutFidStatus`, `OutDirStatus`, fakestat states for both source and directory, and `RXAFS_Link`.

## Control Flow

`afs_link` creates a request, initializes fakestat state, enters disconnected lock, evaluates source and destination directory fakestat, rejects cross-cell or cross-volume links with `EXDEV`, rejects overlong names, verifies the destination directory, rejects read-only volumes, and rejects all disconnected mode with `ENETDOWN`. It obtains the parent dcache, write-locks the parent, sends `RXAFS_Link`, and on success uses `afs_LocalHero` to decide whether to insert the new name into the parent dcache. It then releases the parent lock, write-locks the source file, and marks it stale because the precise new link count may not be authoritative.

## State and Persistence Behavior

Online hard links persist via fileserver RPC. The parent directory dcache may be updated locally if its data version matches the server response. The source vcache is invalidated so link count/status can be refetched. There is no disconnected-write support for hard links in this implementation.

## Dependencies and Integration Points

It depends on fakestat, vcache verification, disconnected locking, RX connections and `afs_Analyze`, directory dcache functions, `afs_LocalHero`, `afs_StaleVCache`, and `afs_CheckCode`. `uafs_link_r` resolves source and destination and calls this operation.

## Risks and Edge Cases

Hard links are prohibited across cells or volumes. Disconnected mode always fails, unlike create/mkdir/rmdir. The file status response is not trusted for link count because concurrent changes can occur while the file is not locked across the RPC. Parent dcache update failure zaps the cache.

## Test Signals

Test successful hard link, cross-volume `EXDEV`, overlong names, read-only volumes, disconnected failure, parent dcache update success and zap paths, source vcache stale marking, and concurrent link/unlink status refresh.
