# File Research: sources/cow-pools/openzfs/module/zfs/zfs_vnops.c

## Summary
Implements common ZPL vnode operations for syncing, access checks, hole/data seeking, reads, writes, rewrites, ACL get/set, ZIL write-data capture, direct I/O alignment reporting, block cloning, and clone replay.

## Main Responsibilities
- Commit ZIL records for fsync and sync-required reads/writes.
- Enforce access checks through ZFS ACL helpers.
- Implement `SEEK_HOLE` / `SEEK_DATA`.
- Set up buffered, uncached, or direct I/O according to flags, dataset policy, alignment, mmap state, and tunables.
- Perform chunked reads and writes under range locks with quota checks, timestamp updates, page-cache synchronization, SA updates, and ZIL logging.
- Rewrite existing data blocks physically or logically for maintenance operations.
- Provide ACL get/set wrappers.
- Supply write data to the ZIL for immediate and indirect write records.
- Implement block cloning and clone-range replay.

## Key APIs
- `zfs_fsync()`, `zfs_access()`, `zfs_holey()`.
- `zfs_read()`, `zfs_write()`.
- `zfs_rewrite()`.
- `zfs_getsecattr()`, `zfs_setsecattr()`.
- `zfs_get_direct_alignment()`.
- `zfs_get_data()`.
- `zfs_clone_range()`, `zfs_clone_range_replay()`.

## Important Behavior
`zfs_setup_direct()` is the central direct-I/O gate. It may force `O_DIRECT` from the dataset property, fall back to uncached ARC I/O when direct I/O is disabled or the range is mmaped, reject misaligned explicit direct I/O when strict mode is set, skip direct I/O for short writes, and pin/map pages for true direct I/O.

`zfs_read()` rejects quarantined files and directories, handles EOF and `FRSYNC`, locks the read range, reads in bounded chunks, chooses mapped-read versus DMU read paths based on cached page state, and falls back from direct I/O to ARC reads after checksum verification failures or trailing unaligned EOF reads.

`zfs_write()` validates readonly/immutable/append-only state, handles append range locking, applies file-size limits, checks user/group/project block quotas for each chunk, grows block size under a whole-file range lock when required, writes via DMU or pre-borrowed ARC buffers, updates mapped pages after races with mmap, clears setid bits when policy requires, updates size and timestamps, logs `TX_WRITE`, and commits when sync flags or sync=always require it.

`zfs_get_data()` is the ZIL get-data callback. Immediate records read data under a reader range lock. Indirect records lock a full block, recheck block size, hold the dbuf, and either record an already-completed direct-I/O block pointer or call `dmu_sync()`. `EALREADY` converts the log record to `TX_WRITE2`.

`zfs_clone_range()` validates same-pool and block-cloning feature state, encryption compatibility, optional strict dataset property matching, quarantine/readonly/immutable state, non-overlap for same-file clones, block alignment, fsize limits, dirty-source behavior, and block-size compatibility. It locks source as reader and destination as writer in a predictable order, reads L0 block pointers, clones through BRT, updates mapped destination pages, timestamps, size, setid bits, and logs `TX_CLONE_RANGE` in chunks that fit ZIL records.

`zfs_clone_range_replay()` replays logged clone records without access to the source znode by using the logged block pointers directly, growing the destination block size when needed and marking replay progress with `zil_replaying()`.

## Dependencies
This file ties together range locks, DMU reads/writes/sync/clone APIs, ARC buffers, page-cache integration, ZIL logging, SA bulk updates, quota checks, BRT block references, dataset properties, encryption-key comparison, and platform idmap/vnode behavior.

## Risks
The read/write paths are sensitive to races among direct I/O, mmap/page-cache state, range locks, and block-size growth. Clone validation has many feature and property constraints; returning partial progress is intentional and callers must honor the updated offsets/length. ZIL get-data runs while syncing is constrained, so it uses asynchronous znode release and callback-driven cleanup.
