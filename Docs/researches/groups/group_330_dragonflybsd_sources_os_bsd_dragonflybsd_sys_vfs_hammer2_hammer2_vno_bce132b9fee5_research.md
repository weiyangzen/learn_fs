# Group Research: group_330_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer2_hammer2_vno_bce132b9fee5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vnops.c

HAMMER2 vnode operation implementation for DragonFlyBSD VFS integration, covering file I/O, directory operations, namespace mutation, metadata changes, vnode lifecycle, kqueue, and special/FIFO vnode operation vectors.

Key responsibilities:
- Defines HAMMER2 VOP tables for regular vnodes, special-device vnodes, and FIFO vnodes.
- Handles vnode inactive/reclaim by disconnecting inodes, queuing unlinked inodes for delayed deletion, truncating cached buffers for deleted objects, and avoiding unsafe flushes during reclaim.
- Implements fsync by syncing logical file buffers, waiting for tracked writes, syncing inode metadata into chains, flushing inode-related chains, and clearing vnode dirty state when safe.
- Implements access, full getattr, lite getattr, setattr, advisory locking, open/close, ioctl, mountctl export setup, markatime, and kqueue filters.
- Implements regular-file and symlink reads/writes through DragonFly buffer-cache helpers, clustered reads/writes, `uiomovebp()`, file-size extension/truncation, resource-limit checks, and transaction interlocks.
- Implements directory readdir with synthetic `.`/`..` entries, directory cookies, XOP-backed scans, inode-vs-dirent result handling, and EOF offset management.
- Implements name resolution, `..` lookup, mkdir, create, mknod, symlink, hardlink, remove, rmdir, and rename using HAMMER2 inode locks, transactions, namecache updates, XOP workers, and kqueue notifications.
- Exposes strategy and bmap VOPs via functions implemented outside this file.

Important implementation details:
- Metadata mutation generally rejects read-only or emergency-mode mounts, starts a HAMMER2 transaction, locks relevant inodes, performs inode/dirent work, then completes the transaction with `HAMMER2_TRANS_SIDEQ`.
- `setattr` uses helper routines for flags, chown, chmod, and file-size changes; truncation and direct-data boundary crossing force `hammer2_inode_chain_sync()` because the chain topology must match the in-memory inode state.
- `hammer2_read_file()` takes inode/truncate locks, determines logical block geometry with `hammer2_calc_logical()`, uses `cluster_readx()`, and caps reads at file EOF.
- `hammer2_write_file()` handles append, pre-extension, partial-buffer read-before-write, `UIO_NOCOPY` pageout writes, direct/semi-sync writes under low-space pressure, and error rollback by truncating back to old EOF.
- Symlink creation creates an inode and directory entry first, then writes the target through the normal file-write path.
- Remove/rmdir use `hammer2_unlink_desc` XOPs and let `hammer2_inode_unlink_finisher()` update frontend inode disposition and possible vnode recycling.
- Rename locks source directory, target directory, source inode, and optional target inode; allocates a collision-safe target directory hash key; issues backend rename; updates frontend metadata/namecache after internal locks are released.
- Kqueue support reports readable bytes from `ip->meta.size`, write readiness, vnode event masks, and revoke EOF/NODATA handling.

Dependencies:
- Includes DragonFly kernel VFS, vnode, buffer-cache, mountctl, dirent, uio, kqueue, file, FIFO, and object-cache headers.
- Depends on HAMMER2 inode, transaction, XOP, chain, namecache, mount/PFS, buffer-cache, strategy, ioctl, and notification APIs from `hammer2.h`.
- Uses DragonFly helpers such as `vfsync`, `bio_track_wait`, `cluster_readx`, `cluster_write`, `bread_kvabio`, `getblk`, `nvtruncbuf`, `nvextendbuf`, `vop_helper_access`, `vop_helper_chown`, `vop_helper_chmod`, `lf_advlock`, and `cache_*`.

Notable risks:
- Lock ordering is subtle across vnode locks, inode locks, truncate locks, transactions, namecache operations, and XOP collection; rename in particular relies on pointer-order locking and cache updates after internal unlocks.
- Comments warn that some inode-chain synchronization for resize/direct-data transitions happens outside normal sync/fsync, creating crash-consistency edge cases.
- Symlink target write errors are explicitly ignored after the write path (`XXX handle error`), which can mask failure during creation.
- Atime is effectively unsupported: getattr reports atime from mtime and markatime only checks writability.
- File extension/truncation assumes VFS-level size interlocks; misuse from other paths can desynchronize buffer cache state and chain topology.
- Space-pressure handling can silently force `IO_DIRECT` for semi-synchronous writes, affecting performance and ordering.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xops.c

HAMMER2 per-node backend XOP implementation. These routines execute VFS/inode operations against one cluster element’s chain topology and feed locked chain results or completion status back to the frontend XOP collector.

Key responsibilities:
- Implements backend operations for inode cluster lookup, readdir, name resolve, unlink/rmdir/PFS delete, rename, collision-space scans, key lookup/delete, full scans, inode create/connect/destroy/unlinkall, inode-chain sync, and bmap.
- Provides `checkdirempty()` to validate directory emptiness while handling both embedded inode chains and separate dirent chains.
- Drives namespace scans over HAMMER2 directory hash ranges and exact key ranges.
- Creates inline or external-buffer directory entries depending on name length.
- Creates normal attached inodes, detached inodes, and inserts detached inodes into the topology.
- Deletes chains permanently or logically depending on operation flags.
- Syncs frontend inode metadata into backend inode chains and removes data chains beyond new EOF for truncation.
- Resolves logical offsets to physical `data_off` values for bmap.

Important implementation details:
- Backend functions typically acquire a chain for `head.ip1` at `clindex` with either shared or exclusive resolve flags, perform lookup/create/delete work, then call `hammer2_xop_feed()`.
- Fed chains are generally locked when transferred to the frontend; callers then unlock/drop local references after feeding according to XOP conventions.
- `checkdirempty()` may unlock and relock caller-supplied chains to find the real inode behind a dirent; it returns `HAMMER2_ERROR_EAGAIN` if topology changed and the caller must retry.
- Name resolution hashes the requested name, scans the collision range, tests candidate dirents, and resolves separate dirent records to inode chains by inode number.
- Unlink/rmdir validate type expectations, directory emptiness, forced/permanent-delete flags, and can return the target inode chain for frontend nlink/disposition finishing.
- Rename handles embedded inodes and separate dirents, deletes the old entry, updates stored filename/name-key/iparent metadata for crash/debug consistency, deletes duplicate target entries as self-healing, then inserts the renamed chain into the target directory.
- `hammer2_xop_inode_chain_sync()` handles truncation by deleting data chains above rounded-up EOF before copying updated inode metadata into the inode chain.

Dependencies:
- Includes `hammer2.h` and relies on HAMMER2 chain lookup, create, delete, resize, modify, parent lookup, inode-chain acquisition, inode-number lookup, dirent comparison, XOP feed, and error-code conventions.
- Called by frontend VOP/inode/admin code via XOP descriptors declared elsewhere, especially from `hammer2_vnops.c`, inode creation/deletion paths, sync paths, and bmap/strategy paths.

Notable risks:
- Topology mutation is concurrency-sensitive; several operations intentionally drop and reacquire locks, so `EAGAIN` retry handling is required for correctness.
- Frontend/backend split means backend chains and frontend `hammer2_inode_t` metadata can be temporarily unsynchronized; comments explicitly assign final nlink and metadata authority to frontend code in several paths.
- Rename is complex and mixes deletion, metadata rewrite, duplicate-target cleanup, and reinsertion; partial errors can leave work for recovery/self-healing.
- Directory emptiness checks for rename/unlink depend on exact visible namespace ranges and correct handling of dirent-vs-inode representations.
- Several paths use assertions or debugging prints for states considered impossible but observed under stress, indicating fragile historical edge cases.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xxhash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xxhash.h

HAMMER2 wrapper header for the bundled xxHash implementation.

Key responsibilities:
- Includes HAMMER2’s vendored `xxhash/xxhash.h`.
- Defines the HAMMER2-specific 64-bit xxHash seed `XXH_HAMMER2_SEED`.
- Provides a small guarded include point for HAMMER2 checksum/hash users.

Dependencies:
- Depends on `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h`, which namespaces exported xxHash symbols with `h2_`.

Notable risks:
- The seed is part of HAMMER2’s hash/checksum behavior; changing it would alter computed values and compatibility expectations.
- Symbol namespace behavior is controlled in the vendored xxHash header, so wrapper users depend on that header retaining `XXH_NAMESPACE h2_`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xxhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.c

Vendored xxHash 0.6.0 implementation adapted for DragonFly kernel builds and namespaced for HAMMER2.

Key responsibilities:
- Implements one-shot `XXH32()` and `XXH64()` hash functions.
- Implements streaming state reset, update, and digest for 32-bit and 64-bit hashes.
- Implements optional userland dynamic state allocation/free, excluded for `_KERNEL` builds.
- Implements canonical big-endian conversion to/from 32-bit and 64-bit hash digests.
- Provides endian-independent reads, byte swapping, alignment-aware fast paths, avalanche finalization, and architecture/compiler tuning macros.

Important implementation details:
- Includes `<sys/types.h>` and `<sys/systm.h>` in kernel builds; userland builds use libc allocation/string headers.
- `XXH_STATIC_LINKING_ONLY` is defined before including the header so internal state layouts are visible.
- Public symbols are transformed by `XXH_NAMESPACE h2_` from the header.
- Memory reads use one of three strategies depending on `XXH_FORCE_MEMORY_ACCESS`: memcpy-safe, packed union, or direct unaligned access.
- Hashes are little-endian canonical internally unless `XXH_FORCE_NATIVE_FORMAT` is enabled.
- Streaming updates buffer incomplete 16-byte or 32-byte stripes in state and process full stripes through four accumulators.
- Canonical representations are explicitly big-endian for persistent/cross-platform comparison.

Dependencies:
- Depends on `xxhash.h` for API types, namespace macros, and static state layouts.
- In kernel mode, depends on DragonFly kernel `memcpy`, `memset`, and basic integer types.

Notable risks:
- Null input pointers are invalid unless `XXH_ACCEPT_NULL_INPUT_POINTER` is enabled; callers must not pass null with nonzero lengths.
- Forced direct unaligned access can violate C aliasing/alignment assumptions on some targets if selected incorrectly.
- Cross-platform persistent hash compatibility depends on leaving endian behavior and canonical conversion semantics unchanged.
- Dynamic create/free APIs are not compiled in `_KERNEL` mode; kernel callers must use stack/static state where needed.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h

Vendored xxHash public/static-linking header with DragonFly-specific symbol namespacing.

Key responsibilities:
- Defines `XXH_NAMESPACE h2_` so all public xxHash symbols are compiled/exported as HAMMER2-private names.
- Declares xxHash version constants and `XXH_versionNumber()`.
- Declares one-shot 32-bit and 64-bit hash APIs.
- Declares streaming state opaque types, create/free/reset/update/digest APIs, and canonical digest conversion APIs.
- Defines `XXH_PUBLIC_API` behavior for normal vs private/static inclusion.
- Under `XXH_STATIC_LINKING_ONLY`, exposes internal `XXH32_state_s` and `XXH64_state_s` layouts.

Important implementation details:
- Skips `<stddef.h>` when `_KERNEL` is defined, relying on kernel-provided `size_t`.
- Namespace macros rewrite `XXH32`, `XXH64`, version, state allocation, reset, update, digest, and related public names.
- Canonical digest structs are byte arrays sized to 4 and 8 bytes.
- Static state layouts contain total length, seed, four accumulators, aligned scratch buffer, and scratch size.

Dependencies:
- Used by `xxhash.c` and by HAMMER2 wrapper `hammer2_xxhash.h`.
- Depends on callers including it consistently with the same namespace/static-linking settings as the compiled implementation.

Notable risks:
- Changing namespace macros can create kernel symbol collisions with other xxHash copies.
- Exposed static-linking state layouts are explicitly not stable upstream API; code depending on them is tied to this vendored version.
- Header/API version is old (`0.6.0`); replacing it requires verifying HAMMER2 hash compatibility and kernel build assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib.h

HAMMER2-local zlib 1.2.8 public interface header, trimmed for in-kernel compression/decompression use.

Key responsibilities:
- Defines zlib version constants, stream type `z_stream`, flush constants, status/error codes, compression levels, strategies, data-type values, and the `Z_DEFLATED` method.
- Declares deflate init, deflate, deflate end, inflate init, inflate, inflate end, and Adler-32 checksum APIs.
- Declares internal version-checking init entry points `deflateInit_()` and `inflateInit_()`.
- Defines convenience macros for `deflateInit`, `inflateInit`, `deflateInit2`, and `inflateInit2` that pass `ZLIB_VERSION` and `sizeof(z_stream)`.
- Includes HAMMER2’s zconf wrapper `hammer2_zlib_zconf.h`.

Important implementation details:
- The visible `z_stream` omits allocator callbacks compared with full upstream zlib in this copy; comments still describe allocator fields from upstream documentation.
- Comments preserve upstream zlib API semantics for streaming compression/decompression, flush modes, return codes, checksum behavior, and gzip/zlib format handling.
- `struct internal_state` is opaque to applications unless a dummy declaration is needed for compiler compatibility.
- The header is not a full general-purpose userland zlib surface; it exposes the subset needed by the bundled HAMMER2 zlib implementation.

Dependencies:
- Depends on `hammer2_zlib_zconf.h` for base zlib typedefs and configuration macros.
- Implemented by HAMMER2-local zlib source files such as deflate, inflate, trees, inffast, inftrees, zutil, and adler32 sources.

Notable risks:
- Upstream comments and local structure definitions diverge in places, especially allocator callback discussion; developers should trust the actual type definition.
- Version/init macros must match implementation `ZLIB_VERSION` and stream layout or init returns `Z_VERSION_ERROR`.
- Since this is vendored zlib 1.2.8, security or correctness updates from newer zlib versions are not automatically present.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_adler32.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_adler32.c

Vendored zlib Adler-32 checksum implementation used by HAMMER2’s zlib compressor/decompressor.

Key responsibilities:
- Implements `adler32()` for running Adler-32 checksum updates over byte buffers.
- Implements `adler32_combine()` and `adler32_combine64()` via shared `adler32_combine_()` for combining checksums of concatenated streams.
- Provides optimized short-length and block-processing paths.

Important implementation details:
- Uses `BASE = 65521` and `NMAX = 5552` to bound modulo operations within 32-bit arithmetic.
- Special-cases one-byte updates and null-buffer initialization.
- Processes large inputs in `NMAX` chunks with unrolled `DO16` byte accumulation.
- Supports a `NO_DIVIDE` path using reduction macros instead of `% BASE`.
- Negative combine lengths return `0xffffffffUL` as an invalid checksum clue.

Dependencies:
- Includes `hammer2_zlib_zutil.h` for zlib typedefs, `Z_NULL`, and utility definitions.

Notable risks:
- The one-byte fast path reads `buf[0]` before the later null-buffer check; callers must only pass `buf == Z_NULL` with `len == 0`.
- Combine correctness depends on signedness and width of `z_off_t`/`z_off64_t`.
- This is checksum/integrity support, not cryptographic protection.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_adler32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.c

HAMMER2-local zlib deflate compressor implementation, adapted from zlib 1.2.8 for kernel allocation and HAMMER2 build integration.

Key responsibilities:
- Implements `deflateInit_()`, `deflateInit2_()`, `deflateResetKeep()`, `deflateReset()`, `deflate()`, and `deflateEnd()`.
- Allocates and initializes compressor state, sliding window, hash chains, and pending/literal/distance buffers.
- Writes zlib headers/trailers, tracks Adler-32, flushes pending output, and manages stream status transitions.
- Implements input reading into the LZ77 window and rolling hash-table maintenance.
- Implements longest-match search, lazy-match compression, RLE strategy, and Huffman-only strategy.
- Flushes completed blocks through tree-building/output helpers declared in the deflate header.

Important implementation details:
- Uses DragonFly kernel `kmalloc`/`kfree` with `C_ZLIB_BUFFER_DEFLATE` instead of userland zlib allocation callbacks.
- All configuration-table compression levels route through `deflate_slow` in this copy; upstream stored/fast paths are commented out.
- `deflate()` emits the zlib header when called, updates `last_flush`, handles duplicate flush cases, runs the selected compression function, emits empty stored blocks for sync/full flush, clears history on full flush, and writes the Adler trailer at finish.
- `read_buf()` copies input into the sliding window, updates `strm->adler` when wrapping is enabled, and advances stream counters.
- `fill_window()` slides the 32 KiB dictionary, updates head/prev hash tables, reads more input, initializes hash state, and zeroes high-water bytes to avoid longest-match reads from uninitialized memory.
- `longest_match()` walks hash chains up to level-dependent limits, applies good/nice match heuristics, and bounds matches by lookahead.
- `deflate_slow()` performs lazy evaluation: it emits the previous match only if the next position does not produce a better match.
- `deflate_rle()` emits distance-one matches for byte runs and does not maintain hash chains.
- `deflate_huff()` emits only literals and uses Huffman coding without LZ77 matches.

Dependencies:
- Includes `hammer2_zlib_deflate.h`, `../hammer2.h`, and DragonFly malloc definitions.
- Depends on zlib tree helpers `_tr_init`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, `_tr_stored_block`, and tally macros.
- Uses zlib utility macros/functions from `hammer2_zlib_zutil.h`, including `zmemcpy`, `zmemzero`, `ERR_RETURN`, `ERR_MSG`, and constants such as `MAX_WBITS`.

Notable risks:
- Kernel allocation has no application-provided allocator hooks; memory pressure behavior depends on `M_INTWAIT` allocations.
- Level 0 is not true store-only in this copy because stored/fast functions are commented out and mapped to `deflate_slow`.
- Header emission appears unconditional in `deflate()` after reset state setup; any change to status handling must preserve zlib stream correctness.
- Compression state is large and pointer-rich; partial allocation failure must continue to be cleaned by `deflateEnd()`.
- Longest-match code intentionally reads guard bytes beyond valid lookahead, relying on `fill_window()` high-water zeroing for safety.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.h

Internal deflate compressor state header for the HAMMER2-local zlib copy.

Key responsibilities:
- Defines deflate coding constants for literal/length codes, distance codes, bit-length codes, heap size, max Huffman bits, and bit-buffer size.
- Defines stream status constants used by the compressor state machine.
- Defines Huffman tree node structures, tree descriptors, position types, and the full `deflate_state` structure.
- Declares tree-output helper functions used by `hammer2_zlib_deflate.c`.
- Defines output, lookahead, distance, and tree-tally helper macros.

Important implementation details:
- `deflate_state` stores the zlib stream pointer, pending output buffer, wrapping/status fields, sliding window, hash chains, match-search state, compression-level tunables, Huffman trees, literal/distance buffers, bit output state, and high-water initialization marker.
- `MIN_LOOKAHEAD`, `MAX_DIST`, and `WIN_INIT` encode assumptions used by match search and window refill code.
- `_tr_tally_lit` and `_tr_tally_dist` are inlined when `H2_ZLIB_DEBUG` is not enabled, updating literal/distance buffers and dynamic tree frequencies directly.
- External `_length_code` and `_dist_code` tables are required for distance/length code mapping.

Dependencies:
- Includes `hammer2_zlib_zutil.h`.
- Used by deflate implementation and tree implementation files in the bundled zlib directory.

Notable risks:
- This is internal zlib ABI; any field layout or macro change must be coordinated with deflate and tree code.
- Buffer overlay assumptions between pending output and literal/distance buffers are made by the implementation and are easy to break.
- Macros such as `_tr_tally_dist` evaluate arguments in specific ways and assume caller-supplied values are already range-adjusted.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.c

Fast inflate inner-loop decoder for HAMMER2’s vendored zlib decompressor.

Key responsibilities:
- Implements `inflate_fast()`, the hot path for decoding deflate literal/length and distance codes.
- Decodes literals, length/distance pairs, second-level Huffman table entries, and end-of-block markers.
- Copies match data either from the current output buffer or from the sliding window.
- Detects invalid literal/length codes, invalid distance codes, and invalid distances too far back.
- Updates `z_stream` pointers/counters and inflate bit buffer state before returning to the main inflate state machine.

Important implementation details:
- The routine assumes it is entered in `LEN` mode with at least six input bytes, at least 258 output bytes, and fewer than eight held bits.
- Localizes stream/state fields for speed, including input/output pointers, window position, bit accumulator, Huffman tables, and masks.
- Supports pre-increment vs post-increment pointer tuning through `POSTINC`.
- A length/distance pair can consume up to 48 bits and output up to 258 bytes, which drives the entry assumptions.
- On end-of-block it sets mode to `TYPE`; on invalid data it sets mode to `BAD` and stores a message.
- Handles wrapped-window copies through `wnext`, `whave`, and `wsize`, then finishes any remaining copy from already-produced output.
- Restores unused input bytes by rolling back whole bytes from the bit accumulator before updating stream fields.

Dependencies:
- Includes zlib utility, inflate tree, inflate state, and inffast headers.
- Called by the main inflate implementation when buffer sizes allow the fast path.

Notable risks:
- Entry preconditions are strict; calling with insufficient input/output space can overrun assumptions.
- Distance-copy logic is intricate around window wraparound and overlap; small changes can corrupt decompressed output.
- Strict distance checking depends on `INFLATE_STRICT` and `state->sane`; compatibility modes may permit invalid-distance recovery behavior if enabled.
- The function mutates mode and error message directly, so callers must resume the main inflate state machine correctly.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.h

Internal header declaring the zlib fast inflate decoder.

Key responsibilities:
- Declares `inflate_fast(z_streamp strm, unsigned start)` with `ZLIB_INTERNAL` visibility.
- Documents that this header is internal implementation detail and not for applications.

Dependencies:
- Requires zlib stream types and `ZLIB_INTERNAL` to be defined before inclusion, normally through zlib utility/inflate headers.

Notable risks:
- The prototype exposes the fast decoder’s low-level entry point; callers must satisfy the assumptions documented in `hammer2_zlib_inffast.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffixed.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffixed.h

Generated fixed Huffman decoding tables for HAMMER2’s vendored zlib inflate implementation.

Key responsibilities:
- Defines static `lenfix[512]` table for fixed literal/length decoding.
- Defines static `distfix[32]` table for fixed distance decoding.
- Provides precomputed `code` entries used when inflating fixed-code deflate blocks.
- Avoids rebuilding fixed Huffman tables at runtime.

Important implementation details:
- The file is generated by zlib’s `makefixed()` tooling.
- Table entries encode operation flags, bit counts, and values for literals, lengths, distances, invalid codes, and end-of-block handling.
- Intended only for internal inclusion by inflate code with the `code` type already defined.

Dependencies:
- Depends on the zlib internal `code` structure definition from inflate tree/header code.
- Used by the main inflate implementation when processing fixed Huffman blocks.

Notable risks:
- The tables must match the zlib `code` layout and fixed-code semantics exactly; hand edits can silently break decompression.
- Because the file is generated internal data, replacing zlib components piecemeal can cause table/layout mismatches.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffixed.h -->