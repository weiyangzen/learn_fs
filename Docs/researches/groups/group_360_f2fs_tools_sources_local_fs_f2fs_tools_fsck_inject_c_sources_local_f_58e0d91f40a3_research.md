# Group Research: group_360_f2fs_tools_sources_local_fs_f2fs_tools_fsck_inject_c_sources_local_f_58e0d91f40a3

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/f2fs-tools`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/inject.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/inject.c

Purpose: implements `inject.f2fs`, a metadata fault-injection utility for F2FS images. It parses injection-specific CLI options and mutates selected on-disk structures: superblocks, checkpoint packs, NAT/SIT entries, summary blocks, node blocks, inode fields, and directory entries.

Key behavior:
- Defines `enum entry_pos` to distinguish metadata entries in current journals versus NAT/SIT pack 1 or pack 2.
- Provides debug printers for raw NAT, SIT, summary, node footer, and dentry structures.
- `inject_parse_options()` handles `--mb`, `--idx`, `--val`, `--str`, `--sb`, `--cp`, `--nat`, `--sit`, `--ssa`, `--node`, `--dent`, `--dots`, `--nid`, `--blk`, `--dry-run`, `-d`, `-V`, and help routing.
- `inject_sb()` reads one superblock copy, changes supported fields (`magic`, `s_stop_reason`, `s_errors`, `feature`, `devs.path`), then calls `update_superblock()`.
- `inject_cp()` can mutate the current or explicitly selected checkpoint pack. It supports core checkpoint fields, curseg arrays, allocation type, checksum, elapsed time, and fsync dnode `next_blkaddr`; it rewrites first and last checkpoint blocks via `write_raw_cp_blocks()`.
- NAT/SIT injection prefers journal entries when present; otherwise it calculates the selected current or alternate pack address and rewrites the corresponding block.
- `inject_ssa()` mutates summary footer fields or per-block summary entries and writes the segment summary block back.
- `inject_node()` mutates node footer fields, inode fields, or direct-node `addr[]`, then writes via `update_inode()` unless explicitly injecting `i_inode_checksum`.
- `inject_dentry()` locates a child entry in inline or regular directory data blocks, supports dot/dotdot selection, and changes bitmap, hash, inode, file type, or filename; filename updates recompute name length and hash.
- `do_inject()` dispatches the selected injection mode and, for host-managed zoned devices, wraps node/dentry injection with fsck initialization plus curseg/journal/SIT/checkpoint flushes.

Important dependencies:
- Uses `node.h` traversal helpers, `get_node_info()`, `get_sum_block()`, `lookup_nat_in_journal()`, `lookup_sit_in_journal()`, `write_sum_block()`, `update_inode()`, `update_block()`, `write_checkpoint()`, and many F2FS endian/accessor macros.
- Relies on global configuration `c`, including `c.private` carrying `struct inject_option`.

Risk notes:
- This file intentionally corrupts or mutates metadata. Bounds checks exist for many array indexes and block/nid ranges, but most I/O uses `ASSERT`, so malformed images can abort the tool.
- `inject_sb()` frees `opt->str`; other string-based injection paths do not, because the option struct is global/static for the process.
- NAT/SIT pack selection uses current version bitmaps when pack is `0`; explicit pack selection can deliberately target stale copies.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/inject.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/inject.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/inject.h

Purpose: declares the public interface and option carrier for `inject.f2fs`.

Key contents:
- Includes standard integer/limits headers plus `f2fs_fs.h` and `fsck.h`.
- Defines `struct inject_option`, which stores selected member name, array index, numeric/string replacement value, target nid/block, selected superblock/checkpoint/NAT/SIT pack, dot/dotdot mode, and boolean selectors for SSA, node, and dentry injection.
- Exposes `inject_usage()`, `inject_parse_options()`, and `do_inject()`.

Role in the group:
- `main.c` allocates a static `inject_option`, initializes sentinel values, passes it to `inject_parse_options()`, and stores it in `c.private`.
- `inject.c` consumes the struct to dispatch and perform mutations.

Risk notes:
- `idx` is unsigned but initialized with `-1` in `main.c`, relying on `UINT_MAX` as the sentinel for “auto index” in several injection paths.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/inject.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/main.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/main.c

Purpose: main entry point and option dispatcher for the fsck-family F2FS tools. One source supports multiple program names: `fsck.f2fs`, `dump.f2fs`, `defrag.f2fs`, `resize.f2fs`, `sload.f2fs`, `f2fslabel`, and optionally `inject.f2fs`.

Key behavior:
- Defines global `struct f2fs_fsck gfsck` and initializes the feature table.
- Provides usage functions for each supported tool mode.
- `f2fs_parse_options()` chooses behavior by `basename(argv[0])`, parses mode-specific flags, sets global configuration `c`, validates device arguments, applies Android default options, and stores per-mode private option structs.
- FSCK mode supports auto/preen/fix policies, cache settings, feature toggles, casefold enablement, quota limit preservation, sparse mode, kernel-version checks, and fault injection settings.
- Dump/defrag/resize/sload/label modes each parse their own option set and update `c`.
- Inject mode is enabled behind `WITH_INJECT`; it initializes `struct inject_option` sentinels and delegates parsing to `inject_parse_options()`.
- `do_fsck()` performs fsck initialization, checkpoint/current-segment checks, optional quota context initialization, orphan/root/tree scans, quota verification, `fsck_verify()`, and maps results to fsck exit codes.
- `do_dump()`, `do_defrag()`, `do_resize()`, `do_sload()`, and `do_label()` wrap mode-specific work.
- `main()` initializes configuration, checks mount state, opens devices, repeatedly mounts via `f2fs_do_mount()`, dispatches by `c.func`, unmounts, optionally reruns fsck after sload or after interactive repair confirmation, finalizes devices, and reports elapsed time.

Important dependencies:
- Calls the mount lifecycle in `mount.c`: `f2fs_do_mount()` and `f2fs_do_umount()`.
- Calls quota functions from `quotaio.h`/`mkquota.c` during fsck.
- Calls mode implementations in other fsck-family files (`fsck.c`, dump/defrag/resize/sload/label/inject code).

Risk notes:
- Program behavior depends heavily on executable name or Android underscore-to-dot rewriting.
- Mounted-device handling is mode-sensitive: dump can proceed differently; fsck on read-only mounted devices disables repair unless forced.
- Sload intentionally remounts by converting itself into an FSCK pass afterward to repair missing quota metadata.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/mkquota.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/mkquota.c

Purpose: builds and reconciles in-memory quota usage, then writes F2FS quota inode contents in VFS v1 quota format.

Key behavior:
- Uses dictionaries keyed by UID/GID/project ID to accumulate `struct dquot` usage records.
- `quota_write_inode()` creates a quota file handle for a quota type, writes all accumulated dquots through `commit_dquot()`, then closes the file and updates inode size.
- `quota_init_context()` allocates `quota_ctx`, initializes per-type dictionaries only for quota inodes present in the superblock, and tracks hard-linked inodes to avoid double counting.
- `quota_release_context()` frees quota dictionaries, linked-inode dictionary nodes, and context memory.
- `quota_data_add()`, `quota_data_sub()`, and `quota_data_inodes()` adjust current space and inode counts across all enabled quota dictionaries.
- `quota_add_inode_usage()` handles hard links and accounts inode block usage as `(i_blocks - 1) * F2FS_BLKSIZE` plus one inode count.
- `quota_compare_and_update()` opens an existing quota file, scans disk dquots, compares disk usage with measured usage, optionally preserves limits, and reports whether usage is inconsistent.
- `scan_dquots_callback()` marks seen entries, logs mismatches, copies limit fields when requested, and can copy usage from disk if enabled.

Important dependencies:
- Uses `dict_t` from `dict.h`.
- Uses generic quota IO from `quotaio.c`, V2 format operations from `quotaio_v2.c`, and qtree scanning from `quotaio_tree.c`.
- Called by fsck quota checks in `fsck.c` and by `do_fsck()` setup in `main.c`.

Risk notes:
- Fault injection for `FAULT_QUOTA` can force `quota_compare_and_update()` failure.
- Missing disk quota entries are treated as usage inconsistency.
- The code preserves limits only when requested, but always compares measured usage against on-disk usage.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/mkquota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/mount.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/mount.c

Purpose: implements the userspace “mount” lifecycle for fsck-family tools: superblock/checkpoint validation, metadata manager construction, NAT/SIT/summary loading and flushing, checkpoint writing, fsync recovery recording, and teardown.

Key behavior:
- Provides debug printers for ACLs, xattrs, inode/node data, extension lists, superblock fields, checkpoint fields, checkpoint state flags, superblock stop reasons, and recorded filesystem errors.
- Zoned-device helpers determine usable segments and zone capacity constraints.
- `f2fs_is_valid_blkaddr()` validates metadata/data block ranges by address type.
- `f2fs_ra_meta_pages()` performs metadata readahead for NAT/SIT/SSA/CP/POR.
- `update_superblock()` recomputes superblock CRC when enabled and writes selected superblock copies.
- `sanity_check_raw_super()` verifies magic, checksums, block/sector geometry, segment/section/zone counts, extension counts, cp payload, reserved inode numbers, zoned feature compatibility, and area boundaries.
- `validate_super_block()` reads a candidate superblock, runs sanity checks, captures kernel/mkfs versions, sets invalid-superblock flags, and reports stop/error state.
- `get_valid_checkpoint()` validates both checkpoint packs, compares checkpoint versions, selects the newest valid pack, copies payload blocks, and marks fsck needed if only one pack is valid.
- `sanity_check_ckpt()` validates and can repair selected checkpoint accounting/layout fields under fix-on policy.
- NAT manager setup loads version bitmap, initializes NID bitmaps early from journal and later from NAT, checks or writes NAT bits.
- Segment manager setup builds SIT info, current segment state, and summary blocks from compacted or normal summaries.
- `build_sit_entries()` reads current SIT blocks plus SIT journal entries into segment entries and counts free segments.
- `build_nat_area_bitmap()` builds fsck NAT bitmaps/cache from NAT packs and NAT journal entries.
- NAT/SIT helpers support journal lookup, flushing journals into packs, nullifying NAT entries, rewriting SIT area bitmaps, updating NAT/data block addresses, and retrieving summaries.
- Curseg allocation helpers find free blocks, move current segments, set section types, relocate curseg offsets, zero journals, and write curseg fields back into checkpoint.
- `write_checkpoint()` recomputes checkpoint counts, flags, checksum, summary blocks, optional NAT bits, and writes first/last checkpoint blocks with fsync ordering.
- `write_checkpoints()` mirrors the valid checkpoint before repairing checkpoint pack 1.
- Fsync recovery support scans warm-node chains, detects loops with Floyd’s algorithm, optionally fixes loops, records fsync inode/data blocks into checkpoint-valid maps, and triggers roll-forward state.
- `f2fs_do_mount()` orchestrates the full mount path: superblock selection, sector tuning, checkpoint loading, fsck/kernel gates, feature tuning, manager builds, fsync record, proceed checks, late manager/NID initialization, and NAT bits validation.
- `f2fs_do_umount()` frees node, segment, SIT, curseg, checkpoint, and superblock memory.
- Android sparse support zeros SIT/NAT/payload metadata regions after sload.

Important dependencies:
- Central dependency for nearly every file in this group: `node.c`, `inject.c`, quota checks, fsck verification, sload/defrag, and summary/NAT/SIT helpers all depend on this mount state.
- Uses global config `c` for mode, fix policy, features, sparse mode, zoned model, kernel checks, and cached geometry.

Risk notes:
- This is the highest-blast-radius file in the group. Many repair writes are guarded by `c.fix_on`, but many reads/writes abort through `ASSERT`.
- Checkpoint and NAT/SIT journal flushing changes persistent metadata and can cascade into checkpoint rewrites.
- Fsync node-chain loop detection returns `-ELOOP` as a nonfatal fsck continuation path unless repair is enabled.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/node.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/node.c

Purpose: provides F2FS node allocation, rebuilding, traversal, and update helpers used by fsck, sload, inject, and quota repair.

Key behavior:
- `f2fs_alloc_nid()` finds the first clear bit in `nm_i->nid_bitmap`, sets it, and returns the allocated NID.
- `f2fs_release_nid()` clears a previously allocated NID bit.
- `f2fs_rebuild_qf_inode()` creates a fresh quota inode node, initializes size/blocks/flags/footer version, reserves a hot node block, writes the inode, updates NAT, and adjusts fsck/NID bitmaps.
- `set_data_blkaddr()` updates the data address in inode or direct-node address arrays and marks inode/node dirty state in `dnode_of_data`.
- `new_node_block()` allocates a node page, fills footer fields, chooses hot/warm/cold node curseg based on dnode/directory/RO feature, reserves a block, updates NAT, and increments inode block count.
- `get_node_path()` maps a file page index into inode direct, direct node, indirect node, or double-indirect node path offsets and node offsets.
- `get_dnode_of_data()` walks or allocates node pages for a file offset, updating parent NIDs and writing parent nodes when allocating, then returns the target node, block address, and offset.
- `update_inode()` recomputes inode checksum when the feature is enabled, then delegates to `update_block()`.

Important dependencies:
- Uses node accessors from `node.h`, metadata updates from `mount.c`, and allocation helpers from segment code.
- `inject_dentry()` uses `get_dnode_of_data()` to find directory data blocks.

Risk notes:
- Allocation scans NIDs linearly from zero and asserts if none are free.
- `get_dnode_of_data()` reads a node even for zero NIDs in lookup modes; callers need valid file topology or sparse handling.
- New node allocation returns `0` on reserve failure, which callers convert to errors.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/node.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/node.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/node.h

Purpose: defines inline node/inode addressing helpers and traversal mode constants for F2FS fsck tooling.

Key contents:
- `IS_INODE()` identifies inode nodes by footer `nid == ino`.
- `ADDRS_PER_PAGE()` returns inode or node address capacity; for non-inode nodes it can read the owning inode to account for extra inode layout.
- `blkaddr_in_inode()`, `blkaddr_in_node()`, and `datablock_addr()` abstract address array access.
- `set_nid()` and `get_nid()` update inode child NID fields or indirect-node NID arrays.
- Defines dnode traversal modes: `ALLOC_NODE`, `LOOKUP_NODE`, `LOOKUP_NODE_RA`.
- `set_new_dnode()` initializes `struct dnode_of_data`.
- `inc_inode_blocks()` increments inode block count and marks inode dirty.
- `IS_DNODE()` distinguishes direct data nodes from indirect nodes based on node offset layout.
- Footer helpers return inode number, checkpoint version, next block address, fsync/dentry bits, and recoverability based on checkpoint CRC flags.
- `set_cold_node()` toggles the cold-node flag based on directory status.

Important dependencies:
- Included by `node.c`, `inject.c`, `quotaio.h`, and `mount.c`.
- Depends on `fsck.h` and F2FS layout macros.

Risk notes:
- Several helpers assume valid node pages and assert on allocation/read failure.
- `ADDRS_PER_PAGE()` can allocate and read an inode block when the caller does not provide one, so it is not a pure accessor.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/node.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio.c

Purpose: generic quota-file IO wrapper for F2FS quota operations.

Key behavior:
- Defines quota type string extensions for user/group/project.
- Exposes global quota-file size-check state: `cur_qtype`, `qf_last_blkofs`, `qf_szchk_type`, and `qf_maxsize`.
- `quota_type2name()` maps quota type enum to text.
- `update_grace_times()` starts or clears block/inode grace timers based on soft-limit violations.
- `quota_write_nomount()` writes to a quota inode via `f2fs_write()`, tracks logical file size, and reports short writes as `-EIO`.
- `quota_read_nomount()` reads from a quota inode via `f2fs_read()`.
- `quota_file_open()` initializes a `quota_handle`, selects VFS v1 ops (`quotafile_ops_2`), verifies format, runs format init, and stores allocated handles in the quota context.
- `quota_file_create()` initializes a new quota file handle and calls V2 `new_io`.
- `quota_file_close()` writes dirty info, calls format close hook if any, optionally updates inode filesize, and frees context-owned handles.
- `get_empty_dquot()` allocates and zeroes a quota record with `dq_id = -1`.

Important dependencies:
- Delegates format behavior to `quotaio_v2.c`.
- Uses F2FS inode read/write helpers and quota context from fsck state.

Risk notes:
- Read/write callback type is `unsigned int`, but write failure paths return negative errno values through it, relying on callers comparing against expected sizes.
- `quota_file_open()` assumes `fsck->qctx` is initialized if it needs to allocate/store handles.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio.h

Purpose: public interface and shared data model for quota IO and in-memory quota accounting.

Key contents:
- Defines quota types `USRQUOTA`, `GRPQUOTA`, `PRJQUOTA`, and bit masks.
- Defines quota size-check modes used while validating quota file sizes.
- Declares global quota size-check state arrays.
- Defines `quota_ctx`, which holds the F2FS superblock info, per-type quota dictionaries, open quota file handles, and linked-inode tracking.
- Defines quota format IDs, default grace periods, and `IOFL_INFODIRTY`.
- Defines `quota_file`, `quota_handle`, `util_dqinfo`, `util_dqblk`, `dquot`, and `quotafile_ops`.
- Declares quota file lifecycle APIs, dquot allocation, grace update, quota context lifecycle, accounting helpers, quota writing, and compare/update.
- Provides small allocation wrappers `quota_get_mem()`, `quota_get_memzero()`, and `quota_free_mem()`.

Important dependencies:
- Includes `dict.h`, F2FS headers, `node.h`, `fsck.h`, and `dqblk_v2.h`.
- Used by all quota implementation files and by fsck quota checks.

Risk notes:
- `quota_free_mem()` nulls the caller’s pointer by memcpy into an opaque pointer location; callers must pass the address of a pointer.
- The comment still references ext4 superblock fields in the ported header, but current usage is F2FS quota inode based.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_tree.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_tree.c

Purpose: implements the quota qtree allocator, lookup, insertion, deletion, and scanning logic used by VFS v1 quota files.

Key behavior:
- Uses `QT_BLKSIZE` quota tree blocks and `struct qt_disk_dqdbheader` for data blocks.
- `qtree_entry_unused()` checks whether a disk quota entry is all zeros.
- `qtree_dqstr_in_blk()` computes entries per quota data block.
- Maintains free block and free-entry lists via `get_free_dqblk()`, `put_free_dqblk()`, `remove_free_dqentry()`, and `insert_free_dqentry()`.
- `find_free_dqentry()` locates or allocates a data block slot, increments block entry count, and records the dquot disk offset.
- `do_insert_tree()` recursively inserts qid-indexed references into a four-level tree.
- `qtree_write_dquot()` inserts a missing dquot into the tree if needed, converts memory to disk format, and writes the entry.
- `qtree_delete_dquot()` removes the tree reference and frees the data slot/block when usage and limits are all zero.
- `qtree_read_dquot()` finds an entry by ID, reads it, and converts it to memory format; absent entries return an empty dquot for the requested ID.
- `qtree_scan_dquots()` traverses all referenced blocks, calls a callback for nonempty entries, and records used entry/data-block counts.

Important dependencies:
- Uses `quota_handle` read/write callbacks from `quotaio.c`.
- Uses format-specific conversion and ID matching operations supplied by `quotaio_v2.c`.

Risk notes:
- Tree corruption is mostly logged and propagated as errors, but some helper writes ignore partial failure once list state has been logically changed.
- `find_block_dqentry()` logs when a referenced ID is absent but still returns a computed offset at the end of the block scan.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_tree.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_tree.h

Purpose: defines shared structures and APIs for quota qtree storage.

Key contents:
- Defines in-memory quota ID type `qid_t`.
- Defines tree constants: `QT_TREEOFF`, `QT_TREEDEPTH`, `QT_BLKSIZE_BITS`, and `QT_BLKSIZE`.
- Defines `struct qt_disk_dqdbheader`, the on-disk header for quota data blocks, with a static size assertion of 16 bytes.
- Declares `struct qtree_fmt_operations`, the format-specific callbacks for memory/disk conversion and ID matching.
- Defines `struct qtree_mem_dqinfo`, holding quota file block count, free block list head, free-entry list head, entry size, and format operations.
- Declares qtree read/write/delete/scan utilities.

Important dependencies:
- Included by `dqblk_v2.h`, `quotaio_v2.c`, and `quotaio_tree.c`.
- Uses little-endian F2FS types from `f2fs_fs.h`.

Risk notes:
- The header comment says “vfsv0 quota format,” but this code is used by the VFS v1 implementation in this tree.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_v2.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_v2.c

Purpose: implements VFS v1 quota file format operations on top of the generic qtree layer.

Key behavior:
- Defines `quotafile_ops_2`, wiring check/init/new/write/read/commit/scan/report operations.
- Converts V2 revision 1 disk dquot blocks to/from `struct dquot`, including limits, current usage, grace timers, and ID.
- Uses a special all-zero entry with `dqb_itime = 1` marker for unused qtree entries when converting to disk.
- Converts disk quota info header fields into memory and back, including grace times, flags, qtree block count, free block, and free-entry heads.
- `v2_check_file()` reads the quota header, rejects wrong-endian magic, and verifies supported version.
- `v2_init_io()` initializes qtree entry size/ops, reads quota info, validates quota file size against discovered size-check state, repairs regular-file size mismatch by calling `f2fs_filesize_update()`, and checks qtree block/free-list bounds.
- `v2_new_io()` writes a new quota header and initializes default grace times and qtree metadata.
- `v2_write_info()` persists the in-memory quota info.
- `v2_commit_dquot()` deletes empty dquots or writes nonempty dquots through qtree.
- `v2_scan_dquots()` delegates to qtree scanning.
- `v2_report()` is intentionally unimplemented.

Important dependencies:
- Uses `quotaio.h`, `quotaio_v2.h`, `dqblk_v2.h`, and `quotaio_tree.h`.
- Relies on `f2fs_quota_size()` and `f2fs_filesize_update()` for F2FS quota inode sizing.

Risk notes:
- Size validation can mutate quota inode size during init when regular-file size metadata disagrees with observed block offsets.
- Format support is fixed to `QFMT_VFS_V1`/`V2_VERSION == 1`.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_v2.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_v2.h

Purpose: declares on-disk structures and constants for the VFS v1 quota file format used by `quotaio_v2.c`.

Key contents:
- Defines `V2_DQINFOOFF` as the offset immediately after `struct v2_disk_dqheader`.
- Defines supported `V2_VERSION` as `1`.
- Defines `struct v2_disk_dqheader` with magic and version, asserted to 8 bytes.
- Defines `V2_DQF_MASK` for valid on-disk quota flags.
- Defines `struct v2_disk_dqinfo` with block/inode grace times, flags, qtree block count, free block, and free-entry heads, asserted to 24 bytes.
- Defines `struct v2r1_disk_dqblk`, the 72-byte disk quota record with ID, inode limits/current count, block limits/current space, and grace timers.

Important dependencies:
- Includes `quotaio.h`, which in turn pulls in quota and F2FS shared types.
- Consumed by V2 quota conversion and initialization code.

Risk notes:
- The structure definitions are exact on-disk ABI and protected by static assertions; changes here would affect quota file compatibility.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/quotaio_v2.h -->