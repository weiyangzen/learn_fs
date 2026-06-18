# Group Research: group_1010_linux_stable_sources_os_linux_linux_stable_fs_jffs2_nodemgmt_c_sour_7d61b6499c27

Scope: `Docs/research_subset_a.md` only. All 13 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodemgmt.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/nodemgmt.c

This file manages JFFS2 physical node allocation, active eraseblock selection, obsolete-node accounting, and garbage-collection wakeup policy.

Key responsibilities:
- Enforces reserved-pool write policy in `jffs2_rp_can_write()`, allowing privileged writers through `CAP_SYS_RESOURCE` when normal free/dirty/unchecked/erasing space drops below the configured pool.
- Implements `jffs2_reserve_space()` for normal/deletion allocations, including allocation semaphore ownership, free-block pressure checks, GC triggering, erase-wait sleeps, signal interruption, and raw-node-ref preallocation.
- Implements `jffs2_reserve_space_gc()` for GC allocations without taking `alloc_sem`.
- Selects and retires `c->nextblock` through `jffs2_find_nextblock()` and `jffs2_close_nextblock()`, moving eraseblocks among `free_list`, `clean_list`, `dirty_list`, `very_dirty_list`, `erasable_list`, `erase_pending_list`, and write-buffer-pending erase lists.
- Handles summary-aware reservations in `jffs2_do_reserve_space()`, writing summary nodes before a block becomes too full when summary collection is active.
- Handles no-summary tail waste by linking an obsolete raw-node ref over unusable trailing space and converting its accounting from dirty to wasted.
- Adds freshly written nodes through `jffs2_add_physical_node_ref()`, enforcing contiguous placement at the current write offset and filing full clean blocks.
- Completes reservations in `jffs2_complete_reservation()` by triggering GC and releasing `alloc_sem`.
- Marks nodes obsolete in `jffs2_mark_node_obsolete()`, updating used/unchecked/dirty/wasted accounting, refiling eraseblocks, optionally clearing the on-flash accurate bit, and unlinking obsolete refs from inode or xattr ownership lists when safe.
- Decides whether the background GC thread should wake in `jffs2_thread_should_wake()` based on pending erases, unchecked nodes, low free block counts, and very-dirty block thresholds.

Important interactions:
- Relies on `erase_completion_lock` for block-list and accounting transitions, `alloc_sem` for single active allocation, and `erase_free_sem` to keep refs stable while physically marking obsolete nodes.
- Calls into GC, erase, summary, write-buffer, raw-node-ref, inode-cache, and xattr subsystems.
- Uses `jffs2_can_mark_obsolete()` and read-only/building/scanning flags to distinguish NOR-style physical obsoletion from NAND/summary modes where deletion nodes and in-memory accounting carry more of the burden.

Notable invariants and risks:
- Non-obsolete writes must be appended at `nextblock`'s current free offset; violations are treated as allocator corruption.
- Space-accounting counters must remain balanced across superblock and per-eraseblock totals; this file deliberately runs paranoia checks after major transitions.
- `jffs2_mark_node_obsolete()` has several mode-dependent exits; lock ownership differs depending on whether physical obsoletion is possible.
- GC can be forced when free blocks are insufficient, but the code guards against endless GC loops by comparing dirty/possibly-available space against reserved thresholds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodemgmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/os-linux.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/os-linux.h

This header is the Linux OS adaptation layer for JFFS2 core code.

Key responsibilities:
- Maps JFFS2 private structures to Linux `inode` and `super_block` objects through `JFFS2_INODE_INFO()`, `OFNI_EDONI_2SFFJ()`, `JFFS2_SB_INFO()`, and `OFNI_BS_2SFFJ()`.
- Exposes inode metadata macros for size, mode, uid, gid, rdev, and clamped 32-bit atime/mtime/ctime values.
- Defines `sleep_on_spinunlock()` for wait-queue sleep while dropping a spinlock.
- Initializes per-inode JFFS2 state in `jffs2_init_inode_info()`.
- Provides read-only detection and sector address helpers.
- Supplies no-op/direct-MTD macro implementations when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Declares write-buffer, NAND, DataFlash, UBI volume, and NOR write-buffer setup/read/write helpers when write-buffer support is enabled.
- Declares Linux-facing JFFS2 operations and helpers implemented across `background.c`, `dir.c`, `file.c`, `ioctl.c`, `fs.c`, `symlink.c`, and `writev.c`.

Important interactions:
- Controls whether core code sees direct `mtd_read`/`mtd_writev` behavior or the write-buffered wrappers from `wbuf.c`.
- Summary support changes `jffs2_can_mark_obsolete()`: with summaries enabled, nodes cannot be physically marked obsolete even without write buffering.
- The header is included by most JFFS2 implementation files and defines much of the OS-specific contract.

Notable invariants and risks:
- Time values are clamped into 32-bit on-flash fields.
- Write-buffer-disabled builds intentionally stub many NAND/OOB/bad-block operations.
- `SECTOR_ADDR(x)` depends on the caller having a visible `c` superblock-info variable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/os-linux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/read.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/read.c

This file implements data reads from JFFS2 raw inode nodes and logical inode ranges.

Key responsibilities:
- `jffs2_read_dnode()` reads a raw inode header, verifies header/node CRC, handles an old zero-compression hole-node size bug, reads compressed or uncompressed data, verifies data CRC, decompresses when needed, and copies requested subranges into the caller buffer.
- Optimizes the full uncompressed-node case by reading directly into the destination buffer.
- Allocates intermediate compressed and decompressed buffers only when partial reads or compression require them.
- Treats `JFFS2_COMPR_ZERO` nodes as holes and fills the requested range with zeroes.
- `jffs2_read_inode_range()` walks the inode fragment tree, fills missing ranges and explicit hole fragments with zeroes, and dispatches real fragments to `jffs2_read_dnode()`.

Important interactions:
- Uses raw node refs from the fragment tree built by `readinode.c`.
- Uses `jffs2_flash_read()` so pending write-buffer contents can be visible to reads.
- Uses `jffs2_decompress()` and compressor identifiers stored in raw inode nodes.

Notable invariants and risks:
- Header and data CRC failures return `-EIO`; `jffs2_read_inode_range()` zeroes the failed read span before returning the error.
- Partial compressed reads must decompress the whole logical dnode before copying the requested slice.
- The code notes that a single physical node referenced by multiple fragments may be read more than once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/readinode.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/readinode.c

This file reconstructs an in-memory JFFS2 inode from all non-obsolete raw node refs associated with an inode number.

Key responsibilities:
- Checks deferred data CRCs for unchecked data nodes in `check_node_data()`, using `mtd_point()` when possible, falling back to `jffs2_flash_read()`, and converting unchecked accounting to used accounting when data is valid.
- Maintains a temporary rb-tree of data nodes in `jffs2_add_tn_to_tree()`, discarding older nodes fully covered by newer valid nodes, handling version collisions, and marking overlap candidates for later resolution.
- Builds the final non-overlapping fragment tree in `jffs2_build_inode_fragtree()` by replaying overlapping groups in version order and adding valid full dnodes through `jffs2_add_full_dnode_to_inode()`.
- Reads dirent nodes in `read_direntry()`, validates node/name CRCs when needed, converts unchecked dirents to normal/deletion state, and accumulates full dirents.
- Reads inode data nodes in `read_dnode()`, validates node CRCs, performs lightweight or deferred data-CRC handling, recognizes zero-data metadata nodes, and inserts temporary dnodes.
- Handles unknown node compatibility policy in `read_unknown()`.
- Iterates all inode refs in `jffs2_get_inode_nodes()`, reading enough bytes for each node type, skipping obsolete refs safely under `erase_completion_lock`, and collecting highest version and latest directory mctime.
- Finalizes inode state in `jffs2_do_read_inode_internal()`: builds fragtree, chooses latest metadata, truncates regular files to latest `isize`, caches symlink targets, converts special-file data to metadata, and sets inocache state present.
- Provides public read, CRC-check, and clear paths through `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`.

Important interactions:
- Depends on scan-time inode caches and raw-node-ref lists built by `scan.c` or `summary.c`.
- Coordinates with inocache state machine values such as `UNCHECKED`, `CHECKING`, `GC`, `READING`, `PRESENT`, `CLEARING`, and `CHECKEDABSENT`.
- Calls xattr CRC/delete helpers during inode checking and clearing.

Notable invariants and risks:
- Obsolete raw refs may disappear after erase, so the next valid ref is found while holding `erase_completion_lock` before processing the current ref unlocked.
- Data CRC checking is intentionally deferred for write-buffered flash to avoid checking nodes later proven obsolete.
- Special files and symlinks are expected to have exactly one data fragment, which is moved into `f->metadata`.
- Root inode number 1 can be synthesized if no on-flash root inode exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/readinode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/scan.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/scan.c

This file performs mount-time flash scanning, discovers JFFS2 nodes, builds initial inode caches/raw refs, and classifies eraseblocks for allocation and GC.

Key responsibilities:
- `jffs2_scan_medium()` obtains either an XIP-style mapped flash pointer or an allocated scan buffer, scans every eraseblock, resets per-block summary collection, and files blocks into free, clean, dirty, very-dirty, erasable, erase-pending, or bad lists.
- Preserves the best partially dirty block as `c->nextblock`, moving previous candidates to dirty lists and preserving collected summary metadata for the chosen nextblock.
- Refuses to erase a filesystem that appears to contain no valid JFFS2 nodes unless the block mix proves it is simply empty.
- `jffs2_scan_eraseblock()` checks NAND OOB cleanmarkers and bad-block status, attempts summary-node scan first, and falls back to a full node-by-node scan when no valid summary exists.
- Full scan recognizes erased regions, cleanmarkers, padding, inode nodes, dirent nodes, xattr/xref nodes, obsolete nodes, endian/old/dirty magic patterns, unknown compatible/incompatible feature nodes, and bad CRCs.
- `jffs2_scan_inode_node()` validates inode-node CRCs, creates/fetches inode caches, links unchecked raw refs, updates pseudo-random rotation seed, and records summary info.
- `jffs2_scan_dirent_node()` validates dirent and name CRCs, creates parent inode caches, links raw refs with dirent state, and stores scan dirents.
- Xattr scanning creates datum/ref staging objects when xattr support is enabled.
- `jffs2_rotate_lists()` rotates allocator/GC lists based on a pseudo-random seed derived from node versions to spread wear.

Important interactions:
- Calls summary reader/writer collection helpers, raw-node-ref allocation/linking, dirty-space accounting, NAND cleanmarker helpers, xattr setup, and GC trigger logic.
- The block classification returned by `jffs2_scan_classify_jeb()` drives later allocator behavior in `nodemgmt.c`.

Notable invariants and risks:
- Scanner helper functions must advance offsets and update dirty/used/unchecked/free accounting consistently.
- Header CRC is trusted enough to determine `totlen`; node/data/name CRC failures then mark the node space dirty rather than aborting mount.
- Unknown read-only-compatible nodes force a read-only mount; incompatible nodes abort.
- Summary fallback must reset accounting and raw refs if summary content contains unsupported compatible node types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/security.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/security.c

This file integrates JFFS2 with Linux security xattrs and inode security labeling.

Key responsibilities:
- Implements `jffs2_initxattrs()` as the callback used by LSM inode initialization to attach initial security xattrs through `do_jffs2_setxattr()`.
- Exposes `jffs2_init_security()` as the filesystem hook that calls `security_inode_init_security()`.
- Provides `security.*` xattr get/set handlers backed by JFFS2 xattr prefix `JFFS2_XPREFIX_SECURITY`.
- Defines `jffs2_security_xattr_handler` with `XATTR_SECURITY_PREFIX`.

Important interactions:
- Used during inode creation after the initial raw inode node is written and before the parent dirent is committed.
- Depends on the generic LSM security-label API and JFFS2 xattr storage implementation.

Notable invariants and risks:
- Initial label attachment stops on the first failed xattr write.
- The set handler ignores idmap-specific behavior and delegates policy/storage to `do_jffs2_setxattr()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/summary.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/summary.c

This file implements optional JFFS2 summary support: compact per-eraseblock metadata used to speed mount-time scanning.

Key responsibilities:
- Initializes and frees `struct jffs2_summary` and its bounded write buffer in `jffs2_sum_init()` and `jffs2_sum_exit()`.
- Collects in-memory summary items for inode, dirent, xattr, xref, and padding nodes through `jffs2_sum_add_*_mem()` and `jffs2_sum_add_kvec()`.
- Supports disabling and resetting summary collection per eraseblock, using `JFFS2_SUMMARY_NOSUM_SIZE` as the disabled sentinel.
- Moves scan-collected summary state into the superblock summary for the selected `nextblock`.
- Processes on-flash summary records in `jffs2_sum_process_sum_data()`, creating inode caches, dirent objects, xattr staging objects, and raw refs without reading every full node.
- Validates summary-node header, node, and payload CRCs in `jffs2_sum_scan_sumnode()` before trusting summary contents.
- Writes summary nodes in `jffs2_sum_write_sumnode()` and `jffs2_sum_write_data()`, serializing collected descriptors, adding a trailing summary marker, padding to consume remaining block space, and linking the summary raw ref.

Important interactions:
- Called from `scan.c` during mount and from `nodemgmt.c` before retiring a `nextblock`.
- `writev.c` and `wbuf.c` feed just-written node kvecs into the summary collector.
- Summary scanning uses `sum_link_node_ref()` to account for gaps because summary data does not explicitly encode dirty space.

Notable invariants and risks:
- Summary size is capped at 64 KiB for kmalloc feasibility.
- Summary nodes are non-fatal optimization data: CRC failures or unsupported compatible summary entries fall back to full block scan.
- Unknown node types in write-time summary collection are treated as programmer errors unless they are compatible-copy nodes, which disable summary for the block.
- Failed summary writes mark written bytes obsolete when possible and disable summary for that block.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/summary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/summary.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/summary.h

This header defines JFFS2 summary constants, on-flash summary record formats, in-memory summary record formats, and summary API stubs/prototypes.

Key responsibilities:
- Defines block-state constants returned by scanner paths: all-FF, clean, partially dirty, cleanmarker-only, all-dirty, and bad-block.
- Defines summary size macros for inode, dirent, xattr, and xref records, plus `MAX_SUMMARY_SIZE` and `JFFS2_SUMMARY_NOSUM_SIZE`.
- Declares packed on-flash summary record structures and matching in-memory linked-list structures.
- Defines `struct jffs2_summary`, which tracks collected size/count/padding/list state and the summary write buffer.
- Defines `struct jffs2_sum_marker`, which stores the summary node offset and magic at the end of a summarized eraseblock.
- Exposes real summary functions when `CONFIG_JFFS2_SUMMARY` is enabled and no-op/stub forms when disabled.

Important interactions:
- Included by scanner, allocator, and write paths to coordinate summary collection and scan acceleration.
- Conditional stubs let the rest of JFFS2 call summary helpers unconditionally without spreading preprocessor logic through all call sites.

Notable invariants and risks:
- On-flash structures are packed and contain endian-tagged JFFS2 integer types.
- `MAX_SUMMARY_SIZE` is a hard allocation and usability boundary; larger summaries are intentionally discarded.
- Disabled builds make `jffs2_sum_active()` false and summary operations benign no-ops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/summary.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/super.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/super.c

This file registers JFFS2 with the Linux VFS/MTD mount layer and manages superblock lifecycle, mount options, inode cache allocation, NFS export hooks, sync, and module init/exit.

Key responsibilities:
- Creates and destroys the `jffs2_i` inode slab cache and initializes per-inode mutex/VFS fields.
- Implements inode allocation/free, including freeing cached symlink target strings.
- Parses `compr=` and `rp_size=` mount options through the `fs_context` parser and displays them through `show_options`.
- Updates remount options under `alloc_sem`, syncs the filesystem before reconfigure, and delegates remount work to `jffs2_do_remount_fs()`.
- Fills the superblock in `jffs2_fill_super()`: attaches MTD and OS private pointers, validates reserved-pool size, initializes locks/wait queues, installs super/export/xattr operations, sets `SB_NOATIME`, and enables POSIX ACL flag when configured.
- Provides NFS export helpers using inode-number file handles and parent lookup via directory `pino_nlink`.
- Flushes the write buffer on sync and put-super.
- Tears down summary, inode caches, raw refs, block arrays, flash resources, xattrs, and MTD state in `jffs2_put_super()`.
- Stops the GC thread before killing writable superblocks in `jffs2_kill_sb()`.
- Registers/unregisters the `jffs2` filesystem and initializes compressors and JFFS2 slab caches in module init/exit.

Important interactions:
- Uses `get_tree_mtd()`/`kill_mtd_super()` for MTD-backed mounting.
- Delegates full filesystem construction to `jffs2_do_fill_super()` in `fs.c`.
- Installs `jffs2_super_operations`, `jffs2_export_ops`, and `jffs2_xattr_handlers`.

Notable invariants and risks:
- `rp_size` is specified in KiB but stored in bytes and must not exceed the MTD size.
- Inode numbers are not protected by generation checks for NFS export; comments state flash lifetime/inode reuse semantics are relied on.
- Write-buffer delayed work is cancelled during sync for write-buffered media before padding/flushing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/symlink.c

This file defines JFFS2 inode operations for symbolic links.

Key responsibilities:
- Uses `simple_get_link` for symlink target lookup.
- Reuses `jffs2_setattr` for attribute changes.
- Reuses `jffs2_listxattr` for xattr listing.

Important interactions:
- Symlink target storage and caching are handled elsewhere, especially `readinode.c` for target read/caching and write/create paths for raw inode data.

Notable invariants and risks:
- The file is intentionally minimal; correctness depends on `f->target` being populated before VFS link resolution uses `simple_get_link`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/wbuf.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/wbuf.c

This file implements JFFS2 write-buffer support for media that cannot support arbitrary byte writes, especially NAND, DataFlash, UBI volumes, and non-bitwriteable NOR.

Key responsibilities:
- Tracks which inodes have pending non-GC writes in the write buffer so GC/fsync can flush only relevant data when possible.
- Refiles eraseblocks that become erasable only after pending write-buffer data is flushed.
- Handles bad or suspect blocks with `jffs2_block_refile()`, moving them to `bad_used_list` or erase-pending state and accounting remaining space as obsolete/wasted.
- Verifies writes when `CONFIG_JFFS2_FS_WBUF_VERIFY` is enabled.
- Recovers from write-buffer flush failures in `jffs2_wbuf_recover()` by marking the failed block bad/obsolete, reading any partially written old data when possible, reserving new GC space, rewriting recoverable nodes, relinking raw refs, and updating in-core full dnode/dirent or xattr references.
- Flushes the write buffer in `__jffs2_flush_wbuf()`, optionally padding with dirty bytes or a padding node, writing exactly one write-buffer page, linking padding refs, refiling erasable-pending blocks, and clearing dirty-inode tracking.
- Exposes `jffs2_flush_wbuf_gc()` and `jffs2_flush_wbuf_pad()` for GC-triggered and pad-to-end flushes.
- Implements write-buffered `jffs2_flash_writev()` and `jffs2_flash_write()`, enforcing contiguous writes, splitting full-page direct writes from buffered tails, and feeding summary collection.
- Implements `jffs2_flash_read()` overlaying pending write-buffer bytes on top of MTD reads and tolerating ECC warning returns when the requested data was returned.
- Implements NAND OOB cleanmarker checks/writes, OOB-empty scans, and bad-block marking after repeated erase failures.
- Schedules delayed write-buffer flushing through `dirty_writeback_interval` and `system_long_wq`.
- Provides setup/cleanup for NAND, DataFlash, NOR write-buffer, and UBI volume modes, configuring cleanmarker size, sector size, write-buffer page size, OOB buffers, delayed work, and optional verify buffers.

Important interactions:
- Sits beneath all JFFS2 flash I/O when `jffs2_is_writebuffered(c)` is true.
- Coordinates with allocator/GC through `alloc_sem`, `wbuf_sem`, `erase_completion_lock`, raw-node-ref lists, and block lists.
- Recovery may fetch present inodes through GC helpers to patch live in-core raw-ref pointers.

Notable invariants and risks:
- Writes must be contiguous within the current eraseblock or start a new block; non-contiguous writes are fatal.
- Recovery is best-effort and logs possible data loss when old partial data or replacement space cannot be obtained.
- Pending write-buffer bytes must be visible to reads; otherwise freshly written nodes could fail CRC or appear absent.
- Summary is disabled for recovered blocks because recovery does not reconstruct collected summary state.
- OOB cleanmarker handling uses only the historical 8-byte cleanmarker prefix.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/wbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/write.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/write.c

This file writes JFFS2 raw inode and dirent nodes and implements core create, unlink, and link mutations.

Key responsibilities:
- `jffs2_do_new_inode()` allocates and initializes a new inode cache, assigns an inode number, seeds raw inode header fields, and starts versioning at 1.
- `jffs2_write_dnode()` writes raw inode nodes plus optional data through kvecs, retries failed writes by reserving new space when allowed, marks partially written failed space obsolete, links successful raw refs, and classifies refs as pristine or normal.
- `jffs2_write_dirent()` writes raw dirent nodes plus names, validates names contain no embedded NULs, retries failed writes, links raw refs with dirent state, and returns full dirents.
- `jffs2_write_inode_range()` chunks a logical write by page boundary and available allocation, compresses data, fills all raw inode CRC/size/version fields, writes dnodes, inserts them into the fragment tree, and obsoletes stale metadata nodes.
- `jffs2_do_create()` writes the initial metadata inode node, initializes security labels and ACLs, writes the parent dirent, and links the dirent into the parent list.
- `jffs2_do_unlink()` either writes a deletion dirent when physical obsolete marking is unavailable or marks the existing dirent raw node obsolete in-place when possible; it also updates/deletes child inode link state and directory deletion dirents.
- `jffs2_do_link()` writes and files a new parent dirent for hard-link/rename-style operations.

Important interactions:
- Depends on reservation and completion paths in `nodemgmt.c`, compression helpers, CRC32, fragment-tree insertion, xattr/security/ACL initialization, and write-buffer/direct flash I/O.
- Uses `f->sem` or parent `dir_f->sem` to serialize per-inode metadata/list changes.

Notable invariants and risks:
- Raw node `hdr_crc`, `node_crc`, `data_crc`, size fields, offsets, versions, and endian conversion must be set before writing.
- If a write retry happens after another version has advanced, the node version is bumped and node CRC recomputed.
- Create is not atomic across inode-node, xattr/ACL initialization, and parent-dirent write; failures after the inode node can leave cleanup to later unlink/GC paths.
- Deletion behavior differs significantly between media that can physically clear `JFFS2_NODE_ACCURATE` and media that cannot.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/writev.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/writev.c

This file provides direct, non-write-buffered flash write helpers.

Key responsibilities:
- `jffs2_flash_direct_writev()` optionally records the kvec write in the summary collector when the filesystem is not write-buffered, then calls `mtd_writev()`.
- `jffs2_flash_direct_write()` calls `mtd_write()` for a contiguous buffer and then records the same write as a one-element kvec in summary collection when summary support is active.

Important interactions:
- Used directly in non-write-buffer builds and indirectly by `wbuf.c` when write buffering is disabled.
- Feeds summary collection for direct writes so mount-time summary nodes can describe newly written data.

Notable invariants and risks:
- In `jffs2_flash_direct_write()`, summary collection runs after `mtd_write()` even if the write returned an error; callers still receive the original write result unless summary collection itself returns an error.
- Summary collection can fail with `-ENOMEM`, replacing the write helper return even though flash I/O may already have occurred.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/writev.c -->