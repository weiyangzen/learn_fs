# subset-b-005601 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/file.c -->
# sources/distributed-fs/ceph-client/fs/adfs/file.c

## Purpose
`file.c` supplies the VFS operation tables for regular files in the Acorn Disc Filing System driver. It is intentionally thin: the real block mapping and metadata translation live in `inode.c`, while this file exposes generic Linux file helpers through ADFS-specific operation tables.

## Important APIs, types, and functions
The exported tables are `adfs_file_operations` and `adfs_file_inode_operations`. Regular-file operations use `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `simple_fsync`, and `filemap_splice_read`. The inode table wires `.setattr` to `adfs_setattr`.

## Control flow
`adfs_iget()` assigns these tables to regular files. VFS read, write, mmap, splice, seek, fsync, and setattr requests then dispatch through generic helpers, which rely on the inode mapping operations in `inode.c` for folio I/O and block translation.

## State and persistence
This file owns no state. Persistent effects are indirect: writes and attribute updates flow into ADFS inode/private fields and directory-entry writeback.

## Dependencies and integration points
It depends on `adfs.h`, VFS file operation contracts, address-space operations installed elsewhere, and `adfs_setattr()`.

## Risks and test signals
Risks are mismatches between generic write paths and ADFS's limited allocation/truncation support. Test signals include regular file read/write smoke tests, mmap read tests, splice reads, fsync on read-only and writable builds, and setattr coverage for mode, time, and size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/adfs/inode.c

## Purpose
`inode.c` translates ADFS object records into Linux inodes and implements regular-file address-space behavior, attribute conversion, timestamp conversion, setattr, and directory-entry metadata writeback.

## Important APIs, types, and functions
Key entry points are `adfs_iget()`, `adfs_setattr()`, and `adfs_write_inode()`. Internal helpers include `adfs_get_block()`, `adfs_read_folio()`, `adfs_writepages()`, `adfs_write_begin()`, `_adfs_bmap()`, `adfs_atts2mode()`, `adfs_mode2atts()`, `adfs_adfs2unix_time()`, and `adfs_unix2adfs_time()`. The file defines `adfs_aops` for buffer-head based regular-file I/O.

## Control flow
`adfs_iget()` creates a new inode from an `object_info`, fills UID/GID from superblock defaults, stores ADFS parent/object/load/exec/attribute fields, converts permissions and time, then attaches directory or regular-file operations. Reads call `block_read_full_folio()` and map logical blocks through `__adfs_block_map()`. Write begin uses `cont_write_begin()`, but block creation returns `-EIO`, so the implementation remains allocation-limited. `adfs_write_inode()` reconstructs an `object_info` and delegates to `adfs_dir_update()`.

## State and persistence
Per-inode ADFS state includes `parent_id`, `indaddr`, `loadaddr`, `execaddr`, `attr`, and `mmu_private`. ADFS uses object IDs as inode numbers because metadata is stored in directories, so parent stability matters for writeback.

## Dependencies and integration points
It depends on `adfs_map_lookup()` through block mapping, directory update code, generic writeback/mpage helpers, VFS setattr validation, and superblock masks for permission translation.

## Risks and test signals
Risks include unsupported allocation/truncation paths, cross-directory rename assumptions, lossy permission conversion, stamped versus unstamped timestamp handling, and inode-number aliasing. Test signals include iget for dirs/files/symlinks, filetype `0xfc0` and `0xfe6`, chmod/chown rejection, mtime centisecond round trips, bmap, and writeback after setattr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/map.c -->
# sources/distributed-fs/ceph-client/fs/adfs/map.c

## Purpose
`map.c` reads, validates, scans, and queries the ADFS free/object map. The map is a zone-based bitstream of variable-length fragments whose fragment IDs identify file and directory extents.

## Important APIs, types, and functions
Public functions are `adfs_read_map()`, `adfs_free_map()`, `adfs_map_lookup()`, and `adfs_map_statfs()`. Important helpers include `lookup_zone()`, `scan_free_map()`, `scan_map()`, `adfs_calczonecheck()`, `adfs_checkmap()`, `adfs_map_layout()`, `adfs_map_read()`, and `adfs_map_relse()`. `GET_FRAG_ID` extracts unaligned little-endian bitfields.

## Control flow
Mount passes a valid disc record to `adfs_read_map()`, which computes zone count, bits-per-map-block conversions, IDs per zone, the central map address, allocates descriptors, reads zone buffers, and validates per-zone and cross checksums. `adfs_map_lookup()` chooses a starting zone from the fragment ID, converts sector offset to map-bit offset, scans zones under `adfs_map_lock`, and returns a physical sector or reports corruption.

## State and persistence
The in-memory `adfs_discmap` array holds buffer_heads and zone bit ranges. On-disk map state persists as checksum-protected zone sectors. This file only reads and releases maps; allocation updates are not implemented here.

## Dependencies and integration points
It integrates with `adfs_fill_super()`, `adfs_get_block()`, statfs, buffer_head I/O, little-endian bit helpers, and ADFS disc-record fields such as `log2bpmb`, `zone_spare`, and `idlen`.

## Risks and test signals
Risks include malformed fragment chains, oversized fragments, invalid free-list links, id-length limits, shift/sign errors in map-to-sector conversion, and checksum false positives. Test signals include valid F/F+ images, corrupt zonecheck and crosscheck images, root fragment lookup, large fragmented files, free-space statfs accuracy, and out-of-range fragment IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/super.c -->
# sources/distributed-fs/ceph-client/fs/adfs/super.c

## Purpose
`super.c` implements ADFS filesystem registration, mount context parsing, disc-record probing, superblock setup, inode-cache lifecycle, statfs, remount option handling, and teardown.

## Important APIs, types, and functions
Key functions are `adfs_init_fs_context()`, `adfs_parse_param()`, `adfs_get_tree()`, `adfs_fill_super()`, `adfs_probe()`, `adfs_validate_bblk()`, `adfs_validate_dr0()`, `adfs_put_super()`, `adfs_statfs()`, and `adfs_reconfigure()`. Module entry/exit are `init_adfs_fs()` and `exit_adfs_fs()`. `adfs_sops` defines superblock operations.

## Control flow
Mount allocates `adfs_sb_info`, parses `uid`, `gid`, `ownmask`, `othmask`, and `ftsuffix`, then probes either the boot-block disc record or single-zone disc record. After `adfs_read_map()` succeeds, it selects F or F+ directory operations, constructs a synthetic root `object_info`, creates the root inode, and installs default dentry operations. Reconfigure syncs and structure-copies parsed options into the live superblock info.

## State and persistence
Superblock state includes ownership/mask options, directory layout operations, name length, map metadata, and UID/GID policy. Persistent media state is read from the disc record and map; teardown releases map buffers and RCU-frees the superblock info.

## Dependencies and integration points
It depends on block-device mounting, `fs_context`, buffer_head probing, ADFS map and directory backends, slab inode caches, and VFS statfs/show_options contracts.

## Risks and test signals
Risks include invalid disc-record acceptance, block-size retry errors, option-copying pointer/state bugs on remount, root object synthesis mismatches, and cleanup leaks after partial mount failure. Test signals include boot-block and DR0 images, 256/512/1024-byte sectors, F and F+ roots, mount option display, remount option changes, silent mount failures, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/affs/Kconfig

## Purpose
This Kconfig entry exposes Amiga Fast File System support as `AFFS_FS`.

## Important APIs, types, and functions
It is declarative build configuration. `AFFS_FS` is a tristate depending on `BLOCK`, selecting `BUFFER_HEAD` and `LEGACY_DIRECT_IO`. Help text documents read/write support for Amiga FFS partitions and loop-mounted emulator disk images.

## Control flow
When enabled as built-in or module, kbuild descends through the AFFS Makefile and builds `affs.o`; otherwise no AFFS code is compiled.

## State and persistence
The only state is `.config` selection. Runtime state is in the compiled filesystem driver.

## Dependencies and integration points
The dependency on block devices and selected buffer-head/direct-I/O helpers matches AFFS's buffer_head-based metadata and direct-I/O implementation in `file.c`.

## Risks and test signals
Risks are stale dependency declarations or missing helper selections causing randconfig build failures. Test signals include `AFFS_FS=y`, `AFFS_FS=m`, `BLOCK=n`, and configs with or without legacy direct I/O support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/Makefile -->
# sources/distributed-fs/ceph-client/fs/affs/Makefile

## Purpose
The AFFS Makefile maps `CONFIG_AFFS_FS` to the composite `affs.o` filesystem module or built-in object.

## Important APIs, types, and functions
It defines `obj-$(CONFIG_AFFS_FS) += affs.o` and composes `affs-objs` from `super.o`, `namei.o`, `inode.o`, `file.o`, `dir.o`, `amigaffs.o`, `bitmap.o`, and `symlink.o`.

## Control flow
kbuild evaluates `CONFIG_AFFS_FS` and links the listed object files into one AFFS driver object. The commented `ccflags-y` debug line indicates optional local debug builds.

## State and persistence
This file has build-graph state only.

## Dependencies and integration points
It must stay synchronized with `Kconfig`, exported symbols in `affs.h`, and module metadata in `super.c`.

## Risks and test signals
Risks include missing a new source file from `affs-objs`, stale object names after file renames, or debug flags leaking into builds. Test signals are module and built-in builds plus link checks for all AFFS object exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/affs.h -->
# sources/distributed-fs/ceph-client/fs/affs/affs.h

## Purpose
`affs.h` is the private interface for the AFFS driver. It defines in-memory inode/superblock structures, mount flags, block/tail access macros, function declarations, operation-table exports, checksum helpers, and locking wrappers.

## Important APIs, types, and functions
Important types are `struct affs_inode_info`, `struct affs_bm_info`, `struct affs_sb_info`, and `struct affs_ext_key`. Key macros are `AFFS_HEAD`, `AFFS_TAIL`, `AFFS_ROOT_HEAD`, `AFFS_ROOT_TAIL`, `AFFS_DATA_HEAD`, `AFFS_BLOCK`, and mount flag helpers. Inline helpers validate block ranges, read/get/zero/get-empty blocks, adjust checksums, release buffer_heads, and lock link, directory/hash, and extension state.

## Control flow
Most AFFS source files include this header and use it to interpret on-disk blocks as header/tail/data structures. VFS operations call functions declared here across source-file boundaries, while locking helpers serialize directory hash chains, hard-link chains, and extension-block caches.

## State and persistence
`affs_inode_info` persists runtime state such as open count, extension caches, metadata buffer tracking, preallocation, `mmu_private`, protection bits, and cached extension buffer. `affs_sb_info` stores mount policy, root block, bitmap cache, symlink prefix/volume, delayed superblock work, and root buffer.

## Dependencies and integration points
The header integrates AFFS with VFS inodes, buffer_heads, metadata buffer tracking, workqueues, mutexes, spinlocks, and Amiga on-disk structures from `amigaffs.h`.

## Risks and test signals
Risks include macro offset mistakes, checksum delta errors, invalid block-boundary assumptions, lock-order inversions, and stale declarations. Test signals include sparse/build coverage, lockdep under create/unlink/rename/write, invalid block reads, and checksum validation after metadata mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/affs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/amigaffs.c -->
# sources/distributed-fs/ceph-client/fs/affs/amigaffs.c

## Purpose
`amigaffs.c` implements low-level AFFS metadata manipulation: directory hash insertion/removal, hard-link chain removal, object header removal, block checksums, Amiga timestamp conversion, protection-bit translation, error reporting, and filename validation/copying.

## Important APIs, types, and functions
Public functions include `affs_insert_hash()`, `affs_remove_hash()`, `affs_remove_header()`, `affs_checksum_block()`, `affs_fix_checksum()`, `affs_secs_to_datestamp()`, `affs_prot_to_mode()`, `affs_mode_to_prot()`, `affs_error()`, `affs_warning()`, `affs_nofilenametruncate()`, `affs_check_name()`, and `affs_copy_name()`. Internal helpers include `affs_fix_dcache()`, `affs_remove_link()`, and `affs_empty_dir()`.

## Control flow
Create/link operations insert headers into a directory hash bucket by walking `hash_chain` to the tail and updating parent/checksum fields. Removal locks link and directory state, validates empty directories, unlinks the header from its hash chain, handles hard-link inheritance if needed, and frees link blocks. Error reporting remounts writable filesystems read-only.

## State and persistence
It mutates on-disk header tails, hash buckets, link chains, parent pointers, checksums, timestamps, and protection bits. Directory inode ctime/mtime and i_version are updated on hash changes.

## Dependencies and integration points
It is used by `namei.c`, `inode.c`, and `file.c`, and depends on buffer-head I/O, AFFS checksum layout, VFS dentry aliases, metadata buffer tracking, and mount flags.

## Risks and test signals
Risks include broken hard-link inheritance, stale `d_fsdata`, checksum delta mistakes, directory non-empty races, remount-readonly behavior on metadata errors, lossy permission mapping, and filename truncation semantics. Test signals include create/unlink/link/rename cycles, hard-link removal order, nonempty rmdir, invalid names, protection-bit round trips, and checksum verification after every mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/amigaffs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/amigaffs.h -->
# sources/distributed-fs/ceph-client/fs/affs/amigaffs.h

## Purpose
`amigaffs.h` documents and defines AFFS on-disk constants and structures, including filesystem signatures, block primary/secondary types, root/header/tail/data layouts, symlink front matter, Amiga timestamps, and protection bits.

## Important APIs, types, and functions
Important definitions include `FS_OFS`, `FS_FFS`, international and dircache variants, MUFS variants, `T_SHORT`, `T_LIST`, `T_DATA`, `ST_FILE`, `ST_USERDIR`, `ST_SOFTLINK`, `ST_LINKFILE`, `ST_ROOT`, `AFFS_ROOT_BMAPS`, `AFFS_EPOCH_DELTA`, `struct affs_date`, `struct affs_root_head`, `struct affs_root_tail`, `struct affs_head`, `struct affs_tail`, `struct slink_front`, and `struct affs_data_head`.

## Control flow
The file is declarative; other AFFS code casts buffer contents through these structures to locate hash tables, tails, bitmap references, names, link chains, extension pointers, and OFS data headers.

## State and persistence
All structures describe persistent big-endian media state. Protection macros encode classic inverted owner bits and extended group/other bits.

## Dependencies and integration points
It depends on Linux fixed-width/big-endian types and is consumed by `affs.h` and all metadata code.

## Risks and test signals
Risks include struct layout drift, incorrect tail positioning for different block sizes, endian mistakes, and misinterpreting dircache/MUFS signatures. Test signals include mounting every supported signature, checksum over block casts, symlink read/write, OFS data block parsing, bitmap-root parsing, and permission conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/amigaffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/affs/bitmap.c

## Purpose
`bitmap.c` manages AFFS free-space accounting and allocation. It initializes bitmap metadata from the root block, counts free blocks, allocates blocks with small preallocation, frees blocks, and releases bitmap caches.

## Important APIs, types, and functions
Public functions are `affs_count_free_blocks()`, `affs_free_block()`, `affs_alloc_block()`, `affs_init_bitmap()`, and `affs_free_bitmap()`.

## Control flow
Mount calls `affs_init_bitmap()` unless read-only. It checks root bitmap validity, reads bitmap blocks and extensions, validates checksums, records per-bitmap free counts, and masks unused tail bits. Allocation consumes an inode's preallocation first, otherwise locates a bitmap with free bits, reads/caches it, clears a bit, adjusts checksum, marks buffers/superblock dirty, and preallocates adjacent bits within a word. Freeing sets the bit, updates checksum/free count, and dirties state.

## State and persistence
Runtime state includes `s_bitmap`, `s_bmap_count`, `s_bmap_bits`, `s_last_bmap`, and cached `s_bmap_bh`. Persistent state is the big-endian bitmap blocks and root-block bitmap pointers. `s_bmlock` serializes all bitmap access.

## Dependencies and integration points
It integrates with block allocation in `file.c`, inode allocation in `inode.c`, metadata deletion in `amigaffs.c`, statfs in `super.c`, and delayed superblock dirtying.

## Risks and test signals
Risks include off-by-one range checks, double frees, bitmap checksum drift, stale cached bitmap buffers, invalid bitmap extensions, and preallocation leaks on close/evict. Test signals include full filesystem allocation, freeing already-free blocks, last-bitmap tail masking, remount read/write transitions, statfs free counts, and ENOSPC paths during writes and creates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/dir.c -->
# sources/distributed-fs/ceph-client/fs/affs/dir.c

## Purpose
`dir.c` provides AFFS directory file operations and readdir implementation over Amiga hash buckets and hash chains.

## Important APIs, types, and functions
Key items are `struct affs_dir_data`, `affs_dir_open()`, `affs_dir_release()`, `affs_dir_llseek()`, `affs_readdir()`, `affs_dir_operations`, and `affs_dir_inode_operations`.

## Control flow
Directory open allocates private cursor data. `readdir` emits dot entries, decodes `ctx->pos` as hash bucket and chain index, optionally resumes from cached inode number if the inode i_version cookie matches, reads the directory block, walks bucket chains, emits names from header tails, and stores resume state. Directory inode operations delegate create, lookup, link, unlink, symlink, mkdir, rmdir, rename, and setattr to namei/inode code.

## State and persistence
Runtime cursor state tracks last inode and i_version cookie. Persistent directory state is the hash table in the directory header and each entry's `hash_chain`. Directory locking uses `affs_lock_dir()`.

## Dependencies and integration points
It depends on VFS `dir_context`, generic cookie llseek, AFFS hash-chain layout, `affs_file_fsync()`, and namei operations.

## Risks and test signals
Risks include resume after mutation, 16-bit chain-position overflow, I/O errors mid-iteration, invalid name lengths, and hash-chain corruption. Test signals include large directories, seekdir/telldir style offsets, concurrent create/unlink during readdir, corrupted chain pointers, and fsync on directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/file.c -->
# sources/distributed-fs/ceph-client/fs/affs/file.c

## Purpose
`file.c` implements AFFS regular-file I/O, logical-to-physical block mapping, extension-block caches, OFS data-block handling, truncation, preallocation cleanup, fsync, and VFS file/address-space operation tables.

## Important APIs, types, and functions
Key functions include `affs_get_block()`, `affs_get_extblock_slow()`, `affs_alloc_extblock()`, `affs_grow_extcache()`, `affs_read_folio()`, `affs_write_begin()`, `affs_write_end()`, `affs_direct_IO()`, OFS variants `affs_read_folio_ofs()`, `affs_write_begin_ofs()`, `affs_write_end_ofs()`, `affs_extent_file_ofs()`, plus `affs_free_prealloc()`, `affs_truncate()`, and `affs_file_fsync()`.

## Control flow
FFS paths use buffer-head block mapping: logical blocks select an extension block, allocate missing extension/data blocks when creating, update header tables/checksums, and use generic buffered/direct I/O helpers. OFS paths account for 24-byte data headers, copy payload data between folios and `AFFS_DATA()`, maintain `next` links, sequence numbers, sizes, and checksums. File release truncates if `i_size` differs from `mmu_private` and frees preallocations. Truncate frees data and extension blocks beyond the new EOF.

## State and persistence
Runtime state includes extension linear/associative caches, cached extension buffer, block counts, extension counts, `mmu_private`, last allocation, and preallocation count. Persistent state includes data block pointers, extension chains, OFS data headers, first-data pointers, checksums, and archived protection bit clearing.

## Dependencies and integration points
It depends on bitmap allocation, metadata buffer tracking, VFS writeback/mpage/direct I/O helpers, `affs.h` block macros, and inode dirtying.

## Risks and test signals
Risks include extension-cache stale entries, checksum delta mistakes, partial-write OFS consistency, preallocation leaks, sparse/growing file edge cases, direct I/O beyond `mmu_private`, and truncate freeing wrong chains. Test signals include FFS and OFS read/write, append, hole extension, short writes, direct I/O fallback, large files spanning many extensions, close-time truncate, fsync, ENOSPC, and archived-bit clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/inode.c -->
# sources/distributed-fs/ceph-client/fs/affs/inode.c

## Purpose
`inode.c` maps AFFS header blocks to Linux inodes, writes inode metadata back to disk, handles setattr/truncate, evicts inodes, allocates new header blocks, and creates directory entries.

## Important APIs, types, and functions
Public entry points are `affs_iget()`, `affs_write_inode()`, `affs_setattr()`, `affs_evict_inode()`, `affs_new_inode()`, and `affs_add_entry()`.

## Control flow
`affs_iget()` reads and checksums a header block, interprets the tail stype, converts protection/UID/GID/time, initializes extension/preallocation caches, and installs file, directory, or symlink operations. `affs_write_inode()` updates tail protection, size, timestamps, UID/GID, root change time, checksums, and metadata buffers. `affs_setattr()` validates option-controlled permission changes and calls `affs_truncate()` for size changes. `affs_add_entry()` initializes a file/dir/link/symlink header and inserts it into the target directory hash.

## State and persistence
It initializes per-inode runtime caches and writes persistent header tails: mode/protection, size, UID/GID, timestamps, names, parents, link chains, and stype.

## Dependencies and integration points
It integrates with bitmap allocation/free, file truncation, namei operations, symlink aops, metadata buffer tracking, and mount flags such as `setuid`, `setgid`, `mode`, `mufs`, `ofs`, and `protect`.

## Risks and test signals
Risks include bad inode acceptance, UID/GID MUFS translation errors, mode override behavior, link-chain nlink approximation, dirty metadata ordering, and freeing header blocks on eviction. Test signals include iget for root/files/dirs/symlinks, chmod/chown under mount policies, create/link/symlink entry creation, truncate on setattr, eviction of unlinked files, and writeback checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/namei.c -->
# sources/distributed-fs/ceph-client/fs/affs/namei.c

## Purpose
`namei.c` implements AFFS namespace operations: case-folded hashing/comparison, lookup, create, mkdir, unlink, rmdir, symlink creation, hard links, rename/exchange, and NFS export helpers.

## Important APIs, types, and functions
Key functions are `affs_hash_name()`, `affs_lookup()`, `affs_create()`, `affs_mkdir()`, `affs_unlink()`, `affs_rmdir()`, `affs_symlink()`, `affs_link()`, `affs_rename2()`, `affs_rename()`, `affs_xrename()`, `affs_get_parent()`, and export/dentry operation tables. Internal case helpers are `affs_toupper()` and `affs_intl_toupper()`.

## Control flow
Lookups hash a case-folded name to a directory bucket, walk the hash chain, store the real header block in `d_fsdata`, and follow file-link originals. Create/mkdir allocate inodes and insert headers. Symlink creation rewrites absolute paths using the configured volume name and collapses simple `.`/`..` syntax into AFFS representation. Rename removes source and optional destination headers, changes the stored name, then inserts into the new directory; exchange swaps two headers.

## State and persistence
Persistent namespace state is encoded in directory hash tables, header names, parent pointers, link chains, originals, and symlink payloads. Dentry state uses AFFS-specific casefolding and `d_fsdata` header keys.

## Dependencies and integration points
It depends on `amigaffs.c` hash/removal helpers, inode allocation, AFFS mount flags, VFS dentry operations, and generic exportfs helpers.

## Risks and test signals
Risks include 30-byte truncation ambiguity, international case folding, rename rollback gaps, hard-link and `d_fsdata` consistency, exchange error handling, and symlink path rewriting. Test signals include case-insensitive lookup, no-truncate mode, create/unlink/mkdir/rmdir/link, rename overwrite and exchange, NFS filehandle lookup, and absolute/relative symlink round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/super.c -->
# sources/distributed-fs/ceph-client/fs/affs/super.c

## Purpose
`super.c` implements AFFS filesystem registration, mount option parsing, root block probing, format detection, bitmap initialization, superblock operations, delayed superblock timestamp flushing, remount handling, statfs, and teardown.

## Important APIs, types, and functions
Important functions include `affs_init_fs_context()`, `affs_parse_param()`, `affs_fill_super()`, `affs_reconfigure()`, `affs_mark_sb_dirty()`, `affs_commit_super()`, `affs_sync_fs()`, `affs_put_super()`, `affs_kill_sb()`, `affs_statfs()`, and module init/exit. `struct affs_context` holds parsed mount options.

## Control flow
Mount parses options such as `bs`, `mode`, `mufs`, `nofilenametruncate`, `prefix`, `protect`, `reserved`, `root`, `setuid`, `setgid`, `verbose`, and `volume`. It probes possible block sizes/root positions, validates root block checksum/type, reads the boot signature to detect OFS/FFS/INTL/MUFS/dircache variants, forces unsupported dircache writes read-only, initializes bitmap state, creates the root inode, selects dentry casefold ops, and installs export ops.

## State and persistence
Runtime superblock state includes root block buffer, bitmap cache, flags, UID/GID/mode overrides, symlink prefix/volume, delayed work, and locks. Persistent state touched here is the root block disk-change timestamp and checksum.

## Dependencies and integration points
It depends on block devices, fs_context, AFFS bitmap/inode code, workqueues, seq_file option display, and VFS mount/sync/statfs APIs.

## Risks and test signals
Risks include mount failure cleanup leaks, incorrect root-block detection on odd-sized partitions, dircache read/write policy, remount read/write bitmap transitions, delayed work after unmount, and symlink prefix races. Test signals include all supported boot signatures, explicit and probed block sizes, read-only dircache mounts, remount option changes, statfs free counts, delayed superblock flush, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/affs/symlink.c

## Purpose
`symlink.c` reads AFFS symbolic-link payloads and translates Amiga volume/assign syntax into Linux path strings exposed through the pagecache link helper.

## Important APIs, types, and functions
The main function is `affs_symlink_read_folio()`. Exported tables are `affs_symlink_aops` and `affs_symlink_inode_operations`, using `page_get_link` and `affs_setattr()`.

## Control flow
The read-folio path reads the symlink header block, treats its front as `struct slink_front`, optionally expands a `volume:` or `assign:` prefix with `s_prefix`, converts doubled slashes into parent-directory markers, copies up to the page-sized link buffer, terminates with NUL, marks the folio uptodate, and unlocks it.

## State and persistence
Persistent symlink data is stored inline in the header block's `symname` area. Runtime prefix and volume settings are protected by `symlink_lock`.

## Dependencies and integration points
It integrates with `affs_iget()` and `affs_symlink()` for symlink inode setup, `page_get_link`, buffer-head reads, and mount options `prefix` and `volume`.

## Risks and test signals
Risks include truncation to 1023 bytes, prefix races, malformed non-NUL payloads, volume/assign interpretation differences, and read I/O errors. Test signals include absolute and relative symlinks, assign-containing links, prefix remount changes, long symlinks, double-slash parent encoding, and corrupted/missing header blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/affs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/afs/Kconfig

## Purpose
This Kconfig file exposes the Linux AFS client, optional dynamic debugging, local caching support, and server cursor debugging.

## Important APIs, types, and functions
Symbols are `AFS_FS`, `AFS_DEBUG`, `AFS_FSCACHE`, and `AFS_DEBUG_CURSOR`. `AFS_FS` depends on `INET` and selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.

## Control flow
Selecting `AFS_FS` causes kbuild to build `kafs.o`; optional symbols enable debug or cache code paths compiled elsewhere.

## State and persistence
Only build-time `.config` state is stored. Runtime state is in the AFS client module.

## Dependencies and integration points
The selected dependencies match AFS's RxRPC transport, DNS-based cell/VL discovery, netfs integration, and Kerberos/RxGK support.

## Risks and test signals
Risks include dependency drift as security and netfs code changes. Test signals include built-in/module builds, `INET=n`, fscache matrix builds, dynamic-debug configs, and randconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/Makefile -->
# sources/distributed-fs/ceph-client/fs/afs/Makefile

## Purpose
The AFS Makefile links the kAFS client from many subsystem objects and conditionally includes procfs support.

## Important APIs, types, and functions
It defines `kafs-y` with address, callback, cell, directory, file, fsclient, RxRPC, security, server, superblock, VL, volume, write, xattr, and YFS client objects. `kafs-$(CONFIG_PROC_FS)` adds `proc.o`, and `obj-$(CONFIG_AFS_FS) := kafs.o` links the composite object.

## Control flow
kbuild includes the complete AFS client object list when `AFS_FS` is enabled and omits procfs integration when `CONFIG_PROC_FS` is disabled.

## State and persistence
This is build-graph state only.

## Dependencies and integration points
It must remain synchronized with Kconfig dependencies and cross-file symbols in `internal.h`.

## Risks and test signals
Risks include missing newly introduced objects, link failures when procfs is disabled, or stale object names. Test signals include `AFS_FS=y/m`, `PROC_FS=n`, and full symbol link checks under security feature matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/addr_list.c -->
# sources/distributed-fs/ceph-client/fs/afs/addr_list.c

## Purpose
`addr_list.c` manages RxRPC peer address lists for AFS servers and VL servers, including allocation/refcounting, parsing textual address lists, DNS lookup results, merging IPv4/IPv6 peers, and updating peer appdata pointers.

## Important APIs, types, and functions
Key functions are `afs_alloc_addrlist()`, `afs_get_addrlist()`, `afs_put_addrlist()`, `afs_parse_text_addrs()`, `afs_dns_query()`, `afs_merge_fs_addr4()`, `afs_merge_fs_addr6()`, and `afs_set_peer_appdata()`.

## Control flow
Address lists are allocated with bounded capacity and freed by RCU after peer references are dropped. Text parsing counts delimited addresses, supports bracketed IPv6 and optional `+port`, parses addresses, creates RxRPC peers, and stores them in a single dummy VL-server list. DNS lookup queries AFSDB/SRV data and either extracts structured VL records or parses comma-delimited addresses. Merge functions de-duplicate and keep IPv4 and IPv6 peer ranges ordered by peer pointer.

## State and persistence
Runtime state includes refcounted `afs_addr_list` objects, RxRPC peer references, `nr_ipv4`, total address count, and per-peer appdata pointing back to an AFS server. No state persists beyond memory caches and DNS TTL consumers.

## Dependencies and integration points
It depends on DNS resolver, RxRPC peer lookup, VL server list allocation, net namespace sockets, `afs_fs.h`/VL constants, and address preferences applied elsewhere.

## Risks and test signals
Risks include parser corner cases, duplicate peer handling, peer pointer ordering assumptions, appdata clearing bugs, DNS malformed data, and address-list truncation at `AFS_MAX_ADDRESSES`. Test signals include IPv4/IPv6/bracket/port parsing, invalid inputs, DNS good/bad/empty results, duplicate addresses, peer appdata replacement, and RCU refcount lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/addr_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/addr_prefs.c -->
# sources/distributed-fs/ceph-client/fs/afs/addr_prefs.c

## Purpose
`addr_prefs.c` implements `/proc/fs/afs/addr_prefs`, allowing administrators to assign priorities to IPv4/IPv6 address or subnet matches and apply those priorities to server address lists.

## Important APIs, types, and functions
Public functions are `afs_proc_addr_prefs_write()`, `afs_get_address_preferences_rcu()`, and `afs_get_address_preferences()`. Internal helpers include `afs_split_string()`, `afs_parse_address()`, `afs_cmp_address_pref()`, `afs_insert_address_pref()`, `afs_add_address_pref()`, `afs_delete_address_pref()`, and `afs_del_address_pref()`.

## Control flow
Proc writes are parsed into line commands such as `add udp IP[/mask] priority` or `del udp IP[/mask]`. A candidate preference list is copied from the old RCU list, modified in sorted IPv4-then-IPv6 order, versioned, published through RCU, and paired with release-store version updates. Address-list application checks versions, walks peers, compares exact/subnet matches, and writes per-address priorities.

## State and persistence
State is runtime per-network-namespace RCU data: `address_prefs`, `address_pref_version`, and each address list's `addr_pref_version` plus per-address `prio`. Preferences do not persist across module/netns lifetime.

## Dependencies and integration points
It depends on procfs seq-file netns mapping, RxRPC remote-address access, Linux IP parsers, RCU, and AFS server rotation using address priorities.

## Risks and test signals
Risks include command parser ambiguity, subnet comparison ordering, version memory-ordering mistakes, list growth to 255 entries, and missed priority updates. Test signals include add/delete exact and subnet IPv4/IPv6 rules, malformed masks, multiple commands per write, RCU readers during updates, version no-op paths, and route selection with priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/addr_prefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs.h -->
# sources/distributed-fs/ceph-client/fs/afs/afs.h

## Purpose
`afs.h` defines protocol-wide AFS types, limits, identifiers, callback/status records, access masks, volume metadata, and XDR UUID layout shared across the client.

## Important APIs, types, and functions
Important definitions include cell/volume/path length limits, `afs_volid_t`, `afs_vnodeid_t`, `afs_dataversion_t`, `afs_voltype_t`, `afs_file_type_t`, `afs_lock_type_t`, `struct afs_fid`, `struct afs_callback`, `struct afs_callback_break`, `struct afs_uuid`, `struct afs_volume_info`, `afs_access_t` ACE bits, `struct afs_file_status`, `struct afs_status_cb`, status-change flags, `struct afs_volsync`, `struct afs_volume_status`, `AFS_BLOCK_SIZE`, and `struct afs_uuid__xdr`.

## Control flow
This header is declarative. Client RPC, inode, volume, validation, callback, and security code use these types to encode/decode wire data and represent cached metadata.

## State and persistence
The structures represent runtime state derived from remote AFS servers and wire-persistent identifiers such as volume IDs, vnode IDs, uniquifiers, callbacks, and status data.

## Dependencies and integration points
It integrates with file service, volume location, cache manager, YFS, and RxRPC client code.

## Risks and test signals
Risks include width/endian mistakes, limit mismatches against protocol specs, and stale shared type assumptions. Test signals include XDR encode/decode tests, large vnode/volume IDs, callback break records, file status conversion, ACL masks, and YFS high-vnode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_cm.h -->
# sources/distributed-fs/ceph-client/fs/afs/afs_cm.h

## Purpose
`afs_cm.h` defines AFS cache-manager service constants and operation IDs for server-to-client callback RPCs.

## Important APIs, types, and functions
It defines `AFS_CM_PORT`, `CM_SERVICE`, `enum AFS_CM_Operations`, and `AFS_CAP_ERROR_TRANSLATION`. Operation IDs include `CBCallBack`, `CBInitCallBackState`, `CBProbe`, `CBInitCallBackState3`, `CBProbeUuid`, and `CBTellMeAboutYourself`.

## Control flow
`cmservice.c` dispatches incoming RxRPC calls by these operation IDs and selects the corresponding call type/deliver/work handlers.

## State and persistence
There is no runtime state in the header. Constants define wire protocol behavior.

## Dependencies and integration points
It is consumed by cache-manager service and security code and must align with AFS/YFS protocol expectations.

## Risks and test signals
Risks include wrong operation IDs or service IDs causing callback dispatch failures. Test signals include incoming callback RPC decoding, probe/probeuuid behavior, capability replies, and unsupported-operation rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_fs.h -->
# sources/distributed-fs/ceph-client/fs/afs/afs_fs.h

## Purpose
`afs_fs.h` defines AFS file service port/service IDs, operation IDs, and file-server abort/error codes.

## Important APIs, types, and functions
It declares `AFS_FS_PORT`, `FS_SERVICE`, `enum AFS_FS_Operations`, and `enum AFS_FS_Errors`. Operations cover fetch/store data/status/ACL, create/remove/rename/link/symlink/mkdir/rmdir, callback relinquish, volume information/status, locks, lookup, inline bulk status, 64-bit data operations, and capabilities.

## Control flow
RPC client code uses these constants when constructing file-server calls and interpreting protocol aborts.

## State and persistence
No runtime state is stored here; constants model wire protocol contract.

## Dependencies and integration points
It integrates with fsclient/yfsclient, server rotation, error translation, and callback/security code that validates service IDs.

## Risks and test signals
Risks are incorrect IDs or error-code signs breaking interoperability. Test signals include wire traces for every operation family, abort-code translation tests, and compatibility with legacy and extended file-server RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_vl.h -->
# sources/distributed-fs/ceph-client/fs/afs/afs_vl.h

## Purpose
`afs_vl.h` defines Volume Location service constants, operation IDs, VL error codes, YFS endpoint tags, VLDB entry structures, and XDR layouts.

## Important APIs, types, and functions
Key definitions include `AFS_VL_PORT`, `VL_SERVICE`, `YFS_VL_SERVICE`, `enum AFSVL_Operations`, `enum AFSVL_Errors`, YFS server/endpoint enums, `YFS_MAXENDPOINTS`, `struct afs_vldbentry`, `AFS_VLF_*` and `AFS_VLSF_*` flags, `struct afs_ListAddrByAttributes__xdr`, and `struct afs_uvldbentry__xdr`.

## Control flow
VL client and rotation code use these constants and structures to query volume records, server UUID/address data, capabilities, endpoints, and cell names.

## State and persistence
The structures represent remote persistent VLDB content and transient decoded results in the client.

## Dependencies and integration points
It depends on common AFS identifiers from `afs.h` and integrates with `vlclient.c`, DNS/cell setup, server list construction, and YFS upgrades.

## Risks and test signals
Risks include fixed array-size mismatches, XDR padding errors, UUID/server-index confusion, and VL error translation drift. Test signals include legacy and UUID VL entry queries, YFS endpoint decoding, max server lists, bad VLDB entries, and all VL error mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/afs_vl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/callback.c -->
# sources/distributed-fs/ceph-client/fs/afs/callback.c

## Purpose
`callback.c` handles AFS callback invalidation: mmap invalidation work, server-wide callback state reset, volume-level callback breaks, vnode-level callback breaks, and grouping callback break requests by volume.

## Important APIs, types, and functions
Public functions are `afs_invalidate_mmap_work()`, `afs_init_callback_state()`, `__afs_break_callback()`, `afs_break_callback()`, and `afs_break_callbacks()`. Internal helpers include `afs_volume_init_callback()`, `afs_lookup_volume_rcu()`, `afs_break_volume_callback()`, `afs_break_one_callback()`, and `afs_break_some_callbacks()`.

## Control flow
Server callback reset iterates volumes served by that server, clears expiry promises, and invalidates open mmaps. Individual callback breaks look up the relevant volume under RCU/seqlock protection, identify volume-wide breaks by zero vnode/unique, otherwise find matching inodes by fid and clear promises under vnode callback locks. File mmaps are unmapped asynchronously so future faults revalidate.

## State and persistence
Runtime state includes vnode callback promises, callback break counters, volume callback break counters, mmap tracking lists, server-volume expiry fields, and permit caches. No durable state exists; remote callbacks drive cache coherency.

## Dependencies and integration points
It integrates with `cmservice.c` callback RPC delivery, AFS inode lookup, volume/server lists, lock wait wakeups, pagecache/mmap invalidation, RCU, seqlocks, and workqueues.

## Risks and test signals
Risks include races with new inodes, RCU volume lookup retries, missed mmap invalidations, volume-wide breaks with missing volumes, and lock-state wakeups. Test signals include CB.CallBack for vnode and volume breaks, InitCallBackState, mmap invalidation under mapped files, deleted-file callbacks, lock callback wakeups, and concurrent volume tree mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cell.c -->
# sources/distributed-fs/ceph-client/fs/afs/cell.c

## Purpose
`cell.c` manages AFS cell records within a network namespace: lookup/allocation, root-cell setup, DNS/VL server refresh, procfs activation, reference and active-use lifetimes, garbage collection, timers, and purge.

## Important APIs, types, and functions
Key public functions are `afs_find_cell()`, `afs_lookup_cell()`, `afs_cell_init()`, `afs_get_cell()`, `afs_put_cell()`, `afs_use_cell()`, `afs_unuse_cell()`, `afs_see_cell()`, `afs_queue_cell()`, `afs_set_cell_timer()`, and `afs_cell_purge()`. Internal helpers include `afs_alloc_cell()`, `afs_update_cell()`, `afs_manage_cell()`, `afs_activate_cell()`, `afs_deactivate_cell()`, and `afs_has_cell_expired()`.

## Control flow
Lookups search the netns rb-tree under `cells_lock`, preallocate a candidate if absent, insert it with RCU rb-linking, optionally queue DNS lookup, and wait for setup unless the caller requested preload/dynroot behavior. The manager work item activates proc entries, refreshes VL server lists from DNS with TTL clamping, transitions cell states, schedules future management, or removes inactive cells by purging servers and root volume references. Purge unpins the workstation cell and waits for outstanding cells to be destroyed.

## State and persistence
Runtime state includes cell rb-tree/proc links, name/key descriptor, VL server list RCU pointer, DNS source/status/expiry/count, state/error, active/ref counts, timers, volumes and file-server trees, alias/root-volume links, anonymous key, and dynroot inode ID.

## Dependencies and integration points
It depends on DNS resolver, address parsing, VL server lists, procfs cell setup, server/volume management, keyring/security, net namespace lifetime, workqueues, timers, RCU, rbtrees, and IDR.

## Risks and test signals
Risks include state-machine races, DNS error classification, TTL clamping, candidate insertion races, use/ref imbalance, root-cell pinning leaks, purge hangs, and procfs list ordering. Test signals include rootcell strings with/without VL addresses, invalid names, concurrent lookups, DNS success/temp/fail/notfound, GC after inactivity, netns teardown purge, and cell reactivation during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cm_security.c -->
# sources/distributed-fs/ceph-client/fs/afs/cm_security.c

## Purpose
`cm_security.c` handles cache-manager-side RxRPC security challenge responses, including RxKAD/RxGK responses and optional creation of YFS RxGK callback appdata/token material.

## Important APIs, types, and functions
Public functions are `afs_process_oob_queue()` and, under `CONFIG_RXGK`, `afs_create_token_key()`. Internal functions include `afs_respond_to_challenge()` and `afs_create_yfs_cm_token()`. Constants include `RXGK_SERVER_ENC_TOKEN`, `xdr_round_up()`, and `xdr_len_object()`.

## Control flow
The OOB worker dequeues RxRPC out-of-band messages, responds to challenges for FS/VL/YFS services, rejects unknown services or unsupported security classes, and delegates to rxkad/rxgk helpers. YFS RxGK challenges may lazily create per-server callback appdata: random callback key, encrypted token container, client/server UUIDs, capability vector, and Kerberos-encrypted token payload.

## State and persistence
Runtime state includes the AFS netns cache-manager token key, per-server `cm_rxgk_appdata`, and random callback keys. These are in-memory security artifacts and are not persistent.

## Dependencies and integration points
It depends on RxRPC OOB APIs, RxKAD/RxGK helpers, Linux keyrings, Kerberos crypto, server peer appdata, AFS/YFS service IDs, and net/server UUIDs.

## Risks and test signals
Risks include accepting unknown challenge contexts, appdata size/XDR padding mistakes, enctype mismatch, token-key absence, random-key handling, and races in lazy server appdata creation. Test signals include RxKAD and RxGK challenge paths, unsupported security rejection, YFS callback challenge with appdata creation, keyring allocation failure, enctype absence, crypto failure injection, and repeated concurrent challenges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cm_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cmservice.c -->
# sources/distributed-fs/ceph-client/fs/afs/cmservice.c

## Purpose
`cmservice.c` implements the incoming AFS/YFS cache-manager RxRPC service. It dispatches callback/probe/capability operations, unmarshals request payloads, schedules work handlers, breaks callbacks before replying, and sends replies or aborts.

## Important APIs, types, and functions
The public dispatcher is `afs_cm_incoming_call()`. Important call types are `afs_SRXCBCallBack`, `afs_SRXCBInitCallBackState`, `afs_SRXCBInitCallBackState3`, `afs_SRXCBProbe`, `afs_SRXCBProbeUuid`, `afs_SRXCBTellMeAboutYourself`, and `afs_SRXYFSCB_CallBack`. Delivery/work handlers include `afs_deliver_cb_callback()`, `SRXAFSCB_CallBack()`, `afs_deliver_cb_init_call_back_state*()`, `SRXAFSCB_InitCallBackState()`, `afs_deliver_cb_probe*()`, `SRXAFSCB_Probe*()`, `afs_deliver_cb_tell_me_about_yourself()`, `SRXAFSCB_TellMeAboutYourself()`, and `afs_deliver_yfs_cb_callback()`.

## Control flow
Incoming calls are matched by operation ID and service. Deliver functions incrementally extract XDR data across network fragments, validate counts, allocate request buffers, and transition to server reply state. Work handlers perform actions: break callbacks before replying, reset callback state, answer probes, compare UUIDs for ProbeUuid, and return interface/capability data for TellMeAboutYourself.

## State and persistence
Per-call runtime state includes unmarshalling stage, temporary buffer, callback count arrays, UUID request buffers, server/net references, and reply state. It mutates callback cache state through `callback.c` but stores no durable data.

## Dependencies and integration points
It depends on RxRPC call helpers, AFS/YFS protocol constants, callback invalidation, net UUIDs, server UUIDs, tracing, workqueues, and abort/error translation.

## Risks and test signals
Risks include XDR count validation, partial receive state bugs, memory leaks in call buffers, callback reply ordering, UUID endian conversion, unsupported YFS service dispatch, and abort semantics. Test signals include CB.CallBack with zero/max/over-limit counts, mismatched callback counts, InitCallBackState3 UUID mismatch, ProbeUuid positive/negative, capability reply decoding, YFS 64-bit fid callbacks, and fragmented RxRPC delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/cmservice.c -->
