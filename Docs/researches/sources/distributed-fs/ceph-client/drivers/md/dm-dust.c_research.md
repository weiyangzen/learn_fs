# `sources/distributed-fs/ceph-client/drivers/md/dm-dust.c`

## Purpose

`dm-dust.c` implements the `dust` test target, which emulates media read errors for selected logical blocks and optional transient write failures. It is designed for fault-injection tests that need deterministic bad-block behavior above a normal block device.

## Important APIs, Types, and Functions

Bad blocks are represented by `struct badblock`, keyed by block number in an RB tree and carrying a remaining write-fail count. `struct dust_device` stores the backing `dm_dev`, RB tree root, badblock count, lock, configured block size and sector shift, starting offset, and mode flags. `dust_ctr()` parses `<device_path> <offset> <blksz>`, validates a power-of-two block size, opens the backing device, initializes the badblock tree, and caps target max IO length to one dust block. `dust_map()` remaps the bio and dispatches to `dust_map_read()` or `dust_map_write()`. Runtime control is via `dust_message()` with commands such as `addbadblock`, `removebadblock`, `queryblock`, `countbadblocks`, `clearbadblocks`, `listbadblocks`, `enable`, `disable`, and `quiet`.

## Control Flow

Reads are only failed when `fail_read_on_bb` is enabled. The sector is converted to dust block number, the badblock tree is searched under `dust_lock`, and matching reads return `DM_MAPIO_KILL`. Writes to a bad block either decrement `wr_fail_cnt` and fail while the count remains positive, or remove the block from the badblock tree and remap normally. Messages mutate or query the RB tree while holding the spinlock, except bulk clear swaps the tree out under lock and frees it outside the critical section.

## State and Persistence Behavior

Bad-block state is entirely in memory and is lost when the mapping is destroyed. There is no on-disk metadata. The backing device receives normal remapped IO for non-failed operations, and successful writes can clear a badblock entry.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.message`, `.status`, `.prepare_ioctl`, and `.iterate_devices`. It uses Linux RB trees, device-mapper messages, `dm_set_target_max_io_len()`, and block ioctl forwarding when the mapping covers the full lower device exactly.

## Risks and Edge Cases

Block-range validation checks `block > size`, which means a block equal to the computed count is accepted even though valid zero-based block indexes normally end at `size - 1`; boundary tests should verify intended semantics. The free path relies on `struct rb_node` being the first field of `struct badblock`, so `kfree(node)` works by layout. Quiet mode suppresses many diagnostics, which can hide command mistakes in tests. The target serializes all tree access with a spinlock, so list output can hold the lock while emitting potentially many lines.

## Test Signals

Tests should create bad blocks, enable/disable read failure, verify read kill versus bypass, verify write-fail counters, verify successful writes remove bad blocks, exercise query/list/count/clear messages, test boundary block numbers, and confirm table/status output round-trips. Ioctl forwarding should be checked for full-size and offset mappings.
