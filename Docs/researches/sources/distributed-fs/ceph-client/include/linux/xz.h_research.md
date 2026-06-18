# sources/distributed-fs/ceph-client/include/linux/xz.h

## Purpose
Declares the XZ and MicroLZMA decompressor APIs used in kernel and standalone/preboot contexts. It defines decoder modes, return codes, buffer descriptors, opaque decoder states, lifecycle routines, and optional internal CRC32 helpers.

## Important APIs, Types, and Functions
`enum xz_mode` selects `XZ_SINGLE`, `XZ_PREALLOC`, or `XZ_DYNALLOC`. `enum xz_ret` reports progress and failures including `XZ_OK`, `XZ_STREAM_END`, unsupported checks, memory errors, memory-limit errors, format/options/data errors, and buffer errors. `struct xz_buf` carries input and output buffers plus current positions. XZ lifecycle APIs are `xz_dec_init()`, `xz_dec_run()`, `xz_dec_reset()`, and `xz_dec_end()`. MicroLZMA uses opaque `struct xz_dec_microlzma` plus `xz_dec_microlzma_alloc()`, `xz_dec_microlzma_reset()`, `xz_dec_microlzma_run()`, and `xz_dec_microlzma_end()`. Standalone CRC support exposes `xz_crc32_init()` and `xz_crc32()` when `XZ_INTERNAL_CRC32` is enabled.

## Control Flow
Callers allocate a decoder for the selected mode, fill `xz_buf`, repeatedly call `xz_dec_run()` until `XZ_STREAM_END` or an error, optionally reset multi-call state for another stream, then end the decoder. Single-call mode decodes an entire stream in one call using the output buffer as dictionary workspace. Preallocated mode reserves dictionary memory at init time. Dynamic mode allocates after stream headers disclose dictionary size. MicroLZMA allocation records mode and dictionary size; each stream must be reset with compressed and uncompressed sizes before `xz_dec_microlzma_run()` loops to completion.

## State and Persistence
Opaque decoder states persist allocation mode, dictionary buffers, stream parser state, and integrity-check state. `xz_buf` position fields are mutable progress state owned by the caller. In single-call XZ mode, failed decodes leave input/output positions unmodified and output contents after the original position undefined.

## Dependencies and Integration Points
Depends on Linux or standalone stddef/stdint types and optional CRC32 selection. Integrates with kernel image/initramfs decompression, filesystems such as EROFS for MicroLZMA, module or firmware decompressors, and preboot code that may compile only selected modes.

## Risks
Mode-specific semantics are easy to misuse. `XZ_DYNALLOC` can return memory errors from `xz_dec_run()`, while `XZ_PREALLOC` reports dictionary limit failures. `XZ_BUF_ERROR` means different things in single-call and multi-call mode. MicroLZMA can keep returning `XZ_OK` without a buffer error, so callers must enforce input/output availability and detect truncation to avoid infinite loops. Unsupported integrity checks may be recoverable only in configurations that define support for any check.

## Test Signals
Signals include valid XZ streams across dictionary sizes, truncated/corrupt stream tests, unsupported option/check tests, low-memory and memory-limit injection, single-call buffer-too-small tests, MicroLZMA EROFS vectors, and standalone builds with internal CRC enabled and disabled.
