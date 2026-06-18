<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h

## Purpose
`dm-bio-record.h` provides inline helpers for DM targets that need to resubmit a bio after lower layers mutate it.

## Important APIs, Types, And Functions
`struct dm_bio_details` stores `bi_bdev`, `__bi_remaining`, `bi_flags`, `bi_iter`, `bi_end_io`, and optionally `bi_integrity`. `dm_bio_record()` copies these fields from a bio. `dm_bio_restore()` writes them back and resets the atomic remaining count.

## Control Flow
A target records before submission and restores before retry/resubmission. The helpers allocate nothing and return no status.

## State And Persistence
Only caller-owned state is used. No global or persistent state exists.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on `linux/bio.h` and optional block integrity support. Risks include recording only selected mutable fields, block-layer structure drift, integrity pointer handling, and use after bio lifetime ends. Test retry paths with split/advanced bios, changed devices, altered endio callbacks, integrity payloads, and repeated retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h -->
