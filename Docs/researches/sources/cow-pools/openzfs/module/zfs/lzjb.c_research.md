# File Research: sources/cow-pools/openzfs/module/zfs/lzjb.c

## Role

`lzjb.c` implements OpenZFS's private LZJB compressor and decompressor. The file keeps a ZFS-owned copy of the algorithm to protect the on-disk format from changes in shared platform compression code, remove checks unnecessary for ZFS's use case, and initialize the Lempel table deterministically so identical input blocks produce identical compressed output for deduplication.

## Compression API

`zfs_lzjb_compress_buf()` receives source and destination buffers, source and destination lengths, and an unused compression level parameter. It allocates a zeroed 1024-entry `uint16_t` Lempel table, then encodes the source as groups controlled by one-byte copy maps.

For each source position:

- A new copy-map byte is opened every eight items.
- The function checks whether enough destination space remains, using a conservative margin for the copy-map byte and worst-case token growth. If not, it frees the Lempel table and returns the source length to signal compression failure.
- Near the end of the source, where a maximum match cannot be safely probed, it emits literals.
- Otherwise it hashes the next three bytes, looks up the previous low-16-bit source position from the Lempel table, updates the table, computes a bounded 10-bit offset, and verifies a valid in-buffer three-byte match.
- Matches are encoded as two bytes containing match length minus `MATCH_MIN` and offset; literals are copied directly.

On success it frees the table and returns the compressed byte count.

## Decompression API

`zfs_lzjb_decompress_buf()` expands an LZJB stream into exactly `d_len` bytes. It reads copy-map bytes, copies literals directly, and decodes match entries into a match length and offset using `MATCH_BITS`, `MATCH_MIN`, and `OFFSET_MASK`. If a match offset points before the destination start, it returns `-1`; otherwise it copies from already produced output until the requested destination length is filled. The compressed input length parameter and compression level parameter are unused.

`ZFS_COMPRESS_WRAP_DECL(zfs_lzjb_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_lzjb_decompress)` expose the routines through OpenZFS's compressor framework.

## Constants And Format

The file defines `MATCH_BITS 6`, `MATCH_MIN 3`, `MATCH_MAX 66`, a 10-bit offset mask derived from a 16-bit encoded match word, and `LEMPEL_SIZE 1024`. Matches therefore encode lengths from 3 through 66 bytes and offsets within the LZJB sliding window represented by the low bits of source positions.

The compressed stream alternates copy-map bytes with up to eight literal or match entries. A set copy-map bit means the corresponding entry is a two-byte back-reference; a clear bit means a one-byte literal.

## State And Dependencies

The implementation is stateless across calls. Compression allocates and frees a temporary zeroed Lempel table with `kmem_zalloc()` and `kmem_free()`. Decompression allocates no memory. The file depends on `sys/zfs_context.h` for OpenZFS kernel/userland compatibility types and allocation APIs, and on `sys/zio_compress.h` for wrapper declarations.

## Risks And Invariants

The compressor intentionally returns `s_len` on destination overflow so the caller can treat the block as uncompressed. Deterministic output depends on the zeroed Lempel table at the start of every compression call.

The decompressor trusts callers to provide a valid compressed stream length indirectly through the containing ZFS block metadata; it ignores `s_len` and stops only when `d_len` bytes have been produced. Its explicit corruption check is limited to rejecting back-references before `d_start`, so caller-level bounds and checksum validation are important for malformed-data handling.
