<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lz4.h -->
# sources/distributed-fs/ceph-client/include/linux/lz4.h

## Purpose
This header declares the kernel LZ4 compression interface, including one-shot, high-compression, streaming compression, streaming decompression, dictionary handling, bounds, and state-buffer sizes.

## Important APIs, Types, and Functions
Constants include `LZ4_MEMORY_USAGE`, `LZ4_MAX_INPUT_SIZE`, `LZ4_COMPRESSBOUND`, `LZ4_MEM_COMPRESS`, `LZ4HC_MEM_COMPRESS`, and `LZ4_DISTANCE_MAX`. State types are `LZ4_stream_t`, `LZ4_streamHC_t`, and `LZ4_streamDecode_t`. APIs include `LZ4_compressBound`, `LZ4_compress_default`, `LZ4_compress_fast`, `LZ4_compress_destSize`, safe and fast decompressors, HC compression and reset/load/save dictionary helpers, streaming continue functions, and dictionary-based decompression.

## Control Flow
Callers allocate work memory or stream state, then compress blocks into caller-sized buffers. Streaming functions preserve recent history or saved dictionaries across blocks. Safe decompression validates input and output bounds; fast decompression assumes trusted input and known output size.

## State and Persistence Behavior
One-shot APIs use caller-provided work memory transiently. Streaming state stores hash tables, offsets, dictionary pointers, prefix state, and HC chains. Compressed data may be persisted by callers, but the header manages no storage.

## Dependencies and Integration Points
It depends on kernel types and string helpers. Integration points include zram, filesystems, network/storage compression, and any kernel subsystem using raw LZ4 blocks.

## Risks and Test Signals
Risks include undersized output buffers, using fast decompression on untrusted data, invalid source sizes above `LZ4_MAX_INPUT_SIZE`, stale dictionary memory, and stream-state reuse without reset. Test signals are compression round trips, malformed-input tests, boundary-size tests, dictionary/ring-buffer streaming tests, and sanitizer/fuzzer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lz4.h -->
