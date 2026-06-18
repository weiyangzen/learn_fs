# sources/distributed-fs/ceph-client/drivers/md/raid10.h

## Purpose
`raid10.h` defines the private data structures and state flags shared by the MD RAID10 implementation. It captures the array geometry, mirror slots, per-array runtime state, per-I/O request state, and the concurrency rules for accessing removable member devices.

## Important APIs, Types, and Functions
`struct raid10_info` represents one logical mirror position and stores a primary `rdev`, an optional `replacement`, and a head-position estimate used by read balancing. `struct r10conf` stores the owning `mddev`, mirror arrays for current/new/old layouts, device lock, current and previous `struct geom`, copy count, device-sector calculations, reshape progress/safety state, retry and endio lists, pending write list, resync barrier counters, mempools, bioset, temporary page, daemon thread pointer, and clustered resync range. The embedded `struct geom` describes `raid_disks`, `near_copies`, `far_copies`, `far_offset`, `stride`, `far_set_size`, `chunk_shift`, and `chunk_mask`.

`struct r10bio` is the private request object used for normal I/O, resync, recovery, reshape, and discard. It records completion count, virtual sector, sector count, state bits, owning `mddev`, original `master_bio`, read slot, retry list node, and a flexible array of mapped per-copy `struct r10dev` entries. Each `r10dev` can hold a cloned bio plus either a replacement bio for writes/resync or the selected rdev for reads. `enum r10bio_state` defines flags such as `R10BIO_Uptodate`, `R10BIO_IsSync`, `R10BIO_IsRecover`, `R10BIO_IsReshape`, `R10BIO_ReadError`, `R10BIO_Returned`, `R10BIO_MadeGood`, `R10BIO_WriteError`, `R10BIO_Previous`, `R10BIO_FailFast`, and `R10BIO_Discard`.

## Control Flow
The header has no executable code, but it defines the objects that `raid10.c` allocates, fills, passes to endio callbacks, queues on daemon retry lists, and uses to translate between logical and physical sectors. Normal request flow allocates an `r10bio` from `r10bio_pool`, fills `devs[]` through geometry mapping, and frees it when the master bio completes. Resync and recovery allocate larger `r10bio` objects from `r10buf_pool` so each mapped device has preallocated bios and pages.

## State and Persistence Behavior
The header describes volatile in-memory state. Persistent state is referenced indirectly through `mddev`, `md_rdev`, rdev flags, recovery offsets, bad-block records, and MD superblock fields. The leading comment is an important persistence and lifetime contract: `raid10_info.rdev` may be set to `NULL` asynchronously by disk removal, and safe access requires `mddev->reconfig_mutex`, a known resync/recovery/reshape context, or RCU lookup plus incrementing `rdev->nr_pending`.

## Dependencies and Integration Points
The declarations depend on MD core types (`struct mddev`, `struct md_rdev`, `struct md_thread`), block-layer `struct bio`, Linux synchronization primitives, mempools, biosets, wait queues, and list heads. The header is private to the MD RAID10 personality and is included by `raid10.c`, which also includes common RAID1/RAID10 helper code.

## Risks and Edge Cases
The flexible `devs[]` sizing must match the active geometry or endio lookup and memory-pool freeing can walk invalid entries. The union inside `struct r10dev` changes meaning between read and write/resync paths, so callers must honor `read_slot` and state bits. `R10BIO_Previous` is critical during reshape because it determines whether device addresses use old or new data offsets. Incorrect rdev lifetime handling can race hot-remove and lead to use-after-free or stalled removal.

## Test Signals
Compile coverage should validate all users of `struct r10conf`, `struct r10bio`, and `enum r10bio_state`. Runtime signals come from the `raid10.c` paths that allocate/free mempools, hot-remove devices while I/O is active, run replacement recovery, retry read/write errors, and reshape while normal I/O is crossing old/new geometry boundaries.
