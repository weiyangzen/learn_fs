# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_remove.c

## Purpose
Implements file removal, local directory cache updates, disconnected remove logging, and final deletion of silly-renamed open files.

## Important APIs, Types, and Functions
`afs_remove` is the vnode remove entry. `afsremove` performs the connected `RXAFS_RemoveFile` call or disconnected local removal and updates the parent dcache. `afs_newname` creates a hidden `.__afs` silly-rename target for open unlinked files. `afs_remunlink` removes that silly name after the last reference is gone. `FetchWholeEnchilada` fetches all chunks before unlinking an active file, and `DemoteSmushedVCache` moves flushed vcaches to the VLRU tail.

## Control Flow and State
`afs_remove` creates a request, fakestats the parent, rejects dynroot mount writes and readonly/offline-without-disconnected-RW cases, verifies the parent, gets the directory dcache, locks the parent and dcache, ensures freshness, and finds the target vcache through DNLC or directory lookup. In disconnected RW mode it shadows the parent directory and records `VDisconRemove`, unless the target was locally created. Active open files are fetched whole, then either silly-renamed with `afsrename` or removed with `afsremove`. `afsremove` removes DNLC entries, performs the fileserver RPC when connected, applies `afs_LocalHero` or local disconnected directory deletion, decrements link counts, smushes inactive last-link files, and demotes smushed vcaches.

Connected removes synchronously persist via fileserver RPC. Local dcache directory entries are deleted when server status proves the cached directory version advanced as expected. Disconnected removes mutate shadow directories and dirty flags for later replay. Open unlinked files store `mvid.silly_name`, `uncred`, `CUnlinked`, and sometimes `CUnlinkedDel` until `afs_remunlink` performs final removal.

## Dependencies and Integration Points
Depends on `afsrename` from rename handling, directory package deletion, DNLC removal, dcache/vcache locks, fileserver `RXAFS_RemoveFile`, `afs_Analyze`, disconnected dirty queues, shadow directory helpers, credential refcounting, active-vnode checks, and cache smushing.

## Risks and Test Signals
Lock ordering is delicate, especially disconnected mode where target vcache locks are obtained while parent locks are held. If a fileserver RPC returns a negative/network error, the parent is marked stale because server state may be ambiguous. `afs_newname` uses a 16-bit random suffix, so rare collisions rely on rename failure handling. Silly-rename cleanup may be called with an unheld vcache and uses nonblocking locks.

Test ordinary removes, active open file removes, inactive last-link files, DNLC hit and miss targets, readonly directories, disconnected non-RW and RW modes, locally-created disconnected files, silly rename collision/failure, final `afs_remunlink`, NFS translator behavior, and server/network errors that should stale parent cache state.
