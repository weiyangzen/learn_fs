# File Research: sources/block-storage/util-linux/libblkid/src/cache.c

## Purpose
Allocates, initializes, persists, garbage-collects, and frees high-level libblkid cache objects.

## Main Components
- `get_default_cache_filename()` selects `/run/blkid/blkid.tab` when `/run` exists, otherwise legacy `/etc/blkid.tab`.
- `blkid_get_cache_filename()` resolves the cache path from `BLKID_FILE`, explicit config, `blkid.conf`, or default.
- `blkid_get_cache()` allocates a cache, initializes device/tag lists, stores the cache filename, and reads existing cache data.
- `blkid_put_cache()` flushes changes, frees all cached devices/tags, frees the low-level probe, filename, and cache object.
- `blkid_gc_cache()` removes entries for missing devices and Linux loop devices with no backing file.
- `TEST_PROGRAM` main exercises cache allocation and probing.

## Dependencies and Interactions
Uses `blkid_read_cache()` and `blkid_flush_cache()` from read/save modules, `blkid_free_dev()`/`blkid_free_tag()` for owned objects, config parsing from `config.c`, and loop-device helpers on Linux.

## Research Notes
Cache file selection prefers an environment override before config. `blkid_put_cache()` always attempts to flush before freeing, so cache mutations are persisted as part of normal cleanup.
