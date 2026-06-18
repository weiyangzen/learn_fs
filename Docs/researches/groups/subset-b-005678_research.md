# Research: subset-b-005678

Grouped source-tree-aligned research for the JFFS2 files in `sources/distributed-fs/ceph-client/fs/jffs2`. Each file section is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodemgmt.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/nodemgmt.c

## Purpose

`nodemgmt.c` owns the core physical-node allocation and obsolescence machinery for JFFS2. It reserves writable space in eraseblocks, chooses and closes `c->nextblock`, links newly written raw node references into eraseblock and inode accounting, marks old nodes obsolete, and decides when the garbage-collection thread should wake. It is the bridge between high-level write operations in `write.c`, mount-time accounting from `scan.c`, summary handling, and erase/GC scheduling.

## Important APIs, Types, And Functions

The main exported entry points are `jffs2_reserve_space()`, `jffs2_reserve_space_gc()`, `jffs2_add_physical_node_ref()`, `jffs2_complete_reservation()`, `jffs2_mark_node_obsolete()`, and `jffs2_thread_should_wake()`. They work on `struct jffs2_sb_info`, `struct jffs2_eraseblock`, `struct jffs2_raw_node_ref`, and inode caches from `nodelist.h`.

`jffs2_rp_can_write()` enforces the reserved-pool mount option, allowing privileged `CAP_SYS_RESOURCE` writers to proceed when ordinary writes would consume the reserve. `jffs2_find_nextblock()` pulls a block from `free_list`, may force erases or write-buffer flushes, and resets collected summaries for the newly selected block. `jffs2_do_reserve_space()` handles summary reservation, end-of-block padding, cleanmarker obsolescence, and returns the usable length in the current block.

`jffs2_mark_node_obsolete()` is the most stateful routine. It moves node length from unchecked or used accounting to dirty or wasted accounting, refiles eraseblocks across clean, dirty, very-dirty, erasable, erase-pending, and write-buffer-pending lists, optionally clears `JFFS2_NODE_ACCURATE` on NOR-like media, and removes obsolete refs from inode/xattr chains when safe.

## Control Flow

Normal writers call `jffs2_reserve_space()`, which pads the minimum size, takes `alloc_sem`, then works under `erase_completion_lock`. It first applies reserved-pool policy, then loops while there are not enough free or erasing blocks. The loop checks whether enough dirty or possibly available space exists, triggers `jffs2_garbage_collect_pass()`, may sleep on `erase_wait`, and aborts on signals. Once block pressure is acceptable it calls `jffs2_do_reserve_space()`, preallocates raw node refs for the selected nextblock, and keeps `alloc_sem` held until `jffs2_complete_reservation()`.

GC uses `jffs2_reserve_space_gc()`, which repeatedly calls `jffs2_do_reserve_space()` without taking `alloc_sem` itself and yields on `-EAGAIN`. Both reservation paths depend on `jffs2_do_reserve_space()` to either reuse the existing nextblock, write a summary node and close it, waste insufficient tail space, or choose a new free block.

After a physical flash write, writers call `jffs2_add_physical_node_ref()` to link the node at the current write offset. If the block is now full and clean, it may flush the write buffer and move the block to `clean_list`. `jffs2_complete_reservation()` then wakes GC and releases `alloc_sem`.

## State And Persistence Behavior

This file maintains persistent-space accounting: `free_size`, `used_size`, `dirty_size`, `wasted_size`, `unchecked_size`, `erasing_size`, per-block equivalents, and list membership. It also changes medium state on media where obsolete nodes can be physically marked by clearing `JFFS2_NODE_ACCURATE` in the node header. On write-buffered/NAND media it cannot rely on in-place marking, so logical refs and deletion nodes carry more of the persistence semantics.

Summary state is integrated in reservation. A nextblock can reserve room for `c->summary->sum_size`, the incoming node summary size, and `JFFS2_SUMMARY_FRAME_SIZE`; if the node no longer fits, `jffs2_sum_write_sumnode()` is called and the block is closed before selecting another block.

## Dependencies And Integration Points

The code depends on MTD read/write through `jffs2_flash_read()` and `jffs2_flash_write()`, GC through `jffs2_garbage_collect_pass()` and `jffs2_garbage_collect_trigger()`, erase scheduling through `jffs2_erase_pending_blocks()`, summary APIs from `summary.h`, write-buffer helpers such as `jffs2_wbuf_dirty()` and `jffs2_flush_wbuf_pad()`, and inode/xattr cache release helpers. High-level file operations in `write.c` rely on its reservation and obsolescence contract.

## Risks And Edge Cases

The main risks are accounting drift and list corruption. Many branches manually move byte counts between global and per-block buckets, and debug paranoia checks are important signals. `jffs2_add_physical_node_ref()` rejects non-obsolete refs written anywhere other than the current nextblock write offset. `jffs2_mark_node_obsolete()` has subtle media-dependent locking: `erase_free_sem` is only taken when it may physically mark obsolete and release refs, and scanning/building modes deliberately avoid list changes or medium writes.

Space-pressure behavior is also sensitive. Incorrect `dirty`, `avail`, or reserve-block calculations can produce endless GC loops or premature `-ENOSPC`. Summary writes can be disabled for a block if there is not enough room, and write-buffered erase-pending blocks require flush coordination before they can be reused.

## Test Signals

Useful tests include forced low-free-space writes, deletion writes under reserve-pool pressure, GC-trigger wakeups, summary-enabled block closure, write-buffer tail padding, NOR obsolete marking, NAND/no-mark-obsolete behavior, and fault injection for failed flash reads/writes during obsolescence. Assertions and debug checks around `jffs2_dbg_acct_sanity_check*`, unexpected nextblock offsets, and list transitions are high-value runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodemgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/os-linux.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/os-linux.h

## Purpose

`os-linux.h` is the Linux adaptation layer for JFFS2. It maps generic JFFS2 inode and superblock concepts onto Linux VFS structures, provides time and mode conversions, defines no-op versus real write-buffer behavior depending on configuration, and declares Linux-specific JFFS2 entry points used across the filesystem.

## Important APIs, Types, And Functions

The key macros are `JFFS2_INODE_INFO()`, `JFFS2_SB_INFO()`, `OFNI_EDONI_2SFFJ()`, `OFNI_BS_2SFFJ()`, inode field accessors such as `JFFS2_F_I_SIZE()`, and time helpers such as `JFFS2_NOW()` and `JFFS2_CLAMP_TIME()`. `jffs2_init_inode_info()` initializes the per-inode JFFS2 state: highest version, fragment tree, metadata, dirents, symlink target, flags, and compression preference.

Configuration gates define write-buffered and non-write-buffered behavior. Without `CONFIG_JFFS2_FS_WRITEBUFFER`, flash reads/writes map directly to MTD operations, write-buffer flush/setup functions are no-ops, and `jffs2_can_mark_obsolete()` is disabled when summaries are enabled. With write-buffer support, this header declares `wbuf.c` APIs for buffered writes, OOB cleanmarkers, bad-block marking, delayed flushing, and NAND/DataFlash/NOR/UBI setup.

It also declares VFS operation tables and filesystem functions from `background.c`, `dir.c`, `file.c`, `fs.c`, `ioctl.c`, `symlink.c`, and `writev.c`.

## Control Flow

This header is not executable control flow by itself, but it shapes compile-time control flow throughout JFFS2. Callers invoke `jffs2_flash_write()`, `jffs2_flash_read()`, `jffs2_flush_wbuf_pad()`, and related helpers uniformly; preprocessor macros either route them to `wbuf.c` or to direct MTD functions. Mount, inode, and write paths include this layer indirectly through `nodelist.h` to avoid scattering Linux VFS details into generic JFFS2 logic.

## State And Persistence Behavior

`jffs2_init_inode_info()` sets volatile in-core inode state. The write-buffer macros control persistence semantics: direct-write builds may mark obsolete nodes in-place and write directly to MTD, while write-buffer builds must account for page-sized programming units, pending buffered data, OOB cleanmarkers, and media-specific setup/cleanup.

Time helpers clamp Linux `time64_t` values into the 32-bit on-medium timestamp fields used by JFFS2, preventing overflow in persisted raw inode fields.

## Dependencies And Integration Points

The file integrates Linux VFS (`struct inode`, `struct super_block`, `struct kstatfs`, operation tables), MTD (`mtd_read`, direct write wrappers), capabilities of the selected flash type, and optional summary support. It is included by JFFS2 implementation files through `nodelist.h`, making it a central ABI contract for the Linux port.

## Risks And Edge Cases

Macro behavior differs substantially by configuration. Tests that pass on direct NOR-like builds may miss write-buffer-only behavior, and summary-enabled direct-write builds intentionally disable physical obsolete marking. Time clamping can silently saturate values beyond `U32_MAX`. The reversed helper names (`OFNI_*`) are historical and easy to misuse, so call-site type expectations matter.

## Test Signals

Build matrix coverage should include write-buffer off, write-buffer on, summary on/off, xattr/ACL on/off, NAND/DataFlash/NOR/UBI setup paths, and remount/read-only behavior. Compile-time coverage is important because many APIs are macros in one configuration and real functions in another.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/os-linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/read.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/read.c

## Purpose

`read.c` implements data reads from JFFS2 raw inode nodes and logical inode ranges. It validates node and data CRCs, handles compression and historical hole-node quirks, fills holes with zeroes, and walks the in-core fragment tree to satisfy reads.

## Important APIs, Types, And Functions

`jffs2_read_dnode()` reads one `struct jffs2_full_dnode` into a caller buffer. It allocates a temporary `struct jffs2_raw_inode`, reads the node header through `jffs2_flash_read()`, verifies `node_crc`, reads compressed or raw data, verifies `data_crc`, decompresses through `jffs2_decompress()` when needed, and copies the requested slice.

`jffs2_read_inode_range()` reads a logical byte range from an inode by walking `struct jffs2_node_frag` entries in `f->fragtree`. It uses `jffs2_lookup_node_frag()`, `frag_next()`, and `jffs2_read_dnode()`, filling both missing fragment gaps and explicit hole fragments with zeroes.

## Control Flow

A range read starts by locating the fragment overlapping the requested offset. While `offset < end`, the code handles three cases: no fragment or a gap before the next fragment, a fragment with no node, or a data fragment. Gaps and node-less fragments are zero-filled. Data fragments compute the offset within the physical dnode and delegate to `jffs2_read_dnode()`. On read error, the corresponding output range is zeroed and the error is returned.

Inside `jffs2_read_dnode()`, uncompressed whole-node reads can target the caller buffer directly. Partial or compressed reads allocate a compressed read buffer and, for partial compressed nodes, a full decompression buffer. `JFFS2_COMPR_ZERO` is optimized as a memset. Historical nodes with swapped `csize`/`dsize` for zero compression are normalized before use.

## State And Persistence Behavior

This file does not mutate persistent flash state. It trusts the in-core fragment tree built by `readinode.c` but independently validates medium contents with CRCs at read time. The returned data model preserves sparse regions as zeroes, matching filesystem hole semantics.

## Dependencies And Integration Points

The read path depends on flash IO from `jffs2_flash_read()`, compression from `compr.h`, CRC32, allocation helpers for raw inode headers, and fragment-tree helpers from `nodelist.h`. It is consumed by VFS page/folio read paths and by any internal code that needs logical inode data.

## Risks And Edge Cases

Memory allocation failures can occur for compressed or partial reads. Short MTD reads are mapped to `-EIO`. CRC mismatches also produce `-EIO`. The range loop notes a known inefficiency: if one physical node appears in multiple fragments, it may be read more than once. Offset arithmetic must remain consistent between fragment offsets and raw node offsets, especially after truncation or overlapping-node replay.

## Test Signals

Read tests should cover uncompressed full-node reads, uncompressed partial reads, compressed full and partial reads, zero-compression hole nodes, sparse ranges before/between/after fragments, bad node CRC, bad data CRC, short reads, and allocation failure injection. Fragment-tree overlap cases from `readinode.c` are important integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/readinode.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/readinode.c

## Purpose

`readinode.c` reconstructs a live JFFS2 inode from raw node references discovered during mount/scan. It reads all non-obsolete nodes for an inode, validates headers and data as needed, resolves overlapping data nodes by version, builds the final fragment tree, reconstructs directory entries and metadata nodes, caches symlink targets, and clears inode state on eviction or CRC-check passes.

## Important APIs, Types, And Functions

The exported functions are `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`. Internal helpers include `check_node_data()`, `check_tn_node()`, `jffs2_add_tn_to_tree()`, `jffs2_build_inode_fragtree()`, `read_direntry()`, `read_dnode()`, `read_unknown()`, `read_more()`, `jffs2_get_inode_nodes()`, and `jffs2_do_read_inode_internal()`.

The central transient state is `struct jffs2_readinode_info`, which holds a temporary dnode rbtree, directory-entry list, metadata candidate, highest version, latest valid raw ref, and latest directory mctime. Temporary data nodes are represented as `struct jffs2_tmp_dnode_info`, while final state is stored in `f->fragtree`, `f->metadata`, `f->dents`, and `f->target`.

## Control Flow

`jffs2_do_read_inode()` locates the inode cache under `inocache_lock`, transitions unchecked/absent state to `INO_STATE_READING`, waits if the inode is checking or in GC, and creates a root inode cache if inode 1 is missing. It then delegates to `jffs2_do_read_inode_internal()`.

The internal read first calls `jffs2_get_inode_nodes()`. That function walks the inode's raw-ref chain while carefully choosing the next non-obsolete ref before dropping `erase_completion_lock`, because obsolete refs may disappear after erase. It reads enough bytes for the node header, expanding reads to write-buffer page boundaries when useful, validates header CRC and magic, and dispatches to dirent, inode, or unknown-node handling.

`read_dnode()` validates raw inode node CRCs, performs partial data CRC precomputation for unchecked write-buffered nodes, accounts zero-length unchecked nodes immediately, constructs a temporary dnode, and inserts it into the temporary rbtree. `jffs2_add_tn_to_tree()` discards fully overlapped older nodes when newer nodes pass CRC checks, handles version collisions, records overlap markers, and preserves metadata-only zero-size nodes separately.

`jffs2_build_inode_fragtree()` consumes the temporary rbtree from the end, groups overlapping nodes into a version-ordered tree, checks only nodes that survive overlap resolution, and calls `jffs2_add_full_dnode_to_inode()` for valid data. Finally `jffs2_do_read_inode_internal()` reads the latest raw inode header, validates its CRC, applies inode-type-specific fixups, truncates regular-file fragments to `isize`, caches symlink targets, and converts special-file data into `f->metadata`.

## State And Persistence Behavior

This file changes in-core inode state and also changes flash/accounting state for nodes whose CRCs fail or whose unchecked status is resolved. `check_node_data()` moves bytes from unchecked to used and marks refs `REF_PRISTINE`; bad nodes are marked obsolete through `jffs2_mark_node_obsolete()`. Dirent reads similarly move unchecked dirents to used and set `dirent_node_state(rd)`.

For symlinks, the target payload is read from flash and cached in `f->target`. On clear, `jffs2_do_clear_inode()` deletes xattrs, marks metadata and fragment nodes obsolete if the inode is deleted, frees dirents, kills the fragment tree, and returns the inode cache to `INO_STATE_CHECKEDABSENT` or removes it if empty.

## Dependencies And Integration Points

The code depends on flash reads, CRC32, write-buffer page sizing, rbtree helpers, node-ref accounting, inode-cache state management, xattr CRC/delete hooks, fragment tree manipulation, and VFS inode mode semantics. It is invoked from Linux inode instantiation (`jffs2_iget()` in other files), GC CRC-checking, and eviction.

## Risks And Edge Cases

This is one of the highest-risk correctness files. Overlap resolution must avoid trusting obsolete or corrupt newer nodes while not retaining old data hidden by valid newer data. The code intentionally defers full data CRC checks for unchecked write-buffered nodes to avoid checking nodes that will later be discarded. Raw refs can disappear when obsolete blocks are erased, so lock dropping around ref traversal is delicate. Special inodes must have exactly one data fragment; otherwise errors are returned. Missing latest refs are tolerated only for root or directories with children, where fake metadata is constructed.

## Test Signals

High-value tests include overlapping writes with increasing versions, version collisions from GC, corrupt data in newer versus older nodes, unchecked NAND nodes, corrupt dirent names, unknown feature-node compatibility classes, symlink target caching, regular-file truncation to latest `isize`, special-file metadata conversion, concurrent read/clear/GC states, and CRC-check-only inode passes. Fault injection for MTD short reads and allocation failures should verify cleanup of temporary rbtrees and dirent lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/readinode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/scan.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/scan.c

## Purpose

`scan.c` scans the flash medium at mount time, discovers raw JFFS2 nodes, builds initial inode/xattr caches and eraseblock accounting, classifies eraseblocks, seeds GC lists, and optionally uses summary nodes to avoid a full scan of summarized blocks.

## Important APIs, Types, And Functions

The exported functions are `jffs2_scan_medium()`, `jffs2_scan_classify_jeb()`, `jffs2_scan_make_ino_cache()`, and `jffs2_rotate_lists()`. Internal scan helpers include `jffs2_scan_eraseblock()`, `jffs2_scan_inode_node()`, `jffs2_scan_dirent_node()`, xattr scanners under `CONFIG_JFFS2_FS_XATTR`, `jffs2_fill_scan_buf()`, `file_dirty()`, and list rotation helpers.

Block states come from `summary.h`: `BLK_STATE_ALLFF`, `CLEAN`, `PARTDIRTY`, `CLEANMARKER`, `ALLDIRTY`, and `BADBLOCK`. The scanner manipulates `struct jffs2_eraseblock` lists in `struct jffs2_sb_info`: free, clean, dirty, very-dirty, erase-pending, erasable, bad, and the special `nextblock`.

## Control Flow

`jffs2_scan_medium()` first tries `mtd_point()` over the whole device; if direct mapping is unavailable, it allocates a scan buffer sized for a page or whole eraseblock on NAND. It optionally allocates temporary summary collection state. For each eraseblock it resets collected summary state, calls `jffs2_scan_eraseblock()`, checks accounting, and places the block on the appropriate list based on the returned block state.

`jffs2_scan_eraseblock()` handles NAND OOB cleanmarkers and bad-block detection, then checks for a summary marker at the end of the eraseblock. If a valid summary node is found and `jffs2_sum_scan_sumnode()` returns a block classification, full scanning is skipped. Otherwise the scanner reads the block incrementally, skips erased `0xff` regions, detects wrong-endian/old/dirty magic patterns, validates node header CRCs, rejects nodes extending past the eraseblock, treats non-accurate nodes as dirty, and dispatches supported node types.

Inode nodes are scanned lightly: node CRC is checked, an inode cache is created, and the node is linked as `REF_UNCHECKED` for later inode read/CRC verification. Dirent nodes are more fully checked at scan time, including name CRC, parent inode cache creation, full-dirent allocation, and insertion into `ic->scan_dents`. Xattr and xref nodes create xattr datum/ref structures when configured.

## State And Persistence Behavior

The scanner is mostly reconstructive. It builds the in-memory view of persisted flash state and records unresolved inode data as unchecked until `readinode.c` validates it. It also converts invalid or unknown regions to dirty accounting by calling `jffs2_scan_dirty_space()`. Blocks that appear empty are queued for erase unless cleanmarkers make them usable. A partially dirty block with enough free space can become `c->nextblock`; otherwise it is filed dirty.

At the end of scanning, nextblock dirty bytes are treated as wasted because they cannot be recycled immediately, and write-buffered nextblocks may be aligned to the write-buffer page size by marking a small skip region dirty.

## Dependencies And Integration Points

This file integrates MTD mapping/reads, NAND OOB helpers from `wbuf.c`, summary parsing from `summary.c`, node-ref and inode-cache allocators, xattr subsystem setup, and garbage-collection triggering. `readinode.c` depends on the raw-ref chains and unchecked accounting produced here.

## Risks And Edge Cases

Mount safety is the dominant risk. The code refuses to erase pending blocks if the filesystem contains no valid JFFS2 nodes, preventing accidental erasure of non-JFFS2 data. Summary trust is bounded by CRC checks and can fall back to full scan. Name strings with embedded zeroes are truncated for historical media, and zero at start in a summary dirent aborts mount. Misdetected erase size, wrong endian media, old JFFS2 magic, or nodes over block boundaries are treated as dirty/error conditions.

## Test Signals

Tests should cover empty media, cleanmarker-only blocks, summarized blocks, corrupt summary CRCs, unknown compatible/incompatible nodes, corrupt header/node/name CRCs, NAND OOB cleanmarkers, bad blocks, partially dirty candidate nextblocks, all-dirty blocks, no-valid-node media refusal, and list rotation. Mount-time accounting totals and block list counts are the primary assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/security.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/security.c

## Purpose

`security.c` connects JFFS2 extended attributes to the Linux Security Module initial-label and `security.*` xattr interfaces. It lets newly created inodes receive security labels and exposes get/set handlers for the security xattr namespace.

## Important APIs, Types, And Functions

`jffs2_init_security()` calls `security_inode_init_security()` with `jffs2_initxattrs()` as the filesystem callback. `jffs2_initxattrs()` iterates the LSM-provided `struct xattr` array and stores each label through `do_jffs2_setxattr()` using `JFFS2_XPREFIX_SECURITY`.

`jffs2_security_getxattr()` and `jffs2_security_setxattr()` wrap `do_jffs2_getxattr()` and `do_jffs2_setxattr()`. The exported `jffs2_security_xattr_handler` registers the `XATTR_SECURITY_PREFIX` handler.

## Control Flow

On inode creation, higher-level create paths call `jffs2_init_security()` after the initial inode node has been written. The LSM builds the initial label set and calls back into `jffs2_initxattrs()`, which writes each label until one fails. Later VFS xattr operations dispatch through `jffs2_security_xattr_handler` to get or set a named security xattr.

## State And Persistence Behavior

Security labels are persisted as JFFS2 xattr nodes via the generic xattr subsystem, not by this file directly. Errors from xattr writes propagate back to the create path. This means label persistence depends on available flash space, xattr node CRC/accounting, and write-buffer behavior in the lower layers.

## Dependencies And Integration Points

The file depends on Linux xattr and security APIs, JFFS2 xattr prefixes and do-get/do-set helpers, and create flows in `write.c` and VFS inode creation code. The xattr handler is installed on the superblock through `sb->s_xattr = jffs2_xattr_handlers` in `super.c`.

## Risks And Edge Cases

The initial inode node may already exist before label attachment fails, so callers must handle partially created objects through normal cleanup paths. Label writes can fail due to ENOSPC, memory pressure, or flash IO errors. Namespace prefix correctness is security-sensitive: all operations here must use `JFFS2_XPREFIX_SECURITY`.

## Test Signals

Useful tests include creating files under SELinux/Smack/AppArmor label initialization, multiple initial xattrs, failure of the second label write, get/set/remove of `security.*` xattrs, and xattr behavior under low-space conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/summary.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/summary.c

## Purpose

`summary.c` implements JFFS2 summary support. Summaries compactly describe the nodes in an eraseblock so mount scanning can reconstruct raw refs without reading and validating every node. The file also collects summary records during scanning/writing and writes summary nodes at the end of eraseblocks.

## Important APIs, Types, And Functions

Exported functions include `jffs2_sum_init()`, `jffs2_sum_exit()`, `jffs2_sum_add_padding_mem()`, `jffs2_sum_add_inode_mem()`, `jffs2_sum_add_dirent_mem()`, optional xattr/xref adders, `jffs2_sum_reset_collected()`, `jffs2_sum_disable_collecting()`, `jffs2_sum_is_disabled()`, `jffs2_sum_move_collected()`, `jffs2_sum_add_kvec()`, `jffs2_sum_scan_sumnode()`, and `jffs2_sum_write_sumnode()`.

Important internal helpers are `jffs2_sum_add_mem()`, `jffs2_sum_clean_collected()`, `sum_link_node_ref()`, `jffs2_sum_process_sum_data()`, and `jffs2_sum_write_data()`.

## Control Flow

Initialization allocates `c->summary` and a per-eraseblock write buffer capped by `MAX_SUMMARY_SIZE`. During full scan, `scan.c` calls `jffs2_sum_add_*_mem()` for each supported node. If a partially dirty block becomes nextblock, `jffs2_sum_move_collected()` transfers temporary scan collection into the superblock summary so future appends preserve the block's existing summary state.

During writes, `jffs2_flash_direct_writev()` or write-buffered `jffs2_flash_writev()` calls `jffs2_sum_add_kvec()`, which decodes the first kvec node type and records compact summary metadata. Unknown unsupported node types either BUG or disable summary collection, depending on compatibility.

At mount time, `jffs2_sum_scan_sumnode()` validates summary header, total length, node CRC, and summary data CRC. It optionally links a cleanmarker, processes each summary entry into raw refs/inode caches/dirents/xattrs, links the summary node itself, wastes any unexpected free remainder, and returns the block classification. Unsupported compatible entries reset the block accounting and return to full scan.

When a nextblock is being closed, `jffs2_sum_write_sumnode()` preallocates refs and calls `jffs2_sum_write_data()`, which serializes collected entries, appends a `jffs2_sum_marker`, computes CRCs, writes via `jffs2_flash_writev()`, and links the summary node or disables summary on write failure.

## State And Persistence Behavior

Summaries are persisted as `JFFS2_NODETYPE_SUMMARY` nodes near the end of an eraseblock, with a marker at the end pointing to the summary offset. In memory, `struct jffs2_summary` maintains a linked list of collected records, total summary byte size, entry count, padded byte count, and serialization buffer. `JFFS2_SUMMARY_NOSUM_SIZE` disables collection for the current block.

The summary is an optimization, not the sole source of truth. CRC failure or unsupported compatible entries cause fallback to full scanning. Successful summary parsing still creates `REF_UNCHECKED` for inode data, preserving later data validation by `readinode.c`.

## Dependencies And Integration Points

This file depends on `summary.h` data structures, raw node formats from `linux/jffs2.h`, MTD flash writes via `jffs2_flash_writev()`, block accounting and raw-ref helpers from `nodelist.h`, xattr setup under `CONFIG_JFFS2_FS_XATTR`, and scan/reservation hooks from `scan.c` and `nodemgmt.c`.

## Risks And Edge Cases

Summary size is capped at 64 KiB; oversized summaries are disabled for that block. The code must keep relative offsets, padded lengths, and dirty gaps accurate, because summary data omits explicit dirty-space entries and `sum_link_node_ref()` reconstructs gaps as dirty. `jffs2_sum_write_data()` consumes and frees collected entries while serializing; failure paths must leave the summary disabled or reset to avoid stale entries. A typo in the lock annotation references `erase_completion_block`, but the code uses `erase_completion_lock`.

## Test Signals

Tests should cover writing summary nodes, mount fast path through valid summaries, fallback on header/node/data CRC errors, unsupported compatible summary entries, summary overflow, summary disabled by lack of tail space, blocks with cleanmarkers, xattr summary entries, and write failures while writing summary data. Cross-checking full-scan and summary-scan block accounting should be part of validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/summary.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/summary.h

## Purpose

`summary.h` defines the on-flash and in-memory summary formats, block-state constants shared between summary and scan code, summary sizing macros, and the summary API surface. It also provides stub macros when `CONFIG_JFFS2_SUMMARY` is disabled.

## Important APIs, Types, And Functions

The file defines block state constants `BLK_STATE_ALLFF`, `BLK_STATE_CLEAN`, `BLK_STATE_PARTDIRTY`, `BLK_STATE_CLEANMARKER`, `BLK_STATE_ALLDIRTY`, and `BLK_STATE_BADBLOCK`. `MAX_SUMMARY_SIZE` limits summary serialization to 64 KiB. `JFFS2_SUMMARY_NOSUM_SIZE` is the disabled sentinel.

On-flash structs include `jffs2_sum_inode_flash`, `jffs2_sum_dirent_flash`, `jffs2_sum_xattr_flash`, `jffs2_sum_xref_flash`, and `jffs2_sum_marker`. In-memory equivalents add linked-list `next` pointers and are combined by `union jffs2_sum_mem`. `struct jffs2_summary` is stored in `struct jffs2_sb_info` and tracks collected entry size/count/list/padding and the serialization buffer.

When enabled, the header declares the summary lifecycle, collection, scanning, and writing functions implemented in `summary.c`. When disabled, it maps the same names to no-op or zero-returning macros so callers do not need local `#ifdef`s.

## Control Flow

The compile-time switch is the central control flow. With summary support, scan, write, and nodemgmt paths actively collect and emit summaries. Without it, `jffs2_sum_active()` is zero and all collection, movement, writing, and scanning calls become inert.

## State And Persistence Behavior

The on-flash structs are packed because their exact byte layout is persisted. Offsets in summary entries are relative to the eraseblock start. `jffs2_sum_marker` at the end of a summarized block stores the offset and magic used by the scanner to locate the summary node. In-memory structs mirror persisted fields but add list linkage for collection before serialization.

## Dependencies And Integration Points

The header depends on Linux `uio` for `struct kvec` declarations and `linux/jffs2.h` for raw node and endian-wrapped integer types. It is included by scan, nodemgmt, writev, and summary implementation files.

## Risks And Edge Cases

Layout compatibility is critical. Any change to packed summary structs affects on-flash format and mount compatibility. Variable-length dirent names make `JFFS2_SUMMARY_DIRENT_SIZE(x)` sensitive to exact name length. Stub macro signatures must stay aligned with real functions to avoid configuration-specific build or behavior drift.

## Test Signals

Build tests should cover summary enabled and disabled. Format tests should assert expected struct sizes and serialized entry lengths, including dirent variable-length entries. Mount tests should verify marker offset interpretation, block-state constants, and no-op behavior when summary is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/summary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/super.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/super.c

## Purpose

`super.c` is the Linux module and superblock integration layer for JFFS2. It registers the filesystem, handles fs_context parsing and mount setup on MTD devices, wires VFS super/export operations, allocates/frees JFFS2 inodes from a slab cache, synchronizes write buffers, and tears down filesystem state on unmount/module exit.

## Important APIs, Types, And Functions

Important functions include `jffs2_alloc_inode()`, `jffs2_free_inode()`, `jffs2_i_init_once()`, `jffs2_show_options()`, `jffs2_sync_fs()`, NFS export helpers (`jffs2_nfs_get_inode()`, `jffs2_fh_to_dentry()`, `jffs2_fh_to_parent()`, `jffs2_get_parent()`), mount-option parsing (`jffs2_parse_param()`, `jffs2_update_mount_opts()`, `jffs2_reconfigure()`), `jffs2_fill_super()`, `jffs2_get_tree()`, `jffs2_init_fs_context()`, `jffs2_put_super()`, `jffs2_kill_sb()`, `init_jffs2_fs()`, and `exit_jffs2_fs()`.

Key operation tables are `jffs2_super_operations`, `jffs2_export_ops`, `jffs2_context_ops`, and `jffs2_fs_type`.

## Control Flow

Module initialization creates the inode slab cache, initializes compressors and JFFS2 slab caches, then registers the filesystem. Mounting allocates a `struct jffs2_sb_info` in `jffs2_init_fs_context()`, parses `compr=` and `rp_size=` options, and calls `get_tree_mtd()` with `jffs2_fill_super()`. `jffs2_fill_super()` binds the MTD device and superblock, validates reserved-pool size, initializes locks and wait queues, sets VFS operation tables and flags, then calls `jffs2_do_fill_super()`.

Sync and unmount paths flush write-buffered data. `jffs2_sync_fs()` cancels delayed write-buffer work when configured, takes `alloc_sem`, and pads/flushes the write buffer. `jffs2_put_super()` flushes again, exits summary support, frees inode caches/raw refs/block arrays/flash resources/inocache lists/xattrs, syncs MTD, and returns. `jffs2_kill_sb()` stops the GC thread for writable mounts before killing the MTD superblock and freeing `c`.

## State And Persistence Behavior

This file initializes persistent-device-facing state but mostly manages volatile VFS/module resources. It sets `SB_NOATIME`, optional `SB_POSIXACL`, xattr handlers, export operations, and mount options stored in `c->mount_opts`. Sync/unmount forces pending write-buffer data to flash, making it persistence-critical even though it does not encode raw nodes itself.

## Dependencies And Integration Points

It integrates Linux module infrastructure, fs_context, MTD superblock helpers, VFS super/export APIs, JFFS2 compressors, xattrs, ACLs, summary cleanup, flash cleanup, and GC thread lifecycle. It also exposes mount options used by allocation/compression code (`rp_size`, compressor override).

## Risks And Edge Cases

Mount option `rp_size` is checked for multiplication overflow and device-size overflow. Remount updates options under `alloc_sem` after syncing. NFS export ignores inode generation because JFFS2 expects not to reuse inode numbers before flash rewrite, which is a semantic tradeoff. Teardown order matters: pending write-buffer work must not race with freed buffers, raw refs must be freed after caches are no longer active, and RCU-delayed inode frees are flushed before destroying the inode cache on module exit.

## Test Signals

Tests should cover mount/unmount, remount with compression and reserve-pool updates, invalid `rp_size`, sync flushing on write-buffered media, module init failure unwinding at each stage, NFS filehandle lookup, xattr/ACL superblock flags, and unmount while delayed writeback work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/symlink.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/symlink.c

## Purpose

`symlink.c` defines the inode operations table for JFFS2 symbolic links. The actual symlink target data is cached during inode read; this file exposes the VFS operations needed to follow and manage symlink inodes.

## Important APIs, Types, And Functions

The sole exported object is `jffs2_symlink_inode_operations`. It assigns `.get_link = simple_get_link`, `.setattr = jffs2_setattr`, and `.listxattr = jffs2_listxattr`.

## Control Flow

When VFS operates on a JFFS2 symlink inode, link resolution calls `simple_get_link()`, which expects the inode's link string to have been set up in the inode state. Attribute changes route through JFFS2's setattr implementation, and xattr listing routes through the common JFFS2 xattr list function.

## State And Persistence Behavior

This file does not directly persist anything. Symlink target persistence is handled as inode data by write/read paths; `readinode.c` loads the target into `f->target`, and `super.c` frees it with the inode. Attribute changes through `.setattr` can persist metadata nodes through other JFFS2 code.

## Dependencies And Integration Points

It depends on `nodelist.h` for operation declarations and on Linux VFS symlink helpers. It integrates with `readinode.c` target caching, `fs.c` setattr/listxattr implementations, and `os-linux.h` declarations.

## Risks And Edge Cases

The correctness of `simple_get_link()` depends on the symlink target being cached and NUL-terminated elsewhere. Large or corrupt symlink targets are rejected in `readinode.c`, not here. The operation table is intentionally minimal, so missing behavior would surface as VFS-level symlink or xattr regressions.

## Test Signals

Tests should cover creating, reading, following, renaming, and deleting symlinks; listing xattrs on symlinks; changing symlink metadata; and corrupt/oversized target handling through inode read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/wbuf.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/wbuf.c

## Purpose

`wbuf.c` implements write-buffer support for flash media that cannot be programmed byte-by-byte, including NAND, DataFlash, non-bitwriteable NOR, and UBI volumes with writesize greater than one. It batches writes into page/programming-unit buffers, merges reads with pending buffer contents, manages delayed flushes, handles NAND OOB cleanmarkers and bad-block marking, and attempts recovery after page-write failures.

## Important APIs, Types, And Functions

Main exported functions include `jffs2_flash_writev()`, `jffs2_flash_write()`, `jffs2_flash_read()`, `jffs2_flush_wbuf_gc()`, `jffs2_flush_wbuf_pad()`, OOB helpers (`jffs2_check_oob_empty()`, `jffs2_check_nand_cleanmarker()`, `jffs2_write_nand_cleanmarker()`, `jffs2_write_nand_badblock()`), delayed flush trigger `jffs2_dirty_trigger()`, and media setup/cleanup functions for NAND, DataFlash, NOR write-buffer flash, and UBI.

Important internal routines are `jffs2_wbuf_pending_for_ino()`, `jffs2_wbuf_dirties_inode()`, `jffs2_refile_wbuf_blocks()`, `jffs2_block_refile()`, `jffs2_incore_replace_raw()`, optional `jffs2_verify_write()`, `jffs2_wbuf_recover()`, `__jffs2_flush_wbuf()`, and `jffs2_fill_wbuf()`.

## Control Flow

Buffered writes enter `jffs2_flash_writev()`. If buffering is disabled it delegates to direct writev. Otherwise it takes `wbuf_sem`, initializes `wbuf_ofs` on first use, flushes if writing into a new eraseblock, enforces contiguous writes, fills the buffer from input kvecs, writes full pages directly or through `__jffs2_flush_wbuf()`, records summary data, and marks the affected inode dirty for delayed flush if non-GC data remains buffered.

`__jffs2_flush_wbuf()` requires `alloc_sem`, optionally pads the current page with dirty or padding-node bytes, writes one page through MTD, verifies when configured, and on failure calls `jffs2_wbuf_recover()`. On success it accounts padding as wasted/obsolete, refiles eraseblocks pending on the write buffer, clears dirty inode tracking, advances `wbuf_ofs`, and empties the buffer.

`jffs2_wbuf_recover()` handles failed page writes by refiling the failed block as bad-used or erase-pending, identifying non-obsolete raw refs affected by the failed buffer range, reading any already-written prefix if possible, reserving space in a new block, disabling summary for the recovery block, rewriting recoverable data, and replacing raw refs in inode/xattr in-core structures.

Reads use `jffs2_flash_read()`, which performs MTD read and then overlays any overlapping pending write-buffer bytes before returning. ECC clean/uncorrectable codes with full retlen are treated as success so higher-level node CRC validation can decide whether data is usable.

## State And Persistence Behavior

The write buffer stores not-yet-programmed bytes in `c->wbuf`, offset `c->wbuf_ofs`, length `c->wbuf_len`, and page size `c->wbuf_pagesize`. `c->wbuf_inodes` tracks which inodes have pending non-GC writes; on allocation failure it uses `inodirty_nomem` to conservatively treat all inodes as dirty.

Flush and recovery directly affect flash persistence, raw-node refs, eraseblock accounting, and bad-block state. NAND cleanmarkers are persisted in OOB, not inline, so `cleanmarker_size` becomes zero for NAND. Bad blocks are marked through `mtd_block_markbad()` after `MAX_ERASE_FAILURES`.

## Dependencies And Integration Points

The file integrates MTD page writes/reads/OOB operations, raw NAND bad-block APIs, delayed work on `system_long_wq`, dirty writeback timing, summary collection, nodemgmt reservation/accounting, GC passes, inode fetch/release helpers, xattr internals, and Linux read/write semaphores.

## Risks And Edge Cases

This is a high-risk area because failed writes can leave a page partly programmed. Recovery has to preserve live nodes, mark old refs obsolete, update in-core pointers for present inodes, and not trust data that could not be reread. Non-contiguous writes are fatal `BUG()` conditions. Summary collection in `jffs2_flash_writev()` returns before releasing `wbuf_sem` if `jffs2_sum_add_kvec()` fails, which is a suspicious locking risk to inspect if reachable. OOB reads/writes must handle bitflip return codes correctly. Setup paths must free partially allocated buffers on failure.

## Test Signals

Tests should cover buffered writes crossing page and eraseblock boundaries, delayed writeback, fsync/sync flushes, read-after-write before flush, GC-triggered flush by inode, padding modes, direct large-page writes, write failure recovery with live and obsolete refs, secondary recovery failure, ECC `-EUCLEAN` and `-EBADMSG` reads, NAND OOB cleanmarkers, bad-block marking threshold, and setup/cleanup for all supported media types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/wbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/write.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/write.c

## Purpose

`write.c` constructs and persists JFFS2 raw inode and dirent nodes for file data, metadata, creation, unlink, and hard-link operations. It handles compression, CRC generation, inode and directory versioning, node-ref linking, retry after flash write failure, and integration with security/ACL initialization.

## Important APIs, Types, And Functions

Exported functions include `jffs2_do_new_inode()`, `jffs2_write_dnode()`, `jffs2_write_dirent()`, `jffs2_write_inode_range()`, `jffs2_do_create()`, `jffs2_do_unlink()`, and `jffs2_do_link()`.

The main raw on-medium structures are `struct jffs2_raw_inode` and `struct jffs2_raw_dirent`; their in-core counterparts include `struct jffs2_full_dnode`, `struct jffs2_full_dirent`, inode caches, and fragment trees.

## Control Flow

`jffs2_do_new_inode()` allocates and initializes an inode cache, assigns an inode number, fills immutable raw inode header fields, sets mode and version 1, and leaves the caller to complete metadata fields.

`jffs2_write_dnode()` writes one raw inode node plus optional data. It validates header CRC under debug, allocates a full dnode, chooses current `write_ofs(c)`, updates stale versions after retry if necessary, writes through `jffs2_flash_writev()`, and on failure marks any partially written space obsolete/dirty, optionally reserves new space and retries. On success it chooses `REF_PRISTINE` for whole-page/end-of-file style nodes and `REF_NORMAL` otherwise, links a raw ref through `jffs2_add_physical_node_ref()`, and fills the full dnode.

`jffs2_write_inode_range()` loops over the caller's data range. Each iteration reserves enough space, locks the inode, limits writes to page boundaries and allocation size, compresses data, fills raw inode metadata/CRCs/version/isize/offset/compression fields, calls `jffs2_write_dnode()` with no internal retry, inserts the returned full dnode into the inode fragment tree, obsoletes old metadata, completes the reservation, and advances the logical range.

`jffs2_write_dirent()` mirrors dnode writing for directory entries, including embedded-zero name detection, version retry, name hash setup, flash write, and raw-ref linking. `jffs2_do_create()` writes the new inode metadata node, initializes security labels and ACLs, then writes the parent directory entry. `jffs2_do_unlink()` either writes a deletion dirent for media that cannot mark obsolete or directly marks the old dirent obsolete on mark-capable media. `jffs2_do_link()` writes a positive dirent pointing to an existing inode.

## State And Persistence Behavior

This file is responsible for constructing persisted node bytes and CRCs. It increments inode or directory `highest_version` for every logical mutation, updates `isize` for data writes, and uses dirent `ino=0` as a persistent deletion record when needed. Successful writes create raw-node refs that become part of eraseblock and inode accounting. Failed partial writes are recorded as obsolete space so later scans do not reuse the corrupted span incorrectly.

Create is two-phase: the inode metadata node is persisted before security/ACL initialization and parent dirent creation. If later steps fail, callers must handle cleanup through normal unlink/eviction semantics.

## Dependencies And Integration Points

Dependencies include nodemgmt reservation/completion and obsolescence, flash IO/write-buffer wrappers, compression, CRC32, fragment-tree insertion, security and ACL initialization, dirent list insertion, and Linux inode mode helpers. It is used by higher-level VFS file and directory operations.

## Risks And Edge Cases

Write retry logic must avoid reusing stale version numbers after another write advanced `highest_version`; both dnode and dirent retry paths update node CRCs after version changes. Partial writes deliberately mark the intended padded node span obsolete rather than the short retlen to avoid future scans seeing a truncated-but-header-valid node. The create sequence can leave an inode node without a dirent if security/ACL/dirent steps fail. Direct obsolete marking during unlink requires holding `alloc_sem` even though no new space is reserved.

## Test Signals

Tests should cover compressed and uncompressed writes, page-boundary splitting, write failures with retry and no-retry paths, partial retlen handling, stale-version retries, create failures after inode node write, security/ACL initialization failures, unlink on mark-capable and no-mark media, hard links, directory entry replacement, embedded-NUL name rejection, and low-space behavior for normal versus deletion allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/writev.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/writev.c

## Purpose

`writev.c` provides direct MTD write helpers for JFFS2 when no write buffer is needed, and it also records summary metadata for direct writes. It is the direct-write backend selected by `os-linux.h` or by `wbuf.c` when write-buffering is disabled.

## Important APIs, Types, And Functions

`jffs2_flash_direct_writev()` optionally calls `jffs2_sum_add_kvec()` for non-writebuffered summary collection, then writes the kvec array through `mtd_writev()`. `jffs2_flash_direct_write()` writes a contiguous buffer through `mtd_write()` and, when summaries are active, wraps the buffer in a single `struct kvec` and records it through `jffs2_sum_add_kvec()`.

## Control Flow

Callers normally use `jffs2_flash_writev()` or `jffs2_flash_write()`. In non-writebuffered builds those names are macros to these direct helpers; in write-buffered builds, `wbuf.c` may still delegate here when `jffs2_is_writebuffered(c)` is false. Summary collection occurs before `mtd_writev()` in the vector path and after `mtd_write()` in the single-buffer path.

## State And Persistence Behavior

The direct helpers persist bytes immediately to MTD and set the caller-provided `retlen`. They do not themselves link raw node refs or adjust eraseblock accounting; callers in `write.c`, `summary.c`, and nodemgmt do that after checking write success. Summary collection updates in-memory `c->summary` state for the current eraseblock.

## Dependencies And Integration Points

Dependencies are minimal: MTD `mtd_writev()`/`mtd_write()`, `struct kvec`, `jffs2_sum_active()`, and `jffs2_sum_add_kvec()`. The helpers are declared in `os-linux.h` and used by write and summary paths.

## Risks And Edge Cases

The order of summary collection differs between vector and single-buffer writes. In `jffs2_flash_direct_writev()`, summary collection can succeed and then the physical write can fail, leaving summary state for a node that did not persist unless higher layers disable/reset appropriately. In direct single writes, the helper can return a summary-add error after the MTD write has already occurred. These paths rely on callers' failure handling and summary reset/disable behavior.

## Test Signals

Tests should cover direct vector and single writes with summary enabled/disabled, MTD write errors and short writes, summary-add failures, and consistency between summary collection and raw-node accounting after higher-level retry or failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/writev.c -->
