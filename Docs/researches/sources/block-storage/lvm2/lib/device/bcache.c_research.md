# File Research: sources/block-storage/lvm2/lib/device/bcache.c

## Purpose
Implements LVM2's block cache and IO-engine abstraction for block device reads/writes. It supports asynchronous Linux AIO and synchronous IO engines, page-aligned cache blocks, dirty writeback, prefetch, invalidation, fd indirection, and write clamping near a configured last byte.

## IO Engines
The async engine uses `io_setup`, `io_submit`, and `io_getevents` with a fixed control-block pool. It tracks the PID that created the AIO context and skips `io_destroy()` after fork in a different process. It requires page-aligned data.

The sync engine uses `lseek`, `read`, and `write`, queues completed contexts on a list, and reports completion through the same `wait()` callback interface.

Both engines support last-byte write limiting through `_last_byte_di`, `_last_byte_offset`, and `_last_byte_sector_size`, reducing writes that would otherwise pass a caller-defined device boundary.

## Cache Data Structures
`struct bcache` stores cache geometry, engine pointer, raw aligned data, block descriptors, free/clean/dirty/errored/io-pending lists, a radix-tree index keyed by packed `(di, block_address)`, lock/dirty/io counters, and hit/miss statistics.

`struct block` exposes `di`, `index`, and `data` to clients, while internally tracking list linkage, flags, refcount, error state, and IO direction.

## Core Behavior
`bcache_create()` validates block size and cache size, creates the radix index, allocates aligned data buffers, initializes free block descriptors, and creates a global fd table.

`bcache_get()` looks up or reads a block, rejects concurrent dirty/zero access to an already referenced block, waits for pending IO when necessary, optionally zeroes the block, marks dirty for write access, and increments lock/ref counters.

`bcache_put()` decrements the reference count and triggers preemptive writeback when dirty pressure crosses thresholds.

`bcache_flush()` retries errored dirty blocks, writes back all available dirty blocks, waits for IO completion, and returns false if dirty writes still failed.

`bcache_invalidate()` writes back a dirty block before recycling it unless the block is still held. `bcache_invalidate_di()` writes back and then invalidates all blocks for one descriptor using radix-prefix iteration. `bcache_abort_di()` discards cached blocks for a descriptor and treats held blocks as fatal.

The fd table maps small device indexes (`di`) to actual file descriptors and can grow in 1024-entry increments.

## Integration
Used by device IO and label scanning paths that want cached block reads across many devices. It depends on the radix tree, libdevmapper lists, LVM logging, signal handling, and Linux AIO when available.

## Risk Notes
- The fd table and last-byte globals are process-global, so the cache is not designed for independent concurrent instances.
- Concurrent access is not protected by locks.
- Dirty writeback skips held blocks; flush can fail while clients still hold dirty blocks.
- Sync IO has commented-out failure return on short reads/writes, so short IO can still be reported as successful through the wait path.
- Async completion accepts short reads of at least one sector as success.
- `create_async_io_engine()` leaks the AIO context if control-block allocation fails after `io_setup()`.
- `bcache_invalidate_di()` depends on radix prefix iteration behavior over packed keys.
