# Group Research: group_331_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer2_zlib_hammer_661e4733d13f

Scope: `Docs/research_subset_a.md`

All listed source files were read completely in manifest order. This grouped report preserves one marker-delimited section per source file for final splitting into source-tree-aligned reports.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.c

Source read: complete file, 1052 lines.

Purpose: This is the HAMMER2-local zlib inflate implementation, adapted for DragonFly kernel use. It initializes and tears down inflate state, decodes zlib/raw deflate streams, builds or references fixed Huffman tables, maintains the sliding output window, verifies Adler checksums, and exposes the usual zlib inflate entry points with `Z_PREFIX` name remapping through the included headers.

Key interfaces:
- `inflateInit2_()` allocates `struct inflate_state` with `kmalloc(..., C_ZLIB_BUFFER_INFLATE, M_INTWAIT)`, validates `ZLIB_VERSION` and `sizeof(z_stream)`, and delegates to `inflateReset2()`.
- `inflateResetKeep()`, `inflateReset()`, and `inflateReset2()` reset stream counters, wrap/window settings, code-table pointers, bit accumulator state, distance sanity, and dictionary flags.
- `inflatePrime()` injects bits into the input accumulator or clears it when called with negative bit count.
- `inflate()` is the main state machine for headers, block type dispatch, stored blocks, fixed blocks, dynamic code tables, literal/length/distance decoding, match copying, trailer verification, and return-code selection.
- `inflateEnd()` releases the optional sliding window and the inflate state with the same DragonFly malloc type.

Implementation notes:
- Only zlib wrapping is meaningfully implemented in the state machine despite enum support for gzip modes in the header; the header path checks the zlib CMF/FLG modulus, method, window size, optional dictionary id, and Adler trailer.
- `fixedtables()` normally includes `hammer2_zlib_inffixed.h`; when `BUILDFIXED` is enabled it generates fixed tables at first use, with comments warning about thread safety.
- `updatewindow()` lazily initializes the circular window only when needed and copies at most the last window-sized suffix of output.
- `inflate()` uses local register-style variables and macros (`LOAD`, `RESTORE`, `NEEDBITS`, `BITS`, `DROPBITS`, `BYTEBITS`) to minimize repeated stream/state memory accesses.
- Dynamic block handling reads `nlen`, `ndist`, and `ncode`, builds the code-length tree with `inflate_table(CODES, ...)`, expands repeat codes 16/17/18 into `state->lens`, then builds literal/length and distance decode tables.
- Fast path handoff to `inflate_fast(strm, out)` occurs when at least six input bytes and 258 output bytes are available.

Integration:
- Depends on `hammer2_zlib_zutil.h`, `hammer2_zlib_inftrees.h`, `hammer2_zlib_inflate.h`, `hammer2_zlib_inffast.h`, and `../hammer2.h`.
- Uses DragonFly `MALLOC_DECLARE`/`MALLOC_DEFINE` and `kmalloc`/`kfree` rather than the stock zlib allocator hooks.
- Consumes `adler32()`, `inflate_table()`, and the `code` layout defined in companion zlib files.

Risks and review notes:
- `updatewindow()` assumes `state->window` is already allocated before writing to it, but this file initializes `state->window` to `Z_NULL` and does not allocate it in `updatewindow()` before `zmemcpy()`. Stock zlib normally allocates the window when first needed; this HAMMER2 copy should be checked against its callers and local patches.
- The `inflate_state` enum includes gzip modes, but `inflate()` does not implement gzip header/trailer processing; callers expecting gzip wrapper support would fail or misinterpret data.
- `INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR` can synthesize zero bytes for invalid distances if enabled; default `state->sane = 1` rejects those streams.
- Error paths report string literals through `strm->msg`; kernel callers should not assume ownership.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.h

Source read: complete file, 113 lines.

Purpose: Internal inflate state definition for the HAMMER2-local zlib copy. It declares the inflate mode enum and the full persistent `struct inflate_state` used across repeated `inflate()` calls.

Key definitions:
- `inflate_mode` enumerates header, dictionary, deflate block, code decode, trailer, terminal, and error states. Gzip-specific states are present even though the local inflate implementation primarily handles zlib/raw deflate.
- `struct inflate_state` stores wrapper flags, dictionary status, checksum, output totals, sliding-window metadata, input bit accumulator, copy/match fields, current decode-table pointers, dynamic Huffman table build workspace, and diagnostic fields such as `back` and `was`.
- `lens[320]`, `work[288]`, and `codes[ENOUGH]` provide fixed-size scratch and decode-table storage for dynamic blocks.

Integration:
- Requires `code` and `ENOUGH` from `hammer2_zlib_inftrees.h`.
- Read and written by `hammer2_zlib_inflate.c` and `hammer2_zlib_inffast.c`.

Risks and review notes:
- The state is large, roughly 10 KiB by the upstream comment, so allocation failures and kernel memory type consistency matter.
- The enum documents gzip transitions that are not fully implemented in this file set, so the structure can overstate supported stream formats.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.c

Source read: complete file, 304 lines.

Purpose: Builds canonical Huffman decoding tables for inflate. `inflate_table()` converts symbol bit lengths into compact `code` tables used by the inflate state machine and fast decoder.

Key interface:
- `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` returns `0` on success, `-1` for invalid over-subscribed or incomplete code sets, and `1` when the caller-provided `ENOUGH_*` capacity is insufficient.

Implementation notes:
- Counts code lengths, finds min/max lengths, adjusts requested root bits, handles the no-symbol case by emitting invalid markers, and validates prefix-code completeness.
- Sorts symbols by length into the caller-provided `work[]` array.
- Chooses base and extra-bit tables for literal/length and distance codes, including end-of-block handling for symbol 256.
- Fills root and sub-tables by replicating entries over unused high index bits and creates sub-table pointers when code lengths exceed root width.
- Updates `*table` to the next free entry and `*bits` to the actual root table width.

Integration:
- Called by `hammer2_zlib_inflate.c` for code-length, literal/length, and distance trees.
- Uses `ENOUGH_LENS` and `ENOUGH_DISTS` from `hammer2_zlib_inftrees.h` to guard table growth.

Risks and review notes:
- The function assumes all `lens[]` entries are in `0..MAXBITS`; callers must validate or construct lengths safely.
- If root table sizes in inflate are changed, `ENOUGH_LENS` and `ENOUGH_DISTS` must be recalculated or this function can return capacity failure.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.h

Source read: complete file, 62 lines.

Purpose: Internal inflate Huffman-table header. It defines the compact decode entry format, table-size constants, code type enum, and `inflate_table()` prototype.

Key definitions:
- `typedef struct code { unsigned char op; unsigned char bits; unsigned short val; } code;` stores a literal, length/distance base, end marker, invalid marker, or sub-table link.
- `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH` size the dynamic table area used inside `struct inflate_state`.
- `codetype` distinguishes code-length (`CODES`), literal/length (`LENS`), and distance (`DISTS`) table generation.

Integration:
- Shared by `hammer2_zlib_inflate.c`, `hammer2_zlib_inftrees.c`, and `hammer2_zlib_inflate.h`.

Risks and review notes:
- The constants are tightly coupled to root table sizes of 9 bits for literal/length and 6 bits for distance tables. Changing those call sites requires recalculating constants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.c

Source read: complete file, 1232 lines.

Purpose: Deflate-side Huffman tree construction and block emission. This file builds static/dynamic literal, distance, and bit-length trees; chooses stored/static/dynamic block encodings; emits compressed block headers and data; and manages bit-buffer output.

Key exported/internal-zlib interfaces:
- `_tr_init(deflate_state *s)` initializes static tables, tree descriptors, bit buffer fields, debug counters, and the first block.
- `_tr_tally(deflate_state *s, unsigned dist, unsigned lc)` records literal or match symbols, updates tree frequencies, and signals when the literal buffer is full enough to flush.
- `_tr_flush_block(deflate_state *s, charf *buf, ulg stored_len, int last)` builds trees, compares stored/static/dynamic sizes, emits the chosen block, resets block state, and winds up bits on the final block.
- `_tr_stored_block()`, `_tr_flush_bits()`, and `_tr_align()` support stored block emission and compressor synchronization.

Implementation notes:
- `tr_static_init()` builds or references the fixed literal and distance trees, length-code map, distance-code map, and base-length/base-distance arrays.
- `build_tree()` uses a heap over frequencies to construct Huffman trees, forces at least two nonzero codes for PKZIP compatibility, computes bit lengths, and generates bit-reversed deflate codes.
- `gen_bitlen()` caps code lengths to maximum widths and redistributes overflowed lengths.
- `scan_tree()` and `send_tree()` encode repeated bit lengths with repeat symbols 16, 17, and 18.
- `build_bl_tree()` constructs the bit-length tree and computes how many bit-length codes need to be transmitted.
- `compress_block()` walks `d_buf`/`l_buf`, emits literal codes or length/distance pairs, includes extra bits, and terminates with end-of-block.
- `detect_data_type()` classifies a block as `Z_TEXT` or `Z_BINARY` from literal frequencies.
- `bi_flush()`, `bi_windup()`, `bi_reverse()`, and `copy_block()` implement low-level bit packing and byte-aligned stored block copying.

Integration:
- Includes `hammer2_zlib_deflate.h`, which defines `deflate_state`, `ct_data`, tree descriptors, buffer helpers, and constants.
- Includes generated `hammer2_zlib_trees.h` unless `GEN_TREES_H` or a non-ANSI compiler path is used.
- Uses `_length_code` and `_dist_code` arrays consumed by both tallying and block compression.

Risks and review notes:
- This file is highly coupled to `deflate_state` buffer layout, especially the overlay assertions involving `pending_buf`, `d_buf`, and `l_buf`.
- Debug code uses `fprintf`, `isgraph`, and debug counters under `H2_ZLIB_DEBUG`; kernel builds should keep debug configuration intentional.
- The generated table path writes `trees.h` through stdio when `GEN_TREES_H` is defined; that should remain a build-time generation mode, not a kernel runtime path.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.h

Source read: complete file, 128 lines.

Purpose: Generated deflate tree constants used by `hammer2_zlib_trees.c` when not building tables at runtime.

Key contents:
- `static_ltree[L_CODES+2]` contains fixed literal/length tree code/length pairs.
- `static_dtree[D_CODES]` contains fixed distance tree code/length pairs.
- `_dist_code[DIST_CODE_LEN]` maps normalized distances to distance code numbers.
- `_length_code[MAX_MATCH-MIN_MATCH+1]` maps normalized match lengths to length code numbers.
- `base_length[LENGTH_CODES]` and `base_dist[D_CODES]` define base values for extra-bit emission.

Integration:
- Included directly by `hammer2_zlib_trees.c`.
- Relies on `ct_data`, `uch`, `L_CODES`, `D_CODES`, `LENGTH_CODES`, `MAX_MATCH`, `MIN_MATCH`, and related constants from `hammer2_zlib_deflate.h`.

Risks and review notes:
- This is generated data; manual edits are risky unless regenerated with the matching generator mode.
- The arrays must stay consistent with deflate tables and extra-bit arrays in `hammer2_zlib_trees.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zconf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zconf.h

Source read: complete file, 292 lines.

Purpose: zlib configuration header for HAMMER2’s embedded copy, with DragonFly-specific symbol prefixing enabled so the files can be included in kernel configuration without colliding with other zlib symbols.

Key definitions:
- Defines `Z_PREFIX`, then maps public and internal zlib symbols such as `inflate`, `deflate`, `adler32`, `_tr_*`, `inflate_table`, and typedef names to `z_*` names.
- Detects C standard support and defines `STDC`/`STDC99`.
- Defines zlib public ABI types: `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `voidp`, `voidpf`, and related aliases.
- Sets `MAX_MEM_LEVEL`, `MAX_WBITS`, `Z_HAVE_UNISTD_H`, `Z_HAVE_STDARG_H`, and `z_off_t`/`z_off64_t` behavior.
- Includes DragonFly/kernel-flavored headers such as `<sys/limits.h>` and `<sys/stdarg.h>`.

Integration:
- Included through `hammer2_zlib.h` and all internal zlib source files.
- Its prefix mapping controls linker-visible names for the entire embedded zlib copy.

Risks and review notes:
- The forced `Z_PREFIX` is intentional for kernel coexistence; removing it can cause duplicate symbol conflicts.
- Type-size and large-file branches are inherited from portable zlib, but this kernel copy only needs a constrained subset; unused portability paths should still compile cleanly under DragonFly headers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.c

Source read: complete file, 182 lines.

Purpose: Target-dependent zlib utility implementation. It provides version/error strings, compile-flag introspection, debug panic/error handling, and fallback memory routines when libc-style memory functions are unavailable.

Key interfaces:
- `zlibVersion()` returns `ZLIB_VERSION`.
- `zlibCompileFlags()` encodes type sizes and compile-time feature flags such as debug, assembly, dynamic CRC, gzip support, PKZIP workaround, and formatting behavior.
- `zError(int err)` maps zlib error codes through `z_errmsg`.
- Under `H2_ZLIB_DEBUG`, `z_error()` panics in kernel builds or prints/exits outside the kernel.
- If `HAVE_MEMCPY` is not defined, `zmemcpy()`, `zmemcmp()`, and `zmemzero()` are supplied.

Integration:
- Included by internal zlib code through `hammer2_zlib_zutil.h`.
- Uses `Z_PREFIX` mapping from `hammer2_zlib_zconf.h`, so visible names are prefixed in normal builds.

Risks and review notes:
- `zError()` indexes `z_errmsg` through `ERR_MSG(err)` and assumes valid zlib error-code ranges.
- Debug panic behavior is appropriate for invariant failures but too aggressive for malformed input paths; callers should not route normal data errors through `Assert`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.h

Source read: complete file, 149 lines.

Purpose: Internal zlib utility header. It defines local/internal linkage macros, common zlib constants, utility typedefs, error-return helpers, memory function selection, debug tracing macros, and byte-swap support.

Key definitions:
- `ZLIB_INTERNAL` optionally sets hidden visibility.
- `local` defaults to `static`.
- `uch`, `ush`, and `ulg` abbreviate unsigned byte/short/long types.
- `ERR_MSG()` and `ERR_RETURN()` centralize stream error reporting.
- Deflate block type constants `STORED_BLOCK`, `STATIC_TREES`, and `DYN_TREES`.
- Match constants `MIN_MATCH` and `MAX_MATCH`, dictionary flag `PRESET_DICT`, defaults for window and memory level, and `ZSWAP32()`.
- `Assert` and trace macros compile away unless `H2_ZLIB_DEBUG` is set.

Integration:
- Includes `<sys/param.h>` for `panic()` and `hammer2_zlib.h` for the public zlib API.
- Used throughout the HAMMER2 zlib source set.

Risks and review notes:
- Memory routine macros map to `memcpy`, `memcmp`, and `memset` when `HAVE_MEMCPY` is detected; kernel availability and include ordering should remain verified.
- Debug tracing references stdio only in debug builds, which may not be suitable for kernel configurations unless guarded consistently.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/Makefile

Source read: complete file, 8 lines.

Purpose: Kernel module makefile for the DragonFly HPFS filesystem implementation.

Key contents:
- Sets `KMOD= hpfs`.
- Builds `hpfs_vfsops.c`, `hpfs_vnops.c`, `hpfs_hash.c`, `hpfs_subr.c`, `hpfs_lookup.c`, and `hpfs_alsubr.c`.
- Includes `<bsd.kmod.mk>`.

Integration:
- Excludes headers from `SRCS`; they are consumed by the listed C files.
- The module registers VFS operations through `VFS_SET(hpfs_vfsops, hpfs, 0)` in `hpfs_vfsops.c`.

Risks and review notes:
- This makefile does not include optional iconv or helper modules; HPFS codepage conversion is internal to HPFS mount arguments and on-disk codepage tables.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs.h

Source read: complete file, 405 lines.

Purpose: Main HPFS internal header. It declares on-disk structures, mount/node in-memory structures, allocation-tree helpers, directory-entry macros, codepage structures, debug/malloc declarations, vnode conversion macros, and hash-cache prototypes.

Key on-disk structures:
- `sublock` and `spblock` model HPFS super and spare blocks, including magic values, root fnode, total sectors, bad blocks, bitmap pointers, dirblock band metadata, hotfix/spare dirblock fields, and codepage index pointers.
- `hpfsdirent` and `dirblk` describe directory B+tree records and 2 KiB directory blocks, including down-pointer handling through `DE_DOWNLSN()`.
- `alblk`, `alleaf`, `alnode`, and `alsec` describe HPFS allocation trees: leaves map logical offsets to physical extents, nodes point to allocation sectors, and sectors store nested allocation blocks.
- `fnode` stores file metadata, parent pointer, embedded allocation block, size, EA metadata, and inline data.
- `ea`, `cpiblk`, `cpisec`, `cpdblk`, and `cpdsec` describe extended attribute and codepage data.

Key in-memory structures:
- `hpfsmount` stores copied super/spare blocks, export state, device vnode/device id, ownership/mode defaults, bitmap index/data, codepage conversion tables, free-block count, and data-band count.
- `hpfsnode` stores vnode-private state, copied fnode, device references, owner/mode, flags, cached parent directory timestamps, and cached name.
- `hpfid` overlays `struct fid` for NFS file handles.

Integration:
- `VFSTOHPFS()`, `VTOHP()`, and `HPTOV()` connect VFS/vnode objects to HPFS private structures.
- Declares hash routines implemented in `hpfs_hash.c`.
- Shared by all HPFS C files.

Risks and review notes:
- Many structures are direct on-disk overlays and assume exact layout, alignment, and endian behavior.
- Directory and allocation macros perform pointer arithmetic against variable-length records; malformed media can drive out-of-bounds access unless all callers validate record lengths.
- `H_INVAL`, `H_CHANGE`, and `H_PARCHANGE` govern lazy writeback and reclaim behavior; missed flag updates can lose metadata.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_alsubr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_alsubr.c

Source read: complete file, 888 lines.

Purpose: HPFS allocation-tree support. It maps logical file blocks to device sectors, allocates and splits allocation sectors, converts embedded allocation blocks into external allocation sectors, extends files with new extents, recursively inserts extents into allocation trees, concatenates allocation sectors, and truncates allocation trees while freeing blocks.

Key interfaces:
- `hpfs_hpbmap()` descends from an fnode allocation block through alnodes/alsecs until it finds an alleaf covering a logical block; it returns the physical sector and optional run length.
- `hpfs_allocalsec()` finds a free sector, marks it busy, creates a zeroed buffer, initializes `AS_MAGIC`, parent/self links, and an empty leaf allocation block.
- `hpfs_splitalsec()` allocates a sibling alsec and moves roughly half of the current alsec records into it.
- `hpfs_concatalsec()` tries to merge two alsecs into the first and returns `ENOSPC` when records will not fit.
- `hpfs_alblk2alsec()` moves an embedded allocation block into a newly allocated allocation sector.
- `hpfs_addextent()` grows a file allocation tree from the fnode root, converting the root to alnodes when needed.
- `hpfs_addextentr()` recursively inserts extents into the rightmost alsec and reports split alnodes back to its caller.
- `hpfs_truncatealblk()` recursively frees extents at or beyond a block number and may free entire child allocation sectors.

Implementation notes:
- Allocation favors runs near the previous physical extent end by calling `hpfs_bmlookup()` with a starting sector.
- The split path sets left-subtree last `an_nextoff` to `~0` for OS/2 compatibility.
- Truncation attempts to keep the B-tree shape and explicitly notes that it never decrements tree depth.
- Buffer writeback uses `bdwrite()` for metadata changes and `brelse()` for read-only paths.

Integration:
- Relies on bitmap helpers in `hpfs_subr.c` and on on-disk allocation macros from `hpfs.h`.
- Called by `hpfs_bmap()`, `hpfs_read()`, `hpfs_write()`, `hpfs_extend()`, and `hpfs_truncate()`.

Risks and review notes:
- The code assumes the allocation tree is well-formed and has many direct pointer arithmetic operations on on-disk records.
- Some recursive error paths release only the current buffer; previously changed bitmap state may not be rolled back if later metadata writes fail.
- Truncation preserves tree depth, so long-lived files that shrink drastically can retain unnecessary allocation-tree levels.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_alsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_hash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_hash.c

Source read: complete file, 172 lines.

Purpose: In-core HPFS node hash table keyed by device and fnode sector number. It prevents duplicate vnodes for the same on-disk fnode and supports lookup/vget during VFS operations.

Key interfaces:
- `hpfs_hphashinit()` initializes a lock, allocates the hash table with `hashinit()`, and initializes the LWKT token.
- `hpfs_hphash_uninit()` destroys the hash table during VFS uninit.
- `hpfs_hphashlookup()` returns a matching `hpfsnode` without taking a vnode reference.
- `hpfs_hphashvget()` finds and exclusively vgets a vnode, then revalidates the hash entry after possible blocking.
- `hpfs_hphashins()` marks a node hashed and inserts it.
- `hpfs_hphashrem()` removes a hashed node and clears diagnostic links under `DIAGNOSTIC`.

Integration:
- Used by `hpfs_vget()` and `hpfs_reclaim()` in `hpfs_vfsops.c`/`hpfs_vnops.c`.
- Protected by `hpfs_hphash_token`; node creation is also serialized with `hpfs_hphash_lock`.

Risks and review notes:
- `hpfs_hphash_uninit()` destroys the table without explicitly nulling `hpfs_hphashtbl`.
- Correctness depends on the revalidation loop in `hpfs_hphashvget()` because `vget()` can block and race with reclaim.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_ioctl.h

Source read: complete file, 44 lines.

Purpose: Public HPFS ioctl definitions for querying inline extended attributes.

Key definitions:
- `struct hpfs_rdea` carries an EA index, returned EA size, and user buffer pointer.
- `HPFSIOCGEANUM` returns the number of EAs.
- `HPFSIOCGEASZ` queries the size of a specific EA.
- `HPFSIOCRDEA` reads EA name/value data into a caller buffer.

Integration:
- Implemented by `hpfs_ioctl()` in `hpfs_vnops.c`.
- Includes `<sys/ioccom.h>` for ioctl encoding macros.

Risks and review notes:
- The ioctl contract exposes a raw user pointer in `hpfs_rdea`; implementation must validate copyout behavior and size handling carefully.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_lookup.c

Source read: complete file, 213 lines.

Purpose: HPFS directory lookup and placeholder write-side directory entry operations.

Key interfaces:
- `hpfs_genlookupbyname()` traverses the HPFS directory B+tree from the first directory block in the parent fnode allocation data, compares Unix-encoded input names against on-disk names with codepage-aware case folding, follows `DE_DOWN` child pointers, and returns the buffer plus matching `hpfsdirent`.
- `hpfs_makefnode()` is a create helper stub that returns `EOPNOTSUPP`.
- `hpfs_removedirent()` contains disabled deletion logic under `#if 0` and currently returns `EOPNOTSUPP`.
- `hpfs_removefnode()` is a remove helper stub that returns `EOPNOTSUPP`.

Integration:
- `hpfs_lookup()` in `hpfs_vnops.c` uses `hpfs_genlookupbyname()` for VOP lookup.
- Parent metadata update in `hpfs_updateparent()` uses `hpfs_genlookupbyname()` to find the cached child dirent.

Risks and review notes:
- Directory creation and removal are not implemented despite VOP stubs routing to these helpers.
- Lookup trusts directory record lengths enough to step through blocks; malformed media can cause invalid pointer traversal if earlier structure checks are insufficient.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.c

Source read: complete file, 868 lines.

Purpose: HPFS support routines for checksums, bitmap loading/flushing/searching/marking, codepage loading and filename comparison, parent directory metadata validation/update, fnode writeback, file size extension/truncation, and typed metadata reads.

Key interfaces:
- `hpfs_checksum()` computes HPFS-style rotating additive checksum.
- `hpfs_bminit()` loads the bitmap index and all bitmap bands, then counts free sectors.
- `hpfs_bmdeinit()` writes dirty in-memory bitmaps back on read-write mounts and frees bitmap memory.
- `hpfs_bmlookup()`, `hpfs_bmfblookup()`, and `hpfs_bmmark()` find free runs, find a single free block, and mark contiguous blocks free or busy.
- `hpfs_cpinit()`, `hpfs_cpload()`, and `hpfs_cpdeinit()` load on-disk codepage data and optional user-provided conversion tables.
- `hpfs_cmpfname()` and `hpfs_cpstrnnicmp()` compare names with HPFS uppercasing and conversion tables.
- `hpfs_validateparent()` searches the parent directory tree to cache a node's dirent name and timestamps.
- `hpfs_updateparent()` writes cached access/modify time and size changes back to the parent dirent.
- `hpfs_update()` writes the fnode to disk and chains parent update if needed.
- `hpfs_truncate()` and `hpfs_extend()` adjust allocation trees and file size.
- `hpfs_breadstruct()` reads a metadata structure and validates its leading magic.

Implementation notes:
- Bitmap bands are 0x4000 sectors each, with one 4-sector bitmap per band.
- `hpfs_bmlookup()` first tries a requested nearby LSN, then scans data bands circularly.
- `hpfs_bmmark()` treats set bits as free and clear bits as busy, updating `hpm_bavail`.
- Codepage tables default to identity mapping for high-half bytes unless `HPFSMNT_TABLES` supplies conversion arrays.
- Parent validation performs a depth-first walk of directory down-pointers and climbs back via `d_parent`.

Integration:
- Used by mount/unmount, vnode read/write/setattr/fsync, lookup, and allocation helpers.

Risks and review notes:
- The source explicitly notes bitmap operations need locking; concurrent allocation/free paths can race without external serialization.
- `hpfs_bmmark()` logs out-of-volume marking but returns success (`0`), which can hide metadata corruption.
- Codepage allocation failure cleanup is incomplete in some `hpfs_cpinit()` error paths; allocated `hpm_cpdblk` can leak if later loads fail before mount teardown handles it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.h

Source read: complete file, 83 lines.

Purpose: HPFS helper API header. It declares bitmap, codepage, file-size, update, lookup, creation/removal, typed-read, block-map, truncation, and extent-allocation helpers.

Key definitions:
- `hpfs_bmmarkfree()` and `hpfs_bmmarkbusy()` wrap `hpfs_bmmark()` with the correct bit state.
- `hpfs_u2d()`, `hpfs_d2u()`, and `hpfs_toupper()` implement byte conversion and case mapping through mount codepage tables.
- Macros `hpfs_breadalsec()` and `hpfs_breaddirblk()` specialize `hpfs_breadstruct()` for allocation sectors and directory blocks.

Integration:
- Included by HPFS implementation files after `hpfs.h`.
- Exposes cross-file dependencies between `hpfs_subr.c`, `hpfs_alsubr.c`, `hpfs_lookup.c`, `hpfs_vfsops.c`, and `hpfs_vnops.c`.

Risks and review notes:
- Conversion macros evaluate some arguments multiple times; callers should avoid side effects.
- The comment asks whether unsigned conversion is needed, signaling historical uncertainty around high-bit character handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vfsops.c

Source read: complete file, 569 lines.

Purpose: HPFS VFS operation implementation. It handles mount/update, device opening, super/spare block validation, bitmap/codepage initialization, root lookup, unmount cleanup, statfs, NFS file handles, vnode instantiation, export checks, and VFS registration.

Key interfaces:
- `hpfs_mount()` copies `hpfs_args`, handles export-only updates, resolves the block device with namecache lookup, verifies disk vnode type, records mount-from name, and calls `hpfs_mountfs()`.
- `hpfs_mountfs()` prevents duplicate/in-use mounts, invalidates old buffers, opens the device read-only or read-write, reads super/spare blocks, validates magic numbers, initializes `hpfsmount`, bitmap and codepage state, installs vnode ops, resolves root, and records fsid/local flags.
- `hpfs_unmount()` flushes vnodes, closes the device, invalidates buffers, frees codepage and bitmap memory, clears mount data, and frees `hpfsmount`.
- `hpfs_root()`, `hpfs_statfs()`, `hpfs_fhtovp()`, `hpfs_vptofh()`, and `hpfs_checkexp()` implement standard VFS services.
- `hpfs_vget()` creates or finds vnodes, reads fnode sectors, validates `FN_MAGIC`, initializes `hpfsnode`, inserts into the hash, and sets vnode type.

Integration:
- Registers `hpfs_vfsops` with `VFS_SET(hpfs_vfsops, hpfs, 0)` and `MODULE_VERSION(hpfs, 1)`.
- Uses `hpfs_hphashinit()` during VFS init and `hpfs_hphash_uninit()` during VFS uninit.
- Adds `hpfs_vnode_vops` to the mount's normal vnode ops.

Risks and review notes:
- `hpfs_vget()` sets `hp->h_gid = hpmp->hpm_uid`; this looks like a uid/gid mix-up and can make all nodes report the uid as gid.
- Several failure paths after partial mount initialization require careful cleanup ordering; `mp->mnt_data` and `dev->si_mountpoint` are cleared in the common failure path.
- HPFS file handles do not validate generation numbers because create/unlink are not supported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vnops.c

Source read: complete file, 1184 lines.

Purpose: HPFS vnode operation implementation. It supports ioctl access to inline extended attributes, bmap/read/write, getattr/setattr, inactive/reclaim, strategy, access checks, readdir, lookup, create/remove stubs, fsync, pathconf, and the vnode op table.

Key interfaces:
- `hpfs_ioctl()` implements EA count, EA size, and EA read ioctls by walking inline `fn_int` EA records.
- `hpfs_bmap()` maps logical byte offsets to device offsets through `hpfs_hpbmap()`.
- `hpfs_read()` maps runs, reads from the device vnode, and `uiomove()`s data out.
- `hpfs_write()` supports append, extends allocation as needed, writes full or partial blocks, and uses sync or async writeback based on `IO_SYNC`.
- `hpfs_getattr()` returns vnode attributes from `hpfsnode`/fnode state and validates parent dirent metadata when needed.
- `hpfs_setattr()` rejects mode/uid/gid/flags changes, supports time updates, and grows/shrinks regular files through `hpfs_extend()`/`hpfs_truncate()`.
- `hpfs_fsync()` flushes dirty buffers with `vfsync()` and writes fnode metadata through `hpfs_update()`.
- `hpfs_inactive()` writes changed fnode or parent-dir metadata and recycles invalid nodes.
- `hpfs_reclaim()` removes hash entries, releases the device vnode, detaches `v_data`, and frees the node.
- `hpfs_readdir()` fakes `.` and `..`, walks HPFS directory down-pointer trees, converts names through `hpfs_d2u()`, and optionally emits NFS cookies.
- `hpfs_lookup()` handles `.`, `..`, access checks, directory searches, VFS_VGET, parent locking flags, and create/delete lookup semantics.
- `hpfs_strategy()` resolves unmapped bios through VOP_BMAP and forwards to the device vnode.
- `hpfs_pathconf()` reports HPFS link/name/path and chown/truncation constraints.

Integration:
- `hpfs_vnode_vops` wires these routines into DragonFly VOP dispatch.
- Uses helpers from `hpfs_subr.c`, `hpfs_alsubr.c`, and `hpfs_lookup.c`.

Risks and review notes:
- Write-side directory operations route to helpers that return `EOPNOTSUPP`, so create/remove VOP entries exist but are not functional.
- `hpfs_ioctl()` prints EA names with `%s` while EA names are length-delimited in the on-disk format; malformed or unterminated names could overrun debug output expectations.
- `hpfs_read()` and `hpfs_write()` compute `resid`/transfer sizes with unsigned and signed conversions; boundary behavior near EOF and large offsets should be tested.
- Readdir's tree walk uses a synthetic numeric offset rather than stable byte offsets; this is simple but can be fragile for NFS-style cookie expectations if directories changed, though HPFS mutation is largely unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfsmount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfsmount.h

Source read: complete file, 40 lines.

Purpose: Public HPFS mount argument header.

Key definitions:
- `HPFSMNT_TABLES` signals that user-provided DOS-to-Unix and Unix-to-DOS high-byte conversion tables should be used.
- `struct hpfs_args` carries block device path, export args, owner uid/gid defaults, mode mask/default, mount flags, and two 0x80-byte conversion tables.

Integration:
- Copied in from user space by `hpfs_mount()`.
- Consumed by `hpfs_mountfs()` and `hpfs_cpinit()`.

Risks and review notes:
- Conversion tables are trusted once copied from mount arguments; invalid tables can affect lookup, readdir, and name comparisons for high-bit filenames.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/Makefile

Source read: complete file, 6 lines.

Purpose: Parent makefile for ISO filesystem modules.

Key contents:
- Sets `SUBDIR=cd9660`.
- Includes `<bsd.subdir.mk>`.

Integration:
- Delegates actual ISO 9660 module building to `sys/vfs/isofs/cd9660/Makefile`.

Risks and review notes:
- None beyond normal subdirectory build registration.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/Makefile

Source read: complete file, 10 lines.

Purpose: Kernel module makefile for the cd9660 ISO 9660 filesystem.

Key contents:
- Sets `KMOD= cd9660`.
- Builds `cd9660_bmap.c`, `cd9660_lookup.c`, `cd9660_node.c`, `cd9660_rrip.c`, `cd9660_util.c`, `cd9660_vfsops.c`, and `cd9660_vnops.c`.
- Exports `cd9660_iconv`.
- Builds `cd9660_iconv` as a subdirectory module.
- Includes `<bsd.kmod.mk>`.

Integration:
- The files in this group are a subset of the module sources; lookup and bmap depend on node, util, RRIP, VFS, and vnode code in neighboring files.

Risks and review notes:
- `EXPORT_SYMS= cd9660_iconv` is important for the iconv support module and VFS code to share the conversion hook.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_bmap.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_bmap.c

Source read: complete file, 100 lines.

Purpose: Logical-to-physical block mapping for cd9660 files.

Key interface:
- `cd9660_bmap(struct vop_bmap_args *ap)` maps a file logical offset to a device offset by adding the file's starting extent (`iso_start << im_bshift`) to the logical offset.

Implementation notes:
- Returns success immediately when no physical offset is requested.
- Asserts the logical offset is block-aligned to the mounted ISO block size.
- Computes `a_runp` as readahead bytes remaining in the file, capped at `MAXBSIZE` and rounded down to block size.
- Sets backward run (`a_runb`) to zero.

Integration:
- Used by read/strategy paths and by directory buffer helpers that need stable physical offsets.
- Depends on `iso_node` mount block-shift and extent metadata.

Risks and review notes:
- ISO files are contiguous extents in this model; sparse or multi-extent semantics must be handled elsewhere if supported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/Makefile

Source read: complete file, 6 lines.

Purpose: Kernel module makefile for cd9660 iconv support.

Key contents:
- Sets `KMOD= cd9660_iconv`.
- Builds `cd9660_iconv.c`.
- Includes `<bsd.kmod.mk>`.

Integration:
- Built as a submodule from the parent cd9660 makefile.

Risks and review notes:
- Module usefulness depends on the kernel iconv framework being available.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/cd9660_iconv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/cd9660_iconv.c

Source read: complete file, 35 lines.

Purpose: Declares cd9660's VFS iconv module integration.

Key contents:
- Includes kernel, module, mount, and iconv headers.
- Invokes `VFS_DECLARE_ICONV(cd9660);`.

Integration:
- Provides the iconv glue for cd9660 Joliet charset conversion flags and mount arguments.
- Complements `EXPORT_SYMS= cd9660_iconv` in the parent cd9660 makefile.

Risks and review notes:
- This file contains no logic of its own; behavior is generated by the `VFS_DECLARE_ICONV` macro and the kernel iconv framework.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/cd9660_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_lookup.c

Source read: complete file, 477 lines.

Purpose: cd9660 pathname lookup and directory block access helpers. It searches ISO directory records, handles ISO/Rock Ridge/Joliet-style names, resolves special entries, and provides buffer helpers for directory contents from vnode or device buffers.

Key interfaces:
- `cd9660_lookup()` implements old-style VOP lookup for ISO directories.
- `cd9660_blkatoff()` reads a block through the directory vnode and ensures buffer `bio2.bio_offset` is mapped.
- `cd9660_devblkatoff()` maps through VOP_BMAP and reads the underlying device vnode directly, putting the device offset in `bio1.bio_offset`.

Lookup implementation notes:
- Handles associated files when a component begins with `=` and Rock Ridge is not active.
- Uses `i_diroff` as a lookup cache for repeated lookup operations and may do two passes if starting from a cached offset.
- Reads directory entries block by block, rejects zero-length padding by advancing to the next block, and stops on malformed entries that are too short or cross block boundaries.
- Compares normal ISO/Joliet names through `isofncmp()` and RRIP names through `cd9660_rrip_getname()`.
- For directories, inode numbers come from `isodirino()`; for files, they can be derived from the physical directory entry offset.
- Returns `EROFS` for create/rename misses because cd9660 is read-only.
- Handles `..` by unlocking the current directory before `cd9660_vget_internal()` to avoid parent/child vnode deadlocks.
- Passes a relocated flag to `cd9660_vget_internal()` when a directory's effective inode differs from the entry-derived inode.

Integration:
- Depends on `iso.h`, `cd9660_node.h`, and `iso_rrip.h`.
- Used by cd9660 vnode operation tables outside this group.
- Directory helpers are used both by lookup and by other metadata paths that need direct directory record access.

Risks and review notes:
- The malformed-entry checks stop search but do not necessarily distinguish corruption from not-found in all cases.
- `cd9660_devblkatoff()` warns that callers must read device offsets from `bio1.bio_offset`, not `bio2.bio_offset`.
- Name sorting optimizations are conditional around `NOSORTBUG`; media with unsorted directory entries may need that compatibility behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_mount.h

Source read: complete file, 68 lines.

Purpose: Public cd9660 mount argument header.

Key definitions:
- `struct iso_args` carries block device path, export args, owner uid/gid defaults, file and directory masks, mount flags, session start sector, and disk/local charset names for Joliet conversion.
- Flags include disabling Rock Ridge, enabling generation numbers or extended attributes, disabling or relaxing Joliet, enabling kernel iconv, and overriding uid/gid/mode masks.

Integration:
- Copied in by cd9660 mount code in `cd9660_vfsops.c`.
- Charset fields depend on `<sys/iconv.h>` and `ICONV_CSNMAXLEN`.

Risks and review notes:
- Mount behavior is strongly flag-dependent: `ISOFSMNT_NORRIP`, `ISOFSMNT_NOJOLIET`, and `ISOFSMNT_KICONV` alter name parsing and presentation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_mount.h -->