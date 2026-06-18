
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-gzip.c

Purpose: provides gzip payload decompression for EFI zboot images.

Important APIs/types/functions: exports `efi_zboot_decompress_init()` and `efi_zboot_decompress()`. Uses zlib inflate sources included directly and a static `z_stream_s`.

Control flow: init skips the fixed 10-byte gzip header, sets input bounds, allocates zlib workspace through EFI pages, initializes raw deflate mode with `-MAX_WBITS`, and returns the uncompressed payload size. Decompress sets output pointers, runs inflate, ends the stream, frees workspace, checks for `Z_STREAM_END`, syncs instruction cache, and returns EFI status.

State and persistence behavior: static stream/workspace state exists between init and decompress only. The decompressed output buffer persists to common stub boot.

Dependencies and integration points: depends on zlib, EFI page allocation/free, linker symbols for compressed data and payload size, and arch `efi_cache_sync_image()`.

Risks and test signals: assumes no gzip filename/extra header beyond 10 bytes and exactly one init/decompress sequence. Test signals include valid gzip zboot, corrupt payload, workspace allocation failure, cache sync, and payload-size consistency.
