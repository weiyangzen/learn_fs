<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c

## Purpose
Provides a tiny gzip decompressor wrapper and bump allocator for Xtensa compressed boot images.

## Important APIs, Types, And Functions
Exports `gunzip(void *dst, int dstlen, unsigned char *src, int *lenp)`. Internal helpers and state are external `avail_ram`/`end_avail`, `exit`, `zalloc`, gzip flag constants, and zlib `z_stream`.

## Control Flow
`gunzip` parses the gzip header, rejects non-deflate or reserved flags, skips optional extra/name/comment/header-CRC fields, allocates zlib workspace with `zalloc`, initializes raw inflate with `zlib_inflateInit2(..., -MAX_WBITS)`, inflates into the destination buffer, stores output length back through `lenp`, and ends the stream. Error paths spin forever in `exit`.

## State And Persistence
State is the boot heap pointer `avail_ram`, bounded by `end_avail`, and temporary zlib stream state. No persistence after kernel jump.

## Dependencies And Integration Points
Depends on boot-redboot `avail_ram`/`end_avail` symbols, zlib inflate sources, and the compressed bootstrap's call convention.

## Risks And Edge Cases
There is no recovery or console output on malformed input or heap exhaustion. Header parsing trusts NUL terminators within `lenp` bounds only after optional scans. Destination size is fixed by caller.

## Test Signals
Boot valid gzip images, test malformed gzip headers under emulator, verify heap sizing against `zlib_inflate_workspacesize`, and compare decompressed bytes to `vmlinux.bin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c -->
