# Group Research: group_1005_linux_stable_sources_os_linux_linux_stable_fs_hfsplus_wrapper_c_sou_507272f16618

Scope: learn_fs subset A, source tree `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/wrapper.c

## Purpose

Handles low-level HFS+ volume-header discovery and block I/O, including HFS wrapper support and multisession CD-ROM offsets. It prepares superblock fields needed by the rest of HFS+ mounting.

## Main Entry Points

- `hfsplus_submit_bio()`: aligns HFS+ sector-based I/O to the device logical block size and calls `bdev_rw_virt()`.
- `hfsplus_read_wrapper()`: finds the real HFS+ volume header, handles HFS wrapper and partition-map indirection, reads primary/backup volume headers, and initializes block-size/offset fields.
- `hfsplus_get_last_session()`: selects explicit or last CD-ROM session start.
- `hfsplus_read_mdb()`: validates an HFS wrapper MDB and extracts embedded HFS+ extents.

## Control Flow And State

`hfsplus_read_wrapper()` allocates primary and backup volume-header buffers, reads sector 2 relative to the current partition/session, and loops when it encounters an HFS wrapper or partition map. Once an HFS+/HFSX signature is found, it validates the backup header, derives allocation block size, chooses a VFS block size aligned to the partition offset, and stores `blockoffset`, `part_start`, `sect_count`, and `fs_shift` in `hfsplus_sb_info`.

## Dependencies

Depends on Linux block-device helpers, CD-ROM TOC/multisession APIs, HFS+ raw offsets/signatures, `hfs_part_find()`, and `hfsplus_min_io_size()`.

## Risks

Mount correctness depends on precise sector arithmetic and alignment. Failure cleanup frees allocated header buffers, but callers must treat failure as mount abort. HFS wrapper and partition-map loops trust validation helpers to avoid accepting inconsistent embedded offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr.c

## Purpose

Implements HFS+ extended attribute support for Linux VFS xattr handlers, including the special Finder Info pseudo-xattr stored in catalog records and normal xattrs stored in the HFS+ attributes B-tree.

## Main Entry Points

- `hfsplus_xattr_handlers[]`: registers OSX, user, trusted, and security handlers.
- `__hfsplus_setxattr()` / `hfsplus_setxattr()`: set, replace, create, or remove xattrs.
- `__hfsplus_getxattr()` / `hfsplus_getxattr()`: read Finder Info or inline attribute records.
- `hfsplus_listxattr()`: lists Finder Info and attributes B-tree names, applying namespace visibility rules.
- `hfsplus_removexattr()`: deletes B-tree attributes and updates catalog flags.
- `hfsplus_create_attributes_file()`: lazily creates and initializes the attributes B-tree file.

## Control Flow And State

The file rejects xattr operations on resource-fork inodes. Finder Info uses catalog record fields directly and requires exact fixed sizes for file or folder records. Other xattrs require an attributes tree; if missing, set operations try to create one using `attr_tree_state` transitions from empty to creating to valid or failed. B-tree header and map nodes are initialized manually, written page-by-page through the attributes file mapping, and then opened with `hfs_btree_open()`.

For ordinary set operations, catalog lookup runs first, then existing attributes are replaced or new records are created through HFS+ attribute helpers. Catalog flags `HFSPLUS_XATTR_EXISTS` and `HFSPLUS_ACL_EXISTS` are updated after successful writes. Removal deletes the attribute and clears flags if the ACL or final xattr disappears. Reads only support inline data records; fork-data or extents xattrs return `-EOPNOTSUPP`.

Listing first probes Finder Info for nonzero data, then walks the attributes tree from the inode CNID, converts Unicode xattr names to filesystem strings, prefixes unnamespaced names with `osx.`, and hides `trusted.*` unless the caller has `CAP_SYS_ADMIN`.

## Dependencies

Uses HFS+ catalog, attributes, B-tree, inode dirtying, Unicode conversion, Linux xattr namespace constants, and capability checks. It is tightly coupled to `hfsplus_attr_*()` helpers in the attributes implementation.

## Risks

Only inline xattrs are supported for reads. Attribute-tree creation has a state machine that can permanently mark the tree failed for non-ENOSPC errors. Name construction uses fixed maximum HFS+ attribute name sizing. Catalog flag updates and attributes-tree changes must remain consistent or later list/lookup behavior can diverge from on-disk metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr.h

## Purpose

Declares HFS+ xattr handlers and internal xattr helper APIs shared by the namespace-specific handler files and the core xattr implementation.

## API Surface

Exports declarations for `hfsplus_xattr_osx_handler`, `hfsplus_xattr_user_handler`, `hfsplus_xattr_trusted_handler`, `hfsplus_xattr_security_handler`, and the handler array. It declares internal and prefixed set/get helpers, listxattr, and `hfsplus_init_security()`.

## Dependencies

Includes `<linux/xattr.h>` and relies on HFS+ inode/superblock types being visible to C files including this header.

## Risks

This header is the namespace-handler contract. Signature drift between VFS xattr handler callbacks and these declarations would break compilation across all HFS+ xattr files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_security.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_security.c

## Purpose

Provides the `security.*` xattr namespace handler and initial security-label setup for HFS+ inodes.

## Main Entry Points

- `hfsplus_security_getxattr()` and `hfsplus_security_setxattr()`: delegate to the core HFS+ xattr helpers with `XATTR_SECURITY_PREFIX`.
- `hfsplus_init_security()`: calls `security_inode_init_security()` with an HFS+ callback.
- `hfsplus_initxattrs()`: writes security xattrs supplied by the LSM during inode creation.
- `hfsplus_xattr_security_handler`: VFS handler descriptor.

## Control Flow And State

Initialization allocates a maximum-sized HFS+ xattr name buffer, skips empty security names, prefixes each LSM name with `security.`, and writes it through `__hfsplus_setxattr()`.

## Dependencies

Depends on Linux security hooks, xattr namespace constants, HFS+ xattr core helpers, and HFS+ attribute name length limits.

## Risks

Security-label persistence depends on HFS+ attributes-tree creation during inode initialization. Any failure stops the loop and returns the first error, potentially aborting inode creation or leaving only earlier labels written.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_trusted.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_trusted.c

## Purpose

Implements the `trusted.*` HFS+ xattr namespace handler.

## Main Entry Points

- `hfsplus_trusted_getxattr()`
- `hfsplus_trusted_setxattr()`
- `hfsplus_xattr_trusted_handler`

## Control Flow And Dependencies

The callbacks simply prepend `XATTR_TRUSTED_PREFIX` through the shared `hfsplus_getxattr()` and `hfsplus_setxattr()` helpers. Visibility filtering for `trusted.*` is handled in the core list function.

## Risks

The file relies entirely on VFS-level namespace permission handling plus the core HFS+ `can_list()` behavior. There is no local validation beyond passing the trusted prefix.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_user.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_user.c

## Purpose

Implements the `user.*` HFS+ xattr namespace handler.

## Main Entry Points

- `hfsplus_user_getxattr()`
- `hfsplus_user_setxattr()`
- `hfsplus_xattr_user_handler`

## Control Flow And Dependencies

The callbacks delegate to the core HFS+ get/set helpers with `XATTR_USER_PREFIX`. All storage, namespace formatting, attributes-tree access, and errors are handled in `xattr.c`.

## Risks

No file-local checks are present. Behavior depends on the shared xattr implementation correctly handling HFS+ unsupported states, resource-fork inodes, and attribute-tree availability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/hostfs/Makefile

## Purpose

Build rules for UML hostfs.

## Build Behavior

`hostfs.o` is built from `hostfs_kern.o`. When `CONFIG_HOSTFS` is enabled, `hostfs_user.o` and `hostfs_user_exp.o` are included in built-in hostfs objects. The file includes `arch/um/scripts/Makefile.rules`, reflecting that hostfs is specific to User-Mode Linux.

## Risks

The split between kernel-facing hostfs code and UML userspace syscall wrappers is build-system dependent. Moving these objects outside UML rules would break symbol availability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs.h -->
# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs.h

## Purpose

Defines the ABI between hostfs kernel-facing code and UML host syscall adapter code.

## API Surface

Defines `hostfs_timespec`, `hostfs_iattr`, and `hostfs_stat`, then declares wrappers for stat/access/open/dir iteration/read/write/fsync/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/statfs.

## Dependencies

Includes UML OS support and generated asm offsets. Types mirror Linux inode attributes but use host-compatible scalar fields and encoded device major/minor pairs.

## Risks

This is a boundary header between VFS code and host syscall code. Layout or type mismatches can corrupt inode metadata, timestamps, or device numbers across the UML boundary.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_kern.c -->
# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_kern.c

## Purpose

Implements the UML `hostfs` filesystem on the Linux VFS side, mapping VFS operations to host-path syscall wrappers.

## Main Entry Points

Defines superblock operations, inode operations for files/directories/symlinks, file operations, address-space operations, fs_context operations, and module init/exit for the `hostfs` filesystem type.

## Control Flow And State

Mount state stores a `host_root_path`. Inode state stores a shared host fd, accumulated open mode, host device identity, birth time, and an open mutex. Path construction uses `dentry_path_raw()` and prefixes the configured host root.

Open upgrades the inode’s shared host fd to cover requested read/write modes, using `dup2()` through `replace_file()` when needed. Read/write page-cache paths call `read_file()` and `write_file()` at folio offsets. Directory iteration opens the host directory for each readdir, seeks to `ctx->pos`, emits entries, and closes it.

Inode instantiation uses `stat_file()` plus `iget5_locked()` keyed by inode number, device, file type, and birth time. Create/mkdir/mknod/link/unlink/symlink/rmdir/rename delegate to host wrappers and then instantiate or update dentries. `hostfs_permission()` combines host `access()` with generic permission. `hostfs_setattr()` translates VFS `iattr` fields to `hostfs_iattr`, suppressing size truncation in append mode.

Mount parsing appends mount-supplied paths to the global `root_ino` prefix. The root inode follows symlinks once if the root path resolves to a symlink.

## Dependencies

Depends on UML setup hooks, the syscall wrappers declared in `hostfs.h`, Linux fs_context, page cache helpers, generic VFS permission/setattr helpers, and a kmem cache for hostfs inodes.

## Risks

Path confinement relies on string prefixing and host filesystem permissions. Append mode blocks unlink and truncation but does not make the whole filesystem immutable. The shared inode fd model requires careful mode upgrades and mutex use. `hostfs_kill_sb()` frees `s_fs_info` directly while `hostfs_fc_free()` also frees fs_context state; mount lifecycle must preserve ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_kern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_user.c -->
# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_user.c

## Purpose

Provides UML host syscall wrappers used by `hostfs_kern.c`.

## Main Entry Points

Implements all functions declared in `hostfs.h`: `stat_file`, `access_file`, `open_file`, directory iteration, pread/pwrite/lseek/fsync, creation, metadata updates, links, unlink, mkdir/rmdir/mknod, rename/renameat2, readlink, and statfs.

## Control Flow And State

The code converts host `statx` into `hostfs_stat`, including birth time when available. It returns Linux-style negative errno values. `set_attr()` applies mode, uid, gid, size, and explicit atime/mtime changes, using fd-based operations when an fd is available and path-based calls otherwise. `rename2_file()` uses `SYS_renameat2` when available, mapping `ENOSYS` or missing syscall support to `-EINVAL`.

## Dependencies

Uses libc/syscall interfaces available to UML userspace code, `os_makedev()` for device numbers, and `panic()` for impossible open modes.

## Risks

The wrappers expose host kernel behavior directly, including filesystem-specific statfs and rename semantics. Timestamp setting uses microsecond `utimes/futimes`, losing nanosecond precision. `replace_file()` returns raw `dup2()` errors without converting errno to negative values, unlike most other wrappers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_user_exp.c -->
# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_user_exp.c

## Purpose

Exports hostfs syscall-wrapper symbols for GPL modules.

## API Surface

Uses `EXPORT_SYMBOL_GPL()` for all hostfs user adapter functions, including stat/access/open/read/write/metadata/namespace/statfs helpers.

## Dependencies

Includes `<linux/module.h>` and `hostfs.h`.

## Risks

This file makes the hostfs syscall adapter available across object boundaries. The exported function list must stay synchronized with `hostfs.h` and the build split.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hostfs/hostfs_user_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/Kconfig

## Purpose

Defines the `HPFS_FS` kernel configuration option.

## Behavior

`HPFS_FS` is a tristate filesystem option for OS/2 HPFS support. It depends on `BLOCK` and selects `BUFFER_HEAD` and `FS_IOMAP`. Help text documents read/write support for HPFS partitions and module name `hpfs`.

## Risks

The option enables write-capable HPFS support. It selects legacy buffer-head infrastructure and iomap support required by the implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/Makefile

## Purpose

Build rules for the HPFS filesystem module.

## Build Behavior

Builds `hpfs.o` when `CONFIG_HPFS_FS` is enabled. The object is composed of allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and superblock source files.

## Risks

The object list captures the filesystem’s subsystem boundaries. Omitting any component would break exported operations referenced through `hpfs_fn.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/alloc.c

## Purpose

Implements HPFS allocation bitmap management, dnode/fnode/anode allocation, free counters, and discard trimming.

## Main Entry Points

- `hpfs_alloc_sector()`, `hpfs_alloc_if_possible()`, `hpfs_free_sectors()`
- `hpfs_check_free_dnodes()`, `hpfs_alloc_dnode()`, `hpfs_free_dnode()`
- `hpfs_alloc_fnode()`, `hpfs_alloc_anode()`
- `hpfs_chk_sectors()`
- `hpfs_trim_fs()`

## Control Flow And State

Main bitmap bits use `1` for free and `0` for allocated. Allocation searches near a target sector, cached bitmap, then all bitmaps, reducing forward preallocation demand if needed. Directory dnodes prefer or avoid the directory band depending on free dnode pressure. Free counters are maintained unless an underflow/overflow is detected, in which case the count is invalidated with `(unsigned)-1`.

`hpfs_alloc_dnode()` initializes a 2048-byte dnode across four sectors with magic, first-free offset, sentinel dirents, and self pointer. Fnodes and anodes are initialized with their magic values and B+ tree free-node counts. `hpfs_trim_fs()` scans free runs in the directory-band bitmap and main bitmaps and issues discard requests within caller-supplied bounds.

## Dependencies

Uses bitmap mapping from `map.c`, four-sector buffer helpers from `buffer.c`, and HPFS superblock state.

## Risks

Allocation correctness depends on bitmap bit semantics and 4-sector dnode alignment. Dnode splitting callers rely on `hpfs_check_free_dnodes()` to avoid mid-operation ENOSPC corruption. Trim takes the HPFS global lock per bitmap and returns `-EROFS` if the filesystem becomes read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/anode.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/anode.c

## Purpose

Manages HPFS allocation B+ trees in fnodes and anodes, including lookup, append, truncation, EA data access, and recursive-free logic.

## Main Entry Points

- `hpfs_bplus_lookup()`: maps file sector numbers to disk sectors.
- `hpfs_add_sector_to_btree()`: appends a sector, splitting B+ tree nodes as needed.
- `hpfs_remove_btree()` and `hpfs_truncate_btree()`: free or shrink allocation trees.
- `hpfs_ea_read()`, `hpfs_ea_write()`, `hpfs_ea_remove()`: access EA storage through direct extents or anodes.
- `hpfs_remove_fnode()`: frees a file or directory fnode, allocation tree/dtree, and EAs.

## Control Flow And State

B+ trees are either leaf extent arrays or internal anode-pointer arrays. Lookup descends internal nodes until a leaf contains the requested file sector, updating the inode’s allocation cache. Appending first attempts to extend the final extent contiguously; otherwise it allocates a new sector and inserts a leaf node, splitting anodes upward and possibly turning the fnode root into an internal node.

Removal avoids recursion to prevent stack overflow. Truncation walks down the subtree containing the truncation boundary, frees later subtrees or extents, and updates used/free node counts and first-free offsets.

## Dependencies

Depends on allocation helpers, fnode/anode mapping, cycle detection, sector validation, and B+ tree structure definitions from `hpfs.h`.

## Risks

This is a high-risk metadata mutation file. Split and root-promotion paths must keep `up` pointers, `BP_fnode_parent`, node counts, and `first_free` consistent. Some EA-anode creation paths are not implemented in `ea.c`, so EA users depend on fallback contiguous relocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/anode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/buffer.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/buffer.c

## Purpose

Provides HPFS sector and four-sector buffer mapping helpers with hotfix remapping and readahead.

## Main Entry Points

- `hpfs_search_hotfix_map()` and `_for_range()`
- `hpfs_prefetch_sectors()`
- `hpfs_map_sector()` / `hpfs_get_sector()`
- `hpfs_map_4sectors()` / `hpfs_get_4sectors()`
- `hpfs_brelse4()` and `hpfs_mark_4buffers_dirty()`

## Control Flow And State

Reads check the hotfix map before buffer access. Four-sector mapping validates alignment and either returns contiguous buffer memory or allocates a temporary 2048-byte concatenation buffer. Dirtying a noncontiguous four-sector buffer copies the temporary data back into the four buffer heads before marking them dirty.

## Dependencies

Uses buffer-head APIs, block readahead, HPFS global lock assertions, and superblock hotfix arrays.

## Risks

Callers must hold the HPFS global lock. Noncontiguous four-sector buffers require explicit `hpfs_mark_4buffers_dirty()` before release or updates are lost. Hotfix ranges suppress merged readahead and merged iomap ranges elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dentry.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/dentry.c

## Purpose

Defines HPFS dcache hashing and comparison behavior for case-insensitive, OS/2-style filename rules.

## Main Entry Points

- `hpfs_hash_dentry()`
- `hpfs_compare_dentry()`
- `hpfs_dentry_operations`

## Control Flow And State

Hashing trims trailing dots/spaces except for `.` and `..`, then hashes uppercase-normalized bytes using the mounted code-page table. Comparison validates the candidate name and compares names through `hpfs_compare_names()`.

## Dependencies

Depends on name helpers and `sb_cp_table`.

## Risks

Correct dcache behavior depends on matching on-disk HPFS collation and trimming rules. Invalid lookup names fail comparison rather than matching existing dentries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/dir.c

## Purpose

Implements HPFS directory VFS operations: lseek, readdir, lookup, release, and directory file operations.

## Main Entry Points

- `hpfs_readdir()`
- `hpfs_lookup()`
- `hpfs_dir_lseek()`
- `hpfs_dir_ops`

## Control Flow And State

Directory positions encode dnode sector and dirent index. `hpfs_readdir()` emits `.` and `..`, registers the file position for later dnode mutation fixups, walks dirents through `map_pos_dirent()`, skips sentinel first/last entries, translates names for lowercase mount behavior, and emits entries.

Lookup validates and adjusts the target name, searches the dnode tree, instantiates the fnode inode with `iget_locked()`, optionally reads the fnode when directory or EA metadata is needed, and fills inode size/time/mode information from the directory entry when possible.

## Dependencies

Uses dnode tree traversal, inode initialization, code-page name translation, and HPFS global locking.

## Risks

Directory position tracking is tied to mutation code in `dnode.c`; missed `hpfs_del_pos()` calls can leave stale position pointers. Lookup rejects HPFS386 ACL/XPERM entries for writable mounts because this driver does not support those structures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dnode.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/dnode.c

## Purpose

Implements HPFS directory dnode tree operations: dirent insertion, deletion, lookup, traversal, position repair, dnode splitting/merging, and empty-directory cleanup.

## Main Entry Points

- `hpfs_add_pos()` / `hpfs_del_pos()`: track live readdir positions.
- `hpfs_add_de()` and `hpfs_add_dirent()`: insert directory entries.
- `hpfs_remove_dirent()`: delete directory entries and rebalance.
- `hpfs_count_dnodes()`: count directory blocks, subdirectories, and items.
- `map_pos_dirent()`, `map_dirent()`, `map_fnode_dirent()`: traversal/search helpers.
- `hpfs_remove_dtree()`: frees an empty directory tree.
- `hpfs_de_as_down_as_possible()`: finds the leftmost reachable dnode for iteration.

## Control Flow And State

Dnodes form a B-tree-like sorted directory tree. Insertions descend by HPFS name comparison, then either fit a new dirent into the current dnode or split the dnode, allocating sibling/root dnodes and promoting a separator dirent upward. Deletions remove a dirent, optionally move the predecessor/successor from a child subtree to the top, and delete empty dnodes while repairing parent down pointers and root dnode ownership.

The file maintains active `loff_t *` directory positions for open readdir streams. Mutation helpers substitute, insert, or delete encoded positions so concurrent directory iteration remains coherent.

## Dependencies

Depends on allocation/free dnode helpers, four-sector dnode mapping, fnode mapping, name comparison, cycle detection, and HPFS inode directory state.

## Risks

This is the most complex HPFS mutation code. ENOSPC during split/delete can corrupt the directory tree, so callers preflight free dnode availability. Position-repair logic is fragile and encodes sentinel values such as `4`, `5`, and `12`. Corrupt up/down pointers are detected in strict check modes but often only log errors before returning.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/dnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/ea.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/ea.c

## Purpose

Handles HPFS extended attributes stored in fnodes, external sector runs, or anode-backed storage.

## Main Entry Points

- `hpfs_ea_ext_remove()`
- `hpfs_read_ea()`
- `hpfs_get_ea()`
- `hpfs_set_ea()`

## Control Flow And State

EA lookup first scans fnode-resident EAs, then external EAs referenced by `ea_secno` and `ea_size_l`. Indirect EAs are read through the sector/anode pointer encoded in the EA value. `hpfs_set_ea()` updates existing EAs only when the size matches; otherwise it appends a new EA to fnode storage if it fits, migrates fnode EAs to external storage if needed, and grows or relocates external sector runs.

## Dependencies

Uses EA read/write helpers from `anode.c`, allocation helpers, fnode layout accessors, and HPFS global metadata rules.

## Risks

The code explicitly cannot resize existing EAs and contains rarely used fallback paths for large external EA growth. EA-anode creation is commented out, so fragmented growth relocates data instead. Corrupt EA length/name fields can stop reads or removals with filesystem errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/file.c

## Purpose

Implements HPFS regular-file operations, page-cache integration, block mapping, truncation, fsync, and fiemap.

## Main Entry Points

- `hpfs_bmap()` and `hpfs_get_block()`
- `hpfs_truncate()`
- `hpfs_read_folio()`, `hpfs_readahead()`, `hpfs_writepages()`
- `hpfs_write_begin()` / `hpfs_write_end()`
- `hpfs_fiemap()`
- `hpfs_file_ops`, `hpfs_file_iops`, `hpfs_aops`

## Control Flow And State

Block mapping first uses a small per-inode allocation cache, then consults the fnode B+ tree. Writes are contiguous-growth oriented: allocation is only allowed when the requested block is exactly at `mmu_private`. New blocks are appended through `hpfs_add_sector_to_btree()`. Write failures beyond EOF truncate page cache and metadata back. Successful writes mark the HPFS inode dirty for later fnode/dirent update.

`fiemap` uses iomap read-only mapping, respecting hotfix boundaries.

## Dependencies

Uses mpage, iomap, buffer-head block mapping, anode allocation-tree helpers, hotfix remapping, and inode writeback helpers.

## Risks

The write path assumes append-style block growth and calls `BUG()` on unexpected sparse-create attempts. Hotfix remapping can split otherwise contiguous extents. `hpfs_truncate()` requires the HPFS lock and directly mutates allocation trees.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/hpfs.h -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/hpfs.h

## Purpose

Defines HPFS on-disk structures, constants, endian-dependent bitfields, and low-level accessors.

## Main Contents

Defines sector-number typedefs, boot block, super block, spare block, code-page structures, dnodes and dirents, B+ tree headers and nodes, fnodes, anodes, and extended attributes. It also defines magic values, B+ tree flags, fnode flags, EA flags, and helpers such as `bp_internal()`, `bp_fnode_parent()`, `fnode_in_anode()`, `fnode_is_dir()`, `ea_indirect()`, and `ea_in_anode()`.

## Dependencies

Requires the build endian macros and Linux flexible-array/container helpers. The structures are consumed by every HPFS source file.

## Risks

The header documents that HPFS knowledge is partly conjectural. Bitfield layouts are endian-sensitive. Any structure packing, offset, or flag change directly affects on-disk compatibility and corruption risk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/hpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/hpfs_fn.h -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/hpfs_fn.h

## Purpose

Central internal HPFS header for runtime state structures, inline helpers, prototypes, time conversion, and locking.

## Main Contents

Defines `hpfs_inode_info`, `hpfs_sb_info`, `quad_buffer_head`, dirent/EA inline accessors, bitmap bit testing, subsystem prototypes, and global lock helpers. It also defines allocation/read-ahead constants and HPFS-specific error aliases.

## Control Flow And State

`hpfs_sb_info` holds the global HPFS mutex, mount options, bitmap directory, code-page table, hotfix map, and allocation counters. `hpfs_inode_info` caches allocation lookup state, directory root dnode, EA metadata flags, dirty state, and active readdir positions. Locking is intentionally filesystem-wide via `hpfs_lock()`.

## Dependencies

Includes Linux mutex, pagemap, buffer-head, slab, signal, block-device, unaligned helpers, plus `hpfs.h`.

## Risks

All HPFS implementation files share this header. The global-lock model simplifies correctness but limits concurrency. Inline dirent and EA accessors assume validated on-disk lengths; misuse on corrupt data can produce invalid pointer arithmetic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/hpfs_fn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/inode.c

## Purpose

Implements HPFS inode initialization, fnode-to-inode loading, inode writeback, setattr, dirty flush, and eviction.

## Main Entry Points

- `hpfs_init_inode()`
- `hpfs_read_inode()`
- `hpfs_write_inode()` / `hpfs_write_inode_nolock()`
- `hpfs_setattr()`
- `hpfs_write_if_changed()`
- `hpfs_evict_inode()`

## Control Flow And State

Inode initialization applies mount default uid/gid/mode and clears HPFS-private caches. Reading an inode maps its fnode, optionally reads EAs for UID/GID/SYMLINK/MODE/DEV, initializes special files or symlinks from EAs, and otherwise configures directory or regular-file operations. Directories count dnodes/subdirectories for size/link count; files set size and address-space ops from the fnode.

Writeback finds the parent directory entry through the fnode and updates file size, times, read-only flag, EA size, and mode/uid/gid/device EAs when EA write support is enabled. `setattr` forbids growing files, validates 16-bit uid/gid limits, truncates on shrink, and writes metadata. Eviction removes fnodes for unlinked inodes.

## Dependencies

Uses fnode mapping, EA helpers, directory search helpers, file/directory/symlink operations, time conversion, and global HPFS locking.

## Risks

HPFS stores Unix metadata in optional EAs, so behavior depends on the `eas` mount mode. Root inode writeback is skipped. File growth through setattr is rejected; normal writes grow through the file block allocator.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/map.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/map.c

## Purpose

Maps HPFS on-disk metadata structures into memory and validates them under configured check levels.

## Main Entry Points

- `hpfs_map_dnode_bitmap()`, `hpfs_map_bitmap()`, `hpfs_prefetch_bitmap()`
- `hpfs_load_code_page()`
- `hpfs_load_bitmap_directory()`
- `hpfs_load_hotfix_map()`
- `hpfs_map_fnode()`, `hpfs_map_anode()`, `hpfs_map_dnode()`
- `hpfs_fnode_dno()`

## Control Flow And State

Bitmap mapping loads four-sector bitmaps through the bitmap directory and prefetches following bitmaps. Code-page loading validates directory/data offsets and builds a 256-byte upper/lowercase table. Hotfix loading validates spare counts and copies remap arrays.

Fnode/anode/dnode mapping wraps buffer helpers and, when checks are enabled, validates magic, self pointers, B+ tree node counts, first-free offsets, EA bounds, and dirent layout.

## Dependencies

Uses buffer mapping helpers, HPFS on-disk structures, allocation-sector checks, and superblock state.

## Risks

Validation is central to avoiding bad pointer arithmetic in higher-level code. In readonly mode, one dnode name-length mismatch is tolerated if the stored dirent is larger than expected. Incorrect check-level behavior can either reject mountable damaged volumes or allow later corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/name.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/name.c

## Purpose

Implements HPFS filename validation, case mapping, comparison, lowercase presentation, long-name detection, and OS/2 trailing-dot/space trimming.

## Main Entry Points

- `hpfs_upcase()`
- `hpfs_chk_name()`
- `hpfs_translate_name()`
- `hpfs_compare_names()`
- `hpfs_is_name_long()`
- `hpfs_adjust_length()`

## Control Flow And State

Validation rejects names longer than 254 bytes, empty names after trimming, reserved characters, `.`, and `..`. Comparison uppercases through the mount code-page table and treats HPFS last sentinel entries as greater than all real names. Lowercase translation allocates a new name buffer only when the lowercase mount option is active.

## Dependencies

Uses the per-superblock code-page table loaded from disk.

## Risks

Name collation must match HPFS directory-tree ordering. `hpfs_is_name_long()` appears to test `name[i]` instead of `name[j]` in the extension loop, preserving existing kernel behavior but making the long-name flag check subtle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/namei.c

## Purpose

Implements HPFS namespace mutation operations: create, mkdir, mknod, symlink, unlink, rmdir, rename, and symlink page reads.

## Main Entry Points

- `hpfs_create()`
- `hpfs_mkdir()`
- `hpfs_mknod()`
- `hpfs_symlink()`
- `hpfs_unlink()`
- `hpfs_rmdir()`
- `hpfs_rename()`
- `hpfs_symlink_read_folio()`
- `hpfs_dir_iops`, `hpfs_symlink_aops`

## Control Flow And State

Create and mkdir validate names, allocate fnodes and optionally dnodes, construct directory entries, instantiate inodes, insert dirents into the parent dnode tree, fill fnodes, update current uid/gid/mode through EAs if needed, and update parent directory times. Special files and symlinks require EA write support because their mode/device/target are stored in EAs; symlink contents use a `SYMLINK` EA read through a folio operation.

Unlink and rmdir locate the dirent, reject protected sentinel entries and wrong file types, remove the dirent through `hpfs_remove_dirent()`, and drop link counts. Rmdir first counts items in the target directory tree.

Rename supports only `RENAME_NOREPLACE`. It rejects overwriting directories, copies the old dirent, removes or replaces target entries, inserts into the new directory, removes the old entry, updates parent link counts for directories, and rewrites the fnode parent/name fields.

## Dependencies

Uses allocation, dnode mutation, EA writing, inode initialization/writeback, time conversion, and global HPFS locking.

## Risks

Namespace updates involve multi-step metadata mutation without journaling. Several failure paths can return ENOSPC/EFSERROR after partial work, relying on conservative preflight and cleanup. Rename-over-file updates the existing target dirent after removing the old one, so consistency depends on successful target lookup after deletion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/namei.c -->