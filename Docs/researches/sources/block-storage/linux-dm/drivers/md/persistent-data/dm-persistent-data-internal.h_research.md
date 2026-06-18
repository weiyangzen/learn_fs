# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-persistent-data-internal.h

## Purpose
Tiny internal utility header for persistent-data implementation files.

## Main Definition
- `dm_hash_block(dm_block_t b, unsigned hash_mask)`: hashes a metadata block number by multiplying the low unsigned portion by a large prime and applying the provided mask.

## Role in Repository
Used by transaction-manager shadow tables and space-map index-entry cache hashing. It is intentionally private to the persistent-data implementation.
