# sources/distributed-fs/ceph-client/crypto/zstd.c

## Purpose
This file registers Zstandard compression as a CryptoAPI acomp algorithm named `zstd` and `zstd-generic`. It wraps kernel zstd compression/decompression streams and scatterlist walking.

## Important APIs, Types, And Functions
`struct zstd_ctx` owns a compression context pointer, decompression context pointer, zstd parameters, and a flexible workspace. `zstd_alloc_stream()` sizes a shared workspace for both cstream and dstream use at default level 3 and max window log 18. `zstd_compress()` and `zstd_decompress()` implement scatterwalk streaming, with `zstd_compress_one()` and `zstd_decompress_one()` fast paths for fully contiguous buffers.

## Control Flow
Algorithm initialization lazily allocates shared acomp streams under `zstd_stream_lock`. Each request locks a stream in bottom-half-safe context, initializes the appropriate zstd stream in the workspace, walks source and destination segments, updates `req->dlen` to total output on success, and resets it to zero on error. Compression flushes after each source segment and ends the stream after input exhaustion; decompression loops until all source data is consumed.

## State, Dependencies, Integration, Risks, And Tests
Persistent state is held in the global stream pool, while each stream context owns reusable workspace allocated with `kvmalloc_flex()`. Dependencies include kernel zstd APIs, acomp internals, scatterwalk, vmalloc, and the CryptoAPI virtual-buffer request flag. Risks include destination exhaustion, workspace sizing drift with zstd API changes, noncoherent streaming assumptions, and serialized throughput due to limited stream pool availability. Test signals are acomp compression/decompression round trips, fragmented scatterlists, too-small destination buffers, corrupt input, large-window boundary inputs, and module unload freeing streams.
