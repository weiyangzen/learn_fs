<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h

## Purpose
Declares the block manager API used by the persistent-data library. It abstracts cached metadata block access, validation, locking, flushing, and checksum support over a block device.

## Important APIs, Types, And Functions
`dm_block_t` is a 64-bit metadata block number. `struct dm_block` and `struct dm_block_manager` are opaque. `dm_block_location()` and `dm_block_data()` expose a locked block's location and memory.

`struct dm_block_validator` names a metadata format and supplies `prepare_for_write()` plus `check()` callbacks. Lock APIs include `dm_bm_read_lock()`, `dm_bm_write_lock()`, `dm_bm_read_try_lock()`, `dm_bm_write_lock_zero()`, and `dm_bm_unlock()`. Lifecycle and state APIs include create/destroy/reset, block-size/device-size queries, flush, prefetch, read-only toggles, and `dm_bm_checksum()`.

## Control Flow
Callers create a manager for a block device and metadata block size, lock blocks with a validator, inspect or modify the returned memory, unlock, then flush at transaction boundaries. `dm_bm_write_lock_zero()` is the preferred path when a caller will overwrite a whole block and wants to avoid a disk read.

## State And Persistence
The API contract states that write-locked memory will be written back sometime after unlock and that superblock-style callers can flush dirty metadata before committing a final root block. Validator consistency persists through cached block lifetime.

## Dependencies And Integration Points
The header depends on Linux types and block-device structures. It is the base layer for the transaction manager, btree, arrays, and space maps.

## Risks
The most common API risks are forgetting to unlock, using inconsistent validators, relying on data in a block after unlock, and writing partially initialized data after `dm_bm_write_lock_zero()`. Read-only mode prevents writes and flushes but cannot prevent misuse of already-returned pointers.

## Test Signals
Header-contract tests should ensure every lock path unlocks correctly, validator failures propagate, write-zero blocks are fully initialized by callers, and flush is called in transaction commit sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h -->
