# Group Research: group_1730_reiserfsprogs_sources_local_fs_reiserfsprogs_fsck_uobjectid_c_sourc_06ea60e9e2ab

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/uobjectid.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/uobjectid.c

Implements fsck’s temporary object-id map. The map is a sparse array of fixed-size bitmap intervals over 32-bit object IDs; an interval pointer of `NULL` means no IDs are used, `(void *)1` means the whole interval is used, and an allocated bitmap tracks mixed intervals. Each bitmap stores a local `__u16` used count at the tail of the 1024-byte allocation.

Key routines:
- `id_map_init()` allocates the index, marks IDs `0` and `1`, then subtracts ID `0` from the global count so callers can treat `0` as reserved convenience state.
- `id_map_test()` and `id_map_mark()` query and mark IDs, upgrading empty intervals to bitmaps and collapsing full bitmaps to the `(void *)1` sentinel.
- `id_map_alloc()` finds the next free object ID, preferring the first non-full bitmap interval, or the first zero interval after a short scan.
- `id_map_flush()` converts the internal bitmap representation back into the superblock object-id interval array, sets `sb_oid_maxsize` / `sb_oid_cursize`, and handles truncation when the superblock map cannot hold all interval boundaries.

Dependencies are `fsck.h`, `misc_*bit()` helpers, ReiserFS superblock accessors, and `reiserfs_super_block_size()`. The commented-out save/load functions are stale alternate object-id-map serialization code and are not active.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/uobjectid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ustree.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/ustree.c

Provides fsck-side wrappers around ReiserFS tree mutation and traversal. `reiserfsck_paste_into_item()`, `reiserfsck_insert_item()`, `reiserfsck_delete_item()`, and `reiserfsck_cut_from_item()` initialize a `tree_balance`, call `fix_nodes()`, then call `do_balance()` with the right mode.

Deletion and truncation paths free unformatted data blocks for indirect items before balancing:
- `free_unformatted_nodes()` walks indirect item block pointers and calls `reiserfs_free_block()`.
- `reiserfsck_cut_from_item()` frees the last unformatted node pointer being cut.

`pass_through_tree()` is a depth-first traversal from the root block. It reads each node, optionally calls an after-read callback, optionally calls a full-path callback for leaves or requested depth, skips subtrees with bad blocks or callback-reported problems, logs corruptions, and updates a spinner/progress display. It uses `bread()`, `brelse()`, path arrays sized by `MAX_HEIGHT`, and child pointers from internal nodes.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ustree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/include/Makefile.am

Autotools install manifest for public and private headers. It keeps `parse_time.h` and `progbar.h` as `noinst_HEADERS`, while installing `io.h`, `misc.h`, `reiserfs_fs.h`, `reiserfs_lib.h`, and `swab.h` under `$(includedir)/reiserfs`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/io.h -->
# File Research: sources/local-fs/reiserfsprogs/include/io.h

Declares the user-space buffer-cache interface used by reiserfsprogs. `struct buffer_head` mirrors kernel-style buffer metadata: block number, device fd, size, data pointer, state bits, refcount, callback hooks, list links, and hash links.

Defines buffer state flags and macros for dirty, uptodate, locked, clean, and do-not-flush status. Exposes `getblk()`, `bread()`, `bwrite()`, `brelse()`, `bforget()`, buffer lookup, flush/free/invalidate operations, and fsck rollback-file helpers.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/misc.h -->
# File Research: sources/local-fs/reiserfsprogs/include/misc.h

General support header not specific to on-disk ReiserFS formats. It declares fatal error handling, guarded allocation helpers, mount detection, DMA probing, device/block counting, progress printing, random generation, confirmation prompts, and a generic binary search.

It also defines little-endian bit operations used throughout the tools:
- `misc_set_bit()`, `misc_clear_bit()`, `misc_test_bit()`
- first/next zero-bit and set-bit scans

Other utilities include stat-field macros for device metadata, bit-mask helpers, sorted block/device list helpers, and compatibility macros for major/minor and IDE/SCSI major detection.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/parse_time.h -->
# File Research: sources/local-fs/reiserfsprogs/include/parse_time.h

Small declaration header for `parse_time(char *str)`. It includes `<time.h>` and returns a `time_t` parsed from the tool’s compact timestamp syntax or the special value handled by the implementation.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/parse_time.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/progbar.h -->
# File Research: sources/local-fs/reiserfsprogs/include/progbar.h

Declares progress bar and spinner state used by fsck/mkfs output. `struct progbar` tracks units, last displayed percent/time, flags, and output file. `struct spinner` tracks spinner position and output file. Functions initialize, update, and clear both display styles.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/progbar.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/reiserfs_fs.h -->
# File Research: sources/local-fs/reiserfsprogs/include/reiserfs_fs.h

Central on-disk ReiserFS format header. It defines endian-safe accessors, superblock layouts for old and current formats, journal descriptor/commit/header structures, keys, item headers, block headers, stat-data formats, directory-entry headers, disk-child pointers, paths, virtual nodes, tree-balance structures, item type constants, and balancing modes.

Major areas:
- Superblock and journal constants: magic strings, disk offsets, format versions, mount/fs states, journal defaults.
- Key/item model: v1 and v2 key encoding, item flags, stat/direct/indirect/directory classification, item-body access macros.
- Tree node layout: block headers, internal child pointers, path macros, node size limits, `MAX_HEIGHT`.
- Directory format: directory entry headers, visibility/bad-location flags, hash/generation offset helpers.
- Balancing model: `virtual_item`, `virtual_node`, `tree_balance`, mode constants, neighbor/FEB arrays, and buffer-info helpers.
- Function declarations for search, fix_nodes, balance, printing, hashing, and node-format helpers.

This file is the contract binding fsck, mkreiserfs, bitmap, journal, and tree-balancing code to the same byte-level disk layout.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/reiserfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/reiserfs_lib.h -->
# File Research: sources/local-fs/reiserfsprogs/include/reiserfs_lib.h

Public library API for reiserfsprogs. Defines `reiserfs_filsys_t`, in-memory bitmap state, hash function type, the filesystem handle, and transaction metadata.

The filesystem handle stores block size, format, hash function, device filenames/fds, superblock buffer, on-disk bitmap, journal device/header state, bad-block bitmap, dirty flags, private pointer, and block allocator/deallocator callbacks.

Declares APIs for opening/creating/flushing/closing filesystems, journal management, bitmap management, tree mutations, directory entry lookup/add/remove, key comparison/search, file and directory iteration, object-id tracking, bad-block list handling, node-format inspection, hash selection, stat-data field access, printing, and xattr/ACL validation.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/reiserfs_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/include/swab.h -->
# File Research: sources/local-fs/reiserfsprogs/include/swab.h

Endian conversion compatibility header. It defines constant and runtime byte-swap helpers for 16/32/64-bit values and supplies `cpu_to_le*`, `le*_to_cpu`, and constant variants when system headers have not already defined them. Little-endian builds use casts; big-endian builds use byte swapping. Non little/big endian architectures are rejected.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/include/swab.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/lib/Makefile.am

Builds the private libtool library `libmisc.la` from `io.c`, `misc.c`, `parse_time.c`, and `progbar.c`. A commented `reiserfs.c` note suggests an older or removed source file.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/io.c -->
# File Research: sources/local-fs/reiserfsprogs/lib/io.c

Implements the user-space buffer cache and rollback support. Buffers are kept in a circular active list, free list, and 4096-bucket hash table. `getblk()` reuses clean unreferenced buffers, grows the cache in groups of ten, and flushes dirty buffers once the soft memory limit is reached. `bread()` reads a block into an uptodate buffer and treats EOF/read errors distinctly.

Write path:
- `bwrite()` skips clean/non-uptodate buffers, invokes optional callbacks, seeks to block offset, optionally saves original disk content to the rollback file, writes full buffer data, marks clean, and invokes end-I/O callback.
- `flush_buffers()`, `free_buffers()`, and `invalidate_buffers()` manage cache lifecycle.

Rollback support writes a magic header, block size, count, and original block images before destructive fsck writes. `do_fsck_rollback()` restores saved blocks to the data or journal device by matching recorded device ids.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/misc.c -->
# File Research: sources/local-fs/reiserfsprogs/lib/misc.c

Implements general utilities. Memory allocation wraps each allocation with begin/end sentinels and size metadata so `checkmem()`, `get_mem_size()`, `expandmem()`, and `freemem()` can detect corruption and manage resizing.

Other responsibilities:
- `die()` formats a fatal message and aborts.
- Mount detection searches `/proc/mounts` and mtab, with special handling for root and read-only mtab.
- Progress helpers render percentage marks and throughput estimates.
- `count_blocks()` determines block-device or regular-file size via `BLKGETSIZE64`, `BLKGETSIZE`, or probing offsets.
- Mask helpers build 16/32/64-bit masks.
- `reiserfs_bin_search()` provides generic sorted-array lookup/insertion positioning.
- Sorted block/device list insertion supports rollback bookkeeping.
- DMA helpers query IDE/XT support and drive DMA state/speed where platform ioctls exist.
- `user_confirmed()` reads an exact confirmation string from stdin.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/parse_time.c -->
# File Research: sources/local-fs/reiserfsprogs/lib/parse_time.c

Parses tool timestamp strings. The special string `"now"` returns `time(NULL)`. Otherwise it parses `YYYYMMDDHHMMSS` using `strptime()` when available, or `sscanf()` fallback with range checks, then returns `mktime(&ts)`. Invalid parse state emits `reiserfs_warning()`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/parse_time.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/progbar.c -->
# File Research: sources/local-fs/reiserfsprogs/lib/progbar.c

Implements terminal progress display. `progbar_init()` initializes static bar/space buffers and context state. `progbar_update()` rate-limits updates, computes a 0.1% fixed percent, renders a label, bar, spinner, percent, and optional numeric units, then clears at 100%. Spinner helpers print and clear a rotating `\|/-` character.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/lib/progbar.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/mkreiserfs/Makefile.am

Builds the `mkreiserfs` sbin program from `mkreiserfs.c`, installs the `mkreiserfs.8` man page, links against `reiserfscore/libreiserfscore.la`, and creates compatibility symlinks `mkfs.reiserfs` and `mkfs.reiserfs.8` at install time.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.8.in -->
# File Research: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.8.in

Manual page template for `mkreiserfs`. Documents command syntax, device and optional filesystem-size arguments, and options for block size, hash function, format 3.5/3.6, UUID, label, quiet mode, separate journal device, journal offset/size, transaction max size, bad-block file, force mode, debug mode, and version output. Also lists author, bug-report guidance, and related tools.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.c -->
# File Research: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.c

Implements filesystem creation. It parses CLI options, selects format, validates size/block options, creates the filesystem handle, creates journal and bitmap structures, builds the superblock, bitmap, and root block, reports the resulting layout, confirms destructive writes, wipes old signatures, zeroes the journal, closes/syncs, and reports success.

Important routines:
- `make_super_block()` sets clean state, tree height, hash, UUID/label for 3.6, reserved journal blocks, and free-block adjustment for bad blocks.
- `invalidate_other_formats()` zeroes the initial 64 KiB to remove old signatures.
- `zero_journal()` writes zero-filled journal blocks with progress.
- `make_bitmap()` marks skipped/super/bitmap/journal/bad/root blocks and computes free blocks.
- `make_root_block()` creates an empty leaf, ensures the root directory exists, and marks root object IDs used.
- `report()` prints superblock, journal, hash, free-space, UUID/label, and debug details.

The main path uses `can_we_format_it()`, `block_size_ok()`, `reiserfs_create()`, `reiserfs_create_journal()`, `reiserfs_create_ondisk_bitmap()`, `create_badblock_bitmap()`, and `add_badblock_list()`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/Makefile.am

Builds and installs `libreiserfscore.la`. It generates `reiserfs_err.c` and `reiserfs_err.h` from `reiserfs_err.et` using `compile_et`, installs `reiserfs_err.h`, and compiles core sources including balancing, searching, hashing, printing, node formats, library logic, bitmap, journal, and xattr support. Links against `../lib/libmisc.la` and `-lcom_err`, and installs `reiserfscore.pc`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/bitmap.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/bitmap.c

Implements in-memory and on-disk ReiserFS block bitmap handling. Basic operations create, expand, shrink, delete, copy, compare, set, clear, test, fill, zero, invert, count, and find zero bits while maintaining `bm_set_bits` and dirty state.

On-disk handling:
- `reiserfs_fetch_ondisk_bitmap()` reads bitmap blocks from the filesystem, following spread-bitmap layout when enabled, copies bytes into memory, validates unused tail bytes/bits, clears out-of-range in-memory bits, and recomputes set-bit count.
- `reiserfs_flush_to_ondisk_bitmap()` writes dirty bitmap contents back, initializes bitmap blocks to `0xff`, copies active bytes, and sets unused tail bits on disk.
- `reiserfs_open_ondisk_bitmap()` validates expected bitmap count, including large-filesystem overflow behavior.
- `reiserfs_create_ondisk_bitmap()` allocates an empty bitmap for new filesystems.
- `reiserfs_close_ondisk_bitmap()` flushes and frees.

Also serializes fsck temporary bitmaps with start/end magic and run-length encoded used/free extents, and saves/validates fsck stage markers.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/do_balan.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/do_balan.c

Core execution phase for ReiserFS tree balancing after `fix_nodes()` has analyzed required shifts, joins, splits, and allocated buffers. It mutates leaf/internal nodes according to the `tree_balance` plan.

Key behavior:
- `balance_leaf_when_delete()` handles delete/cut. It removes or truncates the affected item, updates delimiting keys when first items change, joins with left/right neighbors when requested, invalidates emptied buffers, and frees their blocks.
- `balance_leaf()` handles insert/paste. It shifts content to left and right neighbors, handles whole or partial movement of inserted/pasted data, treats directory entries and indirect items specially, updates key offsets after partial splits, inserts into new split nodes from FEB buffers, and prepares promoted keys/pointers for internal balancing.
- `make_empty_leaf()` and `make_empty_node()` initialize formatted nodes.
- `get_FEB()` obtains and initializes an empty buffer from `tb->FEB`.
- `replace_key()` copies a leaf or internal key into a parent delimiting-key slot and marks the parent dirty.
- `reiserfs_invalidate_buffer()` marks a node free, forgets cached state, and returns the block to the bitmap.
- Neighbor-position helpers map path positions to parent child slots.
- `do_balance()` coordinates leaf balancing, then calls `balance_internal()` for higher levels while `insert_size[h]` remains nonzero, and finally `unfix_nodes()` releases fixed buffers.

The file embodies the classic ReiserFS policy: leaf shifts pack nodes aggressively, deletion can merge nodes, and internal balancing is delegated upward with promoted keys and child pointers.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/do_balan.c -->