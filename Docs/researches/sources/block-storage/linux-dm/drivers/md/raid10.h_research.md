# File Research: sources/block-storage/linux-dm/drivers/md/raid10.h

## Purpose

`raid10.h` defines the private data structures and per-request state bits used by the MD RAID10 personality implemented in `raid10.c`. It is not a standalone API header; it is the contract between RAID10 implementation code, shared RAID1/RAID10 helpers included from `raid1-10.c`, and MD core structures referenced through pointers.

## Structures

`struct raid10_info` represents one mirror slot. It contains:

- `rdev`: the primary MD component device.
- `replacement`: an optional replacement device under recovery.
- `head_position`: an estimated disk-head position for read balancing.
- `recovery_disabled`: a generation marker matching `mddev->recovery_disabled` when this slot should not be recovered.

The opening comment documents the critical concurrency contract for `raid10_info.rdev`: it may be set to `NULL` asynchronously by `raid10_remove_disk()`. Safe access requires either `mddev->reconfig_mutex`, known resync/recovery/reshape context, or RCU lookup followed by incrementing `rdev->nr_pending` before dropping RCU.

`struct r10conf` is the per-array RAID10 configuration. It stores:

- Backpointer to `mddev`.
- Current, old, and newly allocated mirror arrays.
- `device_lock` for mirror/retry state.
- Geometry in `geo` and `prev`, including raid disks, near/far copies, far offset mode, stride, far-set size, chunk shift, and chunk mask.
- Total copy count (`near_copies * far_copies`).
- Device-sector and reshape tracking fields (`dev_sectors`, `reshape_progress`, `reshape_safe`, `reshape_checkpoint`, `offset_diff`).
- Retry and delayed completion lists.
- Pending write bio list and count.
- Barrier/resync counters and wait queue.
- Fullsync and replacement indicators.
- Mempools for normal `r10bio` and resync buffers, temp page, and split bioset.
- A temporary `md_thread` used during takeover before the array fully activates.
- Cluster resync low/high bounds.

`struct r10bio` is the private bio wrapper for normal I/O, sync, recovery, and reshape. It records completion count, virtual sector and length, state bits, start time, `mddev`, original master bio, read slot, retry linkage, and a flexible array of `struct r10dev`.

Each `r10dev` stores a main bio pointer, either a replacement bio or an `rdev` pointer depending on read/write context, a physical address, and a device number. The union is context-sensitive: `repl_bio` is used for writes/resync, while `rdev` is used for reads when `read_slot >= 0`.

## State Bits

`enum r10bio_state` defines flags interpreted by `raid10.c`:

- `R10BIO_Uptodate`: at least one useful I/O completed successfully.
- `R10BIO_IsSync`, `R10BIO_IsRecover`, `R10BIO_IsReshape`: classify background work.
- `R10BIO_Degraded`: write ran with a missing copy.
- `R10BIO_ReadError`: read failed and needs process-context retry.
- `R10BIO_MadeGood`: a write may clear known bad-block records.
- `R10BIO_WriteError`: write failed and needs deferred handling.
- `R10BIO_Previous`: I/O is using previous geometry during reshape.
- `R10BIO_FailFast`: failfast-capable mirrors received failfast requests.
- `R10BIO_Discard`: linked discard request root.

## Dependencies And Integration

The header depends on MD core types (`struct mddev`, `struct md_rdev`, `struct md_thread`), block-layer types (`struct bio`, `struct bio_set`, `struct page`), kernel synchronization primitives, lists, mempools, and wait queues. These are pulled by implementation files before or through Linux kernel headers.

## Notable Invariants

- `r10conf.copies` must match `geo.near_copies * geo.far_copies` and must not exceed `geo.raid_disks`.
- Flexible `r10bio.devs[]` allocation size must match the active geometry for normal I/O, and the resync pool must allocate enough bios/pages for sync/recovery semantics.
- The meaning of `r10dev` union members depends on `read_slot` and operation type; misuse can free or dereference the wrong object.
- `mirrors_old` and `mirrors_new` exist to support reshape table replacement without losing old-layout access.

## Testing Signals

Tests and reviews should focus on RCU-safe `rdev` access, correct `r10bio` allocation sizing across geometry changes, state-bit transitions in retry paths, and replacement/main-device promotion races.
