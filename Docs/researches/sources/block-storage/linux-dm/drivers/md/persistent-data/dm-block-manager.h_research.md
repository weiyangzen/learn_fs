# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.h

## Purpose
Public block-manager interface for persistent metadata users.

## Main Definitions
- `typedef uint64_t dm_block_t`: metadata block number type.
- Opaque `struct dm_block` and `struct dm_block_manager`.
- `struct dm_block_validator`: caller-supplied validator with `prepare_for_write` and `check` callbacks.

## API Contract
- Multiple readers or one writer may hold a block.
- Validators verify read data and stamp/prepare dirty data before writeback.
- Validator changes are only safe when using `dm_bm_write_lock_zero()`.
- `dm_bm_flush()` ensures dirty metadata reaches disk.
- Read-only mode blocks write lock, zero write lock, and flush.
- `dm_bm_prefetch()` requests cached read-ahead for metadata blocks.

## Exposed Functions
Creation/destruction, block size/device size, read/write/try/zero locks, unlock, flush, prefetch, read-only toggles, and checksum helper.
