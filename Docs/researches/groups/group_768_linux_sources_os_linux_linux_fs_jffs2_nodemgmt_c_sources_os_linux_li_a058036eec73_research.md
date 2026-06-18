# Group Research: group_768_linux_sources_os_linux_linux_fs_jffs2_nodemgmt_c_sources_os_linux_li_a058036eec73

Scope: `Docs/research_subset_a.md` only. All 13 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodemgmt.c -->
# File Research: sources/os/linux/linux/fs/jffs2/nodemgmt.c

## Role

Manages JFFS2 physical node allocation, active eraseblock selection, obsolete-node accounting, block-list transitions, and garbage-collection wakeup policy.

## Key Responsibilities

- Enforces reserved-pool write policy in `jffs2_rp_can_write()`, allowing normal writes only when available reclaimable/free space exceeds `rp_size`, with `CAP_SYS_RESOURCE` override.
- Implements normal/deletion reservations in `jffs2_reserve_space()`, including `alloc_sem` ownership, low-space checks, GC passes, erase-wait sleeps, signal interruption, and raw-node-ref preallocation.
- Implements GC reservations in `jffs2_reserve_space_gc()` without taking `alloc_sem`.
- Selects and retires `c->nextblock` through `jffs2_find_nextblock()` and `jffs2_close_nextblock()`.
- Handles summary-aware reservation through `jffs2_do_reserve_space()`, writing summary nodes before an eraseblock becomes too full.
- Converts unusable tail space into obsolete raw-node refs when summaries are disabled or inactive.
- Adds committed nodes through `jffs2_add_physical_node_ref()`, enforcing contiguous placement at the current append point.
- Marks nodes obsolete in `jffs2_mark_node_obsolete()`, updating used/unchecked/dirty/wasted accounting, refiling eraseblocks, optionally clearing the on-flash accurate bit, and detaching obsolete refs from inode or xattr ownership lists when safe.
- Determines whether the background GC thread should wake in `jffs2_thread_should_wake()`.

## Important Interactions

- Uses `erase_completion_lock` for eraseblock lists and accounting.
- Uses `alloc_sem` to serialize active allocations.
- Uses `erase_free_sem` when physical obsoletion is possible so erasure cannot free refs while the obsolete bit is being written.
- Calls GC, erase, summary, write-buffer, raw-node-ref, inode-cache, and xattr helpers.

## Invariants and Risks

- Non-obsolete writes must append at `nextblock`'s current free offset; mismatches are allocator corruption.
- Space counters are balanced at both filesystem and eraseblock granularity and checked with debug paranoia helpers.
- Physical obsoletion depends on flash/writebuffer/summary/read-only/building/scanning state.
- Low-space loops guard against endless GC by checking both dirty space and maximum possible available space.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodemgmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/os-linux.h -->
# File Research: sources/os/linux/linux/fs/jffs2/os-linux.h

## Role

Linux OS adaptation header for JFFS2 core code. It maps JFFS2 internal objects to Linux VFS objects and hides write-buffer configuration differences behind macros/prototypes.

## Key Responsibilities

- Defines conversions between `struct inode`/`struct super_block` and JFFS2 private structures.
- Exposes inode field macros for size, mode, uid, gid, rdev, and clamped 32-bit atime/mtime/ctime values.
- Provides `sleep_on_spinunlock()` for wait-queue sleep while dropping a spinlock.
- Initializes per-inode JFFS2 state in `jffs2_init_inode_info()`.
- Defines read-only and sector-address helpers.
- Provides direct-MTD no-op stubs when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Declares write-buffer, NAND, DataFlash, UBI, and NOR write-buffer helpers when write-buffer support is enabled.
- Declares Linux-facing operations implemented by background, dir, file, ioctl, fs, symlink, and writev code.

## Important Interactions

- Controls whether callers use direct `mtd_read`/`mtd_writev` or buffered wrappers from `wbuf.c`.
- Defines `jffs2_can_mark_obsolete()`, which is disabled when summary support is enabled and otherwise depends on flash bit-writability.
- Exposes `jffs2_flash_writev()` and `jffs2_flash_read()` as the common I/O interface used by scan, read, write, and summary paths.

## Invariants and Risks

- On-flash timestamps are clamped to `U32_MAX`.
- `SECTOR_ADDR(x)` depends on a visible local variable named `c`.
- Write-buffer-disabled builds intentionally stub NAND/OOB/bad-block behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/os-linux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/read.c -->
# File Research: sources/os/linux/linux/fs/jffs2/read.c

## Role

Implements reading data from JFFS2 raw inode nodes and logical inode ranges.

## Key Responsibilities

- `jffs2_read_dnode()` reads a raw inode header, validates header/node CRC, handles an old zero-compression hole-node size bug, reads node payload, validates data CRC, decompresses if needed, and copies requested subranges.
- Optimizes full uncompressed reads by reading directly into the caller buffer.
- Allocates compressed and decompressed scratch buffers only when partial reads or compression require them.
- Handles `JFFS2_COMPR_ZERO` by zero-filling the requested range.
- `jffs2_read_inode_range()` walks the inode fragment tree, zero-fills gaps and hole fragments, and dispatches real fragments to `jffs2_read_dnode()`.

## Important Interactions

- Consumes raw node refs and fragment trees built by `readinode.c`.
- Uses `jffs2_flash_read()` so pending write-buffer data can be visible to reads.
- Uses `jffs2_decompress()` with compression identifiers stored in raw inode nodes.

## Invariants and Risks

- Header or data CRC mismatch returns `-EIO`.
- On read error, `jffs2_read_inode_range()` zeroes the failed span before returning.
- Partial compressed reads must decompress the full logical dnode before copying the requested slice.
- A single physical node referenced by multiple fragments may be read more than once.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/readinode.c -->
# File Research: sources/os/linux/linux/fs/jffs2/readinode.c

## Role

Reconstructs an in-memory JFFS2 inode from all non-obsolete raw node refs associated with an inode number.

## Key Responsibilities

- Checks deferred data CRCs for unchecked data nodes in `check_node_data()`, using `mtd_point()` when possible and falling back to `jffs2_flash_read()`.
- Converts valid unchecked accounting into used accounting and marks bad unchecked nodes obsolete.
- Maintains a temporary rb-tree of data nodes in `jffs2_add_tn_to_tree()`, discarding older fully covered nodes, handling version collisions, and marking overlap groups.
- Builds the final non-overlapping fragment tree in `jffs2_build_inode_fragtree()` by replaying overlap groups in version order.
- Reads and validates dirent nodes in `read_direntry()`, including name CRC validation when needed.
- Reads and validates data nodes in `read_dnode()`, including deferred data-CRC strategy for write-buffered flash.
- Handles unknown compatible/incompatible node types in `read_unknown()`.
- Iterates all inode refs in `jffs2_get_inode_nodes()`, safely finding the next valid ref under `erase_completion_lock` before processing the current one unlocked.
- Finalizes inode state in `jffs2_do_read_inode_internal()`: chooses latest metadata, truncates regular files to latest `isize`, caches symlink targets, moves special-file data into `f->metadata`, and marks the inocache present.
- Provides public read, CRC-check, and clear paths through `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`.

## Important Interactions

- Depends on scan-time inode caches and raw-node-ref lists from `scan.c` or `summary.c`.
- Coordinates with inocache states: unchecked, checking, GC, reading, present, clearing, and checked-absent.
- Calls fragment-tree helpers, xattr CRC/delete helpers, inode-cache state helpers, and node-obsoletion helpers.

## Invariants and Risks

- Obsolete refs may disappear after erase, so traversal obtains the next valid ref while holding `erase_completion_lock`.
- Data CRC checking is intentionally deferred for write-buffered flash to avoid checking nodes later proven obsolete.
- Root inode 1 may be synthesized if absent on flash.
- Symlinks and special files are expected to have exactly one data fragment, which becomes metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/readinode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/scan.c -->
# File Research: sources/os/linux/linux/fs/jffs2/scan.c

## Role

Performs mount-time flash scanning, discovers JFFS2 nodes, builds initial inode caches/raw refs, and classifies eraseblocks for allocation and GC.

## Key Responsibilities

- `jffs2_scan_medium()` maps or buffers flash, scans every eraseblock, resets per-block summary collection, and files blocks into free, clean, dirty, very-dirty, erasable, erase-pending, or bad lists.
- Preserves the best partially dirty block as `c->nextblock` and moves previous candidates to dirty lists.
- Refuses to erase a filesystem with no valid JFFS2 nodes unless the block mix proves it is simply empty.
- `jffs2_scan_eraseblock()` checks NAND OOB cleanmarkers/bad-block state, attempts summary scan first, then falls back to full node-by-node scan.
- Full scan recognizes erased regions, cleanmarkers, padding, inode nodes, dirent nodes, xattr/xref nodes, obsolete nodes, endian/old/dirty magic, unknown compatible/incompatible nodes, and bad CRCs.
- `jffs2_scan_inode_node()` validates inode node CRC, creates/fetches inode cache, links unchecked raw refs, and records summary information.
- `jffs2_scan_dirent_node()` validates dirent and name CRCs, creates parent inode cache, links raw refs with dirent state, and stores scan dirents.
- Xattr scanning stages xattr datum/ref objects when enabled.
- `jffs2_rotate_lists()` pseudo-randomly rotates allocator/GC lists to spread wear.

## Important Interactions

- Calls summary scan/write collection helpers, raw-node-ref allocation/linking, dirty-space accounting, NAND cleanmarker helpers, xattr setup, and GC trigger logic.
- `jffs2_scan_classify_jeb()` returns block states consumed by `jffs2_scan_medium()` and allocator behavior in `nodemgmt.c`.

## Invariants and Risks

- Scanner helpers must advance offsets and update dirty/used/unchecked/free accounting consistently.
- Header CRC is trusted enough to determine `totlen`; later node/data/name CRC failures make space dirty rather than aborting mount.
- Read-only-compatible unknown nodes force read-only mounting; incompatible nodes abort.
- Summary fallback resets accounting and raw refs if summary content cannot be used safely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/security.c -->
# File Research: sources/os/linux/linux/fs/jffs2/security.c

## Role

Integrates JFFS2 with Linux security xattrs and LSM inode security initialization.

## Key Responsibilities

- `jffs2_initxattrs()` attaches initial LSM-provided security xattrs using `do_jffs2_setxattr()`.
- `jffs2_init_security()` calls `security_inode_init_security()` for newly created inodes.
- Provides `security.*` xattr get/set handlers backed by JFFS2 prefix `JFFS2_XPREFIX_SECURITY`.
- Defines `jffs2_security_xattr_handler`.

## Important Interactions

- Used during inode creation after the initial raw inode has been written and before final directory entry commit.
- Delegates storage and policy enforcement to the generic LSM API and JFFS2 xattr implementation.

## Invariants and Risks

- Initial label setup stops on the first failed xattr write.
- The set handler ignores idmap-specific transformation and delegates directly to JFFS2 xattr storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/summary.c -->
# File Research: sources/os/linux/linux/fs/jffs2/summary.c

## Role

Implements optional JFFS2 summary support: compact per-eraseblock metadata used to speed mount-time scanning.

## Key Responsibilities

- Initializes and frees `struct jffs2_summary` and its bounded write buffer in `jffs2_sum_init()` and `jffs2_sum_exit()`.
- Collects in-memory summary records for inode, dirent, xattr, xref, and padding nodes through `jffs2_sum_add_*_mem()` and `jffs2_sum_add_kvec()`.
- Supports disabling/resetting summary collection per eraseblock via `JFFS2_SUMMARY_NOSUM_SIZE`.
- Moves scan-collected summary state into the superblock summary for the selected `nextblock`.
- Processes on-flash summary records in `jffs2_sum_process_sum_data()`, creating inode caches, dirent objects, xattr staging objects, and raw refs.
- Validates summary header, node, and payload CRCs in `jffs2_sum_scan_sumnode()`.
- Writes summary nodes in `jffs2_sum_write_sumnode()` and `jffs2_sum_write_data()`, serializing descriptors, adding the trailing summary marker, padding to consume remaining block space, and linking a summary raw ref.

## Important Interactions

- Called from `scan.c` during mount and from `nodemgmt.c` before retiring a block.
- Fed by `writev.c` and `wbuf.c` for newly written nodes.
- Uses `sum_link_node_ref()` to account for gaps because summary records do not explicitly describe dirty space.

## Invariants and Risks

- Summary size is capped at `MAX_SUMMARY_SIZE` for allocation feasibility.
- Summary nodes are an optimization: CRC failures or unsupported compatible summary entries fall back to full scan.
- Unknown node types in write-time summary collection are programmer errors unless compatible-copy handling disables summary.
- Failed summary writes mark written bytes obsolete when possible and disable summary for the block.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/summary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/summary.h -->
# File Research: sources/os/linux/linux/fs/jffs2/summary.h

## Role

Defines JFFS2 summary constants, on-flash summary record formats, in-memory summary record formats, and enabled/disabled summary APIs.

## Key Responsibilities

- Defines block-state constants returned by scan paths: all-FF, clean, partially dirty, cleanmarker-only, all-dirty, and bad block.
- Defines summary size macros for inode, dirent, xattr, and xref records.
- Defines `MAX_SUMMARY_SIZE`, `JFFS2_SUMMARY_NOSUM_SIZE`, and `JFFS2_SUMMARY_FRAME_SIZE`.
- Declares packed on-flash summary record structures and matching in-memory linked-list structures.
- Defines `struct jffs2_summary` for collected size/count/padding/list state and summary write buffer.
- Defines `struct jffs2_sum_marker`, stored at the end of summarized eraseblocks.
- Provides real prototypes under `CONFIG_JFFS2_SUMMARY` and no-op stubs otherwise.

## Important Interactions

- Included by scanner, allocator, direct-write, and write-buffer paths.
- Conditional stubs let callers invoke summary helpers without duplicating preprocessor checks.

## Invariants and Risks

- On-flash structures are packed and use endian-tagged JFFS2 integer types.
- Summaries larger than `MAX_SUMMARY_SIZE` are discarded.
- Disabled builds make `jffs2_sum_active()` false and all summary operations benign.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/summary.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/super.c -->
# File Research: sources/os/linux/linux/fs/jffs2/super.c

## Role

Registers JFFS2 with Linux VFS/MTD mount infrastructure and manages superblock lifecycle, mount options, inode slab allocation, NFS export hooks, sync, and module init/exit.

## Key Responsibilities

- Creates/destroys the `jffs2_i` inode slab cache and initializes per-inode mutex/VFS fields.
- Allocates and frees VFS inodes, including cached symlink targets.
- Parses `compr=` and `rp_size=` mount options through fs_context.
- Displays active options through `jffs2_show_options()`.
- Updates remount options under `alloc_sem`, syncs before reconfigure, and delegates to `jffs2_do_remount_fs()`.
- Fills the superblock in `jffs2_fill_super()`: attaches MTD and OS private pointers, validates reserve-pool size, initializes locks/wait queues, installs super/export/xattr operations, sets `SB_NOATIME`, and enables POSIX ACLs when configured.
- Provides NFS export helpers based on inode-number file handles and parent lookup through directory `pino_nlink`.
- Flushes write buffers in sync and put-super paths.
- Tears down summary state, inode caches, raw refs, block arrays, flash resources, xattrs, and MTD state in `jffs2_put_super()`.
- Initializes compressors, JFFS2 slab caches, and filesystem registration in `init_jffs2_fs()`.

## Important Interactions

- Calls `jffs2_do_fill_super()` for core filesystem initialization after Linux mount setup.
- Uses compressor mode constants from `compr.h`.
- Coordinates write-buffer flushing with `wbuf.c`.
- Stops the GC thread before killing writable superblocks.

## Invariants and Risks

- On-medium structure sizes are asserted at module init.
- `rp_size` must not exceed MTD size.
- Delayed RCU inode frees are flushed before destroying the inode cache.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/symlink.c -->
# File Research: sources/os/linux/linux/fs/jffs2/symlink.c

## Role

Defines Linux inode operations for JFFS2 symbolic links.

## Key Responsibilities

- Exposes `jffs2_symlink_inode_operations`.
- Uses `simple_get_link` because symlink target text is cached in `inode->i_link`/JFFS2 inode state by inode read/setup code.
- Reuses `jffs2_setattr` for metadata changes.
- Reuses `jffs2_listxattr` for xattr listing.

## Important Interactions

- Symlink targets are read and cached by `readinode.c`.
- Attribute updates route through common JFFS2 setattr logic.
- Xattr listing routes through the shared xattr subsystem.

## Invariants and Risks

- This file contains only the operation table; correctness depends on inode setup and cached symlink target lifetime elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/wbuf.c -->
# File Research: sources/os/linux/linux/fs/jffs2/wbuf.c

## Role

Implements write-buffered flash I/O for NAND, DataFlash, UBI volumes, and write-buffered NOR. It handles page-aligned buffering, pending inode tracking, OOB cleanmarkers, bad-block handling, delayed flushes, and write-failure recovery.

## Key Responsibilities

- Tracks which inode writes are pending in the write buffer through `jffs2_wbuf_pending_for_ino()`, `jffs2_wbuf_dirties_inode()`, and `jffs2_clear_wbuf_ino_list()`.
- Refiles blocks whose erasure was delayed by dirty write-buffer contents via `jffs2_refile_wbuf_blocks()`.
- Moves failed or suspect blocks to bad/erase lists through `jffs2_block_refile()`.
- Recovers from write-buffer write failure in `jffs2_wbuf_recover()`, copying still-valid nodes to a new block and updating raw refs and in-core inode/xattr pointers.
- Flushes buffered pages in `__jffs2_flush_wbuf()`, optionally padding and accounting wasted space.
- Provides GC-triggered and pad-triggered flush entry points: `jffs2_flush_wbuf_gc()` and `jffs2_flush_wbuf_pad()`.
- Implements buffered vector writes in `jffs2_flash_writev()` and scalar writes in `jffs2_flash_write()`.
- Implements `jffs2_flash_read()` that overlays pending write-buffer bytes on top of MTD reads and tolerates ECC-corrected/raw-read cases for later CRC validation.
- Implements NAND OOB helpers: `jffs2_check_oob_empty()`, `jffs2_check_nand_cleanmarker()`, `jffs2_write_nand_cleanmarker()`, and `jffs2_write_nand_badblock()`.
- Schedules delayed write-buffer sync with `jffs2_dirty_trigger()`.
- Provides setup/cleanup for NAND, DataFlash, NOR write-buffered flash, and UBI volume modes.

## Important Interactions

- Serializes buffered reads/writes with `wbuf_sem`.
- Requires `alloc_sem` for flush paths that alter allocation/accounting.
- Uses `erase_completion_lock` for block-list and raw-ref changes.
- Calls allocator, GC, summary, raw-node-ref, xattr, and inode-fetch helpers.
- Summary collection is fed from `jffs2_flash_writev()` after successful writes.

## Invariants and Risks

- Buffered writes must be contiguous within an eraseblock or start a new block; non-contiguous writes trigger `BUG()`.
- Recovery updates both raw-node lists and in-core structures for present inodes.
- If recovery cannot reread partially written old data, earlier affected nodes may be lost and the code advances to recover later complete nodes.
- Pending-inode tracking intentionally degrades to “all dirty” on allocation failure.
- OOB cleanmarker behavior differs from inline cleanmarker behavior used on NOR/direct modes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/wbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/write.c -->
# File Research: sources/os/linux/linux/fs/jffs2/write.c

## Role

Implements core JFFS2 write-side node creation for inode data, metadata, directory entries, create, unlink, and link operations.

## Key Responsibilities

- `jffs2_do_new_inode()` allocates an inode cache, initializes present inode state, assigns an inode number, and initializes a raw inode header/version.
- `jffs2_write_dnode()` writes raw inode nodes and optional data payloads, retries failed writes when allowed, marks partial failed writes obsolete, creates a `jffs2_full_dnode`, and links the physical node ref.
- `jffs2_write_dirent()` writes raw dirent nodes, validates names do not contain embedded NUL bytes, retries failed writes, creates `jffs2_full_dirent`, and links the physical node ref.
- `jffs2_write_inode_range()` splits logical writes by page boundary and available allocation, compresses data, builds raw inode CRCs, writes dnodes, inserts them into the inode fragment tree, and obsoletes old metadata.
- `jffs2_do_create()` writes initial metadata node, initializes security and ACL metadata, writes the parent dirent, and links it into the parent directory list.
- `jffs2_do_unlink()` either writes a deletion dirent when physical obsoletion is unavailable or marks an existing dirent obsolete when it is available, then adjusts dead inode link/parent state.
- `jffs2_do_link()` writes a new dirent for hard links or directory operations and inserts it into the directory list.

## Important Interactions

- Uses reservation APIs from `nodemgmt.c` and must call `jffs2_complete_reservation()` after successful or failed allocations.
- Uses compression dispatcher from `compr.c`.
- Uses `jffs2_flash_writev()` so writes may be direct or write-buffered.
- Updates in-memory fragment and dirent trees via nodelist helpers.
- Calls security and ACL initialization during create.

## Invariants and Risks

- Raw node header CRC, node CRC, data CRC, and name CRC are built before writes and later trusted by scan/read paths.
- Non-GC writes may update versions on retry if another writer advanced `highest_version`.
- Failed writes with nonzero `retlen` are deliberately marked obsolete over the intended padded node length.
- Unlink behavior differs sharply depending on whether the medium can physically mark nodes obsolete.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/writev.c -->
# File Research: sources/os/linux/linux/fs/jffs2/writev.c

## Role

Provides direct MTD write helpers for JFFS2 when write buffering is inactive or when scalar direct writes are needed.

## Key Responsibilities

- `jffs2_flash_direct_writev()` optionally records summary metadata for vector writes when write buffering is not active, then calls `mtd_writev()`.
- `jffs2_flash_direct_write()` calls `mtd_write()` for scalar writes and records summary metadata via a one-element `kvec` when summary support is active.

## Important Interactions

- Used by `os-linux.h` as the direct-write backend when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Used indirectly by write paths that call `jffs2_flash_writev()` in non-write-buffered configurations.
- Feeds summary collection for direct writes so summarized eraseblocks remain consistent.

## Invariants and Risks

- Summary collection errors are returned before or instead of write results where applicable.
- Direct writes do not perform write-buffer recovery, pending-inode tracking, or read-overlay behavior; those are exclusive to `wbuf.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/writev.c -->