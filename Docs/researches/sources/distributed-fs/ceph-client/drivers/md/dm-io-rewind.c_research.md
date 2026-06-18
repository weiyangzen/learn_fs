# sources/distributed-fs/ceph-client/drivers/md/dm-io-rewind.c

### Purpose
`dm-io-rewind.c` reconstructs a `dm_io` original bio after partial splitting/advancement. It rewinds the bio iterator, integrity iterator, and inline encryption data unit number so Device Mapper can restore a fixed-end original bio when an I/O segment must be retried or reprocessed.

### Important APIs, Types, And Functions
The main exported-internal entry is `dm_io_rewind(struct dm_io *io, struct bio_set *bs)`. Helpers include `dm_bvec_iter_rewind`, `dm_bio_integrity_rewind`, `dm_bio_crypt_dun_decrement`, `dm_bio_crypt_rewind`, `dm_bio_rewind_iter`, and `dm_bio_rewind`. The implementation is conditional on `CONFIG_BLK_DEV_INTEGRITY` and `CONFIG_BLK_INLINE_ENCRYPTION`.

### Control Flow
`dm_io_rewind` clones `io->orig_bio` using `bio_alloc_clone`, calculates how many bytes the current original bio has advanced relative to `io->sector_offset`, rewinds the clone, trims it to `io->sectors`, chains it to the old original bio, compensates for `bio_chain` incrementing `__bi_remaining`, and replaces `io->orig_bio`.

The data iterator rewind moves `bi_sector` backward and either increases size for no-advance bios or walks backward through the bvec array, restoring `bi_idx` and `bi_bvec_done`. If integrity metadata is present, `dm_bio_integrity_rewind` converts completed data sectors to integrity intervals/bytes and rewinds `bip_iter`. If inline encryption is present, `dm_bio_crypt_rewind` decrements the DUN as a multi-limb integer by the number of completed encryption data units.

### State And Persistence Behavior
There is no persistent state. Runtime mutation is limited to the cloned bio's `bi_iter`, optional `bio_integrity_payload` iterator, optional `bio_crypt_ctx` DUN array, chaining state, and `io->orig_bio`. The original bio's completion reference count is adjusted after chaining.

### Dependencies And Integration Points
This file depends on block bio vectors, block integrity helpers, inline encryption context, and `dm-core.h`'s `struct dm_io`. It is tightly coupled to DM bio splitting because the caller must provide a bio with a fixed end sector and must restore size separately.

### Risks And Edge Cases
The core risk is rewinding beyond the beginning of the bvec array; this is guarded by `WARN_ONCE` and returns false internally, but `dm_bio_rewind` does not propagate a failure. Inline encryption correctness depends on `bytes` being aligned to the crypto data-unit size. Integrity rewind correctness depends on the block integrity profile for the target disk. Reference-count compensation around `bio_chain` is subtle and must match `dm_split_and_process_bio` behavior.

### Test Signals
Test with partially completed split bios, bios carrying integrity payloads, bios carrying inline encryption contexts, no-advance bio operations, multi-bvec bios, and boundary cases where rewinding crosses vector boundaries. Fault-injection tests should check warning behavior when invalid byte counts attempt to rewind past the original bvec range.
