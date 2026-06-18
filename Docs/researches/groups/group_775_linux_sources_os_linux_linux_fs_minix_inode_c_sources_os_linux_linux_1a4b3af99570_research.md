# Group Research: group_775_linux_sources_os_linux_linux_fs_minix_inode_c_sources_os_linux_linux_1a4b3af99570

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/inode.c -->
# File Research: sources/os/linux/linux/fs/minix/inode.c

## Purpose
Implements the Minix filesystem superblock lifecycle, inode cache, inode read/write translation, page-cache address-space operations, and module registration. It is the central glue between the Linux VFS and Minix V1/V2/V3 on-disk metadata.

## Main Responsibilities
- Mount-time superblock parsing and validation for Minix V1, V2, and V3.
- Bitmap buffer loading for inode and zone maps.
- Root inode lookup and superblock operation installation.
- In-core inode allocation/freeing through `minix_inode_cache`.
- Inode eviction, truncation, free-on-last-link, and metadata buffer synchronization.
- Read/write conversion between Linux `struct inode` and Minix V1/V2 disk inode formats.
- Address-space operations for buffered reads, writes, writeback, bmap, migration, and noop direct I/O.
- Filesystem module registration through `minix_fs_type`.

## Key Functions
- `minix_fill_super()` reads block 1, detects Minix magic/version, initializes `minix_sb_info`, loads imap/zmap blocks, validates geometry, installs `minix_sops`, and creates the root dentry.
- `minix_check_superblock()` rejects unsupported zone sizes, bad inode/data-zone geometry, insufficient bitmap blocks, and invalid V1 maximum size.
- `minix_reconfigure()` handles read-only/read-write remount transitions and preserves/restores legacy `s_state`.
- `minix_put_super()` releases bitmap buffers, superblock buffer, and `minix_sb_info`.
- `minix_evict_inode()` truncates deleted inodes, syncs metadata buffers for live inodes, invalidates Minix metadata buffer tracking, and frees unlinked inodes.
- `minix_get_block()` dispatches block mapping to `V1_minix_get_block()` or `V2_minix_get_block()`.
- `minix_set_inode()` assigns file, directory, symlink, or special-file operations according to inode mode.
- `V1_minix_iget()` / `V2_minix_iget()` load raw on-disk inode fields into VFS inodes.
- `V1_minix_update_inode()` / `V2_minix_update_inode()` write VFS inode fields back into raw Minix inode formats.
- `minix_write_inode()` synchronizes raw inode buffers, including synchronous writeback error detection.
- `minix_getattr()` fills stat data and computes block counts through version-specific block-count helpers.
- `minix_truncate()` dispatches truncation to V1 or V2/V3 indirect-tree implementations.

## Data and Control Flow
Mounting starts with `minix_get_tree()` calling `get_tree_bdev()`, which invokes `minix_fill_super()`. The superblock parser first assumes the old Minix superblock layout, then switches to Minix3 parsing if the V3 magic is present at offset 24. After version detection, it allocates a combined bitmap buffer pointer array, reads all inode and zone bitmap blocks, reserves bit zero in both maps, and fetches `MINIX_ROOT_INO`.

Inode lookup uses `iget_locked()`, then delegates raw inode loading by filesystem version. Inode operation tables and file operation tables are assigned after raw mode and device data are loaded.

Buffered file I/O uses generic block helpers with Minix block mapping. `minix_write_begin()` calls `block_write_begin()` and rolls back failed extension writes by truncating page cache and filesystem blocks.

## Important Behaviors and Edge Cases
- V3 uses its own block size and has no mutable `s_state` in the same way as V1/V2.
- V1 maximum file size is explicitly checked against the indirect-tree mapping limit.
- Deleted raw inodes with zero links are treated as stale and fail with `-ESTALE`.
- Character/block device inodes store old-style encoded device numbers in `i_zone[0]`.
- Symlink inodes use `page_get_link` and `inode_nohighmem()`.
- `minix_getattr()` intentionally uses `nop_mnt_idmap`, so stat ownership is not remapped here.
- Mounting read-write clears legacy `MINIX_VALID_FS` until unmount/remount read-only.

## Dependencies
- Internal Minix declarations from `minix.h`.
- Block and buffer helpers from `buffer_head`, `mpage`, and generic block mapping code.
- Minix bitmap/inode allocators from sibling Minix source files.
- VFS mount API through `fs_context` and `get_tree_bdev()`.

## Research Notes
This file is the Minix filesystem integration point. The actual block tree algorithms are in `itree_common.c` with V1/V2 wrappers, while directory operations are in `namei.c`. The file is conservative and legacy-oriented: fixed V1/V2 structures, old device encoding, and explicit validation around ancient filesystem geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_common.c -->
# File Research: sources/os/linux/linux/fs/minix/itree_common.c

## Purpose
Provides the generic indirect-block tree implementation used by both Minix V1 and V2/V3 block mapping and truncation code. It is included directly by `itree_v1.c` and `itree_v2.c` after each wrapper defines block type, depth, direct-block count, endian conversion, and `block_to_path()`.

## Main Responsibilities
- Resolve logical file blocks through direct and indirect block chains.
- Allocate missing direct/indirect blocks for writes.
- Splice newly allocated branches into the inode tree safely.
- Detect concurrent truncation/modification and retry lookups.
- Free data blocks and indirect subtrees during truncation.
- Compute total blocks consumed by file data and indirect metadata.

## Key Types and State
- `Indirect` stores a pointer to a block pointer slot, its observed key, and the buffer containing it.
- `pointers_lock` protects updates and validation of indirect block pointer chains.
- The including file supplies `block_t`, `DEPTH`, `DIRECT`, `i_data()`, `block_to_cpu()`, `cpu_to_block()`, and `block_to_path()`.

## Key Functions
- `add_chain()` records an observed pointer slot and value.
- `verify_chain()` checks that all recorded pointer slots still contain their observed values.
- `get_branch()` walks a block pointer chain, reading indirect blocks and returning the first missing/failed link.
- `alloc_branch()` allocates a chain of blocks, initializes intermediate indirect buffers, and frees partial allocations on failure.
- `splice_branch()` atomically attaches a new branch after verifying the parent chain has not changed.
- `get_block()` implements Linux `get_block_t` behavior: map existing blocks or allocate on `create`.
- `find_shared()` finds the shared branch point for truncation and detaches the first subtree to free.
- `free_data()` frees contiguous data block pointers.
- `free_branches()` recursively frees indirect trees.
- `truncate()` releases blocks beyond `i_size`, including partial shared branches and whole indirect subtrees.
- `nblocks()` estimates data plus metadata block count for stat reporting.

## Data and Control Flow
`get_block()` first converts the logical block into offsets using version-specific `block_to_path()`. It calls `get_branch()` to traverse existing pointers. If all links exist, it maps the buffer head. If a link is missing and creation is requested, it allocates the remaining branch and attempts to splice it into the tree. If validation fails due to concurrent truncate or mutation, it frees the new branch and retries.

Truncation computes the first logical block beyond EOF, truncates partial page-cache data, then either frees direct blocks or finds the shared indirect chain. It detaches and frees no-longer-needed subtrees, marks changed metadata buffers dirty through Minix metadata buffer tracking, updates timestamps, and marks the inode dirty.

## Important Behaviors and Edge Cases
- `-EAGAIN` is used internally when a pointer chain changes during lookup/allocation; the algorithm retries.
- Failed allocation frees all blocks already allocated for the branch.
- Indirect metadata buffers are dirtied with `mmb_mark_buffer_dirty()` so Minix can sync metadata buffers on eviction/fsync.
- Truncation tolerates unreadable indirect blocks by skipping unreadable subtrees after clearing reachable pointers.
- The code assumes the including V1/V2 file defines compatible constants before inclusion.
- Whole-subtree freeing starts at `DIRECT` indirect roots after partial branch cleanup.

## Dependencies
- Minix block allocator/free routines: `minix_new_block()` and `minix_free_block()`.
- Buffer-head APIs: `sb_bread()`, `sb_getblk()`, `brelse()`, `bforget()`, buffer locking/dirtying.
- Inode timestamp and dirtying helpers.

## Research Notes
This file is a classic shared-C-include pattern: it is not independently compiled. Its behavior changes according to V1/V2 definitions supplied by the wrapper file. The locking model focuses on protecting pointer consistency, not broad inode serialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_v1.c -->
# File Research: sources/os/linux/linux/fs/minix/itree_v1.c

## Purpose
Specializes `itree_common.c` for Minix V1, whose on-disk block pointers are 16-bit values and whose tree supports direct, single-indirect, and double-indirect addressing.

## Main Responsibilities
- Define V1 indirect-tree shape and pointer type.
- Convert logical block numbers into V1 pointer offsets.
- Expose V1 block mapping, truncation, and block-count helpers to `inode.c`.

## Key Constants and Types
- `DEPTH = 3`: direct, single indirect, double indirect.
- `DIRECT = 7`: seven direct zone pointers.
- `block_t = u16`: V1 stores 16-bit block/zone pointers.
- Single-indirect fanout is fixed at 512 entries because V1 uses 1 KiB blocks with 16-bit entries.

## Key Functions
- `block_to_cpu()` and `cpu_to_block()` are identity conversions for host-order `u16`.
- `i_data()` returns the V1 `i1_data` pointer array from `minix_inode_info`.
- `block_to_path()` maps a logical block to offsets:
  - blocks `0..6` use direct pointers;
  - next `512` blocks use pointer `7`;
  - remaining supported blocks use pointer `8` for double indirect.
- `V1_minix_get_block()` delegates to generic `get_block()`.
- `V1_minix_truncate()` delegates to generic `truncate()`.
- `V1_minix_blocks()` delegates to generic `nblocks()`.

## Important Behaviors and Edge Cases
- Negative logical blocks are rejected and logged.
- Blocks whose byte offset would exceed `s_maxbytes` are rejected by returning depth zero.
- V1 only supports double indirect addressing; V1 maximum file-size validation is also enforced in `inode.c`.

## Dependencies
- Includes `itree_common.c` after defining all required macros/types.
- Uses `minix_i()` and V1 inode data layout from `minix.h`.

## Research Notes
The file is intentionally small because all tree mechanics are shared. Its main semantic contribution is the V1 path calculation and the 16-bit pointer format.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_v2.c -->
# File Research: sources/os/linux/linux/fs/minix/itree_v2.c

## Purpose
Specializes `itree_common.c` for Minix V2 and V3, whose block pointers are 32-bit values and whose tree supports direct, single-indirect, double-indirect, and triple-indirect addressing.

## Main Responsibilities
- Define V2/V3 indirect-tree shape and pointer type.
- Calculate block pointer offsets according to current superblock block size.
- Expose V2/V3 block mapping, truncation, and block-count helpers to `inode.c`.

## Key Constants and Types
- `DIRECT = 7`: seven direct zone pointers.
- `DEPTH = 4`: direct, single, double, and triple indirect.
- `block_t = u32`: V2/V3 stores 32-bit block/zone pointers.
- `DIRCOUNT = 7`.
- `INDIRCOUNT(sb) = 1 << (sb->s_blocksize_bits - 2)`, the number of 32-bit entries in an indirect block.

## Key Functions
- `block_to_cpu()` and `cpu_to_block()` are identity conversions for host-order `u32`.
- `i_data()` returns the V2/V3 `i2_data` pointer array from `minix_inode_info`.
- `block_to_path()` maps a logical block through direct, single, double, or triple indirect offsets based on filesystem block size.
- `V2_minix_get_block()` delegates to generic `get_block()`.
- `V2_minix_truncate()` delegates to generic `truncate()`.
- `V2_minix_blocks()` delegates to generic `nblocks()`.

## Important Behaviors and Edge Cases
- Negative logical blocks are rejected and logged.
- Logical blocks whose byte offset exceeds `s_maxbytes` are rejected.
- Triple-indirect addressing places practical mapping limits far above the V1 limit.
- Fanout changes with superblock block size, so V3 larger blocks naturally increase indirect capacity.

## Dependencies
- Includes `itree_common.c` after V2/V3 definitions.
- Uses `minix_i()` and V2 inode data layout from `minix.h`.

## Research Notes
This wrapper covers both Minix V2 and V3 because their in-memory pointer tree logic is compatible. V3 differences are primarily superblock/block-size details handled by `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/itree_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/minix.h -->
# File Research: sources/os/linux/linux/fs/minix/minix.h

## Purpose
Defines Minix filesystem private VFS structures, version constants, function declarations, helpers, and bitmap bit-operation compatibility logic.

## Main Responsibilities
- Declare the in-memory Minix inode and superblock private data.
- Expose Minix inode/block allocation, raw inode access, directory, file, and tree helper APIs.
- Provide `minix_sb()` and `minix_i()` container helpers.
- Provide bitmap operation macros for native-endian, big-endian 16-bit indexed, and little-endian Minix bitmap formats.
- Define the `minix_error_inode()` logging macro.

## Key Structures
- `struct minix_inode_info`
  - Holds V1 `__u16 i1_data[16]` or V2/V3 `__u32 i2_data[16]`.
  - Tracks metadata buffer heads in `i_metadata_bhs`.
  - Embeds the VFS `struct inode`.
- `struct minix_sb_info`
  - Stores inode/zone counts, bitmap block counts, first data zone, log zone size, directory entry size, maximum name length, bitmap buffer arrays, superblock buffer, raw superblock pointer, mount state, and Minix version.

## Key Constants
- `MINIX_V1`, `MINIX_V2`, `MINIX_V3`.
- `INODE_VERSION(inode)` resolves the mounted Minix version from the superblock.
- `minix_blocks_needed(bits, blocksize)` computes bitmap block requirements.

## Declared API Groups
- Inode lifecycle and raw inode access:
  - `minix_iget()`, `minix_new_inode()`, `minix_free_inode()`.
  - `minix_V1_raw_inode()`, `minix_V2_raw_inode()`.
- Block bitmap allocation:
  - `minix_new_block()`, `minix_free_block()`, count helpers.
- File/block mapping:
  - `V1_minix_get_block()`, `V2_minix_get_block()`, truncate and block-count helpers.
- Directory operations:
  - `minix_find_entry()`, `minix_add_link()`, `minix_delete_entry()`, `minix_make_empty()`, `minix_empty_dir()`, `minix_set_link()`, `minix_dotdot()`, `minix_inode_by_name()`.
- VFS operation tables:
  - file, directory, and inode operation tables.

## Bitmap Endianness Behavior
The header supports three bitmap encodings:
- Native-endian bit operations for native Minix bitmap configurations.
- Big-endian 16-bit indexed bitmaps with custom `minix_find_first_zero_bit()` and bit-number swizzling.
- Default little-endian bit operations using Linux little-endian bit helpers.

A compile-time error rejects simultaneously enabling native-endian and big-endian 16-bit indexed modes.

## Important Behaviors and Edge Cases
- `minix_find_first_zero_bit()` has a custom implementation for big-endian 16-bit indexed bitmaps.
- `minix_test_bit()` differs between endian modes.
- The `minix_error_inode()` macro records function and line number automatically.

## Research Notes
This header is the coordination point for all Minix source files. It is especially important for understanding how old on-disk bitmap formats are abstracted behind uniform allocation helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/minix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/minix/namei.c -->
# File Research: sources/os/linux/linux/fs/minix/namei.c

## Purpose
Implements Minix directory inode operations for lookup, create, link, unlink, symlink, mkdir, rmdir, rename, mknod, and tmpfile.

## Main Responsibilities
- Connect Minix directory-entry helpers to the Linux VFS inode operations table.
- Allocate and initialize new Minix inodes for files, directories, symlinks, special files, and tmpfiles.
- Maintain link counts for hard links and directories.
- Update directory entries for unlink and rename.
- Validate Minix name length and basic link-count corruption conditions.

## Key Functions
- `add_nondir()` adds a directory link for a non-directory inode and instantiates the dentry; on failure it decrements the inode link count and drops the inode.
- `minix_lookup()` validates name length, resolves inode number with `minix_inode_by_name()`, and returns `d_splice_alias()`.
- `minix_mknod()` checks old device-number validity, allocates an inode, calls `minix_set_inode()`, marks it dirty, and links it.
- `minix_tmpfile()` creates an unlinked inode and attaches it to a tmpfile.
- `minix_create()` delegates to `minix_mknod()` with `rdev = 0`.
- `minix_symlink()` rejects symlink bodies larger than one filesystem block, creates a symlink inode, and stores the body with `page_symlink()`.
- `minix_link()` increments source link count, takes an inode reference, and adds a new directory entry.
- `minix_mkdir()` creates directory inode, increments parent and child link counts, writes `.`/`..`, and links the new directory.
- `minix_unlink()` finds and deletes the directory entry, then decrements target link count.
- `minix_rmdir()` requires an empty directory, then unlinks it and adjusts parent/child link counts.
- `minix_rename()` handles rename with and without replacement, directory `..` updates, empty-target checks, and link-count adjustment.
- `minix_dir_inode_operations` exports the operation table.

## Data and Control Flow
Most create-like operations allocate an inode through `minix_new_inode()`, initialize operations with `minix_set_inode()`, mark the inode dirty, then add a directory entry. Remove-like operations find a Minix directory entry and operate on the mapped folio before releasing it with `folio_release_kmap()`.

Rename first finds the old entry, optionally finds the old directory’s `..` entry, validates replacement target rules, updates or adds the target entry, deletes the old entry, and if moving a directory updates its `..` entry to the new parent.

## Important Behaviors and Edge Cases
- Names longer than the mounted Minix name limit return `-ENAMETOOLONG`.
- `minix_mknod()` rejects device numbers not representable by old device encoding.
- Symlink targets must fit in one block.
- `minix_unlink()` and `minix_rmdir()` detect corrupted zero/low link counts and report filesystem corruption.
- Rename supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Directory replacement during rename requires the target directory to be empty and have valid link count.
- Moving a directory increments the new parent link count before deleting the old link and updates `..`.

## Dependencies
- Directory-entry helpers declared in `minix.h`, implemented in sibling Minix directory code.
- VFS inode/dentry helpers such as `d_instantiate()`, `d_splice_alias()`, `page_symlink()`, and link-count helpers.
- Minix inode initialization from `inode.c`.

## Research Notes
This is a compact, traditional filesystem `namei` implementation. It relies on the VFS for higher-level permission checks; the file itself mostly performs filesystem-specific entry manipulation and integrity checks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/minix/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/mnt_idmapping.c -->
# File Research: sources/os/linux/linux/fs/mnt_idmapping.c

## Purpose
Implements mount idmapping objects and conversion helpers between filesystem kernel IDs, VFS IDs, and mount-relative IDs. This supports idmapped mounts where UID/GID ownership exposed through a mount may differ from the filesystem’s internal user namespace mapping.

## Main Responsibilities
- Define `struct mnt_idmap` with UID/GID maps and a reference count.
- Provide global identity and invalid mount idmaps.
- Map `kuid_t`/`kgid_t` into `vfsuid_t`/`vfsgid_t` for userspace-visible results.
- Map `vfsuid_t`/`vfsgid_t` back into filesystem `kuid_t`/`kgid_t`.
- Allocate, reference, and free mount idmaps copied from user namespaces.
- Render mount ID mappings for statmount output.

## Key Objects
- `nop_mnt_idmap`: identity mapping used for non-idmapped mounts.
- `invalid_mnt_idmap`: mapping where all IDs are invalid.
- `struct mnt_idmap`: contains `uid_map`, `gid_map`, and `refcount_t count`.

## Key Functions
- `make_vfsuid()` maps a filesystem `kuid_t` through the filesystem user namespace and down through the mount UID map.
- `make_vfsgid()` does the same for groups.
- `from_vfsuid()` maps a mount-visible VFS UID up through the mount UID map and into the filesystem user namespace.
- `from_vfsgid()` does the same for groups.
- `vfsgid_in_group_p()` checks whether a VFS GID is among the caller’s groups, or always succeeds without `CONFIG_MULTIUSER`.
- `copy_mnt_idmap()` copies a user namespace UID/GID map, including dynamically allocated extent arrays for large maps.
- `alloc_mnt_idmap()` allocates a mount idmap from a user namespace.
- `mnt_idmap_get()` / `mnt_idmap_put()` manage references, skipping global identity/invalid maps.
- `statmount_mnt_idmap()` serializes UID or GID map extents relative to the caller’s current user namespace.

## Important Behaviors and Edge Cases
- Identity map fast paths return direct wrapped kernel IDs.
- Invalid map fast paths return invalid VFS or kernel IDs.
- Initial filesystem idmapping avoids `from_kuid()`/`from_kgid()` overhead by using raw values.
- `copy_mnt_idmap()` refuses to copy an unwritten map with zero extents.
- Memory ordering in `copy_mnt_idmap()` pairs with user namespace map publication.
- Dynamic extent arrays are freed only when `nr_extents > UID_GID_MAP_MAX_BASE_EXTENTS`.
- `statmount_mnt_idmap()` skips mappings that cannot be resolved in the caller’s user namespace and returns `-EAGAIN` on seq-file overflow.

## Dependencies
- User namespace UID/GID mapping internals.
- `map_id_down()`, `map_id_up()`, and `map_id_range_up()`.
- VFS ID wrapper types from `linux/mnt_idmapping.h`.
- Seq-file output for statmount.

## Research Notes
This file is core infrastructure for idmapped mounts. It deliberately keeps raw VFS ID initialization private to this implementation, so external users construct VFS IDs only through checked mapping functions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/mnt_idmapping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/mount.h -->
# File Research: sources/os/linux/linux/fs/mount.h

## Purpose
Private VFS mount header defining internal mount namespace, mount, mountpoint, and helper APIs used by mount and path-walk code.

## Main Responsibilities
- Define `struct mnt_namespace`, `struct mount`, `struct mountpoint`, and per-CPU mount counters.
- Provide internal mount propagation and namespace flags.
- Provide helpers for converting public `vfsmount` to private `mount`.
- Provide helpers for mountpoint detection, namespace attachment, namespace RB-tree removal, fsnotify mount notifications, overmount traversal, and writer-hold flag manipulation.

## Key Structures
- `struct mnt_namespace`
  - Contains namespace identity, root mount, RB-tree of mounts, user namespace, ucounts, poll waitqueue, sequence/event counters, visible mounts, mount counts, passive refcount, and anonymous namespace flag.
- `struct mount`
  - Wraps public `struct vfsmount`.
  - Tracks parent, mountpoint, namespace linkage, child mounts, superblock mount list linkage, propagation lists, expiry, pins, visible namespace linkage, overmount, mount IDs, group ID, flags, and optional fsnotify marks.
- `struct mountpoint`
  - Hash entry for a dentry used as a mountpoint and list of mounts at that point.
- `struct mnt_pcp`
  - Per-CPU mount reference and writer counters on SMP.

## Key Helpers
- `real_mount()` converts `struct vfsmount *` to containing `struct mount *`.
- `mnt_has_parent()` tests whether a mount is not its own parent.
- `is_mounted()` checks whether a mount is attached to a real namespace.
- `__path_is_mountpoint()` tests whether a path has a child mount not undergoing sync unmount.
- `detach_mounts()` calls `__detach_mounts()` only when the dentry is a mountpoint.
- `get_mnt_ns()` increments namespace reference.
- `is_local_mountpoint()` tests local mountpoint state.
- `is_anon_ns()` and `anon_ns_root()` classify anonymous mount namespaces.
- `mnt_ns_attached()` and `mnt_ns_empty()` inspect namespace RB-tree membership.
- `move_from_ns()` removes a mount from its namespace RB-tree and visible list.
- `to_mnt_ns()` converts `ns_common` to `mnt_namespace`.
- `mnt_notify_add()` queues fsnotify namespace transition notification when needed.
- `topmost_overmount()` follows `overmount` pointers.
- `test_write_hold()`, `set_write_hold()`, `clear_write_hold()` use the low bit of `mnt_pprev_for_sb` as `WRITE_HOLD`.

## Important Behaviors and Edge Cases
- `MNT_NS_INTERNAL` is a sentinel error pointer distinct from valid namespaces.
- `move_from_ns()` updates cached first/last RB-tree nodes before erasing.
- `mnt_ns` can be observed locklessly under RCU but is normally protected by `namespace_sem`.
- `mnt_pprev_for_sb` steals its low bit for write-hold state, requiring alignment assumptions.
- Fsnotify fields and helpers compile differently under `CONFIG_FSNOTIFY`.

## Dependencies
- Public mount structures from `linux/mount.h`.
- RB-tree, hlist, list, RCU, namespace, fsnotify, and seqlock infrastructure.
- External mount code provides functions declared here, such as `__lookup_mnt()`, `__legitimize_mnt()`, `__detach_mounts()`, and `mnt_ns_from_dentry()`.

## Research Notes
This header exposes the private shape of Linux mount state that `fs/namei.c` depends on for crossing mountpoints, following `..` across mount roots, and enforcing `LOOKUP_NO_XDEV`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/mpage.c -->
# File Research: sources/os/linux/linux/fs/mpage.c

## Purpose
Provides generic multipage BIO assembly for block-mapped filesystems. It batches page-cache folios into larger BIOs for readahead, read-folio, and writeback when logical file blocks map to contiguous disk blocks.

## Main Responsibilities
- Submit multipage read and write BIOs.
- End read/write folio I/O on BIO completion.
- Build read BIOs for fully or partially mapped folios.
- Fall back to buffer-head based I/O for non-contiguous, holey, buffered, or otherwise complex folios.
- Build write BIOs for fully mapped dirty folios.
- Integrate with generic writeback iteration and cgroup writeback accounting.

## Key Functions
- `mpage_read_end_io()` ends read on every folio in a completed read BIO.
- `mpage_write_end_io()` records mapping errors and ends writeback for each folio in a write BIO.
- `mpage_bio_submit_read()` / `mpage_bio_submit_write()` install completion handlers, guard end-of-device, submit BIOs, and return `NULL`.
- `map_buffer_to_folio()` transfers a mapped/up-to-date buffer-head mapping into folio buffers or marks a same-size folio uptodate.
- `do_mpage_readpage()` maps blocks for one folio, builds contiguous read BIOs, zeroes holes at EOF, or falls back to `block_read_full_folio()`.
- `mpage_readahead()` loops over readahead folios and submits accumulated read BIOs.
- `mpage_read_folio()` reads one folio through the same path.
- `clean_buffers()` clears dirty bits for buffers covered by an outgoing write and may free buffer heads.
- `mpage_write_folio()` maps or validates one dirty folio and adds it to a write BIO or falls back to `block_write_full_folio()`.
- `__mpage_writepages()` iterates dirty folios with `writeback_iter()`, optionally delegates first to a filesystem callback, then writes through `mpage_write_folio()`.

## Read Path Behavior
The read path avoids attaching buffer heads unless necessary. It reuses previous `get_block()` results when possible, maps logical blocks for the folio, checks for holes and contiguity, zero-fills holes at EOF, and appends fully suitable folios to a BIO. If a folio already has buffers, contains a hole before non-hole data, has non-contiguous mappings, needs buffer-up-to-date handling, or cannot allocate a BIO, it falls back to `block_read_full_folio()`.

`BH_Boundary` causes accumulated BIOs to be submitted before metadata-dependent future mappings, preserving better disk request order around indirect-block reads.

## Write Path Behavior
The write path accepts folios only when dirty data is fully mapped and contiguous, with a special EOF case for unmapped tail blocks. For folios without buffers, it calls `get_block(..., create=1)` to allocate mappings. It zeroes data beyond `i_size`, submits existing BIOs when disk contiguity breaks, cleans covered buffers only after successfully adding the folio to a BIO, starts writeback, unlocks the folio, and handles boundary blocks.

## Important Behaviors and Edge Cases
- The code avoids multipage BIOs for partial/non-contiguous cases because page completion across multiple BIOs is complex.
- Readahead uses `REQ_RAHEAD` and more conservative GFP flags.
- Whole folios beyond EOF are skipped through fallback handling to avoid allocating blocks past EOF.
- Partial EOF folios are zeroed on every writepage invocation because mmap exposes zeroed bytes beyond file size.
- `buffer_boundary()` triggers BIO submission and optional boundary block write.
- Write fallback records mapping errors from `block_write_full_folio()`.
- `__mpage_writepages()` uses `blk_plug` to improve block-layer batching.

## Dependencies
- Filesystem-supplied `get_block_t`.
- Buffer-head fallback helpers.
- BIO, block device, writeback, folio, readahead, and cgroup writeback infrastructure.

## Research Notes
This file is a generic library used by simple block-mapped filesystems such as Minix. It optimizes the common contiguous mapping case and intentionally delegates complicated buffer states to older buffer-head paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/mpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/namei.c -->
# File Research: sources/os/linux/linux/fs/namei.c

## Purpose
Implements Linux VFS pathname resolution and many pathname-based filesystem operations. It covers filename copying, permission checks, RCU/ref path walking, symlink traversal, mount traversal, lookup helpers, open/create logic, and syscall-level implementations for mknod, mkdir, rmdir, unlink, symlink, link, rename, and readlink-related helpers.

## Main Responsibilities
- Copy user/kernel pathnames into `struct filename` objects.
- Perform DAC, ACL, capability, idmapped mount, device-cgroup, and LSM permission checks.
- Walk paths using RCU-walk fast paths and ref-walk fallback.
- Cross mountpoints, automounts, and `..` across mount roots.
- Enforce scoped lookup flags such as `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_NO_XDEV`, `LOOKUP_NO_SYMLINKS`, and `LOOKUP_NO_MAGICLINKS`.
- Resolve symlinks iteratively with bounded stack depth and total link count.
- Provide in-kernel lookup helpers for one-component lookup and full path lookup.
- Provide directory-operation locking helpers.
- Implement VFS create/remove/link/rename primitives and syscall wrappers.
- Provide generic page-cache symlink helpers.

## Major Data Structures
- `struct filename`: allocated from `names_cache`, can embed short names in `iname` or allocate long names separately.
- `struct nameidata`: carries the current path, root, current inode, lookup flags/state, sequence counters, symlink stack, final component, dirfd, and directory owner/mode snapshots.
- `enum last_type`: classifies final/current component as normal, root, `.`, or `..`.
- Symlink stack entries store saved path, delayed cleanup callback, remaining name, and sequence number.

## Filename Handling
- `filename_init()` creates the filename slab cache.
- `do_getname()` copies user pathnames, rejects empty paths unless `LOOKUP_EMPTY`, and switches to heap storage for long paths.
- `getname_flags()`, `getname_uflags()`, and `__getname_maybe_null()` are user-path wrappers.
- `do_getname_kernel()` handles kernel strings.
- `putname()` releases embedded or separately allocated filename storage.
- Delayed filename helpers allow deferring audit completion.

## Permission Model
- `check_acl()` and `acl_permission_check()` combine POSIX ACL checks with UNIX mode-bit checks and idmapped ownership conversion.
- `generic_permission()` adds capability overrides, with directory-specific handling for search/read.
- `do_inode_permission()` caches the fast generic-permission path in `IOP_FASTPERM`.
- `sb_permission()` rejects writes to read-only superblocks for regular files, directories, and symlinks.
- `inode_permission()` adds immutable/unmapped-ID write checks, device cgroup checks, and LSM permission checks.
- `lookup_inode_permission_may_exec()` is a directory traversal-optimized execute/search permission path.

## Path Walking
- `path_init()` chooses the starting path from root, cwd, dirfd, or provided root and initializes RCU/ref walking state.
- `link_path_walk()` parses components, checks traversal permission, hashes names, handles dots, follows intermediate symlinks, and records final component metadata.
- `lookup_fast()` performs dcache lookup and revalidation, staying in RCU mode when possible.
- `lookup_slow()` and `__lookup_slow()` allocate/lookup dentries under directory inode locks.
- `step_into()` advances to a child dentry, crossing mounts or following symlinks as required.
- `complete_walk()` finalizes RCU walks, performs scoped lookup containment validation, and weak revalidation after jumps.
- `try_to_unlazy()` and `try_to_unlazy_next()` convert RCU-walk state to ref-walk state when blocking or references are needed.
- `terminate_walk()` drops paths, symlink callbacks, and RCU state.

## Mount Traversal
- `follow_up()` moves from a mounted filesystem root to the mountpoint in the parent mount.
- `choose_mountpoint_rcu()` / `choose_mountpoint()` select parent mountpoints while handling bind-mount roots.
- `follow_automount()` triggers automounts when lookup intent requires it.
- `traverse_mounts()` and `__traverse_mounts()` cross mounted dentries, call filesystem `d_manage()`, handle automounts, and enforce `LOOKUP_NO_XDEV`.
- `follow_down_one()` and `follow_down()` are exported helpers for descending into covering mounts.
- RCU mount traversal uses `__follow_mount_rcu()`.

## Symlink Handling
- `reserve_stack()` enforces `MAXSYMLINKS` and expands from embedded to allocated symlink stack storage.
- `pick_link()` checks symlink policy, protected symlink rules, `MNT_NOSYMFOLLOW`, LSM follow-link permission, atime updates, magic-link restrictions, absolute symlink root jumps, and delayed cleanup.
- `put_link()` releases the most recent symlink stack entry.
- `may_follow_link()` enforces `protected_symlinks` for sticky world-writable directories.
- `vfs_readlink()`, `vfs_get_link()`, `page_get_link()`, `page_readlink()`, and `page_symlink()` implement common symlink read/write helpers.

## Name Hashing
- With `CONFIG_DCACHE_WORD_ACCESS`, `full_name_hash()`, `hashlen_string()`, and `hash_name()` use word-at-a-time hashing and delimiter detection.
- Without it, byte-at-a-time fallback hashing is used.
- `hash_name()` also detects `.` and `..` through `lastword`.

## Lookup Entry Points
- `filename_lookup()` performs full lookup with RCU first, then ref-walk retry on `-ECHILD`, and revalidation retry on `-ESTALE`.
- `filename_parentat()` and `__filename_parentat()` return parent path plus final component.
- `kern_path()`, `kern_path_parent()`, `vfs_path_lookup()`, and `vfs_path_parent_lookup()` are kernel-facing wrappers.
- One-component helpers include `lookup_one()`, `lookup_one_unlocked()`, positive-only variants, and no-permission variants.
- `lookup_noperm_common()` rejects empty, dot/dotdot, slash, and NUL-containing component names and calls filesystem `d_hash()` when present.

## Directory Operation Locking Helpers
- `start_dirop()` / `end_dirop()` lock parent directories and perform final lookup.
- `start_creating*()` and `start_removing*()` variants combine component validation, optional permission checks, locking, and lookup.
- `start_creating_dentry()` and `start_removing_dentry()` validate an already supplied child dentry.
- Rename setup helpers lock parent directories with deadlock-aware ordering and ancestor trap detection:
  - `lock_rename()`, `lock_rename_child()`, `unlock_rename()`.
  - `start_renaming()`, `start_renaming_dentry()`, `start_renaming_two_dentries()`, and `end_renaming()`.

## Create/Open Path
- `vfs_prepare_mode()` strips SGID/umask and applies VFS type/permission masks.
- `vfs_create()` performs create permission/security checks, delegation breaking, filesystem `->create()`, and fsnotify.
- `may_open()` validates file type, device/noexec restrictions, permissions, append-only rules, and `O_NOATIME`.
- `lookup_open()` handles last-component lookup, creation permission, atomic open, and fallback `->lookup()`/`->create()`.
- `open_last_lookups()` handles RCU fast lookup, creation locking, delegation retry, and transition into final path.
- `do_open()` completes the walk, handles `O_EXCL`, sticky create protections, `O_DIRECTORY`, `O_TRUNC`, `vfs_open()`, LSM post-open, and truncation.
- `vfs_tmpfile()`, `kernel_tmpfile_open()`, `do_tmpfile()`, and `do_o_path()` implement tmpfile and `O_PATH`.
- `path_openat()`, `do_file_open()`, and `do_file_open_root()` are main open entry points.

## Filesystem Mutation Primitives and Syscalls
- Creation:
  - `filename_create()`, `start_creating_path()`, `end_creating_path()`, `start_creating_user_path()`, and `dentry_create()`.
  - `vfs_mknod()`, `filename_mknodat()`, `mknodat`, `mknod`.
  - `vfs_mkdir()`, `filename_mkdirat()`, `mkdirat`, `mkdir`.
- Removal:
  - `may_delete_dentry()` centralizes unlink/rmdir victim checks.
  - `vfs_rmdir()`, `filename_rmdir()`, `rmdir`.
  - `vfs_unlink()`, `filename_unlinkat()`, `unlinkat`, `unlink`.
- Symlink and hardlink:
  - `vfs_symlink()`, `filename_symlinkat()`, `symlinkat`, `symlink`.
  - `may_linkat()`, `safe_hardlink_source()`, `vfs_link()`, `filename_linkat()`, `linkat`, `link`.
- Rename:
  - `vfs_rename()` performs permission/security checks, delegation breaking, locking of source/target inodes, loop/mountpoint/swapfile/max-link checks, filesystem `->rename()`, dcache move/exchange, and fsnotify.
  - `filename_renameat2()`, `renameat2`, `renameat`, and `rename`.

## Security and Hardening Features
- Sysctls:
  - `protected_symlinks`
  - `protected_hardlinks`
  - `protected_fifos`
  - `protected_regular`
- Sticky directory protections:
  - `may_follow_link()` restricts unsafe symlink following.
  - `may_create_in_sticky()` restricts opening existing FIFO/regular files in sticky writable directories.
  - `__check_sticky()` and `may_delete_dentry()` enforce sticky deletion rules.
- Hardlink protections:
  - `may_linkat()` blocks unsafe hardlinks unless owner/capable or source is safe.
- Scoped lookup:
  - `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_NO_XDEV`, and related flags prevent root/mount/symlink escapes.
- LSM hooks are invoked throughout lookup, create, open, symlink, link, rename, readlink, unlink, mkdir, rmdir, and mknod paths.

## Important Behaviors and Edge Cases
- RCU-walk failures return `-ECHILD` and are retried in ref-walk mode.
- Stale dentries returning `-ESTALE` are retried with `LOOKUP_REVAL`.
- `LOOKUP_CACHED` requires RCU and fails with `-EAGAIN` if used alone.
- Empty paths require `LOOKUP_EMPTY`/`AT_EMPTY_PATH`.
- `..` handling respects bind-mount roots and scoped lookup constraints.
- `LOOKUP_NO_XDEV` blocks mount crossing and automount triggering.
- `MNT_NOSYMFOLLOW` and `LOOKUP_NO_SYMLINKS` reject symlink traversal with `-ELOOP`.
- `O_CREAT` lookup intentionally delays some write errors to preserve correct error precedence.
- Truncation for `O_TRUNC` is performed after open permission checks and with write access held.
- Rename locking carefully avoids directory loops and deadlocks with `s_vfs_rename_mutex`.
- `vfs_rename()` skips VFS `d_move()`/`d_exchange()` if the filesystem advertises `FS_RENAME_DOES_D_MOVE`.
- Page-cache symlink helpers require non-highmem mappings for direct folio address access.

## Dependencies
- Dcache, inode, mount, namespace, RCU, seqlock, audit, fsnotify, LSM, POSIX ACL, file locking/delegation, device cgroup, user namespace/idmapping, and page-cache infrastructure.
- Private mount internals from `mount.h`.

## Research Notes
This file is one of the VFS core files. Its most important architectural split is between fast RCU path walking and slower refcounted walking, with careful fallback points whenever filesystem callbacks, blocking, automounts, sequence mismatches, or symlink operations require stronger references.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/namei.c -->