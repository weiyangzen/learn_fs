# Group Research: group_1159_minix_sources_teaching_minix_minix_fs_isofs_uthash_h_sources_teachi_490733295293

Scope: `Docs/research_subset_a.md`, limited to the listed MINIX teaching filesystem sources under `sources/teaching/minix/minix/fs`.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/uthash.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/uthash.h

This is a complete embedded copy of Troy D. Hanson's `uthash` single-header hash table library, version `1.9.9`, used by ISOFS code as a macro-based intrusive hash table implementation. It is not MINIX-specific logic, but it provides reusable hash table primitives that callers embed by placing a `UT_hash_handle` field in their own structures.

The header defines compiler portability helpers (`DECLTYPE`, `DECLTYPE_ASSIGN`, Windows integer type fallbacks), allocator/error override hooks (`uthash_malloc`, `uthash_free`, `uthash_fatal`), optional bloom-filter support, and the public CRUD-style macros: `HASH_FIND`, `HASH_ADD`, `HASH_REPLACE`, `HASH_DELETE`, `HASH_CLEAR`, `HASH_ITER`, `HASH_COUNT`, and convenience variants for string, integer, and pointer keys. Items are tracked in both bucket chains and an application-order doubly linked list.

Hashing defaults to Jenkins (`HASH_JEN`) but includes Bernstein, SAX, FNV-1a, one-at-a-time, Hsieh/SFH, and optional MurmurHash variants. Bucket arrays start at 32 buckets and double when bucket chains exceed the threshold, with expansion suppression if repeated expansion does not improve distribution.

Important structs are `UT_hash_bucket`, `UT_hash_table`, and `UT_hash_handle`. The implementation is macro-only and relies on caller-owned storage for elements and keys; deletion frees only table metadata when the final item is removed, not user elements.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/uthash.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/utility.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/utility.c

This ISOFS utility file contains small helpers for memory ownership, ISO directory extents, block retrieval, ISO 9660 timestamp conversion, and checked allocation. It includes `inc.h`, so it depends on ISOFS-wide state such as `fs_dev` and `v_pri`.

`free_extent` recursively frees a linked list of `struct dir_extent` nodes. `free_inode_dir_entry` frees the dynamic record name (`r_name`) inside an `inode_dir_entry` but deliberately leaves the entry object itself allocated for the caller to manage.

`get_extent_absolute_block_id` maps a byte/block offset within an extent chain to an absolute ISO logical block number. It divides the supplied offset by the volume logical block size, walks the linked extents by length, and returns zero if the target falls outside the chain. `read_extent_block` builds on that mapper, rejects block zero and blocks beyond `volume_space_size_l`, and then retrieves the block with `lmfs_get_block`.

`date7_to_time_t` converts ISO 9660's 7-byte date format into a `time_t` using `struct tm`, applying the quarter-hour timezone byte as an hour adjustment when the value is in the legal range. `alloc_mem` wraps `calloc(1, size)` and asserts success, giving ISOFS zero-filled allocations with fail-fast semantics.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/mfs/Makefile

This makefile builds the MINIX File System service as program `mfs`. It lists the service implementation sources: cache, link, mount, misc, open, protect, read, stadir, stats, table, time, utility, write, inode, main, path, and super.

The service links against MINIX filesystem support libraries: `libminixfs`, `libfsdriver`, `libbdev`, and `libsys`. `CPPFLAGS` sets `DEFAULT_NR_BUFS=1024`, which is consumed during MFS initialization to size the libminixfs buffer pool. The final include, `<minix.service.mk>`, integrates the program into the MINIX service build framework.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/buf.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/buf.h

`buf.h` adapts libminixfs buffer objects to MFS's on-disk data layouts. It defines `union ixfer_fsdata_u`, a typed overlay for buffer data that can be interpreted as raw bytes, directory entries, V2 indirect zone entries, V2 disk inodes, or bitmap chunks.

The file then exposes accessor macros `b_data`, `b_dir`, `b_v2_ind`, `b_v2_ino`, and `b_bitmap`, each casting `b->data` to the union and selecting the appropriate member. These macros are used throughout MFS to avoid repeated casts in block, directory, inode, indirect block, and bitmap operations.

The header includes `clean.h`, so users of the buffer overlay also get the `MARKDIRTY` helper that routes dirtying through libminixfs with read-only checks.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/cache.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/cache.c

This file provides MFS-specific wrappers around libminixfs buffer and block allocation facilities. The actual buffer cache is in libminixfs; this file supplies policy and filesystem bitmap integration.

`get_block` wraps `lmfs_get_block`, panicking on I/O errors other than `ENOENT` for `PEEK` requests. This reflects MFS's lack of pervasive recoverable read-error handling and prevents unchecked corruption paths.

`alloc_zone` allocates a data zone from the zone bitmap. It translates between bitmap bit numbers and on-disk zone numbers using `s_firstdatazone`, starts near the caller's hint or the superblock search cursor, updates `s_zsearch`, reports `ENOSPC`, and suppresses repeated "No space" messages after the first failure. `free_zone` reverses the mapping, clears the zone bitmap bit, updates the search cursor, and calls `lmfs_free_block` so cached data and VM block-to-inode associations are invalidated. The implementation asserts `s_log_zone_size == 0`, matching MFS's dropped support for multi-block zones.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/clean.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/clean.h

`clean.h` defines the MFS `MARKDIRTY` macro for dirtying cached buffers. If the global `superblock` is read-only, the macro prints a diagnostic and emits a stack trace with `util_stacktrace`; otherwise it delegates to `lmfs_markdirty`.

This centralizes the "do not dirty read-only filesystems" guard for buffer writes. Inode dirtying uses a similar but separate macro in `inode.h`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/clean.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/const.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/const.h

`const.h` collects MFS layout constants, table sizes, operation codes, and derived size macros. It defines V2/V3 inode zone layout values (`V2_NR_DZONES`, `V2_NR_TZONES`), the in-core inode table size (`NR_INODES`), and the inode hash size/mask used by `inode.c`.

Filesystem identity constants include legacy and V3 superblock magic values, but this MFS implementation only accepts `SUPER_V3` in `read_super`. Directory operations use `LOOK_UP`, `ENTER`, `DELETE`, and `IS_EMPTY`, all consumed by `search_dir`. `WMAP_FREE` controls freeing behavior in `write_map`.

The file also defines inode dirty/time-update flags (`IN_CLEAN`, `IN_DIRTY`, `ATIME`, `CTIME`, `MTIME`), root and layout block numbers (`ROOT_INODE`, `BOOT_BLOCK`, `SUPER_BLOCK_BYTES`, `START_BLOCK`), directory entry sizing, bitmap geometry helpers, and V2 disk inode/indirect sizing macros.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/const.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/fs.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/fs.h

This is the umbrella header for the MFS service. It marks the build as system code with `_SYSTEM`, sets a `VERBOSE` initialization flag, and includes the MINIX, libc, system utility, and fsdriver headers required by most service source files.

After the platform and fsdriver includes, it pulls in the local MFS headers in the order needed by the service: `mfsdir.h`, `const.h`, `type.h`, `proto.h`, and `glo.h`. As a result, most `.c` files include `fs.h` first and receive the common constants, on-disk type declarations, prototypes, and global declarations.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/glo.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/glo.h

`glo.h` declares MFS service globals using the `EXTERN` pattern: variables are declarations normally, but become definitions when `_TABLE` is defined by `table.c`.

The globals include `err_code` for temporary error propagation, `cch[NR_INODES]` for disabled inode reference diagnostics in `main.c`, `fs_dev` for the single mounted device handled by the service instance, and `used_zones` for statvfs/block-usage accounting. It also declares the exported fsdriver dispatch table `mfs_table`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/glo.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/inode.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/inode.c

`inode.c` manages the fixed in-core inode table, including lookup, caching, reference counts, allocation, freeing, timestamp updates, and disk inode serialization. It uses a hash table keyed by inode number masked with `INODE_HASH_MASK` plus an unused/LRU tail queue.

`init_inode_cache` initializes hit/miss counters, all hash buckets, and the unused list. `get_inode` searches the hash, revives cached zero-reference inodes from the unused list, or reuses the first unused slot, loading from disk with `rw_inode` unless `NO_DEV` is used during fresh allocation. `find_inode` is a non-acquiring cache lookup for already-open inodes. `fs_putnode`, `put_inode`, and `dup_inode` implement VFS reference release and local reference duplication.

When the last reference drops, `put_inode` writes dirty inodes, truncates and frees unlinked inodes (`i_nlinks == NO_LINK`), and either evicts freed entries or keeps still-linked entries on the unused list as cacheable inodes. `alloc_inode` allocates an inode bitmap bit, sets owner/mode/superblock fields, and calls `wipe_inode` to reset size, update flags, and zones. `free_inode` clears the inode bitmap bit and updates `s_isearch`.

`rw_inode` locates the disk inode block after boot, superblock, inode map, and zone map blocks, then copies fields through `new_icopy`. Only V3 is accepted; `conv2`/`conv4` handle native/swapped values. `update_times` lazily fills atime/ctime/mtime using `clock_time` unless the filesystem is read-only.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/inode.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/inode.h

`inode.h` defines the in-core MFS inode table and associated cache lists. The first fields mirror on-disk V2/V3 inode data: mode, link count, uid/gid, size, timestamps, and ten zone pointers. The remaining fields are memory-only metadata: device, inode number, reference count, zone layout parameters, superblock pointer, dirty state, allocation search hint, last directory search position, mountpoint flag, seek/read-ahead flag, pending timestamp-update bits, hash links, and unused-list links.

The file defines `inode[NR_INODES]`, the unused tail queue, the inode hash bucket array, and hit/miss counters under the `EXTERN` mechanism. It also defines `NO_SEEK`/`ISEEK` and dirty-state macros. `IN_MARKDIRTY` mirrors buffer dirtying by warning and stack-tracing if code attempts to dirty an inode on a read-only superblock.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/link.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/link.c

`link.c` implements hard links, unlink/rmdir, symbolic-link reads, rename, truncation, hole punching/free-space release, and helper zeroing for partial zones. It is one of the main directory mutation files and relies on `advance`, `search_dir`, `get_inode`, `put_inode`, `truncate_inode`, and `write_map`.

`fs_link` rejects directory hard links, checks `LINK_MAX`, verifies the destination name does not already exist, inserts a new directory entry, and increments the target link count. `fs_unlink` handles both unlink and rmdir entry points, rejecting mountpoints and read-only filesystems, dispatching to `unlink_file` or `remove_dir`. `remove_dir` verifies emptiness through `search_dir(..., IS_EMPTY)`, rejects the root inode, unlinks the directory entry, then removes `.` and `..`.

`fs_rdlink` reads symlink contents from the first mapped block and copies up to the inode size. `fs_rename` handles cross-directory and same-directory rename, mountpoint rejection, ancestor checks for directory moves, replacement of existing targets, insertion/deletion ordering, and `..` updates plus parent link-count maintenance for moved directories.

`fs_trunc` dispatches to full truncation or free-space punching. `truncate_inode` rejects special files, enforces `s_max_size`, frees removed zones, clears the gap when extending, updates size and times, and marks the inode dirty. `freesp_inode` zeroes partial zones and calls `write_map(..., WMAP_FREE)` for fully freed zones, allowing indirect blocks to be reclaimed. `zerozone_half` and `zerozone_range` implement partial-zone zero filling through `get_block_map`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/link.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/main.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/main.c

`main.c` is the MFS service entry point and SEF integration layer. `main` records command-line arguments, performs local SEF startup, and hands control to `fsdriver_task(&mfs_table)`.

`sef_local_startup` registers fresh-start initialization, stateful restart handling, and signal handling. `sef_cb_init_fresh` enables VM cache use in libminixfs, initializes inode reference counters and the disabled diagnostic `cch` array, builds the inode cache free/hash structures, and creates the buffer pool using `DEFAULT_NR_BUFS`. `sef_cb_signal_handler` handles only `SIGTERM`, syncing MFS state before asking fsdriver to terminate.

The disabled `cch_check` block is a historical consistency aid for tracking inode reference deltas across requests; it is not compiled.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/mfsdir.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/mfsdir.h

`mfsdir.h` defines the MFS on-disk directory entry format. `MFS_DIRSIZ` is fixed at 60 bytes and cannot change without breaking existing filesystems, because MFS stores names directly in `struct direct`.

`struct direct` is packed and contains a 32-bit inode number (`mfs_d_ino`) plus a fixed-size filename array (`mfs_d_name`). Directory traversal and mutation in `path.c` cast directory blocks to arrays of this structure through `b_dir`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/mfsdir.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/misc.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/misc.c

`misc.c` currently provides `fs_sync`, the service sync operation. It iterates over the in-core inode table and writes every dirty, referenced inode with `rw_inode(..., WRITING)`.

After inodes are written, it flushes all dirty libminixfs buffers with `lmfs_flushall`. The ordering is intentional: inode writes leave modified disk-inode blocks in the buffer cache, so data/cache blocks must be flushed last.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/mount.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/mount.c

`mount.c` handles mounting, mountpoint marking, and unmounting for the single-device MFS service instance. `fs_mount` stores `fs_dev`, opens the block device read-only or read-write, reads and validates the superblock, and remounts read-only if the filesystem is unclean and the caller requested writable access.

After `read_super`, it sets the libminixfs block size, computes `used_zones` by counting free zone bits, reports block usage to libminixfs, loads the root inode, fills the fsdriver root-node response, and marks the filesystem dirty on disk when mounted read-write.

`fs_mountpt` checks that the target inode is not already a mountpoint and not a special device node, then marks it as a mountpoint. `fs_unmount` checks for unexpected live inode references, releases the root inode, syncs inodes and buffers, marks a writable filesystem clean, closes the block device, invalidates cached blocks for the device, and clears `superblock.s_dev`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/open.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/open.c

`open.c` implements node creation operations: regular files, device nodes, directories, symbolic links, and seek notification. All creation paths route through the private `new_node` helper.

`fs_create` creates a regular node in a parent directory and returns an `fsdriver_node` with inode metadata. `fs_mknod` creates special nodes, storing the device number in zone zero. `fs_mkdir` creates the directory inode, then inserts `.` and `..`; if either insertion fails, it removes the parent directory entry and undoes the initial link count. It increments the parent link count for the new `..`.

`fs_slink` creates a symlink inode, allocates the first block, copies the user-provided link target, appends a NUL byte, rejects targets that fill the block or contain embedded NULs, and cleans up the inode/directory entry on failure.

`new_node` rejects deleted parents and directory link-count overflow, checks whether the final component already exists, allocates a fresh inode, increments its link count, writes it to disk before inserting the directory entry for crash robustness, and frees it again if directory insertion fails. `fs_seek` marks an inode as recently seeked to suppress aggressive read-ahead.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/open.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/path.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/path.c

`path.c` contains MFS path-component lookup and directory-entry manipulation. `fs_lookup` receives an already-open directory inode number, looks up a component with `advance`, and returns inode metadata plus mountpoint status while leaving the target inode open for VFS.

`advance` validates nonempty names, rejects deleted directories, searches the directory with `search_dir(..., LOOK_UP)`, and opens the target inode by number.

`search_dir` is the central directory engine. It implements lookup, insertion, deletion, and emptiness checks over fixed-size `struct direct` entries. It validates directory type, rejects mutations on read-only filesystems, scans directory blocks with `get_block_map`, compares names using only `MFS_NAME_MAX` bytes, and treats only `.` and `..` as allowed entries for `IS_EMPTY`.

For deletion, it stores the deleted inode number in the tail of the name field as recovery metadata, clears `mfs_d_ino`, dirties the directory block, updates parent times, and adjusts `i_last_dpos`. For insertion, it reuses a free slot or extends the directory with `new_block`, zero-fills the name field, truncates/copies the new name, writes the inode number with byte-order conversion, updates size when needed, and writes the inode immediately if the directory grew.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/path.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/protect.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/protect.c

`protect.c` implements metadata permission/ownership changes. `fs_chmod` opens the inode, rejects read-only filesystems, replaces only the permission bits (`ALL_MODES`) while preserving file type and other mode bits, marks ctime for update, dirties the inode, returns the full resulting mode, and releases the inode.

`fs_chown` opens the inode, sets uid and gid, clears setuid/setgid bits, marks ctime, dirties the inode, returns the resulting mode, and releases the inode. Unlike `fs_chmod`, it does not explicitly check `s_rd_only`; dirtying on read-only filesystems would be caught by the inode dirty macro diagnostics.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/protect.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/proto.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/proto.h

`proto.h` declares the internal MFS function surface and maps `put_block` directly to `lmfs_put_block`. It forward-declares common structs and groups prototypes by implementation file.

The declared API covers zone/cache operations, inode allocation/reference/disk I/O, link/unlink/rename/truncation, sync, mount/unmount/mountpoint handling, file/directory/symlink creation, lookup and directory search, chmod/chown, read/write/getdents/block mapping, stat/statvfs, bitmap accounting, timestamp updates, byte-order conversion, and write-side block allocation/mapping.

This file is included through `fs.h`, so it is the main cross-module contract for MFS.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/read.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/read.c

`read.c` implements file reads, writes, peeks, logical-to-physical block mapping, read-ahead, indirect block reading, block-map buffer lookup, and directory enumeration.

`fs_readwrite` finds the already-open inode, checks write permission against read-only superblocks, enforces maximum file size, clears the old EOF zone when a write creates a hole, splits I/O into block-bounded chunks, and calls `rw_chunk`. On successful writes it extends file size for regular files/directories and marks ctime/mtime; reads mark atime. Device-node I/O on read-only filesystems is allowed without updating inode timestamps.

`rw_chunk` maps the file position with `read_map`, returns zeroes for holes on reads, reports zero blocks to VM on peeks, allocates missing blocks on writes with `new_block`, uses read-ahead for reads, and uses `lmfs_get_block_ino` for VM-cache-aware buffer lookup. It copies data through `fsdriver_copyout`/`copyin` and dirties written buffers.

`read_map` resolves direct, single-indirect, and double-indirect zone pointers into physical block numbers, returning `NO_BLOCK` for holes or opportunistic metadata misses. `rd_indir` reads and validates indirect zone numbers. `get_block_map` maps a position and returns the corresponding cached block buffer.

`rahead` performs cache probing and prefetch queue construction, including nearby first-indirect-block prefetch and minimum read-ahead after sequential access. `fs_getdents` validates directory offsets, walks directory entries, computes name lengths, fetches target inode modes to provide directory-entry types, adds entries through `fsdriver_dentry_*`, updates the next position, and marks directory atime.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/stadir.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/stadir.c

`stadir.c` implements `stat` and `statvfs` support. The private `estimate_blocks` helper estimates 512-byte block usage from file size, zone size, and the number of indirect and double-indirect blocks that would be needed. It intentionally does not read all indirect blocks, so holes are ignored and the result is conservative.

`fs_stat` opens the inode, materializes pending timestamps with `update_times`, fills mode, link count, owner, special-device number, size, timestamps, block size, and estimated block count, then releases the inode.

`fs_statvfs` reports filesystem totals from `superblock` and `used_zones`: total/free/available blocks, block and fragment size, I/O size, inode totals, free inode count via `count_free_bits(IMAP)`, and maximum filename length.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/stadir.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/stats.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/stats.c

`stats.c` provides `count_free_bits`, a bitmap scanner used for mount-time block usage and statvfs inode/free-space reporting. It supports both inode and zone maps, deriving the start block, number of valid bits, number of bitmap blocks, and starting origin from the superblock.

The scanner walks bitmap blocks and chunks, byte-swapping each chunk with `conv4` when needed, counts zero bits within the valid map range, and stops at the end of the map. It uses `get_block` for bitmap blocks and releases each buffer after scanning.

Despite the stale comment saying "Allocate a bit", the routine is read-only accounting and does not modify bitmap state.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/super.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/super.c

`super.c` manages superblock I/O and inode/zone bitmap allocation. `alloc_bit` searches either the inode map or zone map from a preferred origin, wraps once, finds the first zero bit, sets it, dirties the bitmap block, and updates libminixfs block-usage accounting for zone allocations. `free_bit` clears a bitmap bit, panics if the bit was already free, dirties the block, and decrements zone usage for zone-map frees.

`get_block_size` returns the current libminixfs filesystem block size and rejects `NO_DEV`.

`rw_super` reads or writes the on-disk superblock stored at byte offset 1024 within block zero. Only fields up to `s_disk_version` are copied to disk; in-memory-only fields after that are zeroed/filled separately. On writes it zeroes the full cache block before copying the on-disk prefix, dirties it, releases it, and flushes all buffers. Read failures are returned cleanly so mounting zero-sized or invalid devices can fail without crashing.

`read_super` validates that the magic is `SUPER_V3`, rejects older V1/V2 magic values, converts fields, rejects multi-block zones (`s_log_zone_size != 0`), validates block size, inode size alignment, layout bounds, and mandatory feature flags, computes `s_firstdatazone` when the legacy field is zero, clamps `s_max_size` to `LONG_MAX`, and initializes search cursors and derived layout values. `write_super` rejects read-only superblocks and delegates to `rw_super`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/super.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/super.h

`super.h` defines the MFS superblock structure and documents the on-disk layout: boot block, superblock at 1KB, inode bitmap, zone bitmap, inode table, alignment padding, and data zones. The struct begins with on-disk fields such as inode count, map sizes, first data zone, zone size shift, flags, maximum file size, zone count, magic, block size, and disk format sub-version.

Fields after `s_disk_version` are memory-only and must remain coordinated with `LAST_ONDISK_FIELD` in `super.c`. These include derived counts, first data zone, device, read-only/native/version flags, direct/indirect counts, and bitmap search cursors.

The file defines `IMAP` and `ZMAP` bitmap selectors, the clean flag `MFSFLAG_CLEAN`, and `MFSFLAG_MANDATORY_MASK` for future incompatible features that older MFS implementations must reject.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/super.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/table.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/table.c

`table.c` defines `_TABLE` so global variables declared through `EXTERN` become definitions, includes the MFS headers, and instantiates the `mfs_table` fsdriver dispatch table.

The table maps VFS/fsdriver operations to MFS implementations: mount, unmount, lookup, putnode, read, write, peek, getdents, truncation, seek, create, mkdir, mknod, link, unlink, rmdir, rename, symlink creation/readlink, stat, chown, chmod, utime, mountpoint marking, statvfs, and sync. It also exposes libminixfs block-device operations for driver, bread/bwrite/bpeek, and bflush.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/table.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/time.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/time.c

`time.c` implements `fs_utime`, the timestamp-setting operation. It opens the target inode, resets pending timestamp flags to ctime-only, then handles `atime` and `mtime` separately.

For each supplied `timespec`, `UTIME_NOW` sets the corresponding lazy update bit, `UTIME_OMIT` leaves the field unchanged, and explicit timestamps are stored directly using seconds only. MFS does not support subsecond timestamp resolution, so nanoseconds are discarded. The inode is marked dirty and released.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/time.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/type.h -->
# File Research: sources/teaching/minix/minix/fs/mfs/type.h

`type.h` defines `d2_inode`, the on-disk V2/V3-style disk inode structure used by MFS. It contains mode, link count, uid, gid, size, atime, mtime, ctime, and `V2_NR_TZONES` zone pointers.

The type is used by `buf.h` buffer overlays and by `inode.c`'s `new_icopy` routine to copy between disk inodes and in-core `struct inode` objects with possible byte-order conversion.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/type.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/utility.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/utility.c

`utility.c` contains byte-order conversion helpers for MFS on-disk structures. `conv2` returns a 16-bit value unchanged when `norm` is true, otherwise swaps its two bytes. `conv4` returns a 32-bit value unchanged when native, otherwise swaps the low and high 16-bit halves through `conv2` and recombines them in reversed order.

These helpers are used for superblock fields, inode fields, bitmap chunks, directory inode numbers, and indirect zone entries. Current `read_super` sets `native = 1` for accepted V3 filesystems, but the conversion layer remains part of the shared MFS logic.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/write.c -->
# File Research: sources/teaching/minix/minix/fs/mfs/write.c

`write.c` is the write-side counterpart to `read.c`, responsible for updating inode block maps, allocating blocks, freeing zones, and zeroing buffers.

`write_map` maps a file byte position to the correct direct, single-indirect, or double-indirect slot and either writes a new zone number or frees the existing zone when `WMAP_FREE` is set. It allocates missing indirect and double-indirect blocks as needed, zeroes newly allocated indirect blocks, writes entries with `wr_indir`, and frees now-empty indirect blocks using `empty_indir`. It marks the inode dirty before map updates and maintains references in either the inode zone array or indirect blocks.

`wr_indir` writes one zone entry to an indirect block using `conv4`. `empty_indir` scans an indirect block for any non-`NO_ZONE` entry. `clear_zone` is now effectively a no-op because the implementation asserts block size equals zone size (`s_log_zone_size == 0`).

`new_block` allocates a zone if `read_map` finds no existing block at the requested position, using `i_zsearch` and the first file zone as locality hints, records the mapping with `write_map`, obtains a VM-cache-aware buffer with `lmfs_get_block_ino(..., NO_READ, ...)`, zeroes it, and returns it. `zero_block` clears a buffer's data to zero and marks it dirty.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/mfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/pfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/pfs/Makefile

This makefile builds the Pipe File System service as program `pfs` from a single source file, `pfs.c`. It links against `libfsdriver` and `libsys`, then includes `<minix.service.mk>` to participate in the MINIX service build framework.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/pfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/pfs/pfs.c -->
# File Research: sources/teaching/minix/minix/fs/pfs/pfs.c

`pfs.c` implements the MINIX Pipe File Server, an in-memory fsdriver service for anonymous pipes and cloned device-like nodes. It uses a fixed table of 512 inodes and a free list; there is no persistent storage and no directory tree.

`pfs_mount` initializes all inode slots, reserves inode number zero by numbering slots from one, places them on the free list, returns an empty root node, and advertises `RES_64BIT`. `pfs_unmount` only warns if in-use inodes remain. `pfs_findnode` validates an inode number and requires the slot to be allocated.

`pfs_newnode` supports FIFO nodes and block/character/socket device nodes. It allocates a `PIPE_BUF` data buffer for FIFOs, initializes metadata and pending timestamp bits, stores device numbers for device-like nodes, and fills the fsdriver node response. `pfs_putnode` expects a single reference, frees any pipe buffer, marks the slot free, and returns it to the free list.

`pfs_read` and `pfs_write` implement linear pipe-buffer I/O. Reads copy from `i_data + i_start`, shrink size, advance the start offset, and mark atime. Writes reject growth beyond `PIPE_BUF`, compact unread data to the beginning when needed, copy input after current data, grow size, and mark ctime/mtime. `pfs_trunc` supports only full pipe truncation. `pfs_stat` materializes lazy timestamps and reports metadata. `pfs_chmod` updates permission bits and times.

The file also includes SEF startup/signal handling, privilege drop to `SERVICE_UID`, the `pfs_table` dispatch table, and `main`, which starts fsdriver processing.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/pfs/pfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/procfs/Makefile

This makefile builds the ProcFS service as program `procfs`. It compiles buffer management, CPU info, main/tree hooks, PID generators, root-file generators, service-directory support, and utilities.

It adds include paths for MINIX, MINIX filesystem headers, and MINIX servers. ProcFS links against `libvtreefs` and `libfsdriver`, reflecting that its file tree and inode lifecycle are delegated to VTreeFS rather than a custom disk-backed inode/block layer. The service build is finalized through `<minix.service.mk>`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/buf.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/buf.c

`buf.c` implements ProcFS's per-read output buffer abstraction. It stores static module state for the target buffer pointer, remaining writable bytes, used bytes, and a leading offset to skip for partial reads.

`buf_init` sets up a new output operation, capping output to `BUF_SIZE - 1` because formatted output needs room for a temporary trailing NUL. `buf_printf` appends formatted text with `vsnprintf`, still formatting skipped leading data because output size cannot be known in advance. It handles the skip window by moving unskipped data to the start once the offset is crossed, then clamps output to the requested length.

`buf_append` appends arbitrary bytes with the same skip/length accounting, used for binary-like command-line and environment output. `buf_result` returns the number of produced bytes, excluding any NUL terminator.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/const.h -->
# File Research: sources/teaching/minix/minix/fs/procfs/const.h

`const.h` defines ProcFS sizing and mode constants. `NR_INODES` is set to four times the combined task/process count, with a detailed comment explaining the need for static files, retained deleted inodes still open in VFS, and stable getdents generation for PID directories.

The file defines standard modes for world-readable regular files (`REG_ALL_MODE`), world-accessible directories (`DIR_ALL_MODE`), and symlinks (`LNK_ALL_MODE`). `BUF_SIZE` is `4097`, allowing a 4KB user-visible output buffer plus one byte needed by `vsnprintf` handling in `buf.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/const.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/cpuinfo.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/cpuinfo.c

`cpuinfo.c` generates `/proc/cpuinfo`. On i386, it defines a CPU feature-bit name table and `print_x86_cpu_flags`, which emits supported feature names for two 32-bit flag words.

`print_cpu` emits a processor number and, for i386, vendor, model-family fields, frequency, and feature flags based on `struct cpu_info`. Vendor mapping currently names Intel and AMD explicitly and falls back to `unknown`.

`root_cpuinfo` fetches machine topology with `sys_getmachine` and CPU details with `sys_getcpuinfo`, logging failures to the console. It iterates over `machine.processors_count` and appends each CPU's information through the ProcFS buffer API.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/cpuinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/glo.h -->
# File Research: sources/teaching/minix/minix/fs/procfs/glo.h

`glo.h` declares cross-module ProcFS globals: `pid_files[]` from `pid.c`, `root_files[]` from `root.c`, and `proc_list[NR_PROCS]` from `tree.c`.

These declarations connect the static tree builder, dynamic PID tree manager, and PID-file generator registry without introducing a separate global-definition pattern like MFS uses.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/glo.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/inc.h -->
# File Research: sources/teaching/minix/minix/fs/procfs/inc.h

`inc.h` is the umbrella include for ProcFS. It pulls in MINIX driver, parameter, sysctl, sysinfo, VTreeFS, and ProcFS interfaces, plus assertions and architecture/kernel/VFS internal headers needed for process and device-map data.

It then includes the local ProcFS headers: constants, types, prototypes, and globals. Most ProcFS implementation files include only `inc.h` to obtain the shared service environment.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/inc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/main.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/main.c

`main.c` wires ProcFS into VTreeFS. It defines hook callbacks for initialization, lookup, getdents, read, and readlink, then passes them to `run_vtreefs`.

The private `construct_tree` helper recursively creates the static tree from `struct file` arrays, using `add_inode` and storing each file's data pointer as VTreeFS callback data. Directories recurse into child `struct file` arrays.

`init_hook` runs once. It initializes dynamic process-tree state with `init_tree`, creates static root files from `root_files`, initializes the service directory through `service_init`, and then suppresses duplicate initialization on restarts through a static flag.

`main` defines root directory metadata (`DIR_ALL_MODE`, root ownership, no device) and starts VTreeFS with the hook table, inode budget, root stats, expected dynamic root entries, and ProcFS buffer size.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/pid.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/pid.c

`pid.c` defines the files generated inside each dynamic PID directory: `psinfo`, `cmdline`, `environ`, and `map`. Each entry maps a filename to a generator function taking a kernel process slot.

`get_proc_data` retrieves detailed process data through `__sysctl(CTL_MINIX, MINIX_PROC, PROC_DATA, pid)`. `is_zombie` checks `proc_list` flags for process slots.

`pid_psinfo` emits the compact process information format used by `mtop(1)`: version, process type, endpoint, sanitized name, state, blocked-on endpoint, priority, user/system time, cycle counters, VM memory total, nice value, and effective UID. It combines data from MINIX process sysctl, `proc_list`, and optional VM usage information.

`pid_cmdline` and `pid_environ` fetch argv/environment data through kernel sysctl nodes, skip kernel tasks and zombies, and append raw NUL-separated records to the ProcFS buffer. `pid_map` queries VM regions by endpoint and emits address ranges with read/write/execute protection flags.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/pid.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/proto.h -->
# File Research: sources/teaching/minix/minix/fs/procfs/proto.h

`proto.h` declares ProcFS's internal module interfaces. It covers buffer initialization/append/result functions, `/proc/cpuinfo` generation, service-directory initialization and hooks, tree initialization and VTreeFS hook functions, PID-slot conversion, out-of-inodes reporting, and load-average utility retrieval.

The prototypes expose the service's main extension points around VTreeFS: lookup-time tree refresh, getdents-time expansion, read-time generator dispatch, and future readlink handling.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/root.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/root.c

`root.c` defines the static files in the ProcFS root and their generator functions. `root_files` includes `hz`, `uptime`, `loadavg`, `kinfo`, `meminfo`, `dmap`, `ipcvecs`, and `mounts`, plus i386-only `pci` and `cpuinfo`.

Generators are lightweight snapshots of system state. `root_hz` prints clock frequency, `root_uptime` prints uptime in seconds with two decimals, `root_loadavg` formats 1/5/15-minute load averages from `procfs_getloadavg`, `root_kinfo` prints process/task counts, and `root_meminfo` prints VM page size and memory totals/free/largest/cached.

On i386, `root_pci` initializes PCI once and prints slot/class/revision/vendor/device/subsystem/name records. `root_dmap` dumps assigned major-device mappings from VFS. `root_ipcvecs` prints kernel IPC vector entrypoints only when kernel info says they are exported. `root_mounts` uses `getvfsstat` and prints mounted filesystem source, target, type, and read-only/read-write status.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/root.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/service.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/service.c

`service.c` implements the dynamic `/proc/service` directory. It snapshots RS process tables into a local `rproc` transfer structure, creates one file per active system service, and generates per-service details.

`service_get_policies` currently uses a built-in label-to-policy mapping rather than querying RS policy state. It formats policy names such as `reset` and `restart` into a per-slot buffer. `service_get_flags` formats RS and system flags into a compact character string for active/updating/exiting/no-ping/copy/replication/core-service status.

`service_active` filters RS slots down to live system services, excluding init's user-process representation. `service_update` fetches RS tables, deletes stale service entries in one pass, then adds missing active services in a second pass to avoid name-collision issues. `service_init` creates the static `service` directory under the VTreeFS root.

`service_lookup` lazily refreshes the directory once per clock tick for lookups inside `/proc/service`. `service_getdents` refreshes before listing. `service_read` emits a service file with filename, endpoint, pid, restart count, formatted flags, policy string, and ASR count.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/service.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/tree.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/tree.c

`tree.c` manages ProcFS's dynamic PID directories and implements the VTreeFS hooks registered by `main.c`. It maintains `proc_list[NR_PROCS]`, computes the number of per-PID files from `pid_files`, and updates process state through `__sysctl(CTL_MINIX, MINIX_PROC, PROC_LIST)`.

`pid_from_slot` maps kernel task slots to negative task PIDs and process slots to active process IDs. `make_stat` builds inode metadata for PID directories and their files, assigning root ownership for tasks and process uid/gid for user processes. `check_owner` forces directory reconstruction when process ownership changes.

`construct_pid_dirs` refreshes root-level PID directories in two passes: delete stale/mismatched entries first, then add missing current entries. This avoids VTreeFS assertions and duplicate names during rapid PID reuse. `construct_pid_entries` adds one requested PID file or all PID files, deleting the parent if the process has disappeared.

`lookup_hook` lazily refreshes process data once per tick, then rebuilds root PID directories, creates requested PID entries, or delegates service-directory lookup refresh. `getdents_hook` eagerly prepares directory contents for root, PID directories, or service. `read_hook` initializes the output buffer and dispatches to PID-file, service-file, or static-root generator callbacks based on inode indexes. `rdlink_hook` has placeholder support for PID-directory symlinks through `pid_link`, which currently returns an empty target.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/type.h -->
# File Research: sources/teaching/minix/minix/fs/procfs/type.h

`type.h` defines ProcFS internal data types and documents how `struct file` entries map onto VTreeFS indexes and callback data. `data_t` is an opaque pointer-sized value. `struct load` stores tick count and process-load ticks for load-average calculation.

`struct file` contains a name, mode, and custom data pointer. For static regular files, `data` points to a `void (*)(void)` generator. For static directories, it points to another `struct file` array. For PID dynamic files, it points to a `void (*)(int slot)` generator.

The long comment explains VTreeFS identity rules: PID directories use slot numbers as indexes and PIDs as callback data; PID files use their array index; service files use RS slot indexes; static files/directories use `NO_INDEX` and callback data for generator dispatch. These rules are central to stable getdents behavior and safe regeneration under process churn.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/type.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/util.c -->
# File Research: sources/teaching/minix/minix/fs/procfs/util.c

`util.c` implements `procfs_getloadavg`, a MINIX-specific load-average helper. It fetches kernel load history with `sys_getloadinfo`, caps requested output to three averages, and computes 1, 5, and 15 minute load averages from circular history slots.

The function accounts for the newest slot being partially filled by subtracting unfilled ticks from the denominator. It fills each `struct load` with total process-load ticks and the corresponding tick denominator, leaving formatting to `root_loadavg`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/procfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/ptyfs/Makefile

This makefile builds the PTYFS service as program `ptyfs` from `ptyfs.c` and `node.c`. It links against `libfsdriver` and includes `<minix.service.mk>` for service build integration.

Within this grouped scope, only the node-management companion files are included for source research; the makefile shows that `node.c` is part of the full PTYFS service.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/node.c -->
# File Research: sources/teaching/minix/minix/fs/ptyfs/node.c

`node.c` manages PTY slave node allocation metadata for PTYFS. The implementation preallocates a bitmap and `struct node_data` array sized by `NR_PTYS`, relying on the current system-global PTY limit.

`init_nodes` clears the allocation bitmap. `set_node` validates the requested index, sets the bitmap bit, copies the caller's device/mode/owner/time metadata into `node_data`, and allows updating an already allocated node. `clear_node` unsets the bitmap bit and intentionally ignores attempts to clear an unallocated node.

`get_node` returns `NULL` for out-of-range or unallocated indexes, otherwise returns the stored metadata pointer. `get_max_node` returns `NR_PTYS`; the comment notes that this is acceptable because the limit is small, even though a future implementation could track the actual highest allocated node.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/node.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/node.h -->
# File Research: sources/teaching/minix/minix/fs/ptyfs/node.h

`node.h` declares PTYFS node-management types and functions. `node_t` is an unsigned integer index. `struct node_data` stores the metadata associated with an allocated PTY slave node: device number, mode, uid, gid, and ctime.

The public interface supports initializing the node table, setting/updating a node by index, clearing a node, retrieving node data by index, and retrieving the maximum node index bound used for validation and iteration.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/node.h -->