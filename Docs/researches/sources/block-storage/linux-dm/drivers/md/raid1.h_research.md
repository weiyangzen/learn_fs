# File Research: sources/block-storage/linux-dm/drivers/md/raid1.h

## Purpose
Defines private RAID1 data structures, barrier bucket constants, per-mirror state, per-array configuration, per-I/O `r1bio` state, and the sector-to-barrier-bucket hash helper.

## Main Interfaces
- Barrier sizing: `BARRIER_UNIT_SECTOR_BITS`, `BARRIER_UNIT_SECTOR_SIZE`, `BARRIER_BUCKETS_NR_BITS`, `BARRIER_BUCKETS_NR`.
- Per mirror: `struct raid1_info`.
- Mempool metadata: `struct pool_info`.
- Per array: `struct r1conf`.
- Per logical I/O: `struct r1bio`.
- State bits: `enum r1bio_state`.
- Helper: `sector_to_idx()`.

## Control Flow
Only `sector_to_idx()` has executable logic; it hashes a sector shifted by the 64 MiB barrier unit size into the fixed number of barrier buckets. All other content is structure and flag definition.

## State And Synchronization
The header documents the safe access rules for `raid1_info.rdev`: hold `mddev->reconfig_mutex`, operate during known resync/recovery context, or use RCU and increment `rdev->nr_pending` before dropping the RCU lock. `r1conf` includes `device_lock`, `resync_lock`, `wait_barrier`, per-bucket atomic arrays, retry lists, pending bio queues, mempools, split bioset, and clustered resync bounds.

## Integration Points
Included by `raid1.c` and dependent on MD core types (`mddev`, `md_rdev`, `md_thread`), block types (`bio`, `bio_set`), kernel synchronization primitives, mempools, pages, atomics, waitqueues, and linked lists.

## Notable Behaviors
- The mirror table is sized for primaries plus replacements; comments explain that `pool_info.raid_disks` is twice the configured RAID1 disk count for the same reason.
- Barrier bucket arrays are sized so each atomic array occupies one page.
- `struct r1bio` ends with a flexible `bios[]` array; comments explicitly prohibit adding fields after it.
- `R1BIO_BehindIO`, `R1BIO_Returned`, `R1BIO_MadeGood`, `R1BIO_WriteError`, and `R1BIO_FailFast` encode important completion and error policy decisions used by `raid1.c`.

## Risks And Review Focus
- Any change to barrier constants affects both normal I/O splitting and sync exclusion granularity.
- Misusing `sector_to_idx()` with a range that crosses a barrier unit can mix accounting for unrelated buckets; `raid1_make_request()` avoids this by splitting at unit boundaries.
- Adding fields after `r1bio->bios[]` would corrupt the contiguous allocation pattern used by the mempool allocator.
- The asynchronous `rdev` access rules are easy to violate and are central to safe hot-remove behavior.
