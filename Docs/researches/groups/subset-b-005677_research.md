# Research: subset-b-005677

Grouped research for JFFS2 compression, VFS, erase, garbage collection, debug, allocation, and node-list support files under `sources/distributed-fs/ceph-client/fs/jffs2`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr.c

## Purpose
`compr.c` owns the JFFS2 compressor registry and the policy layer used by inode writes and garbage collection to choose how data nodes are stored. It provides compressor registration, global/default compression-mode selection, runtime compression dispatch, decompression dispatch, statistics accounting, and init/exit ordering for the optional zlib, rtime, Rubin, and LZO backends.

## Important APIs, Types, And Functions
The public entry points are `jffs2_compress()`, `jffs2_decompress()`, `jffs2_register_compressor()`, `jffs2_unregister_compressor()`, `jffs2_free_comprbuf()`, `jffs2_compressors_init()`, and `jffs2_compressors_exit()`. The static `jffs2_selected_compress()` implements priority/forced single-backend selection, while `jffs2_is_best_compression()` ranks backends for size and LZO-favoring modes. All backend implementations plug in through `struct jffs2_compressor` from `compr.h`.

## Control Flow
`jffs2_compress()` derives the active mode from mount options or the global default. Priority mode calls the first registered enabled compressor that succeeds; size and favour-LZO modes try every enabled backend using each compressor's temporary buffer and keep the best result; force modes call a requested backend. If no backend wins, the original input buffer is returned with `JFFS2_COMPR_NONE`. `jffs2_decompress()` special-cases uncompressed and zero-filled nodes, then looks up the backend by compression id and calls its decompressor.

## State And Persistence Behavior
Persistent on-flash state is the compression byte stored in raw inode nodes by write/GC code. In-core state includes `jffs2_compressor_list`, `jffs2_compression_mode`, per-backend `usecount`, temporary compression buffers, and compression/decompression counters. The registry is protected by `jffs2_compressor_list_lock`; the lock is dropped while backend code runs, with `usecount` preventing safe unregister during active use.

## Dependencies And Integration Points
This file depends on Linux list/spinlock allocation APIs, `linux/jffs2.h` compression constants, and the backend init/exit functions declared in `compr.h`. It is called by `write.c` and `gc.c` before `jffs2_write_dnode()` persists raw inode nodes, and by read paths when reconstructing file data.

## Risks And Test Signals
Risk concentrates around lock dropping while manipulating per-compressor buffers, failure to restore `datalen`/`cdatalen` between backend trials, backend id availability for old media, and fallback behavior that returns the original buffer. Useful tests mount with each compression mode, force LZO/zlib, disable individual compressors, verify decompression of legacy images, and stress concurrent writes, GC, and module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr.h

## Purpose
`compr.h` defines the compressor abstraction and compression policy constants shared by the JFFS2 compression manager and backend implementations. It is the contract that lets the filesystem register optional algorithms while keeping write, read, and GC code independent of individual compressor internals.

## Important APIs, Types, And Functions
`struct jffs2_compressor` contains list linkage, priority, human name, on-flash compression id, `compress`/`decompress` callbacks, disable/use counters, scratch buffer fields used by size-selection mode, and statistics counters. The header defines backend priorities, default-disabled Rubin flags, compression policy constants (`NONE`, `PRIORITY`, `SIZE`, `FAVOURLZO`, `FORCELZO`, `FORCEZLIB`), and `FAVOUR_LZO_PERCENT`. It declares the registry API and the module init/exit hooks for zlib, rtime, Rubin, and LZO, with inline no-op stubs when a backend is not configured.

## Control Flow
Consumers call `jffs2_compress()` and `jffs2_decompress()` rather than backend functions directly. During filesystem module initialization, `jffs2_compressors_init()` calls the backend init functions exposed here; during teardown, `jffs2_compressors_exit()` calls the corresponding exits.

## State And Persistence Behavior
The header does not persist data itself, but it defines the compression id and policy machinery that affects `jffs2_raw_inode.compr` and `usercompr` fields on flash. The scratch buffer and stats fields are in-core backend state, while `usecount` and `disabled` influence runtime availability.

## Dependencies And Integration Points
It includes kernel allocation/list/types headers, JFFS2 VFS inode and superblock headers, and `nodelist.h`. Backends include this header to publish a static `struct jffs2_compressor`; write/read/GC paths include it to call compression APIs.

## Risks And Test Signals
The major compatibility risk is that the `compr` byte in each backend must match `linux/jffs2.h` on-flash constants forever. Priority values also affect default behavior. Tests should verify configured-out backends compile through stubs, all configured backends register/unregister cleanly, and old images using disabled/decompress-only algorithms still read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_lzo.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr_lzo.c

## Purpose
`compr_lzo.c` implements the optional LZO compressor backend for JFFS2. LZO provides fast compression/decompression and is favored by the `JFFS2_COMPR_MODE_FAVOURLZO` and force-LZO policies when configured.

## Important APIs, Types, And Functions
The module-local entry points are `jffs2_lzo_compress()`, `jffs2_lzo_decompress()`, `alloc_workspace()`, `free_workspace()`, `jffs2_lzo_init()`, and `jffs2_lzo_exit()`. `jffs2_lzo_comp` registers priority `JFFS2_LZO_PRIORITY`, name `lzo`, id `JFFS2_COMPR_LZO`, and the compress/decompress callbacks.

## Control Flow
Init allocates an LZO work memory buffer sized by `LZO1X_MEM_COMPRESS` and a worst-case page compression buffer, then registers the compressor. Compression locks `deflate_mutex`, compresses from caller input to the shared intermediate buffer using `lzo1x_1_compress()`, fails if the result exceeds caller capacity, copies the compressed bytes to `cpage_out`, updates `*dstlen`, and unlocks. Decompression calls `lzo1x_decompress_safe()` and requires the produced length to exactly match the requested destination length.

## State And Persistence Behavior
The only in-core state is the two vmalloc workspaces and their mutex. Persistent state is limited to raw inode nodes tagged with `JFFS2_COMPR_LZO`; the compressed payload is produced by this backend and later validated by exact-length decompression.

## Dependencies And Integration Points
It depends on Linux LZO helpers, vmalloc, mutexes, and the compressor registry in `compr.c`. It is invoked indirectly by `jffs2_compress()` and `jffs2_decompress()` and participates in GC rewrite compression.

## Risks And Test Signals
Shared workspace serialization is essential; missing locks would corrupt concurrent compression. The backend also assumes page-sized worst-case temporary output is enough for the inputs JFFS2 supplies. Tests should exercise force-LZO mounts, concurrent writers, incompressible pages, truncated/corrupt LZO nodes, and init failure cleanup when only one workspace allocation succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_lzo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_rtime.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr_rtime.c

## Purpose
`compr_rtime.c` implements JFFS2's simple rtime compressor. The algorithm records the last output/source position for each byte value and emits pairs of literal byte plus repeat length, targeting a byte-oriented, low-complexity compression format.

## Important APIs, Types, And Functions
The central callbacks are `jffs2_rtime_compress()` and `jffs2_rtime_decompress()`. The static `jffs2_rtime_comp` registers priority `JFFS2_RTIME_PRIORITY`, name `rtime`, id `JFFS2_COMPR_RTIME`, and optional disabled state under `JFFS2_RTIME_DISABLED`. `jffs2_rtime_init()` and `jffs2_rtime_exit()` register and unregister the backend.

## Control Flow
Compression initializes a 256-entry position table, then emits a literal byte followed by the number of following bytes that match the last occurrence of that literal's value, capped at 255. It stops when input is exhausted or output capacity cannot hold another pair. It fails if the encoded size is not smaller than the amount consumed. Decompression reads literal/repeat pairs, writes the literal, consults the previous position table for that value, and copies repeated bytes either byte-by-byte for overlap or with `memcpy()`.

## State And Persistence Behavior
There is no global workspace; all algorithm state is stack-local. On flash, rtime data is identified only by `JFFS2_COMPR_RTIME` in the raw inode compression field.

## Dependencies And Integration Points
The backend depends on kernel string/types headers and `compr.h`. It integrates through the global compressor list and is selected by priority, size, or explicit policy.

## Risks And Test Signals
The decompressor trusts the encoded stream enough to read pairs until `destlen` is satisfied; malformed streams need coverage for short input and overrun prevention. Compression can partially consume input, which callers must honor via updated `*sourcelen`. Tests should include repeated-byte data, random incompressible data, boundary destination sizes, overlapping repeat copies, and compatibility reads of existing rtime-compressed media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_rtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_rubin.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr_rubin.c

## Purpose
`compr_rubin.c` implements legacy Rubin arithmetic-coding decompressors and a dynamic Rubin compressor. These algorithms remain primarily for compatibility with old JFFS2 images; the header disables Rubin compression by default while keeping decompression available.

## Important APIs, Types, And Functions
The file defines bitstream helper `struct pushpull`, arithmetic coder `struct rubin_state`, helpers `init_pushpull()`, `pushbit()`, `pullbit()`, `init_rubin()`, `encode()`, `decode()`, `out_byte()`, and `in_byte()`. Higher-level functions are `rubin_do_compress()`, `jffs2_dynrubin_compress()`, `rubin_do_decompress()`, `jffs2_rubinmips_decompress()`, and `jffs2_dynrubin_decompress()`. Two `struct jffs2_compressor` instances register `rubinmips` and `dynrubin`.

## Control Flow
Dynamic Rubin compression builds a byte histogram, converts it into eight bit probabilities stored in the first eight output bytes, then arithmetic-encodes input bits into the remaining output area. The fixed MIPS variant uses a hard-coded probability table and has its compressor compiled out. Decompression initializes the arithmetic decoder, optionally reads dynamic probabilities from the stream header, and emits bytes until `dstlen` is reached.

## State And Persistence Behavior
The algorithm uses stack-local coder state and static probability tables. Persistent format is the backend id plus, for dynamic Rubin, eight probability bytes at the start of compressed data. The registered compression ids are legacy-sensitive and must match historical on-flash values.

## Dependencies And Integration Points
It depends on `compr.h`, JFFS2 compression constants, and the compressor registry. Read paths use the decompress callbacks for old nodes even when compression is disabled.

## Risks And Test Signals
Risks include legacy id/name confusion, weak malformed-stream bounds in the bit pull path, divide-by-zero if a zero source length were ever passed to dynamic compression, and silent data corruption if probability headers are damaged. Tests should prioritize decompression of known Rubin/RubinMIPS images, malformed/truncated streams, and verifying disabled compressors are skipped for new writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_rubin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_zlib.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/compr_zlib.c

## Purpose
`compr_zlib.c` implements the zlib compressor backend, historically the main JFFS2 compression method. It wraps kernel zlib deflate/inflate workspaces behind the `struct jffs2_compressor` interface.

## Important APIs, Types, And Functions
Important functions are `alloc_workspaces()`, `free_workspaces()`, `jffs2_zlib_compress()`, `jffs2_zlib_decompress()`, `jffs2_zlib_init()`, and `jffs2_zlib_exit()`. The static `z_stream` objects `def_strm` and `inf_strm` are protected by separate mutexes. `STREAM_END_SPACE` reserves trailing output room for final deflate completion.

## Control Flow
Init vmallocs deflate and inflate workspaces and registers `jffs2_zlib_comp`. Compression initializes deflate at level 3, repeatedly feeds bounded chunks with `Z_PARTIAL_FLUSH` while preserving stream-end space, then finalizes with `Z_FINISH`. It rejects results that are not smaller than input and returns updated source/destination lengths. Decompression optionally skips zlib wrapper/adler handling for plain deflate streams without preset dictionaries, initializes inflate with positive or negative window bits, inflates to `Z_STREAM_END`, and tears down the stream.

## State And Persistence Behavior
Global zlib streams and workspaces are reused across calls, serialized by mutexes. On-flash nodes are tagged `JFFS2_COMPR_ZLIB` and store deflate-compatible payload bytes.

## Dependencies And Integration Points
The backend depends on kernel zlib/zutil, vmalloc, mutex APIs, `nodelist.h`, and `compr.h`. It is registered during compressor initialization and called through `jffs2_compress()`/`jffs2_decompress()` from write, read, and GC paths.

## Risks And Test Signals
The decompressor logs non-`Z_STREAM_END` but still returns zero, so corrupt data detection may rely on lower-level CRC checks before decompression. Compression bounds and `STREAM_END_SPACE` are subtle. Tests should include zlib-compressed fixture images, corrupt data CRC paths, tiny destination buffers, concurrent compression/decompression, and mount configurations forcing zlib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/compr_zlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/debug.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/debug.c

## Purpose
`debug.c` implements JFFS2 sanity checks, deeper paranoia checks, and diagnostic dump routines used by the debug macros in `debug.h`. Its checks validate eraseblock accounting, superblock-wide accounting, fragment tree invariants, pre-write erased-state expectations, node-ref chains, block lists, buffers, and raw on-flash nodes.

## Important APIs, Types, And Functions
Sanity functions are `__jffs2_dbg_acct_sanity_check_nolock()` and `__jffs2_dbg_acct_sanity_check()`. Paranoia functions include `__jffs2_dbg_fragtree_paranoia_check[_nolock]()`, `__jffs2_dbg_prewrite_paranoia_check()`, and `__jffs2_dbg_acct_paranoia_check[_nolock]()`. Dump functions include `__jffs2_dbg_dump_node_refs[_nolock]()`, `__jffs2_dbg_dump_jeb[_nolock]()`, `__jffs2_dbg_dump_block_lists[_nolock]()`, `__jffs2_dbg_dump_fragtree[_nolock]()`, `__jffs2_dbg_dump_buffer()`, and `__jffs2_dbg_dump_node()`.

## Control Flow
Sanity checks compare per-block size buckets against sector size and global buckets against flash size. Paranoia checks recalculate counts by walking list membership and node refs, dumping details and BUGing on mismatch. Dump routines print structured information about eraseblock lists, fragment trees, node references, and decoded inode/dirent nodes after CRC checks.

## State And Persistence Behavior
The file does not mutate persistent state except reading flash for verification/dumps. It observes live in-core state under `erase_completion_lock` or `f->sem` where needed and may terminate the kernel via `BUG()` when debug assertions fail.

## Dependencies And Integration Points
It depends on MTD reads, CRC32, JFFS2 endian helpers and structures from `nodelist.h`, and compile-time flags from `debug.h`. Calls are embedded throughout allocation, node-list, write, erase, and GC code as validation hooks.

## Risks And Test Signals
Debug code can be expensive and fatal by design, so false positives or lock misuse can destabilize debug kernels. Tests should run JFFS2 with `CONFIG_JFFS2_FS_DEBUG` levels enabled under write, truncate, unlink, GC, and bad-block simulations, and verify dumps do not dereference invalid refs while reporting corrupted images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/debug.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/debug.h

## Purpose
`debug.h` centralizes JFFS2 debug configuration, message macros, and declarations/wrappers for sanity, paranoia, and dump helpers. It lets the filesystem compile most diagnostics away while keeping lightweight accounting sanity checks enabled by default.

## Important APIs, Types, And Functions
The header defines `jffs2_dbg()`, `JFFS2_ERROR()`, `JFFS2_WARNING()`, `JFFS2_NOTICE()`, `JFFS2_DEBUG()`, legacy `D1`/`D2` wrappers, subsystem-specific macros such as `dbg_fragtree`, `dbg_dentlist`, `dbg_noderef`, `dbg_inocache`, and `dbg_memalloc`, plus conditional wrappers around the `__jffs2_dbg_*` functions implemented in `debug.c`.

## Control Flow
Compile-time `CONFIG_JFFS2_FS_DEBUG` selects which message categories and heavy checks are active. Level 1 enables paranoia and dumps plus broad subsystem messages; level 2 adds more verbose fragment/readinode and memory allocation traces. Disabled categories route to `no_printk()` to preserve format checking without runtime output.

## State And Persistence Behavior
This header has no runtime state, but controls whether debug code inspects and asserts over in-core eraseblock, inode, node-ref, and fragment state. Its macros may turn validation calls into no-ops or into fatal checks depending on configuration.

## Dependencies And Integration Points
It depends on printk and scheduler task id APIs, and it is included through `nodelist.h`, making the debugging surface broadly available across JFFS2. `debug.c` supplies the backing implementations when enabled.

## Risks And Test Signals
Macro mistakes can silently remove checks or evaluate arguments differently between debug and non-debug builds. The `jffs2_dbg_dump_buffer` wrapper appears argument-sensitive and should be compile-tested when dumps are enabled. Test signals include clean builds for debug levels 0, 1, and 2, plus runtime validation that subsystem messages and sanity checks appear only under the intended configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/dir.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/dir.c

## Purpose
`dir.c` implements JFFS2 directory file operations and inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename. It translates VFS namespace mutations into append-only raw inode and dirent nodes, updating in-core dirent lists and link counts.

## Important APIs, Types, And Functions
Exported operation tables are `jffs2_dir_operations` and `jffs2_dir_inode_operations`. Static operation implementations include `jffs2_lookup()`, `jffs2_readdir()`, `jffs2_create()`, `jffs2_unlink()`, `jffs2_link()`, `jffs2_symlink()`, `jffs2_mkdir()`, `jffs2_rmdir()`, `jffs2_mknod()`, and `jffs2_rename()`.

## Control Flow
Lookup scans the directory's sorted `f->dents` list by name hash and returns the newest matching non-deletion dirent. Readdir emits dots, then live dirents while skipping deletion markers. Create-like operations allocate raw node structures, reserve flash space, call `jffs2_new_inode()`, write a metadata/data node as needed, initialize ACL/security, reserve/write a raw dirent, and insert the full dirent with `jffs2_add_fd_to_list()`. Unlink and rmdir write deletion dirents through `jffs2_do_unlink()`. Rename creates a new link then unlinks the old name.

## State And Persistence Behavior
Directory changes persist as new `JFFS2_NODETYPE_DIRENT` nodes and sometimes new raw inode metadata nodes. In-core state includes `jffs2_inode_info.dents`, `metadata`, `target`, `highest_version`, VFS inode link counts/times, and inode-cache `pino_nlink`. Older dirents are obsoleted rather than overwritten.

## Dependencies And Integration Points
This file depends on VFS dentry/inode APIs, ACL/xattr/security helpers, CRC32, `jffs2_do_create()`, `jffs2_do_link()`, `jffs2_do_unlink()`, `jffs2_write_dnode()`, `jffs2_write_dirent()`, and reservation logic from `nodelist.h`.

## Risks And Test Signals
Rename is explicitly non-atomic: if the new link succeeds and old unlink fails, the filesystem can expose an extra hard link and invalidates the target dentry. Error unwinding after partially written symlink/mkdir/mknod nodes is also important. Tests should cover ENOSPC at each reservation/write step, long names, hard-link restrictions, non-empty directory removal, rename-over-file/dir, crash recovery after partial namespace updates, and readdir ordering with deletion dirents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/erase.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/erase.c

## Purpose
`erase.c` manages eraseblock erasure, erase completion verification, cleanmarker writing, bad-block handling, and removal of raw node references belonging to blocks being erased. It is the bridge between JFFS2 GC/accounting lists and MTD erase/read/write operations.

## Important APIs, Types, And Functions
The public functions are `jffs2_erase_pending_blocks()` and `jffs2_free_jeb_node_refs()`. Internal helpers include `jffs2_erase_block()`, `jffs2_erase_succeeded()`, `jffs2_erase_failed()`, `jffs2_remove_node_refs_from_ino_list()`, `jffs2_block_check_erase()`, and `jffs2_mark_erased_block()`.

## Control Flow
`jffs2_erase_pending_blocks()` first processes completed erases by moving them to checking and calling `jffs2_mark_erased_block()`, then starts pending erases by moving block accounting from dirty/used/free/wasted into erasing state, freeing node refs, and calling MTD erase. Successful erases move to `erase_complete_list`; failed erases are retried for transient errors or moved to bad lists. Marking an erased block verifies all bytes are `0xff`, writes an in-band or OOB cleanmarker when needed, links a cleanmarker node ref, and moves the block to `free_list`.

## State And Persistence Behavior
Persistent effects are physical flash erase and optional cleanmarker writes. In-core effects update superblock size buckets, eraseblock lists, bad-block lists, `nr_erasing_blocks`, `nr_free_blocks`, raw-node-ref chains, inode-cache node lists, and wakeups on `erase_wait`. `erase_completion_lock` and `erase_free_sem` protect list/accounting and ref removal.

## Dependencies And Integration Points
It depends on MTD `mtd_erase()`, `mtd_point()`, `mtd_read()`, cleanmarker helpers from write-buffer/NAND code, CRC32, raw-node-ref allocation/linking, and GC trigger/wakeup paths.

## Risks And Test Signals
Risks include accounting drift across error paths, removing refs while inode/xattr code still observes them, bad-block policy differences for NAND, and verification cost on large eraseblocks. Tests should simulate erase success, `-ENOMEM`/`-EAGAIN` retries, permanent failures, cleanmarker write failure, short reads, non-erased bytes, NAND bad-block updates, and concurrent GC/list wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/erase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/file.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/file.c

## Purpose
`file.c` implements regular file operations and address-space operations for JFFS2. It connects generic VFS buffered I/O to JFFS2's fragment tree and append-only raw inode node writes.

## Important APIs, Types, And Functions
Exported tables are `jffs2_file_operations`, `jffs2_file_inode_operations`, and `jffs2_file_address_operations`. Important functions are `jffs2_fsync()`, `jffs2_do_readpage_nolock()`, `__jffs2_read_folio()`, `jffs2_read_folio()`, `jffs2_write_begin()`, and `jffs2_write_end()`.

## Control Flow
Reads lock `f->sem`, map the folio, call `jffs2_read_inode_range()` for a page-sized range, mark the folio uptodate, flush dcache, and unlock. `write_begin()` handles sparse writes beyond EOF by writing a zero-compressed hole node, then locks `alloc_sem` while obtaining/reading the target folio to avoid GC read deadlocks. `write_end()` writes the modified page range, expanding to a whole page when the write reaches page end, via `jffs2_write_inode_range()`, updates size/timestamps/blocks, and marks the folio not uptodate if fewer bytes reached flash.

## State And Persistence Behavior
Persistent writes create new raw inode data or hole nodes. In-core updates include folio uptodate state, inode size/block/timestamps, `f->fragtree`, `f->metadata`, and raw-node obsolete marking. `jffs2_fsync()` waits on writeback and flushes the write buffer for the inode via GC-flush helpers.

## Dependencies And Integration Points
The file depends on generic file helpers, page/folio APIs, CRC32, `jffs2_read_inode_range()`, `jffs2_write_inode_range()`, reservation/write helpers, compression indirectly through write code, and write-buffer flush helpers.

## Risks And Test Signals
The lock ordering between folio locks, `f->sem`, and `c->alloc_sem` is critical for avoiding GC/write deadlocks. Short writes must correctly invalidate cache state. Tests should cover sparse writes, partial writes under ENOSPC, writes at page boundaries, fsync with write-buffered media, concurrent GC and writes to the same page, mmap-read behavior, and data integrity after remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/fs.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/fs.c

## Purpose
`fs.c` implements core superblock/inode lifecycle operations for JFFS2: setattr, statfs, inode eviction and iget, dirty inode writeback, remount handling, new inode setup, superblock fill, GC inode fetch/release, and flash-type setup/cleanup.

## Important APIs, Types, And Functions
Key functions are `jffs2_do_setattr()`, `jffs2_setattr()`, `jffs2_statfs()`, `jffs2_evict_inode()`, `jffs2_iget()`, `jffs2_dirty_inode()`, `jffs2_do_remount_fs()`, `jffs2_new_inode()`, `jffs2_do_fill_super()`, `jffs2_gc_fetch_inode()`, `jffs2_gc_release_inode()`, `jffs2_flash_setup()`, and `jffs2_flash_cleanup()`.

## Control Flow
Setattr writes a fresh metadata node, preserving symlink targets or device numbers when needed, handles truncate/extend as metadata or hole nodes, updates VFS inode fields, and obsoletes old metadata. `jffs2_iget()` initializes in-core inode info by reading raw inode state, then installs operation tables by file type. Superblock fill rejects unsupported MTD types, aligns flash size, initializes flash-specific write-buffer/OOB handling, allocates inode-cache hash tables, mounts/scans the filesystem, obtains root inode, initializes superblock fields, and starts GC when writable. Remount stops/flushes/restarts GC based on read-only state.

## State And Persistence Behavior
Persistent state includes metadata raw inode nodes for attribute changes and new inode allocation. In-core state includes VFS inode fields, inode-cache hash table, eraseblock array, root dentry, mount options, flash geometry, GC thread state, and write-buffer setup.

## Dependencies And Integration Points
This file integrates VFS, fs_context, MTD geometry, ACL/security helpers, build/scan (`jffs2_do_mount_fs()`), readinode, write, GC background control, xattr/summary subsystems, and flash-specific setup for NAND, DataFlash, NOR write-buffer, and UBI volumes.

## Risks And Test Signals
Risk lies in error unwinding during mount, setattr preserving special-file payloads, truncate ordering without holding `f->sem` during `truncate_setsize()`, and GC fetching unlinked inodes without resurrecting deleted ones. Tests should cover mount failures at each allocation/setup step, read-only remounts, dirty inode metadata sync, symlink/device chmod/chown/truncate, root inode failures, NAND/DataFlash/UBI setups, and GC against linked and unlinked inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/gc.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/gc.c

## Purpose
`gc.c` implements one-pass JFFS2 garbage collection. It checks unchecked inodes, chooses victim eraseblocks, copies or rewrites live nodes, removes obsolete deletion dirents when safe, and schedules fully dirty blocks for erasure.

## Important APIs, Types, And Functions
The public API is `jffs2_garbage_collect_pass()`. Internal helpers include `jffs2_find_gc_block()`, `jffs2_garbage_collect_live()`, `jffs2_garbage_collect_pristine()`, `jffs2_garbage_collect_metadata()`, `jffs2_garbage_collect_dirent()`, `jffs2_garbage_collect_deletion_dirent()`, `jffs2_garbage_collect_hole()`, and `jffs2_garbage_collect_dnode()`.

## Control Flow
Each pass locks `alloc_sem`. If unchecked space remains, it walks inode-cache buckets, runs CRC checks on one unchecked inode, and returns. Otherwise it erases pending/completed blocks if possible, selects a GC block by weighted lists, skips obsolete refs, resolves the owning inode/xattr, and chooses a fast pristine copy or a slow rewrite path. Live dnodes may be merged to page boundaries, read through page cache, recompressed, and written as new raw inode nodes. When a GC block has no used bytes left, it moves to `erase_pending_list`.

## State And Persistence Behavior
GC persists replacement raw inode/dirent nodes or copied raw bytes, then marks old refs obsolete. It mutates `c->gcblock`, eraseblock list membership, node refs, inode-cache states, fragment trees, dirent lists, metadata pointers, compression statistics, and erase scheduling counters.

## Dependencies And Integration Points
It depends on inode-cache state from `nodelist.h`, MTD flash read/write helpers, CRC32, page cache, compression APIs, xattr GC hooks, reservation functions, erase scheduling, and VFS inode fetch/release from `fs.c`.

## Risks And Test Signals
GC is concurrency-sensitive: it drops locks when waiting for inode reads, must not race final `iput()` of unlinked inodes, and must avoid page-cache deadlocks with writes. Deletion dirents are only discardable on media that can mark obsolete nodes or after scanning older matching dirents. Tests should include unchecked CRC progress, GC under ENOSPC, corrupt pristine CRC fallback, hole-node rewrite, page merge behavior, deletion dirent retention on NAND, xattr nodes, unlinked open files, and repeated passes making measurable dirty-space progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/ioctl.c

## Purpose
`ioctl.c` provides the JFFS2 file/directory ioctl hook. In this source snapshot it is a placeholder for future attribute/compression controls and intentionally supports no commands.

## Important APIs, Types, And Functions
The only function is `jffs2_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)`, referenced by both regular file and directory file operation tables.

## Control Flow
Every ioctl call returns `-ENOTTY`, indicating the command is inappropriate/unsupported for the device or filesystem object. There is no command dispatch and no argument access.

## State And Persistence Behavior
No in-core or on-flash JFFS2 state is read or modified. The comment notes possible future `lsattr.jffs2`/`chattr.jffs2` support, including compression settings, but the implementation currently has no persistence behavior.

## Dependencies And Integration Points
It depends only on `linux/fs.h` and `nodelist.h` for declaration context. It integrates through `.unlocked_ioctl = jffs2_ioctl` in `file.c` and `dir.c`.

## Risks And Test Signals
The main compatibility signal is that all ioctls consistently fail with `ENOTTY`; user-space tools must not assume ext-style attribute support. Tests should call arbitrary ioctls on files and directories and verify no state changes, no user-pointer dereferences, and the exact error code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_i.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_i.h

## Purpose
`jffs2_fs_i.h` defines `struct jffs2_inode_info`, the per-inode private state embedded in each VFS inode. It is the central in-core representation for JFFS2 file data layout, directory entries, metadata nodes, symlink targets, inode-cache linkage, and compression preference.

## Important APIs, Types, And Functions
The header defines one type: `struct jffs2_inode_info`. Key fields are `sem`, `highest_version`, `fragtree`, `metadata`, `dents`, `target`, `inocache`, `flags`, `usercompr`, and embedded `vfs_inode`.

## Control Flow
The structure is initialized by `jffs2_init_inode_info()` and populated by `jffs2_do_read_inode()` or `jffs2_new_inode()`. File reads traverse `fragtree`; writes and GC insert or replace fragments; directory operations scan and update `dents`; setattr and GC replace `metadata`; symlink creation and iget set `target`/`i_link`.

## State And Persistence Behavior
This is volatile state reconstructed from raw flash nodes. `highest_version` guides new node versions that become persistent, `fragtree` maps logical file offsets to raw nodes, `metadata` carries non-data or special-file nodes, and `usercompr` can influence future node compression metadata.

## Dependencies And Integration Points
It depends on rbtree, POSIX ACL, mutex, and VFS inode definitions. It is included by compression, nodelist, read/write, dir, fs, GC, and debug code.

## Risks And Test Signals
The private `sem` exists because using only `inode->i_rwsem` would deadlock with GC. Incorrect lock ordering or stale fragment/metadata pointers can corrupt reads and GC. Tests should cover concurrent read/write/GC on the same inode, clear/evict while refs remain, symlink target lifetime, directory dent replacement, and version monotonicity after remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_sb.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_sb.h

## Purpose
`jffs2_fs_sb.h` defines mount options and `struct jffs2_sb_info`, the filesystem-wide JFFS2 control structure. It tracks MTD geometry, space accounting, eraseblock lists, GC state, inode caches, write-buffer state, xattr state, summaries, and OS-private superblock linkage.

## Important APIs, Types, And Functions
Important definitions are `JFFS2_SB_FLAG_RO`, `JFFS2_SB_FLAG_SCANNING`, `JFFS2_SB_FLAG_BUILDING`, `struct jffs2_mount_opts`, and `struct jffs2_sb_info`. The superblock fields include `mtd`, size counters, reservation thresholds, `blocks`, `nextblock`, `gcblock`, all eraseblock lists, `erase_completion_lock`, `alloc_sem`, inode-cache hash state, `erase_free_sem`, write-buffer fields under `CONFIG_JFFS2_FS_WRITEBUFFER`, `summary`, `mount_opts`, and xattr indexes.

## Control Flow
`jffs2_do_fill_super()` initializes geometry, lists, hash size, flash setup, mount scan, and root inode. Allocation, write, erase, and GC paths update counters and move `jffs2_eraseblock` objects through the lists declared here. Mount options override compression behavior and reserved-pool sizing.

## State And Persistence Behavior
The structure is volatile but mirrors persistent flash state: used/dirty/free/unchecked/bad sizes are derived from scan and maintained as nodes are written, obsoleted, erased, and marked bad. Write-buffer fields hold pending bytes not yet durable on NAND-like media.

## Dependencies And Integration Points
It depends on Linux locks, workqueues, timers, wait queues, lists, and rwsems. Almost every JFFS2 subsystem receives a `struct jffs2_sb_info *c`, making this the primary integration object.

## Risks And Test Signals
Space accounting and list membership invariants are critical; drift can cause ENOSPC loops, unsafe erases, or data loss. Tests should validate mount scan accounting, reservation thresholds, GC transitions across every block list, remount and write-buffer flushing, xattr memory accounting, and compression mount-option overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/malloc.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/malloc.c

## Purpose
`malloc.c` centralizes allocation and freeing of JFFS2's frequent in-core objects using slab caches and targeted kmalloc/vmalloc helpers. It covers full dnodes, raw dirents/inodes, temporary dnode info, raw node ref blocks, node fragments, inode caches, and optional xattr objects.

## Important APIs, Types, And Functions
Public functions include `jffs2_create_slab_caches()`, `jffs2_destroy_slab_caches()`, `jffs2_alloc/free_full_dirent()`, `jffs2_alloc/free_full_dnode()`, `jffs2_alloc/free_raw_dirent()`, `jffs2_alloc/free_raw_inode()`, `jffs2_alloc/free_tmp_dnode_info()`, `jffs2_prealloc_raw_node_refs()`, `jffs2_free_refblock()`, `jffs2_alloc/free_node_frag()`, `jffs2_alloc/free_inode_cache()`, and optional xattr alloc/free helpers.

## Control Flow
Module initialization creates all caches, unwinding through `jffs2_destroy_slab_caches()` on failure. Simple alloc/free wrappers call the appropriate cache or kmalloc and emit memory debug traces. Raw-node refs are allocated in blocks of `REFS_PER_BLOCK + 1`, initialized with empty sentinels and a link sentinel. `jffs2_prealloc_raw_node_refs()` ensures an eraseblock has enough empty ref slots before writing nodes.

## State And Persistence Behavior
The file manages only volatile memory, but allocation success is prerequisite for representing persistent raw flash nodes and inode mappings. `jeb->allocated_refs` records reserved ref capacity consumed by later node-linking.

## Dependencies And Integration Points
It depends on kernel slab APIs, `nodelist.h`, debug memory macros, and optional xattr structures. Allocation wrappers are used across scan, readinode, write, dir, erase, and GC code.

## Risks And Test Signals
Partial cache creation must unwind correctly. Raw-ref preallocation must maintain sentinel/link structure or node traversal and erase cleanup break. Tests should inject allocation failures for each cache/object type, stress many node refs per eraseblock, verify no xattr class initialization regressions, and run debug memory tracing during mount/write/GC/unmount cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodelist.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/nodelist.c

## Purpose
`nodelist.c` implements core in-core node bookkeeping: directory entry replacement, fragment-tree mutation, inode-cache hash operations, raw-node-ref linking/freeing, dirty-space scanning, and raw-node total-length calculation. It is the main consistency layer between append-only flash nodes and current file/directory state.

## Important APIs, Types, And Functions
Key public functions are `jffs2_add_fd_to_list()`, `jffs2_truncate_fragtree()`, `jffs2_add_full_dnode_to_inode()`, `jffs2_set_inocache_state()`, `jffs2_get_ino_cache()`, `jffs2_add_ino_cache()`, `jffs2_del_ino_cache()`, `jffs2_free_ino_caches()`, `jffs2_free_raw_node_refs()`, `jffs2_lookup_node_frag()`, `jffs2_kill_fragtree()`, `jffs2_link_node_ref()`, `jffs2_scan_dirty_space()`, and `__jffs2_ref_totlen()`.

## Control Flow
Dirents are kept sorted by name hash; duplicate names are resolved by version, with obsolete raw nodes marked dirty. Fragment insertion handles non-overlap, holes, partial overlap, splitting, replacement, and total obsoletion, updating raw-ref flags from pristine to normal when GC must inspect shared pages. Inode-cache helpers maintain sorted per-bucket lists under `inocache_lock`. Raw-node refs are appended in physical order to eraseblock ref blocks and linked into inode caches.

## State And Persistence Behavior
This file mutates volatile state that mirrors persistent nodes: `f->dents`, `f->fragtree`, `fn->frags`, inode-cache lists/states, eraseblock `first_node`/`last_node`, node ref flags, and superblock/eraseblock used/dirty/free/unchecked counters. Marking obsolete changes JFFS2's logical persistence by invalidating older flash nodes.

## Dependencies And Integration Points
It depends on rbtrees, MTD geometry macros, CRC-related structures, debug checks, allocation wrappers from `malloc.c`, and obsolete marking/reservation functions from nodemgmt/write code. Readinode, write, dir, fs, erase, and GC all rely on these invariants.

## Risks And Test Signals
Fragment overlap logic is intricate and can lose data if split/replace cases mishandle sizes or ref counts. Raw-node refs must remain physically ordered for `ref_totlen()`. Tests should cover random overlapping writes/truncates, sparse holes, same-page node merging flags, dirent version replacement/deletion markers, inode-cache add/delete races, eraseblock ref-block chaining, and accounting sanity under scan and live writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodelist.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/nodelist.h

## Purpose
`nodelist.h` defines the central JFFS2 in-core data structures, endian conversion helpers, node/ref flags, allocation constants, fragment-tree helpers, and cross-file function prototypes. It is the shared contract for scan, readinode, write, GC, erase, compression, xattr, and debug subsystems.

## Important APIs, Types, And Functions
Important types include `jffs2_raw_node_ref`, `jffs2_inode_cache`, `jffs2_full_dnode`, `jffs2_tmp_dnode_info`, `jffs2_readinode_info`, `jffs2_full_dirent`, `jffs2_node_frag`, and `jffs2_eraseblock`. Important macros include endian wrappers, `REF_UNCHECKED`, `REF_OBSOLETE`, `REF_PRISTINE`, `REF_NORMAL`, `ref_flags()`, `ref_offset()`, `dirent_node_state()`, `ALLOC_*`, `VERYDIRTY()`, `ISDIRTY()`, and `PAD()`. Inline helpers cover ref traversal, inode-cache recovery from raw refs, device encoding, and rbtree navigation.

## Control Flow
The header's prototypes define major subsystem boundaries: node-list mutation, node management reservations, writes, readinode, allocation, GC, read, scan, build, erase, and write-buffer operations. Raw-node refs chain physically through eraseblocks and logically through inode/xattr caches; fragment rbtrees map current file ranges to full dnodes or holes.

## State And Persistence Behavior
These structures are volatile reconstructions of persistent raw flash nodes. Ref flags encode whether on-flash nodes are unchecked, obsolete, pristine, or normal. Eraseblock accounting fields drive GC and allocation decisions; inode-cache state controls mount checking, read-inode races, GC exclusion, and deletion lifetime.

## Dependencies And Integration Points
The header includes OS abstraction (`os-linux.h` or `os-ecos.h`), superblock/inode private headers, xattr, ACL, summary, Linux VFS, rbtrees, and JFFS2 raw format definitions. It is included by nearly all files in this subset.

## Risks And Test Signals
Because this header defines shared invariants, small changes can break many subsystems. Risks include endian conversion mismatch, ref flag misuse in low flash-offset bits, inode-cache terminal-pointer assumptions, rbtree macro misuse on NULL, and eraseblock accounting drift. Tests should include cross-endian image compatibility, mount scan/read/write/GC cycles, xattr-enabled builds, NAND write-buffer builds, raw-node ref traversal over chained blocks, and debug sanity/paranoia configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/nodelist.h -->
