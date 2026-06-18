# subset-b-005685 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/inode.c -->
# sources/distributed-fs/ceph-client/fs/minix/inode.c

## Purpose
`inode.c` is the Minix filesystem superblock, inode, address-space, and module registration implementation. It mounts V1/V2/V3 Minix block devices, validates their static layout, reads bitmap blocks, creates the root dentry, selects V1 versus V2 inode formats, wires inode operation tables, and implements inode writeback, eviction, truncation dispatch, statfs, getattr, and page-cache block I/O glue.

## Important APIs, Types, and Functions
Key exported/internal entry points are `minix_iget()`, `minix_set_inode()`, `minix_truncate()`, `minix_getattr()`, `minix_prepare_chunk()`, and the module `minix_fs_type`. `minix_fill_super()` is the mount-time core. It populates `struct minix_sb_info`, identifies Minix V1/V2/V3 magic values and directory name lengths, reads inode and zone bitmaps, sets `s_op`, loads `MINIX_ROOT_INO`, and builds `s_root`. `minix_reconfigure()` handles remount read-only/read-write transitions. `V1_minix_iget()` and `V2_minix_iget()` decode on-disk inode formats into VFS inodes; `V1_minix_update_inode()` and `V2_minix_update_inode()` write them back. `minix_get_block()` dispatches to `V1_minix_get_block()` or `V2_minix_get_block()` from the indirect-tree implementations. `minix_aops` binds Minix files to buffered I/O helpers such as `block_read_full_folio()`, `mpage_writepages()`, `block_write_begin()`, `generic_write_end()`, and `generic_block_bmap()`.

## Control Flow
Mount starts at `minix_init_fs_context()`, then `get_tree_bdev()` calls `minix_fill_super()`. The fill path fixes an initial block size, reads block 1 as the superblock, recognizes the Minix version, validates bitmap capacity and zone constraints with `minix_check_superblock()`, reads bitmap blocks, reserves bit zero, installs super operations, and loads the root inode. Normal inode lookup uses `iget_locked()` then version-specific raw-inode readers. File I/O routes VFS page-cache operations through `minix_get_block()`, which invokes the V1/V2 indirect mapping code. Eviction truncates unlinked files before freeing their inode bitmap entry, while linked inodes sync and invalidate metadata buffer tracking.

## State and Persistence Behavior
Persistent state lives in the on-disk superblock, inode/zone bitmaps, raw inode tables, and data/indirect blocks. For writable non-V3 mounts, `s_state` is cleared on mount/remount-rw and restored on unmount/remount-ro to record clean versus dirty filesystem state. Inode writeback converts kernel uid/gid/timestamps/link counts/size and zone arrays into the V1 or V2 disk format and marks the raw inode buffer dirty; synchronous writeback explicitly calls `sync_dirty_buffer()`. `minix_evict_inode()` integrates pagecache truncation, indirect-block freeing, metadata-buffer sync via `mmb_sync()`, and inode bitmap freeing.

## Dependencies and Integration Points
This file integrates with `minix.h`, bitmap allocation helpers in other Minix files, VFS superblock/inode/address-space operations, buffer heads, block device mounting, `mpage`, writeback control, and fs-context mounting. The VFS calls `minix_dir_inode_operations`, `minix_file_inode_operations`, `minix_dir_operations`, and `minix_file_operations` declared elsewhere. Idmapped mounts are effectively ignored for getattr by passing `&nop_mnt_idmap` to `generic_fillattr()`, matching Minix's legacy on-disk ownership handling.

## Risks
Mount safety depends on superblock validation; unsupported non-zero `s_log_zone_size`, too-small bitmap tables, invalid first data zone, and V1 maximum-size overflow are rejected. The code uses old device encoding for special files and high-to-low uid/gid conversion, so ownership/device fidelity is limited by the Minix format. Error unwinding in `minix_fill_super()` must release all bitmap and superblock buffers correctly. Any mismatch between `s_version`, inode layout, and indirect-tree dispatch can corrupt block pointers. `minix_write_failed()` must truncate partially allocated blocks after failed writes to avoid stale allocation.

## Test Signals
Useful signals include successful mount/read-only remount/read-write remount/unmount across Minix V1, V2, and V3 images; fsck state changes on writable mounts; root inode lookup failures on corrupt images; `statfs` free block/inode counts; create/write/truncate/fsync/readback tests; special-file and symlink creation; block-size handling for V3; and fault injection around bitmap reads, raw inode reads, synchronous inode writeback, and ENOSPC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_common.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_common.c

## Purpose
`itree_common.c` is a generic include-file implementation for Minix direct/indirect block trees. It is included by both V1 and V2 wrappers after they define `block_t`, `DEPTH`, `DIRECT`, `i_data()`, `block_to_cpu()`, `cpu_to_block()`, and `block_to_path()`. It provides block lookup/allocation for buffered I/O and subtree truncation for file size changes.

## Important APIs, Types, and Functions
The central helper type is `Indirect`, a cached pointer-chain element containing a pointer to a block slot, the slot's saved key, and the buffer holding it. `get_block()` maps a logical block to a physical zone and optionally allocates missing direct/indirect blocks. `get_branch()` reads and validates an existing pointer chain. `alloc_branch()` allocates a run of new indirect/data blocks and initializes indirect blocks. `splice_branch()` atomically attaches a newly allocated branch. Truncation is implemented by `truncate()`, `find_shared()`, `free_data()`, `free_branches()`, and `all_zeroes()`. `nblocks()` estimates total data plus metadata blocks for stat reporting.

## Control Flow
Lookup begins with version-specific `block_to_path()`, producing offsets through direct and indirect levels. `get_branch()` walks from the inode's zone array through buffer-head-backed indirect blocks, checking that previously read slots still match with `verify_chain()`. If the path exists, `get_block()` calls `map_bh()`. If a block is missing and `create` is false, it returns the lookup error or hole. If allocation is requested, `alloc_branch()` allocates the missing tail, initializes intermediate buffers, and `splice_branch()` rechecks the old chain under `pointers_lock` before publishing the first pointer. Races with truncate return `-EAGAIN` and restart.

Truncation computes the first block beyond `i_size`, truncates partial pagecache with `block_truncate_page()`, frees direct slots after the new end, finds any shared indirect branch that must be partially preserved, clears and frees the detached subtree, then frees whole indirect subtrees after the shared branch.

## State and Persistence Behavior
Persistent state is the inode's direct/indirect zone array and indirect blocks on disk. Newly allocated indirect buffers are zeroed, marked uptodate, and dirtied through `mmb_mark_buffer_dirty()` so Minix fsync/eviction can track metadata buffers. Publishing a pointer marks either the indirect buffer or inode dirty and updates ctime. Truncation clears pointers before freeing blocks, marks affected buffers/inodes dirty, updates mtime/ctime, and releases or forgets buffers so stale metadata is not written after block reuse.

## Dependencies and Integration Points
The file depends on definitions supplied by `itree_v1.c` or `itree_v2.c`, plus `minix_new_block()`, `minix_free_block()`, `minix_i()`, buffer-head I/O, and mapping metadata buffer tracking. Its `get_block()` is consumed by `inode.c` address-space operations through version-specific wrappers. It assumes Minix zone size equals block size, which `minix_check_superblock()` enforces.

## Risks
This is concurrency-sensitive code. The global `pointers_lock` only protects pointer-chain validation and splicing; buffer I/O and allocation happen outside it, so every publish must revalidate. Error paths must free every allocated block and forget initialized buffers or leaks/corruption result. Failure to dirty metadata buffers can lose indirect-block updates after fsync. Truncation must handle sparse holes, partially shared indirect paths, and races with readers/writers without freeing still-referenced blocks.

## Test Signals
Exercise direct, single-indirect, double-indirect, and V2 triple-indirect boundaries; sparse reads; ENOSPC during each branch allocation level; truncate to direct/indirect boundaries and to the middle of indirect blocks; concurrent write/truncate stress; fsync after indirect allocation; and corruption/fault-injection for unreadable indirect blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v1.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_v1.c

## Purpose
`itree_v1.c` specializes the generic Minix indirect-tree implementation for original Minix V1 filesystems. V1 uses 16-bit block pointers, seven direct zones, one single-indirect slot, and one double-indirect slot.

## Important APIs, Types, and Functions
The file defines `DEPTH = 3`, `DIRECT = 7`, and `typedef u16 block_t`. `i_data()` maps the generic tree code onto `minix_i(inode)->u.i1_data`. `block_to_path()` converts a logical file block into offsets for direct, single-indirect, or double-indirect lookup. Public wrappers `V1_minix_get_block()`, `V1_minix_truncate()`, and `V1_minix_blocks()` expose the generic `get_block()`, `truncate()`, and `nblocks()` to the rest of Minix.

## Control Flow
For logical blocks 0 through 6, `block_to_path()` returns a one-element direct offset. Blocks 7 through 518 use inode slot 7 and an offset in the 512-entry indirect block. Larger valid blocks use inode slot 8, a first-level offset `block >> 9`, and a second-level offset `block & 511`. Negative blocks and blocks whose byte offset exceeds `s_maxbytes` return depth 0, causing the generic mapper to fail without mapping.

## State and Persistence Behavior
All block numbers are kept in host order and returned unchanged by `block_to_cpu()` and `cpu_to_block()`. Persistent pointers live in the V1 raw inode's 16-bit zone fields and in 16-bit indirect blocks. The included common code handles dirtying inode/metadata buffers and block freeing.

## Dependencies and Integration Points
This wrapper is built by textual inclusion of `itree_common.c`, so the macros and helpers it defines are compile-time parameters to the common implementation. It is called by `minix_get_block()`, `minix_truncate()`, and `minix_getattr()` when `INODE_VERSION(inode) == MINIX_V1`.

## Risks
The fixed `512` indirect fanout is tied to 1 KiB `BLOCK_SIZE` and 16-bit pointers; V1 mount validation must keep `s_maxbytes` within the representable mapping limit. Overflow or incorrect bounds here would map logical blocks to the wrong indirect slot. Because V1 block numbers are 16-bit, large devices/images cannot be represented safely.

## Test Signals
Use V1 images to test writes at block 0, block 6/7, block 518/519, maximum-size rejection, double-indirect truncation, sparse holes, and `stat->blocks` accounting through `V1_minix_blocks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v2.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_v2.c

## Purpose
`itree_v2.c` specializes the generic Minix indirect-tree implementation for Minix V2 and V3 inode block mapping. V2/V3 use 32-bit block pointers, seven direct zones, and single, double, and triple indirect slots.

## Important APIs, Types, and Functions
The file defines `DIRECT = 7`, `DEPTH = 4`, and `typedef u32 block_t`. `DIRCOUNT` and `INDIRCOUNT(sb)` describe direct count and per-indirect-block fanout based on filesystem block size. `i_data()` maps the generic implementation onto `minix_i(inode)->u.i2_data`. `block_to_path()` produces up to four offsets. Public wrappers are `V2_minix_get_block()`, `V2_minix_truncate()`, and `V2_minix_blocks()`.

## Control Flow
`block_to_path()` rejects negative logical blocks and byte offsets beyond `s_maxbytes`. It returns a direct offset for the first seven blocks, slot 7 plus one indirect offset for the next `INDIRCOUNT(sb)` blocks, slot 8 plus two offsets for the double-indirect range, and slot 9 plus three offsets for the triple-indirect range. The included common code then uses those offsets for lookup, allocation, and truncation.

## State and Persistence Behavior
Block pointers are 32-bit host-order values in memory and on supported Minix images as used by this code. Indirect fanout scales with `sb->s_blocksize`, unlike V1's hard-coded 1 KiB geometry. Persistent metadata updates and frees are delegated to `itree_common.c`.

## Dependencies and Integration Points
This file is used for both `MINIX_V2` and `MINIX_V3` in `inode.c`. It relies on the V2 raw inode layout, V3 superblock block-size setup, the generic Minix allocator/free routines, and the VFS block mapping callbacks.

## Risks
The triple-indirect arithmetic uses products of `INDIRCOUNT(sb)` and logical block values; bounds must be constrained by `s_maxbytes` to prevent nonsensical paths. V3 block-size changes directly affect indirect fanout, so mount-time block-size setup must happen before inode block mapping. Tests should watch for off-by-one errors at direct/single/double/triple boundaries.

## Test Signals
Use V2/V3 images with different supported block sizes; write and read across single-, double-, and triple-indirect boundaries; truncate from triple-indirect back to smaller sizes; verify `V2_minix_blocks()` metadata accounting; and inject ENOSPC during each indirect allocation depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/minix.h -->
# sources/distributed-fs/ceph-client/fs/minix/minix.h

## Purpose
`minix.h` is the private Minix filesystem header. It defines in-memory Minix inode and superblock state, version constants, accessors, function prototypes shared across Minix source files, bitmap endian abstractions, and error-reporting helpers.

## Important APIs, Types, and Functions
`struct minix_inode_info` embeds VFS `struct inode`, a union of V1 16-bit and V2/V3 32-bit zone arrays, and `struct mapping_metadata_bhs` for metadata buffer tracking. `struct minix_sb_info` stores mount-wide values decoded from the on-disk superblock: inode/zone counts, bitmap block counts, first data zone, directory entry size/name length, bitmap buffer arrays, superblock buffer, mount state, and version. `minix_sb()` and `minix_i()` are the central typed accessors. Prototypes cover inode lookup/allocation/free, block allocation/free/counting, raw inode access, directory entry manipulation, getattr, truncate, block mapping, fsync, and operation tables.

## Control Flow
Other Minix files include this header to coordinate version dispatch. `INODE_VERSION(inode)` reads `s_version` from the superblock info and drives V1 versus V2/V3 raw inode and block tree decisions. Directory and inode operation tables declared here are installed by `minix_set_inode()` and the directory code. `minix_blocks_needed()` is used during mount validation to confirm bitmap capacity.

## State and Persistence Behavior
The header describes the in-memory shadow of persistent Minix metadata. The zone arrays are copied from and back to raw inode zone fields. `s_imap` and `s_zmap` hold buffer heads for persistent inode and zone allocation bitmaps. `s_mount_state` mirrors the clean/error state for V1/V2 filesystems. Bitmap helper macros abstract the persistent bitmap bit order for native-endian, big-endian 16-bit indexed, and little-endian configurations.

## Dependencies and Integration Points
The header depends on core VFS types, folios/page cache types, and UAPI Minix on-disk structures from `<linux/minix_fs.h>`. It is shared by `inode.c`, directory/name lookup code, bitmap code, file/dir operation code, and both indirect tree implementations.

## Risks
Because this header defines compile-time bitmap semantics, incompatible endian configuration is rejected with `#error`. Any mismatch between `minix_inode_info` zone array sizes and raw inode update loops can corrupt in-memory or on-disk zones. The prototypes expose legacy Minix assumptions such as old device numbers and non-idmapped ownership semantics.

## Test Signals
Build coverage across endian configuration options is important. Runtime signals include correct inode/superblock accessors under KASAN/UBSAN, bitmap allocation on little- and big-endian images, V1/V2/V3 version dispatch, and metadata fsync behavior through `mapping_metadata_bhs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/minix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/namei.c -->
# sources/distributed-fs/ceph-client/fs/minix/namei.c

## Purpose
`fs/minix/namei.c` implements Minix directory inode operations: lookup, create, mknod, tmpfile, symlink, hard link, mkdir, unlink, rmdir, and rename. It bridges generic VFS directory requests to Minix directory-entry helpers and inode allocation/link-count rules.

## Important APIs, Types, and Functions
The exported table is `minix_dir_inode_operations`. `minix_lookup()` enforces `s_namelen`, resolves a directory entry through `minix_inode_by_name()`, and returns `d_splice_alias()`. `minix_mknod()`, `minix_create()`, and `minix_tmpfile()` allocate inodes with `minix_new_inode()` and initialize them through `minix_set_inode()`. `minix_symlink()` stores symlink text with `page_symlink()`. `add_nondir()` centralizes `minix_add_link()` plus `d_instantiate()` and cleanup on failure. Directory-specific operations use `minix_make_empty()`, `minix_empty_dir()`, `minix_find_entry()`, `minix_delete_entry()`, `minix_set_link()`, and `minix_dotdot()`.

## Control Flow
Creation allocates an inode, assigns file/special/symlink/dir operations, marks it dirty, inserts a directory entry, and instantiates the dentry. `mkdir` increments the parent link count, initializes the child with two links for `.` and parent reference, creates `.`/`..`, then links the new directory into the parent. On failure, it unwinds both child links and the parent link. `unlink` finds the directory entry, deletes it, releases the mapped folio, copies directory ctime to the victim, and decrements the victim link count. `rmdir` verifies parent link integrity and emptiness, calls unlink, then decrements parent and child directory links. `rename` locates old and optional new entries, handles directory `..`, replaces or adds the target entry, deletes the old entry, and updates link counts for cross-directory moves and overwritten directories.

## State and Persistence Behavior
Persistent changes are Minix directory entries, inode link counts, inode ctime, and page-cache-backed symlink data. Directory entry modifications happen through folio-mapped helper routines that dirty directory data elsewhere. Inode link count changes use VFS helpers such as `inode_inc_link_count()`, `inode_dec_link_count()`, and `drop_nlink()`, causing inode writeback through Minix inode update code. Renames of directories update the `..` entry to point at the new parent.

## Dependencies and Integration Points
This file depends on `minix.h` declarations and generic VFS namei locking/permission layers, which call these inode operations after parent locking and permission checks. It uses folio release helpers for directory-entry mappings and `page_symlink()` from core `fs/namei.c`. It deliberately passes `&nop_mnt_idmap` in `minix_create()` because Minix does not implement idmapped ownership handling in its create path.

## Risks
Link-count corruption is the main risk; the code explicitly checks zero nlink on unlink and low parent nlink on rmdir/rename and reports `-EFSCORRUPTED`. Rename has several delicate cases: replacing non-empty directories, moving directories across parents, updating `..`, and preserving balanced folio releases on every error path. Symlink length is limited to one filesystem block. `old_valid_dev()` rejects device numbers that cannot be represented by the legacy Minix special-file format.

## Test Signals
Test name length limits for 14/30/60-byte variants, create/link/unlink link-count transitions, mkdir/rmdir `.`/`..` correctness, rename over files and directories, cross-directory directory rename updating `..`, tmpfile creation, long symlink rejection, special-file device validation, and corruption tests for invalid link counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mnt_idmapping.c -->
# sources/distributed-fs/ceph-client/fs/mnt_idmapping.c

## Purpose
`mnt_idmapping.c` implements mount idmapping objects and UID/GID translation helpers for idmapped mounts. It maps filesystem `kuid_t`/`kgid_t` values to VFS-facing `vfsuid_t`/`vfsgid_t` values and back, allocates immutable mount idmap copies from user namespaces, reference-counts them, and renders idmap state for mount stat reporting.

## Important APIs, Types, and Functions
`struct mnt_idmap` contains copied `uid_gid_map` instances and a refcount. Two global exported singleton maps exist: `nop_mnt_idmap` for identity mapping and `invalid_mnt_idmap` for forced invalid mapping. `make_vfsuid()` and `make_vfsgid()` map filesystem IDs into the mount idmap for reporting. `from_vfsuid()` and `from_vfsgid()` map VFS IDs back into a filesystem user namespace for inode writes. `vfsgid_in_group_p()` checks group membership. `alloc_mnt_idmap()`, `mnt_idmap_get()`, and `mnt_idmap_put()` manage dynamic idmap lifetime. `statmount_mnt_idmap()` prints UID or GID extents relative to the caller's current user namespace.

## Control Flow
Fast paths return immediately for `nop_mnt_idmap` and `invalid_mnt_idmap`. Otherwise, `make_vfsuid()`/`make_vfsgid()` first translate the kernel ID out of the filesystem namespace with `from_kuid()`/`from_kgid()` unless the filesystem namespace is initial, then map the raw ID down through the mount idmap. Reverse conversion maps up through the mount idmap and constructs a kernel ID in the filesystem namespace. Allocation copies both UID and GID maps from the mount user namespace, duplicating dynamically allocated extent arrays when the map has more than the inline extent capacity. Put frees those arrays when the refcount reaches zero.

## State and Persistence Behavior
Mount idmaps are in-memory kernel objects associated with mounts; they are not themselves persistent filesystem state. They do, however, control whether persisted inode UID/GID writes are allowed and how IDs are presented to userspace. Copied maps are immutable after creation, relying on user namespace map immutability once `nr_extents` is non-zero. The statmount path emits NUL-separated mapping triplets and skips extents that cannot be resolved in the caller's idmap.

## Dependencies and Integration Points
This file integrates with `<linux/mnt_idmapping.h>`, user namespace ID maps, VFS permission helpers, inode ownership helpers, mount lifetime management, and seq-file mount stat reporting. Filesystems and VFS code pass `struct mnt_idmap *` into permission, create, setattr, and getattr paths.

## Risks
Incorrect map direction is security-sensitive: reporting and writing IDs use opposite transformations. `copy_mnt_idmap()` relies on memory barriers and the immutability of written user namespace maps; copying a partially initialized map would be dangerous. Dynamic extent allocation must free both forward and reverse arrays on all failure paths. Invalid or unmapped IDs must remain invalid to prevent inode ownership corruption.

## Test Signals
Exercise identity maps, invalid maps, single and multi-extent maps, mappings relative to non-initial filesystem namespaces, unmapped ID failures, refcount get/put lifetime, allocation failure during reverse extent copy, `vfsgid_in_group_p()` with and without `CONFIG_MULTIUSER`, and `statmount_mnt_idmap()` output/overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mnt_idmapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mount.h -->
# sources/distributed-fs/ceph-client/fs/mount.h

## Purpose
`fs/mount.h` is an internal VFS mount namespace header. It defines the private `struct mount` that embeds public `struct vfsmount`, the mount namespace container, mountpoint records, per-CPU mount reference counters, propagation flags, and helper routines/macros used by path lookup and namespace management.

## Important APIs, Types, and Functions
`struct mnt_namespace` tracks namespace identity, root mount, an rb-tree of mounts, user namespace ownership, poll/event state, fsnotify marks, mount counts, passive references, and anonymous namespace state. `struct mount` contains parent/child topology, mountpoint dentry, namespace membership, per-superblock linkage, propagation lists, expiry/pin state, fsnotify state, IDs, peer group ID, and overmount pointer. Important helpers include `real_mount()`, `mnt_has_parent()`, `is_mounted()`, `__path_is_mountpoint()`, `detach_mounts()`, `get_mnt_ns()`, `is_local_mountpoint()`, `anon_ns_root()`, `mnt_ns_attached()`, `move_from_ns()`, `mnt_notify_add()`, `topmost_overmount()`, and write-hold bit helpers.

## Control Flow
Path lookup uses `real_mount()` to move from public `vfsmount` to private topology and `__lookup_mnt()`/`__path_is_mountpoint()` to detect covered dentries. Namespace mutation code uses `move_from_ns()` to remove a mount from the namespace rb-tree while maintaining cached first/last nodes. `detach_mounts()` avoids work unless the dentry has mountpoints. Lock guard macros wrap `mount_lock` seqlock operations for writers and exclusive readers. Fsnotify-aware builds queue mount namespace notifications only when the current or previous namespace has marks.

## State and Persistence Behavior
The header describes in-memory namespace and mount graph state only. Mount IDs, propagation topology, namespace rb-tree links, writer holds, and fsnotify connector pointers are runtime state. The `WRITE_HOLD` bit is stored in the low bit of `mnt_pprev_for_sb`, so pointer alignment is part of the representation.

## Dependencies and Integration Points
This header is included by core VFS namespace and namei code. `fs/namei.c` uses `real_mount()`, mount parent relationships, `mount_lock`, and `__lookup_mnt()` to implement `..`, mount crossing, `LOOKUP_NO_XDEV`, and managed dentry traversal. It also integrates with fsnotify, namespace common infrastructure, poll wait queues, rb-trees, mount propagation, and mount pinning.

## Risks
Mount topology is highly concurrent and protected by seqlocks, namespace locks, rb-tree invariants, and reference counts. Misusing `real_mount()` on invalid/internal mounts, failing to update first/last rb-tree caches in `move_from_ns()`, or mishandling the low-bit `WRITE_HOLD` encoding can corrupt namespace state. Helper callers must account for detached and internal mounts represented by null or error namespace pointers.

## Test Signals
Signals include mount/umount/move/bind propagation tests, path lookup across stacked mounts, `LOOKUP_NO_XDEV` behavior, namespace cloning and anonymous namespace handling, fsnotify mount namespace events, rb-tree order after mount removal, and stress tests around concurrent mount traversal with `mount_lock` sequence retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mpage.c -->
# sources/distributed-fs/ceph-client/fs/mpage.c

## Purpose
`mpage.c` provides generic multipage BIO assembly for block-mapped filesystems. It batches contiguous page-cache folios into larger block I/O requests for readahead, read-folio, and writepages, while falling back to buffer-head based helpers when a folio has holes, non-contiguous blocks, existing buffers, or filesystem-specific complexity.

## Important APIs, Types, and Functions
Exported entry points are `mpage_readahead()`, `mpage_read_folio()`, and `__mpage_writepages()`. Read-side internals include `struct mpage_readpage_args`, `do_mpage_readpage()`, `map_buffer_to_folio()`, `mpage_bio_submit_read()`, and `mpage_read_end_io()`. Write-side internals include `struct mpage_data`, `mpage_write_folio()`, `clean_buffers()`, `mpage_bio_submit_write()`, and `mpage_write_end_io()`. Filesystems provide a `get_block_t` mapper.

## Control Flow
Read readahead iterates folios from `readahead_folio()`, maps logical blocks with `get_block()`, reuses previous extent information when possible, and accumulates contiguous blocks into a BIO. Holes at EOF are zeroed; all-hole folios are marked uptodate and unlocked. If an existing buffer, uptodate mapped buffer, hole-then-data pattern, non-contiguous mapping, allocation failure, or mapping error is encountered, outstanding BIOs are submitted and the folio falls back to `block_read_full_folio()`.

Writeback iterates dirty folios via `writeback_iter()` inside a block plug. `mpage_write_folio()` either validates existing buffers or maps a bufferless uptodate folio with `get_block(create=1)`. Fully contiguous dirty mapped ranges are added to a write BIO, buffers are cleaned only after the folio is accepted by the BIO, writeback is started, and the folio is unlocked. EOF-straddling folios are zeroed past `i_size`. Non-contiguous or otherwise complex folios fall back to `block_write_full_folio()`.

## State and Persistence Behavior
`mpage.c` does not own filesystem metadata; it drives page-cache folio state, buffer-head state, BIO submission, and writeback error propagation. Read completions call `folio_end_read()`. Write completions set mapping errors and call `folio_end_writeback()`. BIOs are guarded with `guard_bio_eod()` before submission. The write path accounts cgroup ownership and initializes writeback flags from `writeback_control`.

## Dependencies and Integration Points
It depends on block layer BIO APIs, buffer-head block mapping, page cache folios, readahead/writeback infrastructure, backing-dev flags, and filesystem `get_block()` callbacks. Minix uses `mpage_writepages()` from its address-space operations. Other simple block filesystems can use the same helpers when their mappings are block-contiguous enough for batching.

## Risks
The fallback boundaries are critical: submitting partial folios with complex buffer dependencies would make completion accounting incorrect. Cleaning buffers before successful BIO attachment could lose dirty state on allocation failure, which the code explicitly avoids. EOF handling must avoid allocating or writing beyond `i_size` and must zero mapped tail bytes. BIO contiguity, `BH_Boundary`, and block-device changes must be handled to preserve ordering and correctness.

## Test Signals
Use filesystems with `get_block()` to test contiguous reads/writes, sparse holes, hole-then-data fallback, non-contiguous extents, EOF partial folios, mmap-dirtied bufferless pages, BIO allocation pressure, device removal/read mapping errors, writeback error propagation through `mapping_set_error()`, `BH_Boundary` ordering, and high buffer-head pressure triggering `try_to_free_buffers()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/namei.c -->
# sources/distributed-fs/ceph-client/fs/namei.c

## Purpose
`fs/namei.c` is the Linux VFS pathname resolution, permission checking, open/create, link/unlink, rename, and symlink helper implementation. It turns user or kernel path strings into dentries/paths/files, handles RCU-walk versus ref-walk path traversal, crosses mountpoints and automounts, enforces lookup hardening flags, delegates final operations to filesystem inode operations, and provides syscall implementations for common namespace-mutating operations.

## Important APIs, Types, and Functions
Filename management is handled by `filename_init()`, `getname_flags()`, `getname_kernel()`, `putname()`, delayed filename helpers, and the `names_cache` slab. Permission APIs include `generic_permission()`, `inode_permission()`, `may_linkat()`, `may_delete_dentry()`, `may_create_dentry()`, and sticky/protected symlink/hardlink/create helpers. Path walking centers on `struct nameidata`, `path_init()`, `link_path_walk()`, `walk_component()`, `lookup_fast()`, `lookup_slow()`, `step_into()`, `pick_link()`, `complete_walk()`, and `filename_lookup()`. Mount traversal uses `follow_up()`, `follow_down()`, `handle_mounts()`, and automount helpers. Single-component helpers include `lookup_one()`, `lookup_one_unlocked()`, `lookup_noperm*()`, `start_creating*()`, `start_removing*()`, `start_dirop()`, and `end_dirop()`. Mutation APIs include `vfs_create()`, `vfs_mknod()`, `vfs_mkdir()`, `vfs_rmdir()`, `vfs_unlink()`, `vfs_symlink()`, `vfs_link()`, `vfs_rename()`, and their `filename_*` syscall-facing wrappers. Open handling is implemented by `path_openat()`, `open_last_lookups()`, `lookup_open()`, `atomic_open()`, `do_open()`, `vfs_tmpfile()`, and `dentry_create()`. Symlink pagecache helpers are `vfs_readlink()`, `vfs_get_link()`, `page_get_link()`, `page_readlink()`, and `page_symlink()`.

## Control Flow
Path lookup copies a name into kernel memory, initializes `nameidata` from cwd, dirfd, explicit root, or `/`, and first tries RCU-walk. `link_path_walk()` repeatedly checks execute permission on the current directory, hashes the next component, handles `.`, `..`, and normal names, performs fast dcache lookup with revalidation, falls back to locked filesystem `->lookup()`, crosses managed dentries/mounts, and follows symlinks iteratively using a bounded saved-link stack. If RCU-walk cannot proceed, callers retry in ref-walk; stale network results may retry with `LOOKUP_REVAL`. `complete_walk()` legitimizes RCU results, verifies scoped lookups remain under root, and performs weak revalidation after jumps.

Open follows the same path walk until the final component. `open_last_lookups()` handles fast lookup, create-intent locking, write access acquisition, negative dentry creation, and filesystem `->atomic_open()` when available. `do_open()` then enforces `O_EXCL`, directory requirements, sticky-directory protections, append/truncate/noexec/nodev rules, LSM hooks, `vfs_open()`, post-open security hooks, and truncation.

Namespace mutations use parent lookup plus `mnt_want_write()`, lock parent directories with `start_dirop()` or rename locking helpers, run path and inode security hooks, call VFS permission helpers, break delegations when needed, invoke filesystem inode operations, emit fsnotify events, and drop write counts/references. Rename uses `lock_rename()`/`lock_rename_child()` and `s_vfs_rename_mutex` to avoid topology races, then `vfs_rename()` validates delete/create permissions, locks source/target in a defined order, handles exchange/no-replace/whiteout flags, calls filesystem `->rename()`, and updates dcache with `d_move()` or `d_exchange()` unless the filesystem does it itself.

## State and Persistence Behavior
This file primarily orchestrates runtime VFS state: dentries, mount references, nameidata stacks, inode locks, write counts, open file state, fsnotify notifications, audit records, and LSM decisions. Persistent filesystem state changes occur only through filesystem inode operations such as `->create`, `->mkdir`, `->unlink`, `->rename`, `->symlink`, and pagecache write operations for symlink bodies. It protects persistence by checking idmapped ownership validity, read-only superblocks, immutable/append-only/swapfile flags, device cgroup rules, `MNT_NODEV`, `MNT_NOSYMFOLLOW`, and user namespace mappings before calling filesystem code.

## Dependencies and Integration Points
`namei.c` is a central integration point for dcache, mount namespaces (`mount.h`), user namespaces/idmapped mounts, POSIX ACLs, capabilities, LSM hooks, audit, fsnotify, file allocation, page cache, buffer/page symlink helpers, block write/truncate helpers, device cgroups, and every filesystem's inode and dentry operation tables. Syscalls such as `mknod`, `mkdir`, `unlink`, `symlink`, `link`, `rename`, and open-related helpers enter here before reaching filesystem-specific code like Minix `namei.c`.

## Risks
Path lookup is race-prone: RCU sequence validation, mount seqlocks, rename seqlocks, dentry lockrefs, and retry paths must stay consistent. Scoped lookup flags (`LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_NO_XDEV`, `LOOKUP_NO_SYMLINKS`, `LOOKUP_NO_MAGICLINKS`) are security boundaries. Symlink following must enforce `MAXSYMLINKS`, protected symlink sysctls, `MNT_NOSYMFOLLOW`, and atime/security hooks. Mutation operations must balance locks, write counts, dentries, path refs, delegation references, and retry-on-stale logic. Rename is especially sensitive to ancestor loops, mountpoints, cross-directory locking order, target replacement, and filesystem-specific dcache movement.

## Test Signals
Strong coverage includes RCU/ref-walk fallback, stale dentry revalidation, dcache-only `LOOKUP_CACHED`, scoped lookup escape attempts with racing rename/mount changes, symlink loops and protected symlink/hardlink sysctls, automount and `LOOKUP_NO_XDEV`, idmapped mount permission/create cases, sticky directory restrictions, O_CREAT/O_EXCL/O_TRUNC combinations, `atomic_open()` and non-atomic open filesystems, tmpfile linkability, mkdir/rmdir/unlink/link/rename flag matrices, delegation break retries, fsnotify/audit event emission, pagecache symlink read/write behavior, and fault injection for copy_from_user, allocation, LSM denial, and filesystem operation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/namei.c -->
