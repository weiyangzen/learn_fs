# Group Research: group_628_jfsutils_sources_local_fs_jfsutils_fsck_Makefile_sources_local_fs_jf_c5786bd8253c

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/jfsutils` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile -->
# File Research: sources/local-fs/jfsutils/fsck/Makefile

This is the configured Automake output for building the JFS userspace checker binary `jfs_fsck` from the `fsck` subdirectory. It is generated from `Makefile.in` by `configure`, with concrete host/build paths and tool substitutions already resolved for a `jfsutils` 1.1.15 build.

The file builds one `sbin_PROGRAMS` target, `jfs_fsck$(EXEEXT)`, from the fsck source set: block map, connectivity, directory tree, EA, inode map, inode, metadata, fileset, workspace, xtree, main checker, run control, message handling, and headers. It compiles with `-I$(top_srcdir)/include -I$(top_srcdir)/libfs`, links `../libfs/libfs.a`, and adds `-luuid`. The object list explicitly includes `dirindex.o`, `fsck_message.o`, `fsckbmap.o`, `fsckconn.o`, and `fsckdire.o`, tying this group’s C files into the checker executable.

Because it is generated after configuration, it embeds resolved toolchain and install settings such as `CC = gcc`, `CFLAGS = -g -O2`, `AM_CFLAGS = -Wall -Wstrict-prototypes -fno-strict-aliasing`, `prefix = /usr`, `sbindir = /sbin`, `mandir = ${datarootdir}/man`, `LN = /usr/bin/ln`, and absolute build/source directories under `/data2/jfsutils-1.1.15`. The resolved `host_alias` is `mipsel-buildroot-linux-uclibc-`, but the compiler value is still plain `gcc` in this configured snapshot.

The main build rule links `jfs_fsck` from all fsck objects plus `../libfs/libfs.a`. Dependency tracking includes `.deps/*.Po` files for each C translation unit. Standard Automake targets cover compilation, install, uninstall, dist, clean, distclean, maintainer-clean, tags, ctags, and manpage install.

The JFS-specific install hooks create hard links:
`/sbin/fsck.jfs` points to installed `/sbin/jfs_fsck`, and `man8/fsck.jfs.8` points to `jfs_fsck.8`. The uninstall hook removes those aliases. This is important operationally because system fsck dispatch typically invokes filesystem-specific helpers by the `fsck.<fstype>` name.

As a generated file, this is build infrastructure rather than checker logic. Its main maintenance concern is that it contains configured absolute paths and generated dependency behavior. Source changes should usually be made in `Makefile.am` or Autotools inputs, not directly here.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile.am -->
# File Research: sources/local-fs/jfsutils/fsck/Makefile.am

This is the concise Automake source for the JFS fsck build. It defines the include paths, link dependencies, installed binary, manpage, source list, and install aliases.

`INCLUDES` points at the project `include` and `libfs` directories. `LDADD` links the checker against `../libfs/libfs.a` and `libuuid`. The only installed program is `jfs_fsck`, and the installed manpage is `jfs_fsck.8`.

The `jfs_fsck_SOURCES` list is the authoritative module inventory for the checker: `fsckbmap.c`, `fsckconn.c`, `fsckdire.c`, `fsckdtre.c`, `fsckea.c`, `fsckimap.c`, `fsckino.c`, `fsckmeta.c`, `fsckpfs.c`, `dirindex.c`, `fsckwsp.c`, `fsckxtre.c`, `xchkdsk.c`, `fsckruns.c`, `fsck_message.c`, plus fsck headers. This group covers the build file and several core modules from that list.

The install hooks create filesystem-helper aliases with hard links: `jfs_fsck` is also installed as `fsck.jfs`, and `jfs_fsck.8` is also linked as `fsck.jfs.8`. The uninstall-local target removes those alias links.

This file is the right place to add or remove fsck translation units or change install behavior. The generated `Makefile.in` and configured `Makefile` mirror this file plus Automake boilerplate.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile.in -->
# File Research: sources/local-fs/jfsutils/fsck/Makefile.in

This is the Automake 1.11.1 template generated from `Makefile.am`. Unlike the configured `Makefile`, it preserves Autoconf substitution variables such as `@CC@`, `@CFLAGS@`, `@prefix@`, `@sbindir@`, `@AM_CFLAGS@`, `@MAINTAINER_MODE_TRUE@`, and dependency-tracking conditionals.

The template builds the same `jfs_fsck$(EXEEXT)` program from the same source/object set and links it with `$(LDADD)`, where `LDADD = ../libfs/libfs.a -luuid`. It installs the same `jfs_fsck.8` manpage and carries the same hard-link hooks for `fsck.jfs` and `fsck.jfs.8`.

Most of the file is standard Automake machinery: VPATH support, installation directory creation, program install/uninstall, dependency-file inclusion, `.c.o` and `.c.obj` compilation rules, manpage install, dist packaging, clean/distclean/maintainer-clean, tags/ctags, and recursive refresh hooks. The dependency includes are guarded with `@AMDEP_TRUE@` and fast dependency rules are guarded with `@am__fastdepCC_TRUE@`, so `configure` decides the concrete dependency behavior.

The template’s meaningful project-specific content is the same as `Makefile.am`: include paths, link libraries, the fsck source list, manpage distribution, and install aliases. Changes should normally originate in `Makefile.am`; regenerating this file requires the matching Automake version or compatible tooling.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/dirindex.c -->
# File Research: sources/local-fs/jfsutils/fsck/dirindex.c

This module validates and updates the optional JFS directory index table used for indexed directory cookies. It depends on fsck globals `sb_ptr` and `agg_recptr`, disk I/O through `ujfs_rw_diskblocks`, extent lookup through `xTree_search`, endian helpers, and directory-table structures from the fsck/JFS headers.

The module keeps a small in-memory LRU cache of directory index pages. `NUM_INDEX_BUFS` is 16, and each `dir_index_page` tracks the aggregate address, next/previous LRU pointers, a dirty flag, and an array of 512 `dir_table_slot` entries. `allocate_dir_index_buffers()` allocates the cache, initializes a free list, and reports `MSG_OSO_INSUFF_MEMORY` on allocation failure.

`read_index_page()` maps a directory cookie to the corresponding directory-index page. It computes the byte offset from `(cookie - 2) * sizeof(struct dir_table_slot)`, derives the logical block number, searches the inode xtree, and reads the page from disk if it is not already cached. Cache hits are moved to MRU position. On cache eviction, dirty LRU pages are written with `write_index_page()` before reuse. I/O failures return `NULL` and recycle the page to the free list.

`flush_index_pages()` writes all dirty cached index pages and clears their dirty flags, returning the first write error. `dirty_index_page()` marks the most recently used page dirty and prints a diagnostic if called for a table pointer that is not the MRU page. That diagnostic is informal and not routed through fsck messages.

`verify_dir_index()` checks an observed directory entry’s cookie against the index table. It ignores cookie zero for compatibility with runtime repair expectations, rejects cookies below 2 or at/above `di_next_index`, selects inline `di_dirtable` when small enough, otherwise reads the external index page, and verifies that the slot is active, points at the expected directory-tree slot, and stores the expected leaf page address. On mismatch it disables further index checking for the inode, requests dirtable rebuild, and marks aggregate corrections needed.

`modify_index()` updates an index slot after directory-tree mutation. For inline tables it updates the inode’s `di_dirtable`; for external tables it reads the relevant index page, changes address and slot number, and marks the cache page dirty. Invalid cookies and read failures are silently ignored.

The module is tightly coupled to `fsckdire.c`: directory insert/split/delete code calls `modify_index()` when sorted-table positions change or entries move to new pages. Its main risk area is cache consistency: dirty pages must be flushed by the caller, and the dirty marker assumes the modified table is the MRU page returned by the last `read_index_page()`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/dirindex.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsck_message.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsck_message.c

This module centralizes fsck message emission and fsck log recording. It defines global `msg_lvl`, initially `fsck_debug`, and `dbg_output`, initially disabled. It uses the global aggregate fsck record `agg_recptr` for log-buffer state.

`fsck_record_msg()` appends a formatted message string to the in-memory fsck log buffer when logging is active. It skips logging if the log is full, unavailable, or allocation failed. It creates an `fscklog_entry_hdr`, copies the text into a fixed-size local `log_entry`, appends a null terminator, pads the entry to a 4-byte boundary, writes a full buffer out with `fscklog_put_buffer()` when needed, clears the buffer after flushing, swaps the log-entry header on big-endian machines, and copies the entry into the fsck log buffer. It updates `fscklog_last_msghdr` and `fscklog_buf_data_len`.

`v_fsck_send_msg()` is the varargs backend for fsck message macros. It indexes `msg_defs[msg_num]`, formats the message text with `vsnprintf`, builds a debug suffix from `basename(file_name)` and `line_number`, prints the message if `message->msg_level <= msg_lvl`, optionally prints source-location detail when `dbg_output` is set, appends the debug detail to the logged string, and calls `fsck_record_msg()`.

The file uses `_GNU_SOURCE` for `basename()`, includes `fsck_message.h`, `fsckwsp.h`, endian helpers, and `xfsckint.h`. It bridges user-visible stdout diagnostics and persistent fsck log records.

Important implementation detail: `msg_string` is bounded, but `fsck_record_msg()` uses `strncpy()` followed by `strlen(msg_txt)` to advance `entry_length`. If an oversized input ever reached it, length accounting would rely on the original string length rather than the truncated copy. In current use, `v_fsck_send_msg()` formats into a smaller bounded buffer before calling it, which constrains normal callers.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsck_message.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckbmap.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckbmap.c

This module verifies and rebuilds the JFS aggregate block allocation map. It compares on-disk dmap/pmap and summary-tree structures against fsck’s workspace block bitmap, rebuilds those structures when repair is approved, and reports summary diagnostics. It depends on global `sb_ptr`, `agg_recptr`, and `bmap_recptr`, plus block-map constants and helpers from `diskmap.h` and `xfsckint.h`.

The file uses `struct fsck_stree_proc_parms` to pass summary-tree context: buffer tree, buffer/workspace summary arrays, leaf counts, leaf index, minimum buddy value, page level/order, and error flags. The same helper path handles dmap trees and higher-level L0/L1/L2 dmapctl trees.

Control-page handling is split between `ctlpage_verify()` and `ctlpage_rebuild()`. Verification reads the block-map control page, swaps it for host endian, and checks mapsize, free-block count, log2 blocks-per-page, allocation-group count, max level, highest active AG, preferred AG, AG geometry fields, max free buddy, and per-AG free lists. Rebuild recomputes all of those fields from fsck state, picks a valid preferred AG when needed, copies `AGFree_tbl`, swaps back, and writes the page.

Dmap pmap handling is split between `dmap_pmap_verify()` and `dmap_pwmap_rebuild()`. Both locate the corresponding section of fsck’s workspace bitmap using `blkmap_find_bit()` and `blkmap_get_page()`. Rebuild copies workspace bits into both `wmap` and `pmap`, computes each word’s max buddy value, counts free and used blocks, and updates aggregate counters. Verify computes the same workspace-derived truth, compares every bit against on-disk `pmap`, records ranges where pmap is unexpectedly on or off, sets `dmap_pmap_error`, and updates aggregate free/used counters.

`dmappg_verify()` and `dmappg_rebuild()` operate on complete dmap pages. They fetch the page by first block, validate or set `start`, `nblocks`, and `nfree`, handle phantom blocks beyond aggregate size, update total free blocks and per-AG free tables, mark active allocation groups, and verify or rebuild the dmap summary tree.

`dmap_tree_verify()` and `dmap_tree_rebuild()` process the dmap’s local buddy summary tree. Verification first checks tree specification fields (`dmt_nleafs`, `dmt_l2nleafs`, `dmt_leafidx`, height, and `budmin`), then calls `stree_verify()`. Rebuild initializes those fields and calls `stree_rebuild()`.

`Ln_tree_verify()` and `Ln_tree_rebuild()` perform the same work for L0, L1, and L2 summary pages. They select the correct workspace leaf/tree arrays and error flags by level, use `LPERCTL`, `L2LPERCTL`, `CTLLEAFIND`, height 5, and buddy minimum `L2BPERDMAP + level * L2LPERCTL`, and read/write pages through `blktbl_Ln_page_get()` and `blktbl_Ln_page_put()`.

`rebuild_blkall_map()` is the full repair path. It initializes block-map fsck state, flushes pending IAG writes because the dmap buffer aliases IAG storage, walks every dmap page, rebuilds dmap pages, feeds dmap root values into L0 workspace leaves, rebuilds L0/L1/L2 pages as leaf sets fill, handles partial final pages by padding leaves with `-1`, and finally rebuilds the control page.

`verify_blkall_map()` is the full validation path. It follows the same traversal shape as rebuild but compares each dmap and summary page instead of rewriting it, then verifies the control page and calls `verify_blkall_summary_msgs()`.

`stree_rebuild()` copies workspace leaf values into the buffer tree and calls `ujfs_adjtree()` to rebuild internal nodes and root. `stree_verify()` calls `ujfs_adjtree()` on the workspace tree and then compares buffer internal nodes and leaves separately, setting distinct leaf/internal error flags and emitting detailed messages.

`init_bmap_info()` zeroes and initializes `bmap_recptr`, sets eyecatchers, assigns buffer pointers into aggregate workspace buffers, computes total block counts and page counts, initializes AG state, counters, current page ordinals/indices, and error flags.

`verify_blkall_summary_msgs()` emits one summary message per detected class of dmap, L0, L1, L2, or control-page error. It marks `agg_recptr->ag_dirty` when allocation map or control metadata is bad.

The important design pattern is “workspace truth first”: earlier fsck passes mark allocated blocks in an independent workspace bitmap, and this module either reconciles on-disk allocation metadata to that truth or reports divergence. The key risk areas are global state sequencing, endian swap boundaries, partial-page padding with `-1`, and shared buffer aliasing with inode allocation group processing.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckbmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckconn.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckconn.c

This module checks namespace connectedness, duplicate directory parenting, and link-count consistency after inode and directory scanning have populated fsck workspace records. It uses global `agg_recptr`, `sb_ptr`, and directory-name globals from `xchkdsk.c`, although this file’s core logic works through fsck inode records and extension records rather than direct directory parsing.

The central data model is `struct fsck_inode_record` plus linked `struct fsck_inode_ext_record` entries. Parent relationships may be stored as the primary `parent_inonum` or as `parent_extension` records. Planned directory-entry removals and additions are represented as extension records attached to parent inodes or aggregate reconnect lists.

`adjust_parent()` attaches an `rmv_direntry_extension` to a parent inode so a directory entry for a specified child will be removed later. It locates the parent inode record, allocates an extension, records child inode number and type, links it to the parent, sets `adj_entries`, and marks corrections needed.

`adjust_parents()` removes all observed parent entries for an inode, except that a directory with illegal hard links may keep its primary/stored parent when it is not being released. It walks the inode’s extension list, preserves non-parent extensions, drops or converts parent extensions into removal requests, treats rebuilt-root parentage as already gone, and clears `unxpctd_prnts` when the primary parent is kept.

`check_connectedness()` walks fileset-owned inodes after special fileset objects. For in-use inodes not selected for release, it reports missing observed paths, calls `reset_parents()` to account for parents that are being released or ignored, and schedules orphan reconnection when no valid parent remains. Reconnection creates an `add_direntry_extension` on `agg_recptr->inode_reconn_extens`, sets `reconnect`, approves corrections, and increments the inode’s link count for the future lost+found-style parent link. For directories with remaining unexpected parents, it displays paths and either schedules fixes in read-write mode or marks the aggregate dirty in read-only mode. For directories whose single observed parent differs from the stored `..` parent, it similarly reports/schedules parent-reference correction.

`check_dir_integrity()` detects a directory having more than one entry for the same child inode from the same parent directory. It examines parent extensions for each in-use directory, compares parent inode numbers against the primary parent and later extensions, and when it finds duplicate parentage it marks the offending parent inode selected for release and emits a bad-key message. This treats duplicate directory entries as corruption in the parent directory.

`check_link_counts()` first counts directory self links and child-directory-to-parent links after accounting for releases, ignored allocation blocks, rebuilt root special cases, and illegal directory hard links. For directories with multiple parents, it converts the primary parent into a `parent_extension`, clears `parent_inonum`, and counts all parent links. It then walks all active inodes and checks whether the accumulated delta against stored link count is zero. Mismatches set `crrct_link_count`; non-orphan mismatches emit bad-link-count messages. In read-write mode it approves link-count corrections. In read-only mode it may mark the aggregate dirty, clears pending correction counters in workspace to avoid accidental side-effect repairs, and emits a summary bad-link-count message.

`reset_parents()` removes or retains parent relationships based on whether parent inodes are selected for release, ignored because their allocation tree is corrupt, or are the rebuilt root. It detaches the extension list while processing, preserves non-parent extensions, decrements link counts for discarded parent links, chooses a surviving parent when possible, and for directories recalculates whether illegal hard links or incorrect stored parent references remain. If a directory goes from multiple parents to one parent and that survivor differs from the stored parent, it sets `crrct_prnt_inonum` and approves correction.

The file’s role in the fsck pipeline is decision staging. It does not directly edit on-disk directory pages; instead it annotates inode records with correction requests that later directory/inode mutation code consumes. Its behavior depends strongly on global mode flags such as `processing_readwrite`, `rootdir_rebuilt`, and inode flags like `selected_to_rls`, `ignore_alloc_blks`, `unxpctd_prnts`, and `crrct_prnt_inonum`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckconn.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckdire.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckdire.c

This module is the fsck-side directory B+tree manager, derived from JFS `dtree.c`. It provides directory search, insert, delete, page split, page free, key comparison, entry movement, and root initialization routines used while fsck reconstructs or adjusts directories. It operates on `struct dinode` directory trees and uses fsck-specific page buffer/allocation helpers such as `recon_dnode_get()`, `recon_dnode_put()`, `recon_dnode_assign()`, `recon_dnode_release()`, `fsck_alloc_fsblks()`, and `fsck_dealloc_fsblks()`.

The file defines a small traversal stack (`btstack`) of up to `MAXTREEHEIGHT` frames, with macros to clear, push, pop, retrieve search results, and get/put B+tree pages. Root page block number is represented by zero and maps to the inline inode `di_btroot`; non-root pages are fetched through reconstruction dnode buffers. `DO_INDEX()` checks `JFS_DIR_INDEX` in the superblock and enables directory-index maintenance.

`fsck_dtSearch()` searches a directory tree for a Unicode component name. It uppercases the search key for OS/2 case-insensitive directories, descends from root through internal pages with binary search, maintains the traversal stack for later insert/delete propagation, and returns a pinned leaf page plus entry index. For create, an existing leaf hit returns `EEXIST`; for remove, a miss returns `ENOENT` and an inode mismatch returns `ESTALE`.

`fsck_dtInsert()` searches for the insertion position, computes required leaf slots using indexed or legacy leaf sizing, and either inserts directly with `dtInsertEntry()` or calls `dtSplitUp()` when the target leaf lacks space. New leaf data stores the target inode number.

`dtSplitUp()` propagates insertion splits bottom-up. Root leaf splits allocate a full page, call `dtSplitRoot()`, and update directory size. Non-root splits preallocate enough page extents for the maximum possible split cascade, call `dtSplitPage()` on the leaf, then walks parent frames. It computes router keys for new right pages, including suffix-compressed uppercase prefix keys between adjacent leaf pages where safe, inserts router entries into parents, and recursively splits full parents. Unused preallocated extents are deallocated on exit.

`dtSplitPage()` splits a non-root directory page. It allocates/assigns the new right page, sets sibling links, initializes sorted-table and freelist state, handles sequential append as a cheap right-page creation, updates the next sibling’s previous pointer for middle splits, computes a fill split point, moves entries to the right page with `dtMoveEntry()`, and inserts the pending entry on the correct side. When directory indexing is enabled, entries moved to the right page have their directory index slots updated through `modify_index()`. It increments `di_nblocks`.

`dtSplitRoot()` moves the inline root contents into a newly allocated child page and converts the inline root into an internal root with a single router entry. It copies the old sorted table and data area, initializes free slots, updates directory index table entries if the moved root was a leaf, inserts the pending new entry into the child page, resets the inline root header, and increments `di_nblocks`.

`fsck_dtDelete()` searches for a leaf entry to remove. If the page would become empty, it calls `fsck_dtDeleteUp()`; otherwise it frees the entry with `fsck_dtDeleteEntry()`, updates directory index entries whose sorted-table indices shifted, and releases the page.

`fsck_dtDeleteUp()` frees empty non-root pages and propagates router-entry deletion up the tree. It keeps an empty root by reinitializing it with `fsck_dtInitRoot()`, relinks siblings around deleted non-root pages with `dtRelink()`, deallocates backing extents, releases reconstruction buffers, and continues upward while parent pages become empty. It decrements `di_nblocks` for freed pages and reduces `di_size`.

`dtRelink()` updates neighboring directory pages’ `prev` and `next` pointers when a page is removed.

`fsck_dtInitRoot()` initializes an inline directory root as `DXD_INDEX | BT_ROOT | BT_LEAF`, clears entries, builds the freelist, sets free count, stores the `..` inode number in `idotdot`, and sets `di_size` to inline data size.

`dtCompare()` and `ciCompare()` compare search keys against leaf/internal entries, including multi-slot segmented names. `ciCompare()` uppercases stored characters when OS/2 case-insensitive behavior is active. `ciGetLeafPrefixKey()` computes a minimal distinguishing router prefix between adjacent leaf entries for suffix compression. `dtGetKey()` reconstructs a full component key from a directory entry’s segmented slots.

`dtInsertEntry()` allocates slots from a page freelist, writes leaf or internal entry data, copies name segments, terminates the segment chain, shifts the sorted table for middle insertions, and updates directory-index slots for shifted leaf entries when indexing is enabled. New indexed leaf entries initially get index zero until the caller creates or updates index state.

`dtMoveEntry()` moves sorted entries from a source page to a destination page during split, copying head and continuation slots, freeing source slots back to the source freelist, and updating destination sorted table, freelist, free count, and nextindex.

`fsck_dtDeleteEntry()` frees all slots belonging to a leaf/internal entry, returns them to the page freelist, shifts the sorted table left, and decrements `nextindex`.

This file is mutation-heavy and depends on careful invariants: sorted-table order, freelist integrity, segmented Unicode name layout, sibling links, `di_size`/`di_nblocks`, and optional directory-index cookie synchronization. The fsck-specific difference from live filesystem code is that it performs reconstruction against fsck buffers and explicit block allocation/deallocation helpers rather than journaled kernel transaction state.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckdire.c -->