# Group Research: group_940_linux_stable_sources_os_linux_linux_stable_fs_befs_befs_h_sources_os_c647dc704c17

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/befs.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/befs.h

This is the central private BeFS header. It defines the in-memory BeFS superblock state, inode state, common error/result enum, debug API declarations, and key address conversion helpers used by the rest of `fs/befs`.

Key definitions:
- `BEFS_VERSION` identifies the driver as `0.9.3`.
- `befs_blocknr_t` is the host-side block number type.
- `struct befs_mount_options` stores mount-time UID/GID override flags, debug flag, and `iocharset`.
- `struct befs_sb_info` mirrors the BeFS superblock in host byte order and stores allocation group geometry, journal metadata, root/index inode addresses, mount options, and loaded NLS table.
- `struct befs_inode_info` embeds `struct inode` and stores BeFS-specific inode number, parent, attribute inode, flags/type, and either a datastream or short symlink body.
- `enum befs_err` is the internal status vocabulary shared by btree, datastream, inode, and mount validation code.

Important inline helpers:
- `BEFS_SB()` retrieves `super_block->s_fs_info`.
- `BEFS_I()` converts a VFS inode to `struct befs_inode_info`.
- `iaddr2blockno()` maps a BeFS allocation-group address to a linear block number.
- `blockno2iaddr()` performs the reverse mapping for one-block inode addresses.
- `befs_iaddrs_per_block()` computes how many disk inode-address records fit in one filesystem block.

Integration:
- Includes `befs_fs_types.h` for on-disk types, and includes `endian.h` at the end so endian helpers can depend on `BEFS_SB()`.
- Debug prototypes are implemented in `debug.c`.
- Address helpers are used heavily by `io.c`, `datastream.c`, `linuxvfs.c`, and inode validation.

Risk notes:
- The correctness of almost all disk addressing depends on `ag_shift` and `blocks_per_ag` having been validated by `super.c`.
- `iaddr2blockno()` assumes the allocation-group address has already been bounds-checked when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/befs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/befs_fs_types.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/befs_fs_types.h

This header defines BeFS on-disk and host-side filesystem structures. It is the schema layer for superblocks, inodes, datastreams, block runs, small attributes, and B+tree nodes.

Key constants:
- `BEFS_NAME_LEN` is 255.
- `BEFS_SYMLINK_LEN` is 144 for inline symlink storage.
- `BEFS_NUM_DIRECT_BLOCKS` is 12.
- `BEFS_DBLINDIR_BRUN_LEN` is 4, used by double-indirect datastream mapping.
- Superblock magic values: `BEFS_SUPER_MAGIC1`, `BEFS_SUPER_MAGIC2`, `BEFS_SUPER_MAGIC3`.
- Inode magic and flags include `BEFS_INODE_IN_USE`, `BEFS_LONG_SYMLINK`, and transaction/logging flags.
- `BEFS_BTREE_MAGIC` and `enum btree_types` define BeFS B+tree metadata.

Important types:
- `fs64`, `fs32`, and `fs16` are bitwise-tagged on-disk endian-sensitive integer types.
- `befs_disk_block_run` is the packed on-disk allocation-group/start/len tuple.
- `befs_block_run` is the host-side equivalent.
- `befs_super_block` is the packed on-disk superblock.
- `befs_disk_data_stream` and `befs_data_stream` describe direct, indirect, and double-indirect file mappings.
- `befs_inode` is the packed on-disk inode, containing metadata plus either datastream or inline symlink bytes.
- `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and `befs_host_btree_nodehead` define B+tree superblock/node headers.

Integration:
- `endian.h` converts these disk structures into host structures.
- `super.c` consumes `befs_super_block`.
- `inode.c` and `linuxvfs.c` consume `befs_inode`.
- `datastream.c` consumes datastream and block-run types.
- `btree.c` consumes B+tree types.

Risk notes:
- The file intentionally uses packed structures and bitwise endian types; incorrect direct access without conversion would create cross-endian bugs.
- The double-indirect constant has an inline comment questioning whether it means four filesystem blocks or 4 KiB, which is relevant for large block-size compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/befs_fs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/btree.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/btree.c

This file implements BeFS B+tree lookup and sequential directory enumeration. The implementation is built on `datastream.c`, so B+tree nodes are read by byte offset from a BeFS datastream rather than directly from raw blocks.

Main exported functions:
- `befs_btree_find()` looks up a string key and returns its stored value, normally an inode block number.
- `befs_btree_read()` returns the Nth key/value pair in sorted order for directory iteration.

Internal flow:
- `befs_bt_read_super()` reads the B+tree superblock from datastream offset 0, converts fields to host byte order, dumps debug info, and validates `BEFS_BTREE_MAGIC`.
- `befs_bt_read_node()` reads a node at a datastream byte offset, keeps the backing `buffer_head`, and converts the node header into `befs_host_btree_nodehead`.
- `befs_btree_find()` loads the tree superblock, reads the root, descends internal nodes through `befs_find_key()`, follows overflow when needed, then searches the final leaf.
- `befs_find_key()` performs binary search inside one node using packed key data, key length index, and value array.
- `befs_btree_read()` seeks to the first leaf with `befs_btree_seekleaf()`, follows right sibling links, and extracts the requested ordinal key.
- `befs_leafnode()` treats nodes with invalid overflow pointer as leaves.
- `befs_bt_keylen_index()`, `befs_bt_valarray()`, and `befs_bt_keydata()` compute packed node subarray locations.
- `befs_bt_get_key()` returns an indexed key pointer and length.
- `befs_compare_strings()` compares B+tree string keys.

Integration:
- Directory lookup in `linuxvfs.c` uses `befs_btree_find()`.
- Directory iteration in `linuxvfs.c` uses `befs_btree_read()`.
- Node reads depend on `befs_read_datastream()` and endian helpers.

Limitations:
- The implementation says it is currently only suitable for directory B+trees.
- Non-string and duplicate-key index support is not implemented; comparison functions for numeric/float key types are disabled under `#if 0`.

Risk notes:
- `befs_bt_get_key()` checks `index > all_key_count`; valid indexes should be `< all_key_count`, so index equal to count is not rejected before indexing the key length array.
- `befs_find_key()` assumes a node has at least one key before it asks for the last key; empty interior cases are mostly handled by seek logic, but malformed nodes may still stress this path.
- `befs_btree_read()` copies keys with `strscpy(keybuf, keystart, keylen + 1)` even though keys are length-delimited packed data; correctness depends on the on-disk key data being NUL-compatible for directory names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/btree.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/btree.h

This header exposes the BeFS B+tree API to the VFS layer.

Exports:
- `befs_btree_find()` for string-key lookup in a B+tree datastream.
- `befs_btree_read()` for ordinal traversal of B+tree keys and values.

Integration:
- `linuxvfs.c` includes this header for directory lookup and readdir.
- The API takes `struct super_block *` and `const befs_data_stream *`, keeping B+tree traversal independent from VFS inode layout.

Risk notes:
- The API is read-only and directory-oriented; it does not expose mutation or non-string key handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/datastream.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/datastream.c

This file maps BeFS logical file blocks and byte offsets to disk block runs, then reads data through buffer heads. It handles direct, indirect, and double-indirect datastream regions.

Exports:
- `BAD_IADDR` is the zero block-run sentinel.
- `befs_read_datastream()` returns a `buffer_head` containing data at a byte offset and optionally reports the byte offset within the buffer.
- `befs_fblock2brun()` maps a logical file block to a BeFS block run.
- `befs_read_lsymlink()` reads long symlink contents from a datastream into a caller buffer.
- `befs_count_blocks()` estimates VFS `i_blocks`, including inode and indirect metadata blocks.

Mapping logic:
- Direct region: `befs_find_brun_direct()` linearly searches the 12 direct block runs and adjusts returned `start/len` so the requested block is the first returned block.
- Indirect region: `befs_find_brun_indirect()` reads each block in the indirect run, scans disk block-run entries, endian-converts the matching run, and adjusts by offset.
- Double-indirect region: `befs_find_brun_dblindirect()` computes indexes into the double-indirect and indirect levels using `BEFS_DBLINDIR_BRUN_LEN`, reads only the needed metadata blocks, then adjusts the result by logical offset.

Integration:
- `linuxvfs.c` calls `befs_fblock2brun()` from `befs_get_block()`.
- `btree.c` calls `befs_read_datastream()` to read B+tree metadata and nodes.
- `linuxvfs.c` calls `befs_read_lsymlink()` for long symlink folios.
- `befs_count_blocks()` is used when populating VFS inode block counts.

Risk notes:
- The double-indirect code computes `indir_indx = dblindir_leftover / diblklen`; based on the surrounding comments and variables, this looks suspicious because the second-level index would normally divide by the per-indirect-entry data length, not the double-indirect span.
- Double-indirect bounds checks use `>` against lengths; if indexes are equal to length, that is also out of range.
- Indirect mapping trusts disk block-run arrays after minimal validation; corrupt metadata can drive bad run lengths or arithmetic.
- `befs_read_lsymlink()` copies `bh->b_data` whole-block chunks and relies on caller-provided length validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/datastream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/datastream.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/datastream.h

This header exposes BeFS datastream helpers.

Exports:
- `befs_read_datastream()`
- `befs_fblock2brun()`
- `befs_read_lsymlink()`
- `befs_count_blocks()`
- `BAD_IADDR`

Integration:
- Used by `linuxvfs.c` for file block mapping, long symlinks, and block accounting.
- Used by `btree.c` for B+tree reads.
- Depends on BeFS types from `befs.h`.

Risk notes:
- Callers own returned `buffer_head` lifetimes and must `brelse()` them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/datastream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/debug.c

This file implements BeFS logging and optional structured debug dumping.

Logging functions:
- `befs_error()` prints `pr_err()` with the superblock id.
- `befs_warning()` prints `pr_warn()` with the superblock id.
- `befs_debug()` emits `pr_debug()` only under `CONFIG_BEFS_DEBUG`.

Debug dump functions:
- `befs_dump_inode()` prints on-disk inode fields, direct block runs, indirect metadata, datastream size, or symlink bytes.
- `befs_dump_super_block()` prints the on-disk superblock after endian conversion.
- `befs_dump_index_entry()` prints B+tree superblock fields.
- `befs_dump_index_node()` prints B+tree node header fields.
- Unused `befs_dump_small_data()` and `befs_dump_run()` are disabled under `#if 0`.

Integration:
- Called from `super.c`, `linuxvfs.c`, `btree.c`, `datastream.c`, `inode.c`, and `io.c`.
- Uses endian helpers, so dumps are meaningful for both little- and big-endian BeFS volumes.

Risk notes:
- Debug-only symlink dumping prints raw inline symlink bytes as a C string, relying on sane disk contents.
- Production logging is intentionally minimal; detailed metadata visibility requires `CONFIG_BEFS_DEBUG`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/endian.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/endian.h

This header provides BeFS endian conversion helpers for scalar and composite on-disk types.

Scalar helpers:
- `fs64_to_cpu()` / `cpu_to_fs64()`
- `fs32_to_cpu()` / `cpu_to_fs32()`
- `fs16_to_cpu()` / `cpu_to_fs16()`

Composite helpers:
- `fsrun_to_cpu()` converts `befs_disk_block_run` to `befs_block_run`.
- `cpu_to_fsrun()` converts a host block run to disk endian format.
- `fsds_to_cpu()` converts a full on-disk datastream, including all direct runs and range limits.

Integration:
- Included at the end of `befs.h` because conversion depends on `BEFS_SB(sb)->byte_order`.
- Used throughout BeFS superblock, inode, datastream, btree, and debug code.

Risk notes:
- `BEFS_SB(sb)->byte_order` must be initialized before these helpers are used. `befs_load_sb()` sets it based on `fs_byte_order`.
- No fallback branch handles an invalid byte-order marker; callers rely on superblock validation and magic checks to reject unusable state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/inode.c

This file validates raw BeFS inodes before VFS inode population.

Export:
- `befs_check_inode()` returns `BEFS_OK` for usable inodes and `BEFS_BAD_INODE` for invalid ones.

Validation performed:
- Checks `magic1` against `BEFS_INODE_MAGIC1`.
- Converts and checks the inode’s self-reported disk address against the VFS block number being loaded.
- Verifies `BEFS_INODE_IN_USE` is set.

Integration:
- `linuxvfs.c` calls this from `befs_iget()` after reading the inode block.
- Uses `fs32_to_cpu()`, `fsrun_to_cpu()`, and `iaddr2blockno()`.

Risk notes:
- The validation is intentionally limited; it does not deeply validate mode, datastream ranges, parent address, or block-run bounds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/inode.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/inode.h

This small header declares the BeFS inode validation API.

Export:
- `befs_check_inode(struct super_block *sb, befs_inode *raw_inode, befs_blocknr_t inode)`

Integration:
- Included by `linuxvfs.c`.
- Implemented in `inode.c`.

Risk notes:
- The header has no include guard, but it only contains one prototype and is used narrowly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/io.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/io.c

This file provides the lowest BeFS disk-read helper.

Export:
- `befs_bread_iaddr()` converts a BeFS inode/block-run address to a linear block number and reads it with `sb_bread()`.

Flow:
- Logs the allocation group/start/len.
- Rejects allocation groups greater than `num_ags`.
- Converts through `iaddr2blockno()`.
- Calls `sb_bread()`.
- Returns `NULL` on invalid allocation group or read failure.

Integration:
- `datastream.c` uses it in `befs_read_datastream()` after logical-to-run mapping.
- Depends on `BEFS_SB()` geometry and address helpers.

Risk notes:
- The allocation-group check uses `>` rather than `>=`, so an allocation group equal to `num_ags` may pass even though groups are commonly zero-indexed.
- It does not validate `start`, `len`, or final block number against total block count.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/io.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/io.h

This header declares the BeFS block-address read helper.

Export:
- `befs_bread_iaddr(struct super_block *sb, befs_inode_addr iaddr)`

Integration:
- Implemented in `io.c`.
- Used by `datastream.c`.

Risk notes:
- The returned `buffer_head` must be released by callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/linuxvfs.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/linuxvfs.c

This is the BeFS Linux VFS integration layer. It registers the filesystem, mounts block devices read-only, creates VFS inodes from BeFS inodes, implements directory lookup/readdir through BeFS B+trees, supports symlinks, handles NLS filename conversion, and exposes NFS export operations.

Major VFS objects:
- `befs_sops`: inode allocation/free, `put_super`, `statfs`, `show_options`.
- `befs_dir_operations`: generic read dir, `befs_readdir`, llseek, lease handling.
- `befs_dir_inode_operations`: lookup.
- `befs_aops`: read folio and bmap for regular files.
- `befs_symlink_aops`: read folio for long symlinks.
- `befs_export_operations`: file-handle encode/decode and parent lookup.
- `befs_fs_type`: block-device filesystem registration.

Important flows:
- File reads use `befs_read_folio()` -> `block_read_full_folio()` -> `befs_get_block()`.
- `befs_get_block()` rejects writes, maps logical blocks through `befs_fblock2brun()`, and calls `map_bh()`.
- `befs_lookup()` converts requested names to UTF-8 when NLS is active, searches the directory B+tree, and loads the returned inode block with `befs_iget()`.
- `befs_readdir()` repeatedly calls `befs_btree_read()` by `ctx->pos`, converts UTF-8 to NLS if configured, and emits entries.
- `befs_iget()` reads an inode block, validates it, populates mode, uid/gid overrides, timestamps, block accounting, file operations, directory operations, or symlink operations.
- `befs_symlink_read_folio()` reads long symlinks from datastreams and NUL-terminates the loaded page.
- `befs_parse_param()` handles `uid`, `gid`, `iocharset`, and `debug`; reconfigure ignores parsed options.
- `befs_fill_super()` reads the superblock at PPC or x86 offset, validates it, forces read-only mode, sets block size and operations, creates the root dentry, and loads NLS.
- `befs_reconfigure()` only permits remount read-only.
- Module init creates the inode cache and registers the filesystem.

Integration:
- Calls lower-level BeFS modules: `btree.c`, `datastream.c`, `inode.c`, `super.c`, and `io.c`.
- Uses Linux `fs_context`, buffer heads, block mapping helpers, NLS APIs, exportfs helpers, and slab inode caches.

Risk notes:
- The filesystem has no write support; `befs_get_block(create=1)` returns `-EPERM`, and mount forces `SB_RDONLY`.
- `befs_get_parent()` passes `befs_ino->i_parent.start` to `befs_iget()` instead of converting the full allocation-group address with `iaddr2blockno()`, which is suspicious for nonzero allocation groups.
- `show_options()` prints `charset=...`, while parser accepts `iocharset`; this may be user-visible inconsistency.
- Filename conversion allocates per lookup/readdir item and can fail with `-EILSEQ`.
- Mount validation rejects dirty/journaled filesystems rather than replaying journals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/linuxvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/befs/super.c

This file loads and validates BeFS superblock metadata.

Exports:
- `befs_load_sb()` copies the packed on-disk superblock into `struct befs_sb_info` in host byte order.
- `befs_check_sb()` validates magic numbers, block size, shift consistency, allocation-group shift consistency, and clean journal state.

Load behavior:
- Determines byte order from `fs_byte_order`.
- Converts magic fields, block geometry, counts, inode size, allocation group fields, flags, journal fields, root directory, and indices addresses.
- Initializes `nls` to `NULL`.

Validation behavior:
- Requires all three magic values.
- Allows block sizes 1024, 2048, 4096, or 8192.
- Rejects block sizes larger than `PAGE_SIZE`.
- Requires `1 << block_shift == block_size`.
- Logs but does not reject mismatch between `ag_shift` and `blocks_per_ag`.
- Rejects dirty filesystems or nonempty journal ranges.

Integration:
- Called from `befs_fill_super()` in `linuxvfs.c`.
- Depends on endian helpers and BeFS superblock types.

Risk notes:
- If `fs_byte_order` is neither native LE nor BE marker, `byte_order` is not explicitly initialized here before conversions.
- Dirty/journaled volumes are rejected; no journal replay exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/super.h -->
# File Research: sources/os/linux/linux-stable/fs/befs/super.h

This header declares BeFS superblock load and validation helpers.

Exports:
- `befs_load_sb()`
- `befs_check_sb()`

Integration:
- Implemented in `super.c`.
- Used by `linuxvfs.c` during mount.

Risk notes:
- No include guard, but the header is tiny and narrowly included.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/bfs/Kconfig

This Kconfig entry defines `CONFIG_BFS_FS`.

Behavior:
- Adds tristate “BFS file system support”.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD`.
- Help text describes SCO UnixWare Boot File System, usually mounted at `/stand`, with read/write access from Linux.
- Documents that module builds are named `bfs`.
- Notes that a root filesystem cannot be built as a module.

Integration:
- Controls compilation of `fs/bfs/Makefile`.

Risk notes:
- The help text points users toward UnixWare slice support and BFS documentation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/bfs/Makefile

This Makefile builds the BFS filesystem module/object.

Build rules:
- `obj-$(CONFIG_BFS_FS) += bfs.o`
- `bfs-objs := inode.o file.o dir.o`

Integration:
- Controlled by `CONFIG_BFS_FS` from `Kconfig`.
- Links BFS superblock/inode, file, and directory operations into one `bfs` object.

Risk notes:
- No generated or optional components are present.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/bfs.h -->
# File Research: sources/os/linux/linux-stable/fs/bfs/bfs.h

This is the private BFS header for in-core structures and cross-file declarations.

Key definitions:
- Includes public on-disk definitions from `<linux/bfs_fs.h>`.
- `BFS_MAX_LASTI` is 513, with a detailed comment explaining the practical root-directory limit that prevents filling all theoretical 512 inodes.
- `struct bfs_sb_info` tracks total/free blocks, free inodes, last file end block, last inode number, inode bitmap, and a global `bfs_lock`.
- `struct bfs_inode_info` stores disk inode number, start/end blocks, metadata buffer tracking, and embedded VFS inode.

Helpers:
- `BFS_SB()` gets private superblock state.
- `BFS_I()` converts a VFS inode to BFS private inode state.
- `printf` macro prefixes BFS error logging.

Exports:
- `bfs_iget()`, `bfs_dump_imap()`
- file inode/file/address-space operations
- directory inode/file operations

Integration:
- Included by all BFS implementation files.
- Uses `mapping_metadata_bhs` for metadata fsync support.

Risk notes:
- BFS serialization is coarse-grained through one superblock mutex.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/bfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/bfs/dir.c

This file implements BFS directory file and inode operations: readdir, create, lookup, hard link, unlink, rename, adding entries, and finding entries.

Exports:
- `bfs_dir_operations`
- `bfs_dir_inops`

Important flows:
- `bfs_readdir()` validates `ctx->pos` alignment, reads directory blocks from `i_sblock`, emits nonzero directory entries, and advances by fixed `BFS_DIRENT_SIZE`.
- `bfs_fsync()` syncs metadata buffer tracking with `mmb_fsync()`.
- `bfs_create()` allocates a VFS inode, claims the first free inode bit under `bfs_lock`, initializes file operations and mapping ops, inserts into hash, marks dirty, and adds a directory entry.
- `bfs_lookup()` checks name length, searches directory entries under lock, and calls `bfs_iget()`.
- `bfs_link()` adds a directory entry, increments link count, updates ctime, and instantiates the new dentry.
- `bfs_unlink()` finds the directory entry, clears its inode number, marks metadata dirty, updates directory/inode times, and decrements link count.
- `bfs_rename()` supports only default rename and `RENAME_NOREPLACE`, rejects directories, adds/reuses the target entry, clears the old entry, updates timestamps/link counts, and marks old metadata dirty.
- `bfs_add_entry()` scans the existing directory block range for a free fixed-size entry.
- `bfs_find_entry()` scans fixed-size entries by name.

Integration:
- Uses `bfs_lock` to serialize directory mutation and lookup.
- Uses `mmb_mark_buffer_dirty()` so directory metadata buffers can participate in fsync.
- Uses fixed BFS directory-entry format from `<linux/bfs_fs.h>`.

Risk notes:
- Directories do not grow by allocating new blocks here; `bfs_add_entry()` returns `-ENOSPC` when existing directory blocks have no free entry.
- Rename does not mark the newly created target directory buffer dirty in the same visible way as old entry clearing when `bfs_add_entry()` succeeds internally; correctness relies on `bfs_add_entry()` doing its own dirty marking.
- Directory reads skip unreadable blocks by advancing to the next block instead of returning an error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/bfs/file.c

This file implements BFS regular file operations and block mapping/allocation.

Exports:
- `bfs_file_operations`
- `bfs_aops`
- Empty `bfs_file_inops` declaration/definition.

Main file operations:
- Generic llseek, read_iter, write_iter, mmap prepare, and splice read.

Block allocation:
- `bfs_get_block()` maps logical file blocks to physical BFS blocks.
- Reads map blocks if within `i_eblock`.
- Writes can extend in place if the file is already the last allocated file.
- Otherwise, the entire file is moved to the next free block range after `si_lf_eblk`.
- `bfs_move_block()` copies one block and dirties the destination.
- `bfs_move_blocks()` copies a contiguous file extent block-by-block.

Address-space operations:
- `bfs_writepages()` uses `mpage_writepages()`.
- `bfs_read_folio()` uses `block_read_full_folio()`.
- `bfs_write_begin()` uses `block_write_begin()` and truncates page cache on failure.
- `bfs_bmap()` uses `generic_block_bmap()`.

Integration:
- Uses the global BFS superblock lock for write allocation and movement.
- Updates free block counts and last-file end block.
- Called by BFS VFS file operations and page cache writeback.

Risk notes:
- The allocation strategy is simple and potentially expensive: extending a non-last file moves the entire file.
- A comment notes an assumption that nothing writes the inode back during block allocation while `inode->i_blocks` is being used for free block accounting.
- `bfs_move_block()` uses `bforget()` on the source buffer after copying, which intentionally invalidates the old block mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/bfs/inode.c

This file implements BFS mount, inode read/write/evict, statfs, inode cache, filesystem registration, and superblock scanning.

Exports:
- `bfs_iget()`
- `bfs_dump_imap()`

Inode flow:
- `bfs_iget()` validates inode number, reads the inode table block, reconstructs Linux mode from BFS `i_vtype` plus low permission bits, assigns directory or regular-file operations, populates block range, uid/gid, link count, size, block count, and timestamps.
- `find_inode()` locates an on-disk inode and returns the backing buffer.
- `bfs_write_inode()` writes VFS inode state back to disk, including type, mode, owner, nlink, timestamps, start/end blocks, and end offset, with optional synchronous buffer write.
- `bfs_evict_inode()` truncates pages, syncs/invalidates metadata buffers, clears on-disk inode for unlinked files, releases inode/block bitmap accounting, and adjusts `si_lf_eblk`.

Superblock flow:
- `bfs_fill_super()` allocates `bfs_sb_info`, sets BFS block size, reads and validates the superblock magic and start/end fields, computes `si_lasti`, initializes reserved inode bits, loads root inode, computes block/free counts, verifies the final block is readable, scans all inode table entries for corruption, builds the inode bitmap, subtracts used file blocks, and tracks the highest end block.
- `bfs_statfs()` reports block/inode availability.
- `bfs_put_super()` destroys the mutex and frees private state.

Registration:
- Defines slab cache allocation/free for `bfs_inode_info`.
- `bfs_fs_type` uses fs_context with `get_tree_bdev()`.
- Module init creates the cache and registers the filesystem.

Integration:
- Directory and file layers depend on `bfs_iget()` and private inode state.
- Uses fixed on-disk definitions from `<linux/bfs_fs.h>`.
- Uses `mapping_metadata_bhs` initialization for metadata fsync support.

Risk notes:
- Mount continues on unclean BFS filesystems after logging a warning.
- The corruption scan validates inode block ranges and offsets, but skipped unreadable inode-table blocks during scan can leave holes.
- The filesystem is writable but simple; consistency depends on the global mutex and synchronous metadata paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_elf.c -->
# File Research: sources/os/linux/linux-stable/fs/binfmt_elf.c

This file implements the standard ELF binary loader and ELF core dumper.

Loader registration:
- `elf_format` registers `load_elf_binary()` and, when enabled, `elf_core_dump()`.
- Registered at `core_initcall(init_elf_binfmt)`.

ELF exec setup:
- `load_elf_binary()` validates ELF magic/type/architecture, rejects FDPIC, loads program headers, handles `PT_INTERP`, reads interpreter headers, processes `PT_GNU_STACK`, architecture processor headers, GNU properties, and architecture final checks.
- Calls `begin_new_exec()`, sets personality, applies `READ_IMPLIES_EXEC`, snapshots ASLR state, calls `setup_new_exec()`, and maps the user stack with `setup_arg_pages()`.
- Maps `PT_LOAD` segments with `elf_load()`, handling ET_EXEC fixed mapping, ET_DYN PIE/randomized mapping, static PIE loader behavior, alignment, first-load total reservation, BSS zeroing, and overflow checks.
- Loads an interpreter through `load_elf_interp()` when `PT_INTERP` is present.
- Creates the initial stack and auxiliary vector through `create_elf_tables()`.
- Sets `mm` code/data/brk/stack fields, randomizes brk when configured, optionally maps page zero for SVr4 compatibility, applies `ELF_PLAT_INIT`, finalizes exec, and starts the thread.

Support functions:
- `padzero()` clears trailing bytes after file-backed segment data.
- `elf_map()` wraps `vm_mmap()` and unmaps holes after the first full-image reservation.
- `elf_load()` maps file bytes and creates anonymous BSS pages.
- `total_mapping_size()` and `maximum_alignment()` support safe ET_DYN layout.
- `load_elf_phdrs()` reads and validates program headers.
- `parse_elf_properties()` and `parse_elf_property()` read `PT_GNU_PROPERTY` notes and pass properties to architecture code.

Core dump:
- Builds ELF headers, note headers, process notes, per-thread register/regset notes, auxv, siginfo, and NT_FILE mapped-file notes.
- Supports extended program header numbering with `PN_XNUM`.
- Emits PT_LOAD program headers for VMA dumps and writes VMA contents with `dump_user_range()`.
- Supports architecture extra notes/data hooks.

Integration:
- Central to Linux `execve()` for normal ELF binaries.
- Uses mm, binfmt, security, randomization, coredump, regset, rseq, arch ELF hooks, file mapping, and user-copy APIs.

Risk notes:
- This is security-critical parsing and mapping code; it has extensive bounds checks for program-header size, segment overflow, interpreter paths, GNU property ordering, and task address limits.
- The loader carefully distinguishes ET_DYN with interpreter from static PIE to avoid loader/program collisions.
- Core dump NT_FILE generation dynamically resizes to handle long paths and obeys `core_file_note_size_limit`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_elf_fdpic.c -->
# File Research: sources/os/linux/linux-stable/fs/binfmt_elf_fdpic.c

This file implements the ELF-FDPIC binary loader and FDPIC core dumper. FDPIC supports position-independent executables with explicit load maps, commonly for embedded/no-MMU architectures.

Loader registration:
- `elf_fdpic_format` registers `load_elf_fdpic_binary()` and optional `elf_fdpic_core_dump()`.
- Registered at core init and unregistered on module exit.

Exec flow:
- `is_elf()` validates ELF magic, type, architecture, and mmap capability.
- `elf_fdpic_fetch_phdrs()` reads program headers, validates header size/count, and extracts GNU stack policy/stack size.
- `load_elf_fdpic_binary()` validates executable and optional interpreter, loads both program-header tables, derives const-displacement flags, chooses stack executability, calls `begin_new_exec()`, sets personality including `PER_LINUX_FDPIC`, sets up the mm layout, maps executable/interpreter with `elf_fdpic_map_file()`, creates stack/auxv/loadmap tables, applies `ELF_FDPIC_PLAT_INIT`, finalizes exec, and starts the thread at interpreter or executable entry.
- On MMU systems, layout is delegated to `elf_fdpic_arch_lay_out_mm()` and `setup_arg_pages()`.
- On no-MMU systems, it manually maps a stack area and sets `context.end_brk`.

Load mapping:
- `elf_fdpic_map_file()` allocates an `elf_fdpic_loadmap`, maps all `PT_LOAD` segments according to arrangement flags, determines entry address, program-header address, and dynamic section address, validates that the dynamic section ends in a NULL entry, and merges adjacent loadmap segments on MMU.
- `elf_fdpic_map_file_constdisp_on_uclinux()` handles no-MMU constant-displacement loads by allocating one contiguous anonymous block, reading code into it, and clearing BSS.
- `elf_fdpic_map_file_by_direct_mmap()` maps individual load segments, handles independent/honour-vaddr/constdisp/contiguous arrangements, clears leading/trailing bytes, maps anonymous excess on MMU, and updates `mm` code/data bounds.

Stack and auxv:
- `create_elf_fdpic_tables()` copies platform strings, writes executable/interpreter load maps to user stack, creates auxv entries including `AT_BASE`, `AT_ENTRY`, credentials, secureexec, execfn, optional hwcap values, then builds argc/argv/envp tables.

Core dump:
- Adds FDPIC loadmap addresses into `elf_prstatus_fdpic`.
- Emits PRSTATUS/PRFPREG, PRPSINFO, AUXV, PT_LOAD headers, extra core phdrs/data, VMA dumps, and extended numbering metadata.

Integration:
- Uses ELF-FDPIC arch hooks, normal binfmt/exec/mm APIs, coredump APIs, regsets, and no-MMU conditional paths.
- Complements `binfmt_elf.c`; standard ELF handles non-FDPIC on MMU, while this file handles FDPIC and selected no-MMU ET_DYN cases.

Risk notes:
- Mapping correctness depends heavily on arch-provided FDPIC flags and layout hooks.
- Dynamic-section validation catches malformed FDPIC dynamic arrays, but broader segment overlap/arrangement validation is distributed across mapping and arch logic.
- Core dump format carries FDPIC-specific load maps so debuggers can relocate symbols.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_elf_fdpic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_flat.c -->
# File Research: sources/os/linux/linux-stable/fs/binfmt_flat.c

This file implements the `bFLT` flat binary loader, mainly for embedded/no-MMU systems, with optional compressed flat support.

Loader registration:
- `flat_format` registers `load_flat_binary()`.
- Registered at core init.

Stack setup:
- `create_flat_tables()` builds argc, optional argv/envp pointers-on-stack, argv pointer array, envp pointer array, and records `mm->arg_*` and `mm->env_*`.

Compressed support:
- Under `CONFIG_BINFMT_ZFLAT`, `decompress_exec()` parses a gzip header, rejects unsupported flags, initializes zlib inflate, streams file contents through a small buffer, and writes decompressed bytes to the target.

Relocation:
- `calc_reloc()` converts flat-file relative offsets into loaded text/data addresses and kills the process with SIGSEGV on invalid relocation.
- `old_reloc()` supports legacy flat relocation format when `CONFIG_BINFMT_FLAT_OLD` is enabled.
- `skip_got_header()` skips RISC-V GOT PLT reserved header entries.
- Relocation handling supports GOTPIC relocations and relocation table entries, using arch hooks `flat_get_relocate_addr()`, `flat_get_addr_from_rp()`, and `flat_put_addr_at_rp()`.

Main load flow:
- `load_flat_file()` validates the `bFLT` header, version, flags, size sanity, zflat availability, and `RLIMIT_DATA`.
- Calls `begin_new_exec()`, sets `PER_LINUX_32BIT`, and `setup_new_exec()`.
- Computes extra memory for BSS/stack/relocs.
- Handles no-MMU ROM text plus RAM data mapping when possible.
- Otherwise maps/copies text and data together into RAM, supporting gzip whole-file or gzip-data modes.
- Sets `mm->start_code`, `end_code`, `start_data`, `end_data`, `start_brk`, and `brk`.
- Stores loaded module metadata in `lib_info`.
- Applies GOT and relocation-table fixups.
- Flushes user icache and clears BSS, brk slack, and stack area.

Top-level binary load:
- `load_flat_binary()` computes extra stack needs from argc/envp and argument pages, loads the flat file, updates shared-library data segment pointers when configured, sets binfmt, creates argument pages/tables for MMU or no-MMU, applies `FLAT_PLAT_INIT`, finalizes exec, and starts the thread at the flat entry point.

Integration:
- Uses Linux binfmt, mm/mmap, read_code, user-copy, zlib, arch flat hooks, and task register setup.
- Supports a limited `MAX_SHARED_LIBS` structure, currently one shared library slot in this configuration.

Risk notes:
- This parser is highly sensitive to header arithmetic; it rejects sizes with high bits set and enforces data+bss rlimit.
- `calc_reloc()` sends SIGSEGV on invalid relocation in addition to returning failure.
- Optional gzip paths use kernel buffers/vmalloc on MMU for simpler user copying.
- The no-MMU memory layout manually tracks brk/stack boundaries through `mm->context.end_brk`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_flat.c -->