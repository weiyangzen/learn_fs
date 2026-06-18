# sources/distributed-fs/ceph-client/lib/lz4/lz4_compress.c

## Purpose
`lz4_compress.c` implements the kernel LZ4 fast compressor, including one-shot compression, destination-size-limited compression, and streaming compression with a 64 KiB history window. It is a kernel-adapted copy of Yann Collet's LZ4 block compressor and exports the kernel symbols consumed by crypto wrappers, filesystem compression users, and boot/decompression helpers.

## Important APIs, types, and functions
Public exports are `LZ4_compress_fast()`, `LZ4_compress_default()`, `LZ4_compress_destSize()`, `LZ4_resetStream()`, `LZ4_loadDict()`, `LZ4_saveDict()`, and `LZ4_compress_fast_continue()`. The central private routines are `LZ4_compress_generic()` and `LZ4_compress_destSize_generic()`. Hash-table helpers such as `LZ4_hashPosition()`, `LZ4_putPositionOnHash()`, and `LZ4_getPositionOnHash()` abstract the three table encodings: pointer table, 32-bit offset table, and 16-bit offset table. Stream state is `LZ4_stream_t_internal` from `include/linux/lz4.h`, especially `hashTable`, `currentOffset`, `dictionary`, and `dictSize`.

## Control flow
One-shot compression resets caller-provided work memory, chooses `byU16` for inputs below the 64 KiB limit and a native pointer or U32 table otherwise, then calls `LZ4_compress_generic()`. The generic loop seeds the first hash, advances through the input with an acceleration-dependent skip pattern, checks distance and dictionary validity, catches matches backward to maximize literals, emits an LZ4 token, copies literal bytes, writes the match offset, encodes the match length extension bytes, and then probes for an immediate next match. If no more match can be safely searched, `_last_literals` writes the final literal run. The destination-size variant inverts the contract: it reduces the final literal run or match length when needed and updates `*srcSizePtr` with the consumed source bytes.

## State and persistence
Non-streaming calls use only caller-supplied work memory and do not persist state after return. Streaming calls mutate `LZ4_stream_t_internal`: dictionaries are capped to 64 KiB, hash offsets are renormalized when `currentOffset` risks overflow, and `saveDict()` copies the tail dictionary into a safe caller buffer. `LZ4_compress_fast_continue()` supports prefix mode when the next source block immediately follows the previous dictionary and external-dictionary mode when it does not.

## Dependencies and integration points
The file depends on `lz4defs.h`, `linux/lz4.h`, kernel unaligned access helpers, `memset`, `memmove`, and module export infrastructure. Integration is through exported LZ4 symbols and `CONFIG_LZ4_COMPRESS`; known consumers in this tree include `crypto/lz4.c`, `lib/decompress_unlz4.c`, SquashFS, and other kernel compression front ends that allocate `LZ4_MEM_COMPRESS` work buffers.

## Risks and test signals
The highest risks are pointer arithmetic around `match + refDelta`, distance checks, output-limit checks before wild copies, and streaming dictionary transitions where old input must remain readable. Incorrect work-memory sizing or alignment is a caller bug and can corrupt compression state. Test signals include one-shot round trips across small and large inputs, incompressible data returning a valid larger block or zero under tight output limits, `LZ4_compress_destSize()` reporting partial source consumption, streaming compression across contiguous and non-contiguous blocks, dictionary save/load behavior, and malformed boundary fuzzing paired with `LZ4_decompress_safe()`.
