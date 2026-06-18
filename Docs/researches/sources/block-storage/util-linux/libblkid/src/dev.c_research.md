# File Research: sources/block-storage/util-linux/libblkid/src/dev.c

## Purpose
Manages high-level cached device objects and public cache-device iteration.

## Main Components
- `blkid_new_dev()` allocates a device and initializes list heads.
- `blkid_free_dev()` removes the device from the cache list, frees all associated tags, application/canonical names, and the device object.
- `blkid_dev_devname()` returns the application-provided name when present, otherwise the canonical cache name.
- `blkid_debug_dump_dev()` prints device fields and tags for debugging.
- `blkid_dev_iterate_begin()` creates an iterator over cache devices.
- `blkid_dev_set_search()` configures iterator filtering by tag name/value.
- `blkid_dev_next()` returns the next matching cached device.
- `blkid_dev_iterate_end()` invalidates and frees the iterator.
- `TEST_PROGRAM` main lists cached devices, optionally filtered by tag.

## Dependencies and Interactions
Works with cache lists from `cache.c` and tag APIs from `tag.c`. Device iteration is part of the public high-level cache API declared in `blkid.h.in`.

## Research Notes
The iterator uses a magic number to reject invalid handles. Search filtering delegates to `blkid_dev_has_tag()`, so it is tag-based rather than name-based.
