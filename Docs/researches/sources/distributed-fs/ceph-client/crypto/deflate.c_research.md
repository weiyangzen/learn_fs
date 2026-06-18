# sources/distributed-fs/ceph-client/crypto/deflate.c

## Purpose
`deflate.c` registers an asynchronous compression API (`acomp`) implementation for raw DEFLATE, primarily for IPCOMP. It adapts kernel zlib deflate/inflate streams to crypto scatterlist compression requests.

## Important APIs, Types, And Functions
- `struct deflate_stream` embeds `struct z_stream_s` followed by a flexible workspace.
- `deflate_alloc_stream()` allocates enough workspace for either inflate or deflate with the configured raw-deflate parameters.
- `deflate_compress_one()` walks source and destination scatterlists and drives `zlib_deflate()` until `Z_STREAM_END`.
- `deflate_decompress_one()` similarly drives `zlib_inflate()` and detects destination exhaustion.
- `deflate_compress()` and `deflate_decompress()` lock a percpu/shared `crypto_acomp_stream`, initialize zlib state, run the operation, and unlock.
- `deflate_init()` lazily allocates stream contexts under `deflate_stream_lock`.
- `acomp` registers the algorithm as `deflate` / `deflate-generic`.

## Control Flow
Compression locks a stream with bottom halves disabled, initializes zlib with `zlib_deflateInit2()` using negative window bits for raw DEFLATE, then alternates destination chunks and source chunks through `acomp_walk_virt()`. It uses `Z_NO_FLUSH` while more source remains and `Z_FINISH` on the final input. Decompression initializes inflate with negative window bits and feeds source while repeatedly taking destination chunks. It treats lack of progress with no destination as `-ENOSPC`.

## State And Persistence
Zlib state and workspace are retained in allocated stream contexts, but each operation reinitializes zlib before use. The algorithm-level `deflate_streams` pool persists until module exit, then `crypto_acomp_free_streams()` releases it. Request output length is persisted to `req->dlen`.

## Dependencies And Integration Points
The file depends on `<linux/zlib.h>`, crypto acomp stream pooling, and `acomp_walk_*` scatterwalk helpers. It registers with the crypto compression API and is tested by generic compression test descriptors for `deflate`.

## Risks And Edge Cases
The main operational risks are destination exhaustion and zlib return-code translation. Compression returns `-ENOSPC` when no destination chunk exists, and `-EINVAL` if zlib does not finish cleanly. Decompression explicitly detects no-progress/no-output-space. The implementation assumes virtual scatterlist walking because `cra_flags` includes `CRYPTO_ALG_REQ_VIRT`.

## Test Signals
`testmgr.h` includes deflate compression and decompression vectors, and `testmgr.c` maps `deflate` to those vectors. Useful additional signals include truncated input, too-small output buffers, fragmented source/destination scatterlists, and repeated concurrent requests to exercise stream pooling.
