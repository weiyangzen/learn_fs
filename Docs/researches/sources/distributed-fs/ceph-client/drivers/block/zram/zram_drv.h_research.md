# Research: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.h

## Purpose

`zram_drv.h` defines the shared data model, constants, and optional feature fields used by `zram_drv.c` and related zram compressor code. It is intentionally compact because zram maintains one table entry per logical page, so memory overhead in this header directly affects the device footprint.

## Important APIs, Types, And Functions

The file defines page and sector geometry constants: `SECTORS_PER_PAGE`, `ZRAM_LOGICAL_BLOCK_SIZE`, and `ZRAM_SECTOR_PER_LOGICAL_BLOCK`. `ZRAM_FLAG_SHIFT` reserves low bits of the packed flags word for compressed object size and high bits for page flags. `ZRAM_COMP_PRIORITY_MASK` reserves two priority bits for multi-compressor selection.

`enum zram_pageflags` enumerates all per-slot flags: same-filled page, entry lock bit, writeback marker, post-processing marker, huge/incompressible markers, idle marker, and compressor priority bits. `struct zram_table_entry` stores a zsmalloc or backing-device handle and a union containing either the bit lock word or packed attributes, plus a `lockdep_map`. When access-time tracking is enabled, `attr.ac_time` is stored beside flags.

`struct zram_stats` contains atomic counters for compressed bytes, failed reads/writes, free notifications, same/huge page counts, stored pages, max zsmalloc pages, missed slot-free notifications, and optional backing-device reads/writes/count. `struct zram` is the device object: it owns the slot table, zsmalloc pool, compressor instances and parameters, gendisk, device rwsem, memory limit, stats, disk size, configured algorithm names, reset claim flag, and optional writeback/debugfs state.

## Control Flow

This header does not execute code, but it shapes all control flow in `zram_drv.c`. The packed entry layout lets I/O paths lock one slot at a time with a bit lock, inspect flags, and decide whether data is same-filled, compressed in zsmalloc, incompressible in zsmalloc, or written back to a backing block. The compressor arrays are indexed by `ZRAM_PRIMARY_COMP`, `ZRAM_SECONDARY_COMP`, and up to `ZRAM_MAX_COMPS`, with those values changing depending on `CONFIG_ZRAM_MULTI_COMP`.

## State And Persistence

All state described here is runtime state. The only persistent-looking reference is the optional backing device handle in `struct zram`, but the zram metadata that maps slots to backing blocks is in memory and is discarded on reset/removal. The `claim` flag is protected by `disk->open_mutex`; the rest of the mutable device fields are primarily guarded by `dev_lock` and per-slot bit locks.

## Dependencies And Integration Points

The header depends on `linux/rwsem.h`, `linux/zsmalloc.h`, and local `zcomp.h`. It exposes types that integrate with the block layer (`gendisk`, `block_device`), file and backing-device APIs (`struct file`, `struct block_device`), debugfs (`struct dentry`), compressor parameter APIs (`struct zcomp_params`), and atomic stats APIs.

## Risks

The packed flags field is size-sensitive. Adding flags without respecting the `BUILD_BUG_ON` in the implementation can overflow `u32 flags`, and changing `ZRAM_FLAG_SHIFT` affects the maximum storable object size. The union that overlays `__lock` and `attr` is delicate: slot locking helpers must keep using the designated lock bit and avoid corrupting packed attributes. Optional fields under writeback and memory tracking create ABI-dependent structure layouts, so code must keep feature guards consistent between declarations and use sites.

## Test Signals

Build coverage should include configurations with and without `CONFIG_ZRAM_MULTI_COMP`, `CONFIG_ZRAM_WRITEBACK`, `CONFIG_ZRAM_MEMORY_TRACKING`, and `CONFIG_ZRAM_TRACK_ENTRY_ACTIME`. Runtime signals include correct sysfs exposure of optional attributes, valid per-slot debugfs flags, stable stats after resets, and successful compression/recompression with priority bits preserved.
