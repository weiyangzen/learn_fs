# Group Research: group_1125_lvm2_sources_block_storage_lvm2_lib_datastruct_radix_tree_adaptive__74928108c332

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree-adaptive.c -->
# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree-adaptive.c

## Purpose
Implements LVM2's default radix tree as an adaptive radix tree with compressed prefix nodes and node fanout classes `NODE4`, `NODE16`, `NODE48`, and `NODE256`. It stores byte-string keys mapped to `union radix_value`, supports replacement, unique insert reporting, exact lookup/removal, prefix removal, iteration, debugging validation, and textual dumping.

## Main Data Structures
- `struct radix_tree` owns the root value, total entry count, and optional value destructor callback.
- `struct value` is the tagged union used at every tree position.
- `VALUE_CHAIN` represents a key that is both a complete key and a prefix of longer keys.
- `PREFIX_CHAIN` compresses a run of key bytes before a child.
- `node4`, `node16`, `node48`, and `node256` encode increasing fanout density. `node48` maps byte values through a 256-byte index table into 48 compact value slots.

## Core Behavior
Insertion first finds the longest matching prefix with `_lookup_prefix()`, then `_insert()` mutates the matching node. Inserts into `UNSET` create either a direct value or a compressed prefix chain. Inserts under an existing value create or reuse a `VALUE_CHAIN`. Diverging compressed prefixes are split, and dense nodes grow from 4 to 16 to 48 to 256 entries.

Removal walks exact key bytes, calls the configured destructor for removed values, collapses empty value chains and prefix chains, removes node entries by sliding arrays, and may shrink `NODE256` to `NODE48` or `NODE48` to `NODE16`. Prefix removal frees an entire matching subtree and decrements the global entry count by the number of destroyed values.

Lookup returns direct `VALUE` or the value stored in a `VALUE_CHAIN` when the key ends at that node. Iteration descends from a supplied prefix and calls the visitor for each stored value, but the implementation does not reconstruct keys and passes `NULL, 0` as the key arguments.

## Integration
This file is included by `radix-tree.c` unless `SIMPLE_RADIX_TREE` is defined. Device cache and bcache code use this radix tree heavily for path, devno, DM UUID, and cached-block indexes.

## Risk Notes
- Iteration callback keys are not populated despite the public API discussing ordered key traversal.
- `NODE4` and `NODE16` insertion appends keys rather than sorting them, so traversal order depends on insertion order for these nodes.
- `NODE48` iteration walks compact value slots rather than byte-key order.
- Shrink helpers can fail allocation; callers ignore the boolean result, leaving the larger node intact on failure.
- The data structure is recursive and not internally synchronized.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree-adaptive.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree-simple.c -->
# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree-simple.c

## Purpose
Provides an alternate simple radix-tree implementation selected by `SIMPLE_RADIX_TREE`. It is a ternary-search-tree-like byte trie: each node compares one byte and has `left`, `right`, and `center` children.

## Main Data Structures
- `struct node` stores one byte key, left/right alternatives, a center continuation, and an optional value.
- `struct radix_tree` stores the root node, destructor callback, destructor context, and entry count.

## Core Behavior
`radix_tree_insert()` recursively creates nodes along the key path. If a value already exists at the terminal node, the old value is destroyed and replaced; otherwise `nr_entries` is incremented.

`radix_tree_remove()` finds the terminal node, destroys its value, decrements the count, clears `has_value` if children remain, or frees the terminal node if it is a leaf. Parent cleanup is explicitly left as a FIXME.

`radix_tree_remove_prefix()` removes the exact prefix value first, then destroys the subtree reached by that prefix. Lookup uses `_lookup()` on a temporary root pointer and returns the terminal node value when present.

Iteration performs in-order traversal over left, value, center, and right branches. Like the adaptive implementation, it does not rebuild key bytes and passes `NULL, 0` to visitors.

## Integration
Included by `radix-tree.c` only when `SIMPLE_RADIX_TREE` is defined. It exists as a simpler, easier-to-reason-about implementation for comparison or debug builds.

## Risk Notes
- Removed leaf parents are not recursively pruned, so empty internal nodes can remain.
- Visitor key arguments are not populated.
- Prefix removal has subtle behavior because it removes the exact prefix value separately before destroying the looked-up subtree.
- The tree is not balanced, so adversarial key insertion order can produce deep recursion and poor lookup performance.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree-simple.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree.c -->
# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree.c

## Purpose
Selects and compiles the radix-tree implementation, then adds the shared `radix_tree_values()` helper.

## Main Behavior
The file directly includes either:
- `lib/datastruct/radix-tree-simple.c` when `SIMPLE_RADIX_TREE` is defined.
- `lib/datastruct/radix-tree-adaptive.c` otherwise.

`radix_tree_values()` allocates an array sized to the tree's total entry count, iterates over the tree or prefix, and fills the array with matching values through a local visitor.

## Integration
This is the compilation unit clients link against for the public API in `radix-tree.h`. Device-cache iterators rely on `radix_tree_values()` to snapshot current device pointers before filtering.

## Risk Notes
`radix_tree_values()` allocates for all entries even when a prefix is requested, so prefix queries can overallocate. If visitor traversal stops early because the array fills, the function still returns the values collected so far.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree.h -->
# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree.h

## Purpose
Declares the radix-tree API used by LVM2 for byte-string keyed indexes.

## Public API
- Lifecycle: `radix_tree_create()`, `radix_tree_destroy()`.
- Mutation: `radix_tree_insert()`, `radix_tree_uniq_insert()`, `radix_tree_remove()`, `radix_tree_remove_prefix()`.
- Lookup: `radix_tree_lookup()`, `radix_tree_lookup_ptr()`.
- Traversal and collection: `radix_tree_iterate()`, `radix_tree_values()`.
- Debugging: `radix_tree_is_well_formed()`, `radix_tree_dump()`.

## Data Model
Values are stored as `union radix_value`, either `void *ptr` or `uint64_t n`. Optional destructors are called for deleted entries. Inline pointer helpers wrap the union-based calls.

## Integration
Used by bcache for `(di, block)` indexes and by dev-cache for path, devno, DM UUID, and active DM-device indexes.

## Risk Notes
The header warns that storing a `NULL` pointer is indistinguishable from lookup failure through `radix_tree_lookup_ptr()`. The documented lexicographic iteration contract is stronger than what the current implementations fully provide, especially because visitor key data is not reconstructed.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/radix-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/str_list.c -->
# File Research: sources/block-storage/lvm2/lib/datastruct/str_list.c

## Purpose
Implements small string-list utilities around `struct dm_list` and `struct dm_str_list`, using `dm_pool` allocation.

## Main APIs
- `str_list_create()` allocates and initializes a list head.
- `str_list_add()`, `str_list_add_no_dup_check()`, and `str_list_prepend_no_dup_check()` add string references.
- `str_list_add_list()` appends a list while skipping duplicates.
- `str_list_del()` removes all matching entries.
- `str_list_wipe()` unlinks all entries.
- `str_list_dup()` duplicates both list nodes and strings into a pool.
- `str_list_match_item()`, `str_list_match_list()`, and `str_list_lists_equal()` implement membership/set comparisons.
- `str_list_to_str()` joins list items with a delimiter.
- `str_to_str_list()` splits a string on a delimiter into pool-allocated list entries.

## Integration
Used widely for device aliases, WWID filtering, LV role/layout string lists, configuration-derived lists, and CLI/device selection state.

## Risk Notes
Most add functions store the provided string pointer without copying it; callers must ensure the string lifetime exceeds the list lifetime. Equality assumes no duplicate strings. `str_to_str_list()` can create empty string entries when delimiters are adjacent unless `ignore_multiple_delim` is set.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/str_list.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/str_list.h -->
# File Research: sources/block-storage/lvm2/lib/datastruct/str_list.h

## Purpose
Declares LVM2 string-list helpers layered on `dm_list` and `dm_pool`.

## Public Surface
The header documents return conventions, creation, add/prepend, duplicate-aware and no-duplicate-check insertion, deletion, wipe, match, list equality, duplication, join, and split helpers.

## Integration
The functions are generic utilities for LVM2 modules that need ordered lists of string pointers without introducing a separate container type.

## Risk Notes
The header explicitly notes that `str_list_dup()` initializes caller-provided list storage and that no-duplicate-check insertion requires caller-side duplicate discipline.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/datastruct/str_list.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache-utils.c -->
# File Research: sources/block-storage/lvm2/lib/device/bcache-utils.c

## Purpose
Provides byte-range convenience operations on top of block-granular `bcache` APIs.

## Main APIs
- `bcache_prefetch_bytes()` prefetches every cache block intersecting a byte range.
- `bcache_read_bytes()` reads a byte range, handling unaligned leading/trailing block offsets.
- `bcache_write_bytes()` writes arbitrary byte ranges.
- `bcache_zero_bytes()` zeroes arbitrary byte ranges.
- `bcache_set_bytes()` fills a byte range with a byte value.
- `bcache_invalidate_bytes()` invalidates all blocks overlapping a byte range.

## Core Behavior
`byte_range_to_block_range()` converts byte ranges to cache-block indices and rejects `start + len` overflow. Reads prefetch the full range, then copy slices out of `bcache_get()` blocks. Writes/zeroes/sets share `_update_bytes()`, which handles a possible partial first block, whole middle blocks, and a partial final block.

Whole-block writes and fills use `GF_ZERO` to avoid reading a block that will be fully overwritten; partial updates use `GF_DIRTY`, forcing an existing block read before modification.

## Integration
Used by higher-level device IO wrappers that need byte-addressed reads/writes over the block cache.

## Risk Notes
The helpers assume `bcache_block_sectors(cache) << 9` fits the arithmetic being used. Partial writes require successful reads, so an unreadable sector can prevent a small overwrite even if the caller only wants to change part of the block.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache.h -->
# File Research: sources/block-storage/lvm2/lib/device/bcache.h

## Purpose
Declares the block-cache API, IO-engine abstraction, cache block type, byte-range utility helpers, and fd-table helper functions.

## Public Surface
- IO engines: `create_async_io_engine()`, `create_sync_io_engine()`.
- Cache lifecycle: `bcache_create()`, `bcache_destroy()`.
- Geometry: `bcache_block_sectors()`, `bcache_nr_cache_blocks()`, `bcache_max_prefetches()`.
- Cache access: `bcache_prefetch()`, `bcache_get()`, `bcache_put()`.
- Persistence/invalidation: `bcache_flush()`, `bcache_invalidate()`, `bcache_invalidate_di()`, `bcache_abort_di()`.
- Byte helpers: read, write, zero, set, prefetch, and invalidate byte ranges.
- Boundary and fd helpers: `bcache_set_last_byte()`, `bcache_unset_last_byte()`, `bcache_set_fd()`, `bcache_clear_fd()`, `bcache_change_fd()`.

## Data Model
Clients may access only `struct block` fields `di`, `index`, and `data`; the remaining fields are internal cache state. `GF_ZERO` implies dirty access and can avoid a read for full-block overwrites. `GF_DIRTY` marks a block for later writeback.

## Risk Notes
The header documents that invalidating a held block fails, and `bcache_abort_di()` aborts if any blocks for the descriptor are still held.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-cache.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-cache.c

## Purpose
Implements LVM2's global device cache. It discovers block devices from `/dev` or udev, maintains aliases and preferred names, indexes devices by path and devno, supports optional active-DM-device caches, builds VGID/LVID holder indexes, and sets up devices-file/device-list filtering.

## Core State
The file uses one global `_cache` containing:
- Pool allocator and configured `dev_dir`.
- `names`: path string to `struct device`.
- `devices`: devno to `struct device`.
- `sysfs_only_devices`: temporary entries for devices seen in sysfs before `/dev`.
- `vgid_index` and `lvid_index`: LV holder indexes for devices used by LVs.
- Optional active DM caches: `dm_devs`, `dm_uuids`, `dm_devnos`.
- Preferred-name regex matcher.
- Scan directory/file lists and scan status.

## Device Creation And Alias Handling
`dev_init()` initializes nonzero defaults and embedded lists. `_dev_create()` allocates a device and records its `dev_t`.

`_add_alias()` inserts a path into a device alias list and optionally into the `names` radix tree. Preferred alias order is controlled first by configured `devices/preferred_names`, then by built-in path preference rules that de-prioritize `/dev/block`, `/dev/dm-*`, `/dev/disk`, and `/dev/mapper`, then by path depth, symlink preference, and ASCII order.

`_insert_dev()` handles all combinations of existing devno and existing path, including rehashing aliases when a path now refers to a different `dev_t`.

`dev_cache_failed_path()`, `_drop_all_aliases()`, and `dev_cache_verify_aliases()` remove stale aliases when device nodes disappear or are reused.

## Discovery And Indexing
`dev_cache_scan()` scans configured directories with locale forced to `C`. With udev support and configuration, `_insert_udev_dir()` enumerates block devices and devlinks from libudev. Without that, `_insert_dir()` recursively scans directories while skipping known non-block-device `/dev` subdirectories.

The VGID/LVID indexer examines sysfs holders under `/sys/dev/block/<major>:<minor>/holders`, resolves holder devices, checks DM UUIDs for LVM UUID format, skips internal same-VG holders, and stores lists keyed by VG UUID and LV UUID.

The sysfs-only path covers races where sysfs reports a newly created DM/LV device before `/dev` has a matching node.

## Active DM Device Cache
`dm_devs_cache_update()` calls `get_dm_active_devices()`, requires UUID support in the kernel DM device list, and builds radix indexes by devno and UUID. This avoids repeated individual DM ioctl calls. `dm_devs_cache_label_invalidate()` invalidates label scans for active LVM DM devices.

## Public Lookup And Iteration
- `dev_cache_get()` and `dev_cache_get_existing()` resolve path names, repair stale cache entries, optionally add new devices, and apply filters.
- `dev_cache_get_by_devt()` and `dev_cache_get_by_pvid()` find devices by devno or PVID.
- `dev_iter_create()` snapshots values from the devno radix tree; `dev_iter_get()` applies optional filters while iterating.
- `dev_name()` returns the preferred alias or the unknown-device sentinel.

## Devices File Setup
`setup_devices_file()`, `setup_devices()`, `setup_device()`, and `setup_devices_for_online_autoactivation()` coordinate `devices/use_devicesfile`, `--devicesfile`, `--devices`, dmeventd-specific devices files, devices-file locking, reading, delayed creation policy, and matching device IDs to dev-cache entries.

## Integration
This file is central to label scanning, filters, activation, dmeventd, device ID management, DM UUID lookups, sysfs/udev integration, and bcache/device IO setup.

## Risk Notes
- The cache is global mutable state and not internally synchronized.
- Device-node reuse is a recurring edge case; the file contains several defensive alias-drop paths and comments noting that LVs should ideally not use the same dev-cache paths as PV scanning.
- Preferred-name selection depends on filesystem state and symlink layout.
- Udev/sysfs races are explicitly handled but still complex.
- Devices-file behavior has many command-mode exceptions, especially around first-time creation by `pvcreate`/`vgcreate`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-cache.h -->
# File Research: sources/block-storage/lvm2/lib/device/dev-cache.h

## Purpose
Declares the public device-cache API and `struct dev_filter` interface.

## Public Surface
The header exposes:
- Device initialization and global cache lifecycle.
- Device scan, path/devno/PVID lookup, alias verification, preferred name selection, and iteration.
- VGID/LVID device-list lookup.
- Active DM device cache update/lookup/destruction.
- Sysfs value/binary readers.
- Devices-file and one-device setup routines.
- Open-device leak checking.

## Data Model
`struct dev_filter` defines the filtering contract used by cache lookup and iterators: `passes_filter`, `destroy`, `wipe`, private state, use count, and filter name.

## Integration
Included by command setup, label scanning, device filters, activation, and modules that need stable `struct device` lookup.

## Risk Notes
The header exposes a global cache model, so callers must respect lifecycle ordering: initialize before setup/scan, avoid closing paths behind the cache without invalidation, and call exit checks to catch leaked opens.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-dasd.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-dasd.c

## Purpose
Detects whether an IBM s390 DASD device is CDL formatted.

## Core Behavior
On Linux, the file defines the needed DASD userspace ioctl structures and constants locally, opens the device read-only, calls `BIODASDINFO2`, and checks whether `format == DASD_FORMAT_CDL`.

On non-Linux builds, `dasd_is_cdl_formatted()` always returns 0.

## Integration
Used by device-type probing code for platform-specific DASD handling.

## Risk Notes
The function depends on a Linux DASD ioctl ABI copied into this file. It opens and closes the device itself, so failures in open, ioctl, or close are logged and reported as not CDL-formatted.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-dasd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-ext-udev-constants.h -->
# File Research: sources/block-storage/lvm2/lib/device/dev-ext-udev-constants.h

## Purpose
Defines udev property and sysfs attribute names used by LVM2's external device information layer.

## Constants
The header names udev properties for filesystem type, multipath component markers, firmware/software RAID detection, partition table type, device type, device symlinks, and multipath path status. It also defines the sysfs `size` attribute name.

## Integration
Included by udev-backed probing code in MD, multipath, and external device-handle modules.

## Risk Notes
These string constants encode contracts with udev rules, blkid, and multipath. If distribution udev properties change, detection behavior can diverge from native sysfs/signature probing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-ext-udev-constants.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-ext.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-ext.c

## Purpose
Implements external device-information handles attached to `struct device`, currently supporting no external source and libudev.

## Core Behavior
A registry maps `DEV_EXT_NONE` and `DEV_EXT_UDEV` to get/release functions. `dev_ext_enable()` switches the source and releases any old incompatible handle. `dev_ext_get()` lazily creates the source handle. `dev_ext_release()` detaches it, and `dev_ext_disable()` returns the device to `DEV_EXT_NONE`.

For udev builds, `_dev_ext_get_udev()` obtains the global udev context, creates a udev device from block `dev_t`, optionally verifies initialization, and stores the handle in `dev->ext.handle`. Release calls `udev_device_unref()`.

Without udev support, udev get returns NULL and release fails.

## Integration
MD and multipath detection use this layer to read udev properties when `external_device_info_source()` selects udev.

## Risk Notes
`_dev_ext_get_udev()` returns NULL if udev reports incomplete information, but it does not unref the created udev device before that return in the initialized-check failure path.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-ext.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-io.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-io.c

## Purpose
Implements low-level device open/close and ioctl helpers for size, readahead, discard, direct block sizes, flushing, and open flag management.

## Main APIs
- `dev_get_size()` returns cached sector size for regular files or block devices.
- `dev_size_seqno_inc()` invalidates cached size values globally.
- `dev_get_read_ahead()` reads BLKRAGET for block devices.
- `dev_discard_blocks()` issues BLKDISCARD unless in test mode.
- `dev_get_direct_block_sizes()` reads physical/logical block sizes.
- `dev_flush()` uses BLKFLSBUF, then `fsync`, then `sync`.
- `dev_open_flags()` opens devices with direct IO, noatime, read/write, exclusive, and quiet-mode handling.
- `dev_open*()` wrappers select common open modes.
- `dev_close()` and `dev_close_immediate()` manage reference-counted closing.

## Core Behavior
Block-device size is read with `BLKGETSIZE64` through an existing bcache fd if available or through a temporary read-only open. Regular-file size is read with `stat`. Results are cached in the device with a sequence number.

`dev_open_flags()` reuses an already-open fd if it satisfies requested access/exclusive requirements; otherwise it may close and reopen to upgrade. It tests/falls back from `O_NOATIME` and `O_DIRECT`, validates that the opened fd still refers to the expected `dev_t`, and records open mode flags.

## Integration
Used by all device probing, metadata IO, label scanning, wiping, discard, and signature detection paths.

## Risk Notes
- Opening while in a critical section is logged but not rejected.
- Reopening to upgrade access can interact badly with references; comments note unresolved concerns around allocated device lifetime.
- Without `O_DIRECT_SUPPORT`, block devices are flushed after open.
- `dev_flush()` falls back to global `sync()` if device-specific flushing fails.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-io.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-luks.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-luks.c

## Purpose
Detects LUKS signatures at the start of a device.

## Core Behavior
`dev_is_luks()` reads six bytes at offset 0 and compares them with `LUKS\xba\xbe`. It sets `offset_found` to 0 when provided, returns 1 for a match, 0 for no match, and -1 if the read fails.

## Integration
Used by device-type/signature checks to avoid treating encrypted containers as plain LVM PV candidates.

## Risk Notes
Only the primary header at offset 0 is checked here; the `full` parameter is unused.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-luks.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-lvm1-pool.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-lvm1-pool.c

## Purpose
Detects legacy LVM1 PV labels and old pool labels from an already-read buffer.

## LVM1 Detection
The file defines a packed `pv_disk` structure for the old LVM1 on-disk format. `dev_is_lvm1()` checks the `"HM"` identifier and little-endian version 1 or 2.

## Pool Detection
The file defines old pool label constants and `struct pool_disk`. `pool_label_in()` converts/copies fields from the input buffer using big-endian conversions. `dev_is_pool()` checks `POOL_MAGIC` and compares the major/minor version bits of `pl_version`, ignoring the update-level byte.

## Integration
Used by device-type probing to reject or classify legacy LVM/pool signatures before writing new metadata.

## Risk Notes
Both functions trust that the caller supplied a buffer large enough for the corresponding disk structure; `buflen` is not used for bounds checks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-lvm1-pool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-md.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-md.c

## Purpose
Detects Linux MD RAID components and derives MD stripe geometry from sysfs.

## Signature Detection
Native detection checks:
- MD v1.1 magic at offset 0.
- MD v1.2 magic at offset 4096.
- When `full` is set, MD v0.90 magic near the 64KiB-aligned end.
- MD v1.0 magic near 8KiB from the end.
- Intel IMSM signature near the end, adjusted for 4K logical block size.
- DDF headers at 512 bytes or 128KiB from the end, with CRC validation.

With udev support, `DEV_EXT_UDEV_BLKID_TYPE == linux_raid_member` is also accepted when external device info source is udev.

`dev_is_md_component()` marks `DEV_IS_MD_COMPONENT` on success and can return the found offset.

## Sysfs Geometry
The file reads MD sysfs attributes through `_md_sysfs_attribute_scanf()`:
- `chunk_size`
- `level`
- `raid_disks`
- `metadata_version`

`dev_md_stripe_width()` computes data-disk count by RAID level and returns stripe width in sectors. `dev_is_md_with_end_superblock()` identifies MD devices with metadata versions `1.0` or `0.90`.

## Integration
Used by filters and metadata placement code to avoid clobbering MD members and to align LVM data appropriately over MD devices.

## Risk Notes
- End-of-device checks are intentionally skipped unless `full` is requested to avoid extra IO on every command.
- IMSM logging reports the previous `sb_offset` value rather than the exact IMSM offset after detection.
- DDF validation depends on CRC interpretation in either endian form.
- Non-Linux builds return no MD detection/geometry.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-md.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-mpath.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-mpath.c

## Purpose
Detects whether a device is a multipath component and extracts WWIDs from multipath devices.

## Initialization And Caches
`dev_mpath_init()` creates a pool and a hash table caching DM minor numbers as multipath or non-multipath. If configured, it also reads a multipath WWIDs file into `_wwid_hash_tab`.

The file can parse `/etc/multipath.conf` and `/etc/multipath/conf.d/*` blacklist and blacklist_exceptions `wwid` entries. Blacklisted WWIDs are removed from the WWID hash unless they appear in exceptions.

`dev_mpath_exit()` destroys all multipath detection caches.

## Detection Paths
`dev_is_mpath_component()` first restricts checks to SCSI or NVMe devices and resolves partitions to primary devices. It then tries:
- Sysfs holders: a component's holder is a DM device whose UUID begins with `mpath-`.
- The configured multipath WWIDs file, matching WWIDs read from device VPD/sysfs and omitting type prefixes for naa/eui/t10 IDs.
- Udev properties `ID_FS_TYPE=mpath_member` or `DM_MULTIPATH_DEVICE_PATH=1` when udev is the configured external info source.

When sysfs holder detection succeeds, the holder devno is returned through `holder_devno`.

## WWID Extraction
`dev_mpath_component_wwid()` walks a DM multipath device's sysfs `slaves` directory and reads the first component's `device/wwid`, normalizing spaces for `scsi_debug`, and duplicates the result into the command pool.

## Integration
Used by device filters to avoid using individual paths that are members of a multipath map, preventing duplicate PV visibility and unsafe writes.

## Risk Notes
- Multipath config parsing is deliberately narrow and only recognizes simple `wwid` entries in blacklist sections.
- Sysfs detection depends on `/dev/dm-*` holder nodes existing under `cmd->dev_dir`.
- Results are cached by DM minor, so device-minor reuse after topology changes depends on cache lifetime.
- WWID matching handles common type prefixes but can miss device-specific WWID formats.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-mpath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-swap.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-swap.c

## Purpose
Detects swap and suspend signatures on Linux block devices.

## Core Behavior
`dev_is_swap()` gets the device size, then checks the last 10 bytes of possible page-size regions from 4KiB through 64KiB, skipping 32KiB. It recognizes `SWAP-SPACE`, `SWAPSPACE2`, suspend signatures `S1SUSPEND`, `S2SUSPEND`, `ULSUSPEND`, and a binary suspend signature.

On match it sets `offset_found` to the signature offset and returns 1. It returns 0 for no match and -1 on read/size failure.

## Integration
Used by signature probing to avoid overwriting devices that contain swap or hibernation state.

## Risk Notes
The implementation is Linux-only in this file. The `full` parameter is unused, and detection depends on the expected swap-signature placement for supported page sizes.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-swap.c -->