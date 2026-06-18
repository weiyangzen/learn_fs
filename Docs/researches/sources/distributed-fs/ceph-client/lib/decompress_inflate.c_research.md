# sources/distributed-fs/ceph-client/lib/decompress_inflate.c

## Purpose
Wraps zlib inflate to decompress gzip-compressed kernels, initramfs, and initrd images in both preboot static and linked kernel environments.

## APIs, Types, and Functions
The core helper is `__gunzip()`. Linked builds expose `gunzip()`, while preboot builds expose `__decompress()`. The file statically includes zlib inflate sources in `STATIC` builds and uses zlib headers in linked builds. `nofill()` is the fallback reader when no `fill` callback is supplied.

## Control Flow
`__gunzip()` allocates an output buffer when using `flush`, an input buffer when no input pointer is supplied, a zlib stream, and a zlib workspace. It validates the gzip magic/method, skips the basic 10-byte header and optional filename, initializes raw inflate with `zlib_inflateInit2(..., -MAX_WBITS)`, then loops reading input via `fill`, inflating, and flushing produced output. It treats `Z_STREAM_END` as success, maps other zlib errors to `-1`, records `pos` past the gzip trailer, and frees all allocations via cleanup labels.

## State and Persistence
Decompression state is per-call in `struct z_stream_s`, the workspace, input buffer, and output buffer. There is no global mutable state. The caller-provided output buffer is filled in place when no `flush` callback is used.

## Dependencies and Integration Points
Depends on zlib inflate internals, optional DFLTCC workspace sizing, `linux/decompress/mm.h`, and the kernel decompressor callback ABI. It integrates with `decompress.c` for gzip magic dispatch and with early boot code that may lack normal kernel allocation facilities.

## Risks and Test Signals
Risks include incomplete gzip header handling, truncated input, flush short writes, workspace sizing differences with DFLTCC, and unbounded output mode when `out_len` is zero. Test signals include gzip kernel/initramfs boot tests, optional filename header cases, corrupted gzip streams, streaming input/output callbacks, and generic-vs-known-tool decompression comparisons.
