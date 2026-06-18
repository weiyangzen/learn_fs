# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.c

## Purpose
Block cache, lock, validation, and checksum layer for persistent metadata. It wraps `dm-bufio` behind `struct dm_block_manager` and exposes `struct dm_block` without leaking bufio internals.

## Main Structures
- Optional debug-only `struct block_lock`: detects recursive metadata lock acquisition and limits concurrent holders.
- `struct buffer_aux`: per-buffer auxiliary state storing the current validator, write-lock flag, and optional debug lock.
- `struct dm_block_manager`: wraps a `dm_bufio_client` and read-only state.

## Important Behavior
- `dm_block_location()` and `dm_block_data()` map an opaque `dm_block` to its bufio block number and data pointer.
- Block validators are sticky per cached buffer. Re-locking a cached block with a different validator returns `-EINVAL`.
- `dm_bm_read_lock()` reads through bufio, optionally takes a debug read lock, validates the buffer, and returns the block.
- `dm_bm_write_lock()` refuses writes in read-only mode, reads the existing block, takes a write lock, validates it, and returns mutable data.
- `dm_bm_write_lock_zero()` creates/zeros a block without reading it and sets the validator directly.
- `dm_bm_unlock()` marks write-locked buffers dirty before releasing them.
- `dm_bm_flush()` writes dirty buffers unless the manager is read-only.
- `dm_bm_checksum()` is CRC32C seeded with all ones and XORed with caller-provided salt.

## Debug Locking
When `CONFIG_DM_DEBUG_BLOCK_MANAGER_LOCKING` is enabled:
- Recursive locking by the same task is detected.
- Optional stack tracing can report the prior acquisition site.
- Writers are prioritized.
- `dm_bm_read_try_lock()` can return `-EWOULDBLOCK`.

## Exports and Module Metadata
Exports the block-manager API and declares GPL module metadata for the immutable metadata library.
