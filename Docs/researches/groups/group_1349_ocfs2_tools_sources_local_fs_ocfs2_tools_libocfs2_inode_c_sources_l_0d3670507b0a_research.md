# Group Research: group_1349_ocfs2_tools_sources_local_fs_ocfs2_tools_libocfs2_inode_c_sources_l_0d3670507b0a

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ocfs2-tools`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/inode.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/inode.c

Implements core OCFS2 userspace inode I/O and endian conversion.

Key behavior:
- `ocfs2_check_directory()` validates an inode block number, reads the inode, and checks `S_ISDIR(i_mode)`.
- `ocfs2_read_inode()` reads one filesystem block, checks `OCFS2_INODE_SIGNATURE`, validates metadata ECC via `ocfs2_validate_meta_ecc()`, copies the block to the caller, and swaps it to CPU endian.
- `ocfs2_write_inode()` requires `OCFS2_FLAG_RW`, swaps a caller-provided CPU-endian inode to disk endian, recomputes metadata ECC, writes the block, and marks the fs changed.
- `ocfs2_write_inode_without_meta_ecc()` is the same write path without recomputing ECC, explicitly for corruption-injection use by fswreck.

Endian handling:
- The swap path is staged because `ocfs2_dinode` contains unions whose active interpretation depends on flags and mode.
- `ocfs2_swap_inode_first()` swaps common inode fields.
- `ocfs2_swap_inode_second()` swaps device, bitmap, journal, superblock, local alloc, chain, dealloc, inline-data, or indexed-directory union members.
- `ocfs2_swap_inode_third()` swaps chain records or truncate-log records after header counts are in CPU order.
- `has_extents()` excludes super/local-alloc/chain/dealloc inodes, fast symlinks, and inline-data inodes from extent-list swapping.
- Inline directory data is swapped through directory-entry swap helpers, clamped by `ocfs2_max_inline_data_with_xattr()` so corrupt xattr sizes do not overrun the inline area.

Dependencies and interactions:
- Uses block allocation wrappers from `memory.c`.
- Uses metadata ECC helpers, extent-list swap helpers, xattr swap helpers, directory-entry swap helpers, and low-level `ocfs2_read_blocks()` / `io_write_block()`.
- The file is foundational: higher-level path lookup, quota, journal, refcount, and open-super paths all rely on its validated inode read/write semantics.

Important invariants:
- Valid block numbers are between `OCFS2_SUPER_BLOCK_BLKNO` and `fs->fs_blocks`.
- Caller-facing inode buffers are CPU-endian after read and expected CPU-endian before write.
- Signature validation happens before copying/swapping; ECC validation happens on the raw on-disk block before caller use.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/inode_scan.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/inode_scan.c

Implements full inode scanning across global and per-slot inode allocator files.

Main structure:
- `_ocfs2_inode_scan` tracks the filesystem, cached inode allocator inodes, current chain/group descriptor, buffered group blocks, block offsets, and state for discontiguous block groups.
- The scan includes one global inode allocator plus one inode allocator per slot: `s_max_slots + 1`.

Scan flow:
- `ocfs2_open_inode_scan()` allocates scan state, loads global inode alloc and each slot inode alloc through system-inode lookup, and allocates a 4 MiB group buffer sized in filesystem blocks.
- `ocfs2_get_next_inode()` returns the next raw inode block plus its block number. It does not validate the inode signature or swap the inode; callers do that after filtering.
- `ocfs2_close_inode_scan()` releases cached allocator inodes, group buffer, descriptor buffer, and scan state.
- `ocfs2_get_max_inode_count()` sums cluster counts of inode allocator files and converts to blocks.

Allocator traversal:
- `get_next_inode_alloc()` advances to the next non-empty inode allocator.
- `get_next_chain()` selects the next chain record from the inode allocator chain list.
- `get_next_group()` reads the current group descriptor, validates `bg_blkno`, skips the descriptor block, and initializes group bitmap offsets.
- `get_next_read_blocks()` supports both contiguous and discontiguous group descriptors. For discontiguous groups it walks extent records and adjusts `cur_blkno` when moving to a new record.
- `fill_group_buffer()` orchestrates transitions between chains, groups, and buffered reads.

Error and corruption handling:
- Uses `abort()` for internal state violations that should be impossible if callers obey the iterator contract.
- Returns `OCFS2_ET_CORRUPT_GROUP_DESC` or `OCFS2_ET_CORRUPT_CHAIN` for on-disk inconsistency.
- End-of-scan is indicated by `*blkno = 0` with success.

Dependencies and interactions:
- Used by quota usage computation and debug scanning paths.
- Depends on system inode lookup, cached inode reads, group descriptor reads, block reads, and cluster/block conversion.
- Includes support for discontiguous block groups, matching the feature documented in `ocfs2.7.in`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/inode_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/ismounted.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/ismounted.c

Checks whether a device or file is mounted, swap-backed, root-mounted, read-only, or busy.

Main APIs:
- `ocfs2_check_mount_point(device, mount_flags, mtpt, mtlen)` fills OCFS2 mount flags and optional mountpoint text.
- `ocfs2_check_if_mounted(file, mount_flags)` is a wrapper without mountpoint output.

Mount detection:
- With `mntent`, `check_mntent_file()` scans `/proc/mounts` on Linux, then the system mtab path. It compares both path strings and stat-derived device identities.
- It validates mtab entries by statting mount directories and checking mounted device identity to avoid stale entries.
- It has special handling for root filesystem detection, including a write probe to `/.ismount-test-file` to detect read-only root when mtab may be unreliable.
- With `getmntinfo`, a BSD-style fallback compares device names under `_PATH_DEV`.

Swap and busy detection:
- `is_swap_device()` scans `/proc/swaps`, comparing path and block-device `st_rdev`.
- Linux block devices are opened with `O_RDONLY | O_EXCL`; `EBUSY` adds `OCFS2_MF_BUSY`.

Flags produced:
- `OCFS2_MF_MOUNTED`
- `OCFS2_MF_ISROOT`
- `OCFS2_MF_READONLY`
- `OCFS2_MF_SWAP`
- `OCFS2_MF_BUSY`

Notable implementation details:
- Derived from e2fsprogs mount checking and modified for OCFS2.
- Some paths use `strncpy(mtpt, ..., mtlen)` without explicitly forcing NUL termination if the mountpoint is longer than the buffer.
- If `mtpt` is NULL, callers must still ensure paths that write mountpoint text are not reached with a NULL buffer in swap handling; current `ocfs2_check_if_mounted()` passes NULL and `is_swap_device()` path calls `strncpy(mtpt, "<swap>", mtlen)`, which is a latent NULL dereference if used on a swap device with that wrapper.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/ismounted.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/kernel-rbtree.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/kernel-rbtree.c

Provides a userspace copy of the Linux kernel red-black tree implementation.

Exported operations:
- `rb_insert_color()` rebalances and recolors after caller-linked insertion.
- `rb_erase()` removes a node and fixes tree coloring.
- `rb_first()` / `rb_last()` return minimum/maximum nodes.
- `rb_next()` / `rb_prev()` return in-order successor/predecessor.
- `rb_replace_node()` swaps a victim node with a replacement while preserving surrounding links and color.

Internal mechanics:
- `__rb_rotate_left()` and `__rb_rotate_right()` implement tree rotations.
- `__rb_erase_color()` handles delete fixup for black-height preservation.

Design notes:
- This file intentionally does not implement key comparison or insertion search; callers own embedding `struct rb_node` and deciding ordering.
- It is imported kernel infrastructure used where libocfs2 needs sorted in-memory structures.
- The implementation assumes valid rbtree state and non-null sibling nodes in delete fixup, matching kernel-style caller expectations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/kernel-rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/link.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/link.c

Creates directory entries in OCFS2 directories.

Main API:
- `ocfs2_link(fs, dir, name, ino, flags)` inserts `name -> ino` into directory inode `dir`. Low three bits of `flags` are used as directory entry file type.

Insertion logic:
- Uses `ocfs2_dir_iterate()` with `OCFS2_DIRENT_FLAG_INCLUDE_EMPTY`.
- `link_proc()` first tries to absorb a following unused directory entry into the current entry.
- If current entry is used and has slack, it shrinks it to minimum size and creates an unused entry in the remaining space.
- If current entry is unused and large enough, it writes inode, name length, name bytes, and file type.
- If no space exists, `ocfs2_expand_dir()` grows the directory, rereads the directory inode, and retries.

Directory trailer support:
- `blockend` is set to either the full block size or `ocfs2_dir_trailer_blk_off(fs)` when directory trailers are present, preventing writes over trailer metadata.

Indexed directory support:
- After insertion into the directory block, if the filesystem supports indexed directories and the directory has `OCFS2_INDEXED_DIR_FL`, it inserts the name into the dx directory index using `ocfs2_dx_dir_insert_entry()`.

Important checks:
- Requires writable filesystem.
- Validates target inode block number against superblock minimum and filesystem block count.
- Does not itself update target inode link count; this is only the directory-entry insertion helper.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/link.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/lockid.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/lockid.c

Encodes, decodes, and prints OCFS2 lock resource names.

Lock type mapping:
- `ocfs2_get_lock_type()` maps single-character lock prefixes to enum types: metadata, data, super, rename, rw, dentry, open, and flock.
- Unknown prefixes return `OCFS2_NUM_LOCK_TYPES`.

Encoding:
- `ocfs2_encode_lockres()` writes standard lock names as type char, pad, 16 hex block number, and 8 hex generation.
- Dentry locks are special: they include printable parent inode text followed by the target inode encoded in binary big-endian form, matching filesystem lock naming.

Decoding:
- `ocfs2_decode_lockres()` parses standard locks with `sscanf()`.
- For dentry locks, it parses the parent from text and tries to parse the inode payload from the binary-position substring using `strtoull(..., 16)`. This is asymmetric with the binary `memcpy()` encoding and appears fragile for arbitrary binary bytes.

Printing:
- `ocfs2_printable_lockres()` converts dentry binary inode payload back to a printable suffix using `bswap_64()` and truncates to 32-bit in formatting; non-dentry locks are copied as strings.

Context:
- Supports tools/debug output for lock names used by the cluster DLM and filesystem lock debugging documented in `ocfs2.7.in`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/lockid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/lookup.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/lookup.c

Implements name lookup inside a single OCFS2 directory.

Main API:
- `ocfs2_lookup(fs, dir, name, namelen, buf, inode)` returns the inode block number for `name` in directory `dir`.

Non-indexed path:
- Uses `ocfs2_dir_iterate()` and `lookup_proc()`.
- `lookup_proc()` compares `name_len & 0xFF` and name bytes, stores `dirent->inode`, marks found, and aborts iteration.

Indexed directory path:
- Reads the directory inode to check indexed-directory support.
- `ocfs2_find_entry_dx()` reads the dx root block from `di->i_dx_root`, hashes the name with `ocfs2_dx_dir_name_hash()`, searches via `ocfs2_dx_dir_search()`, and returns the found dx entry inode.
- Lookup result resources are released through `release_lookup_res()`.

Behavior:
- Returns `OCFS2_ET_FILE_NOT_FOUND` when no matching entry is found.
- Caller-provided `buf` can be passed to directory iteration as a block buffer; the function separately allocates its own inode buffer for checking directory features.

Debug utility:
- The `DEBUG_EXE` path can traverse a path component by component starting at root or a user-provided inode block.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/memory.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/memory.c

Provides libocfs2 memory allocation wrappers.

Generic allocation:
- `ocfs2_malloc(size, ptr)` allocates with `malloc()` and returns `OCFS2_ET_NO_MEMORY` on failure.
- `ocfs2_malloc0(size, ptr)` allocates and zeroes.
- `ocfs2_free(ptr)` frees `*ptr` and sets it to NULL.
- `ocfs2_realloc(size, ptr)` wraps `realloc()`.
- `ocfs2_realloc0(size, ptr, old_size)` reallocates and zeroes only the newly grown tail.

Block-aligned allocation:
- `ocfs2_malloc_blocks(channel, num_blocks, ptr)` allocates memory aligned to the IO channel block size using `posix_memalign()`.
- It checks multiplication overflow against `SIZE_MAX`.
- It probes with `malloc(bytes)` first because older glibc versions could abort inside `memalign()` on allocation failure.
- `ocfs2_malloc_block(channel, ptr)` allocates one block.

Role:
- Used throughout libocfs2 for disk block buffers that must satisfy direct/block IO alignment constraints.
- The API consistently accepts a pointer-to-pointer as `void *`, matching e2fsprogs-style allocation helpers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/mkjournal.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/mkjournal.c

Creates and formats OCFS2 journal files and JBD2 journal superblocks.

Journal feature helpers:
- `ocfs2_journal_tag_bytes()` selects 32-bit or 64-bit journal tag size based on `JBD2_FEATURE_INCOMPAT_64BIT`.
- `ocfs2_journal_tag_block()` reconstructs a journal tag block number, including high bits for 64-bit tags.
- `ocfs2_journal_set_features()` and `ocfs2_journal_clear_features()` validate feature masks before mutating the journal superblock.

Feature policy:
- Only JBD2 superblock V2 is supported.
- Unknown compat, ro-compat, or incompat bits are rejected.
- JBD2 checksum compat feature is explicitly rejected because OCFS2 wants journal replay rather than refusing replay after partial checkpointing; OCFS2 relies on metadata ECC for corruption detection.

Endian handling:
- `ocfs2_swap_journal_superblock()` swaps JBD2 big-endian superblock fields on little-endian hosts.

Superblock I/O:
- `ocfs2_init_journal_superblock()` initializes a journal superblock buffer, requires at least 1024 journal blocks, sets block size, first usable journal block, sequence, user count, and filesystem UUID.
- `ocfs2_read_journal_superblock()` checks magic in network order, swaps to CPU, and rejects unsupported features.
- `ocfs2_write_journal_superblock()` swaps to disk order, writes the block, and marks the filesystem changed.

Journal formatting:
- `ocfs2_make_journal()` validates that the target inode is a valid system journal file, grows or truncates it to the requested cluster count, updates size/mtime, and calls `ocfs2_format_journal()`.
- `ocfs2_format_journal()` zeroes the entire journal file in 1 MiB chunks with nocache IO, creates a journal superblock sized to allocated clusters, maps the first file block, and writes the journal superblock there.

Dependencies:
- Uses cached inode I/O, extent mapping, file writes, allocation extension, truncate, byte-order helpers, and low-level IO.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/mkjournal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/namei.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/namei.c

Implements pathname resolution over OCFS2 directory lookup primitives.

Main APIs:
- `ocfs2_namei(fs, root, cwd, name, inode)` resolves a pathname without following the final component if it is a symlink.
- `ocfs2_namei_follow(fs, root, cwd, name, inode)` resolves and follows the final symlink.
- `ocfs2_follow_link(fs, root, cwd, inode, res_inode)` follows a specific symlink inode.

Resolution model:
- `dir_namei()` walks all parent path components relative to `cwd` or `root` if the path begins with `/`.
- Each intermediate component is looked up with `ocfs2_lookup()` and passed through `follow_link()`.
- `open_namei()` resolves the containing directory and final basename, handles trailing slash as a special case, and optionally follows the final symlink.

Symlink handling:
- `follow_link()` reads the inode; if it is not a symlink, it returns the inode unchanged.
- Symlink loop depth is capped after five follows with `OCFS2_ET_SYMLINK_LOOP`.
- The implementation only handles symlinks backed by extents: it requires nonzero clusters and an extent-list record, reads the first target block, and resolves the target with `open_namei()`.
- Fast symlink handling is not present here, despite `inode.c` recognizing fast symlinks as non-extent inodes.

Dependencies:
- Uses `ocfs2_lookup()`, inode reads, extent-list fields, block reads, and block-buffer allocation.
- Ported from e2fsprogs namei logic with OCFS2 inode/block semantics.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/ocfs2.7.in -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/ocfs2.7.in

Manual page documenting OCFS2 filesystem semantics, features, tools, cluster stack behavior, operational notes, and debugging guidance.

Core positioning:
- OCFS2 is described as a POSIX-compliant shared-disk cluster filesystem for Linux with local-filesystem semantics across nodes.
- It promises cluster-wide cache coherency across buffered, direct, async, splice, and mmap IO.
- It uses journaling; surviving nodes replay journals of dead nodes.
- It is architecture and endian neutral, matching the byte-swap support in libocfs2 files.

Feature overview:
- Tunable block sizes: 512, 1K, 2K, 4K, with 4K generally recommended.
- Tunable cluster sizes: 4K through 1M.
- Multiple cluster stacks: `o2cb`, userspace stacks `pcmk`/`cman`, and no-stack local mount.
- Extent allocations, sparse files, unwritten extents, hole punching, inline data, reflink/refcount, allocation reservation, indexed directories, file attributes, xattrs, metadata checksums, ACL/security xattrs, quotas, clustered flock/fcntl, online resize, and tool support.

Compatibility model:
- Explains compat, incompat, and ro-compat feature flags.
- Lists feature bits and associated kernel/tool versions, including `indexed-dirs`, `metaecc`, `refcount`, `discontig-bg`, `usrquota`, and `grpquota`.
- Documents how unsupported incompat and ro-compat features surface in mount errors.

Operational guidance:
- Covers formatting and converting local mounts, O2CB local/global heartbeat, and userspace cluster stack updates.
- Lists major filesystem utilities: `mkfs.ocfs2`, `tunefs.ocfs2`, `fsck.ocfs2`, `mount.ocfs2`, `o2cluster`, `o2info`, `debugfs.ocfs2`, `o2image`, and `mounted.ocfs2`.
- Lists O2CB tools: `o2cb`, `ocfs2_hb_ctl`, and `o2hbmonitor`.

Filesystem notes:
- Explains delayed deletion through link count, cluster-wide open references, orphan directories, truncate logs, and sync.
- Explains why directory listing can be expensive in clustered filesystems due to inode stat locking.
- Describes allocation reservation behavior and reflink disk-usage reporting, including need for shared-extent-aware tools.
- Documents discontiguous block groups, backup superblock locations, synthetic filesystems (`configfs`, `dlmfs`, `debugfs`), DLM debugging workflow, NFS export limitations, filesystem size limits, system object layout, heartbeat/quorum/fencing, and kernel thread roles.

Relevance to code group:
- Documents features implemented or supported by adjacent files: endian neutrality (`inode.c`, `quota.c`, `refcount.c`), metadata ECC (`inode.c`, `quota.c`, `openfs.c`, `refcount.c`), indexed directories (`lookup.c`, `link.c`), quotas (`quota.c`), reflink/refcount (`refcount.c`), discontiguous block groups (`inode_scan.c`), lock debugging (`lockid.c`), journals (`mkjournal.c`), and backup superblocks/opening (`openfs.c`).
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/ocfs2.7.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/openfs.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/openfs.c

Opens OCFS2 filesystems, reads/writes superblocks, and abstracts metadata reads for image files.

Block read abstraction:
- `__ocfs2_read_blocks()` handles normal devices and `OCFS2_FLAG_IMAGE_FILE`.
- For image files, it verifies every requested metadata block exists in the image bitmap and maps real block numbers to image-relative block numbers.
- Public wrappers are `ocfs2_read_blocks()` and `ocfs2_read_blocks_nocache()`.

Superblock handling:
- `ocfs2_validate_ocfs1_header()` rejects old OCFS1 volumes unless the caller requested no revision check.
- `ocfs2_read_super()` reads a candidate superblock, checks `OCFS2_SUPER_BLOCK_SIGNATURE`, creates a temporary swapped superblock so metadata ECC can be validated with the correct block size/super context, then returns/stores a CPU-endian superblock.
- `ocfs2_write_primary_super()` writes the primary superblock through inode write semantics.
- `ocfs2_write_super()` writes primary then refreshes backups.
- `ocfs2_write_backup_super()` copies the primary superblock, changes `i_blkno`, sets backup-super compat feature, and writes to the requested backup block.

Open flow:
- `ocfs2_open()` allocates `ocfs2_filesys`, opens the IO channel, stores the device name, optionally loads an o2image bitmap, detects hard read-only devices, rejects OCFS1 if appropriate, discovers or uses supplied block size and superblock block, reads the superblock, and validates feature compatibility.
- If no block size is supplied, it probes from IO block size up to `OCFS2_MAX_BLOCKSIZE`.
- Strict compat checks also validate tunefs-in-progress flags.
- Rejects unsupported incompat features, rejects unsupported ro-compat features when opening RW, and can reject heartbeat devices unless explicitly allowed.
- Validates blocksize bits, inode block number matching the chosen superblock, cluster-size range, root/system directory block numbers, and slot count.
- Allocates cached inode allocator arrays and extent-block allocator arrays sized by `s_max_slots`.
- Initializes cluster/block counts, root/sysdir block numbers, first cluster group, and printable UUID.

Utility helpers:
- `ocfs2_mount_local()` tests local-mount incompat feature.
- `ocfs2_is_hard_readonly()` exposes hard read-only device status.

Important invariants:
- `fs->fs_super` is CPU-endian after open.
- `fs->fs_blocksize` must match the superblock `s_blocksize_bits`.
- Opening read-write is refused when unsupported ro-compat features are present.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/openfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/quota.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/quota.c

Implements userspace OCFS2 quota metadata handling, quota usage computation, cached dquot management, and global/local quota file initialization.

Endian and ECC:
- Swap helpers cover quota headers, local quota info, local chunk headers, global quota info, global dquot records, and quota tree leaf headers.
- `ocfs2_checksum_quota_block()` computes metadata ECC in the quota block trailer.
- `read_blk()` reads from the global quota file and validates trailer ECC.
- `write_blk()` recomputes trailer ECC and writes the full block.

Quota hash cache:
- `ocfs2_new_quota_hash()` creates an 8192-bucket hash.
- Buckets are power-of-two indexed by `id * 5`.
- `ocfs2_insert_quota_hash()` doubles buckets when used entries exceed allocated entries, capped at `1 << 21`.
- Find/create/read helpers cache `ocfs2_cached_dquot` records.
- `ocfs2_write_release_dquots()` iterates cached dquots, clears grace timers when usage is below soft limits, writes each dquot, removes it from the hash, and frees it.
- `ocfs2_free_quota_hash()` refuses to free non-empty hashes.

Usage computation:
- `ocfs2_compute_quota_usage()` scans every inode via `ocfs2_open_inode_scan()` and `ocfs2_get_next_inode()`.
- It filters by inode signature, generation, valid flag, and excludes system files except the root inode.
- It accumulates current space as allocated clusters converted to bytes and increments inode counts for UID and/or GID hashes.

Quota change workflow:
- `ocfs2_init_quota_change()` allocates user/group hashes only when corresponding ro-compat quota features are enabled.
- `ocfs2_apply_quota_change()` reads or creates affected UID/GID dquots and applies signed space/inode deltas.
- `ocfs2_finish_quota_change()` writes/releases hashes and frees them.

Local quota files:
- `ocfs2_init_local_quota_file()` validates the system quota inode, ensures at least two blocks, sets inode size/mtime, writes local quota header and info, initializes clean flags, checksums both initial blocks, and writes through file I/O.
- `ocfs2_init_local_quota_files()` initializes every per-slot local user/group quota file after truncating it.

Global quota info and files:
- `ocfs2_qtree_depth()` computes qtree depth from block size and 32-bit quota IDs.
- `ocfs2_qtree_index()` selects qtree child indexes by depth.
- `ocfs2_init_fs_quota_info()` locates and caches global user/group quota system inodes.
- `ocfs2_read_global_quota_info()` and `ocfs2_write_global_quota_info()` load/store global header and info.
- `ocfs2_load_fs_quota_info()` loads enabled user/group quota info.
- `ocfs2_init_global_quota_file()` initializes the global quota file with two blocks, header, info block, qtree root, inode size, and dirty flags.

Global quota qtree:
- Free block list is managed by `ocfs2_get_free_dqblk()` and `ocfs2_put_free_dqblk()`.
- Blocks with free dquot slots are managed by `ocfs2_insert_free_dqentry()` and `ocfs2_remove_free_dqentry()`.
- `ocfs2_find_free_dqentry()` chooses or creates a leaf block, increments entry count, locates an unused dquot slot, writes the leaf, and returns a byte offset.
- `ocfs2_do_insert_tree()` recursively creates qtree internal blocks and leaf dquot references.
- `ocfs2_write_dquot()` inserts into the qtree if needed, writes the dquot at its offset, clears padding, swaps to disk endian, and writes the block.
- `ocfs2_delete_dquot()` removes a dquot reference, cleans empty leaves, updates free lists, and releases empty internal qtree blocks where possible.
- `ocfs2_read_dquot()` allocates a cached dquot, descends the qtree, finds the leaf entry by ID, sets `d_off`, copies/swap the disk dquot, and returns it.

Notable considerations:
- `ocfs2_read_global_quota_info()` returns early on `read_blk()` failure without freeing its allocated buffer, a small leak on error.
- Global quota qtree code is careful about free-list corruption but comments acknowledge some write failures can leave difficult states.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/refcount.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/refcount.c

Implements OCFS2 refcount trees and copy-on-write handling for reflinked file and xattr data.

Core structures:
- `ocfs2_refcount_block` can be an inline root holding refcount records or a tree root holding an extent list of leaf refcount blocks.
- Leaf records are `ocfs2_refcount_rec` entries with physical cluster position, cluster length, and refcount.
- `ocfs2_cow_context` abstracts CoW over normal inode data and xattr value data, carrying an extent tree, refcount root buffer, target range, cluster lookup callback, and optional post-refcount callback.

Endian and block I/O:
- Swap helpers cover refcount lists, refcount records, refcount block headers, and either extent-list or record-list payload depending on `OCFS2_REFCOUNT_TREE_FL`.
- `ocfs2_read_refcount_block_nocheck()` validates block number, reads the block, validates metadata ECC, checks `OCFS2_REFCOUNT_BLOCK_SIGNATURE`, copies to caller buffer, and swaps to CPU endian.
- `ocfs2_read_refcount_block()` additionally validates list usage/count bounds.
- `ocfs2_write_refcount_block()` requires RW, swaps to disk endian, computes metadata ECC, writes the block, and marks the filesystem changed.

Record lookup and mutation:
- `ocfs2_get_refcount_rec()` returns the record containing a physical cluster position or a synthetic hole record with refcount 0.
- For tree roots, it finds the leaf extent using low 32 bits of the physical cpos, reads the refcount leaf, and searches its record list.
- Record contiguity helpers merge adjacent records with equal refcount.
- `ocfs2_change_refcount_rec()` increments/decrements a record, removes it if count reaches zero, optionally merges, and writes the leaf.
- `ocfs2_insert_refcount_rec()` inserts a new record, expanding the tree if the leaf is full.
- `ocfs2_split_refcount_rec()` splits an existing record around a subrange for partial increments, decrements, or hole punching.

Tree growth and shrinking:
- `ocfs2_expand_inline_ref_root()` converts an inline root into a tree root by allocating a new leaf block and moving existing records there.
- `ocfs2_divide_leaf_refcount_block()` sorts records by low 32-bit cpos, finds a split point that avoids overlapping low-cpos ranges, moves half to a new block, then restores 64-bit order.
- `ocfs2_new_leaf_refcount_block()` allocates and inserts a new leaf into the refcount extent tree.
- `ocfs2_expand_refcount_tree()` handles inline-root expansion and then leaf splitting.
- `ocfs2_adjust_refcount_rec()` updates the extent record cpos when a leaf’s first record changes.
- `ocfs2_remove_refcount_extent()` removes an empty leaf from the tree, deletes its block, decrements root cluster count, and restores inline-root style if no leaves remain.

Public refcount operations:
- `ocfs2_increase_refcount()` reads an inode’s refcount root and increments refcounts over a physical range.
- `ocfs2_decrease_refcount()` decrements records and optionally frees physical clusters when the old refcount was 1 and deletion is requested.
- `ocfs2_refcount_punch_hole()` removes all refcount records over a physical range, decrementing by their full current count.
- `ocfs2_change_refcount()` sets a range to a target refcount by computing a delta and applying the increase path.
- `ocfs2_refcount_tree_get_rec()` maps a physical cpos to the refcount tree extent record covering it.
- `ocfs2_create_refcount_tree()` creates a new refcount tree with random generation from `/dev/urandom`.
- `ocfs2_attach_refcount_tree()` increments tree `rf_count`, then sets inode `i_refcount_loc` and `OCFS2_HAS_REFCOUNT_FL`.
- `ocfs2_detach_refcount_tree()` decrements `rf_count`, deletes the tree if it reaches zero, then clears inode refcount fields.

CoW for file data:
- `ocfs2_refcount_cal_cow_clusters()` chooses the virtual cluster range to CoW, aligning splits to up to 1 MiB (`MAX_CONTIG_BYTES`) for better extent layout while not passing holes, unrefcounted extents, or `max_cpos`.
- `ocfs2_duplicate_clusters()` copies physical cluster contents block-by-block.
- `ocfs2_make_clusters_writable()` walks refcount records: if refcount is 1, it just clears the extent refcount flag; if greater than 1, it allocates replacement clusters, copies data unless unwritten, updates the file extent to the new clusters and clears `OCFS2_EXT_REFCOUNTED`, then decrements old refcounts.
- `ocfs2_refcount_cow()` iterates file extents in a write range and CoWs refcounted hunks before writing the cached inode.

CoW and flag changes for xattrs:
- `ocfs2_change_refcount_flag()` changes refcount flags on either inode data extents or xattr value extents, locating xattr extents by physical cluster.
- `ocfs2_refcount_cow_xattr()` performs the same CoW process for xattr value roots. If the xattr extent root lives in a bucket, it uses a post-refcount callback to write the whole bucket.

Important invariants:
- Most public operations assert the inode has `OCFS2_HAS_REFCOUNT_FL` and a valid `i_refcount_loc`.
- Refcount records are expected sorted by 64-bit `r_cpos` in leaves, while tree indexing uses low 32 bits.
- CoW requires the filesystem-level refcount feature; otherwise `ocfs2_replace_cow()` returns read-only filesystem error.
- Error paths often prioritize on-disk recoverability by writing old/new refcount blocks in ordered steps and relying on fsck to repair partially completed splits.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/refcount.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/refcount.h

Small internal header for refcount post-operation callbacks.

Definitions:
- `ocfs2_post_refcount_func` is a callback type taking `ocfs2_filesys *fs` and opaque `void *para`.
- `struct ocfs2_post_refcount` stores a callback and its parameter.

Purpose:
- Used by `refcount.c` during CoW/refcount operations when callers need extra work after the data b-tree is modified but before the larger operation is considered complete.
- The xattr bucket CoW path uses this to write an entire xattr bucket after refcount and extent updates succeed.

Scope:
- Header is intentionally minimal and private to libocfs2 refcount implementation details.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/refcount.h -->