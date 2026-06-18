# Group Research: group_1009_linux_stable_sources_os_linux_linux_stable_fs_jffs2_compr_c_sources_3ed21b30ed25

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable/fs/jffs2/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr.c

## Role

Central JFFS2 compression dispatcher. It owns the global compressor registry, selects compression algorithms according to global or mount override policy, handles decompression dispatch, tracks simple compressor statistics, and initializes/exits the built-in compressor modules.

## Key Functions

- `jffs2_compress()` is the main write-path compression API.
  - Honors mount-level compression override when present.
  - Supports modes: none, priority, best size, favour LZO, force LZO, and force zlib.
  - Falls back to `JFFS2_COMPR_NONE` by pointing output at the original input buffer when no compressor produces a smaller result.
- `jffs2_selected_compress()` tries a specific compressor type or the first suitable registered compressor in priority order.
- `jffs2_is_best_compression()` compares compressor results for size-based and LZO-favouring modes.
- `jffs2_decompress()` handles `JFFS2_COMPR_NONE`, `JFFS2_COMPR_ZERO`, and registered decompressor callbacks. It masks legacy bad `usercompr` bits for old zlib-era data.
- `jffs2_register_compressor()` inserts compressors in descending priority order and initializes runtime counters/buffers.
- `jffs2_unregister_compressor()` refuses unregister while the compressor `usecount` is nonzero.
- `jffs2_free_comprbuf()` frees compression output only when it is not the original input buffer.
- `jffs2_compressors_init()` registers zlib, rtime, rubinmips, dynrubin, and lzo, then chooses the default compile-time compression mode.
- `jffs2_compressors_exit()` unregisters the compressors in reverse-ish module order.

## Synchronization and State

- `jffs2_compressor_list_lock` protects the compressor list, per-compressor `usecount`, temporary size-mode buffers, and stats updates.
- Compression callbacks are invoked outside the list spinlock after incrementing `usecount`.
- Size-based modes reuse per-compressor `compr_buf` allocations and detach the winning buffer from the compressor object.

## Research Notes

The file separates policy from compressor implementation. Modern compressors such as zlib and LZO register normally; legacy Rubin compressors can remain present for decompression compatibility. The fallback path is explicit: uncompressed data is represented by returning `JFFS2_COMPR_NONE` and using the caller’s original buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr.h

## Role

Private compression subsystem header for JFFS2. It defines compressor priorities, compression modes, the compressor registration structure, dispatcher APIs, and conditional module init/exit declarations.

## Key Definitions

- Compressor priorities:
  - Rubin MIPS: 10
  - Dynamic Rubin: 20
  - LZARI: 30
  - rtime: 50
  - zlib: 60
  - LZO: 80
- Rubin compressors are marked disabled for compression by default and used only for decompression.
- Compression modes:
  - `JFFS2_COMPR_MODE_NONE`
  - `JFFS2_COMPR_MODE_PRIORITY`
  - `JFFS2_COMPR_MODE_SIZE`
  - `JFFS2_COMPR_MODE_FAVOURLZO`
  - `JFFS2_COMPR_MODE_FORCELZO`
  - `JFFS2_COMPR_MODE_FORCEZLIB`
- `FAVOUR_LZO_PERCENT` sets the LZO preference threshold at 80%.

## Main Structure

`struct jffs2_compressor` carries:

- list linkage and priority;
- human-readable name and on-flash compression ID;
- `compress` and `decompress` callbacks;
- runtime `usecount` and disabled flag;
- size-mode scratch buffer and buffer size;
- compression/decompression statistics.

## API Surface

- Compressor registry: `jffs2_register_compressor()`, `jffs2_unregister_compressor()`.
- Compressor subsystem lifecycle: `jffs2_compressors_init()`, `jffs2_compressors_exit()`.
- Data APIs: `jffs2_compress()`, `jffs2_decompress()`, `jffs2_free_comprbuf()`.
- Conditional init/exit declarations for Rubin, rtime, zlib, and LZO based on Kconfig.

## Research Notes

This header is the contract between compressor implementations and the JFFS2 write/read paths. Compression identity is stored in raw inode nodes, so compatibility depends on keeping decompressor registration for historical formats even when those compressors are no longer preferred for new writes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_lzo.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_lzo.c

## Role

Implements the JFFS2 LZO compressor backend using the kernel LZO library.

## Key Functions

- `alloc_workspace()` allocates:
  - `lzo_mem` sized for `LZO1X_MEM_COMPRESS`;
  - `lzo_compress_buf` sized for worst-case compression of one page.
- `free_workspace()` releases both vmalloc-backed buffers.
- `jffs2_lzo_compress()` compresses through `lzo1x_1_compress()`, verifies the compressed output fits the requested destination length, then copies into the caller buffer.
- `jffs2_lzo_decompress()` uses `lzo1x_decompress_safe()` and rejects output length mismatches.
- `jffs2_lzo_init()` allocates workspaces and registers `jffs2_lzo_comp`.
- `jffs2_lzo_exit()` unregisters the compressor and frees workspaces.

## Synchronization

- `deflate_mutex` serializes shared LZO compression workspace use.

## Compressor Registration

`jffs2_lzo_comp` registers:

- priority `JFFS2_LZO_PRIORITY`;
- name `lzo`;
- compression ID `JFFS2_COMPR_LZO`;
- active compression and decompression callbacks;
- `disabled = 0`.

## Research Notes

LZO is designed here as the fast, high-priority compressor. The implementation uses global work buffers rather than per-call allocation, so compression is serialized while decompression has no shared mutable workspace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_rtime.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_rtime.c

## Role

Implements the JFFS2 rtime compressor, a simple byte-oriented LZ77-like scheme based on last occurrences of each byte value.

## Algorithm

- Maintains `positions[256]`, the last output/source position for each byte value.
- Compression emits pairs:
  - a literal byte;
  - a one-byte repeat length copied from the previous occurrence of that literal’s byte value.
- Runs are capped at 255 bytes.
- Compression fails if output is not smaller than the amount of input consumed.
- Decompression reconstructs output with the same positions table and handles overlapping copies byte-by-byte.

## Key Functions

- `jffs2_rtime_compress()` compresses until source is exhausted or destination space runs out.
- `jffs2_rtime_decompress()` expands literal/repeat pairs and returns an error if a repeat would exceed destination length.
- `jffs2_rtime_init()` registers the compressor.
- `jffs2_rtime_exit()` unregisters it.

## Compressor Registration

`jffs2_rtime_comp` registers:

- priority `JFFS2_RTIME_PRIORITY`;
- name `rtime`;
- compression ID `JFFS2_COMPR_RTIME`;
- compression and decompression callbacks;
- disabled status controlled by `JFFS2_RTIME_DISABLED`.

## Research Notes

This compressor is deliberately simple and byte-aligned. It does not use bit packing or external workspace, making it small and predictable, but generally less powerful than zlib or LZO.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_rtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_rubin.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_rubin.c

## Role

Implements the historical Rubin arithmetic-style compressors/decompressors used by JFFS2, including fixed MIPS probabilities and dynamic Rubin probabilities.

## Core Structures

- `struct pushpull` tracks bitstream buffer, bit offset, length, and reserved trailer space.
- `struct rubin_state` stores coding interval state (`p`, `q`, `rec_q`), bit counters, bit divider, per-bit probabilities, and the bitstream cursor.

## Encoding and Decoding

- `pushbit()` and `pullbit()` write/read single bits.
- `init_rubin()`, `encode()`, and `end_rubin()` implement the encoder state machine.
- `init_decode()`, `__do_decode()`, and `decode()` implement decoder reconstruction.
- `out_byte()` encodes one byte least-significant-bit first using per-bit probabilities.
- `in_byte()` decodes one byte with the same bit order.
- `rubin_do_compress()` writes encoded bytes and rejects output that is not smaller than input.
- `rubin_do_decompress()` reconstructs bytes until the requested output length is produced.

## Compressor Variants

- Rubin MIPS:
  - Uses `BIT_DIVIDER_MIPS` and `bits_mips`.
  - Compression function is compiled out.
  - Registered with decompression support.
- Dynamic Rubin:
  - Builds an input histogram.
  - Converts per-bit occurrence counts into 8 probability bytes stored at the start of compressed data.
  - Compresses with divider 256 and rejects non-beneficial output.

## Registration Details

The two compressor structs intentionally use historical on-flash compression IDs:

- `jffs2_rubinmips_comp` name `rubinmips`, compression ID `JFFS2_COMPR_DYNRUBIN`, no compression callback, decompression callback present.
- `jffs2_dynrubin_comp` name `dynrubin`, compression ID `JFFS2_COMPR_RUBINMIPS`, compression callback present but disabled by default, decompression callback present.

## Research Notes

This is compatibility code for older JFFS2 images. The header disables Rubin compressors for new compression, but decompression remains available so existing flash data can still be read.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_rubin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_zlib.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_zlib.c

## Role

Implements the JFFS2 zlib compressor backend using kernel zlib workspaces and stream APIs.

## Key Functions

- `alloc_workspaces()` vmallocs deflate and inflate workspaces.
- `free_workspaces()` releases those workspaces.
- `jffs2_zlib_compress()`:
  - initializes deflate at level 3;
  - reserves `STREAM_END_SPACE` bytes for final stream closure;
  - uses partial flushes while consuming input;
  - finishes with `Z_FINISH`;
  - rejects output that is not smaller than input.
- `jffs2_zlib_decompress()`:
  - initializes inflate;
  - detects normal deflate streams without preset dictionary and skips Adler-32 verification by using negative `wbits`;
  - inflates until stream end and logs non-stream-end returns.
- `jffs2_zlib_init()` allocates workspaces and registers the compressor.
- `jffs2_zlib_exit()` unregisters and frees workspaces.

## Synchronization

- `deflate_mutex` serializes access to the global deflate stream.
- `inflate_mutex` serializes access to the global inflate stream.

## Compressor Registration

`jffs2_zlib_comp` registers:

- priority `JFFS2_ZLIB_PRIORITY`;
- name `zlib`;
- compression ID `JFFS2_COMPR_ZLIB`;
- compression and decompression callbacks;
- disabled state controlled by `JFFS2_ZLIB_DISABLED`.

## Research Notes

zlib is the traditional higher-compression backend. The implementation uses shared global stream objects, so both compression and decompression are serialized separately.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/compr_zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/debug.c

## Role

Implements JFFS2 debug-time sanity checks, paranoia checks, and dump helpers for eraseblock accounting, inode fragment trees, raw node references, buffers, and on-flash node contents.

## Sanity Checks

- `__jffs2_dbg_acct_sanity_check_nolock()` verifies:
  - per-eraseblock accounting sums to `sector_size`;
  - superblock space accounting sums to `flash_size`.
- `__jffs2_dbg_acct_sanity_check()` wraps the nolock check with `erase_completion_lock`.

## Paranoia Checks

- `__jffs2_dbg_fragtree_paranoia_check*()` validates invariants around `REF_PRISTINE` nodes:
  - pristine nodes should not have multiple frags;
  - adjacent same-page non-hole frags require normal GC handling.
- `__jffs2_dbg_prewrite_paranoia_check()` reads flash before a write and BUGs if the target area is not erased.
- `__jffs2_dbg_superblock_counts()` recounts every block list and verifies aggregate counters and block count membership.
- `__jffs2_dbg_acct_paranoia_check*()` walks raw node refs in an eraseblock, recalculates used/unchecked/dirty sizes, validates last-node linkage, and optionally triggers full superblock recounting.

## Dump Helpers

- `__jffs2_dbg_dump_node_refs*()` prints raw node refs for an eraseblock.
- `__jffs2_dbg_dump_jeb*()` prints eraseblock accounting.
- `__jffs2_dbg_dump_block_lists*()` prints all major eraseblock lists and accounting totals.
- `__jffs2_dbg_dump_fragtree*()` prints the logical fragment tree for an inode and BUGs on holes in expected continuity.
- `__jffs2_dbg_dump_buffer()` hex-dumps a buffer at a flash offset.
- `__jffs2_dbg_dump_node()` reads and prints an on-flash inode or dirent node, validating common/header CRCs.

## Dependencies

Uses JFFS2 node list structures, MTD flash reads, CRC32, page sizing, and debug macros from `debug.h`.

## Research Notes

This file is compiled conditionally by debug feature macros. The lightweight accounting sanity path is always exposed through `JFFS2_DBG_SANITY_CHECKS`, while heavier paranoia and dump code only exists when debug options enable it.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/debug.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/debug.h

## Role

Defines JFFS2 debug configuration, message macros, subsystem-specific debug gates, and wrappers around sanity/paranoia/dump functions.

## Debug Configuration

- Defaults `CONFIG_JFFS2_FS_DEBUG` to 0 if unset.
- Debug level greater than 0 enables:
  - paranoia checks;
  - dumps;
  - readinode, fragtree, dentlist, noderef, inocache, summary, and fsbuild messages.
- Debug level greater than 1 enables deeper fragtree, readinode, and memory allocation messages.
- `JFFS2_DBG_SANITY_CHECKS` is always enabled for lightweight checks.

## Message Macros

- `jffs2_dbg(level, ...)` maps to `pr_debug()` when the configured level is high enough.
- `JFFS2_ERROR`, `JFFS2_WARNING`, `JFFS2_NOTICE`, and `JFFS2_DEBUG` include task PID and function context.
- Subsystem macros such as `dbg_fragtree()`, `dbg_noderef()`, and `dbg_memalloc()` either print or compile to `no_printk()`.

## Function Declarations

Declares implementation functions for:

- accounting sanity checks;
- fragment tree and accounting paranoia checks;
- prewrite erased-area validation;
- eraseblock, block-list, node-ref, fragment-tree, buffer, and node dumps.

## Wrapper Macros

- Paranoia wrappers compile to real function calls only with `JFFS2_DBG_PARANOIA_CHECKS`.
- Dump wrappers compile to real function calls only with `JFFS2_DBG_DUMPS`.
- Sanity wrappers compile to real function calls with `JFFS2_DBG_SANITY_CHECKS`.

## Research Notes

This header lets production builds keep core accounting checks while compiling out verbose diagnostics. It is included from `nodelist.h`, making debug macros broadly available across the JFFS2 implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/dir.c

## Role

Implements JFFS2 directory file operations and directory inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## VFS Operation Tables

- `jffs2_dir_operations` wires generic directory read, `jffs2_readdir`, ioctl, fsync, llseek, and file lease support.
- `jffs2_dir_inode_operations` wires create/lookup/link/unlink/symlink/mkdir/rmdir/mknod/rename plus ACL, setattr, and xattr listing hooks.

## Directory Lookup and Read

- `jffs2_lookup()` searches the inode-private sorted `dents` list by full-name hash, name length, name bytes, and highest version.
- `jffs2_readdir()` emits dot entries, then iterates the `dents` list, skipping deletion dirents with `ino == 0`.

## Creation Operations

- `jffs2_create()` allocates a raw inode, creates a JFFS2 inode, installs regular-file ops, and calls `jffs2_do_create()`.
- `jffs2_symlink()` writes a symlink raw inode containing the target path, caches the target in `f->target`, initializes security/ACLs, then writes a parent dirent.
- `jffs2_mkdir()` writes a metadata-only directory inode, sets initial link count, initializes security/ACLs, then writes a directory dirent and increments parent link count.
- `jffs2_mknod()` encodes device numbers for block/char special files, writes metadata inode data, initializes security/ACLs, then writes the dirent.

## Link and Removal Operations

- `jffs2_link()` rejects directory hard links, writes a new dirent via `jffs2_do_link()`, increments inode link accounting, and instantiates the dentry.
- `jffs2_unlink()` appends a deletion dirent through `jffs2_do_unlink()` and updates parent timestamps.
- `jffs2_rmdir()` first verifies no live child dirents remain, then unlinks and updates directory link counts.

## Rename

- Supports only default rename and `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Checks target directory emptiness when replacing a directory.
- Implements rename as link-new-name followed by unlink-old-name.
- Handles victim link count/inocache adjustments and parent link counts for moved directories.
- If unlink of the old name fails after link succeeds, it reports the failure, invalidates the new dentry, and leaves a hard-link-like result.

## Research Notes

The file reflects JFFS2’s log-structured design: namespace changes append new dirent nodes instead of rewriting directories in place. Several operations are two-stage inode-node plus dirent-node sequences, so error paths must treat partially created objects as normal deletion cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/erase.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/erase.c

## Role

Manages eraseblock erase lifecycle: starting erases, handling success/failure, verifying erased contents, writing clean markers, freeing raw node refs, and moving blocks among JFFS2 erase lists.

## Erase Flow

- `jffs2_erase_pending_blocks()` processes one or more blocks from:
  - `erase_complete_list`, by verifying and marking erased blocks;
  - `erase_pending_list`, by clearing accounting/node refs and starting an MTD erase.
- `jffs2_erase_block()` issues `mtd_erase()` for Linux or platform flash erase for eCos.
- `jffs2_erase_succeeded()` moves the block to `erase_complete_list`, triggers GC, and wakes waiters.
- `jffs2_erase_failed()` optionally updates NAND bad-block handling, retries if appropriate, or moves the block to `bad_list`.

## Node Ref Cleanup

- `jffs2_free_jeb_node_refs()` frees all raw node refs for an eraseblock.
- `jffs2_remove_node_refs_from_ino_list()` removes refs from their owning inode/xattr raw-node chain and releases inode/xattr caches when appropriate.

## Erase Verification and Clean Marker

- `jffs2_block_check_erase()` verifies a freshly erased block is all `0xff`.
  - Uses `mtd_point()` when possible for direct mapped access.
  - Falls back to page-sized reads.
  - Returns bad offsets for failure reporting.
- `jffs2_mark_erased_block()`:
  - verifies erase;
  - writes NAND OOB cleanmarker, in-band cleanmarker, or no marker depending on medium setup;
  - accounts cleanmarker refs when in-band;
  - moves the block to `free_list` and updates free/erasing counters.

## Synchronization

- `erase_free_sem` coordinates erase-list transitions and prevents ref freeing races.
- `erase_completion_lock` protects list membership and accounting counters.
- Waiters use `erase_wait`.

## Research Notes

This file is where the physical flash erase lifecycle meets JFFS2’s logical accounting. It carefully transitions blocks between dirty/erasing/complete/free/bad states and verifies erased media before reuse.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/file.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/file.c

## Role

Implements regular-file operations and address-space operations for JFFS2, including folio read, write begin/end, and fsync.

## VFS Tables

- `jffs2_file_operations` uses generic llseek/open/read/write, readonly mmap preparation, splice helpers, ioctl, fsync, and file lease support.
- `jffs2_file_inode_operations` wires ACL, setattr, and xattr listing hooks.
- `jffs2_file_address_operations` provides `read_folio`, `write_begin`, and `write_end`.

## Read Path

- `jffs2_do_readpage_nolock()` maps the folio locally and fills it via `jffs2_read_inode_range()`.
- `__jffs2_read_folio()` performs the read and unlocks the folio.
- `jffs2_read_folio()` wraps the read with the inode-private `f->sem`.

## Write Begin

- If writing beyond EOF, writes a zero-compressed hole node covering old EOF to new position.
- Adds the hole dnode to the inode fragment tree and obsoletes metadata-only node if needed.
- Locks `c->alloc_sem` while acquiring and reading the target folio to avoid GC/read deadlocks.
- Ensures the folio is uptodate before write completion.

## Write End

- Writes the changed range as a new JFFS2 raw inode node via `jffs2_write_inode_range()`.
- Expands the write to the whole page when the write reaches page end, reducing fragmentation for short append-heavy workloads.
- Updates inode size, block count, mtime, and ctime on extension.
- Marks the folio not uptodate if fewer bytes reached flash than were copied into cache.

## Fsync

`jffs2_fsync()` waits for dirty page-cache data, locks the inode, and triggers write-buffer GC flushing for the inode number.

## Research Notes

JFFS2 files are represented as a fragment tree of log nodes rather than block mappings. The file write path appends new inode nodes and updates in-memory fragments, while read reconstructs data ranges through `read_inode_range()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/fs.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/fs.c

## Role

Implements VFS-facing inode/superblock support: setattr, statfs, inode eviction/loading/creation, remount behavior, mount fill, GC inode access helpers, and flash-type setup/cleanup.

## Attribute Handling

- `jffs2_do_setattr()` writes a new metadata raw inode node for ownership, mode, time, and size changes.
- Special files and symlinks preserve their metadata payload:
  - device numbers are re-encoded;
  - symlink target is read from existing metadata node.
- File extension writes a zero-compressed hole node.
- Truncate-to-zero uses deletion allocation priority.
- Shrinking truncates the fragment tree under `f->sem`, then calls `truncate_setsize()` after releasing it.
- `jffs2_setattr()` uses `setattr_prepare()` and applies POSIX ACL chmod updates after mode changes.

## Inode Lifecycle

- `jffs2_iget()` reads an inode from raw nodes, fills VFS metadata, and installs operation tables by file type.
  - Symlinks use cached target.
  - Directories calculate link count from child directory dirents.
  - Device nodes read encoded device numbers from metadata.
- `jffs2_new_inode()` allocates a VFS inode and JFFS2 inode cache, handles setgid/default ACL behavior, calls `jffs2_do_new_inode()`, initializes timestamps and identity, and inserts it into the inode hash.
- `jffs2_evict_inode()` truncates page cache, clears the VFS inode, and clears JFFS2 inode-private state.
- `jffs2_dirty_inode()` converts datasync inode dirtiness into a JFFS2 metadata node rewrite.

## Superblock and Mount

- `jffs2_statfs()` reports flash-derived blocks and available space after reserved write blocks.
- `jffs2_do_remount_fs()` prevents remounting an internally read-only filesystem writable, flushes write buffers when transitioning, and starts/stops GC as needed.
- `jffs2_do_fill_super()`:
  - rejects unsupported MLC NAND;
  - rejects NAND/DataFlash when writebuffer support is absent;
  - aligns flash size to erase size;
  - rejects too-small media;
  - sets cleanmarker size and flash-specific setup;
  - allocates inode cache hash table;
  - initializes xattrs and mounts/scans the filesystem;
  - loads root inode and sets superblock limits/time range;
  - starts GC for writable mounts.

## GC Helpers

- `jffs2_gc_fetch_inode()` gets inodes for GC, using `ilookup()` for unlinked inodes to avoid resurrecting absent deleted inodes.
- `jffs2_gc_release_inode()` drops the VFS inode reference.
- `jffs2_flash_setup()` and `jffs2_flash_cleanup()` dispatch to NAND, DataFlash, NOR write-buffer, and UBI setup/cleanup hooks.

## Research Notes

This file bridges raw JFFS2 log metadata with Linux VFS inode semantics. It is also the main mount setup path, constructing the in-memory eraseblock/inocache world before exposing the root dentry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/gc.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/gc.c

## Role

Implements JFFS2 garbage collection. It selects eraseblocks, verifies unchecked inodes before GC, moves live nodes out of dirty blocks, preserves required deletion markers, rewrites data/metadata/dirent nodes, handles pristine copies, and triggers block erasure when a GC block becomes fully obsolete.

## GC Block Selection

`jffs2_find_gc_block()` chooses a block from lists with probabilistic weighting:

- `bad_used_list` if enough free blocks exist;
- `erasable_list`;
- `very_dirty_list`;
- `dirty_list`;
- `clean_list`;
- fallback dirty/very-dirty/erasable lists;
- flushes writebuffer if only `erasable_pending_wbuf_list` can progress.

It sets `c->gcblock`, initializes `gc_node`, and converts any `wasted_size` in a selected clean block into dirty accounting.

## Main Pass

`jffs2_garbage_collect_pass()` performs one unit of progress:

- Takes `alloc_sem`.
- If unchecked space remains, scans inode caches and invokes `jffs2_do_crccheck_inode()` before real GC.
- Processes pending erases when available.
- Selects or reuses `c->gcblock`.
- Skips obsolete refs and dispatches live node handling.
- Handles inode-less nodes by copying pristine unknown compatible nodes or marking non-pristine ones obsolete.
- Handles xattr raw nodes through xattr GC hooks when enabled.
- Coordinates inode-cache states so absent pristine nodes can be copied without instantiating VFS inodes, while non-pristine or in-core nodes go through normal inode fetch.
- Moves fully obsoleted GC blocks to `erase_pending_list`.

## Live Node Handling

`jffs2_garbage_collect_live()` locks the inode-private `f->sem`, verifies the raw node is still live in the selected GC block, then classifies it as:

- metadata dnode;
- data dnode via fragment tree lookup;
- live dirent;
- deletion dirent;
- unexpected raw node, which triggers debug dump/BUG if not obsolete.

## Pristine Copy Path

`jffs2_garbage_collect_pristine()` copies a `REF_PRISTINE` node intact when it fits:

- reserves GC space;
- reads the full raw node;
- validates common header CRC;
- validates inode node/data CRC or dirent node/name CRC for known node types;
- copies the bytes to a new physical location;
- links a new pristine node ref;
- marks the old raw ref obsolete.
- Returns `-EBADFD` when the node cannot be copied intact and should be handled by slower rewriting.

## Rewrite Paths

- `jffs2_garbage_collect_metadata()` rewrites metadata-only inode nodes, including symlink target or device metadata, and replaces `f->metadata`.
- `jffs2_garbage_collect_dirent()` writes a replacement dirent with a new version and adds it back to the directory list.
- `jffs2_garbage_collect_deletion_dirent()` drops obsolete deletion dirents when safe; on media that cannot mark obsolete nodes permanently, it scans old obsolete dirents to decide whether the deletion marker must be preserved.
- `jffs2_garbage_collect_hole()` writes replacement zero-compressed hole nodes, preserving version for partially overlapped hole nodes when required.
- `jffs2_garbage_collect_dnode()` reads the relevant page through page cache, optionally expands the rewrite range to merge adjacent dirty fragments, compresses data through `jffs2_compress()`, writes new dnodes, and updates the fragment tree.

## Concurrency Notes

- `alloc_sem` serializes allocation and GC.
- `erase_completion_lock` protects block/list/ref state.
- `inocache_lock` protects inode cache state transitions.
- `f->sem` protects per-inode metadata, dents, and fragment trees.
- The data-node GC path drops `f->sem` before acquiring folio locks to obey lock ordering.

## Research Notes

This is the core maintenance engine for the log-structured filesystem. Its behavior depends heavily on raw node ref state: pristine nodes can often be copied byte-for-byte, while normal/overlapped nodes must be reconstructed from inode state and page-cache data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/ioctl.c

## Role

Placeholder ioctl implementation for JFFS2 files and directories.

## Key Function

- `jffs2_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)` always returns `-ENOTTY`.

## Research Notes

The comment notes a future intent for `lsattr.jffs2`/`chattr.jffs2` support, including compression-related attributes. In this version, JFFS2 exposes no private ioctl commands through this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_i.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_i.h

## Role

Defines the JFFS2 private per-inode structure embedded in Linux `struct inode`.

## Main Structure

`struct jffs2_inode_info` contains:

- `sem`: JFFS2-specific inode mutex used instead of `i_rwsem` to avoid GC deadlocks.
- `highest_version`: highest raw dnode version for this inode.
- `fragtree`: red-black tree mapping logical file ranges to `jffs2_node_frag` records.
- `metadata`: metadata-only dnode not referenced by fragments, used for directories, symlinks, device nodes, and metadata updates.
- `dents`: linked list of directory entries for directory inodes.
- `target`: cached symlink target.
- `inocache`: always-resident inode cache entry.
- `flags`: inode flags.
- `usercompr`: user-selected compression byte.
- `vfs_inode`: embedded Linux inode.

## Research Notes

This structure is the in-core expanded form of a JFFS2 inode. The fragment tree is built only when the inode is instantiated, while the smaller inode cache remains available even when the VFS inode is absent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_sb.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_sb.h

## Role

Defines JFFS2 private superblock state and mount options.

## Mount Options

`struct jffs2_mount_opts` stores:

- compression override flag and selected compression mode;
- reserved-pool size flag and value, limiting non-root writes when free space drops below the pool.

## Superblock State

`struct jffs2_sb_info` contains:

- MTD device pointer.
- Highest inode and next inode-to-check counters.
- superblock flags: read-only, scanning, building.
- GC task pointer and start/exit completions.
- `alloc_sem`, protecting allocation, write ordering, and GC-critical fields.
- flash geometry and global accounting:
  - flash, sector, used, dirty, wasted, free, erasing, bad, unchecked sizes;
  - number of free and erasing blocks.
- reserved-block thresholds for writes, deletions, GC triggering, bad-block GC, and GC merging.
- eraseblock array, current write block, and current GC block.
- block lists:
  - clean, very dirty, dirty, erasable, erasable pending writebuffer, erasing, erase checking, erase pending, erase complete, free, bad, and bad-used.
- erase locking and wait queue.
- inode cache hash table, lock, and wait queue.
- `erase_free_sem` for safe erase/ref freeing coordination.
- write-buffer fields when configured:
  - write buffer, offset/length, dirty inode list, rwsem, delayed work, OOB buffer/space, optional verify buffer.
- summary subsystem pointer.
- xattr indexes/lists/semaphores/counters when configured.
- `os_priv` back pointer to the OS superblock.

## Research Notes

This header shows that JFFS2’s superblock is primarily a flash-space and GC ledger. Most high-level operations ultimately update these counters and lists through allocation, node-ref, erase, or GC paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/malloc.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/malloc.c

## Role

Owns JFFS2 object allocation caches and typed allocation/free wrappers for core in-memory and raw-node helper structures.

## Slab Cache Lifecycle

- `jffs2_create_slab_caches()` creates caches for:
  - `jffs2_full_dnode`;
  - `jffs2_raw_dirent`;
  - `jffs2_raw_inode`;
  - `jffs2_tmp_dnode_info`;
  - raw node ref blocks;
  - `jffs2_node_frag`;
  - `jffs2_inode_cache`;
  - xattr datum/ref objects when configured.
- `jffs2_destroy_slab_caches()` destroys all created caches.

## Allocation Wrappers

Provides typed alloc/free functions for:

- full dirents, with variable name tail allocated by `kmalloc`;
- full dnodes;
- raw dirents;
- raw inodes;
- temporary dnode info;
- raw node ref blocks;
- node fragments;
- inode caches;
- xattr datum/ref structures when enabled.

## Raw Node Ref Blocks

- `jffs2_alloc_refblock()` allocates a block of raw node refs.
- Initializes usable slots as `REF_EMPTY_NODE`.
- Sets the final slot as `REF_LINK_NODE`, used to link to another ref block.
- `jffs2_prealloc_raw_node_refs()` walks or extends the refblock chain for an eraseblock and reserves a requested number of refs in `jeb->allocated_refs`.

## Research Notes

The file centralizes memory ownership for JFFS2’s small, high-churn metadata objects. Raw node refs are allocated in small linked blocks rather than one object at a time to reduce overhead while supporting per-eraseblock chains.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodelist.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/nodelist.c

## Role

Implements core in-memory JFFS2 node-list operations: directory entry list replacement, fragment tree updates/truncation, inode cache hash management, raw node ref linking/freeing, dirty-space scanning, and raw ref length calculation.

## Directory Entries

- `jffs2_add_fd_to_list()` keeps the directory entry list sorted by name hash.
- Replaces older entries with newer same-name versions.
- Marks replaced raw nodes obsolete when possible and frees the old full dirent.

## Fragment Tree

- `jffs2_truncate_fragtree()` removes or shrinks fragments beyond a new size and marks affected nodes obsolete/normal.
- `jffs2_obsolete_node_frag()` decrements backing dnode fragment counts and marks nodes obsolete when their final fragment disappears.
- `jffs2_add_frag_to_fragtree()` inserts a new data fragment into the red-black tree, splitting or obsoleting overlapping fragments and inserting hole fragments when needed.
- `jffs2_add_full_dnode_to_inode()` wraps a full dnode in a fragment, inserts it, and marks page-sharing nodes `REF_NORMAL` for safer GC.
- `jffs2_lookup_node_frag()` finds the fragment covering an offset or the closest preceding fragment.
- `jffs2_kill_fragtree()` frees all fragments and optionally marks backing nodes obsolete.

## Inode Cache Management

- `jffs2_set_inocache_state()` updates inode-cache state and wakes waiters.
- `jffs2_get_ino_cache()` looks up an inode cache in the sorted hash bucket.
- `jffs2_add_ino_cache()` assigns an inode number if needed and inserts into the sorted hash chain.
- `jffs2_del_ino_cache()` removes a cache and frees it unless it is in reading/clearing transition.
- `jffs2_free_ino_caches()` frees all inode caches and xattr associations.

## Raw Node Refs

- `jffs2_free_raw_node_refs()` frees all refblocks for all eraseblocks.
- `jffs2_link_node_ref()` consumes a preallocated ref, attaches it to an eraseblock and optional inode cache, validates physical contiguity, and updates used/unchecked/dirty/free accounting based on ref flags.
- `jffs2_scan_dirty_space()` accounts dirty space during mount scan and merges with the previous obsolete ref when possible.
- `__jffs2_ref_totlen()` calculates a raw ref’s total length from the next ref or eraseblock free boundary, with optional `TEST_TOTLEN` validation.

## Research Notes

This file enforces the logical map of current file contents. Overlapping log nodes are resolved by fragment-tree surgery, and obsolete/live status is mirrored into raw node ref flags so GC can later decide whether to copy, rewrite, or discard physical nodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodelist.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/nodelist.h

## Role

Primary private JFFS2 implementation header. It defines endian conversion helpers, raw-node reference structures, inode cache structures, fragment/dnode/dirent/eraseblock structures, allocation constants, helper macros, and cross-file function prototypes.

## Endian and Mode Helpers

- Selects native, big-endian, or little-endian JFFS2 conversion macros.
- Converts 16-bit, 32-bit, and mode fields between CPU and JFFS2 raw wrapper types.
- Includes OS-specific glue through `os-linux.h` or `os-ecos.h`.

## Raw Node References

- `struct jffs2_raw_node_ref` stores physical flash offset plus low-bit status flags and the next-in-inode chain pointer.
- Low two bits of `flash_offset` encode:
  - `REF_UNCHECKED`;
  - `REF_OBSOLETE`;
  - `REF_PRISTINE`;
  - `REF_NORMAL`.
- `REF_LINK_NODE` and `REF_EMPTY_NODE` implement linked raw-ref blocks.
- `ref_next()`, `ref_flags()`, `ref_offset()`, `ref_obsolete()`, and `mark_ref_normal()` are central raw-ref helpers.
- `dirent_node_state()` treats live dirents as pristine and deletion dirents as normal.

## Inode and Node Structures

- `struct jffs2_inode_cache` is the always-resident per-inode summary:
  - scan-time dirents;
  - raw node list;
  - class/state/flags;
  - inode number;
  - xattr association;
  - parent inode or link count.
- Inode states include unchecked, checking, present, checked absent, GC, reading, and clearing.
- `struct jffs2_full_dnode` represents instantiated data/metadata nodes.
- `struct jffs2_tmp_dnode_info` supports read-inode reconstruction.
- `struct jffs2_readinode_info` groups read-inode temporary state.
- `struct jffs2_full_dirent` is an in-memory directory entry with variable-length name.
- `struct jffs2_node_frag` maps a logical file range to a full dnode or hole.
- `struct jffs2_eraseblock` tracks per-block list linkage, accounting, raw refs, and GC cursor.

## Constants and Inline Helpers

- `JFFS2_MIN_NODE_HEADER` uses raw dirent size.
- `REFS_PER_BLOCK` targets raw ref blocks around 256 bytes.
- `write_ofs(c)` computes the next physical write offset in `nextblock`.
- Allocation priorities: normal, deletion, GC, no-retry.
- `VERYDIRTY()`, `ISDIRTY()`, and `PAD()` provide common accounting/alignment checks.
- `jffs2_encode_dev()` chooses old or new device encoding.
- Fragment and tmp-node red-black tree traversal macros wrap Linux rb helpers.

## Cross-File API Surface

Declares APIs from:

- `nodelist.c`: dirent lists, inode cache management, fragment trees, raw refs.
- `nodemgmt.c`: reservation, physical refs, completion, obsolete marking.
- `write.c`: new inode, dnode/dirent writes, range writes, create/unlink/link.
- `readinode.c`: inode read, CRC check, inode clear.
- `malloc.c`: object allocators.
- `gc.c`: garbage collection pass.
- `read.c`: dnode/range/link reads.
- `scan.c`: flash scan and block classification.
- `build.c`: mount build.
- `erase.c`: erase pending blocks and ref freeing.
- `wbuf.c`: writebuffer operations when configured.

## Research Notes

This header is the internal contract for nearly all JFFS2 files. The most important design point is that raw node refs are tiny physical records, while full dnodes/fragments are built only for in-core inodes; this keeps mount-wide memory lower than storing every logical mapping eagerly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/nodelist.h -->