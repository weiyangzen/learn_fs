<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c

## Purpose
Implements the persistent-data block manager using dm-bufio. It provides cached block reads, write locks, dirty tracking, validation callbacks, read-only mode, prefetch, flush, and optional debug locking for metadata blocks.

## Important APIs, Types, And Functions
`struct dm_block_manager` wraps a `dm_bufio_client` and a read-only flag. `struct dm_block` is intentionally opaque and cast internally to `struct dm_buffer`. `struct buffer_aux` records the validator associated with a cached block and whether the current lock is write-owned; in debug builds it also contains a custom `block_lock`.

Public APIs include `dm_block_manager_create()`, `dm_block_manager_destroy()`, `dm_block_manager_reset()`, `dm_bm_block_size()`, `dm_bm_nr_blocks()`, `dm_bm_read_lock()`, `dm_bm_write_lock()`, `dm_bm_read_try_lock()`, `dm_bm_write_lock_zero()`, `dm_bm_unlock()`, `dm_bm_flush()`, `dm_bm_prefetch()`, read-only toggles, `dm_block_location()`, `dm_block_data()`, and `dm_bm_checksum()`.

Validators are central. `dm_block_manager_write_callback()` calls `prepare_for_write()` before a dirty buffer is written. `dm_bm_validate_buffer()` calls `check()` when a cached buffer first receives a validator and rejects validator mismatches on later use, except that zero-write locks can intentionally set the validator for overwritten blocks.

## Control Flow
Creation allocates the manager and creates a dm-bufio client with auxiliary data callbacks. Read locks call `dm_bufio_read()`, acquire a read block lock in debug builds, validate, and return the block. Write locks are similar but check read-only mode and acquire an exclusive lock. `dm_bm_write_lock_zero()` obtains a new/zeroed buffer with no disk read and sets its validator. Unlock marks write-locked buffers dirty before releasing them. Flush writes dirty buffers through dm-bufio.

The debug `block_lock` implementation detects recursive acquisitions by the same task, limits concurrent readers, gives write waiters priority, and can print stack traces when enabled.

## State And Persistence
Runtime state lives in dm-bufio cache buffers and `buffer_aux` metadata. Persistent behavior comes from validator write callbacks, checksum preparation, block-number stamping by higher layers, dirty marking, and `dm_bm_flush()` forcing dirty metadata to the device. Read-only mode blocks write locks and flushes.

## Dependencies And Integration Points
The file depends on dm-bufio, crc32c, device-mapper logging, Linux slab/module/rwsem/task APIs, and optional stacktrace support. All higher persistent-data structures use this layer through the transaction manager or direct prefetch calls.

## Risks
Validator mismatch is a serious integrity issue because the same block cannot safely be interpreted as two metadata formats. Failing to unlock write blocks leaves dirty buffers unflushed and locks held. Recursive locks can deadlock without debug detection. Read-only mode must be respected by all mutating callers. The checksum helper uses a specific crc32c initialization/xor convention that must match validator implementations.

## Test Signals
Tests should cover checksum validation failures, block-number mismatch failures, write-lock dirty marking, zero-write lock without prior read, read-only `-EPERM`, read try-lock `-EWOULDBLOCK`, recursive-lock debug behavior, prefetch smoke tests, and flush ordering through transaction-manager tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c -->
