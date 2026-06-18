<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h

## Purpose
Provides a tiny internal helper shared by persistent-data components.

## Important APIs, Types, And Functions
`dm_hash_block(dm_block_t b, unsigned int hash_mask)` multiplies the low 32 bits of a metadata block number by a large prime and masks the result. It is used for fixed-size hash tables/caches such as transaction-manager shadow tracking and space-map index-entry caches.

## Control Flow
Callers pass a block number and a mask, usually one less than a power-of-two table size. The helper returns the bucket index.

## State And Persistence
There is no state or persistent format in this header. It affects runtime distribution of block numbers across small hash tables.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t`. It is internal to the persistent-data implementation and not a public dm target API.

## Risks
The helper intentionally casts to `unsigned int`, so high bits of very large block numbers do not affect the hash. That is acceptable for small caches but could create clustering if reused for larger or adversarial tables. The caller must pass a mask appropriate for the table size.

## Test Signals
Basic tests should verify bucket values stay within mask bounds and that caches using this helper handle collisions correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h -->
