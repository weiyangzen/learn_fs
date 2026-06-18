<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c

Purpose: implements NTFS LZNT1 compression and decompression for normal NTFS compressed attributes. It supports a fast hash-based compressor, a slower best-match compressor, and chunked decompression of compressed or stored 4 KiB chunks.

Important APIs and types: public functions are `get_lznt_ctx`, `compress_lznt`, and `decompress_lznt`. Internal state is `struct lznt`, which tracks the current uncompressed chunk, best match, max match length, compression mode, and optional 4 KiB hash table. Helpers include `longest_match_std`, `longest_match_best`, `make_pair`, `parse_pair`, `compress_chunk`, and `decompress_chunk`.

Control flow: compression processes the input in 4 KiB chunks. For each chunk it searches for matches of length at least 3, emits groups controlled by one flag byte per eight tokens, encodes `(offset,length)` pairs with a variable split determined by current output position, and falls back to an uncompressed chunk when compressed output would not fit. All-zero chunks are reported specially so the top-level compressor can return size zero. Decompression reads chunk headers, distinguishes compressed chunks from stored chunks, decodes flag-controlled literals or pairs, validates boundaries and offsets, copies overlapping matches, pads short chunks with zeros when needed, and stops at an all-zero chunk header or when output is full.

State and persistence behavior: the compressor context is heap-allocated and temporary. Persistent effects happen in callers that store compressed NTFS attribute data; this file only produces or consumes buffers. LZNT chunk headers and tokens are on-disk data format.

Dependencies and integration points: uses kernel memory/string helpers and NTFS utility macros from `debug.h`/`ntfs_fs.h`. It is used by compressed attribute read/write paths elsewhere in NTFS3.

Risks: compression and decompression must exactly match LZNT1’s position-dependent offset/length bit split. The standard compressor hashes only two candidate positions, so compression ratio varies by level. Decompression has to reject offset underruns, truncated pairs, chunk-size overflows, and impossible headers without writing past 4 KiB. Returning uncompressed size from `compress_lznt` on compression-buffer exhaustion is a special caller contract.

Test signals: round-trip random and patterned buffers, all-zero chunk return, incompressible fallback chunks, best vs standard compression mode, inputs crossing 4 KiB chunk boundaries, malformed pair offset/length fuzz cases, truncated chunks, short final chunks with zero padding, and comparison against Windows/LZNT1 reference vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c -->
