<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h

## Purpose
`dm-bio-prison-v1.h` declares the original DM bio-prison and deferred-set APIs for targets that need to hold bios on conflicting block ranges.

## Important APIs, Types, And Functions
`struct dm_cell_key` describes virtual/physical ranges. `BIO_PRISON_MAX_RANGE` and shift define valid range limits. `struct dm_bio_prison_cell` exposes a client list, rbtree node, key, holder bio, and detained bios. The header declares prison lifecycle, cell allocation, validation, detain/release/error/visit helpers, and deferred set functions.

## Control Flow
Clients validate keys, provide a cell, call `dm_bio_detain()`, process the holder path if granted, and later release to obtain bios for resubmission/completion. Deferred clients balance entry inc/dec and queue work to run when reads drain.

## State And Persistence
Only runtime prison, cell, and deferred handles are defined. No metadata is persisted.

## Dependencies, Integration Points, Risks, And Test Signals
It includes DM block/thin metadata types, bio, and rbtree headers. Risks include exposed cell layout, range-rule violations, return-value misuse, and unbalanced deferred entries. Test compile coverage, oversized range validation, cell ownership/free rules, and concurrent deferred read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h -->
