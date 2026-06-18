# sources/distributed-fs/ceph-client/fs/ubifs/compress.c

## Purpose
`compress.c` is UBIFS' central compression/decompression adapter. It hides the kernel crypto asynchronous compression API behind UBIFS-specific helpers, chooses the compiled-in compressor implementation, falls back to uncompressed storage when compression is not useful or unavailable, and initializes/free compressor transforms at module lifetime boundaries.

## Important APIs, Types, and Functions
- `union ubifs_in_ptr` lets the shared compression helper accept either a linear buffer or a `struct folio`.
- `struct ubifs_compressor *ubifs_compressors[UBIFS_COMPR_TYPES_CNT]` is the global compressor dispatch table indexed by on-flash compression type.
- Static compressor descriptors exist for `none`, `lzo`, `zlib`, and `zstd`; the non-`none` descriptors only carry `capi_name` when the corresponding `CONFIG_UBIFS_FS_*` option is enabled.
- `ubifs_compress()` and `ubifs_compress_folio()` wrap `ubifs_compress_common()` for linear buffers and folio-backed input.
- `ubifs_decompress()` and `ubifs_decompress_folio()` wrap `ubifs_decompress_common()` for linear and folio-backed output.
- `ubifs_compressors_init()` calls `compr_init()` for LZO, ZSTD, and ZLIB, then installs the fake `none` compressor; `ubifs_compressors_exit()` frees any allocated crypto transforms.

## Control Flow
Compression first rejects `UBIFS_COMPR_NONE` and too-small inputs. For real compressors it caps the destination size to `in_len - UBIFS_MIN_COMPRESS_DIFF`, submits an `acomp` request using either `acomp_request_set_src_folio()` or `acomp_request_set_src_dma()`, and handles `-EAGAIN` by cloning the request, enabling backlog, and waiting synchronously through `crypto_wait_req()`. If compression errors or does not beat the minimum-difference threshold, the input is copied verbatim and `*compr_type` is changed to `UBIFS_COMPR_NONE`.

Decompression validates the numeric compressor type, rejects unavailable compiled-out compressors by checking `capi_name`, directly copies `UBIFS_COMPR_NONE` data, and otherwise submits an `acomp` decompression request. It supports DMA-buffer input and either folio or buffer output. Decompression errors are logged with the compressor name and propagated.

Initialization is ordered so partial failures unwind previously initialized compressors. A compressor with no `capi_name` still gets installed in the table, which allows attempts to decompress that type to return a controlled `-EINVAL` instead of dereferencing a missing transform.

## State and Persistence Behavior
The file does not persist data directly, but it controls on-flash data-node encoding through `compr_type`, compressed length, and fallback-to-none behavior used by journal writes. `dn->compr_type` and node data length written elsewhere depend on these helpers. The global compressor table and each descriptor's `cc` transform are process/module state shared by all UBIFS mounts.

## Dependencies and Integration Points
The implementation depends on `crypto/acompress.h`, crypto wait helpers, `struct folio` highmem helpers, and UBIFS constants from `ubifs.h`. It is consumed by file read/write and journal paths, notably data-node creation and `file.c` reads through `ubifs_decompress_folio()`. Encryption is layered separately: `file.c` decrypts before decompression and `crypto.c` encrypts after compression.

## Risks and Edge Cases
- The output buffer length must be initialized correctly by callers; `ubifs_compress_common()` assumes `*out_len` is the allocated destination size.
- Compiled-out compressor types are represented but not usable; reading media containing such a type fails with `-EINVAL`.
- A compression error silently stores uncompressed data, which is intentional for writes but means callers must trust the returned `compr_type`.
- Folio offsets and lengths must describe a valid source/destination range; this file relies on the caller and folio helpers for bounds correctness.
- Async crypto `-EAGAIN` handling allocates a clone with `GFP_NOFS | __GFP_NOWARN`; allocation failure paths depend on the crypto API's returned error behavior.

## Test Signals
Useful test signals include round-trip data-node read/write with all enabled compressors, fallback behavior for small or incompressible buffers, decompression failure when a compressor is compiled out, folio-offset compression/decompression cases, and fault injection around async crypto backlog/clone paths.
