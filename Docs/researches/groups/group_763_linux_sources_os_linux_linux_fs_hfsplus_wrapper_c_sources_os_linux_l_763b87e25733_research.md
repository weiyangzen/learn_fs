# Group Research: group_763_linux_sources_os_linux_linux_fs_hfsplus_wrapper_c_sources_os_linux_l_763b87e25733

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/wrapper.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/wrapper.c

Purpose: Handles low-level HFS+ volume wrapper discovery and volume-header I/O, including plain HFS+ volumes, HFSX volumes, HFS wrapper MDBs, partition-block discovery, and CD-ROM multisession offsets.

Key functions:
- `hfsplus_submit_bio()` performs aligned block-device I/O using `hfsplus_min_io_size()`, returning an offset data pointer for unaligned logical HFS+ sectors.
- `hfsplus_read_mdb()` parses an HFS wrapper MDB, validates embedded HFS+ signatures and wrapper flags, and extracts allocation-block and embedded-volume extents.
- `hfsplus_get_last_session()` resolves the selected or last CD-ROM data session using CD-ROM TOC/multisession APIs.
- `hfsplus_read_wrapper()` initializes minimum I/O size, reads primary and backup volume headers, follows wrappers/partition maps, validates signatures/block sizes, sets superblock block size, and records HFS+ partition offsets.

Dependencies and integration:
- Uses Linux block-device helpers, CD-ROM APIs, HFS partition discovery, and HFS+ raw constants.
- Populates `struct hfsplus_sb_info` fields such as `s_vhdr`, `s_backup_vhdr`, `alloc_blksz`, `blockoffset`, `part_start`, `sect_count`, and `fs_shift`.

Risk notes:
- Correctness depends on sector and block-size alignment; writes rely on buffers matching prior aligned reads.
- Wrapper/partition rediscovery uses `goto reread`, so corrupt metadata can steer repeated reads until validation fails.
- Memory allocated for volume-header buffers is freed only on error paths here; ownership transfers to mounted superblock state on success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/xattr.c

Purpose: Implements HFS+ extended attribute operations and dispatches xattr namespaces. It manages Finder-info catalog attributes, OS X unprefixed attributes, Linux namespace-prefixed attributes, and lazy creation of the HFS+ Attributes File B-tree.

Key functions:
- `hfsplus_create_attributes_file()` initializes an empty HFS+ Attributes File with header/map nodes, allocates clump blocks, opens the B-tree, and transitions `attr_tree_state`.
- `__hfsplus_setxattr()` handles set/remove requests, special-cases `com.apple.FinderInfo`, creates or replaces inline attributes, and updates catalog xattr/ACL flags.
- `hfsplus_setxattr()` prefixes Linux namespace names before calling the core setter.
- `hfsplus_getxattr_finder_info()` reads Finder info directly from catalog folder/file records.
- `__hfsplus_getxattr()` locates xattr records in the Attributes File and returns inline data; fork/extents xattr payloads are explicitly unsupported.
- `hfsplus_listxattr()` lists Finder info and Attributes File records, converting HFS+ Unicode names and hiding trusted attributes unless privileged.
- `hfsplus_removexattr()` deletes an attribute and clears catalog `HFSPLUS_XATTR_EXISTS`/`HFSPLUS_ACL_EXISTS` flags when appropriate.
- `hfsplus_osx_getxattr()` and `hfsplus_osx_setxattr()` expose OS X unprefixed attributes through the synthetic `osx.` namespace while rejecting known Linux prefixes.

Dependencies and integration:
- Uses HFS+ catalog B-tree lookup, Attributes File B-tree helpers, Unicode conversion helpers, inode dirty marking, and VFS `xattr_handler` registration.
- Coordinates with namespace handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c`.
- Uses `HFSPLUS_ATTR_CNID`, catalog flags, and HFS+ inline attribute record structures.

Risk notes:
- Attribute tree creation is stateful and concurrent via `atomic_cmpxchg`; callers can receive `-EAGAIN`, `-EOPNOTSUPP`, `-ENOSPC`, or `-EIO` depending on tree state.
- Only inline attribute data is supported; fork/extents records return `-EOPNOTSUPP`.
- Name buffers are sized for maximum charset expansion, but prefix/name concatenation assumes VFS-provided names fit expected HFS+ limits.
- Finder info does not live in the Attributes File and has separate size validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr.h -->
# File Research: sources/os/linux/linux/fs/hfsplus/xattr.h

Purpose: Declares the HFS+ xattr handler interface shared by the core xattr implementation and per-namespace handler files.

Key declarations:
- Extern handler objects for OS X, user, trusted, and security namespaces.
- `hfsplus_xattr_handlers[]` exported handler table.
- Core internal and prefixed get/set APIs: `__hfsplus_setxattr()`, `hfsplus_setxattr()`, `__hfsplus_getxattr()`, `hfsplus_getxattr()`.
- `hfsplus_listxattr()` for VFS listxattr.
- `hfsplus_init_security()` for security label initialization during inode creation.

Dependencies and integration:
- Includes Linux xattr definitions and is consumed by HFS+ inode/directory creation and all xattr namespace files.

Risk notes:
- The header exposes both raw full-name APIs and prefix-composing APIs; callers must choose the correct layer to avoid duplicate prefixes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_security.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/xattr_security.c

Purpose: Implements the HFS+ `security.*` xattr namespace and security label initialization hook.

Key functions:
- `hfsplus_security_getxattr()` reads `security.*` attributes through `hfsplus_getxattr()`.
- `hfsplus_security_setxattr()` writes `security.*` attributes through `hfsplus_setxattr()`.
- `hfsplus_initxattrs()` receives LSM-provided initial security xattrs, prefixes them with `security.`, and stores them via `__hfsplus_setxattr()`.
- `hfsplus_init_security()` calls `security_inode_init_security()` with the HFS+ initializer callback.

Dependencies and integration:
- Uses Linux security/xattr APIs and the shared HFS+ xattr core.
- Exported as `hfsplus_xattr_security_handler`.

Risk notes:
- Initial xattr name allocation uses the HFS+ max expanded attribute-name size and concatenates prefix plus LSM name.
- Empty security xattr names are skipped during initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_trusted.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/xattr_trusted.c

Purpose: Implements the HFS+ `trusted.*` xattr namespace handler.

Key functions:
- `hfsplus_trusted_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_TRUSTED_PREFIX`.
- `hfsplus_trusted_setxattr()` delegates writes/removals to `hfsplus_setxattr()` with the trusted prefix.

Dependencies and integration:
- Shares all storage behavior with `xattr.c`.
- Exported as `hfsplus_xattr_trusted_handler`.

Risk notes:
- Permission filtering for listing trusted names is handled in the core list path, not in this small handler.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_user.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/xattr_user.c

Purpose: Implements the HFS+ `user.*` xattr namespace handler.

Key functions:
- `hfsplus_user_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_USER_PREFIX`.
- `hfsplus_user_setxattr()` delegates writes/removals to `hfsplus_setxattr()` with the user prefix.

Dependencies and integration:
- Shares all storage behavior with `xattr.c`.
- Exported as `hfsplus_xattr_user_handler`.

Risk notes:
- This handler is intentionally thin; validation and HFS+ storage limitations are enforced by the shared core.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hostfs/Makefile -->
# File Research: sources/os/linux/linux/fs/hostfs/Makefile

Purpose: Builds UML hostfs objects and links the kernel-side filesystem with user-space syscall bridge objects.

Key content:
- Defines `hostfs-objs := hostfs_kern.o`.
- Adds `hostfs_user.o` and `hostfs_user_exp.o` to built-in hostfs support when `CONFIG_HOSTFS` is enabled.
- Adds `hostfs.o` under `obj-$(CONFIG_HOSTFS)`.
- Includes UML-specific `arch/um/scripts/Makefile.rules`.

Dependencies and integration:
- Hostfs is specific to User-Mode Linux and depends on UML build rules for user/kernel object handling.

Risk notes:
- Split object handling is unusual: kernel-facing code and exported user syscall bridge symbols are built together through UML-specific rules.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hostfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs.h -->
# File Research: sources/os/linux/linux/fs/hostfs/hostfs.h

Purpose: Defines the ABI between UML kernel hostfs code and host-side syscall wrapper code.

Key definitions:
- `struct hostfs_timespec`, `struct hostfs_iattr`, and `struct hostfs_stat` mirror metadata passed across the hostfs boundary.
- Declares wrapper functions for stat/access/open/read/write/fsync, directory iteration, creation/removal/linking/renaming, symlink read/write, attribute updates, special node creation, and statfs.

Dependencies and integration:
- Includes UML OS and generated asm-offset headers.
- Implemented by `hostfs_user.c`, exported by `hostfs_user_exp.c`, and consumed by `hostfs_kern.c`.

Risk notes:
- This is an internal ABI; field sizes and signedness must stay compatible between kernel UML code and user syscall wrappers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_kern.c -->
# File Research: sources/os/linux/linux/fs/hostfs/hostfs_kern.c

Purpose: Implements the UML hostfs VFS layer, mapping Linux VFS operations inside UML to filesystem operations on the host path namespace.

Key functions:
- `hostfs_args()` parses early UML `hostfs=` boot options for root confinement and append mode.
- `dentry_name()` and `inode_name()` construct host paths by combining the configured host root with VFS dentry paths.
- `follow_link()` resolves a hostfs root symlink during mount setup.
- `hostfs_statfs()` fills VFS statfs data from host `statfs64`.
- Inode lifecycle functions allocate, initialize, evict, and free `hostfs_inode_info`, including host file descriptor cleanup.
- `hostfs_readdir()` opens the host directory, seeks to `ctx->pos`, reads host dirents, and emits them to VFS.
- `hostfs_open()` opens or upgrades a cached host fd for read/write mode under `open_mutex`.
- `hostfs_read_folio()`, `hostfs_write_begin()`, `hostfs_write_end()`, and `hostfs_writepages()` implement page-cache I/O through `read_file()`/`write_file()`.
- `hostfs_iget()` obtains or updates VFS inodes using host `statx` identity, including device and birth-time matching.
- Namespace operations create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename host paths.
- `hostfs_permission()` delegates access checks to host `access()` for non-special files and then applies generic VFS permission.
- `hostfs_setattr()` maps VFS attributes to host chmod/chown/truncate/time operations.
- FS context functions parse mount parameters, set up a nodev superblock, and register `hostfs`.

Dependencies and integration:
- Consumes all host-side wrappers from `hostfs.h`.
- Uses VFS inode/file/address-space operations, fs_context parsing, dcache aliases, and UML setup hooks.

Risk notes:
- Host path construction is central security surface; root confinement depends on raw dentry path handling and configured `root_ino`.
- Append mode blocks unlink and truncation but still allows other host mutations.
- Cached fd mode upgrades use `dup2` replacement and shared inode state; concurrent opens are serialized with `open_mutex`.
- Hostfs does not cache dentries (`DCACHE_DONTCACHE`), reflecting the host namespace’s external mutability.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_kern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_user.c -->
# File Research: sources/os/linux/linux/fs/hostfs/hostfs_user.c

Purpose: Implements host-side syscall wrappers used by UML hostfs kernel code.

Key functions:
- `statx_to_hostfs()` converts Linux `statx` results into `struct hostfs_stat`.
- `stat_file()` uses `statx()` with `AT_SYMLINK_NOFOLLOW` and optional `AT_EMPTY_PATH`.
- `access_file()`, `open_file()`, `read_file()`, `write_file()`, `lseek_file()`, `fsync_file()`, and `replace_file()` wrap host file operations and return negative errno.
- Directory wrappers use `opendir()`, `seekdir()`, `readdir()`, and `closedir()`.
- Creation/mutation wrappers cover `open64(O_CREAT)`, chmod/chown/truncate, symlink, unlink, mkdir, rmdir, mknod, hardlink, readlink, rename, and renameat2.
- `do_statfs()` wraps `statfs64()` and copies statfs fields to caller-provided outputs.

Dependencies and integration:
- Consumed by `hostfs_kern.c`; exported via `hostfs_user_exp.c`.
- Uses libc/syscall interfaces from the UML host process environment.

Risk notes:
- Most wrappers return raw negative host errno, so kernel-side callers depend on host errno semantics.
- `rename2_file()` supports `renameat2` only when syscall numbers are known or present; otherwise it returns `-EINVAL`.
- `set_attr()` does not set ctime directly and uses microsecond `utimes`/`futimes` precision for atime/mtime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_user_exp.c -->
# File Research: sources/os/linux/linux/fs/hostfs/hostfs_user_exp.c

Purpose: Exports hostfs user-wrapper functions as GPL symbols for UML hostfs linkage.

Key content:
- `EXPORT_SYMBOL_GPL()` entries for hostfs stat, access, file I/O, directory I/O, create/remove/link/rename, setattr, readlink, mknod, and statfs wrappers.

Dependencies and integration:
- Includes `hostfs.h` and Linux module export support.
- Complements `hostfs_user.c` and the UML Makefile’s split build model.

Risk notes:
- Symbol export list must stay synchronized with declarations in `hostfs.h` and uses in `hostfs_kern.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hostfs/hostfs_user_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/hpfs/Kconfig

Purpose: Defines the Linux HPFS filesystem configuration option.

Key content:
- `config HPFS_FS` is a tristate option named “OS/2 HPFS file system support”.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD` and `FS_IOMAP`.
- Help text describes OS/2/Warp HPFS read/write support and module name `hpfs`.

Dependencies and integration:
- Enables compilation of the HPFS filesystem under `fs/hpfs`.

Risk notes:
- HPFS is block-device-only and buffer-head/iomap dependent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/Makefile -->
# File Research: sources/os/linux/linux/fs/hpfs/Makefile

Purpose: Builds the HPFS filesystem module/object.

Key content:
- Adds `hpfs.o` under `obj-$(CONFIG_HPFS_FS)`.
- Links HPFS from allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and super objects.

Dependencies and integration:
- `super.o` is part of the final object but outside this work item.

Risk notes:
- Object list shows HPFS is tightly coupled; most modules share structures and prototypes through `hpfs_fn.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/alloc.c -->
# File Research: sources/os/linux/linux/fs/hpfs/alloc.c

Purpose: Implements HPFS sector and dnode allocation/freeing, bitmap accounting, allocation checks, and filesystem trim/discard.

Key functions:
- `hpfs_claim_alloc()`, `hpfs_claim_free()`, `hpfs_claim_dirband_alloc()`, and `hpfs_claim_dirband_free()` maintain cached free counts, invalidating them on underflow/overflow.
- `hpfs_chk_sectors()` validates sector ranges and, in strict check mode, verifies allocation bitmap state.
- `alloc_in_bmp()` searches and updates a 4-sector bitmap for 1-sector or 4-sector allocations near a target.
- `hpfs_alloc_sector()` implements HPFS allocation strategy: near target, current bitmap, surrounding bitmaps, then reduced forward preallocation.
- `alloc_in_dirband()` allocates dnodes from the dedicated directory band bitmap.
- `hpfs_alloc_if_possible()` opportunistically claims a specific free sector.
- `hpfs_free_sectors()` frees sector runs and updates main bitmap/free count.
- `hpfs_check_free_dnodes()` verifies enough free dnodes are available before directory tree mutations.
- `hpfs_free_dnode()`, `hpfs_alloc_dnode()`, `hpfs_alloc_fnode()`, and `hpfs_alloc_anode()` manage initialized on-disk structures.
- `hpfs_trim_fs()` scans free bitmap runs and issues block discard requests, including directory-band free dnodes.

Dependencies and integration:
- Uses bitmap mapping helpers from `map.c`/`buffer.c`, HPFS superblock counters, dnode band metadata, and global HPFS locking for trim.
- Supplies allocation primitives to dnode, anode, EA, file, and namespace creation code.

Risk notes:
- HPFS bitmaps use inverted semantics: 1 means free, 0 means allocated.
- Directory dnodes are 4-sector aligned and may come from a separate directory band.
- Several paths assume `n` is only 1 or 4 sectors.
- Trim loops can be interrupted by pending fatal signals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/anode.c -->
# File Research: sources/os/linux/linux/fs/hpfs/anode.c

Purpose: Manages HPFS allocation B+ trees stored in fnodes and anodes, including lookup, growth, removal, EA data I/O, and truncation.

Key functions:
- `hpfs_bplus_lookup()` descends internal anodes and finds the disk sector for a file sector, updating the inode’s small extent cache.
- `hpfs_add_sector_to_btree()` appends a sector to an allocation tree, extends the last extent when possible, allocates sectors otherwise, and creates/splits anodes as needed.
- `hpfs_remove_btree()` iteratively frees all extents and anodes without recursion.
- `hpfs_ea_read()` and `hpfs_ea_write()` read/write EA byte ranges through direct sectors or anode-backed allocation trees.
- `hpfs_ea_remove()` frees direct or anode-backed EA storage.
- `hpfs_truncate_btree()` frees sectors beyond a target file-sector count and trims tree metadata.
- `hpfs_remove_fnode()` removes file/directory data trees, indirect EAs, external EA lists, and finally the fnode sector.

Dependencies and integration:
- Uses `hpfs_map_fnode()`, `hpfs_map_anode()`, sector allocation/freeing, and dnode tree removal.
- Core to file writes/truncates, EA storage, and inode eviction.

Risk notes:
- Tree manipulation is complex and assumes append-style growth for files.
- Cycle detection is conditional on check mode.
- Truncation intentionally does not rebalance/join anodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/anode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/buffer.c -->
# File Research: sources/os/linux/linux/fs/hpfs/buffer.c

Purpose: Provides HPFS buffer mapping helpers for single sectors and 4-sector structures, including hotfix remapping and readahead.

Key functions:
- `hpfs_search_hotfix_map()` maps bad original sectors to spare replacement sectors.
- `hpfs_search_hotfix_map_for_range()` shortens contiguous ranges at hotfix boundaries.
- `hpfs_prefetch_sectors()` issues readahead when sectors are valid and not hotfixed.
- `hpfs_map_sector()` reads a sector buffer after hotfix translation.
- `hpfs_get_sector()` obtains a sector buffer for writing without reading existing data.
- `hpfs_map_4sectors()` maps a 4-sector block, allocating a contiguous 2048-byte bounce buffer if buffer_head data is not contiguous.
- `hpfs_get_4sectors()` obtains a 4-sector writable block without reading.
- `hpfs_brelse4()` releases 4-sector mappings and frees bounce buffers.
- `hpfs_mark_4buffers_dirty()` copies bounce-buffer data back and marks all four buffers dirty.

Dependencies and integration:
- All HPFS on-disk structure access flows through these helpers.
- Requires the global HPFS mutex, asserted in mapping paths.

Risk notes:
- Dnodes and bitmaps are 4-sector structures; unaligned 4-sector mapping is rejected.
- Bounce-buffer handling is essential when buffer_head memory is not physically adjacent in kernel virtual memory.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dentry.c -->
# File Research: sources/os/linux/linux/fs/hpfs/dentry.c

Purpose: Implements HPFS dcache hashing and comparison using HPFS filename normalization and case folding.

Key functions:
- `hpfs_hash_dentry()` trims OS/2-style trailing dots/spaces except for `.`/`..`, uppercases through HPFS codepage rules, and computes the dentry hash.
- `hpfs_compare_dentry()` validates the candidate name, adjusts existing-name length, and compares case-insensitively with HPFS ordering rules.

Dependencies and integration:
- Uses name helpers from `name.c` and codepage table stored in `hpfs_sb_info`.
- Exports `hpfs_dentry_operations`.

Risk notes:
- Dcache behavior intentionally mirrors HPFS name equivalence, including trailing-dot/space trimming.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dir.c -->
# File Research: sources/os/linux/linux/fs/hpfs/dir.c

Purpose: Provides HPFS directory VFS operations for readdir, lookup, directory seek, and file operation tables.

Key functions:
- `hpfs_dir_release()` removes tracked readdir position pointers.
- `hpfs_dir_lseek()` validates HPFS synthetic directory positions by walking dnodes.
- `hpfs_readdir()` emits `.`, `..`, then walks HPFS dnode tree entries using encoded positions, translating case as needed.
- `hpfs_lookup()` validates names, finds dirents in the dnode tree, instantiates or fills inodes, handles directory/file distinction, reads EAs when needed, and rejects unsupported HPFS386 ACL/XPERM structures.
- `hpfs_dir_ops` wires directory llseek/read/iterate/release/fsync/ioctl operations.

Dependencies and integration:
- Uses dnode traversal from `dnode.c`, inode initialization from `inode.c`, name validation/translation from `name.c`, and global HPFS locking.
- Directory positions encode dnode sector plus entry index.

Risk notes:
- Readdir depends on tracked position pointers so directory mutations can adjust active iterators.
- Strict check mode performs additional fnode/dnode consistency validation and cycle detection.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dnode.c -->
# File Research: sources/os/linux/linux/fs/hpfs/dnode.c

Purpose: Implements HPFS directory dnode tree manipulation: lookup, insertion with splitting, deletion with balancing, position tracking, counting, and tree removal.

Key functions:
- `hpfs_add_pos()`, `hpfs_del_pos()`, and helper callbacks track active readdir offsets and update them during mutations.
- `hpfs_add_de()` inserts a dirent into a dnode in sorted order without splitting.
- `hpfs_add_to_dnode()` inserts into a dnode tree, splitting full dnodes, creating new root dnodes, and fixing child parent pointers.
- `hpfs_add_dirent()` descends the directory tree and inserts a new dirent, checking free dnode headroom first.
- `move_to_top()` and `delete_empty_dnode()` rebalance after deletion.
- `hpfs_remove_dirent()` removes a dirent and repairs/downshifts the dnode tree.
- `hpfs_count_dnodes()` counts dnodes, subdirectories, and items for inode metadata and emptiness checks.
- `hpfs_de_as_down_as_possible()` finds the leftmost reachable dnode for readdir start.
- `map_pos_dirent()` maps an encoded directory position to a dirent and advances to the next position.
- `map_dirent()` searches by name through the dnode tree.
- `hpfs_remove_dtree()` frees an empty directory tree.
- `map_fnode_dirent()` locates the directory entry for a given fnode, using the fnode’s truncated name as a search hint.

Dependencies and integration:
- Central to directory creation/removal/rename, readdir, lookup, inode writeback, and directory size/link counts.
- Uses allocation helpers, dnode mapping, name comparison, and global cycle checks.

Risk notes:
- This is the most structurally complex HPFS code; dnode splits/merges must preserve parent pointers, sentinel entries, sorted order, and active iterator positions.
- Several errors are reported as filesystem corruption because partial directory tree mutation can leave on-disk structures inconsistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/dnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/ea.c -->
# File Research: sources/os/linux/linux/fs/hpfs/ea.c

Purpose: Handles HPFS extended attributes stored inline in fnodes, externally in sector runs, or indirectly through anode-backed storage.

Key functions:
- `hpfs_ea_ext_remove()` walks and removes external EA lists, including indirect EA values, then frees direct sectors or anode trees.
- `get_indirect_ea()` and `set_indirect_ea()` read/write indirect EA payloads.
- `hpfs_read_ea()` copies a named EA into a caller buffer from inline, external, or indirect storage.
- `hpfs_get_ea()` allocates and returns a named EA value.
- `hpfs_set_ea()` updates an existing fixed-size EA or creates a new EA, preferring fnode-resident storage, then external sectors; it can relocate external EA runs when contiguous growth fails.

Dependencies and integration:
- Used by inode read/write paths for UID, GID, MODE, DEV, and SYMLINK EAs.
- Relies on anode EA read/write/remove helpers and sector allocation.

Risk notes:
- EA resizing is limited: existing EAs are updated only when the size matches.
- Some anode creation for EA list growth is commented out; relocation to a new contiguous run is used instead.
- EA corruption checks focus on list bounds and indirect-value metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/file.c -->
# File Research: sources/os/linux/linux/fs/hpfs/file.c

Purpose: Implements HPFS regular-file VFS and address-space operations, including block mapping, page-cache I/O, writeback, truncate, fiemap, and fsync.

Key functions:
- `hpfs_file_release()` writes dirty inode metadata on close.
- `hpfs_file_fsync()` writes file ranges and syncs the block device.
- `hpfs_bmap()` maps file-sector numbers through the fnode/anode B+ tree and inode extent cache.
- `hpfs_truncate()` truncates the allocation tree and writes inode metadata.
- `hpfs_get_block()` maps or allocates blocks for buffer-head based I/O.
- `hpfs_iomap_begin()` provides read-only iomap mapping for fiemap.
- `hpfs_read_folio()`, `hpfs_readahead()`, and `hpfs_writepages()` delegate to mpage helpers.
- `hpfs_write_begin()` and `hpfs_write_end()` handle contiguous writes and mark inode metadata dirty.
- `hpfs_fiemap()` exposes extents through iomap.
- `hpfs_aops`, `hpfs_file_ops`, and `hpfs_file_iops` wire VFS integration.

Dependencies and integration:
- Uses `anode.c` B+ tree helpers, hotfix range handling, HPFS global lock, and Linux mpage/iomap helpers.

Risk notes:
- Block allocation only permits append at `mmu_private`; unexpected non-append create mappings trigger `BUG()`.
- HPFS setattr rejects file extension through truncate; growth occurs through writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/hpfs.h -->
# File Research: sources/os/linux/linux/fs/hpfs/hpfs.h

Purpose: Defines HPFS on-disk structures, constants, bitfields, and helper predicates.

Key content:
- Sector-number typedefs for fnodes, dnodes, and anodes.
- Boot block, super block, spare block, bad block, hotfix, and codepage structures.
- Bitmap layout documentation for 8 MiB bands and the directory band.
- `struct dnode` and `struct hpfs_dirent` for directory B-tree nodes and entries.
- B+ tree structures for file allocation: leaf extents and internal anode pointers.
- `struct fnode` for file/directory allocation roots and EA metadata.
- `struct anode` for allocation subtrees.
- `struct extended_attribute` and EA flag helpers.

Dependencies and integration:
- Included by `hpfs_fn.h`, which is then used throughout HPFS.
- Encodes little-endian on-disk layout and bitfields conditional on CPU endian.

Risk notes:
- Comments state parts of HPFS are inferred/guesswork; defensive validation elsewhere is important.
- On-disk bitfields and packed flexible layouts are sensitive to compiler layout and endian behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/hpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/hpfs_fn.h -->
# File Research: sources/os/linux/linux/fs/hpfs/hpfs_fn.h

Purpose: Provides HPFS internal types, constants, inline helpers, prototypes, and locking helpers.

Key content:
- Allocation tuning constants, readahead constants, and error aliases.
- `struct hpfs_inode_info` extends VFS inode with HPFS directory/file caches, EA flags, dirty flag, and active readdir positions.
- `struct hpfs_sb_info` stores global HPFS mount state, options, codepage table, bitmap directory, hotfix map, and global mutex.
- `struct quad_buffer_head` represents four sector buffers plus optional contiguous/bounce data.
- Inline helpers navigate dnodes, dirents, fnodes, EAs, and B+ headers.
- Prototypes for all HPFS source files.
- Time conversion helpers between HPFS local time and Unix GMT.
- `hpfs_lock()`, `hpfs_unlock()`, and `hpfs_lock_assert()` define the filesystem-wide lock discipline.

Dependencies and integration:
- Included by every HPFS implementation file.
- Centralizes cross-file contracts for allocation, mapping, dnode, EA, file, inode, name, and superblock operations.

Risk notes:
- HPFS uses a single global filesystem mutex for VFS methods, simplifying correctness at the cost of concurrency.
- Inline dirent/EA pointer arithmetic assumes validated on-disk bounds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/hpfs_fn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/inode.c -->
# File Research: sources/os/linux/linux/fs/hpfs/inode.c

Purpose: Implements HPFS inode initialization, read, writeback, setattr, dirty write-on-close support, and eviction cleanup.

Key functions:
- `hpfs_init_inode()` initializes VFS inode defaults from mount options and clears HPFS-private caches/flags.
- `hpfs_read_inode()` maps an fnode, reads UID/GID/MODE/DEV/SYMLINK EAs when enabled, configures special files/symlinks/directories/regular files, and computes size/block/link metadata.
- `hpfs_write_inode_ea()` writes UID/GID/MODE/DEV EAs when mount options allow writable EAs.
- `hpfs_write_inode()` finds the parent inode and delegates writeback unless root/unlinked.
- `hpfs_write_inode_nolock()` updates fnode and matching dirent metadata, including size, timestamps, read-only bit, and EA size.
- `hpfs_setattr()` validates UID/GID range, prevents extension by truncate, applies size changes, copies attributes, and writes inode metadata.
- `hpfs_write_if_changed()` writes dirty inodes.
- `hpfs_evict_inode()` truncates page cache and removes the fnode for unlinked inodes.

Dependencies and integration:
- Uses fnode/dnode mapping, EA helpers, directory-entry lookup by fnode, file truncation, and global HPFS locking.

Risk notes:
- Root inode writeback is skipped.
- Inode metadata is mirrored between fnodes and dirents, requiring successful parent/dirent lookup.
- UID/GID EAs are limited to 16-bit values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/map.c -->
# File Research: sources/os/linux/linux/fs/hpfs/map.c

Purpose: Maps HPFS on-disk metadata structures into memory and performs optional consistency checks.

Key functions:
- `hpfs_map_dnode_bitmap()` maps the directory-band bitmap.
- `hpfs_map_bitmap()` maps a main bitmap block through the bitmap directory and prefetches the next bitmap.
- `hpfs_prefetch_bitmap()` issues bitmap readahead.
- `hpfs_load_code_page()` loads the first HPFS codepage and builds upper/lowercase tables.
- `hpfs_load_bitmap_directory()` loads the bitmap directory into memory.
- `hpfs_load_hotfix_map()` loads sector remapping pairs from the spare block hotfix map.
- `hpfs_map_fnode()` maps and validates an fnode, including magic, B+ tree counters, and EA bounds.
- `hpfs_map_anode()` maps and validates an anode.
- `hpfs_map_dnode()` maps and validates a 4-sector dnode, including magic, self pointer, dirent sizes, sentinel entry, and down pointers.
- `hpfs_fnode_dno()` returns a directory fnode’s root dnode sector.

Dependencies and integration:
- Uses buffer mapping helpers and HPFS superblock state.
- Provides validation gates for allocation, directory, inode, and file code.

Risk notes:
- Validation depth depends on mount check level.
- Dnode validation prevents malformed dirent sizes from causing infinite loops or out-of-bounds traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/name.c -->
# File Research: sources/os/linux/linux/fs/hpfs/name.c

Purpose: Implements HPFS filename validation, case conversion, comparison, long-name detection, and OS/2 trailing character normalization.

Key functions:
- `hpfs_chk_name()` rejects names longer than 254 bytes, empty names after adjustment, `.`/`..`, and forbidden characters.
- `hpfs_translate_name()` optionally lowercases names for presentation using the mounted codepage table.
- `hpfs_compare_names()` compares names case-insensitively with HPFS ordering and sentinel handling.
- `hpfs_is_name_long()` applies DOS 8.3-style heuristics to set the HPFS long-name flag.
- `hpfs_adjust_length()` trims trailing dots and spaces except for `.` and `..`.

Dependencies and integration:
- Used by dcache operations, lookup, readdir, dnode insertion/search, and namespace mutation.

Risk notes:
- Name equivalence includes case folding and trailing-dot/space trimming, so VFS behavior must stay aligned with dentry hashing/comparison.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/namei.c -->
# File Research: sources/os/linux/linux/fs/hpfs/namei.c

Purpose: Implements HPFS namespace mutation operations: create, mkdir, mknod, symlink, unlink, rmdir, symlink read, and rename.

Key functions:
- `hpfs_update_directory_times()` updates directory mtime/ctime and writes metadata.
- `hpfs_mkdir()` allocates an fnode and root dnode, creates the `^A^A` self entry, inserts a directory dirent, initializes the inode, and updates parent link count/times.
- `hpfs_create()` allocates an fnode and regular-file dirent, initializes file inode/page-cache ops, and writes ownership/mode EAs if needed.
- `hpfs_mknod()` creates special files only when writable EAs are enabled, storing mode/device metadata through inode writeback.
- `hpfs_symlink()` creates symlinks only when writable EAs are enabled, storing target text in the `SYMLINK` EA.
- `hpfs_unlink()` removes non-directory dirents and drops the inode link.
- `hpfs_rmdir()` verifies a directory is empty by counting dnode items, removes its dirent, and clears link counts.
- `hpfs_symlink_read_folio()` reads symlink target data from the `SYMLINK` EA.
- `hpfs_rename()` supports `RENAME_NOREPLACE`, rejects directory overwrite, moves/replaces dirents, updates parent directory accounting, and updates the moved fnode’s parent/name fields.
- `hpfs_dir_iops` wires directory inode operations.

Dependencies and integration:
- Uses allocation, dnode insertion/removal, EA handling, inode writeback, symlink address-space ops, and global HPFS locking.

Risk notes:
- Special files and symlinks depend on EA write support (`sb_eas >= 2`).
- Rename over an existing directory is rejected even if empty.
- Namespace operations must carefully unwind allocated fnodes/dnodes on failure to avoid leaks or corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/namei.c -->