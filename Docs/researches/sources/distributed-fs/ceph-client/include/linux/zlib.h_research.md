# sources/distributed-fs/ceph-client/include/linux/zlib.h

## Purpose
Declares the Linux-kernel zlib deflate/inflate interface. This is a modified zlib API that keeps the stream model but requires callers to allocate per-stream workspaces in advance, adding kernel-specific flush and inflate helpers.

## Important APIs, Types, and Functions
`z_stream` carries input/output pointers, available byte counts, totals, error message, opaque internal state, caller-provided `workspace`, data type, checksum, and reserved field. Constants define flush modes (`Z_NO_FLUSH`, `Z_PACKET_FLUSH`, `Z_SYNC_FLUSH`, `Z_FULL_FLUSH`, `Z_FINISH`, `Z_BLOCK`), return codes, compression levels, strategies, data types, and `Z_DEFLATED`. Workspace APIs are `zlib_deflate_workspacesize()` and `zlib_inflate_workspacesize()`. Core APIs are `zlib_deflateInit2()`, `zlib_deflate()`, `zlib_deflateReset()`, `zlib_deflateEnd()`, `zlib_inflateInit2()`, `zlib_inflate()`, `zlib_inflateReset()`, `zlib_inflateEnd()`, `zlib_inflateIncomp()`, and `zlib_inflate_blob()`. Convenience macros provide `zlib_deflateInit()` and `zlib_inflateInit()`. `deflateBound()` estimates an upper bound for compressed output.

## Control Flow
Compression callers size and assign a workspace, initialize the stream, repeatedly supply input and output space to `zlib_deflate()`, optionally flush, finish with repeated `Z_FINISH` calls until `Z_STREAM_END`, then end or reset. Decompression callers allocate inflate workspace, initialize with default or explicit window bits, repeatedly call `zlib_inflate()` until `Z_STREAM_END` or an error, then reset or end. `Z_BLOCK` lets inflate stop on deflate block boundaries. `zlib_inflateIncomp()` updates history for incompressible data without producing output and is intended for PPP-style stored-block handling.

## State and Persistence
Persistent stream state lives in caller-owned `z_stream` plus the preallocated `workspace`; implementation-private details hang off `state`. `next_in`, `avail_in`, `total_in`, `next_out`, `avail_out`, and `total_out` are mutable progress counters. `adler` tracks Adler-32 or CRC32 depending on format. Reset APIs preserve allocated workspace while returning stream state to a reusable baseline.

## Dependencies and Integration Points
Depends on `linux/zconf.h`. Integrates with kernel compression users including PPP deflate, filesystems, boot and initramfs utilities, firmware/blob unpacking, and any code handling zlib, gzip, or raw deflate streams.

## Risks
Callers must provide correctly sized workspaces before init; unlike userspace zlib, allocation is not implicit. Buffer-progress loops must handle `Z_OK` with full output, nonfatal `Z_BUF_ERROR`, and repeated `Z_FINISH` calls. `windowBits` controls raw versus zlib/gzip decoding and must match producer format. Checksums and dictionary requests must be handled correctly. The visible dummy `internal_state` is only a compiler workaround, not an API.

## Test Signals
Signals include RFC 1950/1951/1952 vectors, raw/zlib/gzip inflate tests, PPP `Z_PACKET_FLUSH` and `zlib_inflateIncomp()` tests, workspace-size boundary tests, `Z_BLOCK` behavior, `zlib_inflate_blob()` success/error paths, truncated/corrupt input fuzzing, and build coverage across reduced `MAX_WBITS`/`MAX_MEM_LEVEL`.
