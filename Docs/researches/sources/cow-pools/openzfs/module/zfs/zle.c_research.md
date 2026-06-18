# File Research: sources/cow-pools/openzfs/module/zfs/zle.c

Read coverage: complete file, 97 lines.

Purpose: zero-length encoding compression algorithm implementation for ZIO compression table entry `zle`.

Algorithm:
- Encodes runs as one-byte length tags.
- If tag value is below parameter `n`, the next `tag + 1` bytes are literal data.
- If tag value is at least `n`, it represents a run of zeros of length `256 - tag + 1`.
- OpenZFS registers this through `ZFS_COMPRESS_WRAP_DECL(zfs_zle_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_zle_decompress)`.

Compression:
- `zfs_zle_compress_buf()` walks source and destination buffers.
- Zero runs are emitted as length-only records.
- Literal runs are emitted as a length byte plus copied non-zero-containing bytes, stopping before zero pairs where possible.
- If output cannot finish within destination capacity, it returns original source length to indicate no useful compression.

Decompression:
- `zfs_zle_decompress_buf()` reads length tags, copies literal bytes or fills zero runs.
- It validates source and destination bounds and returns `0` only when exactly the destination length is produced; malformed/truncated streams return `-1`.

Key dependencies:
- Referenced by `zio_compress_table[]` in `zio_compress.c`.
- Used by write compression and read decompression paths in `zio.c`.
