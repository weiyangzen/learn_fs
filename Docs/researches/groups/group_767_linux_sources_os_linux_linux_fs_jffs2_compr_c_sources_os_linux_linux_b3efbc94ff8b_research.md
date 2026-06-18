# Group Research: group_767_linux_sources_os_linux_linux_fs_jffs2_compr_c_sources_os_linux_linux_b3efbc94ff8b

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`, JFFS2 compression, debug, VFS, erase, allocation, node-list, and GC internals.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr.c -->
# File Research: sources/os/linux/linux/fs/jffs2/compr.c

This file owns the JFFS2 compressor registry and compression/decompression dispatch. It keeps a global priority-ordered `jffs2_compressor_list` protected by `jffs2_compressor_list_lock`, tracks the active global compression mode, and maintains statistics for uncompressed blocks.

`jffs2_compress()` is the main write-side entry point. It selects either the mount override mode or global default, then handles no compression, priority compression, size-based compression, LZO-favored compression, and forced LZO/ZLIB modes. Priority and forced modes use `jffs2_selected_compress()`, which allocates a temporary output buffer, walks enabled compressors, increments `usecount` while calling the compressor outside the list lock, updates per-compressor stats on success, and returns the selected compression ID. Size and favour-LZO modes try all enabled compressors with each compressor’s reusable `compr_buf`, then choose the smallest or LZO-biased best candidate.

`jffs2_decompress()` normalizes old buggy nonzero `usercompr` upper-byte values, special-cases `JFFS2_COMPR_NONE` and `JFFS2_COMPR_ZERO`, and otherwise locates the matching registered decompressor. Unknown compression types return `-EIO`.

Registration is via `jffs2_register_compressor()` and `jffs2_unregister_compressor()`. Registration initializes scratch-buffer/stat fields and inserts by descending priority. Unregistration refuses active compressors by checking `usecount`.

Initialization registers zlib, rtime, rubinmips, dynrubin, and lzo in order, with rollback on init failure. Default compression mode is selected from `CONFIG_JFFS2_CMODE_*`; otherwise priority mode is used. Exit unregisters compressors in reverse-ish module order.

Key dependencies: `compr.h`, compressor modules, `jffs2_sb_info.mount_opts`, node write/read paths in `write.c`, `read.c`, and GC rewrite paths in `gc.c`.

Important invariants: allocated compressed buffers are freed through `jffs2_free_comprbuf()` only when not equal to the original data pointer; compressors must not be unregistered while `usecount` is nonzero; `JFFS2_COMPR_NONE` means the caller stores the original buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr.h -->
# File Research: sources/os/linux/linux/fs/jffs2/compr.h

This header defines the JFFS2 compressor interface, compression priorities, compression modes, and compressor module init/exit declarations.

`struct jffs2_compressor` is the central plugin contract. It contains list linkage, priority, name, on-flash compression ID, optional `compress` callback, required `decompress` callback for registered formats, runtime `usecount`, disabled flag, scratch compression buffer fields used by size-comparison mode, and compression/decompression statistics.

Priority constants rank rubinmips, dynrubin, lzari, rtime, zlib, and lzo. Rubin compressors are compiled as decompression-only by default through `JFFS2_RUBINMIPS_DISABLED` and `JFFS2_DYNRUBIN_DISABLED`.

Compression modes include none, priority, best size, favour LZO, force LZO, and force ZLIB. `FAVOUR_LZO_PERCENT` defines the threshold used by `compr.c` to prefer LZO when it is close enough to the best compression ratio.

The header exposes `jffs2_compress()`, `jffs2_decompress()`, compressor registry functions, compressor subsystem init/exit, and compressed-buffer freeing. It also provides config-gated inline no-op init/exit functions when a compressor family is disabled.

Key dependencies: Linux kernel allocation/string/types headers, on-flash JFFS2 constants from `<linux/jffs2.h>`, and JFFS2 in-core inode/superblock/node structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_lzo.c -->
# File Research: sources/os/linux/linux/fs/jffs2/compr_lzo.c

This file implements the LZO compressor plugin. It allocates global LZO compression workspace with `vmalloc()` and serializes compression with `deflate_mutex` because `lzo_mem` and `lzo_compress_buf` are shared.

`alloc_workspace()` creates `lzo_mem` sized by `LZO1X_MEM_COMPRESS` and a worst-case PAGE_SIZE compression buffer. `free_workspace()` releases both.

`jffs2_lzo_compress()` compresses `*sourcelen` bytes into the shared temporary buffer, fails if the LZO call fails or if the compressed result exceeds caller-provided `*dstlen`, copies the compressed data to `cpage_out`, and updates `*dstlen`. It does not alter `*sourcelen` on success.

`jffs2_lzo_decompress()` uses `lzo1x_decompress_safe()` and requires the decompressed byte count to equal `destlen`, otherwise returning failure.

The static compressor descriptor registers as `JFFS2_COMPR_LZO`, priority `JFFS2_LZO_PRIORITY`, enabled by default. Init allocates the workspace before registry insertion; exit unregisters and frees workspace.

Key dependencies: kernel LZO API, `compr.h`, and the generic compressor registry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_rtime.c -->
# File Research: sources/os/linux/linux/fs/jffs2/compr_rtime.c

This file implements the simple RTIME byte-oriented compressor. The algorithm keeps a 256-entry table of last positions for each byte value. Compression writes each literal byte followed by a run length indicating how many subsequent bytes matched the previous occurrence stream.

`jffs2_rtime_compress()` refuses tiny destination buffers, initializes the positions table, emits byte/run pairs while source and output space remain, and fails if the encoded output is not smaller than consumed input. On success it updates `*sourcelen` to bytes consumed and `*dstlen` to encoded bytes.

`jffs2_rtime_decompress()` mirrors the table process, copying the literal byte, reading the repeat count, then copying repeated bytes either with an overlap-safe loop or `memcpy()` when ranges do not overlap. It detects output overflow and returns nonzero failure.

The compressor descriptor registers as `JFFS2_COMPR_RTIME`, priority `JFFS2_RTIME_PRIORITY`, with optional disabled state if `JFFS2_RTIME_DISABLED` is defined. Init and exit only register/unregister.

Key dependencies: `compr.h`, JFFS2 compression IDs, and the generic registry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_rtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_rubin.c -->
# File Research: sources/os/linux/linux/fs/jffs2/compr_rubin.c

This file implements Rubin arithmetic-style bit compression and decompression for legacy JFFS2 formats. It defines bitstream helpers (`pushpull`), arithmetic codec state (`rubin_state`), MIPS-tuned static probabilities, and dynamic probability encoding.

Core bitstream helpers are `init_pushpull()`, `pushbit()`, `pullbit()`, and `pushedbits()`. Codec helpers include `init_rubin()`, `encode()`, `end_rubin()`, `init_decode()`, `__do_decode()`, and `decode()`. `out_byte()` encodes eight bits of a byte using per-bit probabilities; `in_byte()` decodes the inverse.

`rubin_do_compress()` encodes input bytes into a bounded destination bitstream and fails if compressed size is not smaller than consumed input. The old `jffs2_rubinmips_compress()` is compiled out. `jffs2_dynrubin_compress()` builds an input histogram, derives eight dynamic probability bytes, stores them as an 8-byte header, then compresses the payload with divider 256.

`rubin_do_decompress()` reconstructs bytes until `destlen` is produced. `jffs2_rubinmips_decompress()` uses static MIPS probabilities. `jffs2_dynrubin_decompress()` reads the 8-byte probability header and decodes the remaining stream.

The two compressor descriptors are intentionally legacy-oriented. `rubinmips` has no compress callback and is decompression-only. `dynrubin` has a compressor implementation but is disabled by default via `JFFS2_DYNRUBIN_DISABLED`. Note the on-flash IDs in the descriptors are historically confusing: names and `JFFS2_COMPR_*` constants are cross-assigned for compatibility.

Key dependencies: `compr.h`, legacy on-flash compression IDs, and the compressor registry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_rubin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_zlib.c -->
# File Research: sources/os/linux/linux/fs/jffs2/compr_zlib.c

This file implements the zlib compressor plugin. It uses global `z_stream` instances for deflate and inflate, protected by separate mutexes, and allocates their workspaces with `vmalloc()`.

`alloc_workspaces()` allocates deflate workspace sized by `zlib_deflate_workspacesize(MAX_WBITS, MAX_MEM_LEVEL)` and inflate workspace sized by `zlib_inflate_workspacesize()`. `free_workspaces()` releases both.

`jffs2_zlib_compress()` reserves `STREAM_END_SPACE` bytes for deflate stream termination, initializes zlib with compression level 3, repeatedly calls `zlib_deflate(..., Z_PARTIAL_FLUSH)` while there is input and output room, then finishes with `Z_FINISH`. It fails if zlib errors, the stream does not end cleanly, or output is not smaller than input. It updates `*dstlen` and `*sourcelen` from zlib totals on success.

`jffs2_zlib_decompress()` initializes inflate, with an optimization that skips zlib’s Adler32 verification when the header is a standard deflate stream without a preset dictionary. It inflates until not `Z_OK`, logs non-`Z_STREAM_END`, ends the stream, and returns 0 unless init fails.

The compressor descriptor registers as `JFFS2_COMPR_ZLIB`, priority `JFFS2_ZLIB_PRIORITY`, enabled unless `JFFS2_ZLIB_DISABLED` is defined. Init allocates workspaces then registers; exit unregisters and frees workspaces.

Key dependencies: kernel zlib/zutil APIs, `compr.h`, `nodelist.h`, and the generic compressor registry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/compr_zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/debug.c -->
# File Research: sources/os/linux/linux/fs/jffs2/debug.c

This file implements JFFS2 sanity checks, paranoia checks, and debug dump helpers enabled through `debug.h` macros.

Sanity checks validate space accounting. `__jffs2_dbg_acct_sanity_check_nolock()` verifies that per-eraseblock sizes sum to `sector_size` and global superblock sizes sum to `flash_size`; failures log details and call `BUG()`. The locked wrapper takes `erase_completion_lock`.

Paranoia checks add structural validation. `__jffs2_dbg_fragtree_paranoia_check_nolock()` walks an inode fragment tree, checking that pristine nodes are not multiply fragmented and do not share partial pages with neighboring non-hole fragments. `__jffs2_dbg_prewrite_paranoia_check()` reads the target flash range and asserts it is all `0xff` before writing. `__jffs2_dbg_acct_paranoia_check_nolock()` recomputes eraseblock used/unchecked/dirty accounting from raw node refs and compares list-level superblock counts via `__jffs2_dbg_superblock_counts()`.

Dump helpers print raw node-ref chains, eraseblock accounting, all block lists, inode fragment trees, arbitrary buffers, and decoded node contents. `__jffs2_dbg_dump_node()` reads a node from flash, validates common header CRC and magic, then decodes inode and dirent node fields including node/name/data CRC information.

Key dependencies: `nodelist.h`, `debug.h`, MTD flash read helpers, CRC32, inode fragment and eraseblock structures.

Important invariant coverage: this file is the defensive layer for JFFS2’s manually maintained accounting and raw-node/fragment relationships. Many failures intentionally halt the kernel because corruption means allocator, GC, or mount state has become internally inconsistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/debug.h -->
# File Research: sources/os/linux/linux/fs/jffs2/debug.h

This header controls JFFS2 debug instrumentation. It defaults `CONFIG_JFFS2_FS_DEBUG` to 0, enables paranoia checks and dumps above level 0, and adds more verbose readinode/fragtree/memalloc messages above level 1. Lightweight sanity checks are always enabled through `JFFS2_DBG_SANITY_CHECKS`.

It defines legacy `D1()` and `D2()` conditional execution macros, `jffs2_dbg(level, ...)`, standardized error/warning/notice/debug message macros with PID and function names, and subsystem-specific debug macros such as `dbg_readinode`, `dbg_fragtree`, `dbg_dentlist`, `dbg_noderef`, `dbg_inocache`, `dbg_summary`, `dbg_fsbuild`, `dbg_memalloc`, and `dbg_xattr`.

The header declares all debug implementation functions in `debug.c`, then maps public macros like `jffs2_dbg_acct_sanity_check()`, `jffs2_dbg_fragtree_paranoia_check()`, and `jffs2_dbg_dump_block_lists()` either to real functions or empty statements depending on compile-time debug configuration.

Key dependencies: Linux printk/current task APIs and JFFS2 structures included indirectly by implementation users.

Notable quirk: `jffs2_dbg_dump_buffer(buf, len, offs)` macro in dump-enabled mode dereferences `*buf` when forwarding, which is unusual and likely inherited legacy macro behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/dir.c -->
# File Research: sources/os/linux/linux/fs/jffs2/dir.c

This file implements JFFS2 directory file and inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

`jffs2_lookup()` hashes the target name with `full_name_hash()`, walks the directory’s sorted `full_dirent` list under `dir_f->sem`, chooses the newest matching dirent version, and returns `d_splice_alias()` for the resolved inode if `ino` is nonzero.

`jffs2_readdir()` emits `.` and `..`, then iterates `f->dents` under `f->sem`, using `ctx->pos` as a linear cookie and skipping deletion dirents (`ino == 0`).

Creation-style operations allocate raw inode/dirent records, reserve flash space, create a new inode with `jffs2_new_inode()`, write inode metadata or data nodes, initialize security and ACLs, then write and link a parent dirent. `jffs2_create()` delegates most work to `jffs2_do_create()`. `jffs2_symlink()`, `jffs2_mkdir()`, and `jffs2_mknod()` explicitly write their initial metadata nodes before the parent dirent. Symlinks cache the target in `f->target` and `inode->i_link`; directories set initial nlink 2 and store parent inode in `pino_nlink`; device nodes encode `dev_t` using `jffs2_encode_dev()`.

`jffs2_unlink()` writes a deletion dirent through `jffs2_do_unlink()`, updates the victim nlink from the inocache, and updates parent times. `jffs2_rmdir()` first checks that all child dirents are deletion entries, then unlinks and drops directory link counts. `jffs2_link()` writes a new dirent to the old inode and increments `pino_nlink`.

`jffs2_rename()` only accepts `RENAME_NOREPLACE`. It implements rename as link-new then unlink-old, with explicit victim handling and directory nlink updates. If the unlink-old step fails after link-new succeeds, it logs that a hard link remains and invalidates the new dentry.

Key dependencies: raw node writers in `write.c`, allocation and node-list helpers, `fs.c` inode creation/read paths, ACL/xattr/security hooks, CRC32, and VFS dentry/inode APIs.

Important behavior: rename is not atomically represented by a single on-flash node, and the code explicitly documents the hard-link fallback risk on partial failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/erase.c -->
# File Research: sources/os/linux/linux/fs/jffs2/erase.c

This file manages eraseblock erasure, erase verification, clean-marker writing, bad-block handling, and raw node-ref cleanup for erased blocks.

`jffs2_erase_pending_blocks()` drains `erase_complete_list` and `erase_pending_list` up to a requested count. Completed erases are moved to `erase_checking_list` and verified/marked by `jffs2_mark_erased_block()`. Pending blocks are removed from their list, accounting is moved from used/dirty/free/wasted into `erasing_size`, node refs are freed, and `jffs2_erase_block()` is invoked.

`jffs2_erase_block()` calls `mtd_erase()` on Linux. Allocation failures or transient erase errors refile the block to `erase_pending_list`; permanent failures call `jffs2_erase_failed()`. Successful erase moves the block to `erase_complete_list`, triggers GC, and wakes erase waiters.

`jffs2_erase_failed()` may update NAND bad-block information when cleanmarkers live in OOB and a specific bad offset is known. Blocks that should not be retried are moved to `bad_list`, with global erasing/bad accounting updated.

`jffs2_free_jeb_node_refs()` walks a block’s raw-node-ref blocks, removes refs from each inode/xattr ref chain with `jffs2_remove_node_refs_from_ino_list()`, frees refblocks, and clears `first_node`/`last_node`. This is required before reusing an eraseblock.

`jffs2_block_check_erase()` verifies a newly erased block contains all `0xff`, using `mtd_point()` where possible or page-sized reads otherwise. `jffs2_mark_erased_block()` then writes an OOB or in-band cleanmarker if needed, resets free accounting, links an in-band cleanmarker ref, moves the block to `free_list`, and updates free/erasing block counts.

Key dependencies: MTD erase/read/point APIs, NAND cleanmarker and badblock helpers from writebuffer code, node-ref helpers in `nodelist.c`, and GC trigger/wait mechanisms.

Important invariants: eraseblock list transitions are protected by `erase_free_sem` plus `erase_completion_lock`; a block is only returned to `free_list` after erase verification and cleanmarker handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/file.c -->
# File Research: sources/os/linux/linux/fs/jffs2/file.c

This file implements regular-file VFS operations and address-space operations.

`jffs2_file_operations` wires generic llseek/open/read/write/splice/lease helpers, `jffs2_ioctl()`, read-only mmap prepare, and `jffs2_fsync()`. `jffs2_fsync()` waits for writeback over the requested range, locks the inode, and triggers `jffs2_flush_wbuf_gc()` for that inode to flush pending write-buffer data.

`jffs2_file_inode_operations` provides ACL, setattr, and xattr listing hooks. `jffs2_file_address_operations` provides `read_folio`, `write_begin`, and `write_end`.

`jffs2_do_readpage_nolock()` maps a folio, reads a PAGE_SIZE range through `jffs2_read_inode_range()`, marks the folio uptodate on success, and flushes dcache. `jffs2_read_folio()` serializes with `f->sem`; `__jffs2_read_folio()` is the unlocked helper used by GC page reads.

`jffs2_write_begin()` handles sparse extension before the write by creating a zero-compressed hole node from old EOF to the new position. It then locks `c->alloc_sem`, obtains the target folio, and reads it in under `f->sem` if not uptodate. The alloc semaphore prevents a GC/page-cache deadlock while a page is being brought uptodate.

`jffs2_write_end()` writes back actual data from the folio. It allocates a raw inode, fills identity/mode/uid/gid/size/time fields, maps the folio from an aligned start offset, calls `jffs2_write_inode_range()`, adjusts the returned written length for alignment padding, updates inode size/blocks/timestamps, clears uptodate on partial write, and releases the folio.

Key dependencies: `read.c`, `write.c`, compression through `jffs2_write_inode_range()`, VFS folio APIs, CRC32, and writebuffer flush support.

Important locking: regular reads use `f->sem`; write begin additionally uses `c->alloc_sem` while acquiring/reading the page to avoid GC deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/fs.c -->
# File Research: sources/os/linux/linux/fs/jffs2/fs.c

This file provides Linux VFS superblock/inode integration for JFFS2: setattr, statfs, inode eviction/read/new-inode, remount, mount fill, GC inode fetch/release, and flash-type setup/cleanup.

`jffs2_do_setattr()` writes a new metadata inode node for mode/uid/gid/time/size changes. For device nodes and symlinks it preserves associated metadata data by re-encoding `dev_t` or reading the symlink target. Size extension is represented as a `JFFS2_COMPR_ZERO` hole node; truncate-to-zero uses deletion-priority allocation. After writing the new node, it updates VFS inode fields, truncates the fragment tree on shrink, adds hole nodes on extension, obsoletes old metadata, completes the flash reservation, and performs `truncate_setsize()` after dropping `f->sem`.

`jffs2_setattr()` runs VFS permission/preparation checks and updates POSIX ACL mode data after successful chmod. `jffs2_statfs()` reports flash-size-derived block counts and computes available space from dirty plus free space minus write-reserved blocks.

`jffs2_evict_inode()` drops page cache, clears the VFS inode, and calls `jffs2_do_clear_inode()` to free JFFS2 in-core state. `jffs2_iget()` builds an inode from on-flash data via `jffs2_do_read_inode()`, sets ownership, size, times, nlink, operations, and special inode data; directories recompute nlink by counting live child dirents.

`jffs2_dirty_inode()` persists metadata-only dirty state by constructing an `iattr` and calling `jffs2_do_setattr()`. `jffs2_do_remount_fs()` handles read-only restrictions, stops GC and flushes writebuffer when remounting, restarts GC for writable mounts, and forces `SB_NOATIME`.

`jffs2_new_inode()` allocates a VFS inode, initializes JFFS2 private state, applies gid inheritance and ACL pre-initialization, creates an inocache/raw inode via `jffs2_do_new_inode()`, fills VFS fields, and inserts the inode locked.

`jffs2_do_fill_super()` validates MTD type and geometry, rejects unsupported MLC NAND, sets flash/sector sizes, initializes flash-specific writebuffer behavior, allocates the inocache hash table, initializes xattrs, scans/builds the filesystem with `jffs2_do_mount_fs()`, obtains root inode 1, fills superblock fields, and starts GC for writable mounts. Cleanup unwinds xattr, summary, block, inode-cache, and flash setup state.

`jffs2_gc_fetch_inode()` and `jffs2_gc_release_inode()` are GC-specific inode lifetime helpers. Unlinked inodes are looked up with `ilookup()` to avoid resurrecting deleted objects; linked inodes use `jffs2_iget()`.

Key dependencies: VFS superblock/inode APIs, MTD geometry, mount/build/readinode/write paths, xattr/ACL/security hooks, writebuffer setup backends, and GC thread control.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/gc.c -->
# File Research: sources/os/linux/linux/fs/jffs2/gc.c

This file implements JFFS2 garbage collection. A GC pass checks unchecked nodes, erases pending blocks, chooses a source eraseblock, moves or obsoletes one live node, and schedules fully obsolete blocks for erasure.

`jffs2_find_gc_block()` selects a block under `erase_completion_lock`, weighted by list and `jiffies`: bad-used when enough free blocks exist, then erasable, very-dirty, dirty, clean, and fallbacks. It also flushes pending writebuffer blocks when `erasable_pending_wbuf_list` is the only source. The chosen block becomes `c->gcblock`, with `gc_node` initialized to `first_node`.

`jffs2_garbage_collect_pass()` is the top-level state machine. It takes `alloc_sem`, first forces CRC checking of unchecked inodes by walking inocache buckets and calling `jffs2_do_crccheck_inode()`, then handles one pending erase if available. For a GC block, it skips obsolete refs, handles inode-less nodes by copying pristine unknown nodes or marking them obsolete, delegates xattr nodes to xattr GC helpers, and handles inode nodes according to inocache state. Absent pristine nodes can be copied intact under `INO_STATE_GC`; otherwise the inode is fetched and `jffs2_garbage_collect_live()` performs type-specific rewrite. If the GC block reaches zero used bytes, it is moved to `erase_pending_list`.

`jffs2_garbage_collect_live()` locks `f->sem`, verifies the node is still in the current GC block and not obsolete, then identifies whether the raw node is metadata, a data fragment, a live dirent, or a deletion dirent. Data fragments may use the pristine fast path, hole rewrite path, or page-based dnode rewrite path.

`jffs2_garbage_collect_pristine()` copies a raw pristine node byte-for-byte when it fits in newly reserved GC space and passes header/node/data/name CRC checks. If it cannot fit, or validation says the slow path is needed, it returns `-EBADFD`. On write failure it marks any partially written bytes obsolete and retries one allocation.

`jffs2_garbage_collect_metadata()` rewrites special metadata-only nodes, preserving device numbers or symlink targets, computing current inode length from the fragment tree when available, and replacing `f->metadata`.

`jffs2_garbage_collect_dirent()` writes a replacement dirent with a new version and reinserts it into the directory list. `jffs2_garbage_collect_deletion_dirent()` either preserves a deletion dirent on media where nodes cannot be permanently marked obsolete, if it still suppresses an older real dirent, or removes and obsoletes it.

`jffs2_garbage_collect_hole()` rewrites `JFFS2_COMPR_ZERO` hole nodes, preserving the old version for partially overlapped multi-fragment holes where possible. `jffs2_garbage_collect_dnode()` may expand the rewrite range to adjacent page fragments in dirty blocks, reads the folio with the correct folio-before-`f->sem` lock order, recompresses chunks through `jffs2_compress()`, writes replacement inode data nodes, and updates the fragment tree.

Key dependencies: eraseblock lists/accounting, inocache states, fragment tree logic, raw node writers, compression subsystem, page cache, xattr GC, CRC32, and MTD reads/writes.

Important invariants: `alloc_sem` serializes GC with allocation and many write paths; `INO_STATE_GC` prevents read_inode races for absent pristine nodes; GC must either increase dirty accounting or obsolete the target node, otherwise it reports `-ENOSPC`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/ioctl.c -->
# File Research: sources/os/linux/linux/fs/jffs2/ioctl.c

This file contains the JFFS2 ioctl entry point. `jffs2_ioctl()` currently returns `-ENOTTY` for all commands.

The comment notes a planned future interface for `lsattr.jffs2` and `chattr.jffs2`, including compression-related support, but no command decoding exists here.

Key dependencies: VFS file operation dispatch from `file.c` and `dir.c`, which both wire `.unlocked_ioctl = jffs2_ioctl`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/jffs2_fs_i.h -->
# File Research: sources/os/linux/linux/fs/jffs2/jffs2_fs_i.h

This header defines `struct jffs2_inode_info`, the JFFS2 private inode state embedded in each VFS inode.

The structure contains `sem`, an internal mutex used instead of relying solely on `inode->i_rwsem`, because GC needs locking behavior that avoids VFS inode semaphore deadlocks. It tracks `highest_version`, an rb-tree `fragtree` describing file data extents, optional `metadata` dnode for metadata-only inode data, linked-list `dents` for directories, symlink `target`, the permanent `inocache`, JFFS2 flags and user compression preference, and finally the embedded `struct inode vfs_inode`.

This is the core bridge between VFS inode lifetime and JFFS2’s append-only flash-node model. Regular file reads/writes, directory operations, GC, setattr, and readinode code all synchronize or mutate this structure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/jffs2_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/jffs2_fs_sb.h -->
# File Research: sources/os/linux/linux/fs/jffs2/jffs2_fs_sb.h

This header defines JFFS2 superblock-private state and mount options.

`struct jffs2_mount_opts` records compression override settings and reserved-pool size options. The reserved pool limits non-root writes when available space falls below `rp_size`.

`struct jffs2_sb_info` is the filesystem control structure. It stores the MTD device, inode numbering/check state, mount flags, GC thread state, allocation mutex, cleanmarker size, global flash space accounting, reserve thresholds, eraseblock array, current allocation and GC blocks, and all block-state lists: clean, very dirty, dirty, erasable, pending writebuffer erase, erasing, erase checking, erase pending, erase complete, free, bad, and bad-used.

It also contains erase synchronization (`erase_completion_lock`, `erase_wait`, `erase_free_sem`), inocache hash table and lock/waitqueue, NAND/writebuffer fields under `CONFIG_JFFS2_FS_WRITEBUFFER`, summary state, xattr subsystem state under `CONFIG_JFFS2_FS_XATTR`, mount options, and OS-private superblock linkage.

This structure is the shared state mutated by mount/build, write allocation, GC, erase, statfs, remount, and debug accounting checks. Space-accounting fields must sum to `flash_size`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/jffs2_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/malloc.c -->
# File Research: sources/os/linux/linux/fs/jffs2/malloc.c

This file centralizes allocation and freeing of JFFS2 in-core objects through slab caches and targeted `kmalloc()` allocations.

`jffs2_create_slab_caches()` creates caches for full dnodes, raw dirents, raw inodes, temporary dnode info, raw node-ref blocks, node fragments, inode caches, and optional xattr datum/ref objects. Failure unwinds through `jffs2_destroy_slab_caches()`. `jffs2_destroy_slab_caches()` destroys all caches.

Allocation/free wrappers exist for `jffs2_full_dirent`, `jffs2_full_dnode`, `jffs2_raw_dirent`, `jffs2_raw_inode`, `jffs2_tmp_dnode_info`, `jffs2_node_frag`, and `jffs2_inode_cache`, with memory-allocation debug logging. Full dirents are variable-sized and allocated by `kmalloc(sizeof(...) + namesize)`.

Raw node refs are allocated in blocks. `jffs2_alloc_refblock()` initializes `REFS_PER_BLOCK` entries as `REF_EMPTY_NODE` and the final entry as `REF_LINK_NODE`. `jffs2_prealloc_raw_node_refs()` reserves a requested number of empty refs in an eraseblock’s ref chain, allocating linked refblocks as needed and recording `jeb->allocated_refs`.

Optional xattr allocation helpers zero-initialize xattr objects, set their raw-node class, initialize common fields, and free through their slabs.

Key dependencies: `nodelist.h` object definitions and debug allocation macros.

Important invariant: writes must preallocate enough raw node refs before linking physical nodes; `jffs2_link_node_ref()` later consumes `jeb->allocated_refs`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodelist.c -->
# File Research: sources/os/linux/linux/fs/jffs2/nodelist.c

This file implements JFFS2 in-core dirent lists, inode caches, fragment trees, raw node-ref chains, and related accounting helpers.

`jffs2_add_fd_to_list()` inserts full dirents sorted by name hash, replaces older same-name dirents by version, marks obsolete raw nodes when replacing, and frees discarded dirents.

Fragment-tree functions maintain the file logical extent map. `jffs2_lookup_node_frag()` returns the fragment covering an offset or the closest previous fragment. `jffs2_add_full_dnode_to_inode()` wraps a full dnode in a fragment and inserts it through `jffs2_add_frag_to_fragtree()`, which handles holes, overlap, splitting existing fragments, obsoleting fully covered fragments, and marking page-sharing nodes `REF_NORMAL` for GC scrutiny. `jffs2_truncate_fragtree()` removes fragments at/after a truncation size and marks/frees underlying dnodes as appropriate. `jffs2_kill_fragtree()` tears down an entire tree, optionally marking nodes obsolete.

`jffs2_obsolete_node_frag()` decrements a dnode’s fragment count, marking the raw node obsolete when no fragments remain or marking it normal when partially live. `new_fragment()` and `jffs2_fragtree_insert()` are local helpers for rb-tree insertion.

Inocache helpers manage sorted hash buckets. `jffs2_get_ino_cache()` looks up an inode cache; `jffs2_add_ino_cache()` assigns an inode number if needed and inserts; `jffs2_del_ino_cache()` removes and conditionally frees based on state; `jffs2_free_ino_caches()` releases all caches and xattr linkage.

Raw-node-ref helpers include `jffs2_free_raw_node_refs()`, `jffs2_link_node_ref()`, `jffs2_scan_dirty_space()`, and `__jffs2_ref_totlen()`. `jffs2_link_node_ref()` consumes a preallocated ref, verifies physical contiguity in the eraseblock, links it into the inode cache if present, and updates used/unchecked/dirty/free accounting based on ref flags. `__jffs2_ref_totlen()` computes node length from the next ref offset or eraseblock free boundary.

Key dependencies: rb-tree APIs, eraseblock accounting, raw node ref flags/macros from `nodelist.h`, allocation helpers, and obsolete-node handling in nodemgmt.

Important invariants: fragment trees must be gap-free except represented holes; raw refs in an eraseblock are physically ordered; superblock and eraseblock accounting is updated at the point refs are linked or dirty space is scanned.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodelist.h -->
# File Research: sources/os/linux/linux/fs/jffs2/nodelist.h

This header defines JFFS2’s central in-core node, inode-cache, fragment, dirent, and eraseblock structures, plus conversion macros and subsystem prototypes.

It sets JFFS2 endian conversion helpers for native, big-endian, and little-endian builds, including mode conversion through OS-specific mode helpers. `JFFS2_MIN_NODE_HEADER`, `PAD()`, allocation priority constants, dirty thresholds, and `write_ofs(c)` are defined here.

`struct jffs2_raw_node_ref` is the compact per-raw-node in-core record. Its `flash_offset` lower two bits encode state: unchecked, obsolete, pristine, or normal. Helpers include `ref_next()`, `jffs2_raw_ref_to_ic()`, `ref_flags()`, `ref_offset()`, `ref_obsolete()`, and `mark_ref_normal()`. Refblocks use `REF_LINK_NODE` and `REF_EMPTY_NODE`.

`struct jffs2_inode_cache` tracks mount-wide inode metadata before or without a live VFS inode: raw node refs, inode state, inode number, hash linkage, xattr ref, and `pino_nlink` which stores parent inode for directories or link count for other inodes. The header defines inode states from unchecked through reading/clearing and raw-node classes for inode/xattr objects.

`struct jffs2_full_dnode`, `jffs2_tmp_dnode_info`, `jffs2_readinode_info`, `jffs2_full_dirent`, `jffs2_node_frag`, and `jffs2_eraseblock` define the higher-level in-core representations used by readinode, directories, file data maps, and eraseblock management.

The remainder declares cross-file APIs for nodelist, nodemgmt, write, readinode, malloc, GC, read, scan, build, erase, and writebuffer support, then includes `debug.h`.

Key dependencies: Linux VFS/types/rbtree, JFFS2 on-flash definitions, OS glue (`os-linux.h` or `os-ecos.h`), xattr/ACL/summary headers, and debug instrumentation.

Important design point: most on-flash node state is reconstructed from compact raw refs and inode caches; full dnodes/fragments are only built for active inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/nodelist.h -->